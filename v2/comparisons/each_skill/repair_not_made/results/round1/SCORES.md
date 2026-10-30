# repair_not_made: scores

Claude Sonnet 5.5 answers, 3 runs a story, graded blind by Claude Opus 5.5.
Written by grade.py.

| | v1 | new | fixed |
|---|---|---|---|
| Right (settled) | 5 | 15 | 4 |
| Partly | 5 | 2 | 0 |
| Wrong | 11 | 4 | 2 |
| Right, as the graders read it | 1 | 14 | 5 |
| Made-up dates | 0 | 0 | 0 |
| Skill loaded | 21 | 20 | 6 |
| Errors | 0 | 0 | 0 |
| Empty answers | 0 | 0 | 0 |
| Cost, $ | 2.18 | 1.92 | 0.8 |
| Quotes right | 155 of 160 | 156 of 158 | 50 of 51 |

## Each story (R right, P partly, W wrong; runs 1 to 3)

| Story | v1 | new | fixed |
|---|---|---|---|
| repair-1. The air conditioning is out, and the lease lists it | R W R | R R R |  |
| repair-2. No hot water; a notice to end the lease, delivered after it was mailed | P P W | R R R |  |
| repair-3. A leaking roof; the tenant wants to stop paying rent but has sent nothing | W R W | W W W | W R W |
| repair-4. A closed pool and a broken dishwasher the lease promises | W W R | R R R |  |
| repair-5. A guest broke the window | P R W | R R R |  |
| repair-6. Rent goes up right after a code complaint | W W P | R R R |  |
| repair-7. The lease ended over a repair; now the deposit | P W W | P P W | R R R |
