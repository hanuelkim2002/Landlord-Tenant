# Documentation

How the code works right now. Kept by Claude Code so that a session does not have to read every module to
get oriented. Update it whenever a function, tool, file, event kind, or rule changes. Describe what exists,
not what is planned (that is TODO.md) or what changed (that is CHANGELOG.md).

## Modules

Listed from the bottom of the import chain up. Every module imports `config`. Everything imports without
`UF_API_KEY`; only a model call needs it (see Running and testing).

- `config.py`: paths (`ROOT`, `MATTERS`, `STATUTES`, `PLAYBOOKS`), the two model clients (`agent_llm` on
  `AGENT_MODEL`, `extract_llm` on `EXTRACT_MODEL`, both on the UF gateway at temperature 0), and `squash`
  (collapse whitespace, lowercase; used for every quote comparison). Reads `.env` with python-dotenv. The
  two clients are `None` when `UF_API_KEY` is missing; `require_key()` raises with a clear message then,
  and `run.py` and `smoke_online.py` call it first. Imports nothing from the project.
- `lease.py`: lease intake. `ingest_pdf(pdf_path, matter_dir)` (store the PDF under its hash in the folder
  it is given, extract page text with PyPDF2, write `pages.json`), the `Clause` and `LeaseProfile` shapes (fifteen named clauses), `extract_profile`
  (one call to `extract_llm`), `quote_found` and `check_quotes` (each quote must appear on its cited page,
  or start there and run onto the next). Imports `config`. Imported by `record` and `run.py`.
- `corpus.py`: the stored corpus, loaded once at import. `statute` (dict, section number to text, from
  `statutes/83.*.txt`), the playbook shapes (`Element`, `Clock`, `Spec`, `Playbook`), `load_playbook`,
  `check_playbook`, `check_all_playbooks`, and `playbooks` (dict, issue to `Playbook`, from
  `playbooks/*.yaml`). No model calls. Imports `config`, `lease` (for `LeaseProfile`, to check
  `compare_to`). Imported by `record`, `tools`, `agent`, `sheet`, `smoke`.
- `deterministic.py`: `check_elements` (element status), `lease_value` and `lease_differs` (a lease quote
  read as a date or an amount, and compared with the tenant's value), `compute_deadlines` (the only date arithmetic), `matter_deadlines` (every playbook's
  deadlines, with one that two playbooks share listed once, tagged with both issues),
  `ISSUE_LABELS` (the labels `classify` can pick), and the two one-shot intake calls `classify` and
  `fill_facts`, both through `ask_json` on `agent_llm`. Imports `config`. Imported by `record`,
  `timeline`, `tools`, `agent`, `smoke`.
- `record.py`: the shared state. `matter` and `profile` live here and every other module reaches them as
  `record.matter` and `record.profile`. `confirm_fact` (the only code that writes a confirmed fact),
  `prune_proposals` (drops suggestions that can never be asked; see Data flow 3), `add_issues(issues,
  source, because)` (the only code that adds an issue; never removes one; logs `issue_added`),
  `add_related_issues()` (adds every issue a related_issues rule of an active playbook points to once its
  fact is confirmed with the rule's value, repeating until nothing new is added; returns what it added),
  `matter_dir` (the only function that knows the folder layout),
  `new_tenant_id` (random `t-` plus six hex characters), `new_matter_id(tenant_id)` (`m-001`, `m-002`, ...
  counting the tenant's `m-*` folders), `list_matters` (every saved matter as `{"tenant", "id", "issues"}`,
  nothing else read out), `load_matter(tenant_id, matter_id)` (replaces `matter` from `matter.json` and
  `profile` from `lease_profile.json`, or `None` if there is none; raises `FileNotFoundError` for a matter
  that does not exist), `save` (writes `matter.json`), `append_event` and `read_events`
  (`events.jsonl`), `active_playbooks`, `element_status`. The starting `matter` is the test matter,
  tenant `"t-test"`, id `"test-001"`, used by the smoke scripts through `load_matter`. `new_matter(tenant_id)`
  replaces `matter` with an empty one under the next matter id and clears `profile`; `run.py` calls it.
  `session` holds the open session's id or `None`; `start_session(how)` opens one (a new time-ordered
  uuid7) and logs `session_started`, `end_session()` logs `session_ended` and clears it. While a session is
  open, `append_event` adds its id to every event. `append_transcript(entry)` writes one line to the open
  session's transcript (does nothing with no session open). `tenant_words()` returns the tenant's lines from the open session's
  transcript.
  Imports `config`, `corpus`, `deterministic`, `lease`. Imported by `timeline`, `tools`, `agent`, `run`,
  `smoke`, `smoke_online`.
- `timeline.py`: `render_timeline(issue, full)`, the DATE / EVENT / SOURCE / FILE table, plus helpers
  `label`, `corrected` (the tenant confirmed a different value from the suggestion, compared as shown),
  and `confirmation_of`. A confirmed date's SOURCE reads "tenant (corrected, ...)" when corrected, and in
  `timeline full` a corrected fact reads "corrected from <how> <suggested value>". Not a tool; only the chat loop and `smoke.py` call it. Imports `record`,
  `deterministic`, `sheet` (for `shown`). Imported by `agent`, `smoke`.
- `tools.py`: the seven `@tool` functions and the `tools` list (see Tools the model can call), plus the
  plain helpers `pretty`, `quote_is_real`, and `build_letter`. Imports `record`, `config`, `corpus`,
  `deterministic`, `sheet`. Imported by `agent`, `schemas`, `smoke` (for `build_letter`, `get_deadlines`).
- `agent.py`: `RULES` (the fixed part of the system prompt), `intake` (classify, propose facts, save; for a
  new matter only), `resume` (for an existing matter: log a `tenant_update` event, classify the update only,
  add new issues, propose facts from the update, save). Neither builds the agent: `run.py` runs the intake
  sheet first, then `build_agent`.
  `system_prompt()` (the whole system prompt, built from the record as it stands),
  `prompt_from_record` (LangChain `dynamic_prompt` middleware that calls `system_prompt()` before every
  model call), `build_agent` (a LangChain agent with that middleware and an in-memory checkpointer; no
  model call), `transcript_entry` (one thread message as a transcript line), and `chat` (the terminal loop; its
  thread id is the session id when one is open). Each turn, `chat` writes the tenant's message to the
  transcript before the model runs (so `propose_facts` can check the tenant's words), then every new message
  of the turn. After a turn in which the model called `propose_facts`, it runs the intake sheet; what the
  tenant confirmed there is sent to the model as a "[Program note: ...]" line at the front of the tenant's
  next message, and logged as a `program` transcript line. `timeline` commands go to the transcript too.
  Imports `record`, `config`, `corpus`, `deterministic`, `sheet`, `timeline`, `tools`. Imported by `run`.
- `run.py`: entry point. `start()` asks new or existing. `start_new` picks an existing tenant id or makes one
  (`new_tenant_id`), calls `new_matter` and `start_session("new")`, asks for the lease path (`ask_path`, which accepts a path dragged
  into the terminal), reads the lease (`read_lease`), asks for the description (`ask_text`, several lines
  ended by an empty line), then `intake`. `start_existing` lists matters, `load_matter` on the one picked
  (it stops if the matter has no lease profile), `start_session("existing")`, then asks "Anything new since last time?" with `ask_text`:
  text goes to `resume`, an empty answer goes on. Both return True when a matter is open. Then, if
  `pending_rows()` has anything, `run_sheet()`; then `chat(build_agent())`; then `end_session()` on a normal exit. A session opens before intake or resume, so everything done in the visit carries its id.
- `sheet.py`: the intake sheet, asked and saved by code with no model. `pending_rows()` (every changed,
  proposed, or missing fact across the matter's issues, once per fact id, with its question, type, and
  any suggestion), `parse_answer(kind, text)` (checks an answer against the element's type: dates as
  `2026-07-31` or `7/31/2026`, yes/no, amounts with or without `$` and commas, non-empty text), `shown`,
  and `run_sheet(ask=input)` (asks one fact at a time, rebuilding the list after each answer so an
  `applies_if` fact appears once it applies; Enter accepts a suggestion, `?` skips; shows "your lease
  says" next to a row carrying `lease_says`; saves each answer with
  `record.confirm_fact` and a transcript line; returns the saved facts as `(id, value)` pairs). Imports
  `record`, `corpus`. Imported by `run`, `agent`, `tools` (for `parse_answer` and `shown`).
- `checks.py`: helpers for the smoke scripts. `check(name, condition)` prints `OK` or `FAIL` and keeps the
  failures, `summary()` prints the last line, `make_scratch(tenant_id, **changes)` copies the test matter
  (without its transcripts) to `matters/<tenant_id>/m-001` and changes `matter.json` keys, and
  `remove_scratch(tenant_id)` removes it; it refuses any tenant id not starting with `t-smoke`.
- `smoke.py`: entry point. Checks each piece without the agent or a model (see Running and testing).
- `smoke_online.py`: entry point. `classify` and `fill_facts` on a sample description, then `resume`
  checks on a scratch matter.
- `schemas.py`: entry point. Prints each tool's name, first docstring line, and argument schema.

## Data flow

1. Lease PDF to profile (`read_lease` in `run.py`, new matters only; an existing matter's profile comes
   from `load_matter`). `ingest_pdf` stores the PDF and page text in `matter_dir()`, `extract_profile` asks the extraction model for a JSON `LeaseProfile`, `check_quotes` prints OK or FAIL
   for every clause, and the profile is saved. A FAIL is printed, not enforced: the profile is saved anyway.
2. Description to issues and proposed facts (`intake`). `classify` returns issue labels; labels not in
   `ISSUE_LABELS` are dropped, and the rest are added with `add_issues` (source "classify"). Labels with no
   playbook stay in `matter["issues"]` but have no elements or clocks. For each active playbook, `fill_facts` asks for a value, a `how` ("stated" or "inferred"), and
   the tenant's exact words for every element whose `source` includes `user`. An answer is kept only if
   its words appear in the description (substring after `squash`). The first playbook to propose a fact id
   wins. `intake` resets `facts` and `proposed` to empty before this, then saves `matter.json`.
2b. An update to an existing matter (`resume`). The text is logged verbatim as a `tenant_update` event;
   `description` is not touched. `classify` runs on the update only, and any label not already in
   `matter["issues"]` is added with `add_issues` (source "classify"), then `add_related_issues` in case a
   confirmed fact already triggers a rule of a newly added playbook; none is removed. `fill_facts` runs on the update for every active
   playbook, old and new. A value equal to the confirmed fact of the same id is dropped; the rest go into
   `proposed`, replacing any older pending proposal for that id. A proposal next to a confirmed fact with a
   different value shows as `changed` (step 4). Facts two playbooks share by element id need nothing: there
   is one `facts` pool for the matter, so a new issue's shared elements are already known.
3. Proposed to confirmed (`record.confirm_fact`, the only code that writes `matter["facts"]`). It moves
   the value into `facts`, removes it from `proposed`, and appends a `fact_confirmed` event carrying the
   proposal's `how`, `basis`, and `proposed_value` (or `how: "asked"` when nothing was proposed) and
   `confirmed_in`. One caller: the intake sheet (`sheet.run_sheet`, the tenant answers code directly,
   `confirmed_in: "sheet"`). Then `add_related_issues`: if the fact triggers a related_issues rule, the
   related issue is added at once (source "related"), and since the sheet rebuilds its list after every
   answer, the new issue's questions come up in the same sheet, which says "Added to your matter"; the
   model's next prompt carries the new issue's guidance. Then `prune_proposals` drops every suggestion that can never be asked: all
   elements with its id take the value from the lease (a present clause listed before `user` in
   `source`), or depend on a fact confirmed as not true with no change to it pending, or no active playbook
   asks for it. A suggestion whose condition is still open, or has a pending change, is kept. `intake`,
   `resume`, and `propose_facts` prune too. Pruning is not logged. The model cannot confirm a fact; it can only add to `proposed` with
   `propose_facts`, and the sheet follows its turn. Events from before 2026-09-27 may say
   `confirmed_in: "chat"` or have no `confirmed_in`: those were recorded by the old `record_facts` tool.
4. Element status (`check_elements`). For each element in order: `n/a` if it has an `applies_if` and that
   fact is not confirmed truthy (unconfirmed counts as not truthy); `known` if a source gives a value (a confirmed fact, or a present lease clause's
   quote, in the order listed in `source`); `changed` instead of `known` if the value is a confirmed fact
   and `proposed` holds a different value for the same id (the row carries both, `value` and `new_value`,
   plus the proposal's `how` and `basis`; a value read from the lease is never `changed`); `proposed` if it
   is in `proposed`; otherwise `missing`. Changed, proposed, and missing rows carry the `guidance.questions`
   text in `ask`. A changed row is resolved on the sheet, with either value. A row whose element names a
   lease field in `compare_to` also carries `lease_says`, the lease's exact words, when the lease's value
   (read by `lease_value`: dates as printed, dollar figures) differs from the tenant's value (the confirmed
   one, the suggestion, or for a changed row the new value). Nothing is compared when the quote cannot be
   read. The tool shows both and does not decide which is right.
5. Confirmed to deadlines (`get_deadlines`, then `matter_deadlines`, then `compute_deadlines` per playbook). Refuses while any row is proposed,
   changed, or missing. For each clock: skipped if `applies_if` is not a truthy confirmed fact; "need date for ..."
   if the trigger date is not confirmed; otherwise trigger date plus or minus `days` calendar days, status
   `passed` if before today else `upcoming`, with the cite and the playbook's `counting.convention`.
   `matter_deadlines` then merges a row two playbooks share (same clock id, cite, date, and status) into
   one, and every row carries `issues`, the list of issues it belongs to.
6. Record to timeline (`render_timeline`). Rows come from confirmed date facts, freshly computed deadlines
   (from `matter_deadlines`, so a shared deadline is one row tagged `[issue, issue]`, kept under either
   issue by `timeline <issue>`),
   and events (see Files on disk). Sorted by date only; rows on the same day keep the order they were
   added (confirmed dates and deadlines first, then events in log order). `issue` filters deadlines and
   issue-tagged events; untagged events always show. `full` adds `fact_confirmed`, `fetch`,
   `deadlines_computed`, `issue_added`, `session_started`, and `session_ended` events.
7. Letter assembly (`draft_letter`, then `build_letter`). Checks the issue and posture, checks each quote
   with `quote_is_real` (substring of a present lease clause quote or any stored statute section), then
   builds the letter from a template: today's date, landlord and premises quotes from the profile, every
   confirmed date fact of the active playbooks, the ask, a reply-by date (today plus `respond_within_days`),
   the quotes, the delivery method, and the tenant names quote. Writes the draft file and a `draft` event.

## Files on disk

`matters/<tenant id>/<matter id>/`, built by `record.matter_dir` from `matter["tenant"]` and `matter["id"]`.
A tenant id is opaque, never a name or an email. Currently only `matters/t-test/test-001/`, set in
`record.matter`:

- `lease_<sha256[:12]>.pdf`: the lease as provided, named by its hash.
- `pages.json`: list of `{"page": n, "text": ...}` from PyPDF2.
- `lease_profile.json`: the `LeaseProfile`, one `Clause` per field: `present`, `quote`, `page`, `section`.
- `matter.json`: current state only, overwritten by `save`. Keys: `id`, `tenant`, `description` (the intake text),
  `issues` (labels from `classify`), `facts` (confirmed, element id to value), `proposed` (unconfirmed,
  element id to `{"value", "how", "basis"}`).
- `events.jsonl`: the history, one JSON object per line, append-only. Every event has `when` (local time,
  ISO, to the second) and `kind`, then `session` (the session id) if a session was open when it was
  written. Events written before sessions existed, or outside `run.py`, have no `session`. Kinds and their
  other fields:
  - `fact_confirmed`: `id`, `value`, `how` (stated, inferred, or asked), `basis`, `proposed_value`,
    `confirmed_in` ("sheet" or "chat"; missing on events from before 2026-09-27). Written by
    `record.confirm_fact`.
  - `fetch`: `section` (from `get_statute_section`) or `search` (from `search_statute`).
  - `deadlines_computed`: `issue`, `clocks` (ids of clocks that produced a date). One per active playbook
    per `get_deadlines` call.
  - `draft`: `issue`, `posture`, `cites`, `file`. Written by `draft_letter`.
  - `artifact`: `file` (original name), `sha256`, `note`. Written by `add_artifact`.
  - `communication`: `sent_on` (YYYY-MM-DD), `sender`, `recipient`, `channel`, `text`. Written by
    `add_communication`. The timeline sorts it by `sent_on`, not `when`.
  - `issue_added`: `issue`, `source` ("classify" or "related"), `because` (e.g. "the tenant's update",
    "claim_notice_received is true"). Written by `record.add_issues`. `timeline full` only. Matters from
    before 2026-09-27 have issues with no such event.
  - `tenant_update`: `text`, what a returning tenant typed as new, verbatim. Written by `resume`. Shown in
    the timeline as "tenant update" with the first words.
  - `session_started`: `how` ("new" or "existing"). Written by `start_session`. `timeline full` only, with
    the transcript's path in the FILE column.
  - `session_ended`: no other fields. Written by `end_session` on a normal exit. A session with a start and
    no end was cut off. `timeline full` only.
- `draft_<YYYY-MM-DD>_<issue>_<posture>.txt`: each drafted letter. A second draft on the same day with the
  same issue and posture overwrites the file; the earlier `draft` event remains.
- `artifacts/<sha256[:12]>_<name>`: copies of files stored by `add_artifact`.
- `sessions/<session id>.jsonl`: the transcript of one session, outside the evidentiary log. One line per
  entry, each with `when` and `role`: `tenant` (`text`, as typed), `model` (`text`, plus `tool_calls`, a
  list of `{"name", "args"}`, when it called tools), `tool` (`name`, `text`: the result the model saw),
  `command` (`text`: a `timeline` command, handled without the model), `sheet` (`id`, `question`,
  `typed`: what the tenant typed, empty if they accepted the suggestion, `value`: what was saved, `issues_added`
  when the answer brought in a related issue), or
  `program` (`text`: the note sent to the model ahead of the tenant's message after a sheet). Only the chat is transcribed; the
  intake or resume calls before it are not.

Outside `matters/`: `lease.pdf` (a sample lease for test runs, gitignored; `run.py` asks for a path), `statutes/83.*.txt` and `.html` (the
read-only corpus; only `.txt` is loaded), `playbooks/*.yaml`, `.env` (the key).

## Tools the model can call

All in `tools.py`, in the `tools` list. The docstring is what the model reads; `python schemas.py` shows it.

- `get_statute_section(section)`: the stored text of one section, or a "No section ... stored" message
  listing what is available. Writes a `fetch` event.
- `search_statute(phrase)`: every section containing the phrase (case-insensitive), with a snippet.
  Writes a `fetch` event.
- `propose_facts(facts_json)`: JSON object keyed by element id, each `{"value", "how", "said"}`. Puts a
  suggestion in `proposed` only if the id is a user-sourced element of an active playbook, the value fits
  the element's type (`sheet.parse_answer`, and it is stored as parsed), `how` is stated or inferred, and
  `said` appears in what the tenant typed this session (`record.tenant_words`, substring after `squash`).
  A value equal to the confirmed one is refused. Saves `matter.json`; returns what was taken and why
  anything was refused. Never confirms: the chat loop runs the sheet after the turn.
- `get_deadlines()`: refuses with the list of unconfirmed ids while any row is proposed, changed, or missing.
  Otherwise returns every clock's result for the active playbooks from `matter_deadlines`, each with
  `issues` (a list; a deadline two issues share appears once), and writes a `deadlines_computed` event per
  playbook listing the clocks that belong to it.
- `draft_letter(issue, posture, ask, respond_within_days, delivery_method, obligation_quote,
  obligation_cite, consequence_quote, consequence_cite)`: `issue` must be in the matter and have a playbook;
  `posture` is preserve (no quotes), assert (obligation quote), or escalate (both quotes). Rejects any quote
  `quote_is_real` does not find. Returns the letter plus a "NOTE TO TENANT" line from the playbook's
  `guidance.postures.notice_sufficiency`. Writes the draft file and a `draft` event. The chat loop prints
  this tool's output directly.
- `add_artifact(path, note)`: copies a file into `artifacts/` under its hash. Writes an `artifact` event.
- `add_communication(sent_on, sender, recipient, channel, text)`: rejects a `sent_on` that is not
  YYYY-MM-DD. Writes a `communication` event. Also used for a letter the tenant reports sending (rule 15).

## The system prompt

Built by `agent.system_prompt()` on every model call (through the `prompt_from_record` middleware), so it
always matches the record: facts confirmed on the sheet and issues added mid-chat show up on the model's
next call. The conversation itself is kept by the checkpointer; only the system prompt is rebuilt. In
this order:

1. `RULES`, fifteen numbered rules. In short: 1 quote only from the profile or stored statute; 2 never
   compute dates, use `get_deadlines`; 3 facts are confirmed on the sheet, not in chat: propose with `propose_facts`, read ELEMENT
   STATUS (current as of each reply), no `get_deadlines` while anything is open;
   4 look up the statute when the preloaded text does not answer, otherwise say so; 5 open questions are
   unsettled; 6 draft only when asked, never send; 7 never say which of lease or statute controls; 8 fetch a
   section before mentioning it; 9 the model cannot confirm a fact and never says one is recorded unless ELEMENT STATUS shows it; 10 ask whose notice is meant;
   11 the letter questions (issue, ask, reply days, delivery method, the sentence relied on, posture), then
   `draft_letter` and one sentence; 12 never write a letter yourself; 13 never apply a provision to the
   facts; 14 record pasted messages with `add_communication`; 15 record a sent letter the same way.
2. `LEASE PROFILE`: the whole profile as JSON.
3. `PLAYBOOKS`: for each active playbook, YAML of its `issue`, its `guidance`, and its
   `spec.open_questions` (which rule 5 refers to). The rest of `spec` never enters the context.
4. `STATUTE SECTIONS`: the text of every section the active playbooks list in `sections`, once each. An
   issue with no playbook yet adds none.
5. `ELEMENT STATUS (by issue)`: `element_status()` as JSON at the moment of the call.

The program note after a sheet still tells the model, in the conversation, that a sheet just ran.

## Playbook schema

Nine playbooks, one per label in `ISSUE_LABELS` except `other`: deposit_not_returned,
deposit_claim_received, repair_not_made, notice_received_nonpayment, notice_received_violation,
landlord_entered_unannounced, rent_increased, wants_to_leave_early, lease_ending. The seven written
2026-09-27 are version 0.1 with `verified_by: null` until the author's hand check. Three have no clocks,
and say why in `counting.note`: notice_received_nonpayment (83.56(3) and 83.60(2) exclude weekends and
court-observed holidays), landlord_entered_unannounced (83.53(2) is in hours), rent_increased (no
section on notice of a rent increase). Facts shared across playbooks by id: `claim_notice_date`,
`tenancy_terminated`, `deposit_amount`, `eviction_action_filed`, `fixed_term_lease`, `term_end_date`,
`month_to_month`, `monthly_rent`.

One YAML file per issue in `playbooks/`. `load_playbook` validates it against `Playbook` and raises if a
section is not in `statutes/`, a clock's `trigger` is not a date element or an element's `compare_to` is not a `LeaseProfile` field.
After all playbooks load, `corpus.py` also raises if a related issue is not in `ISSUE_LABELS` or its
condition's fact is not an element of any playbook. Keys the `Playbook` class does not define (`description`) are dropped
on load and never reach the model.

- `issue`: the label; must be in `deterministic.ISSUE_LABELS` to be classified. Key of `playbooks`.
- `sections`: the statute sections the playbook rests on, e.g. `["83.49"]`. `load_playbook` raises if one is
  not in `statutes/`. `system_prompt` puts their text into the prompt while the issue is active.
- `provenance`: statute year, file verified against, who and when, version. Not read by code.
- `counting.convention`: copied into every `compute_deadlines` result. `counting.status` and the optional
  `counting.note` (why a playbook computes fewer dates than its sections mention): not read by code.
- `spec` (typed, read by code):
  - `elements`: `id`, `type` (date, money, bool, text), `source` (list; `user` and/or
    `lease_profile.<field>`, tried in order), `applies_if` (id of a bool element), `compare_to` (optional,
    `lease_profile.<field>`: the lease field to show next to the tenant's value when they differ; the
    deposit playbooks set `tenancy_terminated` against `term_end`; rent_increased, wants_to_leave_early, and
    lease_ending set `term_end_date` against it). Read by
    `check_elements`, `fill_facts` (only elements with `user` in `source`), `build_letter` and
    `render_timeline` (date elements).
  - `clocks`: `id`, `actor` (landlord, tenant), `trigger` (a date element id), `days`, `direction`
    (before, after), `cite`, `quote`, optional `consequence`, `delivery`, `applies_if`. Read by
    `compute_deadlines`; `quote` and `consequence` checked by `check_playbook`; `smoke.py` uses
    `clocks[0].quote`.
  - `lease_overrides`, `exclusions`: lists of dicts. Any item with a `quote` is checked by
    `check_playbook` against the section in its `cite`. Otherwise not read by code.
  - `related_issues`: list of `{issue, when: {fact, equals}}`. Read by `record.add_related_issues`: once
    `fact` is confirmed with the value `equals`, `issue` is added to the matter. Not shown to the model.
  - `open_questions`: not read by code. `system_prompt` puts them into the prompt next to `guidance`, the only
    part of `spec` the model sees.
- `guidance` (prose, put into the prompt by `system_prompt`), with two pieces also read by code:
  - `questions`: one question per element id. `check_elements` needs one for every element that can be
    proposed or missing; `fill_facts` sends them to the model.
  - `postures.notice_sufficiency`: appended to every `draft_letter` result as the note to the tenant.
  - `lease_checks`, `evidence`, `postures` (core, preserve, assert, escalate), `failure_modes`: model only.

## Running and testing

    bash setup.sh            # once: venv, pip install, .env from template, matters/
    source venv/bin/activate

Offline checks (no model call, no key needed):

    python smoke.py                                                              # the offline smoke tests
    python -c "from corpus import check_all_playbooks; check_all_playbooks()"   # playbook quotes: every line OK
    python schemas.py                                                            # what the model sees per tool

- `python smoke.py`: needs the saved test matter `matters/t-test/test-001/` with its lease profile. Opens it
  with `load_matter` and prints `list_matters()`, then runs the playbook quote check, element status and deadlines on hand-typed facts with today fixed at 2026-09-08, a hand-typed update
  against those facts (one changed row, one unchanged, one lease value left alone, `get_deadlines`
  refusing), the letter template, and both
  timelines. The timelines read the real `events.jsonl` of `test-001`. Importing `tools` and `timeline`
  also checks that the modules import. Last, on a scratch copy `matters/t-smoke/m-001` (removed at the
  end, even after a failure), about thirty named checks of the code that writes to a matter: listing and
  ids, sessions and their tags, `propose_facts` taking one suggestion and refusing five for five reasons,
  the sheet with scripted answers (accept, correct, bad input, a changed fact, an `applies_if` fact, a
  skip), `get_deadlines` waiting and then answering, the prompt following the record, events, the transcript, and the
  timeline. Then related issues on `matters/t-smoke-related/m-001`, and every playbook through the real
  code path on `matters/t-smoke-playbooks/m-001`: for each, the sheet is answered by type ("yes" to every
  yes/no, so every `applies_if` question comes up), every clock must get a date, and a preserve letter must
  carry the playbook's `notice_sufficiency` note. A new playbook is covered without a new check. Every line
  must be OK; the last line says "all checks OK" or lists the failures. The test matter itself is not
  changed by a smoke run.

Calls the model (needs the key in `.env`; stops at `require_key()` without it):

- `python smoke_online.py`: opens the same test matter with `load_matter`. `classify` and `fill_facts` on the sample
  description (two model calls), then element status from the proposed facts. Then `resume` on a scratch
  copy `matters/t-smoke-online/m-001` (two more calls) with named checks: the update logged verbatim, the
  description and old issues kept, nothing confirmed, no suggestion equal to a confirmed value. Checks
  marked "(model)" depend on the model's answer (the new issue added, the changed fact proposed).
- `python run.py`: interactive. Asks new or existing. A new matter reads the lease (one extraction call)
  and runs intake (two calls). An existing matter asks what is new: an update runs `resume` (two calls).
  Then the intake sheet asks every open fact (no model), and the chat starts. Chat commands, handled by the loop without the
  model: `timeline`, `timeline full`, `timeline <issue>`; an empty line or `bye` exits. Every run appends
  to the matter's `events.jsonl`.
