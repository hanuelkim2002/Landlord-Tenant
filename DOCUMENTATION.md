# Documentation

How the code works right now. Kept by Claude Code so that a session does not have to read every module to
get oriented. Update it whenever a function, tool, file, event kind, or rule changes. Describe what exists,
not what is planned (that is TODO.md) or what changed (that is CHANGELOG.md).

## Modules

Listed from the bottom of the import chain up. Every module imports `config`, so nothing imports without
`UF_API_KEY` set (see Running and testing).

- `config.py`: paths (`ROOT`, `MATTERS`, `STATUTES`, `PLAYBOOKS`), the two model clients (`agent_llm` on
  `AGENT_MODEL`, `extract_llm` on `EXTRACT_MODEL`, both on the UF gateway at temperature 0), and `squash`
  (collapse whitespace, lowercase; used for every quote comparison). Reads `.env` with python-dotenv and
  raises if `UF_API_KEY` is missing. Imports nothing from the project.
- `lease.py`: lease intake. `ingest_pdf` (store the PDF under its hash, extract page text with PyPDF2,
  write `pages.json`), the `Clause` and `LeaseProfile` shapes (fifteen named clauses), `extract_profile`
  (one call to `extract_llm`), `quote_found` and `check_quotes` (each quote must appear on its cited page,
  or start there and run onto the next). Imports `config`. Imported by `run.py` and `smoke.py`.
- `corpus.py`: the stored corpus, loaded once at import. `statute` (dict, section number to text, from
  `statutes/83.*.txt`), the playbook shapes (`Element`, `Clock`, `Spec`, `Playbook`), `load_playbook`,
  `check_playbook`, `check_all_playbooks`, and `playbooks` (dict, issue to `Playbook`, from
  `playbooks/*.yaml`). No model calls. Imports `config`. Imported by `record`, `tools`, `agent`, `smoke`.
- `deterministic.py`: `check_elements` (element status), `compute_deadlines` (the only date arithmetic),
  `ROUTING` (issue label to statute sections to preload), and the two one-shot intake calls `classify` and
  `fill_facts`, both through `ask_json` on `agent_llm`. Imports `config`. Imported by `record`,
  `timeline`, `tools`, `agent`, `smoke`.
- `record.py`: the shared state. `matter` and `profile` live here and every other module reaches them as
  `record.matter` and `record.profile`. `matter_dir`, `save` (writes `matter.json`), `append_event` and
  `read_events` (`events.jsonl`), `active_playbooks`, `element_status`. The matter id is hard-coded
  `"test-001"`. Imports `config`, `corpus`, `deterministic`. Imported by `timeline`, `tools`, `agent`,
  `run`, `smoke`.
- `timeline.py`: `render_timeline(issue, full)`, the DATE / EVENT / SOURCE / FILE table, plus helpers
  `label` and `confirmation_of`. Not a tool; only the chat loop and `smoke.py` call it. Imports `record`,
  `deterministic`. Imported by `agent`, `smoke`.
- `tools.py`: the seven `@tool` functions and the `tools` list (see Tools the model can call), plus the
  plain helpers `pretty`, `quote_is_real`, and `build_letter`. Imports `record`, `config`, `corpus`,
  `deterministic`. Imported by `agent`, `schemas`, `smoke` (for `build_letter`).
- `agent.py`: `RULES` (the fixed part of the system prompt), `intake` (classify, propose facts, build the
  system prompt, return a LangChain agent with an in-memory checkpointer), and `chat` (the terminal loop).
  Imports `record`, `config`, `corpus`, `deterministic`, `timeline`, `tools`. Imported by `run`.
- `run.py`: entry point. Loads or extracts the lease profile, then `intake` on a hard-coded description,
  then `chat`. Reads `lease.pdf` from the project folder.
- `smoke.py`: entry point. Checks each piece without the agent (see Running and testing).
- `schemas.py`: entry point. Prints each tool's name, first docstring line, and argument schema.

## Data flow

1. Lease PDF to profile (`run.py`). If `matters/<id>/lease_profile.json` exists it is loaded into
   `record.profile` and no model runs. Otherwise `ingest_pdf` stores the PDF and page text,
   `extract_profile` asks the extraction model for a JSON `LeaseProfile`, `check_quotes` prints OK or FAIL
   for every clause, and the profile is saved. A FAIL is printed, not enforced: the profile is saved anyway.
2. Description to issues and proposed facts (`intake`). `classify` returns issue labels; labels not in
   `ROUTING` are dropped. Labels with no playbook stay in `matter["issues"]` but have no elements or
   clocks. For each active playbook, `fill_facts` asks for a value, a `how` ("stated" or "inferred"), and
   the tenant's exact words for every element whose `source` includes `user`. An answer is kept only if
   its words appear in the description (substring after `squash`). The first playbook to propose a fact id
   wins. `intake` resets `facts` and `proposed` to empty before this, then saves `matter.json`.
3. Proposed to confirmed (`record_facts`). The model shows each proposed row, the tenant confirms or
   corrects, and `record_facts` moves the value into `matter["facts"]`, removing it from `proposed`. It
   appends a `fact_confirmed` event carrying the proposal's `how`, `basis`, and `proposed_value`
   (or `how: "asked"` when nothing was proposed). This is the only code that writes `matter["facts"]`.
4. Element status (`check_elements`). For each element in order: `n/a` if it has an `applies_if` and that
   fact is not confirmed truthy (unconfirmed counts as not truthy); `known` if a source gives a value (a confirmed fact, or a present lease clause's
   quote, in the order listed in `source`); `proposed` if it is in `proposed`; otherwise `missing`. Proposed
   and missing rows carry the `guidance.questions` text as `ask`.
5. Confirmed to deadlines (`get_deadlines`, then `compute_deadlines`). Refuses while any row is proposed
   or missing. For each clock: skipped if `applies_if` is not a truthy confirmed fact; "need date for ..."
   if the trigger date is not confirmed; otherwise trigger date plus or minus `days` calendar days, status
   `passed` if before today else `upcoming`, with the cite and the playbook's `counting.convention`.
6. Record to timeline (`render_timeline`). Rows come from confirmed date facts, freshly computed deadlines,
   and events (see Files on disk). Sorted by date string. `issue` filters deadlines and issue-tagged events;
   untagged events always show. `full` adds `fact_confirmed`, `fetch`, and `deadlines_computed` events.
7. Letter assembly (`draft_letter`, then `build_letter`). Checks the issue and posture, checks each quote
   with `quote_is_real` (substring of a present lease clause quote or any stored statute section), then
   builds the letter from a template: today's date, landlord and premises quotes from the profile, every
   confirmed date fact of the active playbooks, the ask, a reply-by date (today plus `respond_within_days`),
   the quotes, the delivery method, and the tenant names quote. Writes the draft file and a `draft` event.

## Files on disk

`matters/<matter id>/` (currently only `test-001`, set in `record.matter`):

- `lease_<sha256[:12]>.pdf`: the lease as provided, named by its hash.
- `pages.json`: list of `{"page": n, "text": ...}` from PyPDF2.
- `lease_profile.json`: the `LeaseProfile`, one `Clause` per field: `present`, `quote`, `page`, `section`.
- `matter.json`: current state only, overwritten by `save`. Keys: `id`, `description` (the intake text),
  `issues` (labels from `classify`), `facts` (confirmed, element id to value), `proposed` (unconfirmed,
  element id to `{"value", "how", "basis"}`).
- `events.jsonl`: the history, one JSON object per line, append-only. Every event has `when` (local time,
  ISO, to the second) and `kind`. Kinds and their other fields:
  - `fact_confirmed`: `id`, `value`, `how` (stated, inferred, or asked), `basis`, `proposed_value`.
    Written by `record_facts`.
  - `fetch`: `section` (from `get_statute_section`) or `search` (from `search_statute`).
  - `deadlines_computed`: `issue`, `clocks` (ids of clocks that produced a date). One per active playbook
    per `get_deadlines` call.
  - `draft`: `issue`, `posture`, `cites`, `file`. Written by `draft_letter`.
  - `artifact`: `file` (original name), `sha256`, `note`. Written by `add_artifact`.
  - `communication`: `sent_on` (YYYY-MM-DD), `sender`, `recipient`, `channel`, `text`. Written by
    `add_communication`. The timeline sorts it by `sent_on`, not `when`.
- `draft_<YYYY-MM-DD>_<issue>_<posture>.txt`: each drafted letter. A second draft on the same day with the
  same issue and posture overwrites the file; the earlier `draft` event remains.
- `artifacts/<sha256[:12]>_<name>`: copies of files stored by `add_artifact`.

Outside `matters/`: `lease.pdf` (the input lease read by `run.py`), `statutes/83.*.txt` and `.html` (the
read-only corpus; only `.txt` is loaded), `playbooks/*.yaml`, `.env` (the key).

## Tools the model can call

All in `tools.py`, in the `tools` list. The docstring is what the model reads; `python schemas.py` shows it.

- `get_statute_section(section)`: the stored text of one section, or a "No section ... stored" message
  listing what is available. Writes a `fetch` event.
- `search_statute(phrase)`: every section containing the phrase (case-insensitive), with a snippet.
  Writes a `fetch` event.
- `record_facts(facts_json)`: JSON object of element id to confirmed value. Moves each into `facts`,
  writes a `fact_confirmed` event per fact, saves `matter.json`, returns the new element status. Does not
  check that the id is a real element or that the value has the element's type.
- `get_deadlines()`: refuses with the list of unconfirmed ids while any row is proposed or missing.
  Otherwise returns every clock's result for every active playbook, tagged with `issue`, and writes a
  `deadlines_computed` event per playbook.
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

Built in `intake`, in this order:

1. `RULES`, fifteen numbered rules. In short: 1 quote only from the profile or stored statute; 2 never
   compute dates, use `get_deadlines`; 3 confirm proposed rows, ask missing rows, then `record_facts`;
   4 look up the statute when the preloaded text does not answer, otherwise say so; 5 open questions are
   unsettled; 6 draft only when asked, never send; 7 never say which of lease or statute controls; 8 fetch a
   section before mentioning it; 9 never record an unconfirmed value; 10 ask whose notice is meant;
   11 the letter questions (issue, ask, reply days, delivery method, the sentence relied on, posture), then
   `draft_letter` and one sentence; 12 never write a letter yourself; 13 never apply a provision to the
   facts; 14 record pasted messages with `add_communication`; 15 record a sent letter the same way.
2. `LEASE PROFILE`: the whole profile as JSON.
3. `PLAYBOOKS`: the full YAML file of each active playbook, `spec` and `guidance` both.
4. `STATUTE SECTIONS`: the text of every section `ROUTING` lists for every issue in the matter, including
   issues that have no playbook.
5. `ELEMENT STATUS (by issue)`: `element_status()` as JSON at intake time.

The prompt is fixed for the session. Later element status reaches the model only through `record_facts`
return values.

## Playbook schema

One YAML file per issue in `playbooks/`. `load_playbook` validates it against `Playbook` and raises if a
clock's `trigger` is not a date element. Keys the `Playbook` class does not define (`description`) are dropped
on load and reach the model only through the pasted YAML.

- `issue`: the label; must match a `ROUTING` key to be classified. Key of `playbooks`.
- `statutory_hook`: section number. Not read by code.
- `provenance`: statute year, file verified against, who and when, version. Not read by code.
- `counting.convention`: copied into every `compute_deadlines` result. `counting.status`: not read by code.
- `spec` (typed, read by code):
  - `elements`: `id`, `type` (date, money, bool, text), `source` (list; `user` and/or
    `lease_profile.<field>`, tried in order), `applies_if` (id of a bool element). Read by
    `check_elements`, `fill_facts` (only elements with `user` in `source`), `build_letter` and
    `render_timeline` (date elements).
  - `clocks`: `id`, `actor` (landlord, tenant), `trigger` (a date element id), `days`, `direction`
    (before, after), `cite`, `quote`, optional `consequence`, `delivery`, `applies_if`. Read by
    `compute_deadlines`; `quote` and `consequence` checked by `check_playbook`; `smoke.py` uses
    `clocks[0].quote`.
  - `lease_overrides`, `exclusions`: lists of dicts. Any item with a `quote` is checked by
    `check_playbook` against the section in its `cite`. Otherwise not read by code.
  - `related_issues`, `open_questions`: not read by code. They reach the model only because the whole YAML
    is pasted into the prompt.
- `guidance` (prose, read by the model through the pasted YAML), with two pieces also read by code:
  - `questions`: one question per element id. `check_elements` needs one for every element that can be
    proposed or missing; `fill_facts` sends them to the model.
  - `postures.notice_sufficiency`: appended to every `draft_letter` result as the note to the tenant.
  - `lease_checks`, `evidence`, `postures` (core, preserve, assert, escalate), `failure_modes`: model only.

## Running and testing

    bash setup.sh            # once: venv, pip install, .env from template, matters/
    source venv/bin/activate

Every module imports `config`, which raises if `UF_API_KEY` is not set. So every command below needs the
key present in `.env`, but only the ones marked "calls the model" send anything to the gateway.

Offline checks (no model call):

    python -c "from corpus import check_all_playbooks; check_all_playbooks()"   # playbook quotes: every line OK
    python -c "import agent, tools, timeline, lease"                             # everything imports
    python schemas.py                                                            # what the model sees per tool

Calls the model:

- `python smoke.py`: needs `matters/test-001/lease_profile.json`. Runs the playbook quote check, element
  status and deadlines on hand-typed facts with today fixed at 2026-09-08, then `classify` and
  `fill_facts` on the sample description (two model calls), then the letter template and both timelines.
  The last two read the real `events.jsonl` of `test-001`.
- `python run.py`: interactive. Extracts the lease profile the first time (one extraction call), then
  intake (two calls) and the chat. Chat commands, handled by the loop without the model: `timeline`,
  `timeline full`, `timeline <issue>`; an empty line or `bye` exits. Each run resets `facts` and
  `proposed` but appends to the same `events.jsonl`.
