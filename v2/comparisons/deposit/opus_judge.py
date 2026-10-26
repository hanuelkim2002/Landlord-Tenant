"""The blind second judging, by Claude Opus 5.5 run as Claude Code subagents (not through an API). pack writes one
packet per story, its answers shuffled under plain labels, and the key to the labels; unpack turns the judges'
grades back into judge_opus_<version>.json for grade.py --judge opus. The judges' rubric is in README.md.
Run from this folder: python opus_judge.py pack <folder> [sonnet] [fixed], then, once the judges are done,
python opus_judge.py unpack <folder> [sonnet]   (sonnet: the answers in results/sonnet/, else the Gemini ones;
the versions to pack, default v1,old,new)
"""
import json
import random
import sys
from pathlib import Path

import run                                                    # this test's stories and where its answers are kept


def pack(folder, model, versions=("v1", "old", "new")):
    """One packet per story, with the answers shuffled (fixed seed) so a judge cannot tell which version wrote which."""
    answers = {}
    for version in versions:                                  # this order keeps earlier packs the same when rebuilt
        for line in map(json.loads, (run.results_folder(model) / f"{version}.jsonl").read_text().splitlines()):
            answers.setdefault(line["story"], []).append((version, line["run"], line["answer"]))
    stories = {s["id"]: s for s in run.all_stories()}
    shuffle, key = random.Random(23), {}
    for story_id, items in answers.items():
        shuffle.shuffle(items)
        s = stories[story_id]
        packet = {"story": {k: s[k] for k in ("id", "title", "today", "facts", "message", "answer", "points", "mistakes")},
                  "lease_file": "comparisons/skills/" + s.get("lease", "lease.txt"),
                  "answers": [{"label": f"{story_id}-A{i + 1}", "answer": a} for i, (_, _, a) in enumerate(items)]}
        (folder / f"{story_id}.json").write_text(json.dumps(packet, indent=1))
        key.update({f"{story_id}-A{i + 1}": {"version": v, "story": story_id, "run": r} for i, (v, r, _) in enumerate(items)})
    (folder / "key.json").write_text(json.dumps(key, indent=1))
    print(f"{len(key)} answers in {len(answers)} packets in {folder}")


def unpack(folder, model):
    """The judges' grades, by version and answer ("deposit-6/2"), into judge_opus_<version>.json beside the answers."""
    key = json.loads((folder / "key.json").read_text())
    by_version = {}
    for path in sorted(folder.glob("grades-*.json")):
        for label, grade in json.loads(path.read_text()).items():
            where = key[label]
            by_version.setdefault(where["version"], {})[f"{where['story']}/{where['run']}"] = grade
    for version, grades in by_version.items():
        (run.results_folder(model) / f"judge_opus_{version}.json").write_text(json.dumps(grades, indent=1, sort_keys=True))
        print(f"{version}: {len(grades)} grades")


if __name__ == "__main__":
    folder, model = Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "gemini"
    if sys.argv[1] == "pack":
        pack(folder, model, *([sys.argv[4].split(",")] if len(sys.argv) > 4 else []))
    else:
        unpack(folder, model)
