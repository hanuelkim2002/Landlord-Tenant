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
