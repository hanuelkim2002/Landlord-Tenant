# Changelog

Newest first. One entry per change, dated. Say what was replaced as well as what was added, so a future
session can see why the code is the way it is.

## 2026-09-26

- Matter structure, step 3 of 3: `run.py` rewritten around `start()`, which asks new or existing. New:
  pick a tenant or make one, `record.new_matter`, lease path asked (replaces hard-coded `lease.pdf`),
  lease read, description typed by the tenant (replaces the hard-coded sample), intake. Existing: pick from
  `list_matters`, `load_matter`, straight to chat with no re-intake. `agent.intake` split: the system
  prompt and agent now come from a new `build_agent`, which a resumed matter calls directly. Tested live:
  resumed `t-test/test-001` went to deadlines from saved facts; a new matter `t-4c4d2e/m-001` was made
  from the sample lease (bad path refused, dragged path with escaped spaces accepted, 15 of 15 quotes OK),
  and its first confirmed fact landed in its own folder. The matter structure item is done.
- Matter structure, step 2 of 3: `list_matters` (tenant, id, and issues of every saved matter; no
  description or facts) and `load_matter(tenant_id, matter_id)` (replaces `record.matter` and
  `record.profile` from disk, profile `None` if the lease has not been read) in `record.py`, which now
  imports `lease` for `LeaseProfile`. `smoke.py` and `smoke_online.py` open the test matter with
  `load_matter` instead of reading the lease profile by hand, and `smoke.py` prints `list_matters()`.
  Checked by hand that `tools` and `timeline` see a newly loaded matter. Step 3 (`start()`) stays in TODO.md.
- Matter structure, step 1 of 3: matters now live at `matters/<tenant id>/<matter id>/`. `record.matter`
  gains a `tenant` key and `record.matter_dir` builds the path from both ids; it replaces
  `MATTERS / matter["id"]`. `ingest_pdf` now takes the matter folder instead of a matter id, so
  `matter_dir` is the only code that knows the layout (it replaces the path `lease.py` built itself).
  New helpers `new_tenant_id` (random `t-xxxxxx`, never from a name or email) and `new_matter_id`
  (`m-001`, `m-002`, ...), not called yet. The test matter moved to `matters/t-test/test-001/` and its
  `matter.json` gained `"tenant": "t-test"`. Steps 2 (list and load) and 3 (`start()`) stay in TODO.md.
- Second end-to-end `run.py` run, after the guidance-only prompt and the smoke split. Same facts, same
  deadlines, email recorded, assert letter drafted, timelines correct. Rule 5 still works (the model said
  the statute does not settle the termination-date question). Run 1's `events.jsonl` and draft renamed to
  `events_run1.jsonl` and `run1_draft_...` in `matters/test-001/` rather than deleted. Two findings added
  to TODO.md (a mis-cite for the escalate posture, an n/a question asked) and a note on the sample lease's
  term. No code changed.
- `smoke.py` split: `smoke.py` keeps the offline checks (playbook quotes, elements, deadlines, letter,
  timelines) and `smoke_online.py` holds the two model calls (`classify`, `fill_facts`). Replaces one
  script that needed the key for everything. To let the offline part run with no key, `config.py` no
  longer raises at import: the model clients are `None` without a key, and the new `require_key()` raises
  the old message. `run.py` and `smoke_online.py` call it first. CLAUDE.md's running lines updated.
  (TODO item 1, formerly item 3.)
- `intake` pastes only the model-facing part of each playbook into the system prompt: `issue`, `guidance`,
  and `spec.open_questions`, dumped as YAML. Replaces pasting the whole YAML file, which put elements,
  clocks, exclusions, related issues, provenance, and counting into the context. `open_questions` kept
  because rule 5 refers to them (decided with the author). Playbook text in the prompt roughly halves.
  `agent.py` no longer imports `PLAYBOOKS`. (TODO item 1, formerly item 2.)
- `lease.pdf` added to `.gitignore`. It is a sample lease, not a real one, but it carries names and
  addresses, so it stays out of history. Replaces the earlier state of leaving it untracked by hand.
- `git init` and first commit of the module split, so every later step is a readable diff. `.gitignore`
  keeps out `.env`, `matters/`, `venv/`, `__pycache__/`. `lease.pdf` left untracked pending a decision on
  whether the sample lease belongs in the repo. (TODO item 1, formerly item 2.)
- DOCUMENTATION.md filled from the code: modules and imports, data flow, files on disk with every event
  kind, the seven tools, the system prompt order, the playbook schema field by field with which code reads
  each, and running and testing. Replaces the section placeholders. Notes that every module needs
  `UF_API_KEY` set to import (config raises), so the offline checks need the key present but make no call.
  (TODO item 3.)
- Ran `python run.py` end to end against the UF gateway on `test-001`: lease profile loaded from disk,
  intake, all five proposed facts confirmed one by one, `get_deadlines`, a pasted landlord email recorded
  by `add_communication`, an assert letter from `draft_letter`, then `timeline`, `timeline full`,
  `timeline lease_ending`, `bye`. `python smoke.py` passed first, all playbook quote checks OK. The move
  from Colab broke nothing. Four findings added to TODO.md (double period in letters, one rule 2 slip,
  `timeline full` tag on a corrected fact, `lease_ending` preloading sections). No code changed.
  (TODO item 1.)
- Added README.md (fixed plan), TODO.md (working list), DOCUMENTATION.md (to be filled), CHANGELOG.md.
  CLAUDE.md slimmed to conventions, guardrails, and pointers to those four files. Its "Next steps" section
  moved to TODO.md with the review pushbacks folded in.

## 2026-09-25

- Moved from `Landlord_Tenant_chatbot_v3_2.ipynb` (Colab) to modules in this folder, one per notebook
  section: config, lease, corpus, deterministic, record, timeline, tools, schemas, agent, run, smoke.
  Colab `userdata` and Drive replaced by `.env` (python-dotenv) and paths relative to the folder.
- Shared state convention: `matter` and `profile` live in `record.py`; other modules use `record.matter`
  and `record.profile`. Replaces the notebook's single namespace.
- `draft_letter` completed: `issue` parameter added to the signature (v3_2 checked it but never received
  it); draft file name is now `draft_<date>_<issue>_<posture>.txt`; the `draft` event carries `issue`; the
  note under the letter comes from `playbooks[issue]` (was a reference to a `playbook` global that no
  longer existed).
- Rule 11: asks which issue the letter is about when the matter has more than one. Rule 15's example file
  name updated to the new pattern.
- `run.py` loads `lease_profile.json` if it exists and runs the extraction model only the first time.
  The notebook re-extracted on every run.
- `corpus.py` loads all playbooks silently at import; `check_all_playbooks()` prints the quote checks on
  demand (the notebook printed them in the loading cell).
- Added requirements.txt, .env.example, .gitignore, setup.sh, empty `matters/`.

## Before the move (from PROJECT_STATE.md, 2026-09-18 and earlier)

- 2026-09-24: multi-playbook support (`playbooks` dict, `active_playbooks`, `element_status`, deadlines
  tagged by issue); timeline as a DATE / EVENT / SOURCE / FILE table with `timeline`, `timeline full`,
  `timeline <issue>`; sent letters recorded through `add_communication` (rule 15) instead of a new tool.
- 2026-09-18: v3 restructured into the class notebook's section layout; PyPDF2 replaced pymupdf.
- 2026-09-15: second playbook deposit_claim_received v0.1, quotes verified; letter became a code template;
  `fetch_log` and `drafts` lists replaced by `fetch` and `draft` events.
- 2026-09-14: fact provenance: `fill_facts` proposes with stated/inferred tags and basis; `record_facts`
  is the only door into confirmed facts; `get_deadlines` refuses while anything is unconfirmed.
