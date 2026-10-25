"""Scores the memory test: per answer, what code can count (the tools called, the lines saved, any date the model
wrote that comes from nowhere, the questions asked) and Claude's reading in review.json; then SCORES.md, the new
memory and the baseline side by side. Run from this folder: python score.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "models"))
from score import dates_in, question_count  # noqa: E402  (the model test's date and question counters)

STORIES = {s["id"]: s for s in json.loads((HERE / "stories.json").read_text())["stories"]}
LEASE = (HERE.parent / "skills" / "lease.txt").read_text()
MODES = ["new", "baseline"]
CHECKS = [("no_retelling", "Asks for nothing it was already told"), ("picks_up_open", "Picks up what was left open"),
          ("saved_line", "Saves the new event as a line"), ("closes_open_line", "Closes the line left open"),
          ("no_made_up_date", "Works out no date itself"), ("answers_first", "Answers first")]
TIMELINE_ONLY = {"saved_line", "closes_open_line"}             # the baseline has no timeline to keep


def counted(line):
    """What code counts in one answer."""
    story = STORIES[line["story"]]
    year = int(story["today"][:4])                            # a date written without a year is in the story's year
    allowed = dates_in(json.dumps(story), year) | dates_in(LEASE, year)
    for call in line["tool_calls"]:                           # dates a tool gave the model are not made up
        allowed |= set(re.findall(r"20\d\d-\d\d-\d\d", str(call["result"])))
    saved = [c for c in line["tool_calls"] if c["name"] == "save_line"]
    return {"tools": [c["name"] for c in line["tool_calls"]], "lines_saved": len(saved),
            "saved_line": bool(saved), "made_up_dates": sorted(dates_in(line["answer"], year) - allowed),
            "questions": question_count(line["answer"])}


def row(line, reviewed):
    """One answer's five checks: code's counts, with Claude's reading where code cannot tell."""
    counts = counted(line)
    return {**counts, "no_retelling": reviewed.get("no_retelling", False),
            "picks_up_open": reviewed.get("picks_up_open", False), "answers_first": reviewed.get("answers_first", False),
            "closes_open_line": reviewed.get("closes_open_line", False),
            "no_made_up_date": reviewed.get("no_made_up_date", not counts["made_up_dates"]),
            "why": reviewed.get("why", "not reviewed yet")}


def table(rows_by_mode):
    """The five checks, each mode out of its answers."""
    lines = ["| Check | New memory | Baseline (main) |", "| --- | --- | --- |"]
    for key, label in CHECKS:
        cells = []
        for mode in MODES:
            rows = rows_by_mode[mode]
            cells.append("n/a (no timeline)" if key in TIMELINE_ONLY and mode == "baseline"
                         else f"{sum(r[key] for r in rows)} of {len(rows)}")
        lines.append(f"| {label} | {cells[0]} | {cells[1]} |")
    return "\n".join(lines)


def main():
    """Read the results and the review, print the table, and write SCORES.md."""
    review_path = HERE / "review.json"
    review = json.loads(review_path.read_text()) if review_path.exists() else {}
    rows_by_mode, notes = {}, []
    for mode in MODES:
        results = [json.loads(text) for text in (HERE / "results" / f"{mode}.jsonl").read_text().splitlines()]
        results.sort(key=lambda line: (line["story"], line["run"]))
        rows_by_mode[mode] = []
        for line in results:
            r = row(line, review.get(f"{mode}/{line['story']}/{line['run']}", {}))
            rows_by_mode[mode].append(r)
            notes.append(f"- **{mode}, {line['story']}, run {line['run']}** ({line['seconds']} s, ${line['cost']:.4f}): "
                         f"tools {', '.join(r['tools']) or 'none'}; lines saved {r['lines_saved']}; questions "
                         f"{r['questions']}; dates from nowhere: {', '.join(r['made_up_dates']) or 'none'}. {r['why']}")
        cost = sum(json.loads(t)["cost"] for t in (HERE / "results" / f"{mode}.jsonl").read_text().splitlines())
        notes.append(f"- {mode}: ${cost:.4f} in all")
    summary = table(rows_by_mode)
    print(summary)
    (HERE / "SCORES.md").write_text(
        "# Memory test: scores\n\nClaude Sonnet 5.5, 3 runs of each of 3 return visits (`stories.json`), the new memory "
        "against v2 on `main`. Code counts the tools, the lines saved, and dates found nowhere in the story, the lease, "
        "or a tool's result; Claude read every answer for the rest (`review.json`).\n\n"
        f"{summary}\n\n## Each answer\n\n" + "\n".join(notes) + "\n")


if __name__ == "__main__":
    main()
