"""Counts the time spans in a skill test's answers ("more than three weeks", "23 days", "several days") and sorts each
one: the tenant's own words, a count code gives (days or whole weeks from a date fact to the story's today), or the
model's own counting. Statute periods ("within 7 days after delivery") are left out. Run from this folder:
python spans.py repair_not_made keys2 [more versions] [--stories 1,2,3,7,9] [--folder results/spans]
"""
import argparse
import re
from datetime import date

import run                                                    # a skill's stories and where its answers are kept

NUMBERS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
           "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
NUMBER = r"(\d+(?:\.\d+)?½?|" + "|".join(NUMBERS) + r")"
SPAN = re.compile(rf"\b{NUMBER}(\s+and\s+a\s+half)?[\s-]+(day|week|month|year)s?\b(\s+and\s+a\s+half)?", re.I)
# A span with no number ("several days", "for weeks"). Its words stand in for the number, so it can match the
# tenant's own words but never a count code gives.
VAGUE = re.compile(r"\b(several|a few|a couple of|many|some)\s+(day|week|month)s\b|\bfor\s+(day|week|month)s\b", re.I)
# Words that make a span a length of time that has passed or is left, not a statute's period.
ELAPSED_BEFORE = re.compile(r"(for|been|lasted|over|more than|almost|nearly|about|roughly|around|already|past|last|"
                            r"close to|just over|under|less than|only)\s*$", re.I)
ELAPSED_AFTER = re.compile(r"^\s*(ago|now|so far|since|and counting|have passed|has passed|of\b|without|later|in)", re.I)
STATUTE = re.compile(r"(within|the|a|this|that|those|its|first|additional)\s*$", re.I)
PERIODS = {5, 7, 15, 30, 60}                                  # the statute's day counts; a story's own spans are none of these


def amount(match):
    """A span's number and unit, like (3.5, "week")."""
    word = match.group(1).lower()
    value = NUMBERS.get(word) or float(word.replace("½", "")) + (0.5 if "½" in word else 0)
    if match.group(2) or match.group(4):                      # "three and a half weeks", "a week and a half"
        value += 0.5
    return value, match.group(3).lower()


def spans_in(text):
    """Every length of time in the text that has passed or is left: [(words, number, unit)]."""
    found = []
    for m in SPAN.finditer(text):
        before, after = text[max(0, m.start() - 25):m.start()], text[m.end():m.end() + 20]
        value, unit = amount(m)
        if (STATUTE.search(before) and not ELAPSED_BEFORE.search(before)) or (unit == "day" and value in PERIODS):
            continue
        if ELAPSED_BEFORE.search(before) or ELAPSED_AFTER.search(after):
            found.append((text[max(0, m.start() - 40):m.end() + 20].replace("\n", " "), value, unit))
    for m in VAGUE.finditer(text):
        if re.search(r"within\s*$", text[max(0, m.start() - 10):m.start()], re.I):   # a period to act in, not a span
            continue
        found.append((text[max(0, m.start() - 40):m.end() + 20].replace("\n", " "), m.group(0).lower(),
                      (m.group(2) or m.group(3)).lower()))
    return found


def code_counts(story):
    """The spans code would give: days and whole weeks from each date fact to the story's today, and to the future."""
    today, counts = date.fromisoformat(story["today"]), set()
    for value in story["facts"].values():
        if re.fullmatch(r"\d{4}-\d\d-\d\d", value):
            days = abs((today - date.fromisoformat(value)).days)
            counts |= {(float(days), "day"), (float(days // 7), "week")}
            if days % 7 in (3, 4):                            # only then is "and a half" a fair reading of code's count
                counts.add((days // 7 + 0.5, "week"))
    return counts


def kind(span, story):
    """Whose span this is: the tenant's words, a count code gives, or the model's own."""
    if (span[1], span[2]) in {(s[1], s[2]) for s in spans_in(story["message"])}:
        return "tenant"
    return "code" if (span[1], span[2]) in code_counts(story) else "own"


def main():
    """Print every span found, then each version's totals."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill")
    parser.add_argument("versions", nargs="+")
    parser.add_argument("--stories", help="only these story numbers, like 1,2,3,7,9")
    parser.add_argument("--folder", default="results", help="where the answers are, inside the skill's folder")
    args = parser.parse_args()
    stories = {s["id"]: s for s in run.chosen(run.all_stories(args.skill), args.stories)}
    for version in args.versions:
        lines = [l for l in run.models.read_lines(run.test_folder(args.skill) / args.folder / f"{version}.jsonl")
                 if l["story"] in stories]
        totals = {"tenant": 0, "code": 0, "own": 0}
        for line in sorted(lines, key=lambda l: (l["story"], l["run"])):
            for span in spans_in(line["answer"]):
                which = kind(span, stories[line["story"]])
                totals[which] += 1
                print(f"{version} {line['story']}/{line['run']} {which:6} | {span[0]}")
        print(f"== {version}: {len(lines)} answers; spans: {totals}\n")


if __name__ == "__main__":
    main()
