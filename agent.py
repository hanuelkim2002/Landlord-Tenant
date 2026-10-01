"""Agent: the rules, intake (builds the system prompt and returns an agent), and the chat loop."""
import json

import yaml
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain.messages import HumanMessage
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

import record
from citations import caution, check_cites, check_quoted, quote_label
from config import agent_llm
from corpus import issue_menu, playbooks, statute
from deterministic import classify, fill_facts
from record import (active_playbooks, add_issues, add_related_issues, append_event, candidate_playbooks,
                    element_status, prune_proposals, read_events, reject_issue, save)
from sheet import pending_rows, run_sheet
from timeline import render_timeline
from tools import tools


# ---- Rules: the fixed part of the system prompt. The lease profile, the playbooks, the statute sections,
# and the element status are appended to it on every model call (system_prompt, below).

RULES = """You help a Florida residential tenant organize a landlord-tenant dispute. You are not a lawyer. You give no
legal advice, make no recommendations, and never send anything.

Rules:
1. A reply is built only from these parts, under short labels:
   (a) a quote from the lease or the statute, in quote marks, with its source (rule 2);
   (b) a fact from ELEMENT STATUS or a line from a tool's result, as it appears there;
   (c) a plain statement that the statute does not answer or does not settle a question (rules 2 and 5);
   (d) a question to the tenant.
   Put each fact, date, and quote on its own line, without connecting them. Never say what a provision means
   for the tenant: not what either party did, must do, may do, or is relieved of; not what a passed deadline
   means; not the tenant's rights or options; not which of the lease or the statute controls. No section
   like "what this means" or "key points". When a lease quote and a statute quote on the same point appear
   together, add one line: this tool does not resolve conflicts between them. Do not offer a letter or
   suggest a next step; wait for the tenant to ask.
2. Quote only text you were given: the LEASE PROFILE quotes, the STATUTE SECTIONS, what get_statute_section
   returns, and the tenant's own words, exactly as written. Never state a provision in your own words: quote
   it or leave it out. To mention a section not in STATUTE SECTIONS, call get_statute_section for it first
   (search_statute finds which section has a phrase). If nothing you have or can fetch answers a question,
   say so plainly and add nothing of your own.
3. Every date you write must appear in ELEMENT STATUS, a lease quote, or a tool's result. Never count, add,
   compare, or work out days or dates. For deadlines, call get_deadlines and report what it returns: each
   deadline with its "counting" line, and the issues still waiting with their open facts.
4. Only the tenant confirms facts, on a sheet the program shows after your reply. When the tenant says
   something that answers a missing fact or differs from a known one, call propose_facts, and do not ask
   them to confirm it in the chat. A fact is confirmed only when ELEMENT STATUS shows it as known. For
   anything else write "you said", never "confirmed" or "recorded".
5. The open_questions in PLAYBOOKS are unsettled. When one comes up, say the statute does not settle it.
6. Letters come only from draft_letter, and only when the tenant asks for one. First ask: which issue (if
   the matter has more than one), what they want the landlord to do, how many days to give for a reply, and
   how they will send it (quote the lease's notices clause; do not tell them which method to use). Show the
   preserve, assert, and escalate lines from the playbook's postures, copied word for word, and ask which
   they want; for assert or escalate, name the sentence the letter will quote. The letter is shown to the
   tenant automatically: reply with one sentence saying it appears above and asking whether they want
   changes. For changes, call draft_letter again. Never write or rewrite a letter yourself.
7. When the tenant pastes or describes a message with the landlord, call add_communication with the text
   exactly as given; if the message's date is not shown, ask for it first. When the tenant says they sent a
   letter, call add_communication with sender "tenant", recipient "landlord", the delivery method as the
   channel, and as text the draft's file name (e.g. "draft_2026-09-15_deposit_not_returned_assert.txt")
   followed by any tracking or receipt number. Ask for whichever of those they did not give.
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


def sections_shown(messages):
    """The sections the model could cite from: its STATUTE SECTIONS (the active playbooks' sections) plus every
    section it fetched with get_statute_section in this chat's thread."""
    fetched = {c["args"].get("section") for m in messages if m.type == "ai"
               for c in m.tool_calls if c["name"] == "get_statute_section"}
    return {s for pb in active_playbooks() for s in pb.sections} | fetched


def given_text(messages):
    """Everything the model was given, as one string, for citations.check_quoted: the system prompt, the lease
    quotes as plain text (the prompt holds them as JSON, with quote marks escaped), the tenant's description
    and updates, and every message in the thread the model did not write (the tenant's messages, program
    notes, tool results)."""
    lease_quotes = ([getattr(record.profile, f).quote or "" for f in type(record.profile).model_fields]
                    if record.profile else [])
    updates = [ev["text"] for ev in read_events() if ev["kind"] == "tenant_update"]
    thread = [str(m.content) for m in messages if m.type != "ai"]
    return "\n".join([system_prompt(), record.matter.get("description", ""), *lease_quotes, *updates, *thread])


def check_reply(text, messages):
    """Check the cites and the quotes in one reply (citations.check_cites and check_quoted), against the chat's
    thread so far. Each one that fails gets a caution printed under the reply, a line in the transcript, and a
    cite_flagged or quote_flagged event. The reply itself was already shown."""
    flagged = []
    for cite, problem in check_cites(text, sections_shown(messages)):
        flagged.append((caution(cite, problem), "cite_flagged", {"cite": cite, "problem": problem}))
    for quote, cite, problem in check_quoted(text, given_text(messages)):
        flagged.append((caution(quote_label(quote, cite), problem), "quote_flagged",
                        {"quote": quote, "cite": cite, "problem": problem}))
    for line, kind, data in flagged:
        print(line)
        record.append_transcript({"role": "check", "text": line})
        append_event(kind, **data)
    if flagged:
        print()


def chat(agent):
    # The chat thread takes the session's id, so the conversation and the record's events share one id.
    config = {"configurable": {"thread_id": record.session or str(uuid7())}}
    seen = 0            # result holds the whole thread; seen marks how much we already printed
    note = ""           # what the tenant confirmed on a sheet since the model last ran; goes with the next message
    while True:
        q = input(">> ")
        if q in ("", "bye"):
            break
        if q.strip().lower() == "issues":                   # the matter's issues, from the record
            record.append_transcript({"role": "command", "text": q})
            for i in record.matter["issues"]:
                print(f"  {i}: {playbooks[i].description if i in playbooks else 'not covered by this tool'}")
            for p in record.matter["proposed_issues"]:
                print(f"  {p['issue']}: suggested, not yet confirmed")
            print()
            continue
        if q.strip().lower().startswith("drop "):           # the tenant takes an issue out of the matter
            record.append_transcript({"role": "command", "text": q})
            issue = q.split(maxsplit=1)[1].strip()
            if issue not in record.matter["issues"] or issue not in playbooks:
                print(f"No active issue named {issue}. Type issues to see them.\n")
                continue
            reject_issue(issue, "issue_dropped")
            save(record.matter)
            print(f"Dropped {issue} from this matter. It is logged, and it can be suggested again later.\n")
            if not active_playbooks():
                print("No issue this tool covers is left in this matter, so the chat ends here.\n")
                break
            continue
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
                check_reply(m.content, result["messages"])   # its cites and quotes, against what it was given
        seen = len(result["messages"])
        # The model suggested facts: the tenant confirms them on the sheet now, with code, not with the model.
        # The model learns the result with the tenant's next message, since the sheet runs between its turns.
        if any(m.type == "tool" and m.name == "propose_facts" for m in new) and pending_rows():
            confirmed = run_sheet()
            print()
            if confirmed:
                note = ("[Program note: the tenant confirmed on the sheet: "
                        + ", ".join(f"{i} = {v}" for i, v in confirmed) + "]\n")
