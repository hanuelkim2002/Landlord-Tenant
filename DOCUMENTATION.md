# Documentation

How the code works right now. Kept by Claude Code so that a session does not have to read every module to
get oriented. Update it whenever a function, tool, file, event kind, or rule changes. Describe what exists,
not what is planned (that is TODO.md) or what changed (that is CHANGELOG.md).

## Modules

Listed from the bottom of the import chain up. Every module imports `config`. Everything imports without
`UF_API_KEY`; only a model call needs it (see Running and testing).

- `config.py`: paths (`ROOT`, `MATTERS`, `STATUTES`, `CASES`, `WIKI`, `PLAYBOOKS`), `WIKI_UNVERIFIED` (true
  when the environment sets `WIKI_UNVERIFIED=1`: development runs only, see `wiki.eligible`), the two model clients (`agent_llm` on
  `AGENT_MODEL`, `extract_llm` on `EXTRACT_MODEL`, both on the UF gateway at temperature 0; `AGENT_MODEL`
  is nemotron-3-super-120b-a12b unless the environment sets `AGENT_MODEL`, for trying another gateway
  model in one run; it drives the chat, `classify`, and `fill_facts`), and `squash`
  (collapse whitespace, lowercase; used for every quote comparison). Reads `.env` with python-dotenv. The
  two clients are `None` when `UF_API_KEY` is missing; `require_key()` raises with a clear message then,
  and `run.py` and `smoke_online.py` call it first. Imports nothing from the project.
- `lease.py`: lease intake. `ingest_pdf(pdf_path, matter_dir)` (store the PDF under its hash in the folder
  it is given, extract page text with PyPDF2, write `pages.json`), the `Clause` and `LeaseProfile` shapes (fifteen named clauses), `extract_profile`
  (one call to `extract_llm`), `quote_found` and `check_quotes` (each quote must appear on its cited page,
  or start there and run onto the next). Imports `config`. Imported by `record` and `run.py`.
- `calendars.py`: the court holiday calendars, loaded once at import from `calendars/*.json` into
  `court_calendars`. `load_calendar` (raises if a holiday is filed under the wrong year or its printed
  weekday is not the date's weekday), `court_calendar(county)` (the calendar of the circuit that includes
  the county, "Alachua" or "Alachua County", or None), `holidays_in(cal)`. Imports `config`. Imported by
  `deterministic`, `smoke`.
- `corpus.py`: the stored corpus, loaded once at import. `statute` (dict, section number to text, from
  `statutes/83.*.txt`), the playbook shapes (`Element`, `Clock`, `Spec`, `Playbook`), `load_playbook`,
  `check_playbook` (one playbook: every spec quote verbatim in its cited section, every
  quotation of 20 or more characters in the guidance and open questions verbatim in a stored section, a
  question for every element and an element for every question, `applies_if` naming a yes/no fact, clock
  cites among `sections`, the guidance parts the tool reads; prints a line per check via `report`, returns
  the failures), `check_all_playbooks` (all of them, plus a fact id shared by playbooks having the same type
  and question; returns the failures), and `playbooks` (dict, issue to `Playbook`, from
  `playbooks/*.yaml`). No model calls. Imports `config`, `lease` (for `LeaseProfile`, to check
  `compare_to`). Imported by `record`, `tools`, `agent`, `sheet`, `smoke`.
- `citations.py`: checks the ch. 83 cites and the quotes in a reply the model wrote. `SUBSECTION_START` (a marker such as
  `(3)` or `(b)` starts a subsection when a space and a capital letter or an opening quote follow it, or a
  lettered marker first, as in `(5)(a) If`; not after "subsection", "paragraph", "subparagraph"),
  `subsections(section)` (every `"(3)"` and `"(3)(a)"` of a stored section with its start and end in the
  text), `cites_in(text)` (every `83.x` cite with its parenthesized parts, spaces removed, each once),
  `check_cites(text, shown)` (returns `(cite, problem)` for a section not in `statutes/`, a section not in
  `shown`, or a subsection the section does not have; cites inside a quoted passage are skipped, since they
  belong to the quoted text and `check_quoted` checks those words). Quotes: `quoted_passages(text)` (every passage of 20
  or more characters in straight or curly quote marks, with its cite: the first cite after the closing mark
  on the same line, or else the last cite in the 80 characters before the opening mark with no quote mark
  in between, never one already used by the previous quote; "" when none; an id alone in quote marks,
  `FIELD_ID`, and an example right after "e.g.", `EXAMPLE`, are not quotes and are left out), `compact` (lowercase, curly
  quote marks and dash variants made plain, all whitespace removed; looser than `squash` because the model
  writes "tenant's" for "tenant’s" and the lease PDF text has broken words like "confir mation"), `is_in`
  (a quote in a text by `compact`, split at an ellipsis into pieces that must each appear, punctuation at
  the ends ignored), `where_in(quote, section)` (the narrowest subsection holding it), and
  `check_quoted(text, given)` (returns `(quote, cite, problem)`: a quote with a cite must be in that
  section and that subsection, and the problem names where it really is; a quote with no cite must be in
  `given` or any stored section). `caution(what, problem)` is the line printed to the tenant and
  `quote_label` names a quote in it by its first six words. These check that a cite exists and was
  available, and that quoted words are real and sit where they are cited. They cannot tell whether a cite
  fits a claim made in the reply's own words, and a paraphrase outside quote marks is not checked.
  `REPORTER` (a reporter cite such as `448 So. 2d 1208` or `103 Fla. 892`) and `check_case_cites(text,
  given)` (each reporter cite in a reply, outside quote marks, must appear in what the model was given, i.e.
  a `get_cases` receipt; returns `(cite, problem)`). Imports `corpus`. Imported by `agent`, `smoke`, `wiki`.
- `wiki.py`: the case wiki's code (see Files on disk, `wiki/`). `read_pages(root)` (every page in
  `cases/` and `topics/` under the wiki folder, by name: `name`, `path`, `meta` from the YAML front matter,
  `body`), `linked` (page names in a front matter field), `opinion(page)` (a case page's opinion from
  `cases/` with its star pages taken out, so a quote may run across a page break, and where each page
  starts; a star outside the opinion's own page range is the court's and stays), `pin` (the page a quote
  starts on), `case_list(topic)` (a topic page's "## Cases" section), `check_quotes` (every quote is
  word for word in its source, by `citations.is_in`, and starts on the page it cites; a statute quote must
  be in the subsection it cites, by `where_in`; a straight-quoted passage of 20 or more characters with no
  source is a problem), `lint(root)` (returns `(problems, warnings)`, lines starting with the page name:
  also front matter fields, section tags in `statutes/`, a case page with no section tag and no
  `scope_note`, links that go to no page, a case page's cite
  against its file's first line, its `Rule:` and `Reasoning:` lines, every topic it names listing it in
  "## Cases", an index out of date; warnings: a section tag the opinion never cites, a page changed since
  it was verified), `render_index` and `write_index`, `page_hash` (the page without its three sign-off
  lines), `verified(page)` (signed off and unchanged since), `verify(name, by, root)` (refused while the
  page has a problem; sets `verified_by`, `verified_on`, `verified_hash`, rewrites the index), and
  `check_wiki` (prints problems and warnings). `python wiki.py check | index | verify "<page>" "<name>"`.
  For the chat: `ROOT` (the wiki the chat reads; `smoke.py` points it at a copy), `eligible(page)` (a case
  page with a part II section tag that the author verified, or any tagged page when `WIKI_UNVERIFIED` is
  set), `issues_on(page, topic)` (the issue sections whose `Topic:` line names the topic),
  `case_topics(sections)` (`{topic: number of eligible cases on it}` for each topic an eligible page tagged
  with one of the sections names on an issue), `citation(meta)`, `plain_links`, and `render_cases(topic)`
  (every eligible case on the topic, oldest first: name and cite, the statute version read, then for each
  of its issues on the topic the question, the rule, the reasoning, and any dissent as quoted on the page,
  with "[not verified]" on unverified pages in a development run, ending with "These are what courts said in
  other people's cases. This tool does not decide whether any of them applies to you."). Imports
  `citations`, `config`, `corpus`. Imported by `tools`, `smoke`.
- `deterministic.py`: `check_elements` (element status), `court_days` (court business days from a
  county's court holiday calendar), `lease_value` and `lease_differs` (a lease quote
  read as a date or an amount, and compared with the tenant's value), `compute_deadlines` (the only date arithmetic), `matter_deadlines` (every playbook's
  deadlines, with one that two playbooks share listed once, tagged with both issues),
  `ISSUE_LABELS` (the labels `classify` can pick), and the two one-shot intake calls `classify` and
  `fill_facts`, both through `ask_json` on `agent_llm`. `classify` adds "other" next to the covered labels
  when a separate problem fits none of them (so `run.py` prints `NOT_COVERED`), and gives "other" alone
  when nothing fits. Imports `config`. Imported by `record`,
  `timeline`, `tools`, `agent`, `smoke`.
- `record.py`: the shared state. `matter` and `profile` live here and every other module reaches them as
  `record.matter` and `record.profile`. `confirm_fact` (the only code that writes a confirmed fact),
  `prune_proposals` (drops suggestions that can never be asked; see Data flow 3), `add_issues(issues,
  source, because)` (suggests each issue not already active or suggested, into `matter["proposed_issues"]`,
  logging `issue_proposed`; a label with no playbook, `other`, is recorded in `issues` at once with
  `issue_added`; a new suggestion clears an earlier rejection), `confirm_issue(issue)` (the tenant said yes:
  active, `issue_confirmed`, then its own related rules are checked), `reject_issue(issue, kind)` (no on the
  sheet, `issue_rejected`, or `drop` in the chat, `issue_dropped`: out of `issues` and `proposed_issues`,
  into `rejected_issues`, pending fact suggestions pruned; confirmed facts stay), `add_related_issues(
  renewed_fact=None)` (suggests every issue a related_issues rule of an active playbook points to once its
  fact is confirmed with the rule's value; skips a rejected issue unless `renewed_fact` is the rule's fact,
  just confirmed with a new value; returns what it suggested), `candidate_playbooks()` (active playbooks,
  then those of suggested issues),
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
- `timeline.py`: `render_deadlines(result)` (a `get_deadlines` result as the tenant reads it: per deadline
  its date, actor, clock, issues, status, rule and start, cite, and counting line; a clock with no date
  shows why; a clock's `shown_with` fact, when confirmed, on a line "beside it, from your record: ..."; with no deadline at all, one line saying so; then each waiting issue with its open facts; also the "Not yet." refusal), and
  `render_timeline(issue, full)`, the DATE / EVENT / SOURCE / FILE table, plus helpers
  `label`, `corrected` (the tenant confirmed a different value from the suggestion, compared as shown),
  and `confirmation_of`. A confirmed date's SOURCE reads "tenant (corrected, ...)" when corrected, and in
  `timeline full` a corrected fact reads "corrected from <how> <suggested value>". Not a tool; only the chat loop and `smoke.py` call it. Imports `record`,
  `deterministic`, `sheet` (for `shown`). Imported by `agent`, `smoke`.
- `tools.py`: the seven `@tool` functions and the `tools` list (see Tools the model can call), plus the
  plain helpers `pretty`, `quote_is_real`, and `build_letter`. Imports `record`, `config`, `corpus`,
  `deterministic`, `sheet`. Imported by `agent`, `schemas`, `smoke` (for `build_letter`, `get_deadlines`).
- `agent.py`: `RULES` (the fixed part of the system prompt; if the environment sets `RULES_FILE`, that
  file's text replaces it for the run, for trying versions of the rules), `rules_for(messages)` (`RULES`
  with its two markers filled: `[RULE 6]` with `LETTER_RULE` once a letter is in play, i.e. a tenant
  message in the chat matches `LETTER_WORDS` (letter, draft, write, writing) or the matter has a `draft`
  event, else nothing; `[RULE 8]` with `CASE_RULE` when CASE TOPICS has a topic, else `NO_CASES_RULE`, one
  line saying there are none; a `RULES_FILE` without the markers is used as is), `intake` (classify, propose facts, save; for a
  new matter only), `resume` (for an existing matter: log a `tenant_update` event, classify the update only,
  add new issues, propose facts from the update, save; returns the issues it added). Neither builds the agent: `run.py` runs the intake
  sheet first, then `build_agent`.
  `system_prompt(messages=())` (the whole system prompt, built from the record as it stands and, for the
  rules, the chat's messages so far), `prompt_from_record` (LangChain `dynamic_prompt` middleware that
  calls `system_prompt(request.messages)` before every model call), `build_agent` (a LangChain agent with that middleware and an in-memory checkpointer; no
  model call), `transcript_entry` (one thread message as a transcript line), and `chat` (the terminal loop; its
  thread id is the session id when one is open). Each turn, `chat` writes the tenant's message to the
  transcript before the model runs (so `propose_facts` can check the tenant's words), then every new message
  of the turn. `show_turn(new, messages)` transcribes the turn and prints the model's replies, a
  `draft_letter` result as is, and the turn's last `get_deadlines` result through `render_deadlines`; other
  tool results are not shown. Under a reply that quotes the statute (a quoted passage with a ch. 83 cite,
  `citations.quoted_passages`) and nowhere says "does not decide", it prints `NOT_DECIDED` ("This tool does
  not decide whether any of this applies to you.", from `not_decided_line`) and writes it to the transcript
  as a `footer` line (TODO item 30). It returns whether anything was printed. When nothing was (the reply was empty
  or blank), `retry_empty` sends the model `EMPTY_REPLY`, a program note asking it to reply, and shows that
  second turn; if it is empty too, it prints `NO_REPLY` ("[Check: no reply came back from the model. Please
  ask again.]"). Either way it logs `reply_empty`. The model's `reasoning_content` is never shown in its
  place: LangChain drops it, and it is the model's unchecked working, not a reply. After a turn in which the model called `propose_facts`, it runs the intake sheet; what the
  tenant confirmed there is sent to the model as a "[Program note: ...]" line at the front of the tenant's
  next message, and logged as a `program` transcript line. `timeline` commands go to the transcript too.
  After printing each reply, `chat` calls `check_reply(text, messages)` with the thread so far. It runs
  `citations.check_cites` against `sections_shown(messages)` (the active playbooks' `sections` plus every
  section fetched with `get_statute_section` in the thread) and `citations.check_quoted` against
  `given_text(messages)` (the system prompt, the lease quotes as plain text, the tenant's description and
  updates, and every thread message the model did not write). Each failure gets a "[Check: ...]" line
  printed under the reply, a `check` transcript line, and a `cite_flagged` or `quote_flagged` event. The
  reply is not held back or changed, and the model is not told.
  Imports `record`, `citations`, `config`, `corpus`, `deterministic`, `sheet`, `timeline`, `tools`. Imported by `run`, `smoke`.
- `run.py`: entry point. `start()` asks new or existing. `start_new` picks an existing tenant id or makes one
  (`new_tenant_id`), calls `new_matter` and `start_session("new")`, asks for the lease path (`ask_path`, which accepts a path dragged
  into the terminal), reads the lease (`read_lease`), asks for the description (`ask_text`, several lines
  ended by an empty line), then `intake`. `start_existing` lists matters, `load_matter` on the one picked
  (it stops if the matter has no lease profile), `start_session("existing")`, then asks "Anything new since last time?" with `ask_text`:
  text goes to `resume`, an empty answer goes on. Both return True when a matter is open. If `other` came in
  alongside a covered issue (active or suggested), the tenant is told part of it may not be covered. Then,
  if `pending_rows()` has anything, `run_sheet()`, which asks the suggested issues and the facts. If no
  active playbook is left after it (every issue was `other`, or the tenant turned the suggestions down), the
  tool says none of the situations it covers applies and stops: no chat; what was described and decided
  stays in the record for a later pipeline. Otherwise `chat(build_agent())`. Then `end_session()` on a
  normal exit. A session opens before intake or resume, so everything done in the visit carries its id.
- `sheet.py`: the intake sheet, asked and saved by code with no model. `pending_rows()` (first every
  suggested issue as a yes/no row, "This looks like: <description> Is that part of your situation?", with
  why it was suggested; then every changed, proposed, or missing fact of the active issues, once per fact
  id, with its question, type, and any suggestion; a yes to an issue calls `confirm_issue` and its
  questions follow, a no calls `reject_issue`), `parse_answer(kind, text)` (checks an answer against the element's type: dates as
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
- `dev/live_run.py`: entry point for live tests. Starts `run.py` itself and drives a whole session from a
  scenario file in `dev/scenarios/` (see Running and testing). Imports nothing from the project.
- `dev/eval.py`: entry point for measuring. Runs `dev/live_run.py` on scenarios several times each and
  scores the runs from their matters by code (see Running and testing). Imports `corpus` only to score.
- `schemas.py`: entry point. Prints each tool's name, first docstring line, and argument schema.

## Data flow

1. Lease PDF to profile (`read_lease` in `run.py`, new matters only; an existing matter's profile comes
   from `load_matter`). `ingest_pdf` stores the PDF and page text in `matter_dir()`, `extract_profile` asks the extraction model for a JSON `LeaseProfile`, `check_quotes` prints OK or FAIL
   for every clause, and the profile is saved. A FAIL is printed, not enforced: the profile is saved anyway.
2. Description to issues and proposed facts (`intake`). `classify` reads each label with its situation
   (`corpus.issue_menu()`: the playbook's `description`, and "None of the situations above." for `other`),
   is told a notice the tenant sent is not one the tenant received, and returns issue labels; an empty
   answer becomes `["other"]`; labels not in
   `ISSUE_LABELS` are dropped, and the rest go through `add_issues` (source "classify"): suggested, not yet active, until the
   tenant says yes on the sheet; `other` is recorded at once. For each active or suggested playbook
   (`candidate_playbooks`), `fill_facts` asks for a value, a `how` ("stated" or "inferred"), and
   the tenant's exact words for every element whose `source` includes `user`. An answer is kept only if
   its words appear in the description (substring after `squash`). The first playbook to propose a fact id
   wins. `intake` resets `facts` and `proposed` to empty before this, then saves `matter.json`.
2b. An update to an existing matter (`resume`). The text is logged verbatim as a `tenant_update` event;
   `description` is not touched. `classify` runs on the update only, and any label not already in
   `matter["issues"]` is suggested with `add_issues` (source "classify"), which also re-suggests an issue
   the tenant rejected before; then `add_related_issues`. Nothing is activated or removed here; the sheet
   asks. `fill_facts` runs on the update for every active or suggested playbook. A value equal to the confirmed fact of the same id is dropped; the rest go into
   `proposed`, replacing any older pending proposal for that id. A proposal next to a confirmed fact with a
   different value shows as `changed` (step 4). Facts two playbooks share by element id need nothing: there
   is one `facts` pool for the matter, so a new issue's shared elements are already known.
3. Proposed to confirmed (`record.confirm_fact`, the only code that writes `matter["facts"]`). It moves
   the value into `facts`, removes it from `proposed`, and appends a `fact_confirmed` event carrying the
   proposal's `how`, `basis`, and `proposed_value` (or `how: "asked"` when nothing was proposed) and
   `confirmed_in`. One caller: the intake sheet (`sheet.run_sheet`, the tenant answers code directly,
   `confirmed_in: "sheet"`). Then `add_related_issues`: if the fact triggers a related_issues rule, the
   related issue is suggested (source "related"); since the sheet rebuilds its list after every answer, it
   is asked next in the same sheet ("Suggested for your matter"), and on a yes its questions follow and the
   model's next prompt carries its guidance. Then `prune_proposals` drops every suggestion that can never be asked: all
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
5. Confirmed to deadlines (`get_deadlines`, then `matter_deadlines`, then `compute_deadlines` per playbook). Only issues with no proposed, changed, or
   missing row are computed; the others are returned as waiting. For each clock: skipped if `applies_if` is not a truthy confirmed fact; "need date for ..."
   if the trigger date is not confirmed; otherwise trigger date plus or minus `days` calendar days, status
   `passed` if before today else `upcoming`, with the cite and the playbook's `counting.convention`. A clock
   with `count: court_business_days` goes through `court_days` instead: one day at a time from the trigger
   date (not counted), skipping Saturdays, Sundays, and every holiday in the calendar of the circuit that
   includes the confirmed `premises_county`. Its row carries its own counting line naming the circuit and
   the memoranda used. With no calendar for the county, or a day in a year with no memorandum loaded, the
   row says "not computed: ..." and has no date; nothing is guessed.
   `matter_deadlines` then merges a row two playbooks share (same clock id, cite, date, and status) into
   one, and every row carries `issues`, the list of issues it belongs to.
6. Record to timeline (`render_timeline`). Rows come from confirmed date facts, freshly computed deadlines
   (from `matter_deadlines`, so a shared deadline is one row tagged `[issue, issue]`, kept under either
   issue by `timeline <issue>`),
   and events (see Files on disk). Sorted by date only; rows on the same day keep the order they were
   added (confirmed dates and deadlines first, then events in log order). `issue` filters deadlines and
   issue-tagged events; untagged events always show. `full` adds `fact_confirmed`, `fetch`, `cite_flagged`, `quote_flagged`, `reply_empty`,
   `deadlines_computed`, the issue events, `session_started`, and `session_ended` events.
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
  `issues` (active: confirmed by the tenant, plus `other` if classified), `proposed_issues` (suggested, not
  yet confirmed: `{"issue", "source", "because"}`), `rejected_issues` (turned down or dropped; a related rule
  skips them), `facts` (confirmed, element id to value), `proposed` (unconfirmed,
  element id to `{"value", "how", "basis"}`).
- `events.jsonl`: the history, one JSON object per line, append-only. Every event has `when` (local time,
  ISO, to the second) and `kind`, then `session` (the session id) if a session was open when it was
  written. Events written before sessions existed, or outside `run.py`, have no `session`. Kinds and their
  other fields:
  - `fact_confirmed`: `id`, `value`, `how` (stated, inferred, or asked), `basis`, `proposed_value`,
    `confirmed_in` ("sheet" or "chat"; missing on events from before 2026-09-27). Written by
    `record.confirm_fact`.
  - `fetch`: `section` (from `get_statute_section`) or `search` (from `search_statute`).
  - `cite_flagged`: `cite` (e.g. "83.64"), `problem` (not a stored section, not shown or fetched in this
    chat, or no such subsection). Written by `agent.check_reply` after a reply. `timeline full` only.
  - `reply_empty`: `recovered` (true if the model's second turn showed the tenant something). Written by
    `agent.retry_empty`. `timeline full` only.
  - `quote_flagged`: `quote` (the quoted words), `cite` (the cite next to it, or ""), `problem` (e.g. "is in
    83.49(3)(a), not 83.49(3)(b)"). Written by `agent.check_reply`. `timeline full` only.
  - `cases_shown`: `topic`, `cases` (the cites printed, oldest first), `unverified` (true, only in a
    development run with `WIKI_UNVERIFIED`). Written by `get_cases` when it prints; once per topic per
    session. `timeline full` only.
  - `deadlines_computed`: `issue`, `clocks` (ids of clocks that produced a date). One per active playbook
    per `get_deadlines` call.
  - `draft`: `issue`, `posture`, `cites`, `file`. Written by `draft_letter`.
  - `artifact`: `file` (original name), `sha256`, `note`. Written by `add_artifact`.
  - `communication`: `sent_on` (YYYY-MM-DD), `sender`, `recipient`, `channel`, `text`. Written by
    `add_communication`. The timeline sorts it by `sent_on`, not `when`.
  - `issue_proposed`: `issue`, `source` ("classify" or "related"), `because` (e.g. "the tenant's update",
    "claim_notice_received is true"). Written by `record.add_issues`. `timeline full` only.
  - `issue_confirmed`, `issue_rejected` (on the sheet), `issue_dropped` (the `drop` chat command): `issue`.
    Written by `record.confirm_issue` / `record.reject_issue`. `timeline full` only.
  - `issue_added`: `issue`, `source`, `because`. Written by `record.add_issues` for a label with no playbook
    (`other`), which has nothing to confirm. Before 2026-09-29 every issue was added this way, without
    confirmation; matters from before 2026-09-27 have issues with no event at all.
  - `tenant_update`: `text`, what a returning tenant typed as new, verbatim. Written by `resume`. Shown in
    the timeline as "tenant update" with the first words.
  - `session_started`: `how` ("new" or "existing"). Written by `start_session`. `timeline full` only, with
    the transcript's path in the FILE column.
  - `session_ended`: no other fields. Written by `end_session` on a normal exit. A session with a start and
    no end was cut off. `timeline full` only.
- `draft_<YYYY-MM-DD>_<issue>_<posture>.txt`: each drafted letter. A second draft on the same day with the
  same issue and posture overwrites the file; the earlier `draft` event remains. An identical redraft in the
  same session writes nothing (see `draft_letter`).
- `artifacts/<sha256[:12]>_<name>`: copies of files stored by `add_artifact`.
- `sessions/<session id>.jsonl`: the transcript of one session, outside the evidentiary log. One line per
  entry, each with `when` and `role`: `tenant` (`text`, as typed), `model` (`text`, plus `tool_calls`, a
  list of `{"name", "args"}`, when it called tools), `tool` (`name`, `text`: the result the model saw, and
  `shown`: what the program printed from it, for `get_cases`),
  `command` (`text`: a `timeline` command, handled without the model), `sheet` (`id`, `question`,
  `typed`: what the tenant typed, empty if they accepted the suggestion, `value`: what was saved, `issues_added`
  when the answer brought in a related issue), or
  `footer` (`text`: `NOT_DECIDED`, printed by the program under a reply that quotes the statute without
  saying the tool does not decide), or
  `program` (`text`: a note sent to the model: ahead of the tenant's message after a sheet, or
  `EMPTY_REPLY` after an empty reply), or `check` (`text`: a "[Check: ...]" line printed to the tenant: a
  caution about a cite or a quote from `check_reply`, or `NO_REPLY` from `retry_empty`). Only the chat is transcribed; the
  intake or resume calls before it are not.

Outside `matters/`: `lease.pdf` (a sample lease for test runs, gitignored; `run.py` asks for a path), `statutes/83.*.txt` and `.html` (the
read-only corpus; only `.txt` is loaded), `playbooks/*.yaml`, `.env` (the key), `docs/trials/` (dated records of trials, e.g. `2026-10-01-rules/`: the versions of the rules tried, the method, and the results; not kept current), `docs/structure/` (dated snapshots of the structure: a diagram of a
session, a diagram of the storage, and the Skills history; not kept current), and `calendars/` (read-only, like `statutes/`):
`court_holidays_circuit8.json` (Eighth Judicial Circuit: Alachua, Baker, Bradford, Gilchrist, Levy, and
Union counties; for each of 2026 and 2027 the holidays in the Chief Judge's memorandum, each with its date,
name, the date as printed, and its marker in the memorandum, plus the memorandum's source URL, issue date, and
fetch date) and `sources/`, the memoranda PDFs. A new year or circuit is added from its official memorandum,
checked against the PDF, never typed from memory.

`cases/` (read-only, like `statutes/`): `<volume>_<reporter>_<page>.txt`, one Florida appellate or federal
opinion per file, e.g. `448_So2d_1208.txt`, built by `dev/build_cases.py` from the author's Westlaw Find and
Print file of 2026-09-09 (82 opinions, the reporter cites of the case-pool candidate list; the print itself
stays outside the repo). Each file is the court's text only: the caption (the cite on the first line, as
Westlaw prints it, then court, parties, docket, dates), "Attorneys and Law Firms" and the panel, the opinion
with any concurrence, dissent, and footnotes, the star pages (`*1209`) that give pin cites, and "All
Citations" (parallel cites, e.g. Hankins v. Smith is `103_Fla_892.txt`, also 138 So. 494). Left out:
Westlaw's KeyCite flag, synopsis and holdings, West headnotes and their `[n]` markers in the opinion (only
numbers up to the opinion's headnote count; a bracketed number beyond it is the court's own), the copyright
line, and the negative-treatment table. 82 files: 81 from the print, and `50_So3d_503.txt` (the 2010
forms decision) from a Southern Reporter PDF the author supplied, by `dev/build_case_pdf.py`, because the
Westlaw print marks that opinion's added and deleted words by formatting. Only the opinion is stored (pages
503 to 504, up to "APPENDIX"): the appendix of forms marks its changes by underlining and strikethrough,
which the PDF's text loses too (it reads "Home andor Duplex"). Read by
`wiki.py` (quotes on wiki pages are checked against it) and the smoke checks; the chat reads the wiki's
pages, never `cases/` directly.

`wiki/` (the case wiki, after Andrej Karpathy's LLM wiki; written by Claude Code in development sessions,
never by a tenant session): `SCHEMA.md` (how pages are built: front matter, the quote syntax, the rule that
prose describes and connects and never states the law, the case and topic page layouts, the ingest steps,
what the checks cover), `cases/<Case name>.md` (one per opinion: front matter `kind`, `cite`, `file`,
`court`, `decided`, `statute_read`, `sections` (tags; empty for an opinion that reads no part II section,
which then needs `scope_note` and is never loaded for a tenant), `topics` (links), and the sign-off fields
`verified_by`, `verified_on`, `verified_hash`; then a line on court and posture, Facts, one section per
issue as a question with `Topic:`, `Rule:`, `Reasoning:`, and any `Dissent:`, Statute read, Related,
Disposition), `topics/<Topic>.md` (one per topic, made as cases raise them: `kind`, `sections`, the sign-off
fields; what it covers, today's statute text when a section speaks to it, "## Cases" listing every case page
that names it with its issue as a question, "## How they relate"), `index.md` (built by `write_index`:
pages by section tag, topics with their cases, every case with its verification), and `log.md` (one entry
per ingest or change, newest last). Quotes are written `"words" (at 1210)` for the page's own opinion,
`"words" ([[Plakhov v. Serova]] at 1223)` for another case's, `"words" (Fla. Stat. 83.49(3)(a))` for the
statute. As of 2026-10-01: 82 case pages (every opinion in `cases/`; 29 untagged, each with a
`scope_note`) and 40 topic pages; none verified yet. A decision approving forms has "What did the court approve?" and "Forms"
in place of issues; a statement outside the issues decided goes under "Also said". The folder opens in Obsidian as a vault; `.obsidian/` is gitignored.

## Tools the model can call

All in `tools.py`, in the `tools` list. The docstring is what the model reads; `python schemas.py` shows it.

- `get_statute_section(section)`: the stored text of one section, or a "No section ... stored" message
  listing what is available. Writes a `fetch` event.
- `search_statute(phrase)`: every section containing the phrase (case-insensitive), with a snippet.
  Writes a `fetch` event.
- `propose_facts(facts_json)`: JSON object keyed by element id, each `{"value", "how", "said"}`. Puts a
  suggestion in `proposed` only if the id is a user-sourced element of an active playbook, the value fits
  the element's type (`sheet.parse_answer`, and it is stored as parsed), `how` is stated or inferred, and
  `said` appears in what the tenant typed this session (`record.tenant_words`, by `citations.is_in`: an
  ellipsis may join pieces, each of which must appear; spacing, quote-mark style, and end punctuation are
  ignored).
  A value equal to the confirmed one is refused. Saves `matter.json`; returns what was taken and why
  anything was refused. Never confirms: the chat loop runs the sheet after the turn.
- `get_deadlines()`: works issue by issue. An issue is ready when none of its rows is proposed, changed, or
  missing. Returns JSON `{"deadlines": [...], "waiting": {issue: [open fact ids]}}`: the clocks of the ready
  issues from `matter_deadlines`, each with `issues` (a list; a deadline two issues share appears once), and,
  if any, the issues still waiting with their open facts. Refuses ("Not yet. ...", with the open facts by
  issue) only when no issue is ready. Writes a `deadlines_computed` event per ready playbook. The model
  does not report the result: the chat loop prints the turn's last `get_deadlines` result itself, through
  `timeline.render_deadlines`. A turn-ending tool (`return_direct=True`): when every tool the model called
  in a step is `get_deadlines` or `get_cases`, the agent stops after the tool and the model writes no reply,
  so it cannot repeat a printed line (TODO item 19); called with another tool, the turn goes on and rule 3
  still tells the model not to repeat or reword it.
- `get_cases(topic)`: `topic` must be one of the matter's CASE TOPICS (`tools.offered_topics`, i.e.
  `wiki.case_topics` for the active playbooks' sections); otherwise "No case topic named ...". A tool with
  `response_format="content_and_artifact"`: the model gets a receipt only (the names and cites of the cases
  printed), and the program gets `wiki.render_cases(topic)` as the message's artifact, which `show_turn`
  prints. So the model never sees a case's words and cannot retell one; a case quote it writes anyway is
  flagged by `check_quoted`. Writes a `cases_shown` event. Turn-ending, like `get_deadlines`: the printed
  cases end with "This tool does not decide whether any of them applies to you." and the model writes
  nothing after them. Every call prints something: a topic already printed in this session prints one line
  ("The cases on ... are printed above in this chat."; the model gets "[... Nothing new was printed.]"), and
  a topic not offered prints "This tool has no case topic named ..." with the matter's CASE TOPICS, so the
  tenant sees the topics there are.
- `draft_letter(issue, posture, ask, respond_within_days, delivery_method, obligation_quote,
  obligation_cite, consequence_quote, consequence_cite)`: `issue` must be in the matter and have a playbook;
  `posture` is preserve (no quotes), assert (obligation quote), or escalate (both quotes). Rejects any quote
  `quote_is_real` does not find. Returns the letter plus a "NOTE TO TENANT" line from the playbook's
  `guidance.postures.notice_sufficiency`. Writes the draft file and a `draft` event. If this session already
  drafted the same file and the new text is identical, it writes nothing and returns "[The same letter was
  already drafted in this session (<file>) and appears above. Nothing new was drafted.]". The chat loop
  prints this tool's output directly.
- `add_artifact(path, note)`: copies a file into `artifacts/` under its hash. Writes an `artifact` event.
- `add_communication(sent_on, sender, recipient, channel, text)`: rejects a `sent_on` that is not
  YYYY-MM-DD. Writes a `communication` event. Also used for a letter the tenant reports sending (rule 7).

## The system prompt

Built by `agent.system_prompt()` on every model call (through the `prompt_from_record` middleware), so it
always matches the record: facts confirmed on the sheet and issues added mid-chat show up on the model's
next call. The conversation itself is kept by the checkpointer; only the system prompt is rebuilt. In
this order:

1. `RULES`, through `rules_for`: 932 words always, plus rule 6 on letters (156 words) once a letter is in
   play, and rule 8 on cases in full (153 words) when there is a case topic, otherwise one line (since
   2026-10-01; rule 1's line on asking how a requested letter will be sent moved into rule 6, which already
   asked it). Pairs added from the eval baseline of 2026-10-01: the format line names issue ids; rule 3, a
   question about when or how long goes to `get_deadlines`; rule 6, the tenant's words are the ask, and the
   posture lines are never retold without quote marks; rule 8, the topic on the same notice, deposit,
   repair, entry, rent, fee, or lease term is called even if it does not name the exact point. Version F of the 2026-10-01 trial (`docs/trials/2026-10-01-rules/`), 1,130 words with a rule
   on cases added after it (TODO item 25) and later fixes for TODO item 23: rule 1's notices-clause line applies only to a requested letter; a pair for legality questions (quote, then "This tool does not decide that."); rule 2's fallback sentence used exactly, and cite the subsection the words sit in; rule 3 names the echoed empty result; rule 4 adds an example of asking for sheet facts. A role
   paragraph (organize lease, statute, and record side by side; not a lawyer; never advise, send, or work
   out a date), a format line (short plain sentences; each quote on its own line, source first, e.g.
   `Fla. Stat. 83.49(3)(a): "..."`; no labels like "Quote:", no field names), then nine numbered rules,
   each stated with "Not:" examples taken from real slips and the "Instead:" form: 1 organize, never advise
   (no must/may/can/should/entitled/required/rights/options about anyone outside quote marks; the conflict
   line only right after a lease quote and a statute quote on one point); 2 quote only what was given, word
   for word, fetch a section before citing one not in STATUTE SECTIONS, say plainly when nothing answers;
   3 dates only from ELEMENT STATUS, a lease quote, the tenant's words, or a tool result, deadlines only
   from `get_deadlines`, called alone, which the program prints, ending the turn; 4 the model proposes
   facts with `propose_facts`, the tenant confirms them on the sheet, nothing asked or confirmed in the
   chat; 5 open questions stay open (quote the open question's text; never resolve it or ask the tenant
   to); 6 letters only when asked, only through `draft_letter`, missing details asked once, posture lines
   copied word for word, then one line; 7 record messages and sent letters with `add_communication`;
   8 cases only through `get_cases`, called alone, which the program prints, ending the turn, only when the
   tenant asks what courts or cases say ("This tool has no cases on that." when no topic fits); 9 offer
   nothing the tenant did not ask for
   (rule 8 until 2026-10-01). Rules 1 to 7 cover the same ground as the seven rules of
   2026-09-30 (whose numbers TODO.md items 15 to 22 use); rule 9 was part of the old rule 1. Old rules 1 to
   15 (until 2026-09-30) map to the seven as: 1, 4, 8 to 2; 2 to 3; 3, 9 to 4; 5 to 5; 6, 11, 12 to 6;
   7, 13 to 1; 14, 15 to 7; 10 dropped.
2. `LEASE PROFILE`: the whole profile as JSON.
3. `PLAYBOOKS`: for each active playbook, YAML of its `issue`, its `guidance`, and its
   `spec.open_questions` (which rule 5 refers to). The rest of `spec` never enters the context.
4. `STATUTE SECTIONS`: the text of every section the active playbooks list in `sections`, once each. An
   issue with no playbook yet adds none.
5. `CASE TOPICS (for get_cases; number of cases on each)`: `agent.case_topics_text()`, one line per topic
   from `tools.offered_topics()`, or "none for these issues" (always, until the author verifies pages).
6. `ELEMENT STATUS (by issue)`: `element_status()` as JSON at the moment of the call.

The program note after a sheet still tells the model, in the conversation, that a sheet just ran.

## Playbook schema

Nine playbooks, one per label in `ISSUE_LABELS` except `other`: deposit_not_returned,
deposit_claim_received, repair_not_made, notice_received_nonpayment, notice_received_violation,
landlord_entered_unannounced, rent_increased, wants_to_leave_early, lease_ending. The seven written
2026-09-27 are version 0.1 with `verified_by: null` until the author's hand check. Two have no clocks,
and say why in `counting.note`: landlord_entered_unannounced (83.53(2) is in hours), rent_increased (no
section on notice of a rent increase). notice_received_nonpayment computes 83.56(3) in court business days
and leaves 83.60(2) uncomputed. Facts shared across playbooks by id: `claim_notice_date`,
`tenancy_terminated`, `deposit_amount`, `eviction_action_filed`, `fixed_term_lease`, `term_end_date`,
`month_to_month`, `monthly_rent`.

One YAML file per issue in `playbooks/`. `load_playbook` validates it against `Playbook` and raises if a
section is not in `statutes/`, a clock's `trigger` is not a date element or an element's `compare_to` is not a `LeaseProfile` field.
After all playbooks load, `corpus.py` also raises if a related issue is not in `ISSUE_LABELS` or its
condition's fact is not an element of any playbook. Keys the `Playbook` class does not define are dropped on load.

- `issue`: the label; must be in `deterministic.ISSUE_LABELS` to be classified. Key of `playbooks`.
- `description`: the situation the playbook covers, in one line, naming the event that starts the issue
  rather than background facts (the classifier reads an update on its own). Read by `corpus.issue_menu`,
  which `classify` receives instead of bare label names.
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
    (before, after), `cite`, `quote`, optional `consequence`, `delivery`, `applies_if`, `shown_with` (a
    date element shown beside the computed date once confirmed, e.g. the date a notice itself states;
    checked by `load_playbook`), `count`
    (`calendar_days`, the default, or `court_business_days`; a playbook with a court-day clock must have a
    `premises_county` element, checked by `load_playbook`). Read by
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
    python -c "from corpus import check_all_playbooks; check_all_playbooks()"   # playbook checks: every line OK
    python schemas.py                                                            # what the model sees per tool
    python dev/build_cases.py "<Westlaw print>"                                  # once: builds cases/
    python wiki.py check                                                         # wiki checks: no problems

- `python dev/build_cases.py <print>`: the print is the Westlaw Find and Print file (Rich Text, turned into
  plain text by macOS's `textutil`; a `.txt` is read as is). `split_print` finds each opinion (a cite on its
  own line with a court named below it; a bare cite in a negative-treatment table has a summary instead) up
  to Westlaw's "End of Document"; `court_text` keeps the caption and everything from "Attorneys and Law
  Firms" on, minus the headnote markers; `file_name` names the file from the cite. An opinion whose print
  carries Westlaw's note "Additions are indicated by ... and deletions by ..." is skipped and listed.
  Rerunning on the same print writes the same files.
- `python dev/build_case_pdf.py <key> <pdf>`: one opinion from a reporter PDF, for an opinion listed in its
  `OPINIONS` (where it stops, where the attorneys and the opinion start). Drops the running heads, marks
  each new reporter page with a star page, removes hyphens between lowercase letters (in the listed
  opinions, each is a line-break hyphen; real compounds there use dashes), and adds the labels the
  Westlaw-built files carry, so the case-file smoke checks hold for it. Spaces the PDF loses where lines
  join ("outlegal") stay lost; quote checks ignore spaces.

- `python smoke.py`: needs the saved test matter `matters/t-test/test-001/` with its lease profile. Opens it
  with `load_matter` and prints `list_matters()`, then runs the playbook checks (one named check, "every
  playbook check is OK", fails if any line of `check_all_playbooks` does), element status and deadlines on hand-typed facts with today fixed at 2026-09-08, the case corpus (every file in `cases/`
  named for the cite on its first line, none of Westlaw's material, no headnote marker opening a line,
  attorneys and parallel cites present, and `court_text` on a hand-typed opinion), the case wiki (the real
  pages pass `lint`; on a throwaway copy, a changed word, a wrong pin page also across a page break, a
  quote with no source, a statute quote in the wrong subsection, a link to no page, an untagged case page
  with no `scope_note`, and a case missing from
  its topic's Cases list are each caught; a verified page stops counting as verified once edited; `verify`
  refuses a page with a problem), cases in the chat on the scratch matter (no topic offered while no page
  is verified; on a copy with Durene and Hankins verified, Durene's topics are offered and Hankins's,
  untagged, are not; `get_cases` prints Durene in the courts' words with the closing line and logs it,
  gives the model only the names, prints nothing the second time in a session, and refuses a topic not
  offered; a case cite not shown is flagged), a hand-typed update
  against those facts (one changed row, one unchanged, one lease value left alone, `get_deadlines`
  refusing), the letter template, the cite checks (subsection markers in order in every stored section,
  each kind of bad cite flagged, and a real, shown but wrong cite passing), the quote checks (which cite goes
  with which quote, a good quote passing despite apostrophes or an ellipsis, items 5 and 6 of TODO.md as
  they would look in quote marks), and both
  timelines. The timelines read the real `events.jsonl` of `test-001`. Importing `tools` and `timeline`
  also checks that the modules import. Last, on a scratch copy `matters/t-smoke/m-001` (removed at the
  end, even after a failure), about thirty named checks of the code that writes to a matter: listing and
  ids, sessions and their tags, `propose_facts` taking one suggestion and refusing five for five reasons,
  the sheet with scripted answers (accept, correct, bad input, a changed fact, an `applies_if` fact, a
  skip), `get_deadlines` waiting and then answering, the prompt following the record, a flagged cite and
  quote printed and logged, the tenant's description counting as given, events, the transcript, and the
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
- `python dev/live_run.py dev/scenarios/<name>.json`: a live session without typing. The scenario gives the
  lines typed before the sheet (`start`), rules for the sheet (`sheet`: a piece of a question's text to a
  list of answers used in order, so a bad answer then a good one tests the re-ask; a question no rule
  matches gets "?"), and the chat lines (`chat`, then "bye"). Questions are found on screen by their type
  hint, since each prints on the same line as the previous prompt. A sheet that appears mid-chat is answered
  by the same rules. Prints the whole screen and the answers typed. Calls the model and writes a real matter:
  use the test tenant `t-test`; every "new" scenario adds a matter. When several rules match a question,
  the longest one with answers left is used. Scenarios, each with its expected results in `about`:
  `nonpayment_3day.json` (the 83.56(3) court-day count, 2026-09-24), `repair_notice.json` (the 83.60(1)(b)
  date 2026-09-17 and a preserve letter with its note), `claim_letter.json` (a claim letter reported
  mid-chat: a sheet in the chat, deposit_claim_received added, objection 2026-10-10 and remit 2026-10-22),
  `not_covered.json` (a roommate dispute: only `other`, the tool stops before the sheet),
  `entry_unannounced.json` (landlord_entered_unannounced; no clocks, a preserve letter; asks "Was it
  legal?"), `rent_increase.json` (rent_increased; no clocks; asks whether it is allowed and whether it is
  retaliation), `leave_early.json` (wants_to_leave_early; the 83.49(5) date 2026-11-08; asks what happens if
  they just leave), `month_to_month_end.json` (lease_ending; both 83.57(3) dates 2026-10-31; asks whether 30
  days notice is required), `deposit_cases.json` (deposit_not_returned, no letter; asks what courts have said
  about a late notice of claim, whether that means the whole deposit comes back, and about lawyers' fees;
  run with `WIKI_UNVERIFIED=1` until pages are verified). The four before it each ask a question the tool must not answer, and answer every
  suggested issue but the intended one with no, keyed on the intended issue's full description (the driver
  takes the longest matching rule, so a shorter key loses to "Is that part of your situation?"). The driver also
  handles run.py exiting by itself.
- `python dev/eval.py run <out dir> <repeats> [scenario ...]`: runs scenarios several times each, several
  sessions at once (`--parallel N`, default 8), and scores every run by code (`python dev/eval.py score <out
  dir>` scores again). With no scenario named, every scenario with an `expect` block. Each run is
  `dev/live_run.py` under its own scratch tenant `matters/t-eval-<out dir name>-<scenario>-<k>`, seeded with an
  `m-000` copy of the test matter so the id exists; the run's matter is the one its screen names.
  `--project <folder>` runs another copy of the project, e.g. a git worktree at an older commit, to compare
  (the scenarios and the seed still come from this copy). The `expect` block: `issues` (the playbook issues
  active at the end), `stops` (the tool stops before the chat), `not_covered_note`, `deadlines` (issues with a
  `deadlines_computed` event naming a clock), `letters` (`draft` events), `turns` (per chat line, found by a
  piece of it: tools `called` and `not_called`, regexes the turn's replies `must` have and `must_not` have
  outside quote marks, the `topics` allowed for `get_cases`), and `screen_must_not`. Every reply is also
  measured: empty turns, program cautions, field names, a printed deadline date repeated, and two word screens
  (`LAW_WORDS`, `OFFER_WORDS`) that only mark a reply for a person to read. Writes `runs/` (screens),
  `runs.json`, `transcripts/` (each run as text marking who produced each part), `scores.json`, and
  `summary.json`, and prints a table per scenario. The eval scenarios are `dev/scenarios/eval_*.json`:
  one realistic lay-tenant story per playbook (`deposit_ghosted`, `claim_carpet`, `entry_shower`,
  `lease_end_renewal`, `nonpayment_taped`, `violation_dog`, `rent_hike_duplex`, `repair_mold_apt`,
  `leave_early_family`), three stories no playbook covers (`nc_roommate`, `nc_noise`, `nc_towing`), one
  covered problem next to an uncovered one (`nc_mixed_heater`), and three with facts like a case in the wiki
  and plain questions about judges (`cases_late_claim`, `cases_3day_cash`, `cases_retaliation`); run with
  `WIKI_UNVERIFIED=1` until pages are verified. Each scenario's `about` says what it tests.
- `python run.py`: interactive. Asks new or existing. A new matter reads the lease (one extraction call)
  and runs intake (two calls). An existing matter asks what is new: an update runs `resume` (two calls).
  Then the intake sheet asks every open fact (no model), and the chat starts. Chat commands, handled by the loop without the
  model: `timeline`, `timeline full`, `timeline <issue>`, `issues` (the active and suggested issues),
  `drop <issue>` (takes an active issue out, logged; the chat ends if no covered issue is left); an empty
  line or `bye` exits. Every run appends
  to the matter's `events.jsonl`.
