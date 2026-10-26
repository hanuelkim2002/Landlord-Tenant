# Memory test

Does the new memory (the timeline and "since last visit", `docs/superpowers/specs/2026-10-25-memory-timeline-design.md`)
help a tenant who comes back days later? Three made-up return visits, each answered by the app's own chat, with the
new memory and with v2 as it is on `main` as the baseline (the old chat and the facts only).

## The stories (`stories.json`)

On the sample lease (`comparisons/skills/lease.txt`). Each first visit is dated days before the story's "today"; its
reply says nothing about the law. Then the tenant comes back:

- `deposit_letter`, 12 days later: "got a letter from him today, he's keeping $500 for carpet cleaning". The tenant
  corrected the move-out date in the sidebar between the visits.
- `repair_no_show`, 5 days later: "nobody came thursday. still no AC". The landlord had promised Thursday.
- `leave_early_reply`, 21 days later: "he finally answered, says i owe rent through july no matter what".

## How it runs

`run_memory.py new|baseline [--runs 3] [--dry]`: 3 runs of each story, through `chat.reply` as the page does it, with
the story's day as "today" for `count_days` and `since_last_visit`. The baseline is a copy of `main`'s v2 made with
`git archive`. Claude Sonnet 5.5 answers through Anthropic's own SDK (`claude_client.py`, test-only), with the key
`ANTHROPIC_API_KEY` from the environment. The SDK is not in v2's venv; it was installed into a scratch folder and put
on `PYTHONPATH` for the run. Every answer also records each step: the text Claude wrote, the tools it called, and why
it stopped. `--tag NAME` writes a rerun to `results/<mode>_<NAME>.jsonl`; `--story ID` runs one story;
`--no-reminder` leaves the open-lines list out of `save_line`'s reply, to compare.

## How it is scored (`score.py`, `review.json`, `SCORES.md`)

Six checks per answer, out of 9 per mode: no retelling asked, picks up the open item, saves the new event as a line
and closes the line left open (new memory only), works out no date itself, answers first. Code counts the tool calls,
the lines saved, and any date in the answer found nowhere in the story, the lease, or a tool's result; Claude reads
every answer for the rest. Each story's `settled_line` is the open line its news settles, so code counts the
closing in the follow-up runs after the fix for open lines.
