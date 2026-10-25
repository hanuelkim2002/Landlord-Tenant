"""The memory test: three made-up return visits (stories.json), each answered by the app's own chat after a first
visit dated days earlier. "new" runs this branch's memory (the timeline and since last visit); "baseline" runs v2 as
it is on main (the old chat and the facts only). Claude Sonnet 5.5 answers, through Anthropic's SDK.
Run from this folder: python run_memory.py new|baseline [--runs 3] [--dry]   (--dry: a fake model, nothing sent)
"""
import argparse
import atexit
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "models"))
import models  # noqa: E402  (the model test's shared helpers: the app set up, the log, the story's day)

MODEL = "claude-sonnet-5-5"
STORIES = json.loads((HERE / "stories.json").read_text())["stories"]
TENANT_NUMBERS = itertools.count(1)                           # each answer gets its own tenant folder
LOCK = threading.Lock()


def parse_args():
    """The command line."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["new", "baseline"])
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--dry", action="store_true", help="use a fake model; nothing is sent anywhere")
    return parser.parse_args()


def main_code():
    """A throwaway copy of v2 as it is on main, for the baseline."""
    folder = Path(tempfile.mkdtemp(prefix="v2_main_"))
    atexit.register(shutil.rmtree, folder, ignore_errors=True)
    archive = subprocess.run(["git", "archive", "main", "v2"], cwd=models.V2.parent, capture_output=True,
                             check=True).stdout                # run from the repo's top, where v2/ is a path
    subprocess.run(["tar", "-x", "-C", str(folder)], input=archive, check=True)
    return folder / "v2"


def setup(args):
    """The app for this run: main's code for the baseline; Claude answers (or the fake model, with --dry)."""
    if args.mode == "baseline":
        models.V2 = main_code()
    app = models.setup("openrouter", chat_model=MODEL, dry=args.dry)   # the gateway only picks the app's settings
    if not args.dry:
        import claude_client
        app.config.client = lambda gateway=None: models.LoggedClient(claude_client.ClaudeClient(), "anthropic")
    if hasattr(app.record, "date"):
        app.record.date = models.StoryDate                     # why: since_last_visit must see the story's day
    return app


def seed(app, story, new_memory):
    """A matter as the first visit left it: the confirmed facts, the lines (new memory only), and the first visit's
    events written with their old times, so the app sees a tenant coming back."""
    with LOCK:
        tenant = f"t{next(TENANT_NUMBERS)}"
    m = app.record.new_matter(tenant, "memory test")
    when, corrected = story["first_visit"], story.get("corrected")
    for name, value in story["facts"].items():
        m["confirmed"][name] = {"value": value, "tenant_words": "(set by the test)", "confirmed": when}
    if corrected:
        m["confirmed"][corrected["fact"]].update(value=corrected["value"], confirmed=corrected["time"])
    events = [{"time": when, "kind": "message", "role": c["role"], "text": c["text"], "checks": None}
              for c in story["chat"]]
    events += [{"time": when, "kind": "fact_confirmed", "fact": name, "value": value, "noted_value": value}
               for name, value in story["facts"].items()]
    if new_memory:
        m["lines"] = {str(n): {**line, "saved": when} for n, line in enumerate(story["lines"], 1)}
        events += [{"time": when, "kind": "line_saved", "number": n, **line} for n, line in enumerate(story["lines"], 1)]
    if corrected:
        events.append({"time": corrected["time"], "kind": "fact_confirmed", "fact": corrected["fact"],
                       "value": corrected["value"], "noted_value": corrected["noted_value"]})
    app.record.save(m)
    pages = models.story_pages(False)                         # the sample lease, as the page stores a read lease
    (app.record.folder(m) / "lease_pages.json").write_text(json.dumps(pages))
    with (app.record.folder(m) / "events.jsonl").open("a") as f:
        f.writelines(json.dumps(event) + "\n" for event in events)
    return m


def answer(app, story, run, mode):
    """One return visit answered the way the page does it. Returns the fields of a results line."""
    m = seed(app, story, mode == "new")
    models.start_log(story["today"])                          # also the day count_days and since_last_visit see
    start = time.perf_counter()
    try:
        text, shown = app.chat.reply(m, story["message"])
        error = False
    except Exception as problem:                              # keep a failed answer, so one bad call does not end the run
        text, shown, error = f"ERROR: {type(problem).__name__}: {problem}", None, True
    requests, tool_calls = models.take_log()
    after = app.record.load(m["tenant"], m["matter"])
    return {"mode": mode, "story": story["id"], "run": run, "answer": text, "error": error, "tool_calls": tool_calls,
            "lines_after": after.get("lines"), "pending_after": after["pending"],
            "seconds": round(time.perf_counter() - start, 1), "requests": requests,
            "cost": round(sum(r["cost"] for r in requests), 6), "checks": shown}


def main():
    """Run every story's runs, the stories in parallel, and write one line per answer."""
    args = parse_args()
    app = setup(args)
    path = HERE / "results" / f"{'dry_' if args.dry else ''}{args.mode}.jsonl"
    done = {(line["story"], line["run"]) for line in models.lines_without_errors(path)}
    print(f"{args.mode} memory, {MODEL}, {args.runs} runs per story, into {path.name}" + (" [dry]" if args.dry else ""))

    def run_story(story):
        """One story's runs, in order."""
        for run in range(1, args.runs + 1):
            if (story["id"], run) not in done:
                line = answer(app, story, run, args.mode)
                models.add_line(path, line)
                models.say(f"{story['id']} run {run}: {line['seconds']} s, {len(line['tool_calls'])} tool calls, "
                           f"${line['cost']:.4f}" + ("  ERROR" if line["error"] else ""))

    start = time.perf_counter()
    with ThreadPoolExecutor(len(STORIES)) as pool:
        list(pool.map(run_story, STORIES))                    # list() so that an error inside a thread is raised here
    lines = models.read_lines(path)
    print(f"Done in {time.perf_counter() - start:.0f} s. {len(lines)} answers, ${sum(l['cost'] for l in lines):.4f}.")


if __name__ == "__main__":
    main()
