---
name: neighbor_disturbance
description: "A neighbor or another tenant keeps disturbing the tenant (noise, parties, or similar), and the tenant wants the landlord to deal with it."
sections: ["83.52", "83.56", "83.64", "83.42", "83.505"]
clocks: []
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
  note: "This playbook has no clocks. Ch. 83 part II sets no deadline for a landlord to act on one tenant's complaint about another."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.52.txt, statutes/83.56.txt, statutes/83.64.txt, statutes/83.42.txt, statutes/83.505.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/neighbor_disturbance.yaml version 0.5"
---
## When to load this skill

Load this skill when a neighbor or another tenant keeps disturbing the tenant (noise, parties, or similar) and the tenant wants the landlord to deal with it. It covers what the landlord may do about the person disturbing, and whether the tenant can end their own lease because the landlord has not dealt with it. It does not decide that the disturbance is unreasonable, and it does not say the landlord must act; both are open (see below). If the landlord has sent the tenant a notice about the tenant's own conduct, load notice_received_violation instead of, or as well as, this skill.

The statute leaves some housing out of this part: "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)) This matters when the tenant lives in college housing. The tool records the facts and does not decide whether this applies to the tenant's housing. Say that it could matter and that the tool does not decide it.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold. Never ask whether something meets a term of the statute or the lease; you apply the term to their answer.

### From the lease (search_lease)

- Whether the lease promises to enforce its rules against other tenants, or promises quiet enjoyment. Try more than one wording ('quiet enjoyment', 'noise', 'disturb', 'rules').
- The lease's quiet hours or rules, where it has them, to set beside what the tenant describes.
- The notices clause: where and how the tenant's letter must be sent to the landlord, and whether the lease or an addendum mentions notices by e-mail.

### From the tenant

- What the disturbance is, in their own words, and who is causing it, as far as they know (for example, the people in the unit above).
- Whether the person causing it rents from the same landlord (for example, another unit in the same building or complex).
- The date it started, or when they first noticed it, and how often it happens and at what times.
- Whether they have complained to the landlord or the leasing office. If so: the date of the first complaint; whether any complaint was in writing (a letter, an e-mail, the resident portal); what the landlord has said or done so far.
- For the written complaint that says the most about what they will do if it goes on: how it reached the landlord (handed over, regular mail, certified mail, e-mail, a resident portal, a text, something else), whether it says anything about ending the lease or moving out, and the sentences that say what they asked for and what they will do if the disturbance goes on, word for word.
- Whether they have reported it to anyone else, such as the police or the city.

No deadline runs from these facts. Part II sets no deadline for a landlord to act on one tenant's complaint about another, so the program computes no date for this situation.

### Evidence worth keeping

- A log of each disturbance, with the date, the times it started and stopped, and what it was.
- Recordings or videos, with dates and times.
- Every complaint to the landlord or the office, with its date, how it was sent, and any reply.
- Names of other neighbors who were disturbed.
- Any report to the police or the city, with its number.

## What the tenant can do

Before any step, say whether the tenant can do it, what that turns on, and what is left to do. Each condition below is settled in one of four ways. The lease can settle it: read that clause with search_lease and say what it says. The tenant can tell you. It is not settled: give the open question from the section below. Or it is outside the tool: say what to check and where.

### End the lease because the landlord has not dealt with the disturbance

This is by a written notice to the landlord and 7 days. The statute: "within 7 days after delivery of written notice by the tenant" (Fla. Stat. 83.56(1)). The tool computes no date for it here; do not count the 7 days yourself. All three conditions need to be met.

1. The landlord failed a material provision of the lease: "If the landlord materially fails to comply with s. 83.51 (1) or material provisions of the rental agreement" (Fla. Stat. 83.56(1)). Either of these ways:
   - The lease promises something about other tenants' conduct, or the tenant's quiet enjoyment, that the landlord has not done (lease). Read the lease with search_lease, say what it promises, and say whether the landlord has done it, from what the tenant told you.
   - The landlord's failure to act is itself a failure of the lease. This is not settled; give the open question on ending the tenant's own lease.
2. The person disturbing rents from the same landlord: the statute names "a subsequent or continued unreasonable disturbance" (Fla. Stat. 83.56(2)(a)) among the noncompliance a landlord may end a tenancy for. The tenant tells you whether the person rents from the same landlord. If they do not, the remedy the statute gives the landlord is against its own tenant; say that. If they do, whether the landlord must use that remedy is not settled; give the open question on remedy, not duty.
3. The disturbance is unreasonable: the statute's duty is to conduct oneself "in a manner that does not unreasonably disturb the tenant’s neighbors or constitute a breach of the peace" (Fla. Stat. 83.52(7)). This is not settled by the statute; give the open question on what is unreasonable.

Steps, in order:

1. Deliver the written notice to the landlord in a way 83.56(4) allows: "The delivery of the written notices required by subsections (1)-(3) shall be by mailing, delivering a true copy thereof, e-mailing in accordance with s. 83.505" (Fla. Stat. 83.56(4)). If the complaint was handed over or mailed (regular or certified), it fits. E-mail counts only as 83.505 allows: ask whether the tenant and the landlord signed an addendum agreeing to notices by e-mail, and read the lease's notices clause. A resident portal message or a text is not one of the ways the sentence names. For any other way, ask how the complaint reached the landlord and set it beside those ways.
2. The notice names the problem and says the tenant intends to end the lease because of it: "specifying the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof" (Fla. Stat. 83.56(1)). Set the words of the tenant's complaint beside these words and say what you see. A complaint that only asks the landlord to act does not say this.

Also see the open question on whose duty it is, for a person disturbing who does not rent from the tenant's landlord.

## What the statute does not settle

For each question below, tell the tenant in plain words that the law does not settle it, give every reading with what it would mean for them, and pick none. Where one step works under every reading, say so.

- Whose duty it is. 83.52(7) says the tenant shall "Conduct himself or herself, and require other persons on the premises with his or her consent to conduct themselves, in a manner that does not unreasonably disturb the tenant’s neighbors or constitute a breach of the peace." (Fla. Stat. 83.52(7)) It states each tenant's own duty. Apply it by who the tenant says is causing the disturbance. When that person rents from the same landlord, the landlord holds the remedy in 83.56(2)(a) against them. When they do not, the tenant's landlord has no tenancy with them under part II, and the tenant's options run through the tenant's own lease and law the tool does not hold. Say that the tool does not work out those options.
- Remedy, not duty. 83.56(2)(a) names "a subsequent or continued unreasonable disturbance" (Fla. Stat. 83.56(2)(a)) among the noncompliance a landlord may end a tenancy for. The stored text gives the landlord that remedy against the tenant who disturbs. Whether the landlord must use it is not settled.
  - The landlord need not act: 83.56(2) says what the landlord 'may' do, and no sentence in part II requires a landlord to act on one tenant's complaint about another.
  - The landlord must act if its lease says so: a lease clause promising quiet enjoyment, or binding every tenant to rules, can make the landlord's not acting a failure to comply with "material provisions of the rental agreement" (Fla. Stat. 83.56(1)).
- What is unreasonable. Neither 83.52(7) nor 83.56(2)(a) says when a disturbance is unreasonable. Set the tenant's description, the times, and the frequency beside the words.
  - Unreasonable by an ordinary neighbor's measure: how loud, how late, and how often, as the tenant describes it.
  - Measured against the lease's quiet hours or rules where the lease has them, since 83.56(2) also reaches noncompliance with "reasonable rules or regulations" (Fla. Stat. 83.56(2)).
- Ending the tenant's own lease. 83.56(1) lets a tenant end the lease when the landlord "materially fails to comply with s. 83.51 (1) or material provisions of the rental agreement within 7 days after delivery of written notice by the tenant specifying the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof" (Fla. Stat. 83.56(1)). Whether a landlord's not acting on a neighbor's disturbance is such a failure is not settled.
  - It can be, when the lease has a clause the landlord fails by not acting, and the tenant gives the 7-day written notice that states the intention to terminate.
  - It is not: the disturbance is the neighbor's failure of 83.52(7), not a duty the landlord owes under 83.51(1), so there is nothing for the landlord to 'comply with' unless the lease adds it.

## Letters

Every letter needs: today's date, what the disturbance is and when it happens, the dates of earlier complaints, what the tenant asks the landlord to do, and how the tenant will deliver it. The tenant sends the letter; you send nothing. Read the lease's notices clause with search_lease and tell the tenant where and how the lease says notices go to the landlord.

The postures, each with its own line:

- preserve: Describes the disturbance, with dates, and the earlier complaints, and asks the landlord to address it. Cites nothing.
- assert: Adds the 83.52(7) sentence on not disturbing neighbors, quoted.
- escalate: Adds the 83.56(2)(a) words on "a subsequent or continued unreasonable disturbance", quoted, as the statute's example of noncompliance a landlord may act on.

When a letter is shown, tell the tenant this. No deadline in Fla. Stat. ch. 83 part II runs from a letter about a neighbor's disturbance, and the tool computes none for this situation. A letter saying they intend to end their own lease is a different notice: 83.56(1) describes "written notice by the tenant specifying the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof" (Fla. Stat. 83.56(1)), and whether it fits a neighbor's disturbance is not settled by the stored text.

## Mistakes to avoid

- Saying the landlord must stop the disturbance or evict the neighbor. The stored text gives the landlord a remedy it 'may' use.
- Calling the disturbance unreasonable without setting the tenant's description, times, and frequency beside the open question.
- Saying the tenant may end the lease without the lease clause the landlord failed and the written notice 83.56(1) requires, or may hold back rent over it. 83.60(1)(b) speaks only of "a material noncompliance with s. 83.51 (1)" (Fla. Stat. 83.60(1)(b)). Section 83.60 is not loaded with this skill; fetch it before you cite it.
- Treating a neighbor who rents from someone else as someone the tenant's landlord can act against under 83.56(2)(a).
- Saying a step the landlord took after the tenant complained was retaliation. 83.64(1) turns on an act "primarily because the landlord is retaliating against the tenant" (Fla. Stat. 83.64(1)), and 83.64(3) says "this section does not apply if the landlord proves that the eviction is for good cause" (Fla. Stat. 83.64(3)).
