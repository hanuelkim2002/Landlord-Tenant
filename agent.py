"""Agent: reading the lease, intake and resume, the agent, and the chat. What the model reads is in prompt.py, and
what the program checks and prints under each reply in replies.py.

The chat is in pieces any front end can call: turn (one model turn) and command (a chat command) return
blocks, the parts the tenant sees, each {"kind", "text"}. "reply" is the model's words; every other kind is the
program's (see BLOCK KINDS below). The terminal loop, chat, prints them with print_blocks; the web page,
app.py, draws the same blocks.
"""
import re

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain.messages import HumanMessage
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

import record
from config import agent_llm
from corpus import issue_menu, playbooks
from deterministic import classify, fill_facts
from lease import check_quotes, extract_profile, ingest_pdf
from prompt import system_prompt
from record import (active_playbooks, add_issues, add_related_issues, append_event, candidate_playbooks, matter_dir,
                    prune_proposals, reject_issue, save)
from replies import CASES_LEFT_OUT, CUT_OFF, cases_left_out, check_reply, cited_words, reading_line
from sheet import pending_rows, run_sheet, stop_text
from timeline import render_deadlines, render_timeline
from tools import deadline_listing, tools


# ---- The lease and intake: read the lease into its profile, then classify the description and propose facts.
# The sheet and the agent come after, in run.py or app.py.

def read_lease(pdf_path):
    """Store the PDF, read it with Gemma into the lease profile, check every quote, save the profile."""
    pages = ingest_pdf(pdf_path, matter_dir())
    record.profile = extract_profile(pages)
    check_quotes(record.profile, pages)
    (matter_dir() / "lease_profile.json").write_text(record.profile.model_dump_json(indent=2))


def intake(description):
    """Classify, fill facts for every matching playbook, save. For a new matter only. The agent is built
    afterwards (build_agent), once the intake sheet has run, so the prompt shows the confirmed facts."""
    matter = record.matter
    matter["description"] = description
    matter["issues"] = []
    matter["facts"] = {}
    matter["proposed"] = {}
    add_issues(classify(description, issue_menu())["issues"], "classify", "the tenant's description")
    for pb in candidate_playbooks():                       # suggested issues too; first to propose a fact wins
        for fact_id, p in fill_facts(description, pb).items():
            matter["proposed"].setdefault(fact_id, p)
    prune_proposals()                                      # e.g. a deposit amount the lease already gives
    save(matter)
    print("proposed:", list(matter["proposed"]))


# ---- Resume: an existing matter, and the tenant says what is new since last time.

def resume(update_text):
    """Record the update, add any new issues, propose facts from the update, return the issues it added. The
    agent is built afterwards.
    Classifies only the update (the old issues are already known) and never removes an issue. Proposes
    for every active playbook, old and new: a value equal to a confirmed fact is dropped, a value that
    differs from one shows up as "changed" in the element status, and a new one as "proposed"."""
    matter = record.matter
    append_event("tenant_update", text=update_text)        # the update, verbatim; description stays the first story

    new_issues = add_issues(classify(update_text, issue_menu())["issues"], "classify", "the tenant's update")
    new_issues += add_related_issues()                     # facts already confirmed may bring in more

    fresh = {}
    for pb in candidate_playbooks():                       # suggested issues too; first to propose a fact wins
        for fact_id, p in fill_facts(update_text, pb).items():
            if fact_id in matter["facts"] and matter["facts"][fact_id] == p["value"]:
                continue                                   # the tenant already confirmed this value
            fresh.setdefault(fact_id, p)
    matter["proposed"].update(fresh)                       # a newer suggestion replaces an older pending one
    prune_proposals()
    save(matter)
    print("new issues:", new_issues, "| proposed from update:", list(fresh))
    return new_issues


# ---- The Agent: its system prompt (prompt.system_prompt) is rebuilt from the record on every model call.

@dynamic_prompt
def prompt_from_record(request):
    """LangChain calls this before every model call and uses what it returns as the system prompt."""
    return system_prompt(request.messages)


def build_agent():
    """An agent whose system prompt is rebuilt from the record on every model call. No model call here."""
    print("issues:", record.matter["issues"], "| playbooks:", [pb.issue for pb in active_playbooks()])
    return create_agent(agent_llm, tools=tools, middleware=[prompt_from_record], checkpointer=InMemorySaver())


# ---- Chat: a turn of the model, or a chat command the program answers itself. Both return blocks, the parts
# the tenant sees, in order. Tool output is hidden except draft_letter, whose result is shown as is, and
# get_deadlines and get_cases, whose listings the program shows. After a turn in which the model proposed facts,
# the intake sheet asks the tenant to confirm them. Everything said, every tool call, every command, and every
# sheet answer goes to the session's transcript.
#
# BLOCK KINDS. From the model: "reply". From the program: "letter" (draft_letter's result), "cases" (get_cases'
# listing), "deadlines" (get_deadlines' listing, through render_deadlines), "sources" (the statute and lease words a
# reply cites, cited_words), "caution" (a failed cite or quote check, or no reply), "footer" (READING_LINE under a reply), "timeline", "notice" (a command's answer), "stop"
# (nothing the tool covers is left).

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


def command(text):
    """A chat command, answered by the program without the model: issues (the active and suggested issues),
    drop <issue> (takes an active issue out, logged), timeline [full] [<issue>]. Returns its blocks, or None
    when the text is not a command. After a drop, no covered issue may be left (active_playbooks): the chat
    ends there."""
    lowered = text.strip().lower()
    if lowered == "issues":                             # the matter's issues, from the record
        record.append_transcript({"role": "command", "text": text})
        lines = [f"  {i}: {playbooks[i].description if i in playbooks else 'not covered by this tool'}"
                 for i in record.matter["issues"]]
        lines += [f"  {p['issue']}: suggested, not yet confirmed" for p in record.matter["proposed_issues"]]
        return [block("notice", "\n".join(lines))]
    if lowered.startswith("drop "):                     # the tenant takes an issue out of the matter
        record.append_transcript({"role": "command", "text": text})
        issue = text.split(maxsplit=1)[1].strip()
        if issue not in record.matter["issues"] or issue not in playbooks:
            return [block("notice", f"No active issue named {issue}. Type issues to see them.")]
        reject_issue(issue, "issue_dropped")
        save(record.matter)
        blocks = [block("notice", f"Dropped {issue} from this matter. It is logged, and it can be suggested again later.")]
        if not active_playbooks():
            blocks.append(block("notice", "No issue this tool covers is left in this matter, so the chat ends here."))
        return blocks
    if lowered.startswith("timeline"):
        record.append_transcript({"role": "command", "text": text})
        words = text.split()[1:]
        full = "full" in words
        issue = next((w for w in words if w != "full"), None)
        if issue and issue not in record.matter["issues"]:
            return [block("notice", f"No issue named {issue} in this matter. Active issues: {record.matter['issues']}")]
        return [block("timeline", render_timeline(issue, full))]
    return None


def stop_block():
    """What the tenant reads when nothing the tool covers is left (sheet.stop_text), as a block, written to the
    transcript as printed."""
    shown = stop_text()
    record.append_transcript({"role": "printed", "text": shown})
    return block("stop", shown)


def chat(agent):
    """The terminal chat: read a line, answer a command or run a turn, print the blocks, and run the intake
    sheet after a turn in which the model proposed facts. An empty line or bye ends it."""
    config = thread_config()
    note = ""           # what the tenant confirmed on a sheet since the model last ran; goes with the next message
    while True:
        q = input(">> ")
        if q in ("", "bye"):
            break
        blocks = command(q)
        if blocks is not None:
            print_blocks(blocks)
            if not active_playbooks():                  # a drop took out the last covered issue
                break
            continue
        blocks, proposed = turn(agent, config, q, note)
        print_blocks(blocks)
        note = ""
        # The model suggested facts: the tenant confirms them on the sheet now, with code, not with the model.
        # The model learns the result with the tenant's next message, since the sheet runs between its turns.
        if proposed and pending_rows():
            confirmed = run_sheet()
            print()
            note = sheet_note(confirmed)
