# TODO

The working list. Move an item to CHANGELOG.md when it is done, with the date. Reorder freely. Keep the
"Open questions" section for things that need a decision before code is written.

## Now

1. Split `smoke.py` into an offline part (playbook quotes, elements, deadlines, letter, timeline) that runs
   without the key, and an online part (classify, fill_facts).

## Data bank

2. Tenant / matter structure: `matters/<tenant_id>/<matter_id>/` with an opaque tenant id (never a name or
   email). `matter.json` gains a `tenant` key. `run.py` takes the lease path as input for a new matter instead
   of hard-coding `lease.pdf`. `list_matters`, `load_matter`, `start()`.
3. Resume path: `intake` on an existing matter takes a "what is new" description, adds issues, leaves
   confirmed facts alone, runs `fill_facts` only for unconfirmed elements. Decide the open question below first.
4. Sessions: `session_started` / `session_ended` events in `events.jsonl` (with a session id) so the record
   shows when the tool was used. Transcripts go to `sessions/<id>.jsonl`, outside the evidentiary log.
   The timeline shows sessions only under `full`.

## Skills

5. `related_issues` as structured data so `record_facts` can activate a second playbook mid-conversation.
6. `load_skill(issue)` tool and a skills index in the system prompt, replacing the pasted guidance.
    Statute text on demand too, every fetch logged (already the case for lookups).

## Playbooks

7. repair_not_made, notice_received_violation, rent_increased, lease_ending. Each is a research task
    against `statutes/`, then `check_all_playbooks` must be all OK, then a hand check.
8. Reword `guidance.postures.notice_sufficiency` in deposit_not_returned.yaml to face the tenant (it
    currently ends with an instruction to the model).

## Guards and known issues

9. Code-side `confirm_facts` guard for rule 9 (the model once recorded a fact without asking).
10. `classify` false positive: `lease_ending` fires on "my lease ended." Becomes real when that playbook exists.
    Even now it adds 83.57, 83.575, and 83.58 to the prompt, since `ROUTING` preloads sections for issues
    with no playbook.
11. `check_elements` should flag a tenant fact that contradicts a lease field (tenant's end date vs. `term_end`).
12. Counting convention is a stated assumption in each playbook. Check the time-computation rule in the
    corpus before relying on it. Do not settle this from memory.
13. Between test runs, delete the test matter's `events.jsonl` or use a new matter id.
14. `build_letter` prints two periods when the ask already ends in one ("...FL 32601..").
15. The model compared dates itself when confirming `early_or_periodic` ("Does that mean you moved out one
    day before the lease ended?"). A rule 2 slip, seen once.
16. `timeline full` shows a corrected fact with the proposal's tag: `early_or_periodic = False` appears as
    "inferred" though the tenant corrected the inferred `true`. The event holds `proposed_value`, so this is
    display only.

## Open questions

- Resume: what does `intake` classify on a returning matter? Rerunning `classify` on the old description
  recreates the old issues. Proposed: a new description of what is new, issues added, never removed.
- Playbook open question (deposit_not_returned): whether returning keys one day before the term end is
  "vacating before the expiration of the term." The 7-day clock currently applies whenever
  `early_or_periodic` is confirmed true.
