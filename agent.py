"""Agent: the rules, intake (builds the system prompt and returns an agent), and the chat loop."""
import json

import yaml
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain.messages import HumanMessage
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

import record
from config import agent_llm
from corpus import statute
from deterministic import classify, fill_facts
from record import (active_playbooks, add_issues, add_related_issues, append_event, element_status,
                    prune_proposals, save)
from sheet import pending_rows, run_sheet
from timeline import render_timeline
from tools import tools


# ---- Rules: the fixed part of the system prompt. The lease profile, the playbooks, the statute sections,
# and the element status are appended to it on every model call (system_prompt, below).

RULES = """You help a Florida residential tenant organize a landlord-tenant dispute. You are not a lawyer.
You give no legal advice and make no recommendations.
Frame everything as: here is what your lease says, here is what the statute says, here are your dates.

Rules:
1. Quote the lease only from the LEASE PROFILE quotes below. Quote the statute only from the STATUTE
   SECTIONS below or from get_statute_section. Never from memory.
2. Never count, add, or compute days or dates. For any deadline, call get_deadlines and report exactly
   what it returns, including its "counting" line.
3. The tenant confirms facts on a sheet the program shows, not in this chat. ELEMENT STATUS below is
   current as of this reply and shows each fact as known, changed, proposed, missing, or n/a. When the
   tenant says something that answers a missing fact or differs from a known one, call propose_facts with
   the value, "stated" or "inferred", and the tenant's exact words. The sheet appears after your reply; do
   not ask the tenant to confirm in the chat. Do not call get_deadlines while any row is proposed, changed,
   or missing.
4. If the preloaded material does not answer a question, use search_statute or get_statute_section.
   If the statute does not answer it either, say so plainly. Do not fill the gap with your own view.
5. The PLAYBOOK's open_questions are unsettled. When one comes up, say the statute does not settle it.
6. You draft letters only when asked. You never send anything.
7. Never state which controls when the lease and the statute differ, and never explain how they
   interact. Show both texts side by side and say: this tool does not resolve conflicts between them.
8. Before you mention any section not in STATUTE SECTIONS, call get_statute_section for it first
   and quote from what it returns.
9. You cannot confirm or record a fact. Never say a fact is recorded unless ELEMENT STATUS shows it as known.
10. If a question could be about the tenant's notice or the landlord's notice, ask which before answering.
11. When the tenant asks for a letter: if the matter has more than one issue, ask which issue the letter is
    about. Ask what they want the landlord to do, how many days to give for a reply, and how they will send
    it (quote the delivery methods from the lease's notices clause). Tell them which lease or statute
    sentence you will rest the letter on. Explain the three postures in one line each and ask which they
    want. Then call draft_letter. Its output is shown to the tenant automatically. Do not repeat or reformat
    the letter. Reply with one sentence saying the draft appears above and asking whether they want changes.
12. Never write a letter yourself. Every letter comes from draft_letter. If the tenant asks for changes,
    call draft_letter again with different arguments.
13. Never apply a provision to the tenant's facts. Do not say what either party did, failed to do, must do,
    may do, or is relieved of under any provision. Do not say what a deadline's passing means. Do not
    describe the tenant's rights, position, or options. You may place record entries next to a provision
    without connecting them: a confirmed fact, then a computed date with its status, then the quoted
    sentence, each as its own line. No section titled "what this means," "key points," or anything like it.
14. When the tenant pastes or describes a message exchanged with the landlord, call add_communication
    with the date on the message, who sent it, who received it, the channel, and the text exactly as
    pasted. If the date is not shown, ask for it first.
15. When the tenant says they have sent a letter, call add_communication with the date sent, sender
    "tenant", recipient "landlord", the delivery method as the channel, and as text the draft's file name
    (e.g. "draft_2026-09-15_deposit_not_returned_assert.txt") followed by any tracking or receipt number.
    Ask for whichever of those they did not give. You never send anything yourself.
"""


# ---- Intake: classify the description and propose facts. The sheet and the agent come after, in run.py.

def intake(description):
    """Classify, fill facts for every matching playbook, save. For a new matter only. The agent is built
    afterwards (build_agent), once the intake sheet has run, so the prompt shows the confirmed facts."""
    matter = record.matter
    matter["description"] = description
    matter["issues"] = []
    matter["facts"] = {}
    matter["proposed"] = {}
    add_issues(classify(description)["issues"], "classify", "the tenant's description")
    for pb in active_playbooks():                          # first playbook to propose a fact wins
        for fact_id, p in fill_facts(description, pb).items():
            matter["proposed"].setdefault(fact_id, p)
    prune_proposals()                                      # e.g. a deposit amount the lease already gives
    save(matter)
    print("proposed:", list(matter["proposed"]))


# ---- Resume: an existing matter, and the tenant says what is new since last time.

def resume(update_text):
    """Record the update, add any new issues, propose facts from the update. The agent is built afterwards.
    Classifies only the update (the old issues are already known) and never removes an issue. Proposes
    for every active playbook, old and new: a value equal to a confirmed fact is dropped, a value that
    differs from one shows up as "changed" in the element status, and a new one as "proposed"."""
    matter = record.matter
    append_event("tenant_update", text=update_text)        # the update, verbatim; description stays the first story

    new_issues = add_issues(classify(update_text)["issues"], "classify", "the tenant's update")
    new_issues += add_related_issues()                     # facts already confirmed may bring in more

    fresh = {}
    for pb in active_playbooks():                          # first playbook to propose a fact wins, as in intake
        for fact_id, p in fill_facts(update_text, pb).items():
            if fact_id in matter["facts"] and matter["facts"][fact_id] == p["value"]:
                continue                                   # the tenant already confirmed this value
            fresh.setdefault(fact_id, p)
    matter["proposed"].update(fresh)                       # a newer suggestion replaces an older pending one
    prune_proposals()
    save(matter)
    print("new issues:", new_issues, "| proposed from update:", list(fresh))


# ---- System Prompt and Agent: the prompt is built from whatever the record holds at the moment the model is
# called, on every call, so facts confirmed on the sheet and issues added mid-chat reach the model at once.

def system_prompt():
    """The rules, the lease profile, each active issue's guidance and open questions, the statute sections,
    and the element status, as the record stands now."""
    matter = record.matter
    sections = sorted({s for pb in active_playbooks() for s in pb.sections})   # an issue with no playbook adds none
    hot = "\n\n".join(f"=== {s} ===\n{statute[s]}" for s in sections)
    # Only the model-facing part of each playbook: the guidance half, plus the open questions rule 5 refers
    # to. The rest of spec (elements, clocks, exclusions) is for code and never enters the context.
    playbook_text = "\n\n".join(
        yaml.safe_dump({"issue": pb.issue, "guidance": pb.guidance, "open_questions": pb.spec.open_questions},
                       sort_keys=False, allow_unicode=True, width=110)
        for pb in active_playbooks())
    return (RULES
            + "\n\nLEASE PROFILE:\n" + record.profile.model_dump_json(indent=2)
            + "\n\nPLAYBOOKS:\n" + playbook_text
            + "\n\nSTATUTE SECTIONS:\n" + hot
            + "\n\nELEMENT STATUS (by issue):\n" + json.dumps(element_status(), indent=2))


@dynamic_prompt
def prompt_from_record(request):
    """LangChain calls this before every model call and uses what it returns as the system prompt."""
    return system_prompt()


def build_agent():
    """An agent whose system prompt is rebuilt from the record on every model call. No model call here."""
    print("issues:", record.matter["issues"], "| playbooks:", [pb.issue for pb in active_playbooks()])
    return create_agent(agent_llm, tools=tools, middleware=[prompt_from_record], checkpointer=InMemorySaver())


# ---- Chat: read a line, run a turn, print the reply. Tool output is hidden except draft_letter, whose
# result is printed directly. The word `timeline` prints the record without the model. After a turn in which
# the model proposed facts, the intake sheet asks the tenant to confirm them. Everything said, every tool
# call, every command, and every sheet answer goes to the session's transcript.

def transcript_entry(m):
    """One message from the thread as a transcript line: who said it, what, and any tool calls with arguments."""
    if m.type == "human":
        return {"role": "tenant", "text": m.content}
    if m.type == "tool":
        return {"role": "tool", "name": m.name, "text": m.content}
    entry = {"role": "model", "text": m.content}
    if m.tool_calls:
        entry["tool_calls"] = [{"name": c["name"], "args": c["args"]} for c in m.tool_calls]
    return entry


def chat(agent):
    # The chat thread takes the session's id, so the conversation and the record's events share one id.
    config = {"configurable": {"thread_id": record.session or str(uuid7())}}
    seen = 0            # result holds the whole thread; seen marks how much we already printed
    note = ""           # what the tenant confirmed on a sheet since the model last ran; goes with the next message
    while True:
        q = input(">> ")
        if q in ("", "bye"):
            break
        if q.strip().lower().startswith("timeline"):
            record.append_transcript({"role": "command", "text": q})
            words = q.split()[1:]
            full = "full" in words
            issue = next((w for w in words if w != "full"), None)
            if issue and issue not in record.matter["issues"]:
                print(f"No issue named {issue} in this matter. Active issues: {record.matter['issues']}\n")
                continue
            print(render_timeline(issue, full), "\n")
            continue
        record.append_transcript({"role": "tenant", "text": q})   # before the model runs: propose_facts checks it
        if note:
            record.append_transcript({"role": "program", "text": note})
        result = agent.invoke({"messages": [HumanMessage(content=note + q)]}, config=config)
        note = ""
        new = result["messages"][seen + 1:]              # everything new this turn, minus the tenant's message
        for m in new:
            record.append_transcript(transcript_entry(m))
        for m in new:                                    # print the replies, and a letter if one was drafted
            if m.type == "tool" and m.name == "draft_letter":
                print(m.content, "\n")
            elif m.type == "ai" and m.content:
                print(m.content, "\n")
        seen = len(result["messages"])
        # The model suggested facts: the tenant confirms them on the sheet now, with code, not with the model.
        # The model learns the result with the tenant's next message, since the sheet runs between its turns.
        if any(m.type == "tool" and m.name == "propose_facts" for m in new) and pending_rows():
            confirmed = run_sheet()
            print()
            if confirmed:
                note = ("[Program note: the tenant confirmed on the sheet: "
                        + ", ".join(f"{i} = {v}" for i, v in confirmed) + "]\n")
