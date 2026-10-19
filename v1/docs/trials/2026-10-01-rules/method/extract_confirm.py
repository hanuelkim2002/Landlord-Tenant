"""Turn the trial's runs into blind transcripts for scorers, plus automatic measures.

For each run: find its matter from the driver's screen output, read the session transcript, and write what
happened in order, marking who produced each part (tenant, model, program). Runs get shuffled codes so a
scorer cannot tell which rules produced them; the key is written separately.
Usage (from the project folder, venv active):  python <this file> <trial dir>
"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from timeline import render_deadlines                                    # noqa: E402

TRIAL = Path(sys.argv[1])
# Expected result per scenario: the intended issue active, plus its dates in the timeline, plus a letter where
# the scenario asks for one. The dates come from compute_deadlines (checked 2026-10-01), not worked out by hand.
EXPECTED = {
    "entry_unannounced": (["landlord_entered_unannounced"], [], 1),
    "rent_increase": (["rent_increased"], [], 0),
    "leave_early": (["wants_to_leave_early"], ["2026-11-08"], 0),
    "month_to_month_end": (["lease_ending"], ["2026-10-31"], 0),
}


def transcript_text(session_file):
    lines, reply_n = [], 0
    for raw in session_file.read_text().splitlines():
        e = json.loads(raw)
        role = e.get("role")
        if role == "tenant":
            lines.append(f"\nTENANT: {e['text']}")
        elif role == "sheet":
            lines.append(f"[SHEET, tenant answered] {e.get('question', e.get('id'))} -> {e.get('value')}")
        elif role == "program":
            lines.append(f"[PROGRAM NOTE sent to the model] {e['text'].strip()}")
        elif role == "check":
            lines.append(f"[PROGRAM CHECK LINE shown to tenant] {e['text']}")
        elif role == "command":
            lines.append(f"\nTENANT COMMAND (handled by the program, no model): {e['text']}")
        elif role == "tool":
            if e["name"] == "get_deadlines":
                lines.append("[PROGRAM PRINTED to tenant, the get_deadlines result]\n" + render_deadlines(e["text"]))
            elif e["name"] == "draft_letter":
                lines.append("[PROGRAM PRINTED to tenant, the draft_letter result]\n" + e["text"])
            elif e["name"] == "propose_facts":
                lines.append(f"[tool result, not shown to tenant] propose_facts: {e['text']}")
        elif role == "model":
            calls = [c["name"] for c in e.get("tool_calls", [])]
            if calls:
                lines.append(f"[model called tools: {', '.join(calls)}]")
            if (e.get("text") or "").strip():
                reply_n += 1
                lines.append(f"MODEL REPLY {reply_n}:\n{e['text'].strip()}")
    return "\n".join(lines), reply_n


runs = []
for out in sorted((TRIAL / "runs").glob("*/*.out")):
    arm, scenario = out.parent.name, re.sub(r"_r\d+$", "", out.stem)
    text = out.read_text()
    m = re.search(r"New matter (\S+) (m-\d+)", text)
    if not m:
        runs.append({"arm": arm, "scenario": scenario, "run": out.stem, "failed": True})
        continue
    folder = Path.cwd() / "matters" / m.group(1) / m.group(2)
    sessions = sorted((folder / "sessions").glob("*.jsonl"))
    body, replies = transcript_text(sessions[-1]) if sessions else ("", 0)
    events = [json.loads(l) for l in (folder / "events.jsonl").read_text().splitlines()]
    timeline_part = text[text.rfind("DATE         EVENT"):] if "DATE         EVENT" in text else ""
    runs.append({
        "arm": arm, "scenario": scenario, "run": out.stem, "matter": f"{m.group(1)}/{m.group(2)}",
        "replies": replies, "body": body,
        "expected_ok": (json.loads((folder / "matter.json").read_text())["issues"] == EXPECTED[scenario][0]
                        and all(d in timeline_part for d in EXPECTED[scenario][1])
                        and sum(e["kind"] == "draft" for e in events) >= EXPECTED[scenario][2]),
        "flags": sum(e["kind"] in ("cite_flagged", "quote_flagged") for e in events),
        "empty": sum(e["kind"] == "reply_empty" for e in events),
        "drafts": sum(e["kind"] == "draft" for e in events),
    })

random.seed(20261001)
order = [r for r in runs if not r.get("failed")]
random.shuffle(order)
for i, r in enumerate(order, start=1):
    r["code"] = f"R{i:02d}"

(TRIAL / "blind").mkdir(exist_ok=True)
for scenario in EXPECTED:
    chunk = [r for r in order if r["scenario"] == scenario]
    with open(TRIAL / "blind" / f"{scenario}.txt", "w") as f:
        for r in chunk:
            f.write(f"\n\n==================== RUN {r['code']} ({r['replies']} model replies) ====================\n")
            f.write(r["body"])
(TRIAL / "key.json").write_text(json.dumps(
    [{k: v for k, v in r.items() if k != "body"} for r in runs], indent=2))
print(len(runs), "runs;", sum(1 for r in runs if r.get("failed")), "failed;",
      {s: sum(1 for r in order if r["scenario"] == s) for s in EXPECTED})
