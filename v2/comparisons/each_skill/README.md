# Each skill's test

One small test per new skill (`docs/superpowers/specs/2026-10-28-other-skills-design.md`): about 6 to 8 stories with
answer keys the author approves first, 3 runs each on the app's chat model (Claude Sonnet 5.5 from Anthropic), v1's
skill run beside the new one as the baseline, graded blind by Claude Opus 5.5 subagents in Claude Code.

## The files

- `run.py`, `judge.py`, `grade.py`: one runner, packer, and scorer for every skill.
- `spans.py`: finds the time spans in answers ("more than three weeks") and sorts each: the tenant's words, a count
  code would give, or the model's own counting. It misses spans with no number ("for weeks"); read those by hand.
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
    an answer, and it does not matter.

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
