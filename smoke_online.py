"""Smoke Tests, online: the two one-shot intake calls on a sample description, then resume on a throwaway copy
of the test matter. Four model calls, needs the key. Needs the saved test matter, matters/t-test/test-001/.
The offline checks are in smoke.py. Checks marked (model) depend on what the model answers.

    python smoke_online.py
"""
from config import require_key
require_key()                   # this script calls the model; stop here if the key is missing

import record
from agent import resume
from checks import check, make_scratch, remove_scratch, summary
from config import MATTERS
from corpus import issue_menu, playbooks
from deterministic import check_elements, classify, fill_facts
from record import end_session, load_matter, read_events, start_session

load_matter("t-test", "test-001")         # the test matter and its lease profile, from disk
pb = playbooks["deposit_not_returned"]

# classifier and slot filling on a description (two model calls)
description = """I rented a house in Gainesville. My lease ended July 31, 2026 and I moved out
and gave the keys back on July 30, 2026. I emailed the property manager my new address the same
day. It's September now and I haven't gotten my $1,850 deposit back or any letter about it."""
print(classify(description, issue_menu()))

# the story that was misread: the tenant's own withholding notice is not a landlord's rent demand
repair = "\n".join([
    "I rent a single-family house in Gainesville. The air conditioning has been broken since September 1, 2026.",
    "On September 10, 2026 I hand-delivered a written notice to the landlord describing the broken air conditioning and saying I will not pay rent until it is fixed.",
    "The landlord has not fixed it or replied. I have not paid rent since the air conditioning broke, and no court papers have been served on me.",
])
check("(model) classify reads the tenant's own notice as the tenant's", classify(repair, issue_menu())["issues"] == ["repair_not_made"])
check("(model) a situation no playbook covers is classified other", classify(
    "My roommate moved out in August and stopped paying his half of the rent. I paid the whole rent for September myself.",
    issue_menu())["issues"] == ["other"])
mixed = classify("My heater hasn't worked since September 15, 2026 and my landlord keeps saying he'll fix it but he "
                 "doesn't. When I asked him about it again he said he regrets renting to 'people like you' because I'm "
                 "Muslim.", issue_menu())["issues"]
check("(model) a covered problem next to one no playbook covers gets both, other included (eval 2026-10-01)",
      "repair_not_made" in mixed and "other" in mixed)
detail = classify("Since August 20, 2026 there's been black mold on my bathroom ceiling and the landlord has not "
                  "fixed it. I have asthma and it's getting worse.", issue_menu())["issues"]
check("(model) a detail of a covered problem is not a separate one", detail == ["repair_not_made"])
proposed = fill_facts(description, pb)
print(proposed)
for row in check_elements(pb, record.profile, {}, proposed):
    print(row)
print()

# resume on a throwaway copy (matters/t-smoke-online/m-001): the update is logged as typed, old issues and
# confirmed facts are untouched, and no suggestion repeats a confirmed value.
make_scratch("t-smoke-online", issues=["deposit_not_returned"],
             facts={"tenancy_terminated": "2026-07-31", "vacated": "2026-07-30", "claim_notice_received": False},
             proposed={})
update = ("I got a letter from the landlord on September 25, 2026 saying they are keeping $400 of my deposit "
          "for cleaning. It came by certified mail and is dated September 22, 2026.")
try:
    load_matter("t-smoke-online", "m-001")
    before = {"description": record.matter["description"], "facts": dict(record.matter["facts"])}
    start_session("existing")
    resume(update)
    end_session()
    logged = [e for e in read_events() if e["kind"] == "tenant_update"]
    facts = record.matter["facts"]
    check("resume logs the update verbatim", logged and logged[-1]["text"] == update)
    check("resume leaves the first description alone", record.matter["description"] == before["description"])
    check("resume keeps the old issues", record.matter["issues"][0] == "deposit_not_returned")
    check("resume confirms nothing", facts == before["facts"])
    check("resume drops suggestions equal to a confirmed value",
          not any(i in facts and p["value"] == facts[i] for i, p in record.matter["proposed"].items()))
    check("(model) resume suggests deposit_claim_received", any(
        p["issue"] == "deposit_claim_received" for p in record.matter["proposed_issues"]))
    check("resume activates nothing: a suggested issue waits for the tenant", record.matter["issues"] == ["deposit_not_returned"])
    check("(model) the changed fact is proposed", record.matter["proposed"].get("claim_notice_received", {}).get("value") is True)
finally:
    remove_scratch("t-smoke-online")
check("the scratch matter is removed", not (MATTERS / "t-smoke-online").exists())
summary()
