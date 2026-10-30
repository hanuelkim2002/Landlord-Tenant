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

## 2026-10-26: three stale AUTHOR.md items brought up to date

Item 5 now says leases, messages, and facts go to Anthropic, and item 6 names Claude Sonnet 5.5 as the chat model
(both the 2026-10-23 decision). Item 11 gives today's line counts (831 without `tests.py`, 1,030 with). Replaces
"the chat to OpenRouter and Google", "Gemini is the chat model", and the old counts. No code changed.

## 2026-10-27: a short plain answer first, each point behind a click

`chat.py`: a "Writing the reply" rules block (3 to 5 plain sentences and the question, then a DETAILS line and a `###`
question heading per point; everyday words; "it" only when it can mean one thing), rule 8 ends the short answer, and
`split_reply` cuts a reply at DETAILS. `app.py`: `show_reply` shows the short part, then one closed box per point.
Replaces one long reply shown whole; old replies still show whole. Rules about 700 words (cap raised from 400).

## 2026-10-27: the plain replies test, run and scored

`comparisons/plain/`: Sonnet answered the 18 deposit stories 3 times with the old rules and the new (108 answers,
$10.25), graded by Opus subagents. New against old: short part 127 words against 462, unexplained legal words 7
against 135, right 41 against 40 of 48. Unclear words 21 against 79 after my review, 39 against 99 on the graders'
counts (the same per 100 words). Missed: the 100-word short part; on the graders' counts, the unclear-words median.
Reply time 24.1 against 19.9 seconds. AUTHOR.md item 15; four new slips in SLIPS.md. Replaces nothing in the app.

## 2026-10-27: the plain replies test's two calls decided

AUTHOR.md item 15: the short answer stays as it is (median 7 sentences, 127 words), and both exemptions in the review
of the plain counts are accepted, so the reviewed counts (21 unclear words against 79) stand. Replaces the open item.
No code changed.

## 2026-10-27: the intake speed test, run and scored

`comparisons/intake/`: the lease read one page at a time, 4, 8, and 16 at once, and 8 at once with smaller pictures,
3 runs on three sample leases, with v1's text step as a baseline (its Gemma step failed: UF's key expired). The
46-page lease: 132 seconds one at a time, 10 at 16 at once; every word and all 35 boxes right either way. Smaller
pictures cost less but did not save time. Replaces nothing in the app.

## 2026-10-27: the lease is read 16 pages at once

`lease.py`: `read_lease` reads the pages 16 at a time (`PAGES_AT_ONCE`, from the intake speed test), each through
the new `read_page`, which opens the PDF itself; the pages are kept in order. Replaces one page at a time. Live on
the 46-page sample lease: 11 seconds, every word and all 35 boxes right. `tests.py`: a stand-in reader checks order
and 16 at once.

## 2026-10-28: the quote checker finds run-together parts

`law.py`: `parts_of` reads a subsection written run together with its first paragraph, "(2)(a)", so cites like
83.51(2)(a), 83.51(4), and 83.60(1)(b) are found (they were not, and 83.51(1)(b) ran to the end of the section). The
page's quote check gains the same. `comparisons/skills/check_key.py` uses `law`'s splitter and takes a key file by its
path. Replaces the space-only marker and the key checker's own copy of the splitter.

## 2026-10-28: the shared skill, who the law covers

`skills/who_the_law_covers.md`: the deposit skill's college-housing check (83.42(1)), word for word, and one line on
83.42's other four exclusions, checked only when the facts point to one. The new skills load it instead of carrying
their own copy. AUTHOR.md records the method approved for the other skills; README.md and TODO.md follow. Replaces
"the others follow only after the author approves".

## 2026-10-28: the repair skill, drafted

`skills/repair_not_made.md`, from v1's repair skill and 83.51, 83.56, 83.60, 83.55, 83.64, 83.47, 83.505: whose job
the repair is (the statute's lists, the lease, who caused it), then five options (end the lease, hold back rent,
damages, retaliation, a landlord unable to fix it), each open point inside its condition. 42 quotes check out. What
it says beyond v1 waits for the author (AUTHOR.md item 16). Replaces nothing; v1's skill stays as the baseline.

## 2026-10-28: one test runner for every skill

`comparisons/each_skill/`: `run.py` runs any skill's stories through the app's chat on Sonnet (new, v1, or a frozen
version), `judge.py` packs the answers blind for Opus graders and unpacks their grades, `grade.py` writes the scores.
The repair skill's seven stories sit in `repair_not_made/`. Tried with a fake model end to end. Replaces nothing; the
deposit test keeps its own runner.

## 2026-10-28: the repair skill test, run and graded

`comparisons/each_skill/repair_not_made/`: seven stories, 3 runs each, on Sonnet; three Opus graders, blind. Right of
21: new 15, v1 5 (14 and 1 if every point is required). No made-up dates; $4.10. `grade.py` counts only required
points, as the rubric says. Misses sorted in the README; five SLIPS.md entries. AUTHOR.md item 16 approved. Replaces
nothing in the app.

## 2026-10-28: the repair pilot's round of fixes

`skills/who_the_law_covers.md`: when the lease settles it, the college check is one line inside another point, never a
point of its own (its repeated opening line dropped). Story 7's key accepts either ground for its two readings.
Stories 3 and 7 rerun: story 7 right 3 of 3 under the widened key (the first round was graded on the old one), story
3 1 of 3 (the "about a month" slip twice). `grade.py` applies
`review.json`, my changes to a grader's verdict. Replaces "say what it shows in one line" and the narrower key.

## 2026-10-28: fixes from the whole-branch review

`comparisons/skills/check_key.py` again offers `squash`, so `score.py` imports. `skills/repair_not_made.md` quotes
three rules it had narrowed: an 83.51(2)(a) item may be changed in writing in any home, an 83.505 e-mail counts when
sent (83.505(4)), and 83.60(2)'s motion to determine rent; some quotes put in plain words to stay under 3,200 words.
`grade.py` applies a `review.json` change only when its quoted words are in the answer, never to a dry run. AUTHOR.md 17.

## 2026-10-28: the repair skill's lease step, general

`skills/repair_not_made.md`: anything the lease says comes with the home, or that the landlord keeps up, counts,
named or not; two worked examples show the handling (a broken dishwasher, a pool closed under a clause). Replaces the
example lists of amenities and the air-conditioning-only rule. Some quotes put in cited plain words (3,196 words).
Two new repair stories, 8 and 9, use amenities the skill never names (furniture, covered parking). Not yet run.

## 2026-10-28: the repair keys take the author's answers

`comparisons/each_skill/repair_not_made/STORIES_REVIEW.md` reviews the nine stories and keys; the author's 25 answers,
at its end, are now in `stories.json`: softer wording on other rent defenses, either 7-day count in story 2, a careless
guest and a pool repair in the facts, three new dates, notes telling graders what not to count, and six sections more.
`skills/repair_not_made.md` option 3 adds attorney fees (83.48); 3,199 words. Replaces the keys as first written.

## 2026-10-28: the repair test, rerun on the new keys

`keys2` (the repair skill with the attorney-fees line, frozen) ran all nine stories; v1 ran stories 1, 4, 5, 8, 9 and
its first-round answers to 2, 3, 6, 7 were regraded. Right of 27: keys2 19, v1 12; about $4.05. The first round's
answers, grades, scores, and `review.json` moved to `results/round1/`. Replaces SCORES.md's first-round scores.

## 2026-10-28: the quote check reads two more ways of writing

`checks.py`: a new `plain()` drops the space before a section number's "(" on both sides, since the stored statutes
write "s. 83.51 (1)" and replies "s. 83.51(1)"; ". . ." now marks a cut like "...". Seven right quotes in the repair
rerun had shown "Does not check out". Two tests added. Replaces the check's exact-spacing match.

## 2026-10-28: five ways to stop the model counting time spans, side by side

`comparisons/each_skill/spans.py` counts the spans in answers and sorts them. Five versions on five repair stories:
v1's date rule and rule 7 naming spans each cut model-counted spans from 3 of 15 to 1; code's day counts raised it to
5 (3 with the rule). Right answers 12 to 14 in all. Results in `repair_not_made/results/spans/`. Nothing in the app
changed yet; AUTHOR.md 19 asks which way to take.

## 2026-10-28: rule 7 names time spans

`chat.py` rule 7 adds: how long something has lasted or how long until a date, and whether one date will have passed
by another, are said only in the tenant's own words, or not at all. In the side-by-side test it cut model-counted
spans from 3 of 15 answers to 1. Replaces the rule's dates-only wording. One test added.

## 2026-10-28: the repair skill tested under the new rule 7

The repair skill ran all nine stories under rule 7's new wording, graded blind beside keys2's rerun answers by the
same graders: right 24 of 27, against 20; spans the model counted itself fell from 3 to 0 by `spans.py` (the graders found
1 against 4). Results in `comparisons/each_skill/repair_not_made/results/rule7/`; about $2.50. Nothing in the app
changed.

## 2026-10-29: three fixes from the repair test under rule 7

`skills/repair_not_made.md` option 1: option 2's notice is not one of its conditions, and in a suit for unpaid rent
only the 83.51(1) defense needs it (83.60(1)), with one more mistake to avoid. `chat.py`: rule 7 names vague spans and
allows the date a problem began; the reply rules' example heading is "### Did your letter count as notice?", replacing
"### Does Florida's deposit law cover you?". Two tests changed, one added. Not yet run live.

## 2026-10-29: the repair test after the three fixes

All nine repair stories on the fixes, graded blind beside the rule 7 run: right 26 of 27, against 25; spans the model
worked out itself 0, against 1. `comparisons/each_skill/spans.py` now finds spans with no number ("several days",
"for weeks"), replacing reading them by hand. Results in `repair_not_made/results/rule7fix/`; about $2.43.

## 2026-10-30: leaving early and the 7-day notice, drafted

`skills/wants_to_leave_early.md` and `skills/notice_received_violation.md`, from v1's skills and the statutes they rest
on, in the repair skill's format; 56 and 51 quotes check out. `comparisons/each_skill/`: 8 and 9 stories with keys and
new leases, and `REVIEW_leave_and_notice.md`, with the new law points and ten questions (AUTHOR.md 21). Two independent
readings of the drafts, fixes applied. Not run yet. Replaces nothing; v1's skills stay the baseline.
