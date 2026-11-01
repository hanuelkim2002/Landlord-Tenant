# TODO

Work Claude can do, in order. Each item is at most three lines. Decisions and sign-offs are in AUTHOR.md; model
mistakes are in SLIPS.md.

## Now

- Three small fixes left out on the author's call (committed as it is, 2026-11-01): the neighbor skill's line on deciding before rent is due is
  wrong once rent has been paid; end-6's missing line on proper notice; a sentence for end-3's short answer. Each needs a rerun.

## Later

- `landlord_entered_unannounced` and `notice_received_nonpayment` wait: the plan for counting hours and holidays was
  dropped for now (AUTHOR.md, 2026-10-31).
- Once the deposit fixes are merged, `deposit_not_returned` loads `who_the_law_covers` instead of its own copy.
- Story 8's lease (`comparisons/skills/lease_email.txt`): have the e-mail addendum say the election is voluntary and
  can be revoked (83.505(1)), so the key holds; rerun story 8 on Sonnet (`comparisons/deposit/README.md`).
- Deposit skill: widen the no-lean line to any point the answer cannot settle (stories 9, 11, 18 leaned on Sonnet);
  rerun those three on Sonnet.
- Trim the rules toward their old length, if the author wants it (about 700 words since 2026-10-27).
