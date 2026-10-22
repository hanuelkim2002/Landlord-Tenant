# Model comparison: scores

Right, partly, wrong: the judge's grades (gpt-oss-120b on UF), after my changes listed under each table. Quotes word for word: quotations of 20 characters or more found word for word in statutes/ or the lease the model read, wherever the cite is; in brackets, how many the page's own check passes (it looks for the cite only after the quote). A made-up date is one the model wrote that is not in the facts, the lease, the tenant's message, or a count_days result. Costs: OpenRouter's own figure; with a ~ they are worked out from token counts and list prices (UF models are always worked out, and are the UF budget, not money).

## Sample leases

### Test 1: the deposit stories (3 runs each)

| Model | Your average rank (1 is best) | Your firsts | Stories 1, 3, 4: right / partly / wrong | Stories 2, 5 (your open calls): right / partly / wrong |
| --- | --- | --- | --- | --- |
| nemotron | - | - | 7 / 0 / 2 | 2 / 0 / 4 |
| haiku | - | - | 7 / 1 / 1 | 6 / 0 / 0 |
| gemini | - | - | 9 / 0 / 0 | 6 / 0 / 0 |
| sonnet | - | - | 9 / 0 / 0 | 6 / 0 / 0 |

| Model | Answers first | Quotes word for word (the page's check) | Answers with a made-up date | Asks more than one question | Skill loaded | count_days used | Median words | Median time | Mean cost per answer | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nemotron | 10 of 15 | 7 of 9 (2) | 3 of 15 | 0 of 15 | 4 of 15 | 12 of 15 | 317 | 27.8 s | ~$0.0018 | 0 |
| haiku | 15 of 15 | 45 of 45 (23) | 0 of 15 | 1 of 15 | 15 of 15 | 15 of 15 | 576 | 29.3 s | $0.0053 | 0 |
| gemini | 15 of 15 | 48 of 50 (24) | 0 of 15 | 3 of 15 | 15 of 15 | 15 of 15 | 444 | 37.0 s | $0.0276 | 0 |
| sonnet | 13 of 15 | 55 of 57 (38) | 0 of 15 | 0 of 15 | 15 of 15 | 15 of 15 | 489 | 17.9 s | $0.0575 | 0 |

My changes to the judge's grades:

- nemotron, deposit-1/2: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- haiku, deposit-1/1: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- haiku, deposit-2/1: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- haiku, deposit-4/1: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- haiku, deposit-5/3: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- haiku, deposit-3/1: right. The judge misread it: the answer says the landlord's silence does not forfeit its claim (83.49(5)), the key's point, not the listed mistake.
- haiku, deposit-3/3: right. All points made. 'The statute does not say how long the landlord has to make one' refers to a claim once the landlord is relieved of the notice; that is accurate, not a denial of the 30-day period.
- haiku, deposit-5/2: right. All points made. 'Owed the $650 under either reading' is true (under one reading the whole $1,050 is owed, which includes it).
- haiku, deposit-1/3: partly. Core right (forfeiture from the missed 30-day notice), but it misstates the 15-day return rule. ('return the deposit, or send a notice of any claim, within 15 days')
- gemini, deposit-1/1: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- gemini, deposit-1/2: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- gemini, deposit-1/3: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- gemini, deposit-2/2: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- gemini, deposit-2/3: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- gemini, deposit-3/1: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- sonnet, deposit-2/3: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- sonnet, deposit-3/2: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- sonnet, deposit-4/3: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- sonnet, deposit-5/2: right. All points made, no listed mistake. The judge's only complaint was a mention of 83.42(1) (whether part II covers housing tied to schooling); the words are in statutes/83.42.txt, and the deposit skill tells the model to read 83.42 and say what it would need to know. The judge had only 83.49 and 83.505.
- sonnet, deposit-2/1: right. All points made. Says a notice sent some other way (regular mail, a text, the portal) may or may not count and gives both readings, as the story 5 key does (83.505(6)); the judge applied its own reading.
- sonnet, deposit-2/2: right. All points made. Says a notice sent some other way (regular mail, a text, the portal) may or may not count and gives both readings, as the story 5 key does (83.505(6)); the judge applied its own reading.
- sonnet, deposit-5/3: right. All points made. Says a notice sent some other way (regular mail, a text, the portal) may or may not count and gives both readings, as the story 5 key does (83.505(6)); the judge applied its own reading.

### Test 2: questions about the lease

| Row | Answers | Right | Partly | Wrong | Wrongly silent (covered, said not covered) | Made up (not covered, answered anyway) | Quotes word for word (the page's check) | Median time | Mean cost per answer | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nemotron | 51 | 48 | 0 | 3 | 0 of 42 | 0 of 9 | 37 of 40 (34) | 6.2 s | ~$0.0010 | 0 |
| nemotron / gemini texts | 12 | 11 | 0 | 1 | 0 of 10 | 0 of 2 | 13 of 13 (12) | 12.2 s | ~$0.0010 | 0 |
| nemotron / gemma texts | 12 | 10 | 0 | 2 | 0 of 10 | 0 of 2 | 13 of 13 (13) | 11.2 s | ~$0.0009 | 0 |
| nemotron / haiku texts | 12 | 10 | 0 | 2 | 0 of 10 | 1 of 2 | 12 of 12 (12) | 9.1 s | ~$0.0007 | 0 |
| nemotron / sonnet texts | 12 | 10 | 0 | 2 | 0 of 10 | 0 of 2 | 14 of 14 (14) | 8.1 s | ~$0.0009 | 0 |
| haiku | 51 | 51 | 0 | 0 | 0 of 42 | 0 of 9 | 82 of 113 (77) | 10.5 s | $0.0015 | 0 |
| gemini | 51 | 50 | 1 | 0 | 0 of 42 | 0 of 9 | 65 of 97 (61) | 15.2 s | $0.0098 | 0 |
| sonnet | 51 | 51 | 0 | 0 | 0 of 42 | 0 of 9 | 122 of 154 (107) | 11.2 s | $0.0202 | 0 |

My changes to the judge's grades:

- nemotron, short-08: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.53(2): entry at any time for protection or preservation.)
- nemotron, short-12: right. Says the lease has no early termination fee; the 83.595 remedies it adds are accurate.
- nemotron, long-14: right. Says the lease does not address it; the conclusion drawn ('so it is not required' / 'so you may') is a fair inference, not a claim that the lease says so (as in the lease test's review of short-11).
- nemotron, scan-07: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.53(2): 24 hours for repairs.)
- haiku, short-08: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.53(2).)
- haiku, short-11: right. Says the lease does not address it; the conclusion drawn ('so it is not required' / 'so you may') is a fair inference, not a claim that the lease says so (as in the lease test's review of short-11).
- haiku, long-08: right. The judge was wrong: Addendum H-1 does say 'Subletting is not allowed'.
- haiku, long-13: right. Says the lease does not address it; the conclusion drawn ('so it is not required' / 'so you may') is a fair inference, not a claim that the lease says so (as in the lease test's review of short-11).
- haiku, long-14: right. Says the lease does not address it; the conclusion drawn ('so it is not required' / 'so you may') is a fair inference, not a claim that the lease says so (as in the lease test's review of short-11).
- haiku, scan-04: right. Right number; the added point on written notice is accurate.
- haiku, scan-07: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.53(2), 83.47(1)(a).)
- haiku, broken-01: right. Both points made. Reading error, not the chat model's: the stored text (Gemma 4's reading) marks this box wrongly, and the answer reports what that text says. (payment boxes)
- haiku, broken-04: right. Portal, as the checked box says; noting that another section lists other ways to give notice is a fair point, not a contradiction.
- haiku, broken-06: right. Reading error, not the chat model's: the stored text (Gemma 4's reading) marks this box wrongly, and the answer reports what that text says. (water is checked under both lists; the answer says the lease contradicts itself)
- haiku, broken-09: right. 30 days and $975 right. Reading error, not the chat model's: the stored text (Gemma 4's reading) marks this box wrongly, and the answer reports what that text says. (a stray [X] in section 2)
- haiku, broken-10: right. The judge was wrong: the answer says subletting is not allowed (checked box).
- gemini, short-08: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.53(2).)
- gemini, short-11: right. Says the lease does not address it; the conclusion drawn ('so it is not required' / 'so you may') is a fair inference, not a claim that the lease says so (as in the lease test's review of short-11).
- gemini, scan-06: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.595(4): the fee needs a signed addendum.)
- gemini, scan-07: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.53(2).)
- gemini, broken-01: right. Both points made: it quotes the clause with the $10 a day and the $175.00 cap.
- gemini, broken-06: right. Reading error, not the chat model's: the stored text (Gemma 4's reading) marks this box wrongly, and the answer reports what that text says. (water checked under both lists; the answer says the lease contradicts itself)
- gemini, broken-09: partly. 30 days right, but it misstates 83.575(1) as 'between 30 and 60 days' (the statute sets only a 60-day maximum).
- sonnet, short-04: right. Says to call the landlord's phone first, then text for a record; not 'just text'.
- sonnet, scan-06: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.595(4).)
- sonnet, scan-07: right. Lease term reported right; the added statute point is accurate (in statutes/). The judge's prompt counts anything the lease does not say as an error, written for lease-only answers; the chat applies the law (rule 1). (83.53(2), 83.47(1)(a).)
- sonnet, scan-12: right. Says the lease does not address it; the conclusion drawn ('so it is not required' / 'so you may') is a fair inference, not a claim that the lease says so (as in the lease test's review of short-11).
- sonnet, broken-06: right. Reading error, not the chat model's: the stored text (Gemma 4's reading) marks this box wrongly, and the answer reports what that text says. (water checked under both lists; the answer says the lease gives no clear answer)
- sonnet, broken-10: right. The judge was wrong: the answer says subletting is not allowed (checked box).

### Test 3: reading pages from images

| Reader | Lease | Word accuracy (mean of runs) | Check boxes right (mean of runs) | Pages that differ between runs | Boxes that differ between runs | Median time per page | Mean cost per page |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gemma | scanned | 100.0% | - | 2 | 0 | 3.7 s | $0.0002 |
| gemma | broken_text | 99.8% | 31.3 of 35 | 2 | 2 | 2.6 s | $0.0002 |
| gemma | all | 99.9% | 31.3 of 35 | 4 | 2 | 3.1 s | $0.0002 |
| gemini | scanned | 100.0% | - | 3 | 0 | 11.4 s | $0.0076 |
| gemini | broken_text | 100.0% | 34.0 of 35 | 1 | 0 | 12.0 s | $0.0074 |
| gemini | all | 100.0% | 34.0 of 35 | 4 | 0 | 11.4 s | $0.0075 |
| haiku | scanned | 100.0% | - | 0 | 0 | 5.5 s | $0.0008 |
| haiku | broken_text | 100.0% | 35.0 of 35 | 0 | 0 | 5.3 s | $0.0008 |
| haiku | all | 100.0% | 35.0 of 35 | 0 | 0 | 5.3 s | $0.0008 |
| sonnet | scanned | 100.0% | - | 1 | 0 | 8.6 s | $0.0166 |
| sonnet | broken_text | 100.0% | 35.0 of 35 | 0 | 0 | 7.2 s | $0.0165 |
| sonnet | all | 100.0% | 35.0 of 35 | 1 | 0 | 8.4 s | $0.0165 |

| Reader | Run | Word accuracy, scanned | Word accuracy, broken_text | Check boxes right, broken_text | Median time per page | Mean cost per page |
| --- | --- | --- | --- | --- | --- | --- |
| gemma | 1 | 100.0% | 99.9% | 31 of 35 | 2.6 s | $0.0002 |
| gemma | 2 | 100.0% | 99.9% | 31 of 35 | 3.1 s | $0.0002 |
| gemma | 3 | 100.0% | 99.8% | 32 of 35 | 3.1 s | $0.0002 |
| gemini | 1 | 100.0% | 100.0% | 34 of 35 | 11.9 s | $0.0072 |
| gemini | 2 | 100.0% | 100.0% | 34 of 35 | 10.9 s | $0.0071 |
| gemini | 3 | 100.0% | 100.0% | 34 of 35 | 12.0 s | $0.0082 |
| haiku | 1 | 100.0% | 100.0% | 35 of 35 | 5.8 s | $0.0008 |
| haiku | 2 | 100.0% | 100.0% | 35 of 35 | 5.3 s | $0.0008 |
| haiku | 3 | 100.0% | 100.0% | 35 of 35 | 5.3 s | $0.0008 |
| sonnet | 1 | 100.0% | 100.0% | 35 of 35 | 7.3 s | $0.0165 |
| sonnet | 2 | 100.0% | 100.0% | 35 of 35 | 8.4 s | $0.0165 |
| sonnet | 3 | 100.0% | 100.0% | 35 of 35 | 8.6 s | $0.0165 |

## The author's own lease

### Test 1: the deposit stories (3 runs each)

| Model | Your average rank (1 is best) | Your firsts | Stories 1, 3, 4: right / partly / wrong | Stories 2, 5 (your open calls): right / partly / wrong |
| --- | --- | --- | --- | --- |
| nemotron | - | - | 4 / 2 / 3 | 2 / 0 / 4 |
| haiku | - | - | 6 / 0 / 3 | 6 / 0 / 0 |
| gemini | - | - | 9 / 0 / 0 | 6 / 0 / 0 |
| sonnet | - | - | 9 / 0 / 0 | 6 / 0 / 0 |

| Model | Answers first | Quotes word for word (the page's check) | Answers with a made-up date | Asks more than one question | Skill loaded | count_days used | Median words | Median time | Mean cost per answer | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nemotron | 15 of 15 | 5 of 7 (4) | 6 of 15 | 1 of 15 | 0 of 15 | 5 of 15 | 340 | 35.1 s | ~$0.0056 | 0 |
| haiku | 14 of 15 | 39 of 40 (12) | 1 of 15 | 0 of 15 | 15 of 15 | 15 of 15 | 570 | 36.8 s | $0.0113 | 0 |
| gemini | 14 of 15 | 47 of 49 (17) | 0 of 15 | 3 of 15 | 15 of 15 | 15 of 15 | 467 | 20.5 s | $0.0486 | 0 |
| sonnet | 15 of 15 | 52 of 54 (34) | 0 of 15 | 0 of 15 | 15 of 15 | 15 of 15 | 499 | 20.2 s | $0.1246 | 0 |

### Test 2: questions about the lease

| Row | Answers | Right | Partly | Wrong | Wrongly silent (covered, said not covered) | Made up (not covered, answered anyway) | Quotes word for word (the page's check) | Median time | Mean cost per answer | Errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nemotron | 17 | 10 | 4 | 3 | 0 of 15 | 1 of 2 | 8 of 10 (8) | 13.4 s | ~$0.0034 | 0 |
| nemotron / app texts | 17 | 9 | 1 | 7 | 2 of 15 | 0 of 2 | 10 of 12 (10) | 21.0 s | ~$0.0060 | 0 |
| nemotron / gemini texts | 17 | 11 | 3 | 3 | 0 of 15 | 1 of 2 | 11 of 12 (11) | 9.4 s | ~$0.0034 | 0 |
| nemotron / gemma texts | 17 | 10 | 1 | 6 | 0 of 15 | 0 of 2 | 11 of 11 (10) | 11.7 s | ~$0.0043 | 0 |
| nemotron / sonnet texts | 17 | 13 | 2 | 2 | 0 of 15 | 0 of 2 | 11 of 12 (11) | 12.8 s | ~$0.0037 | 0 |
| haiku | 17 | 17 | 0 | 0 | 0 of 15 | 0 of 2 | 56 of 72 (55) | 10.3 s | $0.0025 | 0 |
| gemini | 17 | 17 | 0 | 0 | 0 of 15 | 0 of 2 | 30 of 41 (30) | 11.8 s | $0.0110 | 0 |
| sonnet | 17 | 17 | 0 | 0 | 0 of 15 | 0 of 2 | 47 of 75 (47) | 12.7 s | $0.0315 | 0 |

### Test 3: reading pages from images

| Reader | Text fields right | Box fields right | Box fields with no mark found | All fields right | Word recall of the printed text (32 pages) | Pages | Median time per page | Mean cost per page |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| text layer (PyMuPDF) | 22 of 39 | 0 of 32 | 32 | 22 of 71 | - | 32 | - | - |
| app | 25 of 39 | 1 of 32 | 31 | 26 of 71 | 98.7% | 32 | - | - |
| gemma | 27 of 39 | 24 of 32 | 1 | 51 of 71 | 84.3% | 32 | 17.7 s | $0.0004 |
| gemini | 39 of 39 | 32 of 32 | 0 | 71 of 71 | 96.4% | 32 | 19.1 s | $0.0141 |
| haiku | 39 of 39 | 32 of 32 | 0 | 71 of 71 | 96.3% | 32 | 6.4 s | $0.0014 |
| sonnet | 39 of 39 | 32 of 32 | 0 | 71 of 71 | 96.4% | 32 | 10.0 s | $0.0265 |

