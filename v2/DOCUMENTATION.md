# How v2 works

A line or two on every module and function. The plan is README.md; what changed is CHANGELOG.md.

## A message, start to finish

The tenant writes on the page (`app.py`). `chat.reply` records the message, builds the system prompt (the rules, the
whole lease, the facts, the skills), and runs the tool loop with the model. The model may load a skill, read or search
the statute, note a fact, or count days. `checks.check_reply` checks the reply's quotations and finds the cited words,
and the reply and its checks are recorded in the matter's history and shown on the page.

## Modules

### config.py

Paths (`STATUTES`, `SKILLS`, `MATTERS`) and the two gateways (`GATEWAYS`: `uf` and `openrouter`). The chat:
`GATEWAY` (default `openrouter`) and `AGENT_MODEL` (default Gemini 3.8 Flash). The lease reader: `READER_GATEWAY` (default
`openrouter`) and `VISION_MODEL` (default Claude Haiku 5.5). Each can be set in the environment.

- `temperature(gateway)`: temperature 0 on UF, nothing on OpenRouter, where Claude rejects it.
- `client(gateway)`: a gateway (the chat's if none is named), with its key (`UF_API_KEY` or `OPENROUTER_API_KEY`)
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
state: description, loaded skills, pending and confirmed facts), and `events.jsonl` (the history, only added to).

- `now()`, `folder(m)`, `save(m)`, `log(m, kind, **data)`: the time; the folder; write the state; add an event.
- `new_matter(tenant, description)`, `load(tenant, matter)`, `saved_matters()`: start, open, and list matters.
- `events(m)`, `add_message(m, role, text, checks)`, `chat(m)`: the history; record a message; the chat so far.
- `add_skill(m, name)`: mark a skill loaded.
- `note_fact(m, name, value, tenant_words)`: a pending fact. `confirm_fact(m, name, value)`: the only way a fact is
  confirmed, with the value as noted or corrected. `confirmed_facts(m)`: name to value.

Events: `matter_opened`, `lease_read`, `message`, `skill_loaded`, `fact_noted`, `fact_confirmed`.

### lease.py

Every page is read from its image by the vision model (`comparisons/models/`), and the whole lease goes into the
prompt (method A, `comparisons/lease/`).

- `read_image(gateway, page)`: a page's text read from its image by the vision model (`[X]` for a checked box).
- `read_lease(m, pdf_path)`: store the PDF and read every page from its image, one at a time.
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

The five tools the model can call, their descriptions (`SCHEMAS`), and `run_tool(m, name, arguments)`.

- `get_statute_section`, `search_statute`: the statute, in full or by phrase.
- `load_skill`: loads a skill for the matter and returns its instructions.
- `count_days(m, fact, days)`: the only date math: a confirmed date plus the days, and whether it has passed today,
  in calendar days, the start day not counted, no weekend or holiday shift (an assumption, said in every result).
- `note_fact`: saves a pending fact for the tenant to confirm.

### chat.py

- `RULES`: the system prompt's rules (README.md, 390 words).
- `facts_text`, `system_prompt(m, pages)`: the prompt, built fresh for each message.
- `text_tool_calls(content)`: tool calls the model wrote as text; they are run like real ones.
- `run_loop(m, messages)`: the tool loop; after 8 rounds the model is asked to answer with tools off.
- `reply(m, text)`: one message in, one checked reply out, both recorded.

### app.py

The page: `choose_matter` (open a saved matter, or start one from a lease PDF and a description, whose first reply
answers the description), `confirm_facts` (pending facts with a box to correct and a Confirm button; the confirmed
ones), `show_checks` (the quote checks and cited words under a reply). `safe` keeps a "$" from starting a formula.

### tests.py

No model call: the quote checker, the skill quote checker, and `count_days`. Every line should say OK.

## Running and testing

From `v2/`: `bash setup.sh` once; `python tests.py`; `python law.py` after a skill edit; `streamlit run app.py` for the
page at http://localhost:8501. The app's preview attaches to that page; it cannot start it itself, since macOS does
not let the preview's launcher read the Documents folder.

## Elsewhere in v2

`statutes/` (read-only), `skills/` (one file per situation, format A), `comparisons/` (the lease and skills tests,
their answer keys, and scores), `matters/` (private, not in git), `V2_PROMPT.md` (how v2 started).
