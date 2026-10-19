# Eval, 2026-10-12: playbooks become skills (TODO item 116)

A dated record, not kept current. The code before the change (e32ab77: YAML playbooks, the classifier, the sheet, the
options layer, the rules of version G) against the code after it (TODO items 109 to 115: skills the model loads, facts it
proposes and the tenant confirms, no options layer, the rules of version H, the web page only), on the same 26 stories.

## Method

- Runs: `dev/eval.py run <out> 2 --parallel 4` with `WIKI_UNVERIFIED=1`, the 26 stories with an `expect` block, 2 runs
  each, nemotron on the UF gateway, both sides on 2026-10-12. Before: run from the worktree at e32ab77, with its own
  scenarios and driver. After: this copy, whose scenarios carry the old sheet's facts in the story (TODO 115, part 2).
  No gateway trouble and no crash on either side (52 runs each).
- Code scoring: each side's own `dev/eval.py`, its expectations and measures. The two sides' expectations differ where
  the flow differs (the old side expected the stop page for two stories; the new side expects a "no skill" reply and a
  lease search), so "met every expectation" compares roughly, not exactly.
- Blind scoring: `method/blind_mixed.py` shuffled the 100 transcripts that reached the chat (48 before: the two
  stories the old side stops before the chat have no replies; 52 after) under one set of codes, in 13 batches of whole
  stories; two Sonnet scorers per batch (26), each blind to the sides, with `method/scorer_prompt.md` and the rubric
  `dev/eval_rubric.md` as revised on 2026-10-12 (using what the tenant said, asking in the chat for what an answer
  turns on, and offering the next step once are no longer slips; REPEATED, LEASE_PUNTED, ASK_AGAIN, and two ratings are
  new). Each story's context came from the skills (`method/blind_mixed.py`). `method/blind_summary_mixed.py` averaged
  each batch's two scorers. Agreement: 1,070 of 1,552 slips found by either scorer were found by both (69%).
- Limits: the two sides' transcripts look different (a sheet before the chat against confirmations after replies), so a
  scorer could tell them apart; the new side has 64% more replies (the first reply now answers the description, and an
  automatic reply follows each confirmation), so per-reply rates are given beside totals; the scripted chat lines were
  written for the old flow, so a story may ask in turn 2 what the new tool already answered in turn 1, which inflates
  REPEATED on the new side; one scorer (B4_b) read the leave-early story's lease PDF to judge the fee's notice term.

## Results

By code (each side's own eval):

| | Before | After |
|---|---|---|
| Runs that met every expectation | 41 of 52 | 20 of 52 |
| Model replies | 162 | 266 |
| Program cautions (a quote or cite the checks flagged) | 21 | 73 |
| Dates the model wrote that the record does not hold | 3 | 19 |
| Replies reciting (over 300 quoted characters, or facts listed back) | 7 | 34 |
| Lease searches | 34 | 64 |
| "The lease does not mention" with no search | 3 | 0 |

Blind (two scorers averaged; firm = not marked borderline):

| | Before | After |
|---|---|---|
| Transcripts, replies | 48, 162 | 52, 266 |
| Slips, firm slips | 327, 211.5 | 984, 701 |
| Slips per reply, firm per reply | 2.02, 1.31 | 3.70, 2.64 |
| Legal answers applied well | 17 of 123 (13.8%) | 22.5 of 178.5 (12.6%) |
| Rating: helpful (1 to 5) | 2.50 | 2.84 |
| Rating: conversational (1 to 5) | 2.18 | 2.08 |

Firm slips per 100 replies, the largest movements:

| Category | Before | After |
|---|---|---|
| OFFER (not the next step, or made again) | 0.6 | 42.3 |
| REPEATED | 9.0 | 38.2 |
| LAW_UNSOURCED (a rule from memory, or a reading not in the skill) | 13.9 | 34.6 |
| RECITED | 10.8 | 24.8 |
| ASK_AGAIN | 6.5 | 24.6 |
| CONDITION_WRONG | 6.2 | 12.8 |
| CONDITION_MISSED | 8.3 | 12.4 |
| UNCONFIRMED_FACT | 2.8 | 7.5 |
| DATE_MADE | 1.2 | 7.5 |
| OPTION_BEFORE_OPEN | 0.9 | 4.5 |
| CHOICE_MADE | 0.0 | 1.9 |
| LEASE_PUNTED | 7.1 | 2.1 |
| CASE_MISREAD | 6.8 | 3.2 |
| ID | 10.5 | 5.3 |
| QUOTES_ONLY | 3.1 | 0.0 |
| OPEN_CLOSED, GAP_AS_FACT, UNKNOWN_UNTIED, ONE_SIDED | about the same | about the same |

## What it shows

- What the change aimed at, in part: the tool reads the lease itself (searches 34 to 64; sending the tenant to check
  the lease, firm 7.1 to 2.1 per 100 replies; "the lease does not mention" with no search 3 to 0), answers with quotes
  alone almost never, and the blind scorers rated it a little more helpful (2.50 to 2.84).
- What it did not reach: the conversation. Repeated content rose (firm 9.0 to 38.2 per 100 replies) and the
  conversational rating did not move (2.18 to 2.08). A structural cause: the automatic reply after a confirmation
  (TODO 114) is 53 of the new side's 266 replies but carries 46 of its 115 REPEATED slips (0.87 a reply, against 0.32 for
  the others); the program note it answers ("the tenant confirmed ...") leads the model to give its whole answer again.
- What got worse with the guardrail code gone, on this model: law from memory (twice as often), offers in nearly every
  reply, conditions applied wrong or missed, dates the model worked out (3 to 19 by code), an option's steps before
  whether it is open (0.9 to 4.5), and choosing for the tenant (0 to 1.9). The options layer and the fixed answer order
  had been holding these on nemotron, as the eval of 2026-10-04 suggested they did.
- Overall: simpler code (4,477 lines of Python to 3,534; 2,935 lines of playbook YAML to 1,467 lines of skills) and a
  slightly more helpful tool by the blind ratings, but many more slips per reply. Findings go to TODO.md (code-side
  causes) and SLIPS.md (model slips), by their rules.

## Files

`method/`: `blind_mixed.py`, `blind_summary_mixed.py`, `scorer_prompt.md`. `results/`: `blind_key.json`, `batches.json`,
`blind_score_B*_a.json` and `_b.json` (26 scorers), `blind_summary.json`, `code_summary_before.json`,
`code_summary_after.json`. The transcripts and run screens stay in `dev/eval_runs/2026-10-12-skills-*` (not committed:
they quote the test leases).
