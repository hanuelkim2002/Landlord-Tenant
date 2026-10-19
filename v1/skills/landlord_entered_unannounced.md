---
name: landlord_entered_unannounced
description: "The landlord, or someone sent by the landlord, entered the tenant's unit without notice or at an unreasonable time."
sections: ["83.53", "83.67", "83.64", "83.55", "83.42"]
clocks: []
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
  note: "This playbook has no clocks. The notice rule in 83.53(2) is stated in hours, which compute_deadlines does not support."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.53.txt, statutes/83.67.txt, statutes/83.42.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/landlord_entered_unannounced.yaml version 0.6"
---
## When to load this skill

Load this skill when the landlord, or someone sent by the landlord, entered the tenant's unit without notice or at an unreasonable time. It also covers a landlord who changed the locks, cut off a utility, or removed doors, windows, or the tenant's belongings. It covers whether the entry was one the statute allows, and the two damages claims that can follow. It does not compute any deadline, and it does not count hours.

The statute leaves some housing out of this part: "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)) This matters when the tenant lives in college housing. The tool records the facts and does not decide whether this applies to the tenant's housing. Say that it could matter and that the tool does not decide it.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold. Never ask whether something meets a term of the statute or the lease; you apply the term to their answer.

### From the lease (search_lease)

- The notices clause: where and how the tenant's letter must be sent to the landlord.

### From the tenant

- The date of the entry and the time of day.
- The reason the landlord gave for entering, if any.
- Whether the landlord told them ahead of time that they would enter. If so, when and how (the day and time of the message, and whether it was in writing).
- Whether they agreed to the entry.
- Whether the landlord said it was an emergency.
- Whether the landlord had asked to come in before and they refused, and why.
- Whether they were away from the unit when it happened. If so, for how long, whether their rent was paid up to date, and whether they had told the landlord they would be away.
- Whether the landlord has entered without notice more than once, and how often, at what times, and whether it keeps happening.
- Whether the landlord has changed the locks, cut off a utility, or removed doors, windows, or their belongings, and why the landlord said it did.
- What the entry cost them, with receipts or other proof.

No deadline runs from these facts, so the program computes no date for this situation.

### Evidence worth keeping

- Every message from the landlord about entering, with its date and time.
- Door camera footage or photos, with timestamps.
- Names of anyone who saw the entry.
- A list of every entry, with the date, the time, and any reason given.
- Photos of changed locks, missing doors or windows, or utility shutoff notices.

## What the tenant can do

Before any step, say whether the tenant can do it, what that turns on, and what is left to do. Each condition below is settled in one of four ways. The lease can settle it: read that clause with search_lease and say what it says. The tenant can tell you. It is not settled: give the open question from the section below. Or it is outside the tool: say what to check and where.

### Damages of at least 3 months' rent for a utility cut off, a lockout, or things removed

The statute: "A landlord who violates any provision of this section shall be liable to the tenant for actual and consequential damages or 3 months’ rent, whichever is greater, and costs, including attorney’s fees." (Fla. Stat. 83.67(6)) Do not promise an amount. Two conditions need to be met.

1. The landlord cut off a utility, blocked the tenant's access (such as by changing the locks), or removed doors, windows, or the tenant's belongings. The tenant tells you. If they say the landlord did none of these, this option is not open.
2. Anything removed was not removed for maintenance, repair, or replacement, nor after a surrender, abandonment, or lawful eviction: the landlord "shall not remove the outside doors, locks, roof, walls, or windows of the unit except for purposes of maintenance, repair, or replacement" (Fla. Stat. 83.67(5)). Ask what the landlord cut off, locked, or removed, and why. A removal for maintenance, repair, or replacement, and a removal of the tenant's belongings after a surrender, abandonment, or lawful eviction, are the ones the statute allows. Set the tenant's answer beside those and say what you see.

### Recover the damages caused by an entry the statute does not allow

The statute: "the aggrieved party may recover the damages caused by the noncompliance" (Fla. Stat. 83.55). It is open only when none of the ways the statute allows an entry fits. The ways in are in 83.53(2): "The landlord may enter the dwelling unit at any time for the protection or preservation of the premises." (Fla. Stat. 83.53(2)); for repair, "upon reasonable notice to the tenant and at a reasonable time for the purpose of repair of the premises" (Fla. Stat. 83.53(2)); and, for the further purposes in 83.53(1) (inspecting, supplying agreed services, showing the unit, and the others listed), only in the circumstances 83.53(2)(a) to (d) list. Go through these conditions against what the tenant told you. All need to be met.

1. The tenant did not agree to the entry: "With the consent of the tenant" (Fla. Stat. 83.53(2)(a)). The tenant tells you.
2. It was not an emergency: "In case of emergency" (Fla. Stat. 83.53(2)(b)). If the tenant says the landlord claimed an emergency, whether it was one is not settled on what you have; give the open question on the purpose of the entry.
3. The entry was not for the protection or preservation of the premises. This is not settled by the tenant's account alone; give the open question on the purpose of the entry.
4. The tenant had not unreasonably refused to let the landlord in: "When the tenant unreasonably withholds consent" (Fla. Stat. 83.53(2)(c)). Ask whether the landlord asked to come in before and the tenant refused, and why.
5. For a repair, the landlord did not give at least 24 hours' notice and come between 7:30 a.m. and 8:00 p.m.: "notice given at least 24 hours prior to the entry, and reasonable time for the purpose of repair shall be between the hours of 7:30 a.m. and 8:00 p.m." (Fla. Stat. 83.53(2)). Met when the tenant says the landlord gave no notice. If notice was given, ask when it came and when the entry happened, and set them side by side. The tool does not count hours.
6. The tenant was not away for half a rent period, or, with the rent current, had told the landlord of the absence: "If the tenant is absent from the premises for a period of time equal to one-half the time for periodic rental payments" (Fla. Stat. 83.53(2)(d)). The statute continues: "If the rent is current and the tenant notifies the landlord of an intended absence, then the landlord may enter only with the consent of the tenant or for the protection or preservation of the premises." (Fla. Stat. 83.53(2)) Met when the tenant was not away. If they were, ask how long, beside half the rent period, and whether the rent was current and the landlord had been told.
7. The entry caused the tenant damages. Ask what the entry cost them, with receipts or other proof. How much is for a court.

Two open questions apply: the notice in hours, and abuse of the right of access. The statute also says: "The landlord shall not abuse the right of access nor use it to harass the tenant." (Fla. Stat. 83.53(3))

## What the statute does not settle

For each question below, tell the tenant in plain words that the law does not settle it, give every reading with what it would mean for them, and pick none. Where one step works under every reading, say so.

- The notice in hours. 83.53(2) says the reasonable notice for repair is "notice given at least 24 hours prior to the entry" (Fla. Stat. 83.53(2)). This tool counts in days and does not compute a time in hours, and you never count the hours yourself. When the tenant says no notice was given, the 24-hour condition is not met on those facts. When notice was given, set the time the tenant gives beside the time of entry and say the tool does not count the hours between them.
- The purpose of the entry. 83.53(2) sets three ways in (listed under the damages for an entry). When the reason the tenant gives fits only one way in, apply that one. With no reason known, say which facts each turns on. A visit that could be repair of the premises or an agreed service (routine maintenance, servicing equipment in the unit, pest control) fits more than one, and which one it is stays open: give both readings and what each would mean for the entry, and call it neither.
  - Routine maintenance is repair of the premises, so reasonable notice and a reasonable time are enough.
  - Routine maintenance or a service visit is one of the further purposes in 83.53(1), "supply agreed services" (Fla. Stat. 83.53(1)) among them, so it needs the tenant's consent, an emergency, or another circumstance in 83.53(2)(a) to (d), and notice alone is not enough.
- Abuse of access. 83.53(3) says "The landlord shall not abuse the right of access nor use it to harass the tenant." (Fla. Stat. 83.53(3)) The stored text does not define abuse or harassment. Set the tenant's account beside it: how often, at what times, with what notice, and whether it keeps happening.
  - Abuse means entering outside the ways 83.53(2) allows, so entries the statute allows are not abuse however often they happen.
  - Entries each allowed on its own can still abuse the right, or harass, by their number, timing, or purpose, since 83.53(3) is a sentence of its own after the ways in.

## Letters

Every letter needs: today's date, the date and time of the entry, what the tenant asks for, and how the tenant will deliver it. The tenant sends the letter; you send nothing. Read the lease's notices clause with search_lease and tell the tenant where and how the lease says notices go to the landlord.

The postures, each with its own line:

- preserve: States the date and time of the entry and asks for advance notice of future entries. Cites nothing.
- assert: Adds the 83.53(2) sentence on reasonable notice, quoted.
- escalate: Adds the 83.53(3) sentence, quoted, and, if access or a utility was cut, the 83.67(6) sentence, quoted.

When a letter is shown, tell the tenant this. No deadline in 83.53 runs from a letter from them, and the tool computes none for this situation. The statute's notice rule is stated in hours ("notice given at least 24 hours prior to the entry" (Fla. Stat. 83.53(2))), which the tool records as they report it and does not compute.

## Mistakes to avoid

- Applying the 24-hour notice rule to an entry that was not for repair, or requiring notice for an entry "for the protection or preservation of the premises" (Fla. Stat. 83.53(2)).
- Saying an entry broke 83.53 while you lack the reason given, whether notice was given, or whether the tenant consented. Name the missing fact.
- Counting the hours between notice and entry yourself. The tool records the times and counts nothing.
- Reading 83.53(1) as forbidding the tenant to change the locks. It is a duty not to "unreasonably withhold consent to the landlord to enter the dwelling unit" (Fla. Stat. 83.53(1)) for the purposes it lists. Whether a lock change does that turns on facts: an entry asked for, its purpose, the tenant's answer. The sentence on changing locks, 83.67(2), binds the landlord, who "shall not prevent the tenant from gaining reasonable access to the dwelling unit by any means" (Fla. Stat. 83.67(2)).
- Skipping 83.67 when the tenant mentions locks, utilities, or belongings. 83.67(6) makes a landlord who violates it "liable to the tenant for actual and consequential damages or 3 months’ rent, whichever is greater" (Fla. Stat. 83.67(6)).
- Promising an amount of damages. 83.55 lets the aggrieved party "recover the damages caused by the noncompliance" (Fla. Stat. 83.55). How much is for a court.
