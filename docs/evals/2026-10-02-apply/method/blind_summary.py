"""Sum the blind scorers' results: slips per category (each batch's two scorers averaged), firm (not marked
borderline) apart, law replies and those applied well, and agreement (a slip one scorer found that the other
found too, same transcript, reply, and category).

    python docs/evals/2026-10-02-apply/method/blind_summary.py dev/eval_runs/2026-10-02-apply-after/blind
"""
import json
import sys
from collections import Counter
from pathlib import Path

blind = Path(sys.argv[1])
scores = {f.stem.removeprefix("score_"): json.loads(f.read_text()) for f in sorted(blind.glob("score_*.json"))}
batches = sorted({k.split("_")[0] for k in scores})
cats, firm = Counter(), Counter()
law = well = runs = 0
agree = found = 0
per_scorer = {}
for b in batches:
    pair = [scores[f"{b}_a"], scores[f"{b}_b"]]
    for s in pair:
        per_scorer[s["scorer"]] = sum(len(r["slips"]) for r in s["runs"])
        for r in s["runs"]:
            law += r.get("law_replies", 0) / 2
            well += r.get("applied_well", 0) / 2
            for x in r["slips"]:
                cats[x["category"]] += 0.5
                if "borderline" not in x.get("evidence", "").lower():
                    firm[x["category"]] += 0.5
    runs += len(pair[0]["runs"])
    keys = [{(r["code"], x["reply"], x["category"]) for r in s["runs"] for x in r["slips"]} for s in pair]
    agree += len(keys[0] & keys[1])
    found += len(keys[0] | keys[1])
out = {"transcripts": runs, "scorers": per_scorer,
       "slips_by_category": dict(sorted(cats.items(), key=lambda kv: -kv[1])),
       "firm_by_category": dict(sorted(firm.items(), key=lambda kv: -kv[1])),
       "total_slips_avg": sum(cats.values()), "firm_slips_avg": sum(firm.values()),
       "law_replies_avg": law, "applied_well_avg": well,
       "agreement": {"found_by_both": agree, "found_by_either": found}}
print(json.dumps(out, indent=1))
