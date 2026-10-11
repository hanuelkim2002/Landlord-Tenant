# For the author

What only the author can do: decisions, legal sign-offs, research, and open questions. Claude Code adds an entry here
when work needs the author's call, and moves an entry to the CHANGELOG once the author has acted on it. Numbers are
shared with TODO.md and SLIPS.md and never reused.

## Decisions that hold up work

97. The shape of an answer. In the student simulation (`docs/evals/2026-10-06-students/`) every student asked "so can
    I or can't I?" and asked for a few plain lines first on what this means and what can be done now. Rule 1's order
    held, but an open point ends in two readings and "The tool picks neither", read as no answer. Should a short plain
    summary of the options and the next step for each, still not a choice among them, lead every answer? (TODO 98 waits
    on this in part.)
93. Situations no playbook covers, from the same simulation: a disputed charge on the ledger (a roommate's damage), a
    roommate who caused damage, closed amenities and an amenity fee, a service the rent includes (Wi-Fi), the
    guarantor's exposure, and rent back for the time without a repair (83.56(1)(b), 83.60(1)(b)'s reduction, 83.55).
    Also a no to the only suggested issue ends the visit with no warning, and two students asked where to find free
    help. A new playbook changes README's list.
1. Which clocks `compute_deadlines` should support next: other circuits' court calendars (and each new year's
    memorandum; 2028's for any count reaching it), periods the lease sets (83.575(1)-(2), 83.595(4)), hours (83.53(2)),
    months (83.56(2)'s 12 months), and 83.60(2), which waits on the open questions below.
26. Whether to build `search_cases(phrase)` for a situation no playbook covers: the model would choose what to search
    for. Since 2026-10-02 applying the law is the plan, so what remains is whether its search finds the right cases.

## Sign-offs

106. The letter (TODO 95, CHANGELOG 2026-10-11, option D). The program's lines: "Delivery: " and the method, the signer
    (a tenant the lease names, no label), "Please respond by", the "[CHECK BEFORE YOU SEND, not part of the letter: ...]"
    line under a letter with a date or amount the record does not hold, and the web page's label on a letter; the
    `draft_letter` description the model reads (`python schemas.py`); rule 6's new last lines (TODO 96, the reply after a
    draft answers what else was asked). Also README's non-negotiable "Letters are a code
    template, not model text": the model now writes the account and the request, as it wrote the ask before, with every
    date, amount, and cite in them checked. A wording to adopt or change: "Letters are a code template: the program
    writes the date, the addresses, the reply-by date, the quotes, the delivery line, and the signer; the model writes
    only the tenant's account and request, and every date, amount, and cite in them is checked."
84. The options' gates in all ten playbooks against `statutes/`, then sign off as for item 2. The CHANGELOG entries of
    2026-10-04 (items 72, 81, 84) and 2026-10-08 (the sheet asks plain facts, parts 1 and 2) say what each gate holds.
    Points to look at in particular:
    - repair_not_made: a problem 83.51(1)(b) does not name leaves ending the lease not known yet rather than not settled;
      the duty not changed in writing (single-family home or duplex only); rent paid with knowledge as a gate on ending
      the lease only, and its open question; which `problem_is_with` answers meet 83.51(1)(b), with running water and hot
      water not settled; `caused_by` (the tenant, family, or a guest close both options, though 83.51(4) says
      "negligent or wrongful act or omission"); the open questions `roommate_consent` and `withholding_notice_delivery`;
      83.56(4)'s ways (a portal request or a text not one, e-mail only under an 83.505 addendum, and whether a lease
      clause allowing e-mail notices is enough given 83.505(6)); the lease's repair promise as the tenant's check (item
      86, decided on the session's recommendation); rule 1's two changed "Instead:" examples.
    - deposit_not_returned: a claim notice not by certified mail not settled; the notice before moving out read
      against 83.49(5)'s certified mail or personal delivery. deposit_claim_received: an objection done only as a letter
      to the notice's address.
    - lease_ending: the tenant's notice read against 83.56(4); the 83.575(2) gate met on nothing in writing from the
      landlord about the end of the lease. rent_increased: `complaint_kind` against 83.64(1)(a) to (c); the retaliation
      defense's gates, good cause included. wants_to_leave_early: a fee written only in the lease closes the fee route;
      the fee's "no more than 2 months' rent", left to the tenant to check though both amounts are on the record.
    - landlord_entered_unannounced: 83.55 in its sections, and the seven gates read from 83.53(2). neighbor_disturbance:
      whether a neighbor's disturbance can end the lease only through a lease promise. notice_received_violation: the
      broader earlier-warning question.
    - Every playbook: the questions' and choices' wording, and 83.505 added to five playbooks' sections.
    - Left as they were, for you to say whether any should move: the questions where the tenant reports what a paper
      literally says (`notice_offers_cure`, `notice_terminates_now`, `violation_corrected`, `lease_requires_end_notice`,
      `tenant_consented`, `access_or_utilities_cut`), and whether the defective-notice defense gets a way for a 3-day
      notice not delivered as 83.56(4) allows.
2. Hand check of the seven playbooks written 2026-09-27 (repair_not_made, notice_received_nonpayment,
   notice_received_violation, landlord_entered_unannounced, rent_increased, wants_to_leave_early, lease_ending): read
   each quote against `statutes/`, then set `provenance.verified_by` and `verified_on`. Also replace the deposit
   playbooks' 83.42 exclusion ("Not yet read") with the 83.42(1) quote the newer playbooks carry.
34. `notice_received_violation` does not list 83.64 (retaliatory conduct) in `sections`, though a violation notice after
    a complaint is the setting of Salmonte v. Eilertson; adding it is a playbook change for you to check.
63. Condition slips the blind scorers found (2026-10-02) that no failure mode names yet; which belong in the playbooks,
    each quoted from `statutes/`: 83.49(5) left out where no 7-day vacate notice shows; 83.51(1)(b)'s duties applied
    without its opening condition on codes; a common-area duty (83.51(2)(a)) applied inside the unit; 83.56(5)(a)'s
    waiver applied to the 83.60(1)(b) defense; a rent increase read as a decrease. Also whether wants_to_leave_early's
    `fee_notice_period` needs readings (the model took the lease's 7-day vacate notice as the fee's notice period).
24. The case wiki: read each page against its opinion and verify it (`python wiki.py verify`); untag a page that
    should not load for a tenant (a commercial lease, e.g. Multach v. Adams); check each case's status in Westlaw (the
    print flags 27, one red-striped, Charlemagne v. Francis); and the 65 questions the ingest left in `wiki/log.md`.
49. The author's sample of the first applying eval (`docs/evals/2026-10-02-apply/`, materials in
    `dev/eval_runs/2026-10-02-apply-after/author_sample/`, not committed): is each application right on the law? Mark
    the rubric's categories (`dev/eval_rubric.md`) and right, wrong, or partly; the blind scorers' calls are beside it.

## Research

3. The counting convention, a stated assumption in each playbook: check the time-computation rule in the corpus before
   relying on it. Not to be settled from memory.
27. No appellate case on the 83.42(1) exclusion for residence incidental to educational services turned up in the
    candidate list's sources; it decides whether ch. 83 applies to on-campus housing at all.
28. For the professional responsibility professor: the tool applies the law to a tenant's facts, so what supervision
    or review does it need before any tenant uses it?
37. No case page speaks to damage already there at move-in (the claim_carpet story): a gap for research, not code.

## Open questions

- Counting court business days (83.56(3)): whether the delivery day counts, what happens when the notice is delivered
  on a weekend or a holiday, and when the last day ends. The tool counts forward from the delivery date, the delivery
  day not counted, and labels it an assumption.
- Which holidays are "court-observed holidays only" (83.56(3)): the tool skips every holiday in the circuit Chief
  Judge's memorandum, the Chief Judge's designated and discretionary ones included; and whether 83.60(2)'s "legal
  holidays" is the same list, since 83.56(3) defines the term "for the purpose of this section". Until settled,
  83.60(2) is not computed.
- deposit_not_returned: whether returning keys one day before the term end is "vacating before the expiration of the
  term". The 7-day clock applies whenever `early_or_periodic` is confirmed true.
