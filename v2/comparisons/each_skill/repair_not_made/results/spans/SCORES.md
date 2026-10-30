# repair_not_made: scores

Claude Sonnet 5.5 answers, 3 runs a story, graded blind by Claude Opus 5.5.
Written by grade.py.

| | codeB | codeBA | keys2 | ruleA | v1rule |
|---|---|---|---|---|---|
| Right (settled) | 12 | 14 | 13 | 12 | 13 |
| Partly | 2 | 0 | 1 | 2 | 0 |
| Wrong | 1 | 1 | 1 | 1 | 2 |
| Right, as the graders read it | 5 | 5 | 5 | 5 | 5 |
| Made-up dates | 1 | 0 | 0 | 0 | 1 |
| Skill loaded | 15 | 15 | 15 | 15 | 15 |
| Errors | 0 | 0 | 0 | 0 | 0 |
| Empty answers | 0 | 0 | 0 | 0 | 0 |
| Cost, $ | 1.43 | 1.51 | 1.49 | 1.45 | 1.57 |
| Quotes right | 102 of 107 | 113 of 115 | 109 of 112 | 110 of 118 | 113 of 115 |

## Each story (R right, P partly, W wrong; runs 1 to 3)

| Story | codeB | codeBA | keys2 | ruleA | v1rule |
|---|---|---|---|---|---|
| repair-1. The air conditioning is out, and the lease lists it | R R R | R R R | R R R | R R R | W R R |
| repair-2. No hot water; a notice to end the lease, delivered after it was mailed | P R R | R R R | R R R | R R R | R R R |
| repair-3. A leaking roof; the tenant wants to stop paying rent but has sent nothing | R R P | R R R | R P R | P P R | R R R |
| repair-4. A closed pool and a broken dishwasher the lease promises |  |  |  |  |  |
| repair-5. A guest broke the window |  |  |  |  |  |
| repair-6. Rent goes up right after a code complaint |  |  |  |  |  |
| repair-7. The lease ended over a repair; now the deposit | R R R | R R R | W R R | R W R | R W R |
| repair-8. A furnished apartment: the bed frame the lease promises broke |  |  |  |  |  |
| repair-9. The reserved covered parking the lease promises is closed | R W R | R W R | R R R | R R R | R R R |
