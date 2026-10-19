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
