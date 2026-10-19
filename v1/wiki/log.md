# Log

What was added or changed in the wiki, newest last. Entries are added, never rewritten.

## 2026-10-01 pilot ingest

- Case pages: Durene v. Alcime (448 So. 2d 1208), Casey v. Picinich (573 So. 2d 76), Plakhov v. Serova
  (126 So. 3d 1221), each read in full from `cases/`.
- Topic pages, made as the three cases raised them: Landlord's notice of claim on the deposit (all three);
  Fees and costs in a suit over the deposit (Durene, Casey); Notice of how the deposit is held (Plakhov);
  Constructive eviction (Plakhov); Points not raised in the trial court (Plakhov, no section).
- Named in plain text, no page yet: Hankins v. Smith, 103 Fla. 892 (1931), in `cases/`, quoted by Plakhov on
  constructive eviction; In re Hasty, 25 B.R. 429 (Bankr. M.D. Fla. 1982), not in `cases/`, disagreed with by
  Durene; the 83.48 prevailing-party opinions in `cases/`.
- Noted: Casey v. Picinich, marked unverified in the case-pool candidate list, is a per curiam memorandum
  opinion at 573 So. 2d 76. In Plakhov the landlord's notice of claim was sent (the tenant admitted it); the
  court decided the notice was excused anyway.
- `python wiki.py check`: 8 pages, 0 problems, 0 warnings. No page verified yet.

## 2026-10-01 deposit cases ingest

- Case pages, each read in full from `cases/`: Atlantis Estate Acquisitions, Inc. v. DePierro (125 So. 3d
  889), Lewis v. Guthartz (428 So. 2d 222), Guthartz v. Lewis (408 So. 2d 600), Malagon v. Solari (566 So. 2d
  352), Nardi v. Continental National Bank (559 So. 2d 307), Florida RS, Inc. v. Nelson (751 So. 2d 55),
  Florida Bar re Approval of Forms (1991) (591 So. 2d 594), Department of Business Regulation v. Stein (326
  So. 2d 205), Florida Patient's Compensation Fund v. Rowe (472 So. 2d 1145), Meli Investment Corp. v. O.R.
  (621 So. 2d 676), Xanadu of Cocoa Beach, Inc. v. Lenz (504 So. 2d 518), Gilbert v. Jabour (527 So. 2d 951),
  Scruggs v. Sutton (970 So. 2d 853). These and the pilot's three are the opinions in `cases/` that cite
  83.49 or 83.48. Not ingested: 50 So. 3d 503, not in `cases/`.
- Topic renamed: Notice of how the deposit is held is now How the landlord holds the deposit and advance
  rent, since Nardi and Atlantis are about holding the money, not the notice. Plakhov's links follow.
- New topics: Prevailing party fees under 83.48; How a fee award is computed; Interest on the deposit;
  Advance rent; Landlord's remedies after a tenant's breach; Applying an amended statute; Punitive damages
  against a landlord; Court-approved landlord and tenant forms. Existing topics gained cases.
- SCHEMA: a layout for a decision approving forms, and an "Also said" section for statements outside the
  issues decided.
- Noted: Gilbert v. Jabour, listed in the candidate list under 83.51 maintenance, is a fee case (83.48).
  Rowe is a medical malpractice case that names 83.48. The 1991 deposit form's note gives 15 days. The
  interest wording moved (83.49(2) in Stein, 83.49(9) in Nelson, 83.49(1)(b) today), and the advance rent
  definition moved (83.43(9) in Atlantis, 83.43(2) today).
- Named in plain text, no page yet: Kendall East Estates, Inc. v. Banks (in `cases/`), Wagner v. Rice,
  Standard Guar. Ins. Co. v. Quanstrom, Stockman v. Downs, In re Revisions to Simplified Forms (2010).
- One misquote caught by `python wiki.py check` while writing (Meli's disposition) and fixed. Then: 29
  pages, 0 problems, 0 warnings. No page verified yet.

## 2026-10-01 the remaining 65 opinions ingested

- Method: a workflow of nine agents read the 65 opinions in full (related opinions together) and wrote one
  JSON draft per case; each draft was checked by code before it was handed back (every quote word for word
  in its opinion). Topics were then settled by hand from the 77 names the agents proposed: synonyms merged
  (for example eviction or ejectment, contract for sale, contract for deed, lease or license, and transient
  occupancy into Whether there is a tenancy), procedural one-offs dropped. Pages were rendered by code from
  the drafts, with pins computed from the star pages and links added both ways. A second workflow wrote the
  27 new topic pages and extended 8 existing ones (six writers), and three reviewers read the prose of the
  65 new case pages and all 40 topic pages for anything that states the law, says which side a case
  favors, or is not supported by the opinion: 39 case-page lines and 12 topic-page lines reworded.
- Now: 81 case pages (every opinion in `cases/`) and 40 topics. 28 case pages have no section tag, each
  with a scope note: opinions decided under part I, before the 1973 Act, on commercial leases, in criminal
  or federal court, or on matters that are not landlord and tenant.
- Found while reading: many candidate-list entries are not residential landlord-tenant cases. Not landlord
  and tenant at all: Moritz (buying a lot), Prosperi (mechanic's lien), Kendall East (a house sale), Lefemine
  (buying a residence), Cupeiro (an aircraft lease), Purcell (contract for deed). Commercial leases:
  Berwick, Ralston, Bodden, Multach, Kaplan, Clark v. Hiett (638 acres for sod), Malt, Zhang, Colonial
  Promenade, John's Pass. Criminal: Morse, Wolf. Federal district court: Mann.
- Tags set by the court's own reading: Lockamy (only the dissent reads part II) and Wolf (the majority names
  part II only as the basis of counsel's instruction) have no tag.
- Questions for the author, from the writers and reviewers: Stephens-Williams cites 83.56(5)(a)(3) (2014)
  for the three-day notice, a number that falls in today's partial-rent sentences; whether to tag 83.45 on
  Exculpatory clauses in a lease, 83.505 on Three-day notice for nonpayment of rent, and 83.55 on Proximate
  cause of injuries on the premises; whether Mansur, Torres, Lockamy, and Smith should also name Landlord's
  notice of a dangerous condition; Salmonte (fees with no stated basis) under Prevailing party fees under
  83.48, and Solomon (83.42, 83.43) under Landlord's maintenance duties under 83.51; Crocker (51.011
  summary procedure) has no tag though today's 83.59 points to that procedure.
- `python wiki.py check`: 121 pages, 0 problems, 0 warnings. No page verified yet.

## 2026-10-01 the 2010 forms decision

- In re Revisions to Simplified Forms (2010) (50 So. 3d 503), from a Southern Reporter PDF: the opinion
  only; the appendix of forms is not stored (its changes are marked by formatting the text loses). Linked
  with Wilson v. Terwillinger, which cites it, and with the 1991 forms decision. Every opinion in `cases/`
  now has a page: 82.

## 2026-10-02 the facts the decisions turned on

- The chat now gives case pages to the model, which sets each case's facts beside the tenant's (TODO items 47
  and 48), so `SCHEMA.md`'s Facts rule changed from "A few quotes, as background." to the facts the decision
  turned on: the parties, the lease, notice, or property, what each side did and when, what was asked of the
  court; usually three to six quotes.
- Rewritten from the opinions: the Facts sections of the 20 tagged case pages with two quotes or fewer
  (Badaraco, Casey, Stein, Durene, Florida RS v. Nelson, Rowe, Gilbert, Grant, Guthartz v. Lewis, Haynes,
  Lewis v. Guthartz, Malagon, Meli, Moskowitz, Nardi, Olen v. Moss (984 So. 2d 558), Olszewska, Salmonte,
  Scruggs, Xanadu). Earlier bullets kept, most lengthened; prose labels inside two bullets dropped (Haynes,
  Moskowitz). Nothing outside the Facts sections changed. Not touched: the 1991 forms decision (a forms page,
  no dispute facts), the 30 tagged pages that already had three or more, and the untagged pages (never loaded
  for a tenant).
- Opinions that state few facts got the ones they state: Casey (a per curiam memorandum; no dates, roles only
  in the caption), Gilbert (two sentences), Moskowitz (the letter, and what the court did with it), Olen v.
  Moss (a challenge to the lease form, no tenant's own facts). Haynes: the time of day and the number of units
  appear only in the dissent and stay out of Facts. Xanadu: one bullet is the statute's effective date, which
  the decision compares with the agreement date.
- `python wiki.py check`: 122 pages, 0 problems, 0 warnings. No page verified yet.

