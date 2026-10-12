"""Smoke Tests, online: the model's first turn, on throwaway copies of the test matter. Intake and resume call no model
(smoke.py checks that); the model's work is the first turn on the tenant's description or update: load the skills that
fit, propose facts, answer. Needs the key and the saved test matter, matters/t-test/test-001/. The offline checks are in
smoke.py. Checks marked (model) depend on what the model answers.

    python smoke_online.py
"""
from config import require_key
require_key()                   # this script calls the model; stop here if the key is missing

import record
from agent import build_agent, intake, resume, thread_config, turn
from checks import check, make_scratch, remove_scratch, summary
from config import MATTERS
from record import end_session, load_matter, read_events, start_session

load_matter("t-test", "test-001")         # the test matter and its lease profile, from disk


def first_turn(tenant, session_how, opening, message):
    """Run the first turn on a throwaway copy (matters/<tenant>/m-001) after `opening` (intake or resume), and return
    what the model did: its blocks and whether it proposed facts. The copy stays open for the checks."""
    load_matter(tenant, "m-001")
    start_session(session_how)
    opening(message)
    blocks, proposed = turn(build_agent(), thread_config(), message)
    end_session()
    return blocks, proposed


# A new matter: intake saves the description, and the description is the first message.
description = """I rented a house in Gainesville. My lease ended July 31, 2026 and I moved out
and gave the keys back on July 30, 2026. I emailed the property manager my new address the same
day. It's September now and I haven't gotten my $1,850 deposit back or any letter about it."""
make_scratch("t-smoke-online-new", skills=[], facts={}, proposed={})
try:
    blocks, proposed = first_turn("t-smoke-online-new", "new", intake, description)
    print(record.matter["skills"], list(record.matter["proposed"]))
    check("intake saved the description", record.matter["description"] == description)
    check("(model) the first turn answers the tenant", any(b["kind"] == "reply" for b in blocks))
    check("(model) the model loads the skill that fits", "deposit_not_returned" in record.matter["skills"])
    check("(model) the model proposes facts from the description", proposed and record.matter["proposed"])
    check("the model confirms nothing", record.matter["facts"] == {})
    check("every skill loaded is logged", [e["skill"] for e in read_events() if e["kind"] == "skill_loaded"]
          == record.matter["skills"])
finally:
    remove_scratch("t-smoke-online-new")
check("the new-matter scratch matter is removed", not (MATTERS / "t-smoke-online-new").exists())

# A situation no skill covers: the model loads none.
make_scratch("t-smoke-online-none", skills=[], facts={}, proposed={})
try:
    first_turn("t-smoke-online-none", "new", intake,
               "My roommate moved out in August and stopped paying his half of the rent. I paid the whole rent for "
               "September myself.")
    check("(model) a situation no skill covers: no skill is loaded", record.matter["skills"] == [])
finally:
    remove_scratch("t-smoke-online-none")
check("the no-skill scratch matter is removed", not (MATTERS / "t-smoke-online-none").exists())

# resume on a throwaway copy (matters/t-smoke-online/m-001): the update is logged as typed, the skills loaded and the
# confirmed facts are untouched, the update goes to the model as the first message, and no suggestion repeats a
# confirmed value.
make_scratch("t-smoke-online", skills=["deposit_not_returned"],
             facts={"tenancy_terminated": "2026-07-31", "vacated": "2026-07-30", "claim_notice_received": False},
             proposed={})
update = ("I got a letter from the landlord on September 25, 2026 saying they are keeping $400 of my deposit "
          "for cleaning. It came by certified mail and is dated September 22, 2026.")
try:
    load_matter("t-smoke-online", "m-001")
    before = {"description": record.matter["description"], "facts": dict(record.matter["facts"])}
    blocks, proposed = first_turn("t-smoke-online", "existing", resume, update)
    logged = [e for e in read_events() if e["kind"] == "tenant_update"]
    facts = record.matter["facts"]
    check("resume logs the update verbatim", logged and logged[-1]["text"] == update)
    check("resume leaves the first description alone", record.matter["description"] == before["description"])
    check("resume keeps the skills loaded", record.matter["skills"][0] == "deposit_not_returned")
    check("nothing is confirmed by the first turn", facts == before["facts"])
    check("no suggestion repeats a confirmed value",
          not any(i in facts and p["value"] == facts[i] for i, p in record.matter["proposed"].items()))
    check("(model) the model loads deposit_claim_received", "deposit_claim_received" in record.matter["skills"])
    check("(model) the changed fact is proposed", record.matter["proposed"].get("claim_notice_received", {}).get("value") is True)
finally:
    remove_scratch("t-smoke-online")
check("the scratch matter is removed", not (MATTERS / "t-smoke-online").exists())
summary()
