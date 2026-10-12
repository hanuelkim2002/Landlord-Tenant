---
name: notice_received_nonpayment
description: "Tenant received a landlord's written demand for unpaid rent or possession (the 3-day notice)."
sections: ["83.56", "83.60", "83.42"]
clocks:
  - id: three_day_demand_period
    actor: tenant
    trigger: nonpayment_notice_delivered
    days: 3
    direction: after
    count: court_business_days
    shown_with: notice_stated_payment_date
    cite: "83.56(3)"
    quote: "If the tenant fails to pay rent when due and the default continues for 3 days, excluding Saturday, Sunday, and legal holidays, after delivery of written demand by the landlord for payment of the rent or possession of the premises, the landlord may terminate the rental agreement."
    consequence: "Legal holidays for the purpose of this section shall be court-observed holidays only."
counting:
  convention: "court business days, trigger day not counted, Saturdays, Sundays, and the circuit's court holidays skipped (calendars/)"
  status: "ASSUMPTION. The counting rule and which holidays count are open questions (see open_questions). Show the counting line with every computed date."
  note: "83.56(3) is computed in court business days from the circuit's holiday memorandum. 83.60(2) is not computed; whether its \"legal holidays\" are the same list is an open question."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.56.txt, statutes/83.60.txt, statutes/83.42.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/notice_received_nonpayment.yaml version 0.6"
---
## When to load this skill

Load this skill when the tenant has received a landlord's written demand for unpaid rent or possession of the unit (the 3-day notice), or has been sued for possession over unpaid rent. It covers paying within the 3 days, raising a defense once an eviction case is filed, and defending on the ground that the notice is defective. It does not decide whether the notice is in the form the statute gives (see the open question on the notice's form). A notice about a lease violation other than unpaid rent is a different situation; load notice_received_violation for it.

If the tenant held back rent because the landlord did not make repairs, load repair_not_made too.

The statute leaves some housing out of this part: "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)) This matters when the tenant lives in college housing. The tool records the facts and does not decide whether this applies to the tenant's housing. Say that it could matter and that the tool does not decide it.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold, from the papers in their hands. Never ask whether something meets a term of the statute or the lease; you apply the term to their answer.

### From the lease (search_lease)

- The rent amount and the due date, to set beside the amount the notice demands. Do not ask the tenant for the monthly rent when the lease gives it.
- The notices clause: where the tenant's reply must be sent. Any lease clause about notices does not change the notice rules: "The notice requirements of subsections (1)-(3) may not be waived in the rental agreement." (Fla. Stat. 83.56(4)) Give that sentence next to such a clause.

### From the tenant

- The date the landlord's notice was delivered to them (or left at their home), and how it reached them: handed to them, mailed, e-mailed, left at the door, or something else.
- The date the notice itself gives as the last day to pay or leave. Ask them to copy it from the notice.
- How much the notice says they owe.
- Whether any of the rent the notice asks for is still unpaid.
- Whether, after the notice was delivered, they paid part of the rent and the landlord accepted it. If so, whether the landlord gave a receipt showing the date, the amount received, and the agreed date and balance still due.
- Whether they held back rent because the landlord did not make repairs.
- The county the rental is in.
- Whether the landlord has filed an eviction case in court against them. If so: the date they were served with the court papers, and whether they have paid the rent the court papers claim into the court registry, or filed a motion asking the court to decide the amount.

### What the deadline counts from

The program computes the 3-day deadline (see Deadlines) only from facts the tenant has confirmed: the date the notice was delivered, the date the notice itself states as the last day to pay or leave (printed beside the computed date), and the county of the rental, since the days skip the court holidays of that county's circuit. Calendars are stored only for some counties; for any other county, or a year with no memorandum, the date is not computed. When the tenant tells you one of these, propose it for their record, so they can confirm it.

### Evidence worth keeping

- The notice itself, with a photo of where it was left, or the envelope or the e-mail headers.
- Rent receipts, bank or payment app records for the months in question.
- Any receipt for partial rent the landlord accepted.
- Any written notice about repairs sent before rent was held back.
- Court papers, if served, with the date of service.

## What the tenant can do

Before any step, say whether the tenant can do it, what that turns on, and what is left to do. Each condition below is settled in one of four ways. The lease can settle it: read that clause with search_lease and say what it says. The tenant can tell you. It is not settled: give the open question from the section below. Or it is outside the tool: say what to check and where.

### Pay the rent the notice demands before the 3 days end

The statute lets the landlord end the rental agreement when the default continues for 3 days after delivery of the demand: "the landlord may terminate the rental agreement." (Fla. Stat. 83.56(3)) Paying before the 3 days end means the landlord may not end the rental agreement on this notice.

It is open only while the 3 days after delivery, excluding Saturday, Sunday, and legal holidays, have not ended. Whether they have ended comes only from the program's deadlines. If they show the 3 days have passed, say so: after that the statute lets the landlord end the rental agreement. If the program cannot show the deadline, say which fact it is missing (the delivery date or the county) and ask for it.

The step: the rent the notice demands is paid. The notice demands "payment of the rent or possession of the premises within 3 days" (Fla. Stat. 83.56(3)). The tenant tells you whether any of it is unpaid. Three open questions apply: how the days are counted, which holidays count, and the notice's form.

### Raise a defense other than payment in an eviction case

Examples are the landlord's failure to repair, or retaliation. It is open only after the landlord has filed an eviction case, which the tenant tells you: "In an action by the landlord for possession of a dwelling unit, if the tenant interposes any defense other than payment" (Fla. Stat. 83.60(2)). If the tenant says no case has been filed, say a defense is raised in a case once one is filed.

The step: the rent the court papers claim is paid into the registry of the court, or a motion to determine the amount is filed, within 5 days after service, excluding Saturdays, Sundays, and legal holidays. The statute: "Failure of the tenant to pay the rent into the registry of the court or to file a motion to determine the amount of rent to be paid into the registry within 5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process constitutes an absolute waiver of the tenant’s defenses other than payment" (Fla. Stat. 83.60(2)). The tenant tells you whether they did. The tool does not compute this date; give the open question on counting the 5 days.

### Defend an eviction case on the ground that the 3-day notice is defective

Two conditions need to be met.

1. The notice is not in substantially the form the statute gives: "The 3-day notice shall contain a statement in substantially the following form" (Fla. Stat. 83.56(3)). Check the notice itself, part by part, against the form: the sum demanded for the rent and use of the premises, the address with the county, the 3 days excluding Saturday, Sunday, and legal holidays, the date to pay by, and the landlord's name, address, and phone number. Ask the tenant for the notice's words and set them beside the form. How far a notice may differ is not settled; give the open question on the notice's form.
2. The landlord has filed an eviction case (as when raising a defense, above).

The step is the same as when raising a defense: the registry payment or the motion within 5 days after service. The open questions on the notice's form and on counting the 5 days apply.

### Exclusions

- Partial rent: "However, a landlord does not waive the right to terminate the rental agreement or to bring a civil action for that noncompliance by accepting partial rent for the period." (Fla. Stat. 83.56(5)(a)) An accepted partial payment does not end the notice. See the open question on the landlord's steps after partial rent.
- The lease cannot waive the notice (see What to find out).

## Deadlines

The program computes one deadline. It is the tenant's: the 3 days after the landlord's written demand was delivered, excluding Saturday, Sunday, and legal holidays. The statute: "If the tenant fails to pay rent when due and the default continues for 3 days, excluding Saturday, Sunday, and legal holidays, after delivery of written demand by the landlord for payment of the rent or possession of the premises, the landlord may terminate the rental agreement." (Fla. Stat. 83.56(3)) It also says: "Legal holidays for the purpose of this section shall be court-observed holidays only." (Fla. Stat. 83.56(3))

The program counts in court business days from the delivery date, the delivery day not counted, skipping Saturdays, Sundays, and the circuit's court holidays from its published calendar. It prints the date beside the date the notice itself states, and with its counting line. Never give the computed date apart from the counting line or the notice's stated date. The 5 days in 83.60(2) are not computed.

The program computes and prints every date. Never write, count, or compare a date yourself, in calendar days or with holidays, not even for 'what if it ran from another day'. Whether the deadline has passed comes only from the program's deadlines (get_deadlines). The counting is an assumption: which holidays count, and how the days are counted, are open (see below). If the tenant asks how the days are counted, say so.

## What the statute does not settle

For each question below, tell the tenant in plain words that the law does not settle it, give every reading with what it would mean for them, and pick none. Where one step works under every reading, say so.

- How the days are counted. 83.56(3) counts "3 days, excluding Saturday, Sunday, and legal holidays, after delivery of written demand by the landlord for payment of the rent or possession of the premises" (Fla. Stat. 83.56(3)). The program counts forward from the delivery date, the delivery day not counted, and shows the date the notice itself states next to it. How the days are counted (the delivery day, delivery on a weekend or holiday, when the last day ends) is not settled, and the tool does not settle it. Show the counting line with the date.
- Which holidays count. 83.56(3) says "Legal holidays for the purpose of this section shall be court-observed holidays only." (Fla. Stat. 83.56(3)) The program skips every holiday in the circuit Chief Judge's memorandum for the year, including those marked as designated by the Chief Judge and those it marks as additional discretionary holidays. Whether each of those is a court-observed holiday in the statute's sense is not settled.
- Counting the 5 days after service. Once an eviction case is served, 83.60(2) requires a tenant who raises "any defense other than payment" (Fla. Stat. 83.60(2)) to pay the rent into the registry of the court, within "5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process" (Fla. Stat. 83.60(2)). Apply the requirement itself when the tenant says court papers were served. The definition of legal holidays in 83.56(3) is stated "for the purpose of this section" (Fla. Stat. 83.56(3)), and whether 83.60(2) uses the same list is not settled, so the tool does not compute this date.
- The notice's form. 83.56(3) says the notice "shall contain a statement in substantially the following form" (Fla. Stat. 83.56(3)). Set what the tenant says the notice states (the amount demanded, the date to pay by, how it was delivered) beside the form's parts. A defect does not end a case by itself: "The landlord must be given an opportunity to cure a deficiency in a notice or in the pleadings before dismissal of the action." (Fla. Stat. 83.60(1)(a)) What stays open is how far a notice may differ and still be in substantially that form, whether it may demand more than rent, and whether it may add terms the form does not have, such as how, where, or in what form the rent must be paid.
  - A notice that leaves out a part of the form (the county, the excluded days, the date to pay by), demands charges other than rent, or adds a term the form does not have (cash only, a money order, one office) is not in substantially the form, since the form demands only "the sum of dollars for the rent and use of the premises" (Fla. Stat. 83.56(3)).
  - Substantially allows differences that do not mislead the tenant about how much, by when, and to whom, and charges the lease itself calls rent may be demanded as rent.
- The landlord's steps after partial rent. If partial rent is accepted after the notice, 83.56(5)(a) says the landlord does not waive "by accepting partial rent for the period" (Fla. Stat. 83.56(5)(a)), and lists what the landlord must then do: "If partial rent is accepted after posting the notice for nonpayment, the landlord must:" (Fla. Stat. 83.56(5)(a)) give a receipt, put the partial rent in the registry of the court on filing, or post a new 3-day notice. Apply the list to what the tenant tells you. The tool records only whether the tenant got a receipt, so the other two steps are not known unless the tenant says.

## Letters

Every letter needs: today's date, the amount demanded, what the tenant has paid and when, the tenant's reply, and how the tenant will deliver it. The tenant sends the letter; you send nothing. Read the lease's notices clause with search_lease and tell the tenant where and how the lease says the reply must be sent.

The postures, each with its own line:

- preserve: States the amount demanded and what the tenant has paid, and asks the landlord for an account of the balance. Cites nothing.
- assert: Adds the 83.56(5)(a) sentence on partial rent, quoted.
- escalate: Adds the 83.60(1)(a) sentence on defenses, quoted.

When a letter is shown, tell the tenant this. A letter from them does not change the period in 83.56(3), which runs "after delivery of written demand by the landlord for payment of the rent or possession of the premises" (Fla. Stat. 83.56(3)) and counts "3 days, excluding Saturday, Sunday, and legal holidays" (Fla. Stat. 83.56(3)). The program computed that date from the delivery date they gave, skipping the holidays in their court circuit's published calendar, and shows it next to the date the notice states. How the days are counted is stated with the date as an assumption.

## Mistakes to avoid

- Counting the 3 days yourself, in calendar days or with holidays. Only the program computes the date, and whether it has passed comes from its listing.
- Giving the computed date without its counting line, or without the date the notice itself states.
- Saying the tenant has a defense in court without 83.60(2), or giving the registry payment without its other step. What waives the defenses other than payment is failing to pay the rent into the registry "or to file a motion to determine the amount of rent to be paid into the registry" (Fla. Stat. 83.60(2)), which "constitutes an absolute waiver of the tenant’s defenses other than payment" (Fla. Stat. 83.60(2)).
- Treating an accepted partial payment as ending the notice. The landlord does not waive "by accepting partial rent for the period" (Fla. Stat. 83.56(5)(a)).
- Reading the steps after partial rent as settled on the record, or as all due before filing. The receipt comes "before filing an action for possession" (Fla. Stat. 83.56(5)(a)), the partial rent goes into the registry "upon filing the action for possession" (Fla. Stat. 83.56(5)(a)), and the list ends "or 3. Post a new 3-day notice reflecting the new amount due" (Fla. Stat. 83.56(5)(a)). Which step the landlord took is a fact the tenant must tell you.
- Saying a defective notice ends the case. 83.60(1)(a) gives the landlord "an opportunity to cure a deficiency in a notice" (Fla. Stat. 83.60(1)(a)) first.
- Applying the repair defense in 83.60(1)(b) without the written notice it requires, "indicating the intention of the tenant not to pay rent by reason thereof" (Fla. Stat. 83.60(1)(b)). The facts for that are in repair_not_made.
- Not asking whether court papers have been served.
