# Memory Timeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give each matter a numbered timeline of what happened and a "since last visit" note, so a returning
tenant doesn't have to explain it all again.

**Architecture:** Lines live in `matter.json` next to the facts; every version goes to `events.jsonl` as
`line_saved`. One new tool, `save_line`. When the prompt is built, code adds the timeline and, after a gap of a day
or more, the days since the last message and the facts confirmed since then.

**Tech Stack:** Python 3, Streamlit, the OpenAI client to OpenRouter (Gemini 3.8 Flash), v2's own `tests.py`.

**Spec:** `docs/superpowers/specs/2026-10-25-memory-timeline-design.md`

## Global Constraints

- Work in `v2/` of this worktree. The worktree has no venv or `.env`; use the main checkout's:
  `MAIN="/Users/hanuelkim/Documents/ALL_CLAUDE_FILES/Landlord-Tenant/Landlord-Tenant ClaudeCode/v2"`,
  `PY="$MAIN/venv/bin/python"`. `$PY tests.py` runs from `v2/`; the memory scripts run from `comparisons/memory/`.
- `$PY tests.py` must end "All checks passed." after every task.
- The model never works out a date. Code does all date math; `count_days` is the only date math for deadlines.
- Plain names, short functions, a one-line docstring per function, comments say why. No em dashes anywhere.
- Under about 1,000 lines of app code (`wc -l *.py` in `v2/`, 811 before this plan). Stop and say why if it passes.
- No commit until Task 8: the author asked for one commit of everything at the end. Never commit `matters/` or
  `.env`; never print `.env`.
- `../v1/` and `statutes/` are read-only.
- DOCUMENTATION.md is updated in the task that changes a module or function.
- The live test uses only the sample lease (`comparisons/skills/lease.txt`), made-up stories, and Gemini 3.8 Flash
  on OpenRouter. Its key is loaded from the main checkout's `.env` into the environment, never printed.

## Review Focus

- A matter saved before this change has no `lines`: it must still open on the page and in the chat (Task 1 test).
- A model sends `open` as the word "false" or a number as text "3": the line must be saved as meant (Task 3 tests).
- A brand-new matter has no messages yet: its first prompt has no since-last-visit block and no error (Tasks 2, 4).
- A message at 11:30 pm and a return the next morning: one day, counted in calendar days (Task 2 test).
- A line with an amount, like "$500": the page shows it as written, not as a math formula (Task 5 check).

---

### Task 1: Lines in the record

**Files:**
- Modify: `record.py` (`new_matter`, `load`; new `save_line`; module docstring)
- Test: `tests.py` (new section after the count_days section)
- Modify: `DOCUMENTATION.md` (record.py section: the new function, `line_saved` in the events list)

**Interfaces:**
- Produces: `record.save_line(m, number: int, date: str, what: str, open: bool) -> int` (the line's number);
  raises `ValueError` with a plain sentence for an unknown number or an empty `what`. A new matter has
  `m["lines"] == {}`; `record.load` gives `m["lines"]` for old matters too. A line is
  `{"date": str, "what": str, "open": bool, "saved": time}` under the key `str(number)`.

- [ ] **Step 1: Write the failing tests**

At the top of `tests.py`, add the imports `json`, `shutil`, `tempfile`, `atexit`, `from datetime import date`,
`from pathlib import Path`, `config`, `record`, and name the timeline in the module docstring. Then a new section:

```python
# ---- The timeline (record.py), in a throwaway matters folder, never the real matters/

config.MATTERS = Path(tempfile.mkdtemp(prefix="matters_test_"))
atexit.register(shutil.rmtree, config.MATTERS, ignore_errors=True)


def refused(action):
    """Whether an action is refused with a ValueError."""
    try:
        action()
    except ValueError:
        return True
    return False


lines_matter = record.new_matter("t-lines", "test")
check("a new matter starts with no lines", lines_matter["lines"] == {})
first = record.save_line(lines_matter, 0, "2026-10-13", "AC stopped working", True)
second = record.save_line(lines_matter, 0, "", "Tenant texted the landlord about the AC", False)
check("new lines are numbered in order", (first, second) == (1, 2))
record.save_line(lines_matter, 1, "2026-10-14", "AC stopped working", True)
versions = [e["date"] for e in record.events(lines_matter) if e["kind"] == "line_saved" and e["number"] == 1]
check("a new version replaces the line, and the history keeps both",
      record.load("t-lines", lines_matter["matter"])["lines"]["1"]["date"] == "2026-10-14"
      and versions == ["2026-10-13", "2026-10-14"])
check("an unknown line number is refused", refused(lambda: record.save_line(lines_matter, 9, "", "x", False)))
check("a line with nothing in it is refused", refused(lambda: record.save_line(lines_matter, 0, "", "  ", False)))
old_matter = record.new_matter("t-old", "test")
saved = json.loads((record.folder(old_matter) / "matter.json").read_text())
saved.pop("lines")
(record.folder(old_matter) / "matter.json").write_text(json.dumps(saved))
check("a matter saved before lines existed opens with no lines",
      record.load("t-old", old_matter["matter"])["lines"] == {})
```

- [ ] **Step 2: Run the tests to see them fail**

Run: `$PY tests.py`
Expected: a `KeyError: 'lines'` (or AttributeError on `save_line`) before the summary.

- [ ] **Step 3: Implement in `record.py`**

`new_matter` adds `"lines": {}`. `load` does `m.setdefault("lines", {})` before returning (why: matters saved before
this change). `save_line(m, number, date, what, open)`: number 0 means a new line numbered `len(m["lines"]) + 1`
(lines are never removed, so this counts up); another number must already be a key, else
`ValueError(f"No line {number}. The lines: {', '.join(m['lines']) or 'none yet'}.")`; an empty `what.strip()` gives
`ValueError("A line needs what happened, in plain words.")`. Store the line, `save(m)`, then
`log(m, "line_saved", number=n, date=date, what=what, open=open)`. Add one line to the module docstring: the timeline's
lines live in matter.json too, and every version of a line is in the history.

- [ ] **Step 4: Run the tests to see them pass**

Run: `$PY tests.py`
Expected: every line OK, "All checks passed."

- [ ] **Step 5: Update DOCUMENTATION.md** (record.py: `save_line` in one line; add `line_saved` to the events list).

### Task 2: Since last visit

**Files:**
- Modify: `record.py` (new `since_last_visit`; import `date` from datetime)
- Test: `tests.py` (same section)
- Modify: `DOCUMENTATION.md`

**Interfaces:**
- Produces: `record.since_last_visit(m, today: date | None = None) -> dict | None`. `None` when the matter has no
  message yet or the last message was today. Otherwise `{"days": int, "changed": [{"fact", "value",
  "noted_value"}]}`: calendar days from the last `message` event's date to `today` (default `date.today()`, looked up
  at call time so the live test can stand in a story's day), and every `fact_confirmed` event after that message,
  oldest first.

- [ ] **Step 1: Write the failing tests**

```python
def add_event(m, time, kind, **data):
    """Write one event with a chosen time, as if it happened then."""
    with (record.folder(m) / "events.jsonl").open("a") as f:
        f.write(json.dumps({"time": time, "kind": kind, **data}) + "\n")


visit = record.new_matter("t-visit", "test")
check("a matter with no messages yet has no last visit", record.since_last_visit(visit, date(2026, 10, 25)) is None)
add_event(visit, "2026-10-13T19:00:00", "message", role="user", text="hi")
add_event(visit, "2026-10-13T19:00:05", "message", role="assistant", text="hello")
add_event(visit, "2026-10-15T09:00:00", "fact_confirmed", fact="move_out_date", value="2026-07-30",
          noted_value="2026-07-31")
add_event(visit, "2026-10-15T09:01:00", "fact_confirmed", fact="deposit", value="800", noted_value="800")
since = record.since_last_visit(visit, date(2026, 10, 25))
check("the days since the last message are counted by code", since["days"] == 12)
check("facts confirmed since then are listed, with the value first noted", since["changed"] == [
    {"fact": "move_out_date", "value": "2026-07-30", "noted_value": "2026-07-31"},
    {"fact": "deposit", "value": "800", "noted_value": "800"}])
check("no block on the same day", record.since_last_visit(visit, date(2026, 10, 13)) is None)
late = record.new_matter("t-late", "test")
add_event(late, "2026-10-24T23:30:00", "message", role="assistant", text="night")
check("a message late last night counts as one day", record.since_last_visit(late, date(2026, 10, 25))["days"] == 1)
```

- [ ] **Step 2: Run the tests to see them fail** (`$PY tests.py`; expected: AttributeError, no `since_last_visit`).
- [ ] **Step 3: Implement `since_last_visit` in `record.py`** from `events(m)`: the last `message` event's time;
  days = `(today - date.fromisoformat(time[:10])).days`; under 1 gives `None`; `changed` from `fact_confirmed` events
  whose time is later (ISO times compare as text).
- [ ] **Step 4: Run the tests to see them pass** (`$PY tests.py`, "All checks passed.").
- [ ] **Step 5: Update DOCUMENTATION.md** (record.py: `since_last_visit` in one line).

### Task 3: The save_line tool

**Files:**
- Modify: `tools.py` (new `save_line`, a `today()` helper, `RUN`, `SCHEMAS`, `BOOLEAN`; docstring "The six tools")
- Test: `tests.py`
- Modify: `DOCUMENTATION.md` (tools.py section)

**Interfaces:**
- Consumes: `record.save_line` (Task 1).
- Produces: `tools.save_line(m, number, date, what, open) -> str`, run by `run_tool` as `"save_line"`. `date` equal
  to "today" (any case, spaces trimmed) becomes `str(today())`, written by code. `number` is turned into an int;
  `open` counts as true only for `True` or the word "true" (any case). Returns
  `f"Saved line {n}: {date or 'no date'}: {what}" + (" (open)." if open else ".")`, or the ValueError's sentence.
  `today()` is a module-level helper returning `date.today()` (why: the parameter named `date` hides the class
  inside `save_line`, and the live test replaces `tools.date` with the story's day).

- [ ] **Step 1: Write the failing tests**

```python
from tools import save_line

tool_matter = record.new_matter("t-tool", "test")
check("the tool adds a line and says its number",
      save_line(tool_matter, 0, "2026-10-20", "Landlord texted: fix Thursday", True).startswith("Saved line 1:"))
save_line(tool_matter, 0, "Today", "Tenant got the landlord's letter", "false")
check("'today' becomes today's date, written by code", tool_matter["lines"]["2"]["date"] == str(date.today()))
check("open given as the word false is not open", tool_matter["lines"]["2"]["open"] is False)
check("a number given as text works",
      save_line(tool_matter, "1", "2026-10-21", "Landlord texted: fix Thursday", True).startswith("Saved line 1:"))
check("an unknown number gets a plain reply", "No line 7" in save_line(tool_matter, 7, "", "x", False))
```

- [ ] **Step 2: Run the tests to see them fail** (`$PY tests.py`; expected: ImportError, no `save_line` in tools).
- [ ] **Step 3: Implement.** The schema, after `note_fact`, with `BOOLEAN = {"type": "boolean"}`:

```python
tool("save_line", "Save one line of the timeline: one thing that happened between the people in the dispute, or to "
     "the home (a message, a visit, a payment, a promise, a repair, a move). number: 0 for a new line, or a line's "
     "number to save a new version of it, to fix it or close it. date: YYYY-MM-DD if the tenant gave the exact day, "
     "\"today\" if it happened today, otherwise the tenant's words (like \"last Monday\"), or empty. what: plain "
     "words, with who did it and how. open: true while something is still waiting on this line.",
     number=NUMBER, date=TEXT, what=TEXT, open=BOOLEAN),
```

- [ ] **Step 4: Run the tests to see them pass** (`$PY tests.py`, "All checks passed.").
- [ ] **Step 5: Update DOCUMENTATION.md** (tools.py: `save_line` in one line; "five tools" becomes six).

### Task 4: The prompt

**Files:**
- Modify: `chat.py` (`RULES` rules 9 and 10; new `timeline_text`, `since_text`; `system_prompt`; docstring)
- Test: `tests.py`
- Modify: `DOCUMENTATION.md` (chat.py section)

**Interfaces:**
- Consumes: `m["lines"]` (Task 1), `record.since_last_visit` (Task 2), the `save_line` tool (Task 3).
- Produces: `chat.timeline_text(lines: dict) -> str`, `chat.since_text(since: dict | None) -> str`. `system_prompt`
  keeps its signature `(m, pages)`.

- [ ] **Step 1: Write the failing tests**

```python
import chat

check("the timeline shows each line in order, open ones marked",
      chat.timeline_text({"1": {"date": "2026-10-13", "what": "AC stopped working", "open": True},
                          "2": {"date": "", "what": "Tenant texted the landlord", "open": False}})
      == "- 1. 2026-10-13: AC stopped working (open)\n- 2. (no date): Tenant texted the landlord")
check("no lines yet says so", chat.timeline_text({}) == "- none yet")
check("no gap, no block", chat.since_text(None) == "")
check("the block gives the days, and the facts confirmed since, with any correction",
      chat.since_text({"days": 12, "changed": [
          {"fact": "move_out_date", "value": "2026-07-30", "noted_value": "2026-07-31"},
          {"fact": "deposit", "value": "800", "noted_value": "800"}]})
      == "\n\nSINCE LAST VISIT (counted by code):\nThe last message was 12 days ago. Since then the tenant confirmed:"
         "\n- move_out_date: 2026-07-30 (first noted as 2026-07-31)\n- deposit: 800")
check("one day is said as one day",
      chat.since_text({"days": 1, "changed": []}) == "\n\nSINCE LAST VISIT (counted by code):\nThe last message was 1 day ago.")
check("a returning tenant's prompt holds the timeline and the since-last-visit block",
      "TIMELINE" in chat.system_prompt(visit, []) and "SINCE LAST VISIT" in chat.system_prompt(visit, []))
check("a brand-new matter's prompt has no since-last-visit block",
      "SINCE LAST VISIT" not in chat.system_prompt(record.new_matter("t-new", "test"), []))
```

- [ ] **Step 2: Run the tests to see them fail** (`$PY tests.py`; expected: AttributeError, no `timeline_text`).
- [ ] **Step 3: Implement.** Add to `RULES`, after rule 8, word for word:

```
9. Keep the timeline with save_line: one line for each thing that happens between the tenant and the landlord, or to the home. Mark a line open while something is still waiting on it. To fix or close a line, save it again with its number. A date a skill counts from is also noted as a fact.
10. When there is a SINCE LAST VISIT block, the tenant is back after a gap. Start from what they say and the open lines; if an open line is still unsettled, ask about it once. Never ask again for what the facts, the timeline, or the chat already hold.
```

In `system_prompt`, after the PENDING FACTS block and before SKILLS:
`f"TIMELINE (what happened, oldest first; keep it with save_line):\n{timeline_text(m['lines'])}"` followed by
`since_text(record.since_last_visit(m))`, then the usual blank line. The module docstring names the timeline.

- [ ] **Step 4: Run the tests to see them pass** (`$PY tests.py`, "All checks passed.").
- [ ] **Step 5: Update DOCUMENTATION.md** (chat.py: the two blocks and rules 9 and 10 in a line or two).

### Task 5: The page

**Files:**
- Modify: `app.py` (new `show_timeline(m)`, called after `confirm_facts(m)`; docstring mentions the timeline)
- Modify: `DOCUMENTATION.md` (app.py line)

**Interfaces:**
- Consumes: `m["lines"]` (Task 1). Produces nothing others use.

- [ ] **Step 1: Implement `show_timeline(m)`.** In the sidebar: header "Timeline"; "None yet." when empty; each
  line as `safe(f"**{number}.** {line['date'] or 'no date'}: {line['what']}")`, plus " *(open)*" when open.
- [ ] **Step 2: Run `$PY tests.py`** (still "All checks passed."; the page has no automated test).
- [ ] **Step 3: Check the page.** Seed one made-up matter into this worktree's `matters/` (gitignored) with a
  scratch script: the sample lease pages, two lines, one with "$500" in it. Start the page with
  `"$MAIN/venv/bin/streamlit" run app.py` from this worktree's `v2/` in a terminal tab, open http://localhost:8501 in the preview, open
  the matter. Expected: the Timeline shows both lines, "$500" as written, the open one marked. Then stop the page
  and delete the seeded matter.
- [ ] **Step 4: Update DOCUMENTATION.md.**

### Task 6: The live test run

**Files:**
- Create: `comparisons/memory/README.md` (what is tested, how to run, how it is scored; short)
- Create: `comparisons/memory/stories.json`
- Create: `comparisons/memory/run_memory.py`
- Create (by the run): `comparisons/memory/results/new.jsonl`, `comparisons/memory/results/baseline.jsonl`

**Interfaces:**
- Consumes: `comparisons/models/models.py` (`setup`, `start_log`, `take_log`, `StoryDate`, `story_pages(False)`,
  `add_line`, `say`), `chat.reply`, `record.*`.
- Produces: one JSON line per answer: `{"mode", "story", "run", "answer", "tool_calls", "lines_after", "seconds",
  "cost", "checks", "error"}`.

- [ ] **Step 1: Write `stories.json`**: three return visits on the sample lease (tenant Jordan Reyes, term
  2025-08-01 to 2026-07-31). Each: `id`, `today`, `first_visit` (an ISO time days before `today`), `chat` (the first
  visit: the tenant's message and a short reply that says nothing about the law from memory), `facts` (confirmed at
  the first visit), `corrected` (optional: a fact the tenant corrected in the sidebar after the first visit, with
  its time and first-noted value), `lines`, `message` (the return message), `good` (what a good answer does, for the
  review). The three:
  - `deposit_letter`: today 2026-08-20, first visit 2026-08-08. Moved out 2026-07-31 (corrected to 2026-07-30 on
    2026-08-10), forwarding address given by email; open line "Waiting for the landlord to return the deposit or
    send a notice". Return: "got a letter from him today, he's keeping $500 for carpet cleaning. what do i do".
  - `repair_no_show`: today 2026-04-18, first visit 2026-04-13. AC stopped 2026-04-11, tenant texted the landlord
    2026-04-11; open line "Landlord texted: someone will fix the AC Thursday" (2026-04-13). Return: "nobody came
    thursday. still no AC".
  - `leave_early_reply`: today 2026-03-02, first visit 2026-02-09. Goal: out by 2026-05-15 to transfer schools;
    open line "Tenant emailed the manager asking to end the lease early" (2026-02-10). Return: "he finally answered,
    says i owe rent through july no matter what".
  Check every weekday and day gap in these stories with Python's `datetime` before saving the file.
- [ ] **Step 2: Write `run_memory.py`** (`python run_memory.py new|baseline [--runs 3] [--dry]`, from this folder):
  - `baseline`: `git archive main v2 | tar -x -C <temp>` and point `models.V2` at it before `models.setup`, so the
    baseline is today's code on main (the old chat and facts, no timeline, no `save_line`).
  - `models.setup("openrouter", chat_model="google/gemini-3.8-flash", dry=args.dry)`; when the app's `record` has a
    `date`, replace it with `models.StoryDate` too (why: `since_last_visit` must see the story's day).
  - `seed(app, story, tenant, with_lines)`: a new matter; facts into `confirmed`; lines into `lines` (new mode
    only); then the first visit's events written with their old times: the chat as `message` events,
    `fact_confirmed` and `line_saved` (new mode) at `first_visit`, and the correction at its own time.
  - Per answer: `models.start_log(story["today"])`, `app.chat.reply(m, story["message"])`, `models.take_log()`; a
    failed call is kept as an answer with `"error": true`. Stories in parallel (3 threads), runs in order. Output to
    `results/{mode}.jsonl`, or `results/dry_{mode}.jsonl` with `--dry`. Each tenant id is new (`t1`, `t2`, ...).
- [ ] **Step 3: Dry run both modes**: `$PY run_memory.py new --dry` and `$PY run_memory.py baseline --dry`.
  Expected: 9 lines each, no errors, nothing sent anywhere. Delete the dry files.
- [ ] **Step 4: Real runs**: `set -a; . "$MAIN/.env"; set +a` in the same command, then
  `$PY run_memory.py new` and `$PY run_memory.py baseline` (in the background; about 18 answers). Expected: 9 lines
  each, the cost printed, no errors.

### Task 7: Score and report

**Files:**
- Create: `comparisons/memory/score.py`, `comparisons/memory/review.json`, `comparisons/memory/SCORES.md`
- Modify: `SLIPS.md` (model mistakes seen, one entry per kind)

**Interfaces:**
- Consumes: the results files (Task 6); `dates_in` and `question_count` from `comparisons/models/score.py`.

- [ ] **Step 1: Write `score.py`.** Per answer, by code: `saved_line` (a `save_line` call; new mode only),
  `count_days_used`, `made_up_dates` (`dates_in(answer, year)` minus every date in the story, the lease, and the
  results of `count_days` and `save_line` calls), `questions_asked`. It reads `review.json` and writes `SCORES.md`:
  for each mode, out of 9, the five checks: no retelling asked, picks up the open item, saves the new event as a
  line, works out no date itself, answers first; then each answer's notes.
- [ ] **Step 2: Read every answer** and write `review.json`: per answer `{"no_retelling", "picks_up_open",
  "answers_first", "why"}`, judged against the story's `good`. Run `$PY score.py`.
- [ ] **Step 3: Show the comparison as a chart in chat** (load the dataviz skill first): the five checks, new
  memory vs baseline, out of 9. Add model mistakes to SLIPS.md (one entry per kind, with counts).

### Task 8: Docs, review, and the one commit

**Files:**
- Modify: `README.md` (the tools list: six tools with `save_line`; the Record bullet: lines and `line_saved`; a short
  Memory bullet: the timeline and since last visit), `CHANGELOG.md` (one entry, at most five lines), `AUTHOR.md`
  (Decided: the memory design, 2026-10-25, with the spec's path), `DOCUMENTATION.md` (the folder list names
  `comparisons/memory/` and `docs/superpowers/`)

- [ ] **Step 1: Update the docs above.**
- [ ] **Step 2: Verify** (superpowers:verification-before-completion): `$PY tests.py` ends "All checks passed.";
  `$PY law.py` passes; `wc -l *.py` under 1,000; `git status` shows no `matters/` or `.env`; no em dashes in any
  changed file (search the diff and the new files for the character U+2014; none).
- [ ] **Step 3: A fresh review of the whole change** (superpowers:requesting-code-review); fix what it finds, then
  verify again.
- [ ] **Step 4: Commit everything in one commit**: the reworded date rule, the code, the tests, the docs, the spec,
  the plan, and `comparisons/memory/`. Message: "Memory: a timeline of the dispute and since last visit", ending
  with the Co-Authored-By line.
