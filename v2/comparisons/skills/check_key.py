"""Checks the skills test's answer key against statutes/, so the key itself can be trusted.
Each quote must be word for word in the statute subsection (and paragraph) it cites, and each date the key gives
must be the fact's date plus the days, compared with the story's today. Run from this folder:
python check_key.py            (checks stories.json)
python check_key.py stories_more.json            (checks another key file in this folder)
python check_key.py ../each_skill/repair_not_made/stories.json            (or a key file anywhere, by its path)
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
import law                                                    # the app's own splitter, so keys and skills read alike


def quote_in_cite(quote, cite):
    """Whether the quote is word for word in the cited subsection or paragraph of statutes/."""
    return law.squash(quote) in law.squash(law.cited_text(cite) or "")


def problems_with(story, folder):
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
    if story.get("lease") and not (folder / story["lease"]).exists():   # a variant sits beside its key
        found.append(f"lease file not found: {story['lease']}")
    if not story["points"] or not story["law"]:
        found.append("no points or no law")
    return found


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "stories.json"          # which key to check
    key_file = Path(name) if Path(name).exists() else HERE / name
    stories = json.loads(key_file.read_text())["stories"]
    failures = 0
    for story in stories:
        for problem in problems_with(story, key_file.parent):
            failures += 1
            print(f"{story['id']}: {problem}")
        print(f"{story['id']}: {len(story['law'])} quotes, {len(story['dates'])} dates checked")
    print("OK" if failures == 0 else f"{failures} problems")
