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

## Playbooks

2. Hand check of the seven playbooks written 2026-09-27 (repair_not_made, notice_received_nonpayment,
   notice_received_violation, landlord_entered_unannounced, rent_increased, wants_to_leave_early,
   lease_ending): read each quote against `statutes/`, then set `provenance.verified_by` and `verified_on`.
   Also replace the deposit playbooks' 83.42 exclusion ("Not yet read") with the 83.42(1) quote the new
   playbooks carry.
3. Counting convention is a stated assumption in each playbook. Check the time-computation rule in the
    corpus before relying on it. Do not settle this from memory.

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
29. Which topic the tenant sees is still the model's choice. Asked about lawyers' fees in a deposit case,
    one run of `deposit_cases` called Fees and costs in a suit over the deposit and two called Prevailing
    party fees under 83.48, so the tenant saw different sets of cases. Consider printing every offered topic
    a question could fall under, or a chat command `cases` that lists the topics so the tenant picks.
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

31. A web page in place of the terminal, Claude-style (discussed 2026-10-01): the matters and issues in a
    sidebar, the chat in the middle, the timeline and a drafted letter in a side panel. Streamlit
    recommended (one language; chat, file upload, forms, and a sidebar built in); Chainlit the runner-up
    (closest to Claude's look, but chat-only, so the intake sheet would become yes/no prompts). Not an
    off-the-shelf chat UI (Open WebUI, LibreChat): they connect the tenant to the model directly and skip
    what the program does itself (the sheet, the printed timeline and cases). First, without changing what
    the terminal shows: `sheet.run_sheet`, `agent.show_turn`, and the command loop in `agent.chat` return
    blocks (from program or model; kind: timeline, cases, letter, reply, caution; text) instead of printing,
    and `run.py` prints them. Then the page draws the same blocks, with program output styled apart from
    the model's replies, each reply shown only after `check_reply` (no word-by-word streaming), and the page
    on localhost only until deployment is decided (logins, where `matters/` data lives, the unlicensed-practice
    review).

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
    corrected. (Item 21 was the same slip.)

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
