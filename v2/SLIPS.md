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
- 2026-10-23, deposit skill test (`comparisons/deposit/`, gemini): 0 of 108. Until that day the check read
  "July 2026" as July 20; the counts above were not rechecked.

## Asks again for what the tenant said or the lease holds

The answer asks the tenant for a fact they already gave, or one the lease states, instead of noting it with
`note_fact` (or reading the lease), and asks several questions where rule 8 allows one.

- 2026-10-20, first run of the v2 page (nemotron): the first reply asked for the lease end date (in the lease) and
  the move-out date (in the tenant's message), four questions in all; the second asked the tenant to confirm the
  dates in the chat after noting them for the sidebar.
- 2026-10-23, deposit skill test (gemini): more than one question in 1 of 36 answers (v1), 1 (old), 2 (new), all
  in stories 2 and 5.

## States an open question as settled

The skill marks a point as not settled, with a reading on each side; the answer gives one reading as the law.

- 2026-10-19, skills test (nemotron): 12 of 12 answers to story 5 (a claim sent by text), every format. Counts only
  if the author agrees the point is open (AUTHOR.md item 4).
- 2026-10-21, model test, story 5: nemotron 2 of 3 (sample lease) and 3 of 3 (own lease); haiku, gemini, sonnet 0.

## Says the balance is due on day 30 after an objection

The answer says the landlord must send the balance within 30 days after the notice even if the tenant objects.
83.49(3)(b) puts that duty in a sentence that begins "Unless the tenant objects".

- 2026-10-23, deposit skill test (gemini), story 6: v1 2 of 3, old 1 of 3, new 0 of 3 (the new skill says what
  follows an objection is not settled).

## Says the tenant said something they did not

- 2026-10-23, deposit skill test (gemini): "because you mentioned college housing" when the tenant had not, v1 2 of
  36 (stories 1 and 2); old and new 0.

## Treats the 15-day return date as due after a claim

The 15-day return applies only when the landlord intends no claim (83.49(3)(a)); the answer applies it anyway.

- 2026-10-23, deposit skill test (gemini), story 5: v1 3 of 3; old and new 0.

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
