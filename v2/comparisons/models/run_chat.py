"""Tests 1 and 2 of the model comparison: the app's own chat, run with one model, on five deposit stories (3 runs each)
or on lease questions, with the sample leases or with the author's own lease. Each answer is one line in a .jsonl file.
Run from this folder, for example: python run_chat.py stories sample haiku   (add --dry to run with a fake model)
"""
import argparse
import itertools
import time
from concurrent.futures import ThreadPoolExecutor

import models

TENANT_NUMBERS = itertools.count(1)                           # each answer gets its own tenant folder, so two never clash


def parse_args():
    """The command line."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("test", choices=["stories", "questions"])
    parser.add_argument("lease_set", choices=["sample", "own"])
    parser.add_argument("model", choices=list(models.CHAT_MODELS))
    parser.add_argument("--texts", help="questions only: answer from the lease as this reader read it (a reader, or app)")
    parser.add_argument("--leases", help="questions on the sample leases only: just these, like broken_text,scanned")
    parser.add_argument("--dry", action="store_true", help="use a fake model; nothing is sent anywhere")
    return parser.parse_args()


def answer_once(app, pages, message, facts=None, today=None):
    """One tenant message answered the way the page does it, in a new matter. Returns the fields of an answer line."""
    m = app.record.new_matter(f"t{next(TENANT_NUMBERS)}", "model comparison")
    for name, value in (facts or {}).items():                 # a story's facts are already confirmed by the tenant
        m["confirmed"][name] = {"value": value, "tenant_words": "(set by the test)", "confirmed": app.record.now()}
    app.record.save(m)
    models.start_log(today)                                   # also sets the day count_days compares with
    start = time.perf_counter()
    try:
        messages = [{"role": "system", "content": app.chat.system_prompt(m, pages)},
                    {"role": "user", "content": message}]     # no skill loaded: the model must load one itself
        answer, error = app.chat.run_loop(m, messages), False
    except Exception as problem:                              # keep a failed answer, so one bad call does not end the run
        answer, error = f"ERROR: {type(problem).__name__}: {problem}", True
    seconds = round(time.perf_counter() - start, 1)
    requests, tool_calls = models.take_log()
    return {"answer": answer, "error": error, "tool_calls": tool_calls, "skills_loaded": list(m["skills"]),
            "seconds": seconds, "requests": requests, "cost": round(sum(r["cost"] for r in requests), 6),
            "checks": app.checks.check_reply(answer, pages)}


def progress(name, line):
    """Print one finished answer."""
    flag = "  ERROR" if line["error"] else ""
    models.say(f"{name}: {line['seconds']} s, {len(line['requests'])} requests, {len(line['tool_calls'])} tool calls, "
               f"${line['cost']:.4f}{flag}")


def run_stories(app, args, path, header):
    """Five stories in parallel; inside a story, run 1 first and then runs 2 and 3, so the lease is cached by then."""
    pages = models.story_pages(args.lease_set == "own")
    done = {(line["story"], line["run"]) for line in models.lines_without_errors(path)}

    def run_story(story):
        """The three runs of one story, in order."""
        for run in (1, 2, 3):
            if (story["id"], run) in done:
                continue
            line = {**header, "story": story["id"], "run": run,
                    **answer_once(app, pages, story["message"], story["facts"], story["today"])}
            models.add_line(path, line)
            progress(f"{story['id']} run {run}", line)

    stories = models.stories(args.lease_set == "own")["stories"]
    with ThreadPoolExecutor(5) as pool:
        list(pool.map(run_story, stories))                    # list() so that an error inside a thread is raised here


def run_questions(app, args, path, header):
    """Per lease: the first question alone (it fills the cache), then the rest, 4 at a time."""
    own = args.lease_set == "own"
    asked = models.questions(own)
    if args.leases:
        asked = [q for q in asked if q["lease"] in args.leases.split(",")]
    done = {line["id"] for line in models.lines_without_errors(path)}
    for lease in dict.fromkeys(q["lease"] for q in asked):    # each lease once, in order
        todo = [q for q in asked if q["lease"] == lease and q["id"] not in done]
        pages = models.read_json(models.pages_file(own, lease, args.texts, args.dry))["pages"]

        def run_question(question):
            """One question, answered and saved."""
            line = {**header, "id": question["id"], "lease": lease, **answer_once(app, pages, question["question"])}
            models.add_line(path, line)
            progress(f"{lease} {question['id']}", line)

        if todo:
            run_question(todo[0])
            with ThreadPoolExecutor(4) as pool:
                list(pool.map(run_question, todo[1:]))


def files_needed(args):
    """The input files this run reads."""
    own = args.lease_set == "own"
    if args.test == "stories":
        return [models.PRIVATE / "own_stories.json", models.PRIVATE / "text_own_best.json"] if own else []
    needed = [models.PRIVATE / "own_questions.json"] if own else []
    leases = ["own"] if own else sorted({q["lease"] for q in models.questions(False)})
    if args.leases:
        leases = [name for name in leases if name in args.leases.split(",")]
    return needed + [models.pages_file(own, lease, args.texts, args.dry) for lease in leases]


def main():
    """Check the input files, set up the app for the model, and run."""
    args = parse_args()
    own = args.lease_set == "own"
    lacking = models.missing(files_needed(args))
    if lacking:
        print("Cannot run yet. These files are missing:", *[f"  {p}" for p in lacking], sep="\n")
        return
    gateway, model_id = models.CHAT_MODELS[args.model]
    app = models.setup(gateway, chat_model=model_id, dry=args.dry)
    name = f"{args.test}_{args.model}" + (f"_{args.texts}" if args.test == "questions" and args.texts else "")
    path = models.results_folder(own, args.dry) / f"{name}.jsonl"
    texts = (args.texts or "best") if args.test == "questions" else "best"
    header = {"test": args.test, "lease_set": args.lease_set, "model": args.model, "texts": texts}
    print(f"{args.test} on the {args.lease_set} lease with {args.model} ({model_id}), into {path.name}"
          + (" [dry]" if args.dry else ""))
    before = models.spend_before(gateway, args.dry)
    start = time.perf_counter()
    (run_stories if args.test == "stories" else run_questions)(app, args, path, header)
    lines = models.read_lines(path)
    print(f"Done in {time.perf_counter() - start:.0f} s. {len(lines)} answers in the file, "
          f"${sum(line['cost'] for line in lines):.4f} by the logged costs.")
    models.spend_after(before)


if __name__ == "__main__":
    main()
