"""Citations: find the statute cites in a reply the model wrote and check them against the stored statutes.

Nothing here calls a model or writes to a matter. The chat loop (agent.chat) runs check_cites on every reply
and prints a caution for each cite that fails; the reply itself is still shown.
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
    """Every ch. 83 cite in the text, spaces removed, in order, each once: ["83.49(3)(a)", "83.56"]."""
    found = []
    for m in CITE.finditer(text):
        cite = m.group(0).replace(" ", "")
        if cite not in found:
            found.append(cite)
    return found


def check_cites(text, shown):
    """Check each cite in a reply. shown: the sections the model had in this turn (its STATUTE SECTIONS plus any
    it fetched with get_statute_section). Returns [(cite, problem)], empty when every cite passes:
    - the section is not in the stored statutes;
    - it was not shown or fetched (rule 8: fetch a section before mentioning it);
    - the section has no such subsection."""
    problems = []
    for cite in cites_in(text):
        section, _, rest = cite.partition("(")
        if section not in statute:
            problems.append((cite, "is not a section in this tool's copy of ch. 83 part II"))
        elif section not in shown:
            problems.append((cite, "was not among the sections this chat loaded or looked up"))
        elif rest and "(" + rest not in subsections(section):
            problems.append((cite, f"names a subsection that {section} does not have"))
    return problems


def caution(cite, problem):
    """The line printed under a reply for one failed cite. Written to the tenant."""
    return f"[Check: {cite} {problem}. Read it in the statute yourself before relying on it.]"
