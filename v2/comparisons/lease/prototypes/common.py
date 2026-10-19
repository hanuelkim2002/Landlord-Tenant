"""The part every lease method shares, so the method is the only difference: the questions, the instruction, the
model, the tool loop, the clause splitter (B and C), and how results and intake times are written.
Throwaway: this folder is deleted once a method is chosen.
"""
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

LEASE_DIR = Path(__file__).resolve().parent.parent          # comparisons/lease/
RESULTS = LEASE_DIR / "results"
ENV_FILE = Path(os.environ.get("UF_ENV", LEASE_DIR.parent.parent / ".env"))
MODEL = "nemotron-3-super-120b-a12b"
MAX_STEPS = 8                                                # tool rounds before the model must answer
INSTRUCTION = ("Answer the tenant's question from the lease only. If the lease does not address it, say so. Reply in "
               "JSON: {\"answer\": \"...\", \"quotes\": [\"...\"]}. \"quotes\" are the lease's exact words your "
               "answer rests on.")
LEASES = ["short_headings", "long_numbered", "scanned", "broken_text", "sample_v1"]


def client():
    """The UF gateway, with the key read from .env (never printed)."""
    return OpenAI(base_url="https://api.ai.it.ufl.edu/v1", api_key=dotenv_values(ENV_FILE)["UF_API_KEY"])


def questions():
    """The 64 questions of the answer key."""
    return json.loads((LEASE_DIR / "answer_key.json").read_text())["questions"]


def lease_pages(name):
    """Step 1's text of one lease: [{"page": 1, "text": ...}], the same text for methods A, B, and C."""
    return json.loads((LEASE_DIR / "texts" / f"{name}.json").read_text())["pages"]


# ---- The clause splitter (B and C use the same clauses)

NUMBERED = re.compile(r"^((?:[A-Z]-)?\d{1,2}(?:\.\d{1,3})*\.)\s+([A-Z][^.]{0,60}\.)?")   # "4.2. Due Date." "8. PETS."
SMALL_WORDS = {"of", "the", "and", "to", "a", "an", "in", "for", "on", "or", "by"}


def repeated_lines(pages):
    """Lines that recur on many pages (running headers and footers), digits ignored, so they are not headings."""
    counts = {}
    for page in pages:
        for line in {re.sub(r"\d+", "#", l.strip()) for l in page["text"].splitlines() if l.strip()}:
            counts[line] = counts.get(line, 0) + 1
    return {line for line, n in counts.items() if len(pages) > 2 and n >= max(2, 0.3 * len(pages))}


def is_caps_heading(line, previous):
    """An all-capitals line that is short, like "ARTICLE 3. RENT" or "ANIMAL ADDENDUM", and not a line of an
    all-capitals paragraph (the deposit disclosure)."""
    letters = [c for c in line if c.isalpha()]
    if len(line) > 60 or len(letters) < 3 or any(c.islower() for c in letters):
        return False
    return not (previous.isupper() and len(previous) > 60)


def is_title_heading(line, following):
    """A short line in title case, like "Late Rent" or "Keys, Locks, and Access", followed by a paragraph."""
    words = line.replace(",", "").split()
    if not 1 <= len(words) <= 6 or line.endswith((".", ":", ";")) or len(following) < 60:
        return False
    return all(w[0].isupper() or w in SMALL_WORDS for w in words if w[0].isalpha())


def split_clauses(pages):
    """The lease cut into clauses at its headings, numbered or not: [{"id", "title", "page", "text"}].
    A heading line starts a section; a numbered line ("4.2. Due Date. ...") starts a clause inside it."""
    skip = repeated_lines(pages)
    lines = [(p["page"], l.strip()) for p in pages for l in p["text"].splitlines()
             if l.strip() and re.sub(r"\d+", "#", l.strip()) not in skip]
    clauses, section, current = [], "", None
    for i, (page, line) in enumerate(lines):
        previous = lines[i - 1][1] if i else ""
        following = lines[i + 1][1] if i + 1 < len(lines) else ""
        numbered = NUMBERED.match(line)
        if is_caps_heading(line, previous) or is_title_heading(line, following):
            section = line
            current = {"title": section, "page": page, "text": []}
            clauses.append(current)
        elif numbered and (numbered.group(2) or len(line) < 70):
            caption = f"{numbered.group(1)} {numbered.group(2) or ''}".strip()
            current = {"title": f"{section} > {caption}" if section else caption, "page": page, "text": [line]}
            clauses.append(current)
        else:
            if current is None:
                current = {"title": "(start of the lease)", "page": page, "text": []}
                clauses.append(current)
            current["text"].append(line)
    kept = [c for c in clauses if c["text"]]                   # a heading with no words of its own is just a title
    return [{"id": f"c{n}", "title": c["title"], "page": c["page"], "text": " ".join(c["text"])}
            for n, c in enumerate(kept, start=1)]


# ---- Asking one question

TEXT_CALL = re.compile(r"<function=([\w-]+)>(.*?)</function>", re.S)
TEXT_PARAMETER = re.compile(r"<parameter=([\w-]+)>\s*(.*?)\s*</parameter>", re.S)


def text_tool_calls(content):
    """Tool calls the model wrote as text ("<function=search_lease><parameter=words>late fee</parameter>"), as
    [(name, arguments)]. Nemotron does this now and then instead of making the call."""
    calls = []
    for name, body in TEXT_CALL.findall(content or ""):
        arguments = {}
        for key, value in TEXT_PARAMETER.findall(body):
            try:
                arguments[key] = json.loads(value)
            except json.JSONDecodeError:
                arguments[key] = value
        calls.append((name, arguments))
    return calls


def parse_reply(content):
    """The model's JSON answer, or its raw words as the answer if the JSON cannot be read."""
    content = re.sub(r"<think>.*?</think>", "", content or "", flags=re.S).strip()
    start, end = content.find("{"), content.rfind("}")
    if start != -1 and end > start:
        try:
            reply = json.loads(content[start:end + 1])
            quotes = reply.get("quotes") or []
            return {"answer": str(reply.get("answer", "")), "quotes": [str(q) for q in quotes]}
        except (json.JSONDecodeError, AttributeError):
            pass
    return {"answer": content, "quotes": []}


def call(gateway, **request):
    """One request to the gateway, tried up to three times if the connection fails."""
    for attempt in range(3):
        try:
            return gateway.chat.completions.create(**request)
        except Exception as error:                            # a dropped connection or a busy gateway
            if attempt == 2:
                raise
            print(f"  retrying after: {error}", file=sys.stderr)
            time.sleep(10)


def ask(gateway, lease_part, question, tools, run_tool):
    """Ask one question in a fresh chat: the shared instruction, the method's lease part, and its tools. Runs the
    tool loop until the model answers. Returns the answer, its quotes, the tool calls, and the seconds it took."""
    messages = [{"role": "system", "content": f"{INSTRUCTION}\n\n{lease_part}"},
                {"role": "user", "content": question}]
    calls, content, answered, start = [], "", False, time.perf_counter()
    for _ in range(MAX_STEPS):
        request = {"model": MODEL, "messages": messages, "temperature": 0, "max_tokens": 8000}
        if tools:
            request["tools"] = tools
        message = call(gateway, **request).choices[0].message
        content = message.content or ""
        written = [] if message.tool_calls else text_tool_calls(content)
        if written:                                          # run calls written as text, and hand back the results
            messages.append({"role": "assistant", "content": content})
            for name, arguments in written:
                calls.append({"name": name, "arguments": arguments})
                messages.append({"role": "user", "content": f"Result of {name}:\n{run_tool(name, arguments)}"})
            continue
        if not message.tool_calls:
            answered = True
            break
        messages.append({"role": "assistant", "content": content,
                         "tool_calls": [c.model_dump() for c in message.tool_calls]})
        for tool_call in message.tool_calls:
            try:
                arguments = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}
            calls.append({"name": tool_call.function.name, "arguments": arguments})
            result = run_tool(tool_call.function.name, arguments)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
    if not answered:                                         # out of tool rounds: answer from what was read
        request = {"model": MODEL, "messages": messages, "temperature": 0, "max_tokens": 8000,
                   "tools": tools, "tool_choice": "none"}
        content = call(gateway, **request).choices[0].message.content or ""
    seconds = time.perf_counter() - start
    return {**parse_reply(content), "raw": content, "tool_calls": calls, "seconds": round(seconds, 1)}


# ---- Running a method over the whole test

def run(method, setup, lease_part, tools, run_tool, only=None):
    """Time the method's intake of each lease (the middle of three runs), then ask every question.
    setup(lease) -> state; lease_part(state) -> the system prompt's lease text; tools(state) -> tool list;
    run_tool(state, name, arguments) -> text. Writes results/<method>.jsonl and results/<method>_intake.json."""
    RESULTS.mkdir(exist_ok=True)
    gateway = client()
    states, intake = {}, {}
    timed = RESULTS / f"{method}_intake.json"
    saved = json.loads(timed.read_text()) if timed.exists() else {}
    for lease in LEASES:
        if lease in saved:                                   # already timed: set it up once, keep the timing
            states[lease], intake[lease] = setup(lease), saved[lease]
            continue
        times = []
        for _ in range(3):
            start = time.perf_counter()
            states[lease] = setup(lease)
            times.append(time.perf_counter() - start)
        intake[lease] = round(statistics.median(times), 3)
    (RESULTS / f"{method}_intake.json").write_text(json.dumps(intake, indent=1))
    out = RESULTS / f"{method}.jsonl"
    done = {json.loads(l)["id"] for l in out.read_text().splitlines()} if out.exists() else set()
    for q in questions():
        if q["id"] in done or (only and q["lease"] not in only):
            continue
        state = states[q["lease"]]
        result = ask(gateway, lease_part(state), q["question"], tools(state),
                     lambda name, arguments: run_tool(state, name, arguments))
        with out.open("a") as f:
            f.write(json.dumps({"id": q["id"], "lease": q["lease"], "method": method, **result}) + "\n")
        print(f"{method} {q['id']} {result['seconds']}s {len(result['tool_calls'])} tool calls", flush=True)
