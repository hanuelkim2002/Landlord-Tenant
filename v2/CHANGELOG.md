# Changelog

## 2026-10-19: v2 starts

v1 moved into `../v1/` with `git mv` (its CLAUDE.md renamed CLAUDE_v1.md). `v2/` made with v1's 40 statute files and
`index.json`, `.env.example`, `.streamlit/config.toml`, the starting prompt (`V2_PROMPT.md`), README.md, and CLAUDE.md.
The top level keeps a short README.md and CLAUDE.md, and the preview runs v2's page. Replaces v1 as the working version.

## 2026-10-19: the lease intake test

`comparisons/lease/`: the shortlist of methods (SHORTLIST.md), four made-up test leases (short, 46 pages, scanned,
broken text) built by `make_leases.py`, and 64 questions with their answers (`answer_key.json`), checked against the
leases by `check_key.py`. Nothing replaced; no method is built yet.

## 2026-10-19: lease answers judged by meaning

The answer key now lists the points a right answer must make and the mistakes that make it wrong, judged by meaning
by a second model (`gpt-oss-120b`), not by exact phrases. Only quotations are checked word for word. Two "not covered"
questions were replaced with cleaner ones. Replaces the key's `must_say` phrases and the model's "covered" flag.

## 2026-10-19: v1's lease method as a baseline

The lease comparison adds v1's own method (PyPDF2, the four-clause form, the exact-phrase search), run unedited from
`v1/` and scored like the three new methods, so the scores show the change from v1. Nothing replaced.

## 2026-10-19: intake time as its own metric

The lease comparison times each method's intake (PDF to ready for the first question, all its steps, the middle of
three runs) apart from its answer time per question. Replaces the README's single "time" line.

## 2026-10-19: the lease comparison, run and scored

Step 1 (four PDF readers, Gemma 4 for pages without text) and the three methods plus v1, 64 questions each, scored by
a judge that now sees the whole lease, with my review of its grades (`review.json`). Results in `SCORES.md`. The
prototypes in `prototypes/` stay until the author chooses. Replaces nothing in the app.

## 2026-10-19: lease method A chosen

The author chose method A (the whole lease in the prompt). The prototype code is deleted (in git at 784dd82). README:
five tools, no `search_lease`. AUTHOR.md and SLIPS.md started with the comparison's findings. Draft lease-reading
rules await the author's OK. Replaces the open lease question and the planned `search_lease`.

## 2026-10-19: lease-reading rules approved

Rules 1 to 4 for reading the lease are approved and in README.md, for the system prompt; rule 5 waits on AUTHOR.md
item 1. Replaces the draft in `comparisons/lease/README.md`.

## 2026-10-19: the skills test

`comparisons/skills/`: the shortlist of skill formats (an element checklist, worked examples, a short core with a
details file) with v1's skill as the baseline; a test lease; five deposit stories with an answer key whose quotes and
dates `check_key.py` checks against `statutes/`. Nothing replaced; no skill is written yet.
