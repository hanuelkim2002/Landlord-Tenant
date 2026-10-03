# Eval, 2026-10-02: the tool applying the law (TODO items 46 to 50)

A dated record, not kept current. The runner is `dev/eval.py`; the scenarios are `dev/scenarios/eval_*.json`;
the rubric is `dev/eval_rubric.md` as of commit 8f4ae3b and the scorer fixes below.

## What was asked

The author decided that the tool applies the stored statute and cases to the tenant's confirmed facts (README,
Purpose) and asked for TODO items 46 to 50: the playbooks' open questions with readings and failure modes as
application slips (50), rules version G (46), the cases' words to the model (47), case pages' facts (48), and
an eval for applied answers (49).

## Method

- Old code ("base": commit 29df5d7, the plan change with the organizing code, in a git worktree) against new
  code ("after": commit 8f4ae3b), 16 scenarios, 3 runs each per side, both sides at the same time, 6
  sessions each, `WIKI_UNVERIFIED=1`, nemotron-3-super-120b-a12b. No crash, no gateway trouble on either side.
- Code scoring by the expectations of 2026-10-02 (`dev/eval.py score`; `method/compare.py`). A legal question
  expects `applied` (a quote and 40 or more words of the model's own, addressed to the tenant), a court
  question `cases_used`, the noise story's open points their readings. Three scorer fixes after the first
  read of the results, applied to both sides: the test lease's own dates count as known (the dates-made
  measure flagged the lease's 2027 term end); the noise story's pattern takes "not settled" and "readings" as
  well as "does not settle"; a court question answered from cases `get_cases` gave earlier in the chat counts
  (the model now calls it when a topic is on the point, rule 8), and a case name with a leading "In" is
  matched without it.
- Blind scoring of the after side only (the base side's answers are quotes by design): 42 transcripts that
  reached the chat, under shuffled codes (`method/blind.py`), eight scorer agents, four batches of two, with
  `dev/eval_rubric.md` (`method/scorer_prompt.md`); the scorers could open `statutes/`. Agreement: 235 of 305
  slips found by both scorers of a batch (77%).
- A sample for the author: `dev/eval_runs/2026-10-02-apply-after/author_sample/` (six transcripts, their
  contexts, and a scoring sheet), not committed because the transcripts quote the test lease.

## Results, code-scored (`results/compare_base_after.json`)

| Expectation | Before | After |
|---|---|---|
| Runs meeting every expectation | 6 / 48 | 31 / 48 |
| Legal question: the answer applies the law | 0 / 75 | 62 / 75 |
| Open point: its readings given | 0 / 6 | 6 / 6 |
| Court question: cases got / used in the answer | 18 / 18, 0 / 18 | 18 / 18, 18 / 18 |
| Deadline question: `get_deadlines` called | 37 / 39 | 37 / 39 |
| Deadlines computed | 13 / 15 | 15 / 15 |
| Letters as asked | 40 / 42 | 41 / 42 |
| Not-covered stop or note right | 46 / 48 | 46 / 48 |
| Forbidden words absent | 33 / 33 | 29 / 33 |
| Quotes-only replies | 72 | 0 |
| Program cautions (quote or cite), turns with ids, dates made | 6, 5, 0 | 48, 39, 4 |

The 13 legal questions not applied: 6 ended at `get_deadlines`, which still ends the turn, on questions that
mix a deadline with the law ("If I get rid of the dog by Friday, am I safe?" 3 of 3); 6 got the fallback line
where an open question or a case is on the point (a cash-only 3-day notice, 3 of 3, though the notice-form open
question and Moskowitz v. Aslam speak to it; "Do I have to sign the renewal by October 15?" 2 of 3); 1 restated
the rule without quote marks. Forbidden words: "nicest" or "gentlest" for a posture (2), federal law named for a
religion question (1), "you should" (1).

## Results, blind-scored (`results/blind_summary.json`; after side, two scorers averaged)

21.5 of 101.5 legal answers were applied well (the rule quoted, the facts, each condition, what follows, and
no slip in the applying categories). 270 slips in 128 replies, 192.5 firm:

| Category | All | Firm |
|---|---|---|
| ID (field ids, "ELEMENT STATUS", "PLAYBOOKS", open question ids) | 48 | 46 |
| LAW_UNSOURCED (a rule restated without its quote) | 42 | 34.5 |
| CONDITION_WRONG | 28 | 15.5 |
| OPEN_CLOSED | 19.5 | 11.5 |
| CASE_MISREAD | 16.5 | 11.5 |
| CONDITION_MISSED | 16.5 | 10.5 |
| QUOTE_UNMARKED | 15 | 10 |
| UNCONFIRMED_FACT | 14 | 6.5 |
| QUOTE_WRONG | 13 | 10.5 |
| ONE_SIDED | 12.5 | 9 |
| DATE_MADE | 12.5 | 11 |
| POSTURE_OWN_WORDS | 11 | 4.5 |
| QUOTES_ONLY, LETTER_ORDER, OVERCLAIM, CONFIRM_IN_CHAT, OFFER | 6, 4, 4, 3.5, 2 | 0.5, 2, 4, 3, 0 |

What the scorers saw, by story:
- Mold: all three runs leaned on the cases that help the tenant (Bennett, Mansur, Paterson, Smith) and left out
  Solomon v. Gentry, Haynes v. Lloyd, and Menendez from the same result, which went for the landlord; one
  credited Paterson's words to Bennett and read Mansur's gas explosion as a repair failure.
- Entry: every run settled the open question on an air-conditioning filter change as "repair"; two said
  83.53(1) forbids the tenant to change the locks.
- Late claim: deposit cases applied with no word on how alike the facts are; one run counted 30 days from the
  move-out itself ("2026-07-30"), another "about 52 days".
- Cash-only 3-day notice: the registry requirement given without the motion to determine rent the same
  sentence of 83.60(2) offers.
- Dog notice: "the landlord can end the lease" with no word that the 7-day cure period had not run.
- Lease end: 83.575(3)'s extra month without its second condition (no 83.57(3) notice).
- Rent notice: the steps 83.56(5)(a) lists after partial rent treated as settled or as conditions on filing.
- Rent hike: the scenario's rent and the test lease's $1,850 conflict, so some replies called the increase a
  decrease. Late claim: the story says a $1,000 deposit, the lease $1,850, and the tool reads the lease first.
  These are faults of the test data (every scenario uses the same test lease), not of the model.

## What it means

Applying works where it did not exist: every court question now ends with the cases set beside the facts, the
open points come with their readings, and no answer is a bare list of quotes. The answers are not yet right
often enough: about one legal answer in five passes the scorers whole. The largest causes are structural and
fixable in code or rules (ids leaking from the prompt and the playbooks' own prose, `get_deadlines` ending the
turn, the fallback line used where an open question applies, nested quote marks tripping the quote check), then
the model's own reading (conditions, open points closed, cases one-sided). TODO items 51 to 60.

## Files

`method/`: `blind.py` (blind transcripts and the author's sample), `scorer_prompt.md`, `blind_summary.py`,
`compare.py`. `results/`: `compare_base_after.json`, `summary_base.json`, `summary_after.json`,
`blind_score_*.json` (the eight scorers), `blind_key.json`, `blind_summary.json`. The runs (screens,
transcripts, each run's record) are in `dev/eval_runs/2026-10-02-apply-base/` and `-after/`, which git ignores.
