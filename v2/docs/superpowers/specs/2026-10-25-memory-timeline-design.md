# Memory: a timeline of the dispute (design)

2026-10-25. Agreed in chat with the author; this writes it down.

## Why

A tenant comes back days or weeks later ("he finally texted back, now what?"). Today the chatbot gets the old chat
and the facts, but it does not know how long the tenant was gone, what is still waiting, or what happened between the
tenant and the landlord, in order. The tenant's top needs: don't make me explain it again; tell me what's next and if
I'm running out of time; get my facts right; keep what he sent and what I sent; tell me if your answer changed.

## What stays the same

- Facts: `note_fact`, the tenant confirms in the sidebar, only confirmed facts count.
- Deadlines: `count_days` counts only from confirmed facts. A date a skill counts from is noted as a fact, even when
  the same event is also a line.
- The history: `events.jsonl` only grows. The old chat stays in the prompt.
- Nothing in the memory names a dispute or a skill. A new skill needs no new code.

## What is new

**1. Timeline lines.** `matter.json` gets `"lines": {}`. Each line is the story of one thing that happened between
the people in the dispute, or to the home: a message, a visit, a payment, a promise, a repair, a move.

    "lines": {"3": {"date": "2026-10-21", "what": "Landlord texted: someone fixes the AC Thursday", "open": true}}

- `date`: YYYY-MM-DD if the tenant gave the exact day; "today" is turned into today's date by code; otherwise the
  tenant's words ("last Monday") or blank. The model never works out a date.
- `what`: plain words, with who did it and how.
- `open`: true while something is still waiting on this line.
- Lines are numbered 1, 2, 3 in the order added. Lines are never removed. Saving a line again with its number
  replaces it in `matter.json`, and the history keeps every version (event `line_saved`). That is how a line is
  fixed or closed.
- Lines are not confirmed by the tenant, because nothing is counted from them.

**2. One new tool, `save_line(number, date, what, open)`.** Number 0 adds a new line; a line's number saves a new
version of it. A number that does not exist, or an empty `what`, is refused with a plain reply.

**3. Since last visit.** When the prompt is built, code finds the last message in the chat (the tenant's or the
chatbot's; the new message is not recorded yet). If it was on an earlier day,
the prompt gets a block: how many days ago (calendar days, counted by code), and the facts the tenant confirmed or
corrected since then. On the same day, no block.

**4. The prompt.** Two new blocks after the facts: TIMELINE (every line, oldest first, open ones marked) and, when
there was a gap, SINCE LAST VISIT. Two new rules, in general words:
- Keep the timeline with `save_line`: one line for each thing that happens; mark it open while something waits on
  it; fix or close a line by saving it again with its number.
- When the tenant comes back after a gap, pick up from the open lines and ask about each one once. Don't ask again
  for what the facts, the timeline, or the chat already hold.

**5. The page.** The sidebar shows the timeline under the confirmed facts, to read only. To fix a line, the tenant
tells the chatbot.

## Left out on purpose

A due date on a line (turning "Thursday" into a date is date math; it stays in the words), confirming lines, taking a
line back, a date picker, a "done" button, where a line came from, the time of day, papers besides the lease, and
privacy controls. Each can come back if a live run shows it is needed (SLIPS.md).

## Size

About 70 new lines of app code (record.py, tools.py, chat.py, app.py), from 811 to about 880, under 1,000.

## Testing

- `tests.py`, no model: lines are numbered in order; a new version replaces the line and the history keeps both; an
  unknown number and an empty `what` are refused; "today" becomes the day's date; the days since the last message
  are counted in calendar days; no block on the same day; a fact confirmed after the last message shows as changed,
  with its noted value when the tenant corrected it; old matters without `lines` still open.
- A live test run (`comparisons/memory/`): three made-up return visits on the sample lease (a deposit letter arrives,
  a promised repair does not happen, a landlord answers about leaving early). Each starts from a first visit dated
  days earlier. Run with the new memory and with today's memory (the old chat and facts only) as the baseline, 3
  runs each, with Gemini 3.8 Flash as on the page. Each answer is checked for: no retelling asked, picks up the open
  item, saves the new event as a line (new memory only), works out no date itself, answers first. Code checks what it
  can; Claude reads every answer. Results shown as a chart; model mistakes go in SLIPS.md.
