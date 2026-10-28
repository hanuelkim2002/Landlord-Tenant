# How v2 works

A line or two on every module and function. The plan is README.md; what changed is CHANGELOG.md.

## A message, start to finish

The tenant writes on the page (`app.py`). `chat.reply` records the message, builds the system prompt (the rules, the
whole lease, the facts, the timeline, the skills), and runs the tool loop with the model. The model may load a skill,
read or search the statute, note a fact, save a line of the timeline, or count days. `checks.check_reply` checks the reply's quotations and finds the cited words,
and the reply and its checks are recorded in the matter's history and shown on the page.

## Modules

### config.py

Paths (`STATUTES`, `SKILLS`, `MATTERS`) and the three gateways (`GATEWAYS`: `uf`, `openrouter`, and `anthropic`,
Anthropic's OpenAI-compatible endpoint). The chat: `GATEWAY` (default `anthropic`) and `AGENT_MODEL` (default Claude
Sonnet 5.5). The lease reader: `READER_GATEWAY` (default `anthropic`) and `VISION_MODEL` (default Claude Haiku 5.5).
Each can be set in the environment.

- `temperature(gateway)`: temperature 0 on UF, nothing elsewhere, since Claude rejects it.
- `client(gateway)`: a gateway (the chat's if none is named), with its key (`UF_API_KEY`, `OPENROUTER_API_KEY`, or `ANTHROPIC_API_KEY`)
  from `.env` or the environment.

### law.py

The statutes in `statutes/`, the skills in `skills/`, and the skill quote checker. `python law.py` checks every skill.

- `squash(text)`: spacing, line breaks, quote marks, and hyphens made uniform, so only words are compared.
- `section_text(section)`: one section's full text. `section_titles()`: each section's title, from `index.json`.
- `search_statute(phrase)`: the sections holding a phrase, with the words around it.
- `parts_of(text)`: a section cut into subsections and paragraphs, `(3)` and `(3)(a)`, in order.
- `cited_text(cite)`: the words a cite like `83.49(3)(a)` points to, without the history note.
- `read_skill(path)`, `skills()`: a skill's name, description, and body; every skill by name.
- `check_quotes(text)`: each quote followed by a cite, and whether it is word for word in that part.
- `check_all_skills()`: prints a line per skill; true if every quote in every skill checks out.

### record.py

A matter is a folder `matters/<tenant>/<matter>/` holding `lease.pdf`, `lease_pages.json`, `matter.json` (the current
state: description, loaded skills, pending and confirmed facts, the timeline's lines), and `events.jsonl` (the
history, only added to).

- `now()`, `folder(m)`, `save(m)`, `log(m, kind, **data)`: the time; the folder; write the state; add an event.
- `new_matter(tenant, description)`, `load(tenant, matter)`, `saved_matters()`: start, open, and list matters.
- `events(m)`, `add_message(m, role, text, checks)`, `chat(m)`: the history; record a message; the chat so far.
- `add_skill(m, name)`: mark a skill loaded.
- `note_fact(m, name, value, tenant_words)`: a pending fact. `confirm_fact(m, name, value)`: the only way a fact is
  confirmed, with the value as noted or corrected. `confirmed_facts(m)`: name to value.
- `save_line(m, number, date, what, open)`: one line of the timeline. Number 0 adds a line; a line's number saves
  a new version of it. Every version goes to the history.
- `since_last_visit(m, today)`: after a gap of a day or more, the days since the last message (calendar days,
  counted by code) and the facts confirmed since then; None on the same day or before any message.

Events: `matter_opened`, `lease_read`, `message`, `skill_loaded`, `fact_noted`, `fact_confirmed`, `line_saved`.

### lease.py

Every page is read from its image by the vision model (`comparisons/models/`), 16 pages at once (`PAGES_AT_ONCE`,
`comparisons/intake/`), and the whole lease goes into the prompt (method A, `comparisons/lease/`).

- `read_image(gateway, page)`: a page's text read from its image by the vision model (`[X]` for a checked box).
- `read_page(gateway, pdf_path, number)`: one page read from its image. It opens its own copy of the PDF, since
  PyMuPDF is not built for threads; Python lets one thread into PyMuPDF at a time, so only the waits for the model
  overlap.
- `read_lease(m, pdf_path)`: store the PDF and read every page, 16 at once, kept in page order.
- `lease_pages(m)`, `lease_text(pages)`: the stored pages; the lease for the prompt, with page markers.

### checks.py

Shown under each reply; the reply is never blocked.

- `quote_parts(quote)`, `found_in(parts, text)`: a quotation's words, cut at an ellipsis or a bracketed change.
- `QUOTE`: a quotation of 20+ characters. Its opening mark must follow the start, a space, a bracket, or a bold mark,
  and its closing mark must not be followed by a letter or digit, so the words between two quotations are not one.
- `nearby_cites(reply, match)`: the statute cites next to a quotation: the first just after it, the last just before.
- `check_quote(reply, match, lease)`: where a quotation is word for word: a section cited next to it, or the lease.
- `lease_passage(lease, number)`: the lease's paragraph that starts with a section number.
- `cited_words(reply, pages)`: the words each statute or lease cite points to. `check_reply(reply, pages)`: both.

### tools.py

The six tools the model can call, their descriptions (`SCHEMAS`), and `run_tool(m, name, arguments)`.

- `get_statute_section`, `search_statute`: the statute, in full or by phrase.
- `load_skill`: loads a skill for the matter and returns its instructions.
- `count_days(m, fact, days)`: the only date math for deadlines: a confirmed date plus the days, and whether it has
  passed today, in calendar days, the start day not counted, no weekend or holiday shift (an assumption, said in every
  result).
- `note_fact`: saves a pending fact for the tenant to confirm.
- `save_line(m, number, date, what, open)`: saves a line of the timeline. "today" as the date becomes today's
  date, by code (`today()`); `open` counts as true only for true or the word "true". The reply ends with the
  lines still open (`open_lines_text(m)`), so the model can close one the news settles.

### chat.py

- `RULES`: the system prompt's rules (README.md, 703 words). Rule 9 keeps the timeline; rule 10 says how to pick
  up after a gap; rule 8 ends the short answer with its question. "Writing the reply" asks for the short answer, a
  `DETAILS` line, and a `###` question heading per point, in plain words.
- `facts_text`, `timeline_text(lines)`, `since_text(since)`, `system_prompt(m, pages)`: the prompt, built fresh for
  each message. After the facts: TIMELINE, and SINCE LAST VISIT when the last message was on an earlier day.
- `split_reply(text)`: a reply's short part and its points, [(title, body)]. It cuts at the first line holding only
  `DETAILS` (any case, maybe bold or with a colon); each `#` heading under it starts a point; text before the first
  heading becomes the point titled `WHY`; a point with nothing in it is dropped. No marker: the whole reply, no points.
- `text_tool_calls(content)`: tool calls the model wrote as text; they are run like real ones.
- `run_loop(m, messages)`: the tool loop; after 8 rounds the model is asked to answer with tools off.
- `reply(m, text)`: one message in, one checked reply out, both recorded.

### app.py

The page: `choose_matter` (open a saved matter, or start one from a lease PDF and a description, whose first reply
answers the description), `confirm_facts` (pending facts with a box to correct and a Confirm button; the confirmed
ones), `show_timeline` (the timeline's lines, to read only, the open ones marked), `show_reply` (a reply's short
answer, then one click-to-open box per point, from `chat.split_reply`), `show_checks` (the quote checks and cited
words under a reply). `safe` keeps a "$" from starting a formula, in box titles too.

### tests.py

No model call: the quote checker, the skill quote checker, `count_days`, the timeline (lines, since last visit,
`save_line`, the prompt's two blocks), in a throwaway matters folder, `split_reply`, and `read_lease` with a stand-in
reader (pages kept in order, 16 at once). Every line should say OK.

## Running and testing

From `v2/`: `bash setup.sh` once; `python tests.py`; `python law.py` after a skill edit; `streamlit run app.py` for the
page at http://localhost:8501. The app's preview attaches to that page; it cannot start it itself, since macOS does
not let the preview's launcher read the Documents folder.

## Elsewhere in v2

`statutes/` (read-only), `skills/` (one file per situation, format A), `comparisons/` (the lease, skills, model,
deposit skill, plain replies, and intake speed tests, the memory tests, their answer keys, and scores),
`docs/superpowers/` (the memory's spec and plan), `matters/` (private, not in git), `V2_PROMPT.md` (how v2 started).
