"""Checks the skills test's answer key against statutes/, so the key itself can be trusted.
Each quote must be word for word in the statute subsection (and paragraph) it cites, and each date the key gives
must be the fact's date plus the days, compared with the story's today. Run from this folder:
python check_key.py            (checks stories.json)
python check_key.py stories_more.json            (checks another key file in this folder)
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATUTES = HERE.parent.parent / "statutes"
CITE = re.compile(r"^(\d+\.\d+)((?:\(\w+\))*)$")            # "83.49(3)(a)" -> "83.49", "(3)(a)"
MARKER = re.compile(r"\s\((\d+|[a-z])\)(?=\s|\()")           # " (3) " or " (a) " where a subsection or paragraph starts;
                                                            # "(1)(a)" run together, as in 83.491, counts too


def squash(text):
    """One space between words and straight quote marks, so line breaks and curly quotes are not differences."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip()


def parts_of(text):
    """The statute text cut where its subsections and paragraphs start, as {"(3)": text, "(3)(a)": text, ...}.
    Numbers must come in order (1, 2, 3 ...) and letters in order inside each, so a cross-reference like
    "s. 83.49 (3)" in the middle of a paragraph is not taken for a new subsection."""
    found, number, letter = [], 0, ""
    for m in MARKER.finditer(text):
        label = m.group(1)
        if label.isdigit() and int(label) == number + 1:
            number, letter = number + 1, ""
            found.append((m.start(), f"({number})"))
        elif label.isalpha() and len(label) == 1 and number and ord(label) == ord(letter or "`") + 1:
            letter = label
            found.append((m.start(), f"({number})({letter})"))
    parts = {}
    for i, (start, key) in enumerate(found):
        later = [s for s, k in found[i + 1:] if not k.startswith(key)]   # a subsection runs past its own paragraphs
        parts[key] = text[start:later[0] if later else len(text)]
    return parts


def quote_in_cite(quote, cite):
    """Whether the quote is word for word in the cited subsection or paragraph of statutes/."""
    section, where = CITE.match(cite).groups()
    text = (STATUTES / f"{section}.txt").read_text()
    part = parts_of(text).get(where, "") if where else text
    return squash(quote) in squash(part)


def problems_with(story, lease):
    """Every way one story's key disagrees with the statutes or with its own dates."""
    found = []
    for law in story["law"]:
        if not quote_in_cite(law["quote"], law["cite"]):
            found.append(f"not in {law['cite']}: {law['quote'][:70]}")
    today = date.fromisoformat(story["today"])
    for d in story["dates"]:
        start = date.fromisoformat(story["facts"][d["fact"]])
        due = start + timedelta(days=d["days"])
        if due.isoformat() != d["date"] or (due < today) != d["passed"]:
            found.append(f"date wrong: {d}")
    if story.get("lease") and not (HERE / story["lease"]).exists():
        found.append(f"lease file not found: {story['lease']}")
    if not story["points"] or not story["law"]:
        found.append("no points or no law")
    return found


if __name__ == "__main__":
    lease = (HERE / "lease.txt").read_text()
    key_file = sys.argv[1] if len(sys.argv) > 1 else "stories.json"      # which key to check
    stories = json.loads((HERE / key_file).read_text())["stories"]
    failures = 0
    for story in stories:
        for problem in problems_with(story, lease):
            failures += 1
            print(f"{story['id']}: {problem}")
        print(f"{story['id']}: {len(story['law'])} quotes, {len(story['dates'])} dates checked")
    print("OK" if failures == 0 else f"{failures} problems")
