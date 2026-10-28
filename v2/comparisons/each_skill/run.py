"""Runs one version of one skill on that skill's stories, three runs each, through the app's own chat, as the page
runs it, with Claude Sonnet 5.5 from Anthropic. One runner for every skill: a skill's stories, leases, versions, and
answers live in a folder named after it, like repair_not_made/. Run from this folder:
python run.py repair_not_made new   (or v1, or a name in <skill>/versions/; --stories 1,3-5; --dry for a fake model)
"""
import argparse
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
V2 = HERE.parents[1]
SKILLS_TEST = V2 / "comparisons" / "skills"                  # the made-up lease every story starts from
SHARED = "who_the_law_covers"                                 # part of the new method, so v1's runs leave it out
CHAT = "sonnet-anthropic"                                     # the app's chat model, by its name in models.CHAT_MODELS
sys.path.insert(0, str(V2 / "comparisons" / "models"))
import models                                                 # the model test's set-up, request log, and file helpers
import run_chat                                               # its answer_once: one message answered as the page does


def test_folder(skill):
    """Where a skill's stories, leases, versions, and results are kept."""
    return HERE / skill


def results_folder(skill, dry=False):
    """The skill's answers and grades; a dry run's go in results/dry/."""
    return test_folder(skill) / "results" / ("dry" if dry else "")


def version_file(skill, version):
    """The skill file a version names: new is the app's own, v1 is v1's, any other name is a copy in versions/."""
    if version == "new":
        return V2 / "skills" / f"{skill}.md"
    if version == "v1":
        return V2.parent / "v1" / "skills" / f"{skill}.md"
    return test_folder(skill) / "versions" / f"{version}.md"


def skill_folder(skill, version):
    """A throwaway skills folder: every skill in skills/, with this one replaced by the version's text, so the model
    chooses skills as it does on the page. v1's body goes under the current header, so all versions are listed and
    loaded the same way, and v1's folder has no shared skill, since v1's skill carries its own college note."""
    folder = Path(tempfile.mkdtemp(prefix="skills_"))
    for path in (V2 / "skills").glob("*.md"):
        if not (version == "v1" and path.stem == SHARED):
            shutil.copy(path, folder / path.name)
    text = version_file(skill, version).read_text()
    if version == "v1":
        header = (V2 / "skills" / f"{skill}.md").read_text().split("---", 2)[1]
        text = f"---{header}---{text.split('---', 2)[2]}"
    (folder / f"{skill}.md").write_text(text)
    return folder


def all_stories(skill):
    """Every story of the skill, in order."""
    return models.read_json(test_folder(skill) / "stories.json")["stories"]


def chosen(stories, numbers):
    """The stories named by numbers and ranges like "1,3-5" (all of them if none are given)."""
    if not numbers:
        return stories
    wanted = set()
    for part in numbers.split(","):
        first, _, last = part.partition("-")
        wanted |= set(range(int(first), int(last or first) + 1))
    return [s for s in stories if int(s["id"].split("-")[1]) in wanted]


def pages_for(skill, story):
    """The story's lease in the app's page format: comparisons/skills/lease.txt, or the variant the story names."""
    path = test_folder(skill) / story["lease"] if story.get("lease") else SKILLS_TEST / "lease.txt"
    return [{"page": 1, "text": path.read_text(), "read_by": "text"}]


def parse_args():
    """The command line."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill", help="the skill's name, like repair_not_made")
    parser.add_argument("version", help="new, v1, or a name in <skill>/versions/")
    parser.add_argument("--stories", help="only these story numbers, like 1,3-5")
    parser.add_argument("--dry", action="store_true", help="use a fake model; nothing is sent anywhere")
    return parser.parse_args()


def main():
    """Set up the app with the chat model and this skill version, and run each story three times."""
    args = parse_args()
    gateway, model_id = models.CHAT_MODELS[CHAT]
    app = models.setup(gateway, chat_model=model_id, dry=args.dry)
    app.law.SKILLS = skill_folder(args.skill, args.version)    # load_skill and the prompt read the skills from here
    folder = results_folder(args.skill, args.dry)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{args.version}.jsonl"
    done = {(line["story"], line["run"]) for line in models.lines_without_errors(path)}

    def run_story(story):
        """The three runs of one story, in order, so the lease is cached after run 1."""
        for run in (1, 2, 3):
            if (story["id"], run) in done:
                continue
            line = {"skill": args.skill, "version": args.version, "story": story["id"], "run": run,
                    **run_chat.answer_once(app, pages_for(args.skill, story), story["message"], story["facts"],
                                           story["today"])}
            models.add_line(path, line)
            run_chat.progress(f"{args.version} {story['id']} run {run}", line)

    print(f"{args.skill}, {args.version}, {model_id}, into {path}" + (" [dry]" if args.dry else ""))
    with ThreadPoolExecutor(6) as pool:
        list(pool.map(run_story, chosen(all_stories(args.skill), args.stories)))   # list() so a thread's error shows
    lines = models.read_lines(path)
    print(f"Done. {len(lines)} answers, ${sum(line['cost'] for line in lines):.4f} by the logged costs.")


if __name__ == "__main__":
    main()
