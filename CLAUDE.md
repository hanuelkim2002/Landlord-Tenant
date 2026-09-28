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
2. Run the offline checks (see DOCUMENTATION.md, Running and testing). Playbook quote checks and the
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
  can only propose (`propose_facts`). `record.add_issues` is the only door into `matter["issues"]`; issues are
  never removed. `compute_deadlines` is the only date arithmetic.
- Every quote (lease, statute, tenant's words) is checked by substring against its source before use.
- Letters are a code template (`build_letter`). The timeline is printed by the chat loop, never by the model.

## Guardrails

- `statutes/` is a read-only corpus. Never edit it. Never write statutory text, a section number, or a
  deadline into a playbook, a rule, or a reply from memory. Cite into `statutes/` or say it needs checking.
- After any edit to a playbook YAML, run the playbook quote check and every line must be OK.
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
    python run.py            # new matter (lease, intake) or existing (what is new, resume), then the sheet, then chat
    python smoke.py          # offline checks, no key needed
    python smoke_online.py   # classify, fill_facts, resume; calls the model
    python schemas.py        # what the model sees per tool

Chat commands: `timeline`, `timeline full`, `timeline <issue>`, `bye`.
