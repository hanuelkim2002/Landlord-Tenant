# TODO

The working list. Move an item to CHANGELOG.md when it is done, with the date. Reorder freely. Keep the
"Open questions" section for things that need a decision before code is written.

## Harness and code

Code-side checks and bookkeeping that hold whatever the model does. Ahead of model behavior.

1. Clocks `compute_deadlines` cannot compute yet: (a) court business days are done for 83.56(3) in the
   Eighth Judicial Circuit, 2026 and 2027; other circuits need their own memoranda (add a county's circuit
   when a tenant there uses the tool), and each new year's memorandum must be added when the circuit
   publishes it (the 2028 one is needed for any count reaching January 2028); 83.60(2) waits on the open
   question below; (b) periods the lease sets (83.575(1)-(2), 83.595(4)); needs a clock whose length is a
   confirmed fact; (c) hours (83.53(2)); (d) months (83.56(2), 12 months). Decide which to support.

33. Some live sessions crash on their first attempt and pass on the second: 6 of 48 runs on the code before
    the eval changes and 3 of 48 after (2026-10-01), three of them one mixed story. Two causes found: malformed
    JSON (now asked for again) and a line break inside a quoted JSON string (the mixed story; now accepted,
    `strict=False`). The other screens were written over; the eval now keeps a crashed first attempt's screen.
    Read the next ones before changing anything.

## Playbooks

2. Hand check of the seven playbooks written 2026-09-27 (repair_not_made, notice_received_nonpayment,
   notice_received_violation, landlord_entered_unannounced, rent_increased, wants_to_leave_early,
   lease_ending): read each quote against `statutes/`, then set `provenance.verified_by` and `verified_on`.
   Also replace the deposit playbooks' 83.42 exclusion ("Not yet read") with the 83.42(1) quote the new
   playbooks carry.
3. Counting convention is a stated assumption in each playbook. Check the time-computation rule in the
    corpus before relying on it. Do not settle this from memory.

34. For the author: `notice_received_violation` does not list 83.64 (retaliatory conduct) in `sections`. A
    violation notice that follows a tenant's complaint is the setting of Salmonte v. Eilertson; in the eval
    (cases_retaliation) its case topic was offered only because the story also confirmed repair_not_made.
    Adding the section is a playbook change for the author to check against `statutes/`.

43. No lease profile field holds a conduct, nuisance, or vehicle clause (the test lease has them at 5.2 and
    5.4), so the model cannot quote the lease's own rule in a neighbor_disturbance chat or letter; only the
    stop text shows such clauses, by code. Consider a `conduct_and_use` field in `lease.LeaseProfile` (a
    change to extraction: every lease would be read again).

## Case law

The case wiki (README, The unit of legal knowledge): linked markdown pages in `wiki/`, one per case and one
per topic, with topics made as they emerge from the cases, not fixed in advance. `cases/` (the opinions,
built 2026-10-01, 81 opinions) comes first; then these, in order.

24. The case wiki and its checks: a schema page, an index built by code, a log, and code checks run like
    the playbook checks. Done 2026-10-01: every opinion in `cases/`, 81 case pages and 40 topics (28 case
    pages untagged, with scope notes). Next: the author reads each page against its opinion and verifies it
    (`python wiki.py verify`); only verified pages go further, and only tagged ones ever load for a tenant,
    so untag a page that should not (a commercial lease, e.g. Multach v. Adams). While verifying, check each case's status in
    Westlaw (the print flags 27 opinions; one red-striped, Charlemagne v. Francis), and look at the questions
    the ingest left in `wiki/log.md` (2026-10-01, the remaining 65).
29. Which topic the tenant sees is still the model's choice (in the eval of 2026-10-01 each court question
    got the same topic in every run, item 36). Asked about lawyers' fees in a deposit case,
    one run of `deposit_cases` called Fees and costs in a suit over the deposit and two called Prevailing
    party fees under 83.48, so the tenant saw different sets of cases. Consider printing every offered topic
    a question could fall under, or a chat command `cases` that lists the topics so the tenant picks.
35. Case topics per playbook are many and mixed: 13 for the deposit playbooks, 27 for repair_not_made, among
    them procedural topics (Points not raised in the trial court, Applying an amended statute) and deposit
    topics under the rent-notice playbooks, because a topic is offered when any page tagged with one of the
    playbook's sections is on it. Consider sections on the topic pages (or a topic list per playbook) before
    any topic list is shown to a tenant (item 36).
36. Cases reach a tenant only when the tenant asks what courts or judges said (rule 8). In the eval
    (2026-10-01) plain questions ("Has this happened to other people? Did a judge ever ...") reached
    `get_cases` on a topic whose cases include the one with facts like the tenant's in 17 of 18 runs before
    the changes and 16 of 18 after (one count copied into the topic name, since accepted by
    `tools.topic_named`; one statute answer). A tenant who never asks never sees them. If that matters, a line
    the program prints, listing the case topics for the confirmed issues, keeps the choice with the tenant;
    do it after item 35. Not built: the model saying a case supports or fits the tenant (Brumbaugh, discussed
    2026-10-01).
37. No case page speaks to damage that was already there at move-in (the claim_carpet story). Asked "Did a
    judge ever make a landlord give back money for damage that was already there?", the model printed the
    notice-of-claim topic, the nearest deposit topic. A gap for the author's research, not a code change.
26. `search_cases(phrase)`, like `search_statute`, for a tenant whose situation fits no playbook ("other").
    Reconsider before building: here the model, not code, decides what to look for from the tenant's
    story, which is selection by judgment, the unlicensed-practice risk discussed 2026-10-01 (Brumbaugh:
    general information is allowed, applying law to one person's facts is not).
27. For the author's research: no appellate case on the 83.42(1) exclusion for residence incidental to
    educational services turned up in the candidate list's sources; it decides whether ch. 83 applies to
    on-campus housing at all.
28. For the author's professional responsibility professor: computing a tenant's own deadline from their
    facts (`compute_deadlines`) is arguably closer to applying law to facts than anything in the case
    plan. The tool shows the counting rule and labels it an assumption; whether that is enough is open.

## Interface

45. The web page (`app.py`), limits seen while building it (2026-10-02): reopening a matter does not show
    earlier sessions' chats (the terminal does not either; the transcripts are in `sessions/`); one browser
    tab at a time, since every tab of the one Streamlit program shares `record.matter`; closing the tab
    leaves the session with no `session_ended`, as a crash does in the terminal; a file the tenant wants
    stored goes in only by its path, through the model's `add_artifact`, not by upload on the page.

## Model behavior (later)

Slips seen in live runs and not fixed yet. Rule numbers are the current rules (version F, adopted
2026-10-01). Items 4 to 23, logged under earlier rule sets, were taken off on 2026-10-01: most are now
handled in code (deadlines printed by the program, the empty-reply retry, the duplicate-draft stop, the
quote and cite checks) or by the current rules, which showed none of those slips in the trial
(`docs/trials/2026-10-01-rules/`). CHANGELOG.md (2026-10-01) says where each went. Item numbers are never
reused, so older references (smoke check names, the changelog) still point to the right slip.

12. The model suggests a claim letter's printed date as the date it was received (`claim_notice_date`; the
    printed date is `claim_notice_dated`). Still seen with the current rules: 1 of 3 claim runs in the trial
    (the old rules also 1 of 3). The sheet shows the suggestion and the tenant corrects it, logged as
    corrected. (Item 21 was the same slip.) Not seen in the eval of 2026-10-01: claim_carpet, whose letter is
    dated three days before it arrived, got the right suggestion in all 9 runs (3 per side, and the first baseline).

38. Asked which posture is "the nicest", the model calls preserve "the gentlest option" (2 of 3
    deposit_ghosted after-runs, 2026-10-01), though rule 6 has that "Not:". Scored POSTURE_OWN_WORDS.
39. Letter requests: the model still asks again for something the tenant said (the amount, the days, the
    delivery) in about 1 in 3 letter runs (blind scorers: 9 slips before the changes, 6.5 after, 2026-10-01),
    and in the confirmation run it asked "is that correct?" until the scripted tenant ran out of lines (15 of
    21 letters drafted, against 20 of 21 the run before). A code-side option: fill the ask from confirmed
    facts (the deposit amount, the forwarding address) so fewer details are left to ask. On 2026-10-02 the
    carpet story's letter was drafted in 0 of 3 runs: asked again "What do you want the landlord to do?", asked
    for today's date (the letter fills it in), and once asked the tenant to quote the lease's notices clause
    (rule 6's "quote the notices clause" read as an instruction to the tenant). Now the most common miss. Seen
    again in the web page's live check (2026-10-02): asked for the forwarding address (fair: the ask needs it),
    then for today's date.
40. "The lease and statute text I have do not answer that." to a legal question the playbook does not list
    as open (whether the renewal must be signed by October 15; changing the locks): the blind scorers count
    it as LAW under the rubric's literal rule (12 of 38 after-runs' LAW calls, most marked borderline). Decide
    whether this line is the wanted answer there or the quote-then-"does not decide" form is.
41. Empty replies remain rare (2 and 3 turns in 48 runs before and after, 2026-10-01); `reply_empty` now logs
    the gateway's finish_reason, so the next ones show whether the model or the gateway left them empty.

42. Classify adds "other" next to a covered issue for a detail of it: after the wording fix, still 2 of 3
    rent-notice runs (3 of 3 on 2026-10-02; a partial payment with no receipt read as a separate problem), while the mixed story
    (a heater and a remark about religion) now gets "other" in 3 of 3 (was 0 of 6). The note it triggers is
    mild ("may not be covered ... continues with what it does cover"). Options: keep it; ask the classifier
    to quote the separate problem and check the quote is not a fact a playbook asks for; or drop "other"
    beside covered issues again.

## Open questions

- Counting court business days (83.56(3)), for the author to research: whether the delivery day counts,
  what happens when the notice is delivered on a weekend or a holiday, and when the last day ends. The tool
  counts forward from the delivery date, the delivery day not counted, and labels it an assumption.
- Which holidays are "court-observed holidays only" (83.56(3)): the tool skips every holiday in the circuit
  Chief Judge's memorandum, including those marked as designated by the Chief Judge and the additional
  discretionary ones. And whether 83.60(2)'s "legal holidays" is the same list, since 83.56(3) defines the
  term "for the purpose of this section". Until settled, 83.60(2) is not computed.
- Playbook open question (deposit_not_returned): whether returning keys one day before the term end is
  "vacating before the expiration of the term." The 7-day clock currently applies whenever
  `early_or_periodic` is confirmed true.
