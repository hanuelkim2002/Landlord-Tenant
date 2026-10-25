"""The record of a matter: its folder matters/<tenant id>/<matter id>/, its current state in matter.json, and its
history in events.jsonl, which is only ever added to. A matter is a plain dict passed to these functions.
confirm_fact is the only code that confirms a fact. The timeline's lines live in matter.json too, and every
version of a line is in the history.
"""
import json
import re
from datetime import date, datetime

import config

NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")              # tenant ids and fact names: lowercase, short, no spaces


def now():
    """The time, to the second, for the record."""
    return datetime.now().isoformat(timespec="seconds")


def folder(m):
    """The matter's folder."""
    return config.MATTERS / m["tenant"] / m["matter"]


def save(m):
    """Write the matter's current state to matter.json."""
    (folder(m) / "matter.json").write_text(json.dumps(m, indent=1))


def log(m, kind, **data):
    """Add one event to the matter's history. Events are never changed or deleted."""
    with (folder(m) / "events.jsonl").open("a") as f:
        f.write(json.dumps({"time": now(), "kind": kind, **data}) + "\n")


def new_matter(tenant, description):
    """Start a matter for a tenant: its folder, its state, and the first event. Returns the matter."""
    if not NAME.match(tenant):
        raise ValueError("A tenant id is lowercase letters, digits, - or _, up to 40 characters.")
    m = {"tenant": tenant, "matter": datetime.now().strftime("m-%Y%m%d-%H%M%S"), "opened": now(),
         "description": description, "skills": [], "pending": {}, "confirmed": {}, "lines": {}}
    folder(m).mkdir(parents=True)
    save(m)
    log(m, "matter_opened", description=description)
    return m


def load(tenant, matter):
    """Open a saved matter."""
    m = json.loads((config.MATTERS / tenant / matter / "matter.json").read_text())
    m.setdefault("lines", {})                                 # matters saved before the timeline have none
    return m


def saved_matters():
    """Every saved matter, newest first, as (tenant, matter id, description)."""
    found = [load(p.parent.parent.name, p.parent.name) for p in config.MATTERS.glob("*/*/matter.json")]
    found.sort(key=lambda m: m["opened"], reverse=True)
    return [(m["tenant"], m["matter"], m["description"]) for m in found]


def events(m):
    """The matter's history, oldest first."""
    path = folder(m) / "events.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def add_message(m, role, text, checks=None):
    """Record one chat message (the tenant's or the tool's), with the checks shown under a reply."""
    log(m, "message", role=role, text=text, checks=checks)


def chat(m):
    """The chat so far, from the history: [{"role", "text", "checks"}], so a saved matter reopens with its chat."""
    return [{"role": e["role"], "text": e["text"], "checks": e.get("checks")} for e in events(m) if e["kind"] == "message"]


def add_skill(m, name):
    """Mark a skill as loaded for this matter, so its instructions stay in the prompt."""
    if name not in m["skills"]:
        m["skills"].append(name)
        save(m)
        log(m, "skill_loaded", skill=name)


def note_fact(m, name, value, tenant_words):
    """Save what the tenant said as a pending fact. It does not count until the tenant confirms it."""
    if not NAME.match(name):
        raise ValueError("A fact name is lowercase words joined by underscores, up to 40 characters.")
    m["pending"][name] = {"value": str(value), "tenant_words": tenant_words, "noted": now()}
    save(m)
    log(m, "fact_noted", fact=name, value=str(value), tenant_words=tenant_words)


def confirm_fact(m, name, value):
    """The tenant confirms a pending fact, with the value as noted or as they corrected it. The only door into
    the confirmed facts."""
    noted = m["pending"].pop(name)
    m["confirmed"][name] = {"value": value, "tenant_words": noted["tenant_words"], "confirmed": now()}
    save(m)
    log(m, "fact_confirmed", fact=name, value=value, noted_value=noted["value"])


def confirmed_facts(m):
    """The confirmed facts, name to value."""
    return {name: fact["value"] for name, fact in m["confirmed"].items()}


def save_line(m, number, date, what, open):
    """Save one line of the timeline: number 0 adds a new line, a line's number saves a new version of it.
    Returns the line's number."""
    if not what.strip():
        raise ValueError("A line needs what happened, in plain words.")
    if number == 0:
        number = len(m["lines"]) + 1                          # lines are never removed, so this counts up
    elif str(number) not in m["lines"]:
        raise ValueError(f"No line {number}. The lines: {', '.join(m['lines']) or 'none yet'}.")
    m["lines"][str(number)] = {"date": date, "what": what, "open": open, "saved": now()}
    save(m)
    log(m, "line_saved", number=number, date=date, what=what, open=open)
    return number


def since_last_visit(m, today=None):
    """After a gap of a day or more: the days since the last message, counted by code, and the facts confirmed
    since then. None on the same day, or when there is no message yet."""
    history = events(m)
    messages = [e for e in history if e["kind"] == "message"]
    if not messages:
        return None
    last = messages[-1]["time"]
    today = today or date.today()                             # looked up here, so a test can stand in another day
    days = (today - date.fromisoformat(last[:10])).days      # calendar days: 11 pm to the next morning is one
    if days < 1:
        return None
    changed = [{"fact": e["fact"], "value": e["value"], "noted_value": e["noted_value"]}
               for e in history if e["kind"] == "fact_confirmed" and e["time"] > last]
    return {"days": days, "changed": changed}
