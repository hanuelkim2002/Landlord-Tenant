"""Live Run: drive run.py through a whole session from a scenario file, the way a tenant would type it.

    python dev/live_run.py dev/scenarios/nonpayment_3day.json

A scenario is a JSON file with three parts:
  "start"  the lines typed before the sheet: new or existing, the tenant id, the lease path, the description
           (or the update), and the empty line that ends it.
  "sheet"  rules for the intake sheet: a piece of a question's text -> a list of answers, used in order, so a
           bad answer then a good one tests that the sheet asks again. When several rules match, the longest
           one with answers left is used. A question no rule matches is skipped with "?". Used for every sheet in the session, including one that appears mid-chat.
  "chat"   the lines typed in the chat, one at a time; "bye" is sent after the last.

It calls the model (run.py does) and writes a real matter under matters/, so use a test tenant (t-test).
The whole screen is printed at the end, followed by the answers the sheet was given.
"""
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent            # the project folder
QUESTION = re.compile(r"([A-Z][^\n>]*?\((?:YYYY-MM-DD|yes/no|amount|words|number or words)\))")


def wait_for_prompt(log, after, process, seconds=600):
    """Wait until the screen has grown past `after` characters and ends with a prompt: "    > " (the sheet)
    or ">> " (the chat), or until run.py has exited (it stops by itself when nothing it covers applies).
    Returns the screen so far."""
    for _ in range(seconds * 5):
        text = log.read_text()
        if len(text) > after and (text.endswith("    > ") or text.endswith(">> ")):
            return text
        if process.poll() is not None:
            return log.read_text()
        time.sleep(0.2)
    raise TimeoutError("run.py did not come back to a prompt")


def answer_sheet(process, log, text, rules, typed):
    """Answer sheet questions by the question on screen until the chat prompt comes back."""
    while text.endswith("    > "):
        question = QUESTION.findall(text)[-1]
        # the longest matching rule that still has answers, so a broad rule cannot take a specific one's question
        matching = sorted((k for k in rules if k in question and rules[k]), key=len, reverse=True)
        answer = rules[matching[0]].pop(0) if matching else "?"
        typed.append((question, answer))
        size = len(text)
        send(process, answer)
        text = wait_for_prompt(log, size, process)
    return text


def send(process, line):
    process.stdin.write(line + "\n")
    process.stdin.flush()


def main(scenario_path):
    scenario = json.loads(Path(scenario_path).read_text())
    rules = {k: list(v) for k, v in scenario["sheet"].items()}
    typed = []
    with tempfile.NamedTemporaryFile("w+", suffix=".log", delete=False) as screen:
        log = Path(screen.name)
        process = subprocess.Popen([sys.executable, "-u", "run.py"], cwd=ROOT, stdin=subprocess.PIPE,
                                   stdout=screen, stderr=subprocess.STDOUT, text=True)
        for line in scenario["start"]:
            send(process, line)
        text = answer_sheet(process, log, wait_for_prompt(log, 0, process), rules, typed)
        for line in scenario["chat"]:
            if process.poll() is not None:                # run.py stopped before the chat
                break
            size = len(text)
            send(process, line)
            text = answer_sheet(process, log, wait_for_prompt(log, size, process), rules, typed)
        if process.poll() is None:
            send(process, "bye")
        process.wait(timeout=60)
    print(log.read_text())
    print("\n--- sheet answers typed")
    for question, answer in typed:
        print(f"  {answer!r:<45} <- {question[:80]}")
    print("unused answers:", {k: v for k, v in rules.items() if v})
    log.unlink()


if __name__ == "__main__":
    main(sys.argv[1])
