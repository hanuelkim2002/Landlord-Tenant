# Changelog

Newest first. One entry per change, dated. Say what was replaced as well as what was added, so a future
session can see why the code is the way it is.

## 2026-10-01

- `get_cases` takes a topic written with its case count or in other letter case (`tools.topic_named`). Was:
  only the exact name; in the eval after-runs the model once sent "Landlord's maintenance duties under 83.51
  (9)", copying the count from the prompt's CASE TOPICS list, and the tenant got the topic list instead of
  the cases. Smoke check.
- Classify: a detail of a covered situation (why it happened, its effect, what was paid or charged, what a
  notice says) is part of it, not a separate problem. Was: after "other" was allowed next to covered issues,
  the classifier added it for a partial payment with no receipt in a rent-notice story, in 3 of 3 eval
  after-runs, so the "may not be covered" note printed for a story the tool covers. Tried on all 16 eval
  stories (the rent-notice and mixed ones three times): "other" exactly where the story has an uncovered
  problem. One more `smoke_online` check.
- Eval scenarios: deposit_ghosted's tenant gives the forwarding address when the posture is chosen (the model
  asks for it, and draft_letter's ask carries it; the baseline was rerun for this scenario); a legality
  answer also passes with rule 2's "do not answer that"; "you should" inside "does not decide whether you
  should" is not counted; every covered story expects no not-covered note.
- The eval marks runs the gateway failed (`gateway_trouble`: run.py never came back, an empty answer where
  JSON was expected, or two unrecovered empty turns in a row) and counts them apart. Was: they counted as the
  model's misses; the first after-runs of 2026-10-01 lost 18 of 48 runs to an eight-minute gateway failure
  and looked far worse than the baseline for that reason alone. Both sides were run again at the same time.
- `reply_empty` events carry `finish`, the gateway's `finish_reason` for each empty answer. Was: only
  `recovered`, so an empty reply from the model could not be told from a gateway failure; the eval's first
  after-runs (2026-10-01) hit eight minutes in which nearly every call came back empty, and only the clock
  times showed it was the gateway. Smoke check extended.
- Rule 6: posture lines are written after their name only, as preserve: "[its line]". Was: "copy ... word for
  word in quote marks", which the after-runs of the eval followed with a label taken from the prompt's own
  layout ("PLAYBOOKS issue deposit_not_returned guidance postures:") in front of each line. A "Not:" with that
  label and the new "Instead:".
- Quote marks in a reply pair in order (`citations.quote_spans`, `unquoted`). Was: `QUOTED` needed 20
  characters between two marks, so after a short quote ("assert,") it paired the short quote's closing mark
  with the next quote's opening one and checked the words between them as a quote: three false cautions in
  one reply of the eval after-runs (2026-10-01), and a quote running over two lines (a lease clause with a
  blank line in it) did the same. Short quotes are still left out of the check. Two smoke checks.
- Intake no longer crashes on a model answer that is not valid JSON. Was: `deterministic.ask_json` parsed
  the first answer, and `run.py` stopped with a traceback when `fill_facts` (or `classify`) got malformed
  JSON: 3 of 51 intake attempts in the eval baseline, one run lost after two tries. Now `ask_json` asks again
  with `NOT_JSON` ("Your last answer was not valid JSON. Return ONLY the JSON object, nothing else."), up to
  three answers, and raises the last error only then. Two smoke checks with a stand-in model.
- Eval runner `dev/eval.py` and 16 eval scenarios (`dev/scenarios/eval_*.json`). Was: one live run per
  scenario, read by eye, or the rules trial's one-off scripts and scorer agents; two runs of the same setup
  had scored 0.50 and 1.00 slips per reply, so one run could not show whether a change helped. Now each
  scenario carries an `expect` block and runs several times, several at once, each under its own scratch
  tenant; code scores every run (expected results, tools called per turn, required and forbidden words,
  case topics, the not-covered note, cautions, empty turns, ids, deadline echo, two word screens) and writes
  readable transcripts. `--project` runs an older commit's worktree for a before-and-after comparison. The
  scenarios: one lay-tenant story per playbook, three not covered, one mixed, three with facts like a case in
  the wiki. A turn's required words are matched against what the tenant read, the program's footer line
  included, and footers are counted apart so the model's own lines can be told from the program's.
- Rules: four "Not:" / "Instead:" pairs from the eval baseline's slips (16 new scenarios, run on the code
  before today's changes). Rule 3: a lay question about time ("How long do I have to tell them I disagree?",
  "When do I have to tell them?") goes to `get_deadlines`; was answered with statute quotes alone in 3 of
  the 9 playbook stories. Rule 8: asked about courts, the model calls the topic on the same notice, deposit,
  repair, entry, rent, fee, or lease term even if it does not name the exact point; was "This tool has no
  cases on that." to "a notice that says cash only" with the three-day notice topic offered (2 of 3 runs).
  Rule 6: the tenant's words are the ask (was: "What exactly do you want the landlord to do?" after "asking
  for my $900 back"), and the posture lines are never retold without quote marks. Format line: no issue ids
  like deposit_not_returned. RULES 932 words, rule 6 156, rule 8 153.
- Classify flags a separate problem no playbook covers even when another one is covered. Was: its prompt said
  'Use "other" only if none of the situations fits', so a mixed story never got "other" and `run.py`'s
  "Part of what you described may not be covered" note (`NOT_COVERED`, which needs "other" next to a covered
  issue) could not print: in the eval baseline, a broken heater plus a landlord's remark about the tenant's
  religion was classified repair_not_made and lease_ending only. Now the prompt adds "other" for a separate
  uncovered problem, and says a detail of a covered problem (its effect on the tenant) is not one. Tried
  twice each on four stories: the mixed one gets other, a mold story with asthma does not, the roommate story
  is other alone, a nonpayment story is unchanged. Two `smoke_online` checks.
- Rules that can apply only sometimes go in only then (`agent.rules_for`). Was: all nine rules in every
  prompt (1,130 words); a rule about a letter nobody asked for was copied out of context in the trial ("How
  will you send it?", month-to-month story). Now rule 6 (letters) joins once a letter is in play (the
  tenant's words in the chat mention a letter or writing one, `LETTER_WORDS`, or the matter has a drafted
  letter), and rule 8 (cases) is in full only when CASE TOPICS has a topic, otherwise one line: no cases for
  these issues, never name one from memory, and the fixed reply. Rule 1's line on asking how a requested
  letter will be sent moved into rule 6, which already asked it. Rule numbers stay as they were.
  `system_prompt` takes the chat's messages (`prompt_from_record` passes them; `given_text` too).
  `RULES_FILE` still replaces the whole text. Three smoke checks, one on a scratch matter with no letter.
- The program prints "This tool does not decide whether any of this applies to you." under a reply that
  quotes the statute without saying the tool does not decide (TODO item 30, done). Was: only rule 1 asked the
  model to end a legality answer with "This tool does not decide that."; it left the line out in 1 of 3
  `deposit_cases` runs, and in 8 of the first 16 runs of the eval baseline (2026-10-01). `agent.show_turn`
  prints `NOT_DECIDED` (`not_decided_line`) and writes a `footer` transcript line. Rule 1 is unchanged, so a
  reply that has the model's own line gets no second one. Smoke check.
- Printing tools end the model's turn (TODO item 19, done). Was: after `get_deadlines` or `get_cases` the
  model wrote a reply, which rule 3 and rule 8 limited to "The deadlines appear above." and "The cases appear
  above. This tool does not decide ...", and which sometimes repeated a printed deadline line (4 of 18
  replies in the rules trial). Now both tools are `return_direct`: when every tool the model calls in a step
  is one of them, the agent stops after the tool and the chat loop prints what the program made, with no
  model reply after it. `get_cases` now prints something on every call: one line pointing up for a topic
  already printed, and, for a topic not offered, "This tool has no case topic named ..." with the matter's
  CASE TOPICS (was: nothing printed, a note to the model). Its receipt no longer tells the model what to
  reply. Rules 3 and 8: call the tool alone; the program prints and the turn ends. Smoke: a stand-in model
  that calls `get_deadlines` and would then reply is stopped after the tool; the get_cases checks updated.
- Quote check: an id alone in quote marks ("claim_notice_deadline") and an example right after "e.g." are no
  longer checked as quotes (TODO item 14, done). Was: both were flagged as misquotes in the gpt-oss runs of
  2026-09-30 (m-023, m-022), a caution the tenant saw for nothing. `citations.quoted_passages` skips them
  (`FIELD_ID`, `EXAMPLE`); only "e.g." counts as an example, so a real quote after "for example" is still
  checked. Three smoke checks.
- TODO: new item 31 (Interface), a Claude-style web page in place of the terminal, Streamlit recommended,
  starting with the chat's output returned as blocks instead of printed. Planning only; no code changed.
- Cases in the chat (TODO item 25, done). Was: the plan to load verified wiki pages into the prompt for the
  model to quote. Now, like the deadlines, the program prints and the model only asks: the prompt lists
  CASE TOPICS (topics of verified, tagged pages for the active issues' sections; "none for these issues"
  until the author verifies pages), and the new tool `get_cases(topic)` prints every eligible case on the
  topic, oldest first, in the courts' quoted words with pin pages and the statute version read, ending
  "These are what courts said in other people's cases. This tool does not decide whether any of them
  applies to you." The tool returns content and artifact: the model gets only the names and cites printed;
  `show_turn` prints the artifact. A topic is printed once per session. New rule 8 (cases only through
  `get_cases`, only when asked, then only "The cases appear above. ..."); old rule 8 is now 9. Eligible:
  verified pages with a part II tag; untagged pages never load, so the author decides what loads by
  verifying and untagging (this answers the commercial-lease question). `WIKI_UNVERIFIED=1` loads unverified
  pages for development runs, marked "[not verified]". New event `cases_shown` (timeline full),
  `citations.check_case_cites` (a reporter cite in a reply must be one shown), transcript field `shown`,
  scenario `deposit_cases.json`, seven smoke checks. README: the cases are code output, like the timeline.
  Live runs with `WIKI_UNVERIFIED=1`: the first, with the full text returned to the model, printed the same
  topic four times and then twice, and on the fees question the model retyped the case quotes itself (one
  quote's marks changed, caught by the quote check); after the receipt fix and the once-per-session stop,
  three runs printed each topic once, replied only with the fixed line every time, and never named,
  quoted, or applied a case (expected results 8 of 9; the miss was a legality answer without "This tool does
  not decide that.", TODO 30). Not done: a reply check for applying language (the model no longer sees case
  text; no application in four runs). New TODO 29: the topic choice varies between runs.
- 50 So. 3d 503 (In re Revisions to Simplified Forms, Fla. 2010) added to `cases/` and the wiki, from a
  Southern Reporter PDF the author supplied. Was: not in `cases/`, because the Westlaw print marks its added
  and deleted words by formatting. The PDF shows the marks on the page (struck and underlined words) but
  its text layer merges them too ("Home andor Duplex"), so only the opinion (503 to 504, up to the
  appendix) is stored; the appendix of forms is not. New `dev/build_case_pdf.py` (one listed opinion from a
  reporter PDF: running heads dropped, star pages added, line-break hyphens joined, the Westlaw files'
  labels added). Wiki: a forms-decision page (untagged, with a scope note), linked both ways to Wilson v.
  Terwillinger (which cites it) and to the 1991 forms decision; the forms topic quotes the 2010 court's
  "We express no opinion as to whether the approved lease forms comport with current law." TODO item 24's
  note on 50 So. 3d 503 removed. Smoke all checks OK; wiki check 122 pages, 0 problems.
- Case wiki: the remaining 65 opinions ingested, so every opinion in `cases/` has a page (81 case pages,
  40 topics; TODO item 24). Run as two workflows, with the author's go-ahead: nine agents read the
  opinions in full and wrote JSON drafts, each checked by code before hand-back (every quote word for word
  in its opinion); topics were settled by hand from the 77 proposed names (synonyms merged, one-offs
  dropped); the pages were rendered by code from the drafts (pins computed from star pages, links added both
  ways, each topic's Cases list built from the case pages); then six agents wrote the 27 new topic pages and
  extended 8 existing ones, and three reviewers read all new prose (39 case-page and 12 topic-page lines
  reworded). By hand after: duplicate topic links removed, Lockamy and Wolf untagged (their part II
  sections come only from a dissent or from counsel's requested instruction), Ray added to Landlord's
  liability for criminal attacks on tenants, a statute year no longer read from "§ 1983". 28 pages are
  untagged with scope notes. Found: many candidate-list entries are commercial leases, criminal cases, or
  not landlord and tenant at all (listed in `wiki/log.md`). `python wiki.py check`: 121 pages, 0 problems,
  0 warnings. No page verified.
- Case wiki: a case page may have no section tag (`sections: []`) if it carries a `scope_note` saying why
  (part I, before the Act, a federal case, or a general case citing no section of ch. 83). Was: every case
  page needed a part II tag, so the 24 remaining opinions that read none could not be ingested honestly
  (83.20 is not in `statutes/`). Such pages are for research and are never loaded for a tenant. `lint`
  refuses an untagged page without a note; the index lists untagged cases under "No section"; SCHEMA says
  when to use it. One smoke check. Decided with the author before ingesting the remaining 65 opinions.
- Case wiki: the other thirteen deposit opinions ingested (TODO item 24), each read in full: Atlantis
  Estate Acquisitions v. DePierro, Lewis v. Guthartz, Guthartz v. Lewis, Malagon v. Solari, Nardi v.
  Continental National Bank, Florida RS v. Nelson, Florida Bar re Approval of Forms (1991), Department of
  Business Regulation v. Stein, Florida Patient's Compensation Fund v. Rowe, Meli Investment Corp. v. O.R.,
  Xanadu of Cocoa Beach v. Lenz, Gilbert v. Jabour, Scruggs v. Sutton. With the pilot, every opinion in
  `cases/` citing 83.49 or 83.48 (the candidate list's 17, less 50 So. 3d 503, not in `cases/`). One topic
  renamed (Notice of how the deposit is held, now How the landlord holds the deposit and advance rent, since
  two new cases are about holding the money), eight new topics (Prevailing party fees under 83.48; How a fee
  award is computed; Interest on the deposit; Advance rent; Landlord's remedies after a tenant's breach;
  Applying an amended statute; Punitive damages against a landlord; Court-approved landlord and tenant
  forms). SCHEMA gains a layout for a forms decision and an "Also said" section. Topic pages record, in the
  courts' words, the changes in 83.48's wording (1977, 1983, today), the moves of the interest and advance
  rent provisions, Xanadu's footnote beside Scruggs on fees as costs, and Rowe on the "derogation of the
  common law" phrase Guthartz used. `python wiki.py check` caught one misquote of mine while writing (Meli's
  disposition), fixed; three prose lines that went beyond the opinions were reworded on reading. Noted for
  the author: Gilbert v. Jabour, listed under 83.51 in the candidate list, is a fee case. 29 pages, 0
  problems, 0 warnings; smoke all checks OK. No page verified.
- Case wiki pilot (TODO item 24, first part): `wiki/` with `SCHEMA.md`, `index.md` (built by code),
  `log.md`, three case pages (Durene v. Alcime, Casey v. Picinich, Plakhov v. Serova, each read in full from
  `cases/`), and five topic pages made as the cases raised them (Landlord's notice of claim on the deposit;
  Fees and costs in a suit over the deposit; Notice of how the deposit is held; Constructive eviction;
  Points not raised in the trial court). Each case page has its issues as questions, each with Rule and
  Reasoning quoted from the opinion with pin pages; topic pages quote today's stored statute beside the
  version the courts read and record how the cases relate (Plakhov distinguishes Durene; Durene's set-off
  sentence beside Plakhov's applying the deposit to damages; the 15-day period Durene read against today's
  30). New module `wiki.py`: `lint` (every quote word for word in its source and on its cited page, also
  across a page break; statute quotes in the cited subsection; no unsourced quote; links resolve; every case
  listed on the topics it names; front matter; index current; warnings for a tag the opinion never cites and
  a page changed since verified), `verify` (the author's sign-off, refused while a page has a problem,
  undone by any later edit through a hash), `write_index`, and `python wiki.py check | index | verify`.
  Before writing the smoke checks, each check was shown to catch its fault on a copy; one did not (a topic
  "listed" a case only through a quote's source link) and now reads only the topic's Cases list. Eight
  smoke checks; `config.WIKI`; CLAUDE.md guardrail (pages from `cases/` and `statutes/` only, run the
  checks after an edit, only the author signs off); `.obsidian/` gitignored. No page verified. Smoke: all
  checks OK; `python wiki.py check`: 8 pages, 0 problems, 0 warnings.
- README and TODO: the casebook becomes a case wiki (after Andrej Karpathy's LLM wiki). Was: one YAML file
  per statute section, each holding predefined questions with the cases that answered them; the author
  found fixed questions too rigid, and a question can rest on two sections (deposit fees: 83.49(3)(c) and
  83.48), while no playbook lists 83.48, so a file of its own would never load. Now: linked markdown pages
  in `wiki/`, one per case and one per topic, topics made as they emerge; statute sections are tags on a
  page. The wiki's prose describes and connects and never states the law; the tenant sees only the court's
  quoted words; a page reaches the chat only once the author verifies it, and an edit undoes that; tenant
  sessions never write to it. TODO items 24 to 26 rewritten for the wiki; 26 (`search_cases`) now says to
  reconsider it first, since there the model chooses what to look for (the unlicensed-practice line in
  Florida Bar v. Brumbaugh, discussed with the author); new item 28, whether computing a tenant's own
  deadline is closer to applying law to facts, for the author's professional responsibility professor.
  No code changed.
- `cases/`: 81 Florida appellate and federal opinions, the court's text only, one file per opinion
  (`448_So2d_1208.txt`), committed. Built by the new `dev/build_cases.py` from the author's Westlaw Find and
  Print file (82 opinions, the reporter cites of the case-pool candidate list), which stays outside the repo.
  The build leaves out Westlaw's own material (KeyCite flags, synopsis and holdings, West headnotes and
  their `[n]` markers, the copyright line, the negative-treatment table) and keeps the caption, attorneys
  and panel, the opinion with concurrences, dissents, and footnotes, star pages for pin cites, and parallel
  cites. A bracketed number beyond an opinion's headnote count is kept as the court's own (Malagon v.
  Solari's "[1116]"). Skipped: 50 So. 3d 503, the 2010 forms decision, whose print marks deletions by
  strikethrough (391 runs, the only opinion with any), which plain text would keep as current words; noted
  under TODO item 24. Checked against the print: every opinion's court text is in its file. New path
  `config.CASES`; CLAUDE.md lists `cases/` as read-only; six smoke checks (files present, each named for its cite, no
  Westlaw material, no headnote marker opening a line, attorneys and parallel cites present, the build on a
  hand-typed opinion). The print also confirmed Casey v. Picinich (573 So. 2d 76), marked unverified in the
  candidate list, and that Lucite Center begins at 492, not 493. Nothing reads `cases/` yet. Smoke: all
  checks OK.
- README: case law joins the plan (was listed under "Beyond the current plan": a case pool by section, no
  code). Purpose and the output framing add what courts that read the statute said; goal 3 and Skills add
  the court decisions for each issue's sections; the non-negotiables add case quotes from `cases/`, the
  neutral showing of cases (every case on a question, whichever side it favors, with court, year, and the
  statute version read; only author-verified entries reach the tenant; never whether a case applies), and
  `cases/` as a read-only corpus of the court's text only. The unit of legal knowledge adds the casebook:
  one file per section, organized by the question a court answered, each case's rule and reasoning quoted
  from the opinion. Decided with the author: the neutral framing, organization by rule and reasoning, and
  `cases/` committed. TODO.md gains a Case law section (items 24 to 27). No code changed.
- Live check of the notice's stated date (item 10's fix): `nonpayment_3day` (`t-test/m-001`) printed
  "beside it, from your record: notice stated payment date 2026-09-21" under the 2026-09-24 deadline; the
  model replied only "The deadlines appear above." (noted under TODO item 19). No code changed.
- The printed 83.56(3) deadline now shows the date the notice itself states beside it (TODO item 10). New
  optional clock field `shown_with` (a date element; `load_playbook` refuses anything else):
  `compute_deadlines` adds it to the row once that fact is confirmed, and `render_deadlines` prints
  "beside it, from your record: notice stated payment date 2026-09-21". Set on notice_received_nonpayment's
  three_day_demand_period, whose own open question already said the tool shows the notice's date next to
  the computed one; the playbook's failure modes asked for it too. Before, only the timeline showed both,
  and reporting it was left to the model, which did not. Playbook checks OK; two smoke checks.
- TODO.md, Model behavior tidied: items 4 to 23 were logged under the fifteen rules and the seven, and
  most are handled now. Taken off: 4, 11, 16 (saying what the law means), 7, 13 (dates the model worked out),
  8, 9 (confirming in the chat, calling facts confirmed), 15 (terse replies under the seven rules' wording),
  22 (a run record): none of these kinds in the current rules' trial runs; 5, 6 (misquotes, wrong
  subsections): `check_quoted` flags them when quoted; 17 (empty reply): retried in code; 20 (duplicate
  draft): stopped in code; 18 (gpt-oss-120b): a model comparison, nemotron kept; 23: fixed. Kept, with
  their numbers: 10 (the notice's stated date next to the 83.56(3) date, now a `render_deadlines` change),
  12 (a claim letter's printed date suggested as the date received; seen again with the current rules, 1
  of 3 claim runs; item 21 folded in), and 19, narrowed to the repeated deadline line. Numbers are not
  reused, so the smoke check names that cite items 5, 6, and 11 stay accurate. No code changed.
- Rules: the rest of TODO item 23. Rule 1 gains a pair for questions about whether something was legal,
  allowed, timely, or valid ("Not:" the fallback sentence with "whether the entry was legal" attached;
  "Instead:" quote the text on the point with its source, then only "This tool does not decide that.").
  Rule 2: the fallback "The lease and statute text I have do not answer that." is written exactly, with
  nothing after "that" (was "Add nothing."), and a pair on citing the subsection the words sit in (83.64(1)
  words were cited as 83.64(4)). Rule 3 names the echo `{ "deadlines": [] }`. Rule 4 adds "Please tell me:
  your monthly rent, the new rent, and the date you got the notice." as a "Not:" and says to read facts in
  ELEMENT STATUS. Rules now 1,028 words. Reruns of `entry_unannounced` and `rent_increase`, three each: all
  expected results; every legality question answered with sourced quotes and "This tool does not decide
  that." (9 of 9); no sheet facts asked in the chat; no cautions; no echoed deadlines. Offline checks OK.
- `render_deadlines` says "No deadlines: none of the deadlines this tool computes applies to your confirmed
  facts." when there are none (an issue with no clocks, such as landlord_entered_unannounced and
  rent_increased, or clocks whose conditions do not apply). Was: the heading "Deadlines, computed by the
  tool from your confirmed facts:" with nothing under it, after which the model echoed `{ "deadlines": [] }`
  in the 2026-10-01 trial (TODO item 23). One smoke check.
- Rules, rule 1: the "Instead:" line under "You must choose from the lease's notice methods" now applies
  only to a letter the tenant asked for, and says nothing about sending anything otherwise. Was: "quote the
  notices clause from LEASE PROFILE, then ask: How will you send it?", which the model asked in 2 of 3
  month-to-month runs with no letter requested (TODO item 23). Rerun of `month_to_month_end` three times:
  0 of 3 asked it; each answered "Do I have to give 30 days notice?" with the 83.57(3) quote and its source
  only; both 2026-10-31 dates printed; no cautions. Rules now 914 words. Offline checks OK.
- RULES replaced by version F of a trial of seven versions (`docs/trials/2026-10-01-rules/`, with the
  versions, the brief, the rubric, the scripts, and the results). Was: the seven rules of 2026-09-30, kept
  there as `rules_control.txt`. F states eight rules, each with "Not:" examples taken from real slips and
  the "Instead:" form, after a role paragraph and a format line (source first, no labels or field names).
  Trial: six designer agents wrote one version each under assigned strategies; each version and the
  control ran the three original stories 3 times (63 runs) and were scored blind by two scorer agents per
  story: control 0.47 slips per reply, F 0.00, with every expected result; D also scored 0.00 but missed
  the deposit-claim deadlines in 2 of 9 runs, and C left 3 replies empty. Confirmation round on the four
  new stories (24 runs): control 0.82 slips per reply and 9 of 12 expected results, F 0.13 (0.23 with three
  wrong-subsection quotes the program caught) and 12 of 12. F's remaining slips are TODO.md item 23. Rule
  numbers 1 to 7 keep their topics, so the references in `citations.py` and DOCUMENTATION.md hold; rule 8
  (offer nothing unasked) is new as its own rule. Offline checks OK.
- Four live scenarios for the playbooks no scenario covered: `entry_unannounced`, `rent_increase`,
  `leave_early`, `month_to_month_end` (expected results in each `about`; the dates come from
  `compute_deadlines`). Each also asks a question that invites legal advice. Dry runs found two things,
  fixed before committing: a short sheet key ("raised the rent") lost to the generic "Is that part of your
  situation?" in the driver's longest-match rule, so the scenario stopped; and the classifier read "I want
  to move out at the end of November" (month-to-month) as wants_to_leave_early and one longer wording as
  other, so the story now says the tenancy is ending. For the confirmation round of the rules trial.

## 2026-09-30

- `RULES_FILE` in the environment replaces `RULES` with that file's text for one run, like `AGENT_MODEL` for
  the model; the rules in `agent.py` stay the default. For a trial of several versions of the rules on the
  live scenarios without editing code. Was: the rules could only be changed by editing `agent.py`.
- Second run of the harness setup logged in TODO.md (item 22; m-029 to m-032): 1.00 slips per reply against
  0.50 in the first run, 0.75 over both. The duplicate-draft stop worked live. No code changed.
- `draft_letter` does not draft the same letter twice in one session: if this session already drafted the
  file and the new text is identical, nothing is written or logged and the tool says so (the chat loop
  prints that line). Before, the repair run (m-026) wrote the same letter twice with two `draft` events,
  after the model asked for a posture it had already used. A changed letter, or one in a later session, is
  drafted as before. One smoke check: same letter twice gives one draft, a changed reply period gives a new one.
- Live runs after the harness fixes logged in TODO.md (items 19 to 21; m-025 to m-028, nemotron). With the
  same rubric: 0.50 slips per reply, was 1.00 with the new rules alone and 0.91 with the old; every
  scenario as expected; deadlines printed in full by code each time; postures copied word for word. No
  code changed.
- An empty reply is asked for again (`agent.show_turn`, `retry_empty`, `EMPTY_REPLY`, `NO_REPLY`; new event
  `reply_empty`). When a turn shows the tenant nothing (no reply text, letter, or deadlines; seen in m-018),
  the program sends the model a note asking it to reply and shows the second turn; if that is empty too, it
  prints "[Check: no reply came back from the model. Please ask again.]". Before, the tenant saw a blank
  prompt. The printing part of `chat` moved into `show_turn`, unchanged except that a reply of only blank
  lines now counts as empty. Planned as "show the model's reasoning_content instead"; not done that way,
  since LangChain drops that field and it is the model's unchecked working, which would bypass rule 1.
  Two smoke checks with a stand-in agent: a recovered reply, and a second empty one.
- `propose_facts` takes a `said` shortened with "...": each piece must be the tenant's words (now
  `citations.is_in`, the quote check's comparison; was a whole-string substring after `squash`). In the
  gpt-oss-120b claim run (m-023) the model wrote "I just got a letter from the landlord..." and the
  refusal of claim_notice_received cost the scenario deposit_claim_received and two deadlines. The
  docstring says shortening is allowed only that way, and the refusal says so. Two smoke checks: pieces of
  the tenant's words pass, a piece the tenant never typed is refused.
- Deadlines are printed by code: the chat loop prints the turn's last `get_deadlines` result through the new
  `timeline.render_deadlines` (date, actor, clock, issues, status, rule and start date, cite, counting line;
  a clock with no date shows why; waiting issues with their open facts), as `draft_letter`'s result already
  was. Before, the model reported the result itself, and dropped parts of it: the counting line, status,
  and actor (m-017, m-022, m-023) or the whole reply (m-018). Rule 3 and `get_deadlines`' docstring now say
  the program shows the result and the model is not to repeat or reword it (was: report what it returns,
  "Report both parts"). Four smoke checks: none ready, all fields, one issue ready and one waiting, a
  refused court-day count.
- Live runs of the new rules logged in TODO.md: on nemotron (m-017 to m-020) and on gpt-oss-120b (m-021 to
  m-024), scored against 22 replies from the old-rules runs with one rubric. Slips per reply: 0.91 old
  rules, 1.00 new rules, 1.17 new rules on gpt-oss-120b; the kinds changed more than the rate. Model items
  15 to 18, and harness item 14 (quote-check noise). No code changed.
- `AGENT_MODEL` can be set in the environment (`AGENT_MODEL=gpt-oss-120b python dev/live_run.py ...`);
  the default is still nemotron-3-super-120b-a12b. Was a fixed constant. For comparing models on the live
  scenarios without editing code. Checked before: the gateway lists only open-weight models; gpt-oss-120b
  calls the tools, llama-3.3-70b-instruct does not (no tool call, "Your input is incomplete"). Also found:
  nemotron returns a separate `reasoning_content` field that the chat loop never reads; replaying the empty
  repair reply (m-018) three times gave a normal reply each time, so the empty reply was intermittent.
- RULES rewritten: fifteen rules condensed into seven, most important first, replacing the old list in
  which each topic was split across two or three rules and the most-broken one (13, never apply a provision)
  came near the end as eight prohibitions. New 1 says what a reply is made of (quotes with their source,
  record entries, "the statute does not answer or settle this", questions) and keeps one sentence of
  prohibitions; 2 sources (old 1, 4, 8); 3 dates (old 2 plus the get_deadlines part of 3); 4 facts (old 3,
  9); 5 open questions; 6 letters (old 6, 11, 12); 7 messages (old 14, 15). Old 10 (ask whose notice is
  meant) dropped: the classifier fix and the sheet's questions cover it. Behavior changes, approved by the
  author: no letter offers or next steps unless asked; posture lines copied word for word from the playbook
  (paraphrasing them is where TODO items 6 and 11 came from); the notices clause quoted without choosing a
  delivery method; every date must come from the record; no provision in the model's own words; "you said"
  for anything unconfirmed. 620 words, was 676. The mapping from old numbers is in DOCUMENTATION.md, and
  TODO.md's mistake log keeps the old numbers. Offline checks OK; live scenarios follow.
- Two model slips from the live claim run (`t-test/m-015`) logged in TODO.md: item 9 seen again (unconfirmed
  dates listed as confirmed before the sheet), and new item 13 (a lease end date, 2026-09-30, that is
  neither the lease's nor the tenant's). No code changed. The run itself gave the expected deadlines
  (objection 2026-10-10, remit 2026-10-22, the shared claim-notice deadline once).
- `check_cites` skips cites inside a quoted passage (20 or more characters in quote marks, the passages
  `check_quoted` covers). Before, it read every cite in the reply, so the live claim scenario (`t-test/m-015`)
  flagged "83.505" from inside a correct quote of 83.49(3)(a) ("in accordance with s. 83.505"), a false
  alarm; the replay had missed it because 83.505 is now loaded while deposit_claim_received is active, and
  in m-015 only deposit_not_returned was. A short quoted cite ("cite": "83.64") is still checked. Two smoke
  checks added. The replay now flags only m-009's 83.505, which is outside any quote.
- deposit_claim_received: `sections` is now ["83.49", "83.505"], was ["83.49"]. Its open questions
  (`receipt_date`, `email_notice_conditions`) quote 83.505, but 83.505's text never reached the prompt, so a
  reply mentioning it broke rule 8 and was flagged by the new cite check (m-001 twice in the replay). Now
  loaded while the issue is active. Playbook checks all OK. The replay's one remaining flag is m-009, a
  lease_ending matter, whose playbook does not mention 83.505. deposit_not_returned names 83.505 only in a
  clock's `delivery`, which the model never sees, so it is unchanged.

## 2026-09-29

- Quote check on the model's replies (`citations.quoted_passages`, `check_quoted`; `agent.given_text`;
  `check_reply` now takes the thread's messages and runs both checks). Every passage of 20 or more
  characters in quote marks is checked. With a ch. 83 cite next to it (after it on the same line, or in a
  heading just before it), the words must be in that section and, when one is named, that subsection; the
  caution names where they really are ("is in 83.49(3)(a), not 83.49(3)(b)"). With no cite, the words must
  be in the statutes or in what the model was given (its prompt, the lease quotes, the tenant's
  description, updates, and messages, the tool results). A failure gets the same "[Check: ...]" line and a
  new `quote_flagged` event (`timeline full`). Before this, rule 1 was only a prompt rule for replies;
  quotes were checked only in letters (`quote_is_real`) and playbooks. The comparison ignores spacing,
  curly versus straight quote marks, dash variants, and punctuation at a quote's ends, since a replay over
  the `t-test` transcripts showed each of these in quotes that were correct (straight apostrophes, the lease
  PDF's "confir mation", a closing period added). After those fixes the replay flags 1 of 33 quotes:
  "repair within 5 days" in m-007, words put in the tenant's mouth (they wrote "Give them 5 days to
  reply"). Covers TODO items 5 and 6 when the words are in quote marks; a paraphrase is still unchecked.
  The caution's last sentence now says "Check it against the source yourself" (was "Read it in the
  statute yourself"), since a quote's source may be the lease or the tenant's words.
- Cite check on the model's replies (new `citations.py`; `agent.check_reply` and `sections_shown`). After each
  reply, every ch. 83 cite in it is checked: the section must be in `statutes/`, must have been in the
  prompt's STATUTE SECTIONS or fetched with `get_statute_section` in the chat (rule 8), and a subsection
  such as 83.49(3)(b) must exist in the text. A failed cite gets a "[Check: ...]" line to the tenant under
  the reply, a `check` transcript line, and a new `cite_flagged` event (`timeline full`). Before this,
  rule 8 was only a prompt rule and nothing looked at the cites a reply contained. Subsections are found by
  their markers in the one-line section text; smoke checks that the markers run in order in all 40 stored
  sections. This does not catch TODO items 6 or 11: both cite a real subsection of a shown section, and the
  check cannot tell whether a cite fits what the reply says (a smoke check records that item 11 passes).
  Replayed over the `t-test` transcripts: 35 cites, 3 flagged, all 83.505 mentioned without a fetch
  (m-001, m-009).
- TODO.md tidied. Removed the model-behavior item on `classify` suggesting `lease_ending` for "my lease
  ended": the classifier now reads each label's description, and a wrong suggestion is turned down on the
  sheet instead of becoming active (both entries below). Removed the empty "Now" and "Data bank" headings
  and renumbered the model-behavior items 4 to 12. No code changed.
- Issues are suggestions the tenant confirms, replacing the rule that issues are only ever added (the
  author's decision). `record.add_issues` now suggests (`matter["proposed_issues"]`, event
  `issue_proposed`); the intake sheet asks each suggested issue first, "This looks like: <description> Is
  that part of your situation?", and a yes (`record.confirm_issue`, `issue_confirmed`) makes it active with
  its questions next, a no (`record.reject_issue`, `issue_rejected`) takes it out and prunes its pending
  suggestions. New chat commands `issues` and `drop <issue>` (`issue_dropped`). A related rule does not
  re-suggest a rejected or dropped issue unless its fact is confirmed with a new value; a later
  classification does. `other` is recorded at once (`issue_added`). Facts are suggested for suggested
  issues too (`record.candidate_playbooks`). `run.py` now stops after the sheet when no covered issue is
  active, so turning every suggestion down ends the visit as `other` does. `matter.json` gains
  `proposed_issues` and `rejected_issues` (older matters get them empty on load). Smoke: the related-issue
  section rewritten for suggestions, plus checks for reject, drop, not re-suggesting, and re-suggesting;
  `smoke_online.py` checks resume suggests without activating. Scenarios answer the new question; claim,
  repair, and not-covered scenarios rerun as expected (`t-test/m-012` to `m-014`).
- The classifier reads each label with the situation it covers (the playbook's `description`, now a
  `Playbook` field, through the new `corpus.issue_menu()`), replacing bare label names; the prompt also
  says a notice the tenant sent is not one the tenant received, and an empty answer becomes `other`. The
  repair story that was read as a landlord's rent demand four times in four now classifies as
  repair_not_made four times in four. Two descriptions reworded to name the event that starts the issue,
  since an update is classified on its own and the classifier would not assume a move-out
  (deposit_claim_received, deposit_not_returned). Checked on five stories; two new checks in
  `smoke_online.py`.

## 2026-09-28

- The tool stops when nothing it covers applies: if every issue in the matter is `other`, `run.py` says so
  and ends the session before the sheet and the chat, keeping the description (or update) and the `other`
  label in the record. Before, such a matter went on to an empty sheet and a chat with no guidance. When
  `other` comes with a covered issue, the tenant is told part of it may not be covered. `resume` now returns
  the issues it added. `dev/live_run.py` handles run.py exiting by itself; new scenario
  `dev/scenarios/not_covered.json` (run: stopped as expected, `t-test/m-011`). Investigated the repair
  misclassification: the classifier sees bare label names and read the tenant's own withholding notice as a
  landlord's rent demand; added to TODO.md with a proposed fix.
- `get_deadlines` works issue by issue: it returns the deadlines of every issue whose facts are all
  confirmed and lists the issues still waiting with their open facts, as `{"deadlines", "waiting"}`. It
  replaces a matter-wide refusal, under which one issue with open facts (such as one classified by mistake)
  hid every deadline in the matter. It refuses only when no issue is ready. Rule 3 updated. One new smoke
  check; three smoke checks read the new shape.
- `docs/structure/2026-09-28.md` with two standalone SVG diagrams (how a session works, where data is
  stored) and the history of the Skills plan versus what was built: a dated snapshot of the structure,
  not kept current (DOCUMENTATION.md is). No code changed.
- Two more live scenarios, both run: `dev/scenarios/repair_notice.json` (repair_not_made, 83.60(1)(b)
  date 2026-09-17, a preserve letter with its note) and `dev/scenarios/claim_letter.json` (a claim letter
  reported mid-chat: sheet in the chat, claim_notice_received no to yes, deposit_claim_received added with
  its questions, then four deadlines with the shared one listed once, objection 2026-10-10, remit
  2026-10-22). `dev/live_run.py` now uses the longest matching rule that still has answers, replacing the
  first match (a broad rule had taken a more specific rule's question). The first repair run showed that a
  wrongly classified issue blocks every deadline in the matter; added to TODO.md as a harness decision,
  with two model-behavior findings. Test matters `t-test/m-006` to `m-010` created (three repair runs, two claim runs).

## 2026-09-27

- New `dev/live_run.py` and `dev/scenarios/nonpayment_3day.json`: the live-test driver moved into the project.
  It replaces the scratch scripts (a shell loop feeding run.py through a file, and a separate sheet driver):
  it starts run.py itself, types the scenario's start lines, answers every sheet by the question on screen
  (including one that appears mid-chat), sends the chat lines, and prints the screen and the answers typed.
  Run once: the 3-day scenario gave 2026-09-24 again, both bad answers were asked again, `t-test/m-004` was
  created. DOCUMENTATION.md and CLAUDE.md's Running list updated.
- Rerun of the 83.56(3) live test with typed answers (`t-test/m-003`), after fixing the test driver, which
  had pressed Enter at every question because each question prints on the same line as the previous
  prompt. The new driver finds the question on screen by its type hint. Typed answers in other formats
  were saved normalized (9/18/2026 as 2026-09-18, $1,850.00 as 1850, n as false); two bad answers
  ("Sept 18", "maybe") were refused and asked again; two answers that differed from the suggestions were
  logged as corrections. `get_deadlines` again gave 2026-09-24. No code changed.
- Live test of the 83.56(3) court-day clock through `run.py`: a new matter `t-test/m-002` (sample lease,
  Alachua County) with a notice handed over Friday 2026-09-18 and stating "pay or leave by September 21".
  The classifier picked notice_received_nonpayment, the sheet confirmed the facts (county included), and
  `get_deadlines` gave 2026-09-24, skipping the weekend and Yom Kippur (Monday 2026-09-21, on the Eighth
  Circuit's list), with the counting line naming the memorandum. The timeline shows the delivery date, the
  notice's stated date, and the computed date side by side. One model-behavior finding added to TODO.md.
  No code changed.
- Court business days, for 83.56(3). New `calendars/` corpus (read-only, like `statutes/`) with the
  Eighth Judicial Circuit's official holiday memoranda for 2026 and 2027 (Chief Judge William E. Davis,
  issued 2025-07-08 and 2026-08-21, from circuit8.org, PDFs kept in `calendars/sources/`), extracted by code
  and checked name by name and date by date against the PDFs; the 2026 list also matches the circuit's web
  page. New `calendars.py` loads them and checks printed weekdays. Clocks gain `count: court_business_days`;
  `deterministic.court_days` counts inside `compute_deadlines`, skipping Saturdays, Sundays, and the
  circuit's holidays, and refuses (no date) for a county with no calendar or a year with no memorandum.
  notice_received_nonpayment gains the 83.56(3) clock `three_day_demand_period` and a `premises_county`
  fact, replacing "no clocks" for that playbook; 83.60(2) stays uncomputed. The two legal questions
  (how the days are counted, which holidays count) are recorded as open, as the author asked, in the
  playbook and in TODO.md. Found while researching: court holidays are set per circuit, not statewide.
  Seven new smoke checks (the calendar against its PDFs, four hand-checked counts including both
  refusals, the counting line). CLAUDE.md: `calendars/` guardrail.
- The stricter playbook checks moved into `corpus.check_playbook` / `check_all_playbooks`, replacing the
  quote-only check (and the one-off draft script): quotations in guidance and open-question prose are now
  checked too, plus a question per element, `applies_if` on yes/no facts, clock cites among `sections`, the
  guidance parts the tool reads, and shared fact ids with the same type and question. Both functions return
  the number of failures; `smoke.py` turns that into a named check. The new checks caught two things in the
  deposit playbooks, fixed: a quote with its period inside the quote marks ("last known mailing address."),
  and `claim_notice_date` asked in two wordings (now one: "What date did you receive the landlord's written
  notice about keeping part of the deposit?"). Checked that an altered prose quote fails. CLAUDE.md's
  playbook-check lines updated.
- Seven playbooks, version 0.1, written against `statutes/` in the format of the deposit playbooks:
  repair_not_made (83.51, 83.56(1) and 83.60(1)(b) 7-day notices), notice_received_nonpayment (83.56(3),
  83.60; no clocks), notice_received_violation (83.56(2)(a) and (b) 7-day periods), landlord_entered_unannounced
  (83.53, 83.67; no clocks), rent_increased (83.46, 83.57, 83.64, 83.425; no clocks, the stored text has no
  rent-increase notice section), wants_to_leave_early (83.49(5) 7-day notice, 83.682(1) servicemember
  30 days, 83.595), lease_ending (83.57(3) month-to-month 30 days for each party, 83.575, 83.58). Each
  carries the 83.42(1) exclusion quote for college housing, undecided. Two new related rules:
  withheld_for_repairs and reason_is_landlord_noncompliance bring in repair_not_made. Checked before
  installing by a stricter one-off script (145 checks: quotes in the prose too, a question per element,
  applies_if on yes/no facts, shared fact ids consistent); playbook quote checks 44 OK. New smoke section
  runs every playbook through the sheet, deadlines, and a letter; the "no playbook adds no sections" check
  now uses `other`. Checked live: one update about a broken AC, withheld rent, and a 3-day notice brought
  in both new issues with sensible suggestions. Clocks that cannot be computed yet, and folding the stricter
  checks into `check_all_playbooks`, went to TODO.md. Replaces the TODO item listing the seven to write.
- deposit_not_returned.yaml: `guidance.postures.notice_sufficiency` (printed under every letter for this
  issue as a note to the tenant) reworded to face the tenant. It replaces text that ended with an
  instruction to the model ("Say so when it is missing") and stated a conclusion ("cannot be cured
  afterward"). The new note says what the tool tracks and quotes 83.49(5); both quotes were checked by
  substring against `statutes/83.49.txt` before writing, since the playbook quote check does not cover
  guidance prose. Playbook quote checks all OK.
- deposit_claim_received.yaml: the fact `claim_notice_received_on` renamed `claim_notice_date`, the id
  deposit_not_returned already uses for the same date (when the tenant received the landlord's notice),
  along with the `tenant_objection_deadline` trigger and the question key. Facts carry across issues by
  id, so the tenant is now asked this date once instead of twice. In deposit_not_returned the fact still
  applies only once a notice is confirmed received; in deposit_claim_received it is always asked. Playbook
  quote checks all OK. Existing test matters keep the old key in `matter.json` as an unused leftover; both
  also hold `claim_notice_date` with the same date. Smoke fixture and counts adjusted; the "asked once"
  check now covers this date too.
- A deadline two issues share is listed once, tagged with both (the author's decision). New
  `deterministic.matter_deadlines` merges rows with the same clock id, cite, date, and status; both
  `get_deadlines` (rows now carry `issues`, a list, instead of `issue`) and the timeline use it, replacing
  their own per-playbook loops. `claim_notice_deadline` now shows once as
  `[deposit_not_returned, deposit_claim_received]`, and `timeline <issue>` keeps it under either issue.
  Three new smoke checks.
- Live run of the Skills chain on `t-test/m-001` (one issue): the tenant reported the claim letter in the
  chat, the model proposed the change, the sheet confirmed it, `deposit_claim_received` was added by its
  related rule and logged, its questions came up in the same sheet, corrections typed in the chat came back
  as changed rows, and the model then gave both issues' deadlines (objection 2026-10-10, remit 2026-10-22)
  with the remit condition stated the right way round. Two findings added to TODO.md: a shared clock
  listed twice (harness), and an "as you just confirmed" slip (model behavior). No code changed.
- Skills, step 3 of 3: statute sections come from the playbook. `statutory_hook: "83.49"` (read by no
  code) became `sections: ["83.49"]`, checked against `statutes/` by `load_playbook`; `system_prompt`
  loads the sections of the active playbooks, so an issue with no playbook yet adds none (a `lease_ending`
  label used to add 83.57, 83.575, and 83.58). `deterministic.ROUTING` (label to unverified section list)
  became `ISSUE_LABELS`, the labels `classify` can pick; its section lists moved to the TODO Playbooks
  item as unverified research candidates. README's Skills line now says guidance and sections load when an
  issue becomes active. The planned `load_skill` tool was dropped (the author's decision): code, not the
  model, decides what is in the prompt. The Skills TODO section is done. Two new smoke checks; checked
  that a playbook naming a section not in `statutes/` is refused.
- Skills, step 2 of 3: related issues as data. In both deposit playbooks `when: claim_notice_received ==
  true` (a string no code read) became `when: {fact: claim_notice_received, equals: true}`, typed in
  `corpus.py` (`Condition`, `RelatedIssue`) and validated after load. New `record.add_issues`, the only
  code that adds an issue, logging a new `issue_added` event (source and reason); `intake` and `resume`
  use it instead of writing `matter["issues"]` directly. New `record.add_related_issues`, run after every
  confirmed fact and in `resume`: a matching rule adds its issue at once, the sheet says "Added to your
  matter" and asks the new issue's questions in the same run, and the model's next prompt carries its
  guidance. `timeline full` shows added issues. CLAUDE.md names `add_issues` as the only door into
  issues. Playbook quote checks all OK after the YAML edits. Seven new smoke checks on a second scratch
  matter.
- Skills, step 1 of 3: the system prompt is rebuilt from the record on every model call. `build_agent` now
  gives `create_agent` a `dynamic_prompt` middleware (`prompt_from_record`) that calls the new
  `system_prompt()`; before, the prompt was built once and frozen for the session. The conversation is
  kept by the checkpointer as before. The `fact_status` tool is removed (the prompt's element status is
  now always current); rules 3 and 9 point at ELEMENT STATUS instead. This also settles the model-behavior
  item about the stale intake-time status. Two new smoke checks; checked live on a scratch matter that a
  fact changed in the record between two turns shows up in the model's next answer, with the history kept.
- TODO.md: dropped the note about clearing a test matter's history between runs; the smoke scripts now use
  scratch copies and never write to the test matters. No code changed.
- The timeline marks a fact the tenant corrected: "tenant (corrected, confirmed ...)" in the plain
  timeline, "corrected from <how> <suggested value>" in `timeline full`, replacing the suggestion's own
  tag (a corrected `early_or_periodic = False` used to read "inferred"). New `timeline.corrected`. The
  scratch smoke run now corrects two suggestions on the sheet; four new checks.
- `build_letter` strips a trailing period from the ask before adding its own, so a request ending in "."
  no longer prints ".." (seen in the first live run). One new smoke check.
- Stale suggestions are cleared: new `record.prune_proposals`, called by `confirm_fact`, `intake`,
  `resume`, and `propose_facts`. It drops a suggestion only when it can never be asked (the lease gives
  the value, its condition is confirmed as no with no change pending, or no issue asks for it). Before
  this, suggestions such as `deposit_amount` sat in `matter.json` forever. The first version also dropped
  a suggestion whose condition was a confirmed no with a change to yes pending; the smoke run caught it
  (the notice date lost its suggestion once the tenant accepted the change), and pending changes now keep
  it. Four new smoke checks.
- A tenant fact that differs from the lease is shown next to it. Playbook elements gain an optional
  `compare_to: lease_profile.<field>` (checked by `load_playbook`); both deposit playbooks set it on
  `tenancy_terminated` against `term_end`. `check_elements` adds `lease_says`, the lease's exact words,
  when the lease value (new `lease_value`: printed dates, dollar figures) differs from the tenant's; the
  sheet prints "your lease says" with it, and the model sees it in the element status. The tool shows both
  and decides nothing. Before this, a tenant date a year off the lease's term end passed unremarked.
  Playbook quote checks all OK after the YAML edit. Five new smoke checks; the scratch run now asks the
  termination date on the sheet, so the note is tested where the tenant sees it.
- README.md: the playbooks in scope grow from six to nine, adding notice_received_nonpayment,
  landlord_entered_unannounced, and wants_to_leave_early, so every classifier label but "other" gets one
  (the author's decision).
- TODO.md: the `ROUTING` preloading item moved from "Harness and code" into the Skills `load_skill` item,
  since every label but `other` will get a playbook and on-demand loading replaces preloading. The
  Playbooks item now lists all seven playbooks still to write, each carrying its own checked section list
  in `statutory_hook`. The Skills `related_issues` item no longer names the removed `record_facts`.
  No code changed.
- Permanent smoke checks for code that writes to a matter, replacing the hand tests on throwaway copies.
  New `checks.py` (named OK/FAIL checks, a summary line, and scratch copies of the test matter that can
  only be made and removed under `matters/t-smoke*`). `smoke.py` gained 31 checks on `t-smoke/m-001`:
  sessions, `propose_facts`, the sheet, deadlines, `fact_status`, events, the transcript, the timeline.
  `smoke_online.py` gained 7 `resume` checks on `t-smoke-online/m-001` (2 of them depend on the model).
  Checked that the checks fail when they should: with the tenant-words test removed from `propose_facts`,
  exactly the two checks covering it failed and the scratch copy was still removed. The test matter's files
  are unchanged by smoke runs. CLAUDE.md: every named check must be OK, and a change to code that writes to
  a matter gets a check.
- Intake sheet, step 3 of 3: the model can no longer confirm a fact. `record_facts` is replaced by
  `propose_facts`, which only adds to `proposed` and checks each suggestion in code (the id is a fact of the
  matter's issues, the value fits its type, how is stated or inferred, and the cited words appear in what
  the tenant typed this session, from the new `record.tenant_words`). New read-only `fact_status` tool,
  replacing the element status `record_facts` used to return. The chat loop writes the tenant's message to
  the transcript before the model runs, runs the sheet after any turn that proposed a fact, and sends what
  the tenant confirmed to the model as a "[Program note: ...]" at the front of the next message (added
  after the first live run showed the model did not know the sheet had run). `run_sheet` returns the saved
  facts instead of a count. Rules 3 and 9 reworded. CLAUDE.md's "only door" line updated. Tested offline
  (one proposal taken, five refused for five reasons) and live on `t-test/m-001` (a date corrected in the
  chat, confirmed on the sheet, then deadlines on the next turn). The intake sheet item is done.
- Intake sheet, step 2 of 3: `run.py` runs the sheet after intake or resume (and on an existing matter with
  facts still open), then builds the agent. `intake` and `resume` no longer build the agent; they only
  update the record, and `start()` returns True when a matter is open. This way the prompt's ELEMENT
  STATUS is taken after the sheet. Tested live: new matter `t-test/m-001` from the sample lease, five facts
  confirmed on the sheet (one inferred suggestion corrected), and the model gave deadlines on the first
  question with no confirmation back-and-forth.
- Intake sheet, step 1 of 3: new `sheet.py`. `pending_rows` lists every changed, proposed, or missing fact
  of the matter's issues once per fact id; `run_sheet` asks them in the terminal one at a time, checks each
  answer against the element's type (`parse_answer`), pre-fills suggestions with the tenant's words,
  accepts `?` to skip, and saves through the new `record.confirm_fact`. That function is now the only code
  that writes a confirmed fact; it replaces the body of `tools.record_facts`, which now calls it. Every
  `fact_confirmed` event gains `confirmed_in` ("sheet" or "chat"). CLAUDE.md's "only door" line updated.
  Not called from `run.py` yet. Tested offline on a throwaway copy of `t-test/test-002` with scripted
  answers (corrections, bad input re-asked, a changed fact, an applies_if fact appearing, a skip).
  This replaces the planned code-side `confirm_facts` guard.
- Sessions, step 2 of 2: transcripts. `record.append_transcript` writes to
  `matters/<tenant>/<matter>/sessions/<session id>.jsonl`; `agent.chat` writes every new message of each
  turn (tenant, model with its tool calls and arguments, tool results) and every `timeline` command.
  `timeline full` puts the transcript path next to "session started". Tested live on `t-test/test-002`:
  the transcript held the question, both tool calls with arguments, both results, the reply, and the
  command; the session's tagged events matched the visit. The sessions item is done.
- Sessions, step 1 of 2: `record.start_session(how)` / `record.end_session()` log `session_started` and
  `session_ended`, and while a session is open `append_event` tags every event with its id (a time-ordered
  uuid7). `run.py` opens the session once the matter is chosen, before intake or resume, and closes it after
  the chat. The chat's thread id is now the session id (was a fresh uuid7 per chat). `timeline full` shows
  sessions. `render_timeline` sorts by date only, keeping the order rows were added within a day; before,
  same-day rows sorted alphabetically, which would have put "session ended" before "session started".
  Tested on a throwaway copy of the test matter.
- TODO.md reorganized by the author's priority: structure and code first, model behavior later. "Guards and
  known issues" split into "Harness and code" and "Model behavior (later)"; playbook data items moved under
  "Playbooks". The `lease_ending` item split into its code half (`ROUTING` preloading sections for issues
  without a playbook) and its model half (the classifier). New harness item for stale proposals. No code
  changed.
- Resume, step 3 of 3: `start_existing` asks "Anything new since last time?" after loading a matter; text
  goes to `agent.resume`, an empty answer straight to chat. `ask_description` in `run.py` became
  `ask_text(prompt)` and serves both questions. Tested live on a copy of the test matter
  (`t-test/test-002`, so `test-001` stays one issue for the smoke scripts): the claim-letter update added
  `deposit_claim_received`, the model showed `claim_notice_received` as false against true and recorded
  true, the claim facts were confirmed, and `get_deadlines` gave the objection date (Oct 10) and the remit
  date (Oct 22). Timeline shows the update. Two rule slips from that run added to TODO.md. The resume item
  is done.
- Resume, step 2 of 3: `agent.resume(update_text)` for an existing matter. Logs the update verbatim as a
  new `tenant_update` event (the description keeps the first story), classifies only the update, appends
  new issues without removing any, runs `fill_facts` on the update for every active playbook, drops values
  equal to confirmed facts, and lets a newer proposal replace an older pending one. The timeline shows a
  "tenant update" row. Nothing calls `resume` yet. Tested on a throwaway copy of `test-001` with a
  claim-letter update: `deposit_claim_received` added, `claim_notice_received` shown as changed from False
  to True, shared facts known in the new issue, the notice's dated and received dates proposed separately.
- Resume, step 1 of 3: `check_elements` has a fifth status, `changed`, for a confirmed fact whose id also
  has a different value waiting in `proposed`. The row carries both values and the tenant's words; before
  this, any confirmed fact read as `known` and a differing proposal was invisible. Only confirmed facts can
  be changed this way, not lease values. `get_deadlines` now also waits on changed rows. Rule 3 says to show
  both values and record whichever the tenant picks. `smoke.py` gained an offline block that checks all of
  this with a hand-typed update.
- Resume decisions written into TODO.md (A to D), replacing the open question on what `intake` classifies
  for a returning matter. Checked offline that facts shared by element id already carry across issues.
  Added a TODO item for the one fact the two deposit playbooks name twice. No code changed.

## 2026-09-26

- Matter structure, step 3 of 3: `run.py` rewritten around `start()`, which asks new or existing. New:
  pick a tenant or make one, `record.new_matter`, lease path asked (replaces hard-coded `lease.pdf`),
  lease read, description typed by the tenant (replaces the hard-coded sample), intake. Existing: pick from
  `list_matters`, `load_matter`, straight to chat with no re-intake. `agent.intake` split: the system
  prompt and agent now come from a new `build_agent`, which a resumed matter calls directly. Tested live:
  resumed `t-test/test-001` went to deadlines from saved facts; a new matter `t-4c4d2e/m-001` was made
  from the sample lease (bad path refused, dragged path with escaped spaces accepted, 15 of 15 quotes OK),
  and its first confirmed fact landed in its own folder. The matter structure item is done.
- Matter structure, step 2 of 3: `list_matters` (tenant, id, and issues of every saved matter; no
  description or facts) and `load_matter(tenant_id, matter_id)` (replaces `record.matter` and
  `record.profile` from disk, profile `None` if the lease has not been read) in `record.py`, which now
  imports `lease` for `LeaseProfile`. `smoke.py` and `smoke_online.py` open the test matter with
  `load_matter` instead of reading the lease profile by hand, and `smoke.py` prints `list_matters()`.
  Checked by hand that `tools` and `timeline` see a newly loaded matter. Step 3 (`start()`) stays in TODO.md.
- Matter structure, step 1 of 3: matters now live at `matters/<tenant id>/<matter id>/`. `record.matter`
  gains a `tenant` key and `record.matter_dir` builds the path from both ids; it replaces
  `MATTERS / matter["id"]`. `ingest_pdf` now takes the matter folder instead of a matter id, so
  `matter_dir` is the only code that knows the layout (it replaces the path `lease.py` built itself).
  New helpers `new_tenant_id` (random `t-xxxxxx`, never from a name or email) and `new_matter_id`
  (`m-001`, `m-002`, ...), not called yet. The test matter moved to `matters/t-test/test-001/` and its
  `matter.json` gained `"tenant": "t-test"`. Steps 2 (list and load) and 3 (`start()`) stay in TODO.md.
- Second end-to-end `run.py` run, after the guidance-only prompt and the smoke split. Same facts, same
  deadlines, email recorded, assert letter drafted, timelines correct. Rule 5 still works (the model said
  the statute does not settle the termination-date question). Run 1's `events.jsonl` and draft renamed to
  `events_run1.jsonl` and `run1_draft_...` in `matters/test-001/` rather than deleted. Two findings added
  to TODO.md (a mis-cite for the escalate posture, an n/a question asked) and a note on the sample lease's
  term. No code changed.
- `smoke.py` split: `smoke.py` keeps the offline checks (playbook quotes, elements, deadlines, letter,
  timelines) and `smoke_online.py` holds the two model calls (`classify`, `fill_facts`). Replaces one
  script that needed the key for everything. To let the offline part run with no key, `config.py` no
  longer raises at import: the model clients are `None` without a key, and the new `require_key()` raises
  the old message. `run.py` and `smoke_online.py` call it first. CLAUDE.md's running lines updated.
  (TODO item 1, formerly item 3.)
- `intake` pastes only the model-facing part of each playbook into the system prompt: `issue`, `guidance`,
  and `spec.open_questions`, dumped as YAML. Replaces pasting the whole YAML file, which put elements,
  clocks, exclusions, related issues, provenance, and counting into the context. `open_questions` kept
  because rule 5 refers to them (decided with the author). Playbook text in the prompt roughly halves.
  `agent.py` no longer imports `PLAYBOOKS`. (TODO item 1, formerly item 2.)
- `lease.pdf` added to `.gitignore`. It is a sample lease, not a real one, but it carries names and
  addresses, so it stays out of history. Replaces the earlier state of leaving it untracked by hand.
- `git init` and first commit of the module split, so every later step is a readable diff. `.gitignore`
  keeps out `.env`, `matters/`, `venv/`, `__pycache__/`. `lease.pdf` left untracked pending a decision on
  whether the sample lease belongs in the repo. (TODO item 1, formerly item 2.)
- DOCUMENTATION.md filled from the code: modules and imports, data flow, files on disk with every event
  kind, the seven tools, the system prompt order, the playbook schema field by field with which code reads
  each, and running and testing. Replaces the section placeholders. Notes that every module needs
  `UF_API_KEY` set to import (config raises), so the offline checks need the key present but make no call.
  (TODO item 3.)
- Ran `python run.py` end to end against the UF gateway on `test-001`: lease profile loaded from disk,
  intake, all five proposed facts confirmed one by one, `get_deadlines`, a pasted landlord email recorded
  by `add_communication`, an assert letter from `draft_letter`, then `timeline`, `timeline full`,
  `timeline lease_ending`, `bye`. `python smoke.py` passed first, all playbook quote checks OK. The move
  from Colab broke nothing. Four findings added to TODO.md (double period in letters, one rule 2 slip,
  `timeline full` tag on a corrected fact, `lease_ending` preloading sections). No code changed.
  (TODO item 1.)
- Added README.md (fixed plan), TODO.md (working list), DOCUMENTATION.md (to be filled), CHANGELOG.md.
  CLAUDE.md slimmed to conventions, guardrails, and pointers to those four files. Its "Next steps" section
  moved to TODO.md with the review pushbacks folded in.

## 2026-09-25

- Moved from `Landlord_Tenant_chatbot_v3_2.ipynb` (Colab) to modules in this folder, one per notebook
  section: config, lease, corpus, deterministic, record, timeline, tools, schemas, agent, run, smoke.
  Colab `userdata` and Drive replaced by `.env` (python-dotenv) and paths relative to the folder.
- Shared state convention: `matter` and `profile` live in `record.py`; other modules use `record.matter`
  and `record.profile`. Replaces the notebook's single namespace.
- `draft_letter` completed: `issue` parameter added to the signature (v3_2 checked it but never received
  it); draft file name is now `draft_<date>_<issue>_<posture>.txt`; the `draft` event carries `issue`; the
  note under the letter comes from `playbooks[issue]` (was a reference to a `playbook` global that no
  longer existed).
- Rule 11: asks which issue the letter is about when the matter has more than one. Rule 15's example file
  name updated to the new pattern.
- `run.py` loads `lease_profile.json` if it exists and runs the extraction model only the first time.
  The notebook re-extracted on every run.
- `corpus.py` loads all playbooks silently at import; `check_all_playbooks()` prints the quote checks on
  demand (the notebook printed them in the loading cell).
- Added requirements.txt, .env.example, .gitignore, setup.sh, empty `matters/`.

## Before the move (from PROJECT_STATE.md, 2026-09-18 and earlier)

- 2026-09-24: multi-playbook support (`playbooks` dict, `active_playbooks`, `element_status`, deadlines
  tagged by issue); timeline as a DATE / EVENT / SOURCE / FILE table with `timeline`, `timeline full`,
  `timeline <issue>`; sent letters recorded through `add_communication` (rule 15) instead of a new tool.
- 2026-09-18: v3 restructured into the class notebook's section layout; PyPDF2 replaced pymupdf.
- 2026-09-15: second playbook deposit_claim_received v0.1, quotes verified; letter became a code template;
  `fetch_log` and `drafts` lists replaced by `fetch` and `draft` events.
- 2026-09-14: fact provenance: `fill_facts` proposes with stated/inferred tags and basis; `record_facts`
  is the only door into confirmed facts; `get_deadlines` refuses while anything is unconfirmed.
