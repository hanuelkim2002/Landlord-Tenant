"""Shared by the model comparison scripts: the models under test, the app set up for one model, a log of every
request and tool call, a fake client for --dry runs, and where each script finds and keeps its files.
"""
import atexit
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import urllib.request
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from dotenv import dotenv_values

HERE = Path(__file__).resolve().parent
V2 = HERE.parents[1]
LEASE_TEST = V2 / "comparisons" / "lease"                     # the lease reading test: its questions, leases, texts
SKILLS_TEST = V2 / "comparisons" / "skills"                   # the skills test: its stories and sample lease
# The author's own lease and everything about it. MODEL_TEST_PRIVATE points to another folder, for trying the
# scripts on made-up files.
PRIVATE = Path(os.environ.get("MODEL_TEST_PRIVATE", HERE / "private"))

# name: (gateway, model id on that gateway)
CHAT_MODELS = {"nemotron": ("uf", "nemotron-3-super-120b-a12b"), "haiku": ("openrouter", "anthropic/claude-haiku-5.5"),
               "gemini": ("openrouter", "google/gemini-3.8-flash"), "sonnet": ("openrouter", "anthropic/claude-sonnet-5.5"),
               "sonnet-anthropic": ("anthropic", "claude-sonnet-5-5")}
READERS = {"gemma": ("uf", "gemma-4-31b-it"), "gemini": ("openrouter", "google/gemini-3.8-flash"),
           "haiku": ("openrouter", "anthropic/claude-haiku-5.5"), "sonnet": ("openrouter", "anthropic/claude-sonnet-5.5")}

# Dollars per million tokens, (in, out). Used only when the gateway does not say what a request cost. The UF prices
# are the UF budget, not money; the OpenRouter ones are list prices.
PRICES = {"nemotron-3-super-120b-a12b": (0.06, 0.24), "gemma-4-31b-it": (0.12, 0.36), "gpt-oss-120b": (0.06, 0.15),
          "anthropic/claude-haiku-5.5": (0.10, 0.50), "google/gemini-3.8-flash": (0.825, 4.125),
          "anthropic/claude-sonnet-5.5": (2, 10),
          "claude-sonnet-5-5": (2, 10), "claude-haiku-5-5": (0.10, 0.50)}

LOCAL = threading.local()                                     # one log per thread: threads answer different stories at once
LOCK = threading.Lock()                                       # one thread at a time writes to a file or to the screen


# ---- The log of requests and tool calls, one per thread

def start_log(today=None):
    """Begin a fresh log for this thread. today is the story's date as YYYY-MM-DD, or None for the real day."""
    LOCAL.log = {"requests": [], "tools": [], "today": date.fromisoformat(today) if today else None}


def log_for_thread():
    """This thread's log (made empty the first time a thread asks for it)."""
    if not hasattr(LOCAL, "log"):
        start_log()
    return LOCAL.log


def take_log():
    """This thread's (requests, tool calls) since start_log."""
    log = log_for_thread()
    return log["requests"], log["tools"]


class StoryDate(date):
    """Stands in for date inside tools.py: today() is the story's day on this thread, else the real day."""

    @classmethod
    def today(cls):
        """The story's day on this thread, or the real day."""
        return log_for_thread()["today"] or date.today()


def request_record(model, reply, seconds):
    """What one request cost: its tokens, the cost the gateway reported (or one worked out from list prices)."""
    usage = getattr(reply, "usage", None)
    details = getattr(usage, "prompt_tokens_details", None)
    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage, "completion_tokens", 0) or 0
    cost = getattr(usage, "cost", None)                       # OpenRouter reports it when asked (see prepare)
    estimated = cost is None
    if estimated:
        price_in, price_out = PRICES.get(model, (0, 0))
        cost = (prompt_tokens * price_in + completion_tokens * price_out) / 1_000_000
    return {"model": model, "seconds": round(seconds, 2), "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens, "cached_tokens": getattr(details, "cached_tokens", 0) or 0,
            "cache_write_tokens": getattr(details, "cache_write_tokens", 0) or 0, "cost": round(cost, 6),
            "finish_reason": reply.choices[0].finish_reason, "estimated": estimated}


# ---- The client the app gets: it adds what each gateway needs and logs every request

def with_cache_marker(messages):
    """The same messages, with the first one (the system prompt) marked for prompt caching. The long lease is sent
    again every round, so the gateway can reuse it. A new list is built; the caller's list is not changed."""
    first = messages[0]
    if first["role"] != "system" or not isinstance(first["content"], str):
        return messages
    marked = {**first, "content": [{"type": "text", "text": first["content"], "cache_control": {"type": "ephemeral"}}]}
    return [marked] + list(messages[1:])


def prepare(request, gateway):
    """The request as it is sent. On OpenRouter: ask for the cost, and mark the system prompt for caching on the
    models that take it (Anthropic and Google)."""
    if gateway != "openrouter":
        return request
    sent = {**request, "extra_body": {"usage": {"include": True}}}
    if request["model"].startswith(("anthropic/", "google/")):
        sent["messages"] = with_cache_marker(request["messages"])
    return sent


class LoggedClient:
    """Looks like the OpenAI client to the app. Each request goes through prepare and is added to this thread's log."""

    def __init__(self, inner, gateway):
        """Keep the real client and the gateway's name; offer chat.completions.create as the app expects."""
        self.inner, self.gateway = inner, gateway
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **request):
        """Send one request and log it."""
        start = time.perf_counter()
        reply = self.inner.chat.completions.create(**prepare(request, self.gateway))
        log_for_thread()["requests"].append(request_record(request["model"], reply, time.perf_counter() - start))
        return reply


# ---- The fake client for --dry: replies in the right shape, no model called

def text_of(content):
    """A message's text, whether its content is a string or a list of blocks."""
    if isinstance(content, str):
        return content
    return " ".join(block.get("text", "") for block in content)


def fake_tool_call(name, arguments):
    """A tool call shaped like the one the SDK returns."""
    call = {"id": f"call_{name}", "type": "function", "function": {"name": name, "arguments": json.dumps(arguments)}}
    return SimpleNamespace(id=call["id"], function=SimpleNamespace(**call["function"]), model_dump=lambda: call)


def fake_chat_message(request):
    """The chat's next reply: load a skill, then count days from the first confirmed fact, then answer."""
    system = text_of(request["messages"][0]["content"])
    steps = []
    skill = re.search(r"SKILLS \(load[^\n]*\n- ([\w-]+):", system)
    if skill and "LOADED SKILLS:\nnone yet" in system:
        steps.append(("load_skill", {"name": skill.group(1)}))
    fact = re.search(r"CONFIRMED FACTS[^\n]*\n- ([\w-]+):", system)
    if fact:
        steps.append(("count_days", {"fact": fact.group(1), "days": 30}))
    tools_done = sum(m["role"] == "tool" for m in request["messages"])
    if tools_done < len(steps) and request.get("tool_choice") != "none":
        return SimpleNamespace(content="", tool_calls=[fake_tool_call(*steps[tools_done])]), "tool_calls"
    text = "This is a made-up answer from a dry run. Which date did the landlord's notice arrive?"
    return SimpleNamespace(content=text, tool_calls=None), "stop"


def fake_judge_message():
    """A judge's reading that passes everything, with enough true and false entries for any number of points."""
    grade = {"answers_first": True, "says_lease_silent": False, "points_made": [True] * 10,
             "mistakes_made": [False] * 10, "other_error": "", "reason": "dry run"}
    return SimpleNamespace(content=json.dumps(grade), tool_calls=None), "stop"


class FakeClient:
    """Stands in for the gateway in --dry runs: chat replies, page reads, and judge readings, all made up."""

    def __init__(self):
        """Offer chat.completions.create as the app expects."""
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **request):
        """A reply for a chat request (it has tools), an image read (it has an image), or else a judge reading."""
        messages = request["messages"]
        has_image = any(isinstance(m["content"], list) and any(b.get("type") == "image_url" for b in m["content"])
                        for m in messages)
        if "tools" in request:
            message, reason = fake_chat_message(request)
        elif has_image:
            message, reason = SimpleNamespace(content="[X] Water [ ] Gas Tenant pays rent on the first day of the month.",
                                              tool_calls=None), "stop"
        else:
            message, reason = fake_judge_message()
        prompt = " ".join(text_of(m["content"]) for m in messages)
        usage = SimpleNamespace(prompt_tokens=len(prompt) // 4, completion_tokens=30,
                                prompt_tokens_details=SimpleNamespace(cached_tokens=0))
        return SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason=reason)], usage=usage)


# ---- Setting up the app for one model

def setup(gateway, chat_model=None, vision_model=None, dry=False):
    """Load the app set up for one model and return its modules. Call it once per process: the app reads its settings
    (gateway, models) when it is first imported, exactly as it does on the page."""
    os.environ["GATEWAY"] = gateway
    os.environ["READER_GATEWAY"] = gateway                   # one process tests one model, chat or reader
    for name, value in (("AGENT_MODEL", chat_model), ("VISION_MODEL", vision_model)):
        if value:
            os.environ[name] = value
        else:
            os.environ.pop(name, None)                        # not set: the gateway's default model
    sys.path.insert(0, str(V2))
    import chat, checks, config, law, lease, record, tools    # after the settings above, so the app reads them
    config.MATTERS = Path(tempfile.mkdtemp(prefix="matters_"))   # throwaway matters never land in the repo
    atexit.register(shutil.rmtree, config.MATTERS, ignore_errors=True)   # and are deleted when the run ends
    real_client = config.client

    def client(gateway=None):
        """The gateway's client, with a timeout and retries, and wrapped to log each request."""
        inner = FakeClient() if dry else real_client(gateway).with_options(timeout=120, max_retries=2)
        return LoggedClient(inner, gateway or config.GATEWAY)

    config.client = client
    real_run_tool = tools.run_tool

    def logged_run_tool(m, name, arguments):
        """Run the tool as the app does, and log the call and its result."""
        result = real_run_tool(m, name, arguments)
        log_for_thread()["tools"].append({"name": name, "arguments": arguments, "result": result})
        return result

    tools.run_tool = logged_run_tool
    tools.date = StoryDate
    return SimpleNamespace(chat=chat, checks=checks, config=config, law=law, lease=lease, record=record, tools=tools)


def usable(text):
    """The app's old test of a page's own text (lease.py before 2026-10-21): real words, at least 5, and most of
    what was read is words, not symbols. Kept here to rebuild what the app used to read ("own app")."""
    tokens = text.split()
    words = [t for t in tokens if re.fullmatch(r"[A-Za-z][A-Za-z'.,;:()\"-]*", t)]
    return len(words) >= 5 and len(words) >= 0.5 * len(tokens)


# ---- OpenRouter spending (read-only)

def spend():
    """Dollars OpenRouter says this account has used so far, or None if it cannot be read."""
    key = dotenv_values(V2 / ".env").get("OPENROUTER_API_KEY")
    request = urllib.request.Request("https://openrouter.ai/api/v1/credits", headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)["data"]["total_usage"]
    except (OSError, ValueError, KeyError) as problem:
        say(f"Could not read OpenRouter's spending: {type(problem).__name__}")
        return None


def spend_before(gateway, dry):
    """Print what OpenRouter says is spent so far, before a run on OpenRouter. Returns it (None if not applicable)."""
    if gateway != "openrouter" or dry:
        return None
    used = spend()
    say(f"OpenRouter used so far: ${used:.4f}")
    return used


def spend_after(before):
    """Print what OpenRouter says is spent now, and the difference, after a run. Its total runs a little behind, so
    this waits half a minute first."""
    if before is None:
        return
    say("Waiting 30 s for OpenRouter's total to catch up ...")
    time.sleep(30)
    used = spend()
    if used is not None:
        say(f"OpenRouter used now: ${used:.4f}  (this run: ${used - before:.4f})")


# ---- Where things are, and reading and writing them

def say(text):
    """Print a line; the lock keeps lines from different threads apart."""
    with LOCK:
        print(text, flush=True)


def results_folder(own, dry):
    """Where results are kept: results/ for the sample leases, private/results/ for the own lease. A --dry run keeps
    its made-up results in a dry/ folder inside, so they never mix with real ones."""
    folder = (PRIVATE if own else HERE) / "results"
    folder = folder / "dry" if dry else folder
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def scores_folder(own, dry):
    """Where score.py writes: this folder for the sample leases, private/ for the own lease (its detail file). A --dry
    run writes into its dry results folder instead."""
    return results_folder(own, True) if dry else (PRIVATE if own else HERE)


def blind_folder(own, dry):
    """Where the blind ranking files are: blind/ for the sample leases, private/blind/ for the own lease. A --dry run
    uses a folder inside its dry results."""
    if dry:
        return results_folder(own, True) / "blind"
    return (PRIVATE if own else HERE) / "blind"


def read_json(path):
    """A JSON file."""
    return json.loads(Path(path).read_text())


def read_lines(path):
    """The lines of a .jsonl file (an empty list if there is no such file)."""
    path = Path(path)
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def add_line(path, line):
    """Add one result to a .jsonl file as soon as it is done, so a stopped run loses nothing."""
    with LOCK:
        with Path(path).open("a") as f:
            f.write(json.dumps(line) + "\n")


def lines_without_errors(path):
    """The lines of a results file that are not errors. The file is rewritten without its error lines, so a rerun
    redoes them."""
    lines = read_lines(path)
    good = [line for line in lines if not line.get("error")]
    if len(good) < len(lines):
        path.write_text("".join(json.dumps(line) + "\n" for line in good))
        say(f"{len(lines) - len(good)} earlier errors in {path.name} will be run again")
    return good


def missing(paths):
    """The files among these that do not exist."""
    return [Path(p) for p in paths if not Path(p).exists()]


def stories(own):
    """The stories for a lease set: the whole file (its "stories", and for the own lease maybe "lease_dates")."""
    return read_json(PRIVATE / "own_stories.json" if own else SKILLS_TEST / "stories.json")


def questions(own):
    """The lease questions for a lease set. The sample ones leave out the lease the lease test took from v1."""
    if own:
        return read_json(PRIVATE / "own_questions.json")["questions"]
    return [q for q in read_json(LEASE_TEST / "answer_key.json")["questions"] if q["lease"] != "sample_v1"]


def story_pages(own):
    """The lease pages the stories are answered from, in the app's page format."""
    if own:
        return read_json(PRIVATE / "text_own_best.json")["pages"]
    return [{"page": 1, "text": (SKILLS_TEST / "lease.txt").read_text(), "read_by": "text"}]


def pages_file(own, lease, texts, dry):
    """The file with a lease's pages as one reader read them. No reader named: the best reading, made before."""
    if texts in (None, "best"):
        return PRIVATE / "text_own_best.json" if own else LEASE_TEST / "texts" / f"{lease}.json"
    return results_folder(own, dry) / f"text_{lease}_{texts}.json"


def lease_text(pages):
    """A lease's pages joined into one text."""
    return "\n".join(p["text"] for p in pages)
