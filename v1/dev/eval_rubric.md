# Scoring rubric: slips in a landlord-tenant tool's applied answers

The rubric for blind scoring since 2026-10-02 (TODO item 49), when the tool began applying the law to the
tenant's facts (README, Purpose). It replaces the organizing rubric of 2026-10-01
(`docs/evals/2026-10-01/method/rubric_eval.md`), whose LAW and CASE_APPLIED categories counted applying the law
as a slip. Revised 2026-10-12 (TODO item 116) for the conversation the author asked for (README, Purpose): using what
the tenant said before they confirm it, asking in the chat for what an answer turns on, and offering the next step
once are no longer slips; REPEATED, LEASE_PUNTED, and two ratings per transcript are new.

You score the MODEL REPLY parts of chat transcripts. The tool applies the lease, the stored statute
(Fla. Stat. ch. 83, part II), and the cases it gives the model to the tenant's facts, and helps the tenant get what
they want, in a conversation. An answer to a question about the law should make clear, in plain words: asked what
the tenant can do, whether they can before any step toward it; what that turns on, each rule in one plain sentence
cited to its section, lease section, or case and page (the program prints the cited words under the reply, so the
reply does not recite them); whether the tenant's facts and their lease meet each condition, or what is not known
yet and how it would change things; what is left to do; and any open question in the way, with its readings. A
follow-up builds on what was already said. It never chooses among the options for the tenant, never works out a
date, and never states law it does not cite.

Other parts of each transcript were produced by the program, not the model; never score them:
- `[PROGRAM PRINTED, from get_deadlines]`, `[PROGRAM PRINTED, from draft_letter]`, `[PROGRAM PRINTED, from
  get_cases]`: deadlines, letters, and court cases printed by code. The model also received the cases' text.
- `[PROGRAM CAUTION shown to the tenant]`: automatic cautions. Hints, not verdicts: judge the reply yourself.
- `[PROGRAM LINE printed under the reply]`: a fixed line the program adds ("This is the tool's reading ...").
- `[PROGRAM PRINTED, the statute and lease words the reply cites]`: the cited words, printed by code; judge the
  reply's plain-words rule against them.
- `[SHEET, tenant answered]` or `[CONFIRMED by the tenant]`: facts the tenant confirmed, on a form before the chat
  or after a reply (some transcripts show one kind, some the other). A fact is confirmed only from the moment its
  line appears (facts confirmed in an earlier session are in the context file).
- `[PROGRAM NOTE to the model]`, `[model called] ...`, `[tool result, not shown to the tenant] ...`: context.
- `TENANT COMMAND`: answered by the program, not the model.

The context file for the scenario gives the tenant's description at intake, the chat lines, what the lease holds on
the chat's points for some stories, and, for each situation the story is about, the statute sections the model had,
the open questions (with their readings), and the letter postures.

## Categories

Count at most one slip per category per reply. Give each slip a short verbatim excerpt as evidence; mark a
borderline call "borderline: ...".

Applying:
- OPTION_BEFORE_OPEN (since 2026-10-04): the steps of an option (how to end the lease, how to withhold rent)
  given before, or without, whether that option is open on the tenant's facts.
- QUOTES_ONLY: a question about the law answered with quotes and no application to the tenant's facts (the
  rule set out, nothing said about whether the tenant's facts meet it or what follows), or with "This tool
  does not decide that." where stored text answers. "The lease and statute text I have do not answer that."
  is not a slip when nothing quoted in the transcript speaks to the question.
- UNCONFIRMED_FACT: the application treats as true a fact neither the tenant said in this chat nor the record holds
  (not confirmed, not in a lease clause, not in the tenant's own words), instead of naming it as not known yet, or
  calls a fact the tenant only said "confirmed". Using what the tenant said as what they said ("you told me ...")
  is the wanted form (since 2026-10-12).
- CONDITION_MISSED: the reply concludes from a quoted rule while leaving out one of its conditions the facts
  turn on (e.g. forfeiture under 83.49(3)(a) stated without the 30-day period; withholding rent without the
  written notice 83.60(1)(b) requires).
- CONDITION_WRONG: a condition called met or failed against what the record shows, or a rule applied to a
  situation its words do not reach (a duty of 83.51(1) applied to an item only 83.51(2) lists).
- OPEN_CLOSED: an open question of the context file presented as settled, one reading picked, or the tenant asked
  to settle it. Giving the readings and what each would mean is the wanted form. A reading that is not in the
  context file is LAW_UNSOURCED.
- CASE_MISREAD: a case's facts, rule, or holding misstated against the printed case text, a case named that
  the tool did not give in this chat, or a case's rule said to reach the tenant with no word on how alike the
  facts are.
- ONE_SIDED: the reply relies on cases from a get_cases result and leaves out one in the same result that
  cuts against the tenant, or leaves out the half of a rule that helps the landlord (the forfeiture without
  "may file an action for damages after returning the security deposit").
- CHOICE_MADE: the reply chooses for the tenant ("you should withhold rent", "your best option is to sue",
  "I recommend"). Laying out options and what each requires is the wanted form.
- GAP_AS_FACT (since 2026-10-04, TODO item 85): a point the tool does not know stated as a fact: "the lease does not
  mention X" said from the clauses the tool reads, with no search of the lease that found nothing, or when a search
  found the clause; "the landlord forfeited the deposit" while whether a notice came is not confirmed; "your
  county's code requires it"; a date or a yes or no for a period the program could not count. The program's options
  and its list of what the tool does not know give each such point as one the tenant can tell the tool, can check,
  not settled, or outside the tool; saying which, and what follows either way, is the wanted form.
- UNKNOWN_UNTIED (since 2026-10-04, TODO item 85): an unknown named without what it changes for the tenant ("that
  depends on your lease" and nothing on what follows if it does and if it does not), or without who can settle it
  (the tenant on the form, the tenant checking the lease, a notice, a code office), when the answer turns on it.
- LEASE_PUNTED (since 2026-10-12): the tenant sent to check their lease for a point the tool could read (with its
  lease search, or in the lease words printed in the transcript) instead of reading it and saying what it says.
  Sending the tenant to check what the tool cannot read (military orders, a local code, a paper it does not hold)
  is fine.
- OVERCLAIM: a prediction the record cannot support ("you will win", "you are safe", "you will get your money
  back") rather than what follows on the facts under the quoted rule.

Quoting and the record (as before):
- RECITED (since 2026-10-04): a statute or lease passage pasted into the reply (more than a sentence) instead of
  cited, or what the tenant already confirmed or said listed back.
- QUOTE_UNMARKED: lease or statute text reproduced word for word without quote marks, or a quote with no source
  next to it. A rule restated in plain words with its cite is not this slip.
- QUOTE_WRONG: words in quote marks that are not word for word in their source, or cited to the wrong section,
  subsection, case, or page. Spacing artifacts ("reaso n"), curly versus straight apostrophes, and a trailing
  period are not slips.
- LAW_UNSOURCED: a legal rule stated with no cite to a stored section, lease section, or printed case behind
  it, or with a cite whose printed words do not say it (a rule from memory, another statute, federal law). A
  rule in plain words with a cite whose words say it is the wanted form (since 2026-10-04).
- DATE_MADE: a date that is not in the record (tenant's words, SHEET values, lease quotes, printed
  deadlines), or a date the model counted, added, or compared itself ("would have ended on August 29").
  Applying the program's "passed" or "upcoming" is fine.
- ID: a field or clock id, a prompt part's name as the prompt writes it, in capitals ("YOUR FACTS shows",
  "DEADLINE STATUS"), or a rule's number ("rule 8") in a reply ("claim_notice_received"). A source named in plain
  words ("your lease", "the program's deadlines", "the statute does not settle this") is not a slip.
- ASK_AGAIN (since 2026-10-12; was CONFIRM_IN_CHAT): the reply asks for a fact the tenant already gave, the record
  holds, or the lease holds, or asks for more than two things at once. Asking one or two things the answer turns on
  is the wanted form.
- OFFER: an offer the tenant did not ask for that is not the next step toward what they want, or the same offer made
  again. Offering the next step once is the wanted form (since 2026-10-12).
- REPEATED (since 2026-10-12): a reply that repeats a substantial part of an earlier reply in the same transcript (the
  same list of conditions, the same steps) instead of building on it or referring back to it.
- POSTURE_OWN_WORDS: describes preserve, assert, or escalate other than with the posture lines of the context file.
- LETTER_ORDER: letter steps out of order, or asking again for details the tenant already gave.
- DEADLINE_REPEAT (minor, reported separately): repeats or rewords dates from the deadlines the program
  printed.

## Ratings (since 2026-10-12)

For each transcript, two ratings from 1 (poor) to 5 (excellent), each with a one-line reason:
- helpful: would a college tenant with no legal training finish this chat knowing where they stand on what they
  asked and what to do next?
- conversational: do the replies read as one conversation, building on each other and on what the tenant said,
  rather than as separate standalone answers?

Score what is there, consistently across runs. When a case is borderline, decide by the definitions above and
say so in the evidence.
