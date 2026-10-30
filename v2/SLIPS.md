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
- 2026-10-25, memory test (`comparisons/memory/`, Sonnet 5.5): 1 of 18, new memory, leave-early story: "May 15 to
  July 31 would be about 2.5 months", a period it worked out itself.
- 2026-10-28, repair skill test (`comparisons/each_skill/`, Sonnet 5.5), story 3: a leak that began 13 days
  before called "about a month" or "over a month" (new skill 2 of 3, v1 2 of 3), and once (new) "the 7 days would
  probably not be over by May 1" for a notice delivered April 10.
  After the round of fixes (shared skill only changed): 2 of 3 again.
- 2026-10-28, repair rerun on the new keys (Sonnet 5.5): story 2's outage, 23 days, called "more than three weeks"
  or "about three and a half weeks", keys2 3 of 3; story 3, 0 of 3. Spans that repeat the tenant's words not counted.
- 2026-10-28, five ways side by side (repair stories 1, 2, 3, 7, 9; `comparisons/each_skill/README.md`): answers with
  a span the model counted, of 15: current 3, v1's rule 1, rule 7 naming spans 1, code's day counts 5, both 3. With
  code's counts it also misapplied one ("more than 9 weeks" for a leak that ended 26 days in).
- 2026-10-28, the repair skill under rule 7 naming spans (all nine stories, graded beside keys2): 1 of 27, "no
  repair for several days after your notice" (story 7), a span with no number. keys2, same graders: 4 of 27.

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
- 2026-10-24, deposit skill test on Sonnet: not flat, but a lean. Story 14 (Section 8), every answer in all three
  versions opens "Probably yes" before giving both readings; stories 15 and 16, once each.
- 2026-10-24, the current skill on Sonnet: after the no-lean line, still a lean where the skill does not mark the
  point not settled: story 11 ("Probably yes" on the college question), story 18 ("Yes, the 30-day deadline has
  passed" after an objection), story 9 once.
- 2026-10-28, repair skill test (Sonnet 5.5), story 2: "You probably can move out" on the hot-water question,
  v1 3 of 3, new 0 of 3.
- 2026-10-28, repair rerun, story 7: both readings of when the lease ended, then one outcome for both ("Under either
  reading, the 15-day return date ... has passed"), keys2 2 of 3; v1's first-round answers, regraded, 2 of 3.

## Says the balance is due on day 30 after an objection

The answer says the landlord must send the balance within 30 days after the notice even if the tenant objects.
83.49(3)(b) puts that duty in a sentence that begins "Unless the tenant objects".

- 2026-10-23, deposit skill test (gemini), story 6: v1 2 of 3, old 1 of 3, new 0 of 3 (the new skill says what
  follows an objection is not settled).
- 2026-10-24, deposit skill test on Sonnet, story 18: old 3 of 3, v1 0, new 0.

## Says the tenant said something they did not

- 2026-10-23, deposit skill test (gemini): "because you mentioned college housing" when the tenant had not, v1 2 of
  36 (stories 1 and 2); old and new 0.
- 2026-10-24, deposit skill test on Sonnet, stories 13 to 18: "you called this college housing", v1 2 of 18, new 1
  of 18, old 0.

## Treats the 15-day return date as due after a claim

The 15-day return applies only when the landlord intends no claim (83.49(3)(a)); the answer applies it anyway.

- 2026-10-23, deposit skill test (gemini), story 5: v1 3 of 3; old and new 0.
- 2026-10-24, the current skill on Sonnet, story 5: 2 of 3.

## States a rule the statute does not have

- 2026-10-24, deposit skill test on Sonnet, story 16: "the landlord could deduct only what it can justify" (new 1
  of 3); 83.49(3)(b) sets no such limit.
- 2026-10-24, the fixed skill on Sonnet, story 14: reading two narrowed to "a program that sets or limits the
  deposit amount", dropping the rent that 83.49(4) names (2 of 3).
- 2026-10-24, the current skill on Sonnet: receipt as the test for the landlord's 30 days (story 9, 1 of 3); a
  result 83.491 does not give, that a landlord who skips a fee notice cannot keep the fee (story 12, 1 of 3).
- 2026-10-27, plain replies test (`comparisons/plain/`, Sonnet 5.5): new rules 2 of 54 ("the deposit is still yours
  unless your landlord shows it has a right to keep some of it", story 14; the landlord "would have to show the
  carpet damage is more than ordinary wear", story 18); old rules 1 of 54 (the fee might be a deposit "under another
  name", against the confirmed facts, story 12).
- 2026-10-28, repair skill test (Sonnet 5.5): v1 8 of 21 answers (a lease cannot change the hot-water duty; 83.64
  bars any retaliatory end; no way to sue over a rent increase; the 83.60 defense only in an eviction), new 1 of 21
  (story 7: the repair question "does not change the notice rules").
- 2026-10-28, repair rerun: keys2 2 of 27 (83.51(4) read as making the landlord answer for whatever the tenant did
  not cause, story 8; "no defense based on the garage", though 83.60(1)(a) allows other defenses, story 9). v1's new
  answers 5 of 15, stories 8 and 9 (the 83.56(1)(b) rent cut for the landlord's own repaving, twice; ending the
  lease "the only remedy" rent paid could affect; notice before May 1 "avoids" that question; the garage "a
  structural component", against the lease).
- 2026-10-28, the repair skill under the new rule 7: 1 of 27 (story 2: stopping rent after moving out "isn't safe
  yet, because your letter only said you would end the lease", as if the notice for holding back rent decided it;
  that notice is needed only for the 83.51(1) defense if sued for rent (83.60(1)), and ending the lease needs none).

## Does not load the skill

The tenant's question fits a skill, but the model answers without calling `load_skill`, so the skill's checklist is
never read.

- 2026-10-21, model test, deposit stories (skill not loaded for it, as on the page): nemotron 4 of 15 (sample lease)
  and 0 of 15 (own lease); haiku, gemini, sonnet 30 of 30.
- 2026-10-28, repair skill test (Sonnet 5.5): new 1 of 21 (story 6, read 83.64 itself), v1 0 of 21.
- 2026-10-28, repair rerun: keys2 0 of 27, v1 0 of 15.
- 2026-10-28, the repair skill under the new rule 7: 2 of 27, both story 6 (retaliation), which read 83.64 itself and
  was right both times.

## Empty answer

The tool loop ends with no text, so the page would show the tenant nothing.

- 2026-10-21, model test: 2 of 392 answers, haiku (own lease, story 3, after 9 tool calls) and nemotron (own lease,
  the grill question).
- 2026-10-22, live checks of story 5 (gemini, after the college-housing step): 2 of 5 answers empty. All 5 used the
  full 8 tool rounds (one lookup per round) before being told to answer.
- 2026-10-25, memory test with the open-lines reminder (Sonnet 5.5): 1 of 15 answers nearly empty (deposit story):
  only "I've saved 2026-08-20 as your receipt date. Please confirm it in the sidebar...". A rerun logging every
  step (12 answers, 6 with the reminder) found no text written beside tool calls, only hidden reasoning, so the
  chat loop dropped nothing: the model ended its turn with a short note. Not seen again in 12 reruns.
- 2026-10-27, plain replies test (Sonnet 5.5, old rules): 1 of 54 (story 12, run 3, after 8 tool calls). New
  rules: 0 of 54.

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
- 2026-10-25, after rewording what open means (rule 9, `save_line`): 2 of 15 (0 of 9, then 2 of 6 in the deposit
  reruns); with the open-lines reminder too: 0 of 15.
- Answer: the author kept both, 2026-10-25 (AUTHOR.md item 10).

## Changes the statute's words inside quote marks

A quote ends with a period where the statute goes on, or changes a word's form. The page's quote check flags it.

- 2026-10-26, deposit skill test (`comparisons/deposit/`, Sonnet 5.5, stories 16 and 18): 3 of 6 answers. A period
  added inside the quote 3 times; "forfeited the right" for the statute's "forfeits the right" once.
- 2026-10-28, repair rerun (quotes not found word for word anywhere): keys2 4 of 193 ("will not pay rent by reason"
  for "not to pay rent by reason"; "provision" for "provisions"; "beyond the landlord's control"; "is the landlord
  covered", nobody's words); v1's new answers 4 times the sign's words from the facts, "closed until further notice".
  Not slips: 7 more were right but flagged, since the stored text writes "s. 83.51 (1)" with a space (5) and the
  check did not read ". . ." as a cut (2, v1). The check reads both since 2026-10-28.
- 2026-10-28, the repair skill under the new rule 7: 3 of 183 ("beyond the landlord's control" twice, for "beyond
  the control of the landlord"; "after delivery" for "after the delivery").

## Writes a short answer longer than asked

The "Writing the reply" rules ask for 3 to 5 plain sentences before the question; the answer writes more.

- 2026-10-27, plain replies test (`comparisons/plain/`, Sonnet 5.5, new rules): 45 of 54 short answers had more than
  5 sentences before the question (median 7, median 127 words with the question; the longest 16 sentences).

## Quotes the law in the short answer

The rules keep quotations and section numbers behind the click; the short answer quotes anyway.

- 2026-10-27, plain replies test (Sonnet 5.5, new rules): 7 of 54 short answers held a quotation; none held a
  section number.

## Uses "it" or "this" for something not named nearby

A pointing word whose thing is two or more sentences back, or that could mean two things ("It can still sue you",
the landlord last named two sentences before).

- 2026-10-27, plain replies test (Sonnet 5.5, counted by Opus with my review, in what the tenant sees first): old
  rules 79 in 54 answers, new rules 21 in 54 (the graders' own counts: 99 and 39, the same per 100 words). Most are a
  chain of "it" for the landlord or the letter.

## Shows the tenant a tool's name

The reply names one of the model's tools, like "(count_days)", which means nothing to a tenant.

- 2026-10-27, plain replies test (Sonnet 5.5): old rules 2 of 54, both in what the tenant sees first; new rules 1 of
  54, inside a box.

## Gives the college-housing check its own point when the lease settles it

The shared skill asks for one line when the lease shows no tie to a school; the answer gives it a box of its own and
tells the tenant the noted fact waits for them to confirm.

- 2026-10-28, repair skill test (Sonnet 5.5), story 3 (no `school_housing` in the facts): new skill 3 of 3, a box
  titled "Does Florida's landlord-tenant law cover your home?"; once it names the fact as "school_housing = no".
- 2026-10-28, after the shared skill asked for one line inside another point: 2 of 3 still give it a box. The reply
  rules' example heading, "Does Florida's deposit law cover you?", may invite it.
- 2026-10-28, repair rerun (keys2), story 3: 3 of 3, each a box titled "Does Florida's landlord-tenant law cover your
  home?". The key now allows one line at most, as optional detail, so the graders did not count it.
- 2026-10-28, the repair skill under the new rule 7, story 3: 3 of 3 a box of its own; once it ends "I've saved 'no
  school housing' as a pending fact for you to confirm", which the grader read as asking (1 of 54 answers say so).
  The example heading also shows up where the check is settled: "Does Florida's deposit law cover you?" in story 7,
  2 of 3 in both versions. The example was changed on 2026-10-29.
