---
name: repair_not_made
description: Something in the home needs repair, or something the lease promises is broken or closed, and the landlord has not fixed it.
---
# Repair not made

Rests on 83.51 (repairs), 83.56 (ending the lease, notices, rent paid), 83.60 (holding back rent), 83.55 (damages), 83.64 (retaliation), 83.47 (void lease clauses), and 83.505 (e-mail notices). Read a section in full with get_statute_section.

When the answer turns on a point marked not settled, the first sentence says it is not settled and leans neither way (never "probably yes").

## First, whether this applies

- Load who_the_law_covers, unless the facts already hold school_housing.
- "The landlord is not required to maintain a mobile home or other structure owned by the tenant." (83.51(1)).
- If the landlord has filed an eviction case, see "If the landlord sues" under option 2. Court steps beyond what this skill says are outside this tool.
- If the tenant ended the lease and moved out, load deposit_not_returned for the deposit.

## Whose job the repair is

Ask what broke, in plain words. Never ask whether it is "structural", a "code" matter, or "material".

1. **What 83.51(1) requires.** The landlord must "Comply with the requirements of applicable building, housing, and health codes" (83.51(1)(a)), or, where there are none, "maintain the roofs, windows, doors, floors, steps, porches, exterior walls, foundations, and all other structural components in good repair and capable of resisting normal forces and loads and the plumbing in reasonable working condition" (83.51(1)(b)). Screens: in reasonable condition when the tenancy starts, then damage repaired once a year when needed (83.51(1)).
   - The structure or the plumbing: an 83.51(1) duty.
   - Whether a code covers the problem: outside the tool, since the codes are not stored; the city or county code office can say and inspect.
   - "The landlord's obligations under this subsection may be altered or modified in writing with respect to a single-family home or duplex." (83.51(1)). For a house or duplex, read the lease's repair clause and ask whether they signed anything else about repairs; say what it says. For any other home, the statute gives no such change.
2. **What 83.51(2)(a) adds,** for a home other than a single-family home or duplex, "Unless otherwise agreed in writing" (83.51(2)(a)): "The extermination of rats, mice, roaches, ants, wood-destroying organisms, and bedbugs." (83.51(2)(a)); locks and keys; clean and safe common areas; garbage removal; and "Functioning facilities for heat during winter, running water, and hot water." (83.51(2)(a)).
   - These are not a defense to eviction: "Nothing in this part authorizes the tenant to raise a noncompliance by the landlord with this subsection as a defense to an action for possession under s. 83.59" (83.51(2)(c)). 83.56(1) and 83.60(1)(b) speak only of 83.51(1), so an item only (2) names reaches option 1 only if a code or the lease also covers it, and option 2 only if a code does.
   - Pest treatment: "If the tenant must vacate the premises for such extermination, the landlord is not liable for damages but must abate the rent." (83.51(2)(a)). The landlord gives 7 days' written notice when the tenant must leave for it, and the tenant need leave for at most 4 days (83.51(2)(a)).
   - Running water and hot water: not settled which list holds them. The plumbing is in 83.51(1)(b), and (2)(a) names them too. "If the duty imposed by subsection (1) is the same or greater than any duty imposed by subsection (2), the landlord's duty is determined by subsection (1)." (83.51(3)). Give both readings and choose neither. One: the failure is in the plumbing, so it is an 83.51(1) duty and options 1 and 2 reach it. The other: (2)(a) names it, so it is a (2) duty, which 83.51(2)(c) keeps out of a defense to eviction. Heat is named only in (2)(a), so it is a (2) duty unless a code or the lease covers it.
3. **What the lease adds.** Anything the lease says comes with the home, or that the landlord will keep up, counts, whatever it is and whether or not this skill names it. Read the whole lease for the broken or closed item: whether the lease promises it, who repairs it, any clause on closing it, and any fee for it. Quote the clause and cite its section.
   - The lease promises the item, or says the landlord repairs it: a lease duty. Options 1, 3, and 4 can reach it. Option 2 never does, since it rests on 83.51(1) alone. Say so plainly when the tenant asks about holding back rent.
   - An item neither of 83.51's lists names is the landlord's job only if the lease says so or a local code requires it (outside the tool). Never say 83.51 requires it. Air conditioning is a common one.
   - Two examples of the handling, not a list. A dishwasher the lease provides breaks: 83.51 does not name it, so it is a lease promise; ending the lease may reach it (material is not settled), holding back rent does not, damages may. A pool the lease lets the landlord close for cleaning stays closed a month: read that clause first; whether it limits the promise is the open question below.
   - The lease puts a repair on the tenant, or says an item may be closed or is offered only as a courtesy: say what it says. For a house or duplex, a writing may change the 83.51(1) duty (above). For an item only 83.51(2)(a) names, a writing may change it in any home, since the paragraph applies "Unless otherwise agreed in writing" (83.51(2)(a)). Otherwise, a clause is void "to the extent that it" (83.47(1)) does either of two things: "Purports to waive or preclude the rights, remedies, or requirements set forth in this part." (83.47(1)(a)) or limits a party's liability under law (83.47(1)(b)). Whether a clause that limits an amenity itself (its hours, its closures) is such a clause is not settled. Give both readings and choose neither. One: it only says what the lease promises, so it stands, and the promise is what it describes. The other: it takes away a right part II gives (ending the lease under 83.56(1), damages under 83.55), so it is void to that extent.
4. **Who caused it.** "The landlord is not responsible to the tenant under this section for conditions created or caused by the negligent or wrongful act or omission of the tenant, a member of the tenant's family, or other person on the premises with the tenant's consent." (83.51(4)).
   - Nothing anyone did (age, wear, weather), the landlord or its workers, or someone the tenant did not let in: the landlord's, as far as 83.51(4) goes.
   - The tenant, a family member, or a guest they let in: not the landlord's under 83.51. Say so in one sentence, and say what the lease says about who pays.
   - A roommate: not settled. Give both readings and choose neither, and ask how the roommate came to live there. One: a roommate sharing the home is there with the tenant's consent, so 83.51(4) applies. The other: a roommate the landlord placed under a lease of their own is there by the landlord's leave, so 83.51(4) does not reach what they caused.
   - The tenant does not know: a work order, a repair person's note, or the landlord's messages may show it.

## Facts the answer turns on

Read the lease first. Ask the tenant only plain facts, one or two at a time. Note each fact with note_fact under these names, dates written YYYY-MM-DD; a date counts only once the tenant has confirmed it.

- problem: what broke, in the tenant's words, and which part of the home.
- problem_noticed_date: when they first noticed it.
- home_type: a single-family house, a duplex, or a unit in a larger building.
- cause: who or what caused it, as far as they know.
- repair_notice_delivered: the date a written notice saying they will end the lease over the problem reached the landlord. Also note how it went (handed over, mailed, e-mail, portal, text) and what it says about ending the lease.
- withhold_notice_delivered: the date a written notice saying they will not pay rent over the problem reached the landlord, and who received it.
- rent_paid_since: whether they paid rent after they knew of the problem.
- eviction_filed: whether the landlord has filed an eviction case.
- code_complaint_date: the date they complained to a code office, if they did.

A notice counts from the day it reached the landlord, not the day it was sent. If the tenant gives only the day it was sent, ask when it arrived (the day it was handed over, or a mail receipt). The exception is e-mail under 83.505: "A notice sent electronically pursuant to this section is deemed delivered at the time it is sent, unless the e-mail is returned to the sender as undeliverable." (83.505(4)).

## Option 1: end the lease

The rule: "If the landlord materially fails to comply with s. 83.51 (1) or material provisions of the rental agreement within 7 days after delivery of written notice by the tenant specifying the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof, the tenant may terminate the rental agreement." (83.56(1)).

All four conditions must be met. Settle each one from the facts: met, not met, the tenant can tell us, not settled, or outside the tool.

1. **A duty the landlord failed.** An 83.51(1) duty, or a material provision of the lease (see "Whose job the repair is"). Whether the failure is "material" (83.56(1)) is not settled: the stored text does not define the word. Give both readings and choose neither, setting the tenant's facts beside the word. One: any failure of a duty 83.51(1) lists, or of a lease promise, is material. The other: it turns on how serious the problem is, how long it has lasted, and how it affects living there.
2. **A written notice, delivered a way the statute names, that names the problem and says they will end the lease.** "The delivery of the written notices required by subsections (1)-(3) shall be by mailing, delivering a true copy thereof, e-mailing in accordance with s. 83.505" (83.56(4)). A lease cannot waive these notice rules (83.56(4)).
   - Handed to the landlord or the office, or mailed: delivered.
   - E-mail: only if all of 83.505(1)'s conditions are met, "if the parties have signed an addendum to the rental agreement that the parties specifically agree to the electronic delivery of notices and have each provided a valid e-mail address for such purpose, and the addendum conspicuously advises the parties that such election is voluntary and that they may revoke such agreement or update their e-mail addresses at any time." (83.505(1)). Read the lease for such an addendum and say what it shows.
   - A portal message or a text: not one of the ways 83.56(4) names; sending it again by hand or by mail meets the rule.
   - The words: set the tenant's notice beside the statute's. A message that asks for a repair but does not say they will end the lease is not this notice. Say so in one sentence.
3. **Seven days passed without the repair.** Call count_days(repair_notice_delivered, 7). If the date has not passed, the landlord still has time; give the date.
4. **Not given up by paying rent.** If "the tenant pays rent with actual knowledge of a noncompliance by the landlord" (83.56(5)(a)), the tenant "waives his or her right to terminate the rental agreement or to bring a civil action for that noncompliance, but not for any subsequent or continuing noncompliance." (83.56(5)(a)).
   - No rent paid since they knew of the problem: met.
   - Rent paid while the problem goes on: not settled. Give both readings and choose neither. One: a problem still not fixed is a "continuing noncompliance" (83.56(5)(a)), so paying rent gives up nothing. The other: paying rent with knowledge gives up ending the lease over that failure, and only a new failure starts over.

If all four are met, say plainly that the tenant may end the lease (83.56(1)).

## Option 2: hold back rent, and raise the problem if sued

Say first, in plain words, that holding back rent risks an eviction case, and what the tenant must do if sued (below).

The rule: "The defense of a material noncompliance with s. 83.51 (1) may be raised by the tenant if 7 days have elapsed after the delivery of written notice by the tenant to the landlord, specifying the noncompliance and indicating the intention of the tenant not to pay rent by reason thereof." (83.60(1)(b)). What it gives: "A material noncompliance with s. 83.51 (1) by the landlord is a complete defense to an action for possession based upon nonpayment of rent" (83.60(1)(b)), and the court decides how much, if any, the rent is reduced for that time (83.60(1)(b)).

All four conditions must be met.

1. **An 83.51(1) duty, and only that.** Never an item only the lease promises, whatever it is, and never an item only 83.51(2) names. For running and hot water, give the two readings above. Whether the failure is material is not settled, as in option 1.
2. **The written notice.** It names the problem and says they will not pay rent because of it. It may go to the landlord, its designated representative, a resident manager, or whoever collects the rent (83.60(1)(b)). How it must be delivered is not settled, since 83.60(1)(b) names no way. Give both readings and choose neither. One: a written notice that reaches one of those people counts however it was sent, e-mail and portal included. The other: part II's ways for notices apply (83.56(4)), so e-mail counts only under the 83.505 addendum, and a portal message or a text does not. Handing it over or mailing it meets both readings; say so.
3. **Seven days passed.** Call count_days(withhold_notice_delivered, 7).
4. **The tenant's side did not cause it** (see "Who caused it").

If the landlord sues: "the tenant shall pay into the registry of the court the accrued rent as alleged in the complaint or as determined by the court and the rent that accrues during the pendency of the proceeding, when due." (83.60(2)). "Failure of the tenant to pay the rent into the registry of the court or to file a motion to determine the amount of rent to be paid into the registry within 5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process constitutes an absolute waiver of the tenant's defenses other than payment" (83.60(2)). Paying, or filing that motion, in time keeps the defenses. "The clerk shall notify the tenant of such requirement in the summons." (83.60(2)). This tool does not count those 5 days. Never give a date for them; say the summons states the requirement.

## Option 3: damages

"If either the landlord or the tenant fails to comply with the requirements of the rental agreement or this part, the aggrieved party may recover the damages caused by the noncompliance." (83.55). It reaches 83.51 duties and lease promises alike, with no notice named. Rent paid with knowledge may give up the right "to bring a civil action for that noncompliance" (83.56(5)(a)) too; give option 1's two readings. How much, and how to bring the claim in court, is outside this tool.

## Option 4: a code complaint, and protection from retaliation

A code office can inspect (outside the tool; see "Whose job the repair is"). The protection: "It is unlawful for a landlord to discriminatorily increase a tenant's rent or decrease services to a tenant, or to bring or threaten to bring an action for possession or other civil action, primarily because the landlord is retaliating against the tenant." (83.64(1)). Its examples include a complaint to a code agency (83.64(1)(a)) and a repair notice under 83.56(1) (83.64(1)(c)).

- The tenant must have acted in good faith (83.64(1)).
- Being treated differently from other tenants, in rent, services, or action taken, is required (83.64(4)).
- It is a defense in an action for possession (83.64(2)).
- Not when the landlord shows good cause: "In any event, this section does not apply if the landlord proves that the eviction is for good cause." (83.64(3)). Its examples include "good faith actions for nonpayment of rent" (83.64(3)), so for a tenant sued over rent they held back, option 2 is the defense to look at.
- Whether the landlord acted primarily to retaliate is for a court. Give the dates of the complaint and of the landlord's act as the tenant gave them; never count the days between them.

## Option 5: when the landlord is trying but cannot fix it

When the failure of an 83.51(1) duty or a material lease provision is due to causes beyond the landlord's control, and the landlord has made and keeps making every reasonable effort to fix it, the lease "may be terminated or altered by the parties, as follows:" (83.56(1)). "If the landlord's failure to comply renders the dwelling unit untenantable and the tenant vacates, the tenant shall not be liable for rent during the period the dwelling unit remains uninhabitable." (83.56(1)(a)). "If the landlord's failure to comply does not render the dwelling unit untenantable and the tenant remains in occupancy, the rent for the period of noncompliance shall be reduced by an amount in proportion to the loss of rental value caused by the noncompliance." (83.56(1)(b)).

- Whether the cause is beyond the landlord's control, and whether it keeps making every reasonable effort: ask what the landlord has said and done about the problem. The stored text does not define "untenantable" (83.56(1)(a)); set the tenant's facts beside the word.
- "terminated or altered by the parties" (83.56(1)): not settled. Give both readings and choose neither. One: both sides must agree to end or change the lease, and (a) and (b) set what follows. The other: (a) and (b) apply once their facts are met, so a tenant who leaves an untenantable home owes no rent for that time, and one who stays owes reduced rent.

## Mistakes to avoid

- Treating any written complaint as the notice in 83.56(1) or 83.60(1)(b). Each must say what the tenant will do: end the lease, or not pay rent.
- Saying the tenant may hold back rent over an item only the lease or 83.51(2) names.
- Saying 83.51 requires an item its lists do not name, such as air conditioning.
- Writing any date that count_days did not give you, counting the days between two dates, or counting a 7-day period from the day a notice was sent instead of delivered (except an e-mail under 83.505).
- Explaining holding back rent without its risk and 83.60(2), or giving a date for its 5 days.
- Stating a standard for "material", "untenantable", or "good faith" that the statute does not give.
- Leaving out 83.56(5)(a) when the tenant paid rent after knowing of the problem.
- Treating damage the tenant, their family, or a guest caused as the landlord's under 83.51.
