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
help a tenant who asks what they can do, so the tool now applies the law. An answer to a question about the
law has this shape:

- the rule, quoted from the lease, the statute, or a court, with its source;
- the tenant's facts it turns on, each from the record;
- for each condition of the rule, whether those facts meet it, fail it, or are not known yet;
- what follows on those facts: the options the statute gives the tenant and what each requires first;
- any point the stored text and the cases leave unsettled, with the readings on each side.

The tool does not choose among the options for the tenant, and it says that its answer is its reading of
the stored law, not a lawyer's advice.

Applying the law to one person's facts is legal advice. The tool is in development: it runs on test matters
only, and no tenant uses it until the unlicensed-practice question is settled (an attorney's supervision or
a review).

## The four goals

1. Intake the contract: read the lease PDF, extract a fixed profile of named clauses, verify every quote
   against the page it cites.
2. Match the dispute with the contract: classify the tenant's description into issues, work out which facts
   each issue needs, and confirm each one with the tenant before it is recorded.
3. Apply the law to the dispute: preload the statute sections for each issue and the court decisions
   that read them, compute every statutory deadline from confirmed facts in code, and answer the tenant's
   questions by applying stored text, quoted, to the confirmed facts.
4. Keep a coherent evidentiary record: one append-only event log per matter holding facts as confirmed,
   messages as pasted, files as provided, letters as drafted and as sent, and a timeline built from it.

## The three parts

1. The chatbot: a LangChain agent with a small set of tools and a rules-based system prompt.
2. The data bank: one folder per tenant and per matter, so a returning tenant resumes where they left off.
3. Skills: the guidance half of each playbook, the statute sections it rests on, and the topics of the
   case wiki's verified pages for those sections, loaded into the prompt when its issue becomes active (a
   topic's cases, with their facts and rules as quoted on their pages, reach the model when it asks for them,
   so it can set them beside the tenant's facts) instead of pasted for every issue, so the context window
   holds only what the matter's issues need.

## Non-negotiables

- An application rests only on confirmed facts and stored text. A fact the record does not hold is named as
  missing, never assumed, and the step that needs it is left open. Every rule in an answer is quoted with its
  source, and every fact carries where it came from.
- An open point stays open. Where the statute's words and the cases do not settle a question (a playbook's
  open questions), the answer says so and gives the readings on each side; it never presents one as settled.
- The model never computes a date. All date arithmetic is in one function, from confirmed facts only.
- The model never sends anything. Letters are drafted; the tenant sends them and reports the sending.
- The model never quotes from memory. Lease quotes come from the verified profile; statute quotes come from
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
- Letters are a code template, not model text. The timeline and the cases' text are printed by code; the
  model's answer applies and quotes them, never retells them in its own words.
- `statutes/` and `cases/` are read-only corpora. Playbook and case wiki quotes are verified against them
  after every edit. `cases/` holds the court's text only: no publisher's headnotes, synopses, or citator
  flags.

## The unit of legal knowledge

A playbook: one YAML file per issue. Its `spec` half is typed and read by code (the facts needed, the
statutory clocks, exclusions, related issues, open questions). Its `guidance` half is prose for the model
(questions to ask, letter postures, what the statute leaves unsettled). Playbooks in scope, in order:
deposit_not_returned, deposit_claim_received, repair_not_made, notice_received_violation, rent_increased,
lease_ending, notice_received_nonpayment, landlord_entered_unannounced, wants_to_leave_early,
neighbor_disturbance. That is one per issue label the classifier can pick, except "other", which means none
of them fits.

Beside the playbooks, a case wiki (`wiki/`), after Andrej Karpathy's LLM wiki: linked markdown pages that
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

A chatbot front end in place of the terminal loop: `app.py`, a web page on this computer only (2026-10-02),
draws what the terminal prints, with the model's words apart from the program's. Putting it in front of
tenants waits until the data bank, skills, and case wiki work is done, and on logins, where `matters/` data
lives, and the unlicensed-practice review.

## Stack

Python, LangChain agent with `@tool` functions, Pydantic for every structured shape, PyPDF2 for the lease,
YAML playbooks, a markdown case wiki, two models on the UF gateway (an agent model and an extraction model), Streamlit for
the web page. Built first as a
Colab notebook, moved to this folder as modules on 2026-09-25.
