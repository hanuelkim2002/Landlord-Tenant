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
