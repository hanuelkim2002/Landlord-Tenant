"""Agent: the rules, reading the lease, intake, the system prompt and the agent, and the chat.

The chat is in pieces any front end can call: turn (one model turn) and command (a chat command) return
blocks, the parts the tenant sees, each {"kind", "text"}. "reply" is the model's words; every other kind is the
program's (see BLOCK KINDS below). The terminal loop, chat, prints them with print_blocks; the web page,
app.py, draws the same blocks.
"""
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
from lease import check_quotes, extract_profile, ingest_pdf
from record import (active_playbooks, add_issues, add_related_issues, append_event, candidate_playbooks,
                    element_status, matter_dir, prune_proposals, read_events, reject_issue, save)
from sheet import pending_rows, run_sheet, stop_text
from timeline import render_deadlines, render_timeline
from tools import deadline_status, offered_topics, tools


# ---- Rules: the fixed part of the system prompt. The lease profile, the playbooks' notes and open questions,
# the statute sections, the case topics, the element status, and the deadline status are appended to it on every
# model call (system_prompt, below), each under a name a tenant can read (PARTS, below; TODO item 61).
# Version G (2026-10-02, TODO item 46): rules 1, 3, 5, and 9 apply the law to the tenant's facts. Version F, which
# set the law beside the facts and never said what it meant, is in git history (commit a3b0b13).

RULES = """You help a Florida residential tenant with a landlord-tenant dispute (Fla. Stat. ch. 83, part II). You apply the lease text in YOUR LEASE, the statute text in THE STATUTE, and the cases get_cases gives you to the tenant's record in YOUR FACTS and THE PROGRAM'S DEADLINES, and say what they mean for the tenant. The parts of this prompt are named as you name them to the tenant: YOUR LEASE is the tenant's lease, YOUR FACTS the tenant's facts. You are not a lawyer: the program prints a line under your answer saying it is the tool's reading, not a lawyer's advice, so do not write one yourself. You never send anything and never work out a date.

Write short plain sentences. Put each quote on its own line, source first: Lease Section 4.3, page 2: "..." or Fla. Stat. 83.49(3)(a): "...". Say where each fact or date came from, in plain lower-case words: "your lease", "the statute", "you confirmed", "the program's deadlines", "the statute does not settle this". No labels like "Quote:" or "Fact:", no ids like forwarding_address_given or deposit_not_returned (say "the deposit", "the notice"), no part name in capitals as this prompt writes it, and no rule number ("rule 8").

Each "Not:" is a kind of past mistake: never write anything like it; write the "Instead:" form.

1. Apply the law to the tenant's facts.
Not: three statute quotes, then "This tool does not decide that." (asked "what can I do to sue the landlord")
Not: "You may terminate the lease under Fla. Stat. 83.56(1)." (a conclusion with no rule quoted and no facts)
Instead: answer a question about the law in this order, each part short:
- The rule: the sentence that answers it, quoted, source first.
- Your facts: each fact the rule turns on, with where it came from (you confirmed it, the lease says it). Something the tenant said in this chat but has not confirmed: You said: "[their words]", not known yet until the sheet confirms it (rule 4).
- Applied: for each condition in the rule, whether those facts meet it, fail it, or are not known yet.
- So: what follows on those facts, in plain words. Asked what they can do: each option the stored text gives and what it requires first (a written notice, a waiting period, rent paid into the court registry). search_statute and get_statute_section find a section that is not in THE STATUTE, such as 83.55 on damages or 83.48 on attorney fees.
- Cases: when a case topic is on the point, as rule 8 says.
- Not settled: an open question in the way, with its readings (rule 5).
Not: "No written claim notice received: claim_notice_received false (user)" or "(YOUR FACTS shows eviction_action_filed: true)" (ids, and part names as this prompt writes them)
Instead: "You confirmed you got no written notice from the landlord." and "The program's deadlines show the 30-day deadline has passed."
Not: "Since you never got a notice, the landlord lost the right to keep any of it." while YOUR FACTS does not show that fact.
Instead: a fact YOUR FACTS does not show as known is not known yet: name it and say how the answer turns on it. Never assume it.
Not: "You should withhold rent." or "Your best option is to sue."
Instead: lay out the options and what each requires; the tenant chooses.
When the lease and the statute differ on a point, quote both; say which controls only from a stored section (83.47 on lease terms that waive a right in part II).

2. Quote only what you were given: YOUR LEASE quotes, THE STATUTE, get_statute_section results, the tenant's own words. Word for word, never from memory.
Not: The lease says the deposit comes back after inspection. (no quote marks, no source)
Instead: the quote from YOUR LEASE, unchanged, in quote marks after its section and page.
Not: the "repair within 5 days" you requested (the tenant wrote "Give them 5 days to reply")
Instead: You said: "Give them 5 days to reply"
Not: citing a section missing from THE STATUTE.
Instead: get_statute_section first (search_statute finds a phrase), then quote.
Not: words from 83.64(1) cited as "Fla. Stat. 83.64(4)".
Instead: cite the subsection the words sit in: the nearest "(1)" and "(a)" markers before the sentence in THE STATUTE.
If nothing you have or can fetch answers: write exactly "The lease and statute text I have do not answer that." and nothing after "that".
Not: that fallback line to "My notice says I can only pay by money order at the office. Can he do that?" while WHAT THE STATUTE DOES NOT SETTLE has an open question on the notice's form (no stored sentence says "money order").
Instead: the fallback line only when no stored sentence, no open question in WHAT THE STATUTE DOES NOT SETTLE, and no topic in COURT CASES THIS TOOL HAS is on the point. When an open question or a topic is on it, even in other words than the tenant's, give its readings (rule 5) or its cases (rule 8), applied to the facts.

3. Dates come only from YOUR FACTS, a lease quote, the tenant's words, or a tool result.
Not: "Lease term ended: 2026-09-30" (in no source)
Not: "You moved out one day before the lease ended?"
Instead: each date on its own line, copied with its source. Never count, add, or compare dates.
Not: "The 30 days ran out on August 30, so the landlord is late." or any comparison of two dates of your own.
Instead: whether a deadline has passed comes only from THE PROGRAM'S DEADLINES ("passed" or "upcoming"); apply that word. For the date itself, call get_deadlines.
Not: "Even if the clock ran from the move-out date, the 30-day period would have ended on 2026-08-29." (a date worked out for a reading)
Instead: the tool computed its dates from the date you confirmed; from any other date it computes nothing.
Not: answering "What are my deadlines?" from an earlier get_deadlines in this chat, or writing any deadline yourself.
Instead: call get_deadlines every time; the program prints the deadlines above your reply, and you never see their dates. Asked only for the deadlines, add nothing after it. Asked more ("If I get rid of the dog by Friday, am I safe?"), answer the rest as rule 1 says, applying THE PROGRAM'S DEADLINES, never writing a date.
Not: answering "How long do I have to tell them I disagree?" or "When do I have to tell them?" with statute quotes alone.
Instead: for any question about when, how long, how many days, or a last day, call get_deadlines.

4. You propose facts; the tenant confirms them on the sheet.
Not: "Your confirmed dates: ..." or "Fact: claim_notice_date: 2026-09-22" before YOUR FACTS shows them as known.
Instead: You said: "[their exact words]", and call propose_facts with those words as "said" (shortened only by "..." between exact pieces).
Not: "Can you confirm the date you moved out?" or "Please tell me: your monthly rent, the new rent, and the date you got the notice."
Instead: read facts in YOUR FACTS; for anything the tenant states, call propose_facts; the sheet asks the tenant after your reply. Never ask in the chat to confirm or supply a fact listed in YOUR FACTS.

5. The open questions in WHAT THE STATUTE DOES NOT SETTLE stay open, with their readings.
Not: "The termination date is the day you moved out." (an open question settled) or "Which date do you consider the termination of the rental agreement?" (asking the tenant to settle it)
Not: "The statute does not settle this." and nothing more.
Instead: "The statute does not settle this:" then the point in plain words, then each of the open question's readings and what it would mean on the tenant's facts. Never pick one. An open question with no readings is a limit of the tool: say what the tool does not compute.

[RULE 6]

7. Record each message the tenant pastes or describes with add_communication.
Not: a summary of the landlord's email as the text.
Instead: the text exactly as given; if its date is missing, ask for it first.
For a letter the tenant says they sent: sender "tenant", recipient "landlord", sent_on the date sent, channel the delivery method, and as text the draft's file name (draft_YYYY-MM-DD_issue_posture.txt, with the letter's date) then any tracking number. Ask for whatever is missing.

[RULE 8]

9. Offer nothing the tenant did not ask for.
Not: "Do you want to send a written objection to the landlord's claim?", "Would you like to proceed with any action based on this deadline?", "If you would like me to draft a letter..."
Instead: end with the last point of your answer. A step the statute requires before an option belongs in the answer; offering to draft it, or anything else, does not. Ask a question only when you need its answer for what the tenant asked.
"""

# Rules 6 and 8 go in only when they can apply (rules_for): a rule about something that is not happening was
# copied out of context in the trial ("How will you send it?" with no letter asked for, month-to-month story).
LETTER_RULE = """6. Letters only when the tenant asks, only through draft_letter.
Not: drafting, then asking the posture, then drafting again; or asking for days after the tenant wrote "Give them 5 days".
Not: "What exactly do you want the landlord to do?" after the tenant wrote "asking for my $900 back".
Instead: before draft_letter, ask once for whatever is missing: which issue (if more than one), what they want the landlord to do, days to reply, how they will send it (quote the notices clause), and the posture.
Not: "Preserve is the gentle option." or the posture lines retold without quote marks.
Not: THE TOOL'S NOTES ON YOUR ISSUES, deposit_not_returned, postures: "preserve: States move-out date, ..." (labels from this prompt)
Instead: each posture line word for word after its name only, as preserve: "[its line]", then ask which; for assert or escalate, name the sentence the letter will quote.
After draft_letter, reply only: "The letter appears above; tell me if you want changes." Changes go through draft_letter again. Never write or rewrite a letter yourself."""

CASE_RULE = """8. Cases only through get_cases. The program prints them for the tenant, and you get their words to apply.
Not: "In Durene v. Alcime the court held a late notice forfeits the deposit, so your landlord forfeited yours." (a case named from memory, its holding in your own words)
Not: "This tool has no cases on that." to "Has a court ever said anything about a notice that says cash only?" while COURT CASES THIS TOOL HAS lists "Three-day notice for nonpayment of rent".
Instead: when the tenant asks what courts or judges said, or a topic in COURT CASES THIS TOOL HAS is on the point you are applying (the same notice, deposit, repair, entry, rent, fee, or lease term), call get_cases with the topic's exact name from there, even if the topic does not name the tenant's exact point. Then, for every case it gives, not only those that help:
- its facts beside the tenant's: where they match and where they differ;
- its rule, quoted from the result with the case name and page, and the statute version it read when that is not today's text;
- what the rule would mean on the tenant's facts, and whether another case distinguished it.
Say plainly when a case cuts against the tenant. Quote a case only from get_cases' result, and never say a case held anything you do not quote.
Only when no topic is on the same thing, write exactly "This tool has no cases on that." and nothing after "that"."""

NO_CASES_RULE = """8. This tool has no cases for these issues. Never name a case from memory. Asked what courts or cases say, write exactly "This tool has no cases on that." and nothing after "that"."""

# Rule 6 joins once a letter is in play: the tenant's words in this chat mention a letter or writing one, or a
# letter was already drafted for this matter.
LETTER_WORDS = re.compile(r"\b(letters?|draft|write|writing)\b", re.I)


def rules_for(messages):
    """RULES with rule 6 (letters) only once a letter is in play, and rule 8 (cases) in full only when there
    is a case topic (one line saying there are none otherwise). A RULES_FILE without the markers is used
    as is."""
    letters = (any(m.type == "human" and LETTER_WORDS.search(str(m.content)) for m in messages)
               or any(ev["kind"] == "draft" for ev in read_events()))
    return (RULES.replace("[RULE 6]\n\n", LETTER_RULE + "\n\n" if letters else "")
                 .replace("[RULE 8]", CASE_RULE if offered_topics() else NO_CASES_RULE))


# RULES_FILE in the environment swaps in another rules text for one run, for trying versions of the rules,
# e.g. RULES_FILE=/path/rules_b.txt python dev/live_run.py ... The text above stays the default.
if os.environ.get("RULES_FILE"):
    RULES = Path(os.environ["RULES_FILE"]).read_text()


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


# ---- System Prompt and Agent: the prompt is built from whatever the record holds at the moment the model is
# called, on every call, so facts confirmed on the sheet and issues added mid-chat reach the model at once.

# The prompt's parts, in order, each under a name a tenant can read. The model names its sources, and with
# names like "ELEMENT STATUS" and "PLAYBOOKS" it wrote "(ELEMENT STATUS shows ...)" in 17 replies per 100, though
# the rules forbade it (TODO item 61). Under these names, a source named in plain words reads right to the tenant.
PARTS = {
    "lease": "YOUR LEASE (the tenant's lease: each clause quoted, with its section and page)",
    "notes": "THE TOOL'S NOTES ON YOUR ISSUES (by issue: questions, lease checks, evidence, postures, mistakes to avoid)",
    "open": "WHAT THE STATUTE DOES NOT SETTLE (by issue: each open question, its sections, and its readings)",
    "statute": "THE STATUTE (the sections for your issues, Fla. Stat. ch. 83, part II)",
    "cases": "COURT CASES THIS TOOL HAS (topics for get_cases; number of cases on each)",
    "facts": "YOUR FACTS (by issue: known, changed, proposed, missing, or n/a, and where each came from)",
    "deadlines": "THE PROGRAM'S DEADLINES (passed or upcoming; no dates here, get_deadlines prints them)",
}


def system_prompt(messages=()):
    """The rules (rules_for the chat so far, `messages`), then each part under its name in PARTS: the lease
    profile, each active issue's guidance, its open questions, the statute sections, the case topics, the element
    status, and the deadline status (tools.deadline_status: passed or upcoming, no dates), as the record stands
    now."""
    sections = sorted({s for pb in active_playbooks() for s in pb.sections})   # an issue with no playbook adds none
    hot = "\n\n".join(f"=== {s} ===\n{statute[s]}" for s in sections)
    # Only the model-facing part of each playbook: the guidance half, and the open questions rule 5 refers to,
    # each in its own part. The rest of spec (elements, clocks, exclusions) is for code and never enters the
    # context. The open questions go in without their ids: no tool takes one, and the model copied them into
    # replies (TODO item 53).
    dump = lambda data: yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=110)
    notes = "\n\n".join(dump({"issue": pb.issue, **pb.guidance}) for pb in active_playbooks())
    open_text = "\n\n".join(
        dump({"issue": pb.issue,
              "open_questions": [{k: v for k, v in q.items() if k != "id"} for q in pb.spec.open_questions]})
        for pb in active_playbooks() if pb.spec.open_questions) or "none listed for these issues"
    return (rules_for(messages)
            + f"\n\n{PARTS['lease']}:\n" + record.profile.model_dump_json(indent=2)
            + f"\n\n{PARTS['notes']}:\n" + notes
            + f"\n\n{PARTS['open']}:\n" + open_text
            + f"\n\n{PARTS['statute']}:\n" + hot
            + f"\n\n{PARTS['cases']}:\n" + case_topics_text()
            + f"\n\n{PARTS['facts']}:\n" + json.dumps(element_status(), indent=2)
            + f"\n\n{PARTS['deadlines']}:\n" + deadline_status())


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


# ---- Chat: a turn of the model, or a chat command the program answers itself. Both return blocks, the parts
# the tenant sees, in order. Tool output is hidden except draft_letter, whose result is shown as is, and
# get_deadlines and get_cases, whose listings the program shows. After a turn in which the model proposed facts,
# the intake sheet asks the tenant to confirm them. Everything said, every tool call, every command, and every
# sheet answer goes to the session's transcript.
#
# BLOCK KINDS. From the model: "reply". From the program: "letter" (draft_letter's result), "cases" (get_cases'
# listing), "deadlines" (get_deadlines' listing, through render_deadlines), "caution" (a failed cite or quote
# check, or no reply), "footer" (READING_LINE under a reply), "timeline", "notice" (a command's answer), "stop"
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


def sections_shown(messages):
    """The sections the model could cite from: THE STATUTE in its prompt (the active playbooks' sections) plus every
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
    thread so far. Each one that fails gets a caution line, shown under the reply, a line in the transcript, and
    a cite_flagged or quote_flagged event. Returns the caution lines. The reply itself is not changed."""
    flagged = []
    for cite, problem in check_cites(text, sections_shown(messages)):
        flagged.append((caution(cite, problem), "cite_flagged", {"cite": cite, "problem": problem}))
    for cite, problem in check_case_cites(text, given_text(messages)):
        flagged.append((caution(cite, problem), "cite_flagged", {"cite": cite, "problem": problem}))
    for quote, cite, problem in check_quoted(text, given_text(messages)):
        flagged.append((caution(quote_label(quote, cite), problem), "quote_flagged",
                        {"quote": quote, "cite": cite, "problem": problem}))
    for line, kind, data in flagged:
        record.append_transcript({"role": "check", "text": line})
        append_event(kind, **data)
    return [line for line, _, _ in flagged]


# A reply that quotes the statute or the lease is the tool applying the law, so the program prints its own line
# under it: the answer is the tool's reading, not a lawyer's advice (README, Purpose). The model is told not to
# write one. Was NOT_DECIDED, "This tool does not decide whether any of this applies to you." (TODO item 30),
# from when the tool only set the law beside the facts.
READING_LINE = "This is the tool's reading of the stored law and your confirmed facts, not a lawyer's advice."
# A reply the gateway stopped at the length limit reads as if it were whole; the tenant is told it is not.
CUT_OFF = "[Check: this reply was cut off at the model's length limit. Ask again for the rest.]"


def reading_line(text):
    """READING_LINE if the reply quotes the statute (a quoted passage with a cite to ch. 83) or the lease (a
    quoted passage found in a lease profile quote) and does not already carry the line; else None."""
    lease = [c.quote for _, c in record.profile if c.present and c.quote] if record.profile else []
    quotes_source = any(cite.startswith("83.") or any(is_in(quote, q) for q in lease)
                        for quote, cite in quoted_passages(text))
    return READING_LINE if quotes_source and READING_LINE not in text else None


def turn_blocks(new, messages):
    """Transcribe a turn's new messages and return what the tenant sees, as blocks: a drafted letter as is, the
    cases get_cases printed, the turn's last get_deadlines result through render_deadlines (shown by code,
    before any reply), and each reply with text, then the cautions check_reply finds in it (and CUT_OFF when the
    reply stopped at the length limit), then READING_LINE when it quotes the statute or the lease. Empty when the
    turn showed the tenant nothing."""
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


def thread_config():
    """The chat thread's config. The thread takes the session's id, so the conversation and the record's events
    share one id."""
    return {"configurable": {"thread_id": record.session or str(uuid7())}}


def turn(agent, config, text, note=""):
    """One turn of the model on the tenant's message, with any note from the sheet in front of it. The message
    goes to the transcript before the model runs (propose_facts checks the tenant's words against it). A turn
    that shows the tenant nothing is asked once more (retry_empty). Returns the turn's blocks, and whether the
    model proposed facts, so the sheet comes next."""
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
