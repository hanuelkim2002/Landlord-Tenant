"""Runs one skill version on the five deposit stories, three times each, as v2's chat will: the rules, the lease, the
confirmed facts, and the skill already loaded; tools count_days, get_statute_section, and (method C) read_skill_details.
Throwaway: deleted once a format is chosen. Run from this folder: python run.py A   (or B, C, v1)
"""
import json
import os
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

HERE = Path(__file__).resolve().parent.parent                  # comparisons/skills/
V2 = HERE.parents[1]
ENV_FILE = Path(os.environ.get("UF_ENV", V2 / ".env"))
MODEL = "nemotron-3-super-120b-a12b"
RUNS, MAX_STEPS = 3, 8
SKILL_FILES = {"A": HERE / "versions/A_checklist.md", "B": HERE / "versions/B_examples.md",
               "C": HERE / "versions/C_core.md", "v1": V2.parent / "v1/skills/deposit_not_returned.md"}

RULES = """You help a tenant in Florida with a dispute with their landlord, under Fla. Stat. ch. 83, part II.

1. Apply the law to the tenant's facts and give an answer, not a list of quotes.
2. Answer what was asked first. When asked "can I ...", say whether they can before giving any step.
3. Know what you know. Each point the answer turns on is one of these: known (a confirmed fact, a lease clause you read, the statute), something the tenant can tell you, something they must check, unsettled, or outside the tool. Never state a gap as a fact, and never assume a fact you haven't been given. Say how an unknown would change the answer.
4. An open question stays open: give the reading on each side.
5. Ask the tenant only plain facts (what happened, when, how something was sent, what a paper says). Never ask whether something meets a legal term.
6. Cite each rule to its source: a statute section and subsection, or the lease.
7. Dates come only from count_days. Never add, subtract, or compare dates yourself.
8. End with the one question your answer needs, if any. Don't offer help the tenant didn't ask for, and never repeat an offer.

Reading the lease:
1. THE LEASE below is the tenant's whole lease. Read all of it before you say whether it covers a point.
2. Say the lease does not address a point only if no part of it does. If a clause comes close but does not settle the point, say what it does say.
3. Quote the lease's own words, and cite the section number, or the page when there is none.
4. A choice in the lease counts only if it is marked: a checked box, or initials on the line. An unchecked box or a blank initials line was not chosen."""

TOOLS = [
    {"type": "function", "function": {
        "name": "count_days",
        "description": "The only date math. Takes a confirmed fact holding a date and a number of days (negative for "
                       "a deadline before the date); returns the date and whether it has passed.",
        "parameters": {"type": "object", "properties": {
            "fact": {"type": "string", "description": "The name of a confirmed fact holding a date, like lease_end_date"},
            "days": {"type": "integer"}}, "required": ["fact", "days"]}}},
    {"type": "function", "function": {
        "name": "get_statute_section",
        "description": "The full text of one section of Fla. Stat. ch. 83, part II, like 83.49.",
        "parameters": {"type": "object", "properties": {"section": {"type": "string"}}, "required": ["section"]}}}]
DETAILS_TOOL = {"type": "function", "function": {
    "name": "read_skill_details",
    "description": "Read the details file of the loaded skill: the statute's exact words, the open questions, and the "
                   "mistakes to avoid.",
    "parameters": {"type": "object", "properties": {}}}}


def skill_body(method):
    """The skill as the model gets it once loaded: the text after its header."""
    text = SKILL_FILES[method].read_text()
    return text.split("---", 2)[2].strip() if text.startswith("---") else text


def count_days(story, fact, days):
    """The confirmed date of the fact plus the days, and whether that date has passed on the story's today."""
    value = story["facts"].get(str(fact), "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)):
        dated = [k for k, v in story["facts"].items() if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(v))]
        return f"No confirmed date named {fact}. Confirmed dates: {', '.join(dated)}."
    due = date.fromisoformat(value) + timedelta(days=int(days))
    today = date.fromisoformat(story["today"])
    status = "has passed" if due < today else "is today" if due == today else "has not passed"
    return (f"{fact} ({value}) {'+' if int(days) >= 0 else '-'} {abs(int(days))} days = {due.isoformat()}, which "
            f"{status}. Counted in calendar days, the start day not counted, with no weekend or holiday shift; this "
            f"way of counting has not been checked against the statute yet.")


def run_tool(method, story, name, arguments):
    """One tool call's result."""
    if name == "count_days":
        return count_days(story, arguments.get("fact"), arguments.get("days", 0))
    if name == "get_statute_section":
        path = V2 / "statutes" / f"{str(arguments.get('section', '')).strip()}.txt"
        return path.read_text() if path.exists() else "No such section in statutes/."
    if name == "read_skill_details" and method == "C":
        return (HERE / "versions/C_details.md").read_text()
    return f"No tool named {name}."


TEXT_CALL = re.compile(r"<function=([\w-]+)>(.*?)</function>", re.S)
TEXT_PARAMETER = re.compile(r"<parameter=([\w-]+)>\s*(.*?)\s*</parameter>", re.S)


def text_calls(content):
    """Tool calls nemotron wrote as text instead of making them, as [(name, arguments)]."""
    calls = []
    for name, inner in TEXT_CALL.findall(content or ""):
        arguments = {}
        for key, value in TEXT_PARAMETER.findall(inner):
            try:
                arguments[key] = json.loads(value)
            except json.JSONDecodeError:
                arguments[key] = value
        calls.append((name, arguments))
    return calls


def ask(gateway, method, story):
    """One story in a fresh chat; the tool loop runs until the model answers. Returns the answer, calls, seconds."""
    facts = "\n".join(f"- {k}: {v}" for k, v in story["facts"].items())
    system = (f"{RULES}\n\nTHE LEASE:\n{(HERE / 'lease.txt').read_text()}\n\nCONFIRMED FACTS (the tenant confirmed "
              f"these):\n{facts}\n\nLOADED SKILLS:\n{skill_body(method)}")
    tools = TOOLS + ([DETAILS_TOOL] if method == "C" else [])
    messages = [{"role": "system", "content": system}, {"role": "user", "content": story["message"]}]
    calls, content, start = [], "", time.perf_counter()
    for step in range(MAX_STEPS + 1):
        request = {"model": MODEL, "messages": messages, "temperature": 0, "max_tokens": 8000, "tools": tools}
        if step == MAX_STEPS:
            request["tool_choice"] = "none"                    # out of rounds: answer from what was read
        message = gateway.chat.completions.create(**request).choices[0].message
        content = message.content or ""
        written = [] if message.tool_calls else text_calls(content)
        if message.tool_calls:
            messages.append({"role": "assistant", "content": content,
                             "tool_calls": [c.model_dump() for c in message.tool_calls]})
            for c in message.tool_calls:
                arguments = json.loads(c.function.arguments or "{}")
                calls.append({"name": c.function.name, "arguments": arguments})
                messages.append({"role": "tool", "tool_call_id": c.id,
                                 "content": run_tool(method, story, c.function.name, arguments)})
        elif written and step < MAX_STEPS:
            messages.append({"role": "assistant", "content": content})
            for name, arguments in written:
                calls.append({"name": name, "arguments": arguments})
                messages.append({"role": "user", "content": f"Result of {name}:\n{run_tool(method, story, name, arguments)}"})
        else:
            break
    answer = re.sub(r"<think>.*?</think>", "", content, flags=re.S).strip()
    return {"answer": answer, "tool_calls": calls, "seconds": round(time.perf_counter() - start, 1)}


if __name__ == "__main__":
    method = sys.argv[1]
    gateway = OpenAI(base_url="https://api.ai.it.ufl.edu/v1", api_key=dotenv_values(ENV_FILE)["UF_API_KEY"])
    stories = json.loads((HERE / "stories.json").read_text())["stories"]
    out = HERE / "results" / f"{method}.jsonl"
    out.parent.mkdir(exist_ok=True)
    done = {(r["story"], r["run"]) for r in map(json.loads, out.read_text().splitlines())} if out.exists() else set()
    for run in range(1, RUNS + 1):
        for story in stories:
            if (story["id"], run) in done:
                continue
            result = None
            for attempt in range(3):                               # a dropped connection is tried again
                try:
                    result = ask(gateway, method, story)
                    break
                except Exception as error:
                    print(f"retrying {story['id']}: {error}", file=sys.stderr)
                    time.sleep(10)
            if result is None:                                     # three failures: leave it for a rerun
                continue
            with out.open("a") as f:
                f.write(json.dumps({"method": method, "story": story["id"], "run": run, **result}) + "\n")
            print(method, story["id"], run, result["seconds"], "s", len(result["tool_calls"]), "calls", flush=True)
