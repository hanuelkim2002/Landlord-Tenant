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
from corpus import playbooks
from deterministic import check_elements
from lease import LeaseProfile

# The test matter. "t-test" is the test tenant's id; a real tenant gets a random one from new_tenant_id().
matter = {"id": "test-001", "tenant": "t-test", "issues": [], "proposed_issues": [], "rejected_issues": [],
          "facts": {}, "proposed": {}}
profile = None          # the LeaseProfile for this matter. Set by run.py after intake or load.
session = None          # the open session's id, or None. Set by start_session, cleared by end_session.


# ---- Where a matter lives: matters/<tenant id>/<matter id>/. The only function that knows this layout.

def matter_dir():
    return MATTERS / matter["tenant"] / matter["id"]


def new_tenant_id():
    """A random id like 't-3f9a2c'. Never built from a name or an email, so no folder name says who it is."""
    return "t-" + secrets.token_hex(3)


def new_matter_id(tenant_id):
    """The next matter id for this tenant: 'm-001', then 'm-002', counting the folders already there."""
    existing = list((MATTERS / tenant_id).glob("m-*")) if (MATTERS / tenant_id).exists() else []
    return f"m-{len(existing) + 1:03d}"


# ---- Finding and opening a saved matter.

def list_matters():
    """Every saved matter, as {"tenant", "id", "issues"}. Nothing else is read out, so a listing never shows
    a description or a fact."""
    found = []
    for path in sorted(MATTERS.glob("*/*/matter.json")):
        saved = json.loads(path.read_text())
        found.append({"tenant": saved["tenant"], "id": saved["id"], "issues": saved["issues"]})
    return found


def load_matter(tenant_id, matter_id):
    """Open a saved matter: replace `matter` with its matter.json and `profile` with its lease profile (None if
    the lease has not been read yet). This is why every module uses record.matter, never its own copy."""
    global matter, profile
    folder = MATTERS / tenant_id / matter_id
    matter = json.loads((folder / "matter.json").read_text())
    matter.setdefault("proposed_issues", [])            # matters saved before issues were confirmed
    matter.setdefault("rejected_issues", [])
    profile_path = folder / "lease_profile.json"
    profile = LeaseProfile.model_validate_json(profile_path.read_text()) if profile_path.exists() else None
    return matter


def new_matter(tenant_id):
    """Start an empty matter for this tenant with the next matter id, and clear `profile`. Nothing is written
    until the lease is read or the matter is saved."""
    global matter, profile
    matter = {"id": new_matter_id(tenant_id), "tenant": tenant_id, "issues": [], "proposed_issues": [],
              "rejected_issues": [], "facts": {}, "proposed": {}}
    profile = None
    return matter


# ---- Confirm Fact: the only code that writes a confirmed fact.

def confirm_fact(fact_id, value, confirmed_in):
    """Move one fact into matter["facts"] and log it. confirmed_in: where the tenant confirmed it; "sheet"
    (the intake sheet) is the only caller now. The event keeps what was proposed and on what words."""
    was = matter["proposed"].pop(fact_id, {"value": None, "how": "asked", "basis": None})
    renewed = fact_id not in matter["facts"] or matter["facts"][fact_id] != value     # new information
    matter["facts"][fact_id] = value
    append_event("fact_confirmed", id=fact_id, value=value, how=was["how"], basis=was["basis"],
                 proposed_value=was["value"], confirmed_in=confirmed_in)
    add_related_issues(fact_id if renewed else None)   # this fact may suggest another issue (related_issues)
    prune_proposals()                          # a "no" here can make another suggestion moot


# ---- Issues. The classifier and related rules only suggest an issue (add_issues); the tenant confirms or
# rejects it on the intake sheet (confirm_issue, reject_issue) and can drop an active one in the chat. Every
# step is logged; nothing is taken out of the history.

def add_issues(issues, source, because):
    """Suggest each issue that is not already active or suggested. source: "classify" (from the tenant's
    description or update) or "related" (a related_issues rule); because: what brought it in, in words. An
    issue with no playbook ("other") has nothing to confirm or ask, so it is recorded at once (issue_added).
    A new suggestion clears an earlier rejection: the tenant is asked again. Returns the issues it took in."""
    new = []
    for issue in issues:
        if issue in matter["issues"] or any(p["issue"] == issue for p in matter["proposed_issues"]):
            continue
        if issue not in playbooks:
            matter["issues"].append(issue)
            append_event("issue_added", issue=issue, source=source, because=because)
        else:
            matter["proposed_issues"].append({"issue": issue, "source": source, "because": because})
            if issue in matter["rejected_issues"]:
                matter["rejected_issues"].remove(issue)
            append_event("issue_proposed", issue=issue, source=source, because=because)
        new.append(issue)
    return new


def confirm_issue(issue):
    """The tenant said yes on the sheet: the issue becomes active and its own related rules are checked."""
    matter["proposed_issues"] = [p for p in matter["proposed_issues"] if p["issue"] != issue]
    matter["issues"].append(issue)
    append_event("issue_confirmed", issue=issue)
    add_related_issues()


def reject_issue(issue, kind="issue_rejected"):
    """The tenant said no to a suggested issue (issue_rejected, on the sheet) or dropped an active one
    (issue_dropped, in the chat). Its questions stop and its pending suggestions go. A related rule does not
    suggest it again unless the rule's fact is confirmed anew; a later classification of the tenant's words
    does. Facts already confirmed stay in the matter."""
    matter["proposed_issues"] = [p for p in matter["proposed_issues"] if p["issue"] != issue]
    if issue in matter["issues"]:
        matter["issues"].remove(issue)
    if issue not in matter["rejected_issues"]:
        matter["rejected_issues"].append(issue)
    append_event(kind, issue=issue)
    prune_proposals()


def add_related_issues(renewed_fact=None):
    """Suggest every issue an active playbook's related_issues rule points to, once the rule's fact is confirmed
    with the rule's value. An issue the tenant rejected or dropped is skipped, unless renewed_fact is the
    rule's fact, just confirmed with a new value. Returns the issues suggested."""
    added = []
    for pb in active_playbooks():
        for rel in pb.spec.related_issues:
            fact = rel.when.fact
            if fact not in matter["facts"] or matter["facts"][fact] != rel.when.equals:
                continue
            if rel.issue in matter["rejected_issues"] and fact != renewed_fact:
                continue
            added += add_issues([rel.issue], "related", f"{fact} is {json.dumps(rel.when.equals)}")
    return added


def prune_proposals():
    """Drop suggestions that can never be asked: every element with that id either takes its value from the
    lease, depends on a fact the tenant confirmed as no (with no change to it pending), or no issue of the
    matter, active or suggested, asks for it. A suggestion that depends on a fact still open is kept, since that fact may yet be yes. Nothing is logged: suggestions
    are not history, and the tenant's words they came from stay in the description or the update."""
    for fact_id in list(matter["proposed"]):
        uses = [e for pb in candidate_playbooks() for e in pb.spec.elements if e.id == fact_id]
        if all(_cannot_be_asked(e) for e in uses):
            del matter["proposed"][fact_id]


def _cannot_be_asked(e):
    """True if this element will never show a suggestion: the lease comes first in its sources and has the
    clause, or the fact it depends on (applies_if) is confirmed as not true with no change to it pending."""
    for src in e.source:
        if src == "user":
            break
        if profile is not None and getattr(profile, src.replace("lease_profile.", "")).present:
            return True
    return (e.applies_if in matter["facts"] and not matter["facts"][e.applies_if]
            and e.applies_if not in matter["proposed"])     # a pending change could still make it true


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


def active_playbooks():
    """The loaded playbooks for this matter's issues, in the order classify listed them."""
    return [playbooks[i] for i in matter["issues"] if i in playbooks]


def candidate_playbooks():
    """The active playbooks, then those of suggested issues: the ones whose facts fill_facts may suggest and
    prune_proposals keeps, since a suggested issue may yet be confirmed."""
    return active_playbooks() + [playbooks[p["issue"]] for p in matter["proposed_issues"] if p["issue"] in playbooks]


def element_status():
    """Element rows for every active playbook, keyed by issue."""
    return {pb.issue: check_elements(pb, profile, matter["facts"], matter["proposed"]) for pb in active_playbooks()}
