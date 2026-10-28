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

## Results

None yet. The repair skill's run waits for the author's review of its new law points and its keys.
