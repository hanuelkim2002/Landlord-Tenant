"""Runs the plain-replies test: the 18 deposit stories (comparisons/skills/), three runs each, through the app's own
chat on Sonnet 5.5 from Anthropic, with the rules from before this change (old, rules_old.txt) or the app's rules now
(new). Both use the app's own skills. Answers go to results/<rules>.jsonl.
Run from this folder: python run.py old   (or new; --stories 6,8,13-18; --dry for a fake model)
"""
import argparse
import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPARISONS = HERE.parent
sys.path.insert(0, str(COMPARISONS / "models"))
import models                                                 # the model test's set-up, request log, and file helpers
import run_chat                                               # its answer_once: one message answered as the page does

# The deposit test's runner holds the stories and their leases. It is loaded by its path, since this file is also
# named run.py and "import run" here would load this file again.
_spec = importlib.util.spec_from_file_location("deposit_run", COMPARISONS / "deposit" / "run.py")
deposit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(deposit)


def parse_args():
    """The command line."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("rules", choices=["old", "new"])
    parser.add_argument("--stories", help="only these story numbers, like 6,8,13-18")
    parser.add_argument("--dry", action="store_true", help="use a fake model; nothing is sent anywhere")
    return parser.parse_args()


def main():
    """Set up the app on Sonnet with these rules, and run each story three times."""
    args = parse_args()
    gateway, model_id = models.CHAT_MODELS["sonnet-anthropic"]
    app = models.setup(gateway, chat_model=model_id, dry=args.dry)
    if args.rules == "old":
        app.chat.RULES = (HERE / "rules_old.txt").read_text()   # the rules as they were before this change
    folder = HERE / "results" / ("dry" if args.dry else "")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{args.rules}.jsonl"
    done = {(line["story"], line["run"]) for line in models.lines_without_errors(path)}

    def run_story(story):
        """The three runs of one story, in order, so the lease is cached after run 1."""
        for run in (1, 2, 3):
            if (story["id"], run) in done:
                continue
            line = {"rules": args.rules, "story": story["id"], "run": run,
                    **run_chat.answer_once(app, deposit.pages_for(story), story["message"], story["facts"],
                                           story["today"])}
            models.add_line(path, line)
            run_chat.progress(f"{args.rules} {story['id']} run {run}", line)

    print(f"{args.rules} rules, Sonnet ({model_id}), into {path}" + (" [dry]" if args.dry else ""))
    with ThreadPoolExecutor(6) as pool:
        list(pool.map(run_story, deposit.chosen(deposit.all_stories(), args.stories)))   # list() raises a thread's error
    lines = models.read_lines(path)
    print(f"Done. {len(lines)} answers, ${sum(line['cost'] for line in lines):.4f} by the logged costs.")


if __name__ == "__main__":
    main()
