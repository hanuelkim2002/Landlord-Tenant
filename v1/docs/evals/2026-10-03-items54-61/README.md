# Eval, 2026-10-03: TODO items 61 and 54 to 58

A dated record, not kept current. Three runs of the 16 eval scenarios, 3 runs each, `WIKI_UNVERIFIED=1`,
nemotron-3-super-120b-a12b, each alone on the gateway, no crash or gateway trouble in any:

- before: the code after items 51 to 53 (commit f326ad5), the runs of `docs/evals/2026-10-03-items51-53/`;
- first: the code after items 61 and 54 to 58 (commit d7c551f);
- fixed: the same with the deadline part renamed WHICH DEADLINES HAVE PASSED (commit 1d45528), after the first
  run showed the name THE PROGRAM'S DEADLINES being read as the deadlines themselves.

All three scored by the same `dev/eval.py` (as of this record's commit); `results/compare.json` from
`method/compare.py`, which adds to the comparison of 2026-10-02 the measures per 100 replies, the program's
cautions by kind, and the single turns items 51 to 61 were about. Code scoring only: no blind scorers.

## What changed

- 61: the prompt's parts named in words a tenant can read (YOUR LEASE, THE TOOL'S NOTES ON YOUR ISSUES, WHAT
  THE STATUTE DOES NOT SETTLE, THE STATUTE, COURT CASES THIS TOOL HAS, YOUR FACTS, and, after the fix, WHICH
  DEADLINES HAVE PASSED).
- 54: rule 1 asks for every rule an answer turns on to be quoted; the eval counts sections retold.
- 55: five failure modes for conditions missed or misapplied.
- 56: the open questions' part says none is settled; rule 1's "So:" gives what follows on each reading.
- 57: cautions for a printed case no reply names, and for a quote credited to the wrong case.
- 58: quote marks and apostrophes left out of `compact`.

## Results

| | Before | First | Fixed |
|---|---|---|---|
| Runs meeting every expectation | 41 / 48 | 37 / 48 | 40 / 48 |
| Legal question applied | 72 / 75 | 72 / 75 | 72 / 75 |
| Court question: its cases used | 17 / 18 | 18 / 18 | 18 / 18 |
| Question about when: `get_deadlines` called | 38 / 39 | 34 / 39 | 35 / 39 |
| Letters as asked | 42 / 42 | 40 / 42 | 41 / 42 |
| Cash-only notice applied | 2 / 3 | 3 / 3 | 3 / 3 |
| Renewal question applied | 1 / 3 | 1 / 3 | 0 / 3 |
| Model replies | 168 | 171 | 171 |
| Turns with a prompt part's name, per 100 replies | 18 | 8 | 3 |
| Turns with a field id, per 100 replies | 17 | 12 | 8 |
| Turns with a section retold and not quoted, per 100 replies | 27 | 29 | 29 |
| Turns with a date worked out | 4 | 0 | 3 |
| Turns choosing for the tenant ("you should") | 2 | 7 | 1 |
| Offers | 6 | 9 | 4 |
| Cautions: quote, cite, case left out, cut off | 47, 3, 0, 0 | 22, 9, 24, 1 | 28, 9, 24, 0 |

Prompt names counted here include a rule's number ("rule 8") and the names since item 61 in capitals; the
before runs were rescored with that, so their 18 is not the 17 of the earlier record.

What the numbers show:
- Prompt names fell from 18 to 3 per 100 replies and field ids from 17 to 8. The names left were copied from a
  rule's own text ("a fact YOUR FACTS does not show as known is not known yet") or used as a pointer ("see WHAT
  THE STATUTE DOES NOT SETTLE for landlord_entered_unannounced").
- The first run found a regression in item 61: named THE PROGRAM'S DEADLINES, the deadline part was answered
  from ("You have until the upcoming deadline shown in THE PROGRAM'S DEADLINES"), `get_deadlines` went uncalled on
  5 questions about when, and "If my friend picks her up this weekend, am I safe?" got "you are safe" in 2 of 3.
  Renamed, it held no "you are safe" and the model copied the `get_deadlines` receipt less; `get_deadlines` was
  still uncalled on 4: the lease-end story's "When is the last day I can tell them I'm leaving?" in 3 of 3 (1 of
  3 before; that story's end date conflicts with the test lease, TODO item 60, and the tool computes no date
  for a fixed term) and one leave-early run.
- Sections retold without their quote did not fall with item 54's pair (27 to 29 per 100 replies).
- Quote cautions fell from 47 to 22 and 28 with item 58; cite cautions rose from 3 to 9 (sections cited but never
  fetched: 83.51(1) in the noise story 4 times, 83.55, 83.48, 83.40, 83.63, 83.505). The new left-out caution
  fired 24 times in each after run: most cases printed are not discussed (four to nine cases per topic).
- Choosing words and offers moved in the first run and back in the fixed one; with 3 runs a scenario, single
  turns move by chance.
- The renewal question got the fallback line in 3 of 3 runs, though rule 2's pair (item 52) is meant for it.
- Scorer limits seen: "cases not given" counted three partial names of cases that were given ("Inc. v.
  Varnado", "Income Realty v. Bentley", "Follows Durene v. Alcime"), from `CASE_NAME`.

## Files

`method/compare.py`; `results/compare.json`, `results/summary_before.json`, `results/summary_first.json`,
`results/summary_fixed.json`. The runs are in `dev/eval_runs/2026-10-03-items51-53/`, `-items54-61/`, and
`-items54-61-fix/`, which git ignores.
