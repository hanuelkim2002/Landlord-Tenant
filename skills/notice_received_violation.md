---
name: notice_received_violation
description: "Tenant received a landlord's written notice about a lease violation other than unpaid rent (the 7-day notice)."
sections: ["83.56", "83.52", "83.42"]
clocks:
  - id: seven_days_to_correct
    actor: tenant
    trigger: violation_notice_delivered
    days: 7
    direction: after
    applies_if: notice_offers_cure
    cite: "83.56(2)(b)"
    quote: "deliver a written notice to the tenant specifying the noncompliance, including a notice that, if the noncompliance is not corrected within 7 days from the date that the written notice is delivered, the landlord shall terminate the rental agreement by reason thereof."
    consequence: "If such noncompliance recurs within 12 months after notice, an eviction action may commence without delivering a subsequent notice pursuant to paragraph (a) or this paragraph."
  - id: seven_days_to_vacate
    actor: tenant
    trigger: violation_notice_delivered
    days: 7
    direction: after
    applies_if: notice_terminates_now
    cite: "83.56(2)(a)"
    quote: "In such event, the landlord may terminate the rental agreement, and the tenant shall have 7 days from the date that the notice is delivered to vacate the premises."
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.56.txt, statutes/83.52.txt, statutes/83.42.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/notice_received_violation.yaml version 0.6"
---
## When to load this skill

Load this skill when the tenant has received a landlord's written notice about a lease violation other than unpaid rent (the 7-day notice). There are two kinds. One gives the tenant 7 days to fix the problem. The other says the lease is terminated and gives 7 days to move out. It covers fixing the problem, defending an eviction case over the notice, and the landlord giving up the right to end the lease by accepting rent. It does not decide which kind of notice the landlord should have sent, or whether the one sent is valid. A demand for unpaid rent is a different situation; load notice_received_nonpayment for it.

The statute leaves some housing out of this part: "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)) This matters when the tenant lives in college housing. The tool records the facts and does not decide whether this applies to the tenant's housing. Say that it could matter and that the tool does not decide it.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold, from the notice in their hands. Never ask whether something meets a term of the statute or the lease; you apply the term to their answer.

### From the lease (search_lease)

- The lease clause or rule the notice points to: read it and set it beside what the notice says the tenant did.
- The notices clause: where the tenant's reply must be sent. A lease clause about notices does not change the notice rules: "The notice requirements of subsections (1)-(3) may not be waived in the rental agreement." (Fla. Stat. 83.56(4)) Give that sentence next to such a clause.
- What the lease requires when a tenant moves out, if the notice says the lease is terminated.

### From the tenant

- The date the landlord's notice was delivered to them (not the date it was written), and how it reached them: handed to them, mailed, e-mailed, left at the door, or something else.
- What the notice says they did. Ask them to copy the words from the notice.
- Whether the notice gives them 7 days to fix the problem, saying the lease will end if they do not.
- Whether the notice says the lease is terminated and gives them 7 days to move out.
- Whether, before this notice, the landlord had ever given them a written warning or notice about anything. If so, the date they got it and what it was about.
- Whether they have fixed the problem the notice describes, and on what date.
- Whether the landlord has accepted rent from them since the notice was delivered.
- Whether the landlord has filed an eviction case in court against them. If so, whether they have paid the rent the court papers claim into the court registry, or filed a motion asking the court to decide the amount.

### What the deadlines count from

The program computes a deadline (see Deadlines) only from facts the tenant has confirmed: the date the notice was delivered, whether the notice gives 7 days to fix the problem, and whether the notice says the lease is terminated and gives 7 days to move out. Only one of the two deadlines applies, depending on the kind of notice. When the tenant tells you one of these, propose it for their record, so they can confirm it.

### Evidence worth keeping

- The notice itself, with a photo of where it was left, or the envelope or the e-mail headers.
- Photos or other proof of the correction, with dates.
- Any earlier written warning.
- Receipts for rent paid after the notice.
- The lease clause or rule the notice points to.

## What the tenant can do

Before any step, say whether the tenant can do it, what that turns on, and what is left to do. Each condition below is settled in one of four ways. The lease can settle it: read that clause with search_lease and say what it says. The tenant can tell you. It is not settled: give the open question from the section below. Or it is outside the tool: say what to check and where.

### Fix the problem the notice names within 7 days

Fixing it means the landlord may not end the lease on this notice. Two conditions need to be met.

1. The notice gives the tenant 7 days to fix the problem. The statute describes it: "if the noncompliance is not corrected within 7 days from the date that the written notice is delivered, the landlord shall terminate the rental agreement by reason thereof" (Fla. Stat. 83.56(2)(b)). The tenant tells you whether the notice gives that chance. If it says the lease ends at once, this option is not open on this notice; say so.
2. The 7 days after delivery have not ended, or the problem was fixed within them: "within 7 days from the date that the written notice is delivered" (Fla. Stat. 83.56(2)(b)). Whether the 7 days have ended comes only from the program's deadlines. If the tenant says they fixed the problem, ask for the date, and set it beside the last day of the 7 days the program shows. The tool compares no dates, so say that and let the tenant see it.

The step: the problem the notice names is fixed. The statute's form of this notice says: "Demand is hereby made that you remedy the noncompliance within 7 days of receipt of this notice" (Fla. Stat. 83.56(2)(b)). The tenant tells you whether it is fixed. Two open questions apply: delivered or received, and the 12 months.

### Defend an eviction case on the ground that the notice ended the lease without the chance to fix

This is for a notice that ended the lease at once over a violation the statute says should have had a chance to be fixed. Four conditions need to be met.

1. The notice ends the lease with no chance to fix the problem. The statute's form for it says: "You are advised that your lease is terminated effective immediately." (Fla. Stat. 83.56(2)(a)) The tenant tells you whether their notice says that.
2. The violation is of a nature the tenant should be given a chance to fix: "If such noncompliance is of a nature that the tenant should be given an opportunity to cure it" (Fla. Stat. 83.56(2)(b)). This is not settled for a violation like neither list's examples; give the open question on which paragraph applies.
3. There was no written warning of a similar violation in the 12 months before: "if the noncompliance constitutes a subsequent or continuing noncompliance within 12 months of a written warning by the landlord of a similar violation" (Fla. Stat. 83.56(2)(a)). The tenant tells you whether there was an earlier warning. If there was, set the date of the earlier warning and what it was about beside this notice. The tool does not count months.
4. The landlord has filed an eviction case: "Any tenant who wishes to defend against an action by the landlord for possession of the unit for noncompliance of the rental agreement or of relevant statutes must comply with s. 83.60 (2)." (Fla. Stat. 83.56(5)(b)) If the tenant says no case has been filed, say a defense is raised in a case once one is filed.

The step: the rent is paid into the registry of the court, as the statute requires of a tenant who defends ("must comply with s. 83.60 (2)" (Fla. Stat. 83.56(5)(b))). The tenant tells you whether they did. Section 83.60 is not loaded with this skill; fetch it before you describe what it requires. The open question on the 12 months applies.

### The landlord gave up ending the lease by accepting rent knowing of the violation

Two conditions need to be met. There are no steps for the tenant to take.

1. The landlord accepted rent after knowing of the violation: "If the landlord accepts rent with actual knowledge of a noncompliance by the tenant" (Fla. Stat. 83.56(5)(a)). The tenant tells you whether the landlord has accepted rent since the notice.
2. The violation did not go on after the rent was accepted, nor happen again: "but not for any subsequent or continuing noncompliance" (Fla. Stat. 83.56(5)(a)). Ask whether the problem the notice names stopped before the rent was accepted and has not happened again.

The full sentence: "If the landlord accepts rent with actual knowledge of a noncompliance by the tenant or accepts performance by the tenant of any other provision of the rental agreement that is at variance with its provisions, or if the tenant pays rent with actual knowledge of a noncompliance by the landlord or accepts performance by the landlord of any other provision of the rental agreement that is at variance with its provisions, the landlord or tenant waives his or her right to terminate the rental agreement or to bring a civil action for that noncompliance, but not for any subsequent or continuing noncompliance." (Fla. Stat. 83.56(5)(a))

## Deadlines

The program computes two deadlines, both the tenant's, both counted from the date the landlord's notice was delivered (not the date it was written), once the tenant has confirmed that date. Only one applies.

- Seven days to fix the problem. It counts only when the notice gives the chance to fix. The statute: "deliver a written notice to the tenant specifying the noncompliance, including a notice that, if the noncompliance is not corrected within 7 days from the date that the written notice is delivered, the landlord shall terminate the rental agreement by reason thereof." (Fla. Stat. 83.56(2)(b)) The statute then adds: "If such noncompliance recurs within 12 months after notice, an eviction action may commence without delivering a subsequent notice pursuant to paragraph (a) or this paragraph." (Fla. Stat. 83.56(2)(b))
- Seven days to vacate. It counts only when the notice says the lease is terminated. The statute: "In such event, the landlord may terminate the rental agreement, and the tenant shall have 7 days from the date that the notice is delivered to vacate the premises." (Fla. Stat. 83.56(2)(a))

The program computes and prints every date. Never write, count, or compare a date yourself, not even for 'what if it ran from another day'. Whether a period has passed comes only from the program's deadlines (get_deadlines). The program prints the counting convention with each date: calendar days, the delivery day not counted, no weekend or holiday adjustment. It is an assumption: Florida's court rule for counting days has not been checked against these statutory deadlines. If the tenant asks how the days are counted, say so. The tool counts days only and does not compute a 12-month period.

## What the statute does not settle

For each question below, tell the tenant in plain words that the law does not settle it, give every reading with what it would mean for them, and pick none. Where one step works under every reading, say so.

- Which paragraph applies. 83.56(2)(a) covers noncompliance "of a nature that the tenant should not be given an opportunity to cure it" (Fla. Stat. 83.56(2)(a)), with examples: "destruction, damage, or misuse of the landlord’s or other tenants’ property by intentional act" (Fla. Stat. 83.56(2)(a)) and "a subsequent or continued unreasonable disturbance" (Fla. Stat. 83.56(2)(a)). 83.56(2)(b) covers noncompliance "of a nature that the tenant should be given an opportunity to cure it" (Fla. Stat. 83.56(2)(b)), with examples such as "having or permitting unauthorized pets, guests, or vehicles" (Fla. Stat. 83.56(2)(b)). The tenant's notice shows which kind the landlord sent; set the violation it describes beside each list. What stays open is a violation like neither list's examples, sent as a notice that ends the tenancy at once.
  - The landlord's notice stands when the violation is like 83.56(2)(a)'s examples, or repeats within 12 months of a written warning of a similar violation.
  - A violation like 83.56(2)(b)'s examples must get the notice with 7 days to correct, and a notice under 83.56(2)(a) for it denies the tenant the chance the statute says the tenant 'should be given'.
- Delivered or received. The text of 83.56(2)(b) runs the period "from the date that the written notice is delivered" (Fla. Stat. 83.56(2)(b)), while the model form says "within 7 days of receipt of this notice" (Fla. Stat. 83.56(2)(b)). The tool counts from the delivery date the tenant gives. When delivery and receipt are the same day the question does not arise.
  - The statute's own words govern: 7 days from the date the written notice is delivered.
  - The form the statute prescribes tells the tenant 'within 7 days of receipt', and a tenant who relies on it should not lose by the difference.
- The 12 months. Both paragraphs refer to a period of 12 months: a "written warning by the landlord of a similar violation" (Fla. Stat. 83.56(2)(a)), and noncompliance that "recurs within 12 months after notice" (Fla. Stat. 83.56(2)(b)). This tool counts in days and does not compute a 12-month period. Set the dates the tenant gives beside the words and say the tool does not count the months.

## Letters

Every letter needs: today's date, the notice and its date, the tenant's account or the correction made, and how the tenant will deliver it. The tenant sends the letter; you send nothing. Read the lease's notices clause with search_lease and tell the tenant where and how the lease says the reply must be sent.

The postures, each with its own line:

- preserve: States the tenant's account and any correction made, and asks the landlord to confirm the matter is resolved. Cites nothing.
- assert: Adds the 83.56(2)(b) sentence, quoted.
- escalate: Adds the 83.56(5)(a) sentence, quoted.

When a letter is shown, tell the tenant this. The 7-day periods the program computes run from the date the landlord's notice was delivered, as they gave it. 83.56(2)(b) speaks of a noncompliance "corrected within 7 days from the date that the written notice is delivered" (Fla. Stat. 83.56(2)(b)). A letter from them does not change that date. What the statute looks to is whether the noncompliance was corrected within the period, and the letter can say when it was.

## Mistakes to avoid

- Counting from the date the notice was written instead of the date it was delivered.
- Saying the tenant must leave in 7 days when the notice offers a chance to correct, or that correcting the violation ends the matter when the notice ends the tenancy at once.
- Saying the violation was corrected in time without the tenant's correction date beside the 7-day date the program shows. The tool compares no dates.
- Saying the landlord may terminate, or that the tenant failed to cure, on a notice that offers a chance to correct while its 7 days have not run. The landlord terminates only "if the noncompliance is not corrected within 7 days from the date that the written notice is delivered" (Fla. Stat. 83.56(2)(b)). Whether that period has passed comes from the program's deadlines.
- Skipping 83.56(5)(a). A landlord who "accepts rent with actual knowledge of a noncompliance by the tenant" (Fla. Stat. 83.56(5)(a)) waives the right to terminate for it, "but not for any subsequent or continuing noncompliance" (Fla. Stat. 83.56(5)(a)).
- Computing a 12-month period. The tool counts days only.
- Computing any date yourself.
