#!/usr/bin/env bash
# Build oligo and affxparser from source in a conda R, for the whole-transcript array route.
#
# Why this exists: bioconductor-oligo is absent from bioconda, and Bioconductor's macOS
# binaries link against CRAN's R.framework/libRlapack.dylib, so they will not load under a
# conda R. Two source-level fixes make the build work, both in this folder:
#   Makevars                        endianness macros the Affymetrix Fusion SDK reads
#   oligo-ParserXYS-error.patch     declares and remaps R's error() for R 4.4's R_NO_REMAP
#
# Usage:
#   phase-2/scripts/r-build/build_oligo.sh <conda-env-prefix> <r-library-path>
# Example:
#   phase-2/scripts/r-build/build_oligo.sh ~/.claude-science/conda/envs/nf-phase2 "$PWD/.r-libs/nf-phase2"
#
# The environment needs the compiler toolchain first:
#   clang_osx-arm64 clangxx_osx-arm64 gfortran_osx-arm64 make pkg-config
# Afterwards, point the pipeline at the library with
#   python phase-2/scripts/phase2_ingest.py --rlibs <r-library-path> ...

set -euo pipefail

ENV_PREFIX="${1:?conda env prefix}"
R_LIB="${2:?R library path}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d)"
BIOC_SOURCE="https://bioconductor.org/packages/3.20/bioc"
CRAN="https://cloud.r-project.org"

export R_LIBS_USER="$R_LIB"
export R_MAKEVARS_USER="$HERE/Makevars"
export MAKEFLAGS="-j4"
export PATH="$ENV_PREFIX/bin:$PATH"
mkdir -p "$R_LIB"

echo "[1/4] CRAN dependencies (source builds, so they link against this R)"
"$ENV_PREFIX/bin/Rscript" -e "install.packages(c('ff','foreach','iterators','bit','bit64'), \
  repos='$CRAN', type='source', quiet=TRUE)"

echo "[2/4] affxparser and oligoClasses"
"$ENV_PREFIX/bin/Rscript" -e "install.packages(c('affxparser','oligoClasses'), \
  repos='$BIOC_SOURCE', type='source', quiet=TRUE)"

echo "[3/4] oligo, patched"
cd "$WORK"
"$ENV_PREFIX/bin/Rscript" -e "download.packages('oligo', destdir='.', repos='$BIOC_SOURCE', \
  type='source', quiet=TRUE)" >/dev/null
tar xzf oligo_*.tar.gz
patch -p0 -d oligo/src < "$HERE/oligo-ParserXYS-error.patch" || \
  patch -p1 -d oligo < "$HERE/oligo-ParserXYS-error.patch"
"$ENV_PREFIX/bin/R" CMD INSTALL oligo -l "$R_LIB"

echo "[4/4] platform design package for HTA 2.0 (GSE108524); add others as datasets need them"
"$ENV_PREFIX/bin/Rscript" -e "install.packages('pd.hta.2.0', \
  repos='https://bioconductor.org/packages/3.20/data/annotation', type='source', quiet=TRUE)"

"$ENV_PREFIX/bin/Rscript" -e "suppressMessages(library(oligo)); \
  cat('oligo', as.character(packageVersion('oligo')), 'loads from', .libPaths()[1], '\n')"
rm -rf "$WORK"
