# Memory test: scores

Claude Sonnet 5.5, 3 runs of each of 3 return visits (`stories.json`), the new memory against v2 on `main`. Code counts the tools, the lines saved, and dates found nowhere in the story, the lease, or a tool's result; Claude read every answer for the rest (`review.json`).

| Check | New memory | Baseline (main) |
| --- | --- | --- |
| Asks for nothing it was already told | 9 of 9 | 9 of 9 |
| Picks up what was left open | 9 of 9 | 9 of 9 |
| Saves the new event as a line | 9 of 9 | n/a (no timeline) |
| Closes the line left open | 3 of 9 | n/a (no timeline) |
| Works out no date itself | 8 of 9 | 9 of 9 |
| Answers first | 9 of 9 | 9 of 9 |

## Each answer

- **new, deposit_letter, run 1** (24.7 s, $0.0699): tools load_skill, get_statute_section, count_days, count_days, count_days, save_line, save_line, note_fact; lines saved 2; questions 1; dates from nowhere: none. Leads with 'object in writing'; closes the waiting line and saves the letter as a line dated by code; counts from the corrected move-out date; one question about how the letter came.
- **new, deposit_letter, run 2** (19.0 s, $0.0507): tools load_skill, get_statute_section, save_line, count_days, count_days, note_fact; lines saved 1; questions 2; dates from nowhere: none. Same answer; saves the letter as a line but leaves the waiting line open.
- **new, deposit_letter, run 3** (22.2 s, $0.0570): tools load_skill, get_statute_section, count_days, count_days, save_line, save_line, note_fact; lines saved 2; questions 1; dates from nowhere: none. Closes the waiting line with the letter and opens a line for the objection still to send; also catches that the tenant left a day early (83.49(5)).
- **new, leave_early_reply, run 1** (12.7 s, $0.0285): tools get_statute_section, search_statute, save_line; lines saved 1; questions 1; dates from nowhere: none. Answers from the lease and 83.595; saves the manager's reply as a line but leaves the request line open.
- **new, leave_early_reply, run 2** (15.1 s, $0.0247): tools get_statute_section, get_statute_section, save_line; lines saved 1; questions 1; dates from nowhere: none. Same; the request line stays open.
- **new, leave_early_reply, run 3** (15.6 s, $0.0236): tools get_statute_section, search_statute, save_line; lines saved 1; questions 1; dates from nowhere: none. Good answer, but it works out a period itself ('May 15 to July 31 would be about 2.5 months'), against rule 7; the request line stays open.
- **new, repair_no_show, run 1** (15.3 s, $0.0389): tools get_statute_section, get_statute_section, save_line; lines saved 1; questions 2; dates from nowhere: none. Starts from the missed Thursday promise; saves 'nobody came' dated with the tenant's word Thursday; leaves the promise line open.
- **new, repair_no_show, run 2** (18.2 s, $0.0351): tools get_statute_section, get_statute_section, search_statute, save_line, count_days; lines saved 1; questions 2; dates from nowhere: none. Starts from the missed promise; 7 days out counted by count_days; leaves the promise line open.
- **new, repair_no_show, run 3** (17.1 s, $0.0344): tools get_statute_section, get_statute_section, search_statute, save_line, save_line; lines saved 2; questions 1; dates from nowhere: none. Closes the promise line and saves 'nobody came'; the next step is a written notice by hand or certified mail.
- new: $0.3627 in all
- **baseline, deposit_letter, run 1** (17.9 s, $0.0543): tools load_skill, get_statute_section, count_days, count_days, note_fact; lines saved 0; questions 2; dates from nowhere: none. From the old chat and facts: leads with 'object'; uses the confirmed move-out date; one question about the letter.
- **baseline, deposit_letter, run 2** (17.8 s, $0.0489): tools load_skill, get_statute_section, count_days, count_days, note_fact; lines saved 0; questions 1; dates from nowhere: none. Leads with what to do; catches the early move-out point (83.49(5)).
- **baseline, deposit_letter, run 3** (24.3 s, $0.0564): tools load_skill, get_statute_section, count_days, count_days, note_fact; lines saved 0; questions 1; dates from nowhere: none. Leads with 'object'; notes the claim's reason as a fact but not the day the letter came, so no deadline can be counted yet.
- **baseline, leave_early_reply, run 1** (13.9 s, $0.0335): tools get_statute_section, get_statute_section; lines saved 0; questions 1; dates from nowhere: none. Answers from the lease and 83.595; asks whether the reply said anything about re-renting.
- **baseline, leave_early_reply, run 2** (13.9 s, $0.0219): tools get_statute_section, search_statute, note_fact; lines saved 0; questions 1; dates from nowhere: none. Same; notes the landlord's answer as a fact.
- **baseline, leave_early_reply, run 3** (17.3 s, $0.0255): tools get_statute_section, search_statute, note_fact; lines saved 0; questions 1; dates from nowhere: none. Leads with 'Probably not'; same reasoning.
- **baseline, repair_no_show, run 1** (23.7 s, $0.0586): tools get_statute_section, get_statute_section, search_statute, count_days, get_statute_section, get_statute_section; lines saved 0; questions 2; dates from nowhere: none. Starts from the missed promise (from the old chat); asks what the text said, which it was not told.
- **baseline, repair_no_show, run 2** (18.7 s, $0.0383): tools get_statute_section, get_statute_section, search_statute, search_statute, count_days; lines saved 0; questions 1; dates from nowhere: none. Starts from the missed Thursday; asks whether anything besides texts was sent.
- **baseline, repair_no_show, run 3** (19.1 s, $0.0377): tools get_statute_section, get_statute_section, get_statute_section, count_days, search_statute; lines saved 0; questions 2; dates from nowhere: none. Starts from 'Thursday has passed with no repair'; same next step.
- baseline: $0.3751 in all
