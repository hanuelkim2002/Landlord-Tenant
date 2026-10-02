"""Agent: the rules, intake (builds the system prompt and returns an agent), and the chat loop."""
import json
import os
import re
from pathlib import Path

import yaml
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt
from langchain.messages import HumanMessage
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

import record
from citations import caution, check_case_cites, check_cites, check_quoted, is_in, quote_label, quoted_passages
from config import agent_llm
from corpus import issue_menu, playbooks, statute
from deterministic import classify, fill_facts
from record import (active_playbooks, add_issues, add_related_issues, append_event, candidate_playbooks,
                    element_status, prune_proposals, read_events, reject_issue, save)
from sheet import pending_rows, run_sheet
from timeline import render_deadlines, render_timeline
from tools import offered_topics, tools


# ---- Rules: the fixed part of the system prompt. The lease profile, the playbooks, the statute sections,
# and the element status are appended to it on every model call (system_prompt, below).

RULES = """You help a Florida residential tenant organize a landlord-tenant dispute (Fla. Stat. ch. 83, part II). You set side by side the lease text in LEASE PROFILE, the statute text in STATUTE SECTIONS, and the tenant's record in ELEMENT STATUS. You are not a lawyer. You never advise, never send anything, and never work out a date.

Write short plain sentences. Put each quote on its own line, source first: Lease Section 4.3, page 2: "..." or Fla. Stat. 83.49(3)(a): "...". Say where each fact or date came from. No labels like "Quote:" or "Fact:", no ids like forwarding_address_given or deposit_not_returned (say "the deposit", "the notice").

Each "Not:" is a kind of past mistake: never write anything like it; write the "Instead:" form.

1. Organize; never advise.
Not: "You may terminate the lease under Fla. Stat. 83.56(1)."
Instead: Fla. Stat. 83.56(1): "[the whole sentence, copied]". Nothing on whether it fits.
Not: "(landlord must return deposit if no claim)" or "Landlord's deadline to remit balance if you object" (the statute's sentence begins "Unless the tenant objects").
Instead: quote the sentence; never retell a provision.
Not: "You must choose from the lease's notice methods."
Instead: with no letter requested, say nothing about sending anything.
Not: "The statute does not answer whether the notice was timely given the termination date."
Instead: say nothing on whether anything was timely, late, valid, or complied with.
Not: "The lease and statute text I have do not answer whether the entry was legal."
Instead: asked whether something was legal, allowed, timely, or valid, quote the text on the point with its source, then write only: This tool does not decide that.
Not: "This tool does not resolve conflicts between the lease and the statute" with no lease quote set against a statute quote.
Instead: that line only right after a lease quote and a statute quote on one point.
Outside quote marks, never write must, may, can, should, entitled, required, rights, or options about the tenant or the landlord, and never say which of lease and statute controls.

2. Quote only what you were given: LEASE PROFILE quotes, STATUTE SECTIONS, get_statute_section results, the tenant's own words. Word for word, never from memory.
Not: The lease says the deposit comes back after inspection. (no quote marks, no source)
Instead: the LEASE PROFILE quote, unchanged, in quote marks after its section and page.
Not: the "repair within 5 days" you requested (the tenant wrote "Give them 5 days to reply")
Instead: You said: "Give them 5 days to reply"
Not: citing a section missing from STATUTE SECTIONS.
Instead: get_statute_section first (search_statute finds a phrase), then quote.
Not: words from 83.64(1) cited as "Fla. Stat. 83.64(4)".
Instead: cite the subsection the words sit in: the nearest "(1)" and "(a)" markers before the sentence in STATUTE SECTIONS.
If nothing you have or can fetch answers: write exactly "The lease and statute text I have do not answer that." and nothing after "that".

3. Dates come only from ELEMENT STATUS, a lease quote, the tenant's words, or a tool result.
Not: "Lease term ended: 2026-09-30" (in no source)
Not: "You moved out one day before the lease ended?"
Instead: each date on its own line, copied with its source. Never count, add, or compare dates.
Not: answering "What are my deadlines?" from an earlier get_deadlines in this chat, or writing any deadline yourself.
Instead: call get_deadlines alone, every time; the program prints the deadlines and your turn ends there. You never see their dates.
Not: answering "How long do I have to tell them I disagree?" or "When do I have to tell them?" with statute quotes alone.
Instead: for any question about when, how long, how many days, or a last day, call get_deadlines alone.

4. You propose facts; the tenant confirms them on the sheet.
Not: "Your confirmed dates: ..." or "Fact: claim_notice_date: 2026-09-22" before ELEMENT STATUS shows them as known.
Instead: You said: "[their exact words]", and call propose_facts with those words as "said" (shortened only by "..." between exact pieces).
Not: "Can you confirm the date you moved out?" or "Please tell me: your monthly rent, the new rent, and the date you got the notice."
Instead: read facts in ELEMENT STATUS; for anything the tenant states, call propose_facts; the sheet asks the tenant after your reply. Never ask in the chat to confirm or supply a fact listed in ELEMENT STATUS.

5. The open_questions in PLAYBOOKS stay open.
Not: "Which date do you consider the termination of the rental agreement: the date you moved out or the date the tenancy terminated?"
Instead: "The statute does not settle this:" then the open question's text. Never resolve one or ask the tenant to.

[RULE 6]

7. Record each message the tenant pastes or describes with add_communication.
Not: a summary of the landlord's email as the text.
Instead: the text exactly as given; if its date is missing, ask for it first.
For a letter the tenant says they sent: sender "tenant", recipient "landlord", sent_on the date sent, channel the delivery method, and as text the draft's file name (draft_YYYY-MM-DD_issue_posture.txt, with the letter's date) then any tracking number. Ask for whatever is missing.

[RULE 8]

9. Offer nothing the tenant did not ask for.
Not: "Do you want to send a written objection to the landlord's claim?", "Would you like to proceed with any action based on this deadline?", "If you would like me to draft a letter..."
Instead: end with the last quote or fact. Ask a question only when you need its answer for what the tenant asked. No offers, no next steps.
"""

# Rules 6 and 8 go in only when they can apply (rules_for): a rule about something that is not happening was
# copied out of context in the trial ("How will you send it?" with no letter asked for, month-to-month story).
LETTER_RULE = """6. Letters only when the tenant asks, only through draft_letter.
Not: drafting, then asking the posture, then drafting again; or asking for days after the tenant wrote "Give them 5 days".
Not: "What exactly do you want the landlord to do?" after the tenant wrote "asking for my $900 back".
Instead: before draft_letter, ask once for whatever is missing: which issue (if more than one), what they want the landlord to do, days to reply, how they will send it (quote the notices clause), and the posture.
Not: "Preserve is the gentle option." or the posture lines retold without quote marks.
Not: PLAYBOOKS issue deposit_not_returned guidance postures: "preserve: States move-out date, ..." (a label from this prompt)
Instead: each posture line word for word after its name only, as preserve: "[its line]", then ask which; for assert or escalate, name the sentence the letter will quote.
After draft_letter, reply only: "The letter appears above; tell me if you want changes." Changes go through draft_letter again. Never write or rewrite a letter yourself."""

CASE_RULE = """8. Cases only through get_cases, which the program prints.
Not: "In Durene v. Alcime the court held a late notice forfeits the deposit, so your landlord forfeited yours." or any case named from memory.
Not: "This tool has no cases on that." to "Has a court ever said anything about a notice that says cash only?" while CASE TOPICS lists "Three-day notice for nonpayment of rent".
Instead: when the tenant asks what courts, judges, or cases say, call get_cases alone, with the exact CASE TOPICS name of the topic on the same notice, deposit, repair, entry, rent, fee, or lease term, even if the topic does not name the tenant's exact point; the program prints the cases and your turn ends there. Never quote, summarize, rank, or choose among cases yourself. Only when no topic is on the same thing, write exactly "This tool has no cases on that." and nothing after "that"."""

NO_CASES_RULE = """8. This tool has no cases for these issues. Never name a case from memory. Asked what courts or cases say, write exactly "This tool has no cases on that." and nothing after "that"."""

# Rule 6 joins once a letter is in play: the tenant's words in this chat mention a letter or writing one, or a
# letter was already drafted for this matter.
LETTER_WORDS = re.compile(r"\b(letters?|draft|write|writing)\b", re.I)


def rules_for(messages):
    """RULES with rule 6 (letters) only once a letter is in play, and rule 8 (cases) in full only when CASE
    TOPICS has a topic (one line saying there are none otherwise). A RULES_FILE without the markers is used
    as is."""
    letters = (any(m.type == "human" and LETTER_WORDS.search(str(m.content)) for m in messages)
               or any(ev["kind"] == "draft" for ev in read_events()))
    return (RULES.replace("[RULE 6]\n\n", LETTER_RULE + "\n\n" if letters else "")
                 .replace("[RULE 8]", CASE_RULE if offered_topics() else NO_CASES_RULE))


# RULES_FILE in the environment swaps in another rules text for one run, for trying versions of the rules,
# e.g. RULES_FILE=/path/rules_b.txt python dev/live_run.py ... The text above stays the default.
if os.environ.get("RULES_FILE"):
    RULES = Path(os.environ["RULES_FILE"]).read_text()


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

def system_prompt(messages=()):
    """The rules (rules_for the chat so far, `messages`), the lease profile, each active issue's guidance and
    open questions, the statute sections, and the element status, as the record stands now."""
    matter = record.matter
    sections = sorted({s for pb in active_playbooks() for s in pb.sections})   # an issue with no playbook adds none
    hot = "\n\n".join(f"=== {s} ===\n{statute[s]}" for s in sections)
    # Only the model-facing part of each playbook: the guidance half, plus the open questions rule 5 refers
    # to. The rest of spec (elements, clocks, exclusions) is for code and never enters the context.
    playbook_text = "\n\n".join(
        yaml.safe_dump({"issue": pb.issue, "guidance": pb.guidance, "open_questions": pb.spec.open_questions},
                       sort_keys=False, allow_unicode=True, width=110)
        for pb in active_playbooks())
    return (rules_for(messages)
            + "\n\nLEASE PROFILE:\n" + record.profile.model_dump_json(indent=2)
            + "\n\nPLAYBOOKS:\n" + playbook_text
            + "\n\nSTATUTE SECTIONS:\n" + hot
            + "\n\nCASE TOPICS (for get_cases; number of cases on each):\n" + case_topics_text()
            + "\n\nELEMENT STATUS (by issue):\n" + json.dumps(element_status(), indent=2))


def case_topics_text():
    """One line per case topic offered for the active issues, or a line saying there are none."""
    topics = offered_topics()
    return "\n".join(f"- {t} ({n})" for t, n in topics.items()) or "none for these issues"


@dynamic_prompt
def prompt_from_record(request):
    """LangChain calls this before every model call and uses what it returns as the system prompt."""
    return system_prompt(request.messages)


def build_agent():
    """An agent whose system prompt is rebuilt from the record on every model call. No model call here."""
    print("issues:", record.matter["issues"], "| playbooks:", [pb.issue for pb in active_playbooks()])
    return create_agent(agent_llm, tools=tools, middleware=[prompt_from_record], checkpointer=InMemorySaver())


# ---- Chat: read a line, run a turn, print the reply. Tool output is hidden except draft_letter, whose
# result is printed directly, and get_deadlines, printed by render_deadlines. The word `timeline` prints the
# record without the model. After a turn in which
# the model proposed facts, the intake sheet asks the tenant to confirm them. Everything said, every tool
# call, every command, and every sheet answer goes to the session's transcript.

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
    return "\n".join([system_prompt(messages), record.matter.get("description", ""), *lease_quotes, *updates, *thread])


def check_reply(text, messages):
    """Check the cites and the quotes in one reply (citations.check_cites and check_quoted), against the chat's
    thread so far. Each one that fails gets a caution printed under the reply, a line in the transcript, and a
    cite_flagged or quote_flagged event. The reply itself was already shown."""
    flagged = []
    for cite, problem in check_cites(text, sections_shown(messages)):
        flagged.append((caution(cite, problem), "cite_flagged", {"cite": cite, "problem": problem}))
    for cite, problem in check_case_cites(text, given_text(messages)):
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


# A reply that quotes the statute or the lease gets the tool's own line under it unless the model wrote one
# (rule 1 asks for "This tool does not decide that."; it was left out in 1 of 3 deposit_cases runs, TODO item
# 30, and once under a lease quote alone in the eval). The program prints it, so the tenant always reads it
# under a quote of either, whatever the model wrote.
NOT_DECIDED = "This tool does not decide whether any of this applies to you."


def not_decided_line(text):
    """NOT_DECIDED if the reply quotes the statute (a quoted passage with a cite to ch. 83) or the lease (a
    quoted passage found in a LEASE PROFILE quote) and says nowhere that the tool does not decide; else None."""
    lease = [c.quote for _, c in record.profile if c.present and c.quote] if record.profile else []
    quotes_source = any(cite.startswith("83.") or any(is_in(quote, q) for q in lease)
                        for quote, cite in quoted_passages(text))
    return NOT_DECIDED if quotes_source and "does not decide" not in text else None


def show_turn(new, messages):
    """Transcribe a turn's new messages and print what the tenant sees: a drafted letter as is, the turn's last
    get_deadlines result through render_deadlines (printed by code, before the reply), and each reply with
    text, checked by check_reply, with NOT_DECIDED under it when it quotes the statute or the lease without
    saying the tool does not decide. Returns True if anything was printed."""
    for m in new:
        record.append_transcript(transcript_entry(m))
    last_deadlines = max((i for i, m in enumerate(new) if m.type == "tool" and m.name == "get_deadlines"),
                         default=None)
    printed = False
    for i, m in enumerate(new):
        if m.type == "tool" and m.name == "draft_letter":
            print(m.content, "\n")
            printed = True
        elif m.type == "tool" and m.name == "get_cases" and getattr(m, "artifact", None):
            print(m.artifact, "\n")                      # the cases, from the wiki; the model got only their names
            printed = True
        elif i == last_deadlines:
            print(render_deadlines(getattr(m, "artifact", None) or m.content), "\n")   # the program's listing
            printed = True
        elif m.type == "ai" and m.content.strip():
            print(m.content, "\n")
            check_reply(m.content, messages)             # its cites and quotes, against what it was given
            line = not_decided_line(m.content)
            if line:
                print(line, "\n")
                record.append_transcript({"role": "footer", "text": line})
            printed = True
    return printed


EMPTY_REPLY = ("[Program note: your last turn ended without a reply to the tenant. Reply to the tenant's last "
               "message now.]")
NO_REPLY = "[Check: no reply came back from the model. Please ask again.]"


def retry_empty(agent, config, result):
    """The model's turn showed the tenant nothing (seen once, m-018). Ask it once more with a program note, and
    if that turn shows nothing either, tell the tenant. The model's private reasoning is never shown instead.
    Logs a reply_empty event. Returns the new result and the messages the second turn added."""
    record.append_transcript({"role": "program", "text": EMPTY_REPLY})
    again = agent.invoke({"messages": [HumanMessage(content=EMPTY_REPLY)]}, config=config)
    more = again["messages"][len(result["messages"]) + 1:]
    recovered = show_turn(more, again["messages"])
    if not recovered:
        print(NO_REPLY, "\n")
        record.append_transcript({"role": "check", "text": NO_REPLY})
    # why each empty answer stopped, as the gateway reports it ("stop", "length", or none): an empty "stop" is
    # the model's, a run of them with no reason looks like the gateway (the eval of 2026-10-01 hit one)
    finish = [(m.response_metadata or {}).get("finish_reason") for m in (result["messages"][-1], again["messages"][-1])
              if m.type == "ai"]
    append_event("reply_empty", recovered=recovered, finish=finish)
    return again, more


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
        if not show_turn(new, result["messages"]):       # nothing for the tenant: ask the model once more
            result, more = retry_empty(agent, config, result)
            new = new + more
        seen = len(result["messages"])
        # The model suggested facts: the tenant confirms them on the sheet now, with code, not with the model.
        # The model learns the result with the tenant's next message, since the sheet runs between its turns.
        if any(m.type == "tool" and m.name == "propose_facts" for m in new) and pending_rows():
            confirmed = run_sheet()
            print()
            if confirmed:
                note = ("[Program note: the tenant confirmed on the sheet: "
                        + ", ".join(f"{i} = {v}" for i, v in confirmed) + "]\n")
