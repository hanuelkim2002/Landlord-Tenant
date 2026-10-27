# Plain replies: a short answer, the reasons one click away (design)

2026-10-27. Agreed in chat with the author; this writes it down.

## Why

A tenant without legal training finds the replies hard to read and too long. In 60 Sonnet answers to the deposit
stories, a reply runs about 450 words (330 to 575), with about 7 uses of "it". In one answer, three "it"s in the first
lines meant three things: the deposit (not yet named), the statute, and the landlord's company. A tenant who wants the
reasons should get them with a click on the same reply, not by asking again and waiting.

## What stays the same

- One model call per reply. No extra wait.
- The reply is stored whole in `events.jsonl`, and the model sees its own whole earlier replies.
- The quote check runs on the whole reply, and its box under the reply does not change.
- Rules 1 to 10 keep their numbers, so AUTHOR.md and SLIPS.md still point to the right rules.
- The skills do not change. The deposit skill's line "the first sentence says it is not settled" fits the short answer.

## What is new

**1. A rules block, "Writing the reply",** after rules 1 to 10, worded as approved:

    Writing the reply. The tenant has no legal training.
    1. Start with the short answer: 3 to 5 plain sentences that answer what was asked (rule 2), give the main
       reason, and say what it means for the tenant. Then the one question (rule 8). No section numbers or
       quotations here.
    2. Then a line with only DETAILS on it. Below it, put each point the answer rests on under its own heading: a
       line that starts with ### and asks a plain question, like ### Does Florida's deposit law cover you? The
       reasons, citations (rule 6), and quotations go there.
    3. Use short sentences and everyday words. Say what a legal word means the first time you use it.
    4. Use "it", "this", "that", or "they" only when it can mean just one thing, named in the same sentence or the
       one before. Otherwise name the thing again: "the deposit", "the law", "your landlord".

Rule 8 begins "End the short answer with the one question" instead of "End with the one question".

**2. The rules' word cap.** README's "under about 400 words in all" becomes "about 700 words in all" (the rules are
545 words today and about 700 with this block, right at the new cap). Trimming them is a later TODO.md item, if the
author wants it.

**3. `chat.split_reply(text)`.** It returns the short part and a list of (title, body) points.
- The marker is a line holding only DETAILS (bold marks or a colon around it allowed). "DETAILS" inside a sentence is
  not the marker.
- Each line starting with # under the marker starts a point (the rule asks for ###, but ## or #### count too); its
  title is the line without the # and bold marks.
- Text under the marker before the first heading, or with no heading at all, becomes a point titled "Why, and the
  law behind it".
- No marker: the whole reply is the short part and there are no points. Old chats show as they do now.

It sits in `chat.py`, next to the rules that set the format.

**4. The page.** For each reply, `app.py` shows the short part, then one click-to-open box per point, titled with its
question, then the quote check's box as now.

## Left out on purpose

A second model call to shorten the answer (adds a wait), a form-like answer tool (more code, stiffer writing), a
reading-level formula, a length counter on the page, and changes to the skills or the quote check. Each can come
back if the test shows it is needed.

## Size

About 20 new lines of app code (`chat.py`, `app.py`), from 831 to about 850.

## Testing

- `tests.py`, no model: headings become points with clean titles; DETAILS with no heading becomes one point titled
  "Why, and the law behind it"; text before the first heading goes in that point; no DETAILS gives the whole reply
  and no points; "DETAILS" inside a sentence is not the marker.
- A live test (`comparisons/plain/`): Sonnet 5.5 from Anthropic, today's deposit skill, the 18 deposit stories, 3
  runs each, once with today's rules (the baseline, saved as a file) and once with the new rules: 108 answers, about
  $7. It reuses the deposit test's runner and stories.
- Counted by code, per answer: whether it followed the format (a DETAILS line and at least one heading); the words in
  what the tenant sees first (today's rules: the whole reply; new rules: the short part); any section number or
  quotation in the short part.
- Graded by Opus subagents, as in the deposit test:
  1. Right, partly, or wrong against each story's key, on the whole reply, blind to the rules, with the deposit
     test's rubric and its settled stories.
  2. Plain reading, on what the tenant sees first (new rules: the short part and the box titles). This grade cannot
     be blind, since the format shows the rules, so every count quotes its words and Claude checks the counts. The
     grader's wording, for the author to approve before anything runs:

         You are reading what a tenant with no legal training sees first.
         1. Unclear words: list each "it", "its", "this", "that", "these", "those", "they", or "them" that could mean
            more than one thing, or that points to something not named in the same sentence or the one before.
            Quote the sentence and say what the word could mean.
         2. Legal words left unexplained: list each word or phrase a person without legal training would not know,
            like "forfeit", "setoff", or "periodic tenancy", that is not put in plain words where it first appears.
            Quote it.
         3. Does this part alone tell the tenant the answer to what they asked? Yes or no, with one line why.

- Done when: the format is followed in at least 52 of 54 new answers; the short part's median is 100 words or less;
  the median count of unclear words and of unexplained legal words is 0 per answer, and lower than under today's
  rules; and right answers are not fewer than under today's rules.
- Results as a chart, in `comparisons/plain/SCORES.md`, with a few answers for the author to try on the page. Model
  mistakes go in SLIPS.md.

## Docs

README.md (the new block and the cap), DOCUMENTATION.md (`split_reply`), CHANGELOG.md, AUTHOR.md (the decision),
TODO.md (trimming the rules, later).
