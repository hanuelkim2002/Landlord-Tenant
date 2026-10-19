"""Compare the organizing code (base) with the applying code (after), both scored by dev/eval.py's expectations of
2026-10-02: each kind of expectation's pass rate, and the measures on every reply.

    python docs/evals/2026-10-02-apply/method/compare.py base dev/eval_runs/2026-10-02-apply-base after dev/eval_runs/2026-10-02-apply-after
"""
import json
import re
import sys
from pathlib import Path

KINDS = [   # (label, test on an expectation's "what")
    ("Legal question: answer applies the law", lambda w: w.endswith("' applied")),
    ("Open point: readings given", lambda w: "has /does not settle" in w),
    ("Court question: get_cases called", lambda w: "calls get_cases" in w),
    ("Court question: its cases used in the answer", lambda w: w.endswith("uses its cases")),
    ("Deadline question: get_deadlines called", lambda w: "calls get_deadlines" in w),
    ("Deadlines computed", lambda w: w.startswith("deadlines ")),
    ("Letters as asked", lambda w: w == "letters" or "calls draft_letter" in w or "no draft_letter" in w),
    ("Not-covered stop or note right", lambda w: w in ("stops", "not_covered_note")),
    ("Forbidden words absent", lambda w: "lacks /" in w),
]
MEASURES = ["replies", "quotes_only", "cautions", "field_names", "dates_made", "choose_screen", "cases_not_given",
            "offer_screen", "empty_turns", "footers", "crashed", "gateway_trouble"]


def side(folder):
    scores = json.loads((Path(folder) / "scores.json").read_text())
    kinds = {}
    for label, test in KINDS:
        items = [x for s in scores for x in s["expect"] if test(x["what"])]
        kinds[label] = [sum(x["ok"] for x in items), len(items)]
    totals = {m: sum(int(s[m]) for s in scores) for m in MEASURES}
    totals["runs"] = len(scores)
    totals["expected_ok"] = sum(s["expected_ok"] for s in scores)
    return {"kinds": kinds, "totals": totals,
            "by_scenario": {sc: [sum(s["expected_ok"] for s in scores if s["scenario"] == sc),
                                 sum(1 for s in scores if s["scenario"] == sc)]
                            for sc in sorted({s["scenario"] for s in scores})}}


if __name__ == "__main__":
    arms = dict(zip(sys.argv[1::2], sys.argv[2::2]))
    print(json.dumps({name: side(folder) for name, folder in arms.items()}, indent=1))
