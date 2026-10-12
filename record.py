"""Matter Record: the shared state and the only history the tool keeps.

matter.json holds current state only. events.jsonl is the history: one line per event, never edited, never deleted.

One convention for shared state: `matter` and `profile` live here, and every other module reaches them as
record.matter and record.profile (never `from record import matter`). That way, when a matter is loaded or
switched, every module sees the same object.
"""
import json
import secrets
from datetime import datetime

from langchain_core.utils.uuid import uuid7

from config import MATTERS
from lease import LeaseProfile
from skills import clock_facts as skill_clock_facts, skills

# The test matter. "t-test" is the test tenant's id; a real tenant gets a random one from new_tenant_id().
matter = {"id": "test-001", "tenant": "t-test", "skills": [], "facts": {}, "proposed": {}}
profile = None          # the LeaseProfile for this matter. Set by agent.read_lease for a new matter, or by load_matter.
session = None          # the open session's id, or None. Set by start_session, cleared by end_session.


# ---- Where a matter lives: matters/<tenant id>/<matter id>/. The only function that knows this layout.

def matter_dir():
    return MATTERS / matter["tenant"] / matter["id"]


def lease_pages():
    """The open matter's lease text, page by page, as lease.ingest_pdf stored it (pages.json), or [] when none is
    stored. Read by the lease search and the words a reply cites."""
    path = matter_dir() / "pages.json"
    return json.loads(path.read_text()) if path.exists() else []


def new_tenant_id():
    """A random id like 't-3f9a2c'. Never built from a name or an email, so no folder name says who it is."""
    return "t-" + secrets.token_hex(3)


def new_matter_id(tenant_id):
    """The next matter id for this tenant: 'm-001', then 'm-002', counting the folders already there."""
    existing = list((MATTERS / tenant_id).glob("m-*")) if (MATTERS / tenant_id).exists() else []
    return f"m-{len(existing) + 1:03d}"


# ---- Finding and opening a saved matter.

def list_matters():
    """Every saved matter, as {"tenant", "id", "skills"}. Nothing else is read out, so a listing never shows
    a description or a fact."""
    found = []
    for path in sorted(MATTERS.glob("*/*/matter.json")):
        saved = with_skills(json.loads(path.read_text()))
        found.append({"tenant": saved["tenant"], "id": saved["id"], "skills": saved["skills"]})
    return found


def with_skills(saved):
    """A matter.json as the code reads it. One saved before skills has `issues`, `proposed_issues`, and
    `rejected_issues` instead of `skills`: each issue that is the name of a skill becomes a loaded skill (the names
    are the same), and the three old keys are dropped. The file is not rewritten until the matter is next saved."""
    if "skills" not in saved:
        saved["skills"] = [name for name in saved.get("issues", []) if name in skills]
    for old in ("issues", "proposed_issues", "rejected_issues"):
        saved.pop(old, None)
    return saved


def load_matter(tenant_id, matter_id):
    """Open a saved matter: replace `matter` with its matter.json (with_skills) and `profile` with its lease profile
    (None if the lease has not been read yet). This is why every module uses record.matter, never its own copy."""
    global matter, profile
    folder = MATTERS / tenant_id / matter_id
    matter = with_skills(json.loads((folder / "matter.json").read_text()))
    profile_path = folder / "lease_profile.json"
    profile = LeaseProfile.model_validate_json(profile_path.read_text()) if profile_path.exists() else None
    return matter


def new_matter(tenant_id):
    """Start an empty matter for this tenant with the next matter id, and clear `profile`. Nothing is written
    until the lease is read or the matter is saved."""
    global matter, profile
    matter = {"id": new_matter_id(tenant_id), "tenant": tenant_id, "skills": [], "facts": {}, "proposed": {}}
    profile = None
    return matter


# ---- Confirm Fact: the only code that writes a confirmed fact.

def confirm_fact(fact_id, value, confirmed_in):
    """Move one fact into matter["facts"] and log it. confirmed_in: where the tenant confirmed it; "sheet"
    (the confirmation after a turn, sheet.save_answer) is the only caller. The event keeps what was proposed and on
    what words. A proposal stays in matter["proposed"] until this runs for its id."""
    was = matter["proposed"].pop(fact_id, {"value": None, "how": "asked", "basis": None})
    matter["facts"][fact_id] = value
    append_event("fact_confirmed", id=fact_id, value=value, how=was["how"], basis=was["basis"],
                 proposed_value=was["value"], confirmed_in=confirmed_in)


# ---- Skills. The model loads a skill with the load_skill tool, which calls add_skill: the only code that writes
# matter["skills"]. Every load is logged; nothing is taken out of the history.

def add_skill(name):
    """Load a skill into the matter: append its name, save matter.json, and log a skill_loaded event. The caller
    (tools.load_skill) has checked that the name is a skill and not loaded yet. Its instructions and statute sections
    enter the system prompt from the next model call, for the rest of the matter and on a return visit."""
    matter["skills"].append(name)
    save(matter)
    append_event("skill_loaded", skill=name)


def save(matter):
    """matter.json holds current state only. History lives in events.jsonl."""
    folder = matter_dir()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "matter.json").write_text(json.dumps(matter, indent=2, default=str))


def append_event(kind, **data):
    """One line to events.jsonl. Never edited, never deleted. The only history the tool keeps.
    While a session is open, the event carries its id, so every entry can be traced to the visit it came from."""
    folder = matter_dir()
    folder.mkdir(parents=True, exist_ok=True)
    event = {"when": datetime.now().isoformat(timespec="seconds"), "kind": kind}
    if session:
        event["session"] = session
    event.update(data)
    with open(folder / "events.jsonl", "a") as f:
        f.write(json.dumps(event, default=str) + "\n")


# ---- Sessions: one visit to one matter, from the moment the matter is chosen to the end of the chat.

def start_session(how):
    """Open a session on the current matter and log it. how: "new" or "existing". Returns the session id."""
    global session
    session = str(uuid7())                  # time-ordered, so session ids sort by when they started
    append_event("session_started", how=how)
    return session


def end_session():
    """Log the end of the open session and close it. A crash leaves a start with no end, which is the truth."""
    global session
    append_event("session_ended")
    session = None


def append_transcript(entry):
    """One line to sessions/<session id>.jsonl: what was said in this session. Outside events.jsonl, so the
    evidentiary log stays facts, messages, files, and letters. Does nothing when no session is open."""
    if not session:
        return
    folder = matter_dir() / "sessions"
    folder.mkdir(parents=True, exist_ok=True)
    line = {"when": datetime.now().isoformat(timespec="seconds"), **entry}
    with open(folder / f"{session}.jsonl", "a") as f:
        f.write(json.dumps(line, default=str) + "\n")


def tenant_words():
    """Everything the tenant typed in the open session's chat, from the transcript. Empty with no session."""
    if not session:
        return []
    path = matter_dir() / "sessions" / f"{session}.jsonl"
    if not path.exists():
        return []
    lines = [json.loads(line) for line in path.read_text().splitlines()]
    return [line["text"] for line in lines if line["role"] == "tenant"]


def read_events():
    path = matter_dir() / "events.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines()]


def active_skills():
    """The Skill objects for this matter's loaded skills, in the order they were loaded."""
    return [skills[name] for name in matter["skills"] if name in skills]


def clock_facts():
    """The facts the loaded skills' clocks count from, as {fact id: type}, merged across the skills (skills.clock_facts of
    each: "date", "bool", or "county"). propose_facts parses a proposal for one of these by its type; skills.type_conflicts
    (run by smoke.py) keeps a fact id from being typed two ways."""
    return {fact: kind for skill in active_skills() for fact, kind in skill_clock_facts(skill).items()}
