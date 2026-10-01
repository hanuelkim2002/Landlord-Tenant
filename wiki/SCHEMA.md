# Case wiki schema

How the pages in this folder are built. Claude Code follows it when it adds or changes a page; the author
reads pages against it; `python wiki.py check` enforces the parts code can check. The pattern is Andrej
Karpathy's LLM wiki: the sources stay untouched (`cases/`, `statutes/`), the pages are written and kept up
by the LLM, and this file is the schema.

## Who does what

- Claude Code writes and updates pages in development sessions, from `cases/` and `statutes/` only, never
  from memory.
- The author reads each page against the opinion and signs off with
  `python wiki.py verify "<page>" "<name>"`. Any later edit to the page undoes the sign-off.
- Tenant sessions will read verified pages only, chosen in code by section tags, and never write here.

## Pages

- `cases/<Case name>.md`: one per opinion, named as the case is cited, e.g. `Durene v. Alcime`.
- `topics/<Topic>.md`: one per topic. A topic is made when a case raises it; there is no fixed list. Its
  name is a neutral noun phrase (`Landlord's notice of claim on the deposit`), never a rule
  (`Late notice forfeits the deposit`).
- `index.md`: built by `python wiki.py index`. Never edited by hand.
- `log.md`: one entry per ingest or change, newest last. Never rewritten.

## Front matter

Case pages:

- `kind: case`
- `cite`: as reported, e.g. `448 So. 2d 1208`; must be the cite of the file.
- `file`: the opinion in `cases/`, e.g. `448_So2d_1208.txt`.
- `court`: e.g. `Fla. 3d DCA`. `decided`: `YYYY-MM-DD`.
- `statute_read`: each section with the year the court read, as the court states it.
- `sections`: tags, the ch. 83 sections the opinion reads. Code loads pages by these. A tag the opinion
  never cites is a warning.
- `topics`: links to the topic pages the case speaks to.
- `verified_by`, `verified_on`, `verified_hash`: left empty; set by `verify`.

Topic pages: `kind: topic`, `sections` (tags; empty for a topic no section speaks to, such as procedure),
and the three verified fields.

## Quotes

The court's and the statute's words appear only as quotes followed by their source, in straight double
quotes:

- `"words" (at 1210)`: this case page's own opinion, starting on page 1210.
- `"words" ([[Plakhov v. Serova]] at 1223)`: another case page's opinion.
- `"words" (Fla. Stat. 83.49(3)(a))`: the stored statute, in that subsection.

Word for word from the source; an ellipsis may join pieces. The pin page is the page the words start on.
Quote marks inside a quote stay as the opinion prints them (curly). Straight double quotes are used for
nothing else.

## Prose

The prose describes and connects: what a case is about, its court and posture, the facts as background,
and which cases it relates to and how (cites, follows, distinguishes, disagrees with, quotes, reads an
older version of the statute). It never states what the law is, never says what a case held except by
quoting it, never says which side a case favors, and never says whether it applies to anyone. Issues are
written as questions.

## A case page

    # <Case name>
    One or two lines: court, posture, who appealed.

    ## Facts
    A few quotes, as background.

    ## <An issue the court decided, as a question>      (one section per issue)
    Topic: [[...]]                                    (when one fits)
    Rule:        quotes
    Reasoning:   quotes, or "none stated" when the court gave none
    Dissent:     quotes, when there is one

    ## Statute read
    The court's own quote of the statute, when it gives one.

    ## Related
    Links to other case pages and how they relate, with quotes. Cases with no page yet are named in plain
    text with their cite.

    ## Disposition
    A quote.

## A topic page

    # <Topic>
    One or two lines on what the topic covers.
    Today's stored text, quoted, when a section speaks to it.

    ## Cases
    Every case page that names the topic: court, year, the statute year it read, and its issue as a question.

    ## How they relate
    Agreements, distinctions, tensions, and changes in the statute's wording, with quotes.

## Adding a case (ingest)

1. Read the opinion in `cases/` in full.
2. Write its case page.
3. For each issue, link a topic page that fits or make a new one; list the case on every topic page it
   names, and update How they relate.
4. Link related case pages both ways.
5. `python wiki.py index`, then `python wiki.py check`: fix every problem.
6. Add an entry to `log.md`.

## Checking (lint)

By code (`python wiki.py check`), problems: a quote not word for word in its source or not on the page it
cites, a quote with no source, a link to no page, a case not listed on a topic page it names, a missing
front matter field, a tag not in `statutes/`, a cite that is not its file's, a case page with no Rule or
Reasoning line, an index out of date. Warnings: a section tag the opinion never cites, a page changed
since it was verified.

By reading (Claude Code, when asked): a case missing from a topic, a topic to split or merge, a case that
read an older version of the statute or another part of ch. 83, a tension between cases not yet recorded,
prose that slips into stating the law.
