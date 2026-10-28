"""Scores one skill's test from the graders' grades (judge.py unpack) and code's own counts: right, partly, and wrong
on the settled stories, made-up dates, quotes, and whether the skill was loaded. Writes scores.json and SCORES.md in
the skill's folder (a dry run's in results/dry/). Run from this folder: python grade.py repair_not_made [--dry]
"""
import argparse
import json
import sys

import run                                                    # a skill's stories, leases, and answers
import score                                                  # the model test's counts (run put it on the path)

sys.path.insert(0, str(run.V2))                               # score's quote count imports the app's checks.py

ORDER = ("v1", "new")                                         # the baseline first; other versions follow by name


def optional(point):
    """A point written wholly in parentheses: helpful detail, not required, as the rubric says."""
    return point.strip().startswith("(") and point.strip().endswith(")")


def verdict(story, grade):
    """Right, partly, or wrong, as score.story_verdict reads a grade, counting only the required points. The graders
    were told parentheses mark helpful detail, but some still required a point written wholly in parentheses."""
    made = (list(grade.get("points_made") or []) + [False] * len(story["points"]))[:len(story["points"])]
    required = [(p, m) for p, m in zip(story["points"], made) if not optional(p)]
    return score.story_verdict({"points": [p for p, _ in required]}, {**grade, "points_made": [m for _, m in required]})


def applies(reviewed, answer):
    """Whether a change in review.json still fits this answer: it quotes the words it turns on, and they are there. A
    rerun writes new answers under the same story and run, and an old change must not carry over to them."""
    return bool(reviewed.get("quote")) and reviewed["quote"] in answer


def rows_for(skill, version, stories, dry):
    """Every answer of one version, graded and counted, in the stories' order."""
    order = list(stories)
    folder = run.results_folder(skill, dry)
    lines = sorted(run.models.read_lines(folder / f"{version}.jsonl"),
                   key=lambda line: (order.index(line["story"]), line["run"]))
    grades = run.models.read_json(folder / f"judge_opus_{version}.json")
    review_file = run.test_folder(skill) / "review.json"      # my changes to the graders' verdicts, each with why
    review = run.models.read_json(review_file).get(version, {}) if review_file.exists() and not dry else {}
    missing = [f"{line['story']}/{line['run']}" for line in lines if f"{line['story']}/{line['run']}" not in grades]
    if missing:
        raise SystemExit(f"These {version} answers are not graded yet: {missing}")
    rows = []
    for line in lines:
        story = stories[line["story"]]
        row = score.story_row(line, story, order.index(story["id"]) + 1, grades[f"{story['id']}/{line['run']}"], {},
                              run.pages_for(skill, story)[0]["text"], [])
        row["skill_loaded"] = skill in line["skills_loaded"]  # story_row looks for the deposit skill only
        if not line.get("error"):                             # judge_verdict keeps the graders' own reading
            row["verdict"] = verdict(story, grades[f"{story['id']}/{line['run']}"])
        reviewed = review.get(f"{story['id']}/{line['run']}", {})
        if applies(reviewed, line["answer"]):
            row["verdict"], row["why_reviewed"] = reviewed["verdict"], reviewed["why"]
        rows.append(row)
    return rows


def summary(rows, stories):
    """One version's totals. Right, partly, and wrong count only the stories not marked open."""
    settled = [r for r in rows if not stories[r["story"]].get("open")]
    per_story = {}
    for r in rows:
        per_story.setdefault(r["story"], []).append(r["verdict"])
    return {"answers": len(rows), "settled": len(settled),
            **{v: sum(r["verdict"] == v for r in settled) for v in ("right", "partly", "wrong")},
            "right_every_point": sum(r["judge_verdict"] == "right" for r in settled),
            "made_up_dates": sum(bool(r["made_up_dates"]) for r in rows), "errors": sum(r["error"] for r in rows),
            "empty": sum(r["words"] == 0 for r in rows), "skill_loaded": sum(r["skill_loaded"] for r in rows),
            "quotes": sum(r["quotes"] for r in rows), "quotes_ok": sum(r["quotes_ok"] for r in rows),
            "seconds_median": score.middle([r["seconds"] for r in rows]),
            "cost": round(sum(r["cost"] for r in rows), 2), "per_story": per_story}


def markdown(skill, summaries, stories):
    """SCORES.md: the totals per version, then each story's verdicts per run."""
    versions = list(summaries)
    lines = [f"# {skill}: scores", "", "Claude Sonnet 5.5 answers, 3 runs a story, graded blind by Claude Opus 5.5.",
             "Written by grade.py.", "", "| | " + " | ".join(versions) + " |", "|---|" + "---|" * len(versions)]
    for name, label in (("right", "Right (settled)"), ("partly", "Partly"), ("wrong", "Wrong"),
                        ("right_every_point", "Right, as the graders read it"),
                        ("made_up_dates", "Made-up dates"), ("skill_loaded", "Skill loaded"), ("errors", "Errors"),
                        ("empty", "Empty answers"), ("cost", "Cost, $")):
        lines.append(f"| {label} | " + " | ".join(str(summaries[v][name]) for v in versions) + " |")
    lines.append("| Quotes right | " + " | ".join(f"{summaries[v]['quotes_ok']} of {summaries[v]['quotes']}"
                                                  for v in versions) + " |")
    lines += ["", "## Each story (R right, P partly, W wrong; runs 1 to 3)", "",
              "| Story | " + " | ".join(versions) + " |", "|---|" + "---|" * len(versions)]
    for story in stories.values():
        title = f"{story['id']}. {story['title']}" + (" (open)" if story.get("open") else "")
        cells = [" ".join(v[0].upper() for v in summaries[version]["per_story"].get(story["id"], []))
                 for version in versions]
        lines.append(f"| {title} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main():
    """Grade every version that has answers, baseline first, and write the scores."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill")
    parser.add_argument("--dry", action="store_true", help="the dry run's answers and grades")
    args = parser.parse_args()
    stories = {s["id"]: s for s in run.all_stories(args.skill)}
    folder = run.results_folder(args.skill, args.dry)
    found = sorted(p.stem for p in folder.glob("*.jsonl"))
    versions = [v for v in ORDER if v in found] + [v for v in found if v not in ORDER]
    rows = {v: rows_for(args.skill, v, stories, args.dry) for v in versions}
    summaries = {v: summary(rows[v], stories) for v in versions}
    out = folder if args.dry else run.test_folder(args.skill)
    (out / "scores.json").write_text(json.dumps({"summaries": summaries, "rows": rows}, indent=1))
    (out / "SCORES.md").write_text(markdown(args.skill, summaries, stories))
    print(f"wrote scores.json and SCORES.md in {out}")


if __name__ == "__main__":
    main()
