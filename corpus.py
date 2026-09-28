"""Statutes and Playbooks: the stored corpus. Statute text keyed by section; playbooks keyed by issue.

Both are loaded once when this module is imported. Nothing here calls a model.
"""
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
    days, and the sentence it comes from. compute_deadlines reads these."""
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
    sections: the statute sections the playbook rests on, put into the prompt while its issue is active."""
    issue: str
    sections: List[str]
    provenance: dict
    counting: dict
    spec: Spec
    guidance: dict


# ---- Load and Check Playbook

def load_playbook(path):
    """Validate the shape, confirm every section is in statutes/, every clock counts from a date element,
    and every compare_to names a real lease field."""
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
    return pb


def check_playbook(playbook, statute):
    """Every quote in spec must appear word for word in the section it cites."""
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
        found = squash(quote) in squash(statute[section])
        print("OK  " if found else "FAIL", name, cite)


def check_all_playbooks():
    """Run check_playbook on every loaded playbook. Called by smoke.py, not at import."""
    for issue, pb in playbooks.items():
        print(f"--- {issue}")
        check_playbook(pb, statute)
    print(len(playbooks), "playbooks loaded:", list(playbooks))


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
