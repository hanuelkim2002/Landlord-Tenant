# Lease intake: the shortlist

Reading a lease has two steps, and they are tested apart so each answer is clear.

1. **Getting the text out of the PDF.** No chat model is involved, so code scores it alone: how close each reader's
   text is to the words I wrote, how fast it is, and whether it notices a PDF it cannot read.
2. **How the chat model uses the text.** This is where the three methods differ. All three get the same text from
   step 1 and use the same model, nemotron, so the method is the only difference.

## Step 1: the PDF readers (scored by code, no agents)

All four readers are tried on every test lease: PyPDF2 (v1's), pypdf, pdfminer.six, PyMuPDF.

- PyPDF2 is retired; its maintainer moved the work to pypdf ([pypdf history][pypdf]).
- A study of 10 readers on 6 kinds of documents found PyMuPDF and pypdfium best at plain text, with pypdf and
  pdfminer behind ([Adhikari and Agarwal 2024][parsers]). Another found PyMuPDF about 10 times faster than pypdf
  ([2026 URL study][urls]).
- PyMuPDF's license is AGPL. That is fine for a tool on this computer. It matters only if the tool is ever offered to
  others as a service, which waits on the unlicensed-practice question anyway.

**Scans and broken PDFs.** Nemotron reads text only ([NVIDIA model card][nemotron]). So a page with no usable text
must be turned into text first. Two ways: a vision model on the UF gateway reads the page image (Gemma 4 31B takes
images, per [UF's model page][gemma]), or OCR software (Tesseract) does. Vision models beat Tesseract on messy scans
in most published tests, but can "rewrite" instead of copy, which matters for quotes ([olmOCR][olmocr],
[transcription faithfulness][faithful]). I will test Gemma 4 only, because it needs nothing installed. Tesseract
needs a program installed on your Mac; I can add it if you want.

## Step 2: the three methods (one agent each)

### A. The whole lease in the prompt

Every turn, the model gets the full lease text, with page and section markers.

- Why it is promising: nemotron takes 262,144 tokens on the UF gateway ([UF][ufnemotron]). A 57-page lease is about
  40,000 tokens, so it fits. A large study found that when the whole text fits, giving it all beat search-based
  methods on average ([Li et al. 2024][lc]). Nothing can be missed by a bad search, so "the lease is silent" should
  only happen when it is.
- The risk: models miss facts in the middle of a long text ([Liu et al. 2024][middle]), and get worse as the text
  grows and holds look-alike passages ([Chroma 2025][rot]). A long lease is full of look-alikes (a late fee in the
  rent section and another in a fee table). Each turn also sends the whole lease, which may be slow.
- Quote check: a lease quote must be in the stored text, word for word.

### B. A table of contents, and a tool to read a clause

Code splits the lease into clauses at its headings (numbered or not). The prompt holds only the list of clause
titles; the model calls `read_clause` to read one, or a few.

- Why it is promising: this is how a person reads a lease, and how tools like PageIndex search long legal and
  financial papers ([PageIndex][pageindex]). Anthropic's advice for agents is the same idea: keep short pointers in
  the prompt and load the text when needed ([Anthropic][context]). The prompt stays short, and every quote comes
  from one known clause, so it is easy to check and to print under the reply.
- The risk: a point filed under an unhelpful heading (pets inside "Miscellaneous") may never be opened, and the
  splitter has to handle unnumbered headings, tables, and odd lines (v1's sample lease has a line that starts with
  "22.1." in the middle of a clause).
- Quote check: in the clause it came from, or anywhere in the stored text.

### C. A ranked word search over clauses (v1's search, improved)

The same clauses as B, but no table of contents. The model calls `search_lease` with words, and gets back the
best-matching whole clauses, ranked (BM25, a standard word-search score).

- Why it is in the list: it is v1's method with its weakest part fixed. v1 found only the exact phrase typed, and
  returned up to five clauses in the lease's order, not the best matches first. Word search finds exact terms like "late charge" well, which is why Anthropic adds it next to
  meaning-based search ([Contextual Retrieval][contextual]). It also shows whether v1's "the lease is silent"
  mistakes came from the search or from the model.
- The risk: legal search is hard; the right clause often uses other words than the question ([LegalBench-RAG][lbrag]).
  A tenant asks "can I have a cat"; the lease says "animal".
- Quote check: as in B.

## Left off the list, and why

- **A model summary of key clauses** (v1's four-clause extraction). It was v1's slow step (about four minutes for 57
  pages), it covers only the clauses chosen in advance, and a summary is not the lease's words, so it cannot be
  checked word for word.
- **The chat model reading page images.** Nemotron cannot read images. Page images are used only in step 1, to turn
  a scan into text.
- **Whole lease, with search as a fallback** ("Self-Route", [Li et al. 2024][lc]). Worth trying later if A wins but
  is too slow.

[pypdf]: https://pypdf.readthedocs.io/en/6.18.0/_sources/meta/history.md.txt
[parsers]: https://arxiv.org/abs/2410.09871v2
[urls]: https://arxiv.org/pdf/2609.08019
[nemotron]: https://build.nvidia.com/nvidia/nemotron-3-super-120b-a12b/modelcard
[ufnemotron]: https://docs.ai.it.ufl.edu/docs/navigator_models/models/nvidia-nemotron-3-super-120b-a12b
[gemma]: https://docs.ai.it.ufl.edu/docs/navigator_models/models/gemma-4-31b-it
[olmocr]: https://arxiv.org/pdf/2502.18443v3
[faithful]: https://arxiv.org/pdf/2607.21617
[lc]: https://arxiv.org/abs/2407.16833v1
[middle]: https://aclanthology.org/2024.tacl-1.9/
[rot]: https://trychroma.com/research/context-rot
[pageindex]: https://pypi.org/project/PageIndex/
[context]: https://agentic-ai.readthedocs.io/en/latest/ContextEngineering/anthropic/
[contextual]: https://anthropic.com/news/contextual-retrieval
[lbrag]: https://arxiv.org/abs/2408.10343v1
