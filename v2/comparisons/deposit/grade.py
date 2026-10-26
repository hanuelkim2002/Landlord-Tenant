"""Grades the deposit skill test: a judge reads each answer by meaning against its story's key, and code counts quotes,
made-up dates, questions, and empty answers. Two judges: gpt-oss-120b on UF (the model test's judge; my changes to
its grades are in review.json), or Claude Opus 5.5, blind (its grades come from opus_judge.py). Writes scores.json and
SCORES.md, or scores_opus.json and SCORES_opus.md. Run from this folder: python grade.py   (or --judge opus)
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "models"))
import models                                                 # the model test's set-up and file helpers
import run                                                    # this test's stories and their leases
import score                                                  # the model test's scorer: judge prompt, verdicts, counts

# judge: (its grades file per version, my review of its grades, the suffix on the score files, its name)
JUDGES = {"gpt-oss": ("judge_{}.json", "review.json", "", "gpt-oss-120b on UF"),
          "opus": ("judge_opus_{}.json", "review_opus.json", "_opus", "Claude Opus 5.5, blind")}
OPEN_STORIES = ("deposit-2", "deposit-5")                     # their keys turn on the author's open calls (AUTHOR.md 3, 4)
# Every section the stories rest on, so the judge does not count a right point from 83.42 or 83.491 as an error.
STATUTE = "\n\n".join((models.V2 / "statutes" / f"{s}.txt").read_text()
                      for s in ("83.42", "83.43", "83.49", "83.491", "83.505"))


def lease_of(story):
    """The lease text the story was answered with."""
    return run.pages_for(story)[0]["text"]


def key_of(line):
    """An answer's key in the judge's and the review's files, like "deposit-6/2"."""
    return f"{line['story']}/{line['run']}"


def prompt_for(story, line):
    """The judge's prompt for one answer."""
    return score.STORY_PROMPT.format(statute=STATUTE, lease=lease_of(story), today=story["today"],
                                     facts=json.dumps(story["facts"], indent=1), message=story["message"],
                                     answer=story["answer"], points=json.dumps(story["points"]),
                                     mistakes=json.dumps(story["mistakes"]), reply=line["answer"] or "(no answer)")


def grade_version(gateway, version, stories, review, judge, model):
    """Every answer of one version, judged and counted, in the stories' order. gpt-oss is asked for any answer it
    has not graded yet; Opus's grades must all be there already (opus_judge.py unpack)."""
    order = list(stories)
    lines = sorted(models.read_lines(run.results_folder(model) / f"{version}.jsonl"),
                   key=lambda line: (order.index(line["story"]), line["run"]))
    grades_file = run.results_folder(model) / JUDGES[judge][0].format(version)
    if judge == "opus":
        grades = models.read_json(grades_file)
        missing = [key_of(line) for line in lines if key_of(line) not in grades]
        if missing:
            raise SystemExit(f"Opus has not graded these {version} answers: {missing}")
    else:
        grades = score.judge_all(gateway, grades_file, [(key_of(line), line) for line in lines],
                                 lambda line: prompt_for(stories[line["story"]], line))
    return [score.story_row(line, stories[line["story"]], order.index(line["story"]) + 1, grades.get(key_of(line)),
                            review.get(version, {}).get(key_of(line), {}), lease_of(stories[line["story"]]), [])
            for line in lines]


def summary(rows):
    """One version's totals. Right, partly, and wrong count only the ten stories whose keys are settled."""
    settled = [r for r in rows if r["story"] not in OPEN_STORIES]
    per_story = {}
    for r in rows:
        per_story.setdefault(r["story"], []).append(r["verdict"])
    return {"answers": len(rows), **{v: sum(r["verdict"] == v for r in settled) for v in ("right", "partly", "wrong")},
            "settled": len(settled), "empty": sum(r["words"] == 0 for r in rows),
            "answers_first": sum(r["answers_first"] for r in rows),
            "made_up_dates": sum(bool(r["made_up_dates"]) for r in rows),
            "asks_more_than_one": sum(r["questions_asked"] >= 2 for r in rows),
            "skill_loaded": sum(r["skill_loaded"] for r in rows), "count_days_used": sum(r["count_days_used"] for r in rows),
            "quotes": sum(r["quotes"] for r in rows), "quotes_ok": sum(r["quotes_ok"] for r in rows),
            "words_median": score.middle([r["words"] for r in rows]), "seconds_median": score.middle([r["seconds"] for r in rows]),
            "cost_mean": score.average([r["cost"] for r in rows]), "per_story": per_story}


def markdown(summaries, stories, review, judge_name, model):
    """SCORES.md: the totals, each story's verdicts per version, and my changes to the judge's grades."""
    s = summaries
    versions = list(s)                                        # the versions graded this time, in order
    last = s[versions[-1]]
    ran = [story for story in stories.values() if story["id"] in last["per_story"]]   # the stories this run had
    rows = [[name] + [str(s[v][field]) for v in versions] for name, field in (
        (f"Right, settled stories (of {last['settled']})", "right"), ("Partly", "partly"), ("Wrong", "wrong"),
        (f"Empty answers (of {last['answers']})", "empty"), ("Answers first", "answers_first"),
        ("Made-up dates", "made_up_dates"),
        ("Asks more than one question", "asks_more_than_one"), ("Skill loaded", "skill_loaded"),
        ("count_days used", "count_days_used"), ("Median words", "words_median"),
        ("Median seconds", "seconds_median"))]
    rows.append(["Quotes word for word"] + [f"{s[v]['quotes_ok']} of {s[v]['quotes']}" for v in versions])
    rows.append(["Cost per answer"] + [f"${s[v]['cost_mean']:.4f}" for v in versions])
    per_story = [[f"{story['id'].split('-')[1]}. {story['title']}" + (" (open call)" if story["id"] in OPEN_STORIES else "")]
                 + [" ".join(verdict[0].upper() for verdict in s[v]["per_story"].get(story["id"], [])) for v in versions]
                 for story in ran]
    notes = [f"- {v}, {key}: {change['verdict']}. {change['why']}" for v in versions for key, change in review.get(v, {}).items()]
    chat = {"gemini": "Gemini", "sonnet": "Sonnet 5.5"}[model]
    return "\n\n".join([
        "# Deposit skill test: scores",
        f"{chat}, {len(ran)} stories, 3 runs each, per skill version. Judge: {judge_name}. Written by grade.py.",
        "## Totals", "\n".join(score.table(["", *versions], rows)),
        "## Each story (R right, P partly, W wrong; runs 1 to 3)", "\n".join(score.table(["Story", *versions], per_story)),
        "## My changes to the judge's grades", "\n".join(notes) or "None."]) + "\n"


def main():
    """Judge and count every version's answers, and write the score files."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--judge", choices=list(JUDGES), default="gpt-oss")
    parser.add_argument("--model", choices=list(run.CHAT), default="gemini", help="whose answers: results/ or results/sonnet/")
    parser.add_argument("--versions", default="v1,old,new", help="which skill versions, in order, like fixed")
    args = parser.parse_args()
    judge, model, versions = args.judge, args.model, args.versions.split(",")
    _, review_name, suffix, judge_name = JUDGES[judge]
    suffix += "" if model == "gemini" else f"_{model}"        # Gemini's files keep their first names
    suffix += "" if versions == ["v1", "old", "new"] else "_" + "_".join(versions)
    app = models.setup("uf")                                  # gpt-oss runs on UF, through the app's own client
    gateway = app.config.client()
    stories = {story["id"]: story for story in run.all_stories()}
    review_path = HERE / review_name
    review = models.read_json(review_path) if review_path.exists() and model == "gemini" else {}
    all_rows = {v: grade_version(gateway, v, stories, review, judge, model) for v in versions}
    summaries = {v: summary(rows) for v, rows in all_rows.items()}
    (HERE / f"scores{suffix}.json").write_text(json.dumps({"summaries": summaries, "rows": all_rows}, indent=1))
    (HERE / f"SCORES{suffix}.md").write_text(markdown(summaries, stories, review, judge_name, model))
    for v in versions:
        print(f"{v}: right {summaries[v]['right']}, partly {summaries[v]['partly']}, wrong {summaries[v]['wrong']} "
              f"of {summaries[v]['settled']}; empty {summaries[v]['empty']}")
    print(f"wrote scores{suffix}.json and SCORES{suffix}.md")


if __name__ == "__main__":
    main()
