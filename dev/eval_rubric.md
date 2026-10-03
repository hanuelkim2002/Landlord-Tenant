# Scoring rubric: slips in a landlord-tenant tool's applied answers

The rubric for blind scoring since 2026-10-02 (TODO item 49), when the tool began applying the law to the
tenant's facts (README, Purpose). It replaces the organizing rubric of 2026-10-01
(`docs/evals/2026-10-01/method/rubric_eval.md`), whose LAW and CASE_APPLIED categories counted applying the law
as a slip.

You score the MODEL REPLY parts of chat transcripts. The tool applies the lease, the stored statute
(Fla. Stat. ch. 83, part II), and the cases it gives the model to the tenant's confirmed facts, and says what
follows. An answer to a question about the law should give, in plain words: the rule, quoted with its source;
the tenant's facts it turns on, each from the record; for each condition of the rule, whether those facts meet
it, fail it, or are not known yet; what follows on those facts, including the options the stored text gives
and what each requires first; and any open question in the way, with its readings. It never chooses among the
options for the tenant, never works out a date, and never states law it does not quote.

Other parts of each transcript were produced by the program, not the model; never score them:
- `[PROGRAM PRINTED, from get_deadlines]`, `[PROGRAM PRINTED, from draft_letter]`, `[PROGRAM PRINTED, from
  get_cases]`: deadlines, letters, and court cases printed by code. The model also received the cases' text.
- `[PROGRAM CAUTION shown to the tenant]`: automatic cautions. Hints, not verdicts: judge the reply yourself.
- `[PROGRAM LINE printed under the reply]`: a fixed line the program adds ("This is the tool's reading ...").
- `[SHEET, tenant answered]`: facts the tenant confirmed on a form. A fact is confirmed only from the moment
  its SHEET line appears (facts confirmed in an earlier session are in the context file).
- `[PROGRAM NOTE to the model]`, `[model called] ...`, `[tool result, not shown to the tenant] ...`: context.
- `TENANT COMMAND`: answered by the program, not the model.

The context file for the scenario gives the tenant's description at intake, the chat lines, the facts
confirmed before the chat, and each active playbook's open questions (with their readings) and posture lines.

## Categories

Count at most one slip per category per reply. Give each slip a short verbatim excerpt as evidence; mark a
borderline call "borderline: ...".

Applying:
- QUOTES_ONLY: a question about the law answered with quotes and no application to the tenant's facts (the
  rule set out, nothing said about whether the tenant's facts meet it or what follows), or with "This tool
  does not decide that." where stored text answers. "The lease and statute text I have do not answer that."
  is not a slip when nothing quoted in the transcript speaks to the question.
- UNCONFIRMED_FACT: the application treats as true a fact the record does not hold (not on a SHEET line, not
  confirmed earlier, not in a lease quote), instead of naming it as not known yet. "You said X" with X then
  treated as not known yet is fine.
- CONDITION_MISSED: the reply concludes from a quoted rule while leaving out one of its conditions the facts
  turn on (e.g. forfeiture under 83.49(3)(a) stated without the 30-day period; withholding rent without the
  written notice 83.60(1)(b) requires).
- CONDITION_WRONG: a condition called met or failed against what the record shows, or a rule applied to a
  situation its words do not reach (a duty of 83.51(1) applied to an item only 83.51(2) lists).
- OPEN_CLOSED: a playbook open question presented as settled, one reading picked, or the tenant asked to
  settle it. Giving the readings and what each would mean is the wanted form.
- CASE_MISREAD: a case's facts, rule, or holding misstated against the printed case text, a case named that
  the tool did not give in this chat, or a case's rule said to reach the tenant with no word on how alike the
  facts are.
- ONE_SIDED: the reply relies on cases from a get_cases result and leaves out one in the same result that
  cuts against the tenant, or leaves out the half of a rule that helps the landlord (the forfeiture without
  "may file an action for damages after returning the security deposit").
- CHOICE_MADE: the reply chooses for the tenant ("you should withhold rent", "your best option is to sue",
  "I recommend"). Laying out options and what each requires is the wanted form.
- OVERCLAIM: a prediction the record cannot support ("you will win", "you are safe", "you will get your money
  back") rather than what follows on the facts under the quoted rule.

Quoting and the record (as before):
- QUOTE_UNMARKED: lease or statute text reproduced without quote marks, or a quote with no source next to it.
- QUOTE_WRONG: words in quote marks that are not word for word in their source, or cited to the wrong section,
  subsection, case, or page. Spacing artifacts ("reaso n"), curly versus straight apostrophes, and a trailing
  period are not slips.
- LAW_UNSOURCED: a legal rule stated in the model's own words with no quote behind it anywhere in the reply
  (a rule from memory, another statute, federal law). Restating a quoted rule in plain words next to the
  quote is fine.
- DATE_MADE: a date that is not in the record (tenant's words, SHEET values, lease quotes, printed
  deadlines), or a date the model counted, added, or compared itself ("would have ended on August 29").
  Applying the program's "passed" or "upcoming" is fine.
- ID: a field or clock id, a prompt part's name as the prompt writes it, in capitals ("YOUR FACTS shows",
  "DEADLINE STATUS"), or a rule's number ("rule 8") in a reply ("claim_notice_received"). A source named in plain
  words ("your lease", "the program's deadlines", "the statute does not settle this") is not a slip.
- CONFIRM_IN_CHAT: the reply asks the tenant, in the chat, to confirm or supply a fact the sheet asks.
- OFFER: offers a letter or any action the tenant did not ask for ("Would you like me to draft ..."). A step
  the statute requires before an option, stated as part of the answer, is not an offer.
- POSTURE_OWN_WORDS: describes preserve, assert, or escalate other than with the playbook's posture lines.
- LETTER_ORDER: letter steps out of order, or asking again for details the tenant already gave.
- DEADLINE_REPEAT (minor, reported separately): repeats or rewords dates from the deadlines the program
  printed.

Score what is there, consistently across runs. When a case is borderline, decide by the definitions above and
say so in the evidence.
