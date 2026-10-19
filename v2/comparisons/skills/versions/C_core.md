---
name: deposit_not_returned
description: The tenant moved out and the landlord has not returned all of the security deposit.
---
# Deposit not returned

Rests on 83.49 and 83.505. This is the core. The statute's exact words, the points the statute does not settle, and
the mistakes to avoid are in the details file: call read_skill_details before you quote the statute, before you
answer on a notice that came some other way than certified mail or agreed e-mail, and whenever the tenant left
before the lease's end or had a periodic tenancy.

## Check first

Whether 83.49 and part II apply at all: transient rentals and regulated deposits are outside 83.49 (83.49(4)), and
college housing may be outside part II (83.42(1)). Money the lease calls nonrefundable may fall under 83.491.

## Facts the answer turns on

lease_end_date; move_out_date; whether the tenant left before the lease's end or had a periodic tenancy, and if so
what written notice they gave, how, and whether it had an address; what the landlord sent about keeping any of the
deposit, how it came, and its date (claim_notice_date); whether they signed an addendum agreeing to e-mail notices.

## Option 1: the whole deposit, because no notice of a claim came in time (83.49(3)(a))

All three must be met:

1. No written notice of a claim by certified mail, or by e-mail under a signed addendum (83.505(1)), reached the
   tenant. If one came another way, it is not settled (details).
2. 30 days after lease_end_date have passed (count_days). If not, the option is not open yet.
3. The landlord was not relieved of the notice by 83.49(5): the tenant stayed to the end with no periodic tenancy,
   or gave 7 days' written notice by certified mail or personal delivery with an address, or followed a different
   rule in the lease. Otherwise the landlord's silence forfeits nothing, but the tenant keeps the right to the deposit.

If all are met, the landlord forfeits the claim and must return all of it, but may still sue for damages after.

## Option 2: the balance after a notice of a claim (83.49(3)(b))

The tenant has 15 days after receiving the notice to object in writing. The landlord must send the balance within
30 days after the date of the notice. Not objecting does not end the tenant's right to sue separately.

## Deadlines (count_days only; never count yourself)

15 and 30 days after lease_end_date (the return with no claim; the last day for a notice of a claim); 7 days before
move_out_date (days: -7), when 83.49(5) applies; 15 days after the tenant received a notice of a claim; 30 days after
claim_notice_date. Passing the 15-day date forfeits nothing while the 30 days still run.
