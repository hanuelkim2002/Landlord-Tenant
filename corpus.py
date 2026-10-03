"""Statutes and Playbooks: the stored corpus. Statute text keyed by section; playbooks keyed by issue.

Both are loaded once when this module is imported. Nothing here calls a model.
"""
import re
from typing import List, Literal, Optional, Union

import yaml
from pydantic import BaseModel

from config import PLAYBOOKS, STATUTES, squash
from deterministic import ISSUE_LABELS
from lease import LeaseProfile


# ---- Load Statutes: one entry per section, keyed by number ("83.49").

statute = {p.stem: p.read_text() for p in STATUTES.glob("83.*.txt")}


# ---- Playbook Shape: the spec half is read by code and strictly typed; the guidance half is prose, left as a dict.

class Element(BaseModel):
    """One fact the tool needs before it can say anything about this issue.
    check_elements reads these to decide what is known and what to ask. compare_to names a lease field
    (e.g. "lease_profile.term_end") to set next to the tenant's answer when the two differ."""
    id: str
    type: Literal["date", "money", "bool", "text"]
    source: List[str]
    applies_if: Optional[str] = None
    compare_to: Optional[str] = None


class Clock(BaseModel):
    """One statutory deadline: whose it is, which date it counts from, how many
    days, and the sentence it comes from. compute_deadlines reads these. count: calendar days (the default)
    or court business days, which skip Saturdays, Sundays, and the county's court holidays (calendars.py).
    shown_with names a date element printed next to the computed date once confirmed, such as the date the
    notice itself states, so the tenant sees both."""
    id: str
    actor: Literal["landlord", "tenant"]
    trigger: str
    days: int
    direction: Literal["before", "after"]
    cite: str
    quote: str
    consequence: Optional[str] = None
    delivery: Optional[List[str]] = None
    applies_if: Optional[str] = None
    count: Literal["calendar_days", "court_business_days"] = "calendar_days"
    shown_with: Optional[str] = None


class Condition(BaseModel):
    """A confirmed fact and the value it must have, e.g. claim_notice_received equals true."""
    fact: str
    equals: Union[bool, str, int, float]


class RelatedIssue(BaseModel):
    """Another issue this one leads to: record.add_related_issues adds it once the condition's fact is
    confirmed with that value."""
    issue: str
    when: Condition


class Spec(BaseModel):
    """The code-facing half of a playbook. Strictly typed where code computes
    from it (elements, clocks); loose lists where nothing does yet."""
    elements: List[Element]
    clocks: List[Clock]
    lease_overrides: list = []
    exclusions: list = []
    related_issues: List[RelatedIssue] = []
    open_questions: list = []


class Playbook(BaseModel):
    """One YAML playbook loaded into Python. spec is validated; provenance,
    counting, and guidance are plain dicts read by people or the model.
    sections: the statute sections the playbook rests on, put into the prompt while its issue is active.
    description: the situation the playbook covers, in one line; shown to the classifier and to the tenant."""
    issue: str
    description: str
    sections: List[str]
    provenance: dict
    counting: dict
    spec: Spec
    guidance: dict


# ---- Load and Check Playbook

def load_playbook(path):
    """Validate the shape, confirm every section is in statutes/, every clock counts from a date element
    (and any shown_with names one), and every compare_to names a real lease field."""
    pb = Playbook.model_validate(yaml.safe_load(open(path)))
    for s in pb.sections:
        if s not in statute:
            raise ValueError(f"{pb.issue}: section {s} is not in statutes/")
    for e in pb.spec.elements:
        if e.compare_to and e.compare_to.replace("lease_profile.", "") not in LeaseProfile.model_fields:
            raise ValueError(f"element {e.id}: compare_to {e.compare_to} is not a lease profile field")
    date_ids = [e.id for e in pb.spec.elements if e.type == "date"]
    for c in pb.spec.clocks:
        if c.trigger not in date_ids:
            raise ValueError(f"clock {c.id}: trigger {c.trigger} is not a date element")
        if c.shown_with and c.shown_with not in date_ids:
            raise ValueError(f"clock {c.id}: shown_with {c.shown_with} is not a date element")
        if c.count == "court_business_days" and "premises_county" not in [e.id for e in pb.spec.elements]:
            raise ValueError(f"clock {c.id}: court business days need a premises_county element")
    return pb


def report(name, ok):
    """Print one playbook check line, OK or FAIL, and return 1 for a failure so callers can count them."""
    print(("OK   " if ok else "FAIL ") + name)
    return 0 if ok else 1


def prose_strings(x):
    """Every string inside a playbook's guidance or open questions, one at a time, so quotations are read
    within the string they belong to."""
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from prose_strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from prose_strings(v)


def check_playbook(playbook, statute):
    """Check one playbook and print a line per check. Returns the number of failures.
    Quotes: every spec quote word for word in the section it cites, and every quotation of 20 or more
    characters in the guidance and open questions word for word in a stored section. Shape: a question for
    every element and an element for every question, applies_if naming a yes/no fact, clock cites among the
    playbook's sections, each open question's id, sections, text, and readings (two or more when given), and
    the guidance parts the tool reads (postures, including notice_sufficiency)."""
    fails = 0
    quotes = []
    for c in playbook.spec.clocks:
        quotes.append((c.id, c.cite, c.quote))
        if c.consequence:
            quotes.append((c.id + " consequence", c.cite, c.consequence))
    for item in playbook.spec.lease_overrides + playbook.spec.exclusions:
        if item.get("quote"):
            quotes.append((item["cite"], item["cite"], item["quote"]))
    for name, cite, quote in quotes:
        section = cite.split("(")[0]                    # "83.49(3)(a)" -> "83.49"
        fails += report(f"{name} {cite}", squash(quote) in squash(statute[section]))

    for text in prose_strings([playbook.guidance, playbook.spec.open_questions]):
        for quoted in re.findall(r'"([^"]*)"', text):
            if len(quoted) >= 20:                        # shorter ones are words in quotes, not statute text
                fails += report(f'prose quote "{quoted[:50]}..."',
                                any(squash(quoted) in squash(t) for t in statute.values()))

    elements = {e.id: e for e in playbook.spec.elements}
    questions = playbook.guidance.get("questions", {})
    fails += report("a question for every element, an element for every question", set(elements) == set(questions))
    for thing in playbook.spec.elements + playbook.spec.clocks:
        if thing.applies_if:
            target = elements.get(thing.applies_if)
            fails += report(f"{thing.id}: applies_if {thing.applies_if} is a yes/no fact", target is not None and target.type == "bool")
    for c in playbook.spec.clocks:
        fails += report(f"clock {c.id}: {c.cite} is among the playbook's sections", c.cite.split("(")[0] in playbook.sections)
    # Open questions (rule 5): each says what applies and what stays open; an open point carries two or more
    # readings, which the model gives side by side instead of settling it.
    fails += report("open questions: each has an id, sections in statutes/, and text; readings, if any, two or more",
                    all(isinstance(q, dict) and q.get("id") and q.get("text") and q.get("sections")
                        and all(s in statute for s in q["sections"])
                        and ("readings" not in q or (isinstance(q["readings"], list) and len(q["readings"]) >= 2
                                                     and all(isinstance(r, str) for r in q["readings"])))
                        for q in playbook.spec.open_questions))
    postures = playbook.guidance.get("postures", {})
    fails += report("guidance has lease_checks, evidence, failure_modes, and every posture",
                    all(k in playbook.guidance for k in ("lease_checks", "evidence", "failure_modes"))
                    and all(k in postures for k in ("core", "preserve", "assert", "escalate", "notice_sufficiency")))
    return fails


def check_all_playbooks():
    """Run check_playbook on every loaded playbook, then check that a fact id used by more than one playbook
    has the same type and question in each. Called by smoke.py, not at import. Returns the number of failures."""
    fails = 0
    for issue, pb in playbooks.items():
        print(f"--- {issue}")
        fails += check_playbook(pb, statute)
    print("--- facts shared across playbooks")
    for fact_id in sorted({e.id for pb in playbooks.values() for e in pb.spec.elements}):
        uses = [(pb.issue, e.type, pb.guidance["questions"].get(fact_id)) for pb in playbooks.values()
                for e in pb.spec.elements if e.id == fact_id]
        if len(uses) > 1:
            fails += report(f"{fact_id}: same type and question in {[u[0] for u in uses]}",
                            len({u[1] for u in uses}) == 1 and len({u[2] for u in uses}) == 1)
    print(len(playbooks), "playbooks loaded:", list(playbooks))
    return fails


playbooks = {}
for path in sorted(PLAYBOOKS.glob("*.yaml")):
    pb = load_playbook(path)
    playbooks[pb.issue] = pb

# A related issue must be a label the classifier knows, and its condition a fact some playbook asks for.
_all_facts = {e.id for pb in playbooks.values() for e in pb.spec.elements}
for pb in playbooks.values():
    for rel in pb.spec.related_issues:
        if rel.issue not in ISSUE_LABELS:
            raise ValueError(f"{pb.issue}: related issue {rel.issue} is not an issue label")
        if rel.when.fact not in _all_facts:
            raise ValueError(f"{pb.issue}: related issue condition {rel.when.fact} is not a fact any playbook asks for")


def issue_menu():
    """Every label classify can pick, with the situation it covers: a playbook's description, and "other" for
    none of them. What the classifier reads instead of bare label names."""
    return {label: playbooks[label].description if label in playbooks else "None of the situations above."
            for label in ISSUE_LABELS}
