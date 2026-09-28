# TODO

The working list. Move an item to CHANGELOG.md when it is done, with the date. Reorder freely. Keep the
"Open questions" section for things that need a decision before code is written.

## Now


## Data bank

## Skills

1. `related_issues` as structured data so a fact confirmed on the sheet can activate a second playbook
   mid-conversation.
2. `load_skill(issue)` tool and a skills index in the system prompt, replacing the pasted guidance.
   Statute text on demand too, every fetch logged (already the case for lookups). An issue's sections come
   from its playbook (`statutory_hook`), not from `ROUTING`, which keeps only the labels `classify` can
   pick. This replaces preloading from `ROUTING`, which today pastes sections even for a label with no
   playbook yet (a `lease_ending` label adds 83.57, 83.575, and 83.58, unverified). Left as is until then,
   since every label but `other` will get a playbook (decided 2026-09-27).

## Harness and code

Code-side checks and bookkeeping that hold whatever the model does. Ahead of model behavior.

3. `build_letter` prints two periods when the ask already ends in one ("...FL 32601..").
4. `timeline full` shows a corrected fact with the proposal's tag: `early_or_periodic = False` appears as
   "inferred" though the tenant corrected the inferred `true`. The event holds `proposed_value`, so this is
   display only.
5. Between test runs, delete the test matter's `events.jsonl` or use a new matter id. Test matters now:
    `t-test/test-001` (one issue, used by the smoke scripts), `t-test/test-002` (two issues, after resume),
    `t-4c4d2e/m-001` (made by the new-matter run).

## Playbooks

6. repair_not_made, notice_received_violation, rent_increased, lease_ending, then
    notice_received_nonpayment, landlord_entered_unannounced, wants_to_leave_early (every `ROUTING` label
    but `other`). Each is a research task against `statutes/`, then `check_all_playbooks` must be all OK,
    then a hand check. Each lists the sections it rests on in `statutory_hook`, checked against
    `statutes/`, replacing the unverified `ROUTING` list for that label.
7. The two deposit playbooks name the same fact twice: `claim_notice_date` (deposit_not_returned) and
    `claim_notice_received_on` (deposit_claim_received) both ask when the tenant received the landlord's
    notice. Facts carry across issues only by id, so the tenant is asked twice (seen live 2026-09-27).
    Rename one in its playbook, then run the quote check.
8. Counting convention is a stated assumption in each playbook. Check the time-computation rule in the
    corpus before relying on it. Do not settle this from memory.
9. Reword `guidance.postures.notice_sufficiency` in deposit_not_returned.yaml to face the tenant (it
    currently ends with an instruction to the model).

## Model behavior (later)

Slips seen in live runs. Logged, not fixed yet: rules and prompts get tuned after the structure is right,
and some may go away with a more capable model.

10. The model stated the remit clock's condition backwards: "Landlord's deadline to remit balance if you
    object." 83.49(3)(b) begins "Unless the tenant objects." A rule 13 breach close to the playbook's own
    failure mode (2026-09-27, resume run on `t-test/test-002`). The clock's quote no longer reaches the
    model since only `guidance` is pasted.
11. In the same run the model summarized 83.49 in its own words instead of quoting it (rule 1), and
    added words the sentence does not have ("objects in writing within 15 days").
12. Since only `guidance` is pasted, the model mis-cited the forfeiture sentence as 83.49(3)(b) when
    explaining the escalate posture (it is 83.49(3)(a)). The escalate line in `guidance.postures` names no
    cite.
13. After `record_facts` turned `seven_day_notice_given` to n/a, the model still asked its question. It
    had the intake-time ELEMENT STATUS in the prompt, where that row was proposed.
14. The model compared dates itself when confirming `early_or_periodic` ("Does that mean you moved out one
    day before the lease ended?"). A rule 2 slip, seen once.
15. `classify` false positive: `lease_ending` fires on "my lease ended." Seen in two of four runs.
16. After calling `propose_facts` the model still asks the tenant to confirm in the chat ("Is that
    correct?"), though rule 3 says the sheet does it. Harmless: the sheet follows and is what counts.

## Open questions

- Playbook open question (deposit_not_returned): whether returning keys one day before the term end is
  "vacating before the expiration of the term." The 7-day clock currently applies whenever
  `early_or_periodic` is confirmed true.
