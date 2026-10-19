"""Method B: a table of contents in the prompt, and a tool to read clauses. Run: python method_b.py"""
import re

import common

TOOLS = [{"type": "function", "function": {
    "name": "read_clause",
    "description": "Read the full words of one or more clauses of the tenant's lease, by their ids in the table of "
                   "contents (like \"c12\"), or by the lease's own section numbers (like \"4.2\").",
    "parameters": {"type": "object", "properties": {"ids": {"type": "array", "items": {"type": "string"},
                                                            "description": "Clause ids, like [\"c12\", \"c40\"]"}},
                   "required": ["ids"]}}}]


def setup(lease):
    """The lease's clauses, by id."""
    return {c["id"]: c for c in common.split_clauses(common.lease_pages(lease))}


def lease_part(clauses):
    """The system prompt's lease part: only the clause titles."""
    contents = "\n".join(f"[{c['id']}] {c['title']} (page {c['page']})" for c in clauses.values())
    return ("THE LEASE: the tenant's lease is split into the clauses listed below. You see only their titles. Call "
            "read_clause with the ids of the clauses you need. Read every clause that may bear on the question "
            "before you answer, and before you say the lease does not address it.\n\n"
            f"TABLE OF CONTENTS\n{contents}")


def matching(clauses, wanted):
    """The clauses a requested id points to: the id itself ("c74" or "74"), or the lease's own section number
    ("21.2"), which the model often uses; a section number brings that section's clauses, at most 12."""
    wanted = str(wanted).strip()
    for key in (wanted, f"c{wanted}"):
        if key in clauses:
            return [clauses[key]]
    number = re.escape(wanted.rstrip("."))
    printed = re.compile(rf"(^|[\s>]){number}\.(\s|$)")
    return [c for c in clauses.values() if printed.search(c["title"])][:12]


def read_clause(clauses, name, arguments):
    """The asked-for clauses' titles and words."""
    ids = arguments.get("ids") or []
    if isinstance(ids, str):
        ids = [ids]
    found = []
    for wanted in ids:
        found += [c for c in matching(clauses, wanted) if c not in found]
    if not found:
        return "No clause has those ids. Use the ids in the table of contents."
    return "\n\n".join(f"Clause {c['id']}. {c['title']} (page {c['page']}):\n{c['text']}" for c in found)


if __name__ == "__main__":
    common.run("B", setup, lease_part, lambda state: TOOLS, read_clause)
