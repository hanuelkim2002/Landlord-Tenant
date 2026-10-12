"""Smoke, part: visits (TODO item 115), through visit.py with a stand-in model and a stand-in extraction (no gateway):
Visit.new reads the lease, runs the first turn on the description, and returns the confirmation rows; confirm with an accepted
suggestion, a correction, a bad answer refused, and a skip, then the model's reply at once; the reply bound (once per tenant
message, the second confirmation's note carried to the next message); Visit.existing with and without an update, with a
matter saved with all sixteen of the old lease fields, and with no lease profile; the record put back for each call even when
another matter was opened in between; a model error; a lease that cannot be read; and that run.py is gone and nothing
imports it. Each on its own scratch matter under matters/t-smoke-visit*, removed at its end.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import contextlib
import io
import json
import re
from langchain.messages import AIMessage
import agent
import record
from checks import TEST_MATTER, check, make_scratch, remove_scratch
from config import MATTERS, ROOT
from lease import LeaseProfile
from record import list_matters, matter_dir, read_events
from sheet import pending_rows
from visit import Result, Visit
from smoke_parts.common import StandIn

LEASE_PDF = next(TEST_MATTER.glob("lease_*.pdf"))                      # the test lease, as the tenant would upload it
PROFILE_TEXT = (TEST_MATTER / "lease_profile.json").read_text()
extractions = []


def extraction(pages):
    """Stands in for the extraction model: the test lease's profile, read from disk."""
    extractions.append(len(pages))
    return LeaseProfile.model_validate_json(PROFILE_TEXT)


def proposes(call_id, facts):
    """A stand-in model message that calls propose_facts."""
    return AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": call_id, "args": {"facts_json": json.dumps(facts)}}])


def loads(call_id, name):
    """A stand-in model message that calls load_skill."""
    return AIMessage(content="", tool_calls=[{"name": "load_skill", "id": call_id, "args": {"name": name}}])


def said(value, words, how="stated"):
    return {"value": value, "how": how, "said": words}


def thread(visit):
    """The messages of the visit's chat thread, as the model got them."""
    return visit.agent.get_state(visit.config).values["messages"]


def humans(visit):
    return [m.content for m in thread(visit) if m.type == "human"]


def transcript(visit):
    path = MATTERS / visit.tenant_id / visit.matter_id / "sessions" / f"{visit.session_id}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


def kinds(result):
    return [b["kind"] for b in result.blocks]


def quiet(call, *args):
    """Call with the print of the lease reading and the agent building kept out of the smoke output."""
    with contextlib.redirect_stdout(io.StringIO()):
        return call(*args)


def elsewhere():
    """Another visit's doing, in between: another matter opened in the record, another session in its place."""
    record.load_matter("t-smoke-visit-other", "m-001")
    record.session = "someone-else"


real_llm, real_extract = agent.agent_llm, agent.extract_profile
agent.extract_profile = extraction
try:
    # ---- Visit.new: the lease read (stand-in extraction), the description saved, the first turn on it (stand-in model), the
    # confirmation rows back. The model loads the skill, proposes four facts from the description, and answers.
    description = ("My lease ended July 31, 2026. I moved out on July 28, 2026 and I did not leave early. "
                   "The landlord said he would send a check.")
    note = ("[Program note: the tenant confirmed on the sheet: vacated = 2026-07-28, tenancy_terminated = 2026-07-30, "
            "early_or_periodic = False]\n")
    agent.agent_llm = StandIn(messages=iter([
        loads("n1", "deposit_not_returned"),
        proposes("n2", {"vacated": said("2026-07-28", "I moved out on July 28, 2026"),
                        "tenancy_terminated": said("2026-07-31", "My lease ended July 31, 2026"),
                        "early_or_periodic": said(False, "I did not leave early", "inferred"),
                        "landlord_response": said("he would send a check", "he would send a check")}),
        AIMessage(content="That sounds like a deposit question."),
        AIMessage(content="Thank you. With the move-out date confirmed, the next thing to find out is whether a letter came."),
        AIMessage(content="Third."), AIMessage(content="Fourth.")]))
    remove_scratch("t-smoke-visit")
    make_scratch("t-smoke-visit-other")                                   # the matter another visit has open in between
    try:
        visit, first = quiet(Visit.new, "t-smoke-visit", LEASE_PDF, description)
        check("item 115: Visit.new makes the tenant's matter, opens a session, reads the lease with the extraction model (once, "
              "12 pages), saves the short profile and the lease text, and saves the description",
              (visit.tenant_id, visit.matter_id) == ("t-smoke-visit", "m-001") and extractions == [12]
              and record.session == visit.session_id and read_events()[0] == {
                  "when": read_events()[0]["when"], "kind": "session_started", "session": visit.session_id, "how": "new"}
              and list(json.loads((matter_dir() / "lease_profile.json").read_text())) == [
                  "landlord_name_and_address", "tenant_names", "premises_address", "notices_to_landlord"]
              and (matter_dir() / "pages.json").exists()
              and json.loads((matter_dir() / "matter.json").read_text())["description"] == description)
        check("item 115: Visit.new runs the first turn with the description as the tenant's first message: the model loads the "
              "skill and proposes facts from the tenant's own words, its reply is the result's block, and the rows to "
              "confirm come back, in the order proposed, each with the tenant's words",
              humans(visit) == [description] and transcript(visit)[0] == {
                  "when": transcript(visit)[0]["when"], "role": "tenant", "text": description}
              and kinds(first) == ["reply"] and first.blocks[0]["text"] == "That sounds like a deposit question."
              and first.refused == {} and record.matter["skills"] == ["deposit_not_returned"]
              and [r["id"] for r in first.rows] == ["vacated", "tenancy_terminated", "early_or_periodic", "landlord_response"]
              and first.rows == pending_rows() and first.rows[0]["basis"] == "I moved out on July 28, 2026"
              and record.matter["facts"] == {})

        # ---- confirm: one row at a time, as the page asks, then the rest at once. An accepted suggestion and a correction are
        # saved with no model call while a row is open; a bad answer is refused and saves nothing.
        accepted = visit.confirm({"vacated": ""})
        corrected = visit.confirm({"tenancy_terminated": "7/30/2026"})
        check("item 115: confirm with an empty answer accepts the suggestion and with a typed one corrects it (parsed by the "
              "row's type): each is saved, shown as a sheet block, and the rows still open come back; no model call while a "
              "row is open",
              kinds(accepted) == ["sheet"] and accepted.blocks[0]["text"] == "vacated: 2026-07-28"
              and [r["id"] for r in accepted.rows] == ["tenancy_terminated", "early_or_periodic", "landlord_response"]
              and corrected.blocks == [{"kind": "sheet", "text": "tenancy terminated: 2026-07-30"}]
              and [r["id"] for r in corrected.rows] == ["early_or_periodic", "landlord_response"]
              and record.matter["facts"] == {"vacated": "2026-07-28", "tenancy_terminated": "2026-07-30"}
              and humans(visit) == [description])
        refused = visit.confirm({"early_or_periodic": "maybe"})
        check("item 115: a bad answer is refused with what is expected, nothing is saved, its row stays open to be asked again, "
              "and the model is not called",
              refused.refused == {"early_or_periodic": "yes or no"} and refused.blocks == []
              and [r["id"] for r in refused.rows] == ["early_or_periodic", "landlord_response"]
              and "early_or_periodic" not in record.matter["facts"] and humans(visit) == [description])
        done = visit.confirm({"early_or_periodic": "no", "landlord_response": "?"})
        lines = transcript(visit)
        check("item 115: once every row is answered or skipped, the tenant is told what was skipped (it stays pending, to be "
              "asked again) and the model replies at once to what was confirmed: the note as a turn of its own, a program "
              "line and no tenant line for it, the reply shown",
              kinds(done) == ["sheet", "notice", "reply"] and done.rows == [] and done.refused == {}
              and done.blocks[1]["text"].startswith("Skipped for now: landlord response.")
              and done.blocks[2]["text"].startswith("Thank you. With the move-out date confirmed")
              and humans(visit) == [description, note] and [r["id"] for r in pending_rows()] == ["landlord_response"]
              and record.matter["facts"] == {"vacated": "2026-07-28", "tenancy_terminated": "2026-07-30", "early_or_periodic": False}
              and [l["text"] for l in lines if l["role"] == "program"] == [note]
              and [l["text"] for l in lines if l["role"] == "tenant"] == [description]
              and [(l["id"], l["typed"], l["value"]) for l in lines if l["role"] == "sheet"] == [
                  ("vacated", "", "2026-07-28"), ("tenancy_terminated", "7/30/2026", "2026-07-30"),
                  ("early_or_periodic", "no", False)]
              and visit.replied and visit.note == "")
        next_blocks = visit.say("And?")
        check("item 115: the next tenant message goes to the model without a note; the skipped fact is not asked again unless "
              "the model proposes facts",
              humans(visit) == [description, note, "And?"] and next_blocks.blocks == [{"kind": "reply", "text": "Third."}]
              and next_blocks.rows == [] and not visit.replied)

        # ---- the record put back: another matter and another session were opened in between; each call uses its own
        other = MATTERS / "t-smoke-visit-other" / "m-001"
        elsewhere()
        said_back = visit.say("What now?")
        check("item 115: say puts the visit's matter and session back into the record, even when another matter was opened in "
              "between: the tenant's line goes to this visit's transcript, none to the other matter",
              record.matter["tenant"] == "t-smoke-visit" and record.session == visit.session_id
              and said_back.blocks == [{"kind": "reply", "text": "Fourth."}]
              and "What now?" in [l["text"] for l in transcript(visit) if l["role"] == "tenant"]
              and not (other / "sessions" / "someone-else.jsonl").exists())
        elsewhere()
        rows_back = visit.rows()
        check("item 115: rows puts the visit's matter back too, and lists its pending row", record.matter["tenant"] == "t-smoke-visit"
              and record.session == visit.session_id and [r["id"] for r in rows_back] == ["landlord_response"])
        elsewhere()
        visit.confirm({"landlord_response": "?"})
        check("item 115: confirm puts the visit's matter back too (the skipped row is a fact of this matter, not the other's)",
              record.matter["tenant"] == "t-smoke-visit" and record.session == visit.session_id
              and "landlord_response" in json.loads((matter_dir() / "matter.json").read_text())["proposed"])
        elsewhere()
        visit.end()
        visit.end()
        events_mine = [e for e in read_events() if e.get("session") == visit.session_id]
        check("item 115: end puts the visit's matter back, logs the end in its session, once however often it is called, and "
              "leaves no session open; nothing of it reached the other matter",
              record.matter["tenant"] == "t-smoke-visit" and events_mine[-1]["kind"] == "session_ended"
              and sum(e["kind"] == "session_ended" for e in events_mine) == 1 and record.session is None
              and "someone-else" not in (other / "events.jsonl").read_text() and not (other / "sessions" / "someone-else.jsonl").exists())
    finally:
        remove_scratch("t-smoke-visit")
        remove_scratch("t-smoke-visit-other")
    check("the Visit.new scratch matter is removed", not (MATTERS / "t-smoke-visit").exists())

    # ---- Visit.existing with an update: the update is logged as typed after the session opens, it is the first message, and
    # the reply bound holds: the model's reply right after the confirmation proposes facts again, the form comes again, and
    # what the tenant confirms then gets no second automatic reply: it waits and goes with the next message. The matter was
    # saved with all sixteen of the old lease fields, which load as the four.
    sixteen = json.loads(PROFILE_TEXT)
    sixteen["maintenance_and_repairs"] = {"present": True, "quote": "Landlord shall repair the heating", "page": 4, "section": "7.2"}
    update = "I moved out on July 28, 2026. The landlord said he would send a check."
    said_one, said_two = "I moved out on July 28, 2026", "he would send a check"
    note_one = "[Program note: the tenant confirmed on the sheet: vacated = 2026-07-28]\n"
    note_two = "[Program note: the tenant confirmed on the sheet: landlord_response = he would send a check]\n"
    agent.agent_llm = StandIn(messages=iter([
        proposes("e1", {"vacated": said("2026-07-28", said_one)}), AIMessage(content="Noted."),
        proposes("e2", {"landlord_response": said(said_two, said_two)}), AIMessage(content="Automatic."),
        AIMessage(content="Next.")]))
    make_scratch("t-smoke-visit-old", skills=["deposit_not_returned"], facts={}, proposed={})
    (MATTERS / "t-smoke-visit-old" / "m-001" / "lease_profile.json").write_text(json.dumps(sixteen))
    try:
        visit, first = quiet(Visit.existing, "t-smoke-visit-old", "m-001", update)
        events_now = [e for e in read_events() if e.get("session") == visit.session_id]
        check("item 115: Visit.existing loads the matter (its lease profile saved with sixteen fields loads as the four), opens a "
              "session, logs the update verbatim after it opens, and runs the first turn with the update as the tenant's first "
              "message",
              [n for n, _ in record.profile.clauses()] == ["landlord_name_and_address", "tenant_names", "premises_address",
                                                            "notices_to_landlord"]
              and [(e["kind"], e.get("how"), e.get("text")) for e in events_now] == [
                  ("session_started", "existing", None), ("tenant_update", None, update)]
              and humans(visit) == [update] and kinds(first) == ["reply"] and [r["id"] for r in first.rows] == ["vacated"]
              and record.matter["description"] == json.loads((TEST_MATTER / "matter.json").read_text())["description"])
        second = visit.confirm({"vacated": ""})
        third = visit.confirm({"landlord_response": ""})
        check("item 115: the reply right after a confirmation happens once per tenant message: its own proposals bring the rows "
              "again, and what is confirmed then gets no second automatic reply, but is kept as the note for the next message",
              kinds(second) == ["sheet", "reply"] and second.blocks[1]["text"] == "Automatic."
              and [r["id"] for r in second.rows] == ["landlord_response"] and humans(visit) == [update, note_one]
              and kinds(third) == ["sheet"] and third.rows == [] and visit.note == note_two and humans(visit) == [update, note_one]
              and [l["text"] for l in transcript(visit) if l["role"] == "program"] == [note_one])
        after = visit.say("And?")
        check("item 115: the carried note goes in front of the tenant's next message, once",
              humans(visit) == [update, note_one, note_two + "And?"] and after.blocks == [{"kind": "reply", "text": "Next."}]
              and visit.note == "" and [l["text"] for l in transcript(visit) if l["role"] == "program"] == [note_one, note_two])
        visit.end()
    finally:
        remove_scratch("t-smoke-visit-old")

    # every row skipped: nothing was confirmed, so the model is not called (a stand-in with one message left would fail the
    # next turn if it were), and the tenant is told what was skipped
    agent.agent_llm = StandIn(messages=iter([proposes("s1", {"vacated": said("2026-07-28", said_one)}), AIMessage(content="Noted.")]))
    make_scratch("t-smoke-visit-skip", skills=["deposit_not_returned"], facts={}, proposed={})
    try:
        visit, first = quiet(Visit.existing, "t-smoke-visit-skip", "m-001", update)
        skipped = visit.confirm({"vacated": "?"})
        check("item 115: with every row skipped the model is not called again: only the skipped notice comes back, the fact stays "
              "pending, and nothing is carried to the next message",
              [r["id"] for r in first.rows] == ["vacated"] and kinds(skipped) == ["notice"] and skipped.rows == []
              and humans(visit) == [update] and [r["id"] for r in pending_rows()] == ["vacated"] and visit.note == ""
              and not any(l["role"] == "program" for l in transcript(visit)))
        visit.end()
    finally:
        remove_scratch("t-smoke-visit-skip")

    # ---- Visit.existing without an update: the session opens, nothing is logged, no model is called, the result is empty; the
    # chat waits for the tenant's first message. A matter with no lease profile is refused and no session opens.
    agent.agent_llm = StandIn(messages=iter([AIMessage(content="Only after I am asked.")]))
    make_scratch("t-smoke-visit-none", skills=["deposit_not_returned"], facts={}, proposed={})
    try:
        visit, nothing = quiet(Visit.existing, "t-smoke-visit-none", "m-001")
        mine = [e for e in read_events() if e.get("session") == visit.session_id]
        asked = visit.say("Hello?")
        check("item 115: Visit.existing with no update opens a session, logs no update, calls no model, and returns an empty result; "
              "the tenant's first message is the first turn",
              nothing == Result() and [e["kind"] for e in mine] == ["session_started"] and mine[0]["how"] == "existing"
              and humans(visit) == ["Hello?"] and asked.blocks == [{"kind": "reply", "text": "Only after I am asked."}])
        visit.end()
        (MATTERS / "t-smoke-visit-none" / "m-001" / "lease_profile.json").unlink()
        events_before = len(read_events())
        try:
            Visit.existing("t-smoke-visit-none", "m-001", "x")
            raised = None
        except ValueError as error:
            raised = str(error)
        check("item 115: Visit.existing refuses a matter with no lease profile, and opens no session and logs nothing",
              raised == "This matter has no lease profile yet. Start a new matter with the lease instead."
              and len(read_events()) == events_before)
    finally:
        remove_scratch("t-smoke-visit-none")

    # ---- A model error comes back as a caution, with the whole error to stderr; the note is kept for the next message. A lease
    # that cannot be read ends the session it opened and raises.
    agent.agent_llm = StandIn(messages=iter([]))                          # a stand-in with nothing left to say
    make_scratch("t-smoke-visit-error", skills=["deposit_not_returned"], facts={}, proposed={})
    try:
        visit, nothing = quiet(Visit.existing, "t-smoke-visit-error", "m-001")
        visit.note = "[Program note: x]\n"
        with contextlib.redirect_stderr(io.StringIO()) as printed:
            failed = visit.say("Second.")
        check("item 115: when the model cannot be reached the result is one caution naming the error, the whole error goes to "
              "stderr, and the note stays for the tenant's next message",
              kinds(failed) == ["caution"] and failed.blocks[0]["text"].startswith("[Check: the model could not be reached (")
              and failed.rows == [] and "Traceback" in printed.getvalue() and visit.note == "[Program note: x]\n")
        visit.end()
    finally:
        remove_scratch("t-smoke-visit-error")

    def unreadable(pages):
        raise ValueError("the extraction model answered with something that is not JSON")
    agent.extract_profile = unreadable
    remove_scratch("t-smoke-visit-bad")
    try:
        try:
            quiet(Visit.new, "t-smoke-visit-bad", LEASE_PDF, description)
            raised = None
        except ValueError as error:
            raised = str(error)
        events_bad = read_events()
        check("item 115: a lease that cannot be read raises and ends the session it opened (a start with an end, the matter "
              "not saved)", raised and raised.startswith("the extraction model answered")
              and [e["kind"] for e in events_bad] == ["session_started", "session_ended"] and record.session is None
              and not (matter_dir() / "matter.json").exists())
    finally:
        agent.extract_profile = extraction
        remove_scratch("t-smoke-visit-bad")
finally:
    agent.agent_llm, agent.extract_profile = real_llm, real_extract
    for tenant in ("t-smoke-visit", "t-smoke-visit-other", "t-smoke-visit-old", "t-smoke-visit-skip", "t-smoke-visit-none",
                   "t-smoke-visit-error", "t-smoke-visit-bad"):
        remove_scratch(tenant)
record.session = None
check("the visits' scratch matters are removed", not any(m["tenant"].startswith("t-smoke-visit") for m in list_matters())
      and not list(MATTERS.glob("t-smoke-visit*")))

# ---- The terminal is gone (TODO item 115): run.py does not exist, nothing imports it, and no module still has the terminal's
# chat loop, its block printer, or its confirmation. (dev/live_run.py still starts run.py as a subprocess until the eval driver
# is rewritten; it is not imported by anything here.)
terminal = {"agent.py": ("def chat(", "def print_blocks("), "sheet.py": ("def run_sheet(",)}
python_files = [p for p in ROOT.rglob("*.py") if "venv" not in p.parts and "eval_runs" not in p.parts and "docs" not in p.parts
                and "__pycache__" not in p.parts]
check("item 115: run.py is gone and no Python file imports it; the terminal's chat loop, block printer, and confirmation are gone",
      not (ROOT / "run.py").exists()
      and not [p for p in python_files if re.search(r"^\s*(import run\b|from run import)", p.read_text(), re.M)]
      and not any(old in (ROOT / name).read_text() for name, olds in terminal.items() for old in olds))
print()
