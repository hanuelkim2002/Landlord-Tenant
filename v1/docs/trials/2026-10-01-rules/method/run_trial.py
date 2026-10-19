"""Run the rules trial: every arm (a rules file) through the three chat scenarios, REPEATS times each.

Arms run in parallel, one thread each; within an arm the runs are sequential, so matter ids in the arm's
own tenant folder (matters/t-trial-<arm>) never collide. Each run is retried once if run.py crashed.
Usage (from the project folder, venv active):  python <this file> <trial dir> <arm> [<arm> ...]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

PROJECT = Path.cwd()
TRIAL = Path(sys.argv[1])
ARMS = sys.argv[2:]
SCENARIOS = ["nonpayment_3day", "repair_notice", "claim_letter"]
REPEATS = 3
SEED = PROJECT / "matters" / "t-test" / "test-001"


def seed_tenant(tenant):
    """A tenant folder with one seed matter (a copy of the test matter, no transcripts), so run.py lists the
    tenant and the scenario can pick it. The seed is m-000; runs get m-002, m-003, ..."""
    folder = PROJECT / "matters" / tenant / "m-000"
    if folder.exists():
        return
    shutil.copytree(SEED, folder, ignore=shutil.ignore_patterns("sessions"))
    saved = json.loads((folder / "matter.json").read_text())
    saved.update({"tenant": tenant, "id": "m-000"})
    (folder / "matter.json").write_text(json.dumps(saved, indent=2))


def scenario_for(arm, name):
    """The scenario with the arm's tenant in place of t-test."""
    data = json.loads((PROJECT / "dev" / "scenarios" / f"{name}.json").read_text())
    data["start"] = [f"t-trial-{arm}" if line == "t-test" else line for line in data["start"]]
    path = TRIAL / "scenarios" / f"{arm}_{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    return path


def run_arm(arm):
    tenant = f"t-trial-{arm}"
    seed_tenant(tenant)
    env = {**os.environ, "RULES_FILE": str(TRIAL / f"rules_{arm}.txt")}
    out_dir = TRIAL / "runs" / arm
    out_dir.mkdir(parents=True, exist_ok=True)
    for rep in range(1, REPEATS + 1):
        for name in SCENARIOS:
            out = out_dir / f"{name}_r{rep}.out"
            if out.exists() and "New matter" in out.read_text() and "Traceback" not in out.read_text():
                continue                                         # done in an earlier launch
            for attempt in (1, 2):
                with open(out, "w") as f:
                    code = subprocess.run([sys.executable, "dev/live_run.py", str(scenario_for(arm, name))],
                                          cwd=PROJECT, env=env, stdout=f, stderr=subprocess.STDOUT).returncode
                text = out.read_text()
                if code == 0 and "Traceback" not in text and re.search(r"New matter \S+ m-\d+", text):
                    break
            with open(TRIAL / "progress.txt", "a") as p:
                p.write(f"{arm} {name} r{rep} exit {code} attempt {attempt}\n")


threads = [threading.Thread(target=run_arm, args=(arm,)) for arm in ARMS]
for t in threads:
    t.start()
for t in threads:
    t.join()
with open(TRIAL / "progress.txt", "a") as p:
    p.write("ALL DONE\n")
