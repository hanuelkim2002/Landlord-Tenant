"""Run a round: every (arm, scenario) pair in its own thread and its own tenant, REPEATS runs in sequence.

Usage (from the project folder, venv active):
    python <this file> <round dir> <repeats> <arm,arm,...> <scenario,scenario,...>
Arm X uses <round dir>/rules_X.txt as RULES_FILE. Output: <round dir>/runs/<arm>/<scenario>_r<k>.out.
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
ROUND = Path(sys.argv[1])
REPEATS = int(sys.argv[2])
ARMS = sys.argv[3].split(",")
SCENARIOS = sys.argv[4].split(",")
SEED = PROJECT / "matters" / "t-test" / "test-001"


def seed_tenant(tenant):
    folder = PROJECT / "matters" / tenant / "m-000"
    if not folder.exists():
        shutil.copytree(SEED, folder, ignore=shutil.ignore_patterns("sessions"))
        saved = json.loads((folder / "matter.json").read_text())
        saved.update({"tenant": tenant, "id": "m-000"})
        (folder / "matter.json").write_text(json.dumps(saved, indent=2))


def run_pair(arm, name, n):
    tenant = f"t-{ROUND.name}-{arm}-{n}"
    seed_tenant(tenant)
    data = json.loads((PROJECT / "dev" / "scenarios" / f"{name}.json").read_text())
    data["start"] = [tenant if line == "t-test" else line for line in data["start"]]
    scenario = ROUND / "scenarios" / f"{arm}_{name}.json"
    scenario.parent.mkdir(parents=True, exist_ok=True)
    scenario.write_text(json.dumps(data, indent=2))
    env = {**os.environ, "RULES_FILE": str(ROUND / f"rules_{arm}.txt")}
    (ROUND / "runs" / arm).mkdir(parents=True, exist_ok=True)
    for rep in range(1, REPEATS + 1):
        out = ROUND / "runs" / arm / f"{name}_r{rep}.out"
        if out.exists() and "New matter" in out.read_text() and "Traceback" not in out.read_text():
            continue
        for attempt in (1, 2):
            with open(out, "w") as f:
                code = subprocess.run([sys.executable, "dev/live_run.py", str(scenario)], cwd=PROJECT, env=env,
                                      stdout=f, stderr=subprocess.STDOUT).returncode
            text = out.read_text()
            if code == 0 and "Traceback" not in text and re.search(r"New matter \S+ m-\d+", text):
                break
        with open(ROUND / "progress.txt", "a") as p:
            p.write(f"{arm} {name} r{rep} exit {code} attempt {attempt}\n")


threads = [threading.Thread(target=run_pair, args=(arm, name, i))
           for arm in ARMS for i, name in enumerate(SCENARIOS)]
for t in threads:
    t.start()
for t in threads:
    t.join()
with open(ROUND / "progress.txt", "a") as p:
    p.write("ALL DONE\n")
