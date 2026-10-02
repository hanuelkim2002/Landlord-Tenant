# Eval, 2026-10-01: the eval runner, five harness and rules changes, cases, and stories no playbook covers

A dated record, not kept current. The runner is `dev/eval.py`; the scenarios are `dev/scenarios/eval_*.json`.

## What was asked

The author asked for: an eval runner; changes 2, 3, 5, 8, and 9 from the list of tweaks (printing tools end
the model's turn; the program prints "does not decide" under a quote; no false cautions for ids and "e.g."
examples; rules that load only when they can apply; "Not:" / "Instead:" pairs from real slips); runs of each
playbook with realistic stories from tenants who know no law; runs where nothing fits a playbook; and a check
that a tenant whose facts are like a case can get that case.

## Method

- 16 scenarios, each with an `expect` block scored by code: one per playbook (a graduate whose landlord went
  silent, a carpet charge, maintenance walking in during a shower, a renewal deadline, a notice taped to the
  door, a friend's dog, a rent hike after a roof complaint, mold in an apartment, leaving early for a sick
  parent), three stories no playbook covers (a roommate, noisy neighbors, a towed car), one covered problem
  next to an uncovered one (a broken heater and a remark about the tenant's religion), and three with facts
  like a case in the wiki (a late claim letter, a cash-only three-day notice, a violation notice after a
  complaint to the city). `method/make_scenarios.py` wrote them.
- Old code ("base", commit 555a18d, in a git worktree) against new code ("after", commit 8acda0d's runtime
  code), 3 runs per scenario per side, `WIKI_UNVERIFIED=1`, nemotron-3-super-120b-a12b.
- Code scoring: `dev/eval.py score` (expected results, tools per turn, required and forbidden words, case
  topics, cautions, empty turns). `method/compare.py` groups the expectations by kind.
- Blind scoring: the 77 transcripts that reached the chat, under shuffled codes (`method/blind.py`), scored
  by eight agents (four batches, two independent scorers each) with `method/rubric_eval.md`, the rules trial's
  rubric plus CASE_APPLIED. Scorer agreement: 48 of 50 slips found by both scorers of a batch. The scorers
  could not open `statutes/`, so QUOTE_WRONG rests on the program's own quote check more than on them.

## The gateway failure

The first after-runs (`results/summary_after_gateway_failure.json`) hit eight minutes (19:44 to 19:52) in
which nearly every call to the gateway came back empty, then timed out: 12 crashes and 30 empty turns, all in
that window, and 18 of 48 runs lost. The baseline had run before it. A probe (`method/ab_first_turn.py`) gave
the new code normal answers afterwards. Both sides were run again at the same time (base2, after2), 6
sessions each, with no gateway trouble. Since then `dev/eval.py` marks such runs `gateway_trouble` and
`reply_empty` events log the gateway's `finish_reason`.

## Results, base2 against after2 (run at the same time)

Code-scored (`results/compare_base2_after2.json`):

| Expectation | Before | After |
|---|---|---|
| Runs meeting every expectation | 32 / 48 | 37 / 48 |
| Legality question: "does not decide" shown | 49 / 57 | 55 / 56 |
| Time question in plain words ("How long do I have ...") calls `get_deadlines` | 2 / 9 | 8 / 9 |
| "What are my deadlines?" calls `get_deadlines` | 27 / 27 | 26 / 26 |
| Deadlines computed where expected | 10 / 15 | 15 / 15 |
| Letter asked for: drafted | 17 / 21 | 20 / 21 |
| No letter when none asked for | 15 / 15 | 15 / 15 |
| Court question: `get_cases` on a right topic | 36 / 36 | 33 / 36 |
| Not-covered stop or note right | 45 / 48 | 44 / 48 |
| Forbidden words absent | 129 / 129 | 124 / 126 |
| Program cautions, empty turns, deadline echoes, ids in replies | 2, 2, 1, 4 | 2, 3, 0, 1 |
| Model replies (fewer: printing tools now end the turn) | 155 | 99 |
| "Does not decide" lines the program added | 0 | 18 |

Blind-scored slips (two scorers averaged; "firm" leaves out those a scorer marked borderline):

| Category | Before | After | Before, firm | After, firm |
|---|---|---|---|---|
| LAW | 10.5 | 9 | 3.5 | 3.5 |
| LETTER_ORDER | 9 | 6.5 | 7 | 3 |
| QUOTE_UNMARKED | 3 | 1 | 1 | 0 |
| QUOTE_WRONG | 2 | 2 | 1 | 2 |
| POSTURE_OWN_WORDS | 1 | 2 | 1 | 1 |
| CONFIRM_IN_CHAT, UNCONFIRMED | 0 | 1, 1 | 0 | 1, 0 |
| DEADLINE_REPEAT (minor) | 1 | 0 | 1 | 0 |
| Per run (39 and 38 runs), DEADLINE_REPEAT aside | 0.65 | 0.59 | | |

Most LAW calls on both sides are one sentence, "The lease and statute text I have do not answer that.", to a
legal question the playbook does not list as open (TODO item 40). Per reply the after side looks worse only
because it has a third fewer replies: the easy ones ("The deadlines appear above.") are gone.

The after side's misses, read one by one: a topic sent with its case count, "(9)" (now accepted,
`tools.topic_named`); one court question answered with a statute quote; a classifier that called a partial
payment a separate uncovered problem in all three rent-notice runs (fixed, c448481); "the gentlest option"
for preserve twice; one legality answer with only a lease quote and no line (the program's line now covers
lease quotes, ddcac0f).

## Cases

Every plain question about courts ("Has this happened to other people? Did a judge ever ...") that reached
`get_cases` got a topic whose cases include the one with facts like the tenant's: Casey v. Picinich and
Durene v. Alcime for a late claim letter, Moskowitz v. Aslam for a cash-only notice, Stanley v. Quest for
paying rent into the court, Salmonte v. Eilertson for retaliation, Olen v. Moss and Wilson v. Terwillinger
for an early termination fee. 17 of 18 runs before, 16 of 18 after. No reply named, retold, or applied a case
(CASE_APPLIED: 0 on both sides). Cases appear only when the tenant asks; the model is never asked to say a
case supports the tenant (TODO item 36).

## Not covered

The roommate, noise, and towing stories stopped before the chat in every run (one after-run crashed first and
passed on its retry). The mixed story got no "may not be covered" note before the classify change (0 of 6
runs), and 2 of 3 after it; the third crashed at intake on both attempts. The cause: the classifier's reason
quoted the story's two lines with a raw line break inside a JSON string, which Python's strict parser refuses
("Invalid control character"), the same crash as the first attempts of all three after-runs; `ask_json` now
parses with `strict=False` (2163ef0). The religion question got "The lease and statute text I have do not
answer that." in every run, which the scorers marked borderline LAW under the rubric's literal rule, and no
federal law was cited from memory.

## Confirmation run (after3: the code with the follow-ups)

The follow-ups made after reading after2: `ask_json` asks again on malformed JSON; quote marks pair in order;
rule 6 writes posture lines after their name only; `reply_empty` logs `finish_reason`; classify treats details
of a covered situation as part of it; `get_cases` takes a topic with its count; the "does not decide" line
also goes under lease quotes. (The `strict=False` JSON fix came after this run.) One more run, 16 x 3, alone
on the gateway, with no gateway trouble and no crash or retry (`results/summary_after3.json`,
`results/compare_base2_after2_after3.json`):

| Expectation | Before (base2) | After (after2) | Final (after3) |
|---|---|---|---|
| Runs meeting every expectation | 32 / 48 | 37 / 48 | 39 / 48 |
| Legality question: "does not decide" shown | 49 / 57 | 55 / 56 | 55 / 57 |
| Time question in plain words calls `get_deadlines` | 2 / 9 | 8 / 9 | 6 / 9 |
| "What are my deadlines?" calls `get_deadlines` | 27 / 27 | 26 / 26 | 25 / 27 |
| Deadlines computed where expected | 10 / 15 | 15 / 15 | 12 / 15 |
| Letter asked for: drafted | 17 / 21 | 20 / 21 | 15 / 21 |
| Court question: `get_cases` on a right topic | 36 / 36 | 33 / 36 | 36 / 36 |
| Not-covered stop or note right | 45 / 48 | 44 / 48 | 46 / 48 |
| Forbidden words absent | 129 / 129 | 124 / 126 | 129 / 129 |
| Crashes, program cautions, empty turns | 0, 2, 2 | 1, 2, 3 | 0, 0, 1 |

Read with the run-to-run spread in mind (3 runs a scenario). The letter misses in after3 are the model asking
again for what the tenant already gave ("You said $900, is that correct?"), which the scripted tenant cannot
answer, so the letter never comes (TODO item 39); the posture lines themselves came out in the new form. The
classify change put the not-covered note on the mixed story in 3 of 3 runs, and still on 2 of 3 rent-notice
runs, where a partial payment was read as a separate problem (TODO item 42).

## Files

`method/`: the scenario generator, the blind-transcript script, the comparison script, the rubric, the
scorer prompt, the first-turn probe. `results/`: per-side summaries, the comparison, the eight scorers' JSON,
and the key from codes to sides. The runs themselves (screens, transcripts, each run's record) are in
`dev/eval_runs/2026-10-01/`, which git ignores.
