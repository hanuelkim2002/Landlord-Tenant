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

## Second run (2026-10-24): stories 13 to 18 on Sonnet

The six stories for what the skill gained on 2026-10-22, run with the app's chat model since 2026-10-23, Claude
Sonnet 5.5 from Anthropic (`python run.py new --model sonnet --stories 13-18`, answers in `results/sonnet/`), three
runs per version, graded blind by three Opus subagents (`scores_opus_sonnet.json`, `SCORES_opus_sonnet.md`). About
$4.80 at list prices; no errors, no empty answers, the skill loaded every time.

Right of 18: new 11 (3 wrong), old 2 (11 wrong), v1 3 (8 wrong).

- The new parts work where the old skill fails: public housing (13) new 3 of 3, old and v1 0, which call the
  housing authority question open; no reason (17) new 2 of 3, old and v1 0, which give two readings; an objection
  (18) new 3 of 3, old 0 (it calls the $650 overdue), v1 3.
- The Section 8 voucher (14) is right nowhere: every answer, all versions, opens "Probably yes" before giving both
  readings, so it does not choose neither. The judge's call; read as a mere hedge, most would be right.
- The old address (15) and no amount (16): the usual miss, all versions, is the landlord's date for the balance
  under the reading where the letter counts.
- Three answers (v1 2, new 1) say the tenant called it college housing; the tenant never did.
- The judge is Opus grading Sonnet answers, one model family; all three versions share that.

## Third run (2026-10-24): the four fixes, on the stories that missed

`versions/fixed.md` is the new skill with three fixes (no lean on a point that is not settled; a proper notice named
as such; both option 2 dates under a reading where a letter counts), and `chat.py` no longer calls every tenant one
in college housing. Stories 6, 8, and 14 to 17 ran three times on Sonnet (`run.py fixed --model sonnet --stories
6,8,14-17`), graded blind by three Opus subagents (`SCORES_opus_sonnet_fixed.md`). $1.40.

Right of 18: fixed 16 (2 wrong); the new skill on the same stories had 8 (7 partly, 3 wrong). No answer leaned
"probably", none invented a college-housing premise, every answer led with the answer. Stories 6 and 8 ran on
Gemini before and Sonnet now, so part of their change may be the model. The 2 wrong are story 14: the answer
narrowed 83.49(4) to a program that sets the deposit amount, dropping the rent; the skill's own reading says only
"the amount". The stories that were right before were not rerun.

Then (`versions/fixed2.md`) the Section 8 reading names both the rent and the deposit; story 14 rerun on Sonnet, 3 of
3 right (`SCORES_opus_sonnet_fixed2.md`), $0.14.

## Fourth run (2026-10-24): all 18 stories on Sonnet with the current skill

`run.py fixed2 --model sonnet`, three runs per story, graded blind by six Opus subagents (`SCORES_opus_sonnet_fixed2.md`).
$4.04; no errors, no empty answers, the skill loaded every time, every answer led with the answer.

Right of 48 settled answers: 37 (3 partly, 8 wrong). Stories 13 to 18 ran on Sonnet both times: 11 right before the
fixes, 15 now. Stories 1 to 12 ran on Gemini with the new skill before (27 of 30) and on Sonnet with the fixed skill now
(22 of 30), so that drop mixes the model and the skill; this run cannot say which.

- Still 3 of 3: stories 1, 3, 4, 6, 10, 13 to 16.
- Story 8 (e-mail notice), 0 of 3: every answer adds that 83.505(1) asks the addendum to say e-mail is voluntary and can
  be revoked, and `lease_email.txt` does not say whether it does. The judge read that as treating the notice as open;
  an earlier judge did not. The story's lease leaves the point out, not the answer.
- New Sonnet slips: the 15-day return applied after a claim (story 5, 2 of 3); receipt as the test for the landlord's
  30 days (story 9); a made-up result under 83.491 (story 12); "ordinary wear" asked as if it were the rule (story 7).
- A lean outside the points marked not settled: "Probably yes" on the college question (story 11), and "Yes, the
  30-day deadline has passed" after an objection (story 18).
- Story 17, 1 of 3: two answers add "even if the letter counted, at least $650 is owed". This judge counted that as
  two readings; the judge of the third run did not count the same thing. A judge call, not settled here.
