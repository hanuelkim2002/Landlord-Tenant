"""Scores the skill versions' answers (results/<method>.jsonl): by meaning, with a judge model; by code, the quotes
and dates in each answer; and the author's blind ranks (ranks.json), once given. Writes scores.json and SCORES.md.
Run from this folder: python score.py
"""
import json
import os
import re
import statistics
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

from check_key import HERE, squash
from check_skills import check as check_skill

V2 = HERE.parents[1]
RESULTS = HERE / "results"
ENV_FILE = Path(os.environ.get("UF_ENV", V2 / ".env"))
JUDGE = "gpt-oss-120b"                                  # not nemotron, so the tested model never grades itself
METHODS = ["v1", "A", "B", "C"]
MONTHS = "January February March April May June July August September October November December".split()

JUDGE_PROMPT = """You grade a chatbot's answer to a Florida tenant about their security deposit. Judge meaning only,
never wording: a point counts if the answer conveys its substance in any words; words in parentheses in a point are
helpful detail, not required. Count as an error any claim the statute, the lease, or the facts below contradict, and
any rule stated without support in them.

THE STATUTE:
{statute}

THE LEASE:
{lease}

THE CONFIRMED FACTS (today is {today}):
{facts}

The tenant wrote: {message}
Right answer: {answer}
Points a right answer must make: {points}
Mistakes: {mistakes}

Chatbot's answer: {reply}

Reply with JSON only: {{"answers_first": true if the first sentence answers what the tenant asked, "points_made":
[true or false for each point], "mistakes_made": [true or false for each mistake], "other_error": "any other claim
that the statute, lease, or facts contradict, or empty", "reason": "one sentence"}}"""


def same_marks(text):
    """Every kind of hyphen as "-" and every quote mark as "'": typography, not wording."""
    text = re.sub("[‐‑]", "-", text).replace(" ", " ")
    return re.sub("[\"‘’“”]", "'", text)


def sources():
    """Every text a quote may come from, flattened for matching: the statutes and the lease."""
    texts = [p.read_text() for p in (V2 / "statutes").glob("*.txt")] + [(HERE / "lease.txt").read_text()]
    return [same_marks(squash(t)).lower() for t in texts]


def quotations(answer):
    """The quotations of 20 characters or more in an answer, in straight or curly double quotes."""
    return [q for q in re.findall(r'["“]([^"”]{20,}?)["”]', answer)]


def quote_checks_out(quote, texts):
    """Whether a quotation is word for word in a statute or the lease; an ellipsis splits it into parts."""
    parts = [p for p in re.split(r"\.\.\.|…", quote) if len(p.strip()) > 3]
    return bool(parts) and all(any(same_marks(squash(p)).lower() in t for t in texts) for p in parts)


def dates_in(text):
    """Every date written in the text, as YYYY-MM-DD: "2026-08-30", "August 30, 2026", or "August 30" (year 2026)."""
    found = set(re.findall(r"\b(20\d\d-\d\d-\d\d)\b", text))
    for month, day, year in re.findall(rf"\b({'|'.join(MONTHS)})\s+(\d{{1,2}})(?:st|nd|rd|th)?(?:,\s*(20\d\d))?", text):
        found.add(f"{year or 2026}-{MONTHS.index(month) + 1:02d}-{int(day):02d}")
    return found


def allowed_dates(story, tool_calls):
    """Dates an answer may give: the facts' dates, the lease's dates, the story's message, and count_days results."""
    allowed = dates_in(json.dumps(story["facts"])) | dates_in((HERE / "lease.txt").read_text()) | dates_in(story["message"])
    allowed |= set(re.findall(r"20\d\d-\d\d-\d\d", json.dumps(story["facts"])))
    for call in tool_calls:
        fact, days = call["arguments"].get("fact"), call["arguments"].get("days")
        value = story["facts"].get(str(fact), "")
        if call["name"] == "count_days" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)):
            allowed.add((date.fromisoformat(value) + timedelta(days=int(days or 0))).isoformat())
    return allowed


def judge(gateway, story, reply):
    """The judge's reading of one answer, as a dict."""
    statute = "\n\n".join((V2 / "statutes" / f"{s}.txt").read_text() for s in ("83.49", "83.505"))
    prompt = JUDGE_PROMPT.format(statute=statute, lease=(HERE / "lease.txt").read_text(), today=story["today"],
                                 facts=json.dumps(story["facts"], indent=1), message=story["message"],
                                 answer=story["answer"], points=json.dumps(story["points"]),
                                 mistakes=json.dumps(story["mistakes"]), reply=reply or "(no answer)")
    for _ in range(3):
        content = gateway.chat.completions.create(model=JUDGE, temperature=0, messages=[
            {"role": "user", "content": prompt}]).choices[0].message.content or ""
        try:
            return json.loads(content[content.find("{"):content.rfind("}") + 1])
        except json.JSONDecodeError:
            continue
    return {"answers_first": False, "points_made": [], "mistakes_made": [], "other_error": "judge failed", "reason": ""}


def verdict(story, grade):
    """Right, partly, or wrong, from the judge's reading."""
    points = (list(grade.get("points_made") or []) + [False] * len(story["points"]))[:len(story["points"])]
    if any(grade.get("mistakes_made") or []) or (grade.get("other_error") or "").strip():
        return "wrong"
    return "right" if all(points) else "partly" if any(points) else "wrong"


def score_method(gateway, method, stories, texts):
    """Every answer of one method, judged and checked; the judge's readings are kept in results/judge_<method>.json."""
    answers = [json.loads(l) for l in (RESULTS / f"{method}.jsonl").read_text().splitlines()]
    path = RESULTS / f"judge_{method}.json"
    grades = json.loads(path.read_text()) if path.exists() else {}
    todo = [a for a in answers if f"{a['story']}/{a['run']}" not in grades]
    with ThreadPoolExecutor(4) as pool:
        for a, g in zip(todo, pool.map(lambda a: judge(gateway, stories[a["story"]], a["answer"]), todo)):
            grades[f"{a['story']}/{a['run']}"] = g
    path.write_text(json.dumps(grades, indent=1))
    rows = []
    for a in answers:
        story, grade = stories[a["story"]], grades[f"{a['story']}/{a['run']}"]
        quotes = quotations(a["answer"])
        made_up = sorted(dates_in(a["answer"]) - allowed_dates(story, a["tool_calls"]))
        rows.append({"story": a["story"], "run": a["run"], "verdict": verdict(story, grade),
                     "answers_first": bool(grade.get("answers_first")), "quotes": len(quotes),
                     "quotes_ok": sum(quote_checks_out(q, texts) for q in quotes), "dates_made_up": made_up,
                     "seconds": a["seconds"], "tool_calls": len(a["tool_calls"]), "judge": grade})
    return rows


def summary(rows):
    """One method's totals."""
    return {"right": sum(r["verdict"] == "right" for r in rows), "partly": sum(r["verdict"] == "partly" for r in rows),
            "wrong": sum(r["verdict"] == "wrong" for r in rows), "answers": len(rows),
            "answers_first": sum(r["answers_first"] for r in rows),
            "quotes": sum(r["quotes"] for r in rows), "quotes_ok": sum(r["quotes_ok"] for r in rows),
            "answers_with_made_up_dates": sum(bool(r["dates_made_up"]) for r in rows),
            "seconds_median": statistics.median(r["seconds"] for r in rows)}


if __name__ == "__main__":
    gateway = OpenAI(base_url="https://api.ai.it.ufl.edu/v1", api_key=dotenv_values(ENV_FILE)["UF_API_KEY"])
    stories = {s["id"]: s for s in json.loads((HERE / "stories.json").read_text())["stories"]}
    texts = sources()
    scores = {}
    for method in METHODS:
        rows = score_method(gateway, method, stories, texts)
        quotes_in_skill, words = check_skill(method)
        scores[method] = {**summary(rows), "skill_words": words,
                          "skill_quotes_ok": f"{sum(ok for _, _, ok in quotes_in_skill)} of {len(quotes_in_skill)}",
                          "rows": rows}
        print(method, {k: v for k, v in scores[method].items() if k != "rows"}, flush=True)
    (HERE / "scores.json").write_text(json.dumps(scores, indent=1))
