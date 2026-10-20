# Skill format comparison

Which way of writing a skill should v2 use? Tested on one skill, `deposit_not_returned`. The methods are in
SHORTLIST.md: A, an element checklist; B, worked examples; C, a short core with details in a file read when needed;
and v1's skill as it is, as the baseline.

## The test

- `lease.txt`: one made-up lease for every story (Apartment 12, Lakeview Terrace; ended July 31, 2026; deposit
  $1,050 in a non-interest-bearing account; notices to the tenant go to the forwarding address; no e-mail notices).
- `stories.json`: five deposit stories, each with the tenant's message, the facts the record holds (confirmed), the
  date that counts as today, and the answer key:

| Story | What it tests | The right answer, in short |
| --- | --- | --- |
| 1. No word at all | The 30-day notice rule, plainly met | Yes, all $1,050: no notice of a claim within 30 days |
| 2. Fifteen days gone, thirty not yet | Knowing what is not settled yet | Not yet: the landlord can still send a notice until day 30 |
| 3. Left early, told the manager by text | The 7-day notice on leaving early, 83.49(5) | Not for that reason: the landlord was relieved of the notice, but the tenant keeps the right to the deposit |
| 4. A partial check, no explanation | Keeping part is a claim | Yes, the other $400: no notice of the claim |
| 5. The claim came by text | An open question stays open | Not settled whether a text counts (both readings); the $650 is overdue either way |

  Each answer key gives the points a right answer must make (judged by meaning, as in the lease test), the mistakes
  that make it wrong, the statute words each point rests on, and the dates from `count_days`.
- `python check_key.py` confirms each quote is word for word in the statute subsection it cites, and each date is
  right.

## How a test run works

1. **The skills.** I write `deposit_not_returned` three ways (A, B, C) from v1's skill and the sections it rests on
   (83.49, 83.505). The legal content is the same in all three; only the way it is written differs. Before any run,
   you see the three, with anything they say about the law that v1's does not. v1's skill is used unchanged.
2. **The chat, as v2 will run it.** For each story, nemotron gets the system prompt v2 will have (the 8 rules, the
   lease-reading rules 1 to 4, THE LEASE, the confirmed facts) with the skill already loaded, and the tenant's
   message. Tools: `count_days` (counting from the story's today), `get_statute_section`, and for method C a tool to
   read the skill's details file. Each story runs 3 times per method, to see how much answers vary.
3. **One shared harness** for all four, so only the skill differs. As with the lease, I built it myself rather than
   with agents. It was deleted after the choice; it is in git history at commit 50bd13b
   (`v2/comparisons/skills/prototypes/run.py`).

## How it is scored

- **By you, blind, side by side.** For each story, the four answers (one per method, from the first run) side by
  side, labeled W, X, Y, Z, with the order shuffled for each story so a letter does not tell you the method.
  You rank them 1 (best) to 4, ties allowed, with a note if you like. Only then do I show which method wrote which.
  Your ranks are the main score: the average rank per method over the five stories, and how often each came first.
- **By the judge** (`gpt-oss-120b`, not the tested model), shown only after your ranking, all 60 answers: the
  points and mistakes by meaning, with the statute sections and the lease in front of it; and whether the first
  sentence answers the question. I check its grades as in the lease test.
- **By code:**
  - **Short**: the skill's length in words.
  - **Quotes check out (skill)**: every quote in the skill is word for word in the subsection it cites.
  - **Quotes check out (answer)**: every quotation of 20 characters or more in an answer is word for word in
    `statutes/` or the lease.
  - **No dates made up**: every date in an answer is a fact's date or a `count_days` result.
  - **Time** per answer.

## The results

`SCORES.md` (the summary), `scores.json` (every answer and grade), `review.json` (my changes to the judge's grades),
`blind/` (the page you ranked, your ranks, and the key to the letters). `python score.py` rescores the saved answers.

## The decision (2026-10-20)

The author chose format A, the element checklist, with one change from the tested version: each open question's
readings and each `count_days` call go inside the condition that uses them, not in sections at the end. In the test,
A ranked best on the author's blind ranks (average 1.8, first in 3 of 5 stories), answered first every time, and was
half v1's length; every one of its misses came from something the model needed being filed in a later section.

