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
