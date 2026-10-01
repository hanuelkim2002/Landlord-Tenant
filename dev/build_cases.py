"""Build cases/ from the author's Westlaw Find and Print file: one text file per opinion, the court's text only.

Left out (Westlaw's own material): the KeyCite flag above the cite, the synopsis and holdings, the West
headnotes and their [n] markers inside the opinion, the copyright line, and the negative-treatment table
printed after each opinion. Kept: the caption (cite, court, parties, docket, dates), the attorneys and the
panel, the opinion with any concurrence, dissent, and footnotes, the star pages (*1209) that give pin cites,
and All Citations (the parallel cites).

    python dev/build_cases.py "/path/to/Westlaw Advantage - 82 items from Find And Print.doc"

The print is Rich Text, which macOS's textutil turns into plain text first; a .txt file is read as it is.
Writes cases/<volume>_<reporter>_<page>.txt, e.g. cases/448_So2d_1208.txt for 448 So.2d 1208. Rerunning on
the same print writes the same files. An opinion whose print shows changes by formatting (Westlaw's note
"Additions are indicated by ... and deletions by ...") is skipped and listed: plain text would keep the
struck words as if they were current. cases/ is read-only after the build, like statutes/.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # so config imports from dev/
from config import CASES

# A line that is only a reporter cite, as Westlaw prints one at the top of each opinion: "448 So.2d 1208",
# "50 So.3d 503 (Mem)", "103 Fla. 892", "946 F.Supp. 962".
CITE = re.compile(r"^(\d+) (So\.\s?[23]d|So\.|Fla\.|F\.\s?Supp\.(?:\s?[23]d)?) (\d+)(?: \(Mem\))?$")
COURT = re.compile(r"^(District Court of Appeal|Supreme Court of Florida|United States District Court)")
WESTLAW_PARTS = ("Synopsis", "West Headnotes", "Attorneys and Law Firms")   # the caption ends at the first
SHOWS_CHANGES = "Additions are indicated by"     # Westlaw's editor's note on a print that marks changes


def read_print(path):
    """The print's text as lines."""
    path = Path(path)
    if path.suffix == ".txt":
        return path.read_text().split("\n")
    out = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)],
                         capture_output=True, text=True, check=True)
    return out.stdout.split("\n")


def opens_opinion(lines, i):
    """True if line i starts an opinion: a cite on its own line with a court named just below it. A bare cite
    in a negative-treatment table is followed by a summary instead."""
    below = [line for line in lines[i + 1:i + 8] if line.strip()][:3]
    return bool(CITE.match(lines[i].strip())) and any(COURT.match(line.strip()) for line in below)


def split_print(lines):
    """Each opinion's lines, from its cite line up to Westlaw's "End of Document". After that line come the
    copyright line, the next opinion's negative-treatment table, and its KeyCite flag; the next opinion
    starts at the next line that opens one."""
    opinions, i = [], 0
    while True:
        start = next((k for k in range(i, len(lines)) if opens_opinion(lines, k)), None)
        if start is None:
            return opinions
        end = next(k for k in range(start, len(lines)) if lines[k].startswith("End of Document"))
        opinions.append(lines[start:end])
        i = end + 1


def court_text(opinion):
    """The court's text of one opinion: the caption, then everything from "Attorneys and Law Firms" on, with
    the headnote markers [1], [2], ... taken out. Only numbers up to the headnote count are markers; a
    bracketed number beyond it is the court's own (a pin page, e.g. "13 Fla. Law Weekly [1116] 1117")."""
    caption_end = next(k for k, line in enumerate(opinion) if line.startswith(WESTLAW_PARTS))
    caption = opinion[:caption_end]
    body_start = next((k for k, line in enumerate(opinion) if line.startswith("Attorneys and Law Firms")), None)
    if body_start is None or not any(line.startswith("All Citations") for line in opinion):
        raise ValueError(f"{opinion[0]}: no 'Attorneys and Law Firms' or 'All Citations'; not a Westlaw print?")
    count = next((int(m.group(1)) for line in opinion
                  for m in [re.match(r"West Headnotes \((\d+)\)", line)] if m), 0)
    marker = re.compile(r"\[(\d+)\] ?")
    body = [marker.sub(lambda m: "" if 1 <= int(m.group(1)) <= count else m.group(0), line)
            for line in opinion[body_start:]]
    text = "\n".join(line.rstrip() for line in caption + body)
    return re.sub(r"\n\s*\n(\s*\n)+", "\n\n", text).strip() + "\n"   # no runs of empty lines


def file_name(cite_line):
    """'448 So.2d 1208' -> '448_So2d_1208.txt'; '946 F.Supp. 962' -> '946_FSupp_962.txt'."""
    volume, reporter, page = CITE.match(cite_line.strip()).groups()
    return f"{volume}_{re.sub(r'[^A-Za-z0-9]', '', reporter)}_{page}.txt"


if __name__ == "__main__":
    opinions = split_print(read_print(sys.argv[1]))
    CASES.mkdir(exist_ok=True)
    written, skipped = [], []
    for opinion in opinions:
        if any(SHOWS_CHANGES in line for line in opinion[:12]):
            skipped.append(opinion[0].strip())
            continue
        name = file_name(opinion[0])
        (CASES / name).write_text(court_text(opinion))
        written.append(name)
    print(f"{len(opinions)} opinions in the print; {len(written)} written to {CASES}")
    for cite in skipped:
        print(f"  skipped {cite}: the print marks added and deleted words by formatting, which plain text loses")
