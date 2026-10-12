"""Agent: reading the lease, intake and resume, the agent, and the chat. What the model reads is in prompt.py, and
what the program checks and prints under each reply in replies.py.

The chat is in pieces any front end can call: turn (one model turn) returns blocks, the parts the tenant sees, each
{"kind", "text"}. "reply" is the model's words; every other kind is the program's (see BLOCK KINDS below). The
terminal loop, chat, prints them with print_blocks; the web page, app.py, draws the same blocks.
"""
import re

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain.messages import HumanMessage
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

import record
from config import agent_llm
from lease import check_quotes, extract_profile, ingest_pdf
from prompt import system_prompt
from record import append_event, matter_dir, save
from replies import CASES_LEFT_OUT, CUT_OFF, cases_left_out, check_reply, cited_words, reading_line
from sheet import pending_rows, run_sheet
from timeline import render_deadlines
from tools import deadline_listing, tools


# ---- The lease and intake: read the lease into its profile, then save the description. No model reads the description
# here: it is sent to the model as the tenant's first chat message (turn), which loads the skills that fit and proposes
# facts. The agent comes after, in run.py or app.py.

def read_lease(pdf_path):
    """Store the PDF, read it with Gemma into the lease profile, check every quote, save the profile."""
    pages = ingest_pdf(pdf_path, matter_dir())
    record.profile = extract_profile(pages)
    check_quotes(record.profile, pages)
    (matter_dir() / "lease_profile.json").write_text(record.profile.model_dump_json(indent=2))


def intake(description):
    """Save the tenant's description of a new matter in matter.json. For a new matter only. No model call: the
    caller builds the agent (build_agent) and sends the description as the tenant's first message (turn)."""
    record.matter["description"] = description
    save(record.matter)


# ---- Resume: an existing matter, and the tenant says what is new since last time.

def resume(update_text):
    """Log what the tenant says is new, verbatim, as a tenant_update event; the description stays the first story.
    No model call: the caller sends the update as the tenant's first message of the visit (turn)."""
    append_event("tenant_update", text=update_text)


# ---- The Agent: its system prompt (prompt.system_prompt) is rebuilt from the record on every model call.

@dynamic_prompt
def prompt_from_record(request):
    """LangChain calls this before every model call and uses what it returns as the system prompt."""
    return system_prompt(request.messages)


def build_agent():
    """An agent whose system prompt is rebuilt from the record on every model call. No model call here."""
    print("skills loaded:", record.matter["skills"])
    return create_agent(agent_llm, tools=tools, middleware=[prompt_from_record], checkpointer=InMemorySaver())


# ---- Chat: a turn of the model returns blocks, the parts the tenant sees, in order. Tool output is hidden except
# draft_letter, whose result is shown as is, and get_deadlines and get_cases, whose listings the program shows. After a
# turn in which the model proposed facts, the intake sheet asks the tenant to confirm them. Everything said, every tool
# call, and every sheet answer goes to the session's transcript.
#
# BLOCK KINDS. From the model: "reply". From the program: "letter" (draft_letter's result), "cases" (get_cases'
# listing), "deadlines" (get_deadlines' listing, through render_deadlines), "sources" (the statute and lease words a
# reply cites, cited_words), "caution" (a failed cite or quote check, or no reply), "footer" (READING_LINE under a
# reply), "notice" (a message from the page itself, such as what was skipped on the sheet).

def block(kind, text):
    """One part of what the tenant sees: its kind (BLOCK KINDS above) and its text."""
    return {"kind": kind, "text": text}


def print_blocks(blocks):
    """The terminal's way of showing blocks: each block's text, then an empty line."""
    for b in blocks:
        print(b["text"] + "\n")


def transcript_entry(m):
    """One message from the thread as a transcript line: who said it, what, and any tool calls with arguments."""
    if m.type == "human":
        return {"role": "tenant", "text": m.content}
    if m.type == "tool":
        entry = {"role": "tool", "name": m.name, "text": m.content}
        if getattr(m, "artifact", None):                   # what the program printed from it (get_cases)
            entry["shown"] = m.artifact
        return entry
    entry = {"role": "model", "text": m.content}
    if m.tool_calls:
        entry["tool_calls"] = [{"name": c["name"], "args": c["args"]} for c in m.tool_calls]
    return entry


def turn_blocks(new, messages):
    """Transcribe a turn's new messages and return what the tenant sees, as blocks: a drafted letter as is, the
    cases get_cases printed, the turn's last get_deadlines result through render_deadlines (shown by code,
    before any reply), and each reply with text, then the words it cites (cited_words, a "sources" block, also
    transcribed as a printed line marked "sources"), then the cautions check_reply finds in it (and CUT_OFF when the
    reply stopped at the length limit), then READING_LINE when it quotes the statute or the lease; last, a caution
    naming any case get_cases printed that no reply after it names (cases_left_out). Empty when the turn showed
    the tenant nothing."""
    for m in new:
        record.append_transcript(transcript_entry(m))
    last_deadlines = max((i for i, m in enumerate(new) if m.type == "tool" and m.name == "get_deadlines"),
                         default=None)
    blocks = []
    for i, m in enumerate(new):
        if m.type == "tool" and m.name == "draft_letter":
            blocks.append(block("letter", m.content))
        elif m.type == "tool" and m.name == "get_cases" and getattr(m, "artifact", None):
            blocks.append(block("cases", m.artifact))       # the cases, from the wiki; the model got only their names
        elif i == last_deadlines:
            blocks.append(block("deadlines", render_deadlines(getattr(m, "artifact", None) or m.content)))
        elif m.type == "ai" and m.content.strip():
            blocks.append(block("reply", m.content))
            cited = cited_words(m.content)                  # the words it cites, printed by the program (item 73)
            if cited:
                blocks.append(block("sources", cited))
                record.append_transcript({"role": "printed", "what": "sources", "text": cited})
            cautions = check_reply(m.content, messages)     # its cites and quotes, against what it was given
            if (m.response_metadata or {}).get("finish_reason") == "length":      # stopped at max_tokens
                cautions.append(CUT_OFF)
                record.append_transcript({"role": "check", "text": CUT_OFF})
            if cautions:
                blocks.append(block("caution", "\n".join(cautions)))
            line = reading_line(m.content)
            if line:
                blocks.append(block("footer", line))
                record.append_transcript({"role": "footer", "text": line})
    left_out = cases_left_out(new)                       # printed cases no reply after them names (item 57)
    if left_out:
        line = CASES_LEFT_OUT.format("; ".join(left_out))
        blocks.append(block("caution", line))
        record.append_transcript({"role": "check", "text": line})
        append_event("cases_left_out", cases=left_out)
    return blocks


EMPTY_REPLY = ("[Program note: your last turn ended without a reply to the tenant. Reply to the tenant's last "
               "message now.]")
NO_REPLY = "[Check: no reply came back from the model. Please ask again.]"


def retry_empty(agent, config, result):
    """The model's turn showed the tenant nothing (seen once, m-018). Ask it once more with a program note, and
    if that turn shows nothing either, tell the tenant. The model's private reasoning is never shown instead.
    Logs a reply_empty event. Returns the new result, the messages the second turn added, and its blocks."""
    record.append_transcript({"role": "program", "text": EMPTY_REPLY})
    again = agent.invoke({"messages": [HumanMessage(content=EMPTY_REPLY)]}, config=config)
    more = again["messages"][len(result["messages"]) + 1:]
    blocks = turn_blocks(more, again["messages"])
    recovered = bool(blocks)
    if not recovered:
        blocks = [block("caution", NO_REPLY)]
        record.append_transcript({"role": "check", "text": NO_REPLY})
    # why each empty answer stopped, as the gateway reports it ("stop", "length", or none): an empty "stop" is
    # the model's, a run of them with no reason looks like the gateway (the eval of 2026-10-01 hit one)
    finish = [(m.response_metadata or {}).get("finish_reason") for m in (result["messages"][-1], again["messages"][-1])
              if m.type == "ai"]
    append_event("reply_empty", recovered=recovered, finish=finish)
    return again, more, blocks


# A question about when, how long, how many days, or a last day (rule 3), answered without get_deadlines: the
# program prints the deadlines itself, above the reply, as get_deadlines would have (TODO item 65). In the evals of
# 2026-10-03 the model answered 1, then 4 of 39 such questions without calling it ("the deadline is seven days
# before your planned move-out date"). "When I moved out" is not a question about when; "When do I have to" is.
WHEN_QUESTION = re.compile(r"\b(when (do|does|did|is|are|was|will|would|can|could|should|must|have|has)|how long|"
                           r"how many days|last day|deadlines?|by when)\b", re.I)


def deadlines_unasked(text, new):
    """The deadlines as a block, printed by the program, when the tenant's message asks about when and the turn's
    new messages hold no get_deadlines call; None otherwise. Written to the transcript as a printed line marked
    "deadlines". deadline_listing logs its deadlines_computed events, as for the tool."""
    if not WHEN_QUESTION.search(text) or any(m.type == "tool" and m.name == "get_deadlines" for m in new):
        return None
    shown = render_deadlines(deadline_listing())
    record.append_transcript({"role": "printed", "what": "deadlines", "text": shown})
    return block("deadlines", shown)


def thread_config():
    """The chat thread's config. The thread takes the session's id, so the conversation and the record's events
    share one id."""
    return {"configurable": {"thread_id": record.session or str(uuid7())}}


def turn(agent, config, text, note=""):
    """One turn of the model on the tenant's message, with any note from the sheet in front of it. The message
    goes to the transcript before the model runs (propose_facts checks the tenant's words against it). A turn
    that shows the tenant nothing is asked once more (retry_empty). A question about when that the model
    answered without get_deadlines gets the deadlines printed by the program, first (deadlines_unasked). Returns
    the turn's blocks, and whether the model proposed facts, so the sheet comes next."""
    record.append_transcript({"role": "tenant", "text": text})
    if note:
        record.append_transcript({"role": "program", "text": note})
    seen = len(agent.get_state(config).values.get("messages", []))     # the thread before this turn
    result = agent.invoke({"messages": [HumanMessage(content=note + text)]}, config=config)
    new = result["messages"][seen + 1:]                  # everything new this turn, minus the tenant's message
    blocks = turn_blocks(new, result["messages"])
    if not blocks:                                       # nothing for the tenant: ask the model once more
        result, more, blocks = retry_empty(agent, config, result)
        new = new + more
    unasked = deadlines_unasked(text, new)               # asked when, and the model did not get the deadlines
    if unasked:
        blocks.insert(0, unasked)
    return blocks, any(m.type == "tool" and m.name == "propose_facts" for m in new)


def sheet_note(confirmed):
    """What the tenant confirmed on a sheet between two turns, sent to the model at the front of the tenant's
    next message, since the sheet runs between the model's turns. "" when nothing was confirmed."""
    if not confirmed:
        return ""
    return "[Program note: the tenant confirmed on the sheet: " + ", ".join(f"{i} = {v}" for i, v in confirmed) + "]\n"


def chat(agent, first=""):
    """The terminal chat: run a turn on each line the tenant types, print the blocks, and run the intake sheet after a
    turn in which the model proposed facts. first is the tenant's first message, sent before any line is read: the
    description of a new matter, or what is new on an existing one. An empty line or bye ends it."""
    config = thread_config()
    note = ""           # what the tenant confirmed on a sheet since the model last ran; goes with the next message
    q = first or input(">> ")
    while q not in ("", "bye"):
        blocks, proposed = turn(agent, config, q, note)
        print_blocks(blocks)
        note = ""
        # The model suggested facts: the tenant confirms them on the sheet now, with code, not with the model.
        # The model learns the result with the tenant's next message, since the sheet runs between its turns.
        if proposed and pending_rows():
            confirmed = run_sheet()
            print()
            note = sheet_note(confirmed)
        q = input(">> ")
