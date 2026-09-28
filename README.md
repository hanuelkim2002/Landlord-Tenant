# Landlord-Tenant tool

This file is the fixed description of the project: what it is, what it must never do, and the shape of the
whole plan. It changes only when the project's purpose or architecture changes. Day-to-day state lives in
TODO.md (what is next), DOCUMENTATION.md (how the code works now), and CHANGELOG.md (what changed).

## Purpose

An organizer and information tool for a Florida college-housing tenant in a dispute with a landlord, under
Fla. Stat. ch. 83, pt. II. It reads the tenant's lease, works out which issues they have, lines up the lease
terms and the statute text next to the tenant's facts, keeps an evidentiary record over the life of the
dispute, and drafts letters the tenant sends themselves.

The author is a law student, not admitted. The tool gives no advice. Every output is framed as: here is what
your lease says, here is what the statute says, here are your dates. It never says what a provision means for
the tenant, which of the lease or statute controls, or what the tenant should do.

## The four goals

1. Intake the contract: read the lease PDF, extract a fixed profile of named clauses, verify every quote
   against the page it cites.
2. Match the dispute with the contract: classify the tenant's description into issues, work out which facts
   each issue needs, and confirm each one with the tenant before it is recorded.
3. Match the dispute with the law: preload the statute sections for each issue, compute every statutory
   deadline from confirmed facts in code, and let the model quote only stored text.
4. Keep a coherent evidentiary record: one append-only event log per matter holding facts as confirmed,
   messages as pasted, files as provided, letters as drafted and as sent, and a timeline built from it.

## The three parts

1. The chatbot: a LangChain agent with a small set of tools and a rules-based system prompt.
2. The data bank: one folder per tenant and per matter, so a returning tenant resumes where they left off.
3. Skills: the guidance half of each playbook and the statute sections it rests on, loaded into the prompt
   when its issue becomes active instead of pasted for every issue, so the context window holds only what
   the matter's issues need.

## Non-negotiables

- The model never computes a date. All date arithmetic is in one function, from confirmed facts only.
- The model never sends anything. Letters are drafted; the tenant sends them and reports the sending.
- The model never quotes from memory. Lease quotes come from the verified profile; statute quotes come from
  the stored text in `statutes/`; every quote is checked by substring against its source before use.
- A fact enters the record only after the tenant confirms it. Proposed facts carry how they were proposed
  (stated or inferred) and the tenant's own words as basis.
- The record is append-only. Current state is a snapshot; history is never edited or deleted.
- Letters are a code template, not model text. The timeline is code output, never relayed by the model.
- `statutes/` is a read-only corpus. Playbook quotes are verified against it after every edit.

## The unit of legal knowledge

A playbook: one YAML file per issue. Its `spec` half is typed and read by code (the facts needed, the
statutory clocks, exclusions, related issues, open questions). Its `guidance` half is prose for the model
(questions to ask, letter postures, what the statute leaves unsettled). Playbooks in scope, in order:
deposit_not_returned, deposit_claim_received, repair_not_made, notice_received_violation, rent_increased,
lease_ending, notice_received_nonpayment, landlord_entered_unannounced, wants_to_leave_early. That is one
per issue label the classifier can pick, except "other", which means none of them fits.

## Beyond the current plan

A case pool of Florida appellate decisions by section (a candidate list exists, no code). A chatbot front
end in place of the terminal loop. Both wait until the data bank and skills work is done.

## Stack

Python, LangChain agent with `@tool` functions, Pydantic for every structured shape, PyPDF2 for the lease,
YAML playbooks, two models on the UF gateway (an agent model and an extraction model). Built first as a
Colab notebook, moved to this folder as modules on 2026-09-25.
