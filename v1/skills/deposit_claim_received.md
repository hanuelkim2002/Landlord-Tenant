---
name: deposit_claim_received
description: "Tenant has received the landlord's written notice that the landlord intends to keep all or part of the security deposit (a claim on the deposit)."
sections: ["83.49", "83.505"]
clocks:
  - id: claim_notice_deadline
    actor: landlord
    trigger: tenancy_terminated
    days: 30
    direction: after
    cite: "83.49(3)(a)"
    quote: "If the landlord intends to impose a claim on the deposit, the landlord must, within 30 days after the termination of the rental agreement, provide the tenant written notice by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505 of his or her intention to impose a claim on the deposit and the reason for imposing the claim."
    consequence: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit and may not seek a setoff against the deposit but may file an action for damages after returning the security deposit to the tenant."
  - id: tenant_objection_deadline
    actor: tenant
    trigger: claim_notice_date
    days: 15
    direction: after
    cite: "83.49(3)(b)"
    quote: "Unless the tenant objects to the imposition of the landlord’s claim or the amount thereof within 15 days after receipt of the landlord’s notice of intention to impose a claim, the landlord may then deduct the amount of his or her claim and shall remit the balance of the deposit to the tenant within 30 days after the date of the notice of intention to impose a claim for damages."
    consequence: "The failure of the tenant to make a timely objection does not waive any rights of the tenant to seek damages in a separate action."
  - id: landlord_remit_balance
    actor: landlord
    trigger: claim_notice_dated
    days: 30
    direction: after
    cite: "83.49(3)(b)"
    quote: "shall remit the balance of the deposit to the tenant within 30 days after the date of the notice of intention to impose a claim for damages"
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.49.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/deposit_claim_received.yaml version 0.5"
---
## When to load this skill

Load this skill when the tenant has received the landlord's written notice that the landlord intends to keep all or part of the security deposit (a claim on the deposit). It rests on 83.49 (the deposit) and 83.505 (notices by e-mail).

- If the tenant says no notice of a claim ever arrived, also load deposit_not_returned. It covers a deposit that was not returned and a landlord who sent no claim.
- Money the lease labels nonrefundable may fall under 83.491 instead. Do not treat it as outside 83.49 without reading 83.491 (fetch it with get_statute_section).
- The statute names deposits it does not cover: "This section does not apply to transient rentals by hotels or motels as defined in chapter 509 or in those instances in which the amount of rent or deposit, or both, is regulated by law or by rules or regulations of a public body" (Fla. Stat. 83.49(4)). The tool does not decide whether this applies. Say what the words are and what you would need to know.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold, one or two things at a time and only what your answer turns on. Never ask whether something meets a term of the statute or the lease; ask what happened, then apply the term yourself.

### In the lease (search_lease; try a second wording if the first finds nothing)

- The security deposit clause: the amount, and that the lease calls it a deposit.
- What the lease says the landlord may deduct for. Set it beside the reason the notice gives.
- The move-out requirements. Cleaning and carpet clauses are the usual basis of a claim.
- Any money labeled nonrefundable (see 83.491 above).
- Where the tenant's objection must be sent under the lease, alongside the address the notice gives.
- Whether one roommate's damage can be charged against the whole deposit.

### From the tenant

- How much was the deposit? (Only if the lease does not show it.)
- What date did the lease end, or what date was it terminated? Put it beside the lease's end date, and tell the tenant when they differ.
- What date is printed on the landlord's notice, and what date did they receive it? Ask for both; they can differ.
- How did the notice reach them: certified mail, regular mail, e-mail, handed to them, a text or a resident portal message, something else, or they do not know?
- How much does the notice say the landlord is claiming, and what reason does it give? Ask them to copy the reason from the notice.
- Does the notice tell them they must object in writing within 15 days, and give an address to send the objection to?
- Have they already sent the landlord a written objection? If so, what date, and how did it reach the landlord: a letter mailed to the address the notice gives, a letter handed in at that address, a letter to another address, e-mail, a text or a resident portal message, or something else?

### What the deadlines count from

The program computes dates only from facts the tenant has confirmed, so get these proposed and confirmed:

- The date the rental agreement ended. The landlord's 30 days to give notice of a claim count from it.
- The date the tenant received the notice. The tenant's 15 days to object count from it.
- The date printed on the notice. The landlord's 30 days to send the balance count from it.

### Evidence to suggest the tenant keep

- The notice itself, with the envelope or the full e-mail headers.
- The date the notice arrived: a postmark, a delivery scan, an e-mail timestamp.
- Move-in and move-out photos, and the move-out walkthrough form if there is one.
- Receipts for cleaning or repairs the tenant paid for.
- The objection letter, with proof of how and when it was sent.

## What the tenant can do

Tell the tenant first whether they can do each of these and what it turns on, before any step. Each condition is settled by the lease (read that clause with search_lease and say what it says), by the tenant (ask), by the program's deadlines (call get_deadlines), or not at all (the statute does not settle it: give every reading, see the open questions below).

### Object in writing to the claim within 15 days of receiving the notice, so the landlord may not simply deduct it (Fla. Stat. 83.49(3)(b))

One condition: the objection is made within the 15 days after the tenant received the notice. The statute: "Unless the tenant objects to the imposition of the landlord’s claim or the amount thereof within 15 days after receipt of the landlord’s notice of intention to impose a claim, the landlord may then deduct the amount of his or her claim" (Fla. Stat. 83.49(3)(b)). It is met in either way:

- The 15 days have not ended. Only the program's deadlines settle this. If they show the 15 days have passed, say so, and tell the tenant that not objecting in time does not waive their right to seek damages in a separate action (quoted under Deadlines).
- The objection the tenant already sent went out within the 15 days. Ask the date it was sent, to put beside the last day of the 15 days the program's deadlines show.

The step: a written objection to the claim or its amount, sent to the address the notice gives. The statute's model notice says: "You are hereby notified that you must object in writing to this deduction from your security deposit within 15 days after the time you receive this notice" (Fla. Stat. 83.49(3)(a)).

- If the objection went as a letter to the address the notice gives, mailed or handed in, the step is done.
- If it went another way (e-mail, a text, a portal message) or to another address, whether that counts is not settled. See the third open question.

What counts as receipt, and which ways of objecting count, are also open (the first and third open questions).

### Get the whole deposit back because the landlord did not give the required notice of a claim within the 30 days (Fla. Stat. 83.49(3)(a))

Both conditions must be met. No steps are listed beyond a letter asking for the deposit (see Letters).

1. The 30 days after the end of the rental agreement have passed: "within 30 days after the termination of the rental agreement" (Fla. Stat. 83.49(3)(a)). Only the program's deadlines settle this. If they show the 30 days have not passed, a notice of a claim may still come in time, so the option is not open yet.
2. The notice the landlord gave was not the required notice within those 30 days: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit" (Fla. Stat. 83.49(3)(a)). It is met in either way:
   - The notice was sent after the 30 days. Ask for the date it was sent (its postmark, or the e-mail's date), to put beside the last day of the 30 days the program's deadlines show.
   - The notice did not come by certified mail to the last known mailing address or by e-mail as 83.505 allows, and that makes it not the required notice. The statute names the ways: "by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505" (Fla. Stat. 83.49(3)(a)). This applies when it came by regular mail, e-mail, in hand, as a text or a portal message, or some other way, and whether it makes the notice not the required one is not settled. See the second open question. If the tenant does not know how it came, ask them to check the envelope (a certified mail label or receipt) or the e-mail, which shows it.

What counts as receipt is also open (the first open question).

## Deadlines

The program computes and prints every date from confirmed facts. Never write, count, or compare a date yourself: call get_deadlines, and say a deadline has passed or is upcoming only as its result says. The counting rule is an assumption: Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Each deadline counts from its own date, so ask for the date printed on the notice and the date it was received.

- The landlord's 30 days to give written notice of a claim. It counts from the date the rental agreement ended. The notice must go by certified mail to the tenant's last known mailing address, or by e-mail as 83.505 allows: "If the landlord intends to impose a claim on the deposit, the landlord must, within 30 days after the termination of the rental agreement, provide the tenant written notice by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505 of his or her intention to impose a claim on the deposit and the reason for imposing the claim." (Fla. Stat. 83.49(3)(a)). If it is missed: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit and may not seek a setoff against the deposit but may file an action for damages after returning the security deposit to the tenant." (Fla. Stat. 83.49(3)(a)).
- The tenant's 15 days to object. It counts from the date the tenant received the notice. The statute: "Unless the tenant objects to the imposition of the landlord’s claim or the amount thereof within 15 days after receipt of the landlord’s notice of intention to impose a claim, the landlord may then deduct the amount of his or her claim and shall remit the balance of the deposit to the tenant within 30 days after the date of the notice of intention to impose a claim for damages." (Fla. Stat. 83.49(3)(b)). Missing it: "The failure of the tenant to make a timely objection does not waive any rights of the tenant to seek damages in a separate action." (Fla. Stat. 83.49(3)(b)).
- The landlord's 30 days to remit the balance. It counts from the date printed on the notice: "shall remit the balance of the deposit to the tenant within 30 days after the date of the notice of intention to impose a claim for damages" (Fla. Stat. 83.49(3)(b)). The sentence it comes from begins "Unless the tenant objects" (Fla. Stat. 83.49(3)(b)). The program computes this date in every case and shows the quote; it does not decide whether the condition is met.

## What the statute does not settle

For each of these, tell the tenant in plain words that the law does not settle it, give every reading and what it would mean for them, and pick none.

### When the tenant "received" the notice

The objection clock runs from "receipt of the landlord’s notice" (Fla. Stat. 83.49(3)(b)) while the remit clock runs from "the date of the notice" (Fla. Stat. 83.49(3)(b)). The program records both dates and computes both clocks from them. For a notice sent by e-mail, 83.505(4) says a notice "is deemed delivered at the time it is sent, unless the e-mail is returned to the sender as undeliverable" (Fla. Stat. 83.505(4)). Whether that time is the receipt the objection clock counts from is not settled by the stored text.

- Receipt is the time the e-mail was sent: 83.505(4) makes an e-mailed notice "deemed delivered at the time it is sent" (Fla. Stat. 83.505(4)), and a notice delivered is a notice received.
- Receipt is when the tenant actually got the notice: 83.49(3)(b) says receipt, not delivery, and the model notice tells the tenant to object "within 15 days after the time you receive this notice" (Fla. Stat. 83.49(3)(a)).

### A notice of a claim that came some way other than certified mail

The statute names two ways to give the notice of a claim (quoted under the second option). 83.505(1) allows e-mail only "if the parties have signed an addendum to the rental agreement" (Fla. Stat. 83.505(1)). Apply these to how the tenant says the notice came. If the tenant has not said whether they signed such an addendum, that condition is not known yet. What stays open is a notice that reached the tenant in time some other way.

- A notice given another way is not the required written notice, and "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits the right to impose a claim upon the security deposit" (Fla. Stat. 83.49(3)(a)).
- A notice the tenant actually received in time is enough: 83.505(6) says the section "does not preclude service of notices by any other means permitted by law" (Fla. Stat. 83.505(6)), and the tenant had what the notice is for.

### How the tenant may object

The statute's model notice says the tenant "must object in writing" (Fla. Stat. 83.49(3)(a)) and that the objection "must be sent to (landlord’s address)" (Fla. Stat. 83.49(3)(a)). A written objection sent to that address within the 15 days the program's deadlines show meets those words. What stays open is an objection made another way (e-mail, a text, a resident portal) or sent to another address.

- Only a writing sent to the address the notice gives counts: the form says the objection "must be sent to (landlord’s address)" (Fla. Stat. 83.49(3)(a)).
- Any written objection the landlord receives in time counts: 83.49(3)(b) itself turns on whether "the tenant objects to the imposition of the landlord’s claim or the amount thereof within 15 days after receipt" (Fla. Stat. 83.49(3)(b)), and names no method.

## Letters

The tenant sends every letter; you send nothing. Every letter holds: today's date, the claim amount and reason as stated in the notice, the tenant's objection, the deposit amount, a return address, a response deadline computed by the tool, and the delivery method. The postures, each line as written:

- preserve: States that the tenant objects to the claim, the amount, and the reason. Asks for return of the full deposit. Cites nothing.
- assert: Adds the 83.49(3)(b) sentence on the 15-day objection, quoted.
- escalate: Adds the 83.49(3)(c) sentence on court costs and attorney fees, quoted.

When a letter is shown, tell the tenant that for this situation the letter is the objection itself, and that the program computed the 15-day date from the day they said they received the notice. If the letter is sent after that date, 83.49(3)(b) says the failure to object in time "does not waive any rights of the tenant to seek damages in a separate action" (Fla. Stat. 83.49(3)(b)).

Read the lease's clause on where notices to the landlord must be sent (search_lease), alongside the address the notice gives, and quote it when you ask how they will send the letter.

## Mistakes to avoid

- Counting the objection window from the date printed on the notice, or the remit window from the date it was received. Each clock counts from its own date.
- Treating the remit clock as unconditional. It comes from a sentence that begins "Unless the tenant objects" (Fla. Stat. 83.49(3)(b)).
- Saying the tenant lost the deposit by not objecting in time. The statute says: "The failure of the tenant to make a timely objection does not waive any rights of the tenant to seek damages in a separate action." (Fla. Stat. 83.49(3)(b)).
- Saying the claim is forfeited unless the record shows the notice came after the 30-day date the program lists, or by a way 83.49(3)(a) does not name.
- Judging the claim's amount by a standard neither the lease nor 83.49 states. 83.49 sets the notice and objection steps, not what damage a landlord may charge for; 'normal wear and tear' appears in the stored text only in 83.491, the fee in lieu of a deposit. Set the claim's reason beside the lease's move-out clauses and the tenant's account.
- Computing any date yourself.
