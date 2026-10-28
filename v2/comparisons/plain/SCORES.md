# Plain replies test: scores

Sonnet 5.5 from Anthropic, 18 deposit stories, 3 runs each, with the old rules and the new. Right, partly, and wrong: Claude Opus 5.5, blind. Plain counts: Claude Opus 5.5, with my review. Written by grade.py.

## Targets

- Met: Format followed in at least 52 of 54 new answers
- Missed: Median short part 100 words or less
- Met: Unclear words, after my review: median 0, and fewer in all than the old rules
- Missed: Unclear words, on the graders' own counts: median 0, and fewer in all than the old rules
- Met: Unexplained legal words: median 0, and fewer in all than the old rules
- Met: Right answers not fewer than the old rules

## Totals

|  | old | new |
| --- | --- | --- |
| Right, settled stories (of 48) | 40 | 41 |
| Partly | 2 | 2 |
| Wrong | 6 | 5 |
| Format followed (of 54) | 0 | 54 |
| Median words in the short part | 461.5 | 126.5 |
| Median words seen first, box titles included | 461.5 | 169.0 |
| Median words in all | 461.5 | 672.5 |
| Section number or quote seen first | 53 | 7 |
| Question hidden in a box | 0 | 0 |
| Unclear words, median (after my review) | 1.0 | 0.0 |
| Unclear words, in all (after my review) | 79 | 21 |
| Unclear words, median (the graders' own counts) | 2.0 | 0.5 |
| Unclear words, in all (the graders' own counts) | 99 | 39 |
| Unclear words per 100 words seen first (after my review) | 0.32 | 0.23 |
| Unclear words per 100 words seen first (the graders' own counts) | 0.41 | 0.42 |
| Unexplained legal words, median | 2.0 | 0.0 |
| Unexplained legal words, in all | 135 | 7 |
| Unexplained legal words per 100 words seen first | 0.55 | 0.08 |
| Seen first answers the question alone | 53 | 54 |
| Median seconds per answer | 19.85 | 24.05 |
| Median cost per answer, $ | 0.0875 | 0.0935 |
| Cost of the run, $ | 4.95 | 5.3 |

## Each settled story (R right, P partly, W wrong; runs 1 to 3)

| Story | old | new |
| --- | --- | --- |
| 1. No word at all, more than two months on | R R R | R R R |
| 3. Left early, told the manager by text | R R R | R R R |
| 4. A partial check, no explanation | R R R | R R R |
| 6. A certified notice of claim, still time to object | R R R | R R R |
| 7. A notice came, no objection, no balance sent | R R R | R R R |
| 8. The claim came by e-mail, with a signed e-mail addendum | W W W | W W W |
| 9. Left early with the right notice: which date counts | R R W | R R R |
| 10. Month to month, told the manager out loud | R R R | R R R |
| 11. College housing: the lease does not settle it | R R R | R R R |
| 12. A fee paid instead of a deposit | R W W | P R R |
| 13. Public housing: the housing authority sent nothing | R R R | R R R |
| 14. A Section 8 voucher with a private landlord | R R R | W R R |
| 15. The claim went to the old address and was forwarded | R R R | R R R |
| 16. A certified claim with no amount | R R R | R R R |
| 17. A certified claim with no reason | R R R | R R R |
| 18. The tenant objected in time; nothing since | P P R | W P R |

## My changes to the plain counts

- old, deposit-7/2: unclear 1, legal -. Not counted: "they" in "Yes, they have to send the $650, and it's overdue." echoes the tenant's own words in the first sentence.
- old, deposit-7/3: unclear 0, legal -. Not counted: "they" in "Yes, they had to send you the $650, and it's overdue." echoes the tenant's own words in the first sentence.
- old, deposit-8/1: unclear 1, legal -. Not counted: "it" in "No, don't ignore it." echoes the tenant's own words in the first sentence; "it" in "If it goes to court, that is a factual dispute." can only mean the dispute or the answer as a whole.
- old, deposit-12/2: unclear 1, legal -. Not counted: "this" in "Short answer: No, as the statute reads, this probably isn't " echoes the tenant's own words in the first sentence; "that" in "What that means for you." can only mean the dispute or the answer as a whole.
- old, deposit-10/1: unclear 1, legal -. Not counted: "this" in "What this means for you" can only mean the dispute or the answer as a whole.
- old, deposit-10/2: unclear 2, legal -. Not counted: "it" in "Why the deadlines don't settle it for you" can only mean the dispute or the answer as a whole; "this" in "What this means in practice" can only mean the dispute or the answer as a whole.
- old, deposit-10/3: unclear 0, legal -. Not counted: "it" in "Why the silence doesn't settle it" can only mean the dispute or the answer as a whole; "it" in "If it goes to court" can only mean the dispute or the answer as a whole.
- old, deposit-14/2: unclear 1, legal -. Not counted: "it" in "Why it is unsettled." can only mean the dispute or the answer as a whole.
- old, deposit-15/2: unclear 1, legal -. Not counted: "it" in "Why it matters." can only mean the dispute or the answer as a whole.
- old, deposit-15/3: unclear 2, legal -. Not counted: "this" in "What this means for you now." can only mean the dispute or the answer as a whole.
- old, deposit-16/3: unclear 5, legal -. Not counted: "this" in "The lease (§§7–8) doesn't change any of this." can only mean the dispute or the answer as a whole.
- old, deposit-18/3: unclear 3, legal -. Not counted: "this" in "The lease has no clause that changes any of this." can only mean the dispute or the answer as a whole.
- old, deposit-17/1: unclear 3, legal -. Not counted: "it" in "If it goes to court." can only mean the dispute or the answer as a whole.
- old, deposit-11/1: unclear 0, legal -. Not counted: "this" in "If this is school-run housing, the deposit rules above might" can only mean the dispute or the answer as a whole.
- old, deposit-11/3: unclear 1, legal -. Not counted: "this" in "If this is an ordinary apartment rental, you get back the wh" can only mean the dispute or the answer as a whole; "this" in "The enrollment clause leaves me unable to tell from the leas" can only mean the dispute or the answer as a whole.
- new, deposit-8/3: unclear 0, legal -. Not counted: "it" in "No, don't ignore it." echoes the tenant's own words in the first sentence; "this" in "One thing could change this." can only mean the dispute or the answer as a whole.
- new, deposit-7/1: unclear 0, legal -. Not counted: "this" in "Do any exceptions change this?" can only mean the dispute or the answer as a whole.
- new, deposit-7/2: unclear 0, legal -. Not counted: "this" in "Does your lease change any of this?" can only mean the dispute or the answer as a whole.
- new, deposit-8/1: unclear 0, legal -. Not counted: "this" in "One thing could change this." can only mean the dispute or the answer as a whole.
- new, deposit-8/2: unclear 0, legal -. Not counted: "this" in "What if this goes to court?" can only mean the dispute or the answer as a whole.
- new, deposit-9/1: unclear 0, legal -. Not counted: "this" in "What if this goes to court?" can only mean the dispute or the answer as a whole.
- new, deposit-9/3: unclear 0, legal -. Not counted: "this" in "What if this goes to court?" can only mean the dispute or the answer as a whole.
- new, deposit-10/1: unclear 0, legal -. Not counted: "it" in "Why doesn't that settle it in your favor?" can only mean the dispute or the answer as a whole; "this" in "What does this mean for getting the money?" can only mean the dispute or the answer as a whole.
- new, deposit-10/3: unclear 0, legal -. Not counted: "this" in "What if this goes to court?" can only mean the dispute or the answer as a whole.
- new, deposit-11/1: unclear 0, legal -. Not counted: "this" in "Can you recover court costs if this goes to court?" can only mean the dispute or the answer as a whole.
- new, deposit-12/3: unclear 0, legal -. Not counted: "this" in "One thing could change this: whether your signed fee agreeme" can only mean the dispute or the answer as a whole.
- new, deposit-13/3: unclear 2, legal -. Not counted: "this" in "[ > What does this mean for your money? ]" can only mean the dispute or the answer as a whole.
- new, deposit-16/1: unclear 0, legal -. Not counted: "this" in "[ > What if this goes to court? ]" can only mean the dispute or the answer as a whole.
- new, deposit-16/2: unclear 0, legal -. Not counted: "this" in "[ > What if this ends up in court? ]" can only mean the dispute or the answer as a whole.
- new, deposit-16/3: unclear 1, legal -. Not counted: "this" in "[ > What if this goes to court? ]" can only mean the dispute or the answer as a whole.
- new, deposit-17/1: unclear 0, legal -. Not counted: "this" in "[ > What if this goes to court? ]" can only mean the dispute or the answer as a whole.
