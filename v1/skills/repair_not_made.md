---
name: repair_not_made
description: "Something in the unit needs repair and the landlord has not fixed it."
sections: ["83.51", "83.56", "83.60", "83.64", "83.42", "83.505"]
clocks:
  - id: seven_days_after_termination_notice
    actor: landlord
    trigger: message_date
    days: 7
    direction: after
    applies_if: message_mentions_ending
    cite: "83.56(1)"
    quote: "If the landlord materially fails to comply with s. 83.51 (1) or material provisions of the rental agreement within 7 days after delivery of written notice by the tenant specifying the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof, the tenant may terminate the rental agreement."
    condition: "your message was delivered in a way 83.56(4) allows and says you intend to end the lease because of the problem, which this tool does not decide"
  - id: seven_days_after_withholding_notice
    actor: landlord
    trigger: message_date
    days: 7
    direction: after
    applies_if: message_mentions_rent
    cite: "83.60(1)(b)"
    quote: "The defense of a material noncompliance with s. 83.51 (1) may be raised by the tenant if 7 days have elapsed after the delivery of written notice by the tenant to the landlord, specifying the noncompliance and indicating the intention of the tenant not to pay rent by reason thereof."
    consequence: "A material noncompliance with s. 83.51 (1) by the landlord is a complete defense to an action for possession based upon nonpayment of rent"
    condition: "your message was delivered to the landlord and says you intend not to pay rent because of the problem, which this tool does not decide"
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.51.txt, statutes/83.56.txt, statutes/83.60.txt, statutes/83.42.txt, statutes/83.505.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/repair_not_made.yaml version 0.6"
---
## When to load this skill

Load this skill when something in the unit needs repair and the landlord has not fixed it: the roof, a window or a door, a floor, steps, or a porch, an outside wall or the foundation, pipes, drains, toilets, or faucets, heat, running water, hot water, the air conditioning, an appliance, pests, locks or keys, electrical work, mold, or a common area such as a hallway.

It covers two things the tenant may do about it: end the lease, or not pay rent because of the problem and raise it as a defense if the landlord sues for possession. It also covers the written notice each one starts from. It does not decide whether a local building, housing, or health code covers the problem; the tool does not hold those codes.

If the landlord has also sent a written demand for unpaid rent, or has filed an eviction case, load notice_received_nonpayment too.

The statute leaves some housing out of this part: "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)) This matters when the tenant lives in college housing. The tool records the facts and does not decide whether this applies to the tenant's housing. Say that it could matter and that the tool does not decide it.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold. Never ask whether something meets a term of the statute or the lease; you apply the term to their answer.

### From the lease (search_lease)

- The maintenance and repairs clause: does it say the landlord repairs this kind of problem, and does an exception leave this problem out (such as damage caused by a roommate or a guest)? Try a second wording if the first finds nothing.
- The notices clause: where and how the tenant's written notice must be sent to the landlord, and whether it mentions notices by e-mail.
- Anything it says about repairs the tenant pays for.

### From the tenant

- What the problem is, in their own words, and which part of the unit it is with. Offer the plain choices: the roof; a window or a door; a floor, steps, or a porch; an outside wall or the foundation; another part of the building's structure; pipes, drains, toilets, or faucets; heat; running water; hot water; the air conditioning; an appliance; pests; locks or keys; electrical; mold; a common area; something else.
- When it started, or when they first noticed it.
- Whether they rent a single-family house or a duplex, rather than a unit in an apartment building or a dorm.
- Who or what caused it, as far as they know: nothing anyone did (age, wear, weather), the landlord or its workers, they themselves, a family member who lives with them, a guest or someone else they let in, a roommate, someone they did not let in (a neighbor, a stranger), or they do not know.
- Whether they have sent the landlord or the office anything in writing about it (a letter, an e-mail, a resident portal request, a text). If so: how it reached the landlord (handed over, regular mail, certified mail, e-mail, a resident portal, a text, something else); the date it reached the landlord (the day it was handed over or sent, or the delivery date on a mail receipt); whether it says anything about ending the lease or moving out; whether it says anything about not paying rent; and the sentences that say what they asked for and what they will do if the problem is not fixed, word for word. If they sent more than one, ask about the one that says the most about what they will do.
- Whether they have paid rent since they knew about the problem.
- What the landlord has said or done about it so far.
- Whether the landlord has filed an eviction case against them.

### What the deadlines count from

The program computes the two 7-day deadlines (see Deadlines) only from facts the tenant has confirmed: the date the tenant's written message was delivered to the landlord, whether that message says they intend to end the lease because of the problem, and whether it says they intend not to pay rent because of it. When the tenant tells you one of these, propose it for their record, so they can confirm it.

### Evidence worth keeping

- Photos or video of the condition, with dates.
- The written notice, with proof of how and when it was delivered.
- Every reply from the landlord, with dates.
- Any code enforcement complaint or inspection report.
- Rent receipts for the months since the problem started.

## What the tenant can do

Before any step, say whether the tenant can do it, what that turns on, and what is left to do. Each condition below is settled in one of four ways. The lease can settle it: read that clause with search_lease and say what it says. The tenant can tell you. It is not settled: give the open question from the section below. Or it is outside the tool: say what to check and where.

### End the lease because the landlord has not made the repair

The statute's answer to a landlord who does not act: "the tenant may terminate the rental agreement." (Fla. Stat. 83.56(1)) The full sentence is under Deadlines. All four conditions need to be met.

1. The landlord had a duty to fix this problem, under 83.51(1) or a material provision of the lease. The statute reaches a failure to comply with 83.51(1) "or material provisions of the rental agreement" (Fla. Stat. 83.56(1)). Any one of these ways meets it:
   - The problem is with the structure or the plumbing. 83.51(1)(b) says: "maintain the roofs, windows, doors, floors, steps, porches, exterior walls, foundations, and all other structural components in good repair and capable of resisting normal forces and loads and the plumbing in reasonable working condition" (Fla. Stat. 83.51(1)(b)). The tenant's pick tells you: the roof, a window or door, a floor, steps, or porch, an outside wall or the foundation, another structural part, or pipes, drains, toilets, or faucets. Any other pick is not plainly one of these parts.
   - The problem is running water or hot water. It may be the plumbing 83.51(1)(b) names, or an item only 83.51(2)(a) names: "Functioning facilities for heat during winter, running water, and hot water." (Fla. Stat. 83.51(2)(a)) This is not settled; give the open question on subsection (1) or (2).
   - The tenant picked 'something else'. Ask what the problem is with, beside the structural parts and the plumbing 83.51(1)(b) names.
   - The lease says the landlord repairs this problem (lease). Read the maintenance and repairs clause, say what it says, and say whether an exception leaves this problem out.
   - A building, housing, or health code where the unit is requires the landlord to fix it: "Comply with the requirements of applicable building, housing, and health codes" (Fla. Stat. 83.51(1)(a)). This is outside the tool. The city or county code enforcement office can say whether a code covers the problem, and can inspect the unit. Send the tenant there.
2. The landlord's duty was not changed in writing. The statute names a change in writing only for one kind of home: "The landlord’s obligations under this subsection may be altered or modified in writing with respect to a single-family home or duplex." (Fla. Stat. 83.51(1)) This is met when the tenant's unit is not a single-family home or duplex (tenant). If it is one, read the lease's maintenance and repairs clause (lease), and ask whether they signed anything else that changes who repairs. The tool does not decide the effect of such a writing.
3. The tenant's side did not cause the problem: "The landlord is not responsible to the tenant under this section for conditions created or caused by the negligent or wrongful act or omission of the tenant, a member of the tenant’s family, or other person on the premises with the tenant’s consent." (Fla. Stat. 83.51(4)) Met when the cause is nothing anyone did, the landlord or its workers, or someone the tenant did not let in (tenant). If the tenant, a family member who lives with them, or a guest caused it, the cause is not outside the people 83.51(4) names; say so. A roommate is not settled; give the open question on roommates. If they do not know the cause, say a work order, a technician's note, or the landlord's messages may show it.
4. The tenant did not give up ending the lease by paying rent while knowing of the problem: "the tenant pays rent with actual knowledge of a noncompliance by the landlord" (Fla. Stat. 83.56(5)(a)). Met when no rent was paid since they knew (tenant). If rent was paid, whether that gave up ending the lease over a problem still not fixed is not settled; give the open question on rent paid.

Steps, in order:

1. Deliver a written notice to the landlord in a way 83.56(4) allows: "The delivery of the written notices required by subsections (1)-(3) shall be by mailing, delivering a true copy thereof, e-mailing in accordance with s. 83.505" (Fla. Stat. 83.56(4)). Handed over, regular mail, or certified mail fits. E-mail counts only as 83.505 allows: ask whether the tenant and the landlord signed an addendum agreeing to notices by e-mail, and read the lease's notices clause. A resident portal message or a text is not one of the ways the sentence names. For any other way, ask how the message reached the landlord and set it beside those ways.
2. The notice names the problem and says the tenant intends to end the lease because of it: "specifying the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof" (Fla. Stat. 83.56(1)). Set the words of the tenant's message beside these words and say what you see. If the tenant says the message says nothing about ending the lease, it does not state that intention.
3. Seven days pass after the notice is delivered without the landlord fixing the problem: "within 7 days after delivery of written notice by the tenant" (Fla. Stat. 83.56(1)). The program computes the date.

Whether the landlord's failure is 'material' is not settled; give the open question on that word.

### Not pay rent because of the problem, and raise it as a defense

The statute: "A material noncompliance with s. 83.51 (1) by the landlord is a complete defense to an action for possession based upon nonpayment of rent" (Fla. Stat. 83.60(1)(b)). All three conditions need to be met. This defense rests on the duty in 83.51(1) alone: "The defense of a material noncompliance with s. 83.51 (1) may be raised by the tenant" (Fla. Stat. 83.60(1)(b)). A lease provision by itself does not reach it.

1. The problem is a failure of a duty in 83.51(1). Any one of these ways: the problem is with the structure or the plumbing (the tenant's pick, as for ending the lease); running water or hot water (not settled; give the open question on subsection (1) or (2)); 'something else' (ask what it is with); or a code where the unit is requires the landlord to fix it (outside the tool; send the tenant to the code enforcement office, as for ending the lease).
2. The landlord's duty was not changed in writing: the same condition as for ending the lease.
3. The tenant's side did not cause the problem: the same condition as for ending the lease, including the roommate question.

Steps, in order:

1. Deliver the written notice to the landlord: "7 days have elapsed after the delivery of written notice by the tenant to the landlord" (Fla. Stat. 83.60(1)(b)). If it was handed over or mailed (regular or certified), it was delivered. For e-mail, a resident portal, a text, or anything else, the statute names no way of delivering this notice; give the open question on delivery.
2. The notice names the problem and says the tenant intends not to pay rent because of it: "specifying the noncompliance and indicating the intention of the tenant not to pay rent by reason thereof" (Fla. Stat. 83.60(1)(b)). Set the words of the tenant's message beside these words and say what you see.
3. Seven days pass after the notice is delivered. The program computes the date.

Two open questions apply: what 'material' means, and the court's rule once a case is filed. If the record shows an eviction case was filed, apply the registry requirement itself (see the open question on court procedure); the tool does not compute its date.

### Overrides and exclusions

- A lease can alter the landlord's duty in the one case in condition 2 above. The tool does not decide its effect.
- "Nothing in this part authorizes the tenant to raise a noncompliance by the landlord with this subsection as a defense to an action for possession under s. 83.59" (Fla. Stat. 83.51(2)(c)). This is about the items in 83.51(2): extermination, locks and keys, common areas, garbage, heat, running water, and hot water.
- Paying rent while knowing of the problem: "if the tenant pays rent with actual knowledge of a noncompliance by the landlord or accepts performance by the landlord of any other provision of the rental agreement that is at variance with its provisions, the landlord or tenant waives his or her right to terminate the rental agreement or to bring a civil action for that noncompliance, but not for any subsequent or continuing noncompliance." (Fla. Stat. 83.56(5)(a))

## Deadlines

The program computes two deadlines. Both are the landlord's, and both count from the date the tenant's written message was delivered to the landlord, not the date it was sent, once the tenant has confirmed that date. How the message was delivered matters to both: the ways are in the first step of each option above.

- Seven days to fix the problem after a notice to end the lease. It counts only when the message says the tenant intends to end the lease because of the problem. The statute: "If the landlord materially fails to comply with s. 83.51 (1) or material provisions of the rental agreement within 7 days after delivery of written notice by the tenant specifying the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof, the tenant may terminate the rental agreement." (Fla. Stat. 83.56(1)) The program prints the date with this condition: the message was delivered in a way 83.56(4) allows and says the tenant intends to end the lease because of the problem. The tool does not decide that. Do not say the message meets it.
- Seven days after a notice not to pay rent. It counts only when the message says the tenant intends not to pay rent because of the problem. The statute: "The defense of a material noncompliance with s. 83.51 (1) may be raised by the tenant if 7 days have elapsed after the delivery of written notice by the tenant to the landlord, specifying the noncompliance and indicating the intention of the tenant not to pay rent by reason thereof." (Fla. Stat. 83.60(1)(b)) What follows from it: "A material noncompliance with s. 83.51 (1) by the landlord is a complete defense to an action for possession based upon nonpayment of rent" (Fla. Stat. 83.60(1)(b)). The program prints the date with this condition: the message was delivered to the landlord and says the tenant intends not to pay rent because of the problem. The tool does not decide that either.

The program computes and prints every date. Never write, count, or compare a date yourself, not even for 'what if it ran from another day'. Whether a deadline has passed comes only from the program's deadlines (get_deadlines). The program prints the counting convention with each date: calendar days, the delivery day not counted, no weekend or holiday adjustment. It is an assumption: Florida's court rule for counting days has not been checked against these statutory deadlines. If the tenant asks how the days are counted, say so.

## What the statute does not settle

For each question below, tell the tenant in plain words that the law does not settle it, give every reading with what it would mean for them, and pick none. Where one step works under every reading, say so.

- Which code applies. 83.51(1)(a) points to "the requirements of applicable building, housing, and health codes" (Fla. Stat. 83.51(1)(a)). Those codes are not in the tool, so whether a condition violates a code cannot be applied here; say so. The list in 83.51(1)(b) applies "Where there are no applicable building, housing, or health codes" (Fla. Stat. 83.51(1)(b)).
- What 'material' means. Both 7-day periods concern a landlord who "materially fails to comply" (Fla. Stat. 83.56(1)) or a "material noncompliance" (Fla. Stat. 83.60(1)(b)). The stored text does not define it. Set the tenant's description of the problem, how long it has lasted, and the landlord's response beside the word.
  - A failure is material when it is a failure of a duty 83.51(1) lists (the codes; roofs, windows, doors, floors, steps, porches, exterior walls, foundations, other structural parts; the plumbing), whatever its size.
  - Material turns on degree: how serious the condition is, how long it has lasted, and how it affects living in the unit, so a failure of a listed duty can still be minor.
- Subsection (1) or (2). 83.51(1) covers the codes and the structure and plumbing. 83.51(2)(a) adds, for a unit other than a single-family home or duplex and "Unless otherwise agreed in writing" (Fla. Stat. 83.51(2)(a)), extermination, locks and keys, common areas, garbage removal, and heat, running water, and hot water. 83.56(1) and 83.60(1)(b) speak only of 83.51(1), and 83.51(2)(c) says part II does not let the tenant raise a noncompliance with subsection (2) as a defense to an action for possession. Apply the lists to the problem. What stays open is an item subsection (2) names that a code, or the plumbing 83.51(1)(b) names, may also cover, such as running water and hot water.
  - It is a subsection (1) duty when a code covers it or it is part of the plumbing, and 83.51(3) says that when subsection (1)'s duty is the same or greater, "the landlord’s duty is determined by subsection (1)" (Fla. Stat. 83.51(3)).
  - It is a subsection (2) duty because subsection (2) names it, so 83.56(1) and 83.60(1)(b) do not reach it.
- Court procedure. Once an eviction case is filed, 83.60(2) requires a tenant who raises "any defense other than payment" (Fla. Stat. 83.60(2)) to pay the rent into the registry of the court, within "5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process" (Fla. Stat. 83.60(2)). Apply the requirement itself when the record shows a case was filed. The tool counts calendar days only and does not compute that date.
- Rent paid with knowledge. 83.56(5)(a) says that if the tenant "pays rent with actual knowledge of a noncompliance by the landlord" (Fla. Stat. 83.56(5)(a)), the tenant waives the right "to terminate the rental agreement or to bring a civil action for that noncompliance, but not for any subsequent or continuing noncompliance" (Fla. Stat. 83.56(5)(a)). Set the rent paid since the tenant knew of the problem beside it, and whether the problem goes on.
  - A problem the landlord still has not fixed is a continuing noncompliance, so paying rent while it goes on does not waive ending the lease over it.
  - The noncompliance is the landlord's failure to fix the problem the tenant already knew of; paying rent with that knowledge waives ending the lease over it, and only a new or different failure starts over.
- A roommate who caused it. 83.51(4) leaves the landlord not responsible for conditions caused by "the negligent or wrongful act or omission of the tenant, a member of the tenant’s family, or other person on the premises with the tenant’s consent" (Fla. Stat. 83.51(4)). The stored text does not say whether a roommate is such a person, in particular one the landlord placed in the unit. Set who caused the problem, and how the roommate came to live there, beside it.
  - A roommate who lives in the unit the tenant shares is on the premises with the tenant's consent, so the landlord is not responsible to the tenant for a condition the roommate caused by a negligent or wrongful act.
  - A roommate the landlord placed, under a lease of the roommate's own, is on the premises by the landlord's leave, not the tenant's consent, so 83.51(4) does not reach what the roommate caused, and the landlord stays responsible to the tenant.
- How the rent notice is delivered. 83.60(1)(b) runs its 7 days from "the delivery of written notice by the tenant to the landlord" (Fla. Stat. 83.60(1)(b)) and names who may receive it, but names no way of delivering it. 83.56(4)'s ways are for "the written notices required by subsections (1)-(3)" (Fla. Stat. 83.56(4)) of 83.56, and 83.505 lets a party e-mail "any notices required under this part" (Fla. Stat. 83.505) once both have signed its addendum. Set beside it how the tenant's message reached the landlord.
  - 83.60(1)(b) names no way, so a written notice that reaches the landlord, or a person it names, is delivered however it was sent, by e-mail or the resident portal included.
  - The ways part II gives for notices apply to this one too, so a notice by e-mail counts only under an 83.505 addendum, and a resident portal request or a text is not a delivered notice.

## Letters

Every letter needs: today's date, the condition and when it started, the repair requested, the response deadline the tenant chooses, and how the tenant will deliver it. The tenant sends the letter; you send nothing. Read the lease's notices clause with search_lease and tell the tenant where and how the lease says notices go to the landlord.

The postures, each with its own line:

- preserve: Describes the condition and asks for the repair. Cites nothing.
- assert: Adds the 83.51(1) duty, quoted.
- escalate: Adds the 83.56(1) sentence, quoted.

When a letter is shown, tell the tenant this. The 7-day periods the program computes run from the delivery of a written notice. In 83.56(1) that is a notice "specifying the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof" (Fla. Stat. 83.56(1)), and in 83.60(1)(b) one "specifying the noncompliance and indicating the intention of the tenant not to pay rent by reason thereof" (Fla. Stat. 83.60(1)(b)). The letter states the tenant's request and any sentences quoted in it. It is such a notice only if it states one of those intentions. Offer to apply this to the letter before the tenant sends it.

## Mistakes to avoid

- Treating any written complaint as the notice in 83.56(1) or 83.60(1)(b). Each must state an intention: to end the lease, or not to pay rent.
- Saying the tenant may withhold rent for an item only 83.51(2) lists. 83.60(1)(b) speaks of "a material noncompliance with s. 83.51 (1)" (Fla. Stat. 83.60(1)(b)). For ending the lease, 83.56(1) also reaches "material provisions of the rental agreement" (Fla. Stat. 83.56(1)), so read the lease's repair clause.
- Counting the 7 days yourself, or from the date the notice was sent instead of delivered. Whether they have passed comes from get_deadlines.
- Skipping 83.56(5)(a): paying rent with knowledge of the problem, and the continuing-noncompliance exception.
- Applying 83.51 to a condition the tenant's side caused (83.51(4)).
- Explaining rent withholding without 83.60(2): once a case is filed, any defense other than payment requires paying the rent into the registry of the court.
- Computing any date yourself.
