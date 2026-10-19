# Landlord-Tenant tool

This file is the fixed description of the project: what it is, what it must never do, and the shape of the
whole plan. It changes only when the project's purpose or architecture changes. Day-to-day state lives in
TODO.md (what is next), DOCUMENTATION.md (how the code works now), and CHANGELOG.md (what changed).

## Purpose

A tool for a Florida college-housing tenant in a dispute with a landlord, under Fla. Stat. ch. 83, pt. II.
It reads the tenant's lease, works out which issues they have, applies the lease terms, the statute text,
and what Florida courts have said about that text to the tenant's confirmed facts, keeps an evidentiary
record over the life of the dispute, and drafts letters the tenant sends themselves.

The author is a law student, not admitted. Until 2026-10-02 the tool only set the lease, the statute, and
the cases beside the tenant's facts and never said what they meant for the tenant. A list of quotes does not
help a tenant who asks what they can do, so the tool now applies the law, in a conversation (the author's
decision of 2026-10-12, after trying the web page: the tool had been too rigid, asking what the lease answers,
waiting instead of helping, and sending the tenant to "check your lease"). The tool finds out what the tenant
wants (to move out, get a repair, get the deposit back, answer a notice) and helps them get there:

- it answers what the tenant asked, first, in a reply that fits the question, and a follow-up builds on what was
  already said instead of starting over;
- asked whether or how they can do something, it makes clear whether they can before any step toward it, what
  that turns on, and what is left to do;
- each rule is one plain sentence cited to its source (a section of the statute, a section of the lease, a case
  and page); the program prints the cited words beneath the answer, so the tenant has the exact text to point to
  without reading it inside the answer;
- it reads the lease itself for a point the lease decides, asks the tenant for a fact it does not have, and sends
  the tenant to check only what it cannot read (military orders, a local code, a paper it does not hold);
- a point the stored text and the cases leave unsettled is said briefly, with the readings on each side;
- when the tenant is ready to act, it can help keep a record that each step was done.

The tool knows what it knows (the author's decision of 2026-10-04). A point an answer turns on is known (a
confirmed fact, a lease clause the tool has read, the statute), something the tenant can tell it, something the
tenant can check, not settled (an open question, with its readings), or outside the tool (law it does not hold).
The answer never states a gap as a fact ("the lease does not mention it" from a lease the tool has not searched),
and says how an unknown would change what the tenant can do.

The answer does not recite: no statute or lease passage pasted into it, and no list of what the tenant has
already told the tool. The tool does not choose among the options for the tenant, and it says that its answer
is its reading of the stored law, not a lawyer's advice.

Applying the law to one person's facts is legal advice. The tool is in development: it runs on test matters
only, and no tenant uses it until the unlicensed-practice question is settled (an attorney's supervision or
a review).

## The four goals

1. Intake the contract: read the lease PDF, extract a fixed profile of named clauses, verify every quote
   against the page it cites.
2. Match the dispute with the contract: the model loads the skills whose descriptions fit the tenant's
   situation, finds out the facts each needs (the lease first, then the tenant), and confirms with the tenant
   each fact the record keeps.
3. Apply the law to the dispute: load the statute sections of each loaded skill and the court decisions that
   read them, compute every statutory deadline from confirmed facts in code, and answer the tenant's questions
   by applying the skill's instructions and the stored text, cited and printed by the program, to the facts.
4. Keep a coherent evidentiary record: one append-only event log per matter holding facts as confirmed,
   messages as pasted, files as provided, letters as drafted and as sent, and a timeline built from it.

## The three parts

1. The chatbot: a LangChain agent with a small set of tools and a short system prompt of rules, on one
   front end, the web page.
2. The data bank: one folder per tenant and per matter, so a returning tenant resumes where they left off.
3. Skills: one per situation (2026-10-12; they replace the YAML playbooks). The model sees every skill's name
   and one-line description and loads the ones that fit, as Claude Code loads skills; a loaded skill's
   instructions, the statute sections it rests on, and the topics of the case wiki's verified pages for those
   sections enter the prompt (a topic's cases, with their facts and rules as quoted on their pages, reach the
   model when it asks for them, so it can set them beside the tenant's facts), so the context window holds only
   what the matter needs.

## Non-negotiables

- An application rests only on stored text and on the tenant's own facts: those confirmed, and, in the
  conversation, what the tenant has said, named as what they said until they confirm it (2026-10-12). The
  record, the deadlines, and letters rest on confirmed facts only. A fact the tenant has not given is named as
  missing, never assumed, and the step that needs it is left open. Every rule in an answer is cited to its
  source, and the program prints the cited words; every fact carries where it came from.
- The tool knows what it knows. A point it has not settled from the tenant's facts, a lease clause it read, or
  the statute is named as one the tenant can tell it, can check, that is not settled, or that is outside the
  tool, never answered as if known; and the answer says how it would change the tenant's options.
- An option comes before its steps. The answer says whether the tenant can do what they ask, applying the loaded
  skill's conditions, quoted from the statute, to their facts and their lease, before it gives any step toward
  it. (From 2026-10-04 to 2026-10-12 code decided whether each option was open, from the playbooks' conditions.)
- An open point stays open. Where the statute's words and the cases do not settle a question (a skill's open
  questions), the answer says so and gives the readings on each side; it never presents one as settled.
- The model never computes a date. All date arithmetic is in one function, from confirmed facts only.
- The model never sends anything. Letters are drafted; the tenant sends them and reports the sending.
- The model never quotes from memory. Lease quotes come from the lease's stored text (the verified
  profile, or the clause `search_lease` found); statute quotes come from
  the stored text in `statutes/`; case quotes come from the stored opinions in `cases/`; every quote is
  checked by substring against its source before use.
- Cases are used whole and fairly: an answer that relies on a case shows every case on the question,
  whichever side it favors, each with its court, year, and the statute version it read; it sets the tenant's
  facts beside the case's facts as the court states them and says where they differ; and it names a case
  that cuts against the tenant. A case reaches the tenant only after the author has read it and verified
  its entry.
- A fact enters the record only after the tenant confirms it. Proposed facts carry how they were proposed
  (stated or inferred) and the tenant's own words as basis.
- The record is append-only. Current state is a snapshot; history is never edited or deleted.
- Letters are a code template around the tenant's own account. The program prints the date, the names and
  addresses as the lease gives them, the reply-by date, the quoted sentences (each checked), the delivery line,
  and the signer; the model writes only the tenant's account and request, in the tenant's voice, with no cite
  or legal conclusion in them (2026-10-11). The timeline, the cases' text, and the cited statute and lease
  words are printed by code; the model's answer applies them, cites each case by name and page, and never says
  a case or a section holds anything its printed words do not.
- `statutes/` and `cases/` are read-only corpora. Skill and case wiki quotes are verified against them
  after every edit. `cases/` holds the court's text only: no publisher's headnotes, synopses, or citator
  flags.

## The unit of legal knowledge

A skill: one markdown file per situation in `skills/` (2026-10-12; until then a YAML playbook, whose typed
half let code decide which facts to ask and which options were open). A skill is written to the model as
instructions: when to load it, what to find out and where, what the tenant can do and what each option needs
(the statute's words quoted), what the statute does not settle (the readings on each side), letters, and
mistakes to avoid. Only a short header is typed, because code needs it: the skill's name and one-line
description (how the model picks it), the statute sections it loads, the deadline clocks code counts (with the
facts they count from), and the author's sign-off. Every quote in a skill is checked against `statutes/`.
Skills, one per situation: deposit_not_returned, deposit_claim_received, repair_not_made,
notice_received_violation, rent_increased, lease_ending, notice_received_nonpayment,
landlord_entered_unannounced, wants_to_leave_early, neighbor_disturbance. A situation no skill fits gets an
answer only from what the statute search finds, said as such.

Beside the skills, a case wiki (`wiki/`), after Andrej Karpathy's LLM wiki: linked markdown pages that
Claude Code writes from `cases/` in development sessions and the author reviews. One page per case (its
issue, rule, and reasoning quoted from the opinion with pin pages, the statute version it read, and how it
relates to other cases) and one page per topic, made as topics emerge from the cases, never fixed in
advance. Pages link to each other by topic, rule, reasoning, and how later courts treated earlier ones, and
carry the statute sections they read as tags. The wiki's own prose describes and connects; it never states
the law. Each case page quotes the facts the decision turned on, as well as its rule and reasoning, so the
chat can set a tenant's facts beside them; the application happens in the chat, from those quotes, never on
the page. A page reaches the chat only after the
author verifies it, and an edit afterwards undoes the verification. Tenant sessions read the wiki and never
write to it. Decisions approving forms are filed as forms, not rules. Cases are published opinions of Florida's appellate courts
and of federal courts applying ch. 83, each shown with its court; county and circuit court decisions stay
out.

## Beyond the current plan

A chatbot front end: `app.py`, a web page on this computer only (2026-10-02), with the model's words apart
from the program's; since 2026-10-12 the only front end (the terminal loop was removed). Putting it in front
of tenants waits until the data bank, skills, and case wiki work is done, and on logins, where `matters/` data
lives, and the unlicensed-practice review.

## Stack

Python, LangChain agent with `@tool` functions, Pydantic for every structured shape, PyPDF2 for the lease,
markdown skills, a markdown case wiki, two models on the UF gateway (an agent model and an extraction model), Streamlit for
the web page. Built first as a
Colab notebook, moved to this folder as modules on 2026-09-25.
