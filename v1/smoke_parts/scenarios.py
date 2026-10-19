"""Smoke, part: scenarios and the eval driver (TODO item 115, part 2). Every file in dev/scenarios/ has the conversation format
(a start object, chat lines, confirm rules, expectations dev/eval.py scores, no sheet). dev/live_run.py, with a stand-in model
and a stand-in extraction (no gateway), turns a visit into the screen dev/eval.py reads: the MATTER line first, then TENANT,
MODEL, PROGRAM, and CONFIRM lines; its answer rules (whole words, the longest key, in order) and its end of a confirmation
that cannot be accepted; and dev/eval.py scores that run's matter against expectations. On matters/t-smoke-driver*, removed at
the end. Run by smoke.py, last; each check prints a line, OK or FAIL."""
import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
from pathlib import Path
from langchain.messages import AIMessage
import agent
import record
import visit
from checks import TEST_MATTER, check, make_scratch, remove_scratch
from config import MATTERS, ROOT
from lease import LeaseProfile
from skills import skills
from smoke_parts.common import FORFEIT, StandIn, loads, proposes, said
from visit import Result

sys.path.insert(0, str(ROOT / "dev"))
import live_run                                                      # noqa: E402  (the driver, dev/live_run.py)

spec = importlib.util.spec_from_file_location("dev_eval", ROOT / "dev" / "eval.py")
dev_eval = importlib.util.module_from_spec(spec)                     # the scorer, dev/eval.py (nothing runs at import)
spec.loader.exec_module(dev_eval)

# ---- The scenario files: the new shape, every one.
files = sorted((ROOT / "dev" / "scenarios").glob("*.json"))
scenarios = {f.stem: json.loads(f.read_text()) for f in files}
START_NEW, START_SAVED = {"tenant", "lease", "description"}, {"tenant", "matter", "update"}
OLD_COMMAND = re.compile(r"^(timeline( full)?|issues|bye|drop\b.*)$", re.I)       # the chat commands that went with TODO item 111


def messages_of(scenario):
    """What the tenant types in a scenario: the description or the update, then the chat lines."""
    start = scenario["start"]
    return [start.get("description") or start.get("update", "")] + scenario["chat"]


check("item 115, part 2: every file in dev/scenarios/ has about, start, and chat, optionally confirm and expect, and none has a "
      "sheet",
      files and all(
          {"about", "start", "chat"} <= set(s) <= {"about", "start", "confirm", "chat", "expect"} for s in scenarios.values())
      and not any("sheet" in s for s in scenarios.values()))
check("item 115, part 2: every start is a new matter (tenant, lease, description) whose lease file exists, or a saved one "
      "(tenant, matter, update); a description is words",
      all((set(s["start"]) == START_NEW and s["start"]["lease"].endswith(".pdf") and (ROOT / s["start"]["lease"]).is_file()
           and s["start"]["description"] and s["start"]["description"] == s["start"]["description"].strip())
          or (set(s["start"]) == START_SAVED and s["start"]["matter"].startswith("m-"))
          for s in scenarios.values())
      and all(isinstance(s["start"]["tenant"], str) and s["start"]["tenant"] for s in scenarios.values()))
check("item 115, part 2: every chat is a list of messages, none of them one of the chat commands that are gone",
      all(isinstance(s["chat"], list) and s["chat"] and all(isinstance(m, str) and m.strip() and not OLD_COMMAND.match(m.strip())
                                                            for m in s["chat"]) for s in scenarios.values()))
check("item 115, part 2: every confirm is a mapping of a piece of a fact's label or id to a list of answers",
      all(isinstance(rules, dict) and all(isinstance(k, str) and k and isinstance(v, list) and all(isinstance(a, str) for a in v)
                                          for k, v in rules.items())
          for rules in (s.get("confirm", {}) for s in scenarios.values())))
expects = {name: s["expect"] for name, s in scenarios.items() if "expect" in s}
check("item 115, part 2: every expect (each eval_ scenario has one) uses only the keys dev/eval.py scores (skills, deadlines, "
      "letters, turns, screen_must, screen_must_not), and its turns only the turn keys; skills and deadlines name skills",
      all(set(e) <= set(dev_eval.EXPECT_KEYS) and all(set(t) <= set(dev_eval.TURN_KEYS) and "say" in t for t in e.get("turns", []))
          and all(name in skills for name in e.get("skills", []) + e.get("deadlines", [])) for e in expects.values())
      and all("expect" in s for name, s in scenarios.items() if name.startswith("eval_")))


def regexes_of(e):
    return e.get("screen_must", []) + e.get("screen_must_not", []) + [p for t in e.get("turns", []) for p in t.get("must", []) + t.get("must_not", [])]


try:
    compiled = all(re.compile(p) for e in expects.values() for p in regexes_of(e))
except re.error:
    compiled = False
check("item 115, part 2: every pattern in an expect compiles, and the expectations of the old flow (stops, not_covered_note) are gone",
      compiled and not any({"stops", "not_covered_note", "issues"} & set(e) for e in expects.values()))
check("item 115, part 2: every turn an expect checks is found by a piece of exactly one message, the description (or the update) "
      "or a chat line",
      all(sum(t["say"] in m for m in messages_of(scenarios[name])) == 1 for name, e in expects.items() for t in e.get("turns", [])))
check("item 115, part 2: the scenarios that no skill covers expect no skill and a turn that says so; each other expects the skills "
      "the story needs",
      all(expects[n]["skills"] == [] and any("no skill" in p for p in expects[n]["turns"][0]["must"])
          for n in ("eval_nc_roommate", "eval_nc_towing"))
      and all(expects[n]["skills"] for n in expects if n not in ("eval_nc_roommate", "eval_nc_towing")))

# ---- The driver's answer rules.
row = lambda fact: {"id": fact, "label": fact.replace("_", " "), "suggested": "x"}
rules = {"claim notice date": ["a1", "a2"], "claim notice dated": ["b1"], "notice": ["n1"]}
picked = [live_run.pick_answer(row("claim_notice_dated"), rules), live_run.pick_answer(row("claim_notice_date"), rules),
          live_run.pick_answer(row("claim_notice_dated"), rules), live_run.pick_answer(row("claim_notice_date"), rules),
          live_run.pick_answer(row("claim_notice_date"), rules), live_run.pick_answer(row("other"), rules)]
check("item 115, part 2: the driver's answer rules find a key as whole words in a fact's label or id (\"claim notice date\" is not "
      "found in claim_notice_dated), use the longest key that has answers left, give a key's answers in order, and give "
      "\"\" (accept) when none is left",
      picked == ["b1", "a1", "n1", "a2", "", ""])


class Refusing:
    """A visit whose row can never be accepted as suggested: only a typed answer or a skip is taken."""
    def __init__(self):
        self.answers = []

    def confirm(self, answers):
        (fact, answer), = answers.items()
        self.answers.append(answer)
        return Result() if answer == "?" else Result(rows=[row(fact)], refused={fact: "some words"})


stuck = Refusing()
with contextlib.redirect_stdout(io.StringIO()):
    ended = live_run.confirm_all(stuck, Result(rows=[row("landlord_response")]), {})
check("item 115, part 2: a confirmation whose row cannot be accepted as suggested ends: the empty answer is refused, so the row is "
      "skipped with ?", stuck.answers == ["", "?"] and ended.rows == [])

# ---- The gateway signs: the visit's own caution for a model that could not be reached counts as the gateway's.
try:
    raise ConnectionError("Connection error.")
except ConnectionError as error:
    with contextlib.redirect_stderr(io.StringIO()):
        caution = visit.failed(error)["text"]
check("item 104: dev/eval.py counts as the gateway's the visit's caution for a turn that could not reach the model and the network "
      "errors a traceback names (Connection error, nodename nor servname provided, Client Closed Request)",
      any(sign in caution for sign in dev_eval.GATEWAY_SIGNS)
      and all(sign in dev_eval.GATEWAY_SIGNS for sign in ("Connection error", "nodename nor servname provided", "Client Closed Request")))

# ---- A visit played by the driver, with a stand-in model and a stand-in extraction: the screen, then the scoring.
LEASE_PDF = next(TEST_MATTER.glob("lease_*.pdf"))
PROFILE_TEXT = (TEST_MATTER / "lease_profile.json").read_text()
real_llm, real_extract = agent.agent_llm, agent.extract_profile
agent.extract_profile = lambda pages: LeaseProfile.model_validate_json(PROFILE_TEXT)
description = ("My lease ended July 31, 2026. I moved out on July 28, 2026 and I did not leave early. "
               "The landlord said he would send a check.")
stand_in = iter([
    loads("n1", "deposit_not_returned"),
    proposes("n2", {"vacated": said("2026-07-28", "I moved out on July 28, 2026"),
                    "tenancy_terminated": said("2026-07-31", "My lease ended July 31, 2026"),
                    "early_or_periodic": said(False, "I did not leave early", "inferred"),
                    "landlord_response": said("he would send a check", "he would send a check")}),
    AIMessage(content="That sounds like a deposit question."),
    AIMessage(content="Thank you. The next thing to find out is whether a letter came."),
    AIMessage(content="", tool_calls=[{"name": "get_deadlines", "id": "g1", "args": {}}]), AIMessage(content="Third."),
    AIMessage(content="The statute says it (Fla. Stat. 83.49(3)(a)).")])
scenario = {"start": {"tenant": "t-test", "lease": str(LEASE_PDF), "description": description},
            "confirm": {"tenancy terminated": ["7/30", "7/30/2026"], "early or periodic": ["maybe", "no"],
                        "landlord response": ["?"], "never asked": ["x"]},
            "chat": ["And?", "What now?"]}
tests_before = sorted(p.name for p in (MATTERS / "t-test").glob("m-*"))
remove_scratch("t-smoke-driver")
try:
    agent.agent_llm = StandIn(messages=stand_in)
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        live_run.play(scenario, "t-smoke-driver")                   # the tenant given to --tenant replaces the scenario's
    screen = printed.getvalue()
    marks = re.findall(r"^(MATTER|TENANT|MODEL|PROGRAM \([a-z ]+\)|CONFIRM)(?=[: ])", screen, re.M)
    confirms = re.findall(r"^CONFIRM .*$", screen, re.M)
    folder = MATTERS / "t-smoke-driver" / "m-001"
    saved = json.loads((folder / "matter.json").read_text())
    check("item 115, part 2: the driver's screen starts with the MATTER line of the tenant given to --tenant, not the scenario's, "
          "and the matter is there (and none added for the scenario's tenant)",
          screen.splitlines()[0] == "MATTER: t-smoke-driver/m-001" and folder.is_dir()
          and sorted(p.name for p in (MATTERS / "t-test").glob("m-*")) == tests_before)
    check("item 115, part 2: the driver prints each part marked by who produced it, in order: the tenant's description, the model's "
          "reply, a CONFIRM line and the saved answer for each row, the skipped notice, the model's reply to what was confirmed, "
          "each chat message with the deadlines, the reply, the cited words and the footer after it",
          marks == ["MATTER", "PROGRAM (lease check)", "TENANT", "MODEL",
                    "CONFIRM", "PROGRAM (sheet)", "CONFIRM", "CONFIRM", "PROGRAM (sheet)", "CONFIRM", "CONFIRM", "PROGRAM (sheet)",
                    "CONFIRM", "PROGRAM (notice)", "MODEL", "TENANT", "PROGRAM (deadlines)", "MODEL", "TENANT", "MODEL",
                    "PROGRAM (sources)", "PROGRAM (footer)"]
          and f"\nTENANT: {description}\n" in screen and "\nTENANT: And?\n" in screen
          and "\nMODEL: That sounds like a deposit question.\n" in screen)
    check("item 115, part 2: each CONFIRM line gives the label, the suggestion, and the answer: accepted for an empty one, the typed "
          "answer otherwise (a refused one says what was expected, and is asked again with the next answer), ? for a skip",
          confirms == [
              "CONFIRM vacated: suggested 2026-07-28; answered accepted",
              "CONFIRM tenancy terminated: suggested 2026-07-31; answered 7/30; refused, expected a date like 2026-07-31 or 7/31/2026",
              "CONFIRM tenancy terminated: suggested 2026-07-31; answered 7/30/2026",
              "CONFIRM early or periodic: suggested no; answered maybe; refused, expected yes or no",
              "CONFIRM early or periodic: suggested no; answered no",
              "CONFIRM landlord response: suggested he would send a check; answered ?"]
          and saved["facts"] == {"vacated": "2026-07-28", "tenancy_terminated": "2026-07-30", "early_or_periodic": False}
          and list(saved["proposed"]) == ["landlord_response"])
    check("item 115, part 2: the visit ends when the last message is answered (a session_ended event), a rule with answers left is "
          "said at the end, and no stand-in message is left over or missing (the driver called no gateway model)",
          [json.loads(line)["kind"] for line in (folder / "events.jsonl").read_text().splitlines()][-1] == "session_ended"
          and "Unused confirm answers: {'never asked': ['x']}" in screen
          and next(stand_in, "none") == "none" and "could not be reached" not in screen)

    # ---- dev/eval.py scores that run: the skills from matter.json, the deadlines from events that name the skill, a turn found
    # by a piece of the description, a screen pattern on a CONFIRM line.
    expect = {"skills": ["deposit_not_returned"], "deadlines": ["deposit_not_returned"], "letters": 0,
              "turns": [{"say": "I did not leave early", "must": ["deposit question"]},
                        {"say": "And?", "called": ["get_deadlines"]},
                        {"say": "What now?", "must": [r"83\.49\(3\)\(a\)", "tool's reading"]}],
              "screen_must": ["CONFIRM tenancy terminated: suggested 2026-07-31; answered 7/30/2026"],
              "screen_must_not": ["CONFIRM vacated: suggested 2026-07-30"]}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        (out / "run.out").write_text(screen)
        run = {"scenario": "driver", "rep": 1, "tenant": "t-smoke-driver", "matter": str(folder), "screen": str(out / "run.out"),
               "exit": 0}
        scored = dev_eval.score_run(run, {"expect": expect}, out)
        wrong = dev_eval.score_run(run, {"expect": {**expect, "skills": ["lease_ending"], "deadlines": ["lease_ending"]}}, out)
        transcript = (out / "transcripts" / "driver_r1.txt").read_text()
    check("item 115, part 2: dev/eval.py scores the driver's run: skills read from matter.json, deadlines from the events that name "
          "the skill, a turn found by a piece of the description, patterns on the CONFIRM lines; an expectation that is not met "
          "fails; the run is not marked crashed or gateway trouble",
          scored["expected_ok"] and [x["what"] for x in scored["expect"]][:2] == ["skills", "deadlines deposit_not_returned"]
          and not wrong["expected_ok"] and {x["what"] for x in wrong["expect"] if not x["ok"]} == {"skills", "deadlines lease_ending"}
          and not scored["crashed"] and not scored["gateway_trouble"] and scored["footers"] == 1
          and "[CONFIRMED by the tenant] tenancy terminated -> 2026-07-30" in transcript)
finally:
    agent.agent_llm, agent.extract_profile = real_llm, real_extract
    remove_scratch("t-smoke-driver")
record.session = None

# ---- A saved matter through the driver: the update is the tenant's first message; with no update the chat waits for its first line.
make_scratch("t-smoke-driver-old", skills=["deposit_not_returned"], facts={}, proposed={})
update = "I moved out on July 28, 2026. The landlord said he would send a check."
try:
    agent.extract_profile = real_extract
    agent.agent_llm = StandIn(messages=iter([
        proposes("e1", {"vacated": said("2026-07-28", "I moved out on July 28, 2026")}), AIMessage(content="Noted."),
        AIMessage(content="Next."), AIMessage(content="Answer to the chat."), AIMessage(content="Only after I am asked.")]))
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
        live_run.play({"start": {"tenant": "t-test", "matter": "m-001", "update": update}, "chat": ["And?"]}, "t-smoke-driver-old")
        live_run.play({"start": {"tenant": "t-smoke-driver-old", "matter": "m-001"}, "chat": ["Hello?"]})
    first, second = printed.getvalue().split("MATTER: ")[1:]
    check("item 115, part 2: the driver plays a saved matter: the MATTER line, the update as the tenant's first message, the model's "
          "answer, the confirmation; and with no update the chat starts with the first chat line (no model call before it)",
          first.startswith("t-smoke-driver-old/m-001\n") and f"\nTENANT: {update}\n" in first
          and "\nMODEL: Noted.\n" in first and "CONFIRM vacated: suggested 2026-07-28; answered accepted" in first
          and second.startswith("t-smoke-driver-old/m-001\n") and "\nTENANT: Hello?\n" in second
          and "\nMODEL: Only after I am asked.\n" in second and second.count("TENANT:") == 1)
finally:
    agent.agent_llm, agent.extract_profile = real_llm, real_extract
    remove_scratch("t-smoke-driver-old")
record.session = None
check("the driver's scratch matters are removed", not list(MATTERS.glob("t-smoke-driver*")))
print()
