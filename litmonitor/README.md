# litmonitor

Build a verification-graded map of candidate drug targets for a disease from the literature,
then keep it current. Two commands do the two jobs: `build.py` for the first full map,
`monitor.py` for the monthly increment.

It needs Python, `pandas`, and an Anthropic API key. It does not need this repository, a GitHub
account, or Claude Science. PubMed and Europe PMC are called directly over HTTP.

## Quickstart on your own disease

    cp litmonitor/configs/template.toml mystudy.toml    # then edit it
    export ANTHROPIC_API_KEY=sk-...
    export LITMONITOR_CONTACT_EMAIL=you@example.org     # optional, NCBI asks for one

    python litmonitor/selftest.py                              # proves the install works, no key needed
    python litmonitor/build.py --config mystudy.toml --dry-run  # how many papers, per query
    python litmonitor/build.py --config mystudy.toml --limit 20 # smoke test on 20 papers
    python litmonitor/build.py --config mystudy.toml --annotate # the real build
    python litmonitor/review.py --config mystudy.toml --stamp 2026-11
    python litmonitor/report.py --config mystudy.toml
    python litmonitor/figure.py --config mystudy.toml

Dry-run first, always. It costs nothing and tells you whether your queries are the right shape:
a query returning thousands of records is too broad, one returning nothing is malformed.

Thereafter, monthly:

    python litmonitor/monitor.py --config mystudy.toml --since 2026-11-01 --merge
    python litmonitor/review.py  --config mystudy.toml --stamp 2026-12

## What it produces

| File | Contents |
|---|---|
| `data/targets.csv` | Every row: one per target, disease and manifestation, with its evidence tier, supporting papers, verdict counts and mechanism |
| `data/candidates.csv` | The prioritisation input: the audit table minus the scope exclusions |
| `data/references.csv` | One row per paper: access route, preprint status, what it supports |
| `data/coverage.csv` | Rows per manifestation and disease |
| `data/retrieval-queue.csv` | Papers nobody could read, ranked by how many unverified rows a copy would anchor |
| `data/annotations.csv` | Per-label flags, with `--annotate` |
| `data/run.json` | Build log: per-query yield, token counts, model used |
| `docs/<study>-target-map.md` | The write-up, every number recomputed from the tables |

**Evidence tiers are the product.** `full text - supported` means someone read the whole article
and it says what the abstract implied. `full text - partial` means the article supports the
target but for a different manifestation or disease. `abstract only` means nobody has checked,
which is different from weak evidence and is kept visibly different.

## The config is the whole study

Everything disease-specific lives in one TOML file: disease labels, manifestation vocabulary,
what counts as a target, scope exclusions, output paths, query bank. The code has no disease
knowledge in it. `configs/nf.toml` is the worked example behind the neurofibromatosis map in
this repository; `configs/template.toml` is a commented starting point on a different disease.

Three decisions determine most of the quality, and all three happen before any paper is read.

**The manifestation vocabulary.** Take it from a standard your field already uses: diagnostic
criteria, a registry phenotype list, a consensus guideline. A vocabulary invented for a single
analysis cannot be compared with anyone else's. Keep a catch-all `Other` and watch its share;
the write-up reports it, because a large `Other` means the vocabulary does not fit.

**The query bank.** Write it once and leave it alone. A changed query changes what the corpus
means, so counts stop being comparable between runs. Add a query rather than editing one. Keep
it in the config: in this project the original bank survived only in a chat transcript and had
to be recovered from it, which is the kind of gap that makes a sweep unreproducible.

**The scope exclusions.** `exclude_labels` is for entities everyone already knows about, usually
the germline disease genes. They stay in the audit table with a flag, so an exclusion is
reversible and countable rather than a deletion.

## The review gate

`review.py` is what makes an unattended run trustworthy. Three layers, cheapest first, exit code
1 on failure, `--offline` for the two that need no model:

1. **Frozen-path guard.** Directories your config declares frozen must be untouched, checked
   against git rather than taken on trust.
2. **Deterministic invariants.** Baseline rows still byte-identical, no verified row downgraded,
   every label inside your vocabulary, paper counts matching the pmid lists, every supporting
   pmid present in the references, the candidate list equal to what the derivation rule produces.
3. **Second reader.** Re-judges a random sample of verdicts against the same article bodies and
   measures disagreement, failing above a third, then checks every number in the generated prose
   against a digest computed from the tables.

Layer 3 measures whether a verdict is reproducible, not whether it is right. That is the honest
limit of a single-reader design, and the reason a high disagreement rate should send a run to a
person rather than into your tables. Checks your study cannot support, because it has no baseline
or no annotations, are skipped with a note rather than failed.

## Testing

`python litmonitor/selftest.py` runs the entire pipeline on stub sources with no network and no
API key: four fixture papers, two of which support the same row so aggregation is exercised, one
excluded label, and one paper with no retrievable body. It asserts 20 properties of the result,
including that a row's tier is the best verdict across its papers, that an excluded label stays
in the audit table and out of the candidate list, that the coverage matrix totals the candidate
rows, that the unreadable paper lands in the retrieval queue, and that the figure plots every
row the table holds. Run it after any change.

## Cost

The expensive step is reading article bodies, not searching. For the NF study, a monthly run is
around 0.3M input tokens; a first build is larger in proportion to the corpus. Token counts per
run are written to `run.json`, so you can measure rather than estimate. Check current API rates
for what that converts to.

Do not economise on the verdict step. A fabricated mechanism from a weaker model is the failure
mode this entire design exists to prevent, and it costs more to find later than the model saved.

## Running it inside Claude Science

Two agent profiles cover the same protocol conversationally, for designing a config or arguing
about vocabulary with a person in the loop: the build is `literature-target-map`, the monthly
refresh is `nf-literature-monthly`. Both produce the same tables and follow the same rules.
Bundles to recreate them are in `literature-watch/agents/`.
