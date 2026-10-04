# Eval, 2026-10-04: options before steps, and cite instead of recite (TODO items 72 and 73)

A dated record, not kept current. The author's decision of 2026-10-04, after trying the web page with a real
lease: a reply laid out how to end the lease over an AC not repaired before saying whether that was open at all,
and replies recited sections, lease clauses, and the tenant's own facts.

## Method

- before: the code before the change (commit 03887f3), the runs of `docs/evals/2026-10-03-items60-66/`
  (`dev/eval_runs/2026-10-03-items65-66`), 16 stories, 3 runs each, rescored with today's `dev/eval.py`.
- AC story before: the new story `eval_repair_ac_terminate` (the author's run, made general), 3 runs on the same
  old code from a git worktree (`dev/eval_runs/2026-10-04-ac-before`), the worktree moved to the Trash after.
- after: the code after items 72 and 73 (commit c5b3ad8), all 17 stories, 3 runs each
  (`dev/eval_runs/2026-10-04-after`). Like for like, the after figures below leave out the new story unless they
  are about it.
- `WIKI_UNVERIFIED=1`, nemotron-3-super-120b-a12b, each run alone on the gateway, no crash or gateway trouble.
  Code scoring only (`method/compare.py`, `results/compare.json`).
- New in `dev/eval.py`: `recited` (more than 300 characters in quote marks, or three lines of "You confirmed" or
  "You said"), `applied` taking a cite as well as a quote, and the expectation `open_first` (outside quote marks,
  whether an option is open comes before the first step toward it).

## Results

| | Before | After |
|---|---|---|
| Runs meeting every expectation (the 16 stories) | 34 / 48 | 42 / 48 |
| Model replies | 170 | 171 |
| Turns reciting | 104 (61 per 100 replies) | 5 (3 per 100) |
| AC story, "How do I end my lease because of this?": open or not first | 0 / 3 | 3 / 3 |
| AC story, "Can I just stop paying rent instead?": open or not first | 0 / 3 | 3 / 3 |
| Legal question applied (the 16 stories) | 72 / 75 | 72 / 75 |
| Question about when: model called `get_deadlines` | 35 / 39 | 37 / 39 (40 / 42 with the AC story) |
| Turns with a date worked out | 4 | 0 |
| Offers | 5 | 2 |
| Turns with a field id | 10 | 17 |
| Turns with a prompt name | 6 | 7 |
| Cautions: quote, cite, case left out, section retold | 18, 9, 21, 45 | 10, 8, 21, 0 |

What the numbers show:
- Recitation is nearly gone, and with it the quote cautions it set off. The cited words are printed under each
  reply by the program instead.
- In the AC story, before, each answer to "How do I end my lease" opened by pasting all of 83.56(1), steps
  included, then listed the tenant's facts back; whether ending the lease was open came 1,500 to 4,300
  characters later. After, every answer opens with "Whether you can end the lease over this is not settled", and
  why, from the program's options status, then the rule in a plain sentence with its cite.
- The AC story's "Is the AC part of my lease?" answers were short and failed "applied" in 3 of 3 (no "you"
  addressed); one named a prompt part ("see YOUR LEASE") and wrote its own disclaimer line. Each said the lease
  does not mention air conditioning, which the tool cannot know: the model sees only the 15 lease details the
  profile holds, and none is a repairs or maintenance clause.
- Field ids rose (10 to 17 turns): mostly the lease profile's own field names, `notice_before_vacating` and
  `term_end`, used as a lease cite where the clause has no section number.
- The renewal question was applied in 1 of 3 (0 of 3 before), still mostly the fallback line.

## Files

`method/compare.py`; `results/compare.json`, `results/summary_before.json`, `results/summary_ac_before.json`,
`results/summary_after.json`. The runs are in `dev/eval_runs/`, which git ignores.
