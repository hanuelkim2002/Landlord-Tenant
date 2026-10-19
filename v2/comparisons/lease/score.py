"""Scores each method's answers (results/<method>.jsonl): by meaning, with a judge model, and word for word, by code.
Writes scores.json (every question) and SCORES.md (the summary). Run from this folder: python score.py
"""
import json
import os
import re
import statistics
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import PyPDF2
from dotenv import dotenv_values
from openai import OpenAI

from check_key import squash
from make_leases import HERE

RESULTS = HERE / "results"
ENV_FILE = Path(os.environ.get("UF_ENV", HERE.parent.parent / ".env"))
SAMPLE = Path(os.environ.get("SAMPLE_LEASE", HERE.parent.parent / "lease.pdf"))
JUDGE = "gpt-oss-120b"                  # not nemotron, so the tested model never grades itself
METHODS = ["v1", "A", "B", "C"]
LEASES = ["short_headings", "long_numbered", "scanned", "broken_text", "sample_v1"]

JUDGE_PROMPT = """You grade a chatbot's answer to a tenant's question about their lease. Judge meaning only, never
wording: a point counts if the answer makes it in any words. Extra details are fine if the lease supports them.

Question: {question}
The lease's words that answer it: {passages}
Right answer: {answer}
Points a right answer must make: {points}
Mistakes: {mistakes}

Chatbot's answer: {reply}

Reply with JSON only: {{"says_lease_silent": true or false, "points_made": [true or false for each point],
"mistakes_made": [true or false for each mistake], "other_error": "any other claim that contradicts the lease, or empty",
"reason": "one sentence"}}"""


# ---- Word for word (code)

def stored_text(method, lease):
    """The lease text a method's quotes must match: step 1's text for A, B, C; PyPDF2's text for v1."""
    if method == "v1":
        pdf = SAMPLE if lease == "sample_v1" else HERE / "leases" / f"{lease}.pdf"
        return "\n".join(page.extract_text() or "" for page in PyPDF2.PdfReader(pdf).pages)
    return "\n".join(p["text"] for p in json.loads((HERE / "texts" / f"{lease}.json").read_text())["pages"])


def quote_checks_out(quote, text):
    """Whether a quote is word for word in the text, spacing, line breaks, capitals, and quote marks aside.
    A quote with "..." in it counts if each part is there."""
    parts = [p for p in re.split(r"\.\.\.|…", quote) if p.strip()]
    return bool(parts) and all(squash(p).lower() in text for p in parts)


def plain_words(text):
    """Lowercase letters and digits only, as a list of words, for matching a quote to a passage."""
    return re.findall(r"[a-z0-9]+", text.lower())


def quotes_right_clause(quote, passage):
    """Whether a quote comes from the passage: 8 words in a row from it, or 4 or more words wholly inside it."""
    q, p = plain_words(quote), plain_words(passage)
    inside = " ".join(q) in " ".join(p)
    if len(q) >= 4 and inside:
        return True
    runs = {" ".join(q[i:i + 8]) for i in range(len(q) - 7)}
    return any(run in " ".join(p) for run in runs)


# ---- By meaning (the judge)

def judge(gateway, question, reply):
    """The judge's reading of one answer, as a dict."""
    prompt = JUDGE_PROMPT.format(
        question=question["question"], answer=question["answer"],
        passages=json.dumps(question["passages"]) if question["passages"] else
        "none; the lease does not address this question" + (f" ({question['note']})" if question.get("note") else ""),
        points=json.dumps(question["points"]), mistakes=json.dumps(question["mistakes"]), reply=reply or "(no answer)")
    for _ in range(3):
        content = gateway.chat.completions.create(model=JUDGE, temperature=0, messages=[
            {"role": "user", "content": prompt}]).choices[0].message.content or ""
        start, end = content.find("{"), content.rfind("}")
        try:
            return json.loads(content[start:end + 1])
        except json.JSONDecodeError:
            continue
    return {"says_lease_silent": False, "points_made": [], "mistakes_made": [], "other_error": "judge failed",
            "reason": "the judge's reply could not be read"}


def verdict(question, grade):
    """Right, partly, or wrong, from the judge's reading."""
    points = list(grade.get("points_made") or []) + [False] * len(question["points"])
    points = points[:len(question["points"])]
    erred = any(grade.get("mistakes_made") or []) or bool((grade.get("other_error") or "").strip())
    silent = bool(grade.get("says_lease_silent"))
    if not question["covered"]:
        return "right" if silent and not erred else "wrong"
    if silent or erred:
        return "wrong"
    return "right" if all(points) else "partly" if any(points) else "wrong"


def judged(gateway, method, key):
    """The judge's reading of each of a method's answers, kept in results/judge_<method>.json so a rerun reuses it."""
    path = RESULTS / f"judge_{method}.json"
    grades = json.loads(path.read_text()) if path.exists() else {}
    answers = [json.loads(l) for l in (RESULTS / f"{method}.jsonl").read_text().splitlines()]
    todo = [a for a in answers if a["id"] not in grades]
    with ThreadPoolExecutor(4) as pool:
        for answer, grade in zip(todo, pool.map(lambda a: judge(gateway, key[a["id"]], a["answer"]), todo)):
            grades[answer["id"]] = grade
    path.write_text(json.dumps(grades, indent=1))
    return answers, grades


# ---- The summary

def summarize(method, answers, grades, key, texts, intake):
    """Every score for one method, overall and per lease."""
    rows = []
    for a in answers:
        q = key[a["id"]]
        text = texts[(method, q["lease"])]
        rows.append({
            "id": a["id"], "lease": q["lease"], "covered": q["covered"], "verdict": verdict(q, grades[a["id"]]),
            "silent": bool(grades[a["id"]].get("says_lease_silent")),
            "quotes": len(a["quotes"]), "quotes_ok": sum(quote_checks_out(x, text) for x in a["quotes"]),
            "right_clause": any(quotes_right_clause(x, p) for x in a["quotes"] for p in q["passages"]),
            "seconds": a["seconds"], "tool_calls": len(a["tool_calls"]),
            "answer": a["answer"], "judge": grades[a["id"]]})
    covered = [r for r in rows if r["covered"]]

    def counts(part):
        return {v: sum(r["verdict"] == v for r in part) for v in ("right", "partly", "wrong")}

    return {
        "verdicts": counts(rows),
        "wrongly_silent": sum(r["silent"] for r in covered),
        "made_up": sum(not r["silent"] for r in rows if not r["covered"]),
        "quotes": sum(r["quotes"] for r in rows), "quotes_ok": sum(r["quotes_ok"] for r in rows),
        "right_clause_quoted": sum(r["right_clause"] for r in covered), "covered": len(covered),
        "answer_seconds_median": statistics.median(r["seconds"] for r in rows),
        "answer_seconds_max": max(r["seconds"] for r in rows),
        "per_lease": {lease: {**counts([r for r in rows if r["lease"] == lease]),
                              "answer_seconds_median": statistics.median(
                                  [r["seconds"] for r in rows if r["lease"] == lease] or [0]),
                              "intake_seconds": intake.get(lease)} for lease in LEASES},
        "rows": rows}


def intake_seconds(method):
    """Seconds from PDF to ready, per lease: v1's own intake; step 1 plus the method's setup for A, B, C."""
    own = json.loads((RESULTS / f"{method}_intake.json").read_text())
    if method == "v1":
        return {lease: round(own[lease], 1) for lease in own}
    step1 = json.loads((HERE / "readers.json").read_text())
    return {lease: round(step1[lease]["step1"]["step1_seconds"] + own[lease], 1) for lease in own}


def markdown(scores):
    """SCORES.md: one table overall, one per lease."""
    lines = ["# Lease intake: scores", "",
             "| Method | Right | Partly | Wrong | Wrongly silent | Made up | Quotes check out | Quoted the right clause"
             " | Answer time (typical, slowest) |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for m, s in scores.items():
        v = s["verdicts"]
        lines.append(f"| {m} | {v['right']} | {v['partly']} | {v['wrong']} | {s['wrongly_silent']} of {s['covered']} "
                     f"| {s['made_up']} of {len(s['rows']) - s['covered']} | {s['quotes_ok']} of {s['quotes']} "
                     f"| {s['right_clause_quoted']} of {s['covered']} | {s['answer_seconds_median']:.0f} s, "
                     f"{s['answer_seconds_max']:.0f} s |")
    lines += ["", "## Per lease: right answers, and intake time (PDF to ready)", "",
              "| Lease | " + " | ".join(scores) + " |", "| --- |" + " --- |" * len(scores)]
    for lease in LEASES:
        cells = []
        for s in scores.values():
            p = s["per_lease"][lease]
            total = p["right"] + p["partly"] + p["wrong"]
            cells.append(f"{p['right']} of {total} right, intake {p['intake_seconds']} s")
        lines.append(f"| {lease} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    gateway = OpenAI(base_url="https://api.ai.it.ufl.edu/v1", api_key=dotenv_values(ENV_FILE)["UF_API_KEY"])
    key = {q["id"]: q for q in json.loads((HERE / "answer_key.json").read_text())["questions"]}
    scores = {}
    for method in METHODS:
        if not (RESULTS / f"{method}.jsonl").exists():
            continue
        texts = {(method, lease): squash(stored_text(method, lease)).lower() for lease in LEASES}
        answers, grades = judged(gateway, method, key)
        scores[method] = summarize(method, answers, grades, key, texts, intake_seconds(method))
        print(method, scores[method]["verdicts"], "wrongly silent", scores[method]["wrongly_silent"], flush=True)
    (HERE / "scores.json").write_text(json.dumps(scores, indent=1))
    (HERE / "SCORES.md").write_text(markdown(scores))
