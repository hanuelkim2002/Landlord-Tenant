"""The grading packets of the plain-replies test, and their grades. pack writes two packets per story, the answers
under the same shuffled labels in both: one for the right-or-wrong grade (the whole answers, as in the deposit test)
and one for the plain reading (what the tenant sees before any click). Claude Opus 5.5 subagents in Claude Code grade
them; unpack turns their grades into results/judge_right_<rules>.json and results/judge_plain_<rules>.json.
Run from this folder: python judge.py pack <folder>, then, once the graders are done, python judge.py unpack <folder>
"""
import json
import random
import sys
from pathlib import Path

import run                                                    # this test's answers, and the deposit test's stories
sys.path.insert(0, str(run.models.V2))
import chat                                                   # the app's own split of a reply

RULES = ("old", "new")


def seen_first(answer):
    """What the tenant sees before any click: the short part, then each box's title on its own line."""
    short, points = chat.split_reply(answer)
    return "\n".join([short] + [f"[ > {title} ]" for title, _ in points])


def pack(folder):
    """Two packets per story, the answers shuffled (fixed seed) so a grader cannot tell old from new by order."""
    folder.mkdir(parents=True, exist_ok=True)
    answers = {}
    for rules in RULES:
        for line in run.models.read_lines(run.HERE / "results" / f"{rules}.jsonl"):
            answers.setdefault(line["story"], []).append((rules, line["run"], line["answer"]))
    stories = {s["id"]: s for s in run.deposit.all_stories()}
    shuffle, key = random.Random(23), {}
    for story_id, items in sorted(answers.items()):
        shuffle.shuffle(items)
        s = stories[story_id]
        labels = [f"{story_id}-A{i + 1}" for i in range(len(items))]
        right = {"story": {k: s[k] for k in ("id", "title", "today", "facts", "message", "answer", "points", "mistakes")},
                 "lease_file": "comparisons/skills/" + s.get("lease", "lease.txt"),
                 "answers": [{"label": label, "answer": a} for label, (_, _, a) in zip(labels, items)]}
        plain = {"story": {"id": story_id, "message": s["message"]},
                 "answers": [{"label": label, "seen_first": seen_first(a)} for label, (_, _, a) in zip(labels, items)]}
        (folder / f"right-{story_id}.json").write_text(json.dumps(right, indent=1))
        (folder / f"plain-{story_id}.json").write_text(json.dumps(plain, indent=1))
        key.update({label: {"rules": r, "story": story_id, "run": n} for label, (r, n, _) in zip(labels, items)})
    (folder / "key.json").write_text(json.dumps(key, indent=1))
    print(f"{len(key)} answers in {len(answers)} stories, two packets each, in {folder}")


def unpack(folder):
    """The graders' files, by kind and rules, into results/judge_<kind>_<rules>.json, keyed like "deposit-6/2"."""
    key = json.loads((folder / "key.json").read_text())
    for kind in ("right", "plain"):
        by_rules = {}
        for path in sorted(folder.glob(f"grades-{kind}-*.json")):
            for label, grade in json.loads(path.read_text()).items():
                where = key[label]
                by_rules.setdefault(where["rules"], {})[f"{where['story']}/{where['run']}"] = grade
        for rules, grades in by_rules.items():
            (run.HERE / "results" / f"judge_{kind}_{rules}.json").write_text(json.dumps(grades, indent=1, sort_keys=True))
            print(f"{kind} {rules}: {len(grades)} grades")


if __name__ == "__main__":
    (pack if sys.argv[1] == "pack" else unpack)(Path(sys.argv[2]))
