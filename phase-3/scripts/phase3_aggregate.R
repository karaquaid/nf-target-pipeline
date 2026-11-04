#!/usr/bin/env Rscript
# Phase 3, step 3: rank-based meta-analysis across datasets, one stratum at a time.
#
# Method: Robust Rank Aggregation (Kolde, Laur, Adler, Vilo 2012, Bioinformatics
# 28(4):573-580), as implemented in the RobustRankAggreg package. RRA was chosen
# because it is built for exactly the situation this launch set is in: several
# rankings of different lengths over partly overlapping item sets, with no
# requirement that the underlying scores be on a common scale.
#
# How the "not measured is not a low rank" rule is honoured. RRA scores a gene by
# comparing its normalized ranks against what k independent uniform draws would
# look like, taking the best-supported order statistic and correcting for having
# taken the best. In RobustRankAggreg::betaScores the beta parameters are set from
# n = sum(!is.na(r)) and the ranks are sorted with na.last = TRUE, and
# rhoScores corrects with k = the same non-missing count. So a gene that a dataset
# never measured is passed in as NA and that dataset simply does not appear in the
# gene's test, which is the behaviour the project plan requires. Verified by
# reading the installed package source, not assumed.
#
# Inputs   <build>/rank-long.csv.gz  from phase3_rank_matrix.py
# Output   <build>/rra-scores.csv.gz  comparison_class, direction, gene_symbol,
#                                     n_datasets, rho, rho_fdr, best_rank, median_rank

suppressPackageStartupMessages({
  library(RobustRankAggreg)
  library(data.table)
})

args <- commandArgs(trailingOnly = TRUE)
build <- if (length(args) >= 1) args[[1]] else stop("usage: phase3_aggregate.R <build-dir>")

cat(sprintf("RobustRankAggreg %s\n", as.character(packageVersion("RobustRankAggreg"))))

rl <- fread(file.path(build, "rank-long.csv.gz"))
stopifnot(all(c("comparison_class", "direction", "accession", "gene_symbol", "norm_rank") %in% names(rl)))

out <- list()
for (cls in sort(unique(rl$comparison_class))) {
  for (dir in c("up", "down")) {
    sub <- rl[comparison_class == cls & direction == dir]
    datasets <- sort(unique(sub$accession))
    if (length(datasets) < 2L) {
      cat(sprintf("skip %-42s %-4s  only %d dataset, no aggregation possible\n",
                  cls, dir, length(datasets)))
      next
    }

    # Gene by dataset matrix of normalized ranks. A cell is NA when that dataset
    # did not measure that gene; dcast leaves it NA, which is what RRA needs.
    wide <- dcast(sub, gene_symbol ~ accession, value.var = "norm_rank")
    genes <- wide$gene_symbol
    rmat <- as.matrix(wide[, ..datasets])
    rownames(rmat) <- genes

    res <- aggregateRanks(rmat = rmat, method = "RRA", full = FALSE)
    res <- as.data.table(res)
    setnames(res, c("Name", "Score"), c("gene_symbol", "rho"))

    nmeas <- rowSums(!is.na(rmat))
    best <- apply(rmat, 1, min, na.rm = TRUE)
    med <- apply(rmat, 1, median, na.rm = TRUE)
    info <- data.table(gene_symbol = genes, n_datasets = as.integer(nmeas),
                       best_rank = best, median_rank = med)
    res <- merge(res, info, by = "gene_symbol")

    # rho is already corrected for taking the best order statistic within a gene.
    # BH then controls the false discovery rate across the genes of this stratum.
    res[, rho_fdr := p.adjust(rho, method = "BH")]
    res[, `:=`(comparison_class = cls, direction = dir, n_datasets_in_class = length(datasets))]
    out[[paste(cls, dir)]] <- res

    cat(sprintf("%-42s %-4s  %6d genes over %d datasets, %6d at rho_fdr < 0.05\n",
                cls, dir, nrow(res), length(datasets), sum(res$rho_fdr < 0.05)))
  }
}

all <- rbindlist(out)
setcolorder(all, c("comparison_class", "direction", "gene_symbol", "n_datasets",
                   "n_datasets_in_class", "rho", "rho_fdr", "best_rank", "median_rank"))
setorder(all, comparison_class, direction, rho)
fwrite(all, file.path(build, "rra-scores.csv.gz"))
cat(sprintf("\nwrote %s with %d rows\n", file.path(build, "rra-scores.csv.gz"), nrow(all)))
