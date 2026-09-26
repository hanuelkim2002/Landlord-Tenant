"""Run: start() asks whether this is a new or an existing matter, then the chat.

    python run.py

New matter: pick a tenant (or make a new one), give the lease PDF's path, describe the problem. The lease is
read once with Gemma, then intake. Existing matter: pick it from the list, and the chat picks up from the
saved record. There is no re-intake on an existing matter until the resume question in TODO.md is decided.
"""
from pathlib import Path

from config import require_key
require_key()                   # this script calls the models; stop here if the key is missing

import record
from agent import build_agent, chat, intake
from lease import check_quotes, extract_profile, ingest_pdf
from record import list_matters, load_matter, matter_dir, new_matter, new_tenant_id


def ask_path(prompt):
    """Ask for a file path until one exists. Accepts a path dragged into the terminal (quotes, escaped spaces)."""
    while True:
        raw = input(prompt).strip().strip("'\"").replace("\\ ", " ")
        path = Path(raw).expanduser()
        if path.is_file():
            return path
        print("No file at", path)


def ask_description():
    """Read the tenant's description, several lines, ended by an empty line."""
    print("Describe the problem in your own words. Press Enter on an empty line when done.")
    lines = []
    while True:
        line = input()
        if not line:
            return "\n".join(lines)
        lines.append(line)


def read_lease(pdf_path):
    """Store the PDF, read it with Gemma into the lease profile, check every quote, save the profile."""
    pages = ingest_pdf(pdf_path, matter_dir())
    record.profile = extract_profile(pages)
    check_quotes(record.profile, pages)
    (matter_dir() / "lease_profile.json").write_text(record.profile.model_dump_json(indent=2))


def start_new():
    """New matter: tenant, lease, description, intake. Returns the agent."""
    tenants = sorted({m["tenant"] for m in list_matters()})
    if tenants:
        print("Existing tenants:", ", ".join(tenants))
    tenant = input("Tenant id for this matter (Enter for a new tenant): ").strip()
    if tenant not in tenants:
        tenant = new_tenant_id()
    new_matter(tenant)
    print("New matter", record.matter["tenant"], record.matter["id"])

    read_lease(ask_path("Path to the lease PDF: "))
    return intake(ask_description())


def start_existing():
    """Existing matter: pick from the list, load it, build the agent from the saved record. Returns the agent,
    or None if there is nothing to open."""
    found = list_matters()
    if not found:
        print("No saved matters yet.")
        return None
    for i, m in enumerate(found, start=1):
        print(f"{i}. {m['tenant']} / {m['id']}  issues: {m['issues']}")
    while True:
        pick = input("Number of the matter to open: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(found):
            break
    m = found[int(pick) - 1]
    load_matter(m["tenant"], m["id"])
    if record.profile is None:
        print("This matter has no lease profile yet. Start a new matter with the lease instead.")
        return None
    return build_agent()


def start():
    """The front door: new or existing. Returns an agent, or None to stop."""
    while True:
        choice = input("New matter or existing matter? [new/existing] ").strip().lower()
        if choice in ("new", "n"):
            return start_new()
        if choice in ("existing", "e"):
            return start_existing()


agent = start()
if agent:
    chat(agent)
