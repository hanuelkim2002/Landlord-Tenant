# Author

Your decisions, sign-offs, and open questions. Claude adds an item when something needs you; you close it.

## Decided

- 2026-10-19: the lease is read by method A: PyMuPDF for the text, Gemma 4 for pages without usable text, the whole
  lease in the system prompt (`comparisons/lease/`).
- 2026-10-19: lease-reading rules 1 to 4 go in the system prompt (README.md). Rule 4 answers the slip in SLIPS.md.
  Rule 5 (pages read from an image) waits on item 1 below.
- 2026-10-20: skills are written as element checklists (format A), each open question and `count_days` call inside the
  condition that uses it (`comparisons/skills/`).
- 2026-10-20: OpenRouter is set up to test outside models (Claude, Gemini) against nemotron. UF stays the default.
- 2026-10-20: your own lease goes to OpenRouter (and so to Anthropic and Google) for the model test. It is kept in
  `comparisons/models/private/`, out of git, with the guarantor's details blacked out. Item 5 stays open for anyone
  else's data.
- 2026-10-21: no blind ranking for the model test; its grades rest on the judge and my review of it.
- 2026-10-21: Haiku 5.5 on OpenRouter reads every lease page from its image (item 7). It replaces PyMuPDF's text and
  Gemma 4. Every tenant's lease now goes to OpenRouter and Anthropic.
- 2026-10-21: Gemini 3.8 Flash on OpenRouter is the chat model (item 6). It replaces nemotron on UF. The tenant's
  messages and facts now go to OpenRouter and Google (item 5).
- 2026-10-21: the college-housing question (83.42(1)) is settled once per matter: the lease first, one plain question
  only if the lease is not clear, and the answer saved as a fact (item 8).
- 2026-10-22: quotation marks only for the statute's and the lease's words; what the tenant said, the facts, and
  messages are put in the model's own words, and the quote check does not check them (rule 6).
- 2026-10-22: the model asks for all the lookups it needs in one step, not one at a time.
- 2026-10-24: the keys for deposit stories 13 to 18 (`comparisons/skills/stories_more.json`), as written.
- 2026-10-23: the chat runs on Claude Sonnet 5.5 and the lease reader on Haiku 5.5, both straight from Anthropic
  (your API credit), through its OpenAI-compatible endpoint so the code stays as it is. Tenant messages, facts,
  and leases now go to Anthropic, not OpenRouter or Google. Gemini stays one setting away (GATEWAY=openrouter).
- 2026-10-23: a notice of a claim that gives no reason is not the required notice, since 83.49(3)(a) names the
  reason; only a notice without the amount gets two readings.

## Open

1. **Check boxes on pages read from an image.** Gemma 4 read 3 of the broken lease's 35 boxes wrong, and every
   method then told the tenant they pay for water. The quote check cannot catch it, since the quote matches what was
   read. Options: say so when an answer rests on a page read from an image; read such pages twice and flag any
   difference; or leave it. (`comparisons/lease/README.md`) Since 2026-10-21 Haiku reads every page; in the model test
   it read every box right (35 of 35 on that lease, 32 of 32 on yours), the same in all three runs.
2. **How `count_days` counts.** Calendar days, the start day not counted, no weekend or holiday shift. Nobody has
   checked this against the statute yet (`../v1/AUTHOR.md`, item 3); every result says so until you do.
3. **Skills test, story 2: can the tenant demand the deposit at day 23?** The key says yes, they can ask now, and
   lists "must wait, cannot ask now" as a mistake. Your blind ranking put an answer saying exactly that ("No, wait until
   after August 30") first. Which is right? The judge's story-2 grades follow your answer. (`comparisons/skills/`)
4. **Skills test, story 5: can a text be the notice of a claim?** The key follows v1's skill: not settled, with a
   reading on each side (83.49(3)(a) names certified mail or agreed e-mail; 83.505(6) does not rule out other means).
   No answer gave both readings; all 12 said the text does not count. If you read it as settled, the key changes and
   so do those grades.
5. **Decided 2026-10-21:** tenant data leaves UF: leases go to OpenRouter and Anthropic, the chat to OpenRouter and
   Google (see Decided).
6. **Decided 2026-10-21:** Gemini 3.8 Flash is the chat model (see Decided; scores in `comparisons/models/SCORES.md`).
7. **Decided 2026-10-21:** every lease page is read from its image by Haiku 5.5 (see Decided).
8. **Decided 2026-10-21:** the deposit skill settles the college-housing question once: lease first, then one question
   if the lease is not clear, and the answer is saved as `school_housing` (see Decided). The lease is clear only if
   nothing in it points to a school: an enrollment clause, student-only terms, a school as a party, school services,
   or any other doubt means ask (your choice, 2026-10-21). Check the step's wording: what it looks for is my reading
   of 83.42(1)'s "incidental to the provision of ... educational ... services."
9. **Check my keys for your lease.** `comparisons/models/private/own_questions.json` and `own_stories.json`, written
   from the page images; the grades on your lease follow them.
10. **The deposit skill's new law points (draft, 2026-10-22).** My readings for you to check: a housing authority as
   landlord is still under (3), (5), (6) (83.49(4)); certified mail to the old address counts if no new one was
   given; nothing is settled after an objection; a renewal's end starts the clocks (83.49(6)); a notice with the
   amount and the reason counts without the 15-day warning or the objection address. Left open with two
   readings: a private landlord in a housing program, mail to the old address after a new one was given, a notice
   without the amount. Story 12's key reads 83.491(6) as putting a fee outside 83.49.
11. **Judging story 17: is a backup "two readings"?** Answers say "yes, all $1,050" and then "even if the letter
   counted, at least $650 is owed". One Opus judge counted that as two readings (wrong), another did not. Your rule
   decides the grade; `comparisons/deposit/README.md`, fourth run.
