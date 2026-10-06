"""Replay harness for the student simulation of 2026-10-06 (README.md beside this folder). Runs the real run.py, with every model call answered from a file.

    python harness.py RUN status            replay, then say what is needed next
    python harness.py RUN type "TEXT"       the tenant types TEXT and presses Enter (each line of TEXT is one Enter;
                                            "" is Enter on an empty line), then replay
    python harness.py RUN respond FILE      the stand-in model's answer to the pending request, then replay.
                                            FILE is JSON: {"content": "...", "tool_calls": [{"name": "...", "args": {...}}]}
    python harness.py RUN screen [N]        the tenant's screen (the last N characters)

RUN is a folder holding run.json ({"lease": path, "profile": path, "tenant": id}; paths relative to RUN), and, written here: inputs.json
(what the tenant typed), model.jsonl (the stand-in model's answers, in order), screen.txt (what the tenant sees:
run.py's output without the developer's diagnostic lines), screen_full.txt, status.json, and model/ (the pending
request, the system prompts, the tool list).

Every command replays the whole session from the start in a fresh interpreter, on a fresh matter folder inside RUN,
with the same typed lines and the same model answers, so the program's state is rebuilt exactly; the date is fixed
at 2026-10-06. Nothing is written to the repository's matters/.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]                  # the project folder
TODAY = date(2026, 10, 6)
DIAGNOSTIC = re.compile(r"^(p\s*\d+\s+\d+ chars\s+\S+|sha256 \S+\s+pages \d+|\s*(OK  |FAIL|--  |\?\?  ) ?\S+.*|proposed: \[.*|"
                        r"issues: \[.*\| playbooks: .*|\s*dropped \S+: no supporting quote or tag|new issues: .*)$")


# ---------------------------------------------------------------- the outer commands

def load(run, name, default):
    path = run / name
    return json.loads(path.read_text()) if path.exists() else default


def replay(run):
    old = (run / "screen.txt").read_text() if (run / "screen.txt").exists() else ""
    subprocess.run([sys.executable, __file__, str(run), "_replay"], cwd=REPO)
    status = load(run, "status.json", {})
    new = (run / "screen.txt").read_text()
    shared = os.path.commonprefix([old, new])
    return status, new[len(shared):] if len(shared) >= len(old) - 40 else new


def report(status, new_text):
    print("----- new on the tenant's screen -----")
    print(new_text.rstrip() or "(nothing new)")
    print("--------------------------------------")
    need = status.get("need")
    if need == "input":
        print(f"NEED_INPUT: the program waits for the tenant to type at the prompt {status.get('prompt')!r}")
    elif need == "model":
        print(f"NEED_MODEL: request {status.get('request')} is pending; read model/pending.txt")
    elif need == "done":
        print("DONE: the session has ended")
    else:
        print("ERROR:", status.get("error", "unknown"))


def main():
    run = Path(sys.argv[1]).resolve()
    command = sys.argv[2]
    if command == "_replay":
        return inner(run)
    if command == "screen":
        text = (run / "screen.txt").read_text()
        n = int(sys.argv[3]) if len(sys.argv) > 3 else len(text)
        print(text[-n:])
        return
    if command == "type":
        inputs = load(run, "inputs.json", [])
        inputs += sys.argv[3].split("\n") if sys.argv[3] else [""]
        (run / "inputs.json").write_text(json.dumps(inputs, indent=1))
    elif command == "respond":
        answer = json.loads(Path(sys.argv[3]).read_text())
        assert isinstance(answer.get("content", ""), str), "content must be a string"
        for tc in answer.get("tool_calls", []):
            assert "name" in tc and isinstance(tc.get("args", {}), dict), "each tool call needs a name and args {}"
        status = load(run, "status.json", {})
        assert status.get("need") == "model", "no model request is pending"
        with open(run / "model.jsonl", "a") as f:
            f.write(json.dumps(answer) + "\n")
    elif command != "status":
        sys.exit(__doc__)
    report(*replay(run))


# ---------------------------------------------------------------- the replay, inside a fresh interpreter

def inner(run):
    settings = json.loads((run / "run.json").read_text())
    inputs = list(json.loads((run / "inputs.json").read_text())) if (run / "inputs.json").exists() else []
    inputs = ["new", "", str((run / settings["lease"]).resolve())] + inputs                 # the door, a new tenant, the lease's path
    answers = [json.loads(l) for l in (run / "model.jsonl").read_text().splitlines() if l.strip()] \
        if (run / "model.jsonl").exists() else []
    (run / "model").mkdir(exist_ok=True)
    (run / "status.json").unlink(missing_ok=True)

    os.chdir(REPO)
    sys.path.insert(0, str(REPO))
    os.environ["WIKI_UNVERIFIED"] = "1"                              # as in the author's evals: unverified case pages shown, marked

    screen_parts = []

    class Screen:
        def write(self, s):
            screen_parts.append(s)
            return len(s)

        def flush(self):
            pass

    real_stdout = sys.stdout
    sys.stdout = Screen()

    def finish(status):
        full = "".join(screen_parts)
        (run / "screen_full.txt").write_text(full)
        (run / "screen.txt").write_text("\n".join(l for l in full.split("\n") if not DIAGNOSTIC.match(l)))
        (run / "status.json").write_text(json.dumps(status))
        real_stdout.flush()
        os._exit(0)

    import builtins

    def fake_input(prompt=""):
        sys.stdout.write(prompt)
        if inputs:
            line = inputs.pop(0)
            sys.stdout.write(line + "\n")
            return line
        finish({"need": "input", "prompt": prompt})

    builtins.input = fake_input

    import config
    matters = run / "matters"
    shutil.rmtree(matters, ignore_errors=True)
    matters.mkdir()
    config.MATTERS = matters
    config.uf_api_key = "stand-in"

    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatGeneration, ChatResult
    from langchain_core.utils.function_calling import convert_to_openai_tool

    state = {"n": 0, "tools": []}

    def render(messages):
        lines = []
        for i, m in enumerate(messages):
            if m.type == "system":
                continue
            if m.type == "human" and not any(x.type == "system" for x in messages):
                lines.append(f"[{i}] THE PROGRAM'S PROMPT:\n{m.content}")
            elif m.type == "human":
                lines.append(f"[{i}] HUMAN (the tenant's message, with any program note in front):\n{m.content}")
            elif m.type == "ai":
                calls = "".join(f"\n    tool call: {tc['name']}({json.dumps(tc['args'])})" for tc in m.tool_calls)
                lines.append(f"[{i}] YOU (your earlier answer):\n{m.content}{calls}")
            elif m.type == "tool":
                lines.append(f"[{i}] TOOL RESULT from {m.name}:\n{m.content}")
            else:
                lines.append(f"[{i}] {m.type}:\n{m.content}")
        return "\n\n".join(lines)

    def dump(n, messages):
        out = run / "model"
        system = next((m.content for m in messages if m.type == "system"), None)
        head = [f"REQUEST {n}"]
        if system is None:
            head.append("KIND: a one-shot prompt (the program's own prompt; no system prompt, no tools). "
                        "Answer with \"content\" only, exactly as the prompt asks.")
        else:
            last = sorted(out.glob("system_*.txt"), key=lambda p: int(p.stem.split("_")[1]))
            same = last and last[-1].read_text() == system
            if same:
                head.append(f"KIND: a chat call. SYSTEM PROMPT: unchanged, still {last[-1].name}")
            else:
                (out / f"system_{n}.txt").write_text(system)
                head.append(f"KIND: a chat call. SYSTEM PROMPT: NEW, read model/system_{n}.txt"
                            + (f" (it changed since {last[-1].name})" if last else ""))
            head.append("TOOLS you may call: model/tools.txt")
            (out / "tools.txt").write_text("\n\n".join(json.dumps(t, indent=1) for t in state["tools"]))
        head.append("=" * 60)
        text = "\n".join(head) + "\n" + render(messages)
        (out / f"request_{n}.txt").write_text(text)
        (out / "pending.txt").write_text(text)

    class FileModel(BaseChatModel):
        @property
        def _llm_type(self):
            return "file stand-in"

        def bind_tools(self, tools, **kwargs):
            state["tools"] = [convert_to_openai_tool(t) for t in tools]
            return self

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            n = state["n"]
            state["n"] += 1
            if n < len(answers):
                a = answers[n]
                calls = [{"name": tc["name"], "args": tc.get("args", {}), "id": f"call_{n}_{k}", "type": "tool_call"}
                         for k, tc in enumerate(a.get("tool_calls", []))]
                message = AIMessage(content=a.get("content", ""), tool_calls=calls,
                                    response_metadata={"finish_reason": "stop"})
                return ChatResult(generations=[ChatGeneration(message=message)])
            dump(n, messages)
            finish({"need": "model", "request": n})

    profile_json = (run / settings["profile"]).read_text()

    class ExtractStandIn(BaseChatModel):
        @property
        def _llm_type(self):
            return "extraction stand-in"

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=profile_json))])

    config.agent_llm = FileModel()
    config.extract_llm = ExtractStandIn()

    import record
    record.new_tenant_id = lambda: settings.get("tenant", "t-student")

    class Today(date):
        @classmethod
        def today(cls):
            return TODAY

    import prompt
    import timeline
    import tools
    for module in (prompt, timeline, tools):
        module.date = Today

    import runpy
    try:
        runpy.run_path(str(REPO / "run.py"), run_name="__main__")
    except SystemExit:
        pass
    except Exception as e:                                           # noqa: BLE001
        import traceback
        sys.stdout.write("\n" + traceback.format_exc())
        finish({"need": "error", "error": f"{type(e).__name__}: {e}"})
    finish({"need": "done"})


if __name__ == "__main__":
    main()
