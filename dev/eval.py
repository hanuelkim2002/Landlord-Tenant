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
                     "topics" (the get_cases topics allowed in that turn; any other topic fails),
                     "applied" (true: a reply in the turn applies the law, APPLIED, not quotes alone),
                     "cases_used" (true: a reply names a case the turn's get_cases result gave)
  "screen_must"      regexes the whole screen must match (a lease clause shown at the stop, e.g.)
  "screen_must_not"  regexes the whole screen must not match (a wrong suggestion on the sheet, e.g.)
Every reply is also measured, whatever the scenario: empty turns (reply_empty events), program cautions
(quote_flagged and cite_flagged events), field names (a snake_case id outside quote marks), deadline echo (a
date the program printed in the same turn, repeated in the reply), quotes only (a reply with a quote and fewer
than APPLIED_WORDS words outside quote marks: the law set out and not applied), dates made (a date with a year,
outside quote marks, that is in no fact, no tenant line, no printed deadline, and is not the session's day),
cases not given (a "Name v. Name" in a reply that no get_cases result in the session holds), and two word
screens that mark a reply for a person to read: CHOOSE_WORDS (you should, your best option, I recommend ...)
and OFFER_WORDS (would you like me to ...). The screens find candidates; they are not verdicts. Since
2026-10-02 (TODO item 49) the tool applies the law, so the old LAW_WORDS screen (a party and must, may, can,
entitled ...) is gone: those words are now the point of an answer. A run with signs that the
gateway failed (GATEWAY_SIGNS, or two unrecovered empty turns in a row) is marked gateway_trouble ("gw"). A turn's "must" patterns
are matched against what the tenant read, the replies and any line the program printed under them (footer);
"footers" counts those lines, so the model's own lines and the program's can be told apart.

Output in <out dir> (dev/eval_runs/<name> is ignored by git): matters/ (each run's matter.json, events, and
transcript, copied out; the scratch tenant is then removed from the project's matters/), runs/ (each run's screen, a crashed first attempt's too, and its scenario with the tenant filled in), runs.json,
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
# Choosing for the tenant, which an applied answer never does (README, Purpose): it lays out the options.
CHOOSE_WORDS = re.compile(r"(?<!what )(?<!whether )\byou should\b|\byour best (option|choice|move|bet)\b|"
                          r"\bI (would )?(recommend|suggest|advise)\b|\bthe best (thing|option|choice) (is|would be)\b",
                          re.I)
# An applied answer: a quote, and enough words of the model's own around it to apply it to the tenant. A list of
# quotes with "This tool does not decide that." has a handful (the page's "what can I do to sue" answer, 6).
APPLIED_WORDS = 40
SOURCE_LABEL = re.compile(r"Fla\. Stat\. [\d.()a-z]+|Lease Section [\d.]+(?:, page \d+)?|\(at \d+\)", re.I)
CASE_NAME = re.compile(r"\b[A-Z][A-Za-z.&'’]+(?: [A-Z][A-Za-z.&'’]+)* v\. [A-Z][A-Za-z.&'’]+")
OFFER_WORDS = re.compile(r"\b(would you like|do you want me|if you(?:'d| would) like|i can (?:draft|help|"
                         r"prepare|write)|next steps?|you (?:could|might) (?:consider|want))\b", re.I)
FIELD_NAME = re.compile(r"\b[a-z]+(?:_[a-z]+)+\b")          # forwarding_address_given; file names have digits
ISO_DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
SPOKEN_DATE = re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
                         r" (\d{1,2}),? (20\d\d)\b")
SLASH_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d\d)\b")
# Signs that the gateway, not the model, failed a run: run.py never came back (the driver's timeout), an empty
# answer where JSON was expected, or two turns in a row the model left empty even after the retry. The eval of
# 2026-10-01 hit an eight-minute stretch of these; such runs are counted apart, not as the model's slips.
GATEWAY_SIGNS = ("run.py did not come back to a prompt", "Expecting value: line 1 column 1 (char 0)")
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
        if attempt == 1:                                  # kept, so the cause of a crash can be read later
            screen.rename(screen.with_name(screen.stem + "_attempt1.out"))
    print(f"  {name} r{rep}: exit {code}, attempt {attempt}", flush=True)
    opened = re.search(r"New matter (\S+) (m-\d+)", screen.read_text())
    matter = project / "matters" / tenant / (opened.group(2) if opened else "none")
    return {"scenario": name, "rep": rep, "tenant": tenant, "matter": str(matter), "screen": str(screen), "exit": code}


KEPT = ("matter.json", "events.jsonl", "sessions")        # what scoring reads; the lease copy stays behind


def file_away(project, out, runs):
    """Copy what scoring reads from each run's matter into <out dir>/matters/, then remove the scratch tenant
    from the project's matters/ (only a t-eval- tenant, like smoke.py's t-smoke- ones), so run.py's list of
    tenants is as it was before the eval. Points each run at its copy."""
    for r in runs:
        src = Path(r["matter"])
        dest = out / "matters" / r["tenant"] / src.name
        dest.mkdir(parents=True, exist_ok=True)
        for name in KEPT:
            if (src / name).is_dir():
                shutil.copytree(src / name, dest / name, dirs_exist_ok=True)
            elif (src / name).exists():
                shutil.copy(src / name, dest / name)
        if r["tenant"].startswith("t-eval-"):
            shutil.rmtree(project / "matters" / r["tenant"], ignore_errors=True)
        r["matter"] = str(dest)


def run(out, repeats, names, project, parallel):
    (out / "runs").mkdir(parents=True, exist_ok=True)
    jobs = [(name, rep) for rep in range(1, repeats + 1) for name in names]
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        runs = list(pool.map(lambda job: run_one(project, out, *job), jobs))
    file_away(project, out, runs)
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


def dates_in(text):
    """Every full date in a text (2026-07-31, July 31, 2026, 7/31/2026) as YYYY-MM-DD."""
    found = set(ISO_DATE.findall(text))
    found |= {f"{y}-{MONTHS.index(m) + 1:02d}-{int(d):02d}" for m, d, y in SPOKEN_DATE.findall(text)}
    found |= {f"{y}-{int(m):02d}-{int(d):02d}" for m, d, y in SLASH_DATE.findall(text)}
    return found


def own_words(text):
    """How many words a reply has outside quote marks and source labels: the model's own."""
    return len(SOURCE_LABEL.sub(" ", QUOTED.sub(" ", text)).split())


def quotes_only(reply):
    """A reply with a quote of 20 characters or more and fewer than APPLIED_WORDS words of its own."""
    return any(len(q) >= 22 for q in QUOTED.findall(reply)) and own_words(reply) < APPLIED_WORDS


def applied(reply):
    """A reply that quotes and applies: a quote, APPLIED_WORDS words or more of its own, addressed to the tenant."""
    return (any(len(q) >= 22 for q in QUOTED.findall(reply)) and own_words(reply) >= APPLIED_WORDS
            and re.search(r"\byou(r)?\b", QUOTED.sub(" ", reply), re.I) is not None)


def measure_turn(turn, known_dates=frozenset(), fetched=""):
    """What one turn did: tools called, case topics asked for, replies, and the generic measures. known_dates:
    every date the record holds (facts, the tenant's lines, printed deadlines, the session's days); fetched:
    every get_cases result in the session up to and including this turn."""
    replies = [e["text"].strip() for e in turn["entries"] if e["role"] == "model" and (e.get("text") or "").strip()]
    calls = [c for e in turn["entries"] if e["role"] == "model" for c in e.get("tool_calls", [])]
    printed = [d for e in turn["entries"] if e["role"] == "tool" and e["name"] == "get_deadlines"
               for d in ISO_DATE.findall(e.get("shown") or e["text"])]
    text = "\n".join(replies)
    bare = QUOTED.sub("", text)                       # outside quote marks
    this_turn_cases = "\n".join((e.get("text") or "") for e in turn["entries"]
                                if e["role"] == "tool" and e["name"] == "get_cases")
    return {
        "say": turn["say"],
        "replies": replies,
        "footers": [e["text"] for e in turn["entries"] if e["role"] == "footer"],   # lines the program printed under a reply
        "called": [c["name"] for c in calls],
        "topics": [c["args"].get("topic") for c in calls if c["name"] == "get_cases"],
        "cautions": [e["text"] for e in turn["entries"] if e["role"] == "check" and "no reply came back" not in e["text"]],
        "choose_words": sorted({m.group(0) for m in CHOOSE_WORDS.finditer(bare)}),
        "quotes_only": sum(quotes_only(r) for r in replies),
        "applied": any(applied(r) for r in replies),
        "dates_made": sorted(dates_in(bare) - set(known_dates)),
        "cases_not_given": sorted({m.group(0) for m in CASE_NAME.finditer(text) if m.group(0) not in fetched}),
        "cases_used": sorted({m.group(0) for m in CASE_NAME.finditer(text) if m.group(0) in this_turn_cases}),
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
        if want.get("applied"):
            results.append((f"'{want['say'][:30]}' applied", t["applied"], t["replies"][-1][:200] if t["replies"] else ""))
        if want.get("cases_used"):
            results.append((f"'{want['say'][:30]}' uses its cases", bool(t["cases_used"]), t["cases_used"]))
        if "topics" in want:
            wrong = [x for x in t["topics"] if x not in want["topics"]]
            results.append((f"'{want['say'][:30]}' topic", bool(t["topics"]) and not wrong, t["topics"]))
    for pattern in expect.get("screen_must", []):
        results.append((f"screen has /{pattern}/", bool(re.search(pattern, screen)), ""))
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
        elif role == "printed":
            lines.append(f"[PROGRAM PRINTED, outside the chat]\n{e['text']}")
        elif role == "tool":
            if e["name"] in ("get_deadlines", "draft_letter"):
                lines.append(f"[PROGRAM PRINTED, from {e['name']}]\n{e.get('shown') or e['text']}")
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
    # every date the record holds: confirmed facts, the tenant's words (description, updates, chat), sheet
    # answers, printed deadlines, and the session's own days (a reply may say today's date)
    known = set()
    for value in matter.get("facts", {}).values():
        known |= dates_in(str(value))
    known |= dates_in(matter.get("description", "")) | {e["when"][:10] for e in entries if e.get("when")}
    known |= set().union(*(dates_in(ev.get("text", "")) for ev in events if ev["kind"] == "tenant_update"), set())
    for e in entries:
        if e["role"] in ("tenant", "sheet") or (e["role"] == "tool" and e.get("name") == "get_deadlines"):
            known |= dates_in(" ".join(str(e.get(k) or "") for k in ("text", "shown", "value", "typed")))
    measured, fetched = [], ""
    for t in turns:
        fetched += "\n".join((e.get("text") or "") for e in t["entries"] if e["role"] == "tool" and e["name"] == "get_cases")
        measured.append(measure_turn(t, frozenset(known), fetched))
    unrecovered = [not t["replies"] and any(e["role"] == "check" and "no reply came back" in e["text"]
                                            for e in turn["entries"]) for t, turn in zip(measured, turns)]
    gateway = any(sign in screen for sign in GATEWAY_SIGNS) or any(a and b for a, b in zip(unrecovered, unrecovered[1:]))
    expect = check_expect(scenario.get("expect", {}), matter, events, measured, screen)
    (out / "transcripts").mkdir(exist_ok=True)
    (out / "transcripts" / f"{entry['scenario']}_r{entry['rep']}.txt").write_text(transcript_text(entries))
    return {
        **entry,
        "crashed": entry["exit"] != 0 or "Traceback" in screen,
        "gateway_trouble": gateway,
        "expect": [{"what": w, "ok": ok, "got": str(got)[:200]} for w, ok, got in expect],
        "expected_ok": all(ok for _, ok, _ in expect),
        "replies": sum(len(t["replies"]) for t in measured),
        "empty_turns": sum(ev["kind"] == "reply_empty" for ev in events),
        "cautions": sum(len(t["cautions"]) for t in measured),
        "quotes_only": sum(t["quotes_only"] for t in measured),
        "choose_screen": sum(bool(t["choose_words"]) for t in measured),
        "dates_made": sum(bool(t["dates_made"]) for t in measured),
        "cases_not_given": sum(bool(t["cases_not_given"]) for t in measured),
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
        row = summary.setdefault(s["scenario"], {"runs": 0, "crashed": 0, "gateway_trouble": 0, "expected_ok": 0, "replies": 0,
                                                 "empty_turns": 0, "cautions": 0, "quotes_only": 0, "choose_screen": 0,
                                                 "dates_made": 0, "cases_not_given": 0,
                                                 "offer_screen": 0, "field_names": 0, "echo": 0, "footers": 0,
                                                 "failed": {}})
        row["runs"] += 1
        for key in ("crashed", "gateway_trouble", "expected_ok", "replies", "empty_turns", "cautions", "quotes_only",
                    "choose_screen", "dates_made", "cases_not_given", "offer_screen", "field_names", "echo", "footers"):
            row[key] += int(s[key])
        for x in s["expect"]:
            if not x["ok"]:
                row["failed"][x["what"]] = row["failed"].get(x["what"], 0) + 1
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n{'scenario':<28}{'runs':>5}{'gw':>4}{'ok':>4}{'replies':>8}{'empty':>6}{'caut':>5}{'qonly':>6}"
          f"{'choose?':>8}{'dates':>6}{'cases':>6}{'offer?':>7}{'field':>6}{'echo':>5}{'footer':>7}")
    for name, row in summary.items():
        print(f"{name:<28}{row['runs']:>5}{row['gateway_trouble']:>4}{row['expected_ok']:>4}{row['replies']:>8}{row['empty_turns']:>6}"
              f"{row['cautions']:>5}{row['quotes_only']:>6}{row['choose_screen']:>8}{row['dates_made']:>6}"
              f"{row['cases_not_given']:>6}{row['offer_screen']:>7}{row['field_names']:>6}{row['echo']:>5}{row['footers']:>7}")
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
