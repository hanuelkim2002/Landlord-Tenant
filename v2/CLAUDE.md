# Working on v2

How to work here. The plan is README.md. v1 is in `../v1/`, to read only.

## The author

A law student (not admitted) and a beginning coder, building this to learn and to test the idea.

## How to talk with the author

- Be concise and simple. Short sentences, plain words, no jargon unless you explain it.
- Lead with what matters: what you did, what you found, or what you need.
- Pause for the author's OK where a step says to. Once a plan is approved, do all of it without stopping between steps.
- Push back when you think a choice is wrong.

## Read these first

- README.md: the fixed plan.
- DOCUMENTATION.md: how the code works now, a line or two per module and function.
- TODO.md: work Claude can do, in order. AUTHOR.md: the author's decisions and sign-offs. SLIPS.md: model mistakes
  seen in live runs.
- CHANGELOG.md: what changed.

## On every change

1. Make the one change asked for.
2. Run `python tests.py`. It must pass.
3. Add a CHANGELOG.md entry, at most about five lines: what changed and what it replaced.
4. Update DOCUMENTATION.md if a module or function changed.
5. A model mistake seen in a live run goes in SLIPS.md, not in a guard, unless the author decides to add one.

## How to write the code

- The author reads the code. Plain names, short functions, no clever tricks.
- Each module opens with two or three lines saying what it is for. Each function gets a one-line docstring.
  Comments say why, in plain words.
- Include only the safety checks README.md lists.
- Keep the docs short. A TODO.md item is at most three lines.
- Reuse a v1 function only if it stays short and clear.
- Under about 1,000 lines of app code. If something pushes past that, stop and say why.
- No em dashes in anything you write.

## Guardrails

- `statutes/` is read-only. Never write statute text, a section number, or a deadline from memory into a skill, a
  rule, or a reply. Cite into `statutes/`, or say it needs checking.
- `../v1/` is there to read. Never edit it.
- A rewritten skill is built from v1's skill and the `statutes/` sections it rests on. Quote them where a point turns
  on their words. Show the author anything the new skill says about the law that v1's did not. Run the skill quote
  checker after every skill edit.
- `matters/` and `.env` hold private data. Never print them in full, never commit them.
- The model never computes a date; `count_days` is the only date math.

## Running

Commands run from `v2/`.

    python tests.py          # the checks, no model call
    streamlit run app.py     # the web page, http://localhost:8501
