---
name: lease_ending
description: "The lease is ending or the tenancy is being ended; notice to leave or renew, and staying on after the end."
sections: ["83.575", "83.57", "83.58", "83.46", "83.42", "83.505"]
clocks:
  - id: month_to_month_notice_by_tenant
    actor: tenant
    trigger: period_end_date
    days: 30
    direction: before
    applies_if: month_to_month
    cite: "83.57(3)"
    quote: "When the tenancy is from month to month, by giving not less than 30 days’ notice prior to the end of any monthly period"
  - id: month_to_month_notice_by_landlord
    actor: landlord
    trigger: period_end_date
    days: 30
    direction: before
    applies_if: month_to_month
    cite: "83.57(3)"
    quote: "When the tenancy is from month to month, by giving not less than 30 days’ notice prior to the end of any monthly period"
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.575.txt, statutes/83.57.txt, statutes/83.58.txt, statutes/83.46.txt, statutes/83.42.txt, statutes/83.505.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/lease_ending.yaml version 0.6"
---
## When to load this skill

Load this skill when the lease is ending or the tenancy is being ended: notice to leave or renew, and staying on after the end. It rests on 83.575 (a lease with a specific duration), 83.57 (a tenancy without one), 83.58 (holding over), 83.46 (rent and duration), and 83.505 (notices by e-mail).

- Leaving before a fixed term ends is the subject of wants_to_leave_early; load that skill for it.
- When the lease says nothing on duration, 83.46(2) sets it by how often rent is paid.
- The statute leaves some housing out of part II: "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)). College housing may be an example. The tool records the facts and does not decide whether this applies; say what the words are and what you would need to know.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold, one or two things at a time and only what your answer turns on. Never ask whether something meets a term of the statute or the lease; ask what happened, then apply the term yourself.

### In the lease (search_lease; try a second wording if the first finds nothing)

- The date the lease term ends.
- Any notice the lease requires before moving out at the end. Set it beside 83.575(1) and say what it says; the program does not decide whether a clause complies (see the next section).
- Where and how the tenant's notice must be sent under the lease.
- What the lease requires at move-out.
- The monthly rent, if the tenant stays on after the end.

### From the tenant

- Does the lease have a fixed end date (for example, a one-year lease), and what date does the term end? Or is the tenancy month to month (no fixed end date, rent paid monthly)? If month to month, what is the last day of the current monthly rent period (for example, the last day of this month)?
- Has the landlord sent anything in writing about the end of the lease (a renewal offer, a move-out notice, a reminder of the notice the tenant must give)? What date did it reach them?
- Have they given the landlord anything in writing saying they are leaving or ending the tenancy? How did it reach the landlord (handed to the landlord or the office, regular mail, certified mail, e-mail, a resident portal request or message, a text message, or something else), and what date was it delivered?
- Do they plan to stay after the lease or rental period ends? Has the landlord agreed that they may stay?

### What the deadlines count from

The program computes dates only from facts the tenant has confirmed. It computes only the month-to-month dates, so get these proposed and confirmed:

- Whether the tenancy is month to month. The deadlines apply only then.
- The last day of the current monthly rent period. The 30 days count back from it.

For a lease with a fixed end date, the notice period comes from the lease and the program computes no date from it. For a tenancy from year to year, quarter to quarter, or week to week, see the second open question.

### Evidence to suggest the tenant keep

- The lease, especially its term and notice clauses.
- Any written notice from the landlord about ending or renewing, with its delivery date.
- The tenant's own written notice, with proof of how and when it was delivered.
- Any written agreement to stay on, with the rent agreed.

## What the tenant can do

Tell the tenant first whether they can do each of these and what it turns on, before any step. Each condition is settled by the lease (read that clause with search_lease and say what it says), by the tenant (ask), by the program's deadlines (call get_deadlines), or not at all (the statute does not settle it: give every reading, see the open questions below).

Lease override to show: "A rental agreement may not require less than 30 days’ notice or more than 60 days’ notice from either the tenant or the landlord." (Fla. Stat. 83.575(1)). Show it next to any end-of-term notice clause in the lease. The tool does not decide whether a clause complies.

### End a month-to-month tenancy at the end of this monthly period, with written notice at least 30 days before it ends (Fla. Stat. 83.57(3))

Both conditions must be met.

1. The tenancy is month to month: "When the tenancy is from month to month, by giving not less than 30 days’ notice prior to the end of any monthly period" (Fla. Stat. 83.57(3)). The tenant can tell you, and the lease's term clause shows it. If the tenant says it is not month to month, this option is closed.
2. The last day to give notice for this period has not passed, or the notice already went out by it: "not less than 30 days’ notice prior to the end of any monthly period" (Fla. Stat. 83.57(3)). It is met in either way:
   - The last day has not passed. Only the program's deadlines settle this. If they show it has passed, say so, and add that the statute speaks of the end of any monthly period.
   - The notice already given went out by the last day. Ask the date it was delivered, to put beside the last day the program's deadlines show.

The step: a written notice delivered to the landlord, in a way the statute allows (mail, a true copy by hand, or e-mail under an e-mail addendum). The statute: "may be terminated by either party giving written notice in the manner provided in s. 83.56 (4)" (Fla. Stat. 83.57). Fetch 83.56 with get_statute_section if you need to read 83.56(4).

- If the notice went by mail or by hand, the step is done.
- If it went by e-mail, 83.56(4) counts it only as 83.505 allows. Ask whether the tenant and the landlord signed an addendum agreeing to notices by e-mail, and read the lease's clause on notices to the landlord.
- If it went some other way, ask how it reached the landlord, beside the ways 83.56(4) names.

### Leave at the end of the lease without owing the liquidated damages the lease sets for missing its notice, because the landlord did not send the notice the statute requires first (Fla. Stat. 83.575(2))

All three conditions must be met. No steps are listed beyond a letter (see Letters). The program computes no date for this; see the first open question.

1. The lease has a fixed term: "A rental agreement with a specific duration may contain a provision requiring the tenant to notify the landlord within a specified period before vacating the premises at the end of the rental agreement" (Fla. Stat. 83.575(1)). The tenant can tell you. If the tenant says the lease has no fixed end date, this option is closed.
2. The lease asks for notice before leaving at its end: "may contain a provision requiring the tenant to notify the landlord within a specified period before vacating the premises at the end of the rental agreement" (Fla. Stat. 83.575(1)). The lease settles this: read that clause with search_lease and say what it says. If the lease asks for no notice, there is no notice to miss, and the option is closed.
3. The landlord did not send, within 15 days before the lease's notice period began, a written notice of that requirement, the end date, and every fee: "The landlord must provide such written notice to the tenant in a manner prescribed by s. 83.56 (4) within 15 days before the start of the notification period contained in the rental agreement." (Fla. Stat. 83.575(2)). It is met in either way:
   - The landlord sent no such notice. The tenant can tell you whether anything in writing about the end of the lease reached them. If they say nothing did, this way is met.
   - The landlord's notice came outside those 15 days, or did not list the end date and every fee. The tenant checks the date it came and what it lists, beside the start of the lease's notice period. You give no last day and do not compare the dates yourself.

### Stay on after the lease ends with the landlord's permission (Fla. Stat. 83.575(3))

One condition: the landlord has agreed that the tenant may stay. The statute: "If the tenant remains on the premises with the permission of the landlord after the rental agreement has terminated" (Fla. Stat. 83.575(3)). The tenant can tell you. If the tenant says the landlord has not agreed, a tenant who holds over without permission may be removed and owe double the rent, under 83.58. No steps are listed. What counts as permission is open (the third open question).

## Deadlines

The program computes and prints every date from confirmed facts. Never write, count, or compare a date yourself: call get_deadlines, and say a deadline has passed or is upcoming only as its result says. The counting rule is an assumption: Florida's court rule for counting days has not been checked against statutory deadlines outside litigation.

For a month-to-month tenancy, the program computes the last day each side can give 30 days' notice before the end of the monthly period. Both count back from the last day of the monthly rent period, the same sentence applies to both, and written notice goes in the manner 83.56(4) provides (mail, by hand, or e-mail as 83.505 allows):

- The tenant's last day to give notice to end the tenancy.
- The landlord's last day to give notice to end the tenancy.

The statute: "When the tenancy is from month to month, by giving not less than 30 days’ notice prior to the end of any monthly period" (Fla. Stat. 83.57(3)). The program computes nothing for a lease with a fixed end date.

## What the statute does not settle

For each of these, tell the tenant in plain words that the law does not settle it (or that the tool does not compute it), give every reading and what it would mean for them, and pick none.

### A notice period the lease sets

For a lease with a specific duration, the notice period comes from the lease (83.575(1)), and "A rental agreement may not require less than 30 days’ notice or more than 60 days’ notice from either the tenant or the landlord." (Fla. Stat. 83.575(1)). The landlord's written notice under 83.575(2) is due "within 15 days before the start of the notification period contained in the rental agreement" (Fla. Stat. 83.575(2)). Apply these to the lease's own words and the confirmed dates, but give no last day: the program does not compute a date from a period the lease sets, and you never count one. What stays open is what "within 15 days before the start" asks of the landlord.

- The landlord's notice must come during the 15 days that end when the notification period starts, not earlier.
- The landlord's notice must come no later than 15 days before the notification period starts; earlier is also in time.

### Other kinds of tenancy

83.57 also sets notice for tenancies from year to year, quarter to quarter, and week to week. The program computes only the month-to-month date. For the others, apply the text of 83.57 to the tenancy's period in the record and say the tool does not compute the date.

### Staying on after the end

83.575(3) covers a tenant who "remains on the premises with the permission of the landlord after the rental agreement has terminated" (Fla. Stat. 83.575(3)), and 83.58 a tenant who "holds over and continues in possession of the dwelling unit or any part thereof after the expiration of the rental agreement without the permission of the landlord" (Fla. Stat. 83.58). Apply the one the record points to. What stays open is what counts as permission when the landlord said nothing, or took rent for a period after the end.

- Taking rent for a period after the end is permission: the landlord treats the tenant as staying on with its agreement.
- Permission must be given; taking rent alone does not turn a tenant who "holds over and continues in possession" (Fla. Stat. 83.58) into one who stays with permission.

## Letters

The tenant sends every letter; you send nothing. Every letter holds: today's date, the end date, whether the tenant is leaving or asking to renew, and the delivery method. The postures, each line as written:

- preserve: States the date the tenant will move out, or asks to renew, and asks the landlord to confirm. Cites nothing.
- assert: Adds the 83.57(3) sentence for a month-to-month tenancy, or the lease's notice clause, quoted.
- escalate: Adds the 83.575(2) sentence on the landlord's written notice, quoted.

When a letter is shown, tell the tenant: for a month-to-month tenancy, 83.57 says the tenancy "may be terminated by either party giving written notice in the manner provided in s. 83.56 (4)" (Fla. Stat. 83.57) with "not less than 30 days’ notice prior to the end of any monthly period" (Fla. Stat. 83.57(3)), and the program computed that date from the period end they gave. For a lease with a fixed end date, the notice period comes from the lease, and the program does not compute it. They can ask in the chat to have 83.57 or the lease's notice clause applied to their tenancy before they send the letter.

The tenant delivers the letter. Read the lease's clause on where and how notices must be sent (search_lease), and quote it when you ask how they will send it.

## Mistakes to avoid

- Computing a notice date from a period the lease sets. The program computes only the month-to-month dates.
- Saying a lease's end-of-term notice clause binds the tenant without the condition in 83.575(1): that it also requires the landlord to notify the tenant "within such notice period if the rental agreement will not be renewed" (Fla. Stat. 83.575(1)).
- Saying the tenant owes liquidated damages for missing the lease's notice without the condition in 83.575(2): the landlord's written notice "specifying the tenant’s obligations under the notification provision" (Fla. Stat. 83.575(2)).
- Applying 83.575(3)'s extra month's rent without both its conditions: that the tenant "remains on the premises with the permission of the landlord" (Fla. Stat. 83.575(3)) and "fails to give notice required under s. 83.57 (3)" (Fla. Stat. 83.575(3)). Or applying 83.58's double rent while the record does not show whether the landlord gave permission to stay.
- Applying 83.57 to a lease with a specific duration, or 83.575 to a month-to-month tenancy. When the agreement says nothing on duration, 83.46(2) sets it by how often rent is paid.
- Computing any date yourself.
