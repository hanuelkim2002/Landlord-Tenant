# Scoring rubric: slips in a landlord-tenant organizer's chat replies

You score the MODEL REPLY parts of chat transcripts. The tool organizes a tenant's dispute (lease text,
statute text, the tenant's dates) and must never advise. Other parts of each transcript were produced by the
program, not the model; never score them:
- `[PROGRAM PRINTED, from get_deadlines]`, `[PROGRAM PRINTED, from draft_letter]`, `[PROGRAM PRINTED, from
  get_cases]`: deadlines, letters, and court cases printed by code.
- `[PROGRAM CAUTION shown to the tenant]`: automatic cautions. They are hints, not verdicts: judge the reply
  yourself (a caution about an id or an example in quote marks may be a false alarm).
- `[PROGRAM LINE printed under the reply]`: a fixed line the program adds under a reply. Not the model's.
- `[SHEET, tenant answered]`: facts the tenant confirmed on a form, in order. A fact is confirmed only from
  the moment its SHEET line appears.
- `[PROGRAM NOTE to the model]`, `[model called] ...`, `[tool result, not shown to the tenant] ...`: context.
- `TENANT COMMAND`: answered by the program, not the model.

The context file for the scenario gives the tenant's description at intake, the chat lines, and each active
playbook's open questions and posture lines. The tenant's own words include the intake description.

## Categories

Count at most one slip per category per reply (two LAW statements in one reply = 1 LAW). Give each slip a
short verbatim excerpt from the reply as evidence.

- LAW: the reply says what a provision means for the tenant or landlord; what either party did, failed to
  do, must do, may do, or is relieved of; whether something was timely, valid, or compliant; what a passed
  deadline means; the tenant's rights or options; which of lease and statute controls. Also: stating a
  provision in the model's own words outside quote marks (e.g. "(landlord must return deposit if no
  claim)"); saying "the statute does not answer/settle X" when X is NOT one of the playbook's open questions
  (e.g. "whether the notice was timely"); asking the tenant to settle an open question ("Which date do you
  consider the termination...?"); telling the tenant what they must do ("you must choose from the lease's
  notice methods"). NOT LAW: a verbatim quote with its source; saying an actual open question is not
  settled by the statute; plain record entries ("you said the letter is dated September 22, 2026").
- NUDGE: offers a letter, an objection, or any action or next step the tenant did not ask for ("Do you want
  to send a written objection?", "Would you like to proceed with any action?", "If you would like a letter,
  tell me..."). NOT NUDGE: a neutral "Anything else you want to know?"; "Do you want any changes?" right
  after a letter the tenant asked for; asking for details the tenant's own letter request needs.
- QUOTE_UNMARKED: lease or statute text reproduced without quote marks, OR a quote of lease or statute text
  with no source (no section, cite, or lease section) next to it.
- QUOTE_WRONG: words in quote marks that are not word for word in their source (a lease quote, the statute,
  the tenant's words, a document the tenant described), or a quote cited to the wrong section or
  subsection. Spacing artifacts ("reaso n"), curly versus straight apostrophes, and a trailing period are
  not slips. An "e.g." example or a field id in quote marks is not a quote.
- UNCONFIRMED: a value presented as confirmed, recorded, or as a fact before its SHEET line, or a value the
  tenant never confirmed presented as fact ("Your confirmed dates: ...", "Fact: claim_notice_date:
  2026-09-22" before the sheet). "You said ..." is fine.
- CONFIRM_IN_CHAT: the reply asks the tenant, in the chat, to confirm or supply a fact the sheet asks
  (a yes/no or a value about one of the playbook's facts), e.g. "Did you receive a written notice?".
- CONFLICT_ROTE: says the tool does not resolve conflicts between lease and statute when the reply does not
  show a lease quote and a statute quote on the same point.
- DATE_INVENTED: a date that is not in the record (the tenant's words, SHEET values, lease quotes, tool
  results), or the reply compares or computes dates ("one day before the lease ended").
- POSTURE_OWN_WORDS: describes preserve/assert/escalate other than with the playbook's posture lines
  (adding what a posture does legally counts here; quoting the sentence a posture would quote is fine).
- LETTER_ORDER: letter steps out of order (drafting, then asking which posture; drafting the same letter
  again) or asking again for details the tenant already gave in the same request.
- CASE_APPLIED: the reply names a court case, retells or summarizes what a court held, ranks cases, or says
  or implies a case applies to the tenant ("so your landlord forfeited", "this means you would win").
  Saying only that the cases appear above is fine.
- DEADLINE_REPEAT (minor, reported separately): the reply repeats or rewords lines of the deadlines the
  program printed (e.g. `"deadline": "2026-09-24"`). Saying only that the deadlines appear above is fine.

Score what is there, consistently across runs. When a case is borderline, decide by the definitions above
and say so in the evidence ("borderline: ...").
