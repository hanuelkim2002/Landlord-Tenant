# TODO

Work Claude Code can do, in priority order. Do the top of **Now** unless the author says otherwise. When an item is
done, move it to CHANGELOG.md with the date.

What goes where (the author's decision of 2026-10-09):
- **TODO.md**: a change to code, skills, the harness, or docs that Claude Code can make, with a clear enough goal.
  At most about four lines: what to change, why it matters to a tenant, and what done looks like. No eval history in
  the item; link the record (`docs/evals/...`, the CHANGELOG) instead.
- **AUTHOR.md**: what only the author can do: legal sign-offs, decisions, research, open questions.
- **SLIPS.md**: model behavior seen in live runs, counted per eval. A slip moves to TODO.md only when there is a
  code-side fix to make, or it hurts a tenant and keeps recurring.
- A finding seen again updates its entry (a count, a date); it is never a new item. A finding fixed in the same change
  goes only in the CHANGELOG. An eval's full findings stay in its record.

Item numbers are never reused, so older references (the CHANGELOG, smoke check names) still point to the right item.
When an item is taken up, solve the underlying issue it is an instance of, not only the example that showed it (the
author's rule of 2026-10-06, in CLAUDE.md).

## Now

Playbooks became skills (2026-10-12, TODO 109 to 116 in the CHANGELOG; the eval in `docs/evals/2026-10-12-skills/`).
What the eval found that code can fix:
118. The automatic reply after a confirmation repeats the whole answer: 53 of 266 replies, 46 of 115 REPEATED and 41 of
    127 OFFER slips (`docs/evals/2026-10-12-skills/`). The note could ask only what the confirmation changes, or the
    reply could be skipped when nothing confirmed changes the answer. Done: repeats on automatic replies fall.
119. Asked when, with nothing dated yet, the program prints nothing (TODO 114) and the model writes dates (dates made by code:
    3 before, 19 after, 2026-10-12). Print what the deadlines wait for whenever "when" is asked without get_deadlines.
    Done: dates made back near the old level.
120. The eval's scripted chat lines were written for the old flow and re-ask in turn 2 what the first reply now answers,
    inflating REPEATED. Review each story's chat lines for a conversation. Done: no story asks what turn 1 answered.

The student simulation's remaining cause (`docs/evals/2026-10-06-students/`): what the tenant reads is built for
checking, not for a reader with no legal training (98, 100). The letters (95, 96) are in the CHANGELOG, 2026-10-11;
item 99 and the shape of an answer (AUTHOR 97) went with the skills (CHANGELOG, 2026-10-12).
98. Case listings come first and whole: 51% to 72% of first replies, mostly unrelated injury cases, and every student
    skipped them. The reply first and the cases after it (folded on the web page), or cases only when asked; fewer
    topics per issue joins item 29. Done: the answer is the first thing a tenant reads.
100. Words students did not know: the postures (preserve, assert, escalate) and "matter" on the web page. Plain names
    for the postures with when each fits. (Legal terms in replies, "possession", "material", "waived", are rule H's
    format line since 2026-10-12: say what a term means; the eval of item 116 counts how it holds.)
105. A false cite caution: "83.49(3)(a) (1981)", a statute version year after a cite, read as a subsection by
    `citations.CITE` (6 cautions in 2 `deposit_cases` runs, 2026-10-08). Done: a version year passes; a wrong
    subsection is still caught.

## Next

107. A refused `draft_letter` ("Rejected: obligation_quote is not found ...", eval of 2026-10-08, noise story) is printed
    to the tenant in the letter box, labeled as the program's letter (`agent.turn_blocks` shows every result as is).
    Done: the box shows only a drafted letter (or the same-letter line), and a refusal goes to the model alone.
94. One set of facts per issue: two repair problems (hot water and an AC) share one start date, one notice, and one
    set of options, so a letter's line is wrong for one of them (student story C). A matter per problem, or an issue
    that can repeat with its facts kept per problem: propose before building.
104. `dev/eval.py`: a run stopped by a time limit leaves no `runs.json`, so the runs that finished are lost until scored by
    hand. Item 33 (first attempts that crash, 2026-10-01) joins this. Done: a stopped eval can be scored. (The network signs
    in `GATEWAY_SIGNS` are done: CHANGELOG, 2026-10-12.)
87, 67. Eval checks that count a right answer as a slip: the dog story's "you (are|will be) safe" matches "Whether you
    are safe turns on ..." (2 of 3 runs on 2026-10-04 and on 2026-10-08), `LEASE_ABSENT` counts a reply repeating what
    the tenant confirmed, and "cases not given" counts part of a given case's name ("Inc. v. Varnado"); match against
    `replies.named_cases` instead.
101. The student simulation's other stories as scenarios on nemotron: A, B, D, and D2 (F, C, and E became
    `eval_student_*` on 2026-10-08). Each story's typed lines are in `docs/evals/2026-10-06-students/results/*/inputs.json`.
78. Profiles read before 2026-10-04 lack the repairs clause (`maintenance_and_repairs` is `None`): a way to read just
    that clause from a matter's stored `pages.json`, for the author to run on a matter of their choosing.

## Later

29, 35, 36. Which case topics a tenant sees: the model picks one of many offered topics (two runs of one question saw
    different cases), the topics per skill are many and mixed (27 for repair_not_made, procedural ones among them),
    and a tenant who never asks sees none. Sections on the topic pages or a topic list per skill first, then a line
    or a `cases` command listing the topics so the tenant picks.
43. A `conduct_and_use` lease profile field (the test lease's 5.2 and 5.4), so a neighbor_disturbance chat or letter can
    quote the lease's own rule; every lease would be read again.
75. A lease PDF whose text PyPDF2 cannot decode (Type3 fonts, a 57-page lease of 2026-10-04): try `pypdf` or
    `pdfminer.six`, and switch `lease.ingest_pdf` if one reads it.
45. The web page's limits: earlier sessions' chats not shown on reopening, one tab at a time, no `session_ended` when a
    tab closes, no upload, no sign of progress while a long lease is read (about four minutes for 57 pages), a second
    click starting a second matter, and no time limit on the extraction call.
