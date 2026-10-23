# Deposit skill test

Does the deposit skill with the gaps filled answer better than the one before it? Gemini, the app's chat model,
answers the twelve deposit stories (`comparisons/skills/stories.json` and `stories_more.json`) three times with each
version, through the app's own chat: the model loads the skill itself, as on the page.

- `versions/old.md`: the skill as committed before 2026-10-22. `versions/new.md`: with the gaps filled and the
  author's changes of 2026-10-23. v1's skill (`../v1/skills/deposit_not_returned.md`) runs unchanged under v2's
  header, as the baseline.
- `python run.py new` (or `old`, `v1`): the answers, into `results/<version>.jsonl`. It reuses the model test's set-up
  (`comparisons/models/`). A story with a `lease` field is read with that variant of `lease.txt`.
- The judge, by meaning, against each story's key: Claude Opus 5.5, blind. `python opus_judge.py pack <folder>` puts
  each story's nine answers in one packet, shuffled under plain labels; six Opus subagents in Claude Code (not an
  API) grade two stories each with the model test's rubric, reading the lease and statutes/; `unpack` maps the
  grades back. `python grade.py --judge opus` scores them (`scores_opus.json`, `SCORES_opus.md`).
- The first judge, kept to compare: `python grade.py` asks the model test's judge (`gpt-oss-120b` on UF, with 83.42,
  83.43, 83.49, 83.491, 83.505); my changes to its grades are in `review.json` (`scores.json`, `SCORES.md`).

## Results (2026-10-23), judged by Opus

Of 30 answers on the ten settled stories: new 27 right, 3 partly, 0 wrong; old 25, 3, 2; v1 19, 4, 7. No empty
answers, no made-up dates, and every answer loaded the skill. Spent about $2.40 on OpenRouter; six answers first
failed with OpenRouter's 402 (credits nearly used up) and were run again.

- Most of the new skill's additions are not tested yet: no story has public housing, a notice sent to the old
  address, or a notice without the amount or the reason. The objection guard shows on story 6: answers that say the
  balance is due on day 30 even after an objection, v1 2 of 3, old 1, new 0.
- Story 6, every version: most answers never say that the certified letter is the notice the statute asks for, so
  the landlord kept its claim (the key's first point); new 1 of 3 does.
- Story 2 (an open call, AUTHOR.md item 3): old said "you cannot demand it yet" flatly in 2 of 3; new limited the "no"
  to the forfeiture ground in 3 of 3.
- Story 11 (college housing): v1 has no such step and said "yes, all of it" three times. Old and new open with a
  conditional yes and ask the one question; one old answer adds a rule not in statutes/ ("general contract law").
- v1 only: twice says "because you mentioned college housing" when the tenant did not; in story 5 it treats the
  15-day return date as due although the landlord made a claim.

## The two judges

gpt-oss (with my review) and Opus disagree on 19 of 108 answers, 10 of them on settled stories. I checked the
disagreements: Opus quotes the words it grades, and where they differ it was right each time I looked (story 2's
openings, v1's 15-day slip, v1's made-up premise). It was more lenient on story 7's "the notice was proper" point,
counting it made when the answer applies the deduction rule; it said so. With gpt-oss: new 23, old 24, v1 19 right.
