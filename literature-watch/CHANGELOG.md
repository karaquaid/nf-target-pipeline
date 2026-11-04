# literature-watch changelog

One entry per update run, newest first. A run that found nothing still gets an entry: knowing
the sweep happened and returned nothing is a result.

## Baseline

`literature-watch/data/` has not been created yet. The first run of `NF Literature Monitor`
creates it by copying `phase-1b/data/` verbatim and adding the `first_seen` and
`in_phase1b_snapshot` provenance columns, then merges that month's intake on top.

The frozen snapshot it starts from: 309 candidate rows over 182 target labels from 234 papers,
of which 155 were read in full. See `phase-1b/docs/phase1b-literature-targets.md`.
