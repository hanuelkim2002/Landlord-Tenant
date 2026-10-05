"""Compare two eval runs scored by the same dev/eval.py, for TODO items 81 to 85 (what the tool knows): the kinds of
expectation, the measures per 100 replies (lease searches and lease absences said without a search added), the
program's cautions by kind, and the turns of the six stories of what the tool knows, one per state, each with its
expectations. From docs/evals/2026-10-04-options-cite/method/compare.py.

    python docs/evals/2026-10-04-know/method/compare.py before dev/eval_runs/2026-10-04-know-before \
        after dev/eval_runs/2026-10-04-know-after
"""
import json
import sys
from pathlib import Path

KINDS = [   # (label, test on an expectation's "what")
    ("Legal question: answer applies the law", lambda w: w.endswith("' applied")),
    ("Option: whether it is open comes first", lambda w: w.endswith("is open first")),
    ("Point the tool does not know: said as it is", lambda w: "has /" in w and "Lease" not in w),
    ("Lease point: searched", lambda w: "calls search_lease" in w),
    ("Lease point: the clause cited", lambda w: "has /(?i)Lease" in w),
    ("Court question: get_cases called", lambda w: "calls get_cases" in w),
    ("Court question: its cases used in the answer", lambda w: w.endswith("uses its cases")),
    ("Deadline question: get_deadlines called", lambda w: "calls get_deadlines" in w),
    ("Deadlines computed", lambda w: w.startswith("deadlines ")),
    ("Letters as asked", lambda w: w == "letters" or "calls draft_letter" in w or "no draft_letter" in w),
    ("Not-covered stop or note right", lambda w: w in ("stops", "not_covered_note")),
    ("Forbidden words absent", lambda w: "lacks /" in w),
]
# turns with each measure (dev/eval.py counts a turn once however many it has)
MEASURES = ["replies", "lease_searches", "lease_absent", "recited", "quotes_only", "field_names", "prompt_names",
            "dates_made", "echo", "choose_screen", "offer_screen", "cases_not_given", "empty_turns", "footers",
            "deadlines_by_program", "crashed", "gateway_trouble"]
CAUTION_KINDS = [   # (label, start of the caution line)
    ("quote", "[Check: the quote"),
    ("case left out", "[Check: the program printed cases"),
    ("cut off", "[Check: this reply was cut off"),
]
KNOW = ["eval_know_deposit_unsure", "eval_know_lease_holdover", "eval_know_violation_waterbed",
        "eval_know_repair_mold_code", "eval_know_violation_guest", "eval_know_nonpayment_orange"]


def caution_kind(line):
    return next((label for label, start in CAUTION_KINDS if line.startswith(start)), "cite")


def side(folder):
    scores = json.loads((Path(folder) / "scores.json").read_text())
    kinds = {}
    for label, test in KINDS:
        items = [x for s in scores for x in s["expect"] if test(x["what"])]
        kinds[label] = [sum(x["ok"] for x in items), len(items)]
    totals = {m: sum(int(s.get(m, 0)) for s in scores) for m in MEASURES}
    totals["runs"] = len(scores)
    totals["expected_ok"] = sum(s["expected_ok"] for s in scores)
    cautions = {}
    for s in scores:
        for t in s["turns"]:
            for line in t["cautions"]:
                cautions[caution_kind(line)] = cautions.get(caution_kind(line), 0) + 1
    know = {}
    for s in scores:
        if s["scenario"] in KNOW:
            row = know.setdefault(s["scenario"], {"runs": 0, "all_ok": 0, "expectations": {}})
            row["runs"] += 1
            row["all_ok"] += int(s["expected_ok"])
            for x in s["expect"]:
                got = row["expectations"].setdefault(x["what"], [0, 0])
                got[0] += int(x["ok"])
                got[1] += 1
    scenarios = {}
    for s in scores:
        row = scenarios.setdefault(s["scenario"], [0, 0])
        row[0] += int(s["expected_ok"])
        row[1] += 1
    return {"totals": totals, "kinds": kinds, "cautions": cautions, "know": know, "scenarios": scenarios}


if __name__ == "__main__":
    args = sys.argv[1:]
    sides = {args[i]: side(args[i + 1]) for i in range(0, len(args), 2)}
    print(json.dumps(sides, indent=1))
