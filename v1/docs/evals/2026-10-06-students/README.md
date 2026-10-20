# Eval, 2026-10-06: college students with a broken AC (and other things), simulated

A dated record, not kept current. Asked for by the author: simulate a college student with little legal knowledge,
renting a bedroom in an apartment complex run by a management company, with roommates, whose AC (and other
amenities) does not work; try several variations; and judge the tool as that student would.

## Method

- No `UF_API_KEY` was available in this session, so nemotron on the UF gateway could not be called. What ran instead:
  the real program, `run.py` end to end, with every model call answered by a stand-in. `method/harness.py` replays a
  session from the start in a fresh interpreter for every step, with the lines the student typed and the stand-in's
  answers so far, on a scratch matter folder inside the run (never `matters/`), with the date fixed at 2026-10-06. When
  the program needs a model answer, the harness writes out exactly what the model would get (the system prompt as
  `prompt.system_prompt` built it, the messages, the tools) and stops. So the intake sheet, the options and their
  gates, the deadlines, the cited words, the checks under each reply, the letters, and the stop text are the
  program's own. Only the model's words are not.
- The stand-in model: one Claude agent (Sonnet) per run, told to answer as the model the program expects, from the
  requests and tool results only. It never saw the student's persona or notes. The lease reading (Gemma) was answered
  with a perfect profile: `method/make_lease.py` writes one whose 16 quotes all pass `lease.check_quotes`.
- The lease: made up for this eval, one copy per student (`results/*/program/`). Magnolia Row Student Apartments,
  Gainesville, managed by Hartwell Residential Management; one bedroom of a 4x4 on its own lease (1.3), $789 x 12,
  $300 deposit, $150 non-refundable amenity fee (3.3), individual liability for rent but joint liability for shared
  areas and appliances (3.4), Wi-Fi included (5.1) with no abatement for interruptions (5.2), amenities may close with
  no refund (6.2), the landlord repairs the HVAC and the appliances (7.1), repairs go through the resident portal, an
  emergency line for AC loss above 85 degrees, and "A maintenance request is a request for service and is not by
  itself a notice under Section 13.1" (7.2), notices by hand, certified mail, or e-mail (13.1), 7 days' notice before
  moving out early or the deposit is forfeited (9.2), and an early termination fee of $1,578 in the lease itself, with
  no separate addendum (12.1). Written to test points this tool is built around: an AC is not in 83.51(1)(b) but the
  lease promises it; a portal request is writing but the lease says it is not a notice; amenities and services the
  lease says carry no refund.
- The students: one Claude agent (Sonnet) per student, playing the persona in `method/personas/`. Each saw only the
  tenant's screen (run.py's output without the developer's diagnostic lines, which the web page does not show), typed
  in character, answered the sheet as they understood it, kept a diary, and wrote an evaluation at the end
  (`method/STUDENT_GUIDE.md`). I relayed turns between each student and its stand-in.
- `WIKI_UNVERIFIED=1`, as in the author's evals: unverified case pages shown, marked. No page is verified yet, so a
  tenant using the tool today would see no cases at all.

| Run | Student | The problem | Issues confirmed |
|---|---|---|---|
| A | Jordan, sophomore | AC dead since Sept 18; three portal requests; "parts on backorder"; rent paid | repair |
| B | Alex, junior | AC dead since Sept 22; one e-mail; roommates' rent strike; October unpaid, $839 past due | repair |
| C | Sam, freshman | no hot water since Sept 28; AC cutting out since about Sept 14; portal only | repair |
| D | Taylor, senior | pool, gym, study rooms closed; Wi-Fi drops nightly; wants the amenity fee back | none (answered no) |
| D2 | Taylor, again | the same, answering yes to the repair question | repair |
| E | Chris, sophomore | in-unit washer broken by a roommate; $85 split four ways; still leaks | repair (other noted) |
| F | Morgan, junior | AC leaking since Sept 10, mold, asthma; e-mailed "I'm going to have to move out"; wants out | repair, leave early |

Limits, read before the results:
- The stand-in is not nemotron. It likely follows the rules more closely than nemotron did in the earlier evals, so
  read the model's words as a best case. What the program does is real; that is where most findings below sit.
- The students are model personas, not people. Their ratings cluster (five of seven gave 3, 2, 3, 3, 3); the diaries
  and the quoted confusions are the signal, not the numbers.
- One run per story, and the lease is mine, written to probe known questions.

## Results at a glance

| Run | Chat turns | First reply (characters) | Of it, case listings | Letter drafted | Usefulness / Clarity / Trust / Ease / Recommend |
|---|---|---|---|---|---|
| A | 6 | 61,919 | 43,098 | yes, then redrafted | 3 / 2 / 3 / 3 / 3 |
| B | 6 | 39,769 | 28,777 | yes, then redrafted | 3 / 2 / 3 / 3 / 3 |
| C | 6 | 59,782 | 43,098 | yes, then redrafted | 3 / 2 / 3 / 3 / 3 |
| D | 0 | (stopped after one sheet question) | | no | 1 / 2 / 2 / 3 / 1 |
| D2 | 6 | 12,114 | 6,939 | yes | 3 / 2 / 3 / 3 / 3 |
| E | 6 | 22,439 | 11,485 | yes | 3 / 2 / 3 / 3 / 3 |
| F | 7 | 74,536 | 53,637 | yes, then redrafted | 4 / 2 / 3 / 3 / 3 |

- First replies ran 12,000 to 75,000 characters (median about 50,000). Case listings were 51% to 72% of each first
  reply; the model's own answer was 2,000 to 10,000 characters, printed after them.
- 29 "[Check: ...]" lines in all. 6 caught a real slip (a quote cited to the wrong subsection, or credited to the wrong
  case). 23 flagged words that are real: 8 from the lease, 9 from a printed case, 3 from the tool's own text (two
  posture lines the letter rule says to quote word for word), 1 from the student's own letter, 1 statute sentence
  paired with the cite next to it, and 1 legal bracket ("express[ed]").
- Every student asked, in some form, "so can I or can't I?" and every one asked for the same change: a short plain
  "what to do next" at the top of each answer, with the cases and statute text below or on request.

## What the students said

1. The answer comes last. (6 of 6 chat runs.) The first reply opened with pages of case text, often about injuries
   ("one was a gas explosion, one a kid cut on glass, one a guy shot at his door", Jordan), before a word of answer,
   though Alex had asked for one ("i just want a straight answer"). Later replies were shorter and were praised:
   "that one was way easier to read" (Morgan).
2. Readings without a bottom line. (6 of 6.) "One reading ... The other ... The tool picks neither" came up in nearly
   every legal answer (paying rent as a waiver, "material", the deposit). "I never got what it meant for me" (Alex).
   Asked which letter posture to pick: "The choice is yours; I cannot pick it for you" (Sam; Morgan too wanted a
   pick). Rule 1's "the tenant chooses" is honest, but students read it as no answer.
3. The lease, shown at the right moment, was the most useful thing. Lease 7.2's emergency line for AC above 85
   degrees (A, B: "i should have called it 2.5 weeks ago"); 7.2's portal request not being a notice (A, C, D2, E:
   "That's actually the most useful thing so far", Chris); 3.4, not responsible for a roommate's rent (B: "the
   clearest answer"); 3.2, the late fee growing $10 a day (B: what decided Alex to pay); 7.4, a roommate's damage (E).
4. The warnings cost trust. "[Check: ... is not in 83.51. Check it against the source yourself]" made the tool "look
   broken" (Jordan; also D2, E, F); D2 noticed one flagged its own lease ("That quote is from my lease") and learned to
   ignore them all. "[not verified]" on every case: "ok so why am i reading this" (Jordan).
5. The sheet asks students to make legal calls. "Have you delivered a written notice?" (A, D2, E said yes for portal
   requests; C said no for the same thing, then yes). "Does your written notice say that you intend to end the lease?"
   (F said yes for "If this isn't fixed I'm going to have to move out"). "Caused by you, a member of your household, or
   someone you let in?" (E accepted the suggested yes because a roommate did it). "Structure or plumbing?" for an AC
   ("weird for an AC problem", Jordan) and for a water heater (C said yes). Each answer then decided options, below.
6. Letters were the clearest win, and the template got in the way. Every chat run ended with a letter the student
   planned to send, some after fixing it by hand. But: "Written notice date: September 18, 2026" printed in a letter after the tool
   said the portal request was not a notice (A, D2, E); "sent by by hand" (C, E, F); "I request that you i, Morgan
   Davis, ... am ending my lease" (F); dates the student could not fix from the chat ("I cannot fix those two lines
   from here", D2); the student's own details (the tech visit, the temperature, the doctor's note) left out until
   asked for.
7. Out of scope ends cold. D's whole visit was one yes/no: "no" to "Something in the unit needs repair" ended the
   session, with no warning, and the stop text quoted three lease clauses (6.2, 3.3, 5.1) it "does not apply". D2
   answered yes to keep going and got a repair sheet that did not fit amenities, then honest answers. Nothing covered
   the $85 charge (E), getting a roommate to pay it back, the amenity fee, the ads, or "rent back" as such ("Getting
   rent back is not one of the options the program checks", shown to Jordan).
8. Words a student does not know: preserve, assert, escalate; matter, playbook, "Taken out of your matter; logged";
   `lease_promises_repair` in "Skipped for now"; "the landlord's duty is met" (read as "the landlord did their job");
   "No deadlines: none of the deadlines this tool computes applies" (shown first, to "how long are they allowed to
   leave us without hot water?"); "possession", "registry of the court", "material noncompliance".

What they did not get and expected: a plain word that they may keep paying rent and are not at risk of eviction (A),
whether it is safe to complain while living there (C), a number for rent back or a credit (A, B, C), anything on
roommates unless asked (A, C), the guarantor (A, C, F), where to go after the leasing office or after the reply-by
date (A, B, C, D), free legal help such as UF Student Legal Services (D, F; A and C thought of it on their own), a way
to save or print a letter (B, E), and the timeline (no student typed `timeline` or `issues`; nothing on screen names
them).

## What the program did, for the author

Found in the program's own output; module and function named. Ordered by what it could cost a tenant.

1. A yes on the sheet becomes a done legal step (F). Morgan's e-mail said "If this isn't fixed I'm going to have to
   move out." Morgan answered yes to `notice_states_termination_intent`. `deterministic.check_options` then marked the
   83.56(1) notice steps done and `compute_deadlines` showed `seven_days_after_termination_notice` passed, and the
   reply said "no new step from the statute, since the notice and the 7 days are done." Two things nothing checks: the
   words of the notice (the sheet asks the tenant to characterize them; `add_communication` was never used to record
   them), and the delivery. 83.56(4) as stored allows "e-mailing in accordance with s. 83.505", which needs a signed
   addendum; the playbook's clock lists `delivery: [mailing, delivering a true copy, e-mail per 83.505]`, but
   `written_notice_method` is free text no gate reads. The same path counted portal requests as a delivered notice in
   A, D2, and E, though Lease 7.2 says otherwise and the model said so.
2. Hot water: "Not pay rent ... raise it as a defense" shown OPEN (C). Sam said the water heater is plumbing, which
   meets the gate's only statute way (`problem_is_structure_or_plumbing`). Hot water is in 83.51(2)(a)5, and
   83.51(2)(c) says part II does not let a tenant raise a subsection (2) noncompliance as a defense to possession. The
   playbook's open question `subsection_one_or_two` is on exactly this, but `withhold_rent` does not list it in
   `also_open`, so YOUR OPTIONS showed the option open with no flag. For the author's check of the gates (TODO 84).
3. A roommate as "your household" (E). The question for `caused_by_tenant_side` says "you, a member of your household,
   or someone you let in"; 83.51(4) says "a member of the tenant's family, or other person on the premises with the
   tenant's consent". A roommate the landlord assigned (Lease 1.3) fits "household" to a student, and `fill_facts`
   suggested yes from the description. That closed both repair options until Chris changed it mid-chat.
4. One fact per issue (C). Two repair problems (hot water from Sept 28, AC from Sept 14) share `problem_started`, the
   notice facts, and the options. The sheet asked Sam to pick one date; the letter header was then wrong for the
   other problem.
5. The letter template (`tools.build_letter`). It prints every confirmed date fact under its id ("Written notice date",
   "Problem started", "Planned move out", "Term end date"), which the model cannot change and which contradicted the
   advice in A, D2, and E. It builds `f"I request that you {ask[0].lower() + ask[1:]}."` and `f"This letter is sent by
   {delivery_method}."`, so a first-person ask came out "I request that you i, Morgan Davis, ... am" and a method
   written "by hand ..." came out "sent by by hand". It signs with the profile's `tenant_names` quote, `Jordan Reyes
   ("Resident")`. There is no field for the facts a student wants in the letter; the stand-ins put them into `ask`.
6. "After draft_letter, reply only" (`prompt.LETTER_RULE`). A question asked in the same message as a requested change
   went unanswered: Jordan's "is the written notice date line ok?" and, twice, Morgan's "does this letter count as my
   notice to end the lease?" and "what happens with 4 days' notice instead of 7?", the two questions that mattered
   most before moving out.
7. The quote checker (`replies.check_reply`, `citations.quoted_passages`). 23 of 29 cautions were false, mostly the
   pairing in TODO 64 (a lease or case quote beside a statute cite). New kinds: `LETTER_RULE` tells the model to quote
   the posture lines word for word, and they hold a cite ("Adds the 83.51(1) duty, quoted."), so the program flags
   what its own rule asked for; the playbook's `notice_sufficiency` words and the tenant's own letter were flagged too.
8. Case listings first, and all of them (`wiki.render_cases`, `prompt.CASE_RULE`). A `cases` block prints above the
   reply, every case in full (facts, question, rule, reasoning, related), and rule 8 has the model discuss every case
   printed, so the reply grows with the listing. Topics reach wide: an AC question drew "Landlord's maintenance
   duties under 83.51", whose cases are injury suits. On the web page the cited words fold into an expander; the cases
   do not.
9. The sheet's small things (`sheet.run_sheet`, `sheet.value_of`). An issue row says "suggested because of" but has no
   suggested value, so Enter gives "Please type yes or no" (A, C). "Skipped for now: lease_promises_repair" shows a
   field id. "Taken out of your matter; logged." A sheet mid-chat confirms a changed fact with no word on what it
   changes until the student writes again (E).
10. The deadlines block on any "how many days" (`agent.WHEN_QUESTION`, `deadlines_unasked`): it printed "No deadlines:
   none of the deadlines this tool computes applies to your confirmed facts." above a letter (A) and as the first line
   of the answer to "how long are they allowed to leave us without hot water?" (C).

## What worked

- Options before steps held in every run: AC not in 83.51(1)(b), so the rent defense turns on a code the tenant can
  check, while ending the lease can rest on Lease 7.1 (A, B, F). No reply told a student to withhold rent; B was told
  plainly that withholding "is not safe" and why, and chose to pay.
- `search_lease` found the clauses that mattered most and the program printed them: 7.2, 3.4, 3.2, 7.4, 5.1.
- Deadlines were the clearest block for F: the 7-day notice before moving out had already passed for October 11.
- Nothing was sent; every letter was a draft the student could change, and changes came back right.
- D's stop was honest about scope and quoted the lease's own amenity clauses.
- The stand-ins kept to the rules: no dates worked out, no case named from memory, and unknowns named as unknowns.

## Recommendations, for the author to decide

Nothing in the program was changed by this eval. TODO.md holds these as items 90 to 101 and a note on item 64.

High:
1. A short plain answer first, in every reply: what this means and what can be done now, a few lines, then the rule,
   facts, and readings. Print case listings after the reply, folded on the web page like the cited words, or only
   when asked. Consider letting rule 8 discuss the cases on point rather than every case printed.
2. Do not let a yes/no settle that a notice works. Record the notice's words (`add_communication`) and set them beside
   83.56(1) or 83.60(1)(b); read `written_notice_method` against 83.56(4), 83.505, and the lease's notice clause; and
   treat a portal request as the lease treats it.
3. Fix the letter template: a field for the student's facts; an ask that is not forced into "I request that you";
   "sent by" not doubled; leave out a date line the chat has shown to be in question (or let the tenant correct it in
   place); sign with the name only. Let a reply after `draft_letter` answer a question asked in the same message.
4. Check the gates on three points (TODO 84): hot water and the other 83.51(2) items in `withhold_rent`; "household"
   in the `caused_by_tenant_side` question; and a lease clause that says a portal request is not a notice.

Medium:
5. The quote checker: do not check a posture line or the tool's own notes against the statute; finish TODO 64's
   pairing fix (23 of 29 false here).
6. Plain words for postures (for example "polite request", "cites your rights", "says you may end the lease"), with a
   sentence on when each fits; a glossary line for "possession", "registry of the court", "material".
7. The sheet: Enter on an issue row, no field ids, no "matter" or "logged"; say before a no that ends the visit that it
   will.
8. Say once, at the first chat prompt, that `timeline` and `issues` exist.

Lower, for the plan:
9. Situations students have that no playbook covers: a charge on the ledger the tenant disputes, a roommate who caused
   damage, amenities and fees, services included in rent, and getting rent back (83.56(1)(b), 83.60(1)(b)'s reduction,
   83.55) as an option the program checks.
10. More than one repair problem in a matter, each with its own facts.
11. A line on free help (a legal aid office, student legal services), since the tool itself says it is not a lawyer.

## Questions this eval cannot answer

- How nemotron does on these stories. The students' lines are in `results/*/inputs.json`; the sheet answers and chat
  lines could become `dev/scenarios` files for `dev/eval.py` (they would no longer adapt to the replies).
- How real students read it. Once the unlicensed-practice question is settled, a short usability test with a few
  students and these same stories would check the persona findings.

## Files

- `method/harness.py` (the replay harness), `method/make_lease.py` (the lease and its profile), `method/STUDENT_GUIDE.md`
  and `method/BOT_GUIDE.md` (what the student and stand-in agents were told), `method/personas/` (one per run; D2 used
  D's).
- `results/<run>/`: `screen.txt` (what the student saw), `notes.md` (the student's diary), `evaluation.md` (the
  student's evaluation), `inputs.json` (what the student typed), `model.jsonl` (the stand-in's answers), `run.json`,
  and `program/` (the lease PDF and its profile).
- Replay a run: `python docs/evals/2026-10-06-students/method/harness.py docs/evals/2026-10-06-students/results/A_ac_portal status`
  rebuilds `screen.txt` from `inputs.json` and `model.jsonl` through the current code (it writes `matters/`, `model/`,
  and status files in the run folder; leave them out of a commit). All seven replayed to the same screen on 2026-10-06.
