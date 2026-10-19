# Eval, 2026-10-03: TODO items 51 to 53

A dated record, not kept current. The applying code before items 51 to 53 (the "after" runs of
`docs/evals/2026-10-02-apply/`, commit 8f4ae3b) against the code after them (commit f326ad5), 16 scenarios, 3
runs each, `WIKI_UNVERIFIED=1`, nemotron-3-super-120b-a12b. The new runs were alone on the gateway, with no
crash or gateway trouble. Both sides scored by the same `dev/eval.py` (as of this record's commit);
`results/compare.json` from `docs/evals/2026-10-02-apply/method/compare.py`. Code scoring only: no blind
scorers this time.

## What changed between the runs

- 51: `get_deadlines` no longer ends the turn; the model answers the rest of a question after the listing.
- 52: rule 2's fallback line only where no stored sentence, open question, or case topic is on the point.
- 53: ids out of the playbooks' prose and the open questions' prompt view; labels in DEADLINE STATUS; the format
  line forbids the prompt's part names.

## Results

| | Before | After |
|---|---|---|
| Runs meeting every expectation | 31 / 48 | 41 / 48 |
| Legal question: the answer applies the law | 62 / 75 | 72 / 75 |
| A question mixing a deadline with the law ("If I get rid of the dog by Friday, am I safe?") applied | 0 / 3 | 3 / 3 |
| A 3-day notice demanding cash only, applied | 0 / 3 | 2 / 3 |
| "Do I have to sign the renewal by October 15?", applied | 1 / 3 | 1 / 3 |
| Model replies | 128 | 168 |
| Turns with a field id, per 100 replies | 30 | 17 |
| Turns with a prompt name, per 100 replies | 17 | 17 |
| Program cautions, per 100 replies | 38 | 30 |
| Turns with a date the model worked out | 7 | 4 |
| Offers | 3 | 6 |

More replies because a deadline question now gets the listing and an answer after it. Field ids fell; prompt
names did not: the model cites its sources as "(ELEMENT STATUS shows ...)" and "PLAYBOOKS" despite the format
line. The renewal question still gets the fallback line in 2 of 3. The dates worked out are counts like
"Thirty days after June 30, 2026 is July 30, 2026."

## Scorer fixes, applied to every run rescored

`dev/eval.py`: an echo is now a computed deadline the program printed (the listing's "deadline" fields, not the
confirmed dates it also prints), in a reply, unless the same date is also a fact the record holds; the printed
deadlines no longer count as dates the record holds when looking for dates made, since the model never sees
them. Before, a reply naming a confirmed fact's date that the listing also printed counted as an echo, and a
deadline the model counted itself was not caught as made. New measure: prompt names (`PROMPT_NAME`).

## Files

`results/compare.json`, `results/summary_before.json`, `results/summary_after.json`. The runs are in
`dev/eval_runs/2026-10-03-items51-53/`, which git ignores.
