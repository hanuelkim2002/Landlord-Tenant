"""Run: start() asks whether this is a new or an existing matter, then the chat.

    python run.py

New matter: pick a tenant (or make a new one), give the lease PDF's path, describe the problem. The lease is
read once with Gemma, and the description is saved (intake). Existing matter: pick it from the list and say what is
new, if anything; an update is logged (resume). Either way the chat starts at once, and the description or the update
is the tenant's first message: the model loads the skills that fit and proposes facts, the confirmation asks the
tenant to confirm them after that turn, and the model replies to what was confirmed at once.
"""
from pathlib import Path

from config import require_key
require_key()                   # this script calls the models; stop here if the key is missing

import record
from agent import build_agent, chat, intake, read_lease, resume
from record import end_session, list_matters, load_matter, new_matter, new_tenant_id, start_session


def ask_path(prompt):
    """Ask for a file path until one exists. Accepts a path dragged into the terminal (quotes, escaped spaces)."""
    while True:
        raw = input(prompt).strip().strip("'\"").replace("\\ ", " ")
        path = Path(raw).expanduser()
        if path.is_file():
            return path
        print("No file at", path)


def ask_text(prompt):
    """Read several lines from the tenant, ended by an empty line. An empty first line returns ""."""
    print(prompt)
    lines = []
    while True:
        line = input()
        if not line:
            return "\n".join(lines)
        lines.append(line)


def start_new():
    """New matter: tenant, lease, description, intake. Returns the description: the tenant's first message."""
    tenants = sorted({m["tenant"] for m in list_matters()})
    if tenants:
        print("Existing tenants:", ", ".join(tenants))
    tenant = input("Tenant id for this matter (Enter for a new tenant): ").strip()
    if tenant not in tenants:
        tenant = new_tenant_id()
    new_matter(tenant)
    print("New matter", record.matter["tenant"], record.matter["id"])
    start_session("new")                       # from here on, every event carries this session's id

    read_lease(ask_path("Path to the lease PDF: "))
    description = ask_text("Describe the problem in your own words. Press Enter on an empty line when done.")
    intake(description)
    return description


def start_existing():
    """Existing matter: pick from the list, load it, ask what is new. Returns what is new, the tenant's first
    message ("" if nothing is new), or None if there is nothing to open."""
    found = list_matters()
    if not found:
        print("No saved matters yet.")
        return None
    for i, m in enumerate(found, start=1):
        print(f"{i}. {m['tenant']} / {m['id']}  skills: {m['skills']}")
    while True:
        pick = input("Number of the matter to open: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(found):
            break
    m = found[int(pick) - 1]
    load_matter(m["tenant"], m["id"])
    if record.profile is None:
        print("This matter has no lease profile yet. Start a new matter with the lease instead.")
        return None
    start_session("existing")                  # before the update, so the update belongs to this session

    update = ask_text("Anything new since last time? Type it in your own words and press Enter on an empty\n"
                      "line when done. Press Enter right away if nothing is new.")
    if update:
        resume(update)                         # logs the update
    return update


def start():
    """The front door: new or existing. Returns the tenant's first message ("" if there is none) when a matter is
    open, None to stop."""
    while True:
        choice = input("New matter or existing matter? [new/existing] ").strip().lower()
        if choice in ("new", "n"):
            return start_new()
        if choice in ("existing", "e"):
            return start_existing()


first = start()
if first is not None:
    chat(build_agent(), first)                 # the first message is the description or the update
    end_session()                              # only on a normal exit; a crash leaves the start without an end
