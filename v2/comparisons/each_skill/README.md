# Each skill's test

One small test per new skill (`docs/superpowers/specs/2026-10-28-other-skills-design.md`): about 6 to 8 stories with
answer keys the author approves first, 3 runs each on the app's chat model (Claude Sonnet 5.5 from Anthropic), v1's
skill run beside the new one as the baseline, graded blind by Claude Opus 5.5 subagents in Claude Code.

## The files

- `run.py`, `judge.py`, `grade.py`: one runner, packer, and scorer for every skill.
- `<skill>/stories.json`: the stories and their keys, in the deposit stories' shape, plus `sections` (the statute
  sections the graders read) and, on a story, `lease` (a lease file in that folder; none means
  `comparisons/skills/lease.txt`) and `open: true` (a key that turns on an open call; not counted as settled).
- `<skill>/versions/<name>.md`: a frozen copy of the skill, when a run needs one (after a round of fixes).
- `<skill>/results/`: the answers (`<version>.jsonl`) and the graders' grades (`judge_opus_<version>.json`).
- `<skill>/SCORES.md`, `<skill>/scores.json`: written by `grade.py`.

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
(`repair_not_made/SCORES.md`). About $4.10; no errors, no empty answers, no made-up dates.

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
