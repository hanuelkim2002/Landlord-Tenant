# Slips

Model mistakes seen in live runs: one entry per kind, with a count per run. A slip gets a guard only if the author
decides.

## Does not read which lease option was chosen

The lease offers two options and marks one (initials, or a checked box). The answer treats both as open, or picks the
unmarked one.

- 2026-10-19, lease comparison (nemotron): 6. On v1's sample lease (sample-07), A, B, and C offered the $3,700.00
  early termination fee of Option 1, whose initials line is blank. On the 46-page lease (long-10), A, B, and C said
  "if you initialed Option 1" though the resident did.
- Answer: the author added lease-reading rule 4 (README.md), 2026-10-19.

## Works out a date itself

The answer gives a date that is not a confirmed fact or a `count_days` result (the model counted it, often right,
against rule 7).

- 2026-10-19, skills test (nemotron): 13 of 60 answers (v1 3, A 3, B 5, C 2). Once (C, story 3) the model asked the
  tenant for today's date instead of calling `count_days`.
- 2026-10-20, first run of the v2 page (nemotron): 1, "July 31 + 30 days = August 30" written before the dates were
  confirmed.
- 2026-10-21, model test, deposit stories (`comparisons/models/`): nemotron 3 of 15 (sample lease) and 6 of 15 (own
  lease), haiku 1 of 15 (own), gemini and sonnet 0 of 30.
- 2026-10-25, memory test (`comparisons/memory/`, Sonnet 5.5): 1 of 18, new memory, leave-early story: "May 15 to
  July 31 would be about 2.5 months", a period it worked out itself.

## Asks again for what the tenant said or the lease holds

The answer asks the tenant for a fact they already gave, or one the lease states, instead of noting it with
`note_fact` (or reading the lease), and asks several questions where rule 8 allows one.

- 2026-10-20, first run of the v2 page (nemotron): the first reply asked for the lease end date (in the lease) and
  the move-out date (in the tenant's message), four questions in all; the second asked the tenant to confirm the
  dates in the chat after noting them for the sidebar.

## States an open question as settled

The skill marks a point as not settled, with a reading on each side; the answer gives one reading as the law.

- 2026-10-19, skills test (nemotron): 12 of 12 answers to story 5 (a claim sent by text), every format. Counts only
  if the author agrees the point is open (AUTHOR.md item 4).
- 2026-10-21, model test, story 5: nemotron 2 of 3 (sample lease) and 3 of 3 (own lease); haiku, gemini, sonnet 0.

## Does not load the skill

The tenant's question fits a skill, but the model answers without calling `load_skill`, so the skill's checklist is
never read.

- 2026-10-21, model test, deposit stories (skill not loaded for it, as on the page): nemotron 4 of 15 (sample lease)
  and 0 of 15 (own lease); haiku, gemini, sonnet 30 of 30.

## Empty answer

The tool loop ends with no text, so the page would show the tenant nothing.

- 2026-10-21, model test: 2 of 392 answers, haiku (own lease, story 3, after 9 tool calls) and nemotron (own lease,
  the grill question).
- 2026-10-22, live checks of story 5 (gemini, after the college-housing step): 2 of 5 answers empty. All 5 used the
  full 8 tool rounds (one lookup per round) before being told to answer.

## Misreads a page image

The vision model gets a check box or a typed-in value wrong, or never finishes the page.

- 2026-10-21, model test, gemma: broken sample lease 31.3 of 35 boxes right on average (water and trash shown
  checked for the tenant); own lease 51 of 71 values and boxes; page 11 of the own lease (mostly blank lines) timed out
  twice (2 minutes each). Haiku, Gemini, and Sonnet: 35 of 35 and 71 of 71.

## Leaves the old line open

The tenant brings news that settles an open line of the timeline (the letter came, nobody came, the manager
answered). The model saves the news as a new line but does not save the old line again as closed, so the open
list keeps a line that is done.

- 2026-10-25, memory test (`comparisons/memory/`, Sonnet 5.5): 6 of 9 new-memory answers left it open (deposit 1 of
  3, repair 2 of 3, leave-early 3 of 3).
