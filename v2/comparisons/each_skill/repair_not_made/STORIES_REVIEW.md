# The repair stories: a review of the nine stories and their keys

## How to read this

This reviews the repair skill's nine test stories (`stories.json` in this folder) and their answer keys. The next
test run is graded against these keys, so they need your OK first. I changed nothing: not the stories, the skills,
or the leases.

Each story has seven parts:

1. What happened, with the dates from the facts.
2. The lease clauses that matter, word for word.
3. The tenant's message, as written.
4. The right answer, step by step, with the statute words that decide each step.
5. Each mistake that makes an answer wrong, and why.
6. How the chatbot did in the first test (stories 1 to 7; stories 8 and 9 have not run).
7. Questions for you, where the key looks wrong, too narrow, too strict, or not backed by the stored law or the
   lease. I did not change any key.

All the questions are gathered at the end, biggest first. Q22 to Q25 came from a second check of this review; each
sits in the story it touches most.

**Quotes.** A statute quote sits in double quote marks with its cite after it, like this: "the tenant may terminate
the rental agreement." (83.56(1)). Each is word for word in the cited part of `v2/statutes/`. I checked every one
with the app's own quote checker (the check `python law.py` runs on skills). A lease quote has its clause number
after it, like (clause 11), and is word for word from that story's lease file. Words quoted from a key, a fact, an
answer, or a grader say so: (key), (facts), (new answer), (v1 answer), (grader). A (key) or (facts) quote is the
keys as reviewed, before your answers at the end changed them. The stored sections are current:
their history notes run to ch. 2026-143 for 83.56 and to ch. 2025-16 for 83.51 and 83.505 (fetched 2026-09-11).

**Dates.** Every date here comes from the same math `count_days` does: a confirmed date plus some days, in calendar
days, the start day not counted, with no shift for weekends or holidays. So 7 days after 2026-03-09 is 2026-03-16
(day 1 is 2026-03-10). The code itself warns that this way of counting "has not been checked against the statute
yet" (tools.py). I worked out no date by hand; each one was run through the same date math in Python. The key
checker (`check_key.py`) also passes on all nine stories.

**Words used here.**

- *The statute*: Florida Statutes chapter 83, part II, the landlord-tenant law, as stored in `v2/statutes/`. A cite
  like 83.56(1)(a) means section 83.56, subsection (1), paragraph (a).
- *The key*: a story's right answer, the points a right answer must make, and the mistakes that make one wrong. A
  point written wholly in parentheses is helpful detail, not required.
- *An 83.51(1) duty*: the landlord's main repair duty. Follow the applicable building, housing, and health codes, or,
  where there are none, keep the structure and the plumbing in repair.
- *Material*: important enough to count. The statute uses the word and never defines it.
- *Defense*: a reason a person who is sued gives the court for why they should not lose.
- *Eviction*, or *action for possession*: the landlord's court case to get the home back.
- *Registry of the court*: an account the court clerk keeps. A tenant who is sued and raises a defense pays the rent
  into it while the case goes on.
- *Waive*: give up a right, on purpose or by acting a certain way.
- *Forfeit*: lose a right as a penalty.
- *Retaliation*: the landlord punishing a tenant for using a legal right.
- *Damages*: money a court orders to make up for a loss.
- *Not settled*, or *open*: the stored text can be read two ways. A right answer gives both and picks neither.
- *Code*: the statute defines building, housing, and health codes as "any law, ordinance, or governmental regulation
  concerning health, safety, sanitation or fitness for habitation, or the construction, maintenance, operation,
  occupancy, use, or appearance, of any dwelling unit." (83.43(3)). So a code may be state law or a local rule. Codes
  are not stored, so the tool cannot check them; the city or county code office can.

**The same home in every story.** Each lease is a copy of one base lease (`comparisons/skills/lease.txt`): Apartment
12 at Lakeview Terrace in Gainesville, rent \$1,050 a month, a \$1,050 deposit, written notices to the landlord by hand
or certified mail (clause 7), and no e-mail agreement (clause 8). Some stories add or change a clause.

**One step every story shares: does the law cover this home?** Part II leaves out some homes, among them "Residency or
detention in a facility, whether public or private, when residence or detention is incidental to the provision of
medical, geriatric, educational, counseling, religious, or similar services." (83.42(1)). College housing can fall
here. Every story but story 3 already holds the fact `school_housing: no`, so the answer should not ask again and
needs at most one line on it. Story 3 has no such fact; see its step 1.

## The nine stories at a glance

| # | Story, in one line | Lease | First test (right of 3) |
|---|---|---|---|
| 1 | Air conditioning out. Only the lease promises it, so holding back rent is not protected; a written 7-day notice can end the lease; 'material' is open. | lease_repairs.txt | new 3, v1 2 |
| 2 | No hot water; a mailed notice to end the lease. The 7 days ran from delivery to 2026-03-16; open: which list hot water is on, and whether paying March rent gave up the right. | lease.txt | new 3, v1 0 |
| 3 | Leaking roof; the tenant wants to skip May rent but sent nothing written. Not yet: the rent defense needs a written notice and 7 days, and holding back rent risks eviction. | lease.txt | new 0 (rerun 1), v1 1 |
| 4 | Closed pool and broken dishwasher, both lease promises. Holding back rent is not protected; ending the lease may reach them; whether the pool clause limits the promise is open. | lease_repairs.txt | new 3, v1 1 |
| 5 | A guest broke a window. The statute does not make the landlord responsible for damage a guest caused, and the lease puts it on the tenant. | lease_repairs.txt | new 3, v1 1 |
| 6 | Rent raised soon after a code complaint. It may be unlawful retaliation; a court decides; it works as a defense, with good-faith and good-cause limits. | lease_monthtomonth.txt | new 3, v1 0 |
| 7 | Lease ended over a repair; now the deposit. The deposit rules decide; when the lease ended is open, so the 30 days ran out 2026-05-15 or run to 2026-08-30. | lease.txt | old key: new 0, v1 0; fixed key: rerun 3 |
| 8 | New. Furnished: the bed frame the lease promises broke. Same shape as story 1, with an item the skill never names. | lease_furnished.txt | not run yet |
| 9 | New. The reserved covered parking the lease promises is closed. Same shape, plus rent paid while it was closed. | lease_parking.txt | not run yet |

---

## Story 1. The air conditioning is out, and the lease lists it

### 1. What happened

Today is 2026-06-15. The tenant rents an apartment in a larger building, a private complex not tied to any school.
The central air conditioning stopped on 2026-06-03, for no reason the tenant knows of. On 2026-06-04 the tenant sent
a request through the resident portal. The office replied that a part is on order, and nothing has happened since.
June rent was paid on 2026-06-01, before it broke. July rent is due 2026-07-01. No eviction case has been filed.

### 2. The lease clauses that matter (lease_repairs.txt)

- "Landlord provides the following with the apartment and will keep them in working order: refrigerator, stove,
  dishwasher, and central air conditioning." (clause 11)
- "Tenant shall report the need for repairs in writing through the resident portal." (clause 11)
- "Written notices to Landlord shall be delivered by hand to the office at 1840 SW 13th Street, Suite A, Gainesville,
  Florida 32608, or sent there by certified mail." (clause 7)
- "Landlord and Tenant have not agreed to deliver notices by e-mail." (clause 8)

### 3. The tenant's message

> My AC stopped working on June 3 and it's been almost two weeks. It's 90 degrees in my apartment. I put in a portal request on June 4 and the office said a part was on order, and nothing since. Can I stop paying rent until they fix it? Or can I just break my lease?

### 4. The right answer, step by step

**Step 1. Does the law cover the home?** Yes. The facts already say it is not school housing. At most one line, no
question.

**Step 2. Whose job is the air conditioning?** The landlord's main duty has two parts. The landlord must "Comply with
the requirements of applicable building, housing, and health codes" (83.51(1)(a)), or, "Where there are no
applicable building, housing, or health codes, maintain the roofs, windows, doors, floors, steps, porches, exterior
walls, foundations, and all other structural components in good repair and capable of resisting normal forces and
loads and the plumbing in reasonable working condition" (83.51(1)(b)). Air conditioning is not on that list. The
second list, for apartments, names heat but not cooling: "Functioning facilities for heat during winter, running
water, and hot water." (83.51(2)(a)), item 5 of that paragraph's list. So the statute does not name air conditioning. The lease does: the landlord
"will keep them in working order" (clause 11), and the list ends with "central air conditioning" (clause 11). So the
repair is the landlord's job under the lease. A code (state or local; Q22) might also require air conditioning, which would make it
an 83.51(1)(a) duty, but the codes are not stored, so the answer points the tenant to the city or county code office.

**Step 3. Can the tenant stop paying rent? Not with protection.** The statute's defense for unpaid rent reaches only
an 83.51(1) duty: "The defense of a material noncompliance with s. 83.51 (1) may be raised by the tenant if 7 days
have elapsed after the delivery of written notice by the tenant to the landlord, specifying the noncompliance and
indicating the intention of the tenant not to pay rent by reason thereof." (83.60(1)(b)). A promise only the lease
makes is not an 83.51(1) duty. So this defense does not cover holding back rent over the air conditioning, unless a
code requires it. Holding back rent invites an eviction case. If the landlord sues and the tenant raises any defense
other than payment, "the tenant shall pay into the registry of the court the accrued rent as alleged in the
complaint or as determined by the court and the rent that accrues during the pendency of the proceeding, when due."
(83.60(2)). The key wants this said plainly. (Q1 asks how flatly.)

**Step 4. Can the tenant end the lease? Yes, after a proper notice.** The rule: "If the landlord materially fails to
comply with s. 83.51 (1) or material provisions of the rental agreement within 7 days after delivery of written
notice by the tenant specifying the noncompliance and indicating the intention of the tenant to terminate the rental
agreement by reason thereof, the tenant may terminate the rental agreement." (83.56(1)). Unlike the rent defense,
this rule also reaches "material provisions of the rental agreement" (83.56(1)), so it can reach clause 11. It has
four parts:

- A material failure of a lease promise. Whether it is material is open (step 5).
- A written notice that names the problem and says the tenant will end the lease over it.
- Delivery a way the statute names: "The delivery of the written notices required by subsections (1)-(3) shall be by
  mailing, delivering a true copy thereof, e-mailing in accordance with s. 83.505" (83.56(4)). Clause 7 asks for hand
  delivery to the office or certified mail. Doing what clause 7 says also meets the statute, so that is the safe
  advice. The lease cannot swap in other ways: "The notice requirements of subsections (1)-(3) may not be waived in
  the rental agreement." (83.56(4)).
- Seven days pass after delivery without the repair.

The portal request is not that notice. It is written, and clause 11 even asks for repair reports through the portal.
But a portal message is not one of the ways 83.56(4) names, there is no e-mail agreement (clause 8), and, as far as
the facts show, it asked for a repair without saying the tenant would end the lease. (Q2: the facts do not say what
it said.) So the tenant needs a new notice.

**Step 5. Is a broken air conditioner material? Not settled.** The statute does not define the word. One reading: any
failure of a lease promise is material. The other: it turns on how serious the problem is, how long it lasts, and how
it affects living there. The answer can set the tenant's facts (90 degrees inside, almost two weeks, in the tenant's
words) beside the word, but must not decide.

**Step 6. The part on order (helpful detail).** The statute has a rule for failures the landlord cannot help: "If the
failure to comply with s. 83.51 (1) or material provisions of the rental agreement is due to causes beyond the
control of the landlord and the landlord has made and continues to make every reasonable effort to correct the
failure to comply, the rental agreement may be terminated or altered by the parties, as follows:" (83.56(1)). Then
two cases. "If the landlord's failure to comply renders the dwelling unit untenantable and the tenant vacates, the
tenant shall not be liable for rent during the period the dwelling unit remains uninhabitable." (83.56(1)(a)). And
"If the landlord's failure to comply does not render the dwelling unit untenantable and the tenant remains in
occupancy, the rent for the period of noncompliance shall be reduced by an amount in proportion to the loss of rental
value caused by the noncompliance." (83.56(1)(b)). A part on order may be a cause beyond the landlord's control. But
the facts show one reply and nothing since, so whether the landlord "continues to make every reasonable effort"
(83.56(1)) is a question of fact. 'Untenantable' (not fit to live in) is not defined. And "terminated or altered by
the parties" (83.56(1)) is itself open: one reading says both sides must agree; the other says (a) and (b) apply once
their facts are met. The key names this rule only in parentheses. (Q3.)

**Step 7. Damages (helpful detail).** "If either the landlord or the tenant fails to comply with the requirements of
the rental agreement or this part, the aggrieved party may recover the damages caused by the noncompliance." (83.55).
This reaches a lease promise. How much, and how to bring the claim in court, is outside the tool.

**Step 8. Rent paid.** June rent was paid before the air conditioning broke, so paying rent has given nothing up. If
the tenant pays July rent while it is still broken, the question in story 2, step 5 would come up. The key does not
ask for this, and it does not need to.

**The points a right answer must make**

1. Required. Air conditioning is not in 83.51; it is the landlord's job here because clause 11 promises it. (A code
   might also require it; the code office can say.)
2. Required. Holding back rent is not protected by the lease promise alone, since the 83.60(1)(b) defense reaches
   only an 83.51(1) duty, and it risks an eviction case. Said plainly.
3. Required. To end the lease: a new written notice, by hand or mail (the lease names hand delivery or certified
   mail), naming the problem and saying the tenant will end the lease; the portal request is not it; 7 days after
   delivery; whether the failure is material is open.
4. Helpful detail. The part-on-order rule; damages.

**Open points:** material (step 5); the part-on-order rule's facts and how to read "terminated or altered by the parties" (83.56(1)) (step 6).

**Dates:** none. No notice has been delivered, so `count_days` has nothing to count from. A right answer gives no
date for the 7 days.

### 5. Mistakes that make an answer wrong

1. "Says 83.51 requires the landlord to provide or repair air conditioning." (key). Wrong because neither of 83.51's
   lists names it (step 2). Only the lease, or a code the tool cannot see, makes it the landlord's.
2. "Says the tenant may hold back rent over the air conditioning as a defense under 83.60(1)(b), or explains holding
   back rent without its risk." (key). Wrong because 83.60(1)(b) speaks only of "a material noncompliance with s.
   83.51 (1)" (83.60(1)(b)), and a tenant who holds back rent can be sued (step 3).
3. "Treats the portal request as the written notice that lets the tenant end the lease." (key). Wrong because a
   portal message is not a way of delivery 83.56(4) names, and it did not say the tenant would end the lease (step 4).
4. "Says flatly that the broken air conditioning is, or is not, material." (key). Wrong because the statute does not
   define the word.
5. "Gives a date it worked out itself instead of from count_days." (key). Wrong because the model never works out a
   date (`v2/CLAUDE.md`).

### 6. The first test

- New skill: right in 3 of 3. All three said the lease, not the statute, promises the air conditioning, that holding
  back rent is not protected, that the portal request is not the notice, and that 'material' is open. One left out
  damages, which is helpful detail only.
- v1: right in 2 of 3. All three left out damages. Run 2 was marked wrong for a rule of its own: the grader found
  "Sending your notice before July 1 would avoid the question" (v1 answer) unsupported, since paying July rent with
  knowledge is what raises the waiver question, whatever the notice date.

### 7. Questions for you

**Q1 (stories 1, 4, 8, 9). Is 'no defense' too flat?** The keys say holding back rent over a lease-only promise
"would not protect you" (key) or leaves "no defense behind it" (key). The stored text is narrower. 83.60(1)(b)'s
defense reaches only 83.51(1). But 83.60(1)(a) adds that the tenant "may raise any other defense, whether legal or
equitable, that he or she may have" (83.60(1)(a)). Whether a broken lease promise could be some other defense, the
stored text does not say. Should the keys say *the statute's rent defense does not reach it, and whether any other
defense would is outside what this tool can settle*, instead of saying no defense exists? The practical advice stays
the same: any defense other than payment needs the rent paid into the court registry (83.60(2)), so holding back rent
is risky either way.

**Q2 (stories 1, 4, 8). What did the portal requests say?** The facts do not say. The key's "is not that notice" (key) rests
on two reasons, the way it was sent and its words, and the facts give only the first. And in lease_repairs.txt,
clause 11 itself tells the tenant to report repairs "in writing through the resident portal" (clause 11), so a model
may take the portal request as the lease's own written notice. Should each story's facts add one line, such as *the
request asked for a repair and did not say the tenant would end the lease*?

**Q3 (story 1). Should the part-on-order detail say what the rule does?** The key names the rule but not its effect:
if its facts are met and the tenant stays, the rent "shall be reduced by an amount in proportion to the loss of
rental value" (83.56(1)(b)). The tenant asked about rent, so this matters to them. Should the helpful detail say so,
with "terminated or altered by the parties" (83.56(1)) left open? And should the key say that an answer which raises this rent cut, with its
conditions, is not making mistake 2? I think it is not, but the graders should be told.

**Q22 (stories 1, 2, 3, 6, and the skill). Codes and state preemption.** The keys say "a local code" (key) may
require air conditioning or hot water. Two stored sections bear on that. The definition of codes reaches "any law,
ordinance, or governmental regulation" (83.43(3)), so a code may be state law, not only local. And part II says "The
regulation of residential tenancies, the landlord-tenant relationship, and all other matters covered under this part
are preempted to the state." (83.425). Preempted means only the state may make rules on it. How far that reaches a
local housing code, the stored text does not settle. Two readings:

- Narrow: part II itself makes codes part of the landlord's duty: "Comply with the requirements of applicable
  building, housing, and health codes" (83.51(1)(a)), a term whose definition names an "ordinance" (83.43(3)).
  Following a local housing code is then applying part II, not a competing local rule, so the code survives.
- Broad: 83.425 supersedes local rules "on matters covered under this part" (83.425), and repairs are one (83.51).
  Its list names "the rights and responsibilities of the landlord and tenant" (83.425), which is what a local repair
  code sets. So a local code may not add to the repair duty.

State codes are untouched by either reading. My view: keep the tenant's line simple (*a code, state or local, may
cover it; the code office can say*) and put both readings in the key, not in the answer. Should the keys say *a code
(state or local)* in place of *a local code* and list the two readings, and should the skill mention 83.425?

**Q24 (stories 1, 3, 4, 6, 7, 8, 9). Attorney fees.** "In any civil action brought to enforce the provisions of the
rental agreement or this part, the party in whose favor a judgment or decree has been rendered may recover reasonable
attorney fees and court costs from the nonprevailing party." (83.48). This cuts both ways: a tenant who sues and wins
may recover fees, and one who loses may owe the landlord's. The deposit rules have their own version: "the
prevailing party is entitled to receive his or her court costs plus a reasonable fee for his or her attorney"
(83.49(3)(c)). Three more details from the same text:

- The general rule says the winner "may recover" (83.48) fees; the deposit rule says the winner "is entitled to
  receive" (83.49(3)(c)) them. So the deposit rule in story 7 is the firmer one.
- A lease cannot take the right away: "The right to attorney fees in this section may not be waived in a lease
  agreement." (83.48).
- One exception: fees "may not be awarded under this section in a claim for personal injury damages based on a breach
  of duty under s. 83.51" (83.48). No story here has an injury, but a repair story where someone gets hurt would.

Neither the keys nor the skill mention fees. Add one line of helpful detail wherever a key names damages or a suit? If
so, the skill needs the same line first, or the key asks for more than the skill teaches.

---

## Story 2. No hot water; a notice to end the lease, delivered after it was mailed

### 1. What happened

Today is 2026-03-20. Private apartment. There has been no hot water since 2026-02-25, when the water heater stopped.
The tenant did nothing to cause it. The tenant paid March rent on 2026-03-01, while the hot water was out. On
2026-03-06 the tenant sent a letter by certified mail. It says the water heater is broken and the tenant will end the
lease if it is not fixed within 7 days. The office signed for it on 2026-03-09. The landlord has not replied, and
there is still no hot water. No eviction case.

### 2. The lease clauses that matter (lease.txt, the base lease)

The lease says nothing on repairs or hot water. The clauses that matter:

- "Written notices to Landlord shall be delivered by hand to the office at 1840 SW 13th Street, Suite A, Gainesville,
  Florida 32608, or sent there by certified mail." (clause 7)
- "This lease is the whole agreement. It may be changed only in writing signed by Landlord and Tenant." (clause 10).
  So, as far as the lease shows, no other writing changes the repair duties.

### 3. The tenant's message

> We've had no hot water since February 25. On March 6 I mailed a certified letter saying I'll end my lease if they don't fix it in 7 days, and the office signed for it March 9. It's been two weeks since I mailed it and still nothing. Can I move out now and stop paying rent?

### 4. The right answer, step by step

**Step 1. Coverage.** Yes; not school housing.

**Step 2. Is the letter the right kind of notice? Yes.** 83.56(1) asks for a "written notice by the tenant specifying
the noncompliance and indicating the intention of the tenant to terminate the rental agreement by reason thereof"
(83.56(1)). The letter is written, names the broken water heater, and says the tenant will end the lease. It went by
mail, a way the statute names: delivery "shall be by mailing" (83.56(4)). It went certified, as clause 7 asks.

**Step 3. When the 7 days end.** The rule counts "within 7 days after delivery of written notice" (83.56(1)). The
letter was delivered when the office signed for it, 2026-03-09. `count_days(repair_notice_delivered, 7)` gives
2026-03-16. Today is 2026-03-20, so that day has passed. Counting from the mailing date, 2026-03-06, would give
2026-03-13; the key calls that a mistake. (Q4: the stored text does not say when a mailed notice counts as
delivered.)

**Step 4. Does the rule to end the lease reach hot water at all? Not settled.** The rule reaches "s. 83.51 (1) or
material provisions of the rental agreement" (83.56(1)). This lease has no repair clause, so the question is whether
hot water is an 83.51(1) duty. The statute speaks to it in four places:

- 83.51(1)(b) asks the landlord to keep "the plumbing in reasonable working condition" (83.51(1)(b)).
- 83.51(2)(a), for apartments, asks for "Functioning facilities for heat during winter, running water, and hot
  water." (83.51(2)(a)), item 5.
- A tie-break: "If the duty imposed by subsection (1) is the same or greater than any duty imposed by subsection (2),
  the landlord's duty is determined by subsection (1)." (83.51(3)).
- Subsection (2) items are kept out of the eviction defense: "Nothing in this part authorizes the tenant to raise a
  noncompliance by the landlord with this subsection as a defense to an action for possession under s. 83.59"
  (83.51(2)(c)).

Reading one: a dead water heater is a plumbing failure, so it is an 83.51(1) duty, and 83.51(3) points to subsection
(1). Then the tenant may end the lease now (if the failure is material). Reading two: hot water is named in (2)(a), so
it is a subsection (2) duty, which 83.56(1) does not reach. Then the statute gives no right to end the lease over it,
unless a code (state or local; Q22) requires hot water (an 83.51(1)(a) duty, outside the tool) or the lease promises it (this one does
not). The answer gives both and leans neither way.

**Step 5. Did paying March rent give up the right? Not settled.** The waiver rule: "if the tenant pays rent with
actual knowledge of a noncompliance by the landlord or accepts performance by the landlord of any other provision of
the rental agreement that is at variance with its provisions, the landlord or tenant waives his or her right to
terminate the rental agreement or to bring a civil action for that noncompliance, but not for any subsequent or
continuing noncompliance." (83.56(5)(a)). The tenant paid March rent on 2026-03-01, knowing the hot water was out.
Reading one: a water heater still broken is a "continuing noncompliance" (83.56(5)(a)), so nothing was given up.
Reading two: paying rent with knowledge gave up ending the lease over this failure. Both readings, no lean.

**Step 6. Material.** Not settled, as in story 1.

**Step 7. Stopping rent is a different path (helpful detail).** Holding back rent while staying needs its own notice,
one "indicating the intention of the tenant not to pay rent by reason thereof" (83.60(1)(b)). The letter said the
tenant would end the lease, not that they would stop paying rent. So it does not set up that defense. Under reading
two of step 4, 83.51(2)(c) would also keep hot water out of a defense to eviction. (Q5: the tenant may only mean that
rent stops once they have ended the lease and moved out.)

**The points a right answer must make**

1. Required. The letter is the right kind of notice, and its 7 days, counted from delivery, ended on 2026-03-16
   (count_days), which has passed.
2. Required. Whether hot water is an 83.51(1) duty or only an 83.51(2)(a) item is open; both readings, no lean.
3. Required. Paying March rent: a continuing failure, or a waiver; both readings.
4. Helpful detail. Stopping rent needs its own written notice; material is open.

**Open points:** which list hot water is on (step 4); March rent (step 5); material (step 6).

**Dates:** 2026-03-16, from `count_days(repair_notice_delivered, 7)`, passed. The wrong date the key warns about,
2026-03-13, is the mailing date plus 7.

### 5. Mistakes that make an answer wrong

1. "Counts the 7 days from the day the letter was mailed (giving 2026-03-13) instead of the day it was delivered."
   (key). Wrong under the key because the rule counts from "delivery of written notice" (83.56(1)), and the skill treats the day the letter reached
   the office as delivery. (Q4.)
2. "Says flatly that the tenant may end the lease now, without the hot-water reading or the rent-paid question, or
   says flatly that they may not." (key). Wrong because two open points decide it.
3. "Treats the letter as a notice to hold back rent, or says the tenant may stop paying rent because of it." (key).
   Wrong because the letter does not say the tenant will not pay rent (step 7). (Q5.)
4. "Gives a date it worked out itself instead of from count_days." (key).

### 6. The first test

- New skill: right in 3 of 3. Each counted the 7 days from delivery to 2026-03-16 and gave both readings on hot water
  and on March rent.
- v1: right in 0 of 3 (2 partly, 1 wrong). All three led with "You probably can" (v1 answer), leaning toward reading
  one. Run 3 also said the lease cannot change the landlord's duties for this kind of home; the grader noted that
  83.51(2)(a) applies "Unless otherwise agreed in writing" (83.51(2)(a)).

### 7. Questions for you

**Q4. When does a mailed notice count as delivered?** 83.56(1) counts "within 7 days after delivery of written notice" (83.56(1)), and 83.56(4) says delivery
"shall be by mailing" (83.56(4)). The stored text never says whether a mailed notice is delivered on the day it is
mailed or the day it arrives. It does say so for e-mail: "A notice sent electronically pursuant to this section is
deemed delivered at the time it is sent, unless the e-mail is returned to the sender as undeliverable." (83.505(4)).
Counting from arrival is the skill's rule, and it is the careful choice for a tenant. But the key makes counting from
the mailing date a mistake, and here both dates have passed, so the outcome is the same. Keep it a mistake (it tests
the skill's rule)? Or accept either date, if it comes from count_days and the answer says which day it counted from?
Or mark it open?

**Q5. Does mistake 3 catch a right answer?** 'Can I move out now and stop paying rent?' most likely means: once I end
the lease and leave, do I still owe rent? Under reading one of step 4, a valid ending would end the rent the lease
calls for after that. Mistake 3 counts as wrong an answer that "says the tenant may stop paying rent because of it"
(key). A careful answer saying *if you can end the lease, the rent stops once it ends* could be caught by those words.
Narrow mistake 3 to holding back rent while staying?

**Q6 (stories 2, 3, 5, 7). The (1)(b) list is the fallback where there are no codes.** The keys treat the roof, the
window, and the plumbing as 83.51(1) duties through 83.51(1)(b)'s list. That list applies only "Where there are no
applicable building, housing, or health codes" (83.51(1)(b)); where a code applies, 83.51(1)(a) sets the duty. No
first-test grade turned on this. But a careful answer may say *if a code applies, the code decides; the code
office can say*. Should the keys say *an 83.51(1) duty (on the (1)(b) list, or under a code by (1)(a))*, so a grader
does not mark that answer down?

---

## Story 3. A leaking roof; the tenant wants to stop paying rent but has sent nothing

### 1. What happened

Today is 2026-04-10. Apartment in a larger building. Since 2026-03-28 the roof has leaked into the bedroom whenever it
rains. Rain caused it, not the tenant. The tenant phoned the manager on 2026-03-29 and again on 2026-04-03, and sent
nothing in writing. Nobody has come. April rent was paid on 2026-04-01. May rent is due May 1. No eviction case. This
is the one story whose facts do not say whether the home is school housing.

### 2. The lease clauses that matter (lease.txt, the base lease)

The lease says nothing on repairs or the roof. The clauses that matter:

- The landlord is "Marsh Creek Property Management, LLC, as agent for the owner of Lakeview Terrace Apartments"
  (clause 1). This is for the school-housing step.
- "This lease begins on August 1, 2025 and ends on July 31, 2026." (clause 3)
- Clause 7, how to deliver a written notice (hand or certified mail).

### 3. The tenant's message

> My bedroom ceiling leaks every time it rains, since March 28. I've called the manager twice and nobody has come. My May rent is due May 1. Can I just not pay it until they fix the roof?

### 4. The right answer, step by step

**Step 1. Coverage, from the lease.** No fact settles school housing, so the answer reads the lease. The landlord is a
property management company. Nothing mentions a school, enrollment, students, or a school term; the term is one
year. So the lease is clear. The shared skill (`who_the_law_covers`) says to give this at most one line inside
another point, cite the lease, and ask nothing.

**Step 2. Whose job is the roof?** The landlord's. The roof is on 83.51(1)(b)'s list: "maintain the roofs, windows,
doors, floors, steps, porches, exterior walls, foundations, and all other structural components in good repair"
(83.51(1)(b)). So it is an 83.51(1) duty. (Q6 on codes.)

**Step 3. Can the tenant skip May rent? Not yet.** Because the roof is an 83.51(1) duty, the rent defense can apply,
but only after its steps: "The defense of a material noncompliance with s. 83.51 (1) may be raised by the tenant if 7
days have elapsed after the delivery of written notice by the tenant to the landlord, specifying the noncompliance
and indicating the intention of the tenant not to pay rent by reason thereof." (83.60(1)(b)). The notice may go to
the landlord, its named representative, "a resident manager, or the person or entity who collects the rent on behalf
of the landlord" (83.60(1)(b)). The calls went to the manager, but they were not written and did not say the tenant
would not pay rent. So nothing yet lets the tenant hold back May rent. If the tenant delivers such a notice,
`count_days` on its delivery date gives the day the 7 days end. With no delivery date yet, the answer gives no date.

**Step 4. The risk.** Holding back rent can lead to an eviction case. If sued, "the tenant shall pay into the
registry of the court the accrued rent as alleged in the complaint or as determined by the court and the rent that
accrues during the pendency of the proceeding, when due." (83.60(2)). Missing the deadline costs every defense but
one: "Failure of the tenant to pay the rent into the registry of the court or to file a motion to determine the
amount of rent to be paid into the registry within 5 days, excluding Saturdays, Sundays, and legal holidays, after
the date of service of process constitutes an absolute waiver of the tenant's defenses other than payment" (83.60(2)).
"The clerk shall notify the tenant of such requirement in the summons." (83.60(2)). The tool does not count those 5
days, so the answer gives no date for them. If the defense succeeds, the court sets any rent cut: "the court or the
jury, as the case may be, shall determine the amount, if any, by which the rent is to be reduced to reflect the
diminution in value of the dwelling unit during the period of noncompliance with s. 83.51 (1)" (83.60(1)(b)).

**Step 5. Other paths (helpful detail).**

- End the lease: a written 7-day notice under 83.56(1), as in story 2.
- A code complaint: the city or county code office can inspect. The law protects the tenant from retaliation for it.
  One example it lists: "The tenant has complained to a governmental agency charged with responsibility for
  enforcement of a building, housing, or health code of a suspected violation applicable to the premises"
  (83.64(1)(a)).
- Damages under 83.55.

**Step 6. Material.** Not settled.

**Step 7. April rent (not in the key).** The tenant paid April rent on 2026-04-01, after the leak began on
2026-03-28. That raises the 83.56(5)(a) question for ending the lease or suing (story 2, step 5). It does not touch
the rent defense, since 83.56(5)(a) speaks only of the right "to terminate the rental agreement or to bring a civil
action" (83.56(5)(a)). (Q7.)

**The points a right answer must make**

1. Required. The roof is an 83.51(1) duty, so the 83.60(1)(b) defense can apply, but only after a written notice
   naming the leak and saying the tenant will not pay rent, and 7 days after delivery. The calls are not that notice,
   so nothing yet lets the tenant hold back May rent.
2. Required. Holding back rent risks an eviction case; if sued, the tenant must pay the rent into the registry within
   5 days of service, not counting weekends and legal holidays, or lose every defense but payment; no date for the 5
   days.
3. Helpful detail. Other paths (end the lease, a code complaint with retaliation protection, damages); material is
   open; at most one line on school housing, no question.

**Dates:** none. No date for the 7 days (no notice yet) or for the 5 days (the tool does not count them).

### 5. Mistakes that make an answer wrong

1. "Says the tenant may stop paying rent now, or treats the phone calls as the written notice." (key). Wrong because
   there is no written notice and no 7 days (step 3).
2. "Explains holding back rent without the eviction risk or the registry requirement of 83.60(2), or gives a date for
   the 5 days." (key). Wrong because the risk is what the tenant most needs to know, and the tool does not count court
   days.
3. "Asks the tenant whether the home is college housing, though the lease shows nothing tying it to a school." (key).
   Wrong because the shared skill asks only when the lease leaves doubt.
4. "Gives a date it worked out itself instead of from count_days." (key).

### 6. The first test

- New skill, first round: right in 0 of 3. Each worked out a time span itself. Two said the leak had lasted "about a
  month" (new answer), though it began on 2026-03-28 and today is 2026-04-10. The third said "the 7 days would
  probably not be over by May 1" (new answer), which the grader found wrong. The graders also counted two answers as
  asking the college question, for lines like "I've noted that as a pending fact for you to confirm" (new answer);
  the README reads that as the page's usual confirming, not a question.
- Rerun, after the shared skill was changed to one line: right in 1 of 3. The other two said "about a month" (new answer) again;
  this grader did not count it, and `review.json` counted it, for one standard with the first round.
- v1: right in 1 of 3. Two runs stated the time span themselves: "has lasted about a month" (v1 answer) and "unfixed for over a month" (v1 answer). Two never offered
  the 7-day notice to end the lease. None mentioned retaliation protection or damages (helpful detail).

### 7. Questions for you

**Q7. Add the April-rent question?** The tenant paid April rent after the leak began. Stories 2, 4, and 9 raise
83.56(5)(a) when rent was paid with knowledge, and the skill counts leaving it out as a mistake. Story 3's key is
silent. Add it as helpful detail, tied to the other paths (ending the lease, damages)?

**Q8. Name the motion too?** The key's answer says the tenant "must pay the rent into the court registry within 5
days" (key). 83.60(2) gives a second way to keep the defenses: "or to file a motion to determine the amount of rent to
be paid into the registry" (83.60(2)). The skill says so. Mention the motion, at least as helpful detail?

**Q9 (every story). Name time spans as a mistake?** No key lists a time span the model works out itself, such as "about a month" (new answer),
as a mistake, though the skill forbids "counting the days between two dates" (repair_not_made.md). The first
round's graders counted it as an error; the rerun's grader did not, and `review.json` overrode it. Add one line to
every key's mistakes, such as *Says how long something has lasted, or how long until a date, from its own counting*?
Also, stories 4, 5, 6, 8, and 9 lack the usual "Gives a date it worked out itself instead of from count_days." (key)
line (story 6 has its own line on counting days). Add it to them too, so every grader applies one standard?

**Q25. Casualty damage?** 83.63 covers a home "damaged or destroyed other than by the wrongful or negligent acts of
the tenant so that the enjoyment of the premises is substantially impaired" (83.63). Then "The tenant may terminate
the rental agreement and immediately vacate the premises." (83.63(1)). Or the tenant "may vacate the part of the
premises rendered unusable by the casualty" (83.63(1)), and then rent is "reduced by the fair rental value of that
part of the premises damaged or destroyed" (83.63(1)). The stored text never defines 'casualty' and never says the
damage must be sudden. (I first wrote that the title suggests a sudden event. That was my reading of the word, not
anything the text says, so I have dropped it.) So whether a roof that leaks every time it rains counts is open. If it
does, the fit has limits: the rent cut needs the tenant to move out of the unusable part, a bedroom that leaks only
when it rains may or may not be "rendered unusable" (83.63(1)), and the enjoyment must be "substantially impaired"
(83.63). A fix suggested in a second check, which I agree with: keep 83.63 out of the required points; record in the
key that whether a recurring leak counts is open; and say that an answer which raises it, with its conditions, is
not making mistake 1 (stopping rent now). One more grading risk: 83.63 names no notice before the tenant ends the
lease and leaves, while 83.56(1) needs a written notice and 7 days. So the key should also say that an answer using
83.63's route is not wrong for skipping the 83.56(1) notice, as long as it marks the fit as open and says that leaving
on an open reading is a risk. Add 83.63 to the section list if you take this up (Q14).

---

## Story 4. A closed pool and a broken dishwasher the lease promises

### 1. What happened

Today is 2026-05-12. Private apartment. The community pool has been closed since 2026-04-15, with a sign saying
'closed until further notice'. The dishwasher has not worked since 2026-04-20. The tenant caused neither. The tenant
sent portal requests on 2026-04-21 and 2026-05-01 and got no reply. May rent was paid on 2026-05-01. No eviction case.

### 2. The lease clauses that matter (lease_repairs.txt)

- "Landlord provides the following with the apartment and will keep them in working order: refrigerator, stove,
  dishwasher, and central air conditioning." (clause 11)
- "Residents may use the community pool from 8 a.m. to 10 p.m.; Landlord may close the pool for cleaning, repairs, or
  weather." (clause 11)
- "Tenant shall report the need for repairs in writing through the resident portal." (clause 11)
- Clause 7 (hand or certified mail) and clause 8 (no e-mail agreement), as in story 1.

### 3. The tenant's message

> The pool's been closed for almost a month and my dishwasher has been broken for three weeks. I pay for a place with a pool and a dishwasher! Can I hold back part of my rent until they fix them?

### 4. The right answer, step by step

**Step 1. Coverage.** Yes; not school housing.

**Step 2. Whose job?** Neither of 83.51's lists names a dishwasher or a pool (but see Q11 on common areas). Both come
from the lease. The dishwasher is among the things the landlord "will keep them in working order" (clause 11). The
pool is a use the lease grants, with a limit: "Landlord may close the pool for cleaning, repairs, or weather." (clause
11).

**Step 3. Hold back part of the rent? No.** The rent defense reaches only "a material noncompliance with s. 83.51 (1)"
(83.60(1)(b)). These are lease promises, so holding back rent, in part or in full, has no statute defense behind it
and risks an eviction case. (Q1.)

**Step 4. Ending the lease can reach them.** 83.56(1) reaches "material provisions of the rental agreement"
(83.56(1)). The four parts are the same as in story 1, step 4. One notice can name both problems. The portal requests
are not that notice (story 1, step 4; Q2).

**Step 5. Material.** Not settled, for each item on its own.

**Step 6. Does the pool clause limit the promise? Not settled.** First, a fact: the clause lets the landlord close the
pool "for cleaning, repairs, or weather" (clause 11), and the sign gives no reason (Q10). If the closure is for one of
those reasons, the question is whether the clause stands. The rule on void clauses: "A provision in a rental
agreement is void and unenforceable to the extent that it:" (83.47(1)) "Purports to waive or preclude the rights,
remedies, or requirements set forth in this part." (83.47(1)(a)) or "Purports to limit or preclude any liability of
the landlord to the tenant or of the tenant to the landlord, arising under law." (83.47(1)(b)). Reading one: the
clause only says what the lease promises, a pool that may close for those reasons, so it stands, and such a closure
breaks no promise. Reading two: to the extent it takes away a right part II gives (ending the lease, damages), it is
void. A third point is open too: whether a closure of almost a month, 'until further notice', is still one "for
cleaning, repairs, or weather" (clause 11).

**Step 7. Damages (helpful detail).** 83.55 reaches the lease failure.

**Step 8. May rent (helpful detail).** The tenant paid May rent on 2026-05-01 knowing of both problems. That raises
the 83.56(5)(a) question: a continuing failure, or a waiver (story 2, step 5).

**The points a right answer must make**

1. Required. No: the 83.60(1)(b) defense reaches only 83.51(1); the dishwasher and the pool are lease promises, so
   holding back rent does not protect the tenant and risks an eviction case.
2. Required. The lease promises both (the dishwasher kept in working order; the pool, which may close for cleaning,
   repairs, or weather). Ending the lease can reach a material lease provision after a written 7-day notice by hand
   or mail; the portal requests are not that notice; material is open.
3. Helpful detail. Damages; whether the pool clause limits the promise (83.47) is open; May rent and 83.56(5)(a).

**Dates:** none.

### 5. Mistakes that make an answer wrong

1. "Says the tenant may hold back part or all of the rent over the pool or the dishwasher." (key). Wrong for the
   reason in step 3.
2. "Says 83.51 requires the landlord to provide or keep up a pool or a dishwasher." (key). Wrong because neither list
   names them. (Q11.)
3. "Treats the portal requests as the written notice to end the lease." (key). Wrong for the reasons in story 1, step
   4.
4. "Says flatly that the closed pool or the broken dishwasher is, or is not, material." (key).

### 6. The first test

- New skill: right in 3 of 3. Each covered damages, the pool clause question, and May rent.
- v1: right in 1 of 3. All three left out damages (helpful detail). Run 1 was marked wrong for saying the rent defense
  "only helps if your landlord sues to evict you" (v1 answer); 83.60(1)(a) also lets it be raised in a landlord's
  suit for unpaid rent. Run 2 was marked wrong for hinting that a proper notice could make holding back rent work for
  these lease-only items.

### 7. Questions for you

Q1 and Q2 apply here too.

**Q10. Why is the pool closed?** The clause allows closing only "for cleaning, repairs, or weather" (clause 11). The
sign says only 'closed until further notice', and the facts give no reason. The 83.47 question comes up only if the
closure is for one of those reasons. Should the facts give the reason (for example, a pump repair), or should the key
expect the answer to say the reason matters, and ask it?

**Q11 (stories 4 and 9). Common areas.** 83.51(2)(a) asks for "The clean and safe condition of common areas."
(83.51(2)(a)), item 3. The statute does not define common areas, but its definition of the premises takes in
"areas, facilities, and property held out for the use of tenants generally" (83.43(11)). A shared pool or a shared garage may be a common area. That item is about a clean, safe condition, not
about keeping it open, and as a subsection (2) item it is no defense to eviction (83.51(2)(c)). So the keys' outcome
holds. But story 4's mistake 2, "provide or keep up a pool" (key), and story 9's mistake 3, "the landlord to provide parking" (key), might catch
an answer that mentions the common-areas item correctly, with its limits. Should the keys say that is not a mistake?

---

## Story 5. A guest broke the window

### 1. What happened

Today is 2026-02-10. Private apartment. On 2026-02-01 the tenant had a party. A friend the tenant invited broke the
bedroom window by accident. On 2026-02-02 the tenant sent a portal request; the office replied that the tenant must
pay for the repair. February rent was paid on 2026-02-01, before the party. It is cold. No eviction case.

### 2. The lease clauses that matter (lease_repairs.txt)

- "Tenant shall pay for repairing damage caused by Tenant, Tenant's household, or Tenant's guests." (clause 11)
- "Tenant shall report the need for repairs in writing through the resident portal." (clause 11)

Clause 11's list of what the landlord keeps in working order does not include windows. The lease says nothing else
about windows.

### 3. The tenant's message

> A friend at my party accidentally broke my bedroom window on February 1. The office says I have to pay to fix it, but windows are the landlord's job, right? It's cold. Can I make them fix it?

### 4. The right answer, step by step

**Step 1. Coverage.** Yes; not school housing.

**Step 2. Windows are on the statute's list.** The landlord must "maintain the roofs, windows, doors, floors, steps,
porches, exterior walls, foundations, and all other structural components in good repair" (83.51(1)(b)). So most of
the time a broken window is the landlord's to fix.

**Step 3. But not when a guest caused it.** "The landlord is not responsible to the tenant under this section for
conditions created or caused by the negligent or wrongful act or omission of the tenant, a member of the tenant's
family, or other person on the premises with the tenant's consent." (83.51(4)). A friend the tenant invited to a party
is an "other person on the premises with the tenant's consent" (83.51(4)). The key reads the accident as within this
rule, so the window is not the landlord's job under 83.51. (Q12: the rule speaks of a "negligent or wrongful act"
(83.51(4)); the facts say the friend broke it "by accident" (facts).) The tenant's own duty points the same way. The tenant must "Not
destroy, deface, damage, impair, or remove any part of the premises or property therein belonging to the landlord nor
permit any person to do so." (83.52(6)). (83.52 is stored but is not on this story's section list; Q14.)

**Step 4. The lease says the same.** Clause 11 puts "damage caused by Tenant, Tenant's household, or Tenant's guests"
(clause 11) on the tenant. For an apartment, a writing cannot change the 83.51(1) duty itself: "The landlord's
obligations under this subsection may be altered or modified in writing with respect to a single-family home or
duplex." (83.51(1)). But where 83.51(4) already takes the duty off the landlord, the clause only repeats it. (If the
friend was not careless, the clause would do more than repeat it; Q13.)

**Step 5. So the repair remedies do not reach this window.** Ending the lease (83.56(1)) and holding back rent
(83.60(1)(b)) both need the landlord to have failed a duty. Under the key's reading it has none here. The tenant can
still ask the landlord to make the repair and pay for it, as the office says.

**The points a right answer must make**

1. Required. Windows are on 83.51(1)(b)'s list, but 83.51(4) says the landlord is not responsible for conditions
   caused by the tenant, family, or someone there with the tenant's consent; an invited guest broke it, so 83.51 does
   not make it the landlord's job.
2. Required. Clause 11 puts guest damage on the tenant, so the tenant's repair remedies (ending the lease, holding
   back rent) do not reach it.

**Dates:** none.

### 5. Mistakes that make an answer wrong

1. "Says the landlord must fix the window at its own cost under 83.51." (key). Wrong because of 83.51(4), under the
   key's reading (Q12).
2. "Tells the tenant they may hold back rent or end the lease over the window." (key). Wrong for the reason in step 5.
3. "Treats the invited guest as someone the tenant did not let in." (key). Wrong because the tenant invited the
   friend.

### 6. The first test

- New skill: right in 3 of 3. All three treated the accident as covered by 83.51(4), one saying "An accident doesn't
  change this." (new answer).
- v1: right in 1 of 3 (1 partly, 1 wrong). All three raised the open point the new skill did not: whether an accident
  is 'negligent'. Run 1 left the remedies open until that is answered and was marked partly. Run 3 was marked wrong for
  citing 83.52(6), which the grader called "a rule not in the packet's statute files" (grader). 83.52 is in
  `statutes/`, but not on this story's section list, which is what the graders read.

### 7. Questions for you

**Q12. Is an accident 'negligent'?** 83.51(4) reaches conditions caused by "the negligent or wrongful act or omission"
(83.51(4)) of the tenant or a guest. The facts say the friend broke the window "by accident" (facts). An accident may or may
not be careless, and the stored text does not say that an accident counts. The key treats it as settled. The new
skill's answers said an accident "doesn't change this" (new answer), and v1, which raised the question in all three
runs, was marked down. Either add a fact that makes it careless (for example, the friend was roughhousing and fell
into the window), so the key stays settled; or make it open, with both readings.

**Q13. If the friend was not careless, can the lease still put it on the tenant?** Then 83.51(4) would not apply, and
only clause 11 would put the repair on the tenant. For an apartment, the statute lets a writing change the 83.51(1)
duty only "with respect to a single-family home or duplex" (83.51(1)), and a clause is void to the extent it "Purports
to limit or preclude any liability of the landlord to the tenant or of the tenant to the landlord, arising under
law." (83.47(1)(b)). So under that reading the clause may not shift the window to the tenant. If you choose 'open' in
Q12, should the key's second reading say this?

**Q14 (stories 5 and 7). Two sections missing from the list the graders read.** The graders read only the sections in
the story file's `sections` list. Two stored sections these stories touch are not on it: 83.52 (the tenant's duty not
to damage the home, or let anyone damage it) and 83.595 (the landlord's choices when a tenant leaves early; Q17). A
v1 answer was marked wrong for citing 83.52(6), which is in `statutes/`. Add both? And if you take up Q22, Q24, or
Q25, add the sections they rest on too (83.425 and 83.43, 83.48, 83.63).

---

## Story 6. Rent goes up right after a code complaint

### 1. What happened

Today is 2026-05-20. Private apartment, rented month to month since 2025-08-01. There has been mold in the bathroom
since March 2026; the tenant did nothing to cause it. On 2026-04-28 the tenant complained to the city code
enforcement office about the mold. An inspector came on 2026-05-05. A letter dated 2026-05-08 says the rent goes from
\$1,050 to \$1,300 a month starting 2026-07-01. Two neighbors in the building say their rent did not change. No
eviction case.

### 2. The lease clauses that matter (lease_monthtomonth.txt)

- "This tenancy begins on August 1, 2025 and continues from month to month until ended by Tenant or Landlord."
  (clause 3)
- "Rent is \$1,050.00 per month, due on the first day of each month, paid through the resident portal or by check
  delivered to the office." (clause 4)
- "This is a month-to-month tenancy, so this clause does not apply." (clause 9)

The lease says nothing on raising the rent. Why the story uses a month-to-month lease: under the base lease's fixed
term, the landlord could not change the rent mid-term on its own, since the lease "may be changed only in writing
signed by Landlord and Tenant" (clause 10). Month to month, the question is retaliation alone. The stored statute
sets no limit on how much or how often rent may rise; I searched it, and its only rule on a rent increase is the
retaliation rule below. Part II also keeps such matters from local governments: "This section supersedes any local
government regulations on matters covered under this part" (83.425), and its list includes "terms and conditions of
rental agreements" (83.425). Whether a law outside part II limits rent is outside the tool.

### 3. The tenant's message

> I reported mold to the city on April 28 and an inspector came May 5. Three days later I got a letter raising my rent from \$1,050 to \$1,300 starting July 1. My neighbors' rent didn't go up. Is that even legal?

### 4. The right answer, step by step

**Step 1. Coverage.** Yes; not school housing.

**Step 2. The rule.** "It is unlawful for a landlord to discriminatorily increase a tenant's rent or decrease services
to a tenant, or to bring or threaten to bring an action for possession or other civil action, primarily because the
landlord is retaliating against the tenant." (83.64(1)). Two words do the work: 'discriminatorily' and 'primarily'.

**Step 3. A protected act.** One example the statute lists: "The tenant has complained to a governmental agency
charged with responsibility for enforcement of a building, housing, or health code of a suspected violation
applicable to the premises" (83.64(1)(a)). The complaint to the city code office fits.

**Step 4. Treated differently: required.** The statute defines 'discrimination' this way: "a tenant is being treated
differently as to the rent charged, the services rendered, or the action being taken by the landlord, which shall be
a prerequisite to a finding of retaliatory conduct." (83.64(4)). A prerequisite is a must-have. The neighbors'
unchanged rent goes to that.

**Step 5. Primarily to retaliate: for a court.** The statute gives no test from the dates. The answer repeats the
dates as the tenant gave them (April 28, May 5, May 8) and counts no days between them.

**Step 6. How the protection works: mainly as a defense.** "Evidence of retaliatory conduct may be raised by the
tenant as a defense in any action brought against him or her for possession." (83.64(2)). It can also be raised when
a landlord sues over rent: the tenant may raise any other defense, "including the defense of retaliatory conduct in
accordance with s. 83.64" (83.60(1)(a)).

**Step 7. Two limits, at two different times.** Good faith limits raising the defense at all: "In order for the
tenant to raise the defense of retaliatory conduct, the tenant must have acted in good faith." (83.64(1)). The statute
defines good faith as "honesty in fact in the conduct or transaction concerned." (83.43(8)). Good cause speaks of an
eviction: "In any event, this section does not apply if the landlord
proves that the eviction is for good cause." (83.64(3)). Its examples: "Examples of good cause include, but are not
limited to, good faith actions for nonpayment of rent, violation of the rental agreement or of reasonable rules, or
violation of the terms of this chapter." (83.64(3)). So good cause comes in once the landlord brings an eviction case.
Here the act is a rent increase and no case is filed, so a right answer puts good cause inside the eviction defense,
as the key's point 2 does. (Q23.)

**Step 8. The mold.** Mold is on neither of 83.51's lists. Whether a code covers it is for the code office, which the
tool cannot check.

**The points a right answer must make**

1. Required. It may be unlawful retaliation: the rule, the code complaint as a protected act, being treated
   differently as a must-have (the neighbors' rent goes to that), and whether the landlord acted primarily to
   retaliate is for a court. No flat verdict.
2. Required. Retaliation is a defense if the landlord sues for possession; the tenant must have acted in good faith;
   it does not apply if the landlord proves good cause.
3. Helpful detail. The dates as the tenant gave them, with no days counted between them.

**Dates:** none. The answer counts nothing.

### 5. Mistakes that make an answer wrong

1. "Says flatly that the increase is, or is not, illegal retaliation." (key). Wrong because 'primarily' is for a
   court.
2. "Leaves out that the tenant must be treated differently, or leaves out both the good-faith and the good-cause
   limits." (key). Wrong because 83.64(4) makes different treatment a must-have, and the limits decide whether the
   defense works.
3. "Counts the days between the complaint and the letter itself." (key). Wrong because the model never does date
   math. (Repeating the tenant's own 'three days later' is not counting.)
4. "States a limit on how much or how often rent may rise that the statute does not have." (key). Wrong because the
   stored statute has none.

### 6. The first test

- New skill: right in 3 of 3. One run did not load the skill and read 83.64 itself. One did not lead with the answer
  but still made every point.
- v1: right in 0 of 3 (2 wrong, 1 partly). Run 1 overstated the rule and left out good cause. Run 2 said there is no
  separate way to sue over the increase; the grader pointed to 83.55. Run 3 read good cause as only about eviction
  cases already filed.

### 7. Questions for you

**Q15. Name damages for retaliation?** The key says the protection "works mainly as a defense" (key). 83.55 lets the
aggrieved party recover damages when the other side "fails to comply with the requirements of the rental agreement
or this part" (83.55), and 83.64(1) makes this kind of retaliation unlawful. A grader marked a v1 answer wrong for
saying there is no separate way to sue. Should the key name damages under 83.55 as a possible path (helpful detail;
how much, and how, outside the tool), so graders treat it the same way each time?

**Q23. Good cause and a rent increase.** Good cause applies when "the landlord proves that the eviction is for good
cause" (83.64(3)), so it comes in once the landlord brings an eviction case. A rent increase with no case filed gives
it nothing to attach to. The key is sound on this: its point 2 puts good cause inside the eviction defense, and
mistake 2 counts only leaving out both limits. But in the first test, a v1 answer said "The good-cause examples in
83.64(3) concern evictions" (v1 answer) and noted none had been filed, and the grader counted point 2 as not made, so
that answer was graded partly. Should point 2 say plainly that an answer which ties good cause to an eviction case,
as 83.64(3) does, makes the point? My view: yes. The text itself says "the eviction is for good cause" (83.64(3)),
and an answer should not lose credit for saying what the text says.

---

## Story 7. The lease ended over a repair; now the deposit

### 1. What happened

Today is 2026-05-25. Private apartment, on a lease running to 2026-07-31. From 2026-03-20 the only toilet was broken
and the pipe under the bathroom sink leaked. The tenant did nothing to cause it. March rent was paid on 2026-03-01,
before the problem.

- 2026-03-24: the tenant handed the office a letter naming the toilet and the leak and saying the tenant will end the
  lease if they are not fixed within 7 days.
- Nothing was fixed.
- 2026-04-02: the tenant handed the office a second letter: the tenant is ending the lease because nothing was fixed,
  will move out on 2026-04-15, and can be reached at a new address, given in the letter.
- 2026-04-15: the tenant moved out.

April rent was not paid, and the landlord has not asked for it. The landlord has sent no notice of a claim on the
deposit, by any means, and has returned none of the \$1,050 deposit.

### 2. The lease clauses that matter (lease.txt, the base lease)

- "This lease begins on August 1, 2025 and ends on July 31, 2026." (clause 3)
- "Tenant has paid a security deposit of \$1,050.00." (clause 5)
- "At move-out Tenant shall leave the apartment clean and empty, return all keys to the office, and give Landlord a
  forwarding address in writing." (clause 6)
- Clause 7: written notices by hand to the office or by certified mail.
- "Notices to Tenant shall be delivered to the apartment while Tenant lives there, and after move-out shall be mailed
  to the forwarding address Tenant gives in writing." (clause 8)

The lease says nothing on repairs, and nothing on leaving early.

### 3. The tenant's message

> In March my only toilet broke and the pipe under the sink leaked. I handed the office a letter on March 24 saying I'd end my lease if they didn't fix it in 7 days. They didn't, so on April 2 I gave them another letter saying I was ending the lease and moving out April 15, with my new address. I moved out April 15. It's been over a month and I haven't gotten my \$1,050 deposit back or heard anything. Do they have to give it back?

### 4. The right answer, step by step

**Step 1. Coverage.** Yes; not school housing.

**Step 2. The deposit rules decide.** The tenant asks about the deposit. When a lease ends this way, the repair
statute sends it to the deposit rules: "If the rental agreement is terminated, the landlord shall comply with s.
83.49 (3)." (83.56(6)). The repair rules matter for only one question below: when the rental agreement ended.

**Step 3. The landlord's deadlines.** To return it: "Upon the vacating of the premises for termination of the rental
agreement, if the landlord does not intend to impose a claim on the security deposit, the landlord must return the
security deposit, together with interest if otherwise required, within 15 days after the termination of the rental
agreement." (83.49(3)(a)). To claim part of it: "If the landlord intends to impose a claim on the deposit, the
landlord must, within 30 days after the termination of the rental agreement, provide the tenant written notice by
certified mail to the tenant's last known mailing address or by e-mail in accordance with s. 83.505 of his or her
intention to impose a claim on the deposit and the reason for imposing the claim." (83.49(3)(a)). The penalty for
missing it: "If the landlord fails to give the required written notice within the 30-day period, he or she forfeits
the right to impose a claim upon the security deposit and may not seek a setoff against the deposit but may file an
action for damages after returning the security deposit to the tenant." (83.49(3)(a)). A setoff means keeping some of
the deposit to cover a debt. No notice came, by any means.

**Step 4. When did the rental agreement end? Not settled.** The 30 days run "within 30 days after the termination of
the rental agreement" (83.49(3)(a)), so the start date decides everything. The key accepts either of two grounds for
the two readings.

*Ground one: did the tenant's ending of the lease hold?*

- The duty: a broken toilet and a leaking pipe are plumbing, so an 83.51(1) duty ("the plumbing in reasonable working
  condition" (83.51(1)(b))).
- The notice: written, naming both problems, saying the tenant will end the lease, and handed to the office, which is
  "delivering a true copy thereof" (83.56(4)).
- The 7 days: `count_days(repair_notice_delivered, 7)` gives 2026-03-31. That had passed when the tenant gave the
  second letter on 2026-04-02.
- Rent: March rent was paid before the problem and April rent was not paid, so 83.56(5)(a) does not come up.
- Material: not settled (the only toilet, and a leak).
- If the ending holds, the agreement ended, the key says, when the tenant moved out on 2026-04-15 (Q16). If it does
  not hold, the key says the lease ran to 2026-07-31 (Q17).

*Ground two: the deposit law's own words.* 83.49(3)(a) opens "Upon the vacating of the premises for termination of
the rental agreement" (83.49(3)(a)) and then counts from "the termination of the rental agreement" (83.49(3)(a)). It
names moving out and the end of the agreement as two things. One reading: moving out "for termination" (83.49(3)(a)) starts the
clock. The other: the clock waits for the agreement's end, 2026-07-31. (The notice landlords must give tenants
describes the claim notice as due "WITHIN 30 DAYS AFTER YOU MOVE OUT, OF THE LANDLORD'S INTENT TO IMPOSE A CLAIM
AGAINST THE DEPOSIT" (83.49(2)(d)); Q19.)

*The two outcomes.*

- From the move-out: `count_days(move_out_date, 30)` gives 2026-05-15, which has passed. The landlord forfeited the
  right to claim and owes the whole \$1,050. It may still sue for damages (such as unpaid April rent) after returning
  it.
- From the lease end: `count_days(lease_end_date, 30)` gives 2026-08-30, which has not passed. A notice may still
  come.
- No lean either way.

**Step 5. The tenant's move-out notice.** A tenant who leaves before the term ends "must give at least 7 days' written
notice by certified mail or personal delivery to the landlord before vacating or abandoning the premises, which
notice must include the address where the tenant may be reached." (83.49(5)). If the tenant does not: "Failure to give
such notice relieves the landlord of the notice requirement of paragraph (3)(a) but does not waive any right the
tenant may have to the security deposit or any part of it." (83.49(5)). The April 2 letter was in writing, handed
over (personal delivery), and gave the new address. `count_days(move_out_date, -7)` gives 2026-04-08, the last day to
give it. April 2 is on or before that day. So the landlord was not relieved of its notice.

**The points a right answer must make**

1. Required. The deposit rules (83.49(3)(a)) decide: a landlord who means to keep any of the deposit must give
   written notice of a claim within 30 days after the agreement ended, and none came.
2. Required. When the agreement ended is open; both readings, no lean, on either ground. One: move-out on
   2026-04-15, the 30 days ran out 2026-05-15 (passed), the landlord forfeited its claim and owes the whole \$1,050
   (and may still sue for damages after returning it). Two: the lease end of 2026-07-31, the 30 days run to
   2026-08-30 (not passed), and a notice may still come.
3. Required. The April 2 letter was the 7-day written notice with an address, by personal delivery, on or before
   2026-04-08, so the landlord was not relieved of its notice.

**Dates** (all from `count_days`):

| Counted from | Days | Date | Passed on 2026-05-25? |
|---|---|---|---|
| repair_notice_delivered, 2026-03-24 | 7 | 2026-03-31 | yes |
| move_out_date, 2026-04-15 | -7 | 2026-04-08 | yes |
| move_out_date, 2026-04-15 | 30 | 2026-05-15 | yes |
| lease_end_date, 2026-07-31 | 30 | 2026-08-30 | no |

### 5. Mistakes that make an answer wrong

1. "Says flatly that the whole deposit is owed now, or flatly that it is not owed yet, without both readings of when
   the rental agreement ended." (key). Wrong because the start date is open.
2. "Says the landlord was relieved of the notice under 83.49(5)." (key). Wrong because the tenant gave the notice in
   time (step 5).
3. "Decides the deposit by the repair rules (83.51, 83.56) instead of 83.49." (key). Wrong because 83.56(6) sends a
   terminated agreement to 83.49(3); the repair rules bear only on the date.
4. "Gives a date it worked out itself instead of from count_days." (key).

### 6. The first test

- The key changed after the first round. The old key tied the two readings only to whether the tenant's ending held.
  Under it: new right in 0 of 3 (2 partly, 1 wrong), v1 right in 0 of 3 (1 partly, 2 wrong). Most answers, in both
  versions, rested the readings on the deposit law's wording instead. One new answer left out that the timely move-out
  notice kept the landlord's duty. One said the repair question "does not change the notice rules above" (new
  answer), which the grader counted as an error. One v1 answer said the landlord must return the deposit or send
  notice within 30 days, where 83.49(3)(a) gives 15 days to return it.
- After the fix (the key accepts either ground), the rerun on the new skill was right in 3 of 3. The first round was
  not regraded under the new key.

### 7. Questions for you

**Q16. April 2 or April 15?** If the tenant's ending holds, the key says the agreement ended at move-out, 2026-04-15.
But the April 2 letter said "the tenant is ending the lease because nothing was fixed" (facts) and would move out
April 15. A reader could take April 2, the day that letter was delivered, as the end. `count_days(early_notice_date,
30)` would give 2026-05-02, also passed, so the outcome is the same. Should the key accept an answer that counts from
April 2 with count_days, or name it as a third possible start?

**Q17. Is July 31 the only date if the ending fails?** The key says the lease's end then counts. But 83.595 covers a
tenant who leaves early: it applies when "the tenant has surrendered possession of the dwelling unit to the landlord,
or the tenant has abandoned the dwelling unit" (83.595). The landlord may then, among other choices, "Treat the rental
agreement as terminated and retake possession for his or her own account, thereby terminating any further liability
of the tenant" (83.595(1)), or "Stand by and do nothing, holding the lessee liable for the rent as it comes due"
(83.595(3)). So under the second reading the end could come sooner than July 31, if the landlord retook the home.
Should that reading say *the lease's end, unless the landlord ended it sooner by retaking the home*, with 83.595 added
to the section list (Q14)?

**Q18. Add the 15-day return?** 83.49(3)(a) also gives the landlord 15 days to return the deposit when it does not
mean to claim any of it. The key does not mention this. Under the move-out reading, `count_days(move_out_date, 15)`
gives 2026-04-30, also passed. Add it as helpful detail? A v1 answer was already faulted for giving 30 days where 15
applies, so graders check it anyway.

**Q19. Does the disclosure tip the balance?** The notice landlords must give tenants (83.49(2)(d)) says the claim
notice is due "WITHIN 30 DAYS AFTER YOU MOVE OUT" (83.49(2)(d)). One rerun answer leaned on these words. They point
toward the move-out reading, while the rule itself (83.49(3)(a)) counts from 'termination'. Is 'no lean' still
right, or should the key mention these words beside the rule?

---

## Story 8. A furnished apartment: the bed frame the lease promises broke

### 1. What happened

Today is 2026-04-20. Private apartment, rented furnished. The bed frame the landlord provided broke on 2026-04-08:
the slats split and it sags to the floor. Age caused it, not the tenant. The tenant sent a portal request on
2026-04-09 and an e-mail to the office on 2026-04-14. The office replied that furniture is 'low priority'. April rent
was paid on 2026-04-01, before it broke; May rent is due 2026-05-01. No eviction case.

### 2. The lease clauses that matter (lease_furnished.txt)

- "The apartment is rented furnished. Landlord provides and will keep in good repair: a bed frame and mattress, a desk
  and chair, a sofa, and a dining table with two chairs." (clause 11)
- Clause 7: written notices by hand to the office or by certified mail.
- "Landlord and Tenant have not agreed to deliver notices by e-mail." (clause 8)

Unlike lease_repairs.txt, this lease has no clause on reporting repairs through the portal.

### 3. The tenant's message

> My apartment came furnished, and the bed frame the landlord provided broke on April 8. I've been sleeping on a mattress on the floor for almost two weeks. The office says furniture is 'low priority.' Can I take the cost of a new frame out of my May rent, or stop paying until they fix it?

### 4. The right answer, step by step

**Step 1. Coverage.** Yes; not school housing.

**Step 2. Whose job?** Furniture is on neither of 83.51's lists. Clause 11 says the landlord "provides and will keep
in good repair" (clause 11) a bed frame. So the repair is a lease duty.

**Step 3. Take the cost out of rent, or stop paying? Neither is protected.** The rent defense reaches only "a
material noncompliance with s. 83.51 (1)" (83.60(1)(b)), and a bed frame is a lease-only item. No stored section lets
a tenant fix something and take the cost out of rent. The stored text lowers rent only in set cases, and none fits here. For
example: the landlord "must abate the rent" (83.51(2)(a)) when a tenant must leave for pest treatment (item 1); a court may set
a cut after a successful 83.60(1)(b) defense; and for a failure beyond the landlord's control, the rent "shall be reduced by an
amount in proportion to the loss of rental value" (83.56(1)(b)) under the rule in story 1, step 6. The office's 'low
priority' reply does not suggest a cause beyond the landlord's control. So taking money off the rent risks an
eviction case. (Q1.)

**Step 4. End the lease.** 83.56(1) reaches "material provisions of the rental agreement" (83.56(1)). The tenant
needs a written notice naming the bed frame and saying the tenant will end the lease, delivered by hand to the office
or by certified mail (clause 7). If it is not fixed within 7 days after delivery, the tenant may end the lease.
Neither earlier message is that notice:

- The portal request is not a way 83.56(4) names (story 1, step 4).
- E-mail counts only "if the parties have signed an addendum to the rental agreement that the parties specifically
  agree to the electronic delivery of notices and have each provided a valid e-mail address for such purpose"
  (83.505(1)). An addendum is a signed add-on to the lease. Clause 8 says they have not agreed to e-mail notices.
- And as far as the facts show, neither message said the tenant would end the lease. (Q2.)

**Step 5. Material.** Not settled. The answer may set the tenant's words (a mattress on the floor for almost two
weeks) beside the word, without deciding.

**Step 6. Damages (helpful detail).** 83.55 reaches the lease failure.

**Step 7. Rent paid.** April rent was paid before the frame broke, so there is no waiver question yet.

**The points a right answer must make**

1. Required. The bed frame is not on 83.51's lists; it is the landlord's job because clause 11 promises it.
2. Required. Holding back rent, or taking the cost of a new frame out of rent, is not protected: the 83.60(1)(b)
   defense reaches only an 83.51(1) duty, and the stored statute gives no right to deduct a repair cost from rent;
   doing it risks an eviction case. Said plainly.
3. Required. To end the lease: a written notice by hand or certified mail, naming the problem and saying the tenant
   will end the lease; the portal request and the e-mail are not that notice (no e-mail agreement); 7 days after
   delivery; material is open.
4. Helpful detail. Damages under 83.55.

**Dates:** none.

### 5. Mistakes that make an answer wrong

1. "Says the tenant may hold back rent, or deduct the cost of a new frame from rent, as a protected step." (key). Wrong
   for the reasons in step 3.
2. "Says 83.51 requires the landlord to provide or repair furniture." (key). Wrong because neither list names
   furniture.
3. "Treats the portal request or the e-mail as the written notice that lets the tenant end the lease." (key). Wrong
   for the reasons in step 4.
4. "Says flatly that the broken bed frame is, or is not, material." (key).

### 6. The first test

Not run yet. This story is new. It tests an amenity the skill never names: furniture. Things to watch: whether the
answer finds clause 11 and treats the bed frame as a lease promise with no prompt from the skill; whether it rules out
the e-mail through clause 8 and 83.505(1); and whether it says plainly that deducting from rent is not protected.

### 7. Questions for you

Q1 and Q2 apply here too.

**Q20. Match the answer's wording to the point.** The key's answer says "Nothing in Florida's landlord-tenant law lets
you take a repair cost out of rent." (key). Its point says it more narrowly: "the stored statute gives no right to
deduct a repair cost from rent" (key). The tool can check only the stored part II, not local rules or court-made law.
Should the answer's sentence match the point?

---

## Story 9. The reserved covered parking the lease promises is closed

### 1. What happened

Today is 2026-05-20. Private apartment. The lease includes a reserved space in a covered, gated garage. On 2026-04-10
the landlord closed the whole garage for repaving it ordered; a sign on the gate says 'closed until further notice'.
The tenant parks on the street. On 2026-04-15 the tenant asked the office in person when it would reopen; no date was
given, and nothing was put in writing. May rent was paid on 2026-05-01 while the garage was closed. No eviction case.

### 2. The lease clauses that matter (lease_parking.txt)

- "Rent includes one reserved space in the covered, gated garage behind the building, space number 12." (clause 11)
- Clause 7: written notices by hand to the office or by certified mail.
- "This lease is the whole agreement. It may be changed only in writing signed by Landlord and Tenant." (clause 10)

Nothing in the lease lets the landlord close the garage. (Compare the pool in story 4, which the lease lets the
landlord close for set reasons.)

### 3. The tenant's message

> Our lease includes a reserved covered parking space, but the landlord closed the whole garage on April 10 for repaving and still hasn't reopened it. I've been parking on the street for over a month. Shouldn't my rent go down? What can I do?

### 4. The right answer, step by step

**Step 1. Coverage.** Yes; not school housing.

**Step 2. Whose job?** Parking is on neither of 83.51's lists (Q11 on common areas). Clause 11 makes the space part
of what the rent pays for. So it is a lease promise, and with no clause allowing a closure, the closure fails it.

**Step 3. Does the rent go down on its own? No.** This is the tenant's main question. No stored rule lowers the rent
by itself for a broken lease promise. The one rule that comes close is 83.56(1)(b). It applies to a failure "due to
causes beyond the control of the landlord" (83.56(1)), where the landlord "has made and continues to make every
reasonable effort to correct the failure to comply" (83.56(1)), and the tenant stays. Then the rent "shall be reduced
by an amount in proportion to the loss of rental value caused by the noncompliance." (83.56(1)(b)). Here the landlord
ordered the repaving itself, which points away from a cause beyond its control, and it has given no reopening date.
The key does not discuss this rule. (Q21.)

**Step 4. Hold back rent or pay less? Not protected.** As in stories 1, 4, and 8: the defense reaches only "a material
noncompliance with s. 83.51 (1)" (83.60(1)(b)), so paying less risks an eviction case. (Q1.)

**Step 5. End the lease.** A written notice naming the closed garage and saying the tenant will end the lease if the
space is not back within 7 days, delivered by hand to the office or by certified mail (clause 7). The in-person
question is not that notice: it was not written, and it asked when the garage would reopen, not that the tenant would
end the lease.

**Step 6. Material.** Not settled.

**Step 7. Damages.** 83.55 reaches the lost parking. How much, and how to bring it in court, is outside the tool.

**Step 8. May rent (helpful detail).** The tenant paid May rent while the garage was closed. That raises the
83.56(5)(a) question: a "continuing noncompliance" (83.56(5)(a)), since the garage is still closed, or a waiver. Both
readings.

**The points a right answer must make**

1. Required. The parking space is a lease promise (clause 11), not on 83.51's lists, and no clause lets the landlord
   close the garage.
2. Required. The rent does not go down on its own, and holding back or cutting rent is not protected, since the
   83.60(1)(b) defense reaches only an 83.51(1) duty; it risks an eviction case.
3. Required. The tenant's paths: a written 7-day notice to end the lease over a material lease provision, by hand or
   certified mail (the in-person question is not that notice), with material open; and damages under 83.55.
4. Helpful detail. May rent and 83.56(5)(a): a continuing failure, or a waiver; both readings.

**Dates:** none.

### 5. Mistakes that make an answer wrong

1. "Says the tenant may hold back rent or simply pay less as a protected step." (key). Wrong for the reason in step 4.
2. "Says the rent goes down by law on its own." (key). Wrong because no stored rule does that here. (Q21.)
3. "Says 83.51 requires the landlord to provide parking." (key). Wrong because neither list names parking. (Q11.)
4. "Treats the in-person question as the written notice to end the lease." (key). Wrong for the reasons in step 5.
5. "Says flatly that the closed garage is, or is not, material." (key).

### 6. The first test

Not run yet. This story is new. It tests an amenity the skill never names: covered parking. Things to watch: whether
the answer finds the parking promise with no prompt from the skill; whether it notices that, unlike the pool, nothing
lets the landlord close the garage; and how it answers 'Shouldn't my rent go down?' without promising a rent cut.

### 7. Questions for you

Q1 and Q11 apply here too.

**Q21. The rule that does lower rent.** The tenant asks whether the rent should go down. 83.56(1)(b) is the stored
rule that lowers rent while a tenant stays, for a failure beyond the landlord's control. The key never mentions it,
and mistake 2, "Says the rent goes down by law on its own." (key), could catch an answer that raises it as a possibility. The
facts point away from it, since the landlord ordered the repaving. But the stored text does not say whether a
landlord's own repair project is a cause "beyond the control of the landlord" (83.56(1)). Should the key say why the
rule likely does not apply here (or call it open), and say that an answer which raises it, with its conditions, is not
making mistake 2?

---

## All the questions, in one list

**Bigger: these could change how an answer is graded.**

- **Q1** (stories 1, 4, 8, 9). The keys say holding back rent over a lease-only promise has no defense at all; the
  stored 83.60(1)(a) leaves room for "any other defense" (83.60(1)(a)). Soften to *the statute's rent defense does not reach it*?
- **Q4** (story 2). The stored text does not say when a mailed notice counts as delivered. Keep counting from the
  mailing date as a mistake, accept either count_days date, or mark it open?
- **Q5** (story 2). Mistake 3, "says the tenant may stop paying rent" (key), may catch a right answer that rent stops once
  the lease is validly ended. Narrow it to holding back rent while staying?
- **Q12** (story 5). 83.51(4) needs a "negligent or wrongful act" (83.51(4)); the facts say only "by accident" (facts). Add a fact that
  makes it careless, or make it open?
- **Q13** (story 5). If the guest was not careless, the lease clause may not shift the window to the tenant (83.51(1)
  allows changes only for a house or duplex; 83.47(1)(b)). Add this to the open reading?
- **Q21** (story 9). The key never mentions 83.56(1)(b), the rule that lowers rent for a failure beyond the landlord's
  control, and mistake 2 could catch an answer that raises it. Explain why it likely does not apply, and say raising
  it is not a mistake?
- **Q16** (story 7). If the ending holds, the agreement may have ended on April 2 (the ending letter) rather than
  April 15; count_days would give 2026-05-02. Accept that date?
- **Q17** (story 7). If the ending fails, 83.595 lets the landlord retake the home and end the agreement before
  July 31. Say so in the second reading?
- **Q9** (every story). Add a line like *says how long something has lasted, from its own counting* to every key's mistakes, and
  the usual made-up-date line to stories 4, 5, 6, 8, and 9?
- **Q10** (story 4). The facts do not say why the pool is closed, though the clause allows closing only for cleaning,
  repairs, or weather. Add the reason, or expect the answer to ask?
- **Q2** (stories 1, 4, 8). The facts do not say what the portal requests and the e-mail said. Add a line saying they
  asked for a repair and did not mention ending the lease?
- **Q23** (story 6). Good cause applies to an eviction case; a v1 answer that said so was graded partly. Say in
  point 2 that tying good cause to an eviction case makes the point? (My view: yes.)

**Smaller: wording, a missing section, or helpful detail.**

- **Q3** (story 1). Say what the part-on-order rule can do (a rent cut in proportion), and that raising it is not
  mistake 2?
- **Q6** (stories 2, 3, 5, 7). Note that 83.51(1)(b)'s list applies only where there are no codes, so an answer that
  says *a code may decide* is not marked down?
- **Q7** (story 3). Add the April-rent waiver question (83.56(5)(a)) as helpful detail, as stories 2, 4, and 9 do?
- **Q8** (story 3). Name the motion to determine rent, the second way to keep defenses under 83.60(2)?
- **Q11** (stories 4, 9). Say that mentioning the common-areas item of 83.51(2)(a), with its limits, is not the
  *83.51 requires a pool, or parking* mistake?
- **Q14** (stories 5, 7). Add 83.52 and 83.595 to the section list the graders read (and 83.425, 83.43, 83.48, 83.63
  for any of Q22, Q24, Q25 you take up)?
- **Q15** (story 6). Name damages under 83.55 as a possible path for retaliation?
- **Q18** (story 7). Add the 15-day return rule as helpful detail (2026-04-30 from count_days, passed)?
- **Q19** (story 7). The required disclosure says "WITHIN 30 DAYS AFTER YOU MOVE OUT" (83.49(2)(d)); does 'no lean' still hold?
- **Q20** (story 8). Narrow "Nothing in Florida's landlord-tenant law" (key) to match the point's "the stored statute" (key)?
- **Q22** (stories 1, 2, 3, 6, skill). Codes may be state or local (83.43(3)); how far part II's preemption (83.425)
  reaches a local housing code is open, with a narrow and a broad reading. Say *a code (state or local)*, and put both
  readings in the key?
- **Q24** (stories 1, 3, 4, 6, 7, 8, 9). Add one line on attorney fees (83.48, and 83.49(3)(c) for the deposit), which
  can go to either side (the deposit rule is the firmer one; a lease cannot waive it; no fees for personal injury
  under 83.51), wherever a key names damages or a suit, and the same line to the skill first?
- **Q25** (story 3). Keep 83.63 (casualty damage) out of the required points, note in the key that a recurring leak
  may or may not count, and say an answer raising it with its conditions is not mistake 1, nor wrong for skipping the
  83.56(1) notice?

---

## Your answers (2026-10-28)

You took the starred choice on every question. Q4 is 'accept either date', not your first pick of 'open', so the
skill's delivery rule stays. Q12's careless fact makes Q13 moot. Each answer is now in `stories.json`; the skill gets
the one line Q24 asks for.

| Q | Your answer | Where it went |
|---|---|---|
| Q1 | Soften: the statute's rent defense does not reach a lease-only promise; whether any other defense would is outside the tool; holding back rent stays risky. | Stories 1, 4, 8, 9: answer and point. |
| Q2 | Say what the requests said: a repair, nothing about ending the lease or holding back rent. | Stories 1, 4, 8: facts. |
| Q3 | Say what the part-on-order rule can do (a rent cut in proportion), keep 'by the parties' open, and raising it is not mistake 2. | Story 1: answer and point 4. |
| Q4 | Accept either date, if it comes from count_days and says which day it counted from. | Story 2: point 1, mistake 1, dates. |
| Q5 | Narrow mistake 3 to stopping rent while still living there. | Story 2: mistake 3. |
| Q6 | An 83.51(1) duty is on the (1)(b) list or under a code; 'a code may decide' is not wrong. | Stories 2, 3, 5: points. Story 7 needed no change. |
| Q7 | Add the April-rent waiver question as helpful detail. | Story 3: point 3. |
| Q8 | Name the motion to determine rent as helpful detail. | Story 3: answer and point 2. |
| Q9 | Add a time-span mistake to every key, and the made-up-date mistake to stories 4, 5, 6, 8, 9. | Every story: mistakes. |
| Q10 | Give the pool's reason in the facts: a pump repair. | Story 4: facts and answer. |
| Q11 | Mentioning the common-areas item, with its limits, is not the '83.51 requires' mistake. | Stories 4, 9: mistakes. |
| Q12 | Add a careless fact: the friend was roughhousing and fell into the window. | Story 5: facts, answer, point 1. |
| Q13 | Moot (Q12). | Nothing. |
| Q14 | Add 83.52, 83.595, 83.425, 83.43, 83.48, 83.63 to the section list. | `sections`. |
| Q15 | Name damages under 83.55 for retaliation as helpful detail. | Story 6: point 3. |
| Q16 | Accept April 2 as a start, 2026-05-02 from count_days. | Story 7: point 2, dates. |
| Q17 | Second reading: the lease's end, unless the landlord ended it sooner by retaking the home. | Story 7: answer and point 2. |
| Q18 | Add the 15-day return rule as helpful detail, 2026-04-30 from count_days. | Story 7: point 4, dates. |
| Q19 | Keep no lean; the disclosure may be quoted beside the rule. | Story 7: point 4. |
| Q20 | Narrow the answer to the statute. | Story 8: answer. |
| Q21 | 83.56(1)(b) likely does not apply (the landlord ordered the repaving); raising it with its conditions is not mistake 2. | Story 9: point 2, mistake 2. |
| Q22 | Say 'a code (state or local)'; one simple line for the tenant; the two readings of 83.425 in the key. | Stories 1, 2, 3, 6: answer, points. |
| Q23 | Tying good cause to an eviction case makes point 2. | Story 6: point 2. |
| Q24 | One line on attorney fees wherever a key names damages or a suit; the skill gets it first. | Stories 1, 3, 4, 6, 7, 8, 9; `skills/repair_not_made.md`, option 3. |
| Q25 | 83.63 stays out of the required points; open in the key; raising it, or skipping the 83.56(1) notice on that route, is not a mistake. | Story 3: point 3. |
