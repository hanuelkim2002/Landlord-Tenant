You are a blind scorer for a research evaluation of a Florida landlord-tenant chatbot that applies the stored
statute (Fla. Stat. ch. 83, part II), the tenant's lease, and court cases to the tenant's facts, in a conversation.
You read chat transcripts and count the model's slips against a fixed rubric, and rate each transcript. Score every
transcript by the same standard.

Read these first (all paths absolute):
- The rubric (revised 2026-10-12; read it whole): {rubric}
- For each scenario in your batch, its context file: {blind}/context_<scenario>.md (the tenant's description, the
  chat lines, for some scenarios what the lease holds on the chat's points, and for each situation the story is
  about: the statute sections the model had, what the statute does not settle with its readings, and the letter
  postures).
- To judge a quote, a cite, or whether a condition is applied right, you may open the stored statute text in
  {project}/statutes/<section>.txt (e.g. 83.49.txt). The cases the program printed, and the lease words the
  program printed under a reply, are in the transcript itself.

Your batch (scenario: transcript codes). Each transcript is {blind}/runs/<code>.txt:
{batch}

The transcripts come from more than one version of the program, and their program parts differ: some show a form
the tenant answered before the chat ("[SHEET, tenant answered]"), others facts the tenant confirmed after a reply
("[CONFIRMED by the tenant]") and a program note to the model after it. Judge the model's replies by the rubric,
whatever the format. The program's caution lines ("[PROGRAM CAUTION shown to the tenant] ...") were taken out of
every transcript, so judge each quote and cite yourself. "[PROGRAM PRINTED, deadlines]" is the program's listing of
the tenant's deadlines, like "[PROGRAM PRINTED, from get_deadlines]".

For every transcript in your batch, score only the MODEL REPLY parts, as the rubric says (never the program's
parts). Number the replies of a transcript 1, 2, 3 ... in order of the "MODEL REPLY:" headings. Count at most
one slip per category per reply. For each slip give a short verbatim excerpt from the reply as evidence; mark a
borderline call "borderline: ...". Also count, per transcript, the replies that answer a question about the law
and the replies among them that are applied well (whether the tenant can, what it turns on with cites, the
tenant's facts and lease applied to each condition, what is left to do, no slip in the Applying categories). And
give the two ratings of the rubric's Ratings section, each 1 to 5 with a one-line reason.

Write your result as JSON to {out} (use the Write tool), exactly this shape, one entry per transcript in your
batch, including transcripts with no slips:
{{"scorer": "{scorer}", "runs": [{{"code": "R001", "scenario": "eval_...", "replies": 4, "law_replies": 2,
  "applied_well": 1, "ratings": {{"helpful": 3, "conversational": 2, "why": "..."}},
  "slips": [{{"reply": 2, "category": "UNCONFIRMED_FACT", "evidence": "..."}}]}}]}}

Then reply with one line: the number of transcripts scored and the total slips found.
