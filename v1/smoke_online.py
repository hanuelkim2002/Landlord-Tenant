"""Smoke Tests, online: a visit's first turn (visit.py), on throwaway matters. Intake and resume call no model (smoke.py
checks that); the model's work is the first turn on the tenant's description or update: load the skills that fit, propose
facts, answer. A new matter also reads the test lease with the extraction model. Needs the key and the saved test matter,
matters/t-test/test-001/. The offline checks are in smoke.py. Checks marked (model) depend on what the model answers.

    python smoke_online.py
"""
from config import require_key
require_key()                   # this script calls the model; stop here if the key is missing

import record
from checks import TEST_MATTER, check, make_scratch, remove_scratch, summary
from config import MATTERS
from record import load_matter, read_events
from visit import Visit

load_matter("t-test", "test-001")         # the test matter and its lease profile, from disk
lease_pdf = next(TEST_MATTER.glob("lease_*.pdf"))


def first_turn(tenant, message):
    """A visit to a throwaway copy (matters/<tenant>/m-001) that begins with `message` as the tenant's first message
    (an update), and return what the model did: its blocks and whether it asked for confirmations. The copy stays
    open in the record for the checks."""
    visit, result = Visit.existing(tenant, "m-001", message)
    visit.end()
    return result.blocks, bool(result.rows)


# A new matter: intake saves the description, and the description is the first message.
description = """I rented a house in Gainesville. My lease ended July 31, 2026 and I moved out
and gave the keys back on July 30, 2026. I emailed the property manager my new address the same
day. It's September now and I haven't gotten my $1,850 deposit back or any letter about it."""
remove_scratch("t-smoke-online-new")
try:
    visit, result = Visit.new("t-smoke-online-new", lease_pdf, description)       # reads the lease, then the first turn
    visit.end()
    blocks, proposed = result.blocks, bool(result.rows)
    print(record.matter["skills"], list(record.matter["proposed"]))
    check("the lease is read into the short profile and its text is stored",
          [name for name, _ in record.profile.clauses()] == ["landlord_name_and_address", "tenant_names", "premises_address",
                                                              "notices_to_landlord"]
          and (record.matter_dir() / "pages.json").exists())
    check("intake saved the description", record.matter["description"] == description)
    check("(model) the first turn answers the tenant", any(b["kind"] == "reply" for b in blocks))
    check("(model) the model loads the skill that fits", "deposit_not_returned" in record.matter["skills"])
    check("(model) the model proposes facts from the description", proposed and record.matter["proposed"])
    check("(model) a date the description gives for a loaded skill's clock is proposed under that skill's fact id",
          record.matter["proposed"].get("tenancy_terminated", {}).get("value") == "2026-07-31")
    check("the model confirms nothing", record.matter["facts"] == {})
    check("every skill loaded is logged", [e["skill"] for e in read_events() if e["kind"] == "skill_loaded"]
          == record.matter["skills"])
finally:
    remove_scratch("t-smoke-online-new")
check("the new-matter scratch matter is removed", not (MATTERS / "t-smoke-online-new").exists())

# A situation no skill covers: the model loads none.
make_scratch("t-smoke-online-none", skills=[], facts={}, proposed={})
try:
    first_turn("t-smoke-online-none",
               "My roommate moved out in August and stopped paying his half of the rent. I paid the whole rent for "
               "September myself.")
    check("(model) a situation no skill covers: no skill is loaded", record.matter["skills"] == [])
finally:
    remove_scratch("t-smoke-online-none")
check("the no-skill scratch matter is removed", not (MATTERS / "t-smoke-online-none").exists())

# A returning tenant's update on a throwaway copy (matters/t-smoke-online/m-001): the update is logged as typed, the
# skills loaded and the confirmed facts are untouched, the update goes to the model as the first message, and no
# suggestion repeats a confirmed value.
make_scratch("t-smoke-online", skills=["deposit_not_returned"],
             facts={"tenancy_terminated": "2026-07-31", "vacated": "2026-07-30", "claim_notice_received": False},
             proposed={})
update = ("I got a letter from the landlord on September 25, 2026 saying they are keeping $400 of my deposit "
          "for cleaning. It came by certified mail and is dated September 22, 2026.")
try:
    load_matter("t-smoke-online", "m-001")
    before = {"description": record.matter["description"], "facts": dict(record.matter["facts"])}
    blocks, proposed = first_turn("t-smoke-online", update)
    logged = [e for e in read_events() if e["kind"] == "tenant_update"]
    facts = record.matter["facts"]
    check("resume logs the update verbatim", logged and logged[-1]["text"] == update)
    check("resume leaves the first description alone", record.matter["description"] == before["description"])
    check("resume keeps the skills loaded", record.matter["skills"][0] == "deposit_not_returned")
    check("nothing is confirmed by the first turn", facts == before["facts"])
    check("no suggestion repeats a confirmed value",
          not any(i in facts and p["value"] == facts[i] for i, p in record.matter["proposed"].items()))
    check("(model) the model loads deposit_claim_received", "deposit_claim_received" in record.matter["skills"])
    check("(model) the date the claim notice arrived is proposed under the skill's fact id",
          record.matter["proposed"].get("claim_notice_date", {}).get("value") == "2026-09-25")
finally:
    remove_scratch("t-smoke-online")
check("the scratch matter is removed", not (MATTERS / "t-smoke-online").exists())
summary()
