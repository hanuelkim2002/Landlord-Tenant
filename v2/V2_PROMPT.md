I'm starting v2 of my Florida landlord-tenant tool, in this repo. I'm a law student (not admitted) and a beginning
coder. The code here now is v1. It grew too complex: about 3,500 lines of app code, 2,800 lines of tests, 60,000 words
of project docs, and a case wiki no tenant ever sees. v2 keeps the core and nothing else. v1 moves into `v1/` (see
First steps) and stays there to read. Start with `v1/README.md` for background, but don't port v1's code wholesale.
Reuse a v1 function only if it stays short and clear.

All of v2 lives in `v2/`. Every v2 path in this prompt (`statutes/`, `skills/`, `comparisons/`, `matters/`,
`config.py`, `tests.py`, the docs) is inside `v2/`, and v2's commands run from there.

## What the tool does

A tenant in Florida college housing describes a dispute with their landlord (Fla. Stat. ch. 83, part II) and uploads
their lease. In a chat, the tool applies the statute and the lease to the tenant's facts, counts the statutory deadlines
in code, and keeps a record of the matter. It is in development and runs on test matters only. No real tenant uses it
until the unlicensed-practice question is settled.

## How the model answers (the rules in the system prompt)

Keep the rules short, under about 400 words. Add a rule only when I ask for one.

1. Apply the law to the tenant's facts and give an answer, not a list of quotes.
2. Answer what was asked first. When asked "can I ...", say whether they can before giving any step.
3. Know what you know. Each point the answer turns on is one of these: known (a confirmed fact, a lease clause you read,
   the statute), something the tenant can tell you, something they must check, unsettled, or outside the tool. Never
   state a gap as a fact, and never assume a fact you haven't been given. Say how an unknown would change the answer.
4. An open question stays open: give the reading on each side.
5. Ask the tenant only plain facts (what happened, when, how something was sent, what a paper says). Never ask whether
   something meets a legal term.
6. Cite each rule to its source: a statute section and subsection, or the lease.
7. Dates come only from `count_days`. Never add, subtract, or compare dates yourself.
8. End with the one question your answer needs, if any. Don't offer help the tenant didn't ask for, and never repeat
   an offer.

## What v2 keeps

- **Stored law.** `statutes/`: v1's 40 `.txt` files and `index.json`, copied from `v1/statutes/`; read-only. `skills/`: one file per
  situation, rewritten for v2 (see "Skills: an open question" below). The model sees each skill's name and
  description and loads the ones that fit.
- **Skill quote checker.** Every quotation in a skill must be word for word in the statute subsection it cites. Run it after any skill edit.
- **The lease.** The tenant uploads a PDF. How the tool reads it is still open (see "Lease intake: an open question"
  below).
- **Six tools the model can call:** `get_statute_section`, `search_statute`, `search_lease`, `load_skill`,
  `count_days`, and `note_fact` (both new, described next). `search_lease` may change with the lease method.
- **Facts.** `note_fact(name, value, tenant_words)` saves what the tenant said as a pending fact. The web page lists
  pending facts in the sidebar, each with a Confirm button and a way to correct the value. Only confirmed facts count. A
  date is written YYYY-MM-DD.
- **Dates.** `count_days(fact, days)` is the only date math in the code, about 15 lines with Python's `datetime`. It
  reads the confirmed date of `fact` (or says the fact isn't confirmed yet), adds `days` (negative for a deadline
  before the date), and returns the date and whether it has passed, compared with today. It counts calendar days, the
  start day not counted, with no weekend or holiday shift. That counting is an assumption nobody has checked yet
  (`v1/AUTHOR.md`, item 3), so the result says so. The skill tells the model which fact and how many days.
- **Checks under each reply.** The tenant sees the results; the reply is never blocked. Every quotation of 20 or more
  characters is word for word in the section it cites, or in the lease. Below the reply, the program prints the words each cite points to (the statute
  subsection, or the lease passage).
- **Record.** `matters/<tenant id>/<matter id>/` holds the lease PDF and what the tool reads from it, `matter.json` (current state:
  the description, the loaded skills, pending and confirmed facts), and `events.jsonl` (the history, append-only, never
  edited or deleted). Log the chat's messages as events too, so a saved matter reopens with its chat.
- **Web page.** One Streamlit page, on this computer only (localhost). It starts a new matter (lease PDF and
  description) or opens a saved one, runs the chat, and shows the pending facts to confirm.
- **Project docs.** README.md (the fixed plan), CLAUDE.md (how to work here), DOCUMENTATION.md (how the code works now),
  CHANGELOG.md, TODO.md (work Claude can do), AUTHOR.md (my decisions and sign-offs), SLIPS.md (model mistakes seen in
  live runs).
- **One test file.** `tests.py`, about 100 lines, with no model call, run with `python tests.py`. It covers the quote
  checker, the skill quote checker, and a few `count_days` cases.

## Comparing methods

Two parts of v2 are open questions: how to read the lease, and how to write a skill. Settle each by testing a few
methods side by side, lease first (it is easy to score by code and doesn't depend on the skills), then skills.

1. **Shortlist.** Research the methods listed for the question below and pick the 2 or 3 most promising, with
   sources. Show me the shortlist.
2. **Write the test before any build.** You write the test material and its answer key, in `comparisons/lease/` and
   `comparisons/skills/`. I review both and give my OK before anything is built.
   - Lease: write 3 or 4 test leases that differ the way real ones do: numbered sections and unnumbered headings, short
     and long (one of 40 pages or more), and one saved as page images with no text, as a scanned lease would be. Add
     v1's sample lease (`lease.pdf`). For each lease, write about 10 questions with the clause that answers each (late
     fee, pets, where notices go, repairs), plus a few the lease doesn't answer.
   - Skills: about 5 deposit stories, each with the right answer under the statute, citing the sections in `statutes/`.
3. **Build throwaway prototypes in parallel.** One agent per method, each in its own git worktree. Each builds a small
   script, not the app. All use the same test and the same model, nemotron (`nemotron-3-super-120b-a12b`), so the method
   is the only difference.
4. **Score.** By code where possible: did it find the right clause, did it ever call the lease silent when it isn't, do
   its quotes check out, how long did it take? For skills, show me the answers side by side with the method names
   hidden, and I judge them.
5. **Choose.** Give me the scores and a recommendation, and wait for my choice. Keep the test material, the answer
   key, and the scores in `comparisons/`, so the chosen method can be checked again later. Delete the prototype code,
   then build the winner properly in v2.

Each agent costs about a session's worth of tokens, so use at most three per question.

## Lease intake: an open question

I'm not sure v1's method is the right one. v1 read the PDF's text with PyPDF2, had a model extract four clauses, and
gave the chat model a phrase search over the rest. It was slow on long leases (about four minutes for 57 pages),
failed on a PDF whose text PyPDF2 could not decode, and the model sometimes said the lease was silent on a point it
covered.

- Methods to consider: the whole lease text in the prompt; the lease split into numbered clauses, with a list of clause
  titles in the prompt and a tool to read a clause; a phrase search like v1's; a model summary of key clauses; a model
  reading page images, for scanned leases. Also compare PDF text readers (PyPDF2, pypdf, pdfminer, PyMuPDF).
- Judge each on four questions: does the model find what the lease says on a point, and never call it silent when it
  isn't? Can every lease quote be checked word for word against the stored text? How fast is it on a long lease? Does
  it handle a badly made or scanned PDF?
- The lease method decides `lease.py`, the lease tool, and how lease quotes are checked, so settle it before writing
  that code.
- Once I choose the method, write the rules on reading the lease for the system prompt (for example, search the lease
  before saying it does or doesn't cover a point) and show them to me.

## Skills: an open question

v1's 10 skills (about 28,500 words) were converted from the old YAML playbooks. In v1's last eval, mistakes per reply
rose after the switch to them (`v1/docs/evals/2026-10-12-skills/`). v2 rewrites them, starting with one issue.

- Methods to consider: Anthropic's Agent Skills format (a SKILL.md with a short header, plus files read only when
  needed); an element checklist (each condition of an option, in order); a decision tree; worked examples; v1's current
  skills.
- Judge each on four questions: does the model apply each condition to the facts correctly? Does it answer first? Does
  the skill stay short? Can I check every quote against `statutes/`?
- After I choose: rewrite `deposit_not_returned` (the deposit was not returned) in that method, using v1's skill
  (`v1/skills/deposit_not_returned.md`) and the statute sections it rests on as the source of its legal content. Its deadlines are stated in plain words (which fact, how many days). Build v2 around
  that one skill first, and rewrite the other skills only after I've tried it and approved the method.
- The skill format decides how the skill quote checker reads a skill, so settle it before writing that code.

## What v2 leaves out (don't add these back unless I ask)

The cite checker (maybe later); v1's deadline engine and the typed deadline clocks in skills (maybe later, if the
model often picks the wrong fact or number of days); case opinions and the case wiki; court holiday calendars and court business days; letters; logging messages and files (`add_communication`, `add_artifact`); the `propose_facts` tool and the
confirmation form; the automatic reply after confirming; case checks; deadlines printed automatically when the tenant
asks "when"; empty-reply retries; rules that switch on and off; "which deadlines passed" in the prompt; session
transcripts; the timeline table; old-format migration; the record side panel; the visit runner; smoke and online tests;
v1's eval scoring and its 35 scripted stories (the comparison tests above are separate); the "not a lawyer's advice"
footer.

## Structure

- Python, with no LangChain. The UF gateway is OpenAI-compatible (`https://api.ai.it.ufl.edu`, key `UF_API_KEY` in
  `.env`), so use the `openai` package and a plain tool loop: send the messages, run any tool calls, send the results
  back, and repeat until the model answers.
- The model name lives in one place in `config.py`, read from `AGENT_MODEL` in the environment, with
  `nemotron-3-super-120b-a12b` as the default. I'll pick the model later.
- A few modules, each with one job. Here is a starting point; propose a simpler split if you see one:
  - `config.py`: paths, the key, the model.
  - `record.py`: matter folders, `matter.json`, `events.jsonl`, facts. It is the only code that confirms a fact.
  - `lease.py`: reading the lease, by the method I choose.
  - `law.py`: loads the statutes and skills; the skill quote checker.
  - `checks.py`: the quote check, and the printed cited words.
  - `tools.py`: the six tools, `count_days` among them.
  - `chat.py`: the system prompt and the tool loop.
  - `app.py`: the web page.
  - `tests.py`.
- Aim for under about 1,000 lines of app code in all. If something pushes past that, stop and tell me why.

## How to talk with me

- Be concise and simple, so I can follow. Short sentences, plain words, no jargon unless you explain it.
- Lead with what matters: what you did, what you found, or what you need from me.
- Put this in CLAUDE.md so every session follows it.

## How to write the code

- I want to read the code and understand it. Use plain names and short functions.
- Each module opens with two or three lines saying what it is for. Each function gets a one-line docstring. Comments
  say why, in plain words.
- Include only the safety checks listed above. When the model makes a mistake in a live run, log it in SLIPS.md. Don't
  add a guard for it unless I decide to.
- Keep the docs short. DOCUMENTATION.md covers every module and function in a line or two each. A CHANGELOG entry is at
  most about five lines (what changed and what it replaced). A TODO.md item is at most three lines.
- No em dashes in anything you write.

## Guardrails

- `statutes/` is read-only. Never write statute text, a section number, or a deadline from memory into a skill, a rule,
  or a reply.
- `v1/` is there to read. Never edit it.
- Build a rewritten skill from v1's skill and the sections of `statutes/` it rests on. Read those sections, and quote
  them where a point turns on their words. Show me anything the new skill says about the law that v1's did not. Run
  the skill quote checker after every skill edit.
- `matters/` and `.env` hold private data. Never print them in full and never commit them. The top-level `.gitignore`
  must cover them in `v2/` too, along with `venv/` and `lease.pdf`.

## First steps

1. Move v1 into `v1/` with `git mv`, so git keeps each file's history. Move every tracked file and folder except
   `.claude/` (the app's settings) and `.gitignore`, which stay at the top. Rename `v1/CLAUDE.md` to
   `v1/CLAUDE_v1.md`, so v1's working rules don't load into v2 sessions.
2. Make `v2/`. Copy `v1/statutes/*.txt` and `v1/statutes/index.json` into `v2/statutes/`, and `v1/.env.example` and
   `v1/.streamlit/config.toml` into `v2/`. Don't copy v1's skills; read them in `v1/skills/`. Save this prompt as
   `v2/V2_PROMPT.md`, as a record of how v2 started.
3. At the top of the repo, keep only `v1/`, `v2/`, `.claude/`, `.gitignore`, and two short files:
   - `README.md`: three lines saying `v1/` is the old version, kept to read, and `v2/` is the current one.
   - `CLAUDE.md`: the same, plus the line `@v2/CLAUDE.md`, so every session loads v2's working rules.
   Update `.claude/launch.json` so the app's preview runs v2's page.
4. Some files aren't in git, so they live only in my main checkout
   (`/Users/hanuelkim/Documents/ALL_CLAUDE_FILES/Landlord-Tenant/Landlord-Tenant ClaudeCode/`), not in your worktree:
   `.env`, `lease.pdf`, `matters/`, `venv/`, and v1's test leases in `dev/leases/`. Read the leases from there. Don't
   move these yourself. Once your change is merged, tell me what to move: v1's `matters/` into `v1/matters/` (so its
   test matters don't mix with v2's), and `.env` and `lease.pdf` into `v2/`.
5. Write v2's short README.md and CLAUDE.md in `v2/` from this prompt and show them to me.
6. Run the comparison for lease intake (see "Comparing methods") and wait for my choice.
7. Run the comparison for skills and wait for my choice.
8. Propose the build order, with the one rewritten skill and the chosen lease method, and wait for my OK. Once I approve it, build it all the way
   through without stopping between steps. Then run `python tests.py` and show me the result on the web page.
