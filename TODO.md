# TODO

The working list. Move an item to CHANGELOG.md when it is done, with the date. Reorder freely. Keep the
"Open questions" section for things that need a decision before code is written.

## Now


## Data bank

## Harness and code

Code-side checks and bookkeeping that hold whatever the model does. Ahead of model behavior.

1. Clocks `compute_deadlines` cannot compute yet, found writing the seven playbooks. Each is recorded, quoted,
   and left uncomputed: (a) days "excluding Saturday, Sunday, and legal holidays", with legal holidays
   "court-observed holidays only" (83.56(3), 83.60(2)); needs a court holiday calendar, researched, not from
   memory; (b) periods the lease sets (83.575(1)-(2), 83.595(4)); needs a clock whose length is a confirmed
   fact; (c) hours (83.53(2)); (d) months (83.56(2), 12 months). Decide which to support.
2. Fold the draft-playbook checks into `corpus.check_all_playbooks`: every quotation of 20 or more characters
   in guidance and open questions verbatim in `statutes/`; every element has a question and every question an
   element; `applies_if` names a yes/no fact; clock cites are in `sections`; a fact id shared by playbooks has
   the same type and question. They ran as a one-off script for the seven new playbooks.


## Playbooks

3. Hand check of the seven playbooks written 2026-09-27 (repair_not_made, notice_received_nonpayment,
   notice_received_violation, landlord_entered_unannounced, rent_increased, wants_to_leave_early,
   lease_ending): read each quote against `statutes/`, then set `provenance.verified_by` and `verified_on`.
   Also align the two `claim_notice_date` questions in the deposit playbooks, and replace the deposit
   playbooks' 83.42 exclusion ("Not yet read") with the 83.42(1) quote the new playbooks carry.
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

## Open questions

- Playbook open question (deposit_not_returned): whether returning keys one day before the term end is
  "vacating before the expiration of the term." The 7-day clock currently applies whenever
  `early_or_periodic` is confirmed true.
