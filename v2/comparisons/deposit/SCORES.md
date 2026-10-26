# Deposit skill test: scores

Gemini, 12 stories, 3 runs each, per skill version. Judge: gpt-oss-120b on UF. Written by grade.py.

## Totals

|  | v1 | old | new |
| --- | --- | --- | --- |
| Right, settled stories (of 30) | 19 | 24 | 23 |
| Partly | 5 | 5 | 7 |
| Wrong | 6 | 1 | 0 |
| Empty answers (of 36) | 0 | 0 | 0 |
| Answers first | 29 | 33 | 29 |
| Made-up dates | 0 | 0 | 0 |
| Asks more than one question | 1 | 1 | 2 |
| Skill loaded | 36 | 36 | 36 |
| count_days used | 34 | 33 | 35 |
| Median words | 439.0 | 358.0 | 368.0 |
| Median seconds | 32.3 | 27.95 | 25.7 |
| Quotes word for word | 183 of 187 | 144 of 147 | 117 of 120 |
| Cost per answer | $0.0235 | $0.0221 | $0.0214 |

## Each story (R right, P partly, W wrong; runs 1 to 3)

| Story | v1 | old | new |
| --- | --- | --- | --- |
| 1. No word at all, more than two months on | W R R | R R R | R R R |
| 2. Fifteen days gone, thirty not yet (open call) | R R R | R R R | W W R |
| 3. Left early, told the manager by text | R R R | R R R | R R R |
| 4. A partial check, no explanation | R R R | R R R | R R R |
| 5. The claim came by text (open call) | P P R | R R R | R R R |
| 6. A certified notice of claim, still time to object | W P W | W P P | P P P |
| 7. A notice came, no objection, no balance sent | P R R | P R P | P P P |
| 8. The claim came by e-mail, with a signed e-mail addendum | P P P | R P R | R R P |
| 9. Left early with the right notice: which date counts | R R R | R R R | R R R |
| 10. Month to month, told the manager out loud | R R R | R R R | R R R |
| 11. College housing: the lease does not settle it | W W W | R R R | R R R |
| 12. A fee paid instead of a deposit | R R R | R R R | R R R |

## My changes to the judge's grades

- v1, deposit-2/3: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1); the words are in statutes/83.42.txt and nothing contradicts them. (An open-call story, so not in the settled totals.)
- v1, deposit-6/3: wrong. Says 2026-09-19 'remains the 30-day deadline' even if the tenant objects. The duty to remit sits in the sentence that begins 'Unless the tenant objects' (83.49(3)(b)): mistake 3, the same error the judge marked wrong in v1 deposit-6/1.
- v1, deposit-9/2: right. All points made, no listed mistake. The judge said the disclosure words 'WITHIN 30 DAYS AFTER YOU MOVE OUT' are not in the statute; they are, in 83.49(2)(d).
- old, deposit-6/1: wrong. Says the landlord must send the $650 by 2026-09-19 'regardless of whether you object'. The duty to remit sits in the sentence that begins 'Unless the tenant objects' (83.49(3)(b)): mistake 3, the error the judge marked wrong in v1 deposit-6/1.
- old, deposit-11/1: right. Opens with a conditional yes ('provided' part II applies), names the enrollment clause, and asks the one plain question, like old deposit-11/3 and new deposit-11/2 and 11/3, which the judge graded right. A conditional yes is not the final answer mistake 2 names. My call, for consistency.
- old, deposit-11/2: right. Opens with a conditional yes ('provided' part II applies), names the enrollment clause, and asks the one plain question, like old deposit-11/3 and new deposit-11/2 and 11/3, which the judge graded right. My call, for consistency.
- new, deposit-9/3: right. All points made, no listed mistake. The judge said the disclosure words 'WITHIN 30 DAYS AFTER YOU MOVE OUT' are not in the statute; they are, in 83.49(2)(d).
- new, deposit-11/1: right. Opens with a conditional yes ('provided' part II applies), names the enrollment clause, and asks the one plain question, like new deposit-11/2 and 11/3, which the judge graded right. My call, for consistency.
