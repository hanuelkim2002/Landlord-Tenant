## Scenario entry_unannounced

What the tenant typed at intake, before the chat:
> I rent a house in Gainesville. On September 28, 2026 around 2 pm my landlord came into my house while I was at class. He did not tell me beforehand.
> My roommate saw him and he said he was checking the smoke detectors. This is the second time he has come in without telling me. My rent is paid up.

The tenant's chat lines, in order:
- What are my deadlines?
- Was it legal for him to come in like that?
- I would like a letter asking him to give me notice before he comes in again. Give him 7 days to reply. I will send it by certified mail, return receipt requested. Use the preserve posture.
- timeline

Playbook landlord_entered_unannounced: open questions (the statute does not settle these):
- notice_in_hours: 83.53(2) says "“Reasonable notice” for the purpose of repair is notice given at least 24 hours prior to the entry". This tool counts in days and does not compute a time in hours. It records when the tenant says notice was given and when the entry happened.
- purpose_of_entry: The 24-hour rule is stated "for the purpose of repair". For the other purposes in 83.53(1), 83.53(2) lists circumstances instead ("With the consent of the tenant", "In case of emergency", and others). The tool records the reason the landlord gave and does not decide which rule applies.
- abuse_of_access: 83.53(3) says "The landlord shall not abuse the right of access nor use it to harass the tenant." The stored text does not define abuse or harassment. No cases loaded yet.
Posture lines: preserve: States the date and time of the entry and asks for advance notice of future entries. Cites nothing. | assert: Adds the 83.53(2) sentence on reasonable notice, quoted. | escalate: Adds the 83.53(3) sentence, quoted, and, if access or a utility was cut, the 83.67(6) sentence, quoted.

## Scenario rent_increase

What the tenant typed at intake, before the chat:
> I rent a house in Gainesville on a one-year lease. My rent is $1,850 a month.
> On September 20, 2026 the landlord emailed me that my rent goes up to $2,100 starting November 1, 2026.
> On September 5, 2026 I had complained in writing about the broken water heater.

The tenant's chat lines, in order:
- What are my deadlines?
- Can my landlord raise the rent in the middle of my lease?
- Is this retaliation for my complaint?
- timeline

Playbook rent_increased: open questions (the statute does not settle these):
- no_increase_section: The stored text of Chapter 83, part II has no section setting notice for a rent increase. 83.425 says "The regulation of residential tenancies, the landlord-tenant relationship, and all other matters covered under this part are preempted to the state." The tool shows the lease's rent clause and, for a tenancy without a fixed term, 83.57. It does not decide whether an increase is allowed. Say so plainly.
- retaliation: 83.64(1) says "It is unlawful for a landlord to discriminatorily increase a tenant’s rent or decrease services to a tenant, or to bring or threaten to bring an action for possession or other civil action, primarily because the landlord is retaliating against the tenant." 83.64(4) defines "Discrimination" for that section. The tool records the dates and what the tenant knows about other tenants, and does not decide whether the section applies.
Posture lines: preserve: Asks the landlord to confirm the new rent, the date it applies from, and which lease provision it rests on. Cites nothing. | assert: Adds the lease's rent clause, quoted. | escalate: Adds the 83.64(1) sentence, quoted.

## Scenario leave_early

What the tenant typed at intake, before the chat:
> I rent a house in Gainesville on a one-year lease. I got a job in Tampa and want to move out on November 15, 2026.
> I have not told the landlord yet. I did not sign any early termination addendum, and I am not in the military.

The tenant's chat lines, in order:
- What are my deadlines?
- What happens if I just leave in November?
- timeline

Playbook wants_to_leave_early: open questions (the statute does not settle these):
- landlord_choice: 83.595 lists what "the landlord may" do when a tenant surrenders or abandons the unit, in four subsections. The tool shows the list and does not decide which the landlord will choose or what the tenant will owe.
- fee_notice_period: 83.595(4) refers to an early termination fee where "the tenant is required to give no more than 60 days’ notice, as provided in the rental agreement, prior to the proposed date of early termination". The period comes from the lease, and this tool does not compute a date from a period the lease sets.
- servicemember_criteria: 83.682(1) applies only "if any of the following criteria are met", and 83.682(2) says the notice "must be accompanied by either a copy of the official military orders or a written verification signed by the servicemember’s commanding officer". The tool records what the tenant reports and does not decide whether the criteria are met.
- casualty: If the tenant is leaving because the unit was damaged or destroyed (for example, by fire or a storm), 83.63 may be the relevant section. There is no playbook for it; fetch it with get_statute_section.
Posture lines: preserve: States the planned move-out date and a forwarding address, and asks the landlord to confirm what, if anything, the landlord will charge. Cites nothing. | assert: Adds the 83.49(5) sentence on notice before vacating, quoted. | escalate: Adds the 83.595(4) sentence on liquidated damages or an early termination fee, quoted.

## Scenario month_to_month_end

What the tenant typed at intake, before the chat:
> My month-to-month tenancy in Gainesville is ending: I am giving it up at the end of the rent period on November 30, 2026.
> I have not sent the landlord a notice yet and I will not stay on after that.

The tenant's chat lines, in order:
- What are my deadlines?
- Do I have to give my landlord 30 days notice?
- timeline

Playbook lease_ending: open questions (the statute does not settle these):
- lease_set_period: For a lease with a specific duration, the notice period comes from the lease (83.575(1)), and the landlord's written notice is due "within 15 days before the start of the notification period contained in the rental agreement" (83.575(2)). This tool does not compute a date from a period the lease sets. It records the lease's words and the dates the tenant gives.
- other_periods: 83.57 also sets notice for tenancies from year to year, quarter to quarter, and week to week. This playbook computes only the month-to-month date; for the others, show the text of 83.57 and say the tool does not compute it.
- staying_on: 83.575(3) covers a tenant who "remains on the premises with the permission of the landlord after the rental agreement has terminated", and 83.58 a tenant who "holds over and continues in possession of the dwelling unit or any part thereof after the expiration of the rental agreement without the permission of the landlord". The tool records whether the landlord agreed and does not decide which applies.
Posture lines: preserve: States the date the tenant will move out, or asks to renew, and asks the landlord to confirm. Cites nothing. | assert: Adds the 83.57(3) sentence for a month-to-month tenancy, or the lease's notice clause, quoted. | escalate: Adds the 83.575(2) sentence on the landlord's written notice, quoted.

