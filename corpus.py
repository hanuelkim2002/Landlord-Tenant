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
    (e.g. "lease_profile.term_end") to set next to the tenant's answer when the two differ.
    A choice fact (TODO items 86 and 90 to 92) lists its answers in plain words in choices: what the tenant saw or
    did (how a message was sent, who caused a problem), never a term of the statute; the playbook's ways say what
    each answer means for a condition."""
    id: str
    type: Literal["date", "money", "bool", "text", "choice"]
    source: List[str]
    applies_if: Optional[str] = None
    compare_to: Optional[str] = None
    choices: Optional[List[str]] = None


class Clock(BaseModel):
    """One statutory deadline: whose it is, which date it counts from, how many
    days, and the sentence it comes from. compute_deadlines reads these. count: calendar days (the default)
    or court business days, which skip Saturdays, Sundays, and the county's court holidays (calendars.py).
    shown_with names a date element printed next to the computed date once confirmed, such as the date the
    notice itself states, so the tenant sees both. condition: what the date counts only if, in words, printed with
    it, when it counts from a paper whose sufficiency the tool does not decide (a notice the tenant sent)."""
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
    condition: Optional[str] = None


class Condition(BaseModel):
    """A confirmed fact and the value it must have, e.g. claim_notice_received equals true; for a choice fact, a
    list of answers, any of which holds."""
    fact: str
    equals: Union[bool, str, int, float, List[str]]


class RelatedIssue(BaseModel):
    """Another issue this one leads to: record.add_related_issues adds it once the condition's fact is
    confirmed with that value."""
    issue: str
    when: Condition


class Way(BaseModel):
    """One way a gate's condition can be met (TODO item 81), decided by exactly one of:
    - fact: met when the fact is confirmed with the value in equals. Not confirmed, the tenant can tell the tool
      (the sheet asks), unless the way names a lease clause (lease) the tool has not read: then the tenant can
      check that part of the lease.
    - clock: met when the clock's status from compute_deadlines is equals ("passed", the default, or "upcoming").
      With its start date not confirmed, the tenant can tell the tool; a clock the tool cannot count (no court
      calendar for the county or the year) is outside the tool.
    - check: nothing the tool holds decides it, but the tenant can check it (a part of the lease, a local code, a
      document): what, and where. lease, if given, names the lease clause the check is about.
    - outside: law the tool does not hold, in plain words.
    - open_question alone: the stored text does not settle it (whether a violation could be cured); not settled.
    For a choice fact, equals may list several answers, any of which meets the way.
    applies_if limits a way to when it holds: a yes/no fact confirmed true (an objection already sent), or, as
    {fact, equals}, a choice fact confirmed with one of the answers listed (a message sent by e-mail). Confirmed
    otherwise, the way is not met; not confirmed, the tenant can tell the tool (TODO item 84).
    A fact or clock confirmed against the way: otherwise "closed" (the default; the way fails), "unsettled" (the
    stored text does not settle what follows: open_question names the open question), or "later" (not met yet:
    it may still happen, such as a case not filed yet or a period still running). when_otherwise says why, in plain
    words. says, cite, and quote, when given, are the way's own condition and the statute's words for it; a gate
    with one way leaves them to the gate. beside, on a check, names a text fact whose words (the tenant's notice,
    copied) are given with the check, to set beside the statute's."""
    says: Optional[str] = None
    cite: Optional[str] = None
    quote: Optional[str] = None
    fact: Optional[str] = None
    equals: Optional[Union[bool, str, int, float, List[str]]] = None
    clock: Optional[str] = None
    lease: Optional[str] = None
    check: Optional[str] = None
    outside: Optional[str] = None
    otherwise: Literal["closed", "unsettled", "later"] = "closed"
    when_otherwise: Optional[str] = None
    open_question: Optional[str] = None
    applies_if: Optional[Union[str, Condition]] = None
    beside: Optional[str] = None


class Gate(BaseModel):
    """A condition an option needs (TODO items 72 and 81): says is the condition in plain words, and quote the
    statute's words it rests on, from cite. It is met when any of its ways is met (83.56(1)'s duty can come from
    83.51(1) or from the lease), and deterministic.check_options gives it what the tool knows of it: known (met,
    not met, or not met yet), something the tenant can tell the tool, something the tenant can check, not settled,
    or outside the tool."""
    says: str
    cite: str
    quote: str
    ways: List[Way]


class Step(BaseModel):
    """A step toward an option the tenant takes or waits for, decided by one of: a fact (done when confirmed with the
    value in equals), a clock (done when its date has passed, waiting while upcoming), or ways, as a gate's condition
    is (TODO items 86 and 90 to 92): done through a way met, the tenant can check through a check (whether a notice's
    words state the intention the statute names), not settled through an open question; to do otherwise."""
    says: str
    cite: str
    quote: str
    fact: Optional[str] = None
    equals: Optional[Union[bool, str, int, float]] = None
    clock: Optional[str] = None
    ways: List[Way] = []


class Option(BaseModel):
    """Something the statute lets the tenant do (end the lease, withhold rent), with the gates that decide
    whether it is open on the tenant's facts and the steps it takes. also_open: open questions that stay open
    even when every gate is met (whether a failure is "material")."""
    id: str
    label: str
    cite: str
    gates: List[Gate]
    steps: List[Step]
    also_open: List[str] = []


class Spec(BaseModel):
    """The code-facing half of a playbook. Strictly typed where code computes
    from it (elements, clocks, options); loose lists where nothing does yet."""
    elements: List[Element]
    clocks: List[Clock]
    lease_overrides: list = []
    exclusions: list = []
    related_issues: List[RelatedIssue] = []
    open_questions: list = []
    options: List[Option] = []


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

def answers_problem(element, equals):
    """What is wrong with the answers a way or an applies_if names for a fact, or None: a list only for a choice fact,
    and every answer named one the choice lists."""
    named = equals if isinstance(equals, list) else [equals]
    if element.type != "choice":
        return None if not isinstance(equals, list) else f"lists answers for a fact that is not a choice ({element.id})"
    unknown = [a for a in named if a not in element.choices]
    return f"names an answer {element.id} does not list ({unknown[0]})" if unknown else None


def way_problem(w, facts, clocks, questions):
    """What is wrong with a gate's or a step's way, in words, or None: it must be decided by exactly one of a fact, a
    clock, a check, or law outside the tool, or else by an open question alone; a fact needs equals, an answer its
    choice lists (answers_problem); a clock's equals is "passed" or "upcoming"; a fact or clock needs when_otherwise,
    and an open question exactly when otherwise is "unsettled"; a check or outside way names none; applies_if is a
    yes/no fact, or a choice fact with answers it lists; beside, only on a check, a text fact; and every fact, clock,
    open question, and lease clause named must exist. facts: the playbook's elements by id."""
    deciders = sum(d is not None for d in [w.fact, w.clock, w.check, w.outside])
    if deciders > 1 or (deciders == 0 and not w.open_question):
        return "needs exactly one of fact, clock, check, or outside, or an open question alone"
    if w.open_question and w.open_question not in questions:
        return f"names an open question the playbook lacks ({w.open_question})"
    if w.fact is not None and (w.fact not in facts or w.equals is None):
        return f"names a fact the playbook lacks, or no equals ({w.fact})"
    if w.fact is not None and answers_problem(facts[w.fact], w.equals):
        return answers_problem(facts[w.fact], w.equals)
    if w.clock is not None and (w.clock not in clocks or w.equals not in (None, "passed", "upcoming")):
        return f"names a clock the playbook lacks, or an equals other than passed or upcoming ({w.clock})"
    if (w.fact or w.clock) and not w.when_otherwise:
        return "needs when_otherwise"
    if (w.fact or w.clock) and (w.otherwise == "unsettled") != bool(w.open_question):
        return "needs an open question exactly when otherwise is unsettled"
    if (w.check or w.outside) and w.open_question:
        return "is a check or outside way, which names no open question"
    if isinstance(w.applies_if, str) and (w.applies_if not in facts or facts[w.applies_if].type != "bool"):
        return f"applies_if names no yes/no fact of the playbook ({w.applies_if})"
    if isinstance(w.applies_if, Condition):
        if w.applies_if.fact not in facts or facts[w.applies_if.fact].type != "choice":
            return f"applies_if names no choice fact of the playbook ({w.applies_if.fact})"
        if answers_problem(facts[w.applies_if.fact], w.applies_if.equals):
            return "applies_if " + answers_problem(facts[w.applies_if.fact], w.applies_if.equals)
    if w.beside is not None and (not w.check or w.beside not in facts or facts[w.beside].type != "text"):
        return f"beside names no text fact of the playbook, or is not on a check ({w.beside})"
    if w.lease is not None and w.lease not in LeaseProfile.model_fields:
        return f"names a lease clause that is not a lease profile field ({w.lease})"
    return None


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
        if (e.type == "choice") != bool(e.choices) or (e.choices and len(set(e.choices)) != len(e.choices)):
            raise ValueError(f"element {e.id}: a choice needs its answers, each once, and only a choice has them")
    date_ids = [e.id for e in pb.spec.elements if e.type == "date"]
    for c in pb.spec.clocks:
        if c.trigger not in date_ids:
            raise ValueError(f"clock {c.id}: trigger {c.trigger} is not a date element")
        if c.shown_with and c.shown_with not in date_ids:
            raise ValueError(f"clock {c.id}: shown_with {c.shown_with} is not a date element")
        if c.count == "court_business_days" and "premises_county" not in [e.id for e in pb.spec.elements]:
            raise ValueError(f"clock {c.id}: court business days need a premises_county element")
    facts = {e.id: e for e in pb.spec.elements}
    clocks = {c.id for c in pb.spec.clocks}
    questions = {q.get("id") for q in pb.spec.open_questions if isinstance(q, dict)}
    for o in pb.spec.options:                                # every gate and step names a fact or clock it has
        for g in o.gates:
            if not g.ways:
                raise ValueError(f"option {o.id}: the gate '{g.says[:40]}' has no ways")
            for w in g.ways:
                problem = way_problem(w, facts, clocks, questions)
                if problem:
                    raise ValueError(f"option {o.id}: a way of the gate '{g.says[:40]}' {problem}")
        for s in o.steps:
            if sum([s.fact is not None, s.clock is not None, bool(s.ways)]) != 1 or (s.fact and s.fact not in facts) \
                    or (s.clock and s.clock not in clocks):
                raise ValueError(f"option {o.id}: a step needs one fact, one clock, or ways, of the playbook")
            for w in s.ways:
                problem = way_problem(w, facts, clocks, questions)
                if problem:
                    raise ValueError(f"option {o.id}: a way of the step '{s.says[:40]}' {problem}")
        if not set(o.also_open) <= questions:
            raise ValueError(f"option {o.id}: also_open names an open question the playbook lacks")
    return pb


def option_ways(o):
    """Every way of an option: its gates' and its steps'."""
    return [w for g in o.gates for w in g.ways] + [w for s in o.steps for w in s.ways]


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


def playbook_ids(pbs):
    """Every fact, clock, and open question id of these playbooks: words the model must never write (TODO item 53)."""
    return {i for pb in pbs for i in [e.id for e in pb.spec.elements] + [c.id for c in pb.spec.clocks]
            + [q.get("id") for q in pb.spec.open_questions if isinstance(q, dict)] if i}


def check_playbook(playbook, statute, ids=None):
    """Check one playbook and print a line per check. Returns the number of failures.
    Quotes: every spec quote (clocks, overrides, exclusions, each option's gates and steps) word for word in the
    section it cites, and every quotation of 20 or more characters in the guidance and open questions word for
    word in a stored section. Shape: a question for every element and an element for every question, applies_if
    naming a yes/no fact, clock and option cites among the playbook's sections, each open question's id, sections, text, and readings (two or more when given), no
    id (playbook_ids; this playbook's own when ids is None) in the model's prose, and the guidance parts the
    tool reads (postures, including notice_sufficiency)."""
    fails = 0
    quotes = []
    for c in playbook.spec.clocks:
        quotes.append((c.id, c.cite, c.quote))
        if c.consequence:
            quotes.append((c.id + " consequence", c.cite, c.consequence))
    for item in playbook.spec.lease_overrides + playbook.spec.exclusions:
        if item.get("quote"):
            quotes.append((item["cite"], item["cite"], item["quote"]))
    for o in playbook.spec.options:                          # each gate, way, and step quotes the section it rests on
        for part in o.gates + o.steps + [w for w in option_ways(o) if w.quote]:
            quotes.append((f"option {o.id}: {(part.says or '')[:40]}", part.cite, part.quote))
    for name, cite, quote in quotes:
        section = cite.split("(")[0]                    # "83.49(3)(a)" -> "83.49"
        fails += report(f"{name} {cite}", squash(quote) in squash(statute[section]))

    conditions = [c.condition for c in playbook.spec.clocks if c.condition]
    for text in prose_strings([playbook.guidance, playbook.spec.open_questions, conditions]):
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
    for o in playbook.spec.options:
        cites = [o.cite] + [part.cite for part in o.gates + o.steps] + [w.cite for w in option_ways(o) if w.cite]
        fails += report(f"option {o.id}: every cite is among the playbook's sections",
                        all(c.split("(")[0] in playbook.sections for c in cites))
        fails += report(f"option {o.id}: a way with its own quote has its own cite and says",
                        all(w.cite and w.says for w in option_ways(o) if w.quote))
    # Open questions (rule 5): each says what applies and what stays open; an open point carries two or more
    # readings, which the model gives side by side instead of settling it.
    fails += report("open questions: each has an id, sections in statutes/, and text; readings, if any, two or more",
                    all(isinstance(q, dict) and q.get("id") and q.get("text") and q.get("sections")
                        and all(s in statute for s in q["sections"])
                        and ("readings" not in q or (isinstance(q["readings"], list) and len(q["readings"]) >= 2
                                                     and all(isinstance(r, str) for r in q["readings"])))
                        for q in playbook.spec.open_questions))
    # The model copies an id it reads in prose into its replies (eval of 2026-10-02: 39 turns), so the guidance and
    # the open questions' text and readings say things in words. Keys (questions, lease_checks) may be ids.
    ids = ids or playbook_ids([playbook])
    texts = list(prose_strings(playbook.guidance)) + [q.get("text", "") for q in playbook.spec.open_questions] \
        + [r for q in playbook.spec.open_questions for r in q.get("readings", [])] \
        + [x for o in playbook.spec.options for x in [o.label] + [p.says for p in o.gates + o.steps]
           + [t for w in option_ways(o) for t in (w.says, w.when_otherwise, w.check, w.outside) if t]] + conditions
    named = sorted({w for t in texts for w in re.findall(r"\b[a-z]+(?:_[a-z]+)+\b", t) if w in ids})
    fails += report("no fact, clock, or open question id in the model's prose" + (f": {named}" if named else ""), not named)
    postures = playbook.guidance.get("postures", {})
    fails += report("guidance has lease_checks, evidence, failure_modes, and every posture",
                    all(k in playbook.guidance for k in ("lease_checks", "evidence", "failure_modes"))
                    and all(k in postures for k in ("core", "preserve", "assert", "escalate", "notice_sufficiency")))
    return fails


def check_all_playbooks():
    """Run check_playbook on every loaded playbook, then check that a fact id used by more than one playbook
    has the same type and question in each. Called by smoke.py, not at import. Returns the number of failures."""
    fails = 0
    ids = playbook_ids(playbooks.values())
    for issue, pb in playbooks.items():
        print(f"--- {issue}")
        fails += check_playbook(pb, statute, ids)
    print("--- facts shared across playbooks")
    for fact_id in sorted({e.id for pb in playbooks.values() for e in pb.spec.elements}):
        uses = [(pb.issue, e.type, pb.guidance["questions"].get(fact_id), tuple(e.choices or ()))
                for pb in playbooks.values() for e in pb.spec.elements if e.id == fact_id]
        if len(uses) > 1:
            fails += report(f"{fact_id}: same type, question, and answers in {[u[0] for u in uses]}",
                            all(len({u[k] for u in uses}) == 1 for k in (1, 2, 3)))
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


# The lease clause a fact's question is about, from a gate's way that the fact decides and that names one (TODO item
# 81): the sheet shows the clause, as the tool read it, beside the question (whether the lease promises the repair,
# beside the lease's repairs clause), or says the tool has not read it.
fact_lease = {w.fact: w.lease for pb in playbooks.values() for o in pb.spec.options for w in option_ways(o)
              if w.fact and w.lease}


def issue_menu():
    """Every label classify can pick, with the situation it covers: a playbook's description, and "other" for
    none of them. What the classifier reads instead of bare label names."""
    return {label: playbooks[label].description if label in playbooks else "None of the situations above."
            for label in ISSUE_LABELS}
