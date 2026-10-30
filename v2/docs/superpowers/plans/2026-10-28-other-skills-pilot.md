# The Other Skills, Pilot: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The pilot of the other skills: a shared "who the law covers" skill and the repair skill, written in format
A, tested on about seven stories against v1's repair skill, with one round of fixes.

**Architecture:** Skills are markdown files in `skills/`; the app lists and loads every file there, so no app code
changes for them. One fix to the quote checker (`law.py`) lets a skill cite run-together statute parts like
83.51(2)(a). One test runner in `comparisons/each_skill/` serves this skill and every later one; it reuses the model
test's set-up (`comparisons/models/`) and the deposit test's grading.

**Tech Stack:** Python 3, the OpenAI client to Anthropic (Claude Sonnet 5.5 for the chat), v2's own `tests.py`,
Claude Opus 5.5 subagents in Claude Code as blind graders.

**Spec:** `docs/superpowers/specs/2026-10-28-other-skills-design.md`

## Global Constraints

- Work in `v2/` of this worktree, branch `claude/skills-development-planning-21e2b4`. The worktree has no venv or
  `.env`; use the main checkout's: `MAIN="/Users/hanuelkim/Documents/ALL_CLAUDE_FILES/Landlord-Tenant/Landlord-Tenant ClaudeCode/v2"`,
  `PY="$MAIN/venv/bin/python"`.
- After every task, from `v2/`: `$PY tests.py` ends "All checks passed." and `$PY law.py` prints OK for every skill.
- Never edit `skills/deposit_not_returned.md`: its fixes are on another branch (`claude/peaceful-sanderson-89b337`).
- `statutes/` and `../v1/` are read-only. No statute text, section number, or deadline from memory: every quote is
  copied from `statutes/` and cited, and `law.py` checks it.
- Anything a skill says about the law that v1's skill did not goes to the author before any live run (AUTHOR.md).
- The model never works out a date. Every deadline in a skill is a `count_days` call on a named, confirmed fact.
- App code under about 1,000 lines: `wc -l config.py law.py record.py lease.py checks.py tools.py chat.py app.py`,
  883 before this plan. Test code in `comparisons/` does not count.
- Plain names, short functions, a one-line docstring per function, comments say why. Each new module opens with two
  or three lines on what it is for. No em dashes anywhere.
- A CHANGELOG.md entry is at most about five lines. A TODO.md item is at most three lines.
- The live test uses only made-up stories and leases. Its key comes from the main checkout's `.env` into the
  environment (`set -a; . "$MAIN/.env"; set +a`), never printed. Budget about $4 per full run; stop and tell the
  author if the logged cost passes $8.
- Commit at the end of each task. Push and open a PR only on the author's OK.
- Skills (the author's rule): invoke each task's **Skills** before its first step. For the whole build:
  superpowers:executing-plans (native) or superpowers:subagent-driven-development; superpowers:systematic-debugging
  for any failing check or odd result, before any fix; superpowers:verification-before-completion before saying a
  task is done; at the end, superpowers:requesting-code-review (one fresh reviewer, the whole branch),
  superpowers:receiving-code-review for its findings, and superpowers:finishing-a-development-branch.

## Review Focus

- A notice sent one day and delivered later: both 7-day periods count from delivery, not sending (Task 4, story 2's
  facts give both dates and its key counts from delivery).
- A tenant who wants to hold back rent over something only the lease promises (a pool, a dishwasher): told plainly
  that withholding does not reach it, while ending the lease may (Task 3, a mistakes line; Task 4, story 4).
- A matter whose facts already hold `school_housing`: the shared skill never asks the college question again (Task 2,
  its first line; Task 4, every story but one gives `school_housing` in its facts).
- A quote cited to a run-together statute part, like 83.51(2)(a) or 83.60(1)(b): the checker finds it, in the skill
  and on the page (Task 1 tests).
- A cross-reference like "paragraph (3)(a)" inside another subsection: it starts no new part, so 83.49(5) still reads
  whole and the deposit skill's quotes still check out (Task 1 test).

---

### Task 1: The quote checker finds run-together statute parts

**Skills:** superpowers:test-driven-development, superpowers:verification-before-completion.

Why: `law.cited_text` returns nothing for 83.51(2), 83.51(2)(a), 83.51(2)(c), 83.51(3), 83.51(4), 83.56(5),
83.56(5)(a), 83.60(1)(a), and 83.60(1)(b), because the statute writes "(2)(a)" with no space, and the marker needs a
space after ")". 83.51(1)(b) then runs on to the end of the section. The repair skill quotes all of these, and the
page's quote check uses the same function.

**Files:**
- Modify: `law.py` (`MARKER`, `parts_of`)
- Modify: `comparisons/skills/check_key.py` (`quote_in_cite` uses `law.cited_text`; the key file may be any path;
  a story's lease is looked up beside its key file)
- Test: `tests.py` (the skill quote checker section)
- Modify: `DOCUMENTATION.md` (law.py: `parts_of`), `CHANGELOG.md`

**Interfaces:**
- Produces: `law.parts_of(text) -> dict[str, str]` and `law.cited_text(cite) -> str | None`, same signatures, now
  resolving run-together markers. `python check_key.py <key file>`: a path, or a file name in `comparisons/skills/`.

- [ ] **Step 1: Write the failing tests** in `tests.py`, after the skill quote checker's checks:

```python
check("a run-together part is found: 83.51(2)(a)",
      (law.cited_text("83.51(2)(a)") or "").startswith("(a) Unless otherwise agreed in writing"))
check("the parts after it are found: 83.51(4)",
      (law.cited_text("83.51(4)") or "").startswith("(4) The landlord is not responsible"))
check("83.51(1)(b) stops where (2) starts", "Unless otherwise agreed" not in law.cited_text("83.51(1)(b)"))
check("83.60(1)(b) and 83.56(5)(a) are found",
      (law.cited_text("83.60(1)(b)") or "").startswith("(b) The defense of a material noncompliance")
      and (law.cited_text("83.56(5)(a)") or "").startswith("(a) If the landlord accepts rent"))
check("a cross-reference like 'paragraph (3)(a)' starts no part",
      "(5)(a)" not in law.parts_of(law.section_text("83.49")))
```

- [ ] **Step 2: Run `$PY tests.py`.** Expected: the first four new checks FAIL; the fifth passes.

- [ ] **Step 3: Fix `MARKER` and `parts_of` in `law.py`.** A subsection marker " (N)" may be followed at once by a
  paragraph marker "(x)", as in " (2)(a) Unless". That letter starts a paragraph only when the number right before
  it was taken as the next subsection at that same spot, so "paragraph (3)(a)" inside subsection (5) starts nothing.
  The order rules stay as they are.

- [ ] **Step 4: Run `$PY tests.py` and `$PY law.py`.** Expected: every line OK, "All checks passed.", and
  "deposit_not_returned: 22 of 22 quotes check out".

- [ ] **Step 5: Point `check_key.py` at the same splitter.** `quote_in_cite` becomes `squash(quote) in
  squash(law.cited_text(cite) or "")` (import `law` from `v2/`), and its own `parts_of` and `MARKER` go. The key file
  argument is a path if it exists, else a name in `comparisons/skills/`; a story's `lease` is looked up in the key
  file's folder. Run from `comparisons/skills/`: `$PY check_key.py` and `$PY check_key.py stories_more.json`.
  Expected: both end "OK".

- [ ] **Step 6: Update DOCUMENTATION.md and CHANGELOG.md, and commit** (`law.py tests.py
  comparisons/skills/check_key.py DOCUMENTATION.md CHANGELOG.md`): "The quote checker finds run-together parts like
  83.51(2)(a)".

### Task 2: The shared skill, and the decisions written down

**Skills:** superpowers:verification-before-completion.

**Files:**
- Create: `skills/who_the_law_covers.md`
- Modify: `AUTHOR.md` (Decided: a 2026-10-28 entry), `README.md` (Open questions item 2; The parts: Stored law),
  `TODO.md`, `DOCUMENTATION.md` (Elsewhere: the skills), `CHANGELOG.md`

**Interfaces:**
- Produces: a skill named `who_the_law_covers`; the fact name `school_housing` (as the deposit skill uses it).
  Later skills open with: "Load who_the_law_covers, unless the facts already hold school_housing."

- [ ] **Step 1: Write `skills/who_the_law_covers.md`.**
  - Header: `name: who_the_law_covers`; the spec's draft description, word for word.
  - First line of the body: if the facts hold `school_housing`, pending or confirmed, use it and do not ask again.
  - The 83.42(1) check copied from `skills/deposit_not_returned.md` (the bullet that starts "College housing may be
    outside part II" and its three sub-bullets), with its quote and the fact `school_housing`.
  - One line on 83.42(2) to (5): a contract of sale, transient lodging, a cooperative, a condominium owner; checked
    only when the lease or the facts point to one. Quote a part's words only where the point turns on them.
  - The close: read 83.42 before telling the tenant whether an exclusion applies; if one does, part II's rules do not
    decide the dispute, and what does is outside this tool.

- [ ] **Step 2: Run `$PY law.py` and `$PY tests.py`.** Expected: "OK   who_the_law_covers: N of N quotes check out"
  with N at least 1; "All checks passed."; `wc -w skills/who_the_law_covers.md` at most 450.

- [ ] **Step 3: Write the records.**
  - AUTHOR.md, Decided, 2026-10-28: the method approved (format A for every skill); pilot, then pairs; the shared
    skill; a small test each; weekday counting decided at the unpaid-rent skill; a "what the lease adds" step in
    every skill. Point to the spec.
  - README.md: Open questions item 2 ends with the 2026-10-28 approval and the spec; Stored law names the shared skill.
  - TODO.md, Now: this pilot. Later: pairs 2 to 4 and unpaid rent, in the spec's order; once the deposit fixes are
    merged, the deposit skill points to `who_the_law_covers` instead of its own copy.
  - DOCUMENTATION.md: the skills now in `skills/`. CHANGELOG.md: the shared skill.

- [ ] **Step 4: Commit** (`skills/who_the_law_covers.md AUTHOR.md README.md TODO.md DOCUMENTATION.md CHANGELOG.md`):
  "The shared skill: who the law covers".

### Task 3: The repair skill

**Skills:** superpowers:verification-before-completion.

**Files:**
- Create: `skills/repair_not_made.md`
- Modify: `AUTHOR.md` (Open: the repair skill's new law points), `DOCUMENTATION.md`, `CHANGELOG.md`

**Interfaces:**
- Consumes: `who_the_law_covers` (Task 2); `law.cited_text` for run-together parts (Task 1).
- Produces: a skill named `repair_not_made`, description: "Something in the home needs repair, or something the lease
  promises is broken or closed, and the landlord has not fixed it." Fact names, used by Task 4's stories:
  `problem`, `problem_noticed_date`, `home_type`, `cause`, `repair_notice_delivered` (the notice to end the lease,
  YYYY-MM-DD), `withhold_notice_delivered` (the notice not to pay rent, YYYY-MM-DD), `rent_paid_since`,
  `eviction_filed`, `code_complaint_date`.

- [ ] **Step 1: Write `skills/repair_not_made.md`** from `../v1/skills/repair_not_made.md` and statutes 83.51,
  83.56, 83.60, 83.55, 83.64, 83.47, 83.505, in the spec's format (sections 1 to 7) and with the spec's content
  (Whose job it is; the five options; the not-settled points, each inside its condition; the other skills).
  - The deadlines are exactly `count_days(repair_notice_delivered, 7)` and `count_days(withhold_notice_delivered, 7)`.
    The 83.60(2) registry period is stated, quoted, and marked as a date the tool does not count.
  - "What the lease adds": the items it promises, who repairs them, closures, fees; what each option does with them
    (ending the lease may reach a material lease provision; withholding never does; 83.55 does; 83.47(1) two
    readings).
  - Mistakes to avoid: v1's list, plus: holding back rent over an item only the lease or 83.51(2) names; saying 83.51
    requires air conditioning; stating a standard for "material"; counting from the day a notice was sent.
  - The no-lean line, word for word from the deposit skill.

- [ ] **Step 2: Run `$PY law.py` and `$PY tests.py`.** Expected: "OK   repair_not_made: N of N quotes check out";
  "All checks passed."; `wc -w skills/repair_not_made.md` between 2,300 and 3,200;
  `grep -c "count_days(" skills/repair_not_made.md` at least 2; no em dash in it (`grep -c "$(printf '\342\200\224')" skills/repair_not_made.md` is 0).

- [ ] **Step 3: AUTHOR.md, Open, a new item:** the repair skill's new law points, one line each with where it sits
  in the skill: options 3, 4, 5; the lease-promised items and 83.47(1); air conditioning named nowhere in 83.51; pest
  treatment (83.51(2)(a)); screens; the reading of "terminated or altered by the parties".

- [ ] **Step 4: Update DOCUMENTATION.md and CHANGELOG.md, and commit** (`skills/repair_not_made.md AUTHOR.md
  DOCUMENTATION.md CHANGELOG.md`): "The repair skill, drafted for the author's review".

### Task 4: The repair stories and their keys

**Skills:** superpowers:verification-before-completion.

**Files:**
- Create: `comparisons/each_skill/repair_not_made/stories.json`
- Create: `comparisons/each_skill/repair_not_made/lease_repairs.txt` (a copy of `comparisons/skills/lease.txt` with a
  new clause 11, MAINTENANCE AND REPAIRS: the landlord repairs the appliances it provides (refrigerator, stove,
  dishwasher, air conditioning) and keeps the pool open, may close the pool for upkeep, and asks for repair requests in
  writing through the resident portal)

**Interfaces:**
- Consumes: the fact names from Task 3.
- Produces: `stories.json` = `{"how_to_read": str, "sections": [str], "stories": [story]}`, where `sections` lists the
  statute sections the judge reads, and each story has the deposit stories' fields (`id` "repair-N", `title`,
  `today`, `facts`, `message`, `answer`, `points`, `mistakes`, `law`, `dates`), plus `lease` (a file in this folder;
  none means `comparisons/skills/lease.txt`) and `open: true` when the key turns on an open call.

- [ ] **Step 1: Write the seven stories** from the spec's draft list. Every story but one gives `school_housing`
  ("no, a private apartment complex, not tied to a school") in its facts; story 3 leaves it out. Story 2's facts give
  the date the notice was sent and a later `repair_notice_delivered`, and its key counts from delivery. Story 4's key
  makes "says the tenant may hold back rent over the pool or dishwasher" a mistake. Story 7 expects the deposit skill
  to be loaded too. Each point and mistake is written by meaning, as in the deposit keys; every quote in `law` is
  copied from `statutes/`.

- [ ] **Step 2: Check the keys.** From `comparisons/skills/`: `$PY check_key.py
  ../each_skill/repair_not_made/stories.json`. Expected: a line per story and "OK".

- [ ] **Step 3: Commit** (`comparisons/each_skill/repair_not_made/`): "Seven repair stories and their keys, for the
  author's review".

### Task 5: One test runner for every skill

**Skills:** superpowers:test-driven-development, superpowers:verification-before-completion.

**Files:**
- Create: `comparisons/each_skill/run.py`, `comparisons/each_skill/judge.py`, `comparisons/each_skill/grade.py`
- Create: `comparisons/each_skill/README.md` (how to run, the graders' rubric, and a results section per skill)

**Interfaces:**
- Consumes: `models.setup`, `models.CHAT_MODELS["sonnet-anthropic"]`, `models.add_line`,
  `models.lines_without_errors`, `models.read_lines`, `run_chat.answer_once`, `run_chat.progress`
  (`comparisons/models/`); `score.story_row`, `score.middle` (`comparisons/models/score.py`); `stories.json` (Task 4).
- Produces, in `run.py`:
  - `test_folder(skill) -> Path`: `comparisons/each_skill/<skill>/`. `results_folder(skill, dry=False) -> Path`: its
    `results/`, or `results/dry/`.
  - `version_file(skill, version) -> Path`: "new" is `skills/<skill>.md`; "v1" is `../v1/skills/<skill>.md`; any
    other name is `<test folder>/versions/<name>.md`.
  - `skill_folder(skill, version) -> Path`: a throwaway folder holding every file in `skills/`, with this skill's file
    replaced by the version's text. v1's body goes under the current skill's header, and the v1 folder leaves out
    `who_the_law_covers.md`, since v1's skill carries its own college note.
  - `all_stories(skill) -> list[dict]`, `chosen(stories, numbers) -> list[dict]` (as in `comparisons/deposit/run.py`),
    `pages_for(skill, story) -> list[dict]`.
  - Command line: `python run.py <skill> <version> [--stories 1,3-5] [--dry]`; answers into
    `results/<version>.jsonl`, 3 runs per story, the chat model Sonnet 5.5 from Anthropic.
- Produces, in `judge.py`: `pack(skill, folder, versions=("v1", "new"), dry=False)`, one packet per story with its
  answers shuffled (fixed seed) under labels like "repair-1-A3", plus `key.json`; each packet carries the story, its
  lease file, the statute sections from `stories.json`, and `RUBRIC`. `unpack(skill, folder, dry=False)` reads
  `grades-*.json` and writes `results/judge_opus_<version>.json`. `RUBRIC` is `score.STORY_PROMPT`'s instructions with
  "about their security deposit" made "about their dispute with their landlord"; a grade is
  `{"points_made": [bool], "mistakes_made": [bool], "other_error": str, "answers_first": bool, "reason": str}`.
- Produces, in `grade.py`: `python grade.py <skill> [--dry]` writes `scores.json` and `SCORES.md` in the test
  folder: per version, right, partly, and wrong on the settled stories, made-up dates, quotes checked and right,
  whether the skill was loaded (`skill in line["skills_loaded"]`, set over `story_row`'s deposit-only field), and
  each story's verdicts per run.

- [ ] **Step 1: Write `run.py`.** Then check its folders: `$PY -c "import run; print(sorted(p.name for p in
  run.skill_folder('repair_not_made','v1').iterdir()), sorted(p.name for p in
  run.skill_folder('repair_not_made','new').iterdir()))"` from `comparisons/each_skill/`. Expected: v1's list has
  `deposit_not_returned.md` and `repair_not_made.md` only; new's has those and `who_the_law_covers.md`.

- [ ] **Step 2: A dry run.** `$PY run.py repair_not_made new --stories 1-2 --dry` and the same with `v1`. Expected:
  "Done. 6 answers" each, in `results/dry/`, nothing sent anywhere.

- [ ] **Step 3: Write `judge.py` and `grade.py`, and run them dry end to end.** `$PY judge.py pack repair_not_made
  <scratch>/packets --dry`; write a grades file marking every answer's points made; `$PY judge.py unpack
  repair_not_made <scratch>/packets --dry`; `$PY grade.py repair_not_made --dry`. Expected: 2 packets with 6
  answers each, 12 grades unpacked, and a SCORES table with both versions. Then delete `results/dry/` and the dry
  score files.

- [ ] **Step 4: Write the README** (how to run; the rubric; the graders' instructions: read the packet, the lease
  file, and the sections; write `grades-<n>.json`; judge meaning, not wording). **Commit**
  (`comparisons/each_skill/run.py judge.py grade.py README.md`): "One test runner for every skill".

### Checkpoint: the author reviews before any live run

Show the author, in plain words: the new law points (AUTHOR.md, Task 3's item) with the lines of the skill that hold
them, and the seven stories' keys in short (the answer in a line each, and the mistakes that make one wrong). Make any
changes asked, rerun `$PY law.py`, `$PY tests.py`, and `check_key.py`, commit them, and go on only on the author's OK
to both.

### Task 6: The live run, graded and shown

**Skills:** superpowers:dispatching-parallel-agents (for the graders), superpowers:verification-before-completion.

**Files:**
- Create: `comparisons/each_skill/repair_not_made/results/new.jsonl`, `v1.jsonl`, `judge_opus_new.json`,
  `judge_opus_v1.json`, `scores.json`, `SCORES.md`
- Modify: `comparisons/each_skill/README.md` (Results: repair), `SLIPS.md`, `CHANGELOG.md`

- [ ] **Step 1: Run both versions** from `comparisons/each_skill/`, with the key in the environment:
  `$PY run.py repair_not_made new` and `$PY run.py repair_not_made v1`, in the background. Expected: 21 answers each,
  no errors, total logged cost under $8.

- [ ] **Step 2: Grade blind.** `$PY judge.py pack repair_not_made <scratch>/repair_packets`; three Opus subagents
  (model opus), each given two or three packets and the README's grader instructions, write
  `grades-<n>.json` there; `$PY judge.py unpack repair_not_made <scratch>/repair_packets`;
  `$PY grade.py repair_not_made`. Expected: every answer graded, SCORES.md written.

- [ ] **Step 3: Check the graders.** Read every answer graded partly or wrong, and every disagreement with the key
  that turns on a judgment call; note each in the README as the skill's fault, the test's, or a judge's call.

- [ ] **Step 4: Show the author a chart** (show_widget): right, partly, and wrong per version, and each story's runs,
  with the sample size, and the misses sorted. New slips go in SLIPS.md, one entry per kind with counts.

- [ ] **Step 5: Write the README's results and a CHANGELOG entry, and commit** (the results folder, SCORES.md,
  scores.json, README.md, SLIPS.md, CHANGELOG.md): "The repair skill test, run and graded". Then wait for the author's
  calls on the misses.

### Task 7: One round of fixes

**Skills:** superpowers:systematic-debugging (for each miss), superpowers:verification-before-completion.

**Files:**
- Modify: `skills/repair_not_made.md`; Create: `comparisons/each_skill/repair_not_made/versions/fixed.md` (a copy
  of the fixed skill, so the run can name it)
- Modify: `comparisons/each_skill/README.md`, `CHANGELOG.md`, and any test keys the author changes

- [ ] **Step 1: Fix the misses the author marks as the skill's,** each as a general rule for the skill, not a patch
  for its story. Run `$PY law.py` and `$PY tests.py`. Expected: all OK. New law points go to the author first.

- [ ] **Step 2: Rerun only the missed stories:** `$PY run.py repair_not_made fixed --stories <the missed ones>`;
  pack, grade blind with one or two Opus subagents, unpack, grade. Expected: the done line from the spec holds: new
  right at least as often as v1, no made-up date, every skill quote OK.

- [ ] **Step 3: Record and commit** (README results, CHANGELOG, SLIPS.md, the skill and its copy): "The repair
  skill's round of fixes". Then the whole-branch review and finish (Global Constraints, skills).

## Not in this plan

Pairs 2 to 4 and the unpaid-rent skill each get their own plan, reusing `comparisons/each_skill/`. Pointing the
deposit skill at `who_the_law_covers` waits until the deposit fixes are merged (a TODO.md item from Task 2).
