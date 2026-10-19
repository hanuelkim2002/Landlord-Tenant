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
3. **v1's method, as a baseline.** v1's own lease code, run unedited from `v1/` (PyPDF2, the four-clause form by
   Gemma 4, and its exact-phrase `search_lease`), answers the same questions with nemotron and the same instruction,
   into `results/v1.jsonl`. It is scored exactly like the three methods, so the chart shows each one beside v1.

## How it is scored

The answer is judged by what it means, not how it is worded. Only quotations must match word for word.

**By meaning (a judge model).** A different model from the one tested, `gpt-oss-120b` on the UF gateway, so
nemotron never grades itself, reads each answer beside the key. It is told to judge meaning only: a point counts in
any wording, and extra details are fine if the lease supports them. For each answer it says:

- whether the answer says the lease does not address the question;
- which points the answer makes;
- which listed mistakes it makes, and any other claim that contradicts the lease.

Code turns that into the scores:

- **Right / partly / wrong.** Right: every point made, no mistake. Partly: some points, no mistake. Wrong: a
  mistake, or no point made.
- **Wrongly silent**: says the lease does not address a question it answers. The worst mistake.
- **Made up**: answers a question the lease does not address as if it did.

I check the judge: I read every answer it marks wrong or partly, and a sample of the ones it marks right, and tell
you how many I would change.

**Word for word (code).**

- **Quotes check out**: every quote is word for word in the stored lease text (spacing and line breaks aside).
- **Quoted the right clause**: a quote comes from the passage that answers the question (8 words in a row from it,
  or a quote of 4 or more words wholly inside it).

**Time.** Seconds to read each lease, and seconds per question (typical and slowest), on the long lease above all.
