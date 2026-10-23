"""The blind second judging, by Claude Opus 5.5 run as Claude Code subagents (not through an API). pack writes one
packet per story, its nine answers shuffled under plain labels, and the key to the labels; unpack turns the judges'
grades back into results/judge_opus_<version>.json for grade.py --judge opus. The judges' rubric is in README.md.
Run from this folder: python opus_judge.py pack <folder>, then, once the judges are done, python opus_judge.py unpack <folder>
"""
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS_TEST = HERE.parent / "skills"
VERSIONS = ("v1", "old", "new")


def stories():
    """The twelve stories, by id."""
    return {s["id"]: s for name in ("stories.json", "stories_more.json")
            for s in json.loads((SKILLS_TEST / name).read_text())["stories"]}


def pack(folder):
    """One packet per story, with the answers shuffled (fixed seed) so a judge cannot tell which version wrote which."""
    answers = {}
    for version in VERSIONS:
        for line in map(json.loads, (HERE / "results" / f"{version}.jsonl").read_text().splitlines()):
            answers.setdefault(line["story"], []).append((version, line["run"], line["answer"]))
    shuffle, key = random.Random(23), {}
    for story_id, items in answers.items():
        shuffle.shuffle(items)
        s = stories()[story_id]
        packet = {"story": {k: s[k] for k in ("id", "title", "today", "facts", "message", "answer", "points", "mistakes")},
                  "lease_file": "comparisons/skills/" + s.get("lease", "lease.txt"),
                  "answers": [{"label": f"{story_id}-A{i + 1}", "answer": a} for i, (_, _, a) in enumerate(items)]}
        (folder / f"{story_id}.json").write_text(json.dumps(packet, indent=1))
        key.update({f"{story_id}-A{i + 1}": {"version": v, "story": story_id, "run": r} for i, (v, r, _) in enumerate(items)})
    (folder / "key.json").write_text(json.dumps(key, indent=1))
    print(f"{len(key)} answers in {len(answers)} packets in {folder}")


def unpack(folder):
    """The judges' grades, by version and answer ("deposit-6/2"), into results/judge_opus_<version>.json."""
    key = json.loads((folder / "key.json").read_text())
    by_version = {version: {} for version in VERSIONS}
    for path in sorted(folder.glob("grades-*.json")):
        for label, grade in json.loads(path.read_text()).items():
            where = key[label]
            by_version[where["version"]][f"{where['story']}/{where['run']}"] = grade
    for version, grades in by_version.items():
        (HERE / "results" / f"judge_opus_{version}.json").write_text(json.dumps(grades, indent=1, sort_keys=True))
        print(f"{version}: {len(grades)} grades")


if __name__ == "__main__":
    {"pack": pack, "unpack": unpack}[sys.argv[1]](Path(sys.argv[2]))
