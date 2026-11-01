# rent_increased: scores

Claude Sonnet 5.5 answers, 3 runs a story, graded blind by Claude Opus 5.5.
Written by grade.py.

| | v1 | new | final | fixed | fixed2 | fixed3 |
|---|---|---|---|---|---|---|
| Right (settled) | 3 | 12 | 22 | 9 | 0 | 1 |
| Partly | 6 | 5 | 0 | 1 | 3 | 1 |
| Wrong | 15 | 7 | 2 | 2 | 0 | 1 |
| Right, as the graders read it | 1 | 12 | 19 | 7 | 0 | 0 |
| Made-up dates | 0 | 0 | 2 | 1 | 2 | 0 |
| Skill loaded | 24 | 24 | 24 | 12 | 3 | 3 |
| Errors | 0 | 0 | 0 | 0 | 0 | 0 |
| Empty answers | 0 | 0 | 0 | 0 | 0 | 0 |
| Cost, $ | 1.97 | 2.1 | 2.43 | 1.03 | 0.26 | 0.38 |
| Quotes right | 163 of 164 | 163 of 164 | 194 of 201 | 83 of 83 | 19 of 20 | 24 of 24 |

## Each story (R right, P partly, W wrong; runs 1 to 3)

| Story | v1 | new | final | fixed | fixed2 | fixed3 |
|---|---|---|---|---|---|---|
| rent-1. A raise in the middle of a set term, no clause | W W W | R R R | R R R |  |  |  |
| rent-2. The lease allows a raise on 60 days' notice, and the letter gives less | W P P | W W W | R R R | W R R |  |  |
| rent-3. A much higher rent offered for renewal | W R W | W R R | R R R | R R R |  |  |
| rent-4. Month to month, a raise on short notice | W W P | P P P | R R W | P W R | P P P | W R P |
| rent-5. A code complaint, then a raise for this tenant only | W R W | P R R | R R R |  |  |  |
| rent-6. Everyone got the same raise, in good time | W W P | R R R | R W R |  |  |  |
| rent-7. The tenant already paid the raise for two months | P W W | P W W | R R R | R R R |  |  |
| rent-8. Kept paying the lease's rent, and now sued for the difference | R P W | R R W | R R R |  |  |  |
