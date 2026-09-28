# Changelog

Newest first. One entry per change, dated. Say what was replaced as well as what was added, so a future
session can see why the code is the way it is.

## 2026-09-27

- Seven playbooks, version 0.1, written against `statutes/` in the format of the deposit playbooks:
  repair_not_made (83.51, 83.56(1) and 83.60(1)(b) 7-day notices), notice_received_nonpayment (83.56(3),
  83.60; no clocks), notice_received_violation (83.56(2)(a) and (b) 7-day periods), landlord_entered_unannounced
  (83.53, 83.67; no clocks), rent_increased (83.46, 83.57, 83.64, 83.425; no clocks, the stored text has no
  rent-increase notice section), wants_to_leave_early (83.49(5) 7-day notice, 83.682(1) servicemember
  30 days, 83.595), lease_ending (83.57(3) month-to-month 30 days for each party, 83.575, 83.58). Each
  carries the 83.42(1) exclusion quote for college housing, undecided. Two new related rules:
  withheld_for_repairs and reason_is_landlord_noncompliance bring in repair_not_made. Checked before
  installing by a stricter one-off script (145 checks: quotes in the prose too, a question per element,
  applies_if on yes/no facts, shared fact ids consistent); playbook quote checks 44 OK. New smoke section
  runs every playbook through the sheet, deadlines, and a letter; the "no playbook adds no sections" check
  now uses `other`. Checked live: one update about a broken AC, withheld rent, and a 3-day notice brought
  in both new issues with sensible suggestions. Clocks that cannot be computed yet, and folding the stricter
  checks into `check_all_playbooks`, went to TODO.md. Replaces the TODO item listing the seven to write.
- deposit_not_returned.yaml: `guidance.postures.notice_sufficiency` (printed under every letter for this
  issue as a note to the tenant) reworded to face the tenant. It replaces text that ended with an
  instruction to the model ("Say so when it is missing") and stated a conclusion ("cannot be cured
  afterward"). The new note says what the tool tracks and quotes 83.49(5); both quotes were checked by
  substring against `statutes/83.49.txt` before writing, since the playbook quote check does not cover
  guidance prose. Playbook quote checks all OK.
- deposit_claim_received.yaml: the fact `claim_notice_received_on` renamed `claim_notice_date`, the id
  deposit_not_returned already uses for the same date (when the tenant received the landlord's notice),
  along with the `tenant_objection_deadline` trigger and the question key. Facts carry across issues by
  id, so the tenant is now asked this date once instead of twice. In deposit_not_returned the fact still
  applies only once a notice is confirmed received; in deposit_claim_received it is always asked. Playbook
  quote checks all OK. Existing test matters keep the old key in `matter.json` as an unused leftover; both
  also hold `claim_notice_date` with the same date. Smoke fixture and counts adjusted; the "asked once"
  check now covers this date too.
- A deadline two issues share is listed once, tagged with both (the author's decision). New
  `deterministic.matter_deadlines` merges rows with the same clock id, cite, date, and status; both
  `get_deadlines` (rows now carry `issues`, a list, instead of `issue`) and the timeline use it, replacing
  their own per-playbook loops. `claim_notice_deadline` now shows once as
  `[deposit_not_returned, deposit_claim_received]`, and `timeline <issue>` keeps it under either issue.
  Three new smoke checks.
- Live run of the Skills chain on `t-test/m-001` (one issue): the tenant reported the claim letter in the
  chat, the model proposed the change, the sheet confirmed it, `deposit_claim_received` was added by its
  related rule and logged, its questions came up in the same sheet, corrections typed in the chat came back
  as changed rows, and the model then gave both issues' deadlines (objection 2026-10-10, remit 2026-10-22)
  with the remit condition stated the right way round. Two findings added to TODO.md: a shared clock
  listed twice (harness), and an "as you just confirmed" slip (model behavior). No code changed.
- Skills, step 3 of 3: statute sections come from the playbook. `statutory_hook: "83.49"` (read by no
  code) became `sections: ["83.49"]`, checked against `statutes/` by `load_playbook`; `system_prompt`
  loads the sections of the active playbooks, so an issue with no playbook yet adds none (a `lease_ending`
  label used to add 83.57, 83.575, and 83.58). `deterministic.ROUTING` (label to unverified section list)
  became `ISSUE_LABELS`, the labels `classify` can pick; its section lists moved to the TODO Playbooks
  item as unverified research candidates. README's Skills line now says guidance and sections load when an
  issue becomes active. The planned `load_skill` tool was dropped (the author's decision): code, not the
  model, decides what is in the prompt. The Skills TODO section is done. Two new smoke checks; checked
  that a playbook naming a section not in `statutes/` is refused.
- Skills, step 2 of 3: related issues as data. In both deposit playbooks `when: claim_notice_received ==
  true` (a string no code read) became `when: {fact: claim_notice_received, equals: true}`, typed in
  `corpus.py` (`Condition`, `RelatedIssue`) and validated after load. New `record.add_issues`, the only
  code that adds an issue, logging a new `issue_added` event (source and reason); `intake` and `resume`
  use it instead of writing `matter["issues"]` directly. New `record.add_related_issues`, run after every
  confirmed fact and in `resume`: a matching rule adds its issue at once, the sheet says "Added to your
  matter" and asks the new issue's questions in the same run, and the model's next prompt carries its
  guidance. `timeline full` shows added issues. CLAUDE.md names `add_issues` as the only door into
  issues. Playbook quote checks all OK after the YAML edits. Seven new smoke checks on a second scratch
  matter.
- Skills, step 1 of 3: the system prompt is rebuilt from the record on every model call. `build_agent` now
  gives `create_agent` a `dynamic_prompt` middleware (`prompt_from_record`) that calls the new
  `system_prompt()`; before, the prompt was built once and frozen for the session. The conversation is
  kept by the checkpointer as before. The `fact_status` tool is removed (the prompt's element status is
  now always current); rules 3 and 9 point at ELEMENT STATUS instead. This also settles the model-behavior
  item about the stale intake-time status. Two new smoke checks; checked live on a scratch matter that a
  fact changed in the record between two turns shows up in the model's next answer, with the history kept.
- TODO.md: dropped the note about clearing a test matter's history between runs; the smoke scripts now use
  scratch copies and never write to the test matters. No code changed.
- The timeline marks a fact the tenant corrected: "tenant (corrected, confirmed ...)" in the plain
  timeline, "corrected from <how> <suggested value>" in `timeline full`, replacing the suggestion's own
  tag (a corrected `early_or_periodic = False` used to read "inferred"). New `timeline.corrected`. The
  scratch smoke run now corrects two suggestions on the sheet; four new checks.
- `build_letter` strips a trailing period from the ask before adding its own, so a request ending in "."
  no longer prints ".." (seen in the first live run). One new smoke check.
- Stale suggestions are cleared: new `record.prune_proposals`, called by `confirm_fact`, `intake`,
  `resume`, and `propose_facts`. It drops a suggestion only when it can never be asked (the lease gives
  the value, its condition is confirmed as no with no change pending, or no issue asks for it). Before
  this, suggestions such as `deposit_amount` sat in `matter.json` forever. The first version also dropped
  a suggestion whose condition was a confirmed no with a change to yes pending; the smoke run caught it
  (the notice date lost its suggestion once the tenant accepted the change), and pending changes now keep
  it. Four new smoke checks.
- A tenant fact that differs from the lease is shown next to it. Playbook elements gain an optional
  `compare_to: lease_profile.<field>` (checked by `load_playbook`); both deposit playbooks set it on
  `tenancy_terminated` against `term_end`. `check_elements` adds `lease_says`, the lease's exact words,
  when the lease value (new `lease_value`: printed dates, dollar figures) differs from the tenant's; the
  sheet prints "your lease says" with it, and the model sees it in the element status. The tool shows both
  and decides nothing. Before this, a tenant date a year off the lease's term end passed unremarked.
  Playbook quote checks all OK after the YAML edit. Five new smoke checks; the scratch run now asks the
  termination date on the sheet, so the note is tested where the tenant sees it.
- README.md: the playbooks in scope grow from six to nine, adding notice_received_nonpayment,
  landlord_entered_unannounced, and wants_to_leave_early, so every classifier label but "other" gets one
  (the author's decision).
- TODO.md: the `ROUTING` preloading item moved from "Harness and code" into the Skills `load_skill` item,
  since every label but `other` will get a playbook and on-demand loading replaces preloading. The
  Playbooks item now lists all seven playbooks still to write, each carrying its own checked section list
  in `statutory_hook`. The Skills `related_issues` item no longer names the removed `record_facts`.
  No code changed.
- Permanent smoke checks for code that writes to a matter, replacing the hand tests on throwaway copies.
  New `checks.py` (named OK/FAIL checks, a summary line, and scratch copies of the test matter that can
  only be made and removed under `matters/t-smoke*`). `smoke.py` gained 31 checks on `t-smoke/m-001`:
  sessions, `propose_facts`, the sheet, deadlines, `fact_status`, events, the transcript, the timeline.
  `smoke_online.py` gained 7 `resume` checks on `t-smoke-online/m-001` (2 of them depend on the model).
  Checked that the checks fail when they should: with the tenant-words test removed from `propose_facts`,
  exactly the two checks covering it failed and the scratch copy was still removed. The test matter's files
  are unchanged by smoke runs. CLAUDE.md: every named check must be OK, and a change to code that writes to
  a matter gets a check.
- Intake sheet, step 3 of 3: the model can no longer confirm a fact. `record_facts` is replaced by
  `propose_facts`, which only adds to `proposed` and checks each suggestion in code (the id is a fact of the
  matter's issues, the value fits its type, how is stated or inferred, and the cited words appear in what
  the tenant typed this session, from the new `record.tenant_words`). New read-only `fact_status` tool,
  replacing the element status `record_facts` used to return. The chat loop writes the tenant's message to
  the transcript before the model runs, runs the sheet after any turn that proposed a fact, and sends what
  the tenant confirmed to the model as a "[Program note: ...]" at the front of the next message (added
  after the first live run showed the model did not know the sheet had run). `run_sheet` returns the saved
  facts instead of a count. Rules 3 and 9 reworded. CLAUDE.md's "only door" line updated. Tested offline
  (one proposal taken, five refused for five reasons) and live on `t-test/m-001` (a date corrected in the
  chat, confirmed on the sheet, then deadlines on the next turn). The intake sheet item is done.
- Intake sheet, step 2 of 3: `run.py` runs the sheet after intake or resume (and on an existing matter with
  facts still open), then builds the agent. `intake` and `resume` no longer build the agent; they only
  update the record, and `start()` returns True when a matter is open. This way the prompt's ELEMENT
  STATUS is taken after the sheet. Tested live: new matter `t-test/m-001` from the sample lease, five facts
  confirmed on the sheet (one inferred suggestion corrected), and the model gave deadlines on the first
  question with no confirmation back-and-forth.
- Intake sheet, step 1 of 3: new `sheet.py`. `pending_rows` lists every changed, proposed, or missing fact
  of the matter's issues once per fact id; `run_sheet` asks them in the terminal one at a time, checks each
  answer against the element's type (`parse_answer`), pre-fills suggestions with the tenant's words,
  accepts `?` to skip, and saves through the new `record.confirm_fact`. That function is now the only code
  that writes a confirmed fact; it replaces the body of `tools.record_facts`, which now calls it. Every
  `fact_confirmed` event gains `confirmed_in` ("sheet" or "chat"). CLAUDE.md's "only door" line updated.
  Not called from `run.py` yet. Tested offline on a throwaway copy of `t-test/test-002` with scripted
  answers (corrections, bad input re-asked, a changed fact, an applies_if fact appearing, a skip).
  This replaces the planned code-side `confirm_facts` guard.
- Sessions, step 2 of 2: transcripts. `record.append_transcript` writes to
  `matters/<tenant>/<matter>/sessions/<session id>.jsonl`; `agent.chat` writes every new message of each
  turn (tenant, model with its tool calls and arguments, tool results) and every `timeline` command.
  `timeline full` puts the transcript path next to "session started". Tested live on `t-test/test-002`:
  the transcript held the question, both tool calls with arguments, both results, the reply, and the
  command; the session's tagged events matched the visit. The sessions item is done.
- Sessions, step 1 of 2: `record.start_session(how)` / `record.end_session()` log `session_started` and
  `session_ended`, and while a session is open `append_event` tags every event with its id (a time-ordered
  uuid7). `run.py` opens the session once the matter is chosen, before intake or resume, and closes it after
  the chat. The chat's thread id is now the session id (was a fresh uuid7 per chat). `timeline full` shows
  sessions. `render_timeline` sorts by date only, keeping the order rows were added within a day; before,
  same-day rows sorted alphabetically, which would have put "session ended" before "session started".
  Tested on a throwaway copy of the test matter.
- TODO.md reorganized by the author's priority: structure and code first, model behavior later. "Guards and
  known issues" split into "Harness and code" and "Model behavior (later)"; playbook data items moved under
  "Playbooks". The `lease_ending` item split into its code half (`ROUTING` preloading sections for issues
  without a playbook) and its model half (the classifier). New harness item for stale proposals. No code
  changed.
- Resume, step 3 of 3: `start_existing` asks "Anything new since last time?" after loading a matter; text
  goes to `agent.resume`, an empty answer straight to chat. `ask_description` in `run.py` became
  `ask_text(prompt)` and serves both questions. Tested live on a copy of the test matter
  (`t-test/test-002`, so `test-001` stays one issue for the smoke scripts): the claim-letter update added
  `deposit_claim_received`, the model showed `claim_notice_received` as false against true and recorded
  true, the claim facts were confirmed, and `get_deadlines` gave the objection date (Oct 10) and the remit
  date (Oct 22). Timeline shows the update. Two rule slips from that run added to TODO.md. The resume item
  is done.
- Resume, step 2 of 3: `agent.resume(update_text)` for an existing matter. Logs the update verbatim as a
  new `tenant_update` event (the description keeps the first story), classifies only the update, appends
  new issues without removing any, runs `fill_facts` on the update for every active playbook, drops values
  equal to confirmed facts, and lets a newer proposal replace an older pending one. The timeline shows a
  "tenant update" row. Nothing calls `resume` yet. Tested on a throwaway copy of `test-001` with a
  claim-letter update: `deposit_claim_received` added, `claim_notice_received` shown as changed from False
  to True, shared facts known in the new issue, the notice's dated and received dates proposed separately.
- Resume, step 1 of 3: `check_elements` has a fifth status, `changed`, for a confirmed fact whose id also
  has a different value waiting in `proposed`. The row carries both values and the tenant's words; before
  this, any confirmed fact read as `known` and a differing proposal was invisible. Only confirmed facts can
  be changed this way, not lease values. `get_deadlines` now also waits on changed rows. Rule 3 says to show
  both values and record whichever the tenant picks. `smoke.py` gained an offline block that checks all of
  this with a hand-typed update.
- Resume decisions written into TODO.md (A to D), replacing the open question on what `intake` classifies
  for a returning matter. Checked offline that facts shared by element id already carry across issues.
  Added a TODO item for the one fact the two deposit playbooks name twice. No code changed.

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
