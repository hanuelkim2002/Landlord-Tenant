"""Scores the plain-replies test. Code counts, per answer: the format, the words the tenant sees first, any section
number or quotation there, and a question hidden in a box. The Opus graders give right, partly, or wrong (settled
stories only) and the plain-reading counts, with my review of those counts (review_plain.json) applied. Writes
scores.json and SCORES.md, and prints the spec's targets, met or missed. Run from this folder: python grade.py
"""
import json

import judge                                                  # this test's answers and the app's split; first, as it
import checks                                                 # puts v2 on the path for the app's quote and cite patterns
import score                                                  # the model test's scorer: the verdict, the median, tables

HERE = judge.run.HERE
OPEN_STORIES = ("deposit-2", "deposit-5")                     # their keys turn on the author's open calls (AUTHOR.md 3, 4)


def answer_row(line, story, right, plain, reviewed):
    """Everything counted about one answer."""
    short, points = judge.chat.split_reply(line["answer"])
    return {"rules": line["rules"], "story": line["story"], "run": line["run"],
            "format_followed": any(title != judge.chat.WHY for title, _ in points),
            "short_words": len(short.split()),
            "cites_in_short": bool(checks.STATUTE_CITE.search(short) or checks.QUOTE.search(short)),
            # the one question belongs in the short part; one at the end of the last box is out of sight
            "question_hidden": "?" not in short and bool(points) and points[-1][1].rstrip().endswith("?"),
            "verdict": None if story["id"] in OPEN_STORIES else score.story_verdict(story, right),
            "unclear_words": reviewed.get("unclear_words", len(plain["unclear_words"])),
            "legal_words": reviewed.get("legal_words", len(plain["legal_words"])),
            "answers_alone": bool(plain["answers_alone"]), "words": len(line["answer"].split()),
            "cost": line["cost"]}


def rows_for(rules, stories, review):
    """Every answer of one set of rules, in the stories' order, with its grades."""
    right = score.models.read_json(HERE / "results" / f"judge_right_{rules}.json")
    plain = score.models.read_json(HERE / "results" / f"judge_plain_{rules}.json")
    order = list(stories)
    lines = sorted(score.models.read_lines(HERE / "results" / f"{rules}.jsonl"),
                   key=lambda line: (order.index(line["story"]), line["run"]))
    key = lambda line: f"{line['story']}/{line['run']}"
    return [answer_row(line, stories[line["story"]], right[key(line)], plain[key(line)], review.get(key(line), {}))
            for line in lines]


def summary(rows):
    """One set of rules' totals."""
    settled = [r for r in rows if r["verdict"]]
    per_story = {}
    for r in settled:
        per_story.setdefault(r["story"], []).append(r["verdict"])
    count = lambda field: sum(r[field] for r in rows)
    return {"answers": len(rows), "settled": len(settled),
            **{v: sum(r["verdict"] == v for r in settled) for v in ("right", "partly", "wrong")},
            "format_followed": count("format_followed"), "cites_in_short": count("cites_in_short"),
            "question_hidden": count("question_hidden"), "answers_alone": count("answers_alone"),
            "short_words_median": score.middle([r["short_words"] for r in rows]),
            "words_median": score.middle([r["words"] for r in rows]),
            "unclear_median": score.middle([r["unclear_words"] for r in rows]), "unclear_total": count("unclear_words"),
            "legal_median": score.middle([r["legal_words"] for r in rows]), "legal_total": count("legal_words"),
            "cost": round(sum(r["cost"] for r in rows), 2), "per_story": per_story}


def targets(old, new):
    """The spec's targets, each with whether the new rules met it. "Lower than today's rules" is read on the totals,
    since a median of 0 cannot drop."""
    return [(f"Format followed in at least {new['answers'] - 2} of {new['answers']} new answers",
             new["format_followed"] >= new["answers"] - 2),
            ("Median short part 100 words or less", new["short_words_median"] <= 100),
            ("Unclear words: median 0, and fewer in all than the old rules",
             new["unclear_median"] == 0 and new["unclear_total"] < old["unclear_total"]),
            ("Unexplained legal words: median 0, and fewer in all than the old rules",
             new["legal_median"] == 0 and new["legal_total"] < old["legal_total"]),
            ("Right answers not fewer than the old rules", new["right"] >= old["right"])]


def markdown(s, stories, review, met):
    """SCORES.md: the targets, the totals, each story's verdicts, and my changes to the plain counts."""
    rows = [[name] + [str(s[r][field]) for r in ("old", "new")] for name, field in (
        (f"Right, settled stories (of {s['new']['settled']})", "right"), ("Partly", "partly"), ("Wrong", "wrong"),
        (f"Format followed (of {s['new']['answers']})", "format_followed"),
        ("Median words seen first", "short_words_median"), ("Median words in all", "words_median"),
        ("Section number or quote seen first", "cites_in_short"), ("Question hidden in a box", "question_hidden"),
        ("Unclear words, median", "unclear_median"), ("Unclear words, in all", "unclear_total"),
        ("Unexplained legal words, median", "legal_median"), ("Unexplained legal words, in all", "legal_total"),
        ("Seen first answers the question alone", "answers_alone"), ("Cost of the run, $", "cost"))]
    per_story = [[f"{story['id'].split('-')[1]}. {story['title']}"]
                 + [" ".join(v[0].upper() for v in s[r]["per_story"].get(story["id"], [])) for r in ("old", "new")]
                 for story in stories.values() if story["id"] not in OPEN_STORIES]
    notes = [f"- {r}, {key}: unclear {c.get('unclear_words', '-')}, legal {c.get('legal_words', '-')}. {c['why']}"
             for r in ("old", "new") for key, c in review.get(r, {}).items()]
    return "\n\n".join([
        "# Plain replies test: scores",
        "Sonnet 5.5 from Anthropic, 18 deposit stories, 3 runs each, with the old rules and the new. Right, partly, "
        "and wrong: Claude Opus 5.5, blind. Plain counts: Claude Opus 5.5, with my review. Written by grade.py.",
        "## Targets", "\n".join(f"- {'Met' if ok else 'Missed'}: {name}" for name, ok in met),
        "## Totals", "\n".join(score.table(["", "old", "new"], rows)),
        "## Each settled story (R right, P partly, W wrong; runs 1 to 3)",
        "\n".join(score.table(["Story", "old", "new"], per_story)),
        "## My changes to the plain counts", "\n".join(notes) or "None."]) + "\n"


def main():
    """Count and grade both sets of answers, write the score files, and print the targets."""
    stories = {s["id"]: s for s in judge.run.deposit.all_stories()}
    review_path = HERE / "review_plain.json"
    review = score.models.read_json(review_path) if review_path.exists() else {}
    all_rows = {r: rows_for(r, stories, review.get(r, {})) for r in ("old", "new")}
    s = {r: summary(rows) for r, rows in all_rows.items()}
    met = targets(s["old"], s["new"])
    (HERE / "scores.json").write_text(json.dumps({"summaries": s, "targets": met, "rows": all_rows}, indent=1))
    (HERE / "SCORES.md").write_text(markdown(s, stories, review, met))
    for name, ok in met:
        print(f"{'Met   ' if ok else 'MISSED'} {name}")
    print("wrote scores.json and SCORES.md")


if __name__ == "__main__":
    main()
