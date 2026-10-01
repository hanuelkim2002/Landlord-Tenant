# Landlord-Tenant tool

A Florida landlord-tenant dispute organizer (Fla. Stat. ch. 83, pt. II) for a tenant in college housing.
It never sends anything, never computes a date in the model, and never advises. The author is a law
student, not admitted.

## Read these first

- README.md: the fixed plan. Purpose, four goals, three parts, non-negotiables. Do not edit unless the
  project's purpose or architecture changes.
- DOCUMENTATION.md: how the code works now. Read this instead of every module. Keep it current.
- TODO.md: the working list, in order. Do the top item unless told otherwise.
- CHANGELOG.md: what changed and what it replaced. Add an entry for every change.

## Duties on every change

1. Make the one change asked for. Nothing else.
2. Run the offline checks (see DOCUMENTATION.md, Running and testing). Playbook checks and the
   named smoke checks must all be OK. A change to code that writes to a matter gets a check in `smoke.py`.
3. Add a CHANGELOG.md entry saying what was added and what it replaced.
4. Update DOCUMENTATION.md if a function, tool, file, event kind, or rule changed.
5. Move the finished TODO.md item to the changelog.

## Conventions

- Shared state lives in `record.py`. Other modules do `import record` and use `record.matter`,
  `record.profile`. Never `from record import matter`; the objects get replaced when a matter is loaded.
- Adding a tool: one `@tool` function in `tools.py` with a docstring written to the model, then add it to
  the `tools` list at the bottom of that file. `python schemas.py` shows what the model sees.
- `matter.json` is current state only. `events.jsonl` is the only history, append-only.
- `record.confirm_fact` is the only door into `matter["facts"]`, and only the intake sheet calls it. The model
  can only propose (`propose_facts`). Issues work the same way: `record.add_issues` only suggests (the
  classifier, a related rule), `record.confirm_issue` (a yes on the sheet) makes one active, and
  `record.reject_issue` logs a no or a drop. Nothing is deleted from the history. `compute_deadlines` is the only date arithmetic.
- Every quote (lease, statute, tenant's words) is checked by substring against its source before use.
- Letters are a code template (`build_letter`). The timeline is printed by the chat loop, never by the model.

## Guardrails

- `calendars/` is read-only too: each court holiday comes from the circuit's official memorandum (PDF kept in
  `calendars/sources/`) and is checked against it by `smoke.py`. Never add or change a holiday from memory.
- `cases/` is read-only too: one file per opinion, the court's text only, built by `dev/build_cases.py` from
  the author's Westlaw print with Westlaw's own material (headnotes, synopsis, KeyCite, negative treatment)
  left out, and checked by `smoke.py`. Never edit a case file by hand, and never write a case's words, cite,
  or holding from memory.
- `wiki/` pages are written from `cases/` and `statutes/` only, following `wiki/SCHEMA.md`: the court's and the
  statute's words only as sourced quotes, prose that never states the law. After any edit, run
  `python wiki.py index` and `python wiki.py check`; no problem may remain. Never fill in a page's
  `verified_by`; only the author signs off, with `python wiki.py verify`.
- `statutes/` is a read-only corpus. Never edit it. Never write statutory text, a section number, or a
  deadline into a playbook, a rule, or a reply from memory. Cite into `statutes/` or say it needs checking.
- After any edit to a playbook YAML, run the playbook checks (`check_all_playbooks`, also run by `smoke.py`)
  and every line must be OK. They check quotes in the prose too, not only in `spec`.
- `matters/` and `.env` hold private data. Never print them in full, never commit them.
- `run.py` is interactive and calls the UF gateway. `smoke_online.py` calls the model for classify,
  fill_facts, and resume. Everything else, including `smoke.py`, runs without the key.
- Smoke runs write only to scratch matters under `matters/t-smoke*`, which they remove; never to `t-test`.

## How to work with the author

- Build collaboratively, one change at a time. Do not run ahead autonomously.
- Push back on architecture choices you think are wrong.
- Simple code, one convention, no clever tricks. Explain line by line when asked.
- Refer to code by module and function name.
- No em dashes in drafted writing.

## Running

    bash setup.sh            # once: venv, pip install, .env from template, matters/
    source venv/bin/activate
    python dev/build_cases.py "<Westlaw print>"   # once: cases/ from the author's Westlaw Find and Print file
    python wiki.py check     # the case wiki's checks; also index, and verify "<page>" "<name>" for the author
    python run.py            # new matter (lease, intake) or existing (what is new, resume), then the sheet, then chat
    python smoke.py          # offline checks, no key needed
    python smoke_online.py   # classify, fill_facts, resume; calls the model
    python schemas.py        # what the model sees per tool
    python dev/live_run.py dev/scenarios/nonpayment_3day.json   # a scripted live session; calls the model

Chat commands: `timeline`, `timeline full`, `timeline <issue>`, `issues`, `drop <issue>`, `bye`.
