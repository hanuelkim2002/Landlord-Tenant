# Landlord-Tenant tool

A Florida landlord-tenant dispute tool (Fla. Stat. ch. 83, pt. II) for a tenant in college housing. It
applies the stored statute and cases to the tenant's confirmed facts (decided 2026-10-02; in development, on
test matters only, see README), says first whether an option is open before its steps, cites the law and
prints the cited words by code instead of reciting them, knows what it knows and says how each unknown changes
what the tenant can do (all 2026-10-04; since 2026-10-12 the model does this by applying the loaded skill, where code
decided it from the playbooks before), never sends anything, and never computes a date in the model. The author
is a law student, not admitted.

## Read these first

- README.md: the fixed plan. Purpose, four goals, three parts, non-negotiables. Do not edit unless the
  project's purpose or architecture changes.
- DOCUMENTATION.md: how the code works now. Read this instead of every module. Keep it current.
- TODO.md: the work Claude Code can do, in priority order (Now, Next, Later). Do the top of Now unless told otherwise.
- AUTHOR.md: what only the author can do: decisions, legal sign-offs, research, open questions.
- SLIPS.md: the mistake log, model slips seen in live runs, counted per eval.
- CHANGELOG.md: what changed and what it replaced. Add an entry for every change.

## Duties on every change

1. Make the one change asked for. Nothing else.
2. Run the offline checks (see DOCUMENTATION.md, Running and testing). Skill checks and the
   named smoke checks must all be OK. A change to code that writes to a matter gets a check in `smoke_parts/` (run by `smoke.py`).
3. Add a CHANGELOG.md entry saying what was added and what it replaced.
4. Update DOCUMENTATION.md if a function, tool, file, event kind, or rule changed.
5. Move the finished TODO.md item to the changelog.
6. Log what the change or an eval finds by TODO.md's rules (the author's decision of 2026-10-09): work Claude Code can
   do in TODO.md, at most about four lines with a link to the record instead of eval history; what needs the author in
   AUTHOR.md; a model slip in SLIPS.md, never TODO.md unless it has a code-side fix. A finding seen again updates its
   entry's count; it is never a new item. A finding fixed in the same change goes only in the CHANGELOG.

## Conventions

- Shared state lives in `record.py`. Other modules do `import record` and use `record.matter`,
  `record.profile`. Never `from record import matter`; the objects get replaced when a matter is loaded.
- Adding a tool: one `@tool` function in `tools.py` with a docstring written to the model, then add it to
  the `tools` list at the bottom of that file. `python schemas.py` shows what the model sees.
- `matter.json` is current state only. `events.jsonl` is the only history, append-only.
- `record.confirm_fact` is the only door into `matter["facts"]`, and only the confirmation (`sheet.save_answer`, shown
  after a turn in which the model proposed facts) calls it. The model can only propose (`propose_facts`). Skills work
  the same way: `record.add_skill`, called only by the `load_skill` tool, is the only door into `matter["skills"]`, and
  logs a `skill_loaded` event. Nothing is deleted from the history. `compute_deadlines` is the only date arithmetic.
- The model asks in the chat only for plain facts, what the tenant saw, did, or holds (what happened, when, how something
  was sent, who did it, a paper's own words), never whether something meets a term of the statute or the lease; each
  skill's "What to find out" says so (2026-10-08). The confirmation asks only to confirm what the tenant said, never for a
  fact the record lacks (2026-10-12).
- Every quote (lease, statute, tenant's words) is checked by substring against its source before use.
- Letters are a code template (`build_letter`). The timeline is printed by the chat loop, never by the model.

## Guardrails

- `calendars/` is read-only too: each court holiday comes from the circuit's official memorandum (PDF kept in
  `calendars/sources/`) and is checked against it by `smoke.py`. Never add or change a holiday from memory.
- `cases/` is read-only too: one file per opinion, the court's text only, built by `dev/build_cases.py` from
  the author's Westlaw print (or by `dev/build_case_pdf.py` from a reporter PDF, for an opinion listed there) with Westlaw's own material (headnotes, synopsis, KeyCite, negative treatment)
  left out, and checked by `smoke.py`. Never edit a case file by hand, and never write a case's words, cite,
  or holding from memory.
- `wiki/` pages are written from `cases/` and `statutes/` only, following `wiki/SCHEMA.md`: the court's and the
  statute's words only as sourced quotes, prose that never states the law. After any edit, run
  `python wiki.py index` and `python wiki.py check`; no problem may remain. Never fill in a page's
  `verified_by`; only the author signs off, with `python wiki.py verify`.
- `statutes/` is a read-only corpus. Never edit it. Never write statutory text, a section number, or a
  deadline into a skill, a rule, or a reply from memory. Cite into `statutes/` or say it needs checking.
- After any edit to a skill in `skills/`, run the skill checks (`skills.check_all_skills`, also run by `smoke.py`)
  and every line must be OK. They check quotes in the prose too, not only in the header's clocks.
- `matters/` and `.env` hold private data. Never print them in full, never commit them.
- `run.py` and `app.py` are interactive and call the UF gateway. `smoke_online.py` calls the model for the first turn
  on a description, on a situation no skill covers, and on an update (resume). Everything else, including `smoke.py`, runs without the key.
- Smoke runs write only to scratch matters under `matters/t-smoke*`, which they remove; never to `t-test`.

## How to work with the author

- Build collaboratively, one change at a time. Do not run ahead autonomously.
- Fix the cause, not the instance (the author's rule, 2026-10-06). A TODO item usually comes from one example (an AC,
  a portal request, one story). Before changing anything, name the underlying issue the example shows, find its other
  instances across the skills, the prompt, and the code, and propose a fix for the issue as a whole; a fix fitted
  to the example alone is not done. That fix is the one change. Its CHANGELOG entry names the underlying issue and the
  instances it covers.
- Push back on architecture choices you think are wrong.
- Simple code, one convention, no clever tricks. Explain line by line when asked.
- Refer to code by module and function name.
- No em dashes in drafted writing.

## Running

    bash setup.sh            # once: venv, pip install, .env from template, matters/
    source venv/bin/activate
    python dev/build_cases.py "<Westlaw print>"   # once: cases/ from the author's Westlaw Find and Print file
    python wiki.py check     # the case wiki's checks; also index, and verify "<page>" "<name>" for the author
    python run.py            # new matter (lease, intake) or existing (what is new, resume), then chat; the sheet follows a turn that proposed facts
    streamlit run app.py     # the same as a web page on this computer: http://localhost:8501
    python smoke.py          # offline checks, no key needed
    python smoke_online.py   # the first turn on a description, none covered, resume; calls the model
    python schemas.py        # what the model sees per tool
    python dev/live_run.py dev/scenarios/nonpayment_3day.json   # a scripted live session; calls the model

Chat command: `bye` (the only one left in the terminal, which TODO item 115 removes).
