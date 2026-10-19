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
pets, where notices go, repairs, deposit, guests, entry, and more) and 11 are not. Each answered question lists the
lease's exact words that answer it and the facts the answer must contain. Many carry a near miss: a nearby clause
that looks right but isn't. `python check_key.py` confirms each passage is in its lease word for word and each
"not covered" topic is truly absent.

## How a test run works

1. **Text out of the PDF** (no chat model). Each of PyPDF2, pypdf, pdfminer.six, and PyMuPDF reads every lease.
   Pages with no usable text are read from their images by Gemma 4 on the UF gateway. Scored against the words I
   wrote: how many come back right, how long it takes. The best reader's text is what step 2 uses.
2. **The three methods.** Each prototype answers every question with nemotron (`nemotron-3-super-120b-a12b`), giving
   the model the lease its own way (A, B, or C). Every prototype uses the same instruction for each question:

   > Answer the tenant's question from the lease only. Reply in JSON: {"covered": true or false, "answer": "...",
   > "quotes": ["..."]}. "covered" is false only if the lease does not address the question. "quotes" are the lease's
   > exact words your answer rests on.

   Each writes `results/<method>.jsonl`, one line per question: the reply, the seconds it took, and the tool calls.

## How it is scored (by code)

- **Found it**: for an answered question, the model said covered and quoted the answering passage (at least 8 words
  in a row from it, or a quote of 4+ words wholly inside it).
- **Wrongly silent**: said "not covered" when the lease answers it. The worst mistake.
- **Made up**: said "covered" when the lease does not answer it.
- **Complete**: the answer has every must-say fact.
- **Quotes check out**: every quote is word for word in the stored lease text.
- **Time**: seconds to read each lease, and seconds per question (typical and slowest), on the long lease above all.

Right or wrong on a yes/no answer (for example "can I get a dog") is not scored by code; I list those answers for
you to read.
