"""Citations: find the statute cites and the quotes in a reply the model wrote and check them against the
stored statutes and what the model was given.

Nothing here calls a model or writes to a matter. The chat loop (replies.check_reply) runs check_cites and
check_quoted on every reply and prints a caution for each one that fails; the reply itself is still shown.
"""
import re

from corpus import statute


# ---- Subsections: where each "(3)" and "(3)(a)" starts and ends inside a section's text.
# A section is one long line, so a subsection is found by its marker. A marker starts a subsection when it is
# followed by a space and a capital letter or an opening quote ("(3) The landlord", "(1) “Active duty”"),
# or by a lettered marker first ("(5)(a) If"). Cross-references are not starts: "subsection (3) may",
# "s. 83.51 (1), or". Checked on every stored section by smoke.py: numbers run 1, 2, 3 and letters a, b, c.

SUBSECTION_START = re.compile(r"(?<!subsection )(?<!paragraph )(?<!subparagraph )"
                              r"\((\d+|[a-z])\)(?=(?:\([a-z]\))? [A-Z“\"])")


def subsections(section):
    """Every subsection of one stored section, as {"(3)": (start, end), "(3)(a)": (start, end), ...}: character
    positions in statute[section]. A numbered one runs to the next number; a lettered one to the next marker."""
    text = statute[section]
    starts = [(m.start(), m.group(1)) for m in SUBSECTION_START.finditer(text)]
    found = {}
    number = ""
    for i, (pos, mark) in enumerate(starts):
        if mark.isdigit():
            number = f"({mark})"
            later = [p for p, m in starts[i + 1:] if m.isdigit()]     # a number ends at the next number
            found[number] = (pos, later[0] if later else len(text))
        else:                                                        # a letter ends at the next marker of any kind
            end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            found[number + f"({mark})"] = (pos, end)
    return found


# ---- Cites in a reply: "83.49", "83.49(3)(a)", "Fla. Stat. 83.51 (1)". Only ch. 83 is recognized.

CITE = re.compile(r"\b83\.\d+(?:\s?\((?:\d+|[a-z])\))*")


def cites_in(text):
    """Every ch. 83 cite in the text, spaces removed (a no-break space too, which the model sometimes writes), in
    order, each once: ["83.49(3)(a)", "83.56"]."""
    found = []
    for m in CITE.finditer(text):
        cite = "".join(m.group(0).split())
        if cite not in found:
            found.append(cite)
    return found


def check_cites(text, shown):
    """Check each cite in a reply. shown: the sections the model had in this turn (THE STATUTE in its prompt plus any
    it fetched with get_statute_section). Returns [(cite, problem)], empty when every cite passes:
    - the section is not in the stored statutes;
    - it was not shown or fetched (rule 2: fetch a section before mentioning it);
    - the section has no such subsection.
    Cites inside a quoted passage are skipped: they are the quoted text's own ("in accordance with s. 83.505"
    inside a quote of 83.49), and check_quoted checks those words against their source."""
    problems = []
    for cite in cites_in(unquoted(text)):
        section, _, rest = cite.partition("(")
        if section not in statute:
            problems.append((cite, "is not a section in this tool's copy of ch. 83 part II"))
        elif section not in shown:
            problems.append((cite, "was not among the sections this chat loaded or looked up"))
        elif rest and "(" + rest not in subsections(section):
            problems.append((cite, f"names a subsection that {section} does not have"))
    return problems


# ---- Quotes in a reply: each passage in quote marks, 20 characters or more (the length check_skill uses
# for quotations in prose), with the ch. 83 cite next to it if there is one. The model writes a cite either
# after the quote on the same line ("..." (83.49(3)(a))) or in a heading just before it
# (**Statute quote (Fla. Stat. 83.49(3)(b)):** "...").

# Quote marks pair in order, as a reader pairs them: a straight mark opens, the next one closes (curly marks
# pair by their shape), and a quote may run over lines. A short quote ("assert,") still takes its two marks;
# it is only left out of the passages checked. Was: a pattern needing 20 characters inside skipped a short
# quote and paired its closing mark with the next quote's opening one, so the words between two quotes were
# checked as a quote (three false cautions in one reply, eval of 2026-10-01), and a quote running over two
# lines did the same.
QUOTE_PAIR = re.compile(r'"([^"]*)"|“([^”]*)”')
MIN_QUOTE = 20


def quote_spans(text):
    """Every quoted passage of MIN_QUOTE characters or more: [(start, end, words)], marks paired in order."""
    spans = []
    for m in QUOTE_PAIR.finditer(text):
        words = m.group(1) if m.group(1) is not None else m.group(2)
        if len(words) >= MIN_QUOTE:
            spans.append((m.start(), m.end(), words))
    return spans


def unquoted(text):
    """The text with each quoted passage (quote_spans) blanked out."""
    for start, end, _ in reversed(quote_spans(text)):
        text = text[:start] + " " + text[end:]
    return text


FIELD_ID = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)+")      # a fact or clock id: "claim_notice_deadline"
EXAMPLE = re.compile(r"\be\.g\.,?\s*$", re.I)           # the model's own example follows: e.g., "..."


def quoted_passages(text):
    """Every quoted passage in a reply with the cite next to it, or "" when none: [(quote, cite)]. The cite is
    the first one after the closing quote mark on the same line, or else the last one in the 80 characters
    before the opening mark. A cite already used after one quote is never taken again for the next.
    Two things in quote marks are not quotes and are left out (TODO item 14, seen 2026-09-30): an id alone
    ("claim_notice_deadline"), and an example right after "e.g." (e.g., "repair the air-conditioning unit")."""
    found = []
    used_up_to = 0                                   # nothing before this point can be the next quote's cite
    for start, end, quote in quote_spans(text):
        if FIELD_ID.fullmatch(quote.strip()) or EXAMPLE.search(text[max(0, start - 12):start]):
            continue
        after = CITE.search(text[end:end + 60].split("\n")[0])
        window = text[max(used_up_to, start - 80):start]
        # a cite before the quote counts only with no quote mark between them: in a tool result the model
        # repeats ("cite": "83.56(3)", "counting": "..."), the cite belongs to another field
        before = [c for c in CITE.finditer(window) if not re.search(r'["“”]', window[c.end():])]
        if after:
            cite = after.group(0)
            used_up_to = end + after.end()
        else:
            cite = before[-1].group(0) if before else ""
            used_up_to = end
        found.append((quote, cite.replace(" ", "")))
    return found


TYPOGRAPHY = str.maketrans({"’": None, "‘": None, "“": None, "”": None, "'": None, '"': None,
                            "‑": "-", "‐": "-", "–": "-", "—": "-"})


def compact(text):
    """Lowercase, quote marks and apostrophes left out, dash variants made plain, all whitespace removed. Looser
    than squash on purpose: the model writes "tenant's" for the statute's "tenant’s", and "confirmation" for the
    lease PDF's "confir mation". Neither is a misquote. Nor is a quote inside a quote whose marks the model
    changed, ‘Reasonable notice’ for the statute's “Reasonable notice” (TODO item 58: until then curly marks were
    made straight but kept, so single and double inner marks differed, 15 false cautions in the eval of
    2026-10-03), or the tool's own words the prompt holds as YAML, which doubles an apostrophe ("neighbor''s")."""
    return "".join(text.translate(TYPOGRAPHY).lower().split())


def is_in(quote, text):
    """The quote appears in the text, compared with compact. An ellipsis ("..." or "…") splits the quote into
    pieces that must each appear. Punctuation at either end of a piece is left out: the model closes a quote
    with a period where the source goes on ("July 31, 2026." for "July 31, 2026 and I moved out")."""
    pieces = [p.strip(" .,;:") for p in re.split(r"\.\.\.|…", quote)]
    pieces = [p for p in pieces if p]
    return bool(pieces) and all(compact(p) in compact(text) for p in pieces)


# An alteration a legal quotation marks in square brackets: "[t]he tenant", "upon [the tenant's] security deposit",
# "specif[y] the noncompliance". In the nemotron evals of 2026-10-04 and 2026-10-08, 7 of 36 quote cautions were such
# quotes, every one word for word once its brackets were set aside.
BRACKET = re.compile(r"\[[^\]]*\]")


def unbracketed(quote):
    """The quote with each bracketed alteration set aside as an ellipsis is, so the words around it must still be
    word for word (is_in); the brackets show the reader what was changed."""
    return BRACKET.sub("...", quote)


def where_in(quote, section):
    """The narrowest subsection of a stored section that holds the quote, as a cite ("83.49(3)(a)"); the
    section alone if it is in no single subsection; None if it is not in the section."""
    if not is_in(quote, statute[section]):
        return None
    text = statute[section]
    holding = [key for key, (start, end) in subsections(section).items() if is_in(quote, text[start:end])]
    return section + max(holding, key=len) if holding else section


def check_quoted(text, given):
    """Check each quoted passage in a reply. given: everything the model was given for it, as one string (its
    system prompt, the tenant's messages, the tool results). Returns [(quote, cite, problem)]:
    - a quote with a cite must be in that section, and in that subsection when one is named, unless its words are no
      statute's and are word for word in what the model was given: then it is someone else's quote (the tenant's, the
      lease's, a case's, the tool's own) next to a cite that is not its source, and passes (TODO item 64);
    - a quote without a cite must be in the stored statutes or in what the model was given.
    A bracketed alteration ("[t]he", "specif[y]") is set aside first (unbracketed). A cite to a section or subsection
    that does not exist is left to check_cites."""
    problems = []
    for quote, cite in quoted_passages(text):
        section, _, rest = cite.partition("(")
        words = unbracketed(quote)                       # a bracketed alteration is the quoter's, not a misquote
        if not cite:
            if not (is_in(words, given) or any(is_in(words, t) for t in statute.values())):
                problems.append((quote, cite, "is not word for word in the statute, your lease, your own words, "
                                              "or anything else the tool gave the model"))
        elif section not in statute or (rest and "(" + rest not in subsections(section)):
            continue
        elif not is_in(words, statute[section]):
            elsewhere = [s for s in statute if is_in(words, statute[s])]
            if not elsewhere and is_in(words, given):          # real words, not the statute's: the cite is not theirs
                continue
            problems.append((quote, cite, f"is not in {section}" + (f"; it is in {elsewhere[0]}" if elsewhere else "")))
        elif rest and not is_in(words, statute[section][slice(*subsections(section)["(" + rest])]):
            problems.append((quote, cite, f"is in {where_in(words, section)}, not {cite}"))
    return problems


def cites_without_quote(text):
    """Each ch. 83 cite outside quote marks whose words no quoted passage in the same reply holds: a section or
    subsection named and retold instead of quoted ("Fla. Stat. 83.56(5)(a) states that if ...", TODO item 54).
    "Under 83.49(3)" counts as quoted when a quote from 83.49(3)(a) is in the reply. A cite to a section or
    subsection that does not exist is left to check_cites. Measured by dev/eval.py; nothing is shown to the
    tenant."""
    quotes = [words for _, _, words in quote_spans(text)]
    found = []
    for cite in cites_in(unquoted(text)):
        section, _, rest = cite.partition("(")
        if section not in statute or (rest and "(" + rest not in subsections(section)):
            continue
        span = statute[section][slice(*subsections(section)["(" + rest])] if rest else statute[section]
        if not any(is_in(q, span) for q in quotes):
            found.append(cite)
    return found


# A reporter cite of a court opinion: "448 So. 2d 1208", "448 So.2d 1208", "103 Fla. 892", "946 F. Supp. 962".
REPORTER = re.compile(r"\b\d{1,4} (?:So\.\s?[23]d|So\.|Fla\.|F\.\s?Supp\.(?:\s?[23]d)?) \d{1,5}\b")


def check_case_cites(text, given):
    """Each reporter cite in a reply, outside quote marks, must be one the model was shown in this chat (a
    get_cases result, which the program printed). Returns [(cite, problem)]."""
    return [(cite, "is not a case this tool showed in this chat")
            for cite in dict.fromkeys(m.group() for m in REPORTER.finditer(unquoted(text)))
            if compact(cite) not in compact(given)]


def caution(what, problem):
    """The line printed under a reply for one failed cite or quote. Written to the tenant."""
    return f"[Check: {what} {problem}. Check it against the source yourself before relying on it.]"


def quote_label(quote, cite):
    """How a caution names a quote: its first six words, and its cite if it has one."""
    words = quote.split()
    short = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
    return f'the quote "{short}"' + (f" ({cite})" if cite else "")
