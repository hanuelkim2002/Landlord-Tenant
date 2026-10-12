"""Skills: the instructions the model reads, one markdown file per situation, in skills/. The design is in
docs/structure/2026-10-12-skills.md.

A skill file is a header in YAML between two lines of three dashes, then the instructions in markdown. The header
holds only what code needs: the name and the one-line description the model picks the skill by, the statute sections
the skill loads, the deadline clocks (corpus.Clock, with the facts they count from), the counting convention, and the
author's sign-off. Everything else is prose.

Loaded once when this module is imported. Nothing here calls a model. Nothing reads a skill yet except the checks
(check_skill, check_all_skills, run by smoke.py).
"""
import re
from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from citations import check_quoted, is_in, quoted_passages, subsections, where_in
from config import SKILLS
from corpus import Clock, report, statute


# ---- Skill Shape

class Skill(BaseModel):
    """One skill file loaded into Python. name: the file's name without .md, the situation's label. description: one
    line naming the event that starts the situation, how the model picks the skill. sections: the statute sections the
    skill rests on, put into the prompt once it is loaded. clocks: the deadlines the program computes for it.
    counting: the convention printed with every computed date (and a status and note for people). provenance: statute
    year, file verified against, who and when, version. body: the markdown after the header.
    A key the shape does not define is refused, so a misspelled `clocks` cannot silently drop a deadline."""
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    sections: List[str]
    clocks: List[Clock] = []
    counting: dict = {}
    provenance: dict
    body: str


# The body's "## " headings, in order. "## Deadlines" is for a skill that has clocks, and sits right after "What the
# tenant can do". Other "## " headings are not allowed, so every skill reads the same way; "### " subheadings are free.
DEADLINES = "## Deadlines"
REQUIRED = ["## When to load this skill", "## What to find out", "## What the tenant can do", DEADLINES,
            "## What the statute does not settle", "## Letters", "## Mistakes to avoid"]
MAX_DESCRIPTION = 200


# ---- Load a Skill File

def cite_parts(cite):
    """A cite split into its section and its subsection: "83.60(1)(b)" gives ("83.60", "(1)(b)"); "83.49" gives
    ("83.49", "")."""
    section, bracket, rest = "".join(cite.split()).partition("(")
    return section, bracket + rest


def load_skill_file(path):
    """Read one skill file and validate its header; raise ValueError, naming the file, for anything wrong in it:
    - the file does not start with the header's two lines of three dashes, or the header is not a YAML mapping;
    - a key the shape does not define (also inside a clock), a missing one, or a clock that is not a corpus.Clock;
    - the name is not the file's name without .md;
    - the description is empty, longer than 200 characters, or over more than one line;
    - a section is not in statutes/;
    - a clock's cite names a section that is not among the skill's sections;
    - the skill has clocks and no counting convention.
    The body is everything after the header's second line, without the blank lines around it."""
    path = Path(path)
    lines = path.read_text().splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path.name}: the file must start with a line of three dashes, then the header")
    ends = [i for i, line in enumerate(lines) if i > 0 and line.strip() == "---"]
    if not ends:
        raise ValueError(f"{path.name}: the header has no closing line of three dashes")
    try:
        header = yaml.safe_load("\n".join(lines[1:ends[0]]))
    except yaml.YAMLError as e:
        raise ValueError(f"{path.name}: the header is not valid YAML ({e})") from None
    if not isinstance(header, dict):
        raise ValueError(f"{path.name}: the header must be a mapping of keys to values")
    if "body" in header:
        raise ValueError(f"{path.name}: body is the text after the header, not a key in it")
    for raw in header.get("clocks") or []:                   # a Clock drops a key it does not know; a skill refuses it
        unknown = sorted(set(raw) - set(Clock.model_fields)) if isinstance(raw, dict) else []
        if unknown:
            raise ValueError(f"{path.name}: clock {raw.get('id')} has a key the shape does not define ({unknown[0]})")
    try:
        skill = Skill.model_validate({**header, "body": "\n".join(lines[ends[0] + 1:]).strip()})
    except ValidationError as e:
        raise ValueError(f"{path.name}: {e}") from None

    if skill.name != path.stem:
        raise ValueError(f"{path.name}: name {skill.name} is not the file's name ({path.stem})")
    if not skill.description.strip():
        raise ValueError(f"{skill.name}: the description is empty")
    if "\n" in skill.description or "\r" in skill.description:
        raise ValueError(f"{skill.name}: the description must be one line")
    if len(skill.description) > MAX_DESCRIPTION:
        raise ValueError(f"{skill.name}: the description is {len(skill.description)} characters; "
                         f"the limit is {MAX_DESCRIPTION}")
    for s in skill.sections:
        if s not in statute:
            raise ValueError(f"{skill.name}: section {s} is not in statutes/")
    for c in skill.clocks:
        if cite_parts(c.cite)[0] not in skill.sections:
            raise ValueError(f"{skill.name}: clock {c.id}: cite {c.cite} is not among the skill's sections")
    if skill.clocks and not skill.counting.get("convention"):
        raise ValueError(f"{skill.name}: a skill with clocks needs counting.convention")
    return skill


def clock_facts(skill):
    """The facts the skill's clocks count from, as {fact id: type}, typed by the role each plays (so there is no
    separate list of facts): a trigger and a shown_with are dates, an applies_if is yes/no ("bool"), and a clock
    counted in court business days needs the county ("premises_county", type "county")."""
    facts = {}
    for c in skill.clocks:
        facts[c.trigger] = "date"
        if c.shown_with:
            facts[c.shown_with] = "date"
        if c.applies_if:
            facts[c.applies_if] = "bool"
        if c.count == "court_business_days":
            facts["premises_county"] = "county"
    return facts


# ---- Check a Skill

def headings(body):
    """The body's "## " headings, in order, each as written ("## Letters"); a "### " subheading is not one."""
    return ["## " + h for h in re.findall(r"^## (.+?)\s*$", body, flags=re.M)]


def heading_problem(skill):
    """What is wrong with the skill's "## " headings, in words, or None: REQUIRED in order (with "## Deadlines" only
    when the skill has clocks), none missing, none repeated, and no other."""
    expected = [h for h in REQUIRED if h != DEADLINES or skill.clocks]
    found = headings(skill.body)
    if found == expected:
        return None
    missing = [h for h in expected if h not in found]
    extra = [h for h in found if h not in expected]
    repeated = sorted({h for h in found if found.count(h) > 1})
    if missing:
        return f"missing {missing}"
    if extra:
        return f"not allowed {extra}" + (" (only a skill with clocks has Deadlines)" if DEADLINES in extra else "")
    if repeated:
        return f"repeated {repeated}"
    return "out of order"


def cite_problem(words, cite):
    """Why these words are not in the section a cite names, and in its subsection when it names one, in a few words
    (worded as check_quoted words its problems), or None when they are."""
    section, sub = cite_parts(cite)
    if section not in statute:
        return f"{section} is not in statutes/"
    if not is_in(words, statute[section]):
        return f"is not in {section}"
    if sub:
        span = subsections(section).get(sub)
        if span is None:
            return f"{section} has no subsection {sub}"
        if not is_in(words, statute[section][span[0]:span[1]]):
            return f"is in {where_in(words, section)}, not {cite}"
    return None


def ids_in_prose(skill):
    """The clock ids and clock fact ids that appear in the body as a whole word, sorted. The model copied ids it read
    in prose into its replies (TODO item 53), so the body says things in words; the prompt names the facts by id. Only
    an id with an underscore counts: a one-word id such as "vacated" is also a plain word, harmless in a reply."""
    ids = {i for i in {c.id for c in skill.clocks} | set(clock_facts(skill)) if "_" in i}
    return sorted(i for i in ids if re.search(rf"\b{re.escape(i)}\b", skill.body))


def check_skill(skill):
    """Check one skill and print a line per check, OK or FAIL, each naming the skill. Returns the number of failures.
    Headings: the required ones in order, no others. Clocks: each clock's quote, and its consequence if it has one,
    word for word in the section its cite names and in the subsection the cite names. Body: every quotation of 20
    characters or more word for word in a stored section, and in the cited section and subsection when a cite is next
    to it (citations.check_quoted with nothing given, so only the statute counts). Prose: no clock id or clock fact id
    in the body. (The header was checked when the file was loaded, by load_skill_file.)"""
    fails = 0
    problem = heading_problem(skill)
    fails += report(f"{skill.name}: the body's headings are the required ones, in order" +
                    (f": {problem}" if problem else ""), problem is None)

    for c in skill.clocks:
        for kind, words in [("quote", c.quote), ("consequence", c.consequence)]:
            if words:
                problem = cite_problem(words, c.cite)
                fails += report(f"{skill.name}: clock {c.id} {kind} {c.cite}" +
                                (f": {problem}" if problem else ""), problem is None)

    # check_quoted skips a quote whose cite names a section or subsection that is not stored (replies.check_reply leaves
    # that to check_cites); a skill's quote next to such a cite is not in the cited place, so it fails here.
    failed = {(quote, cite): why for quote, cite, why in check_quoted(skill.body, "")}
    for quote, cite in quoted_passages(skill.body):
        problem = failed.get((quote, cite))
        section, sub = cite_parts(cite)
        if problem is None and cite and (section not in statute or (sub and sub not in subsections(section))):
            problem = f"{cite} is not a section or subsection in statutes/"
        fails += report(f'{skill.name}: body quote "{" ".join(quote.split())[:50]}..."' + (f" {cite}" if cite else "") +
                        (f": {problem}" if problem else ""), problem is None)

    named = ids_in_prose(skill)
    fails += report(f"{skill.name}: no clock id or clock fact id in the body" + (f": {named}" if named else ""), not named)
    return fails


def check_all_skills():
    """Run check_skill on every loaded skill and print a last line with the number of failures. Called by smoke.py,
    not at import. Returns the number of failures."""
    fails = sum(check_skill(skill) for skill in skills.values())
    print(f"{len(skills)} skills checked, {fails} failures")
    return fails


# ---- Load Skills: one entry per file in skills/, keyed by name, in name order. Empty when there is no such folder.

skills = {}
for path in sorted(SKILLS.glob("*.md")):
    skill = load_skill_file(path)
    skills[skill.name] = skill
