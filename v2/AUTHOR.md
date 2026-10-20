# Author

Your decisions, sign-offs, and open questions. Claude adds an item when something needs you; you close it.

## Decided

- 2026-10-19: the lease is read by method A: PyMuPDF for the text, Gemma 4 for pages without usable text, the whole
  lease in the system prompt (`comparisons/lease/`).
- 2026-10-19: lease-reading rules 1 to 4 go in the system prompt (README.md). Rule 4 answers the slip in SLIPS.md.
  Rule 5 (pages read from an image) waits on item 1 below.

## Open

1. **Check boxes on pages read from an image.** Gemma 4 read 3 of the broken lease's 35 boxes wrong, and every
   method then told the tenant they pay for water. The quote check cannot catch it, since the quote matches what was
   read. Options: say so when an answer rests on a page read from an image; read such pages twice and flag any
   difference; or leave it. (`comparisons/lease/README.md`)
2. **How `count_days` counts.** Calendar days, the start day not counted, no weekend or holiday shift. Nobody has
   checked this against the statute yet (`../v1/AUTHOR.md`, item 3); every result says so until you do.
3. **Skills test, story 2: can the tenant demand the deposit at day 23?** The key says yes, they can ask now, and
   lists "must wait, cannot ask now" as a mistake. Your blind ranking put an answer saying exactly that ("No, wait until
   after August 30") first. Which is right? The judge's story-2 grades follow your answer. (`comparisons/skills/`)
4. **Skills test, story 5: can a text be the notice of a claim?** The key follows v1's skill: not settled, with a
   reading on each side (83.49(3)(a) names certified mail or agreed e-mail; 83.505(6) does not rule out other means).
   No answer gave both readings; all 12 said the text does not count. If you read it as settled, the key changes and
   so do those grades.
