# TODO

The working list. Move an item to CHANGELOG.md when it is done, with the date. Reorder freely. Keep the
"Open questions" section for things that need a decision before code is written.

## Harness and code

Code-side checks and bookkeeping that hold whatever the model does. Ahead of model behavior.

1. Clocks `compute_deadlines` cannot compute yet: (a) court business days are done for 83.56(3) in the
   Eighth Judicial Circuit, 2026 and 2027; other circuits need their own memoranda (add a county's circuit
   when a tenant there uses the tool), and each new year's memorandum must be added when the circuit
   publishes it (the 2028 one is needed for any count reaching January 2028); 83.60(2) waits on the open
   question below; (b) periods the lease sets (83.575(1)-(2), 83.595(4)); needs a clock whose length is a
   confirmed fact; (c) hours (83.53(2)); (d) months (83.56(2), 12 months). Decide which to support.
14. `citations.check_quoted` noise seen 2026-09-30 (gpt-oss-120b runs): a clock id in quote marks
   ("claim_notice_deadline" (83.49(3)(a)), m-023) was checked as a statute quote, and an example the model
   offered ("e.g., "repair the air-conditioning unit"", m-022) as a quote of the tenant. Both flagged,
   neither a misquote. Decide whether ids (no spaces, underscores) and "e.g." examples are skipped.

## Playbooks

2. Hand check of the seven playbooks written 2026-09-27 (repair_not_made, notice_received_nonpayment,
   notice_received_violation, landlord_entered_unannounced, rent_increased, wants_to_leave_early,
   lease_ending): read each quote against `statutes/`, then set `provenance.verified_by` and `verified_on`.
   Also replace the deposit playbooks' 83.42 exclusion ("Not yet read") with the 83.42(1) quote the new
   playbooks carry.
3. Counting convention is a stated assumption in each playbook. Check the time-computation rule in the
    corpus before relying on it. Do not settle this from memory.

## Model behavior (later)

Slips seen in live runs. Logged, not fixed yet: rules and prompts get tuned after the structure is right,
and some may go away with a more capable model. Rule numbers in items 4 to 13 are the old fifteen rules
(until 2026-09-30); DOCUMENTATION.md, The system prompt, maps them to the current seven. Items 15 on use
the seven.

4. The model stated the remit clock's condition backwards: "Landlord's deadline to remit balance if you
    object." 83.49(3)(b) begins "Unless the tenant objects." A rule 13 breach close to the playbook's own
    failure mode (2026-09-27, resume run on `t-test/test-002`). The clock's quote no longer reaches the
    model since only `guidance` is pasted.
5. In the same run the model summarized 83.49 in its own words instead of quoting it (rule 1), and
    added words the sentence does not have ("objects in writing within 15 days"). Since 2026-09-29
    `citations.check_quoted` flags the added words when they are inside quote marks; a paraphrase is not
    checked.
6. Since only `guidance` is pasted, the model mis-cited the forfeiture sentence as 83.49(3)(b) when
    explaining the escalate posture (it is 83.49(3)(a)). The escalate line in `guidance.postures` names no
    cite. Since 2026-09-29 `citations.check_quoted` flags this when the sentence is quoted next to the wrong
    cite, naming the right subsection; described in the model's own words it is not caught.
7. The model compared dates itself when confirming `early_or_periodic` ("Does that mean you moved out one
    day before the lease ended?"). A rule 2 slip, seen once.
8. After calling `propose_facts` the model still asks the tenant to confirm in the chat ("Is that
    correct?"), though rule 3 says the sheet does it. Harmless: the sheet follows and is what counts.
9. After calling `propose_facts`, the model told the tenant values were "as you just confirmed" before
    the sheet had run (rule 9). Seen 2026-09-27; the sheet still decided. Seen again 2026-09-30 (claim
    scenario, `t-test/m-015`): the reply listed the claim letter's dates (2026-09-22, 2026-09-25) under
    "Your confirmed dates" before the sheet asked about them.
10. Reporting the 83.56(3) court-day date, the model did not show the date the notice itself states next
    to it, as the playbook's failure modes ask, and closed with "Would you like to proceed with any action
    based on this deadline?" (live run 2026-09-27, `t-test/m-002`). The timeline shows both dates.
11. Explaining the escalate posture for repair_not_made, the model said the tenant "may terminate the lease
    under Fla. Stat. 83.56(1)" (rule 13); the playbook only says the posture adds the quoted sentence
    (2026-09-28, repair scenario).
12. In the claim scenario the model suggested the letter's printed date (2026-09-22) as the date it was
    received; the sheet asked and the tenant's typed 2026-09-25 replaced it (logged as corrected).
13. In the same reply as item 9's second sighting, the model wrote "Lease term ended: 2026-09-30" next to
    the lease quote "ending at 11:59 p.m. on September 30, 2027": a date that is neither the lease's nor the
    tenant's (7/31/2026), in the list it called confirmed (2026-09-30, `t-test/m-015`). Not caught: the
    quote beside it is real, and a date outside quote marks is not checked.
15. New rules on nemotron (2026-09-30, `t-test/m-017` to `m-019`): rule 1's "built only from these parts,
    under short labels" made replies terse. A deadline without its counting line, status, or actor (m-017);
    statute and lease quotes with no quote marks or source, and facts as raw field names (m-019), so the
    quote check could not see the quotes and the cite check flagged 83.505 from inside one. Letter offers
    went on in 2 of 3 runs although rule 1 now forbids them.
16. In m-019 the model wrote "The statute does not settle the question of whether the notice was given within
    the required time." Not one of the playbook's open questions; it frames the landlord's compliance as an
    issue (rule 1).
17. An empty reply after `get_deadlines` (repair scenario, m-018): the tenant saw nothing. Three replays of the
    turn gave normal replies. nemotron returns a separate `reasoning_content` field the chat loop never reads.
18. gpt-oss-120b on the scenarios (2026-09-30, m-021 to m-024; the default stays nemotron): shortened the
    tenant's words with "..." in `propose_facts`, which was refused, so the claim scenario never got
    deposit_claim_received or its two deadlines, and then asked in the chat whether a notice was received
    (rule 4); invented a quote of the landlord's letter and cited a 83.60 quote to (1)(b) when it runs from
    (1)(a) (both flagged by `check_quoted`); described the clocks in its own words ("landlord must return
    deposit if no claim", rule 2); printed ELEMENT STATUS values as a column of quoted "true"/"false"; asked
    again for letter details the tenant had already given. It copied the posture lines word for word,
    showed the notice's stated date next to the 83.56(3) date (item 10), and never left a reply empty.
19. After the harness fixes (2026-09-30, nemotron, m-025 to m-028): 3 slips in 6 replies, all scenarios as
    expected, no cautions, no empty replies. Left: a statute quote with no source (m-026) and a lease quote
    with neither quote marks nor source, next to the tenant's own words also unquoted (m-027), so the quote
    check could not see them (rule 2); a next step pointing to a legal action, "Do you want to send a written
    objection to the landlord's claim?" (m-027, rule 1); and in all three chat runs a line of the printed
    deadlines repeated (`"deadline": "2026-09-24"`), harmless but against rule 3.
20. Letter steps out of order (m-026): the model drafted at once from the tenant's full request, then showed
    the postures and asked which one, then drafted the same letter again. The second, identical draft is
    stopped in code from 2026-09-30; the order of the steps is still the model's (rule 6).
21. Item 12 again (m-027): the letter's printed date (2026-09-22) suggested as the date it was received; the
    tenant typed 2026-09-25 on the sheet, logged as corrected.
22. Second run of the harness setup (2026-09-30, nemotron, m-029 to m-032): 6 slips in 6 replies, against 3
    in 6 the first time, so one run per scenario cannot measure a prompt change. Repeats: item 16 twice
    ("The statute does not answer whether the notice was timely given the termination date"); item 19's
    quotes without a source (m-029, m-031), the objection nudge (m-031), and the repeated deadline line in
    all three runs; item 21, this time shown as "Fact: claim_notice_date: 2026-09-22" before the sheet (rule
    4). New: the model asked the tenant to choose which date is "the termination of the rental agreement",
    the playbook's open question `termination_date_meaning` (rule 5 says only that the statute does not
    settle it). It also labelled its lines "Quote:", "Fact:", "Statement:", "Question:", reading rule 1's
    parts literally. The duplicate-draft stop worked live (m-030: one draft event).

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
