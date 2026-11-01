---
name: deposit_not_returned
description: The tenant moved out and the landlord has not returned all of the security deposit.
---
# Deposit not returned

Rests on 83.49 (the deposit) and 83.505 (notices by e-mail). Read a section in full with get_statute_section.

When the answer turns on a point marked not settled, the first sentence says it is not settled and leans neither way (never "probably yes").

## First, whether this applies

- 83.49 does not cover every deposit: "This section does not apply to transient rentals by hotels or motels as defined in chapter 509 or in those instances in which the amount of rent or deposit, or both, is regulated by law or by rules or regulations of a public body, including public housing authorities and federally administered or regulated housing programs" (83.49(4)). It then says: "With the exception of subsections (3), (5), and (6), this section is not applicable to housing authorities or public housing agencies created pursuant to chapter 421 or other statutes." (83.49(4)).
  - The landlord is a housing authority or public housing agency: (3), (5), and (6) still apply, so this skill still applies.
  - A private landlord in a government housing program: not settled. The text names programs by section number and does not say which tenant subsidies they cover. Give both readings and choose neither. One: the rent or deposit counts as regulated, so 83.49 does not apply (what does is outside this tool). The other: only a program that sets or limits the amount of the rent or of the deposit does that, so 83.49 applies. Name both, rent and deposit, as 83.49(4) does.
- Load who_the_law_covers, unless the facts already hold school_housing.
- Money the lease calls nonrefundable may fall under 83.491. Read it before treating that money as outside 83.49.

## Facts the answer turns on

Read the lease first. Ask the tenant only plain facts, one or two at a time. Note each fact with note_fact under these names, dates written YYYY-MM-DD; a date counts only once the tenant has confirmed it.

- public_housing: whether a housing authority is the landlord, or a government housing program (public housing, Section 8, a subsidized building) pays part of the rent or sets it. Ask only if the lease or the tenant points to one.
- lease_end_date: the date the rental agreement ended (for a renewal, the renewal's end: "a renewal of an existing rental agreement shall be considered a new rental agreement" (83.49(6))). move_out_date: the date they moved out and returned the keys.
- Whether they moved out before the lease's end, or had a month-to-month or other periodic tenancy.
- If so: what written notice they gave before leaving, how it reached the landlord, and whether it gave an address.
- What the landlord sent about keeping any of the deposit: what it said, how it came, the date on it (claim_notice_date), and the date the tenant received it (claim_received_date).
- Whether they and the landlord signed an addendum agreeing to notices by e-mail.
- forwarding_address: whether they gave the landlord a new mailing address, which one, and when (ask only if a notice came by mail). The statute's disclosure to tenants says "YOU MUST GIVE THE LANDLORD YOUR NEW ADDRESS SO THAT THE LANDLORD CAN SEND YOU NOTICES REGARDING YOUR DEPOSIT" (83.49(2)(d)).

## Option 1: the whole deposit, because no notice of a claim came in time

All three conditions must be met. Settle each one from the facts: met, not met, the tenant can tell us, or not settled.

1. **No proper notice of a claim reached the tenant.** The rule: "If the landlord intends to impose a claim on the deposit, the landlord must, within 30 days after the termination of the rental agreement, provide the tenant written notice by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505 of his or her intention to impose a claim on the deposit and the reason for imposing the claim." (83.49(3)(a)). E-mail counts only "if the parties have signed an addendum to the rental agreement that the parties specifically agree to the electronic delivery of notices" (83.505(1)).
   - Nothing in writing about keeping any of it arrived: met.
   - A notice came by certified mail, to the new address the tenant gave (the old one, if they gave none), or by e-mail under a signed addendum: not met. Say so in one sentence: this is the kind of notice the statute requires, so on this ground the landlord has not lost its claim. Then go to option 2.
   - A notice came some other way (regular mail, a text, a portal message, by hand), or by certified mail to the old address after the tenant gave a new one (the text does not define the last known mailing address): not settled. Give both readings and choose neither. One: it is not the required notice, so the claim is forfeited (the forfeiture sentence below). The other: a notice the tenant actually received in time is enough, since 83.505 "does not preclude service of notices by any other means permitted by law." (83.505(6)). Under that reading, go on to option 2 as well and give both of its dates, and say what each reading means for the tenant's money.
   - A notice came the right way but gives no reason for the claim: met. It is not the required notice, since the rule asks for "the reason for imposing the claim" (83.49(3)(a)).
   - A notice came the right way and gives the reason but leaves out the amount, the warning to object within 15 days, or where to send an objection. Those are parts of "a statement in substantially the following form" (83.49(3)(a)), not of the rule's own words: not settled whether it is still the required notice. Give both readings and choose neither. One: without that part it is not the required notice, so the claim is forfeited. The other: the form need only be followed substantially, so it is still enough. Under that reading, go on to option 2 and give both of its dates.
2. **The 30 days have passed.** Call count_days(lease_end_date, 30). If it has not passed, a notice may still come in time, so this option is not open yet.
   - If the tenant moved out before the lease's end date, which date ends the rental agreement is not settled. Call both count_days(lease_end_date, 30) and count_days(move_out_date, 30), and give both readings. The lease end date: 83.49(3)(a) begins "Upon the vacating of the premises for termination of the rental agreement" (83.49(3)(a)), naming vacating and termination as two things. The move-out date: the required disclosure tells tenants the notice comes "WITHIN 30 DAYS AFTER YOU MOVE OUT" (83.49(2)(d)).
3. **The landlord was not relieved of the notice.** A tenant who left early, or had a periodic tenancy, must give notice first. Who: "Except when otherwise provided by the terms of a written rental agreement, any tenant who vacates or abandons the premises before the expiration of the term specified in the rental agreement, or any tenant who vacates or abandons premises which are the subject of a tenancy from week to week, month to month, quarter to quarter, or year to year," (83.49(5)). How: "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which notice must include the address where the tenant may be reached." (83.49(5)).
   - The tenant stayed to the lease's end and had no periodic tenancy: met.
   - They gave that notice, with an address, on or before the date count_days(move_out_date, -7) gives: met.
   - The lease sets a different rule on notice before leaving, and they followed it: met. Read the lease's clause.
   - Otherwise not met: "Failure to give such notice relieves the landlord of the notice requirement of paragraph (3)(a) but does not waive any right the tenant may have to the security deposit or any part of it." (83.49(5)). Say both halves: the landlord's silence forfeits nothing, and the tenant keeps the right to the deposit.

If all three are met: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit and may not seek a setoff against the deposit but may file an action for damages after returning the security deposit to the tenant." (83.49(3)(a)). Say both halves: the whole deposit comes back, and the landlord may still sue for damages after.

## Option 2: the balance after a notice of a claim

When a notice of a claim came (or under the reading that one that came another way counts): "Unless the tenant objects to the imposition of the landlord’s claim or the amount thereof within 15 days after receipt of the landlord’s notice of intention to impose a claim, the landlord may then deduct the amount of his or her claim and shall remit the balance of the deposit to the tenant within 30 days after the date of the notice of intention to impose a claim for damages." (83.49(3)(b)).

- The tenant's last day to object in writing: count_days(claim_received_date, 15).
- The landlord's last day to send the balance: count_days(claim_notice_date, 30).
- If the tenant objected within the 15 days: the right to deduct and the duty to remit the balance are in a sentence that begins "Unless the tenant objects" (83.49(3)(b)). The text sets no step after an objection, only a court action (below). Do not say the landlord may deduct or that the balance is overdue; say what follows is not settled.
- Not objecting is not the end: "The failure of the tenant to make a timely objection does not waive any rights of the tenant to seek damages in a separate action." (83.49(3)(b)).

## The 15-day return

When the landlord intends no claim: "if the landlord does not intend to impose a claim on the security deposit, the landlord must return the security deposit, together with interest if otherwise required, within 15 days after the termination of the rental agreement" (83.49(3)(a)). The date: count_days(lease_end_date, 15). Passing it forfeits nothing while the 30 days for a notice of a claim are still running.

## Court costs and fees

Only if someone sues, and only for the winner: "If either party institutes an action in a court of competent jurisdiction to adjudicate the party’s right to the security deposit, the prevailing party is entitled to receive his or her court costs plus a reasonable fee for his or her attorney." (83.49(3)(c)). The same paragraph adds: "The court shall advance the cause on the calendar." (83.49(3)(c)). Say it plainly: the court hears such a case sooner.

## Mistakes to avoid

- Writing any date that count_days did not give you, or comparing dates yourself.
- Saying the landlord forfeits before count_days shows the 30 days passed, or when a proper notice came.
- Stopping at the forfeiture without saying the landlord may still sue for damages.
- Leaving out 83.49(5) when the tenant left early or had a periodic tenancy.
- Promising court costs or fees without the condition in 83.49(3)(c).
- Leaning toward one reading of a point that is not settled, as in "probably yes".
- Telling a tenant of a housing authority that 83.49 does not apply.
