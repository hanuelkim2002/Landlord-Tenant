---
name: rent_increased
description: The landlord has raised the rent or added a new monthly charge, says it will, or offers a renewal at a higher rent.
---
# Rent increased

Rests on 83.46 (rent, tenancies with no set term), 83.43 (what rent is, good faith), 83.57 (ending a tenancy with no set term), 83.64 (retaliation), 83.425 (local rules), 83.56 (unpaid rent, rent paid, notices), 83.60 (if sued), 83.55 and 83.54 (damages, suits), 83.44 and 83.45 (good faith, unfair clauses), 83.48 (attorney fees), 83.51 and 83.491 (trash, a fee in place of a deposit), 83.59 and 83.67 (no lockout), and 83.505 (e-mail notices). Read a section in full with get_statute_section.

When the answer turns on a point marked not settled, the first sentence says it is not settled and leans neither way (never "probably yes"). Every point marked not settled gets all its readings, and you choose none. When the tenant asks "can I" and the answer turns on such a point, write "You can if X, and X is not settled", never a plain yes.

## First, whether this applies

- Load who_the_law_covers, unless the facts already hold school_housing.
- Part II has no section that sets how much notice a rent increase needs, and none that limits how much rent may go up. Say so plainly when asked. Never state a notice period or a cap as the law.
- Local rules: "The regulation of residential tenancies, the landlord-tenant relationship, and all other matters covered under this part are preempted to the state." (83.425), and the section supersedes local rules on matters including "fees charged by the landlord; or notice requirements." (83.425). The stored text holds no local rent rule. Never apply one from memory.
- Rent paid through a program (a voucher, public housing): the program's own rules are not stored. Say they may limit this, and that they are outside this tool.
- The increase comes with an offer to renew, or the tenant would rather leave: load lease_ending too.

## What the lease adds

Read the whole lease, addenda included, for: the rent, the term, any clause on the rent changing, how the lease may be changed, any charges, staying after the end, and how notices go to the landlord. Quote each clause and cite it.

- **Rent steps set in the lease from the start** (so much until a date, then more): that is the lease's rent, not an increase. Say so.
- **A clause letting the landlord raise the rent during the term:** set the increase beside the clause's conditions (how much notice, how it is given, how much, how often). If it gives a number of days N: the last day to give notice for the start date named is count_days(new_rent_starts, -N), and the earliest start from the notice given is count_days(increase_delivered, N). All conditions met: the rent goes up as the lease says; say so plainly. Any not met: the clause does not support this increase on these terms; say so plainly. The rent stays where it is for now and the tenant keeps paying it, but the landlord can still raise it by meeting the clause, so say that too. Option 1's plain answer is for a lease with no such clause. A clause with no limit at all: say what it says, that it carries "an obligation of good faith in its performance or enforcement." (83.44), and that whether it is unfair enough to be "unconscionable" (83.45(1)) is for a court.
- **A new charge** (an amenity fee, a trash fee): the same questions as for rent. The lease provides it: owed as the lease says. It does not: during a set term the landlord cannot add it alone, any more than it can raise the rent. A fee counts as rent only if it is "designated as rent in a written rental agreement." (83.43(12)). That matters because a demand under 83.56(3) and the registry under 83.60(2) speak of rent.
  - Trash: in a unit other than a single-family home or duplex, "Garbage removal and outside receptacles therefor." (83.51(2)(a)) falls to the landlord "Unless otherwise agreed in writing" (83.51(2)(a)), though the rental agreement may put the charges on the tenant (83.51(2)(e)).
  - A fee in place of a security deposit: "The amount of the fee, which may not be increased during the term of the rental agreement." (83.491(4)(a)).

## Facts the answer turns on

Read the lease first. Ask the tenant only plain facts, one or two at a time. Note each fact with note_fact under these names, dates written YYYY-MM-DD; a date counts only once the tenant has confirmed it.

- new_rent: the new amount. increase_delivered: the date word of it reached them, and how it came (handed over, mail, portal, text, spoken). new_rent_starts: the date it is said to start.
- lease_end_date: the date the lease ends, if it has one. period_end: the last day of the rent period before the new rent starts. next_period_end: the last day of the rent period after that.
- agreed: whether they signed anything or said yes. paid_new_rent: whether they have paid the new amount, for which months, and what they knew about the lease when they paid.
- complaint_date: the date of any complaint or similar step before the increase, and what it was. others_rent: what they know about other tenants' rent.
- rent_demand: any written demand for rent, and its date. eviction_filed: whether a case has been filed, and whether they were served.

## Which kind of increase

Settle this first. With a set end date, call count_days(lease_end_date, 0) and set new_rent_starts beside the date it gives.

- A set end date, and the new rent starts on or before it: option 1.
- A set end date, and the new rent starts after it: option 2.
- No set end date, or the tenant stayed on after a set term with the landlord's permission: option 3. With no term stated, "the duration is determined by the periods for which the rent is payable." (83.46(2)). Stayed on without permission, or in doubt: load lease_ending too.

Any kind: option 4 if the tenant did something first that the landlord may be answering, such as a complaint or joining a tenant group, and the two parts after it if they fit.

## Option 1: during a set term

Part II has no section that lets a landlord raise the rent during a set term. The rent is what the lease says. Quote the rent clause and any clause on changing the lease.

1. **No clause allows it** (see "What the lease adds").
2. **The tenant did not agree.**
   - They signed a change: the rent is what they signed, if it meets the lease's clause on changes.
   - They said yes without signing: not settled whether that changes the rent. One: a rental agreement can include an "oral agreement for a duration of less than 1 year" (83.43(13)). The other: a lease clause requiring a signed change still governs.
   - They paid it without signing: this option's plain answer does not apply. Start from "If the tenant already paid it", which is not settled.

Both met: the landlord cannot change the rent alone before the lease ends. Say so plainly. The tenant keeps paying the lease's rent, in full and on time, and can tell the landlord in writing that they do not agree, quoting the rent clause and sending it the way the lease's notice clause says. It helps to keep the letter, the lease, and proof of each payment. Say the risk too: see "If the landlord treats it as unpaid rent". The landlord can ask for more when the term ends (option 2).

## Option 2: a higher rent for a new term

Part II names no right to renew at the same rent and no limit on what a landlord may ask for a new term. Say so plainly. The lease's rent stands through lease_end_date whatever the offer says. From there:

- **Agree:** the new rent starts with the new term. Say what they should read before signing: the rent, the term, and any new charge.
- **Leave at the end:** load lease_ending for any notice the lease asks for.
- **Stay without agreeing:** load lease_ending. Staying without permission can mean "double the amount of rent due" (83.58). Read the lease's clause on staying after the end; if it makes the tenancy month to month, say what it says, and option 3 applies from then.

## Option 3: no set end date

Part II sets no notice for this and does not say a landlord may change the rent alone, so what an increase takes is not settled. Give all three readings and choose none. Quote any lease clause on signed changes.

- One: a landlord that can end the tenancy only on 83.57's notice can change the rent only with the same notice, written and delivered a way 83.56(4) names, for month to month "not less than 30 days’ notice prior to the end of any monthly period" (83.57(3)).
- Two: no section sets a notice, so none in particular is needed, and the tenant can pay it or leave.
- Three: 83.57 only lets a party end the tenancy, so the rent changes only if the tenant agrees, and a landlord that wants more must end the tenancy on that notice and offer new terms.

The date: count_days(period_end, -N), with N from 83.57: 30 for month to month (83.57(3)), and for other rent periods the number in 83.57(1), (2), or (4). Set increase_delivered beside it. The ways 83.56(4) names are mailing, a true copy by hand, e-mail under the signed addendum in 83.505(1), or, if the tenant is away, a copy left at the home.

- In writing, a way named, and on or before that date: in time under readings one and two. Say so plainly. Under reading three the letter alone still does not change the rent.
- Later than that, or spoken, or by text or portal: not good for that date under reading one, enough under reading two, and no change under reading three. Whether a late notice works for the next period under reading one is not settled, as lease_ending says of a late notice to end a tenancy; its date is count_days(next_period_end, -N).

Under every reading the landlord may end the tenancy on that notice: it "may be terminated by either party giving written notice in the manner provided in s. 83.56 (4)" (83.57), and no reason is named. Say so, so the tenant knows what refusing can lead to.

The short answer here: say it is not settled, then write "You have three choices, and each has a risk", then name the three below without choosing one. In the details, say what each one risks.

- Pay the new rent. Whether paying gives anything up is not settled; give both readings from "If the tenant already paid it", never one as the law.
- Pay the old rent and say in writing why. See "If the landlord treats it as unpaid rent".
- End the tenancy by written notice. Give the last day here, with the other choices: count_days(period_end, -N), or count_days(next_period_end, -N) if that has passed. Then load lease_ending for how the notice goes.

## Option 4: retaliation

"It is unlawful for a landlord to discriminatorily increase a tenant’s rent or decrease services to a tenant, or to bring or threaten to bring an action for possession or other civil action, primarily because the landlord is retaliating against the tenant." (83.64(1)).

All of these must be met.

1. **Something the tenant did first.** "Examples of conduct for which the landlord may not retaliate include, but are not limited to, situations where:" (83.64(1)) they complained to a code agency (83.64(1)(a)), took part in a tenant organization (83.64(1)(b)), complained to the landlord under 83.56(1) (83.64(1)(c)), ended a lease as a servicemember (83.64(1)(d)), paid rent to an association after its demand (83.64(1)(e)), or used fair housing rights (83.64(1)(f)). Fair housing law itself is outside this tool. Another step, like an ordinary repair request: not settled. One: the list is only examples, so it can count. The other: it counts only if it is like the named ones, and a request that says nothing about ending the lease is not 83.56(1)'s complaint.
2. **Good faith** (83.64(1)). "“Good faith” means honesty in fact in the conduct or transaction concerned." (83.43(8)). Applying that is for a court.
3. **Treated differently.** "“Discrimination” under this section means that a tenant is being treated differently as to the rent charged, the services rendered, or the action being taken by the landlord, which shall be a prerequisite to a finding of retaliatory conduct." (83.64(4)). Set what they know of other tenants' rent beside the words. The same increase for everyone points against it; say so plainly. If they do not know, say that is the fact to find out.
4. **Primarily to retaliate.** This is the landlord's motive, for a court. An increase that followed such a step is not retaliation for that reason alone. Give the dates as the tenant gave them; never count the days between them.

What it gives: "Evidence of retaliatory conduct may be raised by the tenant as a defense in any action brought against him or her for possession." (83.64(2)), unless "the landlord proves that the eviction is for good cause." (83.64(3)), whose examples include "good faith actions for nonpayment of rent" (83.64(3)). So not paying the new rent can weaken it; say so.

What the tenant can do about an increase alone, before any case: not settled. One: 83.64(2) makes it only a defense, so there is nothing to raise until a case. The other: 83.64(1) makes the increase unlawful, "Any right or duty declared in this part is enforceable by civil action." (83.54), and a party may recover damages for a failure to comply with "this part" (83.55).

## If the tenant already paid it

"if the tenant pays rent with actual knowledge of a noncompliance by the landlord" (83.56(5)(a)), the tenant "waives his or her right to terminate the rental agreement or to bring a civil action for that noncompliance, but not for any subsequent or continuing noncompliance." (83.56(5)(a)).

Ask what they knew when they paid, and set it beside "actual knowledge" (83.56(5)(a)). Whether paying a raised rent gives up the extra, or changes the rent from then on, is not settled, so going back to the lease's rent and getting the extra back are not settled either. Start the answer there. One: paying with knowledge gives up a suit over those months and may show the tenant agreed. The other: an increase the lease never allowed is not rent "due" (83.43(12)), a clause requiring a signed change still stands, and the extra can be claimed under 83.55, with each later month a "subsequent or continuing noncompliance" (83.56(5)(a)). Amounts and court steps are outside this tool; do not total them.

## If the landlord treats it as unpaid rent

- **A written demand.** "If the tenant fails to pay rent when due and the default continues for 3 days, excluding Saturday, Sunday, and legal holidays, after delivery of written demand by the landlord for payment of the rent or possession of the premises, the landlord may terminate the rental agreement." (83.56(3)). This tool does not count those days; the demand states them. Say not to ignore it.
- **Taking the old rent.** A landlord "does not waive the right to terminate the rental agreement or to bring a civil action for that noncompliance by accepting partial rent for the period." (83.56(5)(a)). So taking it does not mean the landlord gave in. "If partial rent is accepted after posting the notice for nonpayment, the landlord must:" (83.56(5)(a)) give a receipt with the date, the amount, and the balance before filing; or put the amount in the court's registry on filing; or post a new 3-day notice (83.56(5)(a)). Whether the lease's rent is "partial" at all is the dispute.
- **No court case, no removal.** "The landlord shall not recover possession of a dwelling unit except:" (83.59(3)) through a court case, or when the tenant gave up or abandoned the home (83.59(3)). The landlord "shall not prevent the tenant from gaining reasonable access to the dwelling unit by any means" (83.67(2)).
- **A case filed.** Say this first. The tenant must pay into the registry "the accrued rent as alleged in the complaint or as determined by the court and the rent that accrues during the pendency of the proceeding, when due." (83.60(2)). "Failure of the tenant to pay the rent into the registry of the court or to file a motion to determine the amount of rent to be paid into the registry within 5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process constitutes an absolute waiver of the tenant’s defenses other than payment" (83.60(2)), and the landlord is entitled to an immediate default judgment removing the tenant (83.60(2)). When the amount is what they dispute, the motion is the way to say so, with papers showing why the amount in the complaint is wrong (83.60(2)). A tenant with subsidized rent deposits only their own share (83.60(2)). Give the 5 days and what they leave out, but never a calendar date for them; the summons states the requirement (83.60(2)).
- **Defenses.** The tenant "may raise any other defense, whether legal or equitable, that he or she may have, including the defense of retaliatory conduct in accordance with s. 83.64" (83.60(1)(a)). The winner may recover attorney fees and court costs (83.48). Other court steps are outside this tool.

## Mistakes to avoid

- Saying a landlord may raise the rent during a set term with no clause and no agreement, or calling the lease's own rent steps an increase.
- Treating 83.57's 30 days as settled for an increase, saying flatly that no notice is needed, or saying flatly that a letter alone changes the rent with no set end date.
- Saying an increase is retaliation because it followed a complaint, or leaving out good faith or being treated differently.
- Telling a tenant they can stop paying rent altogether, explaining a case without 83.60(2), or giving a calendar date for its 5 days.
- Writing any date count_days did not give you, or counting how long something has lasted or how long until a date. Setting a date from the facts beside a date count_days gave is not counting.
