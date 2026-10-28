"""The intake speed test: how long a lease takes to read before the first answer, and whether a faster way still
reads every word and check box. Ways tried: the app's (one page at a time), several pages at once, smaller page
pictures, and v1's way as a baseline. Run from this folder: python speed.py   (--dry: a fake reader; --score: score
only). Writes results/runs.jsonl (every reading, added to as it goes), scores.json, and SCORES.md.
"""
import argparse
import json
import logging
import os
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "models"))
import models  # noqa: E402  (the model test's helpers: the app set up for one model, the fake reader, the log)
import score  # noqa: E402  (the model test's word and check-box scorers)

# The 46-page lease is the one timed; the 3-page one has 35 check boxes with a key; the 4-page one is a scan.
LEASES = ("long_numbered", "broken_text", "scanned")
# Each way: (pages sent at once, picture sharpness in dots per inch). The app today is one page at a time at 200.
METHODS = {"now: 1 at a time": (1, 200), "4 at once": (4, 200), "8 at once": (8, 200), "16 at once": (16, 200),
           "8 at once, 150 dpi": (8, 150), "8 at once, 100 dpi": (8, 100), "v1": None}
# A Python with v1's packages (v1_intake.py runs in it). Not set: v1 is left out.
V1_PYTHON = os.environ.get("V1_PYTHON")
# Seconds between two live readings, so one reading's burst of requests does not slow the next.
PAUSE = 10


class Sharpness:
    """A page that draws its picture at another sharpness, so the app's own lease.read_image is used unchanged."""

    def __init__(self, page, dpi):
        """Keep the page and the sharpness to draw it at."""
        self.page, self.dpi = page, dpi

    def get_pixmap(self, dpi):
        """The page's picture at this test's sharpness (read_image asks for 200)."""
        return self.page.get_pixmap(dpi=self.dpi)


class RetryCounter(logging.Handler):
    """Counts the OpenAI library's "Retrying request" notes: a page turned away (often too many at once), sent again."""

    def __init__(self):
        """Start at zero."""
        super().__init__()
        self.count = 0

    def emit(self, record):
        """Count one note if it is a retry. logging holds this handler's lock here, so threads do not collide."""
        self.count += "Retrying" in record.getMessage()


def read_page(app, client, pdf, number, dpi):
    """One page read from its picture by the app's own read_image. Returns its line: text, seconds, tokens, error."""
    page = pymupdf.open(pdf)[number - 1]                      # opened here, so each thread has its own document
    models.start_log()
    start = time.perf_counter()
    try:
        text, error = app.lease.read_image(client, Sharpness(page, dpi)), ""
    except Exception as problem:                              # keep a failed page, so one bad call does not end the run
        text, error = "", f"{type(problem).__name__}: {problem}"[:300]
    seconds = time.perf_counter() - start
    requests, _ = models.take_log()
    return {"page": number, "text": text, "error": error, "seconds": round(seconds, 2),
            "in_tokens": sum(r["prompt_tokens"] for r in requests), "out_tokens": sum(r["completion_tokens"] for r in requests)}


def read_v2(app, pdf, at_once, dpi):
    """Read every page of one lease, `at_once` pages at a time, as the app would. Returns (seconds, pages)."""
    start = time.perf_counter()
    client = app.config.client(app.config.READER_GATEWAY)
    count = pymupdf.open(pdf).page_count
    with ThreadPoolExecutor(at_once) as pool:                 # map keeps the pages in order, whenever each finishes
        pages = list(pool.map(lambda number: read_page(app, client, pdf, number, dpi), range(1, count + 1)))
    return time.perf_counter() - start, pages


def read_v1(pdf):
    """v1's intake on one lease, in its own Python (v1_intake.py). Returns (seconds, pages, error)."""
    with tempfile.TemporaryDirectory() as folder:
        out = Path(folder) / "v1.json"
        subprocess.run([V1_PYTHON, str(HERE / "v1_intake.py"), str(pdf), str(out)], check=True)
        result = json.loads(out.read_text())
    pages = [{**p, "error": "", "seconds": None, "in_tokens": None, "out_tokens": None} for p in result["pages"]]
    return result["seconds"], pages, result["error"]


def run_all(app, runs, path, dry):
    """Every way on every lease, `runs` times, one reading at a time. Readings already in the file are skipped."""
    counter = RetryCounter()
    openai_log = logging.getLogger("openai")
    openai_log.setLevel(logging.INFO)
    openai_log.addHandler(counter)
    openai_log.propagate = False                              # count the notes; do not print them
    done = {(line["method"], line["lease"], line["run"]) for line in models.read_lines(path)}
    for run in range(1, runs + 1):                            # each run goes through every way, so a slow hour hits all
        for method, setting in METHODS.items():
            if setting is None and (dry or not V1_PYTHON):
                continue
            for lease in LEASES:
                if (method, lease, run) in done:
                    continue
                pdf = models.LEASE_TEST / "leases" / f"{lease}.pdf"
                counter.count, problem = 0, ""
                if setting is None:
                    seconds, pages, problem = read_v1(pdf)
                else:
                    seconds, pages = read_v2(app, pdf, *setting)
                line = {"method": method, "lease": lease, "run": run, "seconds": round(seconds, 1),
                        "retries": counter.count, "problem": problem, "pages": pages}
                models.add_line(path, line)
                failed = sum(bool(p["error"]) for p in pages)
                models.say(f"run {run}, {method}, {lease}: {seconds:.0f} s, {len(pages)} pages, {counter.count} retries"
                           + (f", {failed} FAILED" if failed else "") + (f", v1 problem: {problem}" if problem else ""))
                if not dry and setting is not None:
                    time.sleep(PAUSE)


def middle(values):
    """The median, or None if there is nothing to take it of."""
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def average(values):
    """The mean, or None if there is nothing to take it of."""
    return statistics.mean(values) if values else None


def score_all(lines):
    """Each way's numbers: the wait for the long lease, words and check boxes right, failures, retries, picture size."""
    written = {lease: score.plain_text(lease) for lease in LEASES}
    source_boxes = score.boxes_in((models.LEASE_TEST / "sources" / "broken_text.txt").read_text())
    rows = {}
    for method in METHODS:
        mine = [line for line in lines if line["method"] == method]
        if not mine:
            continue
        text = {id(line): "\n".join(p["text"] for p in line["pages"]) for line in mine}
        waits = sorted(line["seconds"] for line in mine if line["lease"] == "long_numbered")
        pages = [p for line in mine for p in line["pages"]]
        rows[method] = {
            "runs": len({line["run"] for line in mine}),
            "long_lease_waits": waits, "long_lease_wait": middle(waits),
            "page_seconds": middle([p["seconds"] for p in pages]),
            "words_right": {lease: average([score.word_accuracy(text[id(line)], written[lease])
                                            for line in mine if line["lease"] == lease]) for lease in LEASES},
            "boxes_right": average([score.boxes_right(source_boxes, score.boxes_in(text[id(line)]))[0]
                                    for line in mine if line["lease"] == "broken_text"]),
            "box_total": len(source_boxes),
            "failed_pages": sum(bool(p["error"]) for p in pages), "pages": len(pages),
            "retries": sum(line["retries"] for line in mine),
            "in_tokens_per_page": middle([p["in_tokens"] for p in pages]),
            "problems": [line["problem"] for line in mine if line["problem"]]}
    return rows


def percent(value):
    """A share as a percent with one decimal, or a dash."""
    return "-" if value is None else f"{100 * value:.1f}%"


def scores_table(rows):
    """SCORES.md: one row per way."""
    head = ("| Way | Wait for the 46-page lease (middle run) | Each run | Time per page | Words right: 46-page, "
            "3-page, scan | Check boxes right | Pages that failed | Pages sent again | Picture size (tokens per page) |")
    lines = ["# Intake speed test: scores", "", "Numbers only; what they mean is in README.md.", "", head,
             "| " + " | ".join(["---"] * 9) + " |"]
    for method, r in rows.items():
        words = " / ".join(percent(r["words_right"][lease]) for lease in LEASES)
        boxes = "-" if r["boxes_right"] is None else f"{r['boxes_right']:.1f} of {r['box_total']}"
        # v1 runs in another Python, so its retries cannot be counted; with Gemma's step failing, its wait is the
        # text step only.
        v1 = method == "v1" and r["problems"]
        wait = f"{r['long_lease_wait']:.1f} s (text step only)" if v1 else f"{r['long_lease_wait']:.0f} s"
        failed, retries = ("-", "-") if method == "v1" else (f"{r['failed_pages']} of {r['pages']}", r["retries"])
        lines.append(f"| {method} | {wait} | {', '.join(f'{s:.0f}' for s in r['long_lease_waits'])} "
                     f"| {'-' if r['page_seconds'] is None else f'{r['page_seconds']:.1f} s'} | {words} | {boxes} "
                     f"| {failed} | {retries} "
                     f"| {'-' if r['in_tokens_per_page'] is None else f'{r['in_tokens_per_page']:.0f}'} |")
    return "\n".join(lines) + "\n"


def main():
    """Read (unless --score), then score and write the files."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry", action="store_true", help="use a fake reader; nothing is sent anywhere")
    parser.add_argument("--score", action="store_true", help="score what is in the results file; read nothing")
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    folder = HERE / ("results_dry" if args.dry else "results")
    folder.mkdir(exist_ok=True)
    path = folder / "runs.jsonl"
    if not args.score:
        if not V1_PYTHON and not args.dry:
            print("V1_PYTHON is not set, so v1 is left out.")
        app = models.setup("anthropic", dry=args.dry)
        run_all(app, args.runs, path, args.dry)
    rows = score_all(models.read_lines(path))
    (folder / "scores.json").write_text(json.dumps(rows, indent=1))
    (folder if args.dry else HERE).joinpath("SCORES.md").write_text(scores_table(rows))
    print(scores_table(rows))


if __name__ == "__main__":
    main()
