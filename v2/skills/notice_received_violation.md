---
name: notice_received_violation
description: The tenant got a written notice from the landlord about something other than unpaid rent that they did or allowed (a pet, guests, parking, noise, damage), giving 7 days to fix it or saying the lease is over.
---
# Notice of a violation

Rests on 83.56 (the notice, and how it reaches the tenant), 83.52 (the tenant's duties), 83.59 and 83.67 (getting the home back), 83.60 (if sued), 83.48 and 83.58 (fees, double rent), 83.64 (retaliation), 83.681 (court orders), 83.595 and 83.49 (after moving out), 83.505 (e-mail), and 83.57 and 83.575 (other notices). Read a section in full with get_statute_section.

When the answer turns on a point marked not settled, the first sentence says it is not settled and leans neither way (never "probably yes"). Every point marked not settled gets both readings, and you choose neither.

## First, whether this applies

- Load who_the_law_covers, unless the facts already hold school_housing.
- A demand for unpaid rent is a different notice (83.56(3)), with a different count that this tool does not do. Say so; these 7 days do not apply to it.
- A notice that only says the lease will not renew, or that a month-to-month tenancy is ending, names no violation: 83.57 or 83.575 applies, not this skill.
- Something said out loud is not this notice. The statute speaks of "a written notice" (83.56(2)(a)). Say no count has started.
- If the tenant wants to move out instead, go to "Moving out" below.

## What the lease adds

Read the clause or rule the notice points to, and set it beside what the notice says the tenant did. Quote it and cite it.

- The lease or a rule forbids it: say so. The lease allows it, or says nothing about it: say that plainly, and ask for any rule sheet the notice relies on.
- The lease's clause on notices to the tenant, and any e-mail addendum: use them under "How it reached the tenant".
- A clause that lets the landlord end the lease with no notice, less time, or no chance to fix: "The notice requirements of subsections (1)-(3) may not be waived in the rental agreement." (83.56(4)).

## Facts the answer turns on

Read the lease first. Ask the tenant only plain facts, from the notice in their hands, one or two at a time. Note each fact with note_fact under these names, dates written YYYY-MM-DD; a date counts only once the tenant has confirmed it.

- notice_words: what the notice says the tenant did, and what it demands, copied from the notice. event_date: the date of what it names.
- notice_delivered: the date the notice reached them, not the date written on it. How it came: handed over, mail, e-mail, left at the door, a portal message, a text. If it was left at the door, whether they were home. If mailed or left at the door, notice_sent: the date it was mailed or left, if they can tell.
- fixed_date: the date they fixed the problem, if they did.
- earlier_warning: any earlier written warning, what it was about, and earlier_warning_date.
- rent_since: whether the landlord has taken rent since it knew of the problem, how much of the month's rent, and when it knew.
- eviction_filed: whether the landlord has filed a case, and whether they were served court papers.

## Say this in every answer

After any not-settled sentence, and after what to do about a case already filed, say: the notice does not by itself put the tenant out. "The landlord shall not recover possession of a dwelling unit except:" (83.59(3)) through a court case, or when the tenant gave up the home or abandoned it (83.59(3)). The landlord may not lock them out: it "shall not prevent the tenant from gaining reasonable access to the dwelling unit by any means" (83.67(2)), changing the locks included. If it does, or cuts a utility, it is liable for "actual and consequential damages or 3 months’ rent, whichever is greater, and costs, including attorney’s fees." (83.67(6)). The notice still matters: it starts the count, and a tenant who does nothing can be sued. Never tell a tenant to ignore a notice because it has a flaw.

Then say which kind it is, from the notice's words:

- **Fix it:** it names the problem and says the lease ends if it is not fixed within 7 days. Go to option 1, then options 2 and 3 if they fit.
- **Lease over:** it says the lease is terminated and gives 7 days to leave. "the tenant shall have 7 days from the date that the notice is delivered to vacate the premises." (83.56(2)(a)). The last day: count_days(notice_delivered, 7), or both dates when "How it reached the tenant" gives two. Fixing the problem is not a right under this kind. Go to options 2 and 3, and "If the tenant stays". On a notice over intentional damage to the landlord's property, the landlord may also ask a court for an order against more of it (83.681(1)).
- **Only a warning:** it names a problem but does not end the lease or say the lease will end. No count has started. Say so, and that it may count later as "a written warning by the landlord of a similar violation" (83.56(2)(a)).

## How it reached the tenant

"The delivery of the written notices required by subsections (1)-(3) shall be by mailing, delivering a true copy thereof, e-mailing in accordance with s. 83.505 , or, if the tenant is absent from the premises, by leaving a copy thereof at the residence." (83.56(4)).

- Handed over: delivered that day.
- Mailed, or left at the door while the tenant was away ("if the tenant is absent from the premises" (83.56(4))): a way the statute names, but not settled which day counts. Call both count_days(notice_sent, 7) and count_days(notice_delivered, 7). One: 83.56(4) makes the mailing or the leaving the delivery, so that day. The other: a paper is delivered when it reaches the tenant; a fix notice's form says "within 7 days of receipt of this notice" (83.56(2)(b)), and a lease-over notice's form says "7 days from the delivery of this letter" (83.56(2)(a)). Acting by the earlier date meets both; say so.
- E-mail: only if the signed addendum in 83.505(1) exists; then it is "deemed delivered at the time it is sent, unless the e-mail is returned to the sender as undeliverable." (83.505(4)). Count from the day it was sent. Read the lease.
- A text, a portal message, or an e-mail with no addendum, or left at the door while they were home: not a way 83.56(4) names, and the text does not say what follows from another way. Not settled whether it still counts because it reached them. One: delivery "shall be by" (83.56(4)) the ways named, so it is not the required notice and no count has started. The other: it did what a notice is for, and 83.505 leaves room for "any other means permitted by law." (83.505(6)). Under that reading the count runs from the day it reached them: call count_days(notice_delivered, 7). Acting by that date meets both; say so.

## Option 1: fix it within the 7 days

"if the noncompliance is not corrected within 7 days from the date that the written notice is delivered, the landlord shall terminate the rental agreement by reason thereof." (83.56(2)(b)).

1. **The notice gives the chance.** If it is the "lease over" kind, this option is not open on that notice; say so.
2. **Within the time.** The last day: count_days(notice_delivered, 7), or both dates when "How it reached the tenant" gives two. Set fixed_date beside it: on or before it, met; say so plainly. Between two dates, it depends on the reading; say so.
3. **Fixed means the thing the notice names has stopped or been put right.** The tenant can tell. A tenant who disputes the charge can still fix it, and that meets the deadline whichever way the dispute goes; say so. Keeping proof of the fix and telling the landlord in writing shows when it happened.

Fixed in time: the landlord may not end the lease on this notice. But: "If such noncompliance recurs within 12 months after notice, an eviction action may commence without delivering a subsequent notice pursuant to paragraph (a) or this paragraph." (83.56(2)(b)). Say that in plain words. If the tenant asks until when: count_days(notice_delivered, 365), a stand-in for the 12 months, given as "about" that date, since 12 months is not always 365 days.

Not fixed in time: the rule says "the landlord shall terminate the rental agreement" (83.56(2)(b)), and the form says "your lease shall be deemed terminated" (83.56(2)(b)). Whether the lease ends by itself or only when the landlord acts on it, and so whether a late fix helps before then, is not settled. Go to "If the tenant stays".

## Option 2: the notice does not fit

A tenant can raise these if sued, and can put them to the landlord in writing now. Whether a flaw ends a case is for the court. "The landlord must be given an opportunity to cure a deficiency in a notice or in the pleadings before dismissal of the action." (83.60(1)(a)). That sentence sits in a paragraph about cases over unpaid rent; whether it reaches this kind of case is not settled. Say so whenever you name a flaw.

1. **No violation.** The rule covers a tenant who "materially fails to comply with s. 83.52 or material provisions of the rental agreement, other than a failure to pay rent, or reasonable rules or regulations" (83.56(2)).
   - Set what happened beside 83.52's list and the lease. A guest's conduct can count: the tenant must "require other persons on the premises with his or her consent to conduct themselves" (83.52(7)) so as not to disturb, and not "permit any person" (83.52(6)) to damage the property.
   - "material" is not defined. The lists below show which kind of notice fits; whether conduct on a list is therefore material is not settled. Give both readings and choose neither, with the tenant's facts beside the word. One: breaking a clear term of the lease is enough, and the statute calls listed conduct "Examples of such noncompliance" (83.56(2)(b)). The other: it turns on how serious this instance was and what it did to others.
   - "reasonable" describes the rule, and is not defined: set the rule beside the word, and state no test.
2. **The wrong kind: lease over, for something the tenant should get to fix.** Set the conduct beside the statute's two lists; neither list is complete ("include, but are not limited to" (83.56(2)(a))).
   - The no-fix list: "destruction, damage, or misuse of the landlord’s or other tenants’ property by intentional act" (83.56(2)(a)), fraudulent entry (83.56(2)(a)), or "a subsequent or continued unreasonable disturbance." (83.56(2)(a)). Conduct like these: this kind fits; say so.
   - A repeat: "a subsequent or continuing noncompliance within 12 months of a written warning by the landlord of a similar violation" (83.56(2)(a)). A written warning about something similar: call count_days(earlier_warning_date, 365), a stand-in for the 12 months, and set event_date beside the result. On or before it, this kind fits, even for conduct on the fix list; say so. Within one day of it, either way, say it is too close to tell, since 12 months is not always 365 days. Later than that, this ground does not apply. Whether two events are "similar" is not defined. A spoken warning is not a written one.
   - The fix list: "having or permitting unauthorized pets, guests, or vehicles; parking in an unauthorized manner or permitting such parking; or failing to keep the premises clean and sanitary." (83.56(2)(b)). Conduct like these, with no earlier written warning: this kind does not fit, and the tenant should have had the 7 days. Say so plainly. Stopping the conduct now is still worth doing. The notice's words give no right to fix it, but whether the termination holds is the flaw question for a court.
   - Like neither list, such as a first noise complaint or an accident that damaged something: not settled. One: it is of a nature the tenant should get to fix, so the notice should have given 7 days. The other: the lists are only examples, so the landlord may say it is the kind that gets no chance.
3. **The words are missing.** Each rule has its own words. A notice that does not say what the tenant did is not "specifying the noncompliance" (83.56(2)(a)), so it is not the required notice. So too a notice of either kind that gives less than 7 days. A notice with those but leaving out other parts of "substantially the following form" (83.56(2)(b)), such as the warning about the next 12 months: not settled. One: without that part it is not the required notice. The other: the form need only be followed substantially.
4. **How it came:** see "How it reached the tenant".
5. **A retaliating landlord.** It is unlawful "to bring or threaten to bring an action for possession or other civil action, primarily because the landlord is retaliating against the tenant." (83.64(1)). Raise this when the tenant complained to a code office or to the landlord under 83.56(1), joined a tenant group, or did something like the other examples in 83.64(1). They must have acted in good faith (83.64(1)), and being treated differently in the rent, the services, or the action taken is required (83.64(4)). It is a defense in an action for possession (83.64(2)), and it does not apply if the landlord proves good cause, whose examples include "good faith actions for nonpayment of rent, violation of the rental agreement or of reasonable rules" (83.64(3)). Give the dates as the tenant gave them; never count the days between them.

## Option 3: the landlord gave up the right by taking rent

"If the landlord accepts rent with actual knowledge of a noncompliance by the tenant or accepts performance by the tenant of any other provision of the rental agreement that is at variance with its provisions" (83.56(5)(a)), the landlord "waives his or her right to terminate the rental agreement or to bring a civil action for that noncompliance, but not for any subsequent or continuing noncompliance." (83.56(5)(a)). There is nothing for the tenant to do; it is an answer to the notice or a defense if sued.

1. **The landlord knew when it took the rent.** Rent taken after the notice was delivered: met, since the notice shows it knew. Rent before: ask what shows the landlord knew.
2. **The month's whole rent.** "a landlord does not waive the right to terminate the rental agreement or to bring a civil action for that noncompliance by accepting partial rent for the period." (83.56(5)(a)). Part of the month's rent: not met.
3. **It was over when the rent was taken.** Something that ended before the rent was taken and has not happened again: met, and if 1 and 2 are met, say plainly the landlord gave up ending the lease over it. If it has happened again since: not met for the new event. If it went on after the rent was taken, or is still going on, like a pet still in the home: not settled. One: it is a "continuing noncompliance" (83.56(5)(a)), so taking rent gives up nothing. The other: taking rent with knowledge gives up ending the lease over that violation, and only a new one starts over.
4. **Rent from a program.** The rule "does not apply to that portion of rent subsidies received from a local, state, or national government" (83.56(5)(c)), but "waiver will occur if an action has not been instituted within 45 days after the landlord obtains actual knowledge of the noncompliance." (83.56(5)(c)). Only if the tenant's rent is subsidized.

## If the tenant stays

"If the rental agreement is terminated and the tenant does not vacate the premises, the landlord may recover possession of the dwelling unit as provided in this section." (83.59(1)). That is a court case; it does not happen by itself when the 7 days end.

- Costs: the winner gets judgment for costs (83.59(4)) and may recover attorney fees (83.48).
- Double rent: "The landlord may also recover double the amount of rent due on the dwelling unit, or any part thereof, for the period during which the tenant refuses to surrender possession." (83.58). That section speaks of staying "after the expiration of the rental agreement without the permission of the landlord" (83.58). Whether a lease ended by this notice has reached its "expiration" (83.58) is not settled. One: a lease ended by notice has expired, so double rent can apply. The other: expiration means the end of the term, and a lease cut short has not reached it.

If the landlord sues: "Any tenant who wishes to defend against an action by the landlord for possession of the unit for noncompliance of the rental agreement or of relevant statutes must comply with s. 83.60 (2)." (83.56(5)(b)). That means paying "into the registry of the court the accrued rent as alleged in the complaint or as determined by the court and the rent that accrues during the pendency of the proceeding, when due." (83.60(2)). "Failure of the tenant to pay the rent into the registry of the court or to file a motion to determine the amount of rent to be paid into the registry within 5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process constitutes an absolute waiver of the tenant’s defenses other than payment" (83.60(2)), and the court "must enter a default judgment for removal of the tenant with a writ of possession to issue immediately" (83.56(5)(b)). Paying, or filing that motion with papers showing why the amount is wrong (83.60(2)), in time keeps the defenses. A tenant with subsidized rent deposits only their own share (83.60(2)). "The clerk shall notify the tenant of such requirement in the summons." (83.60(2)). Say this first when a case has been filed. Give the 5 days and what they leave out, but never a calendar date for them; say the summons states the requirement. Other court steps are outside this tool.

## Moving out

- Leaving does not by itself settle what is owed. After a tenant who breached gives up the home, the landlord may choose among the remedies in 83.595, including holding the tenant to the rent. Load wants_to_leave_early for those and for the 7 days' notice with an address (83.49(5)); the next point still holds where it says the choice is the landlord's.
- Whether a landlord that ended the lease itself can still hold the tenant to rent for the rest of the term is not settled. One: ending the lease is the choice to "Treat the rental agreement as terminated" (83.595(1)), "thereby terminating any further liability of the tenant" (83.595(1)). The other: 83.595 applies to any tenant who breached and gave up the home, so the landlord keeps its choice.
- "If the rental agreement is terminated, the landlord shall comply with s. 83.49 (3)." (83.56(6)). After the move, load deposit_not_returned for the deposit.

## Mistakes to avoid

- Saying the tenant must be out when the 7 days end, or that the landlord may then remove them without a court case or lock them out.
- Telling the tenant to ignore a notice because of a flaw, or saying a flaw ends any case, without the sentence on curing a notice.
- Counting from the date written on the notice instead of the day it was delivered.
- Saying a fix saves the tenant under a "lease over" notice, or that they must leave within 7 days under a "fix it" notice.
- Saying a tenant who fixed it is clear for good, leaving out the next 12 months.
- Leaving out 83.56(5)(a) when the landlord has taken rent since it knew, or treating part of a month's rent as giving up the right.
- Explaining how to defend a case without 83.56(5)(b) and 83.60(2), leaving out its 5 days, or giving a calendar date for them.
- Saying a kind of notice fits only if the conduct is on one of the statute's lists. The lists are only examples.
- Working out when 12 months end except by count_days(the date, 365), writing any date count_days did not give you, or counting how long something has lasted or how long until a date. Setting a date from the facts beside a date count_days gave is not counting.
- Stating a test for "material", "reasonable", "similar", or "unreasonable disturbance" that the statute does not give.
