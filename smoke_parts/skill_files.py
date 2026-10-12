"""Smoke, part: the skill format and its checks (TODO item 109). One valid fixture skill and a broken copy for each way a
skill file or its body can be wrong, all written to a temporary folder (never into skills/): the header refused when the
file is loaded, and the body and clock quotes caught by check_skill. Nothing here reads a model or a matter.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

import yaml

import skills
from checks import check
from skills import REQUIRED, check_all_skills, check_skill, clock_facts, load_skill_file

# Statute words copied from playbooks/repair_not_made.yaml (the clocks for 83.56(1) and 83.60(1)(b)) and
# playbooks/notice_received_nonpayment.yaml (83.56(3)), which smoke.py's playbook checks hold word for word in statutes/.
TERMINATE = ("If the landlord materially fails to comply with s. 83.51 (1) or material provisions of the rental agreement "
             "within 7 days after delivery of written notice by the tenant specifying the noncompliance and indicating the "
             "intention of the tenant to terminate the rental agreement by reason thereof, the tenant may terminate the "
             "rental agreement.")
WITHHOLD = ("The defense of a material noncompliance with s. 83.51 (1) may be raised by the tenant if 7 days have elapsed "
            "after the delivery of written notice by the tenant to the landlord, specifying the noncompliance and "
            "indicating the intention of the tenant not to pay rent by reason thereof.")
WITHHOLD_RESULT = ("A material noncompliance with s. 83.51 (1) by the landlord is a complete defense to an action for "
                   "possession based upon nonpayment of rent")
THREE_DAYS = ("If the tenant fails to pay rent when due and the default continues for 3 days, excluding Saturday, Sunday, "
              "and legal holidays, after delivery of written demand by the landlord for payment of the rent or possession "
              "of the premises, the landlord may terminate the rental agreement.")
THREE_DAYS_RESULT = "Legal holidays for the purpose of this section shall be court-observed holidays only."
BODY_QUOTE = "within 7 days after delivery of written notice by the tenant specifying the noncompliance"      # in 83.56(1)

# The fixture's header: two calendar-day clocks.
HEADER = {
    "name": "fixture_repair",
    "description": "Something in the unit needs repair and the landlord has not fixed it.",
    "sections": ["83.51", "83.56", "83.60"],
    "clocks": [
        {"id": "seven_days_after_termination_notice", "actor": "landlord", "trigger": "message_date", "days": 7,
         "direction": "after", "applies_if": "message_mentions_ending", "cite": "83.56(1)", "quote": TERMINATE,
         "condition": "your message says you intend to end the lease because of the problem"},
        {"id": "seven_days_after_withholding_notice", "actor": "landlord", "trigger": "message_date", "days": 7,
         "direction": "after", "applies_if": "message_mentions_rent", "cite": "83.60(1)(b)", "quote": WITHHOLD,
         "consequence": WITHHOLD_RESULT},
    ],
    "counting": {"convention": "calendar days, trigger day not counted, no weekend or holiday adjustment"},
    "provenance": {"statute_year": 2026, "verified_by": None},
}

# The body, as (heading, text) pairs so a test can drop, swap, or add one. One quotation of 20 characters or more with
# its cite next to it, one short quotation (not checked), and a "###" subheading (allowed).
PARTS = [
    ("## When to load this skill", 'Load this when something in the unit needs repair and the landlord has not fixed it. '
                                   'The word "material" is short, so it is not checked.'),
    ("## What to find out", "Ask what the tenant saw and when they wrote to the landlord.\n\n"
                            "### Where each answer comes from\nThe lease first, then the tenant."),
    ("## What the tenant can do", f'The statute lets the tenant end the lease when the landlord does not act: "{BODY_QUOTE}" '
                                  "(Fla. Stat. 83.56(1))."),
    ("## Deadlines", "The program counts seven days from the date of the tenant's written message, once they confirm it."),
    ("## What the statute does not settle", "Whether a failure is material is not settled; say so."),
    ("## Letters", "A letter can ask for the repair."),
    ("## Mistakes to avoid", "Never count the days yourself."),
]


def body(parts=PARTS):
    return "\n\n".join(f"{heading}\n{text}" for heading, text in parts)


def swapped(text, old, new):
    """The text with `old` replaced once by `new`; stops the run if `old` is not there, so a test cannot pass by
    changing nothing."""
    assert old in text, f"the fixture does not contain: {old}"
    return text.replace(old, new, 1)


def skill_text(parts=PARTS, drop=(), **header):
    """A whole skill file: the fixture's header with these changes (and these keys left out), then the body."""
    head = {**HEADER, **header}
    for key in drop:
        del head[key]
    return "---\n" + yaml.safe_dump(head, sort_keys=False, width=100000) + "---\n" + body(parts)


def write(folder, text, file="fixture_repair"):
    path = Path(folder) / f"{file}.md"
    path.write_text(text)
    return path


def refused(folder, text, words, file="fixture_repair"):
    """load_skill_file raises a ValueError that says these words."""
    try:
        load_skill_file(write(folder, text, file))
        return False
    except ValueError as e:
        return words in str(e)


def checked(folder, text, file="fixture_repair"):
    """(failures, lines printed) of check_skill on the skill in this file text."""
    printed = io.StringIO()
    with redirect_stdout(printed):
        fails = check_skill(load_skill_file(write(folder, text, file)))
    return fails, printed.getvalue()


def caught(folder, text, *words, file="fixture_repair"):
    """check_skill fails, on a line that says all of these words (so the right check caught it)."""
    fails, printed = checked(folder, text, file)
    return fails > 0 and any(line.startswith("FAIL") and all(w in line for w in words) for line in printed.splitlines())


def without(heading):
    """The fixture's body parts without this heading."""
    return [p for p in PARTS if p[0] != heading]


def with_clock(index, **changes):
    """The fixture's clocks with these changes made to one of them."""
    return [{**c, **changes} if i == index else c for i, c in enumerate(HEADER["clocks"])]


COURT = {"id": "three_day_demand_period", "actor": "tenant", "trigger": "nonpayment_notice_delivered", "days": 3,
         "direction": "after", "count": "court_business_days", "shown_with": "notice_stated_payment_date",
         "cite": "83.56(3)", "quote": THREE_DAYS, "consequence": THREE_DAYS_RESULT}
COURT_SKILL = dict(name="fixture_court", sections=["83.56"], clocks=[COURT])
NO_CLOCKS = dict(clocks=[], drop=("counting",), sections=["83.51", "83.56"])


with tempfile.TemporaryDirectory() as tmp:
    # a valid skill loads and passes every check
    skill = load_skill_file(write(tmp, skill_text()))
    check("skills: a valid skill file loads, its body being the text after the header",
          skill.name == "fixture_repair" and skill.sections == ["83.51", "83.56", "83.60"] and len(skill.clocks) == 2
          and skill.body.startswith("## When to load this skill") and skill.body.endswith("Never count the days yourself.")
          and skill.counting["convention"].startswith("calendar days") and skill.provenance["verified_by"] is None)
    fails, printed = checked(tmp, skill_text())
    check("skills: a valid skill has no failures; a line each for the headings, three clock quotes, one body quote, and "
          "the ids (a ### subheading and a short quotation are fine)",
          fails == 0 and printed.count("OK   ") == 6 and "FAIL" not in printed)
    check("skills: the required headings are the seven, with Deadlines fourth", len(REQUIRED) == 7 and REQUIRED[3] == "## Deadlines")

    # a skill with no clocks has no Deadlines section and needs no counting convention
    no_clocks = skill_text(parts=without("## Deadlines"), **NO_CLOCKS)
    check("skills: a skill with no clocks loads without Deadlines or a counting convention, and has no clock facts",
          checked(tmp, no_clocks)[0] == 0 and clock_facts(load_skill_file(write(tmp, no_clocks))) == {})

    # the facts the clocks count from are typed by the role they play
    check("skills: clock facts are typed by role (a trigger is a date, an applies_if is yes/no) with no county needed "
          "by a calendar-days clock",
          clock_facts(skill) == {"message_date": "date", "message_mentions_ending": "bool", "message_mentions_rent": "bool"})
    court_text = skill_text(**COURT_SKILL)
    court_skill = load_skill_file(write(tmp, court_text, "fixture_court"))
    check("skills: a court-days clock needs premises_county (a county); its shown_with is a date; 83.56(3) quote and "
          "consequence pass",
          clock_facts(court_skill) == {"nonpayment_notice_delivered": "date", "notice_stated_payment_date": "date",
                                       "premises_county": "county"}
          and checked(tmp, court_text, "fixture_court")[0] == 0)

    # a header that is wrong is refused when the file is loaded
    check("skills: a name that is not the file's name is refused",
          refused(tmp, skill_text(name="other_name"), "is not the file's name"))
    check("skills: a two-line description is refused",
          refused(tmp, skill_text(description="Something needs repair.\nThe landlord has not fixed it."), "one line"))
    check("skills: an empty description is refused", refused(tmp, skill_text(description="  "), "description is empty"))
    check("skills: a description over 200 characters is refused, 200 is not",
          refused(tmp, skill_text(description="a" * 201), "the limit is 200")
          and load_skill_file(write(tmp, skill_text(description="a" * 200))).name == "fixture_repair")
    check("skills: a section that is not in statutes/ is refused",
          refused(tmp, skill_text(sections=["83.51", "83.56", "83.60", "83.99"]), "section 83.99 is not in statutes/"))
    check("skills: a clock whose cite is outside the skill's sections is refused",
          refused(tmp, skill_text(sections=["83.51", "83.56"]), "83.60(1)(b) is not among the skill's sections"))
    check("skills: clocks with no counting convention are refused",
          refused(tmp, skill_text(drop=("counting",)), "needs counting.convention")
          and refused(tmp, skill_text(counting={"status": "ASSUMPTION"}), "needs counting.convention"))
    check("skills: a clock that is not a corpus.Clock (days that is not a number) is refused",
          refused(tmp, skill_text(clocks=with_clock(0, days="seven")), "clocks.0.days"))
    check("skills: a clock key the shape does not define (a misspelled applies_if) is refused, not dropped",
          refused(tmp, skill_text(clocks=with_clock(0, aplies_if="message_mentions_ending")), "aplies_if"))
    check("skills: a header key the shape does not define (clock for clocks), or a missing provenance, is refused",
          refused(tmp, skill_text(clock=[]), "Extra inputs") and refused(tmp, skill_text(drop=("provenance",)), "provenance"))
    check("skills: a file with no header, or a header never closed, is refused",
          refused(tmp, body(), "must start with a line of three dashes")
          and refused(tmp, "---\nname: fixture_repair\n", "no closing line"))

    # a clock quote that is not the statute's words, or not in the subsection the cite names, is caught
    check("skills: a clock quote changed by one word fails its check",
          caught(tmp, skill_text(clocks=with_clock(0, quote=swapped(TERMINATE, "specifying", "describing"))),
                 "clock seven_days_after_termination_notice quote", "not in 83.56"))
    check("skills: a clock consequence changed by one word fails its check",
          caught(tmp, skill_text(clocks=with_clock(1, consequence=swapped(WITHHOLD_RESULT, "complete", "full"))),
                 "clock seven_days_after_withholding_notice consequence", "not in 83.60"))
    check("skills: a clock quote in the section but not in the subsection its cite names fails its check",
          caught(tmp, skill_text(clocks=with_clock(0, cite="83.56(3)")),
                 "clock seven_days_after_termination_notice quote", "is in 83.56(1), not 83.56(3)"))

    # the body's headings: all required, in order, and no others
    check("skills: a missing required heading is caught",
          caught(tmp, skill_text(parts=without("## Letters")), "headings", "missing", "## Letters"))
    swap = [p for p in PARTS]
    swap[-2], swap[-1] = swap[-1], swap[-2]
    check("skills: headings out of order are caught", caught(tmp, skill_text(parts=swap), "headings", "out of order"))
    check("skills: an extra ## heading is caught, and a repeated one",
          caught(tmp, skill_text(parts=PARTS + [("## Appendix", "More.")]), "headings", "not allowed", "## Appendix")
          and caught(tmp, skill_text(parts=PARTS + [PARTS[-1]]), "headings", "repeated"))
    check("skills: Deadlines missing while the skill has clocks is caught",
          caught(tmp, skill_text(parts=without("## Deadlines")), "headings", "missing", "## Deadlines"))
    check("skills: Deadlines present while the skill has no clocks is caught",
          caught(tmp, skill_text(**NO_CLOCKS), "headings", "not allowed", "## Deadlines"))

    # the body's quotations: word for word in a stored section, and in the cited subsection
    fake = "the landlord must repair the unit within seven days of any written request"
    check("skills: a body quotation in no stored section is caught, with a cite next to it or without",
          caught(tmp, skill_text(parts=[(h, swapped(t, BODY_QUOTE, fake)) if h == "## What the tenant can do" else (h, t)
                                        for h, t in PARTS]), "body quote", "the landlord must repair", "not in 83.56")
          and caught(tmp, skill_text(parts=[(h, swapped(t, f"(Fla. Stat. 83.56(1))", "").replace(BODY_QUOTE, fake))
                                            if h == "## What the tenant can do" else (h, t) for h, t in PARTS]),
                     "body quote", "the landlord must repair", "not word for word in the statute"))
    check("skills: a body quotation cited to the wrong subsection is caught",
          caught(tmp, skill_text(parts=[(h, swapped(t, "83.56(1)", "83.56(3)")) if h == "## What the tenant can do" else (h, t)
                                        for h, t in PARTS]), "body quote", "is in 83.56(1), not 83.56(3)"))
    check("skills: a body quotation cited to a subsection the section does not have is caught",
          caught(tmp, skill_text(parts=[(h, swapped(t, "83.56(1)", "83.56(9)")) if h == "## What the tenant can do" else (h, t)
                                        for h, t in PARTS]), "body quote", "83.56(9) is not a section or subsection"))

    # no clock id or clock fact id in the prose
    check("skills: a clock fact id written in the prose is caught",
          caught(tmp, skill_text(parts=[(h, swapped(t, "the date of the tenant's written message", "message_date"))
                                        if h == "## Deadlines" else (h, t) for h, t in PARTS]),
                 "no clock id or clock fact id", "message_date"))
    check("skills: a clock id written in the prose is caught",
          caught(tmp, skill_text(parts=[(h, swapped(t, "seven days", "seven_days_after_termination_notice"))
                                        if h == "## Deadlines" else (h, t) for h, t in PARTS]),
                 "no clock id or clock fact id", "seven_days_after_termination_notice"))
    check("skills: premises_county written in the prose of a skill with a court-days clock is caught",
          caught(tmp, skill_text(parts=[(h, swapped(t, "the tenant's written message", "premises_county"))
                                        if h == "## Deadlines" else (h, t) for h, t in PARTS], **COURT_SKILL),
                 "no clock id or clock fact id", "premises_county", file="fixture_court"))

# the skills folder: a dict, name to Skill, empty until TODO item 110 writes the ten skills; checking it finds no failure
check("skills: skills.skills is a dict, and check_all_skills finds no failure in what it holds",
      isinstance(skills.skills, dict) and check_all_skills() == 0)
print()
