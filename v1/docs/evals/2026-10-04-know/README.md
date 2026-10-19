# Eval, 2026-10-04: the tool knows what it knows (TODO items 81 to 85)

A dated record, not kept current. The author's decision of 2026-10-04: the chatbot must be aware of what it knows
and does not know, and of whether that changes what the tenant can do, as a general theme across playbooks, not the
AC that showed it. Items 81 to 84 built it in code (each option's conditions with a knowledge state, a search of the
whole lease, a prompt part of what the tool does not know, options for every playbook); this eval measures it.

## Method

- before: the code before item 81 (commit 6a30473, a git worktree in the session's scratchpad, removed after), all
  23 stories, 3 runs each (`dev/eval_runs/2026-10-04-know-before`).
- after: the code after items 81 to 84 and the eval tooling (commit c71c87b), the same 23 stories, 3 runs each
  (`dev/eval_runs/2026-10-04-know-after`). Not yet in it: the no-break-space fix found by this eval (commit cb46ed1),
  which changes only what the program prints under a reply.
- The 23 stories: the 17 of the last eval, and six new ones, one per knowledge state, each where the deciding point
  is in that state, across five playbooks (`dev/scenarios/eval_know_*.json`): a fact the tenant has not given
  (deposit), lease clauses the profile does not hold but the lease has (lease ending: the holdover, 2.4, and the late
  charge, 3.3), a lease with no such clause (a violation notice over a waterbed), a local code (mold, the lease not
  promising the repair), an open question (a notice ending the lease over a guest, with no chance to cure), and law
  outside the tool (a 3-day notice in Orange County, for which the tool has no court calendar).
- `WIKI_UNVERIFIED=1`, nemotron-3-super-120b-a12b, the two sides run one after the other, each 8 sessions at a time; no
  crash and no gateway trouble on either side. Both sides scored by today's `dev/eval.py` (with `PLAIN`, so a
  no-break space in a reply reads as a space), compared by `method/compare.py` (`results/compare.json`).
- Blind scoring: see below.

## Results, scored by code

| | Before | After |
|---|---|---|
| Runs meeting every expectation, all 23 stories | 51 / 69 | 55 / 69 |
| the six new stories | 8 / 18 | 18 / 18 |
| the 17 older stories | 43 / 51 | 37 / 51 |
| Lease point: `search_lease` called (it did not exist before) | 0 / 9 | 9 / 9 |
| Lease point: the clause found and cited | 3 / 9 | 9 / 9 |
| Point the tool does not know: said as it is (the stories' "must" lines) | 31 / 39 | 39 / 39 |
| Option: whether it is open comes first | 12 / 12 | 10 / 12 |
| Turns saying the lease lacks something, with no search before (a screen) | 24 | 4 |
| Turns with a lease search | 0 | 38 |
| Model replies | 216 | 216 |
| Turns with a prompt part's name / a field id | 8 / 9 | 15 / 17 |
| Turns with a date worked out | 2 | 5 |
| Cautions: quote, cite, case left out | 8, 9, 25 | 19, 10, 16 |

What the numbers show:
- Each new story now meets its expectations in every run. Asked whether the lease says what happens if the tenant
  keeps paying after it ends, or whether it charges a late fee, every answer searches the lease and cites 2.4 and 3.3
  (before: none searched, none cited them, and 2 of 6 answers said the lease does not mention them). Asked about a
  waterbed, every answer searches two wordings and says the tool found nothing on it in the lease's text (before:
  none searched). The mold answers name a code in every run and, asked who can tell, the code enforcement office (a
  code before in 2 of 3, the office in 1 of 3).
- The 4 lease absences left are the screen's false positives: three mold answers repeating what the tenant confirmed
  on the sheet ("your lease does not say the landlord repairs this kind of problem"), and one duplex answer, "The lease
  does not contain a rent-increase clause that the tool has read".
- The older stories' fall, 43 to 37, is in turns known to vary from run to run, about as many on each side and none
  on a knowledge state: `get_deadlines` not called on a question about when (4 turns before, 4 after); the posture
  called gentle (3, 2); the dog story's check against "you are safe" matching "Whether you are safe turns on ..." (1,
  3; the check's own false positive); one late-claim "you will get"; the "other" note (item 42); and one AC run whose
  answers gave the rule's steps (in the sentence of the rule) before whether ending the lease is open.
- Up: prompt parts named, mostly "(WHAT THE STATUTE DOES NOT SETTLE)" written as a source (12 turns, 2 before); field
  ids, spread over the new facts and tool names; quote cautions, partly item 64's known false cautions (a found lease
  clause's words quoted next to a statute cite, checked against the statute: "If Landlord accepts Rent from
  Tenant..." beside 83.58), partly real (the options' own plain words put in quote marks, in the dog story).
- Found by this eval and fixed (commit cb46ed1): a reply wrote "(Lease Section 7.2)" with a narrow no-break space, and
  the program printed neither the clause nor the reading line under it.

## Blind scoring

- The method of `docs/evals/2026-10-03-blind/`: the runs of both sides that reached the chat (63 a side; the two
  stories that stop before the chat have nothing to score) shuffled under one set of codes by `method/blind_mixed.py`
  and grouped into nine batches of whole stories, so the same two scorers judged both sides of a story without being
  told there were two; the program's cautions taken out. New here: each story's context says what its lease holds on
  the chat's points (`LEASE_NOTES`; the scorers cannot open the leases, and GAP_AS_FACT turns on it), the key moved out
  of the scorers' folder while they worked, and the rubric's two new categories, GAP_AS_FACT and UNKNOWN_UNTIED.
- Eighteen scorer agents (Sonnet), two per batch; `method/blind_summary_mixed.py` averages each pair
  (`results/blind_summary.json`). Agreement between the two scorers of a batch: 458 of 736 slips found by both (62%;
  76% on 2026-10-03, with other scorers and without the two new categories, which are judgment calls).

| | Before | After |
|---|---|---|
| Legal answers (scorers' count, averaged) | 153 | 153 |
| Applied well | 30.5 (20%) | 43.5 (28%) |
| Slips, two scorers averaged | 324 | 273 |
| Firm slips (not marked borderline) | 181.5 | 138.5 |

| Category | Before | After | Firm, before | Firm, after |
|---|---|---|---|---|
| UNKNOWN_UNTIED (an unknown not tied to what the tenant can do) | 41.5 | 19.5 | 17 | 7 |
| GAP_AS_FACT (a point the tool does not know stated as a fact) | 30 | 16 | 21.5 | 5.5 |
| CONDITION_MISSED | 29 | 17 | 13.5 | 6.5 |
| RECITED | 29 | 20 | 13.5 | 10 |
| UNCONFIRMED_FACT | 13 | 6 | 11 | 3 |
| OVERCLAIM | 8.5 | 4 | 3 | 0.5 |
| CONDITION_WRONG | 32 | 31.5 | 18.5 | 14 |
| OPEN_CLOSED | 22 | 24.5 | 15.5 | 11 |
| ONE_SIDED | 19 | 22 | 14.5 | 13 |
| LAW_UNSOURCED | 30.5 | 35 | 13.5 | 16 |
| ID (ids, prompt names) | 15.5 | 24.5 | 12.5 | 21.5 |
| CASE_MISREAD, QUOTE_UNMARKED, QUOTES_ONLY, QUOTE_WRONG, OFFER, DATE_MADE, the rest | 54 | 53 | | |

What it means:
- The theme moved: a point the tool does not know stated as a fact fell by half (firm, 21.5 to 5.5), and an unknown
  named without what it changes fell by half (firm, 17 to 7). Facts treated as confirmed when they were not, and
  conditions missed, fell too; the program now lists each condition and what the tool knows of it.
- The firm gaps left on the after side are mostly a lease searched and then misread ("The lease does not state a
  specific late-fee amount; it only mentions late charges in ... Lease Section 3.4", while 3.3 sets $75; "The lease
  does not provide a specific holdover penalty", while 15.1 sets double rent), "the lease does not forbid it" with no
  search (the dog story's letter), and a yes or a date for a period the program could not count.
- Ids and prompt names rose (firm 12.5 to 21.5), as the code's count did: the prompt's parts now point to each other.
- By story, applied well rose most in the entry story (0 to 5 of 9), the holdover story (1 to 4 of 6), and the renewal
  story (1 to 3.5 of 9), and fell in the late claim (5.5 to 1 of 12: printed cases left out or one-sided, conditions
  applied wrong; the gap slips there went from 3 to none).

## Files

`method/compare.py`, `method/blind_mixed.py`, `method/scorer_prompt.md`, `method/blind_summary_mixed.py`;
`results/compare.json`, `results/summary_before.json`, `results/summary_after.json`, `results/blind_summary.json`,
`results/blind_score_B*_*.json` (the eighteen scorers), `results/blind_key.json` (code, side, scenario, run),
`results/batches.json`. The runs and the blind transcripts are in `dev/eval_runs/` (`2026-10-04-know-before`,
`-after`, `-blind`, and the dry run `-dry`), which git ignores. A chart of both scorings was shown in the session.
