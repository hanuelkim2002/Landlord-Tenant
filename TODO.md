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

The casebook (README, The unit of legal knowledge). Organized by section, then by the question a court
answered, then by case, each with its rule and reasoning in the court's words. `cases/` (the opinions) comes
first (built 2026-10-01, 81 opinions); then these, in order.

24. Casebook files (`casebook/<section>.yaml`) and their check, run like the playbook checks: every quote
    in its stored opinion, pin pages computed from the opinion's star pages, a warning for a section the
    opinion never cites, the statute year suggested where the court states it. Start with 83.49 and 83.48
    (17 opinions cite one or both): entries drafted with `verified_by` empty, then the author reads each
    case, words its question, sets its status, and verifies it. Only verified entries go further. The two
    forms decisions (50 So. 3d 503, 591 So. 2d 594) are filed as forms. 50 So. 3d 503 is not in `cases/`:
    the Westlaw print marks its added and deleted words by formatting, which plain text loses; it needs a
    source that keeps the marks (the court's own opinion) before it can be filed.
25. Verified casebook entries for the active playbooks' sections loaded into the prompt, like STATUTE
    SECTIONS; one rule for the neutral framing; `citations.py` learns reporter cites (a cite not in
    `cases/` gets a caution, and case quotes are checked like statute quotes).
26. `search_cases(phrase)`, like `search_statute`, for a tenant whose situation fits no playbook ("other").
27. For the author's research: no appellate case on the 83.42(1) exclusion for residence incidental to
    educational services turned up in the candidate list's sources; it decides whether ch. 83 applies to
    on-campus housing at all.

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
