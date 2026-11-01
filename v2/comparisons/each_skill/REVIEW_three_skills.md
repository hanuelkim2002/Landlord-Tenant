# The neighbor, rent, and lease-ending skills: what needs your OK

These three instructions for the chatbot are drafted, with test stories and their right answers. Nothing has been sent
to a model yet. Your OK comes first: the test grades against these answers.

- The instructions: `skills/neighbor_disturbance.md`, `skills/rent_increased.md`, `skills/lease_ending.md`.
- The stories: `stories.json` in `neighbor_disturbance/`, `rent_increased/`, and `lease_ending/`, in this folder.
- Every statute quote passed the word-for-word check. Three independent readers then went through each draft against the
  stored statutes, and their fixes are in. I left out one small suggestion (a way to get the end of a rent period from
  `count_days`).

## Questions

Reply "all recommended" to accept every first choice. The first three matter most.

**Q1. A rent increase with no set end date.** The statute sets no notice for an increase, and it never says a landlord may
change the rent alone. The old version gave two readings: the same 30 days it takes to end the tenancy, or no particular
notice. A reader found a third, and the stored text supports it: 83.57 only lets a party end a tenancy, so the rent changes
only if the tenant agrees. The test lease's section 10 (changes must be signed) points the same way.

- Recommended: not settled, all three readings, no lean. Under every reading the landlord may end the tenancy on that
  notice with no reason named, so the tenant hears what refusing can lead to. (rent-4, rent-6)
- Or keep the old version's two readings.

**Q2. A rent increase during a set term, with no clause and no agreement.** The old version listed "an increase needs a
lease clause or the tenant's agreement" as one reading of an open question. Nothing in part II lets a landlord change the
rent during a term, and the lease states the rent.

- Recommended: say it plainly. The landlord cannot change the rent alone before the lease ends. This rests on the lease
  and on the statute's silence, so please read it closely. (rent-1, rent-7, rent-8)
- Or keep it not settled.

**Q3. Must a landlord act on a neighbor?** The old version called this not settled, but its two readings did not oppose
each other ("need not act" and "must act if the lease says so").

- Recommended: say plainly that part II has no sentence requiring it and no deadline, and that a lease can add a duty. With
  no promise in the lease, ending the lease over this is not open on the words the tool holds. One line adds that whether
  other law reads such a promise into a lease without words is outside the tool. (neighbor-1, neighbor-4)
- Or keep it not settled.

**Q4. "Quiet enjoyment" words, and rules that bind every resident.** Does either make the landlord answerable for a
neighbor's conduct? The word "quiet" appears nowhere in the stored statutes. The old version gave only the side saying it
can.

- Recommended: not settled, both readings. This is one a case-law search could settle, if you run one. (neighbor-6)
- Or read it one way.

**Q5. A notice clause outside the statute's limits.** Your call on the fee over two months' rent was that it falls away,
since nothing cuts it down. This one differs: 83.47(1) voids a clause only "to the extent that it" takes away what part II
gives, which supports cutting it to the limit.

- Recommended: not settled, both readings, for a clause over 60 days, under 30, or missing the landlord's half. Notice by
  the limit's date meets both, and the tenant is told so. (end-4)
- Or it falls away, matching your fee call.

**Q6. A landlord who says "no renewal" too late under the lease's clause.** The statute does not say what follows.

- Recommended: not settled, both readings. One: the lease still ends on its date, and the landlord owes damages at most.
  The other: the landlord cannot hold the tenant to the end date without that notice. (end-9)
- Or the lease still ends on its date.

**Q7. A late or wrongly dated notice ending a month-to-month tenancy.** It does not work for the date it names. Does it work
for a later period?

- Recommended: not settled, both readings. (end-6)
- Or it is not the required notice, so the landlord must start over.

**Q8. A tenant suing the neighbor.** The old version did not reach this.

- Recommended: not settled whether part II reaches it. One: 83.52(7) is a duty in part II, 83.54 lets any such duty be
  enforced by a suit, and the neighbor is "the aggrieved party" (83.55). The other: 83.55 speaks of a landlord and tenant
  under one agreement. A reader raised this.
- Or say only that a suit against the neighbor is outside the tool.

**Q9. Holding back rent over a neighbor.** The answer is that part II gives no right to do it. But a tenant sued for unpaid
rent "may raise any other defense, whether legal or equitable" (83.60(1)(a)).

- Recommended: say no right, then one line that whether a failed lease promise is such a defense is not settled. The repair
  skill says holding back rent "never" reaches a lease promise, and it stays as it is for now. (neighbor-5)
- Or leave the line out.

**Q10. Not renewing, or ending a tenancy, after a complaint.** 83.64(1) names raising rent, cutting services, and bringing
or threatening a suit. It does not name not renewing.

- Recommended: not settled whether it is covered by itself, and not settled whether staying after the end is "good cause".
  It stays a defense if sued.
- Or say it is not covered until a suit is brought or threatened.

**Q11. A small fix to the repair skill.** Its mistakes list says the statute gives no standard for "good faith". It does:
"“Good faith” means honesty in fact in the conduct or transaction concerned." (83.43(8)). The new skills quote it.

- Recommended: take "good faith" out of that line. No rerun.
- Or leave it.

## What the new versions say that the old ones did not

These are the points for your check. Everything else comes from the old versions.

### Neighbor

- A rule sheet that binds every resident may or may not promise enforcement (two readings), with good faith (83.44).
- A clause saying the landlord is not responsible for other residents, against 83.47(1)(b) (two readings).
- Shared spaces: "The clean and safe condition of common areas." (83.51(2)(a)). Whether that reaches how people behave is
  not settled. It can reach only damages.
- A way to end the lease is written out, with the four conditions. Rent paid gives up nothing until the tenant knew the
  landlord had not acted. A landlord trying but unable to stop it goes to the repair skill's option 5.
- Damages (83.55), with attorney fees both ways (83.48). The 7 days' notice before moving out (83.49(5)).
- Holding back rent: the risk and the 5 days are spelled out.
- Police and the city: outside the tool, and part II requires no report first.
- Retaliation: its parts, and that an ordinary complaint about a neighbor is not named (two readings).

### Rent

- No cap and no notice period, stated plainly. 83.425 is quoted further, through its words on "fees charged by the landlord;
  or notice requirements."
- Rent steps already in the lease are not an increase.
- A clause allowing a raise: its conditions are checked, with dates from `count_days`.
- A new monthly charge is treated like a raise. A fee is rent only if "designated as rent in a written rental agreement"
  (83.43(12)). Trash (83.51(2)(a) and (e)). A fee in place of a deposit "may not be increased during the term" (83.491(4)(a)).
- A higher rent at renewal has its own option: no right to the same rent, and no limit on what a landlord may ask.
- Saying yes without signing (two readings, 83.43(13)). Paying the raise already (two readings, 83.56(5)(a), with "actual
  knowledge").
- Treated as unpaid rent: the 3-day demand, taking partial rent gives up nothing, the three steps if taken after a 3-day
  notice, no lockout, and the motion on the amount as the way to dispute it (83.60(2)).
- Dates: the old version computed none. The new one uses `count_days` for the month-to-month notice and a lease clause's.

### Lease ending

- The tenant's own notice before leaving at the end of a set term is not tied to 83.56(4); the lease says how it goes.
- Dates for a period the lease sets, from `count_days`: the last day, the start of the notification period, and 15 days
  before it. The old version said the tool computes none. Where the notice falls against those dates decides which reading
  it meets.
- The two months' rent limit and the separate addendum do not apply to the charge for a missed notice (83.595(4)(b)). Part II
  sets no number for this charge; a court may limit an unconscionable clause (83.45(1)).
- A clause that renews the lease if no notice is given (two readings).
- A notice clause outside the limits, or missing the landlord's half (Q5).
- How a notice arrives: the same treatment as the 7-day notice skill, including two readings for a text or a portal message.
- The 7 days' notice for anyone leaving before the term ends, and for any tenant with no set end date (83.49(5)).
- Double rent after a tenancy ended by notice: whether it has reached "expiration" is not settled, as in the 7-day notice
  skill.
- No court case, no lockout, and what a lockout costs (83.59(3), 83.67).
- The landlord's late notice (Q6), a late month-to-month notice (Q7), and retaliation (Q10).
- A new owner after a foreclosure (83.5615): 90 days, and a note that the stored text does not show whether the section has
  taken effect. This needs checking.
- If sued: the registry rule in full, and no calendar date for its 5 days.

## The stories at a glance

Every story holds the fact that this is not college housing. The full right answers, with the points and the mistakes that
fail an answer, are in `stories.json`.

### Neighbor (7)

| Story | What happens | A right answer says |
|---|---|---|
| neighbor-1 | Music upstairs, a plain lease | No duty in part II, no deadline, no promise in the lease. Keep complaining in writing, keep a record. |
| neighbor-2 | Lease promises to enforce quiet hours; portal messages only | Not yet. Portal messages are not the notice. "Material" and rent paid are not settled. |
| neighbor-3 | Same lease; a notice by hand; the 7 days ended March 12 | Not settled, on "material" only. The rest is met. What follows each way. |
| neighbor-4 | The house behind the building, another owner | The manager is right: no remedy against them. No right to end the lease. Moving out does not stop the rent. |
| neighbor-5 | Same lease; wants to hold back rent | No right to. The risk and the 5 days. The promise reaches ending the lease and damages. |
| neighbor-6 | Lease promises "peaceful and quiet enjoyment" | Not settled whether that reaches another tenant. Both readings. |
| neighbor-7 | The manager threatens eviction for complaining | Not settled whether an ordinary complaint counts. Good faith, treated differently, a defense if sued. A threat puts no one out. |

### Rent (8)

| Story | What happens | A right answer says |
|---|---|---|
| rent-1 | A raise mid-term, no clause | No. $1,050 stands through July 31. Keep paying. The risk of a demand. |
| rent-2 | Lease allows a raise on 60 days' notice; the letter gives less | Not on April 1. The last day was January 31. |
| rent-3 | Renewal offered at $1,300 | No cap, no right to the same rent. The new rent only if they agree. Their options. |
| rent-4 | Month to month; letter March 20 for April 1 | Not settled, three readings. March 1 was the 30-day date. The landlord may end the tenancy. Their choices, with March 31. |
| rent-5 | A code complaint, then a raise for this tenant only | It can be retaliation; a court decides. A defense if sued. Not paying can weaken it. The raise alone: not settled. |
| rent-6 | Everyone got the same raise, in good time | In time by March 1. Whether a letter alone changes the rent: not settled. The landlord may end the tenancy. Retaliation looks unsupported. |
| rent-7 | Already paid the raise for two months | Not settled, both readings, with "actual knowledge". |
| rent-8 | Kept paying $1,050, now sued | Leads with the 5 days and the motion on the amount, no date. Then the defense. |

### Lease ending (9)

| Story | What happens | A right answer says |
|---|---|---|
| end-1 | Plain lease, leaving on the end date | No notice owed. What section 6 requires at move-out. |
| end-2 | 60-day clause and $2,100; the landlord sent nothing | Not owed. The last day was June 1. |
| end-3 | The reminder handed over May 20 | Not settled what "within 15 days" asks. June 1 and May 17; May 20 falls between. |
| end-4 | A 90-day clause | Over the limit. Not settled what follows. Notice by June 1 meets both. |
| end-5 | Month to month, leaving April 30 | Written notice by March 31. The 7 days' notice by April 23. One notice can do both. |
| end-6 | A text: be out by March 31 | No, not by then; the last day was March 1. The text and a later period: not settled. A court case is needed. |
| end-7 | Staying until August 20 without permission | No lockout. A suit and double rent are possible. Ask in writing. |
| end-8 | The landlord took August's rent, then gave 5 days | Not settled whether that is permission. Five days puts no one out. |
| end-9 | Notice of no renewal on July 10 | Late against June 1. Not settled what follows. The risk of staying. A court case is needed. |

## The test, once you OK this

The same as the last pair: 3 runs a story through the app's own chat on Sonnet, the old version beside the new, graded
blind by Opus. That is 144 answers, about $14 of your API credit, with the results shown as a chart.

The files run about 2,870, 3,030, and 3,710 words, against the plan's 2,500 to 3,000. As with the last pair, I left them long
for the test and will trim whatever the test shows does nothing.

The rent-paid question you are holding for case law (AUTHOR.md item 22) touches three stories: neighbor-2 requires both
readings, and neighbor-5 and neighbor-6 allow them as an optional point. They match the repair skill, and change if that item
does.

## Your answers (2026-11-01)

All recommended. Q1 to Q10 need no change to the drafts. Q11 took "good faith" out of the repair skill's mistakes line.
