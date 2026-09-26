"""Matter Record: the shared state and the only history the tool keeps.

matter.json holds current state only. events.jsonl is the history: one line per event, never edited, never deleted.

One convention for shared state: `matter` and `profile` live here, and every other module reaches them as
record.matter and record.profile (never `from record import matter`). That way, when a matter is loaded or
switched, every module sees the same object.
"""
import json
import secrets
from datetime import datetime

from config import MATTERS
from corpus import playbooks
from deterministic import check_elements
from lease import LeaseProfile

# The test matter. "t-test" is the test tenant's id; a real tenant gets a random one from new_tenant_id().
matter = {"id": "test-001", "tenant": "t-test", "issues": [], "facts": {}, "proposed": {}}
profile = None          # the LeaseProfile for this matter. Set by run.py after intake or load.


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
    profile_path = folder / "lease_profile.json"
    profile = LeaseProfile.model_validate_json(profile_path.read_text()) if profile_path.exists() else None
    return matter


def new_matter(tenant_id):
    """Start an empty matter for this tenant with the next matter id, and clear `profile`. Nothing is written
    until the lease is read or the matter is saved."""
    global matter, profile
    matter = {"id": new_matter_id(tenant_id), "tenant": tenant_id, "issues": [], "facts": {}, "proposed": {}}
    profile = None
    return matter


def save(matter):
    """matter.json holds current state only. History lives in events.jsonl."""
    folder = matter_dir()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "matter.json").write_text(json.dumps(matter, indent=2, default=str))


def append_event(kind, **data):
    """One line to events.jsonl. Never edited, never deleted. The only history the tool keeps."""
    folder = matter_dir()
    folder.mkdir(parents=True, exist_ok=True)
    event = {"when": datetime.now().isoformat(timespec="seconds"), "kind": kind, **data}
    with open(folder / "events.jsonl", "a") as f:
        f.write(json.dumps(event, default=str) + "\n")


def read_events():
    path = matter_dir() / "events.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines()]


def active_playbooks():
    """The loaded playbooks for this matter's issues, in the order classify listed them."""
    return [playbooks[i] for i in matter["issues"] if i in playbooks]


def element_status():
    """Element rows for every active playbook, keyed by issue."""
    return {pb.issue: check_elements(pb, profile, matter["facts"], matter["proposed"]) for pb in active_playbooks()}
