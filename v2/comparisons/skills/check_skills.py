"""The skill quote checker, tried on each version of deposit_not_returned: every quotation followed by a cite, like
"..." (83.49(3)(a)), must be word for word in that subsection of statutes/. Also counts each skill's words.
Run from this folder: python check_skills.py
"""
import re
from pathlib import Path

from check_key import HERE, quote_in_cite

V1_SKILL = HERE.parents[2] / "v1" / "skills" / "deposit_not_returned.md"
SKILLS = {"A": ["versions/A_checklist.md"], "B": ["versions/B_examples.md"],
          "C": ["versions/C_core.md", "versions/C_details.md"], "v1": [V1_SKILL]}
QUOTED = re.compile(r'"([^"]{8,})"\s*\((?:Fla\. Stat\. )?(\d+\.\d+(?:\(\w+\))*)\)')   # "words" (83.49(3)(a))


def body(path):
    """A skill file's text after its header (the part between the first two "---" lines), as the model reads it."""
    text = Path(path).read_text()
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    return text


def check(name):
    """Each cited quote in the skill, whether it checks out, and the skill's word count."""
    text = "\n".join(body(HERE / p if isinstance(p, str) else p) for p in SKILLS[name])
    results = [(quote, cite, quote_in_cite(quote, cite)) for quote, cite in QUOTED.findall(text)]
    return results, len(text.split())


if __name__ == "__main__":
    for name in SKILLS:
        results, words = check(name)
        bad = [r for r in results if not r[2]]
        print(f"{name:3} {words:5} words   {len(results) - len(bad)} of {len(results)} quotes check out")
        for quote, cite, _ in bad:
            print(f"      not in {cite}: {quote[:80]}")
