"""Checks the answer key against the leases' own words, so the key itself can be trusted.
Each passage must be in its lease word for word, each number or amount in a point must be in the lease, and each
word a 'not covered' question rules out must be nowhere in the lease. Run from this folder: python check_key.py
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

from make_leases import HERE, plain_text

# v1's sample lease stays out of git (the .gitignore covers lease.pdf). It is read from v2/lease.pdf.
SAMPLE = HERE.parent.parent / "lease.pdf"

# A number as a lease prints it: "$1,798.00", "24", "12:00", "555-0177", "32608".
NUMBER = re.compile(r"\$?\d[\d,.:/-]*")


def squash(text):
    """One space between words and straight quotes, so line breaks and curly quotes don't count as differences."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip()


def lease_text(name):
    """The words of a lease as written: the source text for the new leases, PyMuPDF's reading for v1's sample."""
    if name == "sample_v1":
        return "\n".join(page.get_text() for page in pymupdf.open(SAMPLE))
    return plain_text(name)


def problems_with(question, text):
    """Every way one question disagrees with its lease's text."""
    found = []
    if not question["points"]:
        found.append("no points")
    for passage in question["passages"]:
        if squash(passage) not in text:
            found.append(f"passage not in the lease: {passage[:70]}")
    # The points are judged by meaning, but their numbers must still be the lease's numbers.
    for point in question["points"]:
        for number in NUMBER.findall(point):
            if number.rstrip(".,:") not in text:
                found.append(f"number in a point is not in the lease: {number}")
    if question["covered"] and not question["passages"]:
        found.append("covered, but no passage")
    if not question["covered"]:
        for word in question.get("absent_words", []):
            if word.lower() in text.lower():
                found.append(f"'not covered', but the lease has the word: {word}")
    return found


if __name__ == "__main__":
    if len(sys.argv) > 1:
        SAMPLE = Path(sys.argv[1])          # before v2/lease.pdf exists, pass the sample lease's path
    questions = json.loads((HERE / "answer_key.json").read_text())["questions"]
    texts = {}
    failures = 0
    for question in questions:
        name = question["lease"]
        if name not in texts:
            texts[name] = squash(lease_text(name))
        for problem in problems_with(question, texts[name]):
            failures += 1
            print(f"{question['id']}: {problem}")
    for name in texts:
        mine = [q for q in questions if q["lease"] == name]
        print(f"{name:16} {sum(q['covered'] for q in mine):2} answered by the lease, "
              f"{sum(not q['covered'] for q in mine)} not")
    print("OK" if failures == 0 else f"{failures} problems")
