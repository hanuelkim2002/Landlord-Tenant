"""Compare eval runs scored by the same dev/eval.py, for TODO items 72 and 73 (options before steps; cite, do not
recite): the kinds of expectation, the measures per 100 replies (recited added), the program's cautions by kind, the
single turns, and the author's AC story's open_first. From docs/evals/2026-10-03-items60-66/method/compare.py.

    python docs/evals/2026-10-04-options-cite/method/compare.py before dev/eval_runs/2026-10-03-items65-66 after dev/eval_runs/2026-10-04-after
"""
import json
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
# turns with each measure (dev/eval.py counts a turn once however many it has)
MEASURES = ["replies", "recited", "quotes_only", "field_names", "prompt_names", "cites_unquoted", "dates_made", "echo",
            "choose_screen", "offer_screen", "cases_not_given", "empty_turns", "footers", "deadlines_by_program",
            "crashed", "gateway_trouble"]
CAUTION_KINDS = [   # (label, start of the caution line)
    ("quote", "[Check: the quote"),
    ("section retold (item 66, gone)", "[Check: this reply cites"),
    ("case left out", "[Check: the program printed cases"),
    ("cut off", "[Check: this reply was cut off"),
]
TURNS = [   # (label, scenario, piece of the tenant's line, end of the expectation): single turns the items were about
    ("Mixed deadline and law question applied (item 51)", "eval_violation_dog", "am I safe", "' applied"),
    ("Cash-only notice applied (item 52)", "eval_cases_3day_cash", "cash only", "' applied"),
    ("Renewal question applied (items 52, 61)", "eval_lease_end_renewal", "Do I have to sign", "' applied"),
    ("Dog story: no 'you are safe'", "eval_violation_dog", "am I safe", "safe/"),
    ("AC story: ending the lease, open or not first", "eval_repair_ac_terminate", "How do I end my lease", "open first"),
    ("AC story: withholding rent, open or not first", "eval_repair_ac_terminate", "stop paying rent instead", "open first"),
]


def caution_kind(line):
    return next((label for label, start in CAUTION_KINDS if line.startswith(start)), "cite")


def side(folder):
    scores = json.loads((Path(folder) / "scores.json").read_text())
    kinds = {}
    for label, test in KINDS:
        items = [x for s in scores for x in s["expect"] if test(x["what"])]
        kinds[label] = [sum(x["ok"] for x in items), len(items)]
    totals = {m: sum(int(s[m]) for s in scores) for m in MEASURES}
    totals["runs"] = len(scores)
    totals["expected_ok"] = sum(s["expected_ok"] for s in scores)
    cautions = {}
    for s in scores:
        for t in s["turns"]:
            for line in t["cautions"]:
                cautions[caution_kind(line)] = cautions.get(caution_kind(line), 0) + 1
    turns = {}
    for label, scenario, piece, end in TURNS:
        items = [x for s in scores if s["scenario"] == scenario for x in s["expect"]
                 if piece.lower() in x["what"].lower() and x["what"].endswith(end)]
        turns[label] = [sum(x["ok"] for x in items), len(items)]
    # a question about when: the deadlines printed, by the model's call or by the program
    shown = []
    for s in scores:
        for x in s["expect"]:
            if "calls get_deadlines" in x["what"]:
                piece = x["what"].split("'")[1]
                turn = next((t for t in s["turns"] if piece in t["say"]), None)
                shown.append(x["ok"] or bool(turn and turn.get("deadlines_by_program")))
    turns["Question about when: deadlines printed (model or program)"] = [sum(shown), len(shown)]
    per_100 = {m: round(100 * totals[m] / max(totals["replies"], 1)) for m in MEASURES if m != "replies"}
    return {"kinds": kinds, "totals": totals, "per_100_replies": per_100, "cautions": cautions, "turns": turns,
            "by_scenario": {sc: [sum(s["expected_ok"] for s in scores if s["scenario"] == sc),
                                 sum(1 for s in scores if s["scenario"] == sc)]
                            for sc in sorted({s["scenario"] for s in scores})}}


if __name__ == "__main__":
    arms = dict(zip(sys.argv[1::2], sys.argv[2::2]))
    print(json.dumps({name: side(folder) for name, folder in arms.items()}, indent=1))
