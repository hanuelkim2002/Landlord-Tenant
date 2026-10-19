"""Sum the blind scorers' results by side: slips per category (each batch's two scorers averaged), firm (not marked
borderline) apart, law replies and those applied well, per side and per scenario, and agreement (a slip one
scorer found that the other found too, same transcript, reply, and category). From
docs/evals/2026-10-02-apply/method/blind_summary.py, with the sides of key.json.

    python docs/evals/2026-10-03-blind/method/blind_summary_mixed.py dev/eval_runs/2026-10-03-blind
"""
import json
import sys
from collections import Counter
from pathlib import Path

blind = Path(sys.argv[1])
side_of = {k["code"]: k["side"] for k in json.loads((blind / "key.json").read_text())}
scores = {f.stem.removeprefix("score_"): json.loads(f.read_text()) for f in sorted(blind.glob("score_*.json"))}
batches = sorted({k.split("_")[0] for k in scores})
sides = sorted(set(side_of.values()))
cats = {s: Counter() for s in sides}
firm = {s: Counter() for s in sides}
law = Counter()
well = Counter()
runs = Counter()
replies = Counter()
by_scenario = {}
agree = found = 0
per_scorer = {}
missing = [b for b in batches if not (f"{b}_a" in scores and f"{b}_b" in scores)]
for b in batches:
    if b in missing:
        continue
    pair = [scores[f"{b}_a"], scores[f"{b}_b"]]
    for s in pair:
        per_scorer[s["scorer"]] = sum(len(r["slips"]) for r in s["runs"])
        for r in s["runs"]:
            side = side_of[r["code"]]
            law[side] += r.get("law_replies", 0) / 2
            well[side] += r.get("applied_well", 0) / 2
            row = by_scenario.setdefault(r["scenario"], {x: [0, 0] for x in sides})
            row[side][0] += r.get("applied_well", 0) / 2
            row[side][1] += r.get("law_replies", 0) / 2
            for x in r["slips"]:
                cats[side][x["category"]] += 0.5
                if "borderline" not in x.get("evidence", "").lower():
                    firm[side][x["category"]] += 0.5
    for r in pair[0]["runs"]:
        runs[side_of[r["code"]]] += 1
        replies[side_of[r["code"]]] += r.get("replies", 0)
    keys = [{(r["code"], x["reply"], x["category"]) for r in s["runs"] for x in r["slips"]} for s in pair]
    agree += len(keys[0] & keys[1])
    found += len(keys[0] | keys[1])
out = {
    "missing_batches": missing,
    "scorers": per_scorer,
    "agreement": {"found_by_both": agree, "found_by_either": found},
    "sides": {s: {"transcripts": runs[s], "replies": replies[s], "law_replies_avg": law[s], "applied_well_avg": well[s],
                  "total_slips_avg": sum(cats[s].values()), "firm_slips_avg": sum(firm[s].values()),
                  "slips_by_category": dict(sorted(cats[s].items(), key=lambda kv: -kv[1])),
                  "firm_by_category": dict(sorted(firm[s].items(), key=lambda kv: -kv[1]))} for s in sides},
    "applied_well_by_scenario": by_scenario,
}
print(json.dumps(out, indent=1))
