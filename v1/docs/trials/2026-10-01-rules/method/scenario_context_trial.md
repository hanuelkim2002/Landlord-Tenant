## Scenario nonpayment_3day

What the tenant typed at intake, before the chat:
> I rent a house in Gainesville, Alachua County. My rent is $1,850 a month. I did not pay September rent because I lost my job.
> On September 18, 2026 the landlord handed me a notice saying I owe $1,850 and must pay or leave by September 21, 2026.
> I have not paid anything since, and no court papers have been served on me.

The tenant's chat lines, in order:
- What are my deadlines?
- timeline

Playbook notice_received_nonpayment: open questions (the statute does not settle these):
- counting_rule: 83.56(3) counts "3 days, excluding Saturday, Sunday, and legal holidays, after delivery of written demand by the landlord for payment of the rent or possession of the premises". The tool counts forward from the delivery date, the delivery day not counted, and shows the date the notice itself states next to it. How the days are counted (the delivery day, delivery on a weekend or holiday, when the last day ends) is an open question the author is researching. Show the counting line with the date and do not settle it.
- court_observed_holidays: 83.56(3) says "Legal holidays for the purpose of this section shall be court-observed holidays only." The tool skips every holiday in the circuit Chief Judge's memorandum for the year, including those marked as designated by the Chief Judge and those it marks as additional discretionary holidays. Whether each of those is a court-observed holiday in the statute's sense is an open question. Calendars are stored only for the counties in calendars/; for any other county, or a year with no memorandum, the date is not computed.
- registry_count: Once an eviction case is served, 83.60(2) sets "5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process". The definition of legal holidays in 83.56(3) is stated "for the purpose of this section", and whether 83.60(2) uses the same list is an open question. The tool does not compute this date.
- notice_form: 83.56(3) says the notice "shall contain a statement in substantially the following form". The tool does not decide whether a notice meets that form.
- partial_rent_steps: If partial rent is accepted after the notice, 83.56(5)(a) lists what the landlord must then do ("If partial rent is accepted after posting the notice for nonpayment, the landlord must:"). The tool records whether a receipt was given and does not decide whether the list was followed.
Posture lines: preserve: States the amount demanded and what the tenant has paid, and asks the landlord for an account of the balance. Cites nothing. | assert: Adds the 83.56(5)(a) sentence on partial rent, quoted. | escalate: Adds the 83.60(1)(a) sentence on defenses, quoted.

## Scenario repair_notice

What the tenant typed at intake, before the chat:
> I rent a single-family house in Gainesville. The air conditioning has been broken since September 1, 2026.
> On September 10, 2026 I hand-delivered a written notice to the landlord describing the broken air conditioning and saying I will not pay rent until it is fixed.
> The landlord has not fixed it or replied.

The tenant's chat lines, in order:
- What are my deadlines?
- I would like a letter asking the landlord to repair the air conditioning. Give them 5 days to reply. I will send it by certified mail, return receipt requested. Use the preserve posture, with no quotes.
- Yes, that is everything. Please draft it now.
- timeline

Playbook repair_not_made: open questions (the statute does not settle these):
- which_code_applies: 83.51(1)(a) points to "the requirements of applicable building, housing, and health codes". Those codes are not in the stored text. The tool does not decide whether a condition violates a code.
- material_noncompliance: Both 7-day periods concern a landlord who "materially fails to comply" or a "material noncompliance". The stored text does not define "material". No cases loaded yet.
- subsection_one_or_two: 83.51(1) and 83.51(2) list different duties, and 83.51(2)(c) treats subsection (2) differently in an action for possession. The tool shows both texts and does not decide which subsection a condition falls under.
- court_procedure: Once an eviction case is filed, 83.60(2) sets a period of "5 days, excluding Saturdays, Sundays, and legal holidays, after the date of service of process". This tool counts calendar days only and does not compute that date.
Posture lines: preserve: Describes the condition and asks for the repair. Cites nothing. | assert: Adds the 83.51(1) duty, quoted. | escalate: Adds the 83.56(1) sentence, quoted.

## Scenario claim_letter

What the tenant typed at intake, before the chat:
> I rented a house in Gainesville. My lease ended July 31, 2026 and I moved out and gave the keys back on July 30, 2026.
> I emailed the property manager my new address the same day. It's September now and I haven't gotten my $1,850 deposit back or any letter about it.

The tenant's chat lines, in order:
- I just got a letter from the landlord. It is dated September 22, 2026 and it arrived by certified mail on September 25, 2026. It says they are keeping $400 of my deposit for cleaning.
- What are my deadlines now?
- timeline

Playbook deposit_not_returned: open questions (the statute does not settle these):
- termination_date_meaning: The clocks run from "termination of the rental agreement." The text does not say whether that is the lease end date or the move-out date. Record both; no cases loaded yet.
Posture lines: preserve: States move-out date, amount, forwarding address. Asks for return. Cites nothing. | assert: Adds the 83.49(3)(a) obligation, quoted. | escalate: Adds the forfeiture consequence, quoted, and 83.49(3)(c) fee-shifting.

Playbook deposit_claim_received: open questions (the statute does not settle these):
- receipt_date: The objection clock runs from "receipt of the landlord’s notice" while the remit clock runs from "the date of the notice". Record both dates. For e-mail, 83.505(4) says a notice "is deemed delivered at the time it is sent, unless the e-mail is returned to the sender as undeliverable"; the tool records how the notice arrived and does not decide which date counts.
- email_notice_conditions: 83.505(1) allows e-mail delivery only "if the parties have signed an addendum to the rental agreement". The tool records whether the tenant recalls such an addendum and does not decide whether the notice was validly delivered.
- objection_form: The statute's model notice says the tenant "must object in writing" and that the objection "must be sent to (landlord’s address)". No other delivery method or content requirement appears in the text. No cases loaded yet.
Posture lines: preserve: States that the tenant objects to the claim, the amount, and the reason. Asks for return of the full deposit. Cites nothing. | assert: Adds the 83.49(3)(b) sentence on the 15-day objection, quoted. | escalate: Adds the 83.49(3)(c) sentence on court costs and attorney fees, quoted.

