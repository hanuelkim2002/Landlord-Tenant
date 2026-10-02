"""Compare two scored eval folders: run-level totals and each kind of expectation's pass rate."""
import json
import re
import sys
from pathlib import Path

KINDS = [   # (label, test on an expectation's "what")
    ("Legality question: 'does not decide' shown", lambda w: "has /does not decide" in w),
    ("'What are my deadlines?': get_deadlines called", lambda w: "calls get_deadlines" in w and "What are my deadlines" in w),
    ("Time question in plain words: get_deadlines called", lambda w: "calls get_deadlines" in w and "What are my deadlines" not in w),
    ("Court question: get_cases on a right topic", lambda w: re.search(r"calls get_cases|' topic$", w)),
    ("Letter asked for: drafted", lambda w: w == "letters" or "calls draft_letter" in w),
    ("No draft when not asked", lambda w: "no draft_letter" in w),
    ("Issues right at the end", lambda w: w == "issues"),
    ("Not-covered note / stop right", lambda w: w in ("stops", "not_covered_note")),
    ("Deadlines computed", lambda w: w.startswith("deadlines ")),
    ("Forbidden words absent", lambda w: "lacks /" in w),
    ("Sheet suggestion right (TODO 12)", lambda w: w.startswith("screen lacks")),
]


def load(folder):
    return json.loads((Path(folder) / "scores.json").read_text())


def kinds(scores):
    out = {}
    for label, test in KINDS:
        items = [x for s in scores for x in s["expect"] if test(x["what"])]
        out[label] = (sum(x["ok"] for x in items), len(items))
    return out


def totals(scores):
    keys = ["crashed", "expected_ok", "replies", "empty_turns", "cautions", "field_names", "echo", "footers"]
    t = {k: sum(int(s[k]) for s in scores) for k in keys}
    t["runs"] = len(scores)
    return t


if __name__ == "__main__":
    arms = {name: load(folder) for name, folder in zip(sys.argv[1::2], sys.argv[2::2])}
    result = {name: {"totals": totals(s), "kinds": kinds(s),
                     "by_scenario": {sc: (sum(x["expected_ok"] for x in s if x["scenario"] == sc),
                                          sum(1 for x in s if x["scenario"] == sc))
                                     for sc in sorted({x["scenario"] for x in s})}}
              for name, s in arms.items()}
    print(json.dumps(result, indent=1))
