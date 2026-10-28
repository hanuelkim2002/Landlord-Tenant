# Plain Replies Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replies a tenant without legal training can read: a short plain answer first, each reason one click away.

**Architecture:** The model writes the short answer and the question, a DETAILS line, then one `###` heading per
point. `chat.split_reply` cuts the stored reply at the marker; the page shows the short part and one click-to-open
box per point. A live test runs today's rules against the new ones on the 18 deposit stories.

**Tech Stack:** Python 3, Streamlit, the OpenAI client to Anthropic (Sonnet 5.5), v2's own `tests.py`, Opus
subagents in Claude Code as graders.

**Spec:** `docs/superpowers/specs/2026-10-27-plain-replies-design.md`

## Global Constraints

- Work in `v2/` of this worktree, branch `claude/project-status-275683`. The worktree has no venv or `.env`; use the
  main checkout's: `MAIN="/Users/hanuelkim/Documents/ALL_CLAUDE_FILES/Landlord-Tenant/Landlord-Tenant ClaudeCode/v2"`,
  `PY="$MAIN/venv/bin/python"`.
- `$PY tests.py` (from `v2/`) must end "All checks passed." after every task.
- App code under about 1,000 lines: `wc -l config.py law.py record.py lease.py checks.py tools.py chat.py app.py`,
  831 before this plan.
- Plain names, short functions, a one-line docstring per function, comments say why. No em dashes anywhere.
- The "Writing the reply" block and the plain-reading grader's wording are copied verbatim from the spec.
- `statutes/` and `../v1/` are read-only. Never print `.env` or anything in `matters/`.
- The live test uses only the made-up stories and leases in `comparisons/skills/` and Sonnet 5.5 from Anthropic. Its
  key comes from the main checkout's `.env` into the environment (`set -a; . "$MAIN/.env"; set +a`), never printed.
  Budget about $7; stop and tell the author if the logged cost passes $10.
- No rule changes beyond the spec. If a target is missed, report it; the author decides what changes.
- Commit at the end of each task. Push and open a PR only on the author's OK.
- A CHANGELOG.md entry is at most about five lines.
- Skills (the author's rule): invoke each task's **Skills** before its first step. For the whole build:
  superpowers:executing-plans (native) or superpowers:subagent-driven-development; superpowers:systematic-debugging
  for any failing check or odd result, before any fix; superpowers:verification-before-completion before saying a
  task is done; at the end, superpowers:requesting-code-review (one fresh reviewer, the whole branch),
  superpowers:receiving-code-review for its findings, and superpowers:finishing-a-development-branch.

## Review Focus

- A "$" in a box title, like "Why you get the $1,050 back": shown as written, not as a math formula (Task 2 check).
- A heading with nothing under it: no empty box (Task 1 test).
- The model puts its question after the details, out of sight in the last box: counted as "question hidden" (Task 5).
- A chat saved before this change, with no DETAILS line: shown whole, as today (Task 1 test, Task 2 check).
- The marker written "Details:", "**DETAILS**", or in lower case: still found (Task 1 test).

---

### Task 1: `split_reply`

**Skills:** superpowers:test-driven-development, superpowers:verification-before-completion.

**Files:**
- Modify: `chat.py` (new `DETAILS`, `WHY`, `split_reply`; module docstring names the split)
- Test: `tests.py` (new section at the end, before the summary line)
- Modify: `DOCUMENTATION.md` (chat.py section: `split_reply`)

**Interfaces:**
- Produces: `chat.DETAILS = "DETAILS"`, `chat.WHY = "Why, and the law behind it"`,
  `chat.split_reply(text: str) -> tuple[str, list[tuple[str, str]]]`: (short part, [(title, body)]).

- [ ] **Step 1: Write the failing tests**

```python
# ---- Splitting a reply into the short answer and its points (chat.py)

check("each heading under DETAILS becomes a point, its title without the # and bold marks",
      chat.split_reply("You get the deposit back.\n\nWhen did you move out?\n\nDETAILS\n### Does the law cover you?\n"
                       "Yes.\n## **Why your landlord loses the deposit**\nNo letter came.")
      == ("You get the deposit back.\n\nWhen did you move out?",
          [("Does the law cover you?", "Yes."), ("Why your landlord loses the deposit", "No letter came.")]))
check("DETAILS with no heading gives one Why point",
      chat.split_reply("Short.\nDETAILS\nAll the reasons.") == ("Short.", [(chat.WHY, "All the reasons.")]))
check("text before the first heading goes in the Why point",
      chat.split_reply("Short.\nDETAILS\nFirst.\n### Point?\nBody.") == ("Short.", [(chat.WHY, "First."), ("Point?", "Body.")]))
check("no DETAILS line: the whole reply, no points",
      chat.split_reply("All of it.\n### A heading\nBody.") == ("All of it.\n### A heading\nBody.", []))
check("DETAILS inside a sentence is not the marker",
      chat.split_reply("These DETAILS matter.\nMore.") == ("These DETAILS matter.\nMore.", []))
check("the marker may be bold, end in a colon, or be in any case",
      all(chat.split_reply(f"Short.\n{marker}\nWhy.") == ("Short.", [(chat.WHY, "Why.")])
          for marker in ("**DETAILS**", "DETAILS:", "Details", "  details  ")))
check("a heading with nothing under it gives no empty box",
      chat.split_reply("Short.\nDETAILS\n### Empty\n### Full\nBody.") == ("Short.", [("Full", "Body.")]))
```

- [ ] **Step 2: Run `$PY tests.py`.** Expected: the new checks fail (`AttributeError: module 'chat' has no attribute
  'split_reply'` stops the run).

- [ ] **Step 3: Implement `split_reply` in `chat.py`,** after `system_prompt`. Split at the first line matching
  `(?im)^[ \t]*\**[ \t]*details[ \t]*:?[ \t]*\**[ \t]*$` (spaces and tabs only, so a match never spans lines; any
  case, a reading of the spec's "a line holding only DETAILS" that forgives "Details"); under it, a point starts at
  each line matching `(?m)^#+[ \t]+(.*)$`; a title is
  that text with `*` and spaces stripped; text before the first heading is a point titled `WHY`; every part is
  stripped; a point with an empty body is dropped.

- [ ] **Step 4: Run `$PY tests.py`.** Expected: every line OK, "All checks passed."

- [ ] **Step 5: Update DOCUMENTATION.md** (one line for `split_reply` in the chat.py section) **and commit**
  (`chat.py tests.py DOCUMENTATION.md`): "split_reply: a reply's short part and its points".

### Task 2: The page shows the short part and one box per point

**Skills:** anthropic-skills:built-in-browser (before the first browser step),
superpowers:verification-before-completion. The page has no automated test; the browser check in Step 3 is its test.

**Files:**
- Modify: `app.py` (new `show_reply`; the chat loop uses it for the tool's replies)
- Modify: `DOCUMENTATION.md` (app.py section)

**Interfaces:**
- Consumes: `chat.split_reply` (Task 1).
- Produces: `app.show_reply(text: str) -> None`: `safe(short)` as markdown, then one `st.expander(safe(title))`
  per point holding `safe(body)`. The chat loop calls `show_reply` then `show_checks` for an assistant message; a
  tenant's message is shown as now.

- [ ] **Step 1: Write `show_reply` and use it in the chat loop.**

- [ ] **Step 2: Make a throwaway matter for the check.** From `v2/`, with `$PY`, call `record.new_matter("t-plain",
  "page check")`, then `record.add_message` for: a tenant message; a reply in the new form whose first heading is
  "### Why you get the $1,050 back" and whose body quotes 83.49(3)(a); and an old-style reply with no DETAILS.
  (`matters/` is git-ignored.)

- [ ] **Step 3: Start the page and look.** Run in the background from the worktree's `v2/`:
  `"$MAIN/venv/bin/streamlit" run app.py --server.headless true --server.port 8501`, then `preview_start` with name
  `app`. Open the matter. Expected: the short part shows; the boxes are closed and titled with their questions; the
  title shows "$1,050" as written; an opened box shows its body; the "Quotes checked" box is still under the reply;
  the old-style reply shows whole. Take a screenshot for the author.

- [ ] **Step 4: Stop the server, close the preview, and delete `matters/t-plain/`.**

- [ ] **Step 5: Run `$PY tests.py`, update DOCUMENTATION.md, and commit** (`app.py DOCUMENTATION.md`): "The page
  shows a reply's short part and one box per point".

### Task 3: The rules

**Skills:** superpowers:test-driven-development, superpowers:verification-before-completion.

**Files:**
- Create: `comparisons/plain/rules_old.txt` (today's `chat.RULES`, written by code before any edit, byte for byte)
- Modify: `chat.py` (`RULES`: rule 8, and the "Writing the reply" block after rule 10)
- Test: `tests.py` (one check in the Task 1 section)
- Modify: `README.md` (rule 8, the new block after rule 10, the cap, the Web page bullet), `CHANGELOG.md`,
  `AUTHOR.md` (Decided), `TODO.md` (Later)

**Interfaces:**
- Produces: `comparisons/plain/rules_old.txt`, read by Task 4 as the baseline rules.

- [ ] **Step 1: Save today's rules.** `$PY -c "import chat, pathlib; pathlib.Path('comparisons/plain').mkdir();
  pathlib.Path('comparisons/plain/rules_old.txt').write_text(chat.RULES)"`.

- [ ] **Step 2: Write the failing test**

```python
check("the rules ask for the marker the page looks for",
      f"a line with only {chat.DETAILS} on it" in chat.RULES
      and "### Does Florida's deposit law cover you?" in chat.RULES)
```

- [ ] **Step 3: Run `$PY tests.py`.** Expected: that check FAILs.

- [ ] **Step 4: Edit `RULES`.** Rule 8 begins "End the short answer with the one question your answer needs, if
  any." The spec's block goes after rule 10, before "Reading the lease:", as one paragraph heading and four numbered
  lines, worded verbatim. Expected: `len(chat.RULES.split())` is about 700.

- [ ] **Step 5: Run `$PY tests.py`.** Expected: "All checks passed."

- [ ] **Step 6: Docs.** README.md: the same rule 8 and block in "How the model answers", with "(Added 2026-10-27.)";
  "under about 400 words in all" becomes "about 700 words in all"; the Web page bullet says each reply shows a short
  answer with each point behind a click. CHANGELOG.md: one entry for Tasks 1 to 3 (what changed, what it replaced).
  AUTHOR.md Decided: "2026-10-27: replies lead with a short plain answer (3 to 5 sentences, no section numbers or
  quotes), each point behind a click; the rules' cap is about 700 words (spec)". TODO.md Later: "Trim the rules
  toward their old length, if the author wants it (about 700 words since 2026-10-27)."

- [ ] **Step 7: Commit** (`chat.py tests.py README.md CHANGELOG.md AUTHOR.md TODO.md comparisons/plain/rules_old.txt`):
  "Rules: a short plain answer first, each point under DETAILS".

### Task 4: The live test's runs

**Skills:** superpowers:verification-before-completion (the dry run proves the runner before any paid call).

**Files:**
- Create: `comparisons/plain/run.py`, `comparisons/plain/README.md` (what the test asks, how to run it)
- Create (by running): `comparisons/plain/results/old.jsonl`, `comparisons/plain/results/new.jsonl`

**Interfaces:**
- Consumes: `comparisons/plain/rules_old.txt` (Task 3); from `comparisons/deposit/run.py`: `all_stories()`,
  `chosen(stories, numbers)`, `pages_for(story)`; from `comparisons/models/`: `models.setup`,
  `models.CHAT_MODELS["sonnet-anthropic"]`, `models.lines_without_errors`, `models.add_line`, `models.read_lines`,
  `run_chat.answer_once`, `run_chat.progress`.
- Produces: `python run.py old|new [--stories 6,8,13-18] [--dry]` from `comparisons/plain/`, writing one line per
  answer to `results/<rules>.jsonl`: `{"rules", "story", "run", **answer_once's fields}`. `old` sets
  `app.chat.RULES` to `rules_old.txt`'s text; `new` keeps the app's rules. Both use the app's own skills (the deposit
  skill there is the deposit test's `fixed3`). Three runs per story, six stories at a time, skipping answers already
  saved, as `comparisons/deposit/run.py` does.

- [ ] **Step 1: Write `run.py` and README.md.**
- [ ] **Step 2: Dry run.** `$PY run.py new --stories 1 --dry`. Expected: 3 lines in `results/dry/new.jsonl`, no
  request sent. Delete `results/dry/`.
- [ ] **Step 3: Real runs,** in the background, key loaded as in Global Constraints: `$PY run.py old`, then
  `$PY run.py new`. Expected: 54 answers each, no errors (rerun to fill any), "Done" with the logged cost.
- [ ] **Step 4: Commit** (`comparisons/plain/`): "Plain replies test: 108 answers on Sonnet, old rules and new".

### Task 5: Grading, scores, and the chart

**Skills:** superpowers:dispatching-parallel-agents (the nine graders), dataviz (before the chart),
superpowers:verification-before-completion.

**Files:**
- Create: `comparisons/plain/judge.py`, `comparisons/plain/score.py`, `comparisons/plain/review_plain.json`
- Create (by running): `results/judge_right_<rules>.json`, `results/judge_plain_<rules>.json`, `scores.json`,
  `SCORES.md`
- Modify: `comparisons/plain/README.md` (results), `SLIPS.md`, `CHANGELOG.md`

**Interfaces:**
- Consumes: `chat.split_reply`, `chat.WHY` (Task 1); `checks.STATUTE_CITE`, `checks.QUOTE`; `score.story_verdict`,
  `score.middle`, `score.table` from `comparisons/models/score.py`; the results of Task 4.
- Produces:
  - `python judge.py pack <folder>`: per story, `right-<story>.json` (the deposit test's packet shape: the story's
    key fields, its lease file, the six whole answers shuffled with seed 23 under labels like `deposit-6-A1`) and
    `plain-<story>.json` (the tenant's message and, per answer, what the tenant sees first: the short part, then each
    box title as a line `[ > title ]`), plus `key.json`. Use a folder in the scratchpad, not the repo.
  - `python judge.py unpack <folder>`: `grades-right-*.json` and `grades-plain-*.json` into
    `results/judge_right_<rules>.json` and `results/judge_plain_<rules>.json`, keyed like `"deposit-6/2"`.
  - `python score.py`: `scores.json`, `SCORES.md`, and the targets met or missed, printed.

- [ ] **Step 1: Write `judge.py`; pack.**

- [ ] **Step 2: Grade with Opus subagents** (Agent tool, model `opus`), in one message: six for the right grade,
  three stories each, and three for the plain grade, six stories each. Each writes `grades-right-<n>.json` or
  `grades-plain-<n>.json` in the packet folder.
  - Right: the deposit test's instructions, `STORY_PROMPT` in `comparisons/models/score.py`, reading the lease file
    and statutes 83.42, 83.43, 83.49, 83.491, 83.505. Output per label: `points_made`, `mistakes_made`,
    `answers_first`, `other_error`, `reason`, as in `comparisons/deposit/results/sonnet/judge_opus_fixed2.json`.
  - Plain: the spec's grader wording, verbatim. Output per label: `unclear_words` (a list of `{"word", "sentence",
    "could_mean"}`), `legal_words` (a list of quotes), `answers_alone` (true or false), `why`.

- [ ] **Step 3: Unpack, then check every plain count.** Read each quoted word in its sentence. Where a count is
  wrong, record the fix in `review_plain.json` as `{"<rules>": {"deposit-6/2": {"unclear_words": n,
  "legal_words": n, "why": "..."}}}`.

- [ ] **Step 4: Write `score.py`.** Per answer: `format_followed` (a point whose title is not `WHY`), `short_words`,
  `cites_in_short` (`STATUTE_CITE` or `QUOTE` found in the short part), `question_hidden` (no "?" in the short part,
  and the last point's body ends with "?"), the verdict (`score.story_verdict`, settled stories only: not deposit-2,
  deposit-5), and the plain counts with `review_plain.json` applied. Per rules: each of those totaled or as a median,
  and `answers_alone`. Targets, printed met or missed: format followed in at least 52 of 54 new answers; median
  short part 100 words or less; median unclear words and median legal words 0, and lower than under the old rules;
  right answers not fewer than under the old rules.

- [ ] **Step 5: Run `$PY score.py`.** Expected: `SCORES.md` with a totals table (old, new) and each story's
  verdicts; the targets printed.

- [ ] **Step 6: Show the results as a chart in chat** (dataviz skill): old against new for words seen first,
  unclear words, legal words, and right answers.

- [ ] **Step 7: Write up.** `comparisons/plain/README.md`: the results and what they show. SLIPS.md: each kind of
  model mistake seen, with its count (like a hidden question or a section number in the short part). CHANGELOG.md:
  one entry. Run `$PY tests.py` and the line count.

- [ ] **Step 8: Commit** (`comparisons/plain/ SLIPS.md CHANGELOG.md`): "Plain replies test: graded and scored".
  Then report to the author: the chart, the targets, two or three answers to try on the page, and whether to open
  a PR. If a target is missed, say which and stop; the author decides.
