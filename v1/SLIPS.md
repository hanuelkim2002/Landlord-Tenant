# Slips

The mistake log: what the model does wrong in live runs, counted per eval. These are not work items. The author's rule
(2026-09-27): build structure and code first, log model slips, and tune the prompt later. A slip moves to TODO.md only
when there is a code-side fix to make, or it hurts a tenant and keeps recurring; its entry then says so.

How to log:
- One entry per kind of slip: an example in the model's words, the counts per eval (newest last), and a status:
  watching, code-side option noted, promoted to TODO n, or fixed by item n.
- Seen again: add the count to the entry's line, never a new entry or paragraph.
- Counts come from an eval's record (`docs/evals/...`, `dev/eval_runs/...`); name it.
- Rule numbers are the current rules (version G, 2026-10-02). Items 4 to 23, logged under earlier rule sets, were taken
  off on 2026-10-01 (CHANGELOG says where each went). Numbers are shared with TODO.md and AUTHOR.md and never reused.

Latest blind scoring (2026-10-12, `docs/evals/2026-10-12-skills/`, the skills before and after, rubric revised that
day): legal answers applied well 13.8% before, 12.6% after; slips per reply 2.02 to 3.70 (firm 1.31 to 2.64); helpful
2.50 to 2.84, conversational 2.18 to 2.08. After, firm per 100 replies: offers 42.3, repeated content 38.2, law from
memory 34.6, recited 24.8, asked again 24.6, conditions wrong 12.8 or missed 12.4. Earlier: 2026-10-03,
`docs/evals/2026-10-03-blind/` (36 of 115 applied well).

## What the model states as known

103. The lease's notice clause read as settling an e-mail notice's delivery, which the program leaves to check (an
    83.505 addendum): "Your lease permits notices to be sent by e-mail ... so delivery by e-mail is allowed".
    Counts: 2026-10-08 student e-mail story 2 of 3; 2026-10-11 story F's letter question 1 of 3 before and 1 of 3
    after ("which matches the lease's allowed notice methods"). Also once in the roommate story, the lease's own exception applied
    as settled ("Because the damage is traceable to the roommate, the lease excludes the landlord's repair duty").
    Status: watching; the legal point is AUTHOR.md 84's.
89. A lease searched and then misread: "only mentions late charges in ... Lease Section 3.4" (3.3 sets $75), "The lease
    does not provide a specific holdover penalty" (15.1 sets double rent), "the lease does not forbid it" with no search.
    Counts: 2026-10-04 most of the blind scorers' firm GAP_AS_FACT (21.5 down to 5.5). Status: watching.
70. A prediction the record cannot support: "If my friend picks her up this weekend, am I safe?" answered "you are
    safe". Counts: 2026-10-03 evals 0, 2, 0, 3, then 1 of 3. Status: watching; rule 9 does not name it. (The eval's
    pattern also catches right answers: TODO 87.)

## Dates and deadlines

59. Dates the model works out: "Thirty days after June 30, 2026 is July 30, 2026.", "about 52 days". Counts: 2026-10-02
    blind 12.5, code 4; 2026-10-03 (items 51 to 53) 4 turns; 2026-10-03 (items 54 to 61) 3 turns; 2026-10-12 code 3
    before, 19 after the skills (blind firm 2 and 20). Status: code-side cause in TODO 119 (the program no longer
    prints the deadlines when nothing is dated).
65. Asked when, the model does not call `get_deadlines`. Counts: 2026-10-08 part 2 eval 4 of 46 runs (lease renewal 2,
    leaving early 2); 2026-10-12 after the skills 7 turns failed it in 52 runs. Status: since TODO 114 the program prints
    them only when one has a date; TODO 119.
12. A claim letter's printed date suggested as the date it was received. Counts: 2026-10-01 trial 1 of 3 claim runs;
    2026-10-01 eval 0 of 9. Status: watching; the sheet shows the suggestion and the tenant corrects it.

## Letters

39. A letter request asks again for what the tenant said (the amount, the days, the delivery, today's date). Counts:
    2026-10-01 blind 9 then 6.5; 15 of 21 letters drafted in one confirmation run; 2026-10-02 the carpet letter 0 of 3;
    2026-10-08 part 2 eval 1 letter not drafted; 2026-10-11 story F's change not drafted 1 of 3 before and 1 of 3 after
    ("I cannot add that doctor's-visit detail as a new fact"). Status: code-side option noted: fill the ask from
    confirmed facts.
38. Asked which posture is "the nicest", the model calls preserve "the gentlest option" (rule 6's "Not:"). Counts:
    2026-10-01 2 of 3; 2026-10-03 1 to 3 of 3 in each eval; 2026-10-08 part 2 eval 1; 2026-10-11 2 of 3 ("most
    polite", "the nicest"). Status: watching; TODO 100 may give the postures plain names.
108. A letter drafted with a posture the tenant has not picked: asked "which one is the nicest?", the model drafts a
    preserve letter, then answers (rule 6's first "Not:"). Counts: 2026-10-08 deposit_ghosted 1 of 3; 2026-10-11 2 of 3,
    after rule 6 began letting a reply follow a draft (TODO 96), which may make it easier. Status: watching; a code-side
    option: `draft_letter` refuses a posture the tenant's messages have not named.

## The prompt's own words

88. Prompt part names and ids written in replies: "(WHAT THE STATUTE DOES NOT SETTLE)" as a source, field ids, and the
    options' own words in quote marks. Counts: 2026-10-04 part names 8 to 15 turns, field ids 9 to 17, blind ID 15.5 to
    24.5; 2026-10-08 one "caused_by: a roommate"; 2026-10-11 one "through draft_letter again". Status: watching.
68. A tool's receipt copied into a reply ("The program printed the tenant's deadlines: 0 dated, for no issue. ...").
    Counts: 2026-10-03 once. Status: watching.
69. The sheet's own questions asked in the chat, in quote marks (rule 4's "Not:"). Counts: 2026-10-03 3 of 3, then 0
    of 3. Status: watching.

## Answers and offers

40. "The lease and statute text I have do not answer that." to a legal question no open question covers (whether a
    renewal must be signed by October 15). Counts: 2026-10-03 2 of 3, then 3 of 3. Status: watching; since the rules of
    version H (2026-10-12) there is no fixed line, only "say so plainly and do not guess".
62. Offers the tenant did not ask for, more after a deadline listing. Counts: 2026-10-03 3 then 6 turns in 48 runs.
    2026-10-12: blind OFFER (an offer not the next step, or made again) firm 1 before, 112.5 after the skills, in
    266 replies; 41 of the 127 on the automatic reply after a confirmation. Status: watching; rule 9 of version H asks
    for the next step once; TODO 118 for the automatic reply.
122. A reply that repeats an earlier one (the same conditions, the same steps) instead of building on it: blind
    REPEATED firm 14.5 before, 101.5 after the skills (2026-10-12), 46 of the 115 on the automatic reply after a
    confirmation. Status: code-side cause in TODO 118; scripted chat lines written for the old flow add some (TODO 120).
123. A rule or a reading from memory: a reading of an open question that is not in the skill ("Reading 2: A material
    noncompliance can include a serious breach ... that affects habitability"), a three-day-notice warning no loaded
    skill gives. Blind LAW_UNSOURCED firm 22.5 before, 92 after the skills (2026-10-12). Status: watching.
41. Empty replies. Counts: 2026-10-01 2 and 3 turns in 48 runs; 2026-10-08 part 2 eval 2 turns that were scored.
    Status: watching; `reply_empty` logs the gateway's finish_reason.
