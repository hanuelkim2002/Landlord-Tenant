# TODO

The working list. Move an item to CHANGELOG.md when it is done, with the date. Reorder freely. Keep the
"Open questions" section for things that need a decision before code is written.

## Now


## Data bank

## Harness and code

Code-side checks and bookkeeping that hold whatever the model does. Ahead of model behavior.

1. A wrongly classified issue stays forever (issues are only added) and keeps asking its questions. Deadlines
   no longer block on it (computed per issue since 2026-09-28). Decide how an issue can be confirmed or
   removed by the tenant, logged, never deleted.
2. Clocks `compute_deadlines` cannot compute yet: (a) court business days are done for 83.56(3) in the
   Eighth Judicial Circuit, 2026 and 2027; other circuits need their own memoranda (add a county's circuit
   when a tenant there uses the tool), and each new year's memorandum must be added when the circuit
   publishes it (the 2028 one is needed for any count reaching January 2028); 83.60(2) waits on the open
   question below; (b) periods the lease sets (83.575(1)-(2), 83.595(4)); needs a clock whose length is a
   confirmed fact; (c) hours (83.53(2)); (d) months (83.56(2), 12 months). Decide which to support.


## Playbooks

3. Hand check of the seven playbooks written 2026-09-27 (repair_not_made, notice_received_nonpayment,
   notice_received_violation, landlord_entered_unannounced, rent_increased, wants_to_leave_early,
   lease_ending): read each quote against `statutes/`, then set `provenance.verified_by` and `verified_on`.
   Also replace the deposit playbooks' 83.42 exclusion ("Not yet read") with the 83.42(1) quote the new
   playbooks carry.
4. Counting convention is a stated assumption in each playbook. Check the time-computation rule in the
    corpus before relying on it. Do not settle this from memory.

## Model behavior (later)

Slips seen in live runs. Logged, not fixed yet: rules and prompts get tuned after the structure is right,
and some may go away with a more capable model.

5. The model stated the remit clock's condition backwards: "Landlord's deadline to remit balance if you
    object." 83.49(3)(b) begins "Unless the tenant objects." A rule 13 breach close to the playbook's own
    failure mode (2026-09-27, resume run on `t-test/test-002`). The clock's quote no longer reaches the
    model since only `guidance` is pasted.
6. In the same run the model summarized 83.49 in its own words instead of quoting it (rule 1), and
    added words the sentence does not have ("objects in writing within 15 days").
7. Since only `guidance` is pasted, the model mis-cited the forfeiture sentence as 83.49(3)(b) when
    explaining the escalate posture (it is 83.49(3)(a)). The escalate line in `guidance.postures` names no
    cite.
8. The model compared dates itself when confirming `early_or_periodic` ("Does that mean you moved out one
    day before the lease ended?"). A rule 2 slip, seen once.
9. `classify` false positive: `lease_ending` fires on "my lease ended." Seen in two of four runs.
10. After calling `propose_facts` the model still asks the tenant to confirm in the chat ("Is that
    correct?"), though rule 3 says the sheet does it. Harmless: the sheet follows and is what counts.
11. After calling `propose_facts`, the model told the tenant values were "as you just confirmed" before
    the sheet had run (rule 9). Seen 2026-09-27; the sheet still decided.
12. Reporting the 83.56(3) court-day date, the model did not show the date the notice itself states next
    to it, as the playbook's failure modes ask, and closed with "Would you like to proceed with any action
    based on this deadline?" (live run 2026-09-27, `t-test/m-002`). The timeline shows both dates.
13. Explaining the escalate posture for repair_not_made, the model said the tenant "may terminate the lease
    under Fla. Stat. 83.56(1)" (rule 13); the playbook only says the posture adds the quoted sentence
    (2026-09-28, repair scenario).
14. In the claim scenario the model suggested the letter's printed date (2026-09-22) as the date it was
    received; the sheet asked and the tenant's typed 2026-09-25 replaced it (logged as corrected).

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
