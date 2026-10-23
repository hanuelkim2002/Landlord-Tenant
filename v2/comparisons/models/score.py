"""Scores what the model comparison has produced so far: a judge model (gpt-oss-120b on UF, not a tested model) grades
answers by meaning, and code counts quotes, dates, questions, and reader accuracy. Writes scores.json and SCORES.md
(numbers only) and private/SCORES_own_detail.md. Run: python score.py   (--dry: the made-up results; --show-boxes)
"""
import argparse
import difflib
import json
import re
import statistics
from concurrent.futures import ThreadPoolExecutor

import pymupdf

import models

JUDGE = "gpt-oss-120b"
# Stories 2 and 5 turn on the author's open calls (AUTHOR.md items 3 and 4), so they are shown apart.
MAIN_STORIES = (1, 3, 4)
OPEN_STORIES = (2, 5)
MONTHS = "January February March April May June July August September October November December".split()
SAMPLE_READ_LEASES = ("scanned", "broken_text")

# Copied from comparisons/skills/score.py (stories) and comparisons/lease/score.py (questions), so the grades match
# those tests. They are copied, not imported, because the two old scorers each import a module named check_key
# and cannot be imported in one process. The two verdict functions are renamed; their bodies are unchanged.

STORY_PROMPT = """You grade a chatbot's answer to a Florida tenant about their security deposit. Judge meaning only,
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

QUESTION_PROMPT = """You grade a chatbot's answer to a tenant's question about their lease. Judge meaning only, never
wording: a point counts if the answer conveys its substance in any words. Words in parentheses in a point are helpful
detail, not required. Extra details in the answer are fine if the whole lease below supports them; count them as an
error only if the lease contradicts them or does not say them.

THE WHOLE LEASE:
{lease}

Question: {question}
The lease's words that answer it: {passages}
Right answer: {answer}
Points a right answer must make: {points}
Mistakes: {mistakes}

Chatbot's answer: {reply}

"says_lease_silent" is true only if the answer says the lease does not address the question at all (for example
"the lease does not say"). An answer that gives any answer from the lease, even a short one like "$75.00", is false.

Reply with JSON only: {{"says_lease_silent": true or false, "points_made": [true or false for each point],
"mistakes_made": [true or false for each mistake], "other_error": "any other claim that contradicts the lease, or empty",
"reason": "one sentence"}}"""


def dates_in(text, year_if_missing=2026):
    """Every date written in the text, as YYYY-MM-DD: "2026-08-30", "August 30, 2026", or "August 30" (a year given by
    the caller, 2026 unless said otherwise)."""
    found = set(re.findall(r"\b(20\d\d-\d\d-\d\d)\b", text))
    # \b after the day, so "July 2026" (a month and a year) is not read as July 20
    for month, day, year in re.findall(rf"\b({'|'.join(MONTHS)})\s+(\d{{1,2}})(?:st|nd|rd|th)?\b(?:,\s*(20\d\d))?", text):
        found.add(f"{year or year_if_missing}-{MONTHS.index(month) + 1:02d}-{int(day):02d}")
    return found


def quotations(answer):
    """The quotations of 20 characters or more in an answer, in straight or curly double quotes."""
    return [q for q in re.findall(r'["“]([^"”]{20,}?)["”]', answer)]


def story_verdict(story, grade):
    """Right, partly, or wrong, from the judge's reading."""
    points = (list(grade.get("points_made") or []) + [False] * len(story["points"]))[:len(story["points"])]
    if any(grade.get("mistakes_made") or []) or (grade.get("other_error") or "").strip():
        return "wrong"
    return "right" if all(points) else "partly" if any(points) else "wrong"


def question_verdict(question, grade):
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


# Copied from comparisons/lease/score_readers.py (same reason).

def words_of(text):
    """The text as lowercase words and numbers, for comparing what was read with what was written."""
    return re.findall(r"[a-z0-9$]+", text.lower())


def word_accuracy(read, written):
    """The share of the written words that come back, in order."""
    want = words_of(written)
    matcher = difflib.SequenceMatcher(None, want, words_of(read), autojunk=False)
    return sum(block.size for block in matcher.get_matching_blocks()) / max(len(want), 1)


# Copied from comparisons/lease/make_leases.py: that file needs fpdf, which v2's venv does not have.

def source_lines(name):
    """The lines of a sample lease's source text. The long lease is kept in several files, read in order."""
    path = models.LEASE_TEST / "sources" / name
    files = sorted(path.glob("*.txt")) if path.is_dir() else [models.LEASE_TEST / "sources" / f"{name}.txt"]
    return "\n".join(f.read_text() for f in files).splitlines()


def plain_text(name):
    """The lease's words with the layout marks taken out: what a perfect reader would get from the PDF."""
    words = []
    for line in source_lines(name):
        if line.strip() == "<<page>>":
            continue
        if line.startswith("|"):
            line = " ".join(cell.strip() for cell in line.strip("|").split("|"))
        words.append(line.lstrip("# "))
    return "\n".join(words)


# ---- Small helpers

def middle(values):
    """The median of a list, or None if it is empty."""
    return statistics.median(values) if values else None


def average(values):
    """The mean of a list, or None if it is empty."""
    return statistics.mean(values) if values else None


def counts(rows):
    """How many rows are right, partly, and wrong."""
    return {v: sum(r["verdict"] == v for r in rows) for v in ("right", "partly", "wrong")}


def money(value, estimated=False):
    """A cost in dollars; ~ marks one worked out from list prices, not reported by the gateway."""
    return "-" if value is None else f"{'~' if estimated else ''}${value:.4f}"


def seconds_text(value):
    """Seconds, to one decimal."""
    return "-" if value is None else f"{value:.1f} s"


def ratio(value):
    """A share as a percent."""
    return "-" if value is None else f"{100 * value:.1f}%"


def table(headers, rows):
    """A markdown table."""
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    return lines + ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]


def reviews(own):
    """My changes to the judge's grades: {model: {"story/run": {"verdict", "why"}}} for the stories, and
    {"questions": {file stem: {id: {"verdict", "why"}}}} for the lease questions."""
    path = (models.PRIVATE if own else models.HERE) / "review.json"
    return models.read_json(path) if path.exists() else {}


def author_ranks(blind_folder):
    """The author's blind ranks, matched to the models through key.json: {model: {story: rank}}. Empty if not filled."""
    ranks_file, key_file = blind_folder / "ranks.json", blind_folder / "key.json"
    if not ranks_file.exists() or not key_file.exists():
        return {}
    given, key = models.read_json(ranks_file)["ranks_by_letter"], models.read_json(key_file)
    found = {}
    for story, letters in given.items():
        for letter, rank in letters.items():
            if rank is not None:
                found.setdefault(key[story][letter], {})[story] = rank
    return found


# ---- Quotes

STATUTES = "\n".join(path.read_text() for path in sorted((models.V2 / "statutes").glob("*.txt")))


def quotes_found(answer, lease):
    """How many quotations (20 characters or more) the answer has, and how many are word for word in the statutes or
    the lease, wherever the cite is: the skills test's count. The page's own check (saved in "checks") looks for the
    cite after the quote only, so it misses a right quote whose cite comes first ("Under 83.49(3)(a), ...")."""
    import checks                                             # the app's quote matching, loaded by models.setup
    quotes = checks.QUOTE.findall(answer)
    sources = STATUTES + "\n" + lease
    return len(quotes), sum(checks.found_in(checks.quote_parts(q), sources) for q in quotes)


# ---- The judge

def ask_judge(gateway, prompt):
    """The judge's reading of one prompt, as a dict. None if three tries give nothing readable."""
    for _ in range(3):
        try:
            content = gateway.chat.completions.create(model=JUDGE, temperature=0, messages=[
                {"role": "user", "content": prompt}]).choices[0].message.content or ""
        except Exception as problem:                          # one failed call must not lose the others' grades
            models.say(f"judge call failed: {type(problem).__name__}")
            continue
        try:
            return json.loads(content[content.find("{"):content.rfind("}") + 1])
        except json.JSONDecodeError:
            continue
    return None


def judge_all(gateway, cache_path, items, make_prompt):
    """The judge's reading of each (key, answer line). Readings are kept in cache_path, so a rerun judges only the
    new answers. A failed answer is not kept, and not judged: it is graded wrong. Returns {key: reading}."""
    grades = models.read_json(cache_path) if cache_path.exists() else {}
    todo = [(key, line) for key, line in items if key not in grades and not line.get("error")]
    with ThreadPoolExecutor(4) as pool:
        for (key, _), grade in zip(todo, pool.map(lambda item: ask_judge(gateway, make_prompt(item[1])), todo)):
            if grade is not None:
                grades[key] = grade
    cache_path.write_text(json.dumps(grades, indent=1))
    return grades


# ---- Test 1: the stories

def question_count(answer):
    """How many sentences of the answer end in a question mark, not counting words inside quotation marks."""
    for quote in quotations(answer):
        answer = answer.replace(quote, "")
    sentences = re.split(r"(?<=[.!?])\s+|\n+", answer)
    return sum(s.strip().rstrip("*_)\"”'").endswith("?") for s in sentences)


def story_row(line, story, number, grade, reviewed, lease, lease_dates):
    """Everything counted about one story answer."""
    year = int(story["today"][:4])                            # a date written without a year is in the story's year
    allowed = dates_in(json.dumps(story["facts"]), year) | dates_in(lease, year) | dates_in(story["message"], year)
    allowed |= set(lease_dates)
    for call in line["tool_calls"]:
        if call["name"] == "count_days":
            allowed |= set(re.findall(r"20\d\d-\d\d-\d\d", call["result"]))
    judge_says = "wrong" if line.get("error") else story_verdict(story, grade or {"other_error": "not judged"})
    checked = line["checks"]["quotes"]
    quotes, quotes_ok = quotes_found(line["answer"], lease)
    return {"story": line["story"], "run": line["run"], "number": number, "judge_verdict": judge_says,
            "verdict": reviewed.get("verdict", judge_says), "why_reviewed": reviewed.get("why", ""),
            "answers_first": bool((grade or {}).get("answers_first")), "quotes": quotes,
            "quotes_ok": quotes_ok, "quotes_ok_page": sum(q["ok"] for q in checked), "made_up_dates": sorted(dates_in(line["answer"], year) - allowed),
            "questions_asked": question_count(line["answer"]),
            "skill_loaded": "deposit_not_returned" in line["skills_loaded"],
            "count_days_used": any(c["name"] == "count_days" for c in line["tool_calls"]),
            "words": len(line["answer"].split()), "seconds": line["seconds"], "cost": line["cost"],
            "estimated": any(r["estimated"] for r in line["requests"]), "error": bool(line.get("error")),
            "judge_reason": (grade or {}).get("reason", ""), "answer": line["answer"]}


def story_summary(rows):
    """One model's totals on the stories."""
    return {"answers": len(rows), "main": counts([r for r in rows if r["number"] in MAIN_STORIES]),
            "open": counts([r for r in rows if r["number"] in OPEN_STORIES]),
            "answers_first": sum(r["answers_first"] for r in rows), "quotes": sum(r["quotes"] for r in rows),
            "quotes_ok": sum(r["quotes_ok"] for r in rows), "quotes_ok_page": sum(r["quotes_ok_page"] for r in rows),
            "made_up_dates": sum(bool(r["made_up_dates"]) for r in rows),
            "asks_more_than_one": sum(r["questions_asked"] >= 2 for r in rows),
            "skill_loaded": sum(r["skill_loaded"] for r in rows), "count_days_used": sum(r["count_days_used"] for r in rows),
            "words_median": middle([r["words"] for r in rows]), "seconds_median": middle([r["seconds"] for r in rows]),
            "cost_mean": average([r["cost"] for r in rows]), "cost_estimated": any(r["estimated"] for r in rows),
            "errors": sum(r["error"] for r in rows),
            "answers_list": [{"story": r["story"], "run": r["run"], "verdict": r["verdict"],
                              "judge_verdict": r["judge_verdict"]} for r in rows]}


def score_stories(gateway, own, folder):
    """Test 1 for one lease set. Returns ({model: summary}, {model: rows})."""
    data = models.stories(own)
    stories = {s["id"]: s for s in data["stories"]}
    numbers = {s["id"]: n for n, s in enumerate(data["stories"], start=1)}
    lease = models.lease_text(models.story_pages(own))
    statute = "\n\n".join((models.V2 / "statutes" / f"{s}.txt").read_text() for s in ("83.49", "83.505"))
    changes = reviews(own)
    summaries, all_rows = {}, {}
    for model in models.CHAT_MODELS:
        path = folder / f"stories_{model}.jsonl"
        # Threads finish in any order, so put the answers back in the stories' order.
        lines = sorted(models.read_lines(path), key=lambda l: (numbers[l["story"]], l["run"]))
        if not lines:
            continue

        def prompt(line):
            """The judge's prompt for one answer."""
            story = stories[line["story"]]
            return STORY_PROMPT.format(statute=statute, lease=lease, today=story["today"],
                                       facts=json.dumps(story["facts"], indent=1), message=story["message"],
                                       answer=story["answer"], points=json.dumps(story["points"]),
                                       mistakes=json.dumps(story["mistakes"]), reply=line["answer"] or "(no answer)")

        grades = judge_all(gateway, folder / f"judge_{path.stem}.json",
                           [(f"{l['story']}/{l['run']}", l) for l in lines], prompt)
        rows = []
        for line in lines:
            key = f"{line['story']}/{line['run']}"
            rows.append(story_row(line, stories[line["story"]], numbers[line["story"]], grades.get(key),
                                  changes.get(model, {}).get(key, {}), lease, data.get("lease_dates", [])))
        summaries[model], all_rows[model] = story_summary(rows), rows
        models.say(f"stories {model}: {summaries[model]['main']} (stories 1, 3, 4)")
    return summaries, all_rows


# ---- Test 2: the lease questions

def question_row(line, question, grade, lease, reviewed):
    """Everything counted about one question answer. lease is the text the model read; reviewed is my change, if any."""
    checked = line["checks"]["quotes"]
    quotes, quotes_ok = quotes_found(line["answer"], lease)
    judge_says = "wrong" if line.get("error") else question_verdict(question, grade or {"other_error": "not judged"})
    return {"id": line["id"], "lease": line["lease"], "covered": question["covered"], "judge_verdict": judge_says,
            "verdict": reviewed.get("verdict", judge_says), "why_reviewed": reviewed.get("why", ""),
            "silent": bool((grade or {}).get("says_lease_silent")),
            "no_answer": bool(line.get("error")) or "<function=" in line["answer"] or not line["answer"].strip(),
            "quotes": quotes, "quotes_ok": quotes_ok, "quotes_ok_page": sum(q["ok"] for q in checked),
            "seconds": line["seconds"],
            "cost": line["cost"], "estimated": any(r["estimated"] for r in line["requests"]),
            "error": bool(line.get("error")), "judge_reason": (grade or {}).get("reason", ""), "answer": line["answer"]}


def question_summary(rows):
    """One row of the questions table."""
    covered = [r for r in rows if r["covered"]]
    return {"answers": len(rows), "verdicts": counts(rows), "covered": len(covered),
            "wrongly_silent": sum(r["silent"] and r["verdict"] != "right" for r in covered),
            "not_covered": len(rows) - len(covered),
            "made_up": sum(not r["silent"] and not r["no_answer"] and r["verdict"] != "right"
                           for r in rows if not r["covered"]),
            "quotes": sum(r["quotes"] for r in rows), "quotes_ok": sum(r["quotes_ok"] for r in rows),
            "quotes_ok_page": sum(r["quotes_ok_page"] for r in rows), "seconds_median": middle([r["seconds"] for r in rows]), "cost_mean": average([r["cost"] for r in rows]),
            "cost_estimated": any(r["estimated"] for r in rows), "errors": sum(r["error"] for r in rows),
            "answers_list": [{"id": r["id"], "verdict": r["verdict"]} for r in rows]}


def score_questions(gateway, own, folder):
    """Test 2 for one lease set; each file (a model, and which lease texts it read) is a row of its own.
    Returns ({row name: summary}, {row name: rows})."""
    key = {q["id"]: q for q in models.questions(own)}
    own_text = models.lease_text(models.read_json(models.PRIVATE / "text_own_best.json")["pages"]) if own else None
    truth = {}                                                # each sample lease's written text, made once

    def whole_lease(question):
        """The lease as written, for the judge."""
        if own:
            return own_text
        truth.setdefault(question["lease"], plain_text(question["lease"]))
        return truth[question["lease"]]

    def prompt(line):
        """The judge's prompt for one answer."""
        q = key[line["id"]]
        passages = json.dumps(q["passages"]) if q["passages"] else \
            "none; the lease does not address this question" + (f" ({q['note']})" if q.get("note") else "")
        return QUESTION_PROMPT.format(lease=whole_lease(q), question=q["question"], answer=q["answer"],
                                      passages=passages, points=json.dumps(q["points"]),
                                      mistakes=json.dumps(q["mistakes"]), reply=line["answer"] or "(no answer)")

    order = list(models.CHAT_MODELS)
    paths = sorted(folder.glob("questions_*.jsonl"), key=lambda p: (order.index(p.stem.split("_")[1]), p.stem))
    summaries, all_rows = {}, {}
    position = {q["id"]: n for n, q in enumerate(key.values())}
    for path in paths:
        lines = sorted(models.read_lines(path), key=lambda l: position[l["id"]])   # threads finish in any order
        if not lines:
            continue
        name = lines[0]["model"] + ("" if lines[0]["texts"] == "best" else f" / {lines[0]['texts']} texts")
        grades = judge_all(gateway, folder / f"judge_{path.stem}.json", [(l["id"], l) for l in lines], prompt)
        read = {}                                             # each lease's text as this file's model read it

        def lease_read(line):
            """The lease text the model had for this answer."""
            texts = None if line["texts"] == "best" else line["texts"]
            if line["lease"] not in read:
                pages_path = models.pages_file(own, line["lease"], texts, False)
                read[line["lease"]] = models.lease_text(models.read_json(pages_path)["pages"])
            return read[line["lease"]]

        changes = reviews(own).get("questions", {}).get(path.stem, {})
        rows = [question_row(line, key[line["id"]], grades.get(line["id"]), lease_read(line), changes.get(line["id"], {}))
                for line in lines]
        summaries[name], all_rows[name] = question_summary(rows), rows
        models.say(f"questions {name}: {summaries[name]['verdicts']}")
    return summaries, all_rows


# ---- Test 3: reading pages from images

BOX = re.compile(r"\[[Xx]\]|\[ \]|[☒☑■☐❑□]")
CHECKED = {"[X]", "[x]", "☒", "☑", "■"}                      # the other marks (and "[ ]") count as empty
LOOK_AHEAD = 6                                                # read boxes a source box may skip over to find its match


def boxes_in(text):
    """Each check box in a text, in order, as (checked, label). The label is the first four words after the box, on
    its line."""
    found = list(BOX.finditer(text))
    boxes = []
    for i, box in enumerate(found):
        end = found[i + 1].start() if i + 1 < len(found) else len(text)
        line = text[box.end():end].strip().split("\n")[0]
        label = " ".join(re.findall(r"[a-z0-9]+", " ".join(line.split()[:4]).lower()))
        boxes.append((box.group(0) in CHECKED, label))
    return boxes


def match_boxes(source, read):
    """For each source box, the index of the read box it matches, or None. Going in order, a source box looks at the
    next few unused read boxes and takes the one whose label is most like its own (at least 0.6 alike)."""
    matches, start = [], 0
    for _, label in source:
        found, best = None, 0.6
        for j in range(start, min(start + LOOK_AHEAD, len(read))):
            score = difflib.SequenceMatcher(None, label, read[j][1]).ratio()
            if score >= best and (found is None or score > best):   # the first read box wins a tie
                found, best = j, score
        if found is not None:
            start = found + 1
        matches.append(found)
    return matches


def boxes_right(source, read):
    """How many source boxes have the same mark in the read text, and a list of the ones that do not."""
    matches, misses = match_boxes(source, read), []
    for (checked, label), found in zip(source, matches):
        if found is None or read[found][0] != checked:
            misses.append(f"{label!r}: written {'checked' if checked else 'empty'}, read "
                          + ("not found" if found is None else "checked" if read[found][0] else "empty"))
    return len(source) - len(misses), misses


def differences_between_runs(runs):
    """(pages whose text differs between runs, boxes whose mark differs between runs) for one lease. runs is
    {run: {page: text}}."""
    if len(runs) < 2:
        return 0, 0
    pages = sorted({page for text in runs.values() for page in text})
    pages_differ = sum(len({" ".join(runs[r].get(p, "").split()) for r in runs}) > 1 for p in pages)
    boxes_differ = 0
    for page in pages:
        marks = [[checked for checked, _ in boxes_in(runs[r].get(page, ""))] for r in runs]
        for i in range(max(len(m) for m in marks)):
            boxes_differ += len({m[i] if i < len(m) else None for m in marks}) > 1
    return pages_differ, boxes_differ


def score_sample_reader(lines, source_boxes, written):
    """One reader's numbers on the two sample leases, per lease and per run."""
    result = {"reads": len(lines), "errors": sum(bool(l.get("error")) for l in lines), "box_total": len(source_boxes),
              "leases": {}, "runs": {}, "misses": {}}
    run_numbers = sorted({l["run"] for l in lines})
    for lease in SAMPLE_READ_LEASES:
        mine = [l for l in lines if l["lease"] == lease]
        runs = {r: {l["page"]: l["text"] for l in mine if l["run"] == r} for r in run_numbers}
        texts = {r: "\n".join(runs[r][p] for p in sorted(runs[r])) for r in run_numbers}
        accuracy = {r: word_accuracy(texts[r], written[lease]) for r in run_numbers if runs[r]}
        right = {}
        if lease == "broken_text":
            for r in run_numbers:
                right[r], result["misses"][r] = boxes_right(source_boxes, boxes_in(texts[r]))
        pages_differ, boxes_differ = differences_between_runs({r: p for r, p in runs.items() if p})
        result["leases"][lease] = {
            "reads": len(mine), "accuracy": accuracy, "accuracy_mean": average(list(accuracy.values())),
            "boxes_right": right, "boxes_right_mean": average(list(right.values())),
            "pages_differ": pages_differ, "boxes_differ": boxes_differ,
            "seconds_median": middle([l["seconds"] for l in mine]), "cost_mean": average([l["cost"] for l in mine])}
    for r in run_numbers:
        mine = [l for l in lines if l["run"] == r]
        result["runs"][r] = {"accuracy": {lease: result["leases"][lease]["accuracy"].get(r) for lease in SAMPLE_READ_LEASES},
                             "boxes_right": result["leases"]["broken_text"]["boxes_right"].get(r),
                             "seconds_median": middle([l["seconds"] for l in mine]),
                             "cost_mean": average([l["cost"] for l in mine])}
    result["all"] = {"accuracy_mean": average([result["leases"][l]["accuracy_mean"] for l in SAMPLE_READ_LEASES
                                               if result["leases"][l]["accuracy_mean"] is not None]),
                     "boxes_right_mean": result["leases"]["broken_text"]["boxes_right_mean"],
                     "pages_differ": sum(result["leases"][l]["pages_differ"] for l in SAMPLE_READ_LEASES),
                     "boxes_differ": sum(result["leases"][l]["boxes_differ"] for l in SAMPLE_READ_LEASES),
                     "seconds_median": middle([l["seconds"] for l in lines]),
                     "cost_mean": average([l["cost"] for l in lines])}
    return result


def score_sample_readers(folder, show_boxes):
    """Test 3 on the sample leases: {reader: numbers}."""
    source_boxes = boxes_in((models.LEASE_TEST / "sources" / "broken_text.txt").read_text())
    written = {lease: plain_text(lease) for lease in SAMPLE_READ_LEASES}
    results = {}
    for reader in models.READERS:
        lines = models.read_lines(folder / f"reads_{reader}.jsonl")
        if lines:
            results[reader] = score_sample_reader(lines, source_boxes, written)
            models.say(f"readers {reader}: word accuracy {ratio(results[reader]['all']['accuracy_mean'])}, "
                       f"boxes right {results[reader]['all']['boxes_right_mean']} of {len(source_boxes)}")
            if show_boxes:
                for run, misses in results[reader]["misses"].items():
                    print(f"  {reader} run {run}: boxes wrong on broken_text:", *misses, sep="\n    ")
    return results


# The own lease: fields the author listed, found in each reader's text

MARK = r"(\[x\]|\[ \]|[☒☑■☐❑□])"                              # a box mark, in text that normal() has lowercased
MARK_BEFORE = re.compile(MARK + r"(?:\s*\d+\.?)?\s*$")        # a mark, then maybe a number like "1.", then spaces


def normal(text):
    """For matching: lowercase, straight quotes, no "$" "," "_" or "*" (readers draw blanks as underscores and may
    mark bold words with **), one space."""
    text = text.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", re.sub(r"[$,_*]", "", text)).strip()


def text_field_right(field, pages):
    """Whether a text field's value is in its page's text, or the page before or after (a reader may shift text)."""
    near = " ".join(normal(pages.get(p, "")) for p in (field["page"] - 1, field["page"], field["page"] + 1))
    return normal(str(field["value"])) in near


def box_field_state(field, pages):
    """"right", "wrong", or "missing" for a box field. Of the places its label appears on the page, the first with
    a box mark at most 6 characters before it decides; "missing" if none has a mark."""
    text, label = normal(pages.get(field["page"], "")), normal(field["label"])
    for found in re.finditer(re.escape(label), text) if label else []:
        before = text[max(0, found.start() - 9):found.start()]
        mark = MARK_BEFORE.search(before)
        if mark and len(before) - mark.end(1) <= 6:
            return "right" if (mark.group(1) in CHECKED) == field["checked"] else "wrong"
    return "missing"


def score_own_fields(fields, pages):
    """A reader's pages ({page: text}) scored on the author's fields: counts, and (apart) the ids that failed."""
    text_fields = [f for f in fields if f["kind"] == "text"]
    box_fields = [f for f in fields if f["kind"] == "box"]
    text_failed = [f["id"] for f in text_fields if not text_field_right(f, pages)]
    states = {f["id"]: box_field_state(f, pages) for f in box_fields}
    counts_of = {"text_total": len(text_fields), "text_right": len(text_fields) - len(text_failed),
                 "box_total": len(box_fields), "box_right": sum(s == "right" for s in states.values()),
                 "box_missing": sum(s == "missing" for s in states.values())}
    failed = {"failed": text_failed + [i for i, s in states.items() if s != "right"],
              "failed_missing": [i for i, s in states.items() if s == "missing"]}
    return counts_of, failed


def printed_words(text):
    """A page's text with the symbol characters (check marks, boxes, and the like) taken out."""
    return re.sub("[☀-➿]", "", text)


def score_own_readers(app, folder):
    """Test 3 on the own lease, for the PyMuPDF text layer alone, the app's reading, and each model. Returns
    ({reader: numbers}, {reader: ids of the fields it got wrong})."""
    fields_path, pdf = models.PRIVATE / "own_fields.json", models.PRIVATE / "own_lease.pdf"
    if models.missing([fields_path, pdf]):
        print("own readers: private/own_fields.json or own_lease.pdf is missing, so not scored")
        return {}, {}
    fields = models.read_json(fields_path)["fields"]
    layer = {n: page.get_text() for n, page in enumerate(pymupdf.open(pdf), start=1)}
    clean = {n: printed_words(text) for n, text in layer.items()}
    printed = [n for n, text in clean.items() if models.usable(text)]
    sources = {"text layer (PyMuPDF)": layer}
    for name in ["app"] + list(models.READERS):
        path = folder / f"text_own_{name}.json"
        if path.exists():
            sources[name] = {p["page"]: p["text"] for p in models.read_json(path)["pages"]}
    results, failures = {}, {}
    for name, pages in sources.items():
        reads = models.read_lines(folder / f"reads_{name}.jsonl")
        recall = None if name == "text layer (PyMuPDF)" else \
            average([word_accuracy(pages.get(n, ""), clean[n]) for n in printed])
        found, failures[name] = score_own_fields(fields, pages)
        results[name] = {**found, "recall": recall, "printed_pages": len(printed), "pages": len(pages),
                         "seconds_median": middle([r["seconds"] for r in reads]),
                         "cost_mean": average([r["cost"] for r in reads])}
        models.say(f"own readers {name}: text {found['text_right']} of {found['text_total']}, "
                   f"boxes {found['box_right']} of {found['box_total']}")
    return results, failures


# ---- SCORES.md

def stories_markdown(summaries, ranks):
    """The two tables for test 1."""
    first, second = [], []
    for model, s in summaries.items():
        mine = ranks.get(model, {})
        main, open_ones = s["main"], s["open"]
        first.append([model, f"{statistics.mean(mine.values()):.1f}" if mine else "-",
                      f"{sum(r == 1 for r in mine.values())} of {len(mine)}" if mine else "-",
                      f"{main['right']} / {main['partly']} / {main['wrong']}",
                      f"{open_ones['right']} / {open_ones['partly']} / {open_ones['wrong']}"])
        n = s["answers"]
        second.append([model, f"{s['answers_first']} of {n}", f"{s['quotes_ok']} of {s['quotes']} ({s['quotes_ok_page']})",
                       f"{s['made_up_dates']} of {n}", f"{s['asks_more_than_one']} of {n}", f"{s['skill_loaded']} of {n}",
                       f"{s['count_days_used']} of {n}", s["words_median"], seconds_text(s["seconds_median"]),
                       money(s["cost_mean"], s["cost_estimated"]), s["errors"]])
    return (table(["Model", "Your average rank (1 is best)", "Your firsts", "Stories 1, 3, 4: right / partly / wrong",
                   "Stories 2, 5 (your open calls): right / partly / wrong"], first) + [""] +
            table(["Model", "Answers first", "Quotes word for word (the page's check)", "Answers with a made-up date",
                   "Asks more than one question", "Skill loaded", "count_days used", "Median words", "Median time",
                   "Mean cost per answer", "Errors"], second))


def questions_markdown(summaries):
    """The table for test 2."""
    rows = []
    for name, s in summaries.items():
        v = s["verdicts"]
        rows.append([name, s["answers"], v["right"], v["partly"], v["wrong"], f"{s['wrongly_silent']} of {s['covered']}",
                     f"{s['made_up']} of {s['not_covered']}", f"{s['quotes_ok']} of {s['quotes']} ({s['quotes_ok_page']})",
                     seconds_text(s["seconds_median"]), money(s["cost_mean"], s["cost_estimated"]), s["errors"]])
    return table(["Row", "Answers", "Right", "Partly", "Wrong", "Wrongly silent (covered, said not covered)",
                  "Made up (not covered, answered anyway)", "Quotes word for word (the page's check)", "Median time", "Mean cost per answer",
                  "Errors"], rows)


def sample_readers_markdown(results):
    """The tables for test 3 on the sample leases: by lease, and by run."""
    by_lease, by_run = [], []
    for reader, r in results.items():
        total = r["box_total"]
        for lease in SAMPLE_READ_LEASES:
            x = r["leases"][lease]
            by_lease.append([reader, lease, ratio(x["accuracy_mean"]),
                             "-" if lease != "broken_text" else f"{x['boxes_right_mean']:.1f} of {total}",
                             x["pages_differ"], x["boxes_differ"], seconds_text(x["seconds_median"]), money(x["cost_mean"])])
        a = r["all"]
        by_lease.append([reader, "all", ratio(a["accuracy_mean"]),
                         "-" if a["boxes_right_mean"] is None else f"{a['boxes_right_mean']:.1f} of {total}",
                         a["pages_differ"], a["boxes_differ"], seconds_text(a["seconds_median"]), money(a["cost_mean"])])
        for run, x in r["runs"].items():
            by_run.append([reader, run, ratio(x["accuracy"]["scanned"]), ratio(x["accuracy"]["broken_text"]),
                           "-" if x["boxes_right"] is None else f"{x['boxes_right']} of {total}",
                           seconds_text(x["seconds_median"]), money(x["cost_mean"])])
    return (table(["Reader", "Lease", "Word accuracy (mean of runs)", "Check boxes right (mean of runs)",
                   "Pages that differ between runs", "Boxes that differ between runs", "Median time per page",
                   "Mean cost per page"], by_lease) + [""] +
            table(["Reader", "Run", "Word accuracy, scanned", "Word accuracy, broken_text", "Check boxes right, broken_text",
                   "Median time per page", "Mean cost per page"], by_run))


def own_readers_markdown(results):
    """The table for test 3 on the own lease."""
    rows = []
    for name, r in results.items():
        rows.append([name, f"{r['text_right']} of {r['text_total']}", f"{r['box_right']} of {r['box_total']}",
                     r["box_missing"], f"{r['text_right'] + r['box_right']} of {r['text_total'] + r['box_total']}",
                     ratio(r["recall"]), r["pages"], seconds_text(r["seconds_median"]), money(r["cost_mean"])])
    printed_pages = next(iter(results.values()))["printed_pages"]
    return table(["Reader", "Text fields right", "Box fields right", "Box fields with no mark found", "All fields right",
                  f"Word recall of the printed text ({printed_pages} pages)", "Pages", "Median time per page",
                  "Mean cost per page"], rows)


def set_markdown(title, own, summaries, ranks):
    """One lease set's part of SCORES.md."""
    lines = [f"## {title}", ""]
    if not any(summaries.values()):
        return lines + ["No results yet.", ""]
    if summaries["stories"]:
        lines += ["### Test 1: the deposit stories (3 runs each)", ""] + stories_markdown(summaries["stories"], ranks) + [""]
        changed = [(m, k, c) for m, per_model in reviews(own).items() if m != "questions" for k, c in per_model.items()]
        if changed and not own:                               # reasons about the own lease may quote it: kept private
            lines += ["My changes to the judge's grades:", ""]
            lines += [f"- {m}, {k}: {c['verdict']}. {c['why']}" for m, k, c in changed] + [""]
    if summaries["questions"]:
        lines += ["### Test 2: questions about the lease", ""] + questions_markdown(summaries["questions"]) + [""]
        changed = [(f, k, c) for f, per_file in reviews(own).get("questions", {}).items() for k, c in per_file.items()]
        if changed and not own:
            lines += ["My changes to the judge's grades:", ""]
            lines += [f"- {f.removeprefix('questions_')}, {k}: {c['verdict']}. {c['why']}" for f, k, c in changed] + [""]
    if summaries["readers"]:
        lines += ["### Test 3: reading pages from images", ""]
        lines += (own_readers_markdown if own else sample_readers_markdown)(summaries["readers"]) + [""]
    return lines


def markdown(sets):
    """SCORES.md: numbers only, so it is safe to commit."""
    lines = ["# Model comparison: scores", "",
             "Right, partly, wrong: the judge's grades (gpt-oss-120b on UF), after my changes listed under each table. "
             "Quotes word for word: quotations of 20 characters or more found word for word in statutes/ or the lease the model read, wherever the cite is; in brackets, how many the page's own check passes (it looks for the cite only after the quote). A made-up date is one the model wrote that "
             "is not in the facts, the lease, the tenant's message, or a count_days result. Costs: OpenRouter's own "
             "figure; with a ~ they are worked out from token counts and list prices (UF models are always worked out, "
             "and are the UF budget, not money).", ""]
    for title, own, summaries, ranks in sets:
        lines += set_markdown(title, own, summaries, ranks)
    return "\n".join(lines) + "\n"


# ---- The detail file for the own lease (private)

def detail_markdown(story_rows, question_rows, failures):
    """Each answer on the own lease with its grade, and the fields each reader got wrong. Stays in private/."""
    lines = ["# Own lease: detail (private, not for git)", ""]
    for model, rows in story_rows.items():
        lines += [f"## Stories, {model}", ""]
        for r in rows:
            lines += [f"### {r['story']} run {r['run']}: {r['verdict']} (judge: {r['judge_verdict']})", "",
                      f"Judge: {r['judge_reason']}", "",
                      f"Quotes ok {r['quotes_ok']} of {r['quotes']}; "
                      f"dates made up: {', '.join(r['made_up_dates']) or 'none'}; "
                      f"questions asked: {r['questions_asked']}; {r['seconds']} s", "", r["answer"], ""]
    for name, rows in question_rows.items():
        lines += [f"## Questions, {name}", ""]
        for r in rows:
            lines += [f"### {r['id']}: {r['verdict']} (judge: {r['judge_verdict']})", "", f"Judge: {r['judge_reason']}", "",
                      f"Quotes ok {r['quotes_ok']} of {r['quotes']}; said the lease is silent: {r['silent']}", "",
                      r["answer"], ""]
    if failures:
        lines += ["## Readers: fields not right", ""]
        for name, f in failures.items():
            lines.append(f"- {name}: {', '.join(f['failed']) or 'none'}"
                         + (f" (no mark found: {', '.join(f['failed_missing'])})" if f["failed_missing"] else ""))
    return "\n".join(lines) + "\n"


# ---- Putting it together

def parse_args():
    """The command line."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry", action="store_true", help="score the made-up --dry results, with a fake judge")
    parser.add_argument("--show-boxes", action="store_true", help="print each reader's wrong check boxes on broken_text")
    return parser.parse_args()


def have_private(*names):
    """Whether all of these files exist in private/."""
    return not models.missing([models.PRIVATE / name for name in names])


def score_set(app, gateway, own, args):
    """Everything that can be scored for one lease set. The own lease is scored only for the tests whose private
    files exist. Returns the summaries, the author's ranks, the answer rows, and (own) the readers' failed fields."""
    folder = models.results_folder(own, args.dry)
    summaries, rows, failures = {"stories": {}, "questions": {}, "readers": {}}, {"stories": {}, "questions": {}}, {}
    if not own or have_private("own_stories.json", "text_own_best.json"):
        summaries["stories"], rows["stories"] = score_stories(gateway, own, folder)
    if not own or have_private("own_questions.json", "text_own_best.json"):
        summaries["questions"], rows["questions"] = score_questions(gateway, own, folder)
    if own:
        summaries["readers"], failures = score_own_readers(app, folder)
    else:
        summaries["readers"] = score_sample_readers(folder, args.show_boxes)
    ranks = author_ranks(models.blind_folder(own, args.dry))
    for model, summary in summaries["stories"].items():
        mine = ranks.get(model, {})
        summary["author_average_rank"] = round(statistics.mean(mine.values()), 2) if mine else None
        summary["author_firsts"] = sum(r == 1 for r in mine.values())
    return summaries, ranks, rows, failures


def numbers_only(summaries):
    """The summaries without each answer's grade, so what goes in scores.json says nothing about the own lease's words."""
    kept = {"readers": summaries["readers"]}
    for test in ("stories", "questions"):
        kept[test] = {name: {k: v for k, v in s.items() if k != "answers_list"} for name, s in summaries[test].items()}
    return kept


def main():
    """Judge and count everything there is, and write the score files."""
    args = parse_args()
    app = models.setup("uf", dry=args.dry)                    # the judge runs on UF, through the app's own client
    gateway = app.config.client()
    sample, sample_ranks, _, _ = score_set(app, gateway, False, args)
    own, own_ranks, own_rows, own_failures = score_set(app, gateway, True, args)
    out, private_out = models.scores_folder(False, args.dry), models.scores_folder(True, args.dry)
    (out / "scores.json").write_text(json.dumps({"sample": sample, "own": numbers_only(own)}, indent=1))
    (out / "SCORES.md").write_text(markdown([("Sample leases", False, sample, sample_ranks),
                                             ("The author's own lease", True, own, own_ranks)]))
    print(f"wrote {out / 'scores.json'} and SCORES.md")
    if any(own.values()):
        detail = detail_markdown(own_rows["stories"], own_rows["questions"], own_failures)
        (private_out / "SCORES_own_detail.md").write_text(detail)
        print(f"wrote {private_out / 'SCORES_own_detail.md'}")


if __name__ == "__main__":
    main()
