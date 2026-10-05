# Changelog

Newest first. One entry per change, dated. Say what was replaced as well as what was added, so a future
session can see why the code is the way it is.

## 2026-10-04

- What the tool does not know, as a part of the prompt (TODO item 83, done). Was: the options' states (item 81) were
  spread over YOUR OPTIONS, an option at a time, and rule 1 asked only whether an option is open. Now
  `tools.unknowns_status` gathers, from `deterministic.check_options`, each point an option turns on that the tool
  has not decided, once however many options it decides: what it is, its cite and issue, what the tool knows of it
  (the tenant can tell the tool, the tenant can check, not settled, outside the tool, not yet) and why, and for each
  option what the option would be if it holds and what is left if not; then the lease parts the profile did not
  read, and that only a point `search_lease` finds nowhere is known to be absent. A new part, WHAT THE TOOL DOES NOT
  KNOW, after YOUR OPTIONS. Rule 1's first point asks for such a point as the part gives it, with what the option
  would be either way, before any step, and never as a fact; its new "Not:" lines come from four stories (a repair
  whose lease clause the tool has not read, a deposit with the lease's own notice term, a 3-day notice's form, a code
  the tool does not hold), with two "Instead:" lines. RULES is 2,410 words (2,055 before items 82 and 83). The eval's
  prompt names (`dev/eval.py`, `PROMPT_NAME`) take YOUR OPTIONS, missed since item 72, and the new part. Smoke: four
  item 83 checks.

- A search of the whole lease, `search_lease(phrase)` (TODO item 82, done). Was: the model saw only the sixteen
  clauses the profile holds, and said "the lease does not contain a holdover clause" and "the lease does not mention
  any late fee" in 4 turns of 12 runs (`dev/eval_runs/2026-10-04-items76-77`), though the test lease has both (2.4,
  3.3). Now the model's ninth tool finds every numbered clause of the matter's lease text (`pages.json`, through
  `record.lease_pages` and `lease.find_in_lease`) that holds a phrase, ignoring the PDF's broken words ("air
  -conditioning"), with the cite to use and the clause's words; found nowhere, it says so and asks for another
  wording, and a phrase no wording finds is a known absence, unlike a clause the profile did not read. A reply citing
  a clause the profile does not hold gets that clause's words printed under it from the lease text, as a profile
  clause's are (`agent.cited_words`). Rule 2's "Not:" adds the holdover line, its "Instead:" asks for the search and a
  second wording first and "The tool found nothing on that in your lease's text." only after; YOUR LEASE's name line
  names the tool. Also fixed: `lease.FOOTER`, the running header "Residential Lease Agreement (Florida) | Page 2 of
  12", was matched anywhere in the joined pages and took up to 80 characters of the lease before it ("the tenancy
  shall become mont by either Party", Section 2.4, also in the stop text's clauses); now it is taken off each page's
  start or end before the pages are joined (`lease.lease_text`). Smoke: five item 82 checks.

- What the tool knows of each condition of an option, computed by code (TODO item 81, done). Was (item 72): a gate was
  one confirmed fact, so a condition was met, closed, not settled, or not known yet, and ending the lease over an AC
  came out not settled on the statute alone though the lease's Article 7.2 promised the repair (83.56(1) also reaches
  "material provisions of the rental agreement"). Now a gate (`corpus.Gate`) is met through any of its `ways`
  (`corpus.Way`): a fact, a clock, something the tenant can check (a part of the lease, a local code, a document),
  or law outside the tool; a way may name a lease clause. `deterministic.check_options` gives each way and gate one
  of the five states of the author's decision: known (met, not met, or not met yet), the tenant can tell the tool (a
  fact the sheet asks), the tenant can check (a fact resting on a lease clause the tool has not read, a code, the
  notice itself), not settled (an open question), or outside the tool (a county with no court calendar); an
  option's status follows (open, closed, not known yet, not settled, outside the tool, or not open yet), and each
  undecided gate says what the option would be were it met ("if this condition is met, the option is not
  settled; if it is not, the option is closed"). YOUR OPTIONS prints the states and, for a condition with several
  ways, each way. The sheet shows the lease clause a question is about beside it, or says the tool has not read it
  (`sheet.clause_note`, `corpus.fact_lease`). Proved on three playbooks: repair_not_made 0.5 (its gates rewritten:
  the duty to repair through the structure or plumbing, the lease, a new sheet question, or a code the tenant can
  check with code enforcement; a new gate, the duty not changed in writing, which 83.51(1) allows only for a
  single-family home or duplex), deposit_not_returned 0.5 (the whole deposit back: no claim notice, the 30 days
  passed as a clock gate, and 83.49(5) with the lease's own notice term to check), notice_received_nonpayment 0.6
  (paying within the 3 days, defending in a case, defending on a defective notice; a new sheet question, the rent
  paid into the court registry). Rule 1 and the part's name line name the new statuses. Playbook checks: 0
  failures. Smoke: twelve item 81 checks in place of item 72's four (each state on each playbook, the prompt in
  words, the sheet's clause, a malformed way refused).

- The plan updated for the author's decision that the tool knows what it knows, as a general theme (README,
  Purpose and non-negotiables): each condition an answer turns on is known, something the tenant can tell it,
  something the tenant can check, not settled, or outside the tool, worked out by the program; a gap is never
  stated as a fact, and each unknown is tied to what the tenant can do. TODO: a new first section, items 81 to
  85, in order; items 72 (the other playbooks' options and the author's check), 79 (the lease search), and 80
  (a lease promise as a gate) folded into it.

- A check of items 76 and 77 on four stories, 3 runs each (`dev/eval_runs/2026-10-04-items76-77`, against the same
  stories in `-after`). Lease field names used as cites: 3 turns to 0; field ids overall 10 to 5. Asked "Is the
  AC part of my lease?", all three runs now cite the test lease's Article 7, whose 7.2 makes the landlord repair
  the air-conditioning system (before, three runs said the lease does not mention it). Still said from the
  profile: "the lease does not contain a holdover clause", "the lease does not mention any late fee", though the
  test lease has both (TODO item 79). The options do not see a repair promised in the lease (item 80). The AC
  story now expects that answer to cite Article 7 and never say the lease does not mention it, in place of
  "applied", which a correct one-line answer failed.

- Lease clauses in plain words, each with the cite to use (TODO item 77, done). Was: YOUR LEASE was the profile as
  JSON, and the model cited a clause with no section number by its field name ("(Lease notice_before_vacating)",
  "(term_end)"), most of the 17 turns with a field id in the eval of 2026-10-04. Now `lease.lease_lines` gives a
  line per clause: its label in words (`lease.LABELS`), the cite to use (`lease.lease_cite`: "Lease Section 3.1",
  "Lease Article 7", or "Lease, page 1" for a clause with no number), and its words; or that the reading found no
  such clause, or did not read it. `agent.LEASE_CITE` takes the three cite forms, and `cited_words` prints the
  clauses a cite names (`agent.cited_clause`: a numbered clause, one holding the cited number, or the clauses with
  no number on a cited page), each with its label. The format line and rule 2 ask for the cite YOUR LEASE gives,
  with "(Lease notice_before_vacating)" as a "Not:". The eval's `CITE_SEEN` takes the new forms. Smoke: the
  lines, the cite forms, a page cite, a cite inside an article.

- The lease profile's repairs clause, and the lease part is not the whole lease (TODO item 76, done). Was: fifteen
  profile fields, none about repairs, and asked "Is the AC part of my lease?" the model said "the lease does not
  mention air conditioning" in 3 of 3 runs, from those fields alone. Now `lease.LeaseProfile` has a sixteenth,
  `maintenance_and_repairs` (who maintains and repairs the unit, its systems, its appliances), optional so that
  profiles read before it still load, with the field `None` (not read); `LeaseProfile.clauses()` gives the
  clauses read, and `agent.given_text`, `cited_words`, `reading_line`, `tools.quote_is_real`, and
  `lease.check_quotes` (which prints "not read") use it. Its description asks for one passage as printed: the
  first wording ("the sentences that say who repairs what") got two subsections joined with the heading between
  them dropped, and the quote failed `check_quotes`; with the second, both test leases tried give Article 7 whole
  (about 1,100 characters, its 7.2 "Landlord shall repair the heating, air-conditioning, electrical, and
  plumbing systems") and pass. YOUR LEASE's name line now says it holds only the clauses the tool reads, and rule
  2 has the eval's "The lease does not mention air conditioning." as a "Not:". Smoke: an older profile loads
  with the clause not read, the extraction schema asks for it, the name line and the rule. Profiles already
  saved stay without it (TODO item 78).

- Eval of items 72 and 73 (`docs/evals/2026-10-04-options-cite/`; the code before, the new AC story on the old
  code from a worktree, and the code after; code-scored). TODO item 74 done. Recitation 104 turns to 5 (61 to 3
  per 100 replies); the AC story's answers say whether ending the lease, and withholding rent, is open before
  any step in 3 of 3 runs (0 of 3 before); runs meeting every expectation 34 to 42 of 48 on the same 16 stories;
  quote cautions 18 to 10, and item 66's retold caution (45) gone; dates worked out 4 to 0. Field ids rose 10 to
  17 turns, mostly lease profile field names used as lease cites. New eval expectation `open_first`. TODO items
  76 (no repairs clause in the lease profile; the model said the lease does not mention AC) and 77 (lease cites by
  field name). Chart shown in the session.

- Cite, do not recite (TODO item 73, done). Was: every rule quoted in the reply (rule 1, item 54), the tenant's
  confirmed facts listed back ("You confirmed ... You confirmed ..."), and a caution for a section cited without
  its words (item 66); in the author's run a reply pasted a 1,900-character lease clause to answer "was AC part of
  my lease?". Now the format line and rules 1, 2, 3, 4, and 8 ask for each rule in one plain sentence with its
  cite, quote marks only for the few words a point turns on, and only the facts the answer turns on, in a few
  words; the author's recited reply is rule 1's new "Not:". The program prints the cited words under the reply
  (`agent.cited_words`: each ch. 83 cite's subsection or section from `statutes/`, the narrowest once, cut at
  1,500 characters; each cited lease section's clause from the profile), as a `sources` block, folded in an
  expander on the web page, and a printed transcript line marked "sources". `reading_line` counts a cite as well
  as a quote. Item 66's caution (`RETOLD`) is gone. The quote and cite checks stay. Eval: `applied` takes a cite
  or a quote; a new measure, `recited` (more than 300 quoted characters, or three "You confirmed" lines); the
  transcript labels the printed words. Rubric: LAW_UNSOURCED is a rule with no cite, or one its printed words do
  not say; QUOTE_UNMARKED no longer counts a plain-words rule with its cite; new OPTION_BEFORE_OPEN and RECITED.
  New eval scenario `repair_ac_terminate`, the author's AC story; the four stories where a repair is confirmed
  answer the new sheet question. Smoke: the rules, the printed words (the narrowest cite once, the lease clause
  with its page), the block order, no caution for a cite without a quote.

- Options before steps, checked by code: the pilot on repair_not_made (TODO item 72, in part). Was: the model
  decided for itself whether an option was open, and in the author's run it laid out how to end the lease over
  an AC not repaired before any word on whether 83.56(1) reaches an AC. New: a playbook's `spec.options`
  (`corpus.Option`, `Gate`, `Step`), each gate and step tied to a fact or clock and quoted from the statute,
  checked by `load_playbook` and `check_playbook`; `deterministic.check_options` gives each option's status from
  the confirmed facts (open, closed, not settled, not known yet) and each step's (done, waiting, to do);
  `tools.options_status` puts them into a new prompt part, YOUR OPTIONS, between YOUR FACTS and WHICH DEADLINES
  HAVE PASSED; rule 1 begins with "Open or not" and takes the author's AC reply as its "Not:". repair_not_made
  0.4: two options, ending the lease (83.56(1)) and withholding rent (83.60(1)(b)); a new fact asked on the
  sheet, whether the problem is with the roof, windows, other structural parts, or the plumbing (the items
  83.51(1)(b) names); a new open question with two readings, whether rent paid with knowledge waives ending
  the lease over a problem still not fixed (83.56(5)(a)). On the author's facts both options come out not
  settled, with why. Playbook checks: 0 failures. Smoke: the AC story, a roof leak at each stage, a problem the
  tenant caused, a gate not yet answered, and the prompt part in words. The other nine playbooks and the
  author's check of these gates stay as item 72.

- The plan updated for the author's decision of 2026-10-04 (README, Purpose; CLAUDE.md), after the author tried
  the web page with a real 57-page lease. Two changes to what an answer is: whether an option is open comes
  first, checked by code from the confirmed facts and the playbook's conditions for it, before any step toward
  it (a reply had said how to end the lease for an AC not repaired, and the next reply that an AC may not be a
  duty 83.56(1) reaches); and an answer cites the law and the program prints the cited words, instead of the
  model reciting sections, lease clauses, and the tenant's own facts (was, since 2026-10-02: "the rule, quoted
  ... with its source"). README: the answer's shape, goal 3, and three non-negotiables. TODO: items 72 to 74 for
  this, 75 for the lease PDF PyPDF2 could not fully decode, and a note on item 45 (a long lease read with no
  sign of progress, a second click starting a second matter).

## 2026-10-03

- Blind scoring of the applying code of 2026-10-02 against today's (`docs/evals/2026-10-03-blind/`). 84 transcripts,
  42 a side, mixed under one set of codes with the program's cautions taken out, scored by sixteen agents with the
  rubric; the old side scored again came out as on 2026-10-02 (21 of 103 legal answers applied well, 270.5
  slips; then 21.5 of 101.5, 270), and the two scorers of a batch agreed on 76% of slips. Legal answers applied
  well: 21 of 103 (20%) to 36 of 115 (31%); firm slips 192 to 141. Fell: ids and prompt names 46 to 20.5, quotes
  wrong 13.5 to 5.5, conditions missed 19.5 to 13.5, open questions closed 19.5 to 15. Unchanged: rules restated
  without their quote, conditions applied wrong, dates worked out. New method scripts: `blind_mixed.py`,
  `blind_summary_mixed.py`. TODO item 71. Chart shown in the session.

- Eval of items 60, 66, and 65 (`docs/evals/2026-10-03-items60-66/`; three runs: the old shared lease, each
  story's own lease, and own leases with items 66 and 65; code-scored). Questions about when with their
  deadlines printed 35, 36, 39 of 39 (the program printed 4); section-retold cautions 45 in 170 replies; runs
  meeting every expectation 40, 37, 33, the last two differing by chance alone, since items 66 and 65 change
  nothing the model reads. Left to TODO: items 68 to 70, a note on item 38. `method/compare.py` adds the
  program's deadline listings and the new caution kind. Chart shown in the session. The own-leases run came from
  a git worktree, moved to the Trash afterwards.

- The program prints the deadlines when the tenant asks when and the model did not call `get_deadlines` (TODO
  item 65, done). Was: rule 3 asks the model to call it for every question about when, how long, how many days,
  or a last day, and in the evals of 2026-10-03 it did not on 1, 4, then 5 of 39 such questions ("the deadline
  is seven days before your planned move-out date"), so the tenant got no dates. Now `agent.turn` checks the
  tenant's message (`WHEN_QUESTION`; "when I moved out" is not one) and, when the turn holds no `get_deadlines`
  call, `deadlines_unasked` puts the program's listing first, the same `deadlines` block the tool's call would
  print, logged and transcribed as a `printed` line marked "deadlines". The model is not told, and it still
  answers in its own words. `dev/eval.py` counts these (`deadlines_by_program`, "dl-prog") apart from the
  model's calls, which "calls get_deadlines" still measures. Smoke: a stand-in that answers without the tool
  gets the program's listing first; one that calls it gets one listing.

- A caution for a section a reply cites and retells without quoting (TODO item 66, done). Was: item 54's rule pair
  asked for every rule to be quoted and the eval's `cites_unquoted` stayed at 27, then 29 turns per 100 replies;
  the tenant was told nothing. Now `agent.check_reply` adds one line per reply naming the sections it cites with
  none of their words quoted (`citations.cites_without_quote`, which until now only the eval used), less any
  cite already cautioned (not loaded, or a misplaced quote's): "[Check: this reply cites 83.56(5)(a) and 83.55
  without quoting them: what it says they mean is the reply's own wording, not the statute's. Read the
  statute's words before relying on the reply.]", and a `cite_flagged` event per cite. Expected rate, from
  the last eval: about 29 replies in 100. Smoke: a reply quoting 83.49(3)(a) and retelling 83.49(3)(b) gets
  the line for (3)(b) only, and its event.

- A lease for each eval story (TODO item 60, done). Was: every scenario read `lease.pdf`, a twelve-month lease
  from 2026-10-01 at $1,850 with a $1,850 deposit and an authorized dog, so the stories contradicted it (a $950
  month-to-month duplex whose increase was read as a decrease; a $1,000 deposit read as $1,850; a lease that
  ended 2026-07-31 against the lease's 2027; most stories' September events before the lease began). New:
  `dev/build_test_leases.py` writes ten leases into `dev/leases/` (gitignored, like `lease.pdf`), each
  `lease.pdf`'s text with the story's term, rent, deposit, two months' rent as the early termination fee, and
  for the dog and cat stories a no-pets clause, changed word for word and checked when built. Each eval
  scenario names its lease in `start` instead of `lease.pdf`. `dev/eval.py` passes any `.pdf` in `start` as a
  path, stops before running when a lease is missing, and reads the dates a reply may restate from the run's
  own lease (`lease_dates(entry)`) instead of the seed's `pages.json` (rescoring a past run gives the same
  numbers, since its copy names `lease.pdf`). Checked live: Gemma reads every lease with the story's term,
  rent, and deposit, and every quote passes `check_quotes`. Left as they were: the lease is for a house with a
  yard where some stories are apartments, a townhouse, or a duplex, and the addendum's initials are blank.

- Eval of items 61 and 54 to 58 (`docs/evals/2026-10-03-items54-61/`; 16 scenarios, 3 runs, three runs: the code
  before, after, and after the deadline-name fix; code-scored). Runs meeting every expectation 41, 37, 40 of 48;
  prompt part names 18, 8, 3 turns per 100 replies; field ids 17, 12, 8; quote cautions 47, 22, 28; the new
  left-out caution 24 in each after run; sections retold not quoted 27, 29, 29 (item 54's pair did nothing
  measurable); `get_deadlines` on questions about when 38, 34, 35 of 39, the first run's drop being the
  regression the fix addressed. Left to TODO: items 65 to 67, and notes on items 40 and 59. `method/compare.py`
  adds measures per 100 replies, cautions by kind, and single turns to the comparison. Chart shown in the
  session.

- The deadline part of the prompt renamed again, WHICH DEADLINES HAVE PASSED (a fix to TODO item 61). Was, since
  item 61 that morning: THE PROGRAM'S DEADLINES. The eval of items 54 to 61 found the model reading it as the
  deadlines themselves: "You have until the upcoming deadline shown in THE PROGRAM'S DEADLINES", "the deadline is
  seven days before your planned move-out date", and `get_deadlines` uncalled on 5 of 39 questions about when (1
  of 39 before item 61), so a question like "When is the last day I can tell them I'm leaving?" got no dates and
  "If my friend picks her up this weekend, am I safe?" got "you are safe" in 2 of 3 runs. The new name says the
  part has no dates and that a question about when calls `get_deadlines`. The `get_deadlines` receipt no longer
  names a part in capitals ("your instructions say which have passed"), since the model copied the receipt into
  replies with the name in it. The eval's `PROMPT_NAME` adds the new name. Smoke: the receipt's words.

- False quote cautions from a quote's inner marks (TODO item 58, done). Was: program cautions rose from 6 to 48
  in the eval of 2026-10-02, and the item guessed that inner quote marks broke `citations.quote_spans`' pairing.
  Replayed on the 168 replies of 2026-10-03, the cause was elsewhere: `compact` made curly marks straight but
  kept them, so a quote whose inner marks the model changed (‘Reasonable notice’ inside a quote of 83.53(2),
  whose stored text has “Reasonable notice”; ‘cash’ inside Moskowitz v. Aslam's words) was not word for word,
  and the tool's own words, which the prompt holds as YAML with an apostrophe doubled ("neighbor''s"), were not
  either. `compact` now leaves quote marks and apostrophes out. The replay: 69 cautions before, 54 after, the 15
  gone all false, none added. Tried and dropped, since neither changed a caution or a cite check in the replay:
  a pairing that lets a quote hold a quote, and the playbooks' text as plain text in `given_text`. What is left
  went to TODO item 64: mostly real cautions, and about 12 false ones where a quote takes a cite in the prose
  as its source. Smoke: a quote of 83.53(2) with its inner marks made single, and the tool's words with an
  apostrophe doubled in the given text. Wiki checks (which use `compact` for pin pages): 0 problems.

- Two code checks on the cases a reply uses (TODO item 57, done). Was: in the eval of 2026-10-02 every mold-story
  answer left out the three printed cases that went for the landlord (ONE_SIDED 12.5), and one credited a
  case's words to another (part of CASE_MISREAD 16.5); rule 8 already asked for every case. Now, as cautions the
  tenant reads: a case `get_cases` printed in the turn that no reply after it names ("[Check: the program
  printed cases above that this reply does not discuss: ... Read them too before relying on the reply.]", a
  `cases_left_out` event, `agent.cases_left_out`); and a quote credited to a printed case whose printed part
  does not hold it while another case's does ("is in X's text, not Y's", a `quote_flagged` event,
  `agent.check_case_quotes`, run by `check_reply`). New: `wiki.cases_printed` (the cases a printed text holds,
  by their heading lines), `agent.printed_cases`, `agent.named_cases` (a case named by its short name or first
  party, a name inside a longer one being the longer one's). Replayed on the runs of 2026-10-03: 20 of the 32
  turns that printed cases would get the left-out caution (most printed four to nine cases and the reply
  discussed one or two), no quote credited to the wrong case. Writing the replay found two matching bugs, fixed
  before the commit: a name ending in "Corp." never matched (a word boundary cannot follow a period), and
  "Bennett" inside "Bennett M. Lifter" was read as Bennett v. Mattison. Cases applied with no word on how alike
  the facts are stay with rule 8; no code can see it. Timeline full shows `cases_left_out`. Smoke: two printed
  cases, a reply naming one and quoting the other's words under its name, then a reply naming both.

- Open questions read as unsettled (TODO item 56, done). Was: OPEN_CLOSED 19.5 in the blind scores of
  2026-10-02. Checked against the wording the model read, three causes: purpose_of_entry told the model to
  "Apply the one that fits the reason in the record", and every entry run called an air-conditioning filter
  change "repair"; the readings sit as a bare YAML list, and a reply's "So:" line gave the first one as the
  answer before listing them under "Not settled" (remedy_not_duty, notice_form); the rule's order put "So:"
  before "Not settled". Now: the part's name line (`agent.PARTS["open"]`) says the stored text settles none
  of them, so every reading is given and none picked; rule 1's "So:" says that with an open question in the
  way it gives what follows on each reading, never one as the answer; purpose_of_entry (landlord_entered_unannounced
  0.5) applies a way in only when the reason fits one, and names a visit that could be repair or an agreed
  service (routine maintenance, servicing equipment in the unit, pest control) as the open point, called
  neither. The readings' own words are unchanged. wants_to_leave_early's fee_notice_period, which has no
  readings, went to TODO item 63 for the author. Smoke: the name line and the "So:" line in the prompt.

- Failure modes for conditions the model missed or misapplied (TODO item 55, done). Was: CONDITION_WRONG 28 and
  CONDITION_MISSED 16.5 in the blind scores of 2026-10-02, and item 50's failure modes named some of the
  sections but not the slips seen. Five, each quoting `statutes/` (playbook checks: every quote OK), in the
  guidance the model reads under THE TOOL'S NOTES ON YOUR ISSUES:
  landlord_entered_unannounced 0.4, 83.53(1) read as forbidding the tenant to change the locks (its words are a
  duty not to withhold consent to enter unreasonably; 83.67(2) on locks binds the landlord); lease_ending 0.4,
  83.575(3)'s extra month now with both conditions, permission to stay and no 83.57(3) notice (was: only
  permission); notice_received_violation 0.4, termination or a failed cure said while a curable notice's 7 days
  have not run; notice_received_nonpayment 0.5, 83.60(2) given without the motion to determine rent (the old
  failure mode quoted only the waiver, which the replies copied), and 83.56(5)(a)'s steps after partial rent
  read as settled or as all due before filing. The other condition slips the scorers found went to TODO item 63
  for the author. These failure modes, like the rest of the playbooks, wait for the author's hand check (item 2).

- Rules restated without their quote (TODO item 54, done). Was: the blind scorers' second most common slip,
  LAW_UNSOURCED (42, 34.5 firm, eval of 2026-10-02): a section cited and retold ("Fla. Stat. 83.56(5)(a) states
  that if the landlord accepts rent ..."), the second half of a quoted rule in the model's own words, or a
  remedy nothing quoted gives ("you may seek injunctive relief"). Rule 1 gets a pair, with those three as its
  "Not:" lines (the model's own words from the eval): quote every rule the answer turns on, each condition and
  each consequence relied on, then say it plainly beside its quote; a rule that cannot be quoted stays out.
  New: `citations.cites_without_quote` finds a cite outside quote marks with none of its words quoted in the
  same reply, and `dev/eval.py` counts turns with one ("retold", `cites_unquoted`), so the next eval measures
  the slip without the blind scorers. Rescored, the runs of 2026-10-03 have 48 such turns in 168 replies;
  some are false alarms from item 58 (a quote whose inner quote marks broke the pairing, or were changed from
  double to single). Not shown to the tenant: as a caution it would add to the cautions already printed.
  Smoke: the finder, and the pair in the prompt.

- The system prompt's parts renamed in words a tenant can read (TODO item 61, done). Was: LEASE PROFILE,
  PLAYBOOKS, STATUTE SECTIONS, CASE TOPICS, ELEMENT STATUS, DEADLINE STATUS, and after item 53 the model still
  wrote them in 17 replies per 100 ("(ELEMENT STATUS shows eviction_action_filed: true)", "the open question in
  PLAYBOOKS"), naming its source as the format line asks but with the prompt's name for it. Now `agent.PARTS`:
  YOUR LEASE, THE TOOL'S NOTES ON YOUR ISSUES, WHAT THE STATUTE DOES NOT SETTLE, THE STATUTE, COURT CASES THIS
  TOOL HAS, YOUR FACTS, THE PROGRAM'S DEADLINES, each with a short line on what it holds. PLAYBOOKS is split in
  two: the guidance under THE TOOL'S NOTES, the open questions under WHAT THE STATUTE DOES NOT SETTLE (rule 5's
  wanted words). The rules, rule 6 and rule 8, and the tools' descriptions and receipts (`get_deadlines`,
  `deadline_receipt`, `get_cases`) use the new names; the format line now asks for each source in plain
  lower-case words ("your lease", "you confirmed", "the program's deadlines") and forbids a part name in
  capitals and a rule number. The eval's `PROMPT_NAME` counts the old names, the new ones in capitals, and a
  rule's number; the rubric's ID category says the same. Smoke: a `prompt_part` helper reads a part by its name;
  new check that the parts come in order under their names, with no old name in the prompt, the rules, or a
  tool's description. The rest of the item went to TODO: the renewal question's fallback line (item 40), offers
  (new item 62).

- Eval of items 51 to 53 (`docs/evals/2026-10-03-items51-53/`; 16 scenarios, 3 runs, against the applying runs
  of the day before, code-scored): runs meeting every expectation 31 to 41 of 48; legal questions applied 62 to
  72 of 75; a question mixing a deadline with the law applied 0 to 3 of 3; a cash-only 3-day notice applied 0
  to 2 of 3; field ids 30 to 17 turns per 100 replies; prompt names unchanged at 17 (TODO item 61); the renewal
  question still gets the fallback line in 2 of 3; offers 3 to 6. Scorer fixes in `dev/eval.py`, every run
  rescored: an echo is a computed deadline (the listing's "deadline" fields, `deadline_dates`) found in a reply
  and not also a fact the record holds, and the printed deadlines no longer count as dates the record holds.
  Was: the listing's confirmed trigger dates counted as echoes when a reply named them, and a deadline the
  model counted itself went uncaught. Chart shown in the session.

- Ids and prompt names kept out of the model's reading where they need not be there (TODO item 53, done). Was: in
  the eval of 2026-10-02, 39 turns had a field id and the blind scorers' most common slip (48) was an id or a
  prompt name ("ELEMENT STATUS", "PLAYBOOKS", "remedy_not_duty"). Three causes removed at the source: item 50's
  own prose named ids in parentheses ("(rent_paid_since_known)", "(termination_date_meaning)") in 29 places,
  now in words or gone (every playbook one version up); the open questions reached the model with their `id`,
  which no tool takes, and now go without it; DEADLINE STATUS named clocks and facts by id, now by label ("claim
  notice deadline [deposit not returned] ... 30 days after tenancy terminated"). The format line in the rules
  adds: never the name of a part of the prompt or a rule ("ELEMENT STATUS", "rule 8"). Fact ids stay in ELEMENT
  STATUS, since `propose_facts` takes them. New playbook check (`corpus.playbook_ids`, in `check_playbook`): no
  fact, clock, or open question id of any playbook in the guidance's prose or the open questions' text and
  readings. New eval measure: prompt names in replies (`PROMPT_NAME`). Smoke: the open questions reach the
  prompt without ids, the deadline status has no id under its header, the rules name the prompt's parts.
  Playbook checks: 0 failures.

- The fallback line is not for a point an open question or a case speaks to (TODO item 52, done). Was: in the
  eval of 2026-10-02, "The lease and statute text I have do not answer that." answered 6 of the 13 legal
  questions not applied, among them a 3-day notice demanding cash only (3 of 3), though the notice-form open
  question and Moskowitz v. Aslam are on it: no stored sentence says "cash". Rule 2 has a new pair: the fallback
  line only when no stored sentence, no open question, and no case topic is on the point, even in other words
  than the tenant's; otherwise the readings or the cases, applied. Its example is a money-order notice, not the
  eval's own question, so the eval still tests whether the pair carries over. The notice-form open question of
  notice_received_nonpayment (version 0.3) now names terms the form does not have (how, where, or in what form
  rent is paid), in its text and first reading. Smoke: the pair is in the prompt. Playbook checks: 0 failures.

- `get_deadlines` no longer ends the model's turn (TODO item 51, done). Was: `return_direct` since item 19, so a
  question that mixed a deadline with the law ("If I get rid of the dog by Friday, am I safe?") got the printed
  listing and no answer: 6 of the 13 legal questions not applied in the eval of 2026-10-02. The reason for ending
  the turn, the model retyping printed dates, went with item 44 (the model gets no dates) and item 46 (DEADLINE
  STATUS gives "passed" or "upcoming"). Now the listing prints and the model's answer follows it. The receipt
  says to add nothing when only the deadlines were asked for and otherwise to answer the rest without writing a
  date; rule 3 says the same (call `get_deadlines` every time, no longer "alone", and "your turn ends there" is
  gone). Smoke: the stand-in model's answer now follows the listing (was: nothing after it); the page's
  stand-in gets an empty reply after the listing, and its check finds the program note by role.

## 2026-10-02

- The first eval of applied answers (TODO item 49, done but for the author's sample, which stays as item 49;
  `docs/evals/2026-10-02-apply/`). The organizing code (29df5d7, a git worktree) against the applying code
  (8f4ae3b), 16 scenarios, 3 runs each, at the same time, no crash or gateway trouble. Code-scored: runs meeting
  every expectation 6 to 31 of 48; legal questions applied 0 to 62 of 75; quotes-only replies 72 to 0; open
  points with their readings 0 to 6 of 6; court questions with the cases used 0 to 18 of 18; but program
  cautions 6 to 48, turns with ids 5 to 39, dates made 0 to 4. Blind-scored (the applying side, eight scorers,
  77% agreement): 21.5 of 101.5 legal answers applied well; 270 slips in 128 replies, 192.5 firm, led by ids
  and prompt names (48), rules restated without their quote (42), conditions wrong (28) or missed (16.5), open
  questions closed (19.5), and cases misread (16.5) or one-sided (12.5). Findings are TODO items 51 to 60.
  Scorer fixes made while reading the results, applied to both sides: the test lease's own dates count as
  known (`dev/eval.py`, `LEASE_DATES`); the noise story's open points accept "not settled" and "readings"; a
  court question answered from cases given earlier in the chat counts, and a case name with a leading "In" is
  matched without it (`case_given`). Charts shown in the session: the comparison, and the blind slips by
  category. The baseline worktree (no `.env`, no matters left) was moved to the Trash.
- The eval measures applied answers (TODO item 49, first part). Was: a legal question's turn expected "does
  not decide" or the fallback line, `must_not` patterns failed "entitled", "allowed", "forfeit", and case
  names, and a `LAW_WORDS` screen marked must, may, can about a party. Now: 34 turn expectations rewritten; a
  legal question expects `applied` (a quote with 40 or more words of the model's own, addressed to the tenant);
  a court question expects `cases_used` (a reply names a case the turn's `get_cases` gave); the noise story's
  two questions expect "does not settle" with the readings; the mixed story's question nothing stored answers
  accepts the fallback line or an applied answer; kept are the forbidden posture words, money amounts, dates,
  federal-law names, "you should", "you are safe", and new forbidden predictions ("you will get", "you would
  likely win"). New measures on every reply: quotes only, dates made (a date with a year that the record does
  not hold), cases not given, and `CHOOSE_WORDS`. Scored on a copy of the deadline runs from earlier today,
  the organizing code's answers fail every `applied` check and most are quotes only, as expected. The blind
  scorers' rubric is `dev/eval_rubric.md` (QUOTES_ONLY, UNCONFIRMED_FACT, CONDITION_MISSED, CONDITION_WRONG,
  OPEN_CLOSED, CASE_MISREAD, ONE_SIDED, CHOICE_MADE, OVERCLAIM, LAW_UNSOURCED, DATE_MADE, ID, with the quoting
  and letter categories kept); the 2026-10-01 rubric stays in its dated record.
- Case pages' Facts sections hold the facts the decisions turned on (TODO item 48, done). `wiki/SCHEMA.md`: was
  "A few quotes, as background."; now the parties, the lease, notice, or property, what each side did and when,
  and what was asked of the court, usually three to six quotes, so the chat (item 47) can set a tenant's facts
  beside them. The 20 tagged case pages with two quotes or fewer were rewritten from their opinions, by four
  agents in parallel, each page's quotes checked by `wiki.py check`: from 30 quotes to 99 (Durene now has the
  move-out, the written request for the $300, the suit, the counterclaim, its dismissal, the return of the
  deposit, and the panel's reversal). Nothing outside the Facts sections changed (checked section by section
  against git); two bullets lost a prose label. Opinions that state few facts got what they state (Casey,
  Gilbert, Moskowitz, Olen v. Moss); details in `wiki/log.md`. Not touched: the 1991 forms decision, the 30
  tagged pages that had three or more quotes, and the untagged pages. No page was verified, so no sign-off
  was undone; the author verifies pages as before. `wiki.py check`: 0 problems.
- Cases go to the model, which applies them (TODO item 47, done). Was: `get_cases` gave the model only the
  names of the cases it printed and ended the turn, and rule 8 said never quote, summarize, or choose among
  cases. Now `wiki.render_cases` also prints each case's Facts quotes and its Related lines ("Other cases on
  it": followed, distinguished, disagreed with; `wiki.page_section`), the model gets that same text, and
  `get_cases` no longer ends the turn (`return_direct` off; `get_deadlines` keeps it), so the answer comes after
  the printed cases. Rule 8: call `get_cases` when the tenant asks what courts said or a topic is on the point
  being applied; for every case given, its facts beside the tenant's, its rule quoted with name and page, the
  statute version it read when not today's, what it would mean on the tenant's facts, whether another case
  distinguished it, and a case against the tenant said so plainly. The cases' closing line says how far a case
  reaches turns on how alike its facts are (was "This tool does not decide whether any of them applies to
  you."). The chat model's output limit is 8000 tokens (was 4000): in a live probe a four-case answer stopped
  mid-sentence, likely at the limit (a second run finished normally at about 1,000 tokens), and a reply the
  gateway still stops at the limit now gets `CUT_OFF`, a caution saying it was cut off. The live probe (a
  late claim notice, "Has a judge ever ruled ...? Does that help me?", development run): each of Durene,
  Malagon, Casey, and Plakhov quoted from the result and set beside the tenant's facts, and Plakhov named as
  excusing the landlord's notice when the tenant gave no 7-day notice, a fact marked not known yet. It also
  showed an id in a reply ("early_or_periodic false"), for the eval to count. Smoke: three checks (the same
  cases for tenant and model, with facts and treatment; get_cases not turn-ending; the cut-off caution).
- Rules version G: the model applies the law (TODO item 46, done). Was version F, "organize, never advise":
  quotes set beside the facts and "This tool does not decide that."; a question like "what can I do to sue the
  landlord" got three quotes. Rule 1 now answers in order: the rule quoted; the facts it turns on, in plain words
  with their source (a fact said in the chat but not yet confirmed is not known yet); each condition met,
  failed, or not known; what follows, with the options the stored text gives and what each requires first; the
  open question in the way. It never assumes a fact or chooses for the tenant, and says which of lease and
  statute controls only from a stored section (83.47). Rule 3: whether a deadline has passed comes only from
  the new DEADLINE STATUS, never a date comparison or a date worked out for a reading. Rule 5: an open
  question is given with its readings and what each would mean on the facts. Rule 9: a step the statute
  requires before an option is part of the answer, an offer is not. New in the prompt: DEADLINE STATUS
  (`tools.deadline_status`, after ELEMENT STATUS): each computed deadline's issues, whose, what it counts from,
  cite, and "passed" or "upcoming", with no date, and what waiting issues wait for; logs nothing
  (`tools.open_facts_by_issue` now shared with `deadline_listing`). The program's line under a reply that
  quotes the statute or the lease is `READING_LINE`, "This is the tool's reading of the stored law and your
  confirmed facts, not a lawyer's advice." (`agent.reading_line`; was `NOT_DECIDED`, "This tool does not decide
  whether any of this applies to you."), and the model is told not to write its own. The stop text's last line
  says the tool has no playbook for the situation, so it does not apply the clauses. The page's sidebar says
  the tool applies the stored statute, in development. Not done as the item said: today's rules were not kept
  as a `RULES_FILE`; the eval compares with the whole code before the change (a git worktree, `--project`),
  which also keeps the old footer and case tool. Two live probes on a scratch copy of the test matter (the
  author's question from the page, and "Was it legal for them to keep my deposit?"): the first answers applied the rule
  to the facts, gave both readings of the termination date, and listed suing for the deposit and 83.49(3)(c)'s
  costs and fees; they also showed field names in the facts and a date worked out for a reading, both now
  "Not:" pairs; the second probe showed neither. Smoke: five checks on the reading line, DEADLINE STATUS
  (passed, waiting, no date, nothing logged), and the rules and readings in the prompt.
- Playbooks rewritten for applying the law (TODO item 50, done; the author still checks each against
  `statutes/` before signing). Every open question now says what the stored text lets the model apply and what
  stays open, and a point the text does not settle carries `readings`, two or more, each resting on quoted
  words: the deposit termination date (the lease end against the move-out date, with 83.49(2)(d)'s "WITHIN 30
  DAYS AFTER YOU MOVE OUT"), e-mailed notices and receipt, the objection's form, routine maintenance as repair
  or as a further purpose of entry, abuse of access, 83.575(2)'s "within 15 days before the start", permission to
  stay on, whether a landlord must act on a disturbance, what is unreasonable, ending a lease over a neighbor, a
  3-day notice's form and charges other than rent, which paragraph of 83.56(2) a violation falls under, delivery
  against receipt, rent increases, retaliation as a defense or a claim, what is material, an item both
  subsections of 83.51 may cover. Questions about a limit of the tool (hours, months, a lease-set period, the
  court-day counting the author is researching) have no readings. Was: each said "the tool records ... and does
  not decide". `failure_modes` are now slips in applying: a condition skipped (83.49(5)'s missing notice, 83.575(1)'s
  landlord-notice condition, 83.64's good faith and different treatment, 83.51(4)), a fact assumed, a forfeiture or
  a defense stated without its other half (83.49(3)(b)'s "does not waive any rights", 83.60(2)'s registry, 83.60(1)(a)'s
  cure), a date counted by the model. Was: written for organizing ("Deciding whether an increase is retaliatory").
  Letter notes that ended "is not something this tool decides" now say what the statute turns on, or to ask in
  the chat. Versions 0.2 (deposit_not_returned 0.3). `check_playbook` checks each open question's shape (an id,
  sections in `statutes/`, text, and readings of two or more when given); the prose quote check covers the
  readings. Playbook checks: 0 failures.
- The plan: the tool applies the law to the tenant's confirmed facts (the author's decision). Was: an
  organizer that set the lease, the statute, and the cases beside the facts and never said what they meant for
  the tenant; on the web page, "what can I to sue the landlord" got three statute quotes and "This tool does
  not decide that.", which does not help. README: Purpose (the shape of an applied answer: the rule quoted, the
  facts from the record, each condition met, failed, or not known, the options and what each requires, the
  unsettled points with both readings; no choice made for the tenant; development on test matters only until
  the unlicensed-practice question is settled), goal 3, the skills part (cases reach the model), the
  non-negotiables (application only on confirmed facts and stored text; open points stay open; cases used whole
  and fairly, including those against the tenant; the cases' text still printed by code), and the wiki
  paragraph (case pages quote the facts the decision turned on; the application is in the chat). CLAUDE.md's
  description. TODO: a new section, items 46 to 50 (rules, cases to the model, case pages' facts, the eval,
  the playbooks' failure modes); items 26, 28, 36, and 40 updated. No code changed: the rules still organize
  only until item 46.
- The web page, `app.py` (TODO item 31, done): `streamlit run app.py`, on http://localhost:8501 only. The same
  steps as `run.py` on one page: the sidebar holds New matter, the saved matters, and the open matter's issues
  with Drop and End session; the middle holds the front door (tenant, lease PDF, description; or what is new),
  then the intake sheet as a form, one row at a time with a date picker, yes/no, an amount, or words, filled in
  with the suggestion, then the chat; the right holds the timeline (all issues or one, full or not, with a wide
  window) and the last letter drafted, with a download button. It draws the blocks of `agent.turn` and
  `agent.command`: the model's replies in speech bubbles, the program's output (deadlines, letters, cases, the
  timeline, the stop) in boxes labeled as printed by the program, cautions as warnings, the "does not decide"
  line as a note; each reply is shown whole, after `check_reply`, never word by word. Text is shown as written
  (`plain`: a "$" in "$1,850" would otherwise start math). A gateway error during a turn becomes a caution and
  the page goes on. `.streamlit/config.toml`: localhost only, no usage statistics sent to Streamlit, no
  first-run prompt, no Deploy button. `streamlit` added to `requirements.txt`. Was: the terminal only. Checked
  three ways: headless with Streamlit's `AppTest` (now ten smoke checks on `matters/t-smoke-app`, with a
  stand-in model); a live session in the browser pane on a scratch tenant (`t-ui-test`, moved to the Trash
  after): the lease uploaded and read, the issues and facts confirmed on the page's sheet, "What are my
  deadlines?" printed by the program, a legality question answered with the lease and statute quotes, a
  letter request (not drafted: the model asked for the address, then today's date, TODO item 39), End session;
  the record held one session from start to end. Known limits are TODO item 45. README: the front end is no
  longer only planned; Stack names Streamlit. CLAUDE.md and `setup.sh` name the new command.
- The chat returns blocks instead of printing, so a web page can show what the terminal shows (TODO item 31,
  first step). A block is `{"kind", "text"}`: `reply` is the model's words, every other kind the program's
  (`letter`, `cases`, `deadlines`, `caution`, `footer`, `timeline`, `notice`, `stop`). Was: `show_turn`,
  `check_reply`, `retry_empty`, and the command branches of `chat` printed as they went, and `run_sheet` was one
  loop of input and print. Now `agent.turn` runs one model turn and returns its blocks (built by `turn_blocks`,
  which replaces `show_turn`) and whether facts were proposed; it finds the turn's new messages from the
  checkpointer, so no caller keeps a count. `agent.command` answers `issues`, `drop`, and `timeline`, parsed as
  before; `check_reply` returns its caution lines; `retry_empty` returns blocks; `sheet_note`, `thread_config`,
  and `stop_block` hold what both front ends need; `chat` is the terminal loop over them, printing with
  `print_blocks`. The sheet is in pieces: `suggestion`, `row_notes`, `value_of`, `save_answer`, with `run_sheet`
  the terminal's loop over them. `read_lease` moved from `run.py` to `agent.py` and `NOT_COVERED` to `sheet.py`,
  so a second front end need not import the terminal script. A stand-in model drove the old and the new chat
  through the same scripted session (deadlines, a flagged reply with its line, every command, a letter, a sheet
  with a changed fact and a related issue, an empty reply twice, a drop): the screen, the transcript, and the
  events were identical, except a trailing space the old code printed after some blocks. Smoke: the smoke checks
  that read printed output read blocks now, and seven new ones (a reply's blocks in order, `print_blocks`, the
  commands and their transcript lines, `sheet_note`, a whole turn through a stand-in model, a drop that leaves
  no covered issue). DOCUMENTATION: the sheet's transcript field is `issues_suggested` (it said `issues_added`).
- Live check of the deadline receipt (`dev/eval_runs/2026-10-02-deadlines`, five deadline-heavy stories, 3 runs
  each, against the day before's final runs of the same stories): "What are my deadlines?" called the tool 6 of
  6 (was 4 of 6), a time question in plain words 9 of 9 (was 6 of 9), deadlines computed 12 of 12 (was 9 of 12),
  no copied deadline, no id in a reply, no empty turn. Runs meeting every expectation stayed 8 of 15: the misses
  are now letters (TODO item 39) and the classifier's not-covered note on the rent-notice story (item 42).
- `get_deadlines` gives the model a receipt with no dates; the program prints the listing (TODO item 44, done).
  Was: the model got the whole JSON, and once the tool ended the turn (item 19) that JSON stayed in the thread
  with no reply after it, so asked "What are my deadlines?" a second time the model copied it, or reworded a date
  from it, instead of calling the tool (violation_dog, 3 of 3 runs on 2026-10-02). Now the computation is
  `tools.deadline_listing()`, the tool returns content and artifact like `get_cases`, `show_turn` prints the
  artifact through `render_deadlines`, and the model's receipt (`deadline_receipt`) says how many dated deadlines
  were printed for which issues and which issues wait, and to call the tool again to show them. Rule 3: call
  get_deadlines alone every time, never answer from an earlier one, never write a deadline. The eval reads
  printed dates from the transcript's `shown`. Two smoke checks; the deadline checks use `deadline_listing`.
- Eval of the two changes above (`dev/eval_runs/2026-10-02-nc`, six stories, 3 runs each, no crash or gateway
  trouble): runs meeting every expectation 11 of 18 on the day before's code, scored by today's expectations,
  14 of 18 now. The roommate and towing stops showed their lease clause in 6 of 6; the noise story ran as
  neighbor_disturbance in 3 of 3 (one letter not drafted: the model asked to confirm). The dog-notice story fell
  to 0 of 3 on a weakness already seen once the day before, logged as TODO item 44.
- New playbook `neighbor_disturbance` (a neighbor or another tenant keeps disturbing the tenant, and the tenant
  wants the landlord to deal with it), with its label in `ISSUE_LABELS`. Was: a noise story was "other" and
  stopped (the eval's nc_noise, 12 of 12 runs). Sections 83.52, 83.56, 83.64, 83.42. Ten facts (what, who,
  whether that person rents from the same landlord, since when, how often, complaints, in writing, first
  complaint date, the landlord's response, shared with repair_not_made, reports elsewhere); no clocks, since
  ch. 83 part II sets no deadline for a landlord to act on one tenant's complaint about another. Four open
  questions, quoting the stored text: whose duty 83.52(7) states and whether it reaches a neighbor who rents
  from someone else; 83.56(2)(a)'s "a subsequent or continued unreasonable disturbance" as a remedy the landlord
  has, not a duty; what is unreasonable; whether 83.56(1) lets the tenant leave over it. Postures: preserve
  (the facts), assert (83.52(7) quoted), escalate (83.56(2)(a)'s words quoted). Version 0.1, verified_by null
  until the author's check. No lease profile field holds a conduct or nuisance clause, so the model cannot
  quote the lease's own rule on it (TODO item 43). Classify sends two noise stories to it and keeps roommate,
  towing, a repair, and a violation notice for the tenant's own parties where they were. Eval: nc_noise became
  noise_neighbors, a covered scenario. Playbook checks 0 failures; smoke runs it through the sheet and a
  letter; one `smoke_online` check. README's list of playbooks in scope gains it.
- The stop for a story the tool does not cover shows what the tool covers and the tenant's own lease on the
  subject (TODO item 32, done). Was: one line, "None of the situations this tool covers applies, so it stops
  here." Now `sheet.stop_text()` adds every playbook's description with how to come back to one (open the
  matter again and describe that part), and up to three lease clauses on the subject of what the tenant
  wrote, word for word with section, title, and page, and "This tool does not decide what they mean for you."
  The clauses are found by code, not the model: `lease.lease_clauses` splits the stored lease text at its
  numbered headings (78 clauses in the test lease), and `lease.clauses_about` matches the tenant's words
  against clause titles, and a short list of everyday words mapped to lease words (`LEASE_WORDS`: roommate to
  joint and several, car and towed to vehicle and park, parties to disturb and neighbor) against titles and
  text. On the test lease: a roommate story gets 21.3 Joint and Several Liability, a towing story 5.4 Vehicles,
  a noise story 5.2 Prohibited Uses, a cat 10.1 to 10.3, smoke 5.3; a remark about religion or stolen packages
  gets no clause. `run.py` prints it and writes a `printed` transcript line. Eval: `screen_must`, and the
  roommate and towing scenarios expect their clause. Four smoke checks.

## 2026-10-01

- The eval of 2026-10-01 written up in `docs/evals/2026-10-01/` (method, code and blind scores, the gateway
  failure, cases, not covered, a confirmation run); TODO items 32 to 42 added from it, item 12 and item 29
  given its data. Runs meeting every expectation: 32 of 48 on the code before the changes, 37 after, 39 with
  the follow-ups.
- The eval files its runs away (`dev/eval.py` `file_away`): each run's `matter.json`, events, and transcript are
  copied into `<out dir>/matters/`, and the `t-eval-` scratch tenants are removed from `matters/`, as smoke.py
  does with its `t-smoke-` ones. Was: every run left a tenant in `matters/` (144 after today's runs, each with
  a copy of the lease), and `run.py` lists every tenant id when a new matter starts. `dev/eval_runs/` is
  ignored by git; today's runs are kept there (`dev/eval_runs/2026-10-01/`), and their scratch tenants went
  to the Trash.
- `ask_json` parses with `strict=False`: a line break inside a quoted string is kept. Was: refused as an
  "Invalid control character", which crashed intake whenever the classifier's reason quoted a story typed on
  two lines; the mixed story (a heater and a remark about religion) crashed on 3 of 3 first attempts in the
  eval reruns, once the classifier began quoting its second line. Smoke check.
- The eval keeps a crashed first attempt's screen (`<scenario>_r<k>_attempt1.out`). Was: the retry wrote over
  it, so three crashes in the eval reruns could not be traced.
- The program's "does not decide" line also goes under a reply that quotes only the lease. Was: statute quotes
  only; in the eval after-runs, "Do I have to let them take that money?" was answered with a lease quote and
  no line. `agent.not_decided_line` now also counts a quoted passage found in a lease profile quote. Smoke
  check.
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
