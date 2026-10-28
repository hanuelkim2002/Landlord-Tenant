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
- 2026-10-25: code may do date math besides deadlines; the first use is the days since the tenant's last message,
  for the memory's "since last visit" (built the same day). The model still never works out a date, and
  `count_days` stays the only date math for deadlines.
- 2026-10-25: the memory is a timeline of numbered lines (date, what happened, open or not) and a since-last-visit
  note counted by code; the old chat stays; no due dates and no confirming lines
  (`docs/superpowers/specs/2026-10-25-memory-timeline-design.md`). The live test runs on Claude Sonnet 5.5 with the
  Anthropic key (`comparisons/memory/`).
- 2026-10-25: a line is open only while it waits for one specific next thing, and `save_line`'s reply lists the
  open lines (item 10): the old line closed in 15 of 15 answers with both (13 of 15 with the wording alone), up
  from 3 of 9.
- 2026-10-26: item 12's readings, from your review: a housing authority stays under (3), (5), (6); nothing is settled
  after an objection; a renewal's end starts the clocks; mail to the old address counts if no new one was given. A
  notice missing the 15-day warning or the objection address now gets two readings, like one missing the amount.
  The skill adds that the court hears these cases sooner (83.49(3)(c)).
- 2026-10-27: replies lead with a short plain answer (3 to 5 sentences, no section numbers or quotes), each point
  behind a click; the rules' cap is about 700 words (`docs/superpowers/specs/2026-10-27-plain-replies-design.md`).
- 2026-10-27: after the plain replies test (`comparisons/plain/`), the short answer stays as it is, though it runs
  past the rule's 3 to 5 sentences (median 7, 127 words). Both exemptions in my review of the plain counts are
  accepted: an "it" echoing the tenant's question in the first sentence, and a "this" or "it" that can only mean
  the dispute or the answer ("What if this goes to court?"), box titles included. The reviewed counts stand.
- 2026-10-28: the other skills follow the deposit skill's method (format A, built from v1's skill and statutes/).
  A shared skill holds the college-housing check (`who_the_law_covers`); the repair skill is the pilot, then the
  rest go two at a time, each with a small test (about 6 to 8 stories, 3 runs, v1 beside it, judged blind). Every
  skill has a "what the lease adds" step. Weekday counting for the unpaid-rent notice is decided when that skill is
  reached; it goes last (`docs/superpowers/specs/2026-10-28-other-skills-design.md`).
- 2026-10-28: the nine repair stories' keys, with your 25 answers in
  `comparisons/each_skill/repair_not_made/STORIES_REVIEW.md` (every recommended choice; Q4 accepts either date). The
  repair skill's new law point, against v1's: the winner of a suit may recover attorney fees and court costs (83.48).
- 2026-10-28: rule 7 also names time spans: say how long something lasted, or how long until a date, only in the
  tenant's own words. Chosen over v1's date rule and code's day counts (item 19, `comparisons/each_skill/README.md`).

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
5. **Decided 2026-10-21, changed 2026-10-23:** tenant data leaves UF. Leases, messages, and facts now go to
   Anthropic, not OpenRouter or Google (see Decided, 2026-10-23).
6. **Decided 2026-10-21, changed 2026-10-23:** the chat model is Claude Sonnet 5.5 from Anthropic (see Decided,
   2026-10-23). Gemini 3.8 Flash, chosen first (scores in `comparisons/models/SCORES.md`), is one setting away.
7. **Decided 2026-10-21:** every lease page is read from its image by Haiku 5.5 (see Decided).
8. **Decided 2026-10-21:** the deposit skill settles the college-housing question once: lease first, then one question
   if the lease is not clear, and the answer is saved as `school_housing` (see Decided). The lease is clear only if
   nothing in it points to a school: an enrollment clause, student-only terms, a school as a party, school services,
   or any other doubt means ask (your choice, 2026-10-21). Check the step's wording: what it looks for is my reading
   of 83.42(1)'s "incidental to the provision of ... educational ... services."
9. **Check my keys for your lease.** `comparisons/models/private/own_questions.json` and `own_stories.json`, written
   from the page images; the grades on your lease follow them.
10. **Decided 2026-10-25:** the timeline's old open lines: rule 9 and `save_line` say what open means, and
    `save_line`'s reply lists the open lines (see Decided; `comparisons/memory/SCORES.md`).
11. **The 1,000-line limit.** On 2026-10-27 app code is 883 lines without `tests.py` and 1,152 with it (870 and
    1,098 before reading 16 pages at once; 831 and 1,030 before plain replies; 722 and 811 before the memory). Your
    call whether `tests.py` counts toward the limit in CLAUDE.md.
12. **Decided 2026-10-26:** the deposit skill's new law points (see Decided). Still yours to check: story 12's key
    reads 83.491(6) as putting a fee outside 83.49.
13. **Judging story 17: is a backup "two readings"?** Answers say "yes, all $1,050" and then "even if the letter
    counted, at least $650 is owed". One Opus judge counted that as two readings (wrong), another did not. Your rule
    decides the grade; `comparisons/deposit/README.md`, fourth run.
14. **A tenant who stayed on month to month after the lease ran out.** 83.49(6) does not say whether that is a
    renewal. The skill does not ask; it takes the date the tenancy ended. Does that need its own answer?
15. **Decided 2026-10-27:** the plain replies test's two calls: the short answer stays as it is, and both exemptions
    in my review of the plain counts are accepted (see Decided; `comparisons/plain/README.md`).
16. **Decided 2026-10-28: the repair skill's new law points approved,** with the seven repair stories' keys
    (`comparisons/each_skill/repair_not_made/stories.json`). What it says that v1's repair skill did not:
    - Option 3, damages (83.55), for a lease promise or an 83.51 duty; rent paid with knowledge may give it up too
      (83.56(5)(a) names "a civil action").
    - Option 4, retaliation (83.64): good faith, being treated differently (83.64(4)), and good cause, whose examples
      include actions for nonpayment of rent (83.64(3)), so a tenant sued over rent held back looks to option 2.
    - Option 5, a landlord trying but unable to fix it (83.56(1)(a) and (b)); two readings of "terminated or altered
      by the parties".
    - Lease-promised items (an appliance, air conditioning, a pool): ending the lease, damages, and retaliation can
      reach them, holding back rent never does; two readings of whether a clause limiting an amenity is void under
      83.47(1).
    - Air conditioning is named nowhere in 83.51. Pest treatment: rent abated, 7 days' notice, at most 4 days out
      (83.51(2)(a)). Screens (83.51(1)). A mobile home the tenant owns is not the landlord's to maintain (83.51(1)).
    - A lease cannot waive the notice rules of 83.56(1) to (3) (83.56(4)); e-mail counts only with every condition of
      83.505(1), not the signed addendum alone.
17. **Three corrections to the repair skill, from the branch review** (2026-10-28, not yet in a live run). Each
    quotes stored text the skill had left out or narrowed:
    - For an item only 83.51(2)(a) names (pests, locks, common areas, garbage, heat, water), a writing may change the
      landlord's duty in any home: the paragraph applies "Unless otherwise agreed in writing". v1 said the same.
    - An e-mail notice under 83.505 counts from when it was sent, not received (83.505(4)). New against v1.
    - Once sued, paying the rent into the registry "or" filing "a motion to determine the amount of rent" within the 5
      days keeps the defenses (83.60(2)); the skill had named only paying. New against v1.
18. **Judging the repair rerun: narrow but harmless wordings.** Told that any other error fails an answer, one grader
    moved five lines to its reasons: the 83.60 defense "only if" sued for eviction (story 4, v1); ending the lease
    only for an 83.51(1) duty (story 5, keys2 twice, v1 once), harmless since the lease puts guest damage on the
    tenant; "doesn't spell out any other remedy", hedged at once (story 6, keys2). Not counted: keys2 19 of 27 right,
    v1 12. Counted: 16 and 10. Your call. Also: should 83.57 join the graders' sections? Every story-6 answer cites it.
    (`comparisons/each_skill/README.md`, the rerun.)
19. **Decided 2026-10-28: rule 7 names time spans** (see Decided). Side by side on five repair stories, 15 answers
    each: rule 7 naming spans cut model-counted spans from 3 to 1, with the fewest spans of any kind (2 answers) and
    no made-up date; v1's longer date rule also 1; code's day counts made it worse (5, and 3 with the rule). Right
    answers 12 to 14 in all. (`comparisons/each_skill/README.md`)
