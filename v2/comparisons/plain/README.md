# Plain replies test

Do the "Writing the reply" rules (2026-10-27) give a tenant a short, plain answer first, without making the answers
less right? Sonnet 5.5 from Anthropic answers the 18 deposit stories (`comparisons/skills/stories.json` and
`stories_more.json`) three times with the rules from before the change (`rules_old.txt`, saved by code) and three
times with the new rules, through the app's own chat and skills. Spec:
`docs/superpowers/specs/2026-10-27-plain-replies-design.md`.

- `python run.py old` (or `new`): the answers, into `results/<rules>.jsonl`. It reuses the deposit test's stories and
  leases and the model test's set-up. Add `--dry` to try it with a fake model, `--stories 6,8` for some stories.
- Graded in two ways, by Claude Opus 5.5 subagents in Claude Code: right, partly, or wrong against each story's key
  (blind to the rules, the deposit test's rubric), and a plain reading of what the tenant sees first (the spec's
  wording). Code counts the rest. Results below once graded.

## Results (2026-10-27)

Four of the spec's five targets met (`SCORES.md`, `scores.json`). Over 54 answers each, old rules against new:

- What the tenant reads before any click: median 462 words, against 127. **Missed** the 100-word target: 45 of 54
  short answers ran past 5 sentences (median 7). The whole reply grew, from 462 to 673 words (median), with the boxes.
- Unclear "it", "this", "that" in what is seen first: 79 against 21 (median 1 against 0). Unexplained legal words:
  135 against 7 (median 2 against 0). The seen-first part answers the question alone: 53 against 54.
- Right on the 16 settled stories (48 answers): 40 against 41; wrong 6 against 5. Format followed: 54 of 54.
- Section number or quotation in what is seen first: 53 against 7 (the 7 are quotations; no section numbers).
- Story 8 is wrong in all six answers under both rules: the key needs its lease's e-mail addendum to say the election
  is voluntary and revocable (TODO.md). Story 18 misses its "no deadline after an objection" point under both.

How it was graded: six Opus subagents gave right, partly, or wrong, blind to the rules, with the deposit test's
rubric; three gave the plain counts with the spec's wording. The three plain graders drew two lines differently, so
I put every count on one standard (`review_plain.json`): an "it" that echoes the tenant's own words in the first
sentence, and a "this" or "it" that can only mean the dispute or the answer as a whole ("What if this goes to
court?"), are not counted; a chain of "it" with its thing two sentences back is. 20 old and 18 new flags were
dropped. The grader for stories 7 to 12 did not count such chains at all, under either rules, so its counts are low
on both sides. I added no legal words: the ones graders disagreed on ("addendum", "remit") appear only in old answers.
The runs cost $10.25 on the Anthropic key ($4.95 old, $5.30 new); the graders ran on the Claude plan.
