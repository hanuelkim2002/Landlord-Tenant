---
name: lease_ending
description: The lease or tenancy is reaching its end: notice to leave or renew, a charge for missing that notice, a landlord who will not renew or is ending a month-to-month tenancy, or staying on after the end.
---
# Lease ending

Rests on 83.575 (a set end date), 83.57 and 83.46 (no set end date), 83.58, 83.59, and 83.67 (staying on, no lockout), 83.56 and 83.505 (delivering notices), 83.49 (the 7 days' notice, the deposit), 83.595 and 83.45 (limits on charges), 83.43 and 83.64 (good faith, retaliation), 83.60 (if sued), 83.47, 83.55, and 83.48 (void clauses, damages, attorney fees), and 83.5615 (foreclosure). Read a section in full with get_statute_section.

When the answer turns on a point marked not settled, the first sentence says it is not settled and leans neither way (never "probably yes"). Every point marked not settled gets both readings, and you choose neither. When the tenant asks "can I" and the answer turns on such a point, write "You can if X, and X is not settled", never a plain yes.

## First, whether this applies

- Load who_the_law_covers, unless the facts already hold school_housing.
- The tenant wants to move out well before the end date: load wants_to_leave_early.
- The landlord's notice names something the tenant did: load notice_received_violation.
- A higher rent comes with the renewal: load rent_increased too.
- After the move, the deposit: load deposit_not_returned.
- A new owner after a foreclosure says to leave: 83.5615 calls for a notice "at least 90 days before the effective date of the notice" (83.5615(2)(a)) and protects a bona fide lease's remaining term, with limits (83.5615(2)(b)). Its note says it takes effect upon the repeal of a federal act, and the stored text does not say whether that has happened; say this needs checking.

## What the lease adds

Read the whole lease, addenda included, for: the end date; any notice before leaving at the end; any notice from the landlord; any charge for missing a notice; renewal; staying after the end; how notices go; and what move-out requires. Quote each clause and cite it.

A clause that renews the lease if no notice is given: say what it says. Whether option 1's conditions for a charge reach it is not settled. One: it is a way of charging for a missed notice, so the landlord's own notice is needed first. The other: a renewal is not a charge, and 83.575(2) speaks only of liquidated damages, so the clause stands.

## Facts the answer turns on

Read the lease first. Ask the tenant only plain facts, one or two at a time. Note each fact with note_fact under these names, dates written YYYY-MM-DD; a date counts only once the tenant has confirmed it.

- lease_end_date: the date a set term ends. period_end: with no set end date, the last day of the rent period they ask about. next_period_end: the last day of the rent period after that.
- planned_move_out: the date they plan to leave.
- tenant_notice_delivered: the date their notice reached the landlord, and how it went.
- landlord_notice_delivered: the date a paper from the landlord about the end reached them, how it came, and what it lists. If mailed or left at the door, landlord_notice_sent: the date it was mailed or left.
- permission: what the landlord has said or done about their staying, and whether it is in writing. rent_after_end: any rent paid or taken for a time after the end.
- eviction_filed: whether a case has been filed, and whether they were served. complaint_date: the date of any complaint before the landlord acted, and what it was.

## Which kind of tenancy

- **A set end date:** 83.575. Options 1 to 3, and "When the landlord will not renew".
- **No set end date:** 83.57. "If the rental agreement contains no provision as to duration of the tenancy, the duration is determined by the periods for which the rent is payable." (83.46(2)). A home that comes with a job goes by the pay periods (83.46(3)). Option 4, and "When the landlord ends a tenancy with no set end date".
- **Stayed on with permission after a set term:** read the lease's clause on staying. With none, 83.575(3) points to the 83.57(3) notice; see option 2.

Part II names no right to renew.

## How a notice is delivered

This covers a landlord's notice under 83.575, and either side's notice under 83.57. A tenant's own notice before leaving at the end of a set term goes as the lease says; 83.575(1) names no way for it. The ways: "The delivery of the written notices required by subsections (1)-(3) shall be by mailing, delivering a true copy thereof, e-mailing in accordance with s. 83.505 , or, if the tenant is absent from the premises, by leaving a copy thereof at the residence." (83.56(4)).

- **Handed over:** delivered that day.
- **Mailed, or left at the door while the tenant was away:** a way the statute names, but not settled which day counts. One: the mailing or the leaving is the delivery. The other: a paper is delivered when it reaches the person. For a landlord's notice, set both landlord_notice_sent and landlord_notice_delivered beside the date. For the tenant's own notice, handing it over or mailing it early meets both.
- **E-mail under the signed addendum:** only with every condition of 83.505(1); then it is "deemed delivered at the time it is sent, unless the e-mail is returned to the sender as undeliverable." (83.505(4)).
- **A text, a portal message, an e-mail with no addendum, or a copy left at the door while the tenant was home:** not a way 83.56(4) names. Not settled whether it still counts because it reached the person. One: delivery "shall be by" (83.56(4)) the ways named, so it is not the required notice. The other: "This section does not preclude service of notices by any other means permitted by law." (83.505(6)). If there is still time, sending it again by hand or by mail meets both.
- **Spoken:** the statute asks for a written notice in these cases. No notice has been given.

A lease clause on notices adds to this: a way that meets both the clause and the statute is safest. Say what the clause says.

## Option 1: leave at the end of a set term

1. **Does the lease ask for notice?** The lease "may contain a provision requiring the tenant to notify the landlord within a specified period before vacating the premises at the end of the rental agreement" (83.575(1)). No such clause: the stored text asks for no notice before leaving on the end date. Say so plainly.
2. **Is the clause one the statute allows?** Two limits, each with its own question. Say what is not settled, and that notice by the date given meets both readings.
   - The length: "A rental agreement may not require less than 30 days’ notice or more than 60 days’ notice from either the tenant or the landlord." (83.575(1)). A clause outside it: not settled what follows. One: the statute does not rewrite such a clause, so no notice is owed under it. The other: a clause is void only "to the extent that it" (83.47(1)) takes away what part II gives, so it stands at the limit. Over 60 days: the date is count_days(lease_end_date, -60). Under 30 days: count_days(lease_end_date, -30).
   - The landlord's half: the clause must also require "the landlord to notify the tenant in a manner prescribed by s. 83.56 (4) within such notice period if the rental agreement will not be renewed." (83.575(1)). A clause without it: not settled what follows. One: the statute allows the clause only "if such provision also requires" (83.575(1)) that, so no notice is owed under it. The other: the statute does not say the tenant's promise falls away, so it still binds. The date is the lease's own.
3. **The last day.** If the clause gives a number of days N: count_days(lease_end_date, -N). If it is in months, give the lease's words; the tool counts days only.

Leaving before the last day of the term: "Except when otherwise provided by the terms of a written rental agreement" (83.49(5)), a tenant leaving "before the expiration of the term specified in the rental agreement" (83.49(5)) gives the 7 days' notice: count_days(planned_move_out, -7), with planned_move_out the day they will actually leave (if they name no earlier day, give no date), in writing, by certified mail or personal delivery, with an address where the tenant can be reached (83.49(5)). Read the lease for a clause on notice before leaving. Rent through the end date is still owed under the lease.

**What missing the notice costs.** A lease "may provide that if a tenant fails to give the required notice before vacating the premises at the end of the rental agreement, the tenant may be liable for liquidated damages as specified in the rental agreement" (83.575(2)). All of these must be met for that charge:

1. **The tenant missed a required notice.** They gave it in time, or the clause falls under step 2's limits: say so, with step 2's readings.
2. **The lease sets the charge.** No charge in the lease: this part does not apply.
3. **The landlord sent its own written notice first,** "specifying the tenant’s obligations under the notification provision contained in the rental agreement and the date the rental agreement is terminated." (83.575(2)), and it "must list all fees, penalties, and other charges applicable to the tenant under this subsection." (83.575(2)). No such notice, or one that leaves any of these out: not met, and the charge is not owed. Say so plainly.
4. **Delivered a way the statute names** (see "How a notice is delivered").
5. **In time.** "within 15 days before the start of the notification period contained in the rental agreement." (83.575(2)). The start: count_days(lease_end_date, -N). Fifteen days before it: count_days(lease_end_date, -(N+15)); pass the sum as one number. What the words ask is not settled. One: the notice must come during the 15 days that end when the period starts, not earlier. The other: it must come no later than 15 days before the period starts, and earlier is also in time. Set the date it came beside both dates:
   - Exactly on the earlier date: in time under both. Say so plainly.
   - Between the two dates: in time under the first reading, too late under the second.
   - Before the earlier date: too early under the first reading, in time under the second.
   - After the start: too late under both, and the charge is not owed. Say so plainly.

The limit on fees for leaving early does not apply here: 83.595(4) "does not apply if the breach is failure to give notice as provided in s. 83.575 ." (83.595(4)(b)). Do not apply its two months' rent limit or its separate addendum to this charge. Part II sets no number for this charge; a court may refuse or limit an "unconscionable" (83.45(1)) clause, and that is for a court. Apart from this charge, a landlord may claim damages for a failure to follow the lease (83.55); amounts are outside this tool.

Moving out: read what the lease requires. Any claim on the deposit goes through the deposit steps; load deposit_not_returned after the move.

## Option 2: stay on with the landlord's agreement

A new lease or a written agreement says what the rent and the term are. Read the lease's clause on staying and what it requires. "If the tenant remains on the premises with the permission of the landlord after the rental agreement has terminated and fails to give notice required under s. 83.57 (3), the tenant is liable to the landlord for an additional 1 month’s rent." (83.575(3)). So a tenant who stays with permission gives option 4's notice when they leave. Say so. Asking the landlord for its answer in writing settles what permission there is.

## Option 3: stay without permission

Say the risk plainly. A tenant who "holds over and continues in possession of the dwelling unit or any part thereof after the expiration of the rental agreement without the permission of the landlord" (83.58) can be sued for possession (83.58), and "The landlord may also recover double the amount of rent due on the dwelling unit, or any part thereof, for the period during which the tenant refuses to surrender possession." (83.58). Do not total it. For a tenancy ended by a notice under 83.57, whether it has reached its "expiration" (83.58) is not settled. One: a tenancy ended by proper notice has expired, so double rent can apply. The other: expiration means the end of a term, and 83.57 speaks of a tenancy "terminated" (83.57).

But the end date does not put them out by itself: "The landlord shall not recover possession of a dwelling unit except:" (83.59(3)) through a court case, or when the tenant gave up or abandoned the home (83.59(3)). The landlord "shall not prevent the tenant from gaining reasonable access to the dwelling unit by any means" (83.67(2)), changing the locks included, and if it does or cuts a utility it is liable for "actual and consequential damages or 3 months’ rent, whichever is greater, and costs, including attorney’s fees." (83.67(6)).

What counts as permission, when the landlord said nothing or took rent for a time after the end, is not settled. One: taking rent for that time is permission, since a landlord that "accepts rent with actual knowledge of a noncompliance by the tenant" (83.56(5)(a)) gives up acting on it. Then 83.58 does not apply, and 83.575(3) and option 4's notice do. The other: permission must be given, and taking rent alone does not change a tenant who holds over, since the same sentence leaves open "any subsequent or continuing noncompliance." (83.56(5)(a)). Set what the landlord did and any lease clause on consent beside both. The landlord's answer in writing settles it either way.

## Option 4: end a tenancy with no set end date

"A tenancy without a specific duration, as defined in s. 83.46 (2) or (3), may be terminated by either party giving written notice in the manner provided in s. 83.56 (4)" (83.57). No reason is named. The notice, by rent period: year to year, 60 days before the end of the year's period (83.57(1)); quarter to quarter, 30 days (83.57(2)); month to month, "not less than 30 days’ notice prior to the end of any monthly period" (83.57(3)); week to week, 7 days (83.57(4)).

1. **The last day.** Month to month: count_days(period_end, -30). If that has passed, the tenant can give notice for the next period instead: count_days(next_period_end, -30). Say "the next rent period" with no date unless next_period_end is a confirmed fact. Whether a notice that came too late for the end it names still works for a later period is not settled; give the two readings under "When the landlord ends a tenancy with no set end date". For another rent period, use its number of days.
2. **Written, and delivered a way the statute names** (see "How a notice is delivered").
3. **The 7 days' notice too.** "Except when otherwise provided by the terms of a written rental agreement" (83.49(5)), it also applies to "any tenant who vacates or abandons premises which are the subject of a tenancy from week to week, month to month, quarter to quarter, or year to year" (83.49(5)). It must be written, by certified mail or personal delivery, with an address, at least 7 days before leaving: count_days(planned_move_out, -7). Read the lease for a clause on notice before leaving. One notice by hand or certified mail, with the address, in time for both, meets both. Missing it frees the landlord from its deposit notice but gives up no right to the deposit (83.49(5)).

A tenant who stayed on with permission after a set term and misses the 83.57(3) notice owes the extra month's rent (83.575(3)). For a tenancy that was month to month from the start, that is not settled. One: (3) names the month-to-month notice, so it applies. The other: the section is about a tenancy "with specific duration" (83.575), so it does not.

## When the landlord will not renew

The tenant has a set end date and the landlord says it will not renew. Part II names no reason it must give.

- **The lease has a notice clause with the landlord's half.** The last day for the landlord: count_days(lease_end_date, -N). If the clause is outside the limit, set the notice beside the lease's date and the limit's, as in option 1. If it is in months, give the lease's words. In a named way, on or before the last day: met, and the lease ends on its date. Say so plainly. Late, or not in a named way: what follows is not settled. One: the lease still ends on its date by its own words, and the landlord's miss is a failure of the lease, for damages at most (83.55). The other: the clause makes the landlord's notice the way a lease is not renewed, so without it the landlord cannot hold the tenant to the end date. Say what the lease says about renewal.
- **The lease has no such clause.** The stored text asks for no notice from the landlord before a set term ends. Say so plainly.
- Either way, see option 3 for staying, and "After a complaint" below.

## When the landlord ends a tenancy with no set end date

Set the landlord's notice beside option 4's rule. Month to month: count_days(period_end, -30), with period_end the last day of the rent period holding the date the notice names. If it was mailed or left at the door, use both dates, as "How a notice is delivered" says.

- **Written, in a named way, on or before that date:** met, and the tenancy ends at period_end. Say so plainly, and go to option 3 for staying.
- **Too late for that period, or naming a date that is not the end of a rent period:** it does not meet the rule for that date. Say so plainly. Whether it works for a later period is not settled. One: it is still written notice, so if it came by count_days(next_period_end, -30) the tenancy can end at next_period_end. The other: it names an end the statute does not allow, so it is not the required notice, and the landlord must give a new one.
- **By text, by portal, or spoken:** see "How a notice is delivered".

Whichever it is, say not to ignore it, and that the landlord still needs a court case (option 3).

## After a complaint

"It is unlawful for a landlord to discriminatorily increase a tenant’s rent or decrease services to a tenant, or to bring or threaten to bring an action for possession or other civil action, primarily because the landlord is retaliating against the tenant." (83.64(1)). Not renewing, or giving 83.57's notice, is not named there. Whether either is covered by itself is not settled. One: it is a step toward the action the rule names, so it is covered. The other: the rule lists the landlord's acts, and this is not one.

A tenant sued for possession can raise it as a defense (83.64(2)). The protected steps include a complaint to a code agency (83.64(1)(a)), a tenant organization (83.64(1)(b)), and a complaint under 83.56(1) (83.64(1)(c)), and these are only examples (83.64(1)). The tenant must have acted in good faith, which "means honesty in fact in the conduct or transaction concerned." (83.43(8)), and be treated differently (83.64(4)). Whether the landlord acted primarily to retaliate is for a court.

It falls away "if the landlord proves that the eviction is for good cause." (83.64(3)), whose examples include "violation of the terms of this chapter." (83.64(3)). Whether staying after the end is that kind of violation is not settled. One: holding over without permission is what 83.58 addresses, so it is good cause. The other: that would leave the defense nothing to do whenever a lease has ended. Give the dates as the tenant gave them; never count the days between them.

## If the landlord sues

Say this first when a case has been filed. A tenant raising any defense other than payment "shall pay into the registry of the court the accrued rent as alleged in the complaint or as determined by the court and the rent that accrues during the pendency of the proceeding, when due." (83.60(2)). "Failure of the tenant to pay the rent into the registry of the court or to file a motion to determine the amount of rent to be paid into the registry within 5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process constitutes an absolute waiver of the tenant’s defenses other than payment" (83.60(2)), and the landlord is entitled to an immediate default judgment removing the tenant (83.60(2)). A motion needs papers showing why the amount is wrong (83.60(2)). A tenant with subsidized rent deposits only their own share (83.60(2)). Give the 5 days and what they leave out, but never a calendar date for them; the summons states the requirement (83.60(2)). The winner may recover attorney fees and court costs (83.48). Other court steps are outside this tool.

## Mistakes to avoid

- Saying a lease's notice clause binds the tenant without checking the landlord's half and the 30 to 60 days.
- Saying a tenant owes the charge for missing a notice without every condition of 83.575(2), or applying 83.595(4)'s limits to it.
- Saying the tenant must be out on the end date, or that the landlord may then remove them without a court case.
- Stating double rent as owed while what the landlord said or did leaves permission in doubt, or applying 83.575(3) with no permission.
- Applying 83.57's 30 days to a set term still running, or treating a late notice as good for the date it names.
- Writing any date count_days did not give you, or counting how long something has lasted or how long until a date. Setting a date from the facts beside a date count_days gave is not counting.
