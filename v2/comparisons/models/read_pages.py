"""Test 3 of the model comparison: how well a model reads lease pages from their images, through the app's own
lease.read_image. The sample leases are read 3 times, the own lease once; "own app" builds what the app reads today.
Run from this folder, for example: python read_pages.py sample gemma   (add --dry to run with a fake model)
"""
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor

import pymupdf

import models


def parse_args():
    """The command line."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lease_set", choices=["sample", "own"])
    parser.add_argument("reader", choices=list(models.READERS) + ["app"])
    parser.add_argument("--dry", action="store_true", help="use a fake model; nothing is sent anywhere")
    return parser.parse_args()


def leases_to_read(own):
    """The PDFs to read, as {lease name: path}, and how many times to read each."""
    if own:
        return {"own": models.PRIVATE / "own_lease.pdf"}, 1
    return {name: models.LEASE_TEST / "leases" / f"{name}.pdf" for name in ("scanned", "broken_text")}, 3


def read_one(app, client, reader, job):
    """Read one page from its image with the app's own function. Returns the line to keep."""
    lease, path, number, run = job
    page = pymupdf.open(path)[number - 1]                     # opened here, so each thread has its own document
    models.start_log()
    start = time.perf_counter()
    try:
        text, error = app.lease.read_image(client, page), False
    except Exception as problem:                              # keep a failed read, so one bad call does not end the run
        text, error = f"ERROR: {type(problem).__name__}: {problem}", True
    seconds = round(time.perf_counter() - start, 1)
    requests, _ = models.take_log()
    return {"lease": lease, "page": number, "run": run, "reader": reader, "text": text, "error": error,
            "seconds": seconds, "requests": requests, "cost": round(sum(r["cost"] for r in requests), 6)}


def read_all(app, reader, leases, runs, path):
    """Every page of every lease, `runs` times, 4 pages at a time. Pages already in the file are not read again."""
    done = {(line["lease"], line["page"], line["run"]) for line in models.lines_without_errors(path)}
    jobs = [(lease, pdf, number, run) for run in range(1, runs + 1) for lease, pdf in leases.items()
            for number in range(1, pymupdf.open(pdf).page_count + 1) if (lease, number, run) not in done]
    client = app.config.client()

    def read_and_keep(job):
        """Read one page and save it at once."""
        line = read_one(app, client, reader, job)
        models.add_line(path, line)
        models.say(f"{line['lease']} page {line['page']} run {line['run']}: {line['seconds']} s, ${line['cost']:.4f}"
                   + ("  ERROR" if line["error"] else ""))

    with ThreadPoolExecutor(4) as pool:
        list(pool.map(read_and_keep, jobs))


def write_pages_files(folder, reader, leases):
    """For each lease, its run-1 reading as a pages file in the app's format: text_<lease>_<reader>.json."""
    lines = models.read_lines(folder / f"reads_{reader}.jsonl")
    for lease, pdf in leases.items():
        first = {line["page"]: line["text"] for line in lines
                 if line["lease"] == lease and line["run"] == 1 and not line.get("error")}
        if len(first) < pymupdf.open(pdf).page_count:
            print(f"{lease}: run 1 is not complete ({len(first)} pages read), so no pages file yet")
            continue
        pages = [{"page": number, "text": first[number], "read_by": "image"} for number in sorted(first)]
        (folder / f"text_{lease}_{reader}.json").write_text(json.dumps({"lease": lease, "pages": pages}, indent=1))
        print(f"wrote text_{lease}_{reader}.json")


def build_app_text(folder):
    """What the app reads today from the own lease: each page's PyMuPDF text when it is usable, otherwise Gemma's
    run-1 reading of that page (so "own gemma" must have been run). No model is called here."""
    app = models.setup("uf", dry=True)                        # only to load the app's modules
    gemma = {line["page"]: line["text"] for line in models.read_lines(folder / "reads_gemma.jsonl")
             if line["run"] == 1 and not line.get("error")}
    pages, lacking = [], []
    for number, page in enumerate(pymupdf.open(models.PRIVATE / "own_lease.pdf"), start=1):
        text, read_by = page.get_text(), "text"
        if not models.usable(text):
            text, read_by = gemma.get(number), "image"
            if text is None:
                lacking.append(number)
        pages.append({"page": number, "text": text, "read_by": read_by})
    if lacking:
        print(f"Pages {lacking} have no usable text and no Gemma reading. Run: python read_pages.py own gemma")
        return
    (folder / "text_own_app.json").write_text(json.dumps({"lease": "own", "pages": pages}, indent=1))
    print(f"wrote text_own_app.json: {len(pages)} pages, {sum(p['read_by'] == 'image' for p in pages)} read from images")


def main():
    """Read the pages (or build the app's own reading) and write the files."""
    args = parse_args()
    own = args.lease_set == "own"
    if args.reader == "app" and not own:
        print("app is only for the own lease: the sample leases' app reading is comparisons/lease/texts/.")
        return
    leases, runs = leases_to_read(own)
    lacking = models.missing(leases.values())
    if lacking:
        print("Cannot run yet. These files are missing:", *[f"  {p}" for p in lacking], sep="\n")
        return
    folder = models.results_folder(own, args.dry)
    if args.reader == "app":
        build_app_text(folder)
        return
    gateway, model_id = models.READERS[args.reader]
    app = models.setup(gateway, vision_model=model_id, dry=args.dry)
    print(f"Reading the {args.lease_set} lease pages with {args.reader} ({model_id})" + (" [dry]" if args.dry else ""))
    before = models.spend_before(gateway, args.dry)
    start = time.perf_counter()
    read_all(app, args.reader, leases, runs, folder / f"reads_{args.reader}.jsonl")
    write_pages_files(folder, args.reader, leases)
    reads = models.read_lines(folder / f"reads_{args.reader}.jsonl")
    print(f"Done in {time.perf_counter() - start:.0f} s. {len(reads)} reads in the file, "
          f"${sum(line['cost'] for line in reads):.4f} by the logged costs.")
    models.spend_after(before)


if __name__ == "__main__":
    main()
