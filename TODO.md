# TODO

The working list. Move an item to CHANGELOG.md when it is done, with the date. Reorder freely. Keep the
"Open questions" section for things that need a decision before code is written.

## Now


## Data bank

## Harness and code

Code-side checks and bookkeeping that hold whatever the model does. Ahead of model behavior.

Nothing open.


## Playbooks

1. repair_not_made, notice_received_violation, rent_increased, lease_ending, then
    notice_received_nonpayment, landlord_entered_unannounced, wants_to_leave_early (every label in
    `ISSUE_LABELS` but `other`). Each is a research task against `statutes/`, then `check_all_playbooks` must be all OK,
    then a hand check. Each lists the sections it rests on in `sections` (checked against `statutes/` at
    load). Candidate sections from the project plan, NOT verified, to start the research from:
    repair_not_made 83.51, 83.60, 83.56; notice_received_nonpayment 83.56, 83.60; notice_received_violation
    83.56; landlord_entered_unannounced 83.53, 83.67; rent_increased 83.46; wants_to_leave_early 83.595,
    83.56; lease_ending 83.575, 83.57, 83.58.
2. Counting convention is a stated assumption in each playbook. Check the time-computation rule in the
    corpus before relying on it. Do not settle this from memory.

## Model behavior (later)

Slips seen in live runs. Logged, not fixed yet: rules and prompts get tuned after the structure is right,
and some may go away with a more capable model.

3. The model stated the remit clock's condition backwards: "Landlord's deadline to remit balance if you
    object." 83.49(3)(b) begins "Unless the tenant objects." A rule 13 breach close to the playbook's own
    failure mode (2026-09-27, resume run on `t-test/test-002`). The clock's quote no longer reaches the
    model since only `guidance` is pasted.
4. In the same run the model summarized 83.49 in its own words instead of quoting it (rule 1), and
    added words the sentence does not have ("objects in writing within 15 days").
5. Since only `guidance` is pasted, the model mis-cited the forfeiture sentence as 83.49(3)(b) when
    explaining the escalate posture (it is 83.49(3)(a)). The escalate line in `guidance.postures` names no
    cite.
6. The model compared dates itself when confirming `early_or_periodic` ("Does that mean you moved out one
    day before the lease ended?"). A rule 2 slip, seen once.
7. `classify` false positive: `lease_ending` fires on "my lease ended." Seen in two of four runs.
8. After calling `propose_facts` the model still asks the tenant to confirm in the chat ("Is that
    correct?"), though rule 3 says the sheet does it. Harmless: the sheet follows and is what counts.
9. After calling `propose_facts`, the model told the tenant values were "as you just confirmed" before
    the sheet had run (rule 9). Seen 2026-09-27; the sheet still decided.

## Open questions

- Playbook open question (deposit_not_returned): whether returning keys one day before the term end is
  "vacating before the expiration of the term." The 7-day clock currently applies whenever
  `early_or_periodic` is confirmed true.
