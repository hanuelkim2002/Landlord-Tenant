# Changelog

## 2026-10-19: v2 starts

v1 moved into `../v1/` with `git mv` (its CLAUDE.md renamed CLAUDE_v1.md). `v2/` made with v1's 40 statute files and
`index.json`, `.env.example`, `.streamlit/config.toml`, the starting prompt (`V2_PROMPT.md`), README.md, and CLAUDE.md.
The top level keeps a short README.md and CLAUDE.md, and the preview runs v2's page. Replaces v1 as the working version.

## 2026-10-19: the lease intake test

`comparisons/lease/`: the shortlist of methods (SHORTLIST.md), four made-up test leases (short, 46 pages, scanned,
broken text) built by `make_leases.py`, and 64 questions with their answers (`answer_key.json`), checked against the
leases by `check_key.py`. Nothing replaced; no method is built yet.

## 2026-10-19: lease answers judged by meaning

The answer key now lists the points a right answer must make and the mistakes that make it wrong, judged by meaning
by a second model (`gpt-oss-120b`), not by exact phrases. Only quotations are checked word for word. Two "not covered"
questions were replaced with cleaner ones. Replaces the key's `must_say` phrases and the model's "covered" flag.

## 2026-10-19: v1's lease method as a baseline

The lease comparison adds v1's own method (PyPDF2, the four-clause form, the exact-phrase search), run unedited from
`v1/` and scored like the three new methods, so the scores show the change from v1. Nothing replaced.

## 2026-10-19: intake time as its own metric

The lease comparison times each method's intake (PDF to ready for the first question, all its steps, the middle of
three runs) apart from its answer time per question. Replaces the README's single "time" line.

## 2026-10-19: the lease comparison, run and scored

Step 1 (four PDF readers, Gemma 4 for pages without text) and the three methods plus v1, 64 questions each, scored by
a judge that now sees the whole lease, with my review of its grades (`review.json`). Results in `SCORES.md`. The
prototypes in `prototypes/` stay until the author chooses. Replaces nothing in the app.

## 2026-10-19: lease method A chosen

The author chose method A (the whole lease in the prompt). The prototype code is deleted (in git at 784dd82). README:
five tools, no `search_lease`. AUTHOR.md and SLIPS.md started with the comparison's findings. Draft lease-reading
rules await the author's OK. Replaces the open lease question and the planned `search_lease`.

## 2026-10-19: lease-reading rules approved

Rules 1 to 4 for reading the lease are approved and in README.md, for the system prompt; rule 5 waits on AUTHOR.md
item 1. Replaces the draft in `comparisons/lease/README.md`.

## 2026-10-19: the skills test

`comparisons/skills/`: the shortlist of skill formats (an element checklist, worked examples, a short core with a
details file) with v1's skill as the baseline; a test lease; five deposit stories with an answer key whose quotes and
dates `check_key.py` checks against `statutes/`. Nothing replaced; no skill is written yet.

## 2026-10-19: skills answers ranked side by side

In the skills test the author ranks the four answers to each story side by side, blind (letters shuffled per story),
1 to 4; the judge's grades are shown only after. Replaces marking each answer right, partly, or wrong.

## 2026-10-19: the skills test, run and scored

Three versions of `deposit_not_returned` (`comparisons/skills/versions/`) and v1's skill answered five stories three
times each; the author ranked the first runs blind; the judge graded all 60, with my review. Results in `SCORES.md`;
AUTHOR.md items 3 and 4 and two SLIPS.md entries record the findings. Replaces nothing in the app.

## 2026-10-20: skill format A chosen

The author chose the element checklist, with open questions and `count_days` calls inside their conditions. The
skills prototype harness is deleted (in git at 50bd13b). Replaces the open skill-format question.

## 2026-10-20: v2 built

`config.py`, `law.py`, `record.py`, `lease.py`, `checks.py`, `tools.py`, `chat.py`, `app.py` (695 lines in all),
`tests.py` (22 checks, all OK), `skills/deposit_not_returned.md` (format A, 15 quotes checked), `setup.sh`,
`requirements.txt`, DOCUMENTATION.md. The preview attaches to the page instead of starting it. Replaces the first-build
items in TODO.md.


## 2026-10-20: OpenRouter for testing outside models

`config.py` has two gateways: UF (still the default) and OpenRouter, chosen with `GATEWAY=openrouter`, with Claude
Haiku 5.5 for chat and Gemini 3.8 Flash for lease pages by default. `VISION_MODEL` can now be set from the environment.
Temperature 0 is sent only on UF. `OPENROUTER_API_KEY` added to `.env.example`. Replaces the single UF gateway.

## 2026-10-21: model comparison

`comparisons/models/`: nemotron, haiku, gemini, and sonnet on the deposit stories and lease questions through the app's
own chat, and gemma, gemini, haiku, and sonnet reading lease pages, on the sample leases and the author's own lease
(kept in `private/`, out of git). Judge grades reviewed (`review.json`). Results in SCORES.md and AUTHOR.md items 6 to 9.
Nothing in the app replaced.

## 2026-10-21: every lease page read from its image by Haiku

`lease.py` reads every page from its image with Claude Haiku 5.5 on OpenRouter (`READER_GATEWAY`, `VISION_MODEL`).
`config.temperature(gateway)` and `config.client(gateway)` let the chat and the reader use different gateways. Replaces
PyMuPDF's text plus Gemma 4 for pages without usable text (`usable` moved to `comparisons/models/models.py`).

## 2026-10-21: Gemini 3.8 Flash for the chat

`config.py`: the chat now defaults to Gemini 3.8 Flash on OpenRouter (`GATEWAY=openrouter`), the author's choice after
`comparisons/models/`. Replaces nemotron on the UF gateway, which can still be chosen with `GATEWAY=uf`.

## 2026-10-21: the college-housing check asked once

`skills/deposit_not_returned.md`: the 83.42(1) check reads the lease first, asks one plain question only if the lease
is not clear, and saves the answer as `school_housing` so it is never asked twice. The lease counts as clear only if
nothing in it points to a school (an enrollment clause, student-only terms, school services, and other doubt all mean
ask). Replaces "say what you would need to know", asked in nearly every answer. Skill quotes: 15 of 15 check out.

## 2026-10-22: quote only the law and the lease; ask for lookups together

`chat.py` rules: rule 6 now says to put only the statute's or the lease's words in quotation marks and to say the rest
(what the tenant said, confirmed facts, messages they describe) in the model's own words. A new line asks for all
needed lookups in one step: one at a time, Gemini used up all 8 tool rounds, and 2 of 5 answers came back empty.

## 2026-10-22: the page's quote check finds the cite before a quote

`checks.py`: a quote is checked against a section cited just before it as well as just after it (`nearby_cites`), and a
quote mark only opens after a space, bracket, or bold mark, so the words between two quotations are no longer checked
as a quote. Replaces the cite-after-only search and the old pattern that paired any two quote marks. Two new tests.

## 2026-10-22: deposit skill gaps drafted; seven more deposit stories

`skills/deposit_not_returned.md`, a draft waiting on AUTHOR.md item 12: public housing (all of 83.49(4)), where the
notice went, a notice without the amount or the reason, a tenant who objected, a renewal (83.49(6)); 1,575 to 2,055
words. `comparisons/skills/stories_more.json`: stories 6 to 12 with four lease
variants. `check_key.py` takes a key file name and reads "(1)(a)" run together, as 83.491 writes it. Nothing replaced.

## 2026-10-23: a notice with no reason is not the required notice

`skills/deposit_not_returned.md`: a notice of a claim that gives no reason is not the required notice (one reading, the
author's call); only a notice without the amount gets two readings. Replaces two readings for either one missing.

## 2026-10-23: the deposit skill test

`comparisons/deposit/`: Gemini answers the twelve deposit stories three times with v1's skill, the old v2 skill, and
the new one, through the app's chat; graded blind by Claude Opus 5.5 subagents (`opus_judge.py`), with the model
test's judge kept to compare. Right of 30 (Opus): new 27 (0 wrong), old 25 (2 wrong), v1 19 (7 wrong). `comparisons/models/score.py`: the made-up-date check no longer
reads "July 2026" as July 20. Nothing replaced.

## 2026-10-23: Claude from Anthropic for the chat and the lease reader

`config.py`: a third gateway, `anthropic` (Anthropic's OpenAI-compatible endpoint, `ANTHROPIC_API_KEY`), now the
default for the chat (Claude Sonnet 5.5) and the lease reader (Claude Haiku 5.5). No other code changed. Replaces
Gemini 3.8 Flash and Haiku on OpenRouter as the defaults; both stay one setting away.

## 2026-10-24: six stories for the deposit skill's new parts

`comparisons/skills/stories_more.json`: stories 13 to 18 (a housing authority as landlord, a Section 8 voucher, a
claim sent to the old address, a claim with no amount, one with no reason, an objection made in time), with two new
lease variants (`lease_housing_authority.txt`, `lease_voucher.txt`). Keys checked by `check_key.py`. Not run yet.

## 2026-10-24: stories 13 to 18 run on Sonnet

`comparisons/deposit/`: `run.py` takes `--model sonnet` (Sonnet 5.5 from Anthropic, answers in `results/sonnet/`)
and `--stories 13-18`; `opus_judge.py` and `grade.py` take the model too. Right of 18 (Opus, blind): new 11, old 2,
v1 3. `comparisons/models/models.py` names Sonnet from Anthropic and prices it. Nothing replaced.

## 2026-10-24: four fixes from the Sonnet run

`skills/deposit_not_returned.md`: a point that is not settled leads the answer, with no lean ("probably yes"); a
proper notice is named as such in one sentence; under a reading where a letter counts, both option 2 dates are given.
`chat.py`: the rules no longer open "a tenant in Florida college housing", which led the model to say the tenant
called it college housing. Replaces those lines.

## 2026-10-24: the four fixes rerun

`comparisons/deposit/`: the fixed skill (`versions/fixed.md`) on stories 6, 8, and 14 to 17 on Sonnet, 16 of 18 right
(was 8). `run.py` takes a list of stories and the version `fixed`; `opus_judge.py` and `grade.py` take the versions.

## 2026-10-24: the Section 8 reading names the rent and the deposit

`skills/deposit_not_returned.md`: the second reading for a private landlord in a housing program now says a program
that sets or limits "the amount of the rent or of the deposit", as 83.49(4) does. Replaces "the amount", which led
answers to drop the rent. Story 14 rerun on Sonnet: 3 of 3 right (was 1 of 3).

## 2026-10-24: all 18 stories on Sonnet with the current skill

`comparisons/deposit/`: 37 of 48 settled answers right (`SCORES_opus_sonnet_fixed2.md`). Stories 13 to 18 rose from 11
to 15 of 18 on the same model; stories 1 to 12 fell from 27 to 22 of 30, but they ran on Gemini before. Nothing replaced.

## 2026-10-25: the date rule, reworded

CLAUDE.md, README.md, DOCUMENTATION.md, `tools.py`: the model never works out a date; code does all date math;
`count_days` is the only date math for deadlines. Replaces "`count_days` is the only date math", so code can count
the days since the tenant's last message (the memory, next entry). No code behavior changed.

## 2026-10-25: memory, a timeline of the dispute

`record.py`, `tools.py`, `chat.py`, `app.py`: each matter keeps numbered timeline lines (`save_line`, the sixth tool;
every version in the history as `line_saved`), and after a gap of a day the prompt gets SINCE LAST VISIT (the days
since the last message, counted by code, and the facts confirmed since). Rules 9 and 10; the page shows the timeline.
Replaces memory by the old chat and the facts alone (the old chat stays). Spec and plan in `docs/superpowers/`; the
live test in `comparisons/memory/`.

## 2026-10-25: "open" means waiting for one thing; save_line lists the open lines

Rule 9 and `save_line`'s description: a line is open only while it waits for one specific next thing; when that
happens, the line that waited is closed. `save_line`'s reply now lists the lines still open. Replaces "open while
something is still waiting", read as "the dispute goes on". Memory test: the old line closed in 15 of 15 answers
with both, 13 of 15 with the wording alone, 3 of 9 before.

## 2026-10-26: the deposit skill's law points signed off

`skills/deposit_not_returned.md`: a notice with the reason but without the 15-day warning or the objection address
now gets two readings, as one without the amount does. Replaces "treat it as the required notice". The court costs
part adds that the court hears these cases sooner (83.49(3)(c)). AUTHOR.md item 12 closed; item 14 (holdover) opened.

## 2026-10-26: main merged; the signed-off skill checked on Sonnet

Main's memory timeline merged in; AUTHOR.md's deposit items renumbered 12 to 14. `comparisons/deposit/run.py` adds
the version `fixed3` (the skill after the sign-off). Stories 16 and 18 on Sonnet, 6 answers, no errors
(`comparisons/deposit/README.md`, fifth run). Nothing replaced.

## 2026-10-26: two stale AUTHOR.md items brought up to date

Item 6 now names Claude Sonnet 5.5 as the chat model (the 2026-10-23 decision), with Gemini one setting away.
Item 11 gives today's line counts (831 without `tests.py`, 1,030 with). Replaces "Gemini is the chat model" and the
counts from before the deposit merge. No code changed.
