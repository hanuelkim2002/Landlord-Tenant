---
name: deposit_not_returned
description: The tenant moved out and the landlord has not returned all of the security deposit.
---
# Deposit not returned

Rests on 83.49 (the deposit) and 83.505 (notices by e-mail). Read a section in full with get_statute_section.

## The rule in short

If the landlord means to keep any of the deposit, it must send written notice of the claim and the reason within 30 days after the rental agreement ends: "If the landlord intends to impose a claim on the deposit, the landlord must, within 30 days after the termination of the rental agreement, provide the tenant written notice by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505 of his or her intention to impose a claim on the deposit and the reason for imposing the claim." (83.49(3)(a)). E-mail counts only "if the parties have signed an addendum to the rental agreement that the parties specifically agree to the electronic delivery of notices" (83.505(1)). Missing it costs the claim, not the right to sue: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit and may not seek a setoff against the deposit but may file an action for damages after returning the security deposit to the tenant." (83.49(3)(a)). With no claim intended, the deposit comes back sooner: "if the landlord does not intend to impose a claim on the security deposit, the landlord must return the security deposit, together with interest if otherwise required, within 15 days after the termination of the rental agreement" (83.49(3)(a)); passing that date forfeits nothing while the 30 days are still running.

A tenant who leaves before the lease's end, or has a periodic tenancy, must give notice first, unless the lease says otherwise: "Except when otherwise provided by the terms of a written rental agreement, any tenant who vacates or abandons the premises before the expiration of the term specified in the rental agreement, or any tenant who vacates or abandons premises which are the subject of a tenancy from week to week, month to month, quarter to quarter, or year to year," (83.49(5)) "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which notice must include the address where the tenant may be reached." (83.49(5)). Without it: "Failure to give such notice relieves the landlord of the notice requirement of paragraph (3)(a) but does not waive any right the tenant may have to the security deposit or any part of it." (83.49(5)).

When a notice of a claim came: "Unless the tenant objects to the imposition of the landlord’s claim or the amount thereof within 15 days after receipt of the landlord’s notice of intention to impose a claim, the landlord may then deduct the amount of his or her claim and shall remit the balance of the deposit to the tenant within 30 days after the date of the notice of intention to impose a claim for damages." (83.49(3)(b)), and "The failure of the tenant to make a timely objection does not waive any rights of the tenant to seek damages in a separate action." (83.49(3)(b)). Court costs and fees go only to the winner of a suit: "If either party institutes an action in a court of competent jurisdiction to adjudicate the party’s right to the security deposit, the prevailing party is entitled to receive his or her court costs plus a reasonable fee for his or her attorney." (83.49(3)(c)).

Two points are not settled; give each reading and choose none. Which date ends the rental agreement when the tenant left before the lease's end: 83.49(3)(a) begins "Upon the vacating of the premises for termination of the rental agreement" (83.49(3)(a)), naming two things, but the required disclosure says "WITHIN 30 DAYS AFTER YOU MOVE OUT" (83.49(2)(d)). And a notice of a claim that came some way other than certified mail or agreed e-mail: either it is not the required notice and the claim is forfeited, or a notice actually received in time is enough, since 83.505 "does not preclude service of notices by any other means permitted by law." (83.505(6)).

Before applying any of this, check it applies: "This section does not apply to transient rentals by hotels or motels as defined in chapter 509 or in those instances in which the amount of rent or deposit, or both, is regulated by law or by rules or regulations of a public body" (83.49(4)), and college housing may be outside part II: "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (83.42(1)). Money the lease calls nonrefundable may fall under 83.491.

Dates come only from count_days: 15 and 30 days after lease_end_date; 7 days before move_out_date (days: -7); 15 days after the date the tenant received a notice of a claim; 30 days after claim_notice_date.

## Worked examples

These show how to apply the rule. Their facts are not the tenant's; never carry a fact from an example into an answer.

### Example 1: a notice of a claim came by certified mail

Facts: lease ended 2026-03-31, moved out that day; a letter by certified mail dated 2026-04-20 claims $300 of a $900 deposit for cleaning; the tenant received it 2026-04-23 and has not answered. Asks: "Can they keep the $300?"

Answer: For now, yes, unless you object in writing. The notice came by certified mail within the 30 days (count_days(lease_end_date, 30) gives 2026-04-30), so it is the notice the statute requires (83.49(3)(a)). You have 15 days after you received it to object in writing (count_days(claim_received_date, 15) gives 2026-05-08); if you do not, the landlord "may then deduct the amount of his or her claim" (83.49(3)(b)). Either way the landlord must send the other $600 within 30 days after the date of the notice (count_days(claim_notice_date, 30) gives 2026-05-20). Not objecting does not end your right to sue for the $300 later (83.49(3)(b)). Do you want to object to the cleaning charge?

### Example 2: month to month, left with proper notice

Facts: month-to-month tenancy; the tenant hand-delivered a written notice with their new address on 2026-05-20 and moved out 2026-05-31, when the tenancy ended; no deposit and no word from the landlord since; today is 2026-07-15. Asks: "Do I get my $800 back?"

Answer: Yes, all of it. A month-to-month tenant must give 7 days' written notice by certified mail or personal delivery with an address (83.49(5)); yours went by hand with your address, before the last day for it (count_days(move_out_date, -7) gives 2026-05-24). So the landlord had to send any notice of a claim within 30 days after the tenancy ended (count_days(lease_end_date, 30) gives 2026-06-30), and that has passed with none. The landlord "forfeits the right to impose a claim upon the security deposit" but "may file an action for damages after returning the security deposit to the tenant" (83.49(3)(a)).

### Example 3: left early with notice; which date counts is not settled

Facts: lease ends 2026-08-31; the tenant sent 7 days' written notice with an address by certified mail and moved out 2026-06-30; no deposit and no word since; today is 2026-08-10. Asks: "Is it too late for them to claim anything?"

Answer: That depends on a point the statute does not settle: whether the 30 days run from the day you moved out or from the lease's end date. From your move-out, they ended 2026-07-30 (count_days(move_out_date, 30)) and have passed, so the landlord would have lost the right to claim anything. From the lease's end, they end 2026-09-30 (count_days(lease_end_date, 30)), so a notice could still come. For the lease end: the statute speaks of "the vacating of the premises for termination of the rental agreement" (83.49(3)(a)), two separate things. For the move-out: the disclosure the statute requires says "WITHIN 30 DAYS AFTER YOU MOVE OUT" (83.49(2)(d)). Your notice was proper (83.49(5)), so it does not relieve the landlord either way.
