---
name: deposit_not_returned
description: "The landlord has not returned the tenant's security deposit and has not sent a written claim against it."
sections: ["83.49", "83.505"]
clocks:
  - id: return_if_no_claim
    actor: landlord
    trigger: tenancy_terminated
    days: 15
    direction: after
    cite: "83.49(3)(a)"
    quote: "if the landlord does not intend to impose a claim on the security deposit, the landlord must return the security deposit, together with interest if otherwise required, within 15 days after the termination of the rental agreement"
  - id: claim_notice_deadline
    actor: landlord
    trigger: tenancy_terminated
    days: 30
    direction: after
    cite: "83.49(3)(a)"
    quote: "If the landlord intends to impose a claim on the deposit, the landlord must, within 30 days after the termination of the rental agreement, provide the tenant written notice by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505 of his or her intention to impose a claim on the deposit and the reason for imposing the claim."
    consequence: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit and may not seek a setoff against the deposit but may file an action for damages after returning the security deposit to the tenant."
  - id: tenant_seven_day_notice
    actor: tenant
    trigger: vacated
    days: 7
    direction: before
    applies_if: early_or_periodic
    cite: "83.49(5)"
    quote: "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which notice must include the address where the tenant may be reached"
    consequence: "Failure to give such notice relieves the landlord of the notice requirement of paragraph (3)(a) but does not waive any right the tenant may have to the security deposit or any part of it."
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.49.txt, statutes/83.505.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/deposit_not_returned.yaml version 0.6"
---
## When to load this skill

Load this skill when the landlord has not returned the tenant's security deposit and has not sent a written claim against it. It rests on 83.49 (the deposit) and 83.505 (notices by e-mail).

- If the tenant says the landlord sent anything in writing about keeping part of the deposit (a letter, an e-mail, a text, a portal message), also load deposit_claim_received. Whether that notice came in time, and the tenant's 15 days to object, belong there.
- Money the lease labels nonrefundable may fall under 83.491 instead. Do not treat it as outside 83.49 without reading 83.491 (fetch it with get_statute_section).
- The statute names deposits it does not cover: "This section does not apply to transient rentals by hotels or motels as defined in chapter 509 or in those instances in which the amount of rent or deposit, or both, is regulated by law or by rules or regulations of a public body" (Fla. Stat. 83.49(4)).
- Whether the tenant's college housing is outside part II altogether has not been checked for this situation. Section 83.42 lists what part II does not apply to, among them "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)). Fetch 83.42 with get_statute_section and read it before telling the tenant either way.
- The tool does not decide whether any exclusion applies. Say what the words are and what you would need to know.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold, one or two things at a time and only what your answer turns on. Never ask whether something meets a term of the statute or the lease; ask what happened, then apply the term yourself.

### In the lease (search_lease; try a second wording if the first finds nothing)

- The security deposit clause: the amount, and that the lease calls it a deposit.
- Any money labeled nonrefundable (see 83.491 above).
- What the lease says about the tenant's forwarding address. The landlord's notice goes to the tenant's "last known mailing address".
- The move-out requirements. Cleaning and carpet clauses are the usual basis of a claim.
- Where and how the tenant's notices to the landlord must be sent.
- Any term on notice before the tenant moves out early (see the 7-day notice below).
- Whether one roommate's damage can be charged against the whole deposit.
- The date the lease term ends.

### From the tenant

- How much was the deposit? (Only if the lease does not show it.)
- What date did the lease end, or what date was it terminated? Put it beside the lease's end date, and tell the tenant when they differ.
- What date did they move out and return the keys?
- Have they received anything in writing from the landlord about keeping part of the deposit (a letter, an e-mail, a text, a portal message)? If so, what date did it reach them, and how: certified mail, regular mail, e-mail, handed to them, a text or a resident portal message, something else, or they do not know?
- Did they give the landlord their new mailing address in writing?
- Did they move out before the lease end date, or was this a month-to-month arrangement?
- If so, have they given the landlord anything in writing saying they are moving out, and how did it reach the landlord: handed to the landlord or the office, regular mail, certified mail, e-mail, a resident portal request or message, a text message, or something else?

### What the deadlines count from

The program computes dates only from facts the tenant has confirmed, so get these proposed and confirmed:

- The date the rental agreement ended. The landlord's 15 days and 30 days count from it. When it differs from the move-out date, the program records the move-out date beside it (see the first open question below).
- The date the tenant moved out. The tenant's 7 days' notice counts back from it.
- Whether the tenant moved out before the lease's end, or has a month-to-month or other periodic tenancy. The 7-day notice counts only then.

### Evidence to suggest the tenant keep

- Proof the deposit was paid.
- The move-out date: a key receipt, a walkthrough form, the last utility bill.
- Move-in and move-out photos.
- The forwarding-address notice, with proof of delivery.
- Any landlord letters or e-mails, with the envelope or the full headers.

## What the tenant can do

Tell the tenant first whether they can do this and what it turns on, before any step. Each condition is settled by the lease (read that clause with search_lease and say what it says), by the tenant (ask), by the program's deadlines (call get_deadlines), or not at all (the statute does not settle it: give every reading, see the open questions below).

### Get the whole deposit back because the landlord gave no notice of a claim within the 30 days (Fla. Stat. 83.49(3)(a))

All three conditions must be met. This situation lists no steps beyond a letter asking for the deposit (see Letters).

1. The landlord gave the tenant no written notice of a claim on the deposit. The statute: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit" (Fla. Stat. 83.49(3)(a)). The tenant can tell you:
   - Nothing in writing about keeping part of the deposit arrived: met.
   - Something arrived by certified mail: not met here. Whether it came in time belongs to deposit_claim_received.
   - Something arrived another way (regular mail, e-mail, handed over, a text or portal message, something else): whether a notice given that way is the required notice is not settled. The statute names two ways: "by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505" (Fla. Stat. 83.49(3)(a)). See the second open question.
   - The tenant does not know how it came: ask them to check the envelope (a certified mail label or receipt) or the e-mail, which shows it.
2. The 30 days after the end of the rental agreement have passed: "within 30 days after the termination of the rental agreement" (Fla. Stat. 83.49(3)(a)). Only the program's deadlines settle this. If they show the 30 days have not passed, a notice of a claim may still come in time, so the option is not open yet.
3. The landlord was not relieved of that notice. The statute relieves the landlord when a tenant who leaves early, or has a periodic tenancy, gives no 7 days' notice: "Failure to give such notice relieves the landlord of the notice requirement of paragraph (3)(a)" (Fla. Stat. 83.49(5)). This is met in any of these ways:
   - The tenant did not move out before the lease's end, and the tenancy was not month to month or another periodic one. The tenant can tell you.
   - The tenant gave the landlord 7 days' written notice, by certified mail or in person, with an address: "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which notice must include the address where the tenant may be reached" (Fla. Stat. 83.49(5)). Ask the tenant to check that the notice reached the landlord at least 7 days before they moved out (the program's deadlines show the last day) and gave the address where they can be reached.
   - The tenant e-mailed that notice, which counts only as 83.505 allows. They check whether they and the landlord signed an addendum agreeing to notices by e-mail, and the same two points as above. Also read the lease's clause on notices to the landlord with search_lease and say what it says.
   - The notice went some other way (regular mail, a portal message, a text, something else). They check how it reached the landlord, beside the two ways 83.49(5) names, certified mail or personal delivery.
   - The lease provides otherwise on notice before moving out, and the tenant followed it: "Except when otherwise provided by the terms of a written rental agreement" (Fla. Stat. 83.49(5)). Read the lease's clause on notice before moving out with search_lease, say what it says, and ask whether the tenant followed it.

Which date counts as the end of the rental agreement is also open (the first open question below).

## Deadlines

The program computes and prints every date from confirmed facts. Never write, count, or compare a date yourself: call get_deadlines, and say a deadline has passed or is upcoming only as its result says. The counting rule is an assumption: Florida's court rule for counting days has not been checked against statutory deadlines outside litigation.

- The landlord's 15 days to return the deposit when no claim is intended. It counts from the date the rental agreement ended. The statute: "if the landlord does not intend to impose a claim on the security deposit, the landlord must return the security deposit, together with interest if otherwise required, within 15 days after the termination of the rental agreement" (Fla. Stat. 83.49(3)(a)).
- The landlord's 30 days to give written notice of a claim. It counts from the same date. The notice must go by certified mail to the tenant's last known mailing address, or by e-mail as 83.505 allows: "If the landlord intends to impose a claim on the deposit, the landlord must, within 30 days after the termination of the rental agreement, provide the tenant written notice by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505 of his or her intention to impose a claim on the deposit and the reason for imposing the claim." (Fla. Stat. 83.49(3)(a)). If it is missed: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit and may not seek a setoff against the deposit but may file an action for damages after returning the security deposit to the tenant." (Fla. Stat. 83.49(3)(a)).
- The tenant's 7 days' written notice before moving out. It counts back from the date the tenant moved out, and only when the tenant moved out before the lease's end or has a periodic tenancy. It goes by certified mail or personal delivery, with an address where the tenant can be reached (quoted above under the third condition). If it is missed: "Failure to give such notice relieves the landlord of the notice requirement of paragraph (3)(a) but does not waive any right the tenant may have to the security deposit or any part of it." (Fla. Stat. 83.49(5)). The lease can provide otherwise ("Except when otherwise provided by the terms of a written rental agreement", Fla. Stat. 83.49(5)); read its clause on notice before moving out.

## What the statute does not settle

For each of these, tell the tenant in plain words that the law does not settle it, give every reading and what it would mean for them, and pick none.

### Which date is the termination of the rental agreement

The 15-day and 30-day clocks run from "termination of the rental agreement". The text does not say whether that is the lease end date or the move-out date when the two differ; when they are the same day the question does not arise. The program counts from the date the tenant confirmed as the end of the lease and records the move-out date beside it.

- The lease end date: 83.49(3)(a) begins "Upon the vacating of the premises for termination of the rental agreement" (Fla. Stat. 83.49(3)(a)), naming vacating and termination as two things. And 83.49(5) speaks of a tenant who "vacates or abandons the premises before the expiration of the term" (Fla. Stat. 83.49(5)), so leaving early does not by itself end the agreement.
- The move-out date: the disclosure 83.49(2)(d) requires tells the tenant that the landlord must give notice "WITHIN 30 DAYS AFTER YOU MOVE OUT" (Fla. Stat. 83.49(2)(d)), which reads the same clock as running from the day the tenant leaves.

### A notice of a claim that came some way other than certified mail

The statute names two ways to give the notice of a claim (quoted under the first condition). 83.505(1) allows e-mail only "if the parties have signed an addendum to the rental agreement" (Fla. Stat. 83.505(1)). Apply these to how the tenant says the notice came. If the tenant has not said whether they signed such an addendum, that condition is not known yet. What stays open is a notice that reached the tenant in time some other way.

- A notice given another way is not the required written notice, and "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit" (Fla. Stat. 83.49(3)(a)).
- A notice the tenant actually received in time is enough: 83.505(6) says the section "does not preclude service of notices by any other means permitted by law" (Fla. Stat. 83.505(6)), and the tenant had what the notice is for.

## Letters

The tenant sends every letter; you send nothing. Every letter holds: today's date, the obligation identified, the amount and the return address, a response deadline computed by the tool, and the delivery method. The postures, each line as written:

- preserve: States move-out date, amount, forwarding address. Asks for return. Cites nothing.
- assert: Adds the 83.49(3)(a) obligation, quoted.
- escalate: Adds the forfeiture consequence, quoted, and 83.49(3)(c) fee-shifting.

When a letter is shown, tell the tenant that sending it does not start any deadline the program computes for this situation. The only notice from a tenant that the program tracks here is the one in 83.49(5), which says that "any tenant who vacates or abandons the premises before the expiration of the term specified in the rental agreement" (Fla. Stat. 83.49(5)) "must give at least 7 days’ written notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises" (Fla. Stat. 83.49(5)). The same sentence also covers week-to-week, month-to-month, and other periodic tenancies. Whether it applies to them turns on when they moved out and on their lease (the sentence begins "Except when otherwise provided by the terms of a written rental agreement", Fla. Stat. 83.49(5)); offer to apply it to their confirmed facts.

The tenant delivers the letter. Read the lease's clause on where and how notices to the landlord must be sent (search_lease), and quote it when you ask how they will send it.

## Mistakes to avoid

- Applying either landlord clock without saying which date it counts from, or using the lease end date without the move-out date beside it.
- Saying the landlord forfeits the right to impose a claim unless the record shows both conditions: the tenant confirmed that no notice of a claim arrived, and the program's deadlines list the 30-day notice date as passed. Never your own count.
- Stopping at the forfeiture. The same sentence lets the landlord "file an action for damages after returning the security deposit to the tenant" (Fla. Stat. 83.49(3)(a)).
- Applying 83.49(3)(a) to an early move-out or a periodic tenancy without 83.49(5), whose missing 7-day notice "relieves the landlord of the notice requirement of paragraph (3)(a)" (Fla. Stat. 83.49(5)).
- Promising fees and costs without the condition in 83.49(3)(c), which applies when "either party institutes an action in a court of competent jurisdiction to adjudicate the party’s right to the security deposit" (Fla. Stat. 83.49(3)(c)), and then to the prevailing party.
- Treating a nonrefundable fee as outside 83.49 without reading 83.491.
- Computing any date yourself.
