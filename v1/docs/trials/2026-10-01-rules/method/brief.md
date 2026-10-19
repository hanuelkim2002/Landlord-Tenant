# Brief: write one version of the RULES for a landlord-tenant organizer

You are writing one alternative version of the RULES text: the fixed first part of the system prompt of a
chat agent. Several versions will be tested side by side on the same live scenarios and scored blind on
the same rubric. Your version must keep the same big-picture goals as the current rules, but you are free
to change structure, wording, ordering, length, and strategy, within the strategy you are assigned.

## What the tool is

A Florida residential landlord-tenant dispute organizer (Fla. Stat. ch. 83, part II) for a tenant in
college housing. It organizes: here is what your lease says, here is what the statute says, here are your
dates. It never advises, never sends anything, and the model never computes a date. The author is a law
student, not admitted. The chat model is nemotron-3-super-120b-a12b (about 12B parameters active per
token), at temperature 0, behind an OpenAI-compatible gateway, driven by a LangChain agent with tools.

## What the model sees (the system prompt, rebuilt before every model call)

1. RULES (what you are writing).
2. `LEASE PROFILE:` the lease as JSON: fifteen named clauses, each with `present`, `quote` (verbatim lease
   text, already checked against the PDF), `page`, `section` (e.g. "4.3. Return of Deposit and Claims").
   The PDF text has spacing artifacts such as "reaso n" and "move -out"; the quotes keep them.
3. `PLAYBOOKS:` for each active issue, YAML with `issue`, `guidance` (the sheet's questions, lease checks,
   evidence, `postures` with one line each for `preserve`, `assert`, `escalate`, plus `core` and
   `notice_sufficiency`, and `failure_modes`) and `open_questions` (each with `id`, `sections`, `text`).
   A real sample is in prompt_sample.txt next to this brief.
4. `STATUTE SECTIONS:` the full text of every section the active playbooks list (often 10,000 to 16,000
   characters; about half the prompt).
5. `ELEMENT STATUS (by issue):` JSON, per issue a list of facts: `id`, `status` (known, changed, proposed,
   missing, or n/a), `value`, `from` ("user" or a lease field). Only "known" facts are confirmed.

The whole prompt is about 8,600 tokens. RULES is the only part you change, and it stays first.

## The tools (descriptions as the model sees them are in tools.txt)

get_statute_section, search_statute, propose_facts, get_deadlines, draft_letter, add_artifact,
add_communication. Use these exact names.

## What the program does around the model (do not ask the model to do these)

- After a reply in which the model called propose_facts, the program shows the tenant a sheet; the tenant
  confirms or corrects each fact there. The next tenant message then starts with "[Program note: the
  tenant confirmed on the sheet: ...]". The model can only propose; it cannot confirm or record a fact.
- When the model calls get_deadlines, the PROGRAM prints the full result to the tenant (date, whose
  deadline, rule and start date, cite, status, counting line, issues, and which issues are still waiting).
  The model must not repeat or reword it; at most it says the deadlines appear above.
- draft_letter's result (the letter) is printed by the program. An identical redraft in the same session
  returns "[The same letter was already drafted in this session (...) and appears above. Nothing new was
  drafted.]".
- If a reply is empty, the program asks the model once more with "[Program note: your last turn ended
  without a reply to the tenant. Reply to the tenant's last message now.]".
- After each reply the program checks it and prints "[Check: ...]" lines to the tenant for: a ch. 83 cite
  outside quote marks to a section that was neither in STATUTE SECTIONS nor fetched with get_statute_section,
  or to a subsection that does not exist; and every passage of 20 or more characters in quote marks: with a
  cite next to it (after it on the same line, or in a heading just before it) the words must be in that
  section and subsection; with no cite they must be in the prompt, the tenant's words, or a tool result.
  Text without quote marks is not checked at all, so quotes the model leaves unmarked escape the check.

## The current rules (the control arm)

See rules_control.txt (620 words, seven numbered rules, reply format first).

## What goes wrong (from about 40 scored replies across 30 live runs)

The rubric categories, with examples seen:

- LAW, the most serious. The reply says what a provision means for the tenant or the landlord, or states
  the law in its own words, or takes a position on (or asks the tenant to settle) a legal question.
  Seen: "you may terminate the lease under Fla. Stat. 83.56(1)"; "Landlord's deadline to remit balance if
  you object" (the statute says "Unless the tenant objects"); "(landlord must return deposit if no claim)";
  "The statute does not answer whether the notice was timely given the termination date" (not one of the
  playbook's open questions; frames the landlord's compliance); "Which date do you consider the termination
  of the rental agreement: the date you moved out or the date the tenancy terminated?" (asks the tenant to
  settle the open question); "you must choose from the lease's notice methods".
- NUDGE. Offers a letter or suggests an action the tenant did not ask for. Seen in most runs, despite an
  explicit rule against it: "Do you want to send a written objection to the landlord's claim?", "Would you
  like to proceed with any action based on this deadline?", "If you would like me to draft a letter...".
- QUOTE_UNMARKED. Lease or statute text written without quote marks, or a quote with no source next to it.
  Seen often after the current rules; it also hides quotes from the program's quote check.
- QUOTE_WRONG. Words in quote marks that are not in the source, or cited to the wrong subsection. Seen: an
  invented quote of the landlord's letter; "the 'repair within 5 days' you requested" when the tenant wrote
  "Give them 5 days to reply".
- UNCONFIRMED. A value presented as confirmed or as a fact before the sheet confirmed it: "Your confirmed
  dates: ...", "Fact: claim_notice_date: 2026-09-22" (the letter's printed date, not the date received).
- CONFIRM_IN_CHAT. Asking the tenant in the chat to confirm or give a fact the sheet will ask.
- CONFLICT_ROTE. "This tool does not resolve conflicts between the lease and the statute" when nothing in
  the reply sets a lease quote against a statute quote on the same point.
- DATE_INVENTED. A date not in the record, or comparing dates: "Lease term ended: 2026-09-30" (the lease
  says September 30, 2027 and the tenant said July 31, 2026); "you moved out one day before the lease ended?".
- POSTURE_OWN_WORDS. Explaining preserve/assert/escalate other than by the playbook's own lines.
- LETTER_ORDER. Letter steps out of order: drafting, then asking for the posture, then drafting again; or
  asking again for details the tenant already gave.
- DEADLINE_REPEAT (minor). Repeating lines of the program-printed deadlines, e.g. `"deadline": "2026-09-24"`.

Also observed: the model reads instructions very literally. "A reply is built only from these parts, under
short labels" produced replies labelled "Quote:", "Fact:", "Statement:", "Question:", raw field names
(`forwarding_address_given: true`), and quotes with no quote marks. Small models of this size tend to
follow short, concrete, positive instructions better than long lists of prohibitions, and are pulled
toward being "helpful" (offering next steps).

Rates so far, in slips per reply: old fifteen rules 0.91; current seven rules 1.00; current rules plus the
code-side fixes 0.50 and 1.00 on two runs. LAW and NUDGE are the slips that matter most.

## The goals every version must keep (big picture)

1. Organize, never advise: show lease text, statute text, and the tenant's record side by side; never say
   what a provision means for the tenant, what anyone must or may do, whether something was timely or
   valid, what the tenant's rights or options are, or which of lease and statute controls.
2. Quote only text that was given (LEASE PROFILE quotes, STATUTE SECTIONS, get_statute_section results, the
   tenant's own words), word for word, in quote marks, with the source. Never from memory. Fetch a section
   before mentioning one that is not in STATUTE SECTIONS. If nothing answers a question, say so plainly.
3. No date the model works out: every date comes from ELEMENT STATUS, a lease quote, the tenant's words, or
   a tool result. Deadlines come only from get_deadlines, whose result the program prints.
4. Facts are confirmed only by the tenant on the sheet: the model proposes with propose_facts (the
   tenant's exact words, which may be shortened with "..." between exact pieces) and never calls anything
   confirmed unless ELEMENT STATUS shows it as known.
5. The playbooks' open_questions are unsettled: say the statute does not settle them; do not resolve them
   and do not ask the tenant to.
6. Letters only when the tenant asks, only through draft_letter, never written or rewritten by the model.
   Before drafting, the model needs: which issue (if more than one), what the tenant wants the landlord to
   do, days to reply, how they will send it (quote the lease's notices clause, do not pick a method), and
   the posture (show the playbook's three posture lines word for word); for assert or escalate, the
   sentence to be quoted. Skip any question the tenant already answered. After drafting: one sentence.
7. Record messages with add_communication: a message the tenant pastes or describes (text exactly as given;
   ask the date if missing), and a letter the tenant says they sent (sender "tenant", recipient "landlord",
   delivery method as channel, the draft's file name plus any tracking number as text).
8. Never send anything. No offers of letters or next steps the tenant did not ask for.

## Constraints on your text

- Plain text, as it would sit in a Python string. At most 900 words (the control is 620).
- No em dashes anywhere (use colons, semicolons, commas, or parentheses).
- Refer to prompt sections by their exact names (LEASE PROFILE, PLAYBOOKS, STATUTE SECTIONS, ELEMENT
  STATUS) and to tools by their exact names.
- Nothing the program does not support (no new tools, no fields that do not exist, no instruction to report
  deadlines or reprint letters). Do not tell the model that it is being tested.
- Do not tailor it to particular test stories; the same rules serve every issue (deposits, repairs,
  nonpayment notices, entry, rent increases, leaving early, lease ending).
- If you include example replies, make them about issues and facts that are clearly illustrative, keep
  every quote in them real (copy statute text from the project's `statutes/83.*.txt`, read-only, or lease
  wording from prompt_sample.txt), and use no em dashes.
