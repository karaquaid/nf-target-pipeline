# literature-watch

The living half of the NF literature target map.

`phase-1b/` is frozen: it is the snapshot the manuscript cites, and it stays byte-identical so
a reader can reproduce the published numbers. This directory is where everything that arrives
after that snapshot goes. The two are deliberately separate, so "the published list" and "the
current list" are never the same file with different contents on different days.

| Path | What it holds |
|---|---|
| `data/` | The running tables: the frozen snapshot plus every update merged in. Same schema as `phase-1b/data/`, plus two provenance columns. |
| `docs/` | The regenerated write-up and figure, describing the running tables. |
| `updates/<YYYY-MM>/` | One directory per run: new rows, new papers, and the run report. |
| `agents/nf-literature-monitor/` | The agent that does the work, and the protocol it follows. |
| `CHANGELOG.md` | One entry per run, newest first, including runs that found nothing. |

Two columns in `data/` separate the published list from everything after it:

- `first_seen`: `phase-1b snapshot` for baseline rows, `YYYY-MM` for rows added by a run.
- `in_phase1b_snapshot`: true for baseline rows, false for added ones.

So `phase1b-candidate-targets.csv` filtered to `in_phase1b_snapshot` reproduces the published
table exactly, and the unfiltered file is the current state. Cite the frozen copy in papers;
use this one to decide what to work on.

## Running an update

Pick `NF Literature Monitor` from the session config and say `run the monthly update`. It
loads the `nf-literature-monthly` skill, which is the protocol, and opens a pull request with
the deltas. It will not write to `phase-1b/`, change the vocabulary or scope rules, merge its
own pull requests, or edit derived tables by hand.

The analysis scripts are not duplicated here. The monitor runs the committed ones from
`phase-1b/scripts/` with path flags:

    python phase-1b/scripts/make_phase1b_candidates.py --data literature-watch/data

A script that needs fixing is fixed in `phase-1b/scripts/` as its own pull request, never
forked into this folder. That is the one case where a change touches the frozen phase, and it
is a code change, not a data change.

## Setting it up elsewhere

See `agents/nf-literature-monitor/README.md`. Everything needed to recreate the agent and its
protocol in another workspace is in that directory.
