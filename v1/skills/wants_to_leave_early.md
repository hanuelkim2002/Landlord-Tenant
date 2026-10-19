---
name: wants_to_leave_early
description: "Tenant wants to move out before the lease term ends."
sections: ["83.595", "83.49", "83.682", "83.575", "83.42", "83.505"]
clocks:
  - id: seven_day_notice_before_leaving
    actor: tenant
    trigger: planned_move_out
    days: 7
    direction: before
    cite: "83.49(5)"
    quote: "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which notice must include the address where the tenant may be reached"
    consequence: "Failure to give such notice relieves the landlord of the notice requirement of paragraph (3)(a) but does not waive any right the tenant may have to the security deposit or any part of it."
  - id: servicemember_earliest_termination
    actor: tenant
    trigger: servicemember_notice_received
    days: 30
    direction: after
    applies_if: servicemember_notice_given
    cite: "83.682(1)"
    quote: "written notice of termination to be effective on the date stated in the notice which is at least 30 days after the landlord’s receipt of the notice"
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.595.txt, statutes/83.49.txt, statutes/83.682.txt, statutes/83.42.txt, statutes/83.505.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/wants_to_leave_early.yaml version 0.5"
---
## When to load this skill

Load this skill when the tenant wants to move out before the lease term ends. It rests on 83.595 (the landlord's choice of remedies), 83.49 (the deposit and the 7-day notice before leaving), 83.682 (servicemembers), 83.575 (notice at the end of a lease), and 83.505 (notices by e-mail).

- If part of the reason for leaving is that the landlord has not made repairs or kept the unit as required, also load repair_not_made. A way out may run through that skill and 83.56(1).
- Check the other ways out the record points to: military orders (83.682, in this skill), and damage to the unit, such as a fire or a storm. 83.63 may be the relevant section for damage; there is no skill for it, so fetch it with get_statute_section before applying it.
- The statute leaves out some cases. The tool does not decide whether any of them applies; say what the words are and what you would need to know.
  - "This subsection does not apply if the breach is failure to give notice as provided in s. 83.575 ." (Fla. Stat. 83.595(4)(b)). This is about the liquidated damages and early termination fee option below.
  - "The provisions of this section may not be waived or modified by the agreement of the parties under any circumstances." (Fla. Stat. 83.682(5)). The lease cannot take away the servicemember option.
  - "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)). College housing may be an example.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold, one or two things at a time and only what your answer turns on. Never ask whether something meets a term of the statute or the lease; ask what happened, then apply the term yourself.

### In the lease (search_lease; try a second wording if the first finds nothing)

- Any term on notice before moving out early, next to the 7-day notice below.
- The date the lease term ends, next to the date the tenant plans to move out.
- The monthly rent, next to any early termination amount.
- Where and how the tenant's notice must be sent under the lease.
- Any early termination addendum, and whether roommates who stay on are liable for the whole rent.

### From the tenant

- What date do they plan to move out?
- Does the lease have a fixed end date (for example, a one-year lease), and what date does the term end?
- How much is the monthly rent? (Only if the lease does not show it.)
- Why do they want to leave early, in their own words? Is part of the reason that the landlord has not made repairs or kept the unit as required?
- Does the lease, or another paper they signed with it, set an early termination fee or liquidated damages for leaving early? Where is that fee written (in a separate paper signed with the lease, only in the lease itself, in the lease and in a separate paper, or they do not know), and what amount does it set?
- Have they given the landlord anything in writing saying they are moving out? How did it reach the landlord (handed to the landlord or the office, regular mail, certified mail, e-mail, a resident portal request or message, a text message, or something else), and what date was it delivered?
- Are they a servicemember (including the National Guard or reserves) with military orders that affect where they live? If so, have they given the landlord a written notice of termination with a copy of the orders or a letter from the commanding officer, and what date did the landlord receive it?

### What the deadlines count from

The program computes dates only from facts the tenant has confirmed, so get these proposed and confirmed:

- The date the tenant plans to move out. The 7 days' notice count back from it.
- For a servicemember, whether the termination notice with the orders was given, and the date the landlord received it. The 30 days count from that date.

### Evidence to suggest the tenant keep

- The lease and any early termination addendum.
- The written notice of leaving, with proof of certified mail or personal delivery.
- The forwarding address given to the landlord.
- For a servicemember, the orders or the commanding officer's letter sent with the notice.
- Move-out photos and the key return date.

## What the tenant can do

Tell the tenant first whether they can do each of these and what it turns on, before any step. Each condition is settled by the lease (read that clause with search_lease and say what it says), by the tenant (ask), by the program's deadlines (call get_deadlines), or not at all (the statute does not settle it: give every reading, see the open questions below). A few conditions are outside the tool, such as the military orders themselves; say what the tenant must check.

Lease override to show: 83.49(5) begins "Except when otherwise provided by the terms of a written rental agreement" (Fla. Stat. 83.49(5)), so read the lease's term on notice before moving out. The servicemember option cannot be changed by the lease (the exclusion above).

### End the lease as a servicemember with military orders, by written notice with the orders, effective at least 30 days after the landlord receives it (Fla. Stat. 83.682(1))

Both conditions must be met.

1. The tenant is a servicemember: "Any servicemember may terminate his or her rental agreement" (Fla. Stat. 83.682(1)). The tenant can tell you. If they say they are not one, this option is closed.
2. The orders meet one of the criteria the statute lists: "if any of the following criteria are met" (Fla. Stat. 83.682(1)). This is outside the tool: the tenant checks the military orders against the criteria in 83.682(1) (a permanent change of station of 35 miles or more, a discharge or release from active duty, orders into government quarters, temporary orders of more than 60 days to 35 miles or more away, and the others). See the third open question.

Steps, in order:

1. A written notice of termination to the landlord, with a copy of the orders or a letter from the commanding officer: "The notice to the landlord must be accompanied by either a copy of the official military orders or a written verification signed by the servicemember’s commanding officer." (Fla. Stat. 83.682(2)). Ask whether the tenant has given it.
2. The termination takes effect at least 30 days after the landlord receives the notice: "at least 30 days after the landlord’s receipt of the notice" (Fla. Stat. 83.682(1)). The program's deadlines show the earliest date, counted from the date the landlord received the notice.

### Leave early and pay the early termination fee or liquidated damages the lease sets, in place of the landlord's other remedies (Fla. Stat. 83.595(4))

All three conditions must be met.

1. The tenant signed a separate addendum agreeing to the fee or liquidated damages when the lease was made: "This remedy is available only if the tenant and the landlord, at the time the rental agreement was made, indicated acceptance of liquidated damages or an early termination fee." (Fla. Stat. 83.595(4)). It is met in either way:
   - The fee is written in a separate paper the tenant signed with the lease: "The tenant must indicate acceptance of liquidated damages or an early termination fee by signing a separate addendum to the rental agreement" (Fla. Stat. 83.595(4)). The tenant can tell you. If they say the fee is written only in the lease itself, not in a separate paper, the landlord's other remedies in 83.595 apply.
   - Where the fee is written is not known yet. The tenant checks the papers signed with the lease for a separate one agreeing to the fee or liquidated damages.
2. The amount is no more than 2 months' rent: "if the amount does not exceed 2 months’ rent" (Fla. Stat. 83.595(4)). The tenant checks the amount the fee or liquidated damages come to, beside two months' rent.
3. For a fee, the lease asks for no more than 60 days' notice before the early termination: "the tenant is required to give no more than 60 days’ notice, as provided in the rental agreement, prior to the proposed date of early termination" (Fla. Stat. 83.595(4)). The lease settles this: read its clause on notice before an early termination with search_lease and say what it says. See the second open question.

The step: the notice the lease asks for, given to the landlord: "as provided in the rental agreement, prior to the proposed date of early termination" (Fla. Stat. 83.595(4)). If the tenant has already given a notice, ask whether it is the one the lease asks for before an early termination, in its time and way, and read that clause. Which remedy the landlord picks is open (the first open question).

### Give the landlord 7 days' written notice before leaving, by certified mail or in person, with an address, so the landlord stays held to the deposit's notice of a claim (Fla. Stat. 83.49(5))

Both conditions must be met.

1. The last day to give that notice has not passed, or the notice already went out by it: "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises" (Fla. Stat. 83.49(5)). It is met in either way:
   - The last day has not passed. Only the program's deadlines settle this. If they show it has passed, say so.
   - The notice already given went out by the last day, by certified mail or in person, with an address. Ask the date it reached the landlord, to put beside the last day the program's deadlines show.
2. The lease does not provide otherwise on notice before moving out: "Except when otherwise provided by the terms of a written rental agreement" (Fla. Stat. 83.49(5)). The lease settles this: read its clause on notice before moving out early with search_lease and say what it says.

The step: the written notice, with the address where the tenant can be reached, delivered to the landlord by certified mail or in person: "which notice must include the address where the tenant may be reached" (Fla. Stat. 83.49(5)).

- If the notice went by certified mail or by hand, ask the tenant to check that it gave the address where they can be reached.
- If it went by e-mail, it counts only as 83.505 allows. Ask whether the tenant and the landlord signed an addendum agreeing to notices by e-mail, and whether the notice gave the address. Read the lease's clause on notices to the landlord.
- If it went some other way, ask how it reached the landlord, beside the ways 83.49(5) names, certified mail or personal delivery.

## Deadlines

The program computes and prints every date from confirmed facts. Never write, count, or compare a date yourself: call get_deadlines, and say a deadline has passed or is upcoming only as its result says. The counting rule is an assumption: Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. The program computes no date from a period the lease sets, such as the notice for an early termination fee.

- The tenant's 7 days' written notice before leaving. It counts back from the date the tenant plans to move out, not forward from the notice date. It goes by certified mail or personal delivery, with an address where the tenant can be reached: "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which notice must include the address where the tenant may be reached" (Fla. Stat. 83.49(5)). If it is missed: "Failure to give such notice relieves the landlord of the notice requirement of paragraph (3)(a) but does not waive any right the tenant may have to the security deposit or any part of it." (Fla. Stat. 83.49(5)). The lease can provide otherwise (quoted above).
- The servicemember's earliest termination date. It counts from the date the landlord received the notice, and only when the servicemember notice was given: "written notice of termination to be effective on the date stated in the notice which is at least 30 days after the landlord’s receipt of the notice" (Fla. Stat. 83.682(1)).

## What the statute does not settle

Each of these has no listed readings. For each, say what the tool does not work out, apply the text to what the tenant reports, and pick no answer for the law.

### Which remedy the landlord chooses

83.595 lists what the landlord may do when a tenant surrenders or abandons the unit, in four subsections: end the tenancy and the tenant's liability; relet for the tenant's account, where the landlord has "a duty to exercise good faith in attempting to relet the premises" (Fla. Stat. 83.595(2)); stand by and hold the tenant liable for rent as it comes due; or charge liquidated damages or an early termination fee under a separate addendum. The choice is the landlord's. Lay the four beside what the record holds (the addendum, its amount, the monthly rent) so the tenant sees what each would mean. Never say which the landlord will choose, and never give one amount owed.

### The notice period for an early termination fee

83.595(4) refers to an early termination fee where "the tenant is required to give no more than 60 days’ notice, as provided in the rental agreement, prior to the proposed date of early termination" (Fla. Stat. 83.595(4)). The period comes from the lease, and the tool does not compute a date from a period the lease sets.

### Whether the servicemember criteria are met

83.682(1) applies only "if any of the following criteria are met" (Fla. Stat. 83.682(1)), and 83.682(2) says the notice "must be accompanied by either a copy of the official military orders or a written verification signed by the servicemember’s commanding officer" (Fla. Stat. 83.682(2)). Apply the criteria and the documents to what the tenant reports. A criterion the record does not show is not known yet.

### Damage to the unit

If the tenant is leaving because the unit was damaged or destroyed (for example, by fire or a storm), 83.63 may be the relevant section. There is no skill for it. Fetch it with get_statute_section before applying it, and say the tool does not compute anything for it.

## Letters

The tenant sends every letter; you send nothing. Every letter holds: today's date, the planned move-out date, the forwarding address, what the tenant asks for, and the delivery method. The postures, each line as written:

- preserve: States the planned move-out date and a forwarding address, and asks the landlord to confirm what, if anything, the landlord will charge. Cites nothing.
- assert: Adds the 83.49(5) sentence on notice before vacating, quoted.
- escalate: Adds the 83.595(4) sentence on liquidated damages or an early termination fee, quoted.

When a letter is shown, tell the tenant that the program computes the 7-day date in 83.49(5), which requires "at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which notice must include the address where the tenant may be reached" (Fla. Stat. 83.49(5)), counted back from the move-out date they gave. The letter is that notice only if it is sent that way and gives their new address.

The tenant delivers the letter. Read the lease's clause on where and how notices to the landlord must be sent (search_lease), and quote it when you ask how they will send it.

## Mistakes to avoid

- Stating what the tenant will owe as one amount. 83.595 lists the landlord's choices.
- Applying 83.595(4)'s fee or liquidated damages without the separate addendum, which the tenant must accept "by signing a separate addendum to the rental agreement" (Fla. Stat. 83.595(4)).
- Applying 83.595(2) without the landlord's "duty to exercise good faith in attempting to relet the premises" (Fla. Stat. 83.595(2)).
- Missing a way out the record points to, such as the landlord's noncompliance (through the repair skill and 83.56(1)), military orders (83.682), or damage to the unit (83.63).
- Counting the 7 days from the notice date instead of back from the move-out date.
- Computing a period the lease sets, such as the notice for an early termination fee.
- Computing any date yourself.
