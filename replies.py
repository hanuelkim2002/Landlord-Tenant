"""Replies: what the program checks and prints under each reply the model writes. The words a reply cites, printed
from the stored statute and the lease; cautions for a cite or a quote that fails its check, and for a printed case no
reply discusses; the line saying the answer is the tool's reading. The reply itself is never changed, and the model
is not told. Split out of agent.py on 2026-10-06, as it was.
"""
import re

import record
import wiki
from citations import (caution, check_case_cites, check_cites, check_quoted, cites_in, is_in, quote_label, quote_spans,
                       quoted_passages, subsections, unbracketed, unquoted)
from config import shorten
from corpus import statute
from lease import LABELS, SECTION_NUMBER, lease_cite, lease_clauses
from prompt import system_prompt
from record import active_playbooks, append_event, read_events


# ---- What the model had: the sections it could cite, and everything it was given, for the cite and quote checks.

def sections_shown(messages):
    """The sections the model could cite from: THE STATUTE in its prompt (the active playbooks' sections) plus every
    section it fetched with get_statute_section in this chat's thread."""
    fetched = {c["args"].get("section") for m in messages if m.type == "ai"
               for c in m.tool_calls if c["name"] == "get_statute_section"}
    return {s for pb in active_playbooks() for s in pb.sections} | fetched


def given_text(messages):
    """Everything the model was given, as one string, for citations.check_quoted: the system prompt, the lease
    quotes as plain text (the prompt holds them as JSON, with quote marks escaped), the tenant's description
    and updates, and every message in the thread the model did not write (the tenant's messages, program
    notes, tool results)."""
    lease_quotes = [c.quote or "" for _, c in record.profile.clauses()] if record.profile else []
    updates = [ev["text"] for ev in read_events() if ev["kind"] == "tenant_update"]
    thread = [str(m.content) for m in messages if m.type != "ai"]
    return "\n".join([system_prompt(messages), record.matter.get("description", ""), *lease_quotes, *updates, *thread])


# ---- Cases in a reply (TODO item 57). In the eval of 2026-10-02 every mold-story answer left out the three
# printed cases that went for the landlord, and one credited a case's words to another case. Code can see both:
# which printed cases a reply names, and which printed case's text holds a quote.

CASES_LEFT_OUT = ("[Check: the program printed cases above that this reply does not discuss: {}. Read them too "
                  "before relying on the reply.]")


def named_cases(text, names):
    """Where the text names each of these cases: [(start, end, name)]. A case is named by its short name
    ("Bennett v. Mattison") or its first party's name alone ("Bennett"; "Olen Properties Corp." for Olen
    Properties Corp. v. Moss (984 So. 2d 558)). A name inside a longer one is the longer one's: "Bennett" in
    "Bennett M. Lifter" names Bennett M. Lifter, Inc. v. Varnado, and "Lewis" in "Guthartz v. Lewis" names no
    Lewis case."""
    found = []
    for name in names:
        plain = name.split(" (")[0]
        first, _, second = plain.partition(" v. ")
        first = first.split(",")[0]
        forms = sorted({plain, first} | ({f"{first} v. {second.split(',')[0]}"} if second else set()), key=len, reverse=True)
        pattern = r"(?<!\w)(?:" + "|".join(re.escape(f) for f in forms) + r")(?!\w)"
        found += [(m.start(), m.end(), name) for m in re.finditer(pattern, text)]
    return [n for n in found if not any(o[0] <= n[0] and n[1] <= o[1] and o[1] - o[0] > n[1] - n[0] for o in found)]


def printed_cases(messages):
    """Each case a get_cases result in these messages printed, with its own part of the printed text:
    [(name, part)], in order (wiki.cases_printed)."""
    found = []
    for m in messages:
        printed = getattr(m, "artifact", None) if m.type == "tool" and m.name == "get_cases" else None
        heads = wiki.cases_printed(printed) if printed else []
        ends = [start for _, start in heads[1:]] + [len(printed or "")]
        found += [(name, printed[start:end]) for (name, start), end in zip(heads, ends)]
    return found


def cases_left_out(new):
    """The cases get_cases printed in a turn's new messages that no reply after the printing names, by name;
    empty when nothing was printed or no reply followed."""
    first = next((i for i, m in enumerate(new) if printed_cases([m])), None)
    replies = "\n".join(m.content for m in new[first:] if m.type == "ai") if first is not None else ""
    printed = [name for name, _ in printed_cases(new)]
    named = {name for _, _, name in named_cases(replies, printed)}
    return [name for name in printed if replies.strip() and name not in named]


def check_case_quotes(text, messages):
    """Each quote in a reply credited to a printed case whose part does not hold it while another case's part
    does: [(quote, case, problem)]. A quote is credited to the printed case the reply names last before it in
    the same paragraph (none when two cases are named at that same place). Words a statute section also holds are
    left to check_quoted."""
    cases = printed_cases(messages)
    problems = []
    for start, _, quote in quote_spans(text):
        words = unbracketed(quote)                       # "[t]he tenant": the brackets are the quoter's alteration
        holding = [name for name, part in cases if is_in(words, part)]
        if not holding or any(is_in(words, section) for section in statute.values()):
            continue
        paragraph = text[max(0, text.rfind("\n\n", 0, start)):start]
        named = named_cases(paragraph, [name for name, _ in cases])
        last = max((start for start, _, _ in named), default=None)
        at_last = {name for start, _, name in named if start == last}
        credited = at_last.pop() if len(at_last) == 1 else None
        if credited and credited not in holding:
            problems.append((quote, credited, f"is in {holding[0]}'s text, not {credited}'s"))
    return problems


# ---- The words a reply cites (TODO item 73, the author's decision of 2026-10-04): the model gives each rule in a
# plain sentence with its cite, and the program prints the cited words under the reply, from statutes/ and the lease
# profile, so the tenant has the exact text to point to and the reply does not recite it. Was, from item 54 to 66:
# every rule quoted in the reply, and a caution for a section cited without a quote (item 66's RETOLD).

# a lease cite as YOUR LEASE gives it (lease.lease_cite): "Lease Section 4.3", "Lease Article 7", "Lease, page 1", with any
# space between the words: the model wrote "Lease Section\u202f7.2", a narrow no-break space, and the program printed
# nothing under the reply (eval of 2026-10-04, TODO item 85)
LEASE_CITE = re.compile(r"\bLease\s+(?:Section|Article|Paragraph)\s+(\d+(?:\.\d+)*)|\bLease,?\s+page\s+(\d+)", re.I)
CITED_MAX = 1500                                         # characters of one passage printed; the rest is named
CITED_HEAD = "The words the reply above cites, printed by the program from the stored statute and your lease:"


def cited_clause(clause, number, page):
    """The clause is the one a lease cite names: its number is the cited one or holds it (Article 7 for "Lease
    Section 7.2"), or, for a page cite, it has no number and is on that page."""
    found = SECTION_NUMBER.match(clause.section or "")
    if number:
        return bool(found) and (number == found.group(2) or number.startswith(found.group(2) + "."))
    return not found and str(clause.page) == page


def cited_words(text):
    """The statute and lease words a reply cites, as the text of a block, or "" when it cites none: for each ch. 83
    cite outside quote marks that the stored statutes hold, the subsection's words (or the section's), the
    narrowest once (83.56(1) cited, 83.56 alone adds nothing), cut at CITED_MAX characters with the cite for the
    rest; then each lease clause the profile holds under a lease cite (LEASE_CITE): a numbered one, or one inside it
    ("Lease Section 7.2" in "Lease Article 7"), or, for "Lease, page 1", the clauses on that page with no number;
    each with its cite, page, and label; and for a numbered cite the profile holds no clause for, the clause of that
    number in the lease's text (lease.lease_clauses), or each clause of a cited article, as search_lease finds them
    (TODO item 82), with its title."""
    parts = []
    cites = [c for c in cites_in(unquoted(text)) if c.partition("(")[0] in statute
             and (not c.partition("(")[2] or "(" + c.partition("(")[2] in subsections(c.partition("(")[0]))]
    for cite in [c for c in cites if not any(o != c and o.startswith(c) for o in cites)]:
        section, _, rest = cite.partition("(")
        words = statute[section][slice(*subsections(section)["(" + rest])] if rest else statute[section]
        words = shorten(" ".join(words.split()).split(" History. —")[0], CITED_MAX, f"(the rest is in Fla. Stat. {cite})")
        parts.append(f"Fla. Stat. {cite}: {words}")
    clauses = [(n, c) for n, c in record.profile.clauses() if c.present and c.quote] if record.profile else []
    numbered = None                                      # the lease text's own clauses, read once if needed
    for number, page in dict.fromkeys(LEASE_CITE.findall(text)):
        held = {c.quote: (n, c) for n, c in clauses if cited_clause(c, number, page)}
        for quote, (name, clause) in held.items():
            cite = lease_cite(clause)
            where = cite if cite.startswith("Lease, page") else f"{cite}, page {clause.page}"
            parts.append(f"{where} ({LABELS[name]}): {' '.join(quote.split())}")
        if number and not held:                          # a clause the profile does not hold, found in the lease text
            numbered = lease_clauses(record.lease_pages()) if numbered is None else numbered
            for c in [c for c in numbered if c["number"] == number or c["number"].startswith(number + ".")]:
                words = shorten(c["text"], CITED_MAX, f"(the rest is in Lease Section {c['number']})")
                parts.append(f"Lease Section {c['number']}, page {c['page']} ({c['title']}): {words}")
    return CITED_HEAD + "\n\n" + "\n\n".join(parts) if parts else ""


def check_reply(text, messages):
    """Check the cites and the quotes in one reply (citations.check_cites and check_quoted, and check_case_quotes
    for a quote credited to a printed case), against the chat's thread so far. Each one that fails gets a caution
    line, shown under the reply, a line in the transcript, and a cite_flagged or quote_flagged event. Returns the
    caution lines. The reply itself is not changed. A section cited without a quote is no longer cautioned
    (TODO item 73): the program prints its words (cited_words)."""
    flagged = []
    given = given_text(messages)                         # built once: it holds the whole system prompt
    for cite, problem in check_cites(text, sections_shown(messages)):
        flagged.append((caution(cite, problem), "cite_flagged", {"cite": cite, "problem": problem}))
    for cite, problem in check_case_cites(text, given):
        flagged.append((caution(cite, problem), "cite_flagged", {"cite": cite, "problem": problem}))
    for quote, cite, problem in check_quoted(text, given) + check_case_quotes(text, messages):
        flagged.append((caution(quote_label(quote, cite), problem), "quote_flagged",
                        {"quote": quote, "cite": cite, "problem": problem}))
    for line, kind, data in flagged:
        record.append_transcript({"role": "check", "text": line})
        append_event(kind, **data)
    return [line for line, _, _ in flagged]


# A reply that quotes the statute or the lease is the tool applying the law, so the program prints its own line
# under it: the answer is the tool's reading, not a lawyer's advice (README, Purpose). The model is told not to
# write one. Was NOT_DECIDED, "This tool does not decide whether any of this applies to you." (TODO item 30),
# from when the tool only set the law beside the facts.
READING_LINE = "This is the tool's reading of the stored law and your confirmed facts, not a lawyer's advice."
# A reply the gateway stopped at the length limit reads as if it were whole; the tenant is told it is not.
CUT_OFF = "[Check: this reply was cut off at the model's length limit. Ask again for the rest.]"


def reading_line(text):
    """READING_LINE if the reply cites or quotes the statute (a ch. 83 cite, or a quoted passage with one) or the
    lease (a lease section cited, or a quoted passage found in a lease profile quote) and does not already carry
    the line; else None. Citing counts since TODO item 73, when the reply stopped quoting."""
    lease = [c.quote for _, c in record.profile.clauses() if c.present and c.quote] if record.profile else []
    quotes_source = any(cite.startswith("83.") or any(is_in(quote, q) for q in lease)
                        for quote, cite in quoted_passages(text))
    cites_source = bool(cites_in(unquoted(text)) or LEASE_CITE.search(text))
    return READING_LINE if (quotes_source or cites_source) and READING_LINE not in text else None
