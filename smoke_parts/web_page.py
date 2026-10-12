"""Smoke, part: The web page (app.py), run headless by Streamlit's AppTest on a scratch matter with a stand-in model.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import contextlib
import io
import json
import logging
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
# and a bad cite, the model loading a skill (the sidebar follows) and proposing a fact asked on the page's sheet, the
# note that follows, a model error, and End session. AppTest runs the page in this same program, so the page and
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
    said = "I got a letter from the landlord"
    stand_in = StandIn(messages=iter([
        AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"\nSee also 83.64. You paid $900 *or more*.'),
        AIMessage(content="", tool_calls=[{"name": "load_skill", "id": "a0", "args": {"name": "deposit_claim_received"}}]),
        AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": "a1", "args": {"facts_json": json.dumps(
            {"claim_notice_received": {"value": True, "how": "stated", "said": said}})}}]),
        AIMessage(content=f'You said: "{said}"'),
        AIMessage(content="", tool_calls=[{"name": "get_deadlines", "args": {}, "id": "a2"}]),
        AIMessage(content="")]))                            # asked only for the deadlines: nothing after the listing
    page.session_state["agent"] = create_agent(stand_in, tools=model_tools, checkpointer=InMemorySaver())
    page.session_state["config"] = {"configurable": {"thread_id": page.session_state["session"]}}
    next(b for b in page.button if b.label == "Continue").click().run()
    check("with nothing new and no fact open, the page goes straight to the chat", page.session_state["stage"] == "chat")
    page.chat_input[0].set_value("Was that legal?").run()
    bubbles = [(m.name, [x.value for x in m.markdown]) for m in page.chat_message]
    check("the page shows the model's reply in a speech bubble, the program's caution and line outside it",
          bubbles[-1][0] == "assistant" and "83\\.49\\(3\\)\\(a\\)" in bubbles[-1][1][0]
          and any("[Check: 83.64" in w.value.replace("\\", "") for w in page.warning)
          and any(READING_LINE in i.value.replace("\\", "") for i in page.info))
    check("the page shows a reply as written: a $ starts no math, a * no italics",
          "\\$900 \\*or more\\*" in bubbles[-1][1][0])
    page.chat_input[0].set_value(said).run()
    check("after the model loads a skill and proposes a fact, the page shows the sheet with the suggestion filled in, and "
          "the sidebar adds the skill's description",
          page.session_state["stage"] == "sheet" and page.radio[0].value == "yes"
          and record.matter["skills"] == ["deposit_not_returned", "deposit_claim_received"]
          and any(skills["deposit_claim_received"].description in m.value.replace("\\", "") for m in page.sidebar.markdown))
    next(b for b in page.button if b.label == "Save").click().run()
    while page.session_state["stage"] == "sheet":
        next(b for b in page.button if b.label == "Skip for now").click().run()
    check("the page's sheet confirms the fact, asks the loaded skill's facts next, and leaves skipped facts open",
          record.matter["facts"]["claim_notice_received"] is True
          and any(r["id"] == "claim_notice_date" for r in pending_rows()))
    page.chat_input[0].set_value("What are my deadlines?").run()
    lines = [json.loads(line) for line in (matter_dir() / "sessions" / f"{page.session_state['session']}.jsonl").read_text().splitlines()]
    check("what the sheet confirmed goes to the model with the next message, and the deadlines show in a program box",
          [line["text"] for line in lines if line["role"] == "program"][-1]
          == "[Program note: the tenant confirmed on the sheet: claim_notice_received = True]\n"
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

# a choice on the page's sheet (TODO items 90 to 92): its answers in a list to pick from, saved as the words picked. The
# update typed at the door is the tenant's first message; the stand-in model proposes a fact from it, so the sheet comes.
make_scratch("t-smoke-app-choice", skills=["repair_not_made"], proposed={},
             facts={"problem_description": "no hot water", "problem_started": "2026-09-28", "single_family_or_duplex": False,
                    "caused_by": "nothing anyone did (age, wear, weather)", "wrote_to_landlord": False,
                    "rent_paid_since_known": True, "landlord_response": "nothing", "eviction_action_filed": False})
try:
    page = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py"), default_timeout=60)
    page.run()
    listed = page.sidebar.selectbox[0]
    listed.select_index(listed.options.index("t-smoke-app-choice / m-001")).run()
    next(b for b in page.sidebar.button if b.label == "Open").click().run()
    update = "My hot water stopped working again."
    stand_in = StandIn(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": "c1", "args": {"facts_json": json.dumps(
            {"problem_description": {"value": "the hot water stopped again", "how": "stated",
                                     "said": "My hot water stopped working again"}})}}]),
        AIMessage(content="I have noted that.")]))
    page.session_state["agent"] = create_agent(stand_in, tools=model_tools, checkpointer=InMemorySaver())
    page.session_state["config"] = {"configurable": {"thread_id": page.session_state["session"]}}
    page.text_area[0].set_value(update)
    next(b for b in page.button if b.label == "Continue").click().run()
    logged = [e for e in read_events() if e["kind"] == "tenant_update"]
    check("an update typed at the door is logged as typed and is the tenant's first message: the model answers it and the "
          "page shows the sheet that follows",
          len(logged) == 1 and logged[0]["text"] == update and page.session_state["history"][0] == {"kind": "tenant", "text": update}
          and any(b["kind"] == "reply" and b["text"] == "I have noted that." for b in page.session_state["history"])
          and page.session_state["stage"] == "sheet")
    for _ in range(5):                                  # skip the row for the proposed change; the choice comes next
        if any(sb.label == "Your answer" for sb in page.selectbox):
            break
        next(b for b in page.button if b.label == "Skip for now").click().run()
    picker = next(s for s in page.selectbox if s.label == "Your answer")
    shown_answers = list(picker.options)
    picker.set_value("hot water")
    next(b for b in page.button if b.label == "Save").click().run()
    check("the page asks a choice from a list of its answers and saves the one picked",
          "hot water" in shown_answers and "the air conditioning" in shown_answers
          and record.matter["facts"]["problem_is_with"] == "hot water" and page.session_state["stage"] == "chat")
finally:
    remove_scratch("t-smoke-app-choice")
check("the page's choice scratch matter is removed", not (MATTERS / "t-smoke-app-choice").exists())
