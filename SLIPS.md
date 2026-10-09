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

Latest blind scoring (2026-10-03, `docs/evals/2026-10-03-blind/`): 36 of 115 legal answers applied well (21 of 103 on
2026-10-02); rules restated without their quote 46.5, conditions applied wrong 30.5 (AUTHOR.md 63 holds the ones for
the playbooks), quotes without marks 26, facts not confirmed 21.5, dates worked out 13, cases misread 17.5 or one-sided
13.5 (item 71).

## What the model states as known

103. The lease's notice clause read as settling an e-mail notice's delivery, which the program leaves to check (an
    83.505 addendum): "Your lease permits notices to be sent by e-mail ... so delivery by e-mail is allowed".
    Counts: 2026-10-08 student e-mail story 2 of 3. Also once in the roommate story, the lease's own exception applied
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
    blind 12.5, code 4; 2026-10-03 (items 51 to 53) 4 turns; 2026-10-03 (items 54 to 61) 3 turns. Status: watching;
    rule 3's pairs; the eval's echo and dates-made measures catch it.
65. Asked when, the model does not call `get_deadlines`. Counts: 2026-10-08 part 2 eval 4 of 46 runs (lease renewal 2,
    leaving early 2). Status: fixed for the tenant by item 65 (the program prints the deadlines itself); counted only.
12. A claim letter's printed date suggested as the date it was received. Counts: 2026-10-01 trial 1 of 3 claim runs;
    2026-10-01 eval 0 of 9. Status: watching; the sheet shows the suggestion and the tenant corrects it.

## Letters

39. A letter request asks again for what the tenant said (the amount, the days, the delivery, today's date). Counts:
    2026-10-01 blind 9 then 6.5; 15 of 21 letters drafted in one confirmation run; 2026-10-02 the carpet letter 0 of 3;
    2026-10-08 part 2 eval 1 letter not drafted. Status: code-side option noted: fill the ask from confirmed facts.
38. Asked which posture is "the nicest", the model calls preserve "the gentlest option" (rule 6's "Not:"). Counts:
    2026-10-01 2 of 3; 2026-10-03 1 to 3 of 3 in each eval; 2026-10-08 part 2 eval 1. Status: watching; TODO 100 may
    give the postures plain names.

## The prompt's own words

88. Prompt part names and ids written in replies: "(WHAT THE STATUTE DOES NOT SETTLE)" as a source, field ids, and the
    options' own words in quote marks. Counts: 2026-10-04 part names 8 to 15 turns, field ids 9 to 17, blind ID 15.5 to
    24.5; 2026-10-08 one "caused_by: a roommate". Status: watching.
68. A tool's receipt copied into a reply ("The program printed the tenant's deadlines: 0 dated, for no issue. ...").
    Counts: 2026-10-03 once. Status: watching.
69. The sheet's own questions asked in the chat, in quote marks (rule 4's "Not:"). Counts: 2026-10-03 3 of 3, then 0
    of 3. Status: watching.

## Answers and offers

40. "The lease and statute text I have do not answer that." to a legal question the playbook does not list as open
    (whether a renewal must be signed by October 15). Counts: 2026-10-03 2 of 3, then 3 of 3. Status: watching; the
    line is meant for a question nothing stored speaks to.
62. Offers the tenant did not ask for (rule 9), more after a deadline listing. Counts: 2026-10-03 3 then 6 turns in 48
    runs. Status: watching (`OFFER_WORDS`, rubric OFFER).
41. Empty replies. Counts: 2026-10-01 2 and 3 turns in 48 runs; 2026-10-08 part 2 eval 2 turns that were scored.
    Status: watching; `reply_empty` logs the gateway's finish_reason.

## Intake

42. `classify` adds "other" next to a covered issue for a detail of it (a partial payment with no receipt read as a
    separate problem). Counts: 2026-10-02 3 of 3 rent-notice runs; after the wording fix 2 of 3; the mixed story's real
    second problem now 3 of 3. Status: code-side options noted: keep it, have the classifier quote the separate problem
    and check it is not a fact a playbook asks for, or drop "other" beside covered issues.
