# Leaving early and the 7-day notice: what needs your OK

The next pair of instructions for the chatbot is drafted, with test stories and their right answers. Nothing has been
sent to a model yet. Your OK comes first: the test grades against these answers.

- The instructions: `skills/wants_to_leave_early.md` and `skills/notice_received_violation.md`.
- The stories: `stories.json` in `wants_to_leave_early/` and `notice_received_violation/`, in this folder.
- Every statute quote passed the word-for-word check. Two independent readers then went through each draft against the
  stored statutes, and their fixes are in.

## Questions

Reply "all recommended" to accept every first choice. The first three matter most.

**Q1. A violation that is still going on, and the landlord keeps taking rent.** The statute says taking rent with
knowledge gives up the right to end the lease over that violation, "but not for any subsequent or continuing
noncompliance." (83.56(5)(a)). Take a dog still in the apartment.

- Recommended: say it plainly. A dog still there is continuing, so taking rent gave up nothing. The words point one way,
  and the other reading leaves "continuing" with no job to do. This also changes the repair skill, which reads the same
  sentence from the tenant's side, and three of its stories (2, 3, and 9), since you approved "not settled" there.
- Or keep it as drafted, matching the repair skill: not settled, both readings (story notice-6).

**Q2. The 12 months.** A repeat within 12 months of a written warning loses the chance to fix it. The tool counts days,
so the draft says "check these two dates on a calendar", which reads badly when the dates are January and March.

- Recommended: count_days(earlier_warning_date, 365). No code changes. It can be off by a day around a leap year, so the
  skill would say to call anything that close too close to tell.
- Or keep the draft: give both dates, and the tenant checks.
- Or change the code so the tool can count months. That is the most exact, and it is the only choice here that touches
  app code.

**Q3. Comparing a date with a deadline.** Rule 7 says the model never compares dates. But "you fixed it March 12, and the
last day was March 16" is a comparison, and the deposit skill already asks for one.

- Recommended: allow it only for a date in the facts against a date count_days gave. No rule change; the skills say so.
- Or follow rule 7 to the letter: give both dates and let the tenant compare.

**Q4. A fee after military orders (leave-5).** A servicemember "is not liable for any other rent or damages due to the
early termination" (83.682(4)). A fee is not named.

- Recommended: not settled, both readings.
- Or read it as barred, since no agreement can change this section (83.682(5)).

**Q5. A charge only in the body of the lease (leave-3).** The fee is "available only if" (83.595(4)) the tenant signed a
separate addendum.

- Recommended: say plainly the charge cannot be made that way, and that losing the deposit counts the same.
- Or not settled.

**Q6. A fee over two months' rent (leave-4).**

- Recommended: not settled whether it falls away or is cut to the limit. The text does not say.
- Or read it as falling away, since the remedy is "available only if" its conditions are met.

**Q7. A lease-over notice for something on the fix list, with no earlier warning (notice-2).**

- Recommended: say plainly the notice does not fit and the tenant should have had 7 days. Whether that ends a court case
  is for the court.
- Or not settled, since the lists are only examples.

**Q8. A text message as a notice (notice-7).** This is the same kind of call as open item 4 on the decision list, which
asks about a text as the deposit notice.

- Recommended: not settled, both readings, and moving the car within 7 days meets both.
- Or a text does not count. Then item 4 should change too.

**Q9. Moving out after the landlord ended the lease (notice-9).** Does the tenant still owe rent through the lease's end?

- Recommended: not settled, both readings. Ending the lease may be the choice that ends "any further liability"
  (83.595(1)), or the landlord may keep all its choices.
- Or the landlord keeps its choices.

**Q10. Two small fixes to the repair skill.** It says being treated differently "from other tenants" is required for
retaliation; those three words are not in 83.64(4). Its opening list of sections also leaves out 83.48 and 83.59, which
it relies on.

- Recommended: make both. No rerun.
- Or leave it.

## What the new versions say that the old ones did not

These are the points for your check. Everything else comes from the old versions.

### Leaving early

- When no way out fits, the law names no right to end a lease with a set end date just because the tenant wants to move.
  This is drawn from the statute's silence, so please read it closely.
- Any set charge for leaving early is a fee or liquidated damages, whatever the lease calls it, including losing the
  deposit (83.43(6)). It needs the separate signed addendum.
- A clause making all the remaining rent due at once: not settled.
- With a fee, the tenant also owes rent and charges through the end of the month the landlord retakes the home, and any
  damage charges (83.595(4)(a)). The statute's form has the landlord give up rent beyond that month. An addendum without
  those words: not settled.
- Military: the six grounds are listed for the chatbot to apply, not left to the tenant. New too: rent prorated to the
  end date, no other rent or damages, nothing owed if ended 14 or more days before moving in, the family member's right,
  and protection from retaliation.
- Damage to the home (83.63) is written out as an option. The old version only pointed to it. New readings: whether a
  slow leak or mold counts, and whether someone leaving at once still needs the 7 days' notice.
- Flooding with no flood disclosure (83.512) is new: a lease of a year or longer, a loss of at least half the value of
  the belongings, and written notice and moving out within 30 days. The stored text does not say when the section began.
- A deal with the landlord is not a fee (83.43(6)). A "buyout" clause already in the lease: not settled.
- The deposit can go toward the landlord's loss, but only through the deposit steps (83.43(14)).
- When a tenant counts as having abandoned the home (83.59(3)(c)), belongings left behind (83.67(5)), and interest
  (83.49(9)).
- Month to month is not leaving early (83.57). A tenant who stayed on after a set term and leaves without the notice can
  owe a month's rent (83.575(3)). For a tenancy month to month from the start: not settled.

### The 7-day notice

- The notice alone does not put anyone out. The landlord needs a court case and may not lock the tenant out (83.59(3),
  83.67(2)), and a lockout has a price (83.67(6)).
- A letter that only warns starts no count, but can count later as the written warning.
- How the notice came, for the first time: the ways the statute names (83.56(4)); a copy at the door counts only if the
  tenant is away; e-mail counts from when it was sent; for mail or a door copy, both dates; for a text or portal message,
  two readings.
- Flaws: no violation at all, the wrong kind of notice, or missing words. Whether conduct on one of the statute's lists
  is also "material" is not settled. A notice that does not say what the tenant did is not the required notice, the
  same call you made for a deposit notice with no reason. Missing form words get two
  readings, as they do for the deposit. The sentence that lets a landlord fix a flawed notice (83.60(1)(a)) sits in a
  paragraph about unpaid rent, so whether it reaches this case is not settled.
- Taking part of a month's rent gives up nothing, and the subsidized-rent rule has its own 45 days (83.56(5)).
- Retaliation (83.64), with its limit: good faith actions over a violation are good cause.
- Staying: court costs and fees, and double rent (83.58), where "expiration" gets two readings.
- A fix made after the 7 days: not settled whether it helps, since the rule and the form use different words.
- The court registry rule is spelled out, and the 5 days are never given as a date. The old version only pointed to it.
- Moving out: rent may still be owed (83.595), the deposit rules apply (83.56(6)), and the 7 days' notice before leaving.
- A landlord may also ask a court for an order over intentional damage (83.681).

## The stories at a glance

Every story holds the fact that this is not college housing, so the chatbot does not need to ask. The full right answers,
with the points and the mistakes that fail an answer, are in `stories.json`.

### Leaving early (8)

| Story | What happens | A right answer says |
|---|---|---|
| leave-1 | New job, plain lease. "Can I just give notice?" | No such right. Landlord's three choices, no total. The 7 days' notice by March 24, and it does not stop the rent. |
| leave-2 | A signed addendum, $2,100, 30 days' notice | The fee is open. It costs the fee plus rent through the month the landlord retakes the home. Notice by May 1. |
| leave-3 | $1,500 charge and loss of deposit, only in the lease | Cannot be charged that way, but leaving is not free. The deposit goes through its own steps. |
| leave-4 | A signed addendum, $3,000 | Above the limit. Not settled what follows, both readings. |
| leave-5 | Military orders; the office wants the fee and rent through July | Lease can end. Prorated rent only. Earliest date May 6. The fee: not settled. |
| leave-6 | A leak; portal requests only | Needs a written notice first. Portal requests are not it. Two points not settled. Otherwise the landlord's choices. |
| leave-7 | A fire next door | May end the lease at once, or leave the ruined part and pay less. No test for "substantially impaired". |
| leave-8 | A flood, no flood paper | May end the lease with written notice and moving out by July 20. Refund of rent paid ahead. |

### The 7-day notice (9)

| Story | What happens | A right answer says |
|---|---|---|
| notice-1 | Dog; 7 days to fix; dated March 2, handed over March 9 | Need not move if fixed by March 16, counted from delivery. If it recurs within 12 months, no new notice. |
| notice-2 | Guest; lease over; no earlier warning | The wrong kind of notice, but do not ignore it. A court case is needed. |
| notice-3 | A first noise complaint; lease over | Not settled, both readings. A court case is needed. |
| notice-4 | A second loud party after a written warning | No right to fix. Both dates set beside the 12 months. |
| notice-5 | One event, then the landlord took all of April's rent | The landlord gave up ending the lease over that event, not for anything new. |
| notice-6 | Dog still there; rent taken for months | Depends on Q1. Fixing it by March 16 is safe either way. |
| notice-7 | A text about parking | Not settled whether a text counts. Moving the car by February 23 meets both. |
| notice-8 | Sued; served yesterday | Lead with the registry rule and what missing it costs. No date for the 5 days. |
| notice-9 | Leaving within the 7 days | Not settled whether rent through July is owed. The deposit rules. The 7 days' notice is due today. |

## The test, once you OK this

The same as the repair test: 3 runs a story through the app's own chat on Sonnet, the old version beside the new, graded
blind by Opus. That is 102 answers, about $10 of your API credit, with the results shown as a chart.

Both new files are longer than planned: about 3,700 and 3,400 words, against 2,500 to 3,000. I left them long for the
test and will trim whatever the test shows does nothing.
