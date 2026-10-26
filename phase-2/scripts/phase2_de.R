#!/usr/bin/env Rscript
# Phase 2 normalization and differential expression, one dataset per call.
#
# Called by phase-2/scripts/phase2_ingest.py, which resolves the design and hands over a
# sample table. This script owns only the numeric part: read what the archive gave us,
# normalize it for its assay class, optionally correct a within-dataset batch covariate,
# fit the contrast against the reference arm, and write the FULL ranked gene list.
#
# Engines (ratified 2026-10-19, panel route 2026-10-20, see docs/project-plan.md):
#   deseq2                          raw count matrix
#   limma_trend                     expression array
#   pseudobulk_limma_trend          single cell, summed to one profile per patient
#   nanostring_housekeeping_limma   targeted panel, housekeeping-normalized
#   author_matrix_limma_trend       processed matrix only, authors' normalization accepted
#   two_colour_limma                two-colour arrays, log-ratios in a direct design
#
# Output: <accession>_de.csv with one row per gene per contrast, carrying a signed
# statistic and a direction, never thresholded. Phase 3 reads this file and nothing else.
#
# Usage:
#   Rscript phase-2/scripts/phase2_de.R --accession GSE163071 --engine deseq2 \
#     --indir build/phase2/GSE163071 --samples build/phase2/GSE163071/GSE163071_samples.csv \
#     --reference non_neoplastic_brain --out build/phase2/GSE163071/GSE163071_de.csv

suppressPackageStartupMessages({
  library(limma)
  library(data.table)
})

args <- commandArgs(trailingOnly = TRUE)
opt <- function(name, default = NULL) {
  hit <- which(args == paste0("--", name))
  if (length(hit) == 0) return(default)
  args[hit + 1]
}
accession <- opt("accession"); engine <- opt("engine"); indir <- opt("indir")
samples_path <- opt("samples"); reference <- opt("reference"); out_path <- opt("out")
combat_col <- opt("combat")
stopifnot(!is.null(accession), !is.null(engine), !is.null(indir), !is.null(samples_path))

samples <- fread(samples_path)
message(sprintf("[%s] %s: %d samples, reference arm %s", accession, engine, nrow(samples), reference))

stop_with <- function(...) stop(sprintf("[%s] %s", accession, paste0(...)), call. = FALSE)

# ---- readers ---------------------------------------------------------------

METADATA_FILES <- "(_gsm_soft\\.txt|\\.sdrf\\.txt|\\.idf\\.txt|_samples\\.csv|filelist\\.txt)$"

files_in <- function(pattern) {
  hits <- list.files(indir, pattern = pattern, full.names = TRUE, recursive = TRUE)
  hits[!grepl(METADATA_FILES, hits)]
}

#' Read a gene-by-sample table from a text file, whatever the delimiter.
#'
#' Deposited matrices often carry several annotation columns before the samples
#' (GSE163071 leads with Chromosome, Start, Stop, Strand, Gene Symbol), so the gene
#' identifier is chosen by name rather than by position, and the sample columns are
#' selected later by align_to_samples. Nothing is coerced to numeric until then.
ID_COLUMN_PREFERENCE <- c("gene symbol", "gene_symbol", "gene name", "gene_name", "symbol",
                          "gene id", "gene_id", "geneid", "gene", "ensembl", "id", "feature")

read_matrix_file <- function(path) {
  tab <- fread(path, data.table = FALSE)
  if (ncol(tab) < 2) stop_with("could not parse a matrix from ", basename(path))
  lower <- tolower(trimws(names(tab)))
  hit <- which(lower %in% ID_COLUMN_PREFERENCE)
  id_col <- if (length(hit)) hit[order(match(lower[hit], ID_COLUMN_PREFERENCE))][1] else 1L
  message("  gene identifier column: ", names(tab)[id_col])
  rownames(tab) <- make.unique(as.character(tab[[id_col]]))
  tab[, -id_col, drop = FALSE]
}

#' Match the matrix's columns to the sample table. GEO matrices name columns by GSM, by
#' title, or by both; anything unmatched is reported rather than dropped silently.
align_to_samples <- function(mat, samples) {
  as_numeric_matrix <- function(x) {
    out <- as.matrix(x)
    mode(out) <- "numeric"
    out
  }
  ids <- as.character(samples$sample_id)
  keys <- list(ids)
  for (extra in c("title", "soft_title", "description")) {
    if (extra %in% names(samples)) keys[[length(keys) + 1]] <- as.character(samples[[extra]])
  }
  keys <- Filter(function(k) any(nzchar(k)), keys)
  direct <- rep(NA_integer_, length(ids))
  for (key in keys) {
    hit <- match(key, colnames(mat))
    direct[is.na(direct)] <- hit[is.na(direct)]
  }
  # Substring matching in both directions: a column may be named by part of the sample
  # title (GSE207400 columns are M1014 for "Tumor Sample M1014") or carry the title plus a
  # suffix. Only unique hits are accepted.
  for (key in keys) {
    loose <- sapply(key, function(k) {
      h <- grep(k, colnames(mat), fixed = TRUE)
      if (length(h) == 1) h else NA_integer_
    })
    direct[is.na(direct)] <- loose[is.na(direct)]
  }
  for (key in keys) {
    reverse <- sapply(key, function(k) {
      h <- which(sapply(colnames(mat), function(col) nzchar(col) && grepl(col, k, fixed = TRUE)))
      if (length(h) == 1) h else NA_integer_
    })
    direct[is.na(direct)] <- reverse[is.na(direct)]
  }
  if (anyNA(direct)) {
    stop_with(sum(is.na(direct)), " of ", length(ids), " samples are absent from the matrix columns, ",
              "matched on sample_id and on title: ", paste(head(ids[is.na(direct)], 5), collapse = ", "),
              " | matrix columns look like: ", paste(head(colnames(mat), 3), collapse = ", "))
  }
  picked <- mat[, direct, drop = FALSE]
  colnames(picked) <- ids
  as_numeric_matrix(picked)
}

#' One 10x library per matrix.mtx.gz, summed over cells to a pseudobulk column.
#'
#' Cell-level counts are summed per library here and then summed again per patient by
#' pseudobulk(), which keeps the unit of inference the patient (spec call 6).
read_tenx_libraries <- function() {
  mtx <- files_in("matrix\\.mtx(\\.gz)?$")
  if (length(mtx) == 0) return(NULL)
  suppressPackageStartupMessages(library(Matrix))
  per_library <- lapply(mtx, function(path) {
    prefix <- sub("matrix\\.mtx(\\.gz)?$", "", path)
    features_path <- Sys.glob(paste0(prefix, "features.tsv*"))
    if (length(features_path) == 0) features_path <- Sys.glob(paste0(prefix, "genes.tsv*"))
    if (length(features_path) == 0) stop_with("no features file next to ", basename(path))
    features <- fread(features_path[[1]], header = FALSE, data.table = FALSE)
    counts <- readMM(path)
    if (nrow(counts) != nrow(features)) {
      stop_with(basename(path), " has ", nrow(counts), " rows but its features file has ", nrow(features))
    }
    gene <- if (ncol(features) >= 2) features[[2]] else features[[1]]
    summed <- Matrix::rowSums(counts)
    library_id <- regmatches(basename(path), regexpr("GSM[0-9]+", basename(path)))
    data.table(gene = gene, count = as.numeric(summed),
               library = if (length(library_id)) library_id else basename(prefix))
  })
  long <- rbindlist(per_library)
  wide <- dcast(long[, .(count = sum(count)), by = .(gene, library)], gene ~ library, value.var = "count")
  mat <- as.matrix(wide[, -1, with = FALSE])
  mode(mat) <- "numeric"
  rownames(mat) <- wide$gene
  message("  ", length(mtx), " 10x libraries summed to cell-aggregated columns: ",
          paste(head(colnames(mat), 3), collapse = ", "))
  mat
}

#' Per-sample count files, one file per GSM, assembled into a matrix.
#'
#' Several series deposit a file per sample rather than one matrix (GSE145064 ships 46 TSVs,
#' GSE232528 29 TXTs). Each file is keyed by the GSM in its name, the gene column is chosen
#' by name like any other matrix, and the count column is the last numeric column unless a
#' column is named like a count. Files whose GSM is not in the sample table are ignored, and
#' a sample with no file is reported rather than silently dropped.
read_per_sample_files <- function() {
  candidates <- files_in("^GSM[0-9]+.*\\.(txt|tsv|csv|tab)(\\.gz)?$")
  candidates <- candidates[!grepl("matrix\\.mtx|barcodes|features|genes\\.tsv", candidates)]
  wanted <- as.character(samples$sample_id)
  by_gsm <- regmatches(basename(candidates), regexpr("GSM[0-9]+", basename(candidates)))
  keep <- by_gsm %in% wanted
  if (sum(keep) < 2) return(NULL)
  candidates <- candidates[keep]; by_gsm <- by_gsm[keep]
  message("  ", length(candidates), " per-sample files for ", length(unique(by_gsm)), " of ",
          length(wanted), " samples")
  per_file <- Map(function(path, gsm) {
    tab <- fread(path, data.table = FALSE)
    if (ncol(tab) < 2) stop_with("could not parse ", basename(path))
    lower <- tolower(trimws(names(tab)))
    id_col <- which(lower %in% ID_COLUMN_PREFERENCE)
    id_col <- if (length(id_col)) id_col[order(match(lower[id_col], ID_COLUMN_PREFERENCE))][1] else 1L
    numeric_cols <- which(vapply(tab, is.numeric, logical(1)))
    numeric_cols <- setdiff(numeric_cols, id_col)
    if (length(numeric_cols) == 0) stop_with("no numeric column in ", basename(path))
    named_count <- numeric_cols[grepl("count|reads|expected", lower[numeric_cols])]
    value_col <- if (length(named_count)) named_count[1] else numeric_cols[length(numeric_cols)]
    data.table(gene = as.character(tab[[id_col]]), value = as.numeric(tab[[value_col]]), sample = gsm)
  }, candidates, by_gsm)
  long <- rbindlist(per_file)
  long <- long[, .(value = sum(value)), by = .(gene, sample)]   # one file per sample, so this is a no-op guard
  wide <- dcast(long, gene ~ sample, value.var = "value")
  mat <- as.matrix(wide[, -1, with = FALSE])
  mode(mat) <- "numeric"
  rownames(mat) <- wide$gene
  missing <- setdiff(wanted, colnames(mat))
  if (length(missing)) {
    stop_with(length(missing), " samples have no per-sample file: ",
              paste(head(missing, 5), collapse = ", "))
  }
  mat[is.na(mat)] <- 0
  message("  assembled ", nrow(mat), " features x ", ncol(mat), " samples from per-sample files")
  mat
}

#' Applied Biosystems 1700 chemiluminescent arrays (GPL2986), one file per sample.
#'
#' Each file carries Probe_ID, Gene_ID and three per-sample columns whose names embed the
#' sample: Signal_<id>, S_N_<id> and Flags_<id>. The signal is a one-colour chemiluminescent
#' intensity, so neither RMA nor a count model applies: values are masked where the
#' instrument flagged the spot, then log2-transformed and quantile-normalized across arrays.
#'
#' Masking thresholds (Kara, 2026-10-26): Flags > 0 or signal-to-noise < 3.
ABI_MIN_SN <- 3
read_abi_signal <- function() {
  paths <- files_in("^GSM[0-9]+.*\\.(txt|TXT)(\\.gz)?$")
  if (length(paths) == 0) return(NULL)
  first <- names(fread(paths[[1]], nrows = 1, data.table = FALSE))
  if (!any(grepl("^Signal", first)) || !"Probe_ID" %in% first) return(NULL)
  masked_total <- 0; measured_total <- 0
  per_file <- lapply(paths, function(path) {
    tab <- fread(path, data.table = FALSE)
    signal_col <- grep("^Signal", names(tab), value = TRUE)[1]
    sn_col <- grep("^S_N", names(tab), value = TRUE)[1]
    flag_col <- grep("^Flags", names(tab), value = TRUE)[1]
    value <- as.numeric(tab[[signal_col]])
    bad <- rep(FALSE, length(value))
    if (!is.na(flag_col)) bad <- bad | as.numeric(tab[[flag_col]]) > 0
    if (!is.na(sn_col)) bad <- bad | as.numeric(tab[[sn_col]]) < ABI_MIN_SN
    value[bad | value <= 0] <- NA_real_
    masked_total <<- masked_total + sum(bad, na.rm = TRUE)
    measured_total <<- measured_total + length(value)
    gsm <- regmatches(basename(path), regexpr("GSM[0-9]+", basename(path)))
    data.table(probe = as.character(tab$Probe_ID), value = value, sample = gsm)
  })
  wide <- dcast(rbindlist(per_file), probe ~ sample, value.var = "value")
  mat <- as.matrix(wide[, -1, with = FALSE])
  mode(mat) <- "numeric"
  rownames(mat) <- wide$probe
  message("  ", length(paths), " ABI signal files, ", nrow(mat), " probes; masked ",
          masked_total, " of ", measured_total, " spot values (",
          sprintf("%.1f%%", 100 * masked_total / max(measured_total, 1)),
          ") on Flags > 0 or S/N < ", ABI_MIN_SN)
  mat
}

read_counts <- function() {
  tenx <- read_tenx_libraries()
  if (!is.null(tenx)) return(align_to_samples(tenx, samples))
  per_sample <- read_per_sample_files()
  if (!is.null(per_sample)) return(align_to_samples(per_sample, samples))
  candidates <- files_in("(count|Count|COUNT|tpm|TPM|fpkm|FPKM).*\\.(txt|tsv|csv)(\\.gz)?$")
  if (length(candidates) == 0) candidates <- files_in("\\.(txt|tsv|csv)(\\.gz)?$")
  if (length(candidates) == 0) stop_with("no count-like file found in ", indir)
  mat <- read_matrix_file(candidates[[1]])
  message("  counts from ", basename(candidates[[1]]), ": ", nrow(mat), " features x ", ncol(mat), " columns")
  align_to_samples(mat, samples)
}

read_array_matrix <- function() {
  cels <- files_in("\\.(CEL|cel)(\\.gz)?$")
  if (length(cels) > 0) return(rma_from_cels(cels))
  read_author_matrix()
}

#' log2 then quantile normalization across arrays: the route for a one-colour signal that
#' arrives already summarized per probe, where RMA has nothing to do.
normalize_signal <- function(mat) {
  keep <- rowMeans(is.na(mat)) <= 0.5
  message("  dropping ", sum(!keep), " probes missing in more than half the arrays; ",
          sum(keep), " kept")
  logged <- log2(mat[keep, , drop = FALSE])
  normalizeBetweenArrays(logged, method = "quantile")
}

#' RMA from CEL files.
#'
#' affy handles 3-prime arrays (HG-U219, HG-U133 and the custom CDFs some series ship with
#' their raw data). Whole-transcript arrays such as HTA 2.0 need oligo and its pd.* package;
#' oligo is not installable as a conda build here, and the Bioconductor mac binaries link
#' against CRAN's R.framework rather than a conda R, so that case stops with a message.
rma_from_cels <- function(cels) {
  suppressPackageStartupMessages(library(affy))
  # Whole-transcript arrays (HTA, Gene ST) need oligo and the platform's pd.* package;
  # 3-prime arrays go through affy. The CEL header says which chip this is.
  chip <- tryCatch(affyio::read.celfile.header(cels[[1]])$cdfName, error = function(e) NA_character_)
  if (!is.na(chip)) {
    pd <- gsub("[^a-z0-9]+", ".", tolower(chip))
    pd <- paste0("pd.", gsub("^\\.|\\.$", "", pd))
    if (requireNamespace(pd, quietly = TRUE) && requireNamespace("oligo", quietly = TRUE)) {
      suppressPackageStartupMessages(library(oligo))
      message("  ", length(cels), " CEL files, chip ", chip, ", read with oligo via ", pd)
      eset <- oligo::rma(oligo::read.celfiles(cels, verbose = FALSE))
      mat <- Biobase::exprs(eset)
      colnames(mat) <- sub("\\.(CEL|cel)(\\.gz)?$", "", basename(colnames(mat)))
      message("  RMA matrix: ", nrow(mat), " probesets x ", ncol(mat), " arrays")
      return(align_to_samples(mat, samples))
    }
  }
  batch <- try(ReadAffy(filenames = cels), silent = TRUE)
  if (inherits(batch, "try-error")) {
    stop_with("affy could not read these CEL files (", as.character(batch), "). Whole-transcript ",
              "arrays such as HTA 2.0 need oligo plus the platform's pd.* package; see the route ",
              "table in phase-2/docs/phase2-pipeline-spec.md.")
  }
  cdf <- cleancdfname(cdfName(batch))
  message("  ", length(cels), " CEL files, CDF ", cdf)
  if (!requireNamespace(cdf, quietly = TRUE)) {
    shipped <- files_in("\\.(CDF|cdf)(\\.gz)?$")
    if (length(shipped) == 0) {
      stop_with("CDF package ", cdf, " is not installed and the series ships no CDF file. Install it ",
                "with install.packages(\"", cdf, "\", repos = ",
                "\"https://bioconductor.org/packages/3.20/data/annotation\", type = \"source\").")
    }
    message("  using the CDF shipped with the series: ", basename(shipped[[1]]))
    batch@cdfName <- "series_cdf"
    assign("series_cdf", make.cdf.env(shipped[[1]], verbose = FALSE), envir = globalenv())
  }
  eset <- rma(batch)
  mat <- exprs(eset)
  colnames(mat) <- sub("\\.(CEL|cel)(\\.gz)?$", "", basename(colnames(mat)))
  message("  RMA matrix: ", nrow(mat), " probesets x ", ncol(mat), " arrays")
  align_to_samples(mat, samples)
}

read_author_matrix <- function() {
  candidates <- files_in("(Matrix|matrix|processed|normalized)\\.(txt|tsv|csv)(\\.gz)?$")
  if (length(candidates) == 0) candidates <- files_in("\\.(txt|tsv|csv)(\\.gz)?$")
  if (length(candidates) == 0) stop_with("no author matrix found in ", indir)
  mat <- align_to_samples(read_matrix_file(candidates[[1]]), samples)
  # The authors' transformation is accepted as given (policy, 2026-10-21). Only an obviously
  # linear-scale matrix is logged, and the manifest records that this happened.
  if (max(mat, na.rm = TRUE) > 50) {
    message("  matrix is on a linear scale (max ", round(max(mat, na.rm = TRUE)), "), taking log2(x + 1)")
    mat <- log2(mat + 1)
  } else {
    message("  matrix already looks log-scaled (max ", round(max(mat, na.rm = TRUE), 2), "), left as deposited")
  }
  mat
}

#' NanoString nCounter: counts live in the CodeClass/Name/Accession/Count block of each RCC.
read_rcc <- function() {
  rcc <- files_in("\\.RCC(\\.gz)?$")
  if (length(rcc) == 0) stop_with("no RCC files found in ", indir)
  per_file <- lapply(rcc, function(path) {
    lines <- readLines(path, warn = FALSE)
    start <- grep("^<Code_Summary>", lines) + 1L
    end <- grep("^</Code_Summary>", lines) - 1L
    block <- read.csv(text = paste(lines[start:end], collapse = "\n"), stringsAsFactors = FALSE)
    data.table(file = basename(path), class = block$CodeClass, gene = block$Name,
               count = as.numeric(block$Count))
  })
  long <- rbindlist(per_file)
  wide <- dcast(long[class %in% c("Endogenous", "Housekeeping")], gene + class ~ file, value.var = "count")
  mat <- as.matrix(wide[, -(1:2), with = FALSE])
  mode(mat) <- "numeric"
  rownames(mat) <- wide$gene
  attr(mat, "codeclass") <- wide$class
  message("  ", length(rcc), " RCC files, ", sum(wide$class == "Endogenous"), " endogenous and ",
          sum(wide$class == "Housekeeping"), " housekeeping probes")
  mat
}

#' Pseudobulk: sum counts to one profile per patient, never per library (spec, call 6).
pseudobulk <- function(mat, samples) {
  unit <- if ("patient_id" %in% names(samples) && any(nzchar(as.character(samples$patient_id)))) {
    as.character(samples$patient_id)
  } else {
    stop_with("pseudobulk needs a patient id per sample; the ingestion step must supply one ",
              "(spec call 6), otherwise the unit would be the library and n would be inflated")
  }
  # One profile per patient per arm. A patient who contributes to two arms (GSE232516's
  # P13 gives both a pseudarthrosis and an iliac-crest sample) is a paired design, not an
  # ambiguous unit: the profiles stay separate and build_design() blocks on the patient.
  group <- paste(unit, samples$de_arm, sep = "::")
  summed <- t(rowsum(t(mat), group = group))
  per_group <- unique(data.table(sample_id = group, de_arm = samples$de_arm,
                                 de_role = samples$de_role, patient_id = unit))
  setkey(per_group, sample_id)
  paired <- any(duplicated(per_group$patient_id))
  message("  pseudobulked ", ncol(mat), " libraries to ", ncol(summed), " profiles over ",
          length(unique(unit)), " patients", if (paired) ", paired across arms" else "")
  list(matrix = summed[, per_group$sample_id, drop = FALSE], samples = as.data.frame(per_group))
}

#' Counts to log-CPM, the scale limma-trend expects (spec call 1).
log_cpm <- function(mat) {
  libsize <- pmax(colSums(mat), 1)
  log2(sweep(mat, 2, libsize, "/") * 1e6 + 1)
}

# ---- design ----------------------------------------------------------------

build_design <- function(samples, combat_col) {
  arm <- factor(samples$de_arm)
  patient <- NULL
  if ("patient_id" %in% names(samples)) {
    ids <- as.character(samples$patient_id)
    if (any(nzchar(ids)) && any(duplicated(ids[nzchar(ids)])) && length(unique(ids)) > 1) {
      tab <- table(ids, as.character(samples$de_arm))
      if (sum(rowSums(tab > 0) > 1) >= 1) {
        candidate <- factor(ids)
        # Blocking costs a parameter per patient. With few profiles the design saturates and
        # nothing is left to estimate variance from, so the block is only taken where at
        # least 2 residual degrees of freedom survive it.
        params <- nlevels(candidate) + nlevels(arm) - 1
        if (nrow(samples) - params >= 2) {
          patient <- candidate
          message("  paired design: ", nlevels(patient), " patients across arms, ",
                  "patient enters the model as a blocking factor")
        } else {
          message("  partial pairing present (", sum(rowSums(tab > 0) > 1), " patient(s) in more than one arm) ",
                  "but blocking on patient would leave ", nrow(samples) - params,
                  " residual degrees of freedom, so the block is dropped; the pairing is recorded in the ",
                  "sample table and should be stated with any result")
        }
      }
    }
  }
  if (!(reference %in% levels(arm))) stop_with("reference arm ", reference, " is not among the arms")
  arm <- relevel(arm, ref = reference)
  covariate <- NULL
  if (!is.null(combat_col)) {
    if (!(combat_col %in% names(samples))) stop_with("no column ", combat_col, " in the sample table")
    covariate <- factor(samples[[combat_col]])
    if (length(levels(covariate)) < 2) {
      message("  ", combat_col, " has one level, skipping correction")
      covariate <- NULL
    } else if (any(table(covariate, arm) == 0) && nlevels(covariate) == nlevels(arm)) {
      stop_with("batch ", combat_col, " is confounded with the arm; correcting would remove the ",
                "effect being tested (spec call 5)")
    }
  }
  list(arm = arm, covariate = covariate, patient = patient)
}

ranked_table <- function(tab, contrast, statistic_col, lfc_col, p_col, fdr_col) {
  out <- data.table(gene_symbol = rownames(tab), contrast = contrast,
                    statistic = tab[[statistic_col]], log2fc = tab[[lfc_col]],
                    p_value = tab[[p_col]], fdr = tab[[fdr_col]])
  out[, direction := fifelse(log2fc > 0, "up", fifelse(log2fc < 0, "down", "flat"))]
  out <- out[order(-abs(statistic))]
  out[, rank := seq_len(.N)]
  out[]
}

# ---- engines ---------------------------------------------------------------

run_limma <- function(mat, samples, label) {
  design_parts <- build_design(samples, combat_col)
  arm <- design_parts$arm
  if (!is.null(design_parts$covariate)) {
    suppressPackageStartupMessages(library(sva))
    mat <- ComBat(dat = mat, batch = design_parts$covariate, mod = model.matrix(~arm))
    message("  ComBat applied on ", combat_col, " (", nlevels(design_parts$covariate), " levels)")
  }
  patient <- design_parts$patient
  design <- if (is.null(patient)) model.matrix(~arm) else model.matrix(~patient + arm)
  fit <- eBayes(lmFit(mat, design), trend = TRUE)
  coefs <- grep("^arm", colnames(design), value = TRUE)
  rbindlist(lapply(coefs, function(coef) {
    tab <- topTable(fit, coef = coef, number = Inf, sort.by = "none")
    ranked_table(tab, sub("^arm", "", paste0(coef, "_vs_", reference)), "t", "logFC", "P.Value", "adj.P.Val")
  }))
}

run_deseq2 <- function(mat, samples) {
  suppressPackageStartupMessages(library(DESeq2))
  design_parts <- build_design(samples, combat_col)
  arm <- design_parts$arm
  coldata <- data.frame(arm = arm, row.names = colnames(mat))
  formula <- ~arm
  if (!is.null(design_parts$patient)) {
    coldata$patient <- design_parts$patient
    formula <- ~patient + arm
  }
  if (!is.null(design_parts$covariate)) {
    coldata$batch <- design_parts$covariate
    formula <- ~batch + arm
    message("  batch kept in the DESeq2 model rather than ComBat-corrected (counts stay integer)")
  }
  storage.mode(mat) <- "integer"
  dds <- DESeqDataSetFromMatrix(round(mat), colData = coldata, design = formula)
  dds <- DESeq(dds, quiet = TRUE)
  rbindlist(lapply(resultsNames(dds)[grepl("^arm", resultsNames(dds))], function(name) {
    res <- as.data.frame(results(dds, name = name))
    res$fdr <- res$padj
    ranked_table(res[!is.na(res$stat), ], sub("^arm_", "", name), "stat", "log2FoldChange", "pvalue", "fdr")
  }))
}

run_nanostring <- function() {
  mat <- read_rcc()
  codeclass <- attr(mat, "codeclass")
  hk <- mat[codeclass == "Housekeeping", , drop = FALSE]
  if (nrow(hk) == 0) stop_with("no housekeeping probes in the RCC files")
  size_factor <- exp(colMeans(log(pmax(hk, 1))))
  normalized <- log2(sweep(mat, 2, size_factor / mean(size_factor), "/") + 1)
  endogenous <- normalized[codeclass == "Endogenous", , drop = FALSE]
  message("  housekeeping-normalized on ", nrow(hk), " probes; ", nrow(endogenous), " endogenous genes kept")
  run_limma(align_to_samples(endogenous, samples), samples, "panel")
}

run_two_colour <- function() {
  raw <- files_in("-raw-data-.*\\.txt$")
  if (length(raw) == 0) stop_with("no ArrayExpress raw-data files in ", indir)
  stop_with("two-colour route is implemented up to the reader only. The 8 arrays are present, ",
            "but the per-array column names must be read off the file before limma::read.maimages ",
            "can be pointed at them (E-MEXP-258 and E-TABM-69 are legacy Tab2MAGE exports with ",
            "study-specific headers). Inspect head(", basename(raw[[1]]), ") and set the ",
            "columns argument before running this engine.")
}

result <- switch(engine,
  deseq2 = run_deseq2(read_counts(), samples),
  limma_trend = run_limma(read_array_matrix(), samples, "array"),
  pseudobulk_limma_trend = {
    pb <- pseudobulk(read_counts(), samples)
    run_limma(log_cpm(pb$matrix), pb$samples, "pseudobulk")
  },
  nanostring_housekeeping_limma = run_nanostring(),
  author_matrix_limma_trend = run_limma(read_author_matrix(), samples, "author matrix"),
  pseudobulk_author_matrix = {
    pb <- pseudobulk(read_author_matrix(), samples)
    run_limma(pb$matrix, pb$samples, "pseudobulk of an author matrix")
  },
  two_colour_limma = run_two_colour(),
  abi_signal_limma = {
    signal <- read_abi_signal()
    if (is.null(signal)) stop_with("no ABI signal files found; expected per-sample text files with ",
                                   "Probe_ID and Signal_<sample> columns")
    run_limma(normalize_signal(align_to_samples(signal, samples)), samples, "ABI signal")
  },
  stop_with("unknown engine ", engine)
)

setcolorder(result, c("gene_symbol", "contrast", "statistic", "log2fc", "p_value", "fdr", "direction", "rank"))
fwrite(result, out_path)
message(sprintf("[%s] wrote %s: %d rows across %d contrast(s)", accession, basename(out_path),
                nrow(result), length(unique(result$contrast))))
