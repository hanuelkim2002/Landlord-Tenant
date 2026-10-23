"""Runs one version of the deposit skill on the twelve deposit stories (1 to 5 from comparisons/skills/stories.json,
6 to 12 from stories_more.json), three runs each, through the app's own chat with Gemini, as the page runs it.
Run from this folder: python run.py new   (or old, v1; add --dry to try it with a fake model)
"""
import argparse
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
V2 = HERE.parents[1]
SKILLS_TEST = V2 / "comparisons" / "skills"
sys.path.insert(0, str(V2 / "comparisons" / "models"))
import models                                                 # the model test's set-up, request log, and file helpers
import run_chat                                               # its answer_once: one message answered as the page does

# old: the skill before 2026-10-22; new: with the gaps filled; v1: v1's skill, unchanged, under v2's header
VERSIONS = {"old": HERE / "versions" / "old.md", "new": HERE / "versions" / "new.md",
            "v1": V2.parent / "v1" / "skills" / "deposit_not_returned.md"}


def parse_args():
    """The command line."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("version", choices=list(VERSIONS))
    parser.add_argument("--dry", action="store_true", help="use a fake model; nothing is sent anywhere")
    return parser.parse_args()


def skill_folder(version):
    """A throwaway skills folder holding only this version, so load_skill gives the model that version. v1's skill
    gets v2's header (name and description), so all three are listed and loaded the same way; its body is unchanged."""
    text = VERSIONS[version].read_text()
    if version == "v1":
        header = VERSIONS["new"].read_text().split("---", 2)[1]
        text = f"---{header}---{text.split('---', 2)[2]}"
    folder = Path(tempfile.mkdtemp(prefix="skills_"))
    (folder / "deposit_not_returned.md").write_text(text)
    return folder


def all_stories():
    """The twelve stories, in order."""
    return [story for name in ("stories.json", "stories_more.json")
            for story in models.read_json(SKILLS_TEST / name)["stories"]]


def pages_for(story):
    """The story's lease in the app's page format: lease.txt, unless the story names a variant of it."""
    return [{"page": 1, "text": (SKILLS_TEST / story.get("lease", "lease.txt")).read_text(), "read_by": "text"}]


def main():
    """Set up the app with Gemini and this skill version, and run each story three times."""
    args = parse_args()
    gateway, model_id = models.CHAT_MODELS["gemini"]
    app = models.setup(gateway, chat_model=model_id, dry=args.dry)
    app.law.SKILLS = skill_folder(args.version)               # load_skill reads the skills from here
    folder = HERE / "results" / ("dry" if args.dry else "")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{args.version}.jsonl"
    done = {(line["story"], line["run"]) for line in models.lines_without_errors(path)}

    def run_story(story):
        """The three runs of one story, in order, so the lease is cached after run 1."""
        for run in (1, 2, 3):
            if (story["id"], run) in done:
                continue
            line = {"version": args.version, "story": story["id"], "run": run,
                    **run_chat.answer_once(app, pages_for(story), story["message"], story["facts"], story["today"])}
            models.add_line(path, line)
            run_chat.progress(f"{args.version} {story['id']} run {run}", line)

    print(f"{args.version} skill, Gemini ({model_id}), into {path.name}" + (" [dry]" if args.dry else ""))
    with ThreadPoolExecutor(6) as pool:
        list(pool.map(run_story, all_stories()))              # list() so that an error inside a thread is raised here
    lines = models.read_lines(path)
    print(f"Done. {len(lines)} answers, ${sum(line['cost'] for line in lines):.4f} by the logged costs.")


if __name__ == "__main__":
    main()
