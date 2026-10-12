"""Smoke, part: The web page (app.py), run headless by Streamlit's AppTest on a scratch matter with a stand-in model.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import contextlib
import io
import json
import logging
from datetime import date
from pathlib import Path
from langchain.agents import create_agent
from langchain.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from streamlit.testing.v1 import AppTest
import record
from checks import TEST_MATTER, check, make_scratch, remove_scratch
from config import MATTERS
from record import matter_dir, read_events
from sheet import pending_rows
from replies import READING_LINE
from skills import skills
from tools import tools as model_tools
from smoke_parts.common import FORFEIT, StandIn

# ---- The web page (app.py), run headless by Streamlit's AppTest on a scratch matter, with a stand-in model:
# open a saved matter whose sidebar says what it is about, nothing new, a reply with a statute quote, a dollar amount,
# and a bad cite, the model loading a skill (the sidebar follows) and proposing facts confirmed on the page's form (a yes/no
# changed, a date, a text left for later), the note that follows, a model error, and End session. AppTest runs the page in this same program, so the page and
# these checks share record.
logging.getLogger("streamlit").setLevel(logging.ERROR)     # AppTest's warnings about running outside a server
make_scratch("t-smoke-app", skills=["deposit_not_returned"], proposed={},
             facts={**json.loads((TEST_MATTER / "matter.json").read_text())["facts"], "claim_notice_received": False})
try:
    page = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py"), default_timeout=60)
    page.run()
    listed = page.sidebar.selectbox[0]
    listed.select_index(listed.options.index("t-smoke-app / m-001")).run()
    next(b for b in page.sidebar.button if b.label == "Open").click().run()
    check("the page opens a saved matter from the list and starts a session",
          page.session_state["stage"] == "update" and record.matter["tenant"] == "t-smoke-app"
          and read_events()[-1]["kind"] == "session_started")
    check("the sidebar says what the matter is about in the loaded skill's own words, with no id",
          any(m.value.strip("*") == "What this matter is about" for m in page.sidebar.markdown)
          and any(skills["deposit_not_returned"].description in m.value.replace("\\", "") for m in page.sidebar.markdown)
          and not any("deposit_not_returned" in m.value for m in page.sidebar.markdown))
    said = ("I left before the lease was up. I got a letter from the landlord on September 25, 2026. "
            "The landlord said he would send a check.")
    stand_in = StandIn(messages=iter([
        AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"\nSee also 83.64. You paid $900 *or more*.'),
        AIMessage(content="", tool_calls=[{"name": "load_skill", "id": "a0", "args": {"name": "deposit_claim_received"}}]),
        AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": "a1", "args": {"facts_json": json.dumps({
            "early_or_periodic": {"value": True, "how": "inferred", "said": "I left before the lease was up"},
            "claim_notice_date": {"value": "2026-09-25", "how": "stated", "said": "a letter from the landlord on September 25, 2026"},
            "landlord_response": {"value": "said he would send a check", "how": "stated",
                                  "said": "The landlord said he would send a check"}})}}]),
        AIMessage(content='You said: "I left before the lease was up"'),
        AIMessage(content="", tool_calls=[{"name": "get_deadlines", "args": {}, "id": "a2"}]),
        AIMessage(content="")]))                            # asked only for the deadlines: nothing after the listing
    page.session_state["agent"] = create_agent(stand_in, tools=model_tools, checkpointer=InMemorySaver())
    page.session_state["config"] = {"configurable": {"thread_id": page.session_state["session"]}}
    next(b for b in page.button if b.label == "Continue").click().run()
    check("with nothing new and no fact proposed, the page goes straight to the chat", page.session_state["stage"] == "chat")
    page.chat_input[0].set_value("Was that legal?").run()
    bubbles = [(m.name, [x.value for x in m.markdown]) for m in page.chat_message]
    check("the page shows the model's reply in a speech bubble, the program's caution and line outside it",
          bubbles[-1][0] == "assistant" and "83\\.49\\(3\\)\\(a\\)" in bubbles[-1][1][0]
          and any("[Check: 83.64" in w.value.replace("\\", "") for w in page.warning)
          and any(READING_LINE in i.value.replace("\\", "") for i in page.info))
    check("the page shows a reply as written: a $ starts no math, a * no italics",
          "\\$900 \\*or more\\*" in bubbles[-1][1][0])
    page.chat_input[0].set_value(said).run()
    check("after the model loads a skill and proposes facts, the page shows the form with the suggestion filled in (a changed "
          "yes/no first, the old answer beside it), and the sidebar adds the skill's description",
          page.session_state["stage"] == "sheet" and page.radio[0].value == "yes"
          and any("was no, now yes?" in c.value for c in page.caption)
          and record.matter["skills"] == ["deposit_not_returned", "deposit_claim_received"]
          and any(skills["deposit_claim_received"].description in m.value.replace("\\", "") for m in page.sidebar.markdown))
    next(b for b in page.button if b.label == "Save").click().run()
    check("the page asks a date with a date picker holding the suggestion", page.session_state["stage"] == "sheet"
          and page.date_input[0].value == date(2026, 9, 25))
    next(b for b in page.button if b.label == "Save").click().run()
    next(b for b in page.button if b.label == "Skip for now").click().run()
    check("the page's form confirms the facts, leaves the skipped one pending, and says it will be asked again",
          page.session_state["stage"] == "chat" and record.matter["facts"]["early_or_periodic"] is True
          and record.matter["facts"]["claim_notice_date"] == "2026-09-25"
          and [r["id"] for r in pending_rows()] == ["landlord_response"]
          and any("Skipped for now: landlord response." in i.value.replace("\\", "") for i in page.info))
    page.chat_input[0].set_value("What are my deadlines?").run()
    lines = [json.loads(line) for line in (matter_dir() / "sessions" / f"{page.session_state['session']}.jsonl").read_text().splitlines()]
    check("what the sheet confirmed goes to the model with the next message, and the deadlines show in a program box",
          [line["text"] for line in lines if line["role"] == "program"][-1]
          == "[Program note: the tenant confirmed on the sheet: early_or_periodic = True, claim_notice_date = 2026-09-25]\n"
          and page.session_state["history"][-1]["kind"] == "deadlines")
    with contextlib.redirect_stderr(io.StringIO()):                 # the page prints the error's traceback
        page.chat_input[0].set_value("And now?").run()              # the stand-in has nothing left to say
    check("a model error is shown on the page as a caution, and the page goes on",
          page.session_state["history"][-1]["text"].startswith("[Check: the model could not be reached")
          and page.session_state["stage"] == "chat" and not page.exception)
    next(b for b in page.sidebar.button if b.label == "End session").click().run()
    check("End session logs the end and goes back to the start", page.session_state["stage"] == "door"
          and read_events()[-1]["kind"] == "session_ended" and record.session is None)
finally:
    remove_scratch("t-smoke-app")
check("the page's scratch matter is removed", not (MATTERS / "t-smoke-app").exists())

# a county and plain text on the page's form (item 112): a date picker, a county in a line, a text left to correct. The update
# typed at the door is the tenant's first message; the stand-in model proposes facts from it, so the form comes.
make_scratch("t-smoke-app-text", skills=["notice_received_nonpayment"], proposed={}, facts={})
try:
    page = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py"), default_timeout=60)
    page.run()
    listed = page.sidebar.selectbox[0]
    listed.select_index(listed.options.index("t-smoke-app-text / m-001")).run()
    next(b for b in page.sidebar.button if b.label == "Open").click().run()
    update = "The notice was taped to my door on November 24, 2026. I live in Alachua County. The landlord told me to pay in cash."
    stand_in = StandIn(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": "c1", "args": {"facts_json": json.dumps({
            "nonpayment_notice_delivered": {"value": "2026-11-24", "how": "stated", "said": "taped to my door on November 24, 2026"},
            "premises_county": {"value": "Alachua", "how": "stated", "said": "I live in Alachua County"},
            "landlord_instruction": {"value": "pay in cash", "how": "stated", "said": "The landlord told me to pay in cash"}})}}]),
        AIMessage(content="I have noted that.")]))
    page.session_state["agent"] = create_agent(stand_in, tools=model_tools, checkpointer=InMemorySaver())
    page.session_state["config"] = {"configurable": {"thread_id": page.session_state["session"]}}
    page.text_area[0].set_value(update)
    next(b for b in page.button if b.label == "Continue").click().run()
    logged = [e for e in read_events() if e["kind"] == "tenant_update"]
    check("an update typed at the door is logged as typed and is the tenant's first message: the model answers it and the "
          "page shows the form that follows",
          len(logged) == 1 and logged[0]["text"] == update and page.session_state["history"][0] == {"kind": "tenant", "text": update}
          and any(b["kind"] == "reply" and b["text"] == "I have noted that." for b in page.session_state["history"])
          and page.session_state["stage"] == "sheet" and page.date_input[0].value == date(2026, 11, 24))
    next(b for b in page.button if b.label == "Save").click().run()
    county = page.text_input[0]
    check("the page asks a county in a line holding the suggestion", county.label == "County" and county.value == "Alachua")
    next(b for b in page.button if b.label == "Save").click().run()
    page.text_area[0].set_value("pay in cash only")                  # a correction to the suggested words
    next(b for b in page.button if b.label == "Save").click().run()
    lines = [json.loads(line) for line in (matter_dir() / "sessions" / f"{page.session_state['session']}.jsonl").read_text().splitlines()]
    check("the page saves a date, a county, and a corrected text as the tenant confirmed them, and goes back to the chat",
          record.matter["facts"] == {"nonpayment_notice_delivered": "2026-11-24", "premises_county": "Alachua",
                                     "landlord_instruction": "pay in cash only"}
          and page.session_state["stage"] == "chat" and not record.matter["proposed"]
          and [(l["id"], l["typed"], l["value"]) for l in lines if l["role"] == "sheet"] == [
              ("nonpayment_notice_delivered", "", "2026-11-24"), ("premises_county", "", "Alachua"),
              ("landlord_instruction", "pay in cash only", "pay in cash only")])
finally:
    remove_scratch("t-smoke-app-text")
check("the page's text scratch matter is removed", not (MATTERS / "t-smoke-app-text").exists())
