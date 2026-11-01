# lease_ending: scores

Claude Sonnet 5.5 answers, 3 runs a story, graded blind by Claude Opus 5.5.
Written by grade.py.

| | v1 | new | final | fixed | fixed2 |
|---|---|---|---|---|---|
| Right (settled) | 4 | 21 | 20 | 5 | 3 |
| Partly | 17 | 1 | 2 | 0 | 0 |
| Wrong | 6 | 5 | 5 | 1 | 0 |
| Right, as the graders read it | 1 | 17 | 17 | 6 | 3 |
| Made-up dates | 0 | 1 | 0 | 1 | 0 |
| Skill loaded | 27 | 27 | 27 | 6 | 3 |
| Errors | 0 | 0 | 0 | 0 | 0 |
| Empty answers | 0 | 0 | 0 | 0 | 0 |
| Cost, $ | 2.15 | 2.23 | 2.28 | 0.52 | 0.24 |
| Quotes right | 160 of 161 | 176 of 178 | 180 of 180 | 43 of 43 | 23 of 23 |

## Each story (R right, P partly, W wrong; runs 1 to 3)

| Story | v1 | new | final | fixed | fixed2 |
|---|---|---|---|---|---|
| end-1. A plain lease: is notice owed before leaving on the end date? | R R R | R R R | R R R |  |  |
| end-2. Missed the 60 days; the landlord never sent its own notice | P P P | R R R | R R W |  |  |
| end-3. The landlord's reminder came, and the words 'within 15 days' matter | P W P | W W R | R W W | R R R |  |
| end-4. A lease asking for 90 days | W W W | R R W | R R R |  |  |
| end-5. Month to month: the tenant ends it | P P W | W R W | R R R | W R R | R R R |
| end-6. Month to month: a text saying be out in days | P P P | R R R | P R W |  |  |
| end-7. Staying on without permission until a new place is ready | P P P | R R R | P R R |  |  |
| end-8. The landlord took rent after the end, then says leave in 5 days | P W R | R R R | R W R |  |  |
| end-9. The landlord's notice of no renewal comes late | P P P | R R P | R R R |  |  |
