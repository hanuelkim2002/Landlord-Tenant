# Documentation

How the code works right now. Kept by Claude Code so that a session does not have to read every module to
get oriented. Update it whenever a function, tool, file, event kind, or rule changes. Describe what exists,
not what is planned (that is TODO.md) or what changed (that is CHANGELOG.md).

## Modules

Listed from the bottom of the import chain up. Every module imports `config`. Everything imports without
`UF_API_KEY`; only a model call needs it (see Running and testing).

- `config.py`: paths (`ROOT`, `MATTERS`, `STATUTES`, `CASES`, `WIKI`, `PLAYBOOKS`, `SKILLS`), `WIKI_UNVERIFIED` (true
  when the environment sets `WIKI_UNVERIFIED=1`: development runs only, see `wiki.eligible`), the two model clients (`agent_llm` on
  `AGENT_MODEL`, up to 8000 output tokens since applied answers run longer, `extract_llm` on `EXTRACT_MODEL`, both on the UF gateway at temperature 0; `AGENT_MODEL`
  is nemotron-3-super-120b-a12b unless the environment sets `AGENT_MODEL`, for trying another gateway
  model in one run; it drives the chat), and `squash`
  (collapse whitespace, lowercase; used for every quote comparison). Reads `.env` with python-dotenv. The
  two clients are `None` when `UF_API_KEY` is missing; `require_key()` raises with a clear message then,
  and `run.py` and `smoke_online.py` call it first. `shorten(text, limit, rest="")` (a passage cut at its last word
  before `limit` characters, with " ..." and where to read the rest; for the printed words and the lease search).
  Imports nothing from the project.
- `lease.py`: lease intake. `ingest_pdf(pdf_path, matter_dir)` (store the PDF under its hash in the folder
  it is given, extract page text with PyPDF2, write `pages.json`), the `Clause` and `LeaseProfile` shapes (sixteen named clauses; `maintenance_and_repairs`, added 2026-10-04 for
  TODO item 76, is optional, so a profile read before it loads with it `None`, not read; `LeaseProfile.clauses()`
  gives the clauses read, as (name, clause), and every reader of a profile walks it that way; its description asks
  for one passage copied as printed, headings inside it included, since Gemma first joined two subsections and
  dropped the heading between them, and the quote failed `check_quotes`), the profile as the model reads it
  (TODO item 77: `LABELS`, each field in plain words; `SECTION_NUMBER` and `lease_cite(clause)`, the cite to use,
  "Lease Section 3.1", "Lease Article 7", or "Lease, page 1" for a clause with no number; `LEASE_CITE`, such a cite
  in a text, used by `replies` and `tools.draft_letter`; `lease_lines(profile)`,
  a line per clause, label, cite, and words, or that the reading found no such clause, or that it was not read;
  no field name, since given the profile as JSON the model cited clauses by field name), `extract_profile`
  (one call to `extract_llm`), `quote_found` and `check_quotes` (each quote must appear on its cited page,
  or start there and run onto the next). Lease clauses, no model: `lease_text(pages)` (the pages joined, each
  page's running header or footer, `FOOTER`, "... | Page 2 of 12" at its start or end, taken off first, and where each
  page starts; until TODO item 82 `FOOTER` was matched anywhere in the joined text and took up to 80 characters of the
  lease's words before the bar with it), `lease_clauses(pages)` (the lease split at its numbered headings, `HEADING`,
  "5.4. Vehicles."; a heading counts only if its number closely follows the last one's, so a cross-reference is not
  taken for one; each clause's number, title, page, text with a following article heading, `ARTICLE`, removed, and
  `start` and `end` in `lease_text`), `find_in_lease(phrase, pages, limit=5)` (TODO item 82: the numbered clauses
  holding a phrase, and the pages holding it outside any clause with a passage around it; compared by `plain`,
  letters and digits only, lowercase, since the PDF text breaks words, "air -conditioning"; a phrase of three
  letters or digits or fewer must stand as a whole word). Imports `config`. Imported by `record`,
  `agent`, `corpus`, `deterministic`, `prompt`, `replies`, and `tools`.
- `calendars.py`: the court holiday calendars, loaded once at import from `calendars/*.json` into
  `court_calendars`. `load_calendar` (raises if a holiday is filed under the wrong year or its printed
  weekday is not the date's weekday), `court_calendar(county)` (the calendar of the circuit that includes
  the county, "Alachua" or "Alachua County", or None), `holidays_in(cal)`. Imports `config`. Imported by
  `deterministic`, `smoke`.
- `corpus.py`: the stored corpus, loaded once at import. `statute` (dict, section number to text, from
  `statutes/83.*.txt`), the playbook shapes (`Element`, `Clock`, `Spec`, `Playbook`), `load_playbook`,
  `Way` and `Gate` (an option's condition and the ways it can be met; TODO item 81), `way_problem` (what is wrong with a
  way's shape, or None; `answers_problem`: a way or an `applies_if` naming an answer its choice fact does not list),
  `option_ways` (every way of an option, its gates' and its steps'), `check_playbook` (one playbook: every spec quote verbatim in its cited section, every
  quotation of 20 or more characters in the guidance and open questions verbatim in a stored section, a
  question for every element and an element for every question, `applies_if` naming a yes/no fact, clock
  cites among `sections`, each open question's shape, no id from `playbook_ids` (every fact, clock, and open
  question id of the playbooks) in the guidance's prose or the open questions' text and readings, the guidance
  parts the tool reads; prints a line per check via `report`, returns the failures), `check_all_playbooks`
  (all of them, checking ids against every playbook's, plus a fact id shared by playbooks having the same type
  and question; returns the failures), and `playbooks` (dict, issue to `Playbook`, from
  `playbooks/*.yaml`). Since TODO item 112 only the options layer reads the playbooks' elements, ways, and questions
  (and `draft_letter` its note to the tenant): the facts, the deadlines, and the timeline read the skills, and
  `fact_lease`, which the sheet used to show a lease clause beside a question, is gone. No model
  calls. Imports `config`, `lease` (for `LeaseProfile`, to check `compare_to` and a way's `lease`). Imported by `record`, `tools`, `smoke`.
- `citations.py`: checks the ch. 83 cites and the quotes in a reply the model wrote. `SUBSECTION_START` (a marker such as
  `(3)` or `(b)` starts a subsection when a space and a capital letter or an opening quote follow it, or a
  lettered marker first, as in `(5)(a) If`; not after "subsection", "paragraph", "subparagraph"),
  `subsections(section)` (every `"(3)"` and `"(3)(a)"` of a stored section with its start and end in the
  text), `cites_in(text)` (every `83.x` cite with its parenthesized parts, spaces removed, a no-break space too, each once),
  `check_cites(text, shown)` (returns `(cite, problem)` for a section not in `statutes/`, a section not in
  `shown`, or a subsection the section does not have; cites inside a quoted passage are skipped, since they
  belong to the quoted text and `check_quoted` checks those words). Quotes: `quote_spans(text)` (quote marks paired in order, as a reader pairs
  them, so a short quote keeps its two marks and a quote may run over lines; the passages of `MIN_QUOTE`, 20,
  characters or more), `unquoted(text)` (the text with those passages blanked, for `check_cites` and
  `check_case_cites`), `quoted_passages(text)` (every passage of 20
  or more characters in straight or curly quote marks, with its cite: the first cite after the closing mark
  on the same line, or else the last cite in the 80 characters before the opening mark with no quote mark
  in between, never one already used by the previous quote; "" when none; an id alone in quote marks,
  `FIELD_ID`, and an example right after "e.g.", `EXAMPLE`, are not quotes and are left out), `compact` (lowercase, quote
  marks and apostrophes left out, dash variants made plain, all whitespace removed; looser than `squash` because
  the model writes "tenant's" for "tenant’s", changes a quote's inner marks (‘Reasonable notice’ for the
  statute's “Reasonable notice”; TODO item 58), and the lease PDF text has broken words like "confir mation"), `is_in`
  (a quote in a text by `compact`, split at an ellipsis into pieces that must each appear, punctuation at
  the ends ignored), `where_in(quote, section)` (the narrowest subsection holding it), and
  `check_quoted(text, given)` (returns `(quote, cite, problem)`: a quote with a cite must be in that
  section and that subsection, and the problem names where it really is, unless its words are in no stored section
  and are word for word in `given`: then it is someone else's quote, the tenant's, the lease's, a case's, or the
  tool's own, next to a cite that is not its source, and passes (TODO item 64, 2026-10-08); a quote with no cite must
  be in `given` or any stored section; first, a bracketed alteration, "[t]he", "specif[y]", is set aside as an
  ellipsis is, `unbracketed` with `BRACKET`, so the words around it must still be word for word, 2026-10-08). `caution(what, problem)` is the line printed to the tenant and
  `quote_label` names a quote in it by its first six words. These check that a cite exists and was
  available, and that quoted words are real and sit where they are cited. They cannot tell whether a cite
  fits a claim made in the reply's own words, and a paraphrase outside quote marks is not checked.
  `cites_without_quote(text)` (each cite outside quote marks whose words no quoted passage in the same text
  holds: a section or subsection retold instead of quoted; a quote in a narrower subsection counts for the
  wider cite; measured by `dev/eval.py` since TODO item 54; shown to the tenant by `replies.check_reply` from item
  66 until item 73, when a rule in plain words with its cite became the wanted form). `REPORTER` (a reporter cite such as `448 So. 2d 1208` or `103 Fla. 892`) and `check_case_cites(text,
  given)` (each reporter cite in a reply, outside quote marks, must appear in what the model was given, i.e.
  a `get_cases` receipt; returns `(cite, problem)`). Imports `corpus`. Imported by `agent`, `smoke`, `wiki`, `dev/eval.py`.
- `skills.py`: the skill format and its checks (TODO item 109, 2026-10-12; the design is in
  `docs/structure/2026-10-12-skills.md`, a dated note). A skill is one markdown file in `skills/`: a YAML header between
  two lines of three dashes, then the instructions. Since TODO item 111 the chat reads them: the `load_skill` tool, `record.active_skills`,
  and the system prompt (`prompt.system_prompt`) use `skills`; since item 112 so do the facts (`clock_facts`), the
  deadlines (`deterministic.compute_deadlines`), and the timeline. The options layer and `draft_letter`'s note to the
  tenant still run on the playbooks of the loaded skills until item 113. `Skill` (`name`, `description`, `sections`, `clocks` as `corpus.Clock`, `counting`, `provenance`,
  `body`: the markdown after the header; a key the shape does not define is refused, so a misspelled `clocks` cannot drop a
  deadline). `load_skill_file(path)` (raises `ValueError` naming the file when: there is no header or it is not closed or
  is not a mapping; a header key is missing or not defined, also inside a clock, or a clock is not a `Clock`; the name is
  not the file's name without `.md`; the description is empty, over 200 characters (`MAX_DESCRIPTION`), or has a line break;
  a section is not in `statutes/`; a clock's cite names a section not among the skill's `sections`; there are clocks and
  no `counting.convention`), `cite_parts(cite)` ("83.60(1)(b)" to the section and the subsection), `clock_roles(skill)`
  (what the clocks count from, as `(fact id, type, clock, role)` in the clocks' order: the role is `trigger` or
  `shown_with`, "date", `applies_if`, "bool", or, for a clock counted in `court_business_days`, "county" for
  `premises_county`; there is no separate list of facts), `clock_facts(skill)` (the same as `{fact id: type}`),
  `unconfirmed_clock_facts(skill, facts)` (the clock facts not in the confirmed `facts` yet, as `{id: type}`, leaving out the facts
  only a `ruled_out` clock needs, one whose `applies_if` is confirmed no), and `type_conflicts(all_skills)` (the fact ids two clocks type
  differently, one sentence each, in one skill or in two).
  `REQUIRED` (the body's "## " headings, in order: When to load this skill, What to find out, What the tenant can do,
  Deadlines, What the statute does not settle, Letters, Mistakes to avoid; "## Deadlines" only in a skill that has clocks;
  no other "## " heading; "### " subheadings are free). `check_skill(skill)` (prints one line per check through
  `corpus.report`, each naming the skill, and returns the failures: the headings (`heading_problem`: missing, not allowed,
  repeated, or out of order); each clock's quote and consequence word for word in the section its cite names and in the
  subsection the cite names (`cite_problem`, by `citations.is_in`, `subsections`, and `where_in`); every quotation of 20
  characters or more in the body word for word in a stored section, and in the cited section and subsection when a cite is
  next to it (`citations.check_quoted` on the body with nothing given, so only the statute counts; `check_quoted` skips a
  cite to a section or subsection that is not stored, so the skill check fails that one itself); and no clock id or
  clock fact id in the body as a whole word (`ids_in_prose`)). `check_all_skills()` (all of them, then one check that no fact
  id is typed two ways across them (`type_conflicts`), then a last line with the number of failures; returns it; called by
  `smoke.py`, not at import) and `skills` (dict, name to `Skill`, from
  `skills/*.md` in name order; the ten skills since TODO item 110, empty when the folder is absent). No model
  calls. Imports `config`, `corpus`, `citations`. Imported by `record`, `deterministic`, `timeline`, `tools`, `prompt`, `app`, `smoke_parts`.
- `wiki.py`: the case wiki's code (see Files on disk, `wiki/`). `read_pages(root)` (every page in
  `cases/` and `topics/` under the wiki folder, by name: `name`, `path`, `meta` from the YAML front matter,
  `body`; parsed once and reused, in `_read`, while no file there changes its time or size or is added or removed,
  since the chat builds its prompt on every model call; callers never change the pages), `linked` (page names in a front matter field), `opinion(page)` (a case page's opinion from
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
  with one of the sections names on an issue), `citation(meta)`, `plain_links`, `page_section(page, title)`
  (the lines of one "## " section, such as Facts or Related), and `render_cases(topic)` (every eligible case
  on the topic, oldest first: name and cite, the statute version read, the page's Facts quotes, then for each
  of its issues on the topic the question, the rule, the reasoning, and any dissent as quoted on the page,
  then "Other cases on it:", the page's Related lines (followed, distinguished, disagreed with), with "[not
  verified]" on unverified pages in a development run, ending with "These are courts' words in other people's
  cases, each with the statute version it read. How far one reaches your situation turns on how alike its
  facts are to yours."; the tenant and the model get this same text), and `cases_printed(text)` (the cases a
  `render_cases` text prints, in order, each with where its own part starts, found by its heading line, name
  then citation; a case named only under another's "Other cases on it" is not one; TODO item 57). Imports
  `citations`, `config`, `corpus`. Imported by `tools`, `agent`, `smoke`.
- `deterministic.py`: `court_days` (court business days from a
  county's court holiday calendar), `compute_deadlines(skill, facts, today)` (the only date arithmetic; reads `skill.clocks` and
  `skill.counting["convention"]`), `matter_deadlines(loaded, facts, today)` (every loaded skill's
  deadlines, with one that two skills share listed once, tagged with both skills' names in `skills`), `check_options(playbook,
  facts, today, profile=None)` (TODO items 72 and 81; its clocks are its skill's, `skills[playbook.issue]`, since the playbook and
  the skill have the same name and the same clocks; facts through `listed`, which leaves out an answer a choice fact
  does not list, kept from before its question was a choice: each option of the playbook with its status from the
  confirmed facts, the clocks, and the lease profile). Each way of a gate gets a state from `way_state`: a fact
  confirmed with the way's value (`matches`: one of them, for a choice fact's list of answers) is "met", with another
  value its `otherwise` ("not met", or "not settled" through an open question, or "not met yet"); a fact not confirmed
  is "tell" (the model asks the tenant in the chat: "ask the tenant: ..."), or "check" when the way names a lease clause the profile did not read; a way whose
  `applies_if` does not hold (`holds`: a yes/no fact true, or a choice fact with one of the answers listed), or whose
  fact's own question is never asked (`asked_never`), is "not met", why `NOT_APPLY`; a clock is met when its status is
  the way's `equals`, "tell" while its start date is not confirmed, "outside" when it cannot be counted (no court
  calendar); a `check` way is "check", with the tenant's words from the record when it names a text fact in `beside`
  ("your words, as you gave them: ..."), an `outside` way "outside"; a way naming a lease clause says whether the tool
  read it, found none, or did not read it (`lease_note`). A gate takes the best state among its ways (`STATES`: met, tell, check, not settled,
  outside, not met yet, not met), with its status and what the tool knows of it in words (`STATUS`, `KNOWLEDGE`: known,
  the tenant can tell the tool, the tenant can check, not settled, outside the tool), why, its ways, and, while
  not met, `if_met`: the option's status were it met (were it not, the option is closed). `option_status`: closed
  when a gate is not met, else not known yet (a gate to tell or check), not settled, outside the tool, not open yet
  (a gate not met yet), or open. Each step (`step_status`) "done" (its fact confirmed with its value, its clock's date
  passed, through `compute_deadlines`, or a way of its met), "waiting" (the date upcoming), "the tenant can check" or
  "not settled" (through its ways, `STEP_STATUS`, with why), or "to do"; a clock's step whose date has passed while a
  step above it is not done is "passed", with "counts only if the steps above are done" (TODO items 86 and 90 to 92)).
  The options layer goes with the playbooks (TODO item 113). `check_elements` (element status), `lease_value` and `lease_differs`
  (a lease quote read as a date or an amount and compared with the tenant's value), `ask_json`, and `fill_facts` (the
  model's reading of a description into facts) went with TODO item 112: the facts are proposed in the chat and no list of
  them is checked. Imports `calendars`, `lease` (for `LABELS` and `lease_cite`), `skills`. Imported by `timeline`, `tools`,
  `prompt`, `smoke`.
- `record.py`: the shared state. `matter` and `profile` live here and every other module reaches them as
  `record.matter` and `record.profile`. `confirm_fact` (the only code that writes a confirmed fact; a proposal stays in
  `matter["proposed"]` until it runs for its id), `add_skill(name)` (the only code
  that writes `matter["skills"]`, the names of the loaded skills; called only by the `load_skill` tool, which has
  checked that the name is a skill and not loaded yet: appends the name, saves `matter.json`, and logs a
  `skill_loaded` event with `skill`), `active_skills()` (the `skills.Skill` objects for `matter["skills"]`, in the order
  loaded), `clock_facts()` (TODO item 112: the facts the loaded skills' clocks count from, as `{fact id: type}`, merged
  across the skills from `skills.clock_facts`; `propose_facts` and the confirmation read it), `active_playbooks()`
  (TRANSITION, until TODO item 113 removes the playbooks: the playbook of each loaded skill, for the names that have one;
  only `prompt.options_status` and `unknowns_status` call it), `matter_dir` (the only function that knows the
  folder layout), `lease_pages()` (the matter's `pages.json`, or [] with none; read by `search_lease` and
  `replies.cited_words`), `new_tenant_id` (random `t-` plus six hex characters), `new_matter_id(tenant_id)` (`m-001`,
  `m-002`, ... counting the tenant's `m-*` folders), `list_matters` (every saved matter as `{"tenant", "id", "skills"}`,
  nothing else read out), `with_skills(saved)` (a `matter.json` as the code reads it: one saved before skills, with
  `issues`, `proposed_issues`, and `rejected_issues`, gets `skills` = each issue that is the name of a skill, in order,
  and loses the three keys; the file itself is rewritten at the next `save`), `load_matter(tenant_id, matter_id)`
  (replaces `matter` from `matter.json`, through `with_skills`, and `profile` from `lease_profile.json`, or `None` if
  there is none; raises `FileNotFoundError` for a matter that does not exist), `save` (writes `matter.json`),
  `append_event` and `read_events` (`events.jsonl`). The starting `matter` is the test matter,
  tenant `"t-test"`, id `"test-001"`, used by the smoke scripts through `load_matter`. `new_matter(tenant_id)`
  replaces `matter` with an empty one (`skills: []`) under the next matter id and clears `profile`; `run.py` and
  `app.py` call it.
  `session` holds the open session's id or `None`; `start_session(how)` opens one (a new time-ordered
  uuid7) and logs `session_started`, `end_session()` logs `session_ended` and clears it. While a session is
  open, `append_event` adds its id to every event. `append_transcript(entry)` writes one line to the open
  session's transcript (does nothing with no session open). `tenant_words()` returns the tenant's lines from the open session's
  transcript.
  Imports `config`, `corpus`, `lease`, `skills`. Imported by `sheet`, `timeline`, `tools`, `agent`, `run`,
  `smoke`, `smoke_online`.
- `timeline.py`: `render_deadlines(result)` (a `get_deadlines` result as the tenant reads it: per deadline
  its date, actor, clock, skills, status, rule and start, cite, and counting line; a clock with no date
  shows why; a clock's `shown_with` fact, when confirmed, on a line "beside it, from your record: ..."; a clock's
  `condition` on a line "counts only if ..." (TODO items 90 to 92); with no deadline at all, one line saying so, "No
  deadlines yet" while a skill waits for facts; then each waiting skill with its facts), and
  `render_timeline(skill, full)`, the DATE / EVENT / SOURCE / FILE table (`skill` keeps one loaded skill's deadlines and tagged events), whose confirmed-date rows are every
  confirmed fact whose value is a date written YYYY-MM-DD (`is_iso_date`), a plain-text fact among them, each by its id in words (TODO item 112; with a
  skill filter, a date only another loaded skill's clocks count from is left out), plus helpers
  `label`, `corrected` (the tenant confirmed a different value from the suggestion, compared as shown),
  and `confirmation_of`. A confirmed date's SOURCE reads "tenant (corrected, ...)" when corrected, and in
  `timeline full` a corrected fact reads "corrected from <how> <suggested value>". Not a tool; only the web page and `smoke.py` call it. Imports `record`,
  `deterministic`, `sheet` (for `shown`), `skills`. Imported by `agent`, `smoke`.
- `tools.py`: the ten `@tool` functions and the `tools` list (see Tools the model can call), plus the
  plain helpers `pretty`, `quote_is_real`, `sentence`, `build_letter`, `dates_written`, `same_day`, `amount`,
  `not_in_record`, `check_line` (the letter, Data flow, step 7), `computed_deadlines` and `deadlines_waiting` (the
  deadlines the confirmed facts give, and the clock facts each loaded skill still needs; the listing and the prompt both
  read them), `deadline_listing`, and `deadline_receipt`; and, for `propose_facts`, `FACT_ID` (the shape of a fact name),
  `MAX_TEXT`, and `CLOCK_FACT_IDS` (the clock fact ids of every skill, loaded or not). Imports `record`, `citations`, `config`, `corpus`, `deterministic`, `lease`, `sheet`, `skills`, `wiki`.
  Imported by `prompt`, `agent`, `schemas`, `smoke` (for `build_letter`, `get_deadlines`).
- `prompt.py`: what the model reads (split out of `agent.py` and `tools.py` on 2026-10-06, unchanged). `RULES` (the fixed part of the system prompt; if the environment sets `RULES_FILE`, that
  file's text replaces it for the run, for trying versions of the rules), `rules_for(messages)` (`RULES`
  with its two markers filled: `[RULE 6]` with `LETTER_RULE` once a letter is in play, i.e. a tenant
  message in the chat matches `LETTER_WORDS` (letter, draft, write, writing) or the matter has a `draft`
  event, else nothing; `[RULE 8]` with `CASE_RULE` when there is a case topic (`tools.offered_topics`), else `NO_CASES_RULE`, one
  line saying there are none; a `RULES_FILE` without the markers is used as is);
  `PARTS` (each part's name, as the model names it to the tenant), `system_prompt(messages=())` (the whole system prompt, built from the record as it stands and, for the
  rules, the chat's messages so far; the menu of skills, every skill's name and description with `(loaded)` on a loaded
  one, and the loaded skills' instructions, each under `# <name>`, come from `skills.skills` and
  `record.active_skills()`), `case_topics_text`
  (one line per case topic, or none), and four parts the program works out: `facts_status` with `role_words` (YOUR
  FACTS: the confirmed facts, the proposals waiting, and what the deadlines still need), `deadline_status` (WHICH DEADLINES
  HAVE PASSED), `options_status` with `state_words` (YOUR OPTIONS), and `unknowns_status` with `UNDECIDED` and
  `KNOWN_AS` (WHAT THE TOOL DOES NOT KNOW); see The system prompt. Imports `record`, `corpus`, `deterministic`,
  `lease`, `sheet` (for `shown`), `skills`, `tools`. Imported by `replies`, `agent`, `smoke`.
- `replies.py`: what the program checks and prints under each reply (split out of `agent.py` on 2026-10-06,
  unchanged). `check_reply(text, messages)` (which builds `given_text` once for its checks) runs
  `citations.check_cites` against `sections_shown(messages)` (the loaded skills' `sections` plus every
  section fetched with `get_statute_section` in the thread) and `citations.check_quoted` against
  `given_text(messages)` (the system prompt, the lease quotes as plain text, the tenant's description and
  updates, and every thread message the model did not write). Each failure gets a "[Check: ...]" line, a
  `check` transcript line, and a `cite_flagged` or `quote_flagged` event; it returns the lines. The
  reply is not held back or changed, and the model is not told. (From TODO item 66 to 73 it also cautioned a
  section cited with none of its words quoted, `RETOLD`; since item 73 that is the wanted form.) The words a
  reply cites come from `cited_words(text)` (TODO item 73, the author's decision of 2026-10-04): for each ch. 83
  cite outside quote marks that the stored statutes hold, the subsection's words (or the section's), the
  narrowest once (83.56(1) cited, 83.56 alone adds nothing), cut at `CITED_MAX` (1,500) characters with the cite
  for the rest; then each lease clause the profile holds under a lease cite (`LEASE_CITE`: "Lease Section 4.3",
  "Lease Article 7", "Lease, page 1", with any space between the words, since the model wrote "Lease Section\u202f7.2"
  with a narrow no-break space and nothing was printed, TODO item 85; `cited_clause` matches a numbered clause, one holding the cited number,
  such as Article 7 for "Lease Section 7.2", or for a page cite the clauses with no number on that page), each
  with its cite, page, and `lease.LABELS` label; and for a numbered cite no profile clause holds, the clause of that
  number in the lease's own text (`lease.lease_clauses`), or every clause of a cited article, each with its page and
  title, cut at `CITED_MAX` (TODO item 82: a clause `search_lease` found is printed as a profile clause is); under
  `CITED_HEAD`, "The words the reply above cites, printed by the program from the stored statute and your
  lease:". `agent.turn_blocks` shows them as a `sources` block right under the reply and writes them to the transcript
  as a `printed` line marked `"what": "sources"`. It also runs `check_case_quotes(text,
  messages)`: a quote credited to a printed case whose part of the printed text (`printed_cases(messages)`,
  `[(name, part)]` from each `get_cases` artifact through `wiki.cases_printed`; its brackets set aside, `unbracketed`) does not hold it while another
  case's part does is flagged "is in X's text, not Y's" as a `quote_flagged` event with the case as `cite`; the
  credit goes to the printed case the reply names last before the quote in the same paragraph, none when two
  are named at that same place, and words a statute section also holds are left to `check_quoted`.
  `named_cases(text, names)` finds where a text names each case, by its short name or its first party's name
  alone, a name inside a longer one being the longer one's ("Bennett" in "Bennett M. Lifter" names Bennett M.
  Lifter, Inc. v. Varnado). `cases_left_out(new)`: the printed cases no reply after them names,
  for `CASES_LEFT_OUT` (see `agent.turn_blocks`). Imports `record`, `wiki`, `citations`, `config`, `corpus`, `lease`,
  `prompt`. Imported by `agent`, `smoke`.
- `agent.py`: reading the lease, intake and resume, the agent, and the chat. `read_lease(pdf_path)` (store
  the PDF, read it into the lease profile with the extraction model, check every quote, save the profile; for a
  new matter), `intake(description)` (a new matter only: saves the description in `matter.json`, nothing else; no model
  call), `resume(update_text)` (an existing matter: logs the update verbatim as a `tenant_update` event; no model call).
  Neither builds the agent nor reads the text: the front end builds the agent (`build_agent`) right after and sends the
  description, or the update when it is not empty, to the model as the tenant's first chat message through `turn`, so
  the model answers it first: it loads the skills that fit, proposes facts, and replies. If that turn proposed
  facts, the sheet follows, as after any turn.
  `prompt_from_record` (LangChain `dynamic_prompt` middleware that
  calls `system_prompt(request.messages)` before every model call), `build_agent` (a LangChain agent with that middleware and an in-memory checkpointer; no
  model call), `transcript_entry` (one thread message as a transcript line).
  The chat is in pieces both front ends call (the terminal's `chat`, the web page `app.py`). Each returns
  blocks, the parts the tenant sees in order, each `{"kind", "text"}` made by `block`: `reply` is the model's
  words; every other kind is the program's: `letter` (a `draft_letter` result as is), `cases` (a `get_cases`
  listing), `deadlines` (the turn's last `get_deadlines` listing through `render_deadlines`), `caution` (failed
  cite or quote checks, or `NO_REPLY`), `footer` (`READING_LINE`), and `notice` (a message from the web page itself, such as what was
  skipped on the sheet). `turn(agent, config, text, note="")` is one turn of the model: the tenant's message goes to the
  transcript before the model runs (so `propose_facts` can check the tenant's words), then the note, if any; the
  turn's new messages are the thread after what the checkpointer held before it; it returns the blocks and
  whether the model called `propose_facts`, so the sheet comes next. When the tenant's message asks about when
  (`WHEN_QUESTION`: "when do", "when is", and the like, "how long", "how many days", "last day", "deadline", "by
  when"; not "when I moved out") and the turn holds no `get_deadlines` call, `deadlines_unasked` puts the
  deadlines first, as a `deadlines` block printed by the program (`render_deadlines(deadline_listing())`, which
  logs `deadlines_computed` as the tool does), written to the transcript as a `printed` line marked `"what":
  "deadlines"` (TODO item 65: the model answered 1, then 4 of 39 such questions without the tool). The model is
  not told. `turn_blocks(new, messages)` transcribes a
  turn's new messages and builds its blocks; other tool results are not shown. Under each reply come the words
  it cites (`replies.cited_words`), then its cautions (`replies.check_reply`), then, if the reply cites or quotes the statute (a quoted passage with a ch. 83 cite,
  `citations.quoted_passages`, or a ch. 83 cite outside quote marks) or the lease (a quoted passage found in a
  lease profile quote, or a `LEASE_CITE`, "Lease Section 4.3") and does not
  already carry it (after `CUT_OFF`, "[Check: this reply was cut off at the model's length limit. Ask again for
  the rest.]", when the gateway's `finish_reason` was "length"), `READING_LINE` ("This is the tool's reading of the stored law and your confirmed
  facts, not a lawyer's advice.", from `replies.reading_line`), also written to the transcript as a `footer` line
  (TODO item 46; was `NOT_DECIDED`, "This tool does not decide whether any of this applies to you."). When a turn has no blocks (the reply was empty
  or blank), `retry_empty` sends the model `EMPTY_REPLY`, a program note asking it to reply, and returns that
  second turn's blocks; if it is empty too, a `NO_REPLY` caution ("[Check: no reply came back from the model. Please
  ask again.]"). Either way it logs `reply_empty`, with `finish`: the `finish_reason` the gateway gave for each
  empty answer ("stop", "length", or none). The model's `reasoning_content` is never shown in its
  place: LangChain drops it, and it is the model's unchecked working, not a reply.
  After a turn's replies, `turn_blocks` adds one more caution when a case `get_cases`
  printed in the turn is named by no reply after it (`cases_left_out(new)`): `CASES_LEFT_OUT`, "[Check: the
  program printed cases above that this reply does not discuss: <names>. Read them too before relying on the
  reply.]", a `check` transcript line, and a `cases_left_out` event (TODO item 57: every mold-story answer of
  2026-10-02 left out the printed cases that went for the landlord).
  `sheet_note(confirmed)` is the "[Program note:
  the tenant confirmed on the sheet: ...]" line sent to the model at the front of the tenant's next message
  after a sheet ("" when nothing was confirmed). `thread_config()` is the chat thread's config; the thread id
  is the session id when one is open. `print_blocks(blocks)` is the terminal's way of showing blocks: each text,
  then an empty line. `chat(agent, first="")` is the terminal loop: runs a turn on `first` (the description of a new matter, or
  the update; nothing when it is empty) and then on each line it reads (an empty line or `bye` ends it), prints the
  blocks, and after a turn that proposed facts runs `sheet.run_sheet` if `pending_rows()` has anything, keeping its
  `sheet_note` for the next message.
  Imports `record`, `config`, `lease`, `prompt`, `replies`, `sheet`, `timeline`, `tools`.
  Imported by `run`, `app`, `smoke`, `smoke_online`.
- `run.py`: entry point. `start()` asks new or existing and returns the tenant's first message (`""` if there is none),
  or `None` when no matter is open. `start_new` picks an existing tenant id or makes one
  (`new_tenant_id`), calls `new_matter` and `start_session("new")`, asks for the lease path (`ask_path`, which accepts a path dragged
  into the terminal), reads the lease (`agent.read_lease`), asks for the description (`ask_text`, several lines
  ended by an empty line), then `intake` (which saves it), and returns the description. `start_existing` lists matters
  (with their skills), `load_matter` on the one picked (it stops if the matter has no lease profile),
  `start_session("existing")`, then asks "Anything new since last time?" with `ask_text`: text goes to `resume`
  (which logs it) and is returned, an empty answer returns `""`. Then `chat(build_agent(), first)`: the agent is built
  right after, and the description or the update is the tenant's first message, so the model answers it first (loads
  skills, proposes facts); if it proposed facts, the sheet (`run_sheet`) follows, as after any turn. Then
  `end_session()` on a normal exit. A session opens before intake or resume, so everything done in the visit carries
  its id. (TODO item 115 removes this terminal front end.)
- `app.py`: entry point, the same steps as `run.py` as a web page (`streamlit run app.py`, on
  http://localhost:8501; `.streamlit/config.toml` keeps it on this computer, `address = "localhost"`, turns
  off Streamlit's usage statistics and its first-run prompt, and hides the Deploy button). Streamlit runs the
  whole file again on every click, so what must last is in `st.session_state`, one browser tab's memory:
  `stage` (door, new, update, sheet, chat), `ids` (the open matter's tenant and matter id), `session`,
  `agent` and `config` (built when the chat opens, by `open_chat`), `history` (everything shown in
  the middle column, as blocks, plus the page's own `tenant` and `sheet` entries), `pending` (a message
  waiting for the model's turn), `note` (`agent.sheet_note` of the last sheet), `skipped` and `saved` (this
  sheet's). `open_record()` loads the tab's matter into `record` at the top of every run, since every tab
  shares the record module, and sets `record.session`. Sidebar: New matter, the saved matters
  (`list_matters`) with Open, and for the open matter "What this matter is about": each loaded skill's description
  (`record.active_skills`, with no id shown; nothing while no skill is loaded), and End session (`end_session`).
  Middle: `new_matter_form` (tenant, an
  existing one or a new id; the lease PDF, written to a temporary folder for `agent.read_lease`, which keeps
  its own copy under its hash; the description; then `intake` and `open_chat`),
  `update_form` (what is new, through `resume`, which logs it, and `open_chat`), `open_chat(first)` (builds the agent
  once, which makes no model call, shows `first` as the tenant's message, and leaves it as `pending`, so the model's
  first turn answers it), `sheet_form` (the confirmation, one row at a time from `pending_rows`: the
  label, `row_notes`, an input by the row's type (`answer_widget`): a date picker, yes/no, a county in a line, words in a
  text area, filled in with the suggestion; Save goes through `value_of` and `save_answer`, an accepted suggestion logged
  as typed ""; Skip for now leaves the proposal pending), `finish_sheet` (back to the chat with the note, and
  `sheet.skipped_note` when something was skipped), then the chat:
  `take_message` (`bye` ends the session; anything else waits as
  `pending`, so the message shows before the model starts) and `run_pending_turn` (`agent.turn`; the confirmation
  follows when the model proposed facts and rows are pending; an error from the gateway becomes a caution and
  the page goes on, with the traceback printed in the terminal running Streamlit). The terminal's chat commands
  (`issues`, `drop`, `timeline`) are gone since TODO item 111. `show(b)` draws a block:
  the tenant's words and the model's `reply` in speech bubbles; `caution` as a warning; `footer` and
  `notice` as notes; `sources`, the words a reply cites, folded in an expander ("The statute and lease words cited
  above", TODO item 73); `deadlines`, `letter`, `cases` in a box labeled by `PRINTED_BY` as
  printed by the program (listings in fixed-width text, only a letter wrapped). `plain(text)` shows text as
  written: markdown signs escaped (a `$` would start math) and line breaks kept. Right: `record_panel`, the
  timeline (`render_timeline` for all of the matter or one loaded skill, picked by its description, full or not,
  redrawn from the record on every run; Show wide opens it in a wide window, `wide_timeline`) and the
  last letter drafted (from the last `draft` event's file, with a download button). `need_key()` stops a run
  that would call a model without the key. Imports `record`, `agent`, `config`, `sheet`, `skills`,
  `timeline`.
- `sheet.py`: the confirmation, asked and saved by code with no model (TODO item 112; it was the intake sheet, which asked every
  fact the loaded playbooks lacked). It follows a turn in which the model proposed facts and asks only to confirm what the
  tenant said, never for a fact the record lacks. `pending_rows()` (every fact in `matter["proposed"]`, in the order proposed;
  each row: `id`, `label` (the id with spaces), `type` (the type of a clock fact of a loaded skill, from `record.clock_facts`,
  "date", "bool", or "county", else "text"), `status` ("proposed", or "changed" when the id is already confirmed with a value
  that reads differently), `suggested`, `basis` (the tenant's words), and `confirmed` (the confirmed value of a changed row)),
  `parse_answer(kind, text)` (checks an answer against the row's type: dates as `2026-07-31` or `7/31/2026`, yes/no, and for
  any other type, "text" or "county", non-empty words), `shown` (yes/no for a boolean, else as is).
  The pieces, so the terminal and the web page ask a row the same way: `suggestion(r)` (a row's suggested value if it fits the
  type, else `None`), `row_notes(r)` (the lines under a row's label: "was X, now Y?" for a changed row, then the suggestion
  with the tenant's words it came from, or just the words when the suggestion does not fit the type), `value_of(r, answer)`
  (an empty answer takes the suggestion, otherwise `parse_answer`; returns `(value, None)` or `(None, what is expected)`),
  `save_answer(r, answer, value)` (`record.confirm_fact`; saves `matter.json`, writes a `sheet` transcript line with the
  row's `label`; returns the pair `(fact id, value)` for the model's note), and `skipped_note(fact_ids)` (what the tenant is told
  after skipping: the facts stay unconfirmed, nothing is counted from one, and they are asked again at the next confirmation).
  `run_sheet(ask=input)` is the terminal's confirmation: asks one row at a time with those pieces (the label and a hint by
  type), rebuilding the list after each answer; Enter accepts a suggestion, a typed value corrects it, `?` skips (the proposal
  stays pending); returns the saved pairs. Imports `record`. Imported by `app`, `agent`, `prompt`, `timeline`, `tools` (for
  `parse_answer` and `shown`).
- `checks.py`: helpers for the smoke scripts. `check(name, condition)` prints `OK` or `FAIL` and keeps the
  failures, `summary()` prints the last line, `make_scratch(tenant_id, **changes)` copies the test matter
  (without its transcripts) to `matters/<tenant_id>/m-001` and changes `matter.json` keys, and
  `remove_scratch(tenant_id)` removes it; it refuses any tenant id not starting with `t-smoke`.
- `smoke.py`: entry point. Runs the offline checks, which are in `smoke_parts/` (split out of smoke.py on 2026-10-06),
  by importing each part in order, then prints `summary()` (see Running and testing).
- `smoke_parts/`: the smoke checks in six parts, each run when imported: `pieces` (each piece on its own, on the
  test matter in memory), `writing_to_a_matter` (on `matters/t-smoke/m-001` and `matters/t-smoke-county/m-001`), `skills_and_turns` (TODO item 111; named
  `issues_and_turns` until then: the model loading skills on `matters/t-smoke-skills/m-001`, an old matter's issues
  coming out as skills on `matters/t-smoke-old/m-001`, intake and resume making no model call and the description being
  the first turn on `matters/t-smoke-intake/m-001`, and turns with a stand-in model on `matters/t-smoke-related/m-001`),
  `playbooks_options_lease` (every skill's clock facts through the real code path, and the checks of items 72 to 84 on
  their own scratch matters), and
  `web_page`, and `skill_files` (the skill format and the typing of clock facts, on fixture skills written to a temporary folder, never to `skills/`; TODO
  items 109 and 112); and `common.py`, what more than one part uses: `FORFEIT` (a phrase of 83.49(3)(a)), `scripted`,
  `stated`, `screen`, `prompt_part`, and `StandIn` (a stand-in model that takes any tools). Each part imports what it
  uses; named checks and scratch matters come from `checks.py`.
- `smoke_online.py`: entry point. The model's first turn on throwaway copies of the test matter (intake and resume call
  no model, so the model's work is the turn on the description or the update): a new matter's description, a situation no
  skill covers, and `resume` with an update, each with named checks (the ones marked "(model)" depend on the answer).
- `dev/live_run.py`: entry point for live tests. Starts `run.py` itself and drives a whole session from a
  scenario file in `dev/scenarios/` (see Running and testing). Imports nothing from the project.
- `dev/eval.py`: entry point for measuring. Runs `dev/live_run.py` on scenarios several times each and
  scores the runs from their matters by code (see Running and testing). Imports `corpus` only to score.
- `schemas.py`: entry point. Prints each tool's name, first docstring line, and argument schema.

## Data flow

1. Lease PDF to profile (`agent.read_lease`, new matters only; an existing matter's profile comes
   from `load_matter`). `ingest_pdf` stores the PDF and page text in `matter_dir()`, `extract_profile` asks the extraction model for a JSON `LeaseProfile`, `check_quotes` prints OK or FAIL
   for every clause, and the profile is saved. A FAIL is printed, not enforced: the profile is saved anyway.
2. Description to the first turn (`intake`, then `turn`). `intake` saves the description in `matter.json` and nothing
   else: no model call, no issue, no proposed fact. The front end then builds the agent (`build_agent`) and sends the
   description to the model as the tenant's first chat message (`agent.turn`). The model loads the skills that fit
   (`load_skill`; `record.add_skill` saves the name and logs `skill_loaded`), reads the lease and the statute, proposes
   facts from the tenant's own words (`propose_facts`; the description is in the transcript by then, so its `said` words
   can be checked), and answers; the loaded skills' instructions and sections are in its next prompt. If it proposed facts,
   the confirmation follows (step 3). Nothing is confirmed by code before the tenant answers it.
2b. An update to an existing matter (`resume`). The text is logged verbatim as a `tenant_update` event;
   `description` is not touched. The text is sent to the model as the visit's first chat message, as in step 2, with
   no model call before it. Nothing is removed: the skills loaded stay loaded. A proposal next to a confirmed fact with a
   different value shows as `changed` (step 4). Facts two skills share need nothing: there
   is one `facts` pool for the matter, so a new skill's clock facts that are already confirmed are known.
3. Proposed to confirmed (`record.confirm_fact`, the only code that writes `matter["facts"]`). It moves
   the value into `facts`, removes it from `proposed`, and appends a `fact_confirmed` event carrying the
   proposal's `how`, `basis`, and `proposed_value` (or `how: "asked"` when nothing was proposed) and
   `confirmed_in`. One caller: the confirmation (`sheet.save_answer` from `sheet.run_sheet` or the web page's form, the
   tenant answers code directly, `confirmed_in: "sheet"`). The model cannot confirm a fact; it can only add to `proposed`
   with `propose_facts` (TODO item 112), which parses a clock fact of a loaded skill by its type
   (`record.clock_facts`: "date", "bool", "county") and keeps any other fact, under a name of lowercase words joined by
   underscores, as plain text; a proposal stays in `proposed` until the tenant confirms or corrects it (nothing prunes
   it; before item 112 `prune_proposals` dropped a suggestion no playbook asked), and a skipped one is asked again at the
   next confirmation. Events from before 2026-09-27 may say `confirmed_in: "chat"` or have no `confirmed_in`: those
   were recorded by the old `record_facts` tool.
4. The confirmation's rows (`sheet.pending_rows`). One row for each fact in `proposed`, in the order proposed, with its
   label (the id with spaces), type (a clock fact's, else "text"), the suggested value, and the tenant's words it came from;
   a proposal for an id already confirmed with a value that reads differently is a `changed` row, shown "was X, now Y?"
   and resolved with either value. No row is made for a fact the record lacks, and no question comes from a skill or a
   playbook. Enter (or an empty answer on the page) accepts the suggestion, a typed value corrects it, parsed by the type;
   skipping leaves the proposal pending. Before item 112 the sheet asked, from the loaded playbooks' elements, every
   changed, proposed, or missing fact (`check_elements`), with the lease's words beside a value that differed.
5. Confirmed to deadlines (`get_deadlines`, then `tools.computed_deadlines`, `matter_deadlines`, and `compute_deadlines` per loaded
   skill; a "skill" in a deadline's tags is a skill's name; TODO item 112). Only confirmed facts count: a proposal
   is never read. Every clock of every loaded skill that can be computed is listed; there is no "ready" rule, so a skill
   missing one fact still gets its other deadlines. `waiting` (`tools.deadlines_waiting`) is `{skill name: [clock facts
   not confirmed yet]}` for the skills with some (`skills.unconfirmed_clock_facts`: the facts a clock needs, leaving out
   those only a clock needs whose `applies_if` is confirmed no). For each clock: skipped if `applies_if` is not a truthy confirmed fact; "need date for ..."
   if the trigger date is not confirmed (such a row is left out of the listing, since waiting says what it needs); otherwise trigger date plus or minus `days` calendar days, status
   `passed` if before today else `upcoming`, with the cite and the skill's `counting.convention`. A clock
   with `count: court_business_days` goes through `court_days` instead: one day at a time from the trigger
   date (not counted), skipping Saturdays, Sundays, and every holiday in the calendar of the circuit that
   includes the confirmed `premises_county`. Its row carries its own counting line naming the circuit and
   the memoranda used. With no calendar for the county, or a day in a year with no memorandum loaded, the
   row says "not computed: ..." and has no date; nothing is guessed.
   `matter_deadlines` then merges a row two skills share (same clock id, cite, date, and status) into
   one, and every row carries `skills`, the list of skill names it belongs to.
6. Record to timeline (`render_timeline`). Rows come from confirmed date facts (every fact whose value is a date
   written YYYY-MM-DD, a plain-text one too), freshly computed deadlines
   (from `matter_deadlines`, so a shared deadline is one row tagged `[skill, skill]`, kept under either
   skill by the web page's skill filter),
   and events (see Files on disk). Sorted by date only; rows on the same day keep the order they were
   added (confirmed dates and deadlines first, then events in log order). `skill` filters deadlines and
   events tagged with a skill (or, in older matters, an issue); untagged events always show. `full` adds `skill_loaded`, `fact_confirmed`, `fetch`, `cite_flagged`, `quote_flagged`, `cases_left_out`, `reply_empty`,
   `deadlines_computed`, the issue events of older matters, `session_started`, and `session_ended` events.
7. Letter assembly (`draft_letter`, then `build_letter`; TODO item 95, 2026-10-11). Checks that the issue is a loaded skill with a playbook, and the posture;
   refuses a ch. 83 cite (`citations.cites_in`, dollar amounts set aside) or a lease cite (`lease.LEASE_CITE`) in the
   tenant's part (the account, the request, the delivery method), and a `signed_by` with a label (parentheses or quote
   marks) or a signer whose words are not all among the lease's `tenant_names` quote (several signers split at commas
   and "and"; any signer when the lease names none); checks each quote with `quote_is_real` (substring of a present
   lease clause quote or any stored statute section). Then builds the letter: today's date, the landlord and premises
   quotes from the profile, the account and the request as the model wrote them (`sentence` adds a closing period
   if none), a reply-by date (today plus `respond_within_days`), the quotes, "Delivery: " and the delivery method,
   and the signer. The model's words are never put inside a sentence of the program's, and no confirmed fact is
   printed by id. Dates are written "October 6, 2026" (`pretty`). `not_in_record` finds each date (`dates_written`:
   "September 19", "Sept. 19, 2026", "Oct 2nd", "9/19", "9/19/2026", "2026-09-19") and dollar amount in the tenant's
   part that is not today, the reply-by date, in the tenant's own words (the description, updates, this session's
   messages from `record.tenant_words`, recorded messages, and the value of every confirmed fact, whatever its type: a
   plain-text fact's date or amount counts, TODO item 112) or in the lease's quotes, or, for an
   amount, a confirmed number or a number in the tenant's words (a plain-text fact's among them); a date given without a year matches any year
   (`same_day`). `check_line` names them in a "[CHECK BEFORE YOU SEND, not part of the letter: ...]" line under the
   letter, never in the draft file. Writes the draft file and a `draft` event.

## Files on disk

`matters/<tenant id>/<matter id>/`, built by `record.matter_dir` from `matter["tenant"]` and `matter["id"]`.
A tenant id is opaque, never a name or an email. Currently only `matters/t-test/test-001/`, set in
`record.matter`:

- `lease_<sha256[:12]>.pdf`: the lease as provided, named by its hash.
- `pages.json`: list of `{"page": n, "text": ...}` from PyPDF2.
- `lease_profile.json`: the `LeaseProfile`, one `Clause` per field: `present`, `quote`, `page`, `section`; a
  field the profile was read without (`maintenance_and_repairs` before 2026-10-04) is missing or `null`.
- `matter.json`: current state only, overwritten by `save`. Keys: `id`, `tenant`, `description` (the intake text),
  `skills` (the names of the loaded skills, in the order loaded; written only by `record.add_skill`),
  `facts` (confirmed, fact id to value; a clock fact of a skill holds a date string, a boolean, or a county, any other fact
  plain text, and a matter from before TODO item 112 may hold a number or a boolean under a playbook's element id), `proposed` (unconfirmed,
  fact id to `{"value", "how", "basis"}`; kept until the tenant confirms it). A `matter.json` saved before skills has `issues`, `proposed_issues`, and
  `rejected_issues` instead of `skills`; `load_matter` reads them as skills (`record.with_skills`) and the next save
  drops them.
- `events.jsonl`: the history, one JSON object per line, append-only. Every event has `when` (local time,
  ISO, to the second) and `kind`, then `session` (the session id) if a session was open when it was
  written. Events written before sessions existed, or outside `run.py`, have no `session`. Kinds and their
  other fields:
  - `fact_confirmed`: `id`, `value`, `how` (stated, inferred, or asked), `basis`, `proposed_value`,
    `confirmed_in` ("sheet" or "chat"; missing on events from before 2026-09-27). Written by
    `record.confirm_fact`.
  - `fetch`: `section` (from `get_statute_section`), `search` (from `search_statute`), or `lease_search` and `found`
    (from `search_lease`: the phrase, and the clause numbers and pages that hold it).
  - `cite_flagged`: `cite` (e.g. "83.64"), `problem` (not a stored section, not shown or fetched in this
    chat, or no such subsection). Written by `replies.check_reply` after a reply. `timeline full` only.
  - `reply_empty`: `recovered` (true if the model's second turn showed the tenant something), `finish`
    (the gateway's `finish_reason` for each empty answer). Written by
    `agent.retry_empty`. `timeline full` only.
  - `quote_flagged`: `quote` (the quoted words), `cite` (the cite next to it, or ""), `problem` (e.g. "is in
    83.49(3)(a), not 83.49(3)(b)"). Written by `replies.check_reply`. `timeline full` only.
  - `cases_left_out`: `cases` (the names of printed cases no reply after them named). Written by
    `agent.turn_blocks`. `timeline full` only.
  - `cases_shown`: `topic`, `cases` (the cites printed, oldest first), `unverified` (true, only in a
    development run with `WIKI_UNVERIFIED`). Written by `get_cases` when it prints; once per topic per
    session. `timeline full` only.
  - `deadlines_computed`: `skill` (`issue` in events before TODO item 112), `clocks` (ids of clocks that produced a date). One per
    loaded skill that has a dated clock, per `get_deadlines` call.
  - `draft`: `issue`, `posture`, `cites`, `file`. Written by `draft_letter`.
  - `artifact`: `file` (original name), `sha256`, `note`. Written by `add_artifact`.
  - `communication`: `sent_on` (YYYY-MM-DD), `sender`, `recipient`, `channel`, `text`. Written by
    `add_communication`. The timeline sorts it by `sent_on`, not `when`.
  - `skill_loaded`: `skill`. Written by `record.add_skill`, when the model calls `load_skill`. `timeline full` only.
  - `issue_proposed` (`issue`, `source` "classify" or "related", `because`), `issue_confirmed`, `issue_rejected` (on
    the sheet), `issue_dropped` (the `drop` chat command), and `issue_added` (`issue`, `source`, `because`; a label with
    no playbook, `other`): older matters' only, written until TODO item 111 by the issue classifier, the related-issue
    rules, and the sheet; nothing writes them now, and `timeline full` still shows them. Before 2026-09-29 every
    issue was added without confirmation; matters from before 2026-09-27 have issues with no event at all.
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
  `shown`: what the program printed from it, for `get_cases` and `get_deadlines`),
  `command` (`text`: a chat command, `timeline`, `issues`, or `drop`, handled without the model; sessions before TODO
  item 111 only), `sheet` (`id`, `label` (`question` before TODO item 112),
  `typed`: what the tenant typed, empty if they accepted the suggestion, `value`: what was saved; before item 111 also
  `issues_suggested` when the answer brought in a related issue), or
  `printed` (`text`: what the program printed outside the chat, the stop text before item 111, or, with `"what": "deadlines"`,
  the deadlines it printed when asked when and the model did not call `get_deadlines`, or, with `"what":
  "sources"`, the statute and lease words a reply cites), or
  `footer` (`text`: `READING_LINE`, printed by the program under a reply that quotes the statute or the lease; until
  2026-10-02 it was `NOT_DECIDED`), or
  `program` (`text`: a note sent to the model: ahead of the tenant's message after a sheet, or
  `EMPTY_REPLY` after an empty reply), or `check` (`text`: a "[Check: ...]" line printed to the tenant: a
  caution about a cite or a quote from `check_reply`, or `NO_REPLY` from `retry_empty`). Only the chat is transcribed; the
  description or update is in it as the tenant's first message (it is also in `matter.json` or a `tenant_update` event).

Outside `matters/`: `lease.pdf` (a sample lease for test runs, gitignored; `run.py` asks for a path), `dev/leases/`
(the eval's test leases, one per story, built from `lease.pdf` by `dev/build_test_leases.py`; gitignored), `statutes/83.*.txt` and `.html` (the
read-only corpus; only `.txt` is loaded), `playbooks/*.yaml`, `skills/*.md` (the ten skills, one per playbook, written from
the playbooks' own verified content on 2026-10-12, TODO item 110, each with its clocks and counting copied unchanged
and `provenance.converted_from` naming the playbook version; the model loads them with `load_skill` since TODO item 111, and none is signed off), `.env` (the key), `docs/trials/` (dated records of trials, e.g. `2026-10-01-rules/`: the versions of the rules tried, the method, and the results; not kept current), `docs/structure/` (dated snapshots of the structure: a diagram of a
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
`verified_by`, `verified_on`, `verified_hash`; then a line on court and posture, Facts (the facts the
decision turned on, quoted, usually three to six, for the chat to set beside a tenant's), one section per
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
- `load_skill(name)` (TODO item 111): loads one of `skills.skills` into the matter. A name that is not a skill is refused,
  with the names there are; a skill already in `matter["skills"]` is said to be loaded; otherwise `record.add_skill`
  saves the name and logs `skill_loaded`, and the tool answers with a short line: its instructions are now in LOADED
  SKILLS and its sections in THE STATUTE. The prompt is rebuilt before every model call, so they are in the model's
  next call, in the same turn, and in every later turn and visit. Its docstring tells the model what a skill is, that
  SKILLS in its instructions lists every skill with what it covers, to load each one that fits the tenant's situation
  before answering about it (more than one may fit), and that one is loaded once.
- `search_lease(phrase)` (TODO item 82): every numbered clause of the matter's whole lease text (`record.lease_pages`,
  through `lease.find_in_lease`) that holds the phrase, spacing, hyphens, and capitals ignored, each as "Lease Section
  <number>, <title>, page <n>:" with its words (cut at `SEARCH_SHOWN`, 1,500 characters), then any page holding it
  outside a numbered clause, then a line to cite a clause as given; or, found nowhere, that no clause or page of the
  lease's text holds it, to try another wording, and that if none is found the tool found nothing on it in the
  lease's text (a known absence, unlike a clause the profile did not read). Its docstring asks for it before the
  model says the lease does or does not say something. Writes a `fetch` event.
- `propose_facts(facts_json)` (TODO item 112): JSON object keyed by fact id, each `{"value", "how", "said"}`. Its docstring tells the
  model to propose the facts the tenant tells it that the answer, the record, or a letter turns on; to use, for a fact the
  deadlines count from, the id YOUR FACTS gives under what the deadlines still need, in its type; to give any other fact a
  short name of lowercase words joined by underscores; and that the tenant confirms each after the reply. Puts a proposal in `proposed`
  only if: the id is a clock fact of a loaded skill (`record.clock_facts`) and the value fits its type (`sheet.parse_answer`:
  a date as `2026-07-31` or `7/31/2026`, yes/no as true/false or yes/no, a county as non-empty words; stored as parsed), or
  the id is any other fact name (`FACT_ID`, `^[a-z][a-z0-9_]{1,39}$`) and the value is non-empty plain text of at most 300
  characters (`MAX_TEXT`; a number or a boolean is kept as the words `shown` gives); the id of a clock fact of a skill that
  is not loaded is refused ("load that skill first"), so a date is never kept as words; `how` is stated or inferred; and
  `said` appears in what the tenant typed this session (`record.tenant_words`, by `citations.is_in`: an
  ellipsis may join pieces, each of which must appear; spacing, quote-mark style, and end punctuation are
  ignored). A value that reads the same as the confirmed one is refused ("already confirmed with that value"). A proposal for
  a confirmed fact with another value is kept and shown as a changed row. Saves `matter.json`; returns what was proposed and why
  anything was refused. Never confirms: the chat loop runs the confirmation after the turn. It is no longer required that the id
  be an element of a loaded skill's playbook.
- `get_deadlines()`: the listing comes from `tools.deadline_listing()`, which lists every clock of every loaded skill that
  the confirmed facts let the program compute (`tools.computed_deadlines`), with no "ready skill" rule. It returns JSON
  `{"deadlines": [...], "waiting": {skill: [clock facts not confirmed yet]}}`: each deadline carries `skills` (a list; a
  deadline two skills share appears once), and `waiting` appears only when some loaded skill still needs a fact. Writes a
  `deadlines_computed` event per loaded skill that has a dated clock. A tool with `response_format="content_and_artifact"`: the
  program gets the listing as the artifact, and the chat loop prints the turn's last one through
  `timeline.render_deadlines`; the model gets `deadline_receipt(listing)`, how many dated deadlines for which
  skills and which skills wait, with no date in it, so it cannot retype a deadline from earlier in the chat
  and must call the tool to show them again (TODO item 44); the receipt also says the model's instructions say
  which have passed (in lower case: the model copied the receipt into replies, and with it a part's name), to add nothing when the tenant asked only for the deadlines, and otherwise to answer the
  rest without writing a date. Not turn-ending since TODO item 51 (it was `return_direct` from item 19, so the
  model could not retype printed dates; since items 44 and 46 it gets none): the model's answer follows the
  printed listing in the same turn, so a question that mixes a deadline with the law gets both.
- `get_cases(topic)`: `topic` must name one of the matter's case topics, as given or once `topic_named` sets
  aside quote marks, curly apostrophes, letter case, and a trailing case count (`tools.offered_topics`, i.e.
  `wiki.case_topics` for the loaded skills' sections); otherwise "No case topic named ...". A tool with
  `response_format="content_and_artifact"`: the program gets `wiki.render_cases(topic)` as the message's
  artifact, which the chat shows as a `cases` block (`agent.turn_blocks`), and the model gets the same text
  after a line saying it was printed and to apply it as rule 8 says (TODO item 47; was the cases' names only).
  A case quote the model writes is checked by `check_quoted` against what it was given, which now holds the
  cases' words. Writes a `cases_shown` event. Not turn-ending since item 47: the model's answer follows the
  printed cases in the same turn. Every call prints something: a topic already printed in this session prints
  one line ("The cases on ... are printed above in this chat."; the model gets "[... already printed above in
  this chat, and their words are in your earlier get_cases result. Nothing new was printed.]"), and
  a topic not offered prints "This tool has no case topic named ..." with the matter's case topics, so the
  tenant sees the topics there are.
- `draft_letter(issue, posture, account, request, respond_within_days, delivery_method, signed_by,
  obligation_quote, obligation_cite, consequence_quote, consequence_cite)`: `issue` must be a loaded skill that has a
  playbook; `posture` is preserve (no quotes), assert (obligation quote), or escalate (both quotes). `account` (what
  happened, may be "") and `request` are whole sentences in the tenant's voice, printed as written; `signed_by` is the
  tenant's name as the lease gives it. Rejects a cite in the account, request, or delivery method, a signer the lease
  does not name or one with a label, and any quote `quote_is_real` does not find (Data flow, step 7).
  Returns the letter, a "CHECK BEFORE YOU SEND" line when a date or amount in the tenant's part is not in the record,
  and a "NOTE TO TENANT" line from the playbook's `guidance.postures.notice_sufficiency`. Writes the draft file and a `draft` event. If this session already
  drafted the same file and the new text is identical, it writes nothing and returns "[The same letter was
  already drafted in this session (<file>) and appears above. Nothing new was drafted.]". The chat loop
  prints this tool's output directly.
- `add_artifact(path, note)`: copies a file into `artifacts/` under its hash. Writes an `artifact` event.
- `add_communication(sent_on, sender, recipient, channel, text)`: rejects a `sent_on` that is not
  YYYY-MM-DD. Writes a `communication` event. Also used for a letter the tenant reports sending (rule 7).

## The system prompt

Built by `prompt.system_prompt()` on every model call (through the `prompt_from_record` middleware), so it
always matches the record: facts confirmed on the sheet and skills loaded mid-chat show up on the model's
next call. The conversation itself is kept by the checkpointer; only the system prompt is rebuilt. In
this order:

1. `RULES`, through `rules_for`: 2,517 words always (2,492 before TODO item 112, 2,437 before item 111, 2,055 before items 82 and 83), plus rule 6 on letters (219 words; 174 before TODO 96) once a letter is in
   play, and rule 8 on cases in full (271 words) when there is a case topic, otherwise one line. Version G
   (2026-10-02, TODO item 46), for applying the law (README, Purpose). A role paragraph (apply the lease and
   the statute to the record in YOUR FACTS and WHICH DEADLINES HAVE PASSED and say what they mean for the tenant,
   the parts being named as the model names them to the tenant; not
   a lawyer, and the program prints the line saying so, so the model writes none; never send anything or
   work out a date), a format line (short plain sentences; cite, do not recite: each rule in one plain sentence
   with its source in parentheses, "(Fla. Stat. 83.56(1))" or "(Lease Section 4.3)", since the program prints the
   cited words under the reply, never a section, lease clause, or case passage pasted in, quote marks only for
   the few words a point turns on, and never a list of what the tenant confirmed or said, only the facts the
   answer turns on, in a few words, TODO item 73; where a fact came from, when it matters, in plain lower-case
   words, "you confirmed", "your lease says", "the program's deadlines"; no labels like "Quote:", no
   ids, no part name in capitals as the prompt writes it, and no rule number such as "rule 8"; TODO items 53 and
   61), then a short paragraph (TODO item 111: load the skills that fit the tenant's situation with `load_skill` before
   answering about it, more than one may fit; follow a loaded skill's instructions; if none fits, say the tool has no skill
   for that situation and answer only from what `search_statute` and `get_statute_section` find), then nine numbered
   rules, each with
   "Not:" examples and the "Instead:" form: 1 apply the law to the tenant's facts, in order: first, asked what
   they can do or how, whether that option is open, as YOUR OPTIONS gives it, never a step before it (TODO item
   72, with the author's AC reply of 2026-10-04 as its "Not:"), and a point the answer turns on that is in WHAT THE
   TOOL DOES NOT KNOW named as that part gives it (the tenant can tell the tool, can check it, not settled, outside
   the tool, not yet) with what the option would be if it holds and if not, never stated as a fact (TODO item 83;
   its "Not:" lines from four stories: a repair whose lease clause the tool has not read, a deposit with the lease's
   own notice term, a 3-day notice's form, a code the tool does not hold; two "Instead:" lines); the rule in one
   plain sentence with its cite;
   every rule the answer turns on cited to a section whose words say it, each condition and consequence relied
   on, never a rule no cite gives (TODO items 54 and 73; the author's recited reply of 2026-10-04 as its "Not:");
   only the facts it turns on, in a few words, never listed back, never an id or a prompt section's name (a
   fact said in the chat but not confirmed is "not known yet until they confirm it after your reply"); for each condition, met, failed, or not known; what follows, and with an open question in the way what
   follows on each of its readings, never one as the answer (TODO item 56), and when
   asked what they can do, each option the stored text gives and what it requires first (fetching a section
   such as 83.55 or 83.48 when it is not in THE STATUTE); the open question in the way. Never assume a
   fact, never choose among options for the tenant, and say which of lease and statute controls only from a
   stored section (83.47). 2 cite only what was given (a section of the statute shown or fetched, a lease
   section, a case printed), words in quote marks word for word, fetch a section before citing one
   not in THE STATUTE, say plainly when nothing answers, but never with the fallback line when an open
   question or a case topic is on the point, even in other words than the tenant's (TODO item 52); 3 dates only from YOUR FACTS, a lease quote,
   the tenant's words, or a tool result; whether a deadline has passed only from WHICH DEADLINES HAVE PASSED ("passed" or
   "upcoming"), never a comparison of the model's own, nor a date worked out for an open question's reading; the dates only from `get_deadlines`, called every
   time, which the program prints above the reply; asked only for the deadlines the model adds nothing, asked
   more it answers the rest applying WHICH DEADLINES HAVE PASSED (TODO item 51); 4 the model proposes what the tenant tells it with `propose_facts`, the
   tenant confirms it after the reply, and the model asks in the chat only for what its answer turns on, never to confirm
   or supply a fact YOUR FACTS shows (TODO item 112; was "the tenant confirms them on the sheet" and "the sheet asks the
   tenant after your reply"; item 114 rewrites the rules); 5 open questions stay open, given with their readings and what each
   would mean on the tenant's facts, never picked, never put to the tenant; one with no readings is a limit
   of the tool; 6 letters only when asked, only through `draft_letter`, missing details asked once, posture
   lines copied word for word, then an answer to anything else asked with it and one line (TODO 96); 7 record messages and sent letters with `add_communication`;
   8 cases only through `get_cases`, called when the tenant asks what courts said or a case topic is on
   the point being applied; then for every case it gives, its facts beside the tenant's, its rule quoted with
   name and page (and the statute version it read when not today's), what the rule would mean on the
   tenant's facts and whether another case distinguished it, a case against the tenant said so plainly, no
   case quoted except from the result (247 words; TODO item 47); 9 offer nothing the tenant did not ask for,
   though a step the statute requires before an option is part of the answer. Version F (2026-10-01, the
   trial in `docs/trials/2026-10-01-rules/`), which set the lease, the statute, and the record side by side
   and never said what they meant (rule 1 "organize, never advise": no must, may, can, should, entitled,
   required, rights, or options about anyone outside quote marks; quote, then "This tool does not decide
   that."), is in git history at commit a3b0b13. Rules 1 to 7 cover the same ground as the seven rules of
   2026-09-30 (whose numbers TODO.md items 15 to 22 use). Where rules 2 and 5 named WHAT THE STATUTE DOES NOT SETTLE and
   rule 6's "Not:" named THE TOOL'S NOTES ON YOUR ISSUES, they now name a loaded skill's "What the statute does not
   settle" and its Letters section (TODO item 111); rules 1 and 3 still name YOUR OPTIONS and WHAT THE TOOL DOES NOT KNOW,
   which go with item 113.
Then the parts, each under its name in `prompt.PARTS`, a name a tenant can read, with a short line saying what
it holds. A reply that names its source in plain words ("your facts show", "the program's deadlines show")
reads right to the tenant. Until TODO item 61 (2026-10-03) the parts were LEASE PROFILE, PLAYBOOKS (guidance
and open questions together), STATUTE SECTIONS, CASE TOPICS, ELEMENT STATUS, and DEADLINE STATUS, and the
model wrote "(ELEMENT STATUS shows ...)" or "the open question in PLAYBOOKS" in 17 replies per 100 though the
rules forbade it.

2. `YOUR LEASE`, whose name line says it holds only the clauses the tool reads, not the whole lease (TODO item 76;
   rule 2's "Not:" is the eval's "The lease does not mention air conditioning."): `lease.lease_lines`, a line per
   clause in plain words with the cite to use and its words (TODO item 77; was the profile as JSON, whose field
   names the model used as cites; rule 2's "Not:" is "(Lease notice_before_vacating)"). The name line also says
   `search_lease` searches the whole lease's text, and rule 2 asks for it, with a second wording, before the model
   says the lease lacks something, and for "The tool found nothing on that in your lease's text." only when no wording
   is found (TODO item 82; the "Not:" adds the eval's "The lease does not contain a holdover clause.").
3. `SKILLS` (TODO item 111), whose name line says these are the skills the tool has, each loaded with `load_skill`: one
   line per skill in `skills.skills`, "- <name>: <description>", with " (loaded)" after a loaded one. The model picks from
   this menu; the tool `load_skill` loads what it picks.
4. `LOADED SKILLS`: for each skill in `matter["skills"]`, in the order loaded, its name as a heading line, "# <name>", and
   its body (`skills.Skill.body`: when to load it, what to find out, what the tenant can do, deadlines, what the statute
   does not settle with its readings, letters, mistakes to avoid); "none loaded yet" when there is none. These replace
   the earlier parts THE TOOL'S NOTES ON YOUR ISSUES (each playbook's guidance as YAML) and WHAT THE STATUTE DOES NOT
   SETTLE (its open questions), which went with item 111: a skill's body carries both.
5. `THE STATUTE`: the text of every section the loaded skills list in `sections`, once each; empty while no skill is
   loaded (a section outside them is fetched with `get_statute_section`).
6. `COURT CASES THIS TOOL HAS`: `prompt.case_topics_text()`, one line per topic with its number of cases,
   from `tools.offered_topics()`, or "none for these issues" (always, until the author verifies pages).
7. `YOUR FACTS` (TODO item 112; was `element_status()` as JSON, every playbook element known, changed, proposed, missing,
   or n/a): `prompt.facts_status()`, in three lists. "Confirmed by the tenant": each confirmed fact as "- <id>: <value>" (yes/no for a
   boolean; ids are fine in the prompt, the rules forbid them in a reply), or "none yet". "Proposed, waiting for the tenant to
   confirm after your reply": each proposal, likewise, or "none". "What the deadlines still need": each clock fact of a
   loaded skill not confirmed yet (`skills.unconfirmed_clock_facts`), "- <id> (<type>): <what it does for each clock> [<skill
   name in words>]", the type being date, bool, or county, and what it does being "counted from by the <actor>'s <days>-day
   deadline of Fla. Stat. <cite>", "decides whether the <cite> deadline counts" for an `applies_if`, "the county, for counting
   court business days", or "printed beside the <cite> deadline's date; not needed to count it" for a `shown_with`
   (`role_words`); or "nothing: every fact the loaded skills' deadlines count from is confirmed". The model proposes each
   under the id shown.
8. `YOUR OPTIONS`: `prompt.options_status()`: for each active issue's options (`deterministic.check_options`,
   from the confirmed facts, the clocks, and the lease profile), "- <label> (Fla. Stat. <cite>): <STATUS>", then a
   line per condition (gate) with its state in words (`state_words`: its status, what the tool knows of it when
   that says more, "the tenant can tell the tool" or "the tenant can check", and why); a condition not met with
   several ways lists each way with its own state; a condition not decided adds "if this condition is met, the
   option is <status>; if it is not, the option is closed" (TODO item 81); a way for another case (its why
   `NOT_APPLY`: hot water when the problem is the AC) is left out of a condition's list when another way remains; a
   line per step with "done", "waiting", "passed", "the tenant can check", "not settled", or "to do", and why when it
   has one (the tenant's notice's words beside the check; TODO items 90 to 92); and "also, from what the statute does not settle:" with the first sentence of each open question the
   option names in `also_open`. In words, no id. A condition of an option that another condition closes gets no "if
   this condition is met" line (TODO item 84: "closed if it holds; if not, closed" said nothing). "none: no active
   issue lists its options yet" with no active playbook (every playbook has options since item 84). Rule 1 asks for
   an option's status before any of its steps (TODO item 72).
9. `WHAT THE TOOL DOES NOT KNOW` (TODO item 83): `prompt.unknowns_status()`: each point an option of an active issue
   turns on that the tool has not decided (a way of a gate in a state of `UNDECIDED`: tell, check, not settled,
   outside, not met yet) and that could change an option (a condition of an option another condition closes is
   left out), once however many options it decides, as "- whether <the way's condition> (<cite>)
   [<issues>]: <what the tool knows of it, `KNOWN_AS`: the tenant can tell the tool, the tenant can check, not
   settled, outside the tool, not yet>: <why>", then a line per option it decides, "<label>: <status> if it holds; if
   not, the condition turns on whether <the gate's other undecided ways>" (or "closed"); then the lease parts the
   profile did not read, and a last line: YOUR LEASE holds only the clauses the tool reads, `search_lease` searches
   the whole text, and only a point no wording finds there is known to be absent. In words, no id.
10. `WHICH DEADLINES HAVE PASSED`, whose name line says it has no dates and that any question about when calls
   `get_deadlines` (named THE PROGRAM'S DEADLINES for a few hours on 2026-10-03, which the model read as the
   deadlines themselves and answered from): `prompt.deadline_status()`: for each deadline the confirmed facts give (`tools.computed_deadlines`), by its label ("claim
   notice deadline", not the clock's id) with its skills, whose it is, what it counts from (the fact's label,
   not its date), its cite, and "passed" or "upcoming" (or why it has
   no date), with "(counts only if ...)" for a clock with a `condition`; then each skill still waiting, with the facts it waits for
   (`tools.deadlines_waiting`). Logs nothing. So the model can apply a
   condition such as "within the 30-day period" without seeing or comparing a date.

The program note after a sheet still tells the model, in the conversation, that a sheet just ran.

## Playbook schema

Ten playbooks, one per skill (a skill and its playbook have the same name; until TODO item 111 the names were the
issue labels the classifier could pick): deposit_not_returned,
deposit_claim_received, repair_not_made, notice_received_nonpayment, notice_received_violation,
landlord_entered_unannounced, rent_increased, wants_to_leave_early, lease_ending, neighbor_disturbance. The
playbooks have `verified_by: null` until the author's hand check. Their open questions and failure modes were
rewritten for applying the law (2026-10-02), their prose lost its ids (2026-10-03), and four got failure modes
for conditions the model missed or misapplied (TODO item 55, 2026-10-03): version 0.3 for most,
deposit_not_returned, lease_ending, and notice_received_violation 0.4, notice_received_nonpayment 0.5, and
landlord_entered_unannounced 0.5 (its purpose_of_entry open question reworded the same day, item 56); repair_not_made
0.5 since its options' knowledge states (2026-10-04, items 72 and 81), deposit_not_returned 0.5 and
notice_received_nonpayment 0.6 since their options (item 81); the other seven one step up since theirs (item 84):
deposit_claim_received and rent_increased and wants_to_leave_early and neighbor_disturbance 0.4,
notice_received_violation and lease_ending 0.5, landlord_entered_unannounced 0.6; repair_not_made 0.6 and
neighbor_disturbance 0.5 since the sheet asks them plain facts (2026-10-08, TODO items 86 and 90 to 92), and the same day
deposit_not_returned, lease_ending, and notice_received_violation 0.6, deposit_claim_received, rent_increased, and
wants_to_leave_early 0.5 (TODO item 102). Three have no clocks, and say why in `counting.note`: landlord_entered_unannounced
(83.53(2) is in hours), rent_increased (no section on notice of a rent increase), neighbor_disturbance (no
deadline for a landlord to act on one tenant's complaint about another; its open questions: whose duty
83.52(7) states, 83.56(2)(a) as a remedy not a duty, what is unreasonable, and whether 83.56(1) lets the
tenant leave over it). notice_received_nonpayment computes 83.56(3) in court business days
and leaves 83.60(2) uncomputed. Facts shared across playbooks by id: `claim_notice_date`,
`tenancy_terminated`, `deposit_amount`, `eviction_action_filed`, `fixed_term_lease`, `term_end_date`,
`month_to_month`, `monthly_rent`, `registry_paid` (notice_received_nonpayment and notice_received_violation),
`claim_delivery` (the two deposit playbooks), `leave_notice_given` and `leave_notice_sent_by` (deposit_not_returned and
wants_to_leave_early: one notice before moving out, asked once).

One YAML file per issue in `playbooks/`. `load_playbook` validates it against `Playbook` and raises if a
section is not in `statutes/`, a clock's `trigger` is not a date element or an element's `compare_to` is not a `LeaseProfile` field.
After all playbooks load, `corpus.py` also raises if a related issue is not a playbook's issue or its
condition's fact is not an element of any playbook. Keys the `Playbook` class does not define are dropped on load.

- `issue`: the label, the same name as the skill that loads it (`record.active_playbooks` matches them). Key of `playbooks`.
- `description`: the situation the playbook covers, in one line, naming the event that starts the issue
  rather than background facts. Not read by code since TODO item 111 (the skill's own `description` is what the model
  reads in SKILLS).
- `sections`: the statute sections the playbook rests on, e.g. `["83.49"]`. `load_playbook` raises if one is
  not in `statutes/`. Not read by the prompt since TODO item 111: THE STATUTE takes the sections of the loaded skill,
  which are the same.
- `provenance`: statute year, file verified against, who and when, version. Not read by code.
- `counting.convention`: copied into every `compute_deadlines` result. `counting.status` and the optional
  `counting.note` (why a playbook computes fewer dates than its sections mention): not read by code.
- `spec` (typed, read by code):
  - `elements`: `id`, `type` (date, money, bool, text, choice; a choice lists its answers in `choices`, in plain words:
    what the tenant saw or did, never a term of the statute, TODO items 86 and 90 to 92), `source` (list; `user` and/or
    `lease_profile.<field>`, tried in order), `applies_if` (id of a bool element), `compare_to` (optional,
    `lease_profile.<field>`: the lease field to show next to the tenant's value when they differ; read by nothing since
    TODO item 112, when `lease_differs` went; the deposit playbooks set `tenancy_terminated` against `term_end`;
    rent_increased, wants_to_leave_early, and lease_ending set `term_end_date` against it). Read by the options layer
    only (`deterministic.check_options`: `listed`, `asked_never`); since TODO item 112 not by `check_elements` and
    `fill_facts` (gone), `build_letter`, or `render_timeline`, which read the confirmed facts.
  - `clocks`: `id`, `actor` (landlord, tenant), `trigger` (a date element id), `days`, `direction`
    (before, after), `cite`, `quote`, optional `consequence` (`delivery`, a list read by nothing, went on 2026-10-08), `condition` (what the date
    counts only if, in words, printed with it: a notice whose sufficiency the tool does not decide), `applies_if`, `shown_with` (a
    date element shown beside the computed date once confirmed, e.g. the date a notice itself states;
    checked by `load_playbook`), `count`
    (`calendar_days`, the default, or `court_business_days`; a playbook with a court-day clock must have a
    `premises_county` element, checked by `load_playbook`). Read by
    `compute_deadlines`; `quote` and `consequence` checked by `check_playbook`; `smoke.py` uses
    `clocks[0].quote`.
  - `lease_overrides`, `exclusions`: lists of dicts. Any item with a `quote` is checked by
    `check_playbook` against the section in its `cite`. Otherwise not read by code.
  - `related_issues`: list of `{issue, when: {fact, equals}}`. Checked when the playbooks load, and read by nothing
    else since TODO item 111 (`record.add_related_issues` suggested the issue once `fact` was confirmed with the
    value `equals`); it goes with the playbooks (item 113).
  - `options` (TODO items 72, 81, and 84; every playbook): each
    `id`, `label` (plain words), `cite`, `gates`, `steps`, and `also_open` (open questions that bear on it even when
    every gate is met). A gate (`corpus.Gate`) is a condition, `says`, `cite`, `quote`, met through any of its `ways`
    (`corpus.Way`), each decided by exactly one of: a `fact` with `equals`; a `clock` with `equals` "passed" (the
    default) or "upcoming"; `check` (what the tenant can check, and where: a part of the lease, a local code, a
    document); `outside` (law the tool does not hold); or an `open_question` alone (not settled: whether a violation
    could be cured). For a choice fact, `equals` may list several answers, any of which meets the way. A way may have
    `applies_if`, a yes/no fact, or `{fact, equals}` naming answers of a choice fact: it counts only when that holds
    (an objection already sent, a message sent by e-mail), is not met when it does not, and is the tenant's to tell
    before (item 84). A way whose fact's own `applies_if` is confirmed false is not met (a question never
    asked). A check may name a text fact in `beside`, whose words from the record are given with it. A fact
    or clock way has `when_otherwise` and `otherwise`
    for a value against it: "closed" (the default), "unsettled" with an `open_question`, or "later" (not met yet). A
    way may name a lease clause, `lease`, a `LeaseProfile` field: for a fact way, a clause not read makes the fact
    the tenant's to check rather than to tell (until TODO item 112 the sheet also showed the clause beside the fact's
    question, through `corpus.fact_lease`). A way's own `says`, `cite`, and `quote` are optional; a single-way gate leaves them to
    the gate. Steps: `says`, `cite`, `quote`, and one `fact` with `equals`, one `clock`, or `ways` (decided as a
    gate's condition is: done through a way met, the tenant can check, not settled, or to do). `load_playbook` checks
    each way's shape (`way_problem`, a step's ways too) and that every fact, clock, open question, lease clause, and
    choice answer named exists;
    `check_playbook` that every quote (a way's too) is in its section, every cite among the playbook's sections, and
    no id in the prose (a way's `says`, `when_otherwise`, `check`, `outside` included). Read by
    `deterministic.check_options`; the gates are the author's to check (TODO item 84). The model asks only what the
    tenant saw, did, or holds; which answers meet a condition is the playbook's reading, and what no answer settles
    is a check or an open question (2026-10-08, TODO items 86, 90 to 92, and 102; every playbook). repair_not_made (0.6): end the lease (83.56(1)), gated on a duty to fix the problem, met through what the
    problem is with (`problem_is_with`, a choice): the roof, a window or a door, a floor, steps, or a porch, an outside
    wall or the foundation, another structural part, or pipes, drains, toilets, or faucets meet 83.51(1)(b); running
    water and hot water are not settled through `subsection_one_or_two`; something else is the tenant's to check; or
    the lease, the tenant's to check against its repairs clause and its exceptions (83.56(1) also reaches "material
    provisions of the rental agreement"; the sheet no longer asks whether the lease promises it, item 86), or a code
    (83.51(1)(a), the tenant's to check with the code enforcement office); on the duty not changed in writing (only
    for a single-family home or duplex, 83.51(1)); on who caused it (`caused_by`, a choice; 83.51(4)): nothing anyone
    did, the landlord or its workers, or someone the tenant did not let in meet it; the tenant, a family member, or a
    guest close it; a roommate is not settled through `roommate_consent`; not knowing is the tenant's to check; and on
    no waiver by rent paid with knowledge (83.56(5)(a); not settled when rent was paid, `rent_paid_waiver`); steps:
    the message delivered as 83.56(4) allows (`message_sent_by`: by hand or by mail done, e-mail the tenant's to check
    for an 83.505 addendum, something else to check, a portal request or a text to do), its words stating the intent
    to end the lease (the tenant's to check, `message_words` beside it, when `message_mentions_ending`), the 7 days
    (passed, not done, while the steps above are not done; the clock counts from `message_date` and carries its
    `condition`). Withhold rent (83.60(1)(b)): the duty through the structure or plumbing (the same reading) or a code
    (the lease does not reach it), the duty not changed, the same cause; steps: the message delivered (by hand or by
    mail done; any other way not settled through `withholding_notice_delivery`, since 83.60(1)(b) names no way), its
    words stating the intent not to pay rent (to check, when `message_mentions_rent`), the 7 days. deposit_not_returned (0.6): the
    whole deposit back (83.49(3)(a)), gated on no notice of a claim received (nothing in writing received; by certified
    mail, closed; another way, `claim_delivery`, not settled through `email_notice_conditions`, added for it; not known
    how, the tenant's to check), the 30 days passed (the `claim_notice_deadline` clock; not met yet while upcoming), and
    the landlord not relieved of the notice by 83.49(5) (not early or periodic, or the 7-day notice, `leave_notice_sent_by`:
    by certified mail or by hand the tenant's to check against the last day and for the address, by e-mail for the
    83.505 addendum too, something else to check, or the lease's own notice term, the tenant's to check); no steps;
    `termination_date_meaning` also open. notice_received_nonpayment (0.6): paying before the 3
    days end (83.56(3); the clock upcoming; outside the tool with no court calendar for the county), defending in
    an eviction case on a ground other than payment (83.60(2); not open yet until a case is filed; step: the rent
    into the court registry, `registry_paid`, added for it), and defending on a defective notice (the notice
    against 83.56(3)'s form, the tenant's to check; `notice_form` also open). Item 84, the other seven:
    deposit_claim_received (0.5): object within the 15 days (83.49(3)(b); the clock upcoming, or an objection
    already sent, the tenant's to check against the printed date; step: the objection, done for a letter to the address
    the notice gives, `objection_sent_by`, otherwise not settled through `objection_form`), and the whole deposit back
    (83.49(3)(a): the 30 days passed, and a notice sent after them, the tenant's to check against the postmark, or
    one not sent as 83.49(3)(a) names, `claim_delivery` other than certified mail, not settled through
    `email_notice_conditions`, or not known how, to check). notice_received_violation
    (0.6; the question on an earlier warning asks about any written warning or notice, 2026-10-08): fix the problem within the 7 days (83.56(2)(b)); defend a case over a notice that ended the lease
    without a chance to cure (whether the violation is curable not settled, `which_paragraph`; no warning of a
    similar violation in 12 months, or one the tenant can check; a case filed; step: the rent into the court
    registry, `registry_paid`, added for it, as 83.56(5)(b) requires); and the landlord's waiver by rent taken
    (83.56(5)(a), whether the violation went on the tenant's to check). landlord_entered_unannounced (0.6, 83.55
    added to its sections): damages of at least 3 months' rent for a utility cut, a lockout, or a removal
    (83.67(6)); damages for an entry the statute does not allow (83.55, 83.53(2): no consent, no emergency, not for
    protection or preservation, not settled through `purpose_of_entry`, no unreasonable refusal, no 24 hours' notice
    for a repair, not away half a rent period, and damages, the tenant's to check). rent_increased (0.5): the
    retaliation defense (83.64: protected conduct before the increase, `complaint_kind`: a complaint to a code office or
    a tenant group met, a written repair notice to the landlord the tenant's to check against 83.56(1), anything else or
    nothing not settled through `retaliation`; good faith, treated differently, primarily
    retaliating, not settled through `retaliation`, no good cause, a case filed; `eviction_action_filed` added for
    it), and ending a month-to-month tenancy (83.57(3)). wants_to_leave_early (0.5): a servicemember's termination
    (83.682; the orders against the criteria, the tenant's to check; steps: the notice with the orders, the 30 days),
    the early termination fee (83.595(4): the separate addendum, `fee_written_where`: a separate paper met, only the
    lease closed, not known to check; the amount against two months' rent and the lease's notice, the tenant's to check;
    step: the notice the lease asks for, to check), and the 7-day notice before leaving (83.49(5): the last day not
    passed, or a notice already given; the lease's own term to check; step: the notice by certified mail or by hand,
    to check for its address, by e-mail for the 83.505 addendum too, another way to do). lease_ending (0.6): ending a
    month-to-month tenancy (83.57(3); the last day for this period not passed, or a notice already given; step: the
    notice, `end_notice_sent_by` read as 83.56(4) is for repair_not_made's message), leaving at the end without the
    lease's liquidated damages when the landlord did not send the 83.575(2) notice (nothing in writing from the
    landlord about the end of the lease meets it; anything is the tenant's to check), and staying with permission
    (83.575(3)). neighbor_disturbance (0.5): ending the lease (83.56(1): a lease promise the tenant can check with
    `search_lease`, or the failure to act itself, not settled through `ending_own_lease`; the source a tenant of the
    same landlord, else not settled through `remedy_not_duty`; the disturbance unreasonable, not settled; steps: the
    written complaint delivered as 83.56(4) allows, read from `complaint_sent_by` as repair_not_made reads its message,
    and its words stating the intent to end the lease, the tenant's to check, `complaint_words` beside it, when
    `complaint_mentions_ending`; its own facts, so a repair notice and a neighbor complaint are not one paper).
  - `open_questions`: each `id`, `sections`, `text` (what the stored text lets the model apply, and what stays
    open), and, for a point the stored text does not settle, `readings` (two or more readings of it, which the
    model gives side by side; a question about a limit of the tool, such as a period in hours or months, has
    none). `check_playbook` checks the shape and, like all prose, the quotes. Not otherwise read by code. Not shown to the
    model since TODO item 111: each skill's body carries its open questions.
- `guidance` (prose, no longer put into the prompt since TODO item 111; the skill's body carries it), with two pieces also read by code:
  - `questions`: one question per element id. Read by the options layer only, which says "ask the tenant: <question>"
    for a point the tenant can tell the tool (`way_state`); `check_playbook` still checks that every element has one.
    Neither the sheet (until TODO item 112) nor `fill_facts` (until item 111) asks them any more.
  - `postures.notice_sufficiency`: appended to every `draft_letter` result as the note to the tenant.
  - `lease_checks`, `evidence`, `postures` (core, preserve, assert, escalate), `failure_modes` (slips in
    applying this issue's law: a condition skipped, a fact assumed, a date counted by the model): model only.

## Running and testing

    bash setup.sh            # once: venv, pip install, .env from template, matters/
    source venv/bin/activate

Offline checks (no model call, no key needed):

    python smoke.py                                                              # the offline smoke tests
    python -c "from corpus import check_all_playbooks; check_all_playbooks()"   # playbook checks: every line OK
    python -c "import skills; skills.check_all_skills()"                         # skill checks: every line OK
    python schemas.py                                                            # what the model sees per tool
    python dev/build_cases.py "<Westlaw print>"                                  # once: builds cases/
    python dev/build_test_leases.py                                              # once: the eval's test leases
    python wiki.py check                                                         # wiki checks: no problems

- `python dev/build_test_leases.py`: writes `dev/leases/<name>.pdf`, one lease per eval story (TODO item 60,
  2026-10-03; before, every scenario read `lease.pdf`, a twelve-month lease from 2026-10-01 at $1,850, and the
  stories said otherwise, so a rent increase was read as a decrease and a $1,000 deposit as $1,850). Each is
  `lease.pdf`'s text as PyPDF2 reads it, with changes from `LEASES` made word for word: `term(start, end,
  signed)`, `rent(words, figure, fee)` (with the early termination fee, two months' rent), `deposit(words,
  figure)`, `NO_PETS`. A change whose old words are not in the text exactly once stops the build. `pdf_bytes`
  writes a plain PDF (each line in order, Helvetica, WinAnsiEncoding), and `build` reads it back and checks its
  text is the changed text. Eleven leases: `current` (2026-08-01 to 2027-07-31, the old rent and deposit), with
  `_no_pets`, `_orange` (the house in Orlando, Orange County, whose 3-day period the tool cannot count: no court
  calendar for that county; `ORANGE`, TODO item 85), `cash_1300`, `taped_1100`, `family_1050`, three ended ones (`ended_2026-06-30`, `-07-31`,
  `-08-31`), `ends_2026-12-31`, and `month_to_month_950` (a term that ended 2025-09-30, month to month since
  under the lease's Section 2.4). Gemma reads each with the story's term, rent, and deposit (checked
  2026-10-03).
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

- `python smoke.py`: runs the parts in `smoke_parts/`, in order (a new check goes in the part on its subject).
  Needs the saved test matter `matters/t-test/test-001/` with its lease profile. Opens it
  with `load_matter` and prints `list_matters()`, then runs the playbook checks (one named check, "every
  playbook check is OK", fails if any line of `check_all_playbooks` does), deadlines on hand-typed facts with today fixed at 2026-09-08, the case corpus (every file in `cases/`
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
  against those facts (a deadline computed from the confirmed date and not from a proposed one, `waiting` listing the
  clock facts not confirmed, and a fact only a ruled-out clock needs not waited for; TODO item 112), the letter template, the cite checks (subsection markers in order in every stored section,
  each kind of bad cite flagged, and a real, shown but wrong cite passing), the quote checks (which cite goes
  with which quote, a good quote passing despite apostrophes or an ellipsis, items 5 and 6 of TODO.md as
  they would look in quote marks), and both
  timelines. The timelines read the real `events.jsonl` of `test-001`. Importing `tools` and `timeline`
  also checks that the modules import. Last, on a scratch copy `matters/t-smoke/m-001` (removed at the
  end, even after a failure), named checks of the code that writes to a matter: listing and
  ids, sessions and their tags, `record.clock_facts`, nothing dated from a proposed fact, `propose_facts` (TODO item 112) taking a
  clock fact typed (a date) and refusing a bad date and a bad yes/no, taking a free-form fact as plain text, refusing a bad
  name, a clock fact of a skill not loaded, words the tenant never typed, a how that is not stated or inferred, a text over
  300 characters, and a value equal to the confirmed one, and refusing JSON that is not an object; the confirmation's rows
  (only the proposals, a changed fact with both values) and its scripted answers (accept, correct, a bad date asked again, a
  changed fact, a skip that stays pending and is asked again at the next confirmation); YOUR FACTS (confirmed, proposed, what the deadlines still need,
  and after the confirmation); `get_deadlines` computing from the confirmed clock dates with `waiting` naming what is not confirmed, then
  without `waiting`; the timeline's dates (a plain-text date fact among them); the rule 4 text; a county as a clock fact on
  `matters/t-smoke-county/m-001` (taken as words, an empty one refused, a court-days clock dated, a letter's dates and amounts
  checked against every confirmed fact value); the prompt following the record, a flagged cite and
  quote printed and logged, a turn's blocks (the model's reply apart from the program's cautions and line), the
  tenant's description counting as given, events, the transcript, and the
  timeline. Then the skills (TODO item 111; `smoke_parts/skills_and_turns.py`): on `matters/t-smoke-skills/m-001`,
  `load_skill` refusing a name that is not a skill (listing the ones there are), saying one is already loaded, and
  loading one (`matter.json` has it, a `skill_loaded` event with the session, and the next system prompt marks it loaded
  in SKILLS, holds its body in LOADED SKILLS and its sections in THE STATUTE); on `matters/t-smoke-old/m-001`,
  `load_matter` and `list_matters` turning an old matter's issues into skills; on `matters/t-smoke-intake/m-001`,
  `intake` saving the description and `resume` logging the update with a tripwire in place of the model clients, and the
  description and the update going to a stand-in model as the first turn (it loads a skill and proposes a fact from the
  tenant's own words); then turns with a stand-in model on `matters/t-smoke-related/m-001` (a skill with a fact open does not
  block another's deadlines), and every skill's clock facts through the real
  code path on `matters/t-smoke-playbooks/m-001`: for each of the ten, the model's `propose_facts` gives its clock facts (a date
  for every date, yes for every `applies_if`, Alachua for a county), the confirmation accepts each, every clock must get a
  date with nothing left waiting, and a preserve letter must carry the playbook's `notice_sufficiency` note. A new skill is
  covered without a new check. Then the options layer's checks (TODO items 86 and 90 to 92): the eval's stories F, A, C, and E
  through the repair gates and steps, a neighbor complaint, an unlisted answer refused on load, the letter's date line, and the
  prompt's step lines, on `matters/t-smoke-steps/m-001`. Last, the
  web page, run headless by Streamlit's `AppTest` on `matters/t-smoke-app/m-001` with a stand-in model: a
  saved matter opened from the list, nothing new, a reply in a speech bubble with the program's caution and
  line outside it and its `$` and `*` shown as written, the sidebar naming the loaded skill by its description with
  no id, the model loading a second skill and proposing three facts (the sidebar adds the skill; the page's form asks a
  changed yes/no with the old answer beside it, a date with a date picker, and leaves a text pending when skipped), the note with the next message, deadlines in a program box, a model
  error shown as a caution, End session; then, on `matters/t-smoke-app-text/m-001`, an update typed at the door as
  the first message, and a date, a county in a line, and a corrected text confirmed on the form that follows. Then the
  skill format (TODO item 109; `smoke_parts/skill_files.py`, no matter): one valid fixture skill, written to a temporary
  folder with statute quotes copied from `repair_not_made.yaml` and `notice_received_nonpayment.yaml`, loads and has no
  failures; its clock facts are typed by role (and `premises_county` for a court-days clock), and the ones not confirmed yet
  are listed in the clocks' order, leaving out a clock whose `applies_if` is confirmed no (TODO item 112); a fact id typed
  two ways is caught, as a trigger and an `applies_if` in one skill and as two skills, and `check_all_skills` fails
  with a line naming it; and each of these is caught,
  as its own check: a name that is not the file's, a two-line, empty, or overlong description, a section not in `statutes/`,
  a clock cite outside the sections, clocks with no counting convention, a clock that is not a `Clock` or has a misspelled
  key, a file with no header; a clock quote or consequence changed by one word or cited to the wrong subsection; a missing,
  misordered, repeated, or extra "## " heading, "## Deadlines" missing while there are clocks or present while there are
  none; a body quotation in no stored section (cited or not), cited to the wrong subsection, or to a subsection the section
  lacks; a clock id or a clock fact id (also `premises_county`) written in the body; and `skills.skills` a dict that
  `check_all_skills` finds no failure in, with no fact id typed two ways across the ten. Every line
  must be OK; the last line says "all checks OK" or lists the failures. The test matter itself is not
  changed by a smoke run.

Calls the model (needs the key in `.env`; stops at `require_key()` without it):

- `python smoke_online.py`: opens the same test matter with `load_matter`. Since TODO item 111 intake and `resume` call
  no model, so it runs the model's first turn on throwaway copies (one turn each, three in all): a new matter's
  description (`matters/t-smoke-online-new/m-001`: the description saved, a reply, the skill that fits loaded,
  facts proposed, nothing confirmed, each skill loaded logged), a situation no skill covers
  (`matters/t-smoke-online-none/m-001`: no skill loaded), and `resume` with an update
  (`matters/t-smoke-online/m-001`: the update logged verbatim, the description and the skills loaded kept, nothing
  confirmed, no suggestion equal to a confirmed value). A date a loaded skill's clock counts from is checked as proposed
  under that skill's fact id (TODO item 112). Checks marked "(model)" depend on the model's answer.
- `python dev/live_run.py dev/scenarios/<name>.json`: a live session without typing. (Written for the flow before TODO item
  111: the sheet rules for issues and fact questions that came before the chat, and `expect.issues`, which `dev/eval.py` reads from
  `matter.json`'s `issues`, no longer match, and since TODO item 112 the sheet is the confirmation of proposals, whose rows are a
  label and a hint, not a question, so the sheet rules match nothing and skip each row; TODO item 115 rewrites the driver and the scenarios for a conversation.) The scenario gives the
  lines typed before the sheet (`start`), rules for the sheet (`sheet`: a piece of a question's text to a
  list of answers used in order, so a bad answer then a good one tests the re-ask; a question no rule
  matches gets "?"), and the chat lines (`chat`, then "bye"). Questions are found on screen by their type
  hint (a choice's is "number or words"; answer it with its words), since each prints on the same line as the previous prompt. A sheet that appears mid-chat is answered
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
- `python dev/eval.py run <out dir> <repeats> [scenario ...]` (out dir: `dev/eval_runs/<name>`, ignored by git):
  runs scenarios several times each, several
  sessions at once (`--parallel N`, default 8), and scores every run by code (`python dev/eval.py score <out
  dir>` scores again). With no scenario named, every scenario with an `expect` block. Each run is
  `dev/live_run.py` under its own scratch tenant `matters/t-eval-<out dir name>-<scenario>-<k>`, seeded with an
  `m-000` copy of the test matter so the id exists; the run's matter is the one its screen names. When the
  runs end, `file_away` copies each run's `matter.json`, events, and transcript into `<out dir>/matters/` and
  removes the `t-eval-` scratch tenants from `matters/`, so `run.py`'s tenant list is as it was.
  `--project <folder>` runs another copy of the project, e.g. a git worktree at an older commit, to compare
  (the scenarios and the seed still come from this copy). The `expect` block: `issues` (the playbook issues
  active at the end), `stops` (the tool stops before the chat), `not_covered_note`, `deadlines` (issues with a
  `deadlines_computed` event naming a clock), `letters` (`draft` events), `screen_must` and `screen_must_not`
  (regexes on the whole screen), `turns` (per chat line, found by a
  piece of it: tools `called` and `not_called`, regexes the turn's replies `must` have and `must_not` have
  outside quote marks, the `topics` allowed for `get_cases`, `applied`: a reply applies the law, a quote or a
  statute or lease cite (`CITE_SEEN`, since TODO item 73) with `APPLIED_WORDS` (40) words or more of the
  model's own addressed to the tenant, `open_first`: outside quote marks, whether the option is open
  (`OPEN_WORDS`: not settled, turns on, depends on, not known yet, is not open, is closed) comes before the first
  step toward it (`STEP_WORDS`: deliver, send, or give a notice, wait 7 days; TODO item 72), and `cases_used`: a reply names
  a case a `get_cases` result in the session gave, `case_given` matching it with or without leading words such
  as "In"; a court question answered from cases given earlier also counts as calling `get_cases`), and
  `screen_must_not`. Every reply is also
  measured, with the model's no-break spaces and hyphens read as plain ones (`PLAIN`): empty turns, program cautions,
  field names, lease searches (turns calling `search_lease`) and "absent"
  (`LEASE_ABSENT`: a reply saying the lease lacks something, "the lease does not mention", with no `search_lease` call
  before it in the session; TODO item 85), a computed deadline the program printed found in the reply
  (the model never sees one, so it counted it; not when the date is also a fact the record holds), recited
  (`recited`: more than `RECITED_CHARS`, 300, characters in quote marks, or `RECITED_FACTS`, 3, lines of "You
  confirmed" or "You said"; TODO item 73), quotes only (a quote
  and fewer than 40 words of its own), dates made (a date with a year outside quote marks that no fact, tenant
  line, sheet answer, or the run's lease holds, `lease_dates(entry)` from the PDF named in the run's own copy of
  its scenario), cases not given (a "Name v. Name" no `get_cases` result in
  the session holds), retold cites (`citations.cites_without_quote`: a cite outside quote marks with none of
  its words quoted in the same reply; TODO item 54), deadlines the program printed itself (`deadlines_by_program`,
  "dl-prog" in the table: a transcript `printed` line marked `"what": "deadlines"`; an expectation that a turn
  calls `get_deadlines` still counts only the model's call; TODO item 65), and two word screens (`CHOOSE_WORDS`: you should, your best option, I recommend;
  `OFFER_WORDS`) that only mark a reply for a person to read, and prompt names (`PROMPT_NAME`: a prompt
  part's name as the prompt writes it, before TODO item 61 or since, YOUR OPTIONS and WHAT THE TOOL DOES NOT KNOW
  included, in capitals, or a rule's number such as "rule 8"; TODO items 53, 61, and 83). Since 2026-10-02 (TODO item 49) a legal question's
  turn expects `applied` instead of "does not decide", and the `LAW_WORDS` screen and the `must_not` patterns
  against "entitled", "allowed", "forfeit", and case names are gone. The blind scorers' rubric is
  `dev/eval_rubric.md` (applied answers: OPTION_BEFORE_OPEN and RECITED since TODO items 72 and 73, GAP_AS_FACT and
  UNKNOWN_UNTIED since item 85, QUOTES_ONLY, UNCONFIRMED_FACT, CONDITION_MISSED, CONDITION_WRONG,
  OPEN_CLOSED, CASE_MISREAD, ONE_SIDED, CHOICE_MADE, OVERCLAIM, LAW_UNSOURCED, DATE_MADE, ID, and the quoting
  and letter categories). A run with signs that the gateway failed
  (the driver's timeout, an empty answer where JSON was expected, or two unrecovered empty turns in a row) is
  marked `gateway_trouble` and counted apart. Writes `runs/` (screens),
  `runs.json`, `transcripts/` (each run as text marking who produced each part), `scores.json`, and
  `summary.json`, and prints a table per scenario. A scenario's lease is the PDF its `start` names, resolved in
  the scored copy of the project; `run` stops before any session when one is missing ("run python
  dev/build_test_leases.py first"). The eval scenarios are `dev/scenarios/eval_*.json`, each with the lease of
  its story from `dev/leases/` (TODO item 60):
  one realistic lay-tenant story per playbook (`deposit_ghosted`, `claim_carpet`, `entry_shower`,
  `lease_end_renewal`, `nonpayment_taped`, `violation_dog`, `rent_hike_duplex`, `repair_mold_apt`,
  `leave_early_family`, and `noise_neighbors` since neighbor_disturbance was added; it was `nc_noise`), two
  stories no playbook covers (`nc_roommate`, `nc_towing`, each expecting its lease clause at the stop), one
  covered problem next to an uncovered one (`nc_mixed_heater`), and three with facts like a case in the wiki
  and plain questions about judges (`cases_late_claim`, `cases_3day_cash`, `cases_retaliation`), and the
  author's AC story of 2026-10-04 (`repair_ac_terminate`: asked how to end the lease, the answer must say it is
  not settled; TODO items 72 and 73), and six stories of what the tool knows (TODO item 85), one per state, each
  where the deciding point is in that state: `know_deposit_unsure` (a fact the tenant has not given: whether a notice
  of a claim came, skipped on the sheet), `know_lease_holdover` (lease clauses the profile does not hold but the
  lease has: the holdover, 2.4, and the late charge, 3.3; `search_lease` must be called and each cited),
  `know_violation_waterbed` (a lease with no such clause: the search finds nothing on waterbeds),
  `know_repair_mold_code` (a local code: mold, not the structure or the plumbing, so the duty turns on a code or the
  lease's clause, each the tenant's to check), `know_violation_guest` (an open question: whether a guest staying over is
  a violation the tenant should be given a chance to cure), and `know_nonpayment_orange` (outside the tool: a 3-day
  notice in Orange County, which has no court calendar), and three stories of the student simulation of 2026-10-06
  with the students' own lines, each with sheet rules for the questions before and after the sheet asked plain facts
  (2026-10-08, TODO items 86 and 90 to 92), so the same file runs on either code: `student_notice_email` (an e-mail
  saying "I'm going to have to move out": no reply may say the notice steps are done or that it counts), `student_hot_water`
  (no reply may call withholding open), `student_roommate` (no reply may call the repair options closed); run with
  `WIKI_UNVERIFIED=1` until pages are verified. Each scenario's `about` says what it tests.
- `streamlit run app.py`: the web page (see `app.py` in Modules), on http://localhost:8501 only. The same
  model calls as `run.py`. Stop it with Ctrl-C in its terminal.
- `python run.py`: interactive. Asks new or existing. A new matter reads the lease (one extraction call) and saves the
  description (`intake`, no model). An existing matter asks what is new: an update is logged (`resume`, no model).
  Then the chat starts at once, and the description or the update is the first message: the model answers it,
  loading skills and proposing facts, and the confirmation (`sheet.run_sheet`, no model) asks the tenant to confirm what it proposed.
  An empty line or `bye` exits. There are no chat commands since TODO item 111 (`timeline`, `issues`, and `drop`
  are gone; the web page draws the timeline). Every run appends to the matter's `events.jsonl`.
