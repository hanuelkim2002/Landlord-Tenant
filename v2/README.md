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
6. Cite each rule to its source: a statute section and subsection, or the lease. Put in quotation marks only the
   statute's or the lease's own words. Say everything else in your own words: what the tenant told you, the facts they
   confirmed, and any message, letter, or paper they describe.
7. Dates come only from `count_days`.
8. End with the one question the answer needs, if any. No offers the tenant didn't ask for, and none repeated.
9. Keep the timeline with `save_line`: one line for each thing that happens between the tenant and the landlord, or
   to the home. A line is open only while it waits for one specific next thing (a reply, a visit, a repair, a
   payment), not just because the dispute goes on; when that thing happens or can no longer happen, the line that
   waited for it is closed by saving it again with its number. A date a skill counts from is also noted as a fact.
   (Rules 9 and 10 added 2026-10-25, with the memory.)
10. After a gap (a SINCE LAST VISIT block), start from what the tenant says and the open lines, and ask about an
    unsettled open line once. Never ask again for what the facts, the timeline, or the chat already hold.

Reading the lease (approved 2026-10-19, `comparisons/lease/README.md`):

1. THE LEASE is the tenant's whole lease, page by page. Read all of it, addenda and tables included, before saying
   whether it covers a point.
2. Say the lease does not address a point only if no part of it does. If a clause comes close but does not settle
   the point, say what it does say.
3. Quote the lease's own words, and cite the section number, or the page when there is none.
4. A choice in the lease counts only if it is marked: a checked box, or initials on the line. An unchecked box or a
   blank initials line was not chosen.

Looking things up (2026-10-22): when the model needs several lookups (statute sections, skills, day counts, facts to
note), it asks for all of them in the same step, not one at a time. One at a time, Gemini used up all 8 tool rounds.

## The parts

- **Stored law.** `statutes/` (40 sections and `index.json`, read-only). `skills/`, one file per situation; the model
  sees each skill's name and description and loads the ones that fit.
- **The lease.** The tenant uploads a PDF. Every page is read from its image by Claude Haiku 5.5 on OpenRouter (a
  PDF's own text can lose what was typed into the form and its check boxes). The text is stored page by page, and
  the whole lease goes into the system prompt once, every turn (method A, 2026-10-19, `comparisons/lease/`; the
  reader changed 2026-10-21, `comparisons/models/`).
- **Six tools.** `get_statute_section`, `search_statute`, `load_skill`, `count_days`, `note_fact`, `save_line`. No
  `search_lease`: the model has the whole lease.
- **Facts.** `note_fact` saves what the tenant said as a pending fact. The tenant confirms or corrects it on the web
  page. Only confirmed facts count. Dates are written YYYY-MM-DD.
- **Dates.** `count_days(fact, days)` is the only date math for deadlines: calendar days from a confirmed date, start
  day not counted, no weekend or holiday shift. That counting is not yet checked (`../v1/AUTHOR.md`, item 3), and every
  result says so.
- **Checks under each reply.** Every quotation of 20 characters or more is checked word for word against the section
  it cites, or the lease. Below the reply, the program prints the words each cite points to. The tenant sees the
  results; the reply is never blocked.
- **Record.** `matters/<tenant id>/<matter id>/` holds the lease PDF and what the tool read from it, `matter.json`
  (current state), and `events.jsonl` (the history, chat included, append-only).
- **Memory (2026-10-25).** The timeline: numbered lines in `matter.json`, one for each thing that happened, each open
  or not; every version of a line is in `events.jsonl` (`line_saved`). When the last message was on an earlier day,
  code adds the days since then and the facts confirmed since then (SINCE LAST VISIT). The old chat stays in the
  prompt. Spec: `docs/superpowers/specs/2026-10-25-memory-timeline-design.md`; test: `comparisons/memory/`.
- **Web page.** One Streamlit page on this computer only. It starts or opens a matter, runs the chat, lists the
  pending facts to confirm, and shows the timeline.

## Open questions, settled by comparison

Two parts are settled by testing 2 or 3 methods side by side on the same test and the same model, test material
written and approved before any build, scores kept in `comparisons/`:

1. How to read the lease (`comparisons/lease/`): settled 2026-10-19, method A, the whole lease in the prompt. Since
   2026-10-21 every page is read from its image by Haiku 5.5 (`comparisons/models/`).
2. How to write a skill (`comparisons/skills/`): settled 2026-10-20, format A, an element checklist, with each
   open question and each `count_days` call inside the condition that uses it. `deposit_not_returned` is rewritten
   first; the others follow only after the author has tried it and approves the method.

## Non-negotiables

- The model never works out a date. Code does all date math. `count_days` is the only date math for deadlines,
  from confirmed facts only.
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

Python. The `openai` package on OpenRouter (OpenAI-compatible; the UF gateway can still be chosen) with a plain tool
loop, no LangChain. The chat model is set in `config.py` from `AGENT_MODEL`, default `google/gemini-3.8-flash`; the
lease reader from `VISION_MODEL`, default `anthropic/claude-haiku-5.5` (both chosen 2026-10-21, `comparisons/models/`). Streamlit for the page. Under about 1,000
lines of app code.
