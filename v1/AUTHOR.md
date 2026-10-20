# For the author

What only the author can do: decisions, legal sign-offs, research, and open questions. Claude Code adds an entry here
when work needs the author's call, and moves an entry to the CHANGELOG once the author has acted on it. Numbers are
shared with TODO.md and SLIPS.md and never reused.

## Decisions that hold up work

121. After the skills (eval of 2026-10-12, `docs/evals/2026-10-12-skills/`): on nemotron the tool reads the lease and is
    rated a little more helpful (2.50 to 2.84), but slips per reply rose from 2.02 to 3.70: law from memory twice as
    often, offers in most replies, conditions applied wrong or missed more, dates worked out, an option's steps before
    whether it is open (0.9 to 4.5 per 100 replies). Decide the next step: try a stronger agent model on the same
    stories (`AGENT_MODEL`), bring back a small code check for the slips that hurt a tenant most (an option's steps
    before whether it is open, dates), or both; and whether to keep the automatic reply (TODO 118).
117. The rules of version H (`docs/structure/2026-10-12-rules.txt`, in `prompt.py` since TODO 114). The review of
    2026-10-11 and 12 agreed the opening, the format paragraph, and rules 1 to 4, and paused at rule 5 (suggested, not
    agreed). Rule 5, the skills paragraph, and rules 6 to 9 were written in the same style to finish the plan: read them
    and change what you want. Rule 9 now asks for the next step once instead of offering nothing.
93. Situations no skill covers, from the same simulation: a disputed charge on the ledger (a roommate's damage), a
    roommate who caused damage, closed amenities and an amenity fee, a service the rent includes (Wi-Fi), the
    guarantor's exposure, and rent back for the time without a repair (83.56(1)(b), 83.60(1)(b)'s reduction, 83.55).
    Also a no to the only suggested issue ends the visit with no warning, and two students asked where to find free
    help. A new skill changes README's list.
1. Which clocks `compute_deadlines` should support next: other circuits' court calendars (and each new year's
    memorandum; 2028's for any count reaching it), periods the lease sets (83.575(1)-(2), 83.595(4)), hours (83.53(2)),
    months (83.56(2)'s 12 months), and 83.60(2), which waits on the open questions below.
26. Whether to build `search_cases(phrase)` for a situation no skill covers: the model would choose what to search
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
    only the tenant's account and request, and every date, amount, and cite in them is checked." (README took close
    to this wording on 2026-10-12, with the architecture change; change it if you prefer another.)
84. Sign off each skill in `skills/` (read every quote against `statutes/`, then set `provenance.verified_by` and
    `verified_on`), the playbooks' content in prose since 2026-10-12 (TODO 110 to 113; this takes in old item 2, the
    hand check of the seven playbooks of 2026-09-27). Points to look at in particular, each in the skill's "What the
    tenant can do", "What to find out", or "What the statute does not settle":
    - repair_not_made: a problem 83.51(1)(b) does not name (ending the lease then turns on the lease's promise or a
      code); the duty changed in writing only for a single-family home or duplex; rent paid with knowledge as a
      condition on ending the lease only, and its readings; running water and hot water as plumbing or 83.51(2)(a); who
      caused it (the tenant, family, or a guest under 83.51(4), and the roommate readings); how the tenant's message
      was delivered (83.56(4), a portal request or a text, e-mail only under an 83.505 addendum, and the rent notice's
      delivery readings).
    - deposit_not_returned: a claim notice not by certified mail; the notice before moving out against 83.49(5), and
      the 83.42(1) quote now in its exclusion. deposit_claim_received: an objection sent only as a letter to the
      notice's address.
    - lease_ending: the tenant's notice against 83.56(4); the 83.575(2) condition. rent_increased: the kinds of
      complaint against 83.64(1)(a) to (c); the retaliation defense, good cause included. wants_to_leave_early: a fee
      written only in the lease; the fee's "no more than 2 months' rent", now for the model to set beside the rent.
    - landlord_entered_unannounced: 83.55, and the entry conditions read from 83.53(2). neighbor_disturbance: ending the
      lease only through a lease promise. notice_received_violation: the earlier-warning question.
    - Every skill: what it has the model ask (plain facts, never a legal conclusion), and its cross-references.
34. `skills/notice_received_violation.md` does not list 83.64 (retaliatory conduct) in `sections`, though a violation notice
    after a complaint is the setting of Salmonte v. Eilertson; adding it is a skill change for you to check.
63. Condition slips the blind scorers found (2026-10-02) that no failure mode names yet; which belong in the skills (Mistakes to avoid),
    each quoted from `statutes/`: 83.49(5) left out where no 7-day vacate notice shows; 83.51(1)(b)'s duties applied
    without its opening condition on codes; a common-area duty (83.51(2)(a)) applied inside the unit; 83.56(5)(a)'s
    waiver applied to the 83.60(1)(b) defense; a rent increase read as a decrease. Also whether `skills/wants_to_leave_early.md`
    needs readings of the fee's notice period under What the statute does not settle (the model took the lease's 7-day vacate
    notice as the fee's notice period).
24. The case wiki: read each page against its opinion and verify it (`python wiki.py verify`); untag a page that
    should not load for a tenant (a commercial lease, e.g. Multach v. Adams); check each case's status in Westlaw (the
    print flags 27, one red-striped, Charlemagne v. Francis); and the 65 questions the ingest left in `wiki/log.md`.
49. The author's sample of the first applying eval (`docs/evals/2026-10-02-apply/`, materials in
    `dev/eval_runs/2026-10-02-apply-after/author_sample/`, not committed): is each application right on the law? Mark
    the rubric's categories (`dev/eval_rubric.md`) and right, wrong, or partly; the blind scorers' calls are beside it.

## Research

3. The counting convention, a stated assumption in each skill's header: check the time-computation rule in the corpus before
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
