# Each skill's test

One small test per new skill (`docs/superpowers/specs/2026-10-28-other-skills-design.md`): about 6 to 8 stories with
answer keys the author approves first, 3 runs each on the app's chat model (Claude Sonnet 5.5 from Anthropic), v1's
skill run beside the new one as the baseline, graded blind by Claude Opus 5.5 subagents in Claude Code.

## The files

- `run.py`, `judge.py`, `grade.py`: one runner, packer, and scorer for every skill.
- `spans.py`: finds the time spans in answers ("more than three weeks", "several days", "for weeks") and sorts each:
  the tenant's words, a count code would give, or the model's own counting.
- `<skill>/stories.json`: the stories and their keys, in the deposit stories' shape, plus `sections` (the statute
  sections the graders read) and, on a story, `lease` (a lease file in that folder; none means
  `comparisons/skills/lease.txt`) and `open: true` (a key that turns on an open call; not counted as settled).
- `<skill>/versions/<name>.md`: a frozen copy of the skill, when a run needs one (after a round of fixes).
- `<skill>/results/`: the answers (`<version>.jsonl`) and the graders' grades (`judge_opus_<version>.json`).
- `<skill>/SCORES.md`, `<skill>/scores.json`: written by `grade.py`.
- `<skill>/results/round1/`: an earlier round's answers, grades, scores, and `review.json`, set aside when the keys
  changed, since `grade.py` scores every answer file in `results/`.
- `<skill>/results/spans/`, `<skill>/results/rule7/`: side tests, each with its own answers, grades, and scores. Run
  in `results/dry/` (the folder `--dry` reads), then renamed, so the main scores stay as they were.

## Running a test

From this folder, with `ANTHROPIC_API_KEY` in the environment:

1. Check the keys: `python ../skills/check_key.py <skill>/stories.json`. It must end "OK".
2. Try it with a fake model: `python run.py <skill> new --stories 1-2 --dry` (into `results/dry/`; delete after).
3. Run both versions: `python run.py <skill> new` and `python run.py <skill> v1`. Each line holds the answer, the
   tools called, the skills loaded, the cost, and the page's quote checks.
4. Pack for the graders: `python judge.py pack <skill> <folder>`. Each story becomes one packet, its answers shuffled
   under plain labels; `key.json` maps them back.
5. Grade: Opus subagents, two or three packets each, with the instructions below.
6. `python judge.py unpack <skill> <folder>`, then `python grade.py <skill>`.

## The graders' instructions

Each grader gets this, with its packets:

    Read each packet (JSON). It holds the rubric, the story (the tenant's facts and message, the right answer, the
    points a right answer must make, and the mistakes that make one wrong), the lease file, the statute files, and
    the answers under plain labels. Read the lease file and every statute file it names (paths from v2/). Grade every
    answer by the rubric: judge meaning, not wording; count as an error any claim the statute, the lease, or the facts
    contradict, and any rule stated without support in them. Write one file, grades-<n>.json, in the packets' folder:
    {"<label>": {"answers_first": ..., "points_made": [...], "mistakes_made": [...], "other_error": "...",
    "reason": "one sentence, quoting the answer's words the grade turns on"}, ...}. You cannot tell which version wrote
    an answer, and it does not matter. Tool calls are not in the packets, and code checks the dates: do not count a date
    as not from count_days unless the date itself is wrong.

An answer is right when it makes every point with no mistake and no other error; partly when it makes some points
and no error; wrong otherwise (`comparisons/models/score.py`, `story_verdict`).

A point written wholly in parentheses is helpful detail, not required, as the rubric says. The repair test's graders
still required such points, so `grade.py` counts only the required ones. My changes to a grader's verdict, each with
its reason, go in `<skill>/review.json`. `SCORES.md` keeps the graders' own reading beside both.

## Results

### repair_not_made (2026-10-28)

Seven stories, 3 runs each, the new skill against v1's, on Sonnet 5.5; three Opus graders, blind
(`repair_not_made/results/round1/SCORES.md`). About $4.10; no errors, no empty answers, no made-up dates.

Right of 21: new 15 (2 partly, 4 wrong), v1 5 (5 partly, 11 wrong). Every point required: new 14, v1 1.

- The new skill is right in every run of stories 1, 2, 4, 5, and 6. v1 leans "You probably can" on the hot-water
  question (story 2, 3 of 3), misses the good-cause limit on retaliation (story 6), and states rules the statute does
  not have in 8 of 21 answers; the new skill does that once.
- Story 3, new 3 of 3 wrong. Each answer works out a time span itself ("about a month" for 13 days; "the 7 days would
  probably not be over by May 1"), which v1 does too (2 of 3): a model slip, in SLIPS.md. The graders also counted
  "I've noted that as a pending fact for you to confirm" as asking the college question (2 of 3), which I read as the
  page's usual confirming, not a question: a judge's call. And the shared skill's check gets a box of its own where
  the skill asks for one line: the shared skill's.
- Story 7, new 2 partly and 1 wrong. The key ties the two readings of when the lease ended to whether the tenant's
  ending of the lease holds; most answers, both versions, rest the same two readings, dates, and outcomes on the
  deposit law's wording instead. The test's, or a judge's call: counted that way, two new answers and one v1 answer
  move up. One new answer leaves out that the timely move-out notice kept the landlord's duty to send its notice.
- The skill loaded in 20 of 21 new answers (story 6 once read 83.64 itself) and the shared skill only in story 3,
  the one story without `school_housing`.

One round of fixes (the author's calls): the shared skill keeps the college check to one line inside another point,
and story 7's key accepts either ground for its two readings. Stories 3 and 7 rerun on the new skill as `fixed` (the
repair skill unchanged, the shared skill fixed), one Opus grader, blind; $0.80.

- Story 7: right 3 of 3 (new was 0 of 3 under the narrower key; the first round was not regraded under the new key).
- Story 3: right 1 of 3. The other two say the leak has lasted "about a month" again; this grader did not count it,
  the first round's did, so `review.json` counts it, for one standard. One answer kept the college check to a line;
  two still gave it a box of their own, as the reply rules' example heading ("Does Florida's deposit law cover you?")
  invites. None asked the college question.

### repair_not_made, rerun on the new keys (2026-10-28)

Nine stories under the keys with the author's 25 answers. `keys2` (the skill as of the attorney-fees line, frozen in
`versions/`) ran all nine; v1 ran fresh on stories 1, 4, 5, 8, 9 (new facts, or never run), and its first-round
answers to 2, 3, 6, 7 were regraded. Three Opus graders, blind, three stories each (`repair_not_made/SCORES.md`).
About $4.05; no errors, no empty answers, no made-up dates; both skills loaded in every answer.

Right of 27: keys2 19 (1 partly, 7 wrong), v1 12 (1 partly, 14 wrong). Every point required: keys2 11, v1 4.

- Stories 8 and 9, amenities the skill never names (a bed frame, covered parking): keys2 right 2 of 3 in each, v1 0
  of 6. v1 twice gives the 83.56(1)(b) rent cut for the landlord's own repaving, and states rules the statute lacks.
- Story 2, 0 of 3 in both: every keys2 answer makes every point, then counts the outage itself ("more than three
  weeks"), a mistake in the new key. Story 3: keys2 2 right, 1 partly; the "about a month" slip is gone.
- Story 7, keys2 1 of 3: two answers give both readings of when the lease ended, then say the deposit comes out the
  same under both. v1's first-round answers do it too (2 of 3).
- The packets left out 83.57; all six story-6 answers cite 83.57(3) right, from the stored text. Told so, the grader
  dropped those flags. Told also that any other error fails an answer, it moved four narrow wordings it called
  harmless here to its reason (story 4 once, story 5 three times) and one hedged line (story 6). Counted as errors:
  keys2 16, v1 10 (AUTHOR.md 18).

### Time spans the model counts itself: five ways side by side (2026-10-28)

The model says how long something has lasted from its own counting ("more than three weeks", "about a month" for 13
days), against rule 7. Five versions on repair stories 1, 2, 3, 7, 9, 3 runs each, the keys2 skill in all; each
built in its own worktree by a Sonnet agent, run live, then graded blind by five Opus graders, one story each, told
to leave spans to `spans.py` (`repair_not_made/results/spans/`, `SPANS.txt`). About $5.96 for the 60 new answers.

| Version | Change (branch) | Model-counted span | Any span | Right |
|---|---|---|---|---|
| keys2 | none (the rerun's answers, regraded) | 3 of 15 | 8 | 13 |
| v1rule | v1's date rule as rule 7 (`spans-v1rule`) | 1 | 5 | 13 |
| ruleA | rule 7 adds: no span unless in the tenant's words (`spans-ruleA`) | 1 | 2 | 12 |
| codeB | today and a day count beside each date fact (`spans-codeB`) | 5 | 12 | 12 |
| codeBA | both (`spans-codeBA`) | 3 | 4 | 14 |

- Code's counts made it worse: the model writes about time more and misapplies the count ("more than 9 weeks" for a
  leak that ended at move-out, 26 days in), or rounds it ("a month" for 23 days). Rule-only versions cut spans most.
- ruleA's one slip is "for weeks" (13 days), v1rule's "about a month" (13 days). Right answers are within noise
  (12 to 14); every version's wrong answers are about other things. ruleA had no made-up date; v1rule and codeB
  one each, a next rent day read from the lease's "due on the 1st".
- Nearly every model-counted span sits in the repair skill's materiality reading ("how long it lasted"), which
  invites a number.

### repair_not_made under the new rule 7 (2026-10-28)

Rule 7 now keeps time spans to the tenant's own words. The repair skill, unchanged (`versions/rule7.md`, the same as
keys2), ran all nine stories under it as `rule7`. Its answers were shuffled blind among keys2's from the rerun, and
three Opus graders graded both, three stories each (`repair_not_made/results/rule7/`). Told up front what the rerun's
second grader was told late: read a cited section before calling it unsupported, and keep notes out of other_error.
About $2.50; no errors, no empty answers, no made-up dates. v1 was not rerun.

Right of 27, same graders: rule7 24 (3 wrong), keys2 20 (1 partly, 6 wrong; the rerun's graders gave 19).

- Spans the model counted (`spans.py`): keys2 3, all story 2; rule7 0. Story 2 now says "No hot water since
  February 25". The graders found one more each with no number or a changed one: rule7 "no repair for several days
  after your notice" (story 7); keys2 "about a month" for the tenant's "over a month" (story 9).
- Story 2: rule7 right 2 of 3, keys2 0 of 3. The third rule7 answer says stopping rent after moving out "isn't safe
  yet, because your letter only said you would end the lease", as if that notice decided it. The grader said the
  notice "applies only to a tenant who stays", which overstates 83.60(1)(a): it also needs it for the 83.51(1)
  defense in a suit for unpaid rent (AUTHOR.md 20).
- Fixes from these answers (2026-10-29, not yet run live): the repair skill says how options 1 and 2 fit together;
  rule 7 names vague spans and allows the date a problem began; the rules' example heading no longer asks whether the
  law covers the tenant.
- Story 3: one rule7 answer counted wrong for "I've saved 'no school housing' as a pending fact for you to confirm",
  read as asking the college question. Round 1's review read that line as the page's usual confirming. A judge's
  call; read that way, rule7 is 25.
- The skill was not loaded in 2 of 3 story-6 answers (retaliation); the model read 83.64 itself and was right both
  times. keys2 loaded it in all 27.

### repair_not_made after the three fixes (2026-10-29)

The fixes from the run above (the repair skill on options 1 and 2, rule 7 naming vague spans and allowing the start
date, a new example heading) ran all nine stories as `rule7fix` (`versions/rule7fix.md`). Its answers were shuffled
blind among the rule 7 run's, and three new Opus graders graded both, three stories each, with the same instructions
(`repair_not_made/results/rule7fix/`). About $2.43; no errors, no empty answers, no made-up dates.

Right of 27, same graders: rule7fix 26, rule7 25 (the graders before gave rule7 24). Within noise.

- These graders read the rule 7 run differently: its story-2 answer that tied rent to the notice, and its "several
  days", only as notes; a story-6 line ("month to month, so your landlord can generally change the rent") as an error.
- Spans by `spans.py`, which now finds vague ones too: rule7fix 0, rule7 1. No span in the tenant's words either (5
  before).
- Story 2: all three rule7fix answers keep ending the lease and holding back rent apart.
- Story 3: the college check still has a box of its own in 3 of 3; only story 3 copies a "law cover you" heading now.
  One answer, wrong, ends the check "If the housing is run by or for a school, tell me, because that would change the
  answer", rule 3's words.
- The skill loaded in all 27 (rule7 25). Quotes not found word for word: 7 of 185 (rule7 3 of 183); three are the
  skill's own wording, "beyond the landlord's control", put in quote marks.

### wants_to_leave_early and notice_received_violation (2026-10-30)

Eight and nine stories, 3 runs each, the new skill against v1's, on Sonnet 5.5; six Opus graders, blind
(`wants_to_leave_early/SCORES.md`, `notice_received_violation/SCORES.md`). $9.92; no errors, no empty answers. The new
skills loaded in all 51 answers, v1's in 50.

Right, of the settled answers: leaving early, new 23 of 24, v1 12. The 7-day notice, new 20 of 24, v1 13 (notice-6 runs
but is not counted; it waits on AUTHOR.md item 22). v1 could not know two of the author's rulings (leave-4's fee over
the limit, notice-4's 12 months); leaving those stories out, new 37 of 42, v1 25.

Each new answer not right:

- The skill's: notice-2 once, a guest's stay called over when it ran past the rent payment; the skill dropped v1's
  line that the violation must not go on after the rent is taken. notice-8 once, never saying the 5 days, since the
  skill says never to give "a date" for them.
- Model slips, in SLIPS.md: leave-5 once ("well over 30 days"), notice-7 once (a lean), notice-8 once (a flat rule), and,
  in the uncounted notice-6, one unsupported assurance.
- A judge's call, in `notice_received_violation/review.json`: notice-1 once. The grader said the answer worked out
  "about March 9, 2027" itself; it came from `count_days`, and packets do not show tool calls. Without this change, 19.

Code's made-up-date flags, one each way per skill, are read by hand: "May 1" as a rent day from the lease (leave-6, both
versions), "November 10", a fact's date with no year (notice-6, new), and "June 9", which is real (notice-9, v1). The
check for quotes flags 3 right ones, since it does not read the stored text's space before a comma (SLIPS.md).

The round of fixes (the author's OK, 2026-10-30): the skill says a violation must be over when the rent is taken; it and
the repair skill give the 5 days but no calendar date; a mistake line says the lists are only examples; the quote check
reads the stored text's space before a comma. notice-2 and notice-8 rerun as `fixed` (`versions/fixed.md`), one Opus
grader, blind; $0.63. Right 4 of 6 (3 of 6 before). All three lawsuit answers now give the 5 days, and the guest's stay is
not called over. Both misses are new model slips, in SLIPS.md: a closed list, and a burden of proof. Quotes not found
in the new answers: 5 of 271 (8 before), by the same count.

Then both skills were trimmed (about 3,590 and 3,470 words, from 3,820 and 3,590): repeated lines and long quotes put in
cited plain words, with no citation lost. The scores above are from the longer text.

The trim, checked live (2026-10-30, the author's OK): leave-6 and notice-3, 6, 7, 9, 3 runs each, as `trimmed`
(`versions/trimmed.md`), one Opus grader, blind; $1.79. It was not graded beside the longer text, so the two are not
strictly comparable. Settled stories, right of 12: trimmed 9 (1 partly, 2 wrong), longer text 11 (1 partly). The risk the
trim carried, dropping a reading, did not show: every answer on an open point gave both, and none said "probably".

- The skill's: notice-7 once, "It starts the count" on a text, against its own first reading. That line was the skill's,
  in the longer text too, so it is removed, not rerun.
- Model slips, in SLIPS.md: notice-3 once ("normally"), leave-6 once ("supports the second reading"), and notice-6's "for
  four months", 3 of 3 against 0 of 3. The trim did not touch anything about spans, but so few answers cannot rule it out.

### neighbor_disturbance, rent_increased, and lease_ending (2026-11-01)

Seven, eight, and nine stories, 3 runs each, the new skill against v1's, on Sonnet 5.5; eight Opus graders, blind (`SCORES.md`
in each folder). $11.69; no errors, no empty answers. The new skills and v1's loaded in all 144 answers.

Right, of 72: new 48 (9 partly, 15 wrong), v1 8 (32 partly, 32 wrong). By skill: neighbor, new 15 of 21, v1 2; rent, new 12 of
24, v1 2; lease ending, new 21 of 27, v1 4. v1 could not know the author's rulings in seven stories (neighbor-1, 4; rent-1, 4,
6, 7, 8); leaving those out, new 34 of 51, v1 6. One change to a grader's verdict, in `lease_ending/review.json`: end-5/1 down
to wrong for a date no tool gave. Without it, lease ending is 22.

Each new answer not right:

- The skill's: rent-2 once (its "not met" line sends the tenant to option 1's flat "cannot change the rent"); rent-7, 3 of 3
  (option 1's plain answer pulls ahead of the part on rent already paid); end-5, 2 of 3 ("the same notice works for the next
  period", against the skill's own not-settled line on a late notice); neighbor-2 once ("count from the day it arrives", the
  skill's own shortcut, without saying the point is open).
- Model slips, in SLIPS.md: neighbor-3 (3), neighbor-7 (2), rent-2 (2), rent-3, rent-4 (3), rent-5, rent-8, end-3 (2), end-4, end-9.

Quotes not found, new: 5 of 492. Every quote in the three skills checks out (`law.py`).

The round of fixes (the author's OK, 2026-11-01): the rent skill says a clause not met leaves the landlord free to meet it, a
tenant who already paid starts from "not settled", and retaliation no longer reads as complaints only; lease ending says a tenant
past the date can give notice for the next period, spells out too early and too late under the 15-day readings, and ties the 7-day
date to the day they leave; neighbor says a mailed notice's day is open. One guard, the author's call: "Name no choice as the
safest; say what each risks." Eight stories rerun as `fixed` (`versions/fixed.md`), one Opus grader, blind; $2.22. Right 18 of 24
(6 of 24 before). A second change in `lease_ending/review.json`: end-5/1 down to wrong for "May 31" again; without it, 19. Quotes
not found in the new answers: 0 of 169. These numbers are from one grader against the first round's eight, and the other sixteen
stories were not rerun, so end-4's date line has no live check.

What is left, all model slips, in SLIPS.md: neighbor-3 (a lean; "Don't pay April rent"), rent-2 (a span and a wrong amount), rent-4
(a lean; a flat line on paying), and end-5 ("May 31"). No rent-4 answer now calls keeping the old rent the safest course; one says
"I'm not naming any of these as the safest", the guard's own words, to the tenant.

Both first-round and fixed answers ran from the longer text. The skills are not yet trimmed: about 2,870, 3,120, and 3,780 words.

The six left after the fixes, traced (2026-11-01; answers, tool calls, and grades read in full, no new model calls). The run logs
hold no private reasoning: none was requested, and text sent beside a tool call is not saved. Each grader's claim holds against
the text, except that end-5/1 is my change, not the grader's.

- neighbor-3/1, "Don't pay April rent": the skill says what paying may cost but not what not paying costs; option 4 has that, and it
  opens "Say so plainly when asked". Only this story has rent still to come due. 5 of its 6 answers never warn of a demand. A word
  search of all six skills' tests found no other plain advice like it; the other hits say "don't stop paying".
- neighbor-3/3 and rent-4/1, a lean: rule 2 says to answer "can I" first, and the neighbor skill says "say plainly". Opening point on
  "Can I" stories, first round: neighbor-3 1 of 3, rent-7 0 of 3. On others: 3 of 3 on four stories, 2 of 3 on one, 0 of 3 on rent-4.
  rent-7 went to 3 of 3 with "Start the answer there". On rent-4, the skill's own "points this way" is repeated in 6 of 6.
- rent-4/1 and 2, the leaving date: both had March 31 from `count_days` and called leaving "a separate question". None of the 6 loaded
  `lease_ending`, the right one included, so loading is ruled out. The phrase appears in 2 of 3 after the "say what each risks" line,
  0 of 3 before; too few to prove the line caused it. rent-4/2 also states one reading of paying as the law.
- rent-2/1: "about a month" (2 of 96 answers, both this story) and "$50" for a $100 raise (1 of 15 differences stated). "$50" is in no
  lease, skill, or fact. Nothing checks amounts.
- end-5/1, "May 31": a true date no tool could give, since this story has no next period in its facts. 2 of 6 here; none on the five
  stories that have it. Rule 7 is broken, but nothing false is said. Read loosely, the rerun is 19.

Also: the rerun's one grader may read leans less strictly than the first round's, so 6 to 18 may overstate the gain. Regrading both
rounds together would settle it.

The second round of fixes (the author's OK, 2026-11-01): neighbor joins the rent-paid condition to the risk of not paying; all three
skills write "You can if X, and X is not settled" for a "can I" answer that turns on an open point; rent drops "points this way",
gives the leaving date in its own bullet, and marks the paying line as a reading; lease ending gives the next rent period no date
unless the fact is confirmed. neighbor-3, rent-4, and end-5 rerun as `fixed2` (`versions/fixed2.md`), $0.84. One Opus grader read those
answers shuffled blind among the last round's on the same stories (`results/regrade_fixed_same_grader.json`; 8 of 9 verdicts on the last
round matched the earlier grader's, and rent-4/2 moved from wrong to partly).

Same grader, right of 9: last round 5, this round 4 (end-5/1 stays right here; with my change for "May 31", last round is 4). By story:
neighbor-3 W R P then R W W; rent-4 P P R then P P P; end-5 R R R then R R R.

The verdicts barely moved, but what each fix aimed at did. neighbor-3: advice not to pay, 1 of 3 to 0; no warning about not paying, 3 of
3 to 0; a plain yes, 1 of 3 to 0. rent-4: the leaving date missing, 2 of 3 to 0; one reading of paying stated as law, 1 of 3 to 0. end-5:
"May 31", 1 of 3 to 0. What decides the verdicts now is two new one-off errors on neighbor-3 and the rent-4 lean.

The rent-4 lean is where the diagnosis was wrong: with "points this way" gone, the opening leaned in 3 of 3, up from 1 of 3 (first round 3
of 3). The likely driver is the reply rule "say what it means for the tenant" with the question "What can I do?": each short answer
states the tenant's position, then picks a default. The "You can if" form worked 3 of 3 on neighbor-3, a recipe, where "Name no choice
as the safest", a prohibition, did not. Not yet tested on rent-4.

By the latest run of each story, right of 72: 60 (v1 8), with mixed graders and skill text; the sixteen stories not rerun ran on the
first-round text. A clean number needs a full rerun on the final text.

One last try on the rent-4 lean (the author's OK, 2026-11-01; stopping here whatever it showed). The rent skill's option 3 replaces "Name no
choice as the safest" with a recipe: say it is not settled, then "You have three choices, and each has a risk", then name them without
choosing. rent-4 rerun as `fixed3` (`versions/fixed3.md`), $0.38. One Opus grader read those answers shuffled blind among `fixed2`'s
(`results/regrade_fixed2_same_grader.json`; all three verdicts matched the earlier grader's). fixed2 P P P; fixed3 W R P.

All three use the recipe's words, and the default is gone: the opening point went from 0 of 3 to 2 of 3. The miss in run 3 is its closing
question, which drops a choice; the miss in run 1 is "11 days' notice", a count of its own and off by one. Both are in SLIPS.md. All three
now load `lease_ending`, since the bullet gives the date first; none of the nine before did. "From other tenants" is still in 3 of 3.

By the latest run of each story, right of 72: 61 (v1 8), with the same caveat. The eleven left: neighbor-3 (2), neighbor-7 (2), rent-2,
rent-4 (2), rent-5, rent-8, end-4, end-9. Quotes not found in the latest reruns: 1 of 87 (`fixed2`'s rent-4; `fixed3` has none).

The clean number (2026-11-01): the three skills trimmed by about 3 percent (2,870, 3,100, and 3,720 words; no cite, reading, or `count_days`
call lost, checked by script; `versions/final.md`), then all 24 stories, 3 runs each, as `final`. $6.52; no errors, no empty answers, the skill
loaded in all 72. Eight new Opus graders, blind, read `final` shuffled among v1's first-round answers, so both versions face the same
graders. `grade.py`'s v1 rows now use these grades; the first round's are in `results/round1_judge_opus_v1.json`.

Right, of 72: final 61 (2 partly, 9 wrong), v1 9 (33 partly, 30 wrong). By skill: neighbor 19 of 21, v1 2; rent 22 of 24, v1 3; lease ending 20 of
27, v1 4. Leaving out the seven stories on rulings v1 could not know: final 43 of 51, v1 7. The opening point: 3 of 3 on all eight stories that
have it. Quotes not found, final: 8 of 536; the page's stricter check, which wants a cite beside each quote, passes 492.

Each final answer not right:

- The skill's: neighbor-2/3, "Deciding before the next rent is due avoids this question", my own line from the second round, wrong once rent has
  been paid. The line also shows in neighbor-5/3 and neighbor-6/1 and 2, which their grader passed. end-6/1 never says the landlord can give
  proper notice with no reason named; that part of the skill does not say it.
- Model slips, in SLIPS.md: rent-4/3, rent-6/2, end-2/3, end-3/2 and 3 (the skill's outcomes are right; the short answer swaps a word), end-6/3,
  end-7/1 (an omission), end-8/2.
- A judge's call: neighbor-4/3, "damages depend on a failed lease promise", narrow against 83.55's "this part", though no part II duty is at issue
  there. Not changed; if not counted, 62 (AUTHOR.md 25).

