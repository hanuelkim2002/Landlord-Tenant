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
14. `citations.check_quoted` noise seen 2026-09-30 (gpt-oss-120b runs): a clock id in quote marks
   ("claim_notice_deadline" (83.49(3)(a)), m-023) was checked as a statute quote, and an example the model
   offered ("e.g., "repair the air-conditioning unit"", m-022) as a quote of the tenant. Both flagged,
   neither a misquote. Decide whether ids (no spaces, underscores) and "e.g." examples are skipped.

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
    the playbook checks (every quote in its source and at its pin page, every link resolving, every case
    that names a topic listed on that topic's page, a warning for a section the opinion never cites, a
    verification undone by a later edit). Done 2026-10-01: the 16 opinions in `cases/` that cite 83.49 or
    83.48 (pilot of three, then thirteen), 13 topics. Next: the author reads each page against its opinion
    and verifies it (`python wiki.py verify`); only verified pages go further. While verifying, check each
    case's status in Westlaw; the print flags Malagon v. Solari, Guthartz v. Lewis, Durene v. Alcime, and
    Florida Patient's Compensation Fund v. Rowe. Then the other sections' opinions. 50 So. 3d 503 (the
    2010 forms decision) is not in `cases/`: the Westlaw print marks its added and deleted words by
    formatting, which plain text loses; it needs a source that keeps the marks (the court's own opinion)
    before it can be filed.
25. Verified wiki pages for the active playbooks' sections loaded into the prompt, chosen in code by their
    section tags, never by the model; only the court's quoted words go to the tenant, with court, year, and
    the statute version read; one rule for the neutral framing ("This tool does not decide whether it
    applies to you"); `citations.py` learns reporter cites (a cite not in `cases/` gets a caution, and case
    quotes are checked like statute quotes). Consider a reply check for applying language ("applies to
    you", "your case", "you should"), like the cite checks.
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
19. The model repeats a line of the printed deadlines, or says "The deadlines appear above." when the line
    above says there are none (rule 3). Harmless. In the trial the current rules repeated a line in 4 of 18
    replies; after rule 3 named the echo, none of the 6 reruns did (entry, rent: no dates), and one live
    nonpayment run on 2026-10-01 (a dated story, `t-test/m-001`) replied only "The deadlines appear above."
    One dated run is not enough to close this.

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
