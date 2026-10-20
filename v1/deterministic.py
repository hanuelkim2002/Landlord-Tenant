"""Deterministic Layer: date arithmetic (no model)."""
from datetime import date, timedelta

from calendars import court_calendar, holidays_in


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
