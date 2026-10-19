"""Step 1 of the lease comparison: how well each PDF reader gets the words out of each test lease, and how fast.
Pages a reader cannot read (a scan, or broken text) are read from their images by Gemma 4. Writes readers.json and
texts/<lease>.json, the text every method in step 2 starts from. Run from this folder: python score_readers.py
"""
import base64
import difflib
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

import pymupdf
import pypdf
import PyPDF2
from dotenv import dotenv_values
from openai import OpenAI
from pdfminer.high_level import extract_text as pdfminer_text

from check_key import squash
from make_leases import HERE, LEASES, plain_text

SAMPLE = Path(os.environ.get("SAMPLE_LEASE", HERE.parent.parent / "lease.pdf"))   # v1's lease.pdf, kept out of git
ENV_FILE = Path(os.environ.get("UF_ENV", HERE.parent.parent / ".env"))
VISION_MODEL = "gemma-4-31b-it"
VISION_PROMPT = ("Transcribe this lease page exactly, word for word, in reading order. Write a checked box as [X] and "
                 "an empty box as [ ]. Do not fix, summarize, or leave out anything. Output only the page's text.")
RUNS = 3                                    # each timing is the middle of three runs


def lease_files():
    """Each test lease's name and PDF path, v1's sample included."""
    files = {name: HERE / "leases" / f"{name}.pdf" for name in LEASES}
    files["sample_v1"] = SAMPLE
    return files


def read_pypdf2(path):
    """The text of each page, by PyPDF2 (v1's reader)."""
    return [page.extract_text() or "" for page in PyPDF2.PdfReader(path).pages]


def read_pypdf(path):
    """The text of each page, by pypdf (PyPDF2's successor)."""
    return [page.extract_text() or "" for page in pypdf.PdfReader(path).pages]


def read_pdfminer(path):
    """The text of each page, by pdfminer.six (it puts a form feed between pages)."""
    return pdfminer_text(path).split("\f")[: len(pypdf.PdfReader(path).pages)]


def read_pymupdf(path):
    """The text of each page, by PyMuPDF."""
    return [page.get_text() for page in pymupdf.open(path)]


READERS = {"PyPDF2": read_pypdf2, "pypdf": read_pypdf, "pdfminer": read_pdfminer, "PyMuPDF": read_pymupdf}


def usable(page_text):
    """Whether a page's text is real words: at least 5 words, and most of what was read is words, not symbols."""
    tokens = page_text.split()
    words = [t for t in tokens if re.fullmatch(r"[A-Za-z][A-Za-z'.,;:()\"-]*", t)]
    return len(words) >= 5 and len(words) >= 0.5 * len(tokens)


def words_of(text):
    """The text as lowercase words and numbers, for comparing what was read with what was written."""
    return re.findall(r"[a-z0-9$]+", text.lower())


def word_accuracy(read, written):
    """The share of the written words that come back, in order."""
    want = words_of(written)
    matcher = difflib.SequenceMatcher(None, want, words_of(read), autojunk=False)
    return sum(block.size for block in matcher.get_matching_blocks()) / max(len(want), 1)


def passages_found(read, name, key):
    """How many of the answer key's passages for this lease are in the text word for word, of how many."""
    text = squash(read).lower()
    passages = [p for q in key if q["lease"] == name for p in q["passages"]]
    return sum(squash(p).lower() in text for p in passages), len(passages)


def timed(function, *args):
    """The function's result, and the middle of RUNS timings in seconds."""
    times = []
    for _ in range(RUNS):
        start = time.perf_counter()
        result = function(*args)
        times.append(time.perf_counter() - start)
    return result, statistics.median(times)


def read_image(client, path, page_number):
    """One page's text, read from its image by the vision model."""
    png = pymupdf.open(path)[page_number].get_pixmap(dpi=200).tobytes("png")
    reply = client.chat.completions.create(model=VISION_MODEL, temperature=0, messages=[{"role": "user", "content": [
        {"type": "text", "text": VISION_PROMPT},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}]}])
    return reply.choices[0].message.content or ""


def read_missing_pages(client, path, pages):
    """The pages, with each one that has no usable text replaced by the vision model's reading of its image."""
    return [text if usable(text) else read_image(client, path, i) for i, text in enumerate(pages)]


if __name__ == "__main__":
    client = OpenAI(base_url="https://api.ai.it.ufl.edu/v1", api_key=dotenv_values(ENV_FILE)["UF_API_KEY"])
    key = json.loads((HERE / "answer_key.json").read_text())["questions"]
    report = {}
    for name, path in lease_files().items():
        written = None if name == "sample_v1" else plain_text(name)
        report[name] = {}
        for reader, read in READERS.items():
            pages, seconds = timed(read, path)
            text = "\n".join(pages)
            row = {"seconds": round(seconds, 3), "pages": len(pages), "usable_pages": sum(map(usable, pages)),
                   "passages_found": passages_found(text, name, key)}
            if written:
                row["word_accuracy"] = round(word_accuracy(text, written), 3)
            report[name][reader] = row
            print(name, reader, row, flush=True)
    # The reader for step 2: most passages found word for word, then most words right, then fastest.
    def rank(reader):
        found = sum(report[n][reader]["passages_found"][0] for n in report)
        accuracy = sum(report[n][reader].get("word_accuracy", 0) for n in report)
        speed = sum(report[n][reader]["seconds"] for n in report)
        return (found, accuracy, -speed)
    best = max(READERS, key=rank)
    print("best reader:", best, flush=True)
    (HERE / "texts").mkdir(exist_ok=True)
    for name, path in lease_files().items():
        pages = READERS[best](path)
        start = time.perf_counter()
        filled = read_missing_pages(client, path, pages)
        vision_seconds = [time.perf_counter() - start]
        if filled != pages:                                   # time the image reading twice more, for the middle
            for _ in range(RUNS - 1):
                start = time.perf_counter()
                read_missing_pages(client, path, pages)
                vision_seconds.append(time.perf_counter() - start)
        step1 = report[name][best]["seconds"] + (statistics.median(vision_seconds) if filled != pages else 0)
        text = "\n".join(filled)
        row = {"reader": best, "pages_read_from_images": sum(a != b for a, b in zip(filled, pages)),
               "step1_seconds": round(step1, 2), "passages_found": passages_found(text, name, key)}
        if name != "sample_v1":
            row["word_accuracy"] = round(word_accuracy(text, plain_text(name)), 3)
        report[name]["step1"] = row
        pages_out = [{"page": i + 1, "text": t, "read_by": "Gemma 4 (image)" if t != p else best}
                     for i, (t, p) in enumerate(zip(filled, pages))]
        (HERE / "texts" / f"{name}.json").write_text(json.dumps({"lease": name, "pages": pages_out}, indent=1))
        print(name, "step 1:", row, flush=True)
    (HERE / "readers.json").write_text(json.dumps(report, indent=1))
