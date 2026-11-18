# litmonitor

**What this does.** It reads the published literature on a disease and builds a table of the
molecular targets researchers have proposed for it, with every claim graded by how carefully it
was checked. A claim that someone verified against the full article sits in a different row
category from a claim that only ever appeared in an abstract. Nobody has to take the table on
trust: every row lists the papers behind it.

**Who this page is for.** Someone who has never written code. There is nothing to program. You
will copy lines of text, paste them into a window, and press Enter. If you can follow a recipe,
you can run this.

**What it costs.** A first build of a small disease literature is usually a few dollars of API
usage. A monthly update is well under a dollar. The exact figure for your run is written into a
file called `run.json` so you never have to guess.

**How long it takes.** About 45 minutes the first time, most of it installing things and getting
an account. After that, a monthly run is two commands and a cup of coffee.

---

## Contents

1. [Before you start: three decisions](#1-before-you-start-three-decisions)
2. [Get an API key](#2-get-an-api-key)
3. [Install Python](#3-install-python)
4. [Download litmonitor](#4-download-litmonitor)
5. [Open a command window](#5-open-a-command-window)
6. [Install the two add-ons](#6-install-the-two-add-ons)
7. [Check everything works](#7-check-everything-works)
8. [Write your study file](#8-write-your-study-file)
9. [Do a free test run](#9-do-a-free-test-run)
10. [Do a small paid test run](#10-do-a-small-paid-test-run)
11. [Run the real build](#11-run-the-real-build)
12. [Read your results](#12-read-your-results)
13. [Keep it up to date](#13-keep-it-up-to-date)
14. [When something goes wrong](#14-when-something-goes-wrong)
15. [Words you will see](#15-words-you-will-see)
16. [Reference for people who already code](#16-reference-for-people-who-already-code)

---

## 1. Before you start: three decisions

These shape everything the tool produces, and they are the part only you can do. Write your
answers on paper before touching the computer.

**Which diseases or disease subtypes do you want counted separately?** For example a project on
neurofibromatosis counts NF1, NF2-related schwannomatosis and schwannomatosis as three separate
things, because a target found in one is not automatically relevant to the others.

**Which clinical problems do you want to be able to filter by?** These are called
*manifestations*. For neurofibromatosis they include plexiform neurofibroma, vestibular
schwannoma, pain, optic pathway glioma and so on. Take this list from a standard your field
already uses: diagnostic criteria, a patient registry's categories, a consensus guideline. Do
not invent one. A list you invent cannot be compared with anyone else's, and you will be stuck
with it, because changing it later makes your old counts meaningless.

**Which genes is everybody already studying?** In most inherited conditions, the gene that
causes the disease is so well studied that listing it as a promising new target adds nothing.
Those genes get set aside into a separate column rather than deleted, so you can always look at
them again.

You will also need a handful of PubMed searches, one per disease and clinical problem you care
about. If you already search PubMed for this literature, your existing searches are the right
starting point. Section 8 shows exactly where to type them.

---

## 2. Get an API key

The tool uses Claude to read abstracts and articles. That needs an API key, which is a long
password that lets a program use your account. It is separate from a Claude.ai chat
subscription, and a chat subscription will not work here.

1. Go to **console.anthropic.com** and sign up or sign in.
2. Click **Billing** and add a payment method. New accounts often have free starting credit; if
   yours does, you can skip adding a card until it runs out.
3. While you are in Billing, set a **spend limit** of something like $20. This is your safety
   net. The tool cannot spend more than the limit no matter what goes wrong.
4. Click **API keys**, then **Create key**. Give it a name like `litmonitor`.
5. **Copy the key immediately and paste it somewhere safe**, like a password manager or a note
   on your computer. The website will never show it to you again. It looks like
   `sk-ant-api03-` followed by a long string of characters.

Treat the key like a credit card number. Do not email it, do not put it in a shared document,
and do not paste it into a web page other than the Anthropic console.

---

## 3. Install Python

Python is the language the tool is written in. You do not need to learn any of it. You need
**version 3.11 or newer**.

### On a Mac

1. Go to **python.org/downloads**.
2. Click the big yellow **Download Python 3.x** button. Any version from 3.11 up is fine.
3. Open the file that downloads and click through the installer, accepting the defaults.

### On Windows

1. Go to **python.org/downloads**.
2. Click the big yellow **Download Python 3.x** button.
3. Open the file that downloads. **On the first screen, tick the box that says "Add python.exe
   to PATH" before clicking Install Now.** This matters. If you miss it, the computer will not
   find Python later and you will get a "not recognized" error.
4. Click through the rest of the installer.

---

## 4. Download litmonitor

1. Go to **github.com/karaquaid/nf-target-pipeline**.
2. Click the green **Code** button near the top right.
3. Click **Download ZIP**.
4. Find the downloaded file (usually in your Downloads folder) and double-click it to unzip it.
   You will get a folder called `nf-target-pipeline-main`.
5. **Drag that folder onto your Desktop.** The rest of these instructions assume it is there. If
   you put it somewhere else, that is fine, but you will need to adjust the folder name in the
   first command below.

Inside is a folder called `litmonitor`. That is the tool. The other folders are a
neurofibromatosis project that happens to use it, and you can ignore them.

---

## 5. Open a command window

This is the window where you paste commands. It looks intimidating and is not.

**On a Mac:** press `Cmd` and the space bar together, type `Terminal`, press Enter.

**On Windows:** click Start, type `PowerShell`, press Enter.

Now tell it to work inside the folder you downloaded. Copy the line below, paste it into the
window, and press Enter. Paste with `Cmd+V` on a Mac, or right-click in the window on Windows.

```
cd ~/Desktop/nf-target-pipeline-main
```

Nothing visible happens. That is success. Commands in this tool are quiet when they work.

**A tip that will save you trouble:** from now on, every command in this guide must be run in
this same window, with this folder still selected. If you close the window, open a new one and
run the `cd` line above again before anything else.

---

## 6. Install the two add-ons

The tool needs two free add-on packages: `pandas`, which handles tables, and `matplotlib`, which
draws the figure. Paste this line and press Enter:

```
python3 -m pip install pandas matplotlib
```

On Windows, if that gives an error, use `python` instead of `python3`:

```
python -m pip install pandas matplotlib
```

You will see several lines of text scroll past, ending in something like
`Successfully installed pandas-2.2.0 matplotlib-3.8.0`. This takes a minute or two and only
needs doing once.

Whichever of `python3` or `python` worked for you here is the one to use in every later command.

---

## 7. Check everything works

Before spending any money, make sure the tool runs. Paste this:

```
python3 litmonitor/selftest.py
```

This runs the entire pipeline on four made-up papers that live inside the tool. It uses no
internet, no API key, and no money. It should finish in a few seconds and end with:

```
20 checks, 0 failed
```

**If you see that, your installation is correct** and everything else in this guide will work.
If you see anything else, go to [section 14](#14-when-something-goes-wrong).

---

## 8. Write your study file

Everything about your disease lives in one small text file. Nothing about your disease is in the
code, which is why the same tool works for any condition.

Start from the example. Paste this:

```
cp litmonitor/configs/template.toml mystudy.toml
```

On Windows, use this instead:

```
copy litmonitor\configs\template.toml mystudy.toml
```

Now open `mystudy.toml` to edit it. It is in the `nf-target-pipeline-main` folder on your
Desktop.

**On a Mac:** right-click the file, choose **Open With**, then **TextEdit**. Once it is open, go
to the **Format** menu and click **Make Plain Text** if that option is available. This matters:
if TextEdit saves it as rich text, the tool cannot read it.

**On Windows:** right-click the file, choose **Open with**, then **Notepad**.

The file has comments in it, which are the lines starting with `#`. They explain each part and
are ignored by the tool. Here is what you are changing, in order.

**The study name.** Any short word without spaces. It becomes the name of your output folder.

```
[study]
name = "tsc-example"
description = "Template. Candidate targets in tuberous sclerosis complex."
```

**Your diseases**, from decision one:

```
[labels]
diseases = ["TSC"]
```

**Your clinical problems**, from decision two. Keep the last one as `"Other"`: it is where claims
that fit nothing else go, and the share of rows landing there tells you whether your list is any
good.

```
manifestations = [
  "Subependymal giant cell astrocytoma",
  "Cortical tuber / epilepsy",
  "Renal angiomyolipoma",
  "Other",
]
```

**What counts as a target.** Change the disease name in this sentence to yours and leave the
rest alone:

```
[extraction]
entity = "gene/protein/molecular target that the abstract presents as a disease driver, disease modifier, or therapeutic target in tuberous sclerosis complex"
```

**The genes everybody already studies**, from decision three:

```
[scope]
exclude_labels = ["TSC1", "TSC2"]
```

**Your PubMed searches.** This is the most important part of the file. Each block is one search.
Copy the three-line pattern as many times as you need, once per search:

```
[[queries]]
disease = "TSC"
manifestation = "Renal angiomyolipoma"
query = "(angiomyolipoma[Title/Abstract]) AND (therapeutic target[Title/Abstract] OR inhibitor[Title/Abstract])"
```

The `query` line is ordinary PubMed search syntax. If you are not confident writing one, build it
on the PubMed website first: search there until the results look right, then copy what is in the
search box into the `query` line, between the quotation marks. The `disease` name must exactly
match one you listed under `diseases`, including capital letters.

**Write your searches once and then leave them alone.** If you change a search later, your new
results are no longer comparable to your old ones, because they came from a different question.
When you need more coverage, add a new search rather than editing an existing one.

Save the file and close the editor.

---

## 9. Do a free test run

This checks your searches without spending anything. First, tell the tool who you are, which is
a courtesy the US National Library of Medicine asks of anything that queries it automatically.
Replace the address with your own:

**On a Mac:**

```
export LITMONITOR_CONTACT_EMAIL=you@example.org
```

**On Windows:**

```
$env:LITMONITOR_CONTACT_EMAIL="you@example.org"
```

Now the test run:

```
python3 litmonitor/build.py --config mystudy.toml --dry-run
```

It searches PubMed, counts what each of your searches returns, and stops before doing anything
that costs money. You will see something like:

```
study tsc-example | 3 queries | 509 unique records
dry run: search only, no model calls. Per-query yield in tsc-watch/data/run.json
```

**Read that number before going further.** It is the single best check on your searches.

- A few hundred to a couple of thousand records is healthy.
- Zero records means a search has a typo, or is too narrow.
- Tens of thousands means a search is too broad and will be expensive. Tighten it.

To see which individual search is responsible, open the `run.json` file the message names. It
lists every search with its own count.

---

## 10. Do a small paid test run

Now give the tool your API key and let it process twenty papers, so you can check the quality
before paying for the whole corpus.

Paste your key in place of `sk-ant-...` below. Keep the quotation marks on Windows.

**On a Mac:**

```
export ANTHROPIC_API_KEY=sk-ant-...
```

**On Windows:**

```
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

Then:

```
python3 litmonitor/build.py --config mystudy.toml --limit 20
```

This takes a few minutes and costs a few cents. It prints its progress as it goes.

When it finishes, open the folder named after your study (`tsc-watch` in the example), then
`data`, and open `targets.csv` by double-clicking it. It will open in Excel or Numbers.

**Spend five minutes checking it.** Pick three rows. For each one, copy the number in the
`supporting_pmids` column, paste it into the PubMed search box, and read the abstract. Ask
yourself whether the gene in that row really is presented as a target for that disease and that
clinical problem. If two or three rows look wrong in the same way, your `entity` sentence in the
study file probably needs to be more specific. Fix it and run this step again.

**Note the keys you set are temporary.** If you close the command window, you must paste the two
`export` or `$env:` lines again next time. That is deliberate: it keeps your key out of files
where it could leak.

---

## 11. Run the real build

When the sample looks right:

```
python3 litmonitor/build.py --config mystudy.toml --annotate --overwrite
```

`--annotate` adds a useful extra pass that marks which targets look like measurements of
disease rather than things you could actually drug. `--overwrite` tells it to replace the small
test run you just did.

This is the long step. A few hundred papers takes roughly half an hour, and the window will
print progress as it works. Leave it alone until it finishes. If your computer goes to sleep the
run stops, so plug it in and disable sleep first.

Then run these three, one at a time. Each takes seconds:

```
python3 litmonitor/review.py --config mystudy.toml --stamp 2026-11
python3 litmonitor/report.py --config mystudy.toml
python3 litmonitor/figure.py --config mystudy.toml
```

Change `2026-11` to the current year and month.

The first is a safety check. It re-reads a sample of the articles independently to see whether
it reaches the same conclusions, and it checks every number in the write-up against the actual
tables. It prints a list of checks with `pass`, `warn`, `skip` or `FAIL`. Warnings and skips are
normal on a first build; a `FAIL` means something is wrong and the message says what.

The second writes the summary document. The third draws the figure.

---

## 12. Read your results

Everything is in your study folder, in two subfolders. The `.csv` files open in Excel or Numbers
by double-clicking. The `.md` file is plain text: open it in TextEdit, Notepad, or paste it into
a Word document.

| File | What it is |
|---|---|
| `docs/<study>-target-map.md` | **Start here.** The written summary: how many targets, how well verified, where the literature is thin, what the list cannot tell you |
| `docs/figures/<study>-coverage.png` | The same thing as a picture: how many targets per clinical problem, shaded by how well verified |
| `data/candidates.csv` | **The main table.** One row per target, disease and clinical problem, excluding the genes you set aside |
| `data/targets.csv` | The same but including the set-aside genes, each marked in the `excluded_label` column |
| `data/references.csv` | Every paper used, with whether the full article could be read |
| `data/coverage.csv` | A simple count of rows per clinical problem |
| `data/retrieval-queue.csv` | Papers that could not be read in full, most useful first |
| `data/run.json` | What the run did, including what it cost in tokens |

**The columns that matter most in `candidates.csv`:**

- `gene_target` is the gene or protein.
- `disease` and `manifestation` are your own labels.
- `evidence_tier` is the one to sort by. `full text - supported` means the complete article was
  read and it genuinely supports this claim. `full text - partial` means the article supports
  the target but for a different problem than this row claims. `abstract only` means nobody has
  read the full article, so the claim is unchecked rather than weak.
- `n_supporting_papers` is how many papers back the row. One paper is a claim, not a finding.
- `mechanism` is a short phrase describing what the target does, and `mechanism_source` says
  whether that came from the full article or only the abstract.
- `supporting_pmids` lets you check any row yourself: paste a number into PubMed.

**What to do with `retrieval-queue.csv`.** Some articles are not free to read, so nobody checked
them. This file lists them with the most valuable first, meaning the ones that would confirm the
most currently unchecked rows. If you have access through a university library, working down the
first ten or twenty entries improves the map more than anything else you can do by hand.

**The honest limitation**, which the summary document also states: every verdict comes from one
reader working once. The review step measures whether that reader is consistent with itself, not
whether it is right. Treat the map as a well-organised reading list with its uncertainty marked,
not as an oracle.

---

## 13. Keep it up to date

Once a month, open the command window, run the `cd` line from section 5, set your key again as
in section 10, then:

```
python3 litmonitor/monitor.py --config mystudy.toml --since 2026-11-01 --merge
python3 litmonitor/review.py --config mystudy.toml --stamp 2026-12
python3 litmonitor/report.py --config mystudy.toml
python3 litmonitor/figure.py --config mystudy.toml
```

Set `--since` to the date of your last run. The update only looks at papers added since then, so
it is quick and cheap. It adds new rows and can promote an existing row when new evidence
verifies it. It never silently downgrades a row you already verified, so the map stays
comparable with its own earlier versions.

A month with no new papers is a real result, not a failure. The tool says so and stops.

---

## 14. When something goes wrong

Error messages look alarming and almost always mean something small. Find yours below.

**`command not found: python3`** (Mac) or **`'python' is not recognized`** (Windows)

Python is not installed, or on Windows it was installed without the PATH box ticked. Reinstall
from python.org and tick **Add python.exe to PATH** on the first screen. On a Mac, try `python`
instead of `python3`.

**`No such file or directory`** or **`cannot find the path specified`**

The command window is not looking at the right folder. Run the `cd` line from section 5 again.
On Windows, remember that folder separators are backslashes: `litmonitor\build.py`.

**`No module named pandas`** or **`No module named matplotlib`**

Section 6 did not finish. Run it again and watch for `Successfully installed`.

**`ANTHROPIC_API_KEY is not set`**

You did not paste the key in this window, or you closed and reopened the window since. Paste the
`export` or `$env:` line from section 10 again.

**`anthropic 401`** or anything mentioning `authentication_error`

The key is wrong. A common cause is copying it with a space on the end, or copying only part of
it. Create a fresh key in the console and paste it again.

**Anything mentioning `credit balance`**

Your account has no money on it. Add a payment method under Billing.

**`labels.manifestations should include a catch-all 'Other'`**

Your study file needs `"Other"` as the last item in the manifestations list. Add it.

**`queries[2] disease 'tsc' is not in labels.diseases`**

A search names a disease that is spelled differently from your `diseases` list. Capital letters
count. The number in brackets tells you which search: it counts from zero, so `queries[2]` is
the third one.

**`already holds 6 tables; pass --overwrite`**

You have built this study before. Add `--overwrite` to rebuild it from scratch, or use
`monitor.py` from section 13 to add only what is new.

**`HTTP Error 429`**

You are querying PubMed too fast, usually because another copy of the tool is running at the
same time. Wait a minute and run it again. Setting `LITMONITOR_CONTACT_EMAIL` as in section 9
also raises your allowance.

**The run stopped in the middle**

Nothing is broken. Run the same command again with `--overwrite` added. Finished work is written
only at the end, so a half-finished run leaves no bad data behind.

**Still stuck?** Open an issue at
**github.com/karaquaid/nf-target-pipeline/issues** and include three things: the exact command
you ran, the last ten lines the window printed, and your `mystudy.toml` file with the API key
removed. Those three make the problem solvable by someone who cannot see your screen.

---

## 15. Words you will see

**API key.** A long password that lets a program use your Anthropic account. Different from a
Claude.ai subscription.

**Abstract.** The summary at the top of a paper, free to everyone. **Full text** is the complete
article, often behind a paywall. The whole point of this tool is keeping track of which one a
claim was checked against.

**PMID.** The identity number PubMed gives every paper. Paste one into PubMed to find the paper.

**Command window, Terminal, PowerShell.** The same idea on different systems: a window where you
type instructions instead of clicking.

**TOML.** The format of your study file. It is plain text with one setting per line.

**CSV.** A plain-text table that opens in Excel or Numbers.

**Token.** The unit the API bills in, roughly three quarters of a word. `run.json` records how
many your run used.

---

## 16. Reference for people who already code

Requires Python 3.11 or newer (`tomllib`), plus `pandas` and `matplotlib`. No other
dependencies; PubMed and Europe PMC are called directly over HTTP and no connector or framework
is involved.

```
python litmonitor/selftest.py                                   # offline, 20 assertions
python litmonitor/build.py   --config study.toml --dry-run      # per-query yield only
python litmonitor/build.py   --config study.toml --limit 20     # smoke test
python litmonitor/build.py   --config study.toml --annotate --overwrite
python litmonitor/monitor.py --config study.toml --since YYYY-MM-DD --merge
python litmonitor/review.py  --config study.toml --stamp YYYY-MM [--offline]
python litmonitor/report.py  --config study.toml [--out PATH]
python litmonitor/figure.py  --config study.toml [--out PATH] [--dpi N]
```

Environment: `ANTHROPIC_API_KEY` (required for anything but `--dry-run` and `selftest.py`),
`LITMONITOR_CONTACT_EMAIL` (optional, raises NCBI rate limits), `NF_MONITOR_MODEL` (optional,
pins a model id; otherwise the newest Opus or Sonnet is resolved at runtime, because a hardcoded
id silently routes to a retired model).

**How a build differs from an update.** `build.py` aggregates claims across papers into one row
per target, disease and manifestation, carrying every supporting PMID, per-verdict counts, and
the best verdict as the row's tier. `monitor.py` appends to an existing corpus and never
downgrades a verified row.

**The review gate** (`review.py`) has three layers and exits non-zero on failure. A git-checked
guard that directories declared frozen in the config are untouched. Deterministic invariants:
baseline rows byte-identical, no verified row downgraded, labels inside the config vocabulary,
paper counts matching the PMID lists, every supporting PMID present in the references, the
candidate list equal to what the derivation rule produces. Then a model-based second reader that
re-judges a sample of verdicts and fails above a third disagreement, and checks every number in
the generated prose against a digest computed from the tables. Checks a study cannot support,
such as baseline comparisons for a first build, are skipped with a note rather than failed.

**Automation.** `.github/workflows/literature-monitor.yml` runs either mode on a schedule or on
manual dispatch, runs the self-test first and the gate last, and opens a draft pull request
whenever the gate is not clean. Set `ANTHROPIC_API_KEY` as a repository secret. Note that pushing
a workflow file requires a token with GitHub's separate Workflows permission.

**An agent version** exists for Claude Science users who want to design a config conversationally
rather than edit TOML: see `literature-watch/agents/literature-target-map/`. It runs these same
scripts and follows the same rules.
