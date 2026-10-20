"""Blind transcripts for scorer agents: both arms' transcripts under shuffled codes, grouped by scenario, with
each scenario's context (story, chat lines, the active playbooks' open questions and posture lines)."""
import json
import random
import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[4]                # the project folder
sys.path.insert(0, str(PROJECT))
import yaml                                                    # noqa: E402

SP = Path(sys.argv[1])
ARMS = {"base": SP / "eval" / "base2", "after": SP / "eval" / "after2"}
OUT = SP / "eval" / "blind"
shutil.rmtree(OUT, ignore_errors=True)
(OUT / "runs").mkdir(parents=True)
runs = []
for arm, folder in ARMS.items():
    for s in json.loads((folder / "scores.json").read_text()):
        if s["replies"] == 0 and not s["footers"]:
            continue                                           # a run that stopped before the chat: nothing to score
        runs.append({"arm": arm, "scenario": s["scenario"], "rep": s["rep"],
                     "file": folder / "transcripts" / f"{s['scenario']}_r{s['rep']}.txt"})
random.Random(20261001).shuffle(runs)
key = []
for i, r in enumerate(runs, start=1):
    code = f"R{i:03d}"
    shutil.copy(r["file"], OUT / "runs" / f"{code}.txt")
    key.append({"code": code, "arm": r["arm"], "scenario": r["scenario"], "rep": r["rep"]})
(OUT / "key.json").write_text(json.dumps(key, indent=2))

contexts = {}
for scenario in sorted({r["scenario"] for r in runs}):
    data = json.loads((PROJECT / "dev" / "scenarios" / f"{scenario}.json").read_text())
    issues = data["expect"].get("issues", [])
    parts = [f"# {scenario}", "", "Tenant's description at intake (the tenant's own words):", *data["start"][3:-1], "",
             "Chat lines the tenant typed, in order:", *[f"- {c}" for c in data["chat"]], ""]
    for issue in issues:
        pb = yaml.safe_load((PROJECT / "playbooks" / f"{issue}.yaml").read_text())
        parts += [f"Playbook {issue}: open questions (the only questions the reply may call unsettled):",
                  *[f"- {q}" for q in (pb["spec"].get("open_questions") or [])],
                  f"Posture lines (copy-only, for letters):",
                  *[f"- {k}: {v}" for k, v in (pb["guidance"].get("postures") or {}).items() if k != "notice_sufficiency"], ""]
    contexts[scenario] = "\n".join(str(p) for p in parts)
    (OUT / f"context_{scenario}.md").write_text(contexts[scenario])
groups = {}
for k in key:
    groups.setdefault(k["scenario"], []).append(k["code"])
(OUT / "groups.json").write_text(json.dumps(groups, indent=2))
print(len(key), "runs;", {s: len(c) for s, c in groups.items()})
