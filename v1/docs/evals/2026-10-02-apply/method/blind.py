"""Blind transcripts for the scorer agents and a sample for the author (TODO item 49): the new code's runs that
reached the chat, under shuffled codes, grouped by scenario, with each scenario's context (the tenant's story,
the chat lines, each active playbook's open questions with their readings, and its posture lines).

    python docs/evals/2026-10-02-apply/method/blind.py dev/eval_runs/2026-10-02-apply-after

Writes <runs>/blind/ (runs/R001.txt ..., context_<scenario>.md, key.json, groups.json) and <runs>/author_sample/
(one run of each of six scenarios, with a scoring sheet). Both stay under dev/eval_runs/, which git ignores:
the transcripts quote the test lease, which is not committed.
"""
import json
import random
import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[4]                # the project folder
import yaml                                                    # noqa: E402

RUNS = Path(sys.argv[1]).resolve()
OUT = RUNS / "blind"
shutil.rmtree(OUT, ignore_errors=True)
(OUT / "runs").mkdir(parents=True)
scores = json.loads((RUNS / "scores.json").read_text())
runs = [s for s in scores if s["replies"] > 0]                 # a run that stopped before the chat has nothing to score
random.Random(20261002).shuffle(runs)
key = []
for i, s in enumerate(runs, start=1):
    code = f"R{i:03d}"
    shutil.copy(RUNS / "transcripts" / f"{s['scenario']}_r{s['rep']}.txt", OUT / "runs" / f"{code}.txt")
    key.append({"code": code, "scenario": s["scenario"], "rep": s["rep"]})
(OUT / "key.json").write_text(json.dumps(key, indent=2))

for scenario in sorted({k["scenario"] for k in key}):
    data = json.loads((PROJECT / "dev" / "scenarios" / f"{scenario}.json").read_text())
    parts = [f"# {scenario}", "", "Tenant's description at intake (the tenant's own words):", *data["start"][3:-1], "",
             "Chat lines the tenant typed, in order:", *[f"- {c}" for c in data["chat"]], ""]
    for issue in data["expect"].get("issues", []):
        pb = yaml.safe_load((PROJECT / "playbooks" / f"{issue}.yaml").read_text())
        parts += [f"Playbook {issue}: statute sections in the model's prompt: {', '.join(pb['sections'])}",
                  "Open questions (the only points the reply may call unsettled), with their readings:"]
        for q in pb["spec"].get("open_questions") or []:
            parts.append(f"- {q['id']}: {' '.join(q['text'].split())}")
            parts += [f"    reading: {' '.join(r.split())}" for r in q.get("readings", [])]
        parts += ["Posture lines (copy-only, for letters):",
                  *[f"- {k}: {v}" for k, v in (pb["guidance"].get("postures") or {}).items() if k != "notice_sufficiency"], ""]
    (OUT / f"context_{scenario}.md").write_text("\n".join(str(p) for p in parts))
groups = {}
for k in key:
    groups.setdefault(k["scenario"], []).append(k["code"])
(OUT / "groups.json").write_text(json.dumps(groups, indent=2))
print(len(key), "runs;", {s: len(c) for s, c in groups.items()})

# The author's sample: the first run of six scenarios that cover a deposit, a claim with cases, a repair, a
# violation notice, a neighbor, and a 3-day notice.
SAMPLE = ["eval_deposit_ghosted", "eval_cases_late_claim", "eval_repair_mold_apt", "eval_violation_dog",
          "eval_noise_neighbors", "eval_nonpayment_taped"]
sample = RUNS / "author_sample"
shutil.rmtree(sample, ignore_errors=True)
sample.mkdir()
sheet = ["# Scoring sheet for the author", "",
         "For each MODEL REPLY in the six transcripts, mark the rubric's categories (`dev/eval_rubric.md`) that",
         "apply, with a few words of evidence. The question the code cannot answer: is the application right?",
         "", "| Transcript | Reply | Categories | Evidence | Right on the law? (yes / no / partly) |", "|---|---|---|---|---|"]
for scenario in SAMPLE:
    pick = next((s for s in scores if s["scenario"] == scenario and s["replies"] > 0), None)
    if pick is None:
        continue
    name = f"{scenario}_r{pick['rep']}.txt"
    shutil.copy(RUNS / "transcripts" / name, sample / name)
    shutil.copy(OUT / f"context_{scenario}.md", sample / f"context_{scenario}.md")
    sheet += [f"| {name} | {n} |  |  |  |" for n in range(1, pick["replies"] + 1)]
(sample / "scoring_sheet.md").write_text("\n".join(sheet) + "\n")
print("author sample:", sorted(p.name for p in sample.glob("*.txt")))
