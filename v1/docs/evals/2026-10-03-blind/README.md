# Blind scoring, 2026-10-03: the applying code of 2026-10-02 against today's

A dated record, not kept current. The question code scoring cannot answer: since the first blind scoring
(`docs/evals/2026-10-02-apply/`), did the answers get more right on the law?

## Method

- Two sides, mixed: "old", the runs blind-scored on 2026-10-02 (`dev/eval_runs/2026-10-02-apply-after`, commit
  8f4ae3b, every story on `lease.pdf`), and "new", today's last runs (`dev/eval_runs/2026-10-03-items65-66`,
  commit 03887f3, items 50 to 66, each story on its own lease). 42 transcripts each, the runs that reached the chat.
- `method/blind_mixed.py` shuffled all 84 under one set of codes and grouped them by scenario into eight batches
  (whole scenarios, packed under a size cap), so the same two scorers judged both sides of a scenario without
  being told there were two. The program's caution lines were taken out of every transcript (the new side has
  kinds of caution the old has not, which would point the scorers to the slips they name), and the label of
  deadlines the program printed by itself was made the same as any printed deadlines. Each scenario's context
  (its story, chat lines, open questions with readings, posture lines) is built from today's scenarios and
  playbooks for both sides.
- Sixteen scorer agents, two per batch, with today's rubric (`dev/eval_rubric.md`) and the scorer prompt of
  2026-10-02 plus a note that cautions were taken out (`method/scorer_prompt.md`); they could open `statutes/`
  but not the leases. `method/blind_summary_mixed.py` averages each pair and splits by side.
- Consistency check: the old side, scored again today, came out as it did on 2026-10-02 (21 of 103 legal
  answers applied well, 270.5 slips, 192 firm; then 21.5 of 101.5, 270, 192.5). Agreement between the two
  scorers of a batch: 446 of 587 slips found by both (76%; 77% on 2026-10-02).

## Results (`results/blind_summary.json`)

| | Old (2026-10-02) | New (2026-10-03) |
|---|---|---|
| Model replies | 128 | 170 |
| Legal answers | 103 | 115 |
| Applied well (rule quoted, facts, each condition, what follows, no applying slip) | 21 (20%) | 36 (31%) |
| Slips, two scorers averaged | 270.5 | 246 |
| Firm slips (not marked borderline) | 192 | 141 |
| Slips per legal answer | 2.6 | 2.1 |

| Category | Old | New | Firm, old | Firm, new |
|---|---|---|---|---|
| LAW_UNSOURCED (a rule restated without its quote) | 44.5 | 46.5 | 32 | 30.5 |
| ID (ids, prompt part names) | 46 | 20.5 | 45 | 16.5 |
| CONDITION_WRONG | 31.5 | 30.5 | 14.5 | 13 |
| QUOTE_UNMARKED | 19 | 26 | 14.5 | 14 |
| UNCONFIRMED_FACT | 13.5 | 21.5 | 7 | 7 |
| OPEN_CLOSED | 19.5 | 15 | 12 | 7.5 |
| CASE_MISREAD | 16 | 17.5 | 12.5 | 9.5 |
| CONDITION_MISSED | 19.5 | 13.5 | 16 | 6.5 |
| DATE_MADE | 14 | 13 | 12 | 12 |
| ONE_SIDED | 11 | 13.5 | 6 | 8 |
| QUOTE_WRONG | 13.5 | 5.5 | 11.5 | 5 |
| POSTURE_OWN_WORDS, OVERCLAIM, LETTER_ORDER, CONFIRM_IN_CHAT, QUOTES_ONLY | 6, 4, 3, 3, 5.5 | 3.5, 5, 5, 5, 2.5 | | |

Applied well by scenario (old, then new, of the legal answers): cash-only notice 0 of 9, 3.5 of 9.5; carpet
claim 1 of 5, 5 of 9; ghosted deposit 3 of 6, 6 of 6; taped notice 2 of 7, 5 of 9; leaving early 2 of 9, 4 of
12; lease end 0 of 7, 2 of 7.5; late claim 5.5 of 12, 2 of 12; retaliation 3 of 6, 1.5 of 6; the others within
one answer of each other.

## What it means

- More answers are right whole: 31% against 20%, with fewer firm slips on more replies. The largest falls are
  ids and prompt names (items 53 and 61), quotes wrong (item 58's checks do not reach the model, so this is the
  model quoting better), conditions missed (item 55's failure modes) and open questions closed (item 56).
- What did not move: rules restated without their quote (item 54's pair; item 66 now tells the tenant),
  conditions applied wrong, dates worked out, and cases misread or one-sided (item 57's cautions reach the
  tenant, not the model). Facts not confirmed and quotes without marks rose, mostly borderline.
- Two scenarios went down: the late claim (Plakhov v. Serova left out or misread, days counted) and retaliation
  (83.64(1)'s examples read as the only protected acts).
- The new side differs by every change from item 50 to 66 and by its leases (item 60); this scoring cannot say
  which change did what. Scorers noticed that one scenario's transcripts quoted two different leases, so the
  two sides were not perfectly hidden; they were not told which was which.

## Files

`method/blind_mixed.py`, `method/scorer_prompt.md`, `method/blind_summary_mixed.py`; `results/blind_summary.json`,
`results/blind_score_B*_*.json` (the sixteen scorers), `results/blind_key.json` (code, side, scenario, run),
`results/batches.json`. The blind transcripts are in `dev/eval_runs/2026-10-03-blind/`, which git ignores.
