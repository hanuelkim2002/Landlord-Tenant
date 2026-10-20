# Eval, 2026-10-03: TODO items 60, 66, and 65

A dated record, not kept current. Three runs of the 16 eval scenarios, 3 runs each, `WIKI_UNVERIFIED=1`,
nemotron-3-super-120b-a12b, each alone on the gateway, no crash or gateway trouble in any:

- old lease: every story reads `lease.pdf` (commit 1d45528), the "fixed" runs of `docs/evals/2026-10-03-items54-61/`;
- own leases: each story reads its lease from `dev/leases/` (item 60, commit 7ab6708), run from a git worktree at
  that commit so the edits for items 66 and 65 could not reach its sessions;
- after: the same leases with items 66 and 65 (commit 03887f3).

All three scored by the same `dev/eval.py` (as of this record's commit); `results/compare.json` from
`method/compare.py`, which adds to the comparison of `docs/evals/2026-10-03-items54-61/` the deadlines the program
printed, the new caution kind, and whether each question about when got its deadlines printed by either the
model or the program. Code scoring only.

## What changed

- 60: a lease for each story, with its term, rent, deposit, fee, and pet clause (`dev/build_test_leases.py`).
- 66: a caution naming the sections a reply cites with none of their words quoted.
- 65: asked when, a turn without `get_deadlines` gets the deadlines printed by the program.

Neither 66 nor 65 changes what the model reads: the cautions and the program's listing reach the tenant only.
So the model's behavior differs between the own-leases run and the after run by chance alone.

## Results

| | Old lease | Own leases | After |
|---|---|---|---|
| Runs meeting every expectation | 40 / 48 | 37 / 48 | 33 / 48 |
| Legal question applied | 72 / 75 | 71 / 75 | 71 / 75 |
| Question about when: model called `get_deadlines` | 35 / 39 | 36 / 39 | 35 / 39 |
| Question about when: deadlines printed (model or program) | 35 / 39 | 36 / 39 | 39 / 39 |
| Turns with deadlines printed by the program | 0 | 0 | 7 |
| Dog story without "you are safe" | 3 / 3 | 0 / 3 | 2 / 3 |
| Renewal question applied | 0 / 3 | 0 / 3 | 0 / 3 |
| Model replies | 171 | 172 | 170 |
| Turns with a section retold and not quoted | 49 | 47 | 50 |
| Cautions: quote, cite, case left out, section retold, cut off | 28, 9, 24, 0, 0 | 62, 18, 24, 0, 1 | 18, 9, 21, 45, 0 |

What the numbers show:
- Item 65 did what it was for: every question about when got its deadlines, 4 of them printed by the program
  (and 3 more on deposit questions the scenarios do not check: "How long is my landlord supposed to take to give
  my deposit back?"). The model still skips the call on about 1 in 10.
- Item 66's caution fired on 45 replies in 170. It tells the tenant; it does not change the model, which retold
  sections as often as before.
- Runs meeting every expectation moved 37 to 33 with nothing the model reads changed: run-to-run variation of
  about four runs in 48, which every comparison of these evals should be read against. The failures in the after
  run are the model's: the posture called "nicest" or "gentlest" (3 of 3 deposit runs), letter steps, the renewal
  question's fallback line (3 of 3), two not-covered notes.
- With its own lease (a lease from 2024 that went month to month in 2025), the duplex story's replies asked the
  tenant the sheet's own questions in the chat, in quote marks, in 3 of 3 runs (21 of the 62 quote cautions); the
  after run did not. With the no-pets lease the dog story said "you are safe" in 3 of 3, then 1 of 3.
- The model copied the `get_deadlines` receipt into a reply once ("The program printed the tenant's deadlines: 0
  dated, for no issue. You are not shown the dates; ...").

## Files

`method/compare.py`; `results/compare.json`, `results/summary_old_lease.json`, `results/summary_own_leases.json`,
`results/summary_after.json`. The runs are in `dev/eval_runs/2026-10-03-items54-61-fix/`, `-item60/`, and
`-items65-66/`, which git ignores.
