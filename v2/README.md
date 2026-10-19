# Landlord-Tenant tool, v2

The fixed plan. It changes only when the purpose or the design changes. How the code works now is in
DOCUMENTATION.md; what changed is in CHANGELOG.md. v2 started from `V2_PROMPT.md` (2026-10-19). v1 is in `../v1/`,
kept to read.

## What the tool does

A tenant in Florida college housing describes a dispute with their landlord (Fla. Stat. ch. 83, part II) and uploads
their lease. In a chat, the tool applies the statute and the lease to the tenant's facts, counts the statutory
deadlines in code, and keeps a record of the matter.

The author is a law student, not admitted. Applying the law to one person's facts is legal advice, so the tool runs on
test matters only. No real tenant uses it until the unlicensed-practice question is settled.

## How the model answers

The system prompt holds these rules, under about 400 words in all. A rule is added only when the author asks.

1. Apply the law to the tenant's facts and give an answer, not a list of quotes.
2. Answer what was asked first. Asked "can I ...", say whether they can before any step.
3. Know what you know. Each point the answer turns on is known (a confirmed fact, a lease clause read, the statute),
   something the tenant can tell, something they must check, unsettled, or outside the tool. Never state a gap as a
   fact or assume a fact not given. Say how an unknown would change the answer.
4. An open question stays open: give the reading on each side.
5. Ask the tenant only plain facts, never whether something meets a legal term.
6. Cite each rule to its source: a statute section and subsection, or the lease.
7. Dates come only from `count_days`.
8. End with the one question the answer needs, if any. No offers the tenant didn't ask for, and none repeated.

## The parts

- **Stored law.** `statutes/` (40 sections and `index.json`, read-only). `skills/`, one file per situation; the model
  sees each skill's name and description and loads the ones that fit.
- **The lease.** The tenant uploads a PDF. How the tool reads it is decided by a comparison (`comparisons/lease/`).
- **Six tools.** `get_statute_section`, `search_statute`, `search_lease`, `load_skill`, `count_days`, `note_fact`.
- **Facts.** `note_fact` saves what the tenant said as a pending fact. The tenant confirms or corrects it on the web
  page. Only confirmed facts count. Dates are written YYYY-MM-DD.
- **Dates.** `count_days(fact, days)` is the only date math: calendar days from a confirmed date, start day not
  counted, no weekend or holiday shift. That counting is not yet checked (`../v1/AUTHOR.md`, item 3), and every result
  says so.
- **Checks under each reply.** Every quotation of 20 characters or more is checked word for word against the section
  it cites, or the lease. Below the reply, the program prints the words each cite points to. The tenant sees the
  results; the reply is never blocked.
- **Record.** `matters/<tenant id>/<matter id>/` holds the lease PDF and what the tool read from it, `matter.json`
  (current state), and `events.jsonl` (the history, chat included, append-only).
- **Web page.** One Streamlit page on this computer only. It starts or opens a matter, runs the chat, and lists the
  pending facts to confirm.

## Open questions, settled by comparison

Two parts are settled by testing 2 or 3 methods side by side on the same test and the same model, test material
written and approved before any build, scores kept in `comparisons/`:

1. How to read the lease (`comparisons/lease/`): decides `lease.py`, `search_lease`, and how lease quotes are checked.
2. How to write a skill (`comparisons/skills/`): decides the skill format and how the skill quote checker reads it.
   `deposit_not_returned` is rewritten first; the others follow only after the author approves the method.

## Non-negotiables

- The model never computes a date. `count_days` does, from confirmed facts only.
- The model never quotes from memory. Every quote is checked against `statutes/` or the lease's stored text.
- A fact counts only after the tenant confirms it. The model can only note it.
- The history is append-only. Nothing in `events.jsonl` is edited or deleted.
- `statutes/` is read-only. No statute text, section number, or deadline is written from memory into a skill, a rule,
  or a reply.

## Left out of v2

Unless the author asks: the cite checker, a deadline engine and typed deadline clocks, case opinions and the case wiki,
court calendars, letters, logging messages and files, the confirmation form, automatic replies, retries, switchable
rules, the timeline, the visit runner, smoke and online tests, v1's eval stories, and the "not a lawyer's advice"
footer.

## Stack

Python. The `openai` package on the UF gateway (OpenAI-compatible) with a plain tool loop, no LangChain. The model is
set in `config.py` from `AGENT_MODEL`, default `nemotron-3-super-120b-a12b`. Streamlit for the page. Under about 1,000
lines of app code.
