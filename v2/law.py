"""The stored law: the statute sections in statutes/, the skills in skills/, and the skill quote checker.
Run it to check every skill: python law.py
"""
import json
import re

from config import SKILLS, STATUTES

CITE = re.compile(r"^(\d+\.\d+)((?:\(\w+\))*)$")            # "83.49(3)(a)" -> "83.49" and "(3)(a)"
MARKER = re.compile(r"\s\((\d+|[a-z])\)\s")                  # where a subsection " (3) " or a paragraph " (a) " starts
QUOTED = re.compile(r'"([^"]{8,})"\s*\((\d+\.\d+(?:\(\w+\))*)\)')   # a quote and its cite: "words" (83.49(3)(a))


def squash(text):
    """One space between words, straight quote marks, and one kind of hyphen: line breaks and typography aside."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub("[‐‑]", "-", text).replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip()


# ---- Statutes

def section_text(section):
    """The full text of one section, like "83.49", or None if statutes/ does not hold it."""
    path = STATUTES / f"{section.strip()}.txt"
    return path.read_text() if path.exists() else None


def section_titles():
    """Each stored section with its title, from statutes/index.json."""
    return {s["section"]: s["catchline"] for s in json.loads((STATUTES / "index.json").read_text())["sections"]}


def search_statute(phrase):
    """The sections whose text holds the phrase (capitals and spacing aside), with the words around it."""
    wanted, found = squash(phrase).lower(), []
    for path in sorted(STATUTES.glob("*.txt")):
        text = squash(path.read_text())
        at = text.lower().find(wanted)
        if wanted and at != -1:
            found.append((path.stem, text[max(0, at - 200):at + len(wanted) + 200]))
    return found


def parts_of(text):
    """A section cut where its subsections and paragraphs start: {"(3)": ..., "(3)(a)": ...}. Numbers must come in
    order (1, 2, 3) and letters in order inside each, so a cross-reference like "s. 83.49 (3)" is not a new part."""
    starts, number, letter = [], 0, ""
    for m in MARKER.finditer(text):
        label = m.group(1)
        if label.isdigit() and int(label) == number + 1:
            number, letter = number + 1, ""
            starts.append((m.start(), f"({number})"))
        elif label.isalpha() and number and ord(label) == ord(letter or "`") + 1:
            letter = label
            starts.append((m.start(), f"({number})({letter})"))
    parts = {}
    for i, (start, key) in enumerate(starts):
        later = [s for s, k in starts[i + 1:] if not k.startswith(key)]   # a subsection runs past its own paragraphs
        parts[key] = text[start:later[0] if later else len(text)].strip()
    return parts


def cited_text(cite):
    """The words a cite like "83.49(3)(a)" points to, or None if statutes/ does not hold them."""
    found = CITE.match(cite.replace(" ", ""))
    if not found:
        return None
    text = section_text(found.group(1))
    if text is None:
        return None
    words = parts_of(text).get(found.group(2)) if found.group(2) else text
    return words.split(" History. ")[0] if words else None      # the legislative history note is not the law's words


# ---- Skills

def read_skill(path):
    """One skill file: its name and description from the header, and its body (what the model reads once loaded)."""
    _, header, body = path.read_text().split("---", 2)
    fields = dict(line.split(":", 1) for line in header.strip().splitlines())
    return {"name": fields["name"].strip(), "description": fields["description"].strip(), "body": body.strip()}


def skills():
    """Every skill in skills/, by name."""
    return {s["name"]: s for s in map(read_skill, sorted(SKILLS.glob("*.md")))}


def check_quotes(text):
    """Each quote in a skill's text followed by a cite, with whether it is word for word in that cited part."""
    results = []
    for quote, cite in QUOTED.findall(text):
        words = cited_text(cite)
        results.append((quote, cite, words is not None and squash(quote) in squash(words)))
    return results


def check_all_skills():
    """Check every skill's quotes against statutes/; print a line per skill and each quote that fails. True if all pass."""
    all_ok = True
    for name, skill in skills().items():
        results = check_quotes(skill["body"])
        bad = [(q, c) for q, c, ok in results if not ok]
        print(f"{'OK  ' if not bad else 'FAIL'} {name}: {len(results) - len(bad)} of {len(results)} quotes check out")
        for quote, cite in bad:
            print(f"     not in {cite}: {quote[:80]}")
        all_ok = all_ok and not bad
    return all_ok


if __name__ == "__main__":
    check_all_skills()
