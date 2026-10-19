"""Blind transcripts from two eval runs, mixed, for scorer agents who do not know there are two: the runs of each
side that reached the chat, shuffled together under one set of codes, grouped into batches of whole scenarios
(each scenario's transcripts from both sides in the same batch, so the same two scorers judge both).

    python docs/evals/2026-10-12-skills/method/blind_mixed.py dev/eval_runs/2026-10-12-skills-blind \
        before dev/eval_runs/2026-10-12-skills-before after dev/eval_runs/2026-10-12-skills-after

From docs/evals/2026-10-04-know/method/blind_mixed.py, with each story's context built from the skills (TODO 116):
the playbooks are gone, and each skill carries the same sections, open questions, and posture lines. A story's
description and chat lines come from its scenario in this copy (since TODO 115 the description also holds the facts
the old sheet asked; on the side before, those facts are on the transcript's SHEET lines). The program's caution
lines are taken out of every transcript, as before. Writes <out>/runs/R001.txt ..., context_<scenario>.md,
key.json (code, side, scenario, rep), and batches.json, all under dev/eval_runs/, which git ignores.
"""
import json
import random
import re
import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[4]                # the project folder
sys.path.insert(0, str(PROJECT))
import skills                                                # noqa: E402  (the project's skills, for each context)

OUT = Path(sys.argv[1]).resolve()
SIDES = dict(zip(sys.argv[2::2], (Path(p).resolve() for p in sys.argv[3::2])))
CAUTION = re.compile(r"^\[PROGRAM CAUTION shown to the tenant\].*\n?", re.M)
PROGRAM_DEADLINES = "[PROGRAM PRINTED, the deadlines: asked when, the model did not call get_deadlines]"
LEASE_NOTES = {
    "eval_repair_ac_terminate": "The lease's Article 7.2 says the landlord shall repair the heating, air-conditioning, "
                                "electrical, and plumbing systems and the appliances; 7.1 promises compliance with 83.51 "
                                "and the building, housing, and health codes.",
    "eval_know_lease_holdover": "The lease's Section 2.4 (Month-to-Month Holdover With Consent): if the landlord accepts "
                                "rent after the expiration date without a written renewal, the tenancy becomes month to "
                                "month on the same terms; Section 3.3 (Late Charge): rent not received by the fifth is "
                                "late, with a late charge of $75 plus $10 a day, up to $250 a month; Section 2.3: 60 "
                                "days' written notice to end at the expiration date.",
    "eval_lease_end_renewal": "The lease's Section 2.3: no automatic renewal, 60 days' written notice to end at the "
                              "expiration date; Section 2.4: a month-to-month holdover if the landlord accepts rent after it.",
    "eval_nonpayment_taped": "The lease's Section 3.3 (Late Charge): $75 plus $10 a day, up to $250 a month.",
    "eval_know_violation_waterbed": "Nothing in the lease's text is about waterbeds or liquid-filled furniture.",
    "eval_know_repair_mold_code": "The lease's Article 7: the landlord complies with 83.51 including the building, "
                                  "housing, and health codes (7.1) and repairs heating, air-conditioning, electrical, "
                                  "plumbing, and the appliances (7.2); nothing promises mold removal. Section 8.5: the "
                                  "tenant ventilates, keeps humidity reasonable, and reports mold in writing within 48 hours.",
    "eval_know_nonpayment_orange": "The house is in Orlando, Orange County. The tool holds a court holiday calendar only "
                                   "for the Eighth Judicial Circuit (Alachua and nearby counties), so it cannot count the "
                                   "3-day period for Orange County.",
}


def section(body, title):
    """The text under one "## <title>" heading of a skill, up to the next "## " heading."""
    m = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", body, flags=re.M | re.S)
    return m.group(1).strip() if m else ""


shutil.rmtree(OUT, ignore_errors=True)
(OUT / "runs").mkdir(parents=True)
pool = []
for side, folder in SIDES.items():
    for s in json.loads((folder / "scores.json").read_text()):
        if s["replies"] > 0:                                   # a run that stopped before the chat has nothing to score
            pool.append((side, folder, s["scenario"], s["rep"]))
random.Random(20261012).shuffle(pool)
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
    start = data["start"]
    parts = [f"# {scenario}", "", "Tenant's description at intake (the tenant's own words):",
             start.get("description") or start.get("update", ""), "",
             "Chat lines the tenant typed, in order:", *[f"- {c}" for c in data["chat"]], ""]
    if scenario in LEASE_NOTES:
        parts += ["What the lease and the tool hold on the chat's points:", LEASE_NOTES[scenario], ""]
    names = data["expect"].get("skills", [])
    if not names:
        parts += ["No situation the tool has instructions for fits this story.", ""]
    for name in names:
        sk = skills.skills[name]
        parts += [f"Situation {name}: statute sections the model had: {', '.join(sk.sections)}", "",
                  "What the statute does not settle (the only points a reply may call unsettled), with the readings:",
                  section(sk.body, "What the statute does not settle"), "",
                  "Letters, with the posture lines (copy-only):", section(sk.body, "Letters"), ""]
    (OUT / f"context_{scenario}.md").write_text("\n".join(str(p) for p in parts))

# Batches of whole scenarios, packed largest first into the first batch with room under CAP characters, so no
# scorer reads much more than another.
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
