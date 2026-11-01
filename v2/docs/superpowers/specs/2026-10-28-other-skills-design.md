# The other skills: a shared check, then repairs first (design)

2026-10-28. Agreed in chat with the author; this writes it down.

## Why

v1 has ten skills. v2 has one, `deposit_not_returned`, written as an element checklist (format A) and tested on 18
stories. v2's deposit skill already holds most of v1's `deposit_claim_received` (its option 2), so eight are left.
README.md lets the others follow once the author approves the method. On 2026-10-28 the author did, and chose how.

## Decisions (2026-10-28)

- The method: format A, each skill built from v1's skill and the `statutes/` sections it rests on.
- Pilot, then pairs: a shared check and the repair skill first, tested; what that test shows goes into the format;
  then the rest two at a time, each pair tested.
- The college-housing check lives in one shared skill, not in a copy per skill.
- Each skill gets a small test (below), not the deposit skill's 18 stories and five rounds.
- Every skill has a "what the lease adds" step, since what a lease promises differs from lease to lease.
- Weekday counting for the unpaid-rent notice (83.56(3), 83.60(2)) is decided when that skill is reached; it goes
  last.
- The deposit skill's fixes run in another session, on their own branch. This work does not edit
  `skills/deposit_not_returned.md`.

## Order

Names follow v1's.

1. `who_the_law_covers` (new, shared) and `repair_not_made`: the pilot.
2. `wants_to_leave_early` and `notice_received_violation`.
3. `lease_ending` and `rent_increased`.
4. `landlord_entered_unannounced` and `neighbor_disturbance`. The entry rule is in hours (83.53(2)); how to treat it
   is decided with that pair.
5. `notice_received_nonpayment`, after the counting decision.

Changed 2026-10-31: `neighbor_disturbance` goes with step 3 as one group of three. The counting plan is dropped for now, so
`landlord_entered_unannounced` and `notice_received_nonpayment` wait.

## The shared skill: `who_the_law_covers`

- Description, draft: "Whether Florida's landlord-tenant law covers the tenant's home at all, such as college housing.
  Load it with any other skill, unless the facts already hold school_housing."
- Body: the deposit skill's 83.42(1) check as it stands: the lease first; one plain question only if the lease is not
  clear; the answer noted as `school_housing`, never asked twice; 83.42 read before telling the tenant.
- New: one line on the other four exclusions in 83.42(2) to (5) (a contract of sale, transient lodging, a cooperative,
  a condominium owner), checked only when the facts point to one.
- Each other new skill opens by loading it, unless the facts hold `school_housing`.
- `deposit_not_returned` keeps its own copy until the deposit fixes are merged; then it points to the shared skill
  (a TODO.md item).

## The format every skill follows

1. Header: a name, and a one-line description that no other skill's could be mistaken for.
2. The sections it rests on, and the no-lean line: when the answer turns on a point marked not settled, the first
   sentence says so and leans neither way.
3. First, whether this applies: load `who_the_law_covers`, and any limit that applies only to this situation.
4. What the lease adds: which clauses to read, and how a lease promise or limit changes each option.
5. Facts the answer turns on: each named for `note_fact`, dates written YYYY-MM-DD.
6. One part for each thing the tenant can do: numbered conditions, each met, not met, the tenant can tell, not settled
   (both readings, no lean), or outside the tool. Each `count_days` call and each open question sits inside the
   condition that uses it.
7. Mistakes to avoid.

What the deposit skill taught, built in from the start:

- A rule with a time limit: check the date of the act against it, not only whether the period has passed.
- Quote all of a rule's conditions, not the first one only.
- Say plainly when a condition is met.
- State no standard the statute does not set.
- A point another skill covers is left to it ("load X"), not repeated.

## The repair skill: `repair_not_made`

Rests on 83.51, 83.56(1), (4), and (5), 83.60(1) and (2), 83.55, 83.64, 83.47, and 83.505.

**Whose job it is** (every option starts here):

- 83.51(1): what building, housing, and health codes require (outside the tool: send the tenant to the city or county
  code office), or, where there are none, the structure and the plumbing; screens. Changed in writing only for a
  single-family home or duplex.
- 83.51(2)(a): pests, locks and keys, common areas, garbage, heat in winter, running water, and hot water, in a unit
  other than a single-family home or duplex, unless agreed otherwise in writing. Not a defense to an action for
  possession (83.51(2)(c)).
- The lease: items it promises (appliances, air conditioning, a washer and dryer, a pool or gym, parking, furniture,
  internet), who repairs them, any clause on closing them, any fee for them.
- Caused by the tenant, family, or a guest: not the landlord's (83.51(4)).

**What the tenant can do:**

1. End the lease (83.56(1)): a failure of an 83.51(1) duty or a material lease provision; a written notice delivered
   as 83.56(4) allows, naming the problem and the intent to end the lease; 7 days after delivery
   (`count_days`); not given up by rent paid with knowledge (83.56(5)(a)).
2. Hold back rent and raise the problem if sued (83.60(1)(b)): an 83.51(1) duty only, never an item only the lease or
   83.51(2) names; a written notice of the intent not to pay rent, to a person 83.60(1)(b) names; 7 days after
   delivery (`count_days`). The risk comes first: once sued, the rent goes into the court registry within 5 days not
   counting weekends and legal holidays (83.60(2)), a date the tool does not count; the court sets any reduction.
3. Damages (83.55): for a failure to follow the lease or part II.
4. A code complaint, and retaliation (83.64): its list of protected acts, good faith, and good cause (83.64(3)); a
   defense in an action for possession.
5. Causes beyond the landlord's control (83.56(1)(a) and (b)): no rent while the home is untenantable if the tenant
   leaves; rent reduced if they stay.

**Not settled**, each inside the condition that uses it: what "material" means; running and hot water on both lists;
rent paid while the problem goes on; a roommate who caused it; how the rent-withholding notice is delivered; whether a
lease clause that limits an amenity is void under 83.47(1); whether "terminated or altered by the parties" in
83.56(1) needs both to agree.

**New compared with v1**, for the author's check: options 3, 4, and 5; the lease-promised items, with 83.47(1); air
conditioning named nowhere in 83.51; pest treatment (83.51(2)(a)1: 7 days' written notice, at most 4 days out, rent
abated); screens.

**Other skills:** an eviction case filed goes to `notice_received_nonpayment` (until it exists, the registry rule and
"outside the tool"); a tenant who ended the lease and moved out goes to `deposit_not_returned` for the deposit.

## Testing

- `comparisons/each_skill/run.py <skill> <version>`: one runner for every skill. Each story is answered through the
  app's own chat (Claude Sonnet 5.5 from Anthropic), 3 runs, from a throwaway skills folder holding today's skills with
  the tested version in place, so the model chooses skills as it does on the page. v1's skill runs under v2's header,
  as in the deposit test. It reuses `comparisons/models/`.
- `comparisons/each_skill/repair_not_made/`: the stories with their keys (points, mistakes, law, dates), copies of
  `comparisons/skills/lease.txt` with one clause changed (an amenities list, a repair clause, a single-family home),
  the results, a README, and the scores. `comparisons/skills/check_key.py` checks each key's quotes and dates first.
- The repair stories, draft: the air conditioning is out and the lease lists it; no hot water, a notice to end the
  lease delivered 10 days ago; a leaking roof, and the tenant wants to stop paying rent but has sent nothing; a pool or
  dishwasher the lease promises is broken, can they hold back rent; a guest caused the damage; rent went up right after
  a code complaint; the lease ended over a repair, the tenant moved out, and asks about the deposit.
- Graded blind by Claude Opus 5.5 subagents in Claude Code with the deposit test's rubric. Code checks quotes and
  made-up dates. Results as a chart.
- Done when: the new skill is right at least as often as v1 on the settled stories, no date is made up, and every quote
  in the skill checks out (`python law.py`). Each miss is sorted as the skill's, the test's, or a judge's call; one
  round of fixes, rerunning only the missed stories; what is left goes in SLIPS.md.
- About $4 per skill (about 42 answers).

## The author's checkpoints

1. The drafted skills: what they say about the law that v1's did not, before any test.
2. The stories and keys, before any run.
3. The results: the misses and any judge's calls.

## Left out on purpose

Letters (README.md leaves them out); weekday counting (decided at the unpaid-rent skill); counting hours (decided with
the entry skill); any change to `deposit_not_returned` in this work; any change to app code.

## Size

App code: none. Skills: about 300 words (shared) and 2,500 to 3,000 (repair). Test code, outside app code: about 120
lines.

## Docs

README.md (how skills are written now covers all of them; the shared skill), DOCUMENTATION.md (the skills),
AUTHOR.md (the decisions; an open item for the repair skill's new law points), TODO.md (the pairs; pointing the deposit
skill to the shared one), CHANGELOG.md.
