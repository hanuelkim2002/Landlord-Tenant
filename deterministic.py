"""Deterministic Layer: date arithmetic and the options layer (no model)."""
from datetime import date, timedelta

from calendars import court_calendar, holidays_in
from lease import LABELS, lease_cite
from skills import skills


# ---- Deadlines: the only date arithmetic in the project.

def court_days(start, days, direction, county):
    """Count court business days from start: one day at a time, the start day not counted, skipping Saturdays,
    Sundays, and every holiday in the calendar of the circuit that includes the county. Returns (date, the
    counting line to show with it), or (None, why it cannot be computed): no calendar for the county, or a day
    in a year with no memorandum loaded. Never guesses a holiday."""
    cal = court_calendar(county)
    if cal is None:
        return None, f"not computed: no court holiday calendar for {county + ' County' if county else 'the rental county'}"
    holidays = holidays_in(cal)
    step = timedelta(days=1 if direction == "after" else -1)
    day, counted, years = start, 0, set()
    while counted < days:
        day += step
        if str(day.year) not in cal["years"]:
            return None, f"not computed: no {cal['circuit']} holiday memorandum loaded for {day.year}"
        years.add(day.year)
        if day.weekday() < 5 and day not in holidays:      # Monday to Friday, not a court holiday
            counted += 1
    used = ", ".join(f"{y} (issued {cal['years'][str(y)]['issued_on']})" for y in sorted(years))
    return day, (f"court business days, start day not counted, Saturdays, Sundays, and every holiday in the "
                 f"{cal['circuit']} Chief Judge's memorandum skipped ({used}). ASSUMPTION: the counting rule and "
                 f"which holidays count are open questions; show this line with the date.")


def compute_deadlines(skill, facts, today):
    """Date arithmetic only. Dates in facts are strings like '2026-07-31'. One row per clock of the skill that applies
    (its applies_if fact confirmed true, or none): the deadline, or why there is none yet."""
    out = []
    for c in skill.clocks:
        # Skip clocks that don't apply: their applies_if fact is not a confirmed truthy one.
        if c.applies_if and not facts.get(c.applies_if):
            continue
        # Can't compute without the trigger date. Say which one is needed.
        if c.trigger not in facts:
            out.append({"clock": c.id, "status": "need date for " + c.trigger})
            continue

        # Turn "2026-07-31" into a real date, then add or subtract the day count.
        start = date.fromisoformat(facts[c.trigger])
        counting = skill.counting["convention"]
        if c.count == "court_business_days":
            deadline, counting = court_days(start, c.days, c.direction, facts.get("premises_county"))
            if deadline is None:                           # no calendar for the county or the year: say so
                out.append({"clock": c.id, "status": counting})
                continue
        elif c.direction == "after":
            deadline = start + timedelta(days=c.days)
        else:
            deadline = start - timedelta(days=c.days)

        # One result per clock, carrying the cite and the counting assumption
        # so whoever reads it can see where the number came from.
        row = {
            "clock": c.id,
            "actor": c.actor,
            "from": f"{c.trigger} {start}",
            "rule": f"{c.days} {'court business days' if c.count == 'court_business_days' else 'days'} {c.direction}",
            "deadline": deadline,
            "status": "passed" if deadline < today else "upcoming",
            "cite": c.cite,
            "counting": counting,
        }
        if c.shown_with and c.shown_with in facts:          # e.g. the date the notice itself states, beside ours
            row["shown_with"] = f"{c.shown_with} {facts[c.shown_with]}"
        if c.condition:                                     # what the date counts only if, which the tool does not decide
            row["condition"] = " ".join(c.condition.split())
        out.append(row)
    return out


def matter_deadlines(loaded, facts, today):
    """compute_deadlines for every skill in `loaded`, with a deadline two skills share listed once and tagged with every
    skill that has it. Shared means the same clock id, cite, and result (date and status); two different rules that
    happen to share an id stay separate. Each row carries "skills", a list of skill names."""
    merged = []
    for skill in loaded:
        for d in compute_deadlines(skill, facts, today):
            same = next((m for m in merged if m["clock"] == d["clock"] and m.get("cite") == d.get("cite")
                         and m.get("deadline") == d.get("deadline") and m["status"] == d["status"]), None)
            if same:
                same["skills"].append(skill.name)
            else:
                merged.append({**d, "skills": [skill.name]})
    return merged


# ---- Options: whether each thing the statute lets the tenant do is open on the confirmed facts, and how far its
# steps have got (TODO item 72). A reply had told the tenant how to end the lease over an AC not repaired, and only
# the next reply said an AC may not be a duty 83.56(1) reaches; so the program decides openness first.
#
# What the tool knows (TODO item 81, the author's decision of 2026-10-04): each condition (gate) is met through one
# of its ways (a confirmed fact, a clock, a lease clause, something the tenant can check, law outside the tool), and
# the program says which of five things it is: known (met, not met, or not met yet), something the tenant can tell
# the tool (a fact the tenant can state), something the tenant can check (a part of the lease the tool has not read, a
# local code, a document), not settled (an open question), or outside the tool. The model said "the lease does not
# mention air conditioning" from a lease it had not read whole, and called ending the lease over an AC not settled
# on the statute alone while the lease promised the repair.

# The state of a way or a gate, best first: a gate takes the best state among its ways, since any way meets it.
STATES = ["met", "tell", "check", "not settled", "outside", "not met yet", "not met"]
# What each state means for the condition, and what the tool knows of it, in words for the prompt.
STATUS = {"met": "met", "not met": "not met", "not met yet": "not met yet", "tell": "not known yet",
          "check": "not known yet", "not settled": "not settled", "outside": "outside the tool"}
KNOWLEDGE = {"met": "known", "not met": "known", "not met yet": "known", "tell": "the tenant can tell the tool",
             "check": "the tenant can check", "not settled": "not settled", "outside": "outside the tool"}


def lease_note(field, profile):
    """Whether the tool read the lease clause a way rests on, in words: read (with the cite to use), read and found
    no such clause, or not read (a profile read before the clause was added, or no profile)."""
    clause = getattr(profile, field, None) if profile is not None else None
    if clause is None:
        return f"the tool has not read the part of the lease on {LABELS[field]}"
    if not clause.present:
        return f"the tool's reading of the lease found no clause on {LABELS[field]}"
    return f"the tool has read the lease's clause on {LABELS[field]}, {lease_cite(clause)}"


# Why a way is not met when it is for a case the record does not show (its applies_if does not hold, or its fact's
# question is never asked); options_status leaves such a way out of a condition's list.
NOT_APPLY = "it does not apply on the confirmed facts"


def matches(value, equals):
    """Whether a confirmed value is the one a way or a condition asks for: one of them when it lists several (a
    choice's answers), else that one."""
    return value in equals if isinstance(equals, list) else value == equals


def asked_never(fact, playbook, facts):
    """True when a fact's own question does not apply on the confirmed facts (its applies_if fact is confirmed
    false), so it is never asked."""
    element = next(e for e in playbook.spec.elements if e.id == fact)
    return bool(element.applies_if and element.applies_if in facts and not facts[element.applies_if])


def holds(applies_if, facts):
    """Whether a way's applies_if holds on the confirmed facts: True, False, or None while its fact is not
    confirmed. A fact id alone is a yes/no fact confirmed true; {fact, equals} is a choice fact confirmed with one of
    the answers listed."""
    fact = applies_if if isinstance(applies_if, str) else applies_if.fact
    if fact not in facts:
        return None
    return bool(facts[fact]) if isinstance(applies_if, str) else matches(facts[fact], applies_if.equals)


def way_state(w, playbook, facts, clock_rows, profile):
    """One way's state (STATES) and why, in plain words: a fact or clock confirmed one way or the other is known (or
    not settled, through its open question); a fact not confirmed is one the tenant can tell the tool,
    or can check when it rests on a lease clause the tool has not read; a clock waits for its start date (the tenant
    can tell it) or cannot be counted (outside the tool); a check is the tenant's to check, with the tenant's own
    words when it names a fact to set beside the statute (beside); outside is outside; an open question alone is not
    settled. A way with applies_if is not met when it does not hold on the confirmed facts, and the tenant's to tell
    while its fact is not confirmed."""
    questions = playbook.guidance["questions"]
    note = lease_note(w.lease, profile) if w.lease else ""
    otherwise = {"closed": "not met", "unsettled": "not settled", "later": "not met yet"}[w.otherwise]
    if w.applies_if is not None:                               # a way for a case the record may not show yet
        fact = w.applies_if if isinstance(w.applies_if, str) else w.applies_if.fact
        held = holds(w.applies_if, facts)
        if held is False or asked_never(fact, playbook, facts):       # its question is never asked: an answer kept
            return "not met", NOT_APPLY                                # from before does not count
        if held is None:
            return "tell", f"ask the tenant: {questions[fact]}"
    if not (w.fact or w.clock or w.check or w.outside):        # an open question alone decides it
        text = next(q["text"] for q in playbook.spec.open_questions if q.get("id") == w.open_question)
        return "not settled", "the statute does not settle it: " + " ".join(text.split()).split(". ")[0] + "."
    if w.check:
        words = f'; your words, as you gave them: "{" ".join(str(facts[w.beside]).split())}"' \
            if w.beside and w.beside in facts else ""
        return "check", " ".join(w.check.split()) + (f"; {note}" if note else "") + words
    if w.outside:
        return "outside", " ".join(w.outside.split())
    if w.fact:
        if asked_never(w.fact, playbook, facts):
            return "not met", NOT_APPLY                     # a question never asked
        if w.fact in facts:
            return ("met", "") if matches(facts[w.fact], w.equals) else (otherwise, " ".join(w.when_otherwise.split()))
        if w.lease and (profile is None or getattr(profile, w.lease, None) is None):     # a part of the lease not read
            return "check", f"{note}, so the tenant can look there; ask the tenant: {questions[w.fact]}"
        return "tell", f"ask the tenant: {questions[w.fact]}" + (f"; {note}" if note else "")
    row = clock_rows.get(w.clock)
    clock = next(c for c in playbook.spec.clocks if c.id == w.clock)
    if row is None and clock.applies_if in facts:              # the clock does not apply on the confirmed facts
        return "not met", "the period does not apply on the confirmed facts"
    if row is None or row["status"].startswith("need date"):   # its start date (or applies_if fact) not confirmed
        return "tell", f"ask the tenant: {questions[clock.trigger if row is not None else clock.applies_if]}"
    if row["status"].startswith("not computed"):
        return "outside", row["status"]
    return ("met", "") if row["status"] == (w.equals or "passed") else (otherwise, " ".join(w.when_otherwise.split()))


def option_status(states):
    """An option's status from its gates' states: closed when one is not met, else not known yet while one is the
    tenant's to tell or check, else not settled, outside the tool, not open yet, or open."""
    for state, status in (("not met", "closed"), ("tell", "not known yet"), ("check", "not known yet"),
                          ("not settled", "not settled"), ("outside", "outside the tool"), ("not met yet", "not open yet")):
        if state in states:
            return status
    return "open"


# What a step's ways make of it (TODO items 86 and 90 to 92): done through a way met, the tenant's to check through a
# check, not settled through an open question; any other state leaves it to do.
STEP_STATUS = {"met": "done", "check": "the tenant can check", "not settled": "not settled"}


def step_status(s, playbook, facts, clock_rows, profile):
    """One step's status and why: through its ways, the best of them (STEP_STATUS), with why unless it is to do; a
    clock's step "done" once the date has passed, "waiting" while it is upcoming; a fact's step "done" when the fact is
    confirmed with its value; "to do" otherwise."""
    if s.ways:
        state, why = min((way_state(w, playbook, facts, clock_rows, profile) for w in s.ways),
                         key=lambda x: STATES.index(x[0]))
        status = STEP_STATUS.get(state, "to do")
        return status, (why if status != "to do" else "")
    if s.clock:
        return {"passed": "done", "upcoming": "waiting"}.get(clock_rows.get(s.clock, {}).get("status"), "to do"), ""
    return ("done" if s.fact in facts and matches(facts[s.fact], s.equals) else "to do"), ""


def listed(playbook, facts):
    """The confirmed facts with any answer a choice fact does not list left out: an answer kept from before its question
    was a choice (claim_delivery was words until 2026-10-08), which no condition reads. (TRANSITION, with the options
    layer: TODO item 113 removes it.)"""
    choices = {e.id: e.choices for e in playbook.spec.elements if e.type == "choice"}
    return {k: v for k, v in facts.items() if k not in choices or v in choices[k]}


def check_options(playbook, facts, today, profile=None):
    """Each option of the playbook with its status, from the confirmed facts, the clocks, and the lease profile only
    (option_status: open, closed, not known yet, not settled, outside the tool, or not open yet). Each gate takes the best
    state among its ways (STATES): its status and what the tool knows of it (STATUS, KNOWLEDGE), why, its ways with
    theirs, and, while it is not met, if_met: what the option's status would be were it met (were it not met, the
    option is closed). Each step (step_status) is "done", "waiting" (its clock's date upcoming), "the tenant can check",
    "not settled", or "to do", with why when it says more; a clock's step whose date has passed while a step above it is
    not done is "passed", not done: the period counts only if the steps above are done (a notice whose words the tenant
    checks). Returns [{"option", "label", "cite", "status", "gates", "steps", "also_open"}]."""
    facts = listed(playbook, facts)                       # an answer its choice does not list decides nothing
    # TRANSITION, until TODO item 113: a playbook's clocks are the clocks of the skill with its name
    clock_rows = {row["clock"]: row for row in compute_deadlines(skills[playbook.issue], facts, today)}
    results = []
    for o in playbook.spec.options:
        gates = []
        for g in o.gates:
            ways = []
            for w in g.ways:
                state, why = way_state(w, playbook, facts, clock_rows, profile)
                ways.append({"says": w.says or g.says, "cite": w.cite or g.cite, "state": state, "status": STATUS[state],
                             "knowledge": KNOWLEDGE[state], **({"why": why} if why else {})})
            best = min(ways, key=lambda x: STATES.index(x["state"]))
            gates.append({"says": g.says, "cite": g.cite, "state": best["state"], "status": best["status"],
                          "knowledge": best["knowledge"], **({"why": best["why"]} if "why" in best else {}),
                          "ways": ways})
        for i, gate in enumerate(gates):                    # what the option would be were this condition met
            if gate["state"] != "met":
                gate["if_met"] = option_status([x["state"] for j, x in enumerate(gates) if j != i])
        steps = []
        for s in o.steps:
            status, why = step_status(s, playbook, facts, clock_rows, profile)
            if s.clock and status in ("done", "waiting") and any(x["status"] != "done" for x in steps):
                status = "passed" if status == "done" else status          # counts only from steps that hold
                why = "counts only if the steps above are done"
            steps.append({"says": s.says, "cite": s.cite, "status": status, **({"why": why} if why else {})})
        results.append({"option": o.id, "label": o.label, "cite": o.cite,
                        "status": option_status([gate["state"] for gate in gates]), "gates": gates,
                        "steps": steps, "also_open": list(o.also_open)})
    return results
