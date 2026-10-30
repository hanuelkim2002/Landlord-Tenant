"""The blind grading of one skill's test, by Claude Opus 5.5 run as Claude Code subagents (not through an API). pack
writes one packet per story, its answers shuffled under plain labels, with the rubric; unpack turns the graders'
grades back into results/judge_opus_<version>.json for grade.py. Run from this folder:
python judge.py pack repair_not_made <folder> [--versions v1,new] [--dry], then, once the graders are done,
python judge.py unpack repair_not_made <folder> [--dry]
"""
import argparse
import json
import random
from pathlib import Path

import run                                                    # a skill's stories and where its answers are kept
import score                                                  # the model test's judge prompt (run put it on the path)

# The deposit test's rubric, for any skill: the judge prompt's instructions and its reply format, without the parts
# a packet carries itself (the statute, the lease, the story, the answer).
RUBRIC = (score.STORY_PROMPT.split("\n\nTHE STATUTE:")[0].replace("about their security deposit",
                                                                   "about their dispute with their landlord")
          + "\n\nFor each answer, " + score.STORY_PROMPT.split("Chatbot's answer: {reply}\n\n")[1][0].lower()
          + score.STORY_PROMPT.split("Chatbot's answer: {reply}\n\n")[1][1:].replace("{{", "{").replace("}}", "}"))


def lease_file(skill, story):
    """The story's lease, as a path from v2/."""
    if story.get("lease"):
        return f"comparisons/each_skill/{skill}/{story['lease']}"
    return "comparisons/skills/lease.txt"


def pack(skill, folder, versions=("v1", "new"), dry=False):
    """One packet per story, with the answers shuffled (fixed seed) so a grader cannot tell which version wrote which."""
    folder.mkdir(parents=True, exist_ok=True)
    answers = {}
    for version in versions:                                  # this order keeps a rebuilt pack the same
        for line in run.models.read_lines(run.results_folder(skill, dry) / f"{version}.jsonl"):
            answers.setdefault(line["story"], []).append((version, line["run"], line["answer"]))
    stories = {s["id"]: s for s in run.all_stories(skill)}
    sections = run.models.read_json(run.test_folder(skill) / "stories.json")["sections"]
    shuffle, key = random.Random(23), {}
    for story_id, items in answers.items():
        shuffle.shuffle(items)
        s = stories[story_id]
        packet = {"rubric": RUBRIC, "statute_files": [f"statutes/{section}.txt" for section in sections],
                  "lease_file": lease_file(skill, s),
                  "story": {k: s[k] for k in ("id", "title", "today", "facts", "message", "answer", "points", "mistakes")},
                  "answers": [{"label": f"{story_id}-A{i + 1}", "answer": a} for i, (_, _, a) in enumerate(items)]}
        (folder / f"{story_id}.json").write_text(json.dumps(packet, indent=1, ensure_ascii=False))
        key.update({f"{story_id}-A{i + 1}": {"version": v, "story": story_id, "run": r} for i, (v, r, _) in enumerate(items)})
    (folder / "key.json").write_text(json.dumps(key, indent=1))
    print(f"{len(key)} answers in {len(answers)} packets in {folder}")


def unpack(skill, folder, dry=False):
    """The graders' grades, by version and answer ("repair-2/3"), into results/judge_opus_<version>.json."""
    key = json.loads((folder / "key.json").read_text())
    by_version = {}
    for path in sorted(folder.glob("grades-*.json")):
        for label, grade in json.loads(path.read_text()).items():
            where = key[label]
            by_version.setdefault(where["version"], {})[f"{where['story']}/{where['run']}"] = grade
    for version, grades in by_version.items():
        path = run.results_folder(skill, dry) / f"judge_opus_{version}.json"
        path.write_text(json.dumps(grades, indent=1, sort_keys=True))
        print(f"{version}: {len(grades)} grades")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=("pack", "unpack"))
    parser.add_argument("skill")
    parser.add_argument("folder", type=Path, help="where the packets and the graders' grades-<n>.json files go")
    parser.add_argument("--versions", default="v1,new", help="the versions to pack, like v1,new")
    parser.add_argument("--dry", action="store_true", help="the dry run's answers")
    args = parser.parse_args()
    if args.action == "pack":
        pack(args.skill, args.folder, tuple(args.versions.split(",")), args.dry)
    else:
        unpack(args.skill, args.folder, args.dry)
