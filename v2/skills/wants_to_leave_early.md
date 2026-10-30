---
name: wants_to_leave_early
description: The tenant wants to move out before the lease's end date, or asks what leaving early would cost them.
---
# Wants to leave early

Rests on 83.595 (what the landlord may do), 83.43 (what an early termination fee and a security deposit are), 83.49 (the 7-day notice, and interest), 83.682 and 83.64 (servicemembers, and retaliation), 83.63 (damage to the home), 83.512 (flooding), 83.46, 83.57, and 83.575 (no set end date, and staying on after one), 83.56 and 83.505 (how notices are delivered), 83.47 (void lease clauses), 83.48 (attorney fees), and 83.59 and 83.67 (abandonment, and belongings left behind). Read a section in full with get_statute_section.

When the answer turns on a point marked not settled, the first sentence says it is not settled and leans neither way (never "probably yes").

## First, whether this applies

- Load who_the_law_covers, unless the facts already hold school_housing.
- The landlord has failed to make a repair or keep a lease promise, and that is part of why they want out: load repair_not_made too. Its option 1 is a way to end the lease; do not repeat it here.
- The landlord sent a notice saying the tenant broke the lease: load notice_received_violation too. Its "Moving out" part says what is not settled about rent after a landlord ends the lease.
- The tenant has already moved out and asks about the deposit: load deposit_not_returned.
- The lease has no set end date (month to month, or no term stated, "the duration is determined by the periods for which the rent is payable" (83.46(2))): leaving is not early. Written notice ends it, delivered a way 83.56(4) names, by the rent period (83.57(1) to (4)); for month to month "by giving not less than 30 days’ notice prior to the end of any monthly period" (83.57(3)). The last day for that: count_days(period_end, -30), with period_end the last day of the month they plan to end on. A tenant who stayed on with the landlord's permission after a set term ended, and leaves without that notice: "the tenant is liable to the landlord for an additional 1 month’s rent." (83.575(3)). For a tenancy that was month to month from the start, that is not settled. Give both readings and choose neither. One: (3) names the month-to-month notice, so it applies. The other: the section is about a tenancy "with specific duration" (83.575), so it does not. The 7 days' notice below also applies to them. The options below do not.

## What the lease adds

Read the whole lease, addenda included, for: the end date; any clause or addendum on ending the lease early or on what is owed for it; any notice before leaving; subletting or bringing in a replacement; and who else signed. Quote each clause and cite it. A box counts only if it is marked.

- A set charge for leaving early, whatever the lease calls it (a fee, a re-rental charge, losing the deposit): "“Early termination fee” means any charge, fee, or forfeiture that is provided for in a written rental agreement and is assessed to a tenant when a tenant elects to terminate the rental agreement, as provided in the agreement, and vacates a dwelling unit before the end of the rental agreement." (83.43(6)). If it is not that, it is liquidated damages, which the stored text does not define. Either way the name does not save it: 83.595(4) covers both, and it counts only if it meets option 5's conditions. The definition leaves out rent and charges through the end of the month the landlord retakes the home, charges for damage, and a deal to settle or buy out the lease (83.43(6)).
- Any other clause setting what happens on leaving early, such as all the remaining rent falling due at once: 83.595 lists no such choice. Whether the clause stands is not settled. Give both readings and choose neither. One: it is void to the extent it "Purports to waive or preclude the rights, remedies, or requirements set forth in this part." (83.47(1)(a)), or it is a charge that needs option 5's conditions, since the definition leaves out rent only through that month. The other: 83.595 says what the landlord may do after a tenant leaves and does not bar a term both sides agreed to.
- A clause on subletting or a replacement tenant: say what it says. The stored text does not speak to subletting; anything past the lease's words is outside this tool.
- Someone else signed and stays: the stored text does not say what happens when one of several tenants leaves. Say what the lease says about each signer's share of the rent.

## Facts the answer turns on

Read the lease first. Ask the tenant only plain facts, one or two at a time. Note each fact with note_fact under these names, dates written YYYY-MM-DD; a date counts only once the tenant has confirmed it.

- planned_move_out: the date they plan to move out. lease_end_date: the date the lease ends.
- reason: why they want to leave, in their words.
- leaving_notice_given: the date they gave the landlord a written notice that they are leaving, how it went, and whether it gave an address.
- early_addendum: only if the lease you hold does not show it, whether they signed a separate paper about a fee for leaving early, which box is marked, and the amount.
- Only if the reason points to one: orders (what the military orders say, and how far away), servicemember_notice_received (the date the landlord received the written notice), damage_date and what was damaged (and who or what caused it), flood_loss_date.

## How to answer

Give only the options the facts point to, and name the others in one line (military orders, damage to the home, flooding, a landlord who failed a duty), so the tenant can say if one fits. When the facts point to none of those, say that part II names no right to end a lease with a set end date just because the tenant wants to move. The tenant can move out, but moving out or giving notice does not by itself end the lease or stop the rent. What they owe then depends on options 4 to 6.

## Option 1: military orders

All of these must be met.

1. **A servicemember.** The term has "the same meaning as provided in s. 250.01" (83.43(15)), which is not stored; the tenant can say whether they are one.
2. **One of the listed grounds** (83.682(1)(a) to (f)). Ask what the orders say:
   - "required, pursuant to a permanent change of station orders, to move 35 miles or more from the location of the rental premises" (83.682(1)(a));
   - "prematurely or involuntarily discharged or released from active duty or state active duty" (83.682(1)(b));
   - released from active duty after leasing while on active duty, with the home 35 miles or more from the home of record (83.682(1)(c));
   - "After entering into a rental agreement" (83.682(1)(d)), orders into government quarters, or becoming eligible for them and choosing to move there (83.682(1)(d));
   - "temporary duty orders, temporary change of station orders, or state active duty orders to an area 35 miles or more from the location of the rental premises, provided such orders are for a period exceeding 60 days" (83.682(1)(e));
   - a change of orders to 35 miles or more away, before moving in (83.682(1)(f)).
   Orders or a move that fit none of these: not met. Say so in one sentence and go on to the other options.
3. **A written notice with proof.** "The notice to the landlord must be accompanied by either a copy of the official military orders or a written verification signed by the servicemember’s commanding officer." (83.682(2)).
4. **The date.** The notice takes effect "on the date stated in the notice which is at least 30 days after the landlord’s receipt of the notice" (83.682(1)). The earliest date: count_days(servicemember_notice_received, 30). Before the landlord has it, the last day it must arrive to end the lease on the planned date: count_days(planned_move_out, -30).

What it gives: "the tenant is liable for the rent due under the rental agreement prorated to the effective date of the termination" (83.682(4)), and "The tenant is not liable for any other rent or damages due to the early termination of the tenancy as provided for in this section." (83.682(4)). Terminating 14 or more days before moving in: "no damages or penalties of any kind will be assessable." (83.682(4)). "The provisions of this section may not be waived or modified by the agreement of the parties under any circumstances." (83.682(5)). The landlord may not retaliate for it (83.64(1)(d)). Do not work out the prorated amount.

If the tenant also signed an addendum for a fee or liquidated damages, it is not owed; say so plainly. Ending the lease this way is a right, not a breach, and 83.595 opens "If the tenant breaches the rental agreement" (83.595). A fee is assessed when a tenant terminates "as provided in the agreement" (83.43(6)), and this termination is under the statute. Liquidated damages are damages, which (4) rules out. And no agreement can change this section (83.682(5)).

If the servicemember died on active duty, an adult in the immediate family may end the lease the same way, with the death certificate (83.682(3)).

## Option 2: the home was damaged

"If the premises are damaged or destroyed other than by the wrongful or negligent acts of the tenant so that the enjoyment of the premises is substantially impaired" (83.63), then:

- "The tenant may terminate the rental agreement and immediately vacate the premises." (83.63(1)). The section names no notice and no waiting period.
- Or: "The tenant may vacate the part of the premises rendered unusable by the casualty, in which case the tenant’s liability for rent shall be reduced by the fair rental value of that part of the premises damaged or destroyed." (83.63(1)).

Conditions to settle: what was damaged and how much of the home it took out of use; and who caused it, since damage from the tenant's own wrongful or careless act is outside the section. The stored text does not define "substantially impaired" (83.63): set the tenant's facts beside the words and state no test of your own. Whether a slow problem, like a leak or mold that builds up, is this kind of damage is not settled. Give both readings and choose neither, and load repair_not_made for the other route. One: "damaged or destroyed" (83.63) reaches any damage that does this, and the text never says it must be sudden. The other: the word "casualty" (83.63(1)) may suggest a sudden event. If the lease ends this way, "the landlord shall comply with s. 83.49 (3)." (83.63(1)), the deposit rules. The tenant must get the chance to collect belongings when it is safe, or notice of a date within a reasonable time (83.63(2)).

## Option 3: flooding, with no flood disclosure

All of these must be met.

1. **A lease of a year or longer, with no disclosure.** "A landlord must complete and provide a flood disclosure to a prospective tenant of residential real property at or before the execution of a rental agreement for a term of 1 year or longer." (83.512(1)). "The flood disclosure must be in a separate document." (83.512(1)). Read the lease's papers, and ask whether they were given one. A paper that is blank or false: not settled whether that is a violation, since the rule says "complete and provide" (83.512(1)). The stored text does not say from what date the section applies (its history note cites ch. 2025-166); say so, and that this is outside the tool.
2. **A substantial loss from flooding.** "the total cost of repairs to or replacement of the personal property is 50 percent or more of the personal property’s market value on the date the flooding occurred." (83.512(2)). The tenant can give the amounts. The disclosure's form defines flooding as overflowing water, runoff, and standing rainwater (83.512(1)); not settled whether that limits (2), so that a burst pipe is left out.
3. **Notice and leaving in time.** "by giving a written notice of termination and surrendering possession of the premises to the landlord no later than 30 days after the date of the damage or loss." (83.512(2)). The last day: count_days(flood_loss_date, 30).

What it gives: the lease ends when they give up the home (83.512(2)); the landlord refunds "all rent or other amounts paid in advance under the rental agreement for any period after the effective date of the termination of the rental agreement." (83.512(3)). Rent unpaid from before that date is still owed (83.512(4)).

## Option 4: a deal with the landlord

The landlord may agree to let them go. Charges tied to a "rental agreement settlement, release, buyout, or accord and satisfaction agreement" (83.43(6)) are not an early termination fee, so option 5's limits do not apply to the price. Say what the lease requires for a change (a writing, signed, if it says so), and that the deal should say in writing what is owed and that nothing more is. A "buyout" clause already in the lease from the start: not settled whether it is such a deal or a fee under option 5. Give both readings and choose neither.

## Option 5: pay the fee the tenant agreed to

All of these must be met.

1. **A separate signed addendum, from when the lease was made.** "This remedy is available only if the tenant and the landlord, at the time the rental agreement was made, indicated acceptance of liquidated damages or an early termination fee." (83.595(4)). "The tenant must indicate acceptance of liquidated damages or an early termination fee by signing a separate addendum to the rental agreement" (83.595(4)).
   - A separate signed paper with "I agree" marked, or words that agree to the amount: met.
   - The charge is only in the body of the lease, or "I do not agree" is marked, or no choice is marked: not met. Say plainly the fee cannot be charged this way, whatever the lease says, and go to option 6.
2. **The amount.** "if the amount does not exceed 2 months’ rent" (83.595(4)). Set it beside two months of the lease's rent. If it is more: not met, and the fee falls away; nothing in 83.595(4) cuts an amount down to the limit. Say so plainly, and go to option 6.
3. **For a fee, the notice.** "the tenant is required to give no more than 60 days’ notice, as provided in the rental agreement, prior to the proposed date of early termination." (83.595(4)). Read the lease's notice period. If it is more than 60 days: not met for a fee. The words apply only "in the case of an early termination fee" (83.595(4)). If the paper names both a fee and liquidated damages and asks more than 60 days, whether this limit applies is not settled. Give both readings and choose neither.

What it costs: the amount, and "the rent and other charges accrued through the end of the month in which the landlord retakes possession of the dwelling unit and charges for damages to the dwelling unit." (83.595(4)(a)).

What the landlord gives up: the statute's form says "the landlord waives the right to seek additional rent beyond the month in which the landlord retakes possession." (83.595(4)). If the tenant's addendum says so, say plainly that the landlord gave that up. If it leaves those words out, it is not settled whether it is still the addendum the statute asks for. Give both readings and choose neither. One: the form need only be followed "substantially" (83.595(4)), so the fee stands. The other: those words are what the tenant gets for the fee, so without them there is no fee under option 5, and option 6 applies.

The tenant's notice under the lease: if the lease gives a number of days, the last day is count_days(planned_move_out, -N), with N that number. If it is in months, give the lease's words; the tool counts days only. This subsection does not reach a failure to give the end-of-lease notice in 83.575 (83.595(4)(b)).

## Option 6: move out, and the landlord chooses

"If the tenant breaches the rental agreement for the dwelling unit and the landlord has obtained a writ of possession, or the tenant has surrendered possession of the dwelling unit to the landlord, or the tenant has abandoned the dwelling unit, the landlord may:" (83.595). The choice is the landlord's. Never say which it will pick, and never give one total. Set each beside the tenant's rent and lease end date, in words:

- End it: "Treat the rental agreement as terminated and retake possession for his or her own account, thereby terminating any further liability of the tenant" (83.595(1)).
- Re-rent it for the tenant: "holding the tenant liable for the difference between the rent stipulated to be paid under the rental agreement and what the landlord is able to recover from a reletting." (83.595(2)). The landlord "has a duty to exercise good faith in attempting to relet the premises" (83.595(2)), which means "at least the same efforts to relet the premises as were used in the initial rental or at least the same efforts as the landlord uses in attempting to rent other similar rental units" (83.595(2)); rent received is deducted, and the landlord need not prefer this home over its other vacant ones (83.595(2)).
- Wait: "Stand by and do nothing, holding the lessee liable for the rent as it comes due" (83.595(3)). The re-renting duty is in (2) only.
- The fee, only if option 5's conditions are met. Without them the landlord has the first three; say so.

Say the rent for the rest of the lease, through the end date. Never count the months left or total the rent left.

Also: a suit cuts both ways, since the winner may recover attorney fees and court costs (83.48). The deposit may go toward the loss, since security deposits cover "monetary damage to the landlord caused by the tenant’s breach of lease prior to the expiration thereof." (83.43(14)), but only by the steps in 83.49(3); a lease clause that simply takes it is an early termination fee (above). After the move, deposit_not_returned covers those steps. Court steps and amounts are outside this tool.

A tenant who just stops coming may be treated as having abandoned the home: "In the absence of actual knowledge of abandonment, it shall be presumed that the tenant has abandoned the dwelling unit if he or she is absent from the premises for a period of time equal to one-half the time for periodic rental payments." (83.59(3)(c)), unless "the rent is current or the tenant has notified the landlord, in writing, of an intended absence" (83.59(3)(c)). The landlord may remove what they leave behind after "surrender, abandonment" (83.67(5)); read the lease for a clause on it. If the deposit earns interest, "a landlord is not required to pay interest to a tenant who wrongfully terminates his or her tenancy before the end of the rental term." (83.49(9)).

## Whichever way they leave: the 7 days' notice

Any tenant moving out before the end date, and any tenant with no set end date. It keeps the landlord's duty to send a notice about the deposit. It does not end the lease or stop the rent; say so in the same breath.

- Options 1 and 3 have their own written notice. The stored text does not say whether this one applies too; one written notice by hand or certified mail, with the address, in time for both, meets both.
- Option 2 says "immediately vacate" (83.63(1)) and that the landlord shall follow 83.49(3). Whether a tenant leaving at once still needs these 7 days is not settled. Give both readings and choose neither. One: the rule names "any tenant who vacates or abandons the premises before the expiration of the term" (83.49(5)), so the landlord is relieved of the notice. The other: 83.63 sets its own terms, so the landlord is not.
- The rule: "Except when otherwise provided by the terms of a written rental agreement" (83.49(5)), the tenant "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which notice must include the address where the tenant may be reached." (83.49(5)).
- The last day: count_days(planned_move_out, -7), counted back from the move, not forward from the notice. The stored text does not say whether a certified letter counts from mailing or arrival; handing it over, or mailing it early, meets both.
- Handed over or certified mail, with an address: met. E-mail only under the signed addendum in 83.505(1). A portal message, a text, or regular mail is not one of the ways named.
- The lease has a clause on notice before leaving: read it. A different rule for leaving governs. Whether a clause on some other notice, like the notice before paying a fee, is one that "otherwise provided" (83.49(5)) is not settled; one notice in time for both, by hand or certified mail, with the address, meets both.
- If it is missed: "Failure to give such notice relieves the landlord of the notice requirement of paragraph (3)(a) but does not waive any right the tenant may have to the security deposit or any part of it." (83.49(5)). Say both halves.

## Mistakes to avoid

- Saying a tenant may end a lease with a set end date just by giving notice when no way out fits, or that the 7 days' notice ends the lease or stops the rent.
- Stating one total owed, saying which choice the landlord will make, or counting the months left or the rent left.
- Saying the landlord must re-rent the home in every case. The duty is in 83.595(2) only.
- Applying a fee, a charge, or a loss of the deposit without the separate signed addendum and the other conditions, or treating what the lease calls a charge as deciding what it is.
- Leaving out what is still owed with a fee (83.595(4)(a)), or the prorated rent for a servicemember (83.682(4)).
- Missing a way out the facts point to.
- Counting the 7 days forward from the notice instead of back from the move.
- Writing any date count_days did not give you, or counting how long something has lasted or how long until a date. Setting a date from the facts beside a date count_days gave is not counting.
- Stating a test for "substantially impaired" that the statute does not give.
