"""Blind transcripts from two eval runs, mixed, for scorer agents who do not know there are two: the runs of each
side that reached the chat, shuffled together under one set of codes, grouped into batches of whole scenarios
(each scenario's transcripts from both sides in the same batch, so the same two scorers judge both).

    python docs/evals/2026-10-03-blind/method/blind_mixed.py dev/eval_runs/2026-10-03-blind \
        old dev/eval_runs/2026-10-02-apply-after new dev/eval_runs/2026-10-03-items65-66

From docs/evals/2026-10-02-apply/method/blind.py, with three differences: two sides mixed; the program's caution
lines taken out of every transcript (the new side has kinds the old has not, which would point the scorers to
the slips they name; the rubric treats cautions as hints only); and the label of deadlines the program printed
by itself (TODO item 65) made the same as any other printed deadlines. Each scenario's context is built from the
scenario and playbooks as they are now. Writes <out>/runs/R001.txt ..., context_<scenario>.md, key.json (code,
side, scenario, rep), and batches.json. Everything stays under dev/eval_runs/, which git ignores.
"""
import json
import random
import re
import shutil
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[4]                # the project folder
OUT = Path(sys.argv[1]).resolve()
SIDES = dict(zip(sys.argv[2::2], (Path(p).resolve() for p in sys.argv[3::2])))
CAUTION = re.compile(r"^\[PROGRAM CAUTION shown to the tenant\].*\n?", re.M)
PROGRAM_DEADLINES = "[PROGRAM PRINTED, the deadlines: asked when, the model did not call get_deadlines]"

shutil.rmtree(OUT, ignore_errors=True)
(OUT / "runs").mkdir(parents=True)
pool = []
for side, folder in SIDES.items():
    for s in json.loads((folder / "scores.json").read_text()):
        if s["replies"] > 0:                                   # a run that stopped before the chat has nothing to score
            pool.append((side, folder, s["scenario"], s["rep"]))
random.Random(20261003).shuffle(pool)
key = []
for i, (side, folder, scenario, rep) in enumerate(pool, start=1):
    code = f"R{i:03d}"
    text = (folder / "transcripts" / f"{scenario}_r{rep}.txt").read_text()
    text = CAUTION.sub("", text).replace(PROGRAM_DEADLINES, "[PROGRAM PRINTED, deadlines]")
    (OUT / "runs" / f"{code}.txt").write_text(text)
    key.append({"code": code, "side": side, "scenario": scenario, "rep": rep})
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

# Batches of whole scenarios, packed largest first into the first batch with room under CAP characters, so no
# scorer reads much more than another (the mold and cash-notice transcripts carry long printed cases).
CAP = 220_000
codes = {}
for k in key:
    codes.setdefault(k["scenario"], []).append(k["code"])
size = {sc: sum(len((OUT / "runs" / f"{c}.txt").read_text()) for c in cs) for sc, cs in codes.items()}
packed = []
for sc in sorted(codes, key=size.get, reverse=True):
    room = next((b for b in packed if sum(size[s] for s in b) + size[sc] <= CAP), None)
    if room is None:
        packed.append([sc])
    else:
        room.append(sc)
batches = {f"B{i}": {sc: sorted(codes[sc]) for sc in b} for i, b in enumerate(packed, start=1)}
(OUT / "batches.json").write_text(json.dumps(batches, indent=2))
print(len(key), "transcripts:", {side: sum(k["side"] == side for k in key) for side in SIDES})
for b, scs in batches.items():
    print(b, {sc: len(cs) for sc, cs in scs.items()}, sum(size[sc] for sc in scs) // 1000, "KB")
