# TODO

The working list. Move an item to CHANGELOG.md when it is done, with the date. Reorder freely. Keep the
"Open questions" section for things that need a decision before code is written.

## What the tool knows (the author's decision of 2026-10-04)

After items 72 to 77 the author asked for a general theme, not fixes aimed at the example that showed each one
(an AC): the chatbot must be aware of what it knows and does not know, and of whether that changes what the tenant
can do (README, Purpose and non-negotiables). Seen on 2026-10-04: "the lease does not mention air conditioning",
"the lease does not contain a holdover clause", "the lease does not mention any late fee", each said from the
16 clauses the profile holds while the lease had the clause; and ending the lease over an AC shown as not settled
on the statute alone while the lease's Article 7.2 promised the repair. Rule pairs alone did not change such
behavior (items 54, 76); what the program computed did (options, deadlines). So the knowledge is computed by code.
Items 81 to 85 were done 2026-10-04 and 05 (CHANGELOG; the eval in `docs/evals/2026-10-04-know/`). What is left here
is the author's.

84. For the author: check the options' gates in all ten playbooks against `statutes/` (written 2026-10-04, items
    72, 81, and 84; CHANGELOG says what each holds), then sign off as for item 2. In repair_not_made: whether a
    problem 83.51(1)(b) does not name leaves ending the lease not known yet (the lease's promise, then a code the
    tenant can check) rather than not settled; the new gate, the duty not changed in writing, which 83.51(1) allows
    only for a single-family home or duplex; rent paid with knowledge as a gate on ending the lease only; the open
    question on that waiver and its two readings. Elsewhere: 83.55 added to landlord_entered_unannounced's sections
    for damages from an entry the statute does not allow, and that option's seven gates read from 83.53(2); the
    retaliation defense's gates (83.64), including good cause, which the landlord must prove; whether a neighbor's
    disturbance can end the tenant's lease only through a lease promise. A limit to decide on: wants_to_leave_early's
    fee "no more than 2 months' rent" is left to the tenant to check, though both amounts are on the record (the
    rent may come from the lease's words); a computed comparison would make it known.
86. For the author, from the eval of items 81 to 85 (`docs/evals/2026-10-04-know/`): a lease clause the tool has read
    whose words plainly cover the problem (the test lease's 7.2, "Landlord shall repair the heating,
    air-conditioning ...") still leaves the lease's way of the duty condition "not known yet: the sheet asks" until
    the tenant confirms it; in one AC run the model searched the lease, found 7.2, and treated the duty as met ("the
    lease duty exists") against the program's state. Decide whether the tenant's confirmation stays the only way a
    lease clause decides a condition, or whether a clause the tool has read can (and then how code, not the model,
    would read it).

## Applying the law

The author's decision of 2026-10-02 (README, Purpose): an answer applies the stored statute and cases to the
tenant's confirmed facts instead of listing quotes. Seen on the web page that day: "what can I to sue the
landlord" got three statute quotes (83.56(1), 83.60(1)(b), 83.64(1)) and "This tool does not decide that."
In development, on test matters only. Items 46 to 50 were done the same day (CHANGELOG, 2026-10-02); the first
eval of applied answers (`docs/evals/2026-10-02-apply/`) left the author's sample (49) and items 51 to 60, the
structural ones first.

The author's decision of 2026-10-04 (README, Purpose), after trying the web page with a real lease: (1) a reply
said how to end the lease for an AC not repaired (a new notice, 7 days, then terminate) and only in the next
reply that an AC may not be a duty 83.56(1) reaches, so whether an option is open must come first, checked by
code; (2) replies recited too much (the tenant's confirmed facts listed back, whole sections and a 1,900-character
lease clause pasted), so an answer cites and the program prints the cited words. Items 72 to 77 were done that day (CHANGELOG); what remained went to the section above.

49. The author's sample of the first applying eval (`docs/evals/2026-10-02-apply/`): six transcripts, their
    contexts, and a scoring sheet in `dev/eval_runs/2026-10-02-apply-after/author_sample/` (not committed: they
    quote the test lease). The question code and the blind scorers cannot settle: is each application right on
    the law? Mark the rubric's categories (`dev/eval_rubric.md`) and right, wrong, or partly; the scorers'
    calls on the same transcripts are in `results/blind_score_*.json` (codes in `blind_key.json`).
59. Dates the model made (blind 12.5; code 4): 30 days counted from a move-out ("2026-07-30"), "about 52 days",
    "whichever date controls, the 30-day period has passed". Rule 3's pairs are in the prompt; keep counting. After
    items 51 to 53 (2026-10-03): 4 turns, all counts like "Thirty days after June 30, 2026 is July 30, 2026.",
    now caught by the eval's echo measure (a computed deadline in a reply). After items 54 to 61: 3 turns
    (`docs/evals/2026-10-03-items54-61/`), "2026-07-30" counted from a move-out again.
63. Condition slips the blind scorers found on 2026-10-02 that no failure mode names yet (item 55 added five).
    For the author: which belong in the playbooks, each quoted from `statutes/`: 83.49(5) left out where the
    record shows no 7-day vacate notice (wants_to_leave_early, the deposit playbooks); 83.64(1)'s examples read
    as the only protected acts; 83.51(1)(b)'s duties applied without its opening condition on codes, and a
    case's common-area duty (83.51(2)(a)) applied inside the unit (repair_not_made); 83.56(5)(a)'s waiver
    applied to the 83.60(1)(b) defense; a rent increase read as a decrease against the test lease's rent (item 60).
    Also wants_to_leave_early's fee_notice_period, which has no readings: in 3 of 3 runs the model took the
    lease's 7-day notice of vacating as the fee's notice period (scored borderline). Whether it needs readings.
64. Quote cautions left after item 58 (replayed on the runs of 2026-10-03, 54 under the replay's approximate
    given text): most are real (the tenant's words reworded inside quote marks, "I have not sent a written
    objection to the landlord's claim."; the statute misquoted, "decrease in services"; a sentence in
    83.64(1) cited to 83.64(1)(a)). About 12 are false: a quote takes the cite next to it in the prose as its
    source, so a case's, the lease's, or the tool's words, or a phrase of 83.60 followed by "83.51(1)" in the
    reply, are checked against the wrong section (`citations.quoted_passages`). An option: a quote cited to a
    section it is not in, but word for word in what the model was given, is not flagged for the section. Since
    `search_lease` (item 82) more lease words are quoted beside statute cites: in the eval of 2026-10-04 quote cautions
    rose 8 to 19, among them "If Landlord accepts Rent from Tenant..." (Lease 2.4) checked against 83.58.
71. What the blind scoring of 2026-10-03 left (`docs/evals/2026-10-03-blind/`; 36 of 115 legal answers applied
    well, against 21 of 103 on 2026-10-02): rules restated without their quote (46.5, unchanged), conditions
    applied wrong (30.5, unchanged; item 63 holds the ones for the author), quotes without marks (26) and facts
    not confirmed (21.5, both up, mostly borderline), dates worked out (13), cases misread or one-sided (17.5,
    13.5). Two stories went down: the late claim (Plakhov v. Serova left out or misread, days counted) and
    retaliation (83.64(1)'s examples read as the only protected acts).
67. The eval's "cases not given" (`CASE_NAME` in `dev/eval.py`) counts part of a given case's name as another
    case: "Inc. v. Varnado", "Income Realty v. Bentley", "Follows Durene v. Alcime" (3 turns, eval of
    2026-10-03). Match against the names `get_cases` printed (`agent.named_cases`) instead.

## Harness and code

Code-side checks and bookkeeping that hold whatever the model does. Ahead of model behavior.

87. Eval checks that count a right answer as a slip (eval of 2026-10-04, items 81 to 85): the dog story's must_not
    "you (are|will be) safe" matches "Whether you are safe turns on ..." (3 of 3 runs after, 1 before); the lease
    absence screen (`dev/eval.py`, `LEASE_ABSENT`) counts a reply repeating what the tenant confirmed ("your lease does
    not say the landlord repairs this kind of problem", 3 mold runs). Narrow both.

1. Clocks `compute_deadlines` cannot compute yet: (a) court business days are done for 83.56(3) in the
   Eighth Judicial Circuit, 2026 and 2027; other circuits need their own memoranda (add a county's circuit
   when a tenant there uses the tool), and each new year's memorandum must be added when the circuit
   publishes it (the 2028 one is needed for any count reaching January 2028); 83.60(2) waits on the open
   question below; (b) periods the lease sets (83.575(1)-(2), 83.595(4)); needs a clock whose length is a
   confirmed fact; (c) hours (83.53(2)); (d) months (83.56(2), 12 months). Decide which to support.

75. A lease PDF whose text PyPDF2 cannot fully decode (2026-10-04, a 57-page lease made by FPDF): pages 1 to 36
    use Type3 fonts with custom glyph names, and `lease.ingest_pdf` turned a fifth to three quarters of their
    words, the section headings, and the apostrophes into Dingbats symbols; pages 37 to 57 read cleanly. Gemma
    still found all 15 profile fields, but a long clause came back with the symbols in it, the model quoted
    it with them, and the quote check flagged the quote though its words matched the lease. Try `pypdf`
    (PyPDF2's successor) or `pdfminer.six` on such a file; switch `ingest_pdf` if one reads it.
33. Some live sessions crash on their first attempt and pass on the second: 6 of 48 runs on the code before
    the eval changes and 3 of 48 after (2026-10-01), three of them one mixed story. Two causes found: malformed
    JSON (now asked for again) and a line break inside a quoted JSON string (the mixed story; now accepted,
    `strict=False`). The other screens were written over; the eval now keeps a crashed first attempt's screen.
    Read the next ones before changing anything.

## Playbooks

2. Hand check of the seven playbooks written 2026-09-27 (repair_not_made, notice_received_nonpayment,
   notice_received_violation, landlord_entered_unannounced, rent_increased, wants_to_leave_early,
   lease_ending): read each quote against `statutes/`, then set `provenance.verified_by` and `verified_on`.
   Also replace the deposit playbooks' 83.42 exclusion ("Not yet read") with the 83.42(1) quote the new
   playbooks carry.
3. Counting convention is a stated assumption in each playbook. Check the time-computation rule in the
    corpus before relying on it. Do not settle this from memory.

34. For the author: `notice_received_violation` does not list 83.64 (retaliatory conduct) in `sections`. A
    violation notice that follows a tenant's complaint is the setting of Salmonte v. Eilertson; in the eval
    (cases_retaliation) its case topic was offered only because the story also confirmed repair_not_made.
    Adding the section is a playbook change for the author to check against `statutes/`.

78. Profiles read before 2026-10-04 lack the repairs clause (`maintenance_and_repairs` is `None`, "not read"): the
    test matter `t-test`, and any saved matter. A way to read just the new clause from a matter's stored
    `pages.json`, without starting a new matter, for the author to run on a matter of their choosing.
43. No lease profile field holds a conduct, nuisance, or vehicle clause (the test lease has them at 5.2 and
    5.4), so the model cannot quote the lease's own rule in a neighbor_disturbance chat or letter; only the
    stop text shows such clauses, by code. Consider a `conduct_and_use` field in `lease.LeaseProfile` (a
    change to extraction: every lease would be read again).

## Case law

The case wiki (README, The unit of legal knowledge): linked markdown pages in `wiki/`, one per case and one
per topic, with topics made as they emerge from the cases, not fixed in advance. `cases/` (the opinions,
built 2026-10-01, 81 opinions) comes first; then these, in order.

24. The case wiki and its checks: a schema page, an index built by code, a log, and code checks run like
    the playbook checks. Done 2026-10-01: every opinion in `cases/`, 81 case pages and 40 topics (28 case
    pages untagged, with scope notes). Next: the author reads each page against its opinion and verifies it
    (`python wiki.py verify`); only verified pages go further, and only tagged ones ever load for a tenant,
    so untag a page that should not (a commercial lease, e.g. Multach v. Adams). While verifying, check each case's status in
    Westlaw (the print flags 27 opinions; one red-striped, Charlemagne v. Francis), and look at the questions
    the ingest left in `wiki/log.md` (2026-10-01, the remaining 65).
29. Which topic the tenant sees is still the model's choice (in the eval of 2026-10-01 each court question
    got the same topic in every run, item 36). Asked about lawyers' fees in a deposit case,
    one run of `deposit_cases` called Fees and costs in a suit over the deposit and two called Prevailing
    party fees under 83.48, so the tenant saw different sets of cases. Consider printing every offered topic
    a question could fall under, or a chat command `cases` that lists the topics so the tenant picks.
35. Case topics per playbook are many and mixed: 13 for the deposit playbooks, 27 for repair_not_made, among
    them procedural topics (Points not raised in the trial court, Applying an amended statute) and deposit
    topics under the rent-notice playbooks, because a topic is offered when any page tagged with one of the
    playbook's sections is on it. Consider sections on the topic pages (or a topic list per playbook) before
    any topic list is shown to a tenant (item 36).
36. Cases reach a tenant only when the tenant asks what courts or judges said (rule 8). In the eval
    (2026-10-01) plain questions ("Has this happened to other people? Did a judge ever ...") reached
    `get_cases` on a topic whose cases include the one with facts like the tenant's in 17 of 18 runs before
    the changes and 16 of 18 after (one count copied into the topic name, since accepted by
    `tools.topic_named`; one statute answer). A tenant who never asks never sees them. If that matters, a line
    the program prints, listing the case topics for the confirmed issues, keeps the choice with the tenant;
    do it after item 35. Since 2026-10-02 (item 47) the model also calls `get_cases` when a topic is on the point
    it is applying, and compares each case's facts with the tenant's.
37. No case page speaks to damage that was already there at move-in (the claim_carpet story). Asked "Did a
    judge ever make a landlord give back money for damage that was already there?", the model printed the
    notice-of-claim topic, the nearest deposit topic. A gap for the author's research, not a code change.
26. `search_cases(phrase)`, like `search_statute`, for a tenant whose situation fits no playbook ("other").
    Reconsider before building: here the model, not code, decides what to look for from the tenant's
    story, which is selection by judgment, the unlicensed-practice risk discussed 2026-10-01 (Brumbaugh:
    general information is allowed, applying law to one person's facts is not). Since 2026-10-02 applying
    the law is the plan (items 46, 47), so in development that reason is gone; what remains is whether the
    model's search finds the right cases.
27. For the author's research: no appellate case on the 83.42(1) exclusion for residence incidental to
    educational services turned up in the candidate list's sources; it decides whether ch. 83 applies to
    on-campus housing at all.
28. For the author's professional responsibility professor: since 2026-10-02 the tool applies the law to a
    tenant's facts (README, Purpose), so the question to bring is what supervision or review it needs before
    any tenant uses it. (Was: whether computing a tenant's own deadline, `compute_deadlines`, came close to
    applying law to facts.)

## Interface

45. The web page (`app.py`), limits seen while building it (2026-10-02): reopening a matter does not show
    earlier sessions' chats (the terminal does not either; the transcripts are in `sessions/`); one browser
    tab at a time, since every tab of the one Streamlit program shares `record.matter`; closing the tab
    leaves the session with no `session_ended`, as a crash does in the terminal; a file the tenant wants
    stored goes in only by its path, through the model's `add_artifact`, not by upload on the page. Seen with a
    57-page lease (2026-10-04): reading it took about four minutes with no sign of progress, a second click
    on start began a second matter and a second request to the gateway (both ran), and the extraction call
    has no time limit, so a stalled gateway would spin forever.

## Model behavior (later)

88. Prompt parts named and ids written rose with items 81 to 84 (eval of 2026-10-04): turns with a prompt part's name
    8 to 15, mostly "(WHAT THE STATUTE DOES NOT SETTLE)" written as a source (12 turns, 2 before); field ids 9 to 17;
    the blind scorers' ID 15.5 to 24.5 (firm 12.5 to 21.5). The options and the part of what the tool does not know
    point to the other parts by name. Also the options' own plain words put in quote marks (the dog story: "the
    violation did not continue after...", 3 quote cautions in 3 runs).
89. A lease searched and then misread (eval of 2026-10-04): "The lease does not state a specific late-fee amount; it
    only mentions late charges in ... Lease Section 3.4" (3.3 sets $75); "The lease does not provide a specific
    holdover penalty" (15.1 sets double rent); "the lease does not forbid it" with no search (a letter, the dog story).
    The blind scorers' firm GAP_AS_FACT fell 21.5 to 5.5; these are most of what is left.

Slips seen in live runs and not fixed yet. Rule numbers are the current rules (version F, adopted
2026-10-01). Items 4 to 23, logged under earlier rule sets, were taken off on 2026-10-01: most are now
handled in code (deadlines printed by the program, the empty-reply retry, the duplicate-draft stop, the
quote and cite checks) or by the current rules, which showed none of those slips in the trial
(`docs/trials/2026-10-01-rules/`). CHANGELOG.md (2026-10-01) says where each went. Item numbers are never
reused, so older references (smoke check names, the changelog) still point to the right slip.

12. The model suggests a claim letter's printed date as the date it was received (`claim_notice_date`; the
    printed date is `claim_notice_dated`). Still seen with the current rules: 1 of 3 claim runs in the trial
    (the old rules also 1 of 3). The sheet shows the suggestion and the tenant corrects it, logged as
    corrected. (Item 21 was the same slip.) Not seen in the eval of 2026-10-01: claim_carpet, whose letter is
    dated three days before it arrived, got the right suggestion in all 9 runs (3 per side, and the first baseline).

38. Asked which posture is "the nicest", the model calls preserve "the gentlest option" (2 of 3
    deposit_ghosted after-runs, 2026-10-01), though rule 6 has that "Not:". Scored POSTURE_OWN_WORDS. Still 1
    to 3 of 3 in each eval of 2026-10-03 (`docs/evals/2026-10-03-items60-66/`).
39. Letter requests: the model still asks again for something the tenant said (the amount, the days, the
    delivery) in about 1 in 3 letter runs (blind scorers: 9 slips before the changes, 6.5 after, 2026-10-01),
    and in the confirmation run it asked "is that correct?" until the scripted tenant ran out of lines (15 of
    21 letters drafted, against 20 of 21 the run before). A code-side option: fill the ask from confirmed
    facts (the deposit amount, the forwarding address) so fewer details are left to ask. On 2026-10-02 the
    carpet story's letter was drafted in 0 of 3 runs: asked again "What do you want the landlord to do?", asked
    for today's date (the letter fills it in), and once asked the tenant to quote the lease's notices clause
    (rule 6's "quote the notices clause" read as an instruction to the tenant). Now the most common miss. Seen
    again in the web page's live check (2026-10-02): asked for the forwarding address (fair: the ask needs it),
    then for today's date.
40. "The lease and statute text I have do not answer that." to a legal question the playbook does not list
    as open (whether the renewal must be signed by October 15; changing the locks): the blind scorers count
    it as LAW under the rubric's literal rule (12 of 38 after-runs' LAW calls, most marked borderline). Decide
    whether this line is the wanted answer there or the quote-then-"does not decide" form is. Superseded by
    item 46: an answer applies what is stored, and this line is left for a question nothing stored speaks to.
    After item 52 (eval of 2026-10-03), the renewal question still got this line in 2 of 3 runs, and 3 of 3
    after items 54 to 61.
62. Offers the tenant did not ask for (rule 9) rose from 3 to 6 turns in 48 runs after items 51 to 53 (eval of
    2026-10-03), with more replies after a deadline listing. Keep counting (`OFFER_WORDS`, rubric OFFER).
68. The model copies a tool's receipt into its reply: "The program printed the tenant's deadlines: 0 dated, for
    no issue. You are not shown the dates; ..." (eval of 2026-10-03, once), and earlier the receipt's part name.
69. The duplex story with its own lease (a 2024 lease, month to month since 2025): the replies asked the sheet's
    own questions in the chat, in quote marks, in 3 of 3 runs, then 0 of 3 (evals of 2026-10-03). Rule 4's "Not:".
70. "If my friend picks her up this weekend, am I safe?": "you are safe" in 0, 2, 0, 3, then 1 of 3 runs across
    the evals of 2026-10-03, a prediction the record cannot support (rubric OVERCLAIM). Rule 9 does not name it.
41. Empty replies remain rare (2 and 3 turns in 48 runs before and after, 2026-10-01); `reply_empty` now logs
    the gateway's finish_reason, so the next ones show whether the model or the gateway left them empty.

42. Classify adds "other" next to a covered issue for a detail of it: after the wording fix, still 2 of 3
    rent-notice runs (3 of 3 on 2026-10-02; a partial payment with no receipt read as a separate problem), while the mixed story
    (a heater and a remark about religion) now gets "other" in 3 of 3 (was 0 of 6). The note it triggers is
    mild ("may not be covered ... continues with what it does cover"). Options: keep it; ask the classifier
    to quote the separate problem and check the quote is not a fact a playbook asks for; or drop "other"
    beside covered issues again.

## Open questions

- Counting court business days (83.56(3)), for the author to research: whether the delivery day counts,
  what happens when the notice is delivered on a weekend or a holiday, and when the last day ends. The tool
  counts forward from the delivery date, the delivery day not counted, and labels it an assumption.
- Which holidays are "court-observed holidays only" (83.56(3)): the tool skips every holiday in the circuit
  Chief Judge's memorandum, including those marked as designated by the Chief Judge and the additional
  discretionary ones. And whether 83.60(2)'s "legal holidays" is the same list, since 83.56(3) defines the
  term "for the purpose of this section". Until settled, 83.60(2) is not computed.
- Playbook open question (deposit_not_returned): whether returning keys one day before the term end is
  "vacating before the expiration of the term." The 7-day clock currently applies whenever
  `early_or_periodic` is confirmed true.
