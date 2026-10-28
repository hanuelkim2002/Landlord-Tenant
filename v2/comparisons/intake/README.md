# Intake speed test

Can the lease be read faster before the first answer, and still read every word and check box? Today the app reads
one page at a time from its picture with Haiku 5.5 from Anthropic, about 5 seconds a page, so a 32-page lease waits
about 3 minutes (TODO.md). The ways tried, each through the app's own `lease.read_image`:

- **Now:** one page at a time, pictures at 200 dpi (the app as it is).
- **Several pages at once:** 4, 8, and 16 at a time, 200 dpi.
- **Smaller pictures:** 8 at once, at 150 and at 100 dpi.
- **v1, as a baseline:** the PDF's own text (PyPDF2), then Gemma on UF copies four clauses (`v1_intake.py`, v1's
  code run unedited, in its own Python since v1 and v2 both have modules named `config` and `lease`).

Ideas not tried, and why: the PDF's own text for plain pages (reopens the 2026-10-21 decision; the text lost typed-in
values and boxes), the PDF handed straight to the chat (no lease text for the quote checker, and each message would
cost more), a different reader (Haiku was the fastest one that read every box in `comparisons/models/`), several
pages in one request (the model still writes them one after another). Two ideas that hide the wait rather than
shorten it are left for later: reading while the tenant types, and showing the first answer as it is written.

The leases are the lease test's samples (`comparisons/lease/leases/`): the 46-page `long_numbered` (the one timed),
the 3-page `broken_text` with 35 check boxes, and the 4-page `scanned`. Each way reads each lease 3 times; each run
goes through every way in turn, so a slow spell at Anthropic hits them all, with 10 seconds between readings. Words
and check boxes are scored with the model test's scorer (`comparisons/models/score.py`) against the sample sources.

- `python speed.py`: read and score, into `results/runs.jsonl`, `results/scores.json`, and `SCORES.md`. A reading
  already in the file is skipped, so a stopped run picks up where it was. `--dry`: a fake reader, nothing sent.
  `--score`: score only. v1 runs only when `V1_PYTHON` names a Python with v1's packages.

## Results (2026-10-27)

Three runs, 159 page readings per way, no page failed or was sent again (`SCORES.md`, `scores.json`).

- **Pages at once is the whole gain.** The 46-page lease: 132 seconds one at a time, 34 with 4 at once, 18 with 8,
  10 with 16. Each page still takes about 3 seconds; they just overlap. Anthropic turned no page away, even at 16.
- **Nothing is lost.** Every way that reads the pictures read 100% of the words on all three leases and all 35 check
  boxes, in every run.
- **Smaller pictures save money, not time.** 150 and 100 dpi send 2,793 and 1,319 tokens a page against 4,837 at
  200, but the wait is the same (17 seconds against 18 at 8 at once): the time goes into writing the text out. Not
  tried on the author's own lease, a real filled-in form, so 200 stays.
- **v1** took under half a second, but only its first step ran: UF's key expired on 2026-10-24, so Gemma's step
  failed and is not timed. Its text read every word of the clean 46-page lease, almost none of the broken one (0.5%)
  or the scan (0%), and none of the 35 boxes.
- One page at a time took about 3 seconds a page here, against 5.3 in `comparisons/models/` through OpenRouter, so
  today's app reads a 32-page lease in about 1.5 minutes, not the 2 to 3 in TODO.md.

Not measured: a lease read while other tenants' leases are read (the limits are per account), and the first answer,
about 20 seconds, which comes after the reading in every way.
