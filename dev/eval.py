"""Eval: run scenarios several times each and score every run by code, so a change to the harness or the rules
is measured over repeated runs instead of judged from one (two runs of the same setup scored 0.50 and 1.00
slips per reply in the rules trial, docs/trials/2026-10-01-rules).

    python dev/eval.py run <out dir> <repeats> [scenario ...]    # all scenarios with an "expect" block if none named
    python dev/eval.py score <out dir>                            # score the runs in <out dir> again

Options for run: --project <folder> runs another copy of the project (a git worktree at an older commit, to
compare against); --parallel N runs N sessions at once (default 8). It calls the model: each run is
dev/live_run.py, under its own scratch tenant, matters/t-eval-<out dir name>-<scenario>-<k>. The tenant is
seeded with an m-000 copy of matters/t-test/test-001 so the id exists; the run's own matter is the one its
screen names ("New matter <tenant> m-002"). Set
WIKI_UNVERIFIED=1 in the environment to offer the wiki's unverified case pages, as the cases scenarios need.

A scenario's "expect" block (every key optional):
  "issues"           the playbook issues active at the end, exactly
  "stops"            true: the tool stops before the chat (nothing it covers applies)
  "not_covered_note" true: the "may not be covered by this tool" note prints
  "deadlines"        issues whose deadlines get_deadlines computes (a deadlines_computed event naming a clock)
  "letters"          how many letters draft_letter makes
  "turns"            checks on single chat turns, each found by a piece of the tenant's line ("say"):
                     "called" / "not_called" (tool names), "must" / "must_not" (regexes on the turn's replies;
                     must_not looks only outside quote marks),
                     "topics" (the get_cases topics allowed in that turn; any other topic fails)
  "screen_must_not"  regexes the whole screen must not match (a wrong suggestion on the sheet, e.g.)
Every reply is also measured, whatever the scenario: empty turns (reply_empty events), program cautions
(quote_flagged and cite_flagged events), field names (a snake_case id outside quote marks), deadline echo (a
date the program printed in the same turn, repeated in the reply), and two word screens that mark a reply for
a person to read: LAW_WORDS (a party and must, may, can, entitled ... outside quote marks) and OFFER_WORDS
(would you like me to ...). The screens find candidates; they are not verdicts. A turn's "must" patterns
are matched against what the tenant read, the replies and any line the program printed under them (footer);
"footers" counts those lines, so the model's own lines and the program's can be told apart.

Output in <out dir>: runs/ (each run's screen and its scenario with the tenant filled in), runs.json,
transcripts/ (each run as text: who produced each part), scores.json (per run), summary.json (per scenario).
"""
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent              # this copy of the project: its scenarios are used
SCENARIOS = HERE / "dev" / "scenarios"
SEED = HERE / "matters" / "t-test" / "test-001"

QUOTED = re.compile(r"\"[^\"]*\"|“[^”]*”")                  # quoted passages, left out of the word screens
LAW_WORDS = re.compile(r"\b(you|your landlord|the landlord|landlords?|he|she|they|tenants?)\s+(must|may|can|"
                       r"cannot|can't|should|shouldn't|has to|have to|need to|needs to|is required|are required|"
                       r"is entitled|are entitled|is allowed|are allowed|is not allowed|are not allowed)\b"
                       r"|\b(illegal|unlawful|violat(?:ed|es|ing|ion)|forfeit\w*|entitled|your rights)\b", re.I)
OFFER_WORDS = re.compile(r"\b(would you like|do you want me|if you(?:'d| would) like|i can (?:draft|help|"
                         r"prepare|write)|next steps?|you (?:could|might) (?:consider|want))\b", re.I)
FIELD_NAME = re.compile(r"\b[a-z]+(?:_[a-z]+)+\b")          # forwarding_address_given; file names have digits
ISO_DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


# ---- Running: one live session per (scenario, repeat), several at once.

def seed_tenant(project, tenant):
    """Make the tenant id exist (run.py only reuses a tenant it can list), with an m-000 copy of the seed."""
    folder = project / "matters" / tenant / "m-000"
    if not folder.exists():
        shutil.copytree(SEED, folder, ignore=shutil.ignore_patterns("sessions"))
        saved = json.loads((folder / "matter.json").read_text())
        saved.update({"tenant": tenant, "id": "m-000"})
        (folder / "matter.json").write_text(json.dumps(saved, indent=2))


def run_one(project, out, name, rep):
    """One live session. Retried once if it crashed. Returns its line for runs.json."""
    tenant = f"t-eval-{out.name}-{name}-{rep}".replace("_", "-")
    seed_tenant(project, tenant)
    data = json.loads((SCENARIOS / f"{name}.json").read_text())
    data["start"] = [tenant if line == "t-test" else line for line in data["start"]]
    data["start"] = [str(HERE / line) if line == "lease.pdf" else line for line in data["start"]]
    scenario = out / "runs" / f"{name}_r{rep}.json"
    scenario.write_text(json.dumps(data, indent=2))
    screen = out / "runs" / f"{name}_r{rep}.out"
    for attempt in (1, 2):
        with open(screen, "w") as f:
            code = subprocess.run([sys.executable, str(project / "dev" / "live_run.py"), str(scenario)],
                                  cwd=project, stdout=f, stderr=subprocess.STDOUT).returncode
        if code == 0 and "Traceback" not in screen.read_text():
            break
    print(f"  {name} r{rep}: exit {code}, attempt {attempt}", flush=True)
    opened = re.search(r"New matter (\S+) (m-\d+)", screen.read_text())
    matter = project / "matters" / tenant / (opened.group(2) if opened else "none")
    return {"scenario": name, "rep": rep, "tenant": tenant, "matter": str(matter), "screen": str(screen), "exit": code}


def run(out, repeats, names, project, parallel):
    (out / "runs").mkdir(parents=True, exist_ok=True)
    jobs = [(name, rep) for rep in range(1, repeats + 1) for name in names]
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        runs = list(pool.map(lambda job: run_one(project, out, *job), jobs))
    (out / "runs.json").write_text(json.dumps(runs, indent=2))
    score(out)


# ---- Scoring: from the run's matter (its session transcript and events) and its screen.

def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def turns_of(entries):
    """Split a session transcript into chat turns: each starts at a tenant line and holds everything after it
    (model replies and tool calls, tool results, cautions, sheet answers, program notes) up to the next tenant
    line or command."""
    turns, current = [], None
    for e in entries:
        if e["role"] == "tenant":
            current = {"say": e["text"], "entries": []}
            turns.append(current)
        elif e["role"] == "command":
            current = None
        elif current is not None:
            current["entries"].append(e)
    return turns


def spoken_dates(iso):
    """A YYYY-MM-DD date and the ways a reply might write it."""
    y, m, d = iso.split("-")
    month = MONTHS[int(m) - 1]
    return [iso, f"{month} {int(d)}, {y}", f"{month} {int(d)}"]


def measure_turn(turn):
    """What one turn did: tools called, case topics asked for, replies, and the generic measures."""
    replies = [e["text"].strip() for e in turn["entries"] if e["role"] == "model" and (e.get("text") or "").strip()]
    calls = [c for e in turn["entries"] if e["role"] == "model" for c in e.get("tool_calls", [])]
    printed = [d for e in turn["entries"] if e["role"] == "tool" and e["name"] == "get_deadlines"
               for d in ISO_DATE.findall(e["text"])]
    text = "\n".join(replies)
    bare = QUOTED.sub("", text)                       # outside quote marks
    return {
        "say": turn["say"],
        "replies": replies,
        "footers": [e["text"] for e in turn["entries"] if e["role"] == "footer"],   # lines the program printed under a reply
        "called": [c["name"] for c in calls],
        "topics": [c["args"].get("topic") for c in calls if c["name"] == "get_cases"],
        "cautions": [e["text"] for e in turn["entries"] if e["role"] == "check" and "no reply came back" not in e["text"]],
        "law_words": sorted({m.group(0) for m in LAW_WORDS.finditer(bare)}),
        "offer_words": sorted({m.group(0) for m in OFFER_WORDS.finditer(bare)}),
        "field_names": sorted(set(FIELD_NAME.findall(bare))),
        "echo": sorted({iso for iso in set(printed) if any(s in text for s in spoken_dates(iso))}),
    }


def check_expect(expect, matter, events, turns, screen):
    """Each expectation of the scenario: [(what, passed, detail)]."""
    from corpus import playbooks                       # the scored copy's playbooks are this copy's (same issues)
    results = []
    if "issues" in expect:
        active = sorted(i for i in matter.get("issues", []) if i in playbooks)
        results.append(("issues", active == sorted(expect["issues"]), active))
    if "stops" in expect:
        stopped = "None of the situations this tool covers applies" in screen
        results.append(("stops", stopped == expect["stops"], stopped))
    if "not_covered_note" in expect:
        noted = "may not be covered by this tool" in screen
        results.append(("not_covered_note", noted == expect["not_covered_note"], noted))
    for issue in expect.get("deadlines", []):
        got = any(ev["kind"] == "deadlines_computed" and ev.get("issue") == issue and ev.get("clocks") for ev in events)
        results.append((f"deadlines {issue}", got, got))
    if "letters" in expect:
        n = sum(ev["kind"] == "draft" for ev in events)
        results.append(("letters", n == expect["letters"], n))
    for want in expect.get("turns", []):
        found = [t for t in turns if want["say"] in t["say"]]
        if not found:
            results.append((f"turn '{want['say'][:40]}'", False, "the line was never sent"))
            continue
        t = found[0]
        text = "\n".join(t["replies"] + t["footers"])     # what the tenant read: the replies and the program's lines
        for tool in want.get("called", []):
            results.append((f"'{want['say'][:30]}' calls {tool}", tool in t["called"], t["called"]))
        for tool in want.get("not_called", []):
            results.append((f"'{want['say'][:30]}' no {tool}", tool not in t["called"], t["called"]))
        for pattern in want.get("must", []):
            results.append((f"'{want['say'][:30]}' has /{pattern}/", bool(re.search(pattern, text, re.I)), text[:200]))
        for pattern in want.get("must_not", []):           # outside quote marks: a quote may say "forfeits"
            hit = re.search(pattern, QUOTED.sub("", text), re.I)
            results.append((f"'{want['say'][:30]}' lacks /{pattern}/", not hit, hit.group(0) if hit else ""))
        if "topics" in want:
            wrong = [x for x in t["topics"] if x not in want["topics"]]
            results.append((f"'{want['say'][:30]}' topic", bool(t["topics"]) and not wrong, t["topics"]))
    for pattern in expect.get("screen_must_not", []):
        hit = re.search(pattern, screen)
        results.append((f"screen lacks /{pattern}/", not hit, hit.group(0) if hit else ""))
    return results


def transcript_text(entries):
    """The session as text for a person (or a scorer) to read, marking who produced each part."""
    lines = []
    for e in entries:
        role = e["role"]
        if role == "tenant":
            lines.append(f"\nTENANT: {e['text']}")
        elif role == "command":
            lines.append(f"\nTENANT COMMAND (the program answers, not the model): {e['text']}")
        elif role == "sheet":
            lines.append(f"[SHEET, tenant answered] {e.get('question')} -> {e.get('value')}")
        elif role == "program":
            lines.append(f"[PROGRAM NOTE to the model] {e['text'].strip()}")
        elif role == "check":
            lines.append(f"[PROGRAM CAUTION shown to the tenant] {e['text']}")
        elif role == "footer":
            lines.append(f"[PROGRAM LINE printed under the reply] {e['text']}")
        elif role == "tool":
            if e["name"] in ("get_deadlines", "draft_letter"):
                lines.append(f"[PROGRAM PRINTED, from {e['name']}]\n{e['text']}")
            elif e.get("shown"):
                lines.append(f"[PROGRAM PRINTED, from {e['name']}]\n{e['shown']}")
            else:
                lines.append(f"[tool result, not shown to the tenant] {e['name']}: {e['text'][:300]}")
        elif role == "model":
            calls = [f"{c['name']}({json.dumps(c['args'])[:120]})" for c in e.get("tool_calls", [])]
            if calls:
                lines.append(f"[model called] {'; '.join(calls)}")
            if (e.get("text") or "").strip():
                lines.append(f"MODEL REPLY:\n{e['text'].strip()}")
    return "\n".join(lines)


def score_run(entry, scenario, out):
    """Everything measured for one run."""
    matter_dir = Path(entry["matter"])
    screen = Path(entry["screen"]).read_text() if Path(entry["screen"]).exists() else ""
    matter = json.loads((matter_dir / "matter.json").read_text()) if (matter_dir / "matter.json").exists() else {}
    events = read_jsonl(matter_dir / "events.jsonl")
    entries = [e for f in sorted((matter_dir / "sessions").glob("*.jsonl")) for e in read_jsonl(f)] \
        if (matter_dir / "sessions").exists() else []
    turns = turns_of(entries)
    measured = [measure_turn(t) for t in turns]
    expect = check_expect(scenario.get("expect", {}), matter, events, measured, screen)
    (out / "transcripts").mkdir(exist_ok=True)
    (out / "transcripts" / f"{entry['scenario']}_r{entry['rep']}.txt").write_text(transcript_text(entries))
    return {
        **entry,
        "crashed": entry["exit"] != 0 or "Traceback" in screen,
        "expect": [{"what": w, "ok": ok, "got": str(got)[:200]} for w, ok, got in expect],
        "expected_ok": all(ok for _, ok, _ in expect),
        "replies": sum(len(t["replies"]) for t in measured),
        "empty_turns": sum(ev["kind"] == "reply_empty" for ev in events),
        "cautions": sum(len(t["cautions"]) for t in measured),
        "law_screen": sum(bool(t["law_words"]) for t in measured),
        "offer_screen": sum(bool(t["offer_words"]) for t in measured),
        "field_names": sum(bool(t["field_names"]) for t in measured),
        "echo": sum(bool(t["echo"]) for t in measured),
        "footers": sum(len(t["footers"]) for t in measured),
        "turns": measured,
    }


def score(out):
    sys.path.insert(0, str(HERE))                         # corpus, for the playbook issue names
    runs = json.loads((out / "runs.json").read_text())
    scores = [score_run(r, json.loads((SCENARIOS / f"{r['scenario']}.json").read_text()), out) for r in runs]
    (out / "scores.json").write_text(json.dumps(scores, indent=2))
    summary = {}
    for s in scores:
        row = summary.setdefault(s["scenario"], {"runs": 0, "crashed": 0, "expected_ok": 0, "replies": 0,
                                                 "empty_turns": 0, "cautions": 0, "law_screen": 0,
                                                 "offer_screen": 0, "field_names": 0, "echo": 0, "footers": 0,
                                                 "failed": {}})
        row["runs"] += 1
        for key in ("crashed", "expected_ok", "replies", "empty_turns", "cautions", "law_screen", "offer_screen",
                    "field_names", "echo", "footers"):
            row[key] += int(s[key])
        for x in s["expect"]:
            if not x["ok"]:
                row["failed"][x["what"]] = row["failed"].get(x["what"], 0) + 1
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n{'scenario':<28}{'runs':>5}{'ok':>4}{'replies':>8}{'empty':>6}{'caut':>5}{'law?':>5}"
          f"{'offer?':>7}{'field':>6}{'echo':>5}{'footer':>7}")
    for name, row in summary.items():
        print(f"{name:<28}{row['runs']:>5}{row['expected_ok']:>4}{row['replies']:>8}{row['empty_turns']:>6}"
              f"{row['cautions']:>5}{row['law_screen']:>5}{row['offer_screen']:>7}{row['field_names']:>6}"
              f"{row['echo']:>5}{row['footers']:>7}")
        for what, n in row["failed"].items():
            print(f"    failed {n}x: {what}")


if __name__ == "__main__":
    args = sys.argv[1:]
    project = Path(args.pop(args.index("--project") + 1)).resolve() if "--project" in args else HERE
    if "--project" in args:
        args.remove("--project")
    parallel = int(args.pop(args.index("--parallel") + 1)) if "--parallel" in args else 8
    if "--parallel" in args:
        args.remove("--parallel")
    if args[0] == "run":
        out, repeats, names = Path(args[1]).resolve(), int(args[2]), args[3:]
        if not names:
            names = sorted(p.stem for p in SCENARIOS.glob("*.json") if "expect" in json.loads(p.read_text()))
        run(out, repeats, names, project, parallel)
    elif args[0] == "score":
        score(Path(args[1]).resolve())
