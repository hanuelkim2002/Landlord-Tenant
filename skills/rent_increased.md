---
name: rent_increased
description: "The landlord has raised the rent or says the rent will go up."
sections: ["83.46", "83.57", "83.64", "83.425", "83.42"]
clocks: []
counting:
  convention: "calendar days, trigger day not counted, no weekend or holiday adjustment"
  status: "ASSUMPTION. Florida's court rule for counting days has not been checked against statutory deadlines outside litigation. Show this line with every computed date."
  note: "This playbook has no clocks. The stored text of Chapter 83, part II has no section on notice of a rent increase."
provenance:
  statute_year: 2026
  verified_against: "statutes/83.46.txt, statutes/83.57.txt, statutes/83.64.txt, statutes/83.425.txt, statutes/83.42.txt"
  verified_by: null
  verified_on: null
  version: 1
  converted_from: "playbooks/rent_increased.yaml version 0.5"
---
## When to load this skill

Load this skill when the landlord has raised the rent or says the rent will go up. It rests on 83.64 (retaliatory conduct), 83.57 (ending a tenancy without a specific term), 83.46 (rent and duration), and 83.425 (preemption).

- The program computes no deadline for this situation: the stored text of Chapter 83, part II has no section on notice of a rent increase. Never state a notice period for rent increases.
- If the tenant wants to end a month-to-month tenancy rather than pay the new rent, lease_ending also covers it, with the steps and the date; load it too.
- The statute leaves some housing out of part II: "Residency or detention in a facility, whether public or private, when residence or detention is incidental to the provision of medical, geriatric, educational, counseling, religious, or similar services." (Fla. Stat. 83.42(1)). College housing may be an example. The tool records the facts and does not decide whether this applies; say what the words are and what you would need to know.
- The retaliation rules have an exclusion of their own: "In any event, this section does not apply if the landlord proves that the eviction is for good cause." (Fla. Stat. 83.64(3)).
- Do not apply a local rent rule from memory. 83.425 preempts local regulation, and the stored text holds none.

## What to find out

Read the lease first, then ask the tenant. Ask what they saw, did, or hold, one or two things at a time and only what your answer turns on. Never ask whether something meets a term of the statute or the lease; ask what happened, then apply the term yourself.

### In the lease (search_lease; try a second wording if the first finds nothing)

- The rent clause: the rent amount in the lease, next to the new rent.
- The renewal clause, and when the lease term began.
- When the lease term ends, next to the date the new rent applies from. Show both and say what the lease says; you do not compare the dates.

### From the tenant

- How much is the monthly rent? (Only if the lease does not show it.) What new rent is the landlord asking for?
- What date did they receive notice of the increase, was it in writing, and from what date does the landlord say the new rent applies?
- Does the lease have a fixed end date (for example, a one-year lease), and what date does the term end? Or is the tenancy month to month (no fixed end date, rent paid monthly)?
- Before the increase, had they complained to anyone about the unit (the landlord, the office, a city or county office), or taken part in a tenant group? If so, what was it, and on what date? Offer the plain choices: a complaint to a city or county office that enforces building, housing, or health codes; taking part in a tenant group; a written notice to the landlord about a repair; another complaint to the landlord (in person, by phone, a portal request); or something else. If more than one fits, take the first in that list.
- What do they know about whether other tenants got the same increase? It is fine if they do not know.
- Has the landlord filed an eviction case in court against them?

### What the deadlines count from

Nothing: the program computes no date for this situation. Do not compare the date of the increase with the lease term yourself, or without the lease's own words.

### Evidence to suggest the tenant keep

- The notice of the increase, with its date and how it arrived.
- The lease, especially the rent and renewal clauses.
- Any complaint made before the increase, with its date.
- Anything showing what other tenants were charged.

## What the tenant can do

Tell the tenant first whether they can do each of these and what it turns on, before any step. Each condition is settled by the lease (read that clause with search_lease and say what it says), by the tenant (ask), or not at all (the statute does not settle it: give every reading, see the open questions below). Some conditions are for the tenant to check against what the record shows.

### Raise retaliation as a defense if the landlord sues for possession after raising the rent (Fla. Stat. 83.64(2))

All six conditions must be met. No steps are listed. Whether retaliation can be acted on before any such case is open (the second open question).

1. Before the increase, the tenant did something the statute protects, such as a complaint to a code agency, a written notice to the landlord of a repair the landlord has not made, or joining a tenant organization: "Examples of conduct for which the landlord may not retaliate include, but are not limited to, situations where:" (Fla. Stat. 83.64(1)). It is met in any of these ways:
   - The tenant complained to a code enforcement office, or took part in a tenant group, as 83.64(1) names. The tenant can tell you. If their step was something else, it is not one of the examples the statute names outright.
   - The tenant gave the landlord a written notice about a repair, which 83.64(1) names when it is a complaint under 83.56(1). The tenant checks whether that notice was one 83.56(1) describes.
   - The statute's examples are not the only conduct it protects. That is not settled (the second open question).
2. The tenant acted in good faith: "In order for the tenant to raise the defense of retaliatory conduct, the tenant must have acted in good faith." (Fla. Stat. 83.64(1)). The tenant checks whether the complaint or other step was made in good faith, with what the record shows of it.
3. The tenant is treated differently from other tenants as to the rent: "a tenant is being treated differently as to the rent charged, the services rendered, or the action being taken by the landlord, which shall be a prerequisite to a finding of retaliatory conduct" (Fla. Stat. 83.64(4)). The tenant checks whether other tenants got the same increase, from what the landlord or other tenants say.
4. The increase was primarily because the landlord is retaliating: "primarily because the landlord is retaliating against the tenant" (Fla. Stat. 83.64(1)). The landlord's motive is not in the record. That is not settled (the second open question).
5. The landlord has no good cause for the case, such as unpaid rent or a lease violation, which the landlord must prove: "In any event, this section does not apply if the landlord proves that the eviction is for good cause." (Fla. Stat. 83.64(3)). The tenant checks whether any rent is unpaid or the landlord claims a lease violation.
6. The landlord has brought an action for possession: "Evidence of retaliatory conduct may be raised by the tenant as a defense in any action brought against him or her for possession." (Fla. Stat. 83.64(2)). The tenant can tell you. If they say no eviction case has been filed, the defense is raised in a case once one is filed; it is not open yet.

### End a month-to-month tenancy rather than pay the new rent, with written notice at least 30 days before the end of a monthly period (Fla. Stat. 83.57(3))

One condition: the tenancy is month to month. The statute: "When the tenancy is from month to month, by giving not less than 30 days’ notice prior to the end of any monthly period" (Fla. Stat. 83.57(3)). The tenant can tell you, and the lease's term clause shows it. If the tenant says it is not month to month, this option is closed. No steps are listed here, and the program computes no date. Whether an increase may be made, and on what notice, is open (the first open question).

## What the statute does not settle

For each of these, tell the tenant in plain words that the law does not settle it, give every reading and what it would mean for them, and pick none.

### Whether and how a rent increase may be made

The stored text of Chapter 83, part II has no section setting notice for a rent increase. 83.425 says "The regulation of residential tenancies, the landlord-tenant relationship, and all other matters covered under this part are preempted to the state." (Fla. Stat. 83.425). Set the lease's rent clause beside the increase and, for a tenancy without a fixed term, 83.57. Whether and how an increase may be made is not settled by the stored text; say so plainly with the readings.

- During a fixed term the rent is what the lease says, so an increase needs a lease clause allowing it or the tenant's agreement; part II adds nothing either way.
- For a month-to-month tenancy, a landlord who may end it on 83.57 notice may change the rent on the same notice, "not less than 30 days’ notice prior to the end of any monthly period" (Fla. Stat. 83.57(3)).
- For a month-to-month tenancy no particular notice is needed, since no section sets one.

### Retaliation, and what the tenant can do about an increase alone

83.64(1) says "It is unlawful for a landlord to discriminatorily increase a tenant’s rent or decrease services to a tenant, or to bring or threaten to bring an action for possession or other civil action, primarily because the landlord is retaliating against the tenant." (Fla. Stat. 83.64(1)). 83.64(4) defines "Discrimination" for that section. Set the record beside its parts: the complaint and its date, what the tenant knows about other tenants' rent, and the tenant's good faith. The landlord's motive is not in the record. What stays open is what the tenant can do about an increase alone.

- 83.64 works only as a defense: 83.64(2) says retaliation "may be raised by the tenant as a defense in any action brought against him or her for possession" (Fla. Stat. 83.64(2)), so a tenant facing only an increase has nothing to raise until such an action.
- 83.64(1) makes a discriminatory, retaliatory increase unlawful on its own terms, and 83.55 lets the tenant recover damages when the landlord fails to comply with part II. Fetch 83.55 with get_statute_section before relying on it.

## Letters

The tenant sends every letter; you send nothing. Every letter holds: today's date, the current rent, the new rent and the date it applies from, the tenant's request, and the delivery method. The postures, each line as written:

- preserve: Asks the landlord to confirm the new rent, the date it applies from, and which lease provision it rests on. Cites nothing.
- assert: Adds the lease's rent clause, quoted.
- escalate: Adds the 83.64(1) sentence, quoted.

When a letter is shown, tell the tenant that the program computes no deadline for this situation: the statute text it holds (Chapter 83, part II) has no section on notice of a rent increase. A letter from them does not start any period the program tracks.

The tenant delivers the letter. Read the lease's clause on where and how notices to the landlord must be sent (search_lease), and quote it when you ask how they will send it.

## Mistakes to avoid

- Stating a notice period for rent increases. The stored text has none.
- Saying an increase is retaliatory because it followed a complaint. 83.64(1) needs an increase that is discriminatory and "primarily because the landlord is retaliating against the tenant" (Fla. Stat. 83.64(1)), and 83.64(4) makes different treatment "a prerequisite to a finding of retaliatory conduct" (Fla. Stat. 83.64(4)).
- Applying 83.64 without its condition that "the tenant must have acted in good faith" (Fla. Stat. 83.64(1)).
- Applying a local rent rule from memory. 83.425 preempts local regulation, and the stored text holds none.
- Comparing the increase date with the lease term yourself, or without the lease's own words. The tool compares no dates.
- Computing any date yourself.
