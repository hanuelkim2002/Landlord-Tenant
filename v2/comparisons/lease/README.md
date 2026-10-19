# Lease intake comparison

Which way of reading a lease should v2 use? This folder holds the test, its answer key, and (later) the scores, so
the chosen method can be checked again. The methods tested are in SHORTLIST.md.

## The test leases

| Lease | Pages | What it tests |
| --- | --- | --- |
| `leases/short_headings.pdf` | 2 | Short, plain headings with no numbers (a room in a house) |
| `leases/long_numbered.pdf` | 46 | Long, numbered sections and 17 addenda, answers buried deep, two tables (student housing) |
| `leases/scanned.pdf` | 4 | Page images only, no text, slightly tilted and speckled like a scan (a duplex) |
| `leases/broken_text.pdf` | 3 | Looks normal, but every PDF reader gets garbage, like the 57-page lease v1 failed on; the answers are in check boxes (an apartment form) |
| v1's `lease.pdf` | 12 | v1's sample lease (ARTICLE and 1.1 numbering). Kept out of git; read from `v2/lease.pdf` |

The new leases are made up. `python make_leases.py` builds them from the texts in `sources/` (it needs
`pip install pymupdf pypdf fpdf2 pillow`, and the Mac's Arial Unicode font for the check boxes).

## The answer key

`answer_key.json`: 64 questions, 10 to 15 per lease, in a tenant's words. 53 are answered by the lease (late fee,
pets, where notices go, repairs, deposit, guests, entry, and more) and 11 are not. For each question the key gives:

- the right answer in plain words;
- the **points** a right answer must make, judged by meaning, so any wording counts;
- the **mistakes** a reader could fall into (many questions have a near miss: a nearby clause that looks right but
  isn't, or an unchecked box);
- the lease's exact words that answer it, used only to check quotations.

`python check_key.py` confirms each passage is in its lease word for word, each number in a point is the lease's
number, and each "not covered" topic is truly absent.

## How a test run works

1. **Text out of the PDF** (no chat model). Each of PyPDF2, pypdf, pdfminer.six, and PyMuPDF reads every lease.
   Pages with no usable text are read from their images by Gemma 4 on the UF gateway. Scored against the words I
   wrote: how many come back right, how long it takes. The best reader's text is what step 2 uses.
2. **The three methods.** Each prototype answers every question with nemotron (`nemotron-3-super-120b-a12b`), giving
   the model the lease its own way (A, B, or C). Every prototype uses the same instruction for each question:

   > Answer the tenant's question from the lease only. If the lease does not address it, say so. Reply in JSON:
   > {"answer": "...", "quotes": ["..."]}. "quotes" are the lease's exact words your answer rests on.

   Each writes `results/<method>.jsonl`, one line per question: the reply, the seconds it took, and the tool calls.
   The methods shared one harness (the questions, the instruction, the tool loop, the clause splitter B and C used),
   so only the method differed. The prototype code was deleted after the choice; it is in git history at commit
   784dd82 (`v2/comparisons/lease/prototypes/`). It runs a tool call nemotron writes as text, and asks once
   more for an answer if the model is still calling tools after 8 rounds.
3. **v1's method, as a baseline.** v1's own lease code, run unedited from `v1/` (PyPDF2, the four-clause form by
   Gemma 4, and its exact-phrase `search_lease`), answers the same questions with nemotron and the same instruction,
   into `results/v1.jsonl`. It is scored exactly like the three methods, so the chart shows each one beside v1.

## How it is scored

The answer is judged by what it means, not how it is worded. Only quotations must match word for word.

**By meaning (a judge model).** A different model from the one tested, `gpt-oss-120b` on the UF gateway, so
nemotron never grades itself, reads each answer beside the key and the whole lease. It is told to judge meaning
only: a point counts in any wording, words in parentheses in a point are not required, and extra details are fine if
the lease supports them. For each answer it says:

- whether the answer says the lease does not address the question;
- which points the answer makes;
- which listed mistakes it makes, and any other claim that contradicts the lease.

Code turns that into the scores:

- **Right / partly / wrong.** Right: every point made, no mistake. Partly: some points, no mistake. Wrong: a
  mistake, or no point made.
- **Wrongly silent**: says the lease does not address a question it answers. The worst mistake.
- **Made up**: answers a question the lease does not address as if it did.
- **Never answered**: still calling tools when the rounds ran out.

I check the judge: I read every answer it marks wrong or partly, and a sample of the ones it marks right. Each grade
I change is in `review.json`, with why; the scores use my grades and show the judge's own count beside them.

**Word for word (code).**

- **Quotes check out**: every quote is word for word in the stored lease text. Spacing, line breaks, capitals, the
  kind of hyphen or quote mark, and a tool's label pasted in front ("Clause c14 (page 2):") are set aside; the words
  must match.
- **Quoted the right clause**: a quote comes from the passage that answers the question (8 words in a row from it,
  or a quote of 4 or more words wholly inside it).

**Time (code).** Two clocks, kept apart:

- **Intake time**: seconds from the uploaded PDF to the moment the method is ready for the first question, for each
  method and each lease. It counts everything the method does before a question: reading the PDF's text, reading
  page images where the text is missing (Gemma 4), and the method's own setup (B and C: splitting the lease into
  clauses and building the table of contents or the search index; v1: its four-clause form by Gemma 4 and the quote
  check). A, B, and C share step 1's text, so their intake time is step 1's time for that lease plus their own setup,
  both shown. Each intake is run three times and the middle time is reported, because the gateway's speed varies.
- **Answer time**: seconds per question, from asking to the final answer, tool calls included (typical and slowest).

Both are shown per lease, and the 46-page lease above all.

## The results

`SCORES.md` (the summary), `scores.json` (every answer and grade), `review.json` (my changes to the judge's grades),
`readers.json` (step 1). `python score_readers.py` reruns step 1; `python score.py` rescores the saved answers. To
check the chosen method again later, run v2's lease reading and chat on the same questions into `results/` and
rescore.

## The decision (2026-10-19)

The author chose method A: PyMuPDF for the text, Gemma 4 for pages without usable text, and the whole lease in the
system prompt. It scored 61 of 64 (v1: 35), was never wrongly silent, every quote checked out, and it was the
fastest and simplest. B scored 60 and C 57; the gap is within one run's noise, so speed and simplicity decided.

### Draft lease-reading rules for the system prompt (awaiting the author's OK)

1. THE LEASE below is the tenant's whole lease, page by page. Read all of it, addenda and tables included, before
   you say whether it covers a point.
2. Say the lease does not address a point only if no part of it does. If a clause comes close but does not settle
   the point, say what it does say.
3. Quote the lease's own words, and cite the section number, or the page when there is none.
4. (Optional, from a slip in this test.) A choice in the lease counts only if it is marked: a checked box, or
   initials on the line. An unchecked box or a blank initials line was not chosen.
5. (Optional, only if the author takes the first option in AUTHOR.md item 1.) A page marked "read from an image" may
   have misread marks. When your answer turns on a check box or a number on such a page, say so.
