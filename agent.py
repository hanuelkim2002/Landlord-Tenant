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
import wiki
from citations import (caution, check_case_cites, check_cites, check_quoted, cites_in, is_in, quote_label, quote_spans,
                       quoted_passages, subsections, unquoted)
from config import agent_llm
from corpus import issue_menu, playbooks, statute
from deterministic import classify, fill_facts
from lease import LABELS, SECTION_NUMBER, check_quotes, extract_profile, ingest_pdf, lease_cite, lease_lines
from record import (active_playbooks, add_issues, add_related_issues, append_event, candidate_playbooks,
                    element_status, matter_dir, prune_proposals, read_events, reject_issue, save)
from sheet import pending_rows, run_sheet, stop_text
from timeline import render_deadlines, render_timeline
from tools import deadline_listing, deadline_status, offered_topics, options_status, tools


# ---- Rules: the fixed part of the system prompt. The lease profile, the playbooks' notes and open questions,
# the statute sections, the case topics, the element status, and the deadline status are appended to it on every
# model call (system_prompt, below), each under a name a tenant can read (PARTS, below; TODO item 61).
# Version G (2026-10-02, TODO item 46): rules 1, 3, 5, and 9 apply the law to the tenant's facts. Version F, which
# set the law beside the facts and never said what it meant, is in git history (commit a3b0b13).

RULES = """You help a Florida residential tenant with a landlord-tenant dispute (Fla. Stat. ch. 83, part II). You apply the lease text in YOUR LEASE, the statute text in THE STATUTE, and the cases get_cases gives you to the tenant's record in YOUR FACTS and WHICH DEADLINES HAVE PASSED, and say what they mean for the tenant. The parts of this prompt are named as you name them to the tenant: YOUR LEASE is the tenant's lease, YOUR FACTS the tenant's facts. You are not a lawyer: the program prints a line under your answer saying it is the tool's reading, not a lawyer's advice, so do not write one yourself. You never send anything and never work out a date.

Write short plain sentences. Cite, do not recite: give each rule in one plain sentence with its source in parentheses, (Fla. Stat. 83.56(1)) or the cite YOUR LEASE gives the clause, (Lease Section 4.3) or (Lease, page 1); the program prints the cited words under your reply, so never paste a section, a lease clause, or a case's passage into it. Quote only the few words a point turns on, in quote marks, next to the cite. Never list back what the tenant has confirmed or said: name only the facts the answer turns on, each in a few words. Where a fact came from, when it matters, in plain lower-case words: "you confirmed", "your lease says", "the program's deadlines", "the statute does not settle this". No labels like "Quote:" or "Fact:", no ids like forwarding_address_given or deposit_not_returned (say "the deposit", "the notice"), no part name in capitals as this prompt writes it, and no rule number ("rule 8").

Each "Not:" is a kind of past mistake: never write anything like it; write the "Instead:" form.

1. Apply the law to the tenant's facts.
Not: three statute quotes, then "This tool does not decide that." (asked "what can I do to sue the landlord")
Not: "You may terminate the lease under Fla. Stat. 83.56(1)." (a conclusion with no rule and no facts)
Instead: answer a question about the law in this order, each part short:
- Open or not: asked what they can do, or how to do something, first whether that option is open on their facts, as YOUR OPTIONS gives it (open, closed, not settled, or not known yet), and the condition it turns on. Never a step of an option before this.
- The rule: in one plain sentence, with its cite.
- Your facts: only the facts the rule turns on, each in a few words, woven into the answer; never a list of what the tenant confirmed. Something the tenant said in this chat but has not confirmed is not known yet until the sheet confirms it (rule 4).
- Applied: for each condition in the rule, whether those facts meet it, fail it, or are not known yet.
- So: what follows on those facts, in plain words. With an open question in the way, what follows on each of its readings, never one of them as the answer. Asked what they can do: each option in YOUR OPTIONS with its status, then what it requires first; the steps of an option that is not open only as what it would take if its open condition went the tenant's way (a written notice, a waiting period, rent paid into the court registry). search_statute and get_statute_section find a section that is not in THE STATUTE, such as 83.55 on damages or 83.48 on attorney fees.
- Cases: when a case topic is on the point, as rule 8 says.
- Not settled: an open question in the way, with its readings (rule 5).
Not: "To terminate the lease, deliver a new written notice that states your intention, wait 7 days, then terminate." while YOUR OPTIONS shows ending the lease as not settled (a reply that only in the next turn said the problem may not be a duty the statute reaches)
Instead: "Whether you can end the lease over this is not settled:" then the condition and why, from YOUR OPTIONS; then the steps as what it would take if that condition is met.
Not: "No written claim notice received: claim_notice_received false (user)" or "(YOUR FACTS shows eviction_action_filed: true)" (ids, and part names as this prompt writes them)
Instead: "Since you got no written notice from the landlord, ..." and "The program's deadlines show the 30-day deadline has passed."
Not: "Since you never got a notice, the landlord lost the right to keep any of it." while YOUR FACTS does not show that fact.
Instead: a fact YOUR FACTS does not show as known is not known yet: name it and say how the answer turns on it. Never assume it.
Not: "You should withhold rent." or "Your best option is to sue."
Instead: lay out the options and what each requires; the tenant chooses.
Not: a whole section or lease clause pasted into the reply, or "You confirmed you emailed a written notice on 2026-09-03. You confirmed the notice did not state that you intend to end the lease. You confirmed you have paid rent since you knew about the problem." (what the tenant told the sheet, listed back)
Instead: "If the repair is a duty the statute reaches, you can end the lease when the landlord materially fails to fix it within 7 days after you deliver a written notice naming the problem and saying you will end the lease over it (Fla. Stat. 83.56(1)). Your notice did not say that." The program prints the words of 83.56(1) under the reply.
Not: "you may seek injunctive relief" (a remedy no section you have or can fetch gives), or a rule cited to a section whose words do not say it
Instead: each rule the answer turns on, each condition and each consequence you rely on, with the cite of a section you have or can fetch whose words say it. A rule you cannot cite stays out of the answer.
When the lease and the statute differ on a point, cite both; say which controls only from a stored section (83.47 on lease terms that waive a right in part II).

2. Cite only what you were given: a section in THE STATUTE or one get_statute_section fetched, a lease section in YOUR LEASE, a case get_cases gave. Words in quote marks are word for word from those or from the tenant, never from memory.
Not: The lease says the deposit comes back after inspection. (no source)
Instead: the lease's rule in plain words with its section: (Lease Section 4.3).
Not: "The lease does not mention air conditioning." (YOUR LEASE holds only the clauses the tool reads, not the whole lease)
Instead: "The parts of your lease the tool has read do not cover that; the rest of your lease may." Then what the statute says on it.
Not: "(Lease notice_before_vacating)" or "(term_end)" (this tool's name for a clause, as a cite)
Instead: the cite YOUR LEASE gives the clause: (Lease Section 3.1), (Lease Article 7), or (Lease, page 1).
Not: the "repair within 5 days" you requested (the tenant wrote "Give them 5 days to reply")
Instead: You said: "Give them 5 days to reply"
Not: citing a section missing from THE STATUTE.
Instead: get_statute_section first (search_statute finds a phrase), then cite.
Not: a rule from 83.64(1) cited as "Fla. Stat. 83.64(4)".
Instead: cite the subsection the words sit in: the nearest "(1)" and "(a)" markers before the sentence in THE STATUTE.
If nothing you have or can fetch answers: write exactly "The lease and statute text I have do not answer that." and nothing after "that".
Not: that fallback line to "My notice says I can only pay by money order at the office. Can he do that?" while WHAT THE STATUTE DOES NOT SETTLE has an open question on the notice's form (no stored sentence says "money order").
Instead: the fallback line only when no stored sentence, no open question in WHAT THE STATUTE DOES NOT SETTLE, and no topic in COURT CASES THIS TOOL HAS is on the point. When an open question or a topic is on it, even in other words than the tenant's, give its readings (rule 5) or its cases (rule 8), applied to the facts.

3. Dates come only from YOUR FACTS, a lease quote, the tenant's words, or a tool result.
Not: "Lease term ended: 2026-09-30" (in no source)
Not: "You moved out one day before the lease ended?"
Instead: a date only where the answer turns on it, as the record has it. Never count, add, or compare dates.
Not: "The 30 days ran out on August 30, so the landlord is late." or any comparison of two dates of your own.
Instead: whether a deadline has passed comes only from WHICH DEADLINES HAVE PASSED ("passed" or "upcoming"); apply that word. For the date itself, call get_deadlines.
Not: "Even if the clock ran from the move-out date, the 30-day period would have ended on 2026-08-29." (a date worked out for a reading)
Instead: the tool computed its dates from the date you confirmed; from any other date it computes nothing.
Not: answering "What are my deadlines?" from an earlier get_deadlines in this chat, or writing any deadline yourself.
Instead: call get_deadlines every time; the program prints the deadlines above your reply, and you never see their dates. Asked only for the deadlines, add nothing after it. Asked more ("If I get rid of the dog by Friday, am I safe?"), answer the rest as rule 1 says, applying WHICH DEADLINES HAVE PASSED, never writing a date.
Not: answering "How long do I have to tell them I disagree?" or "When do I have to tell them?" with the statute's words alone.
Instead: for any question about when, how long, how many days, or a last day, call get_deadlines.

4. You propose facts; the tenant confirms them on the sheet.
Not: "Your confirmed dates: ..." or "Fact: claim_notice_date: 2026-09-22" before YOUR FACTS shows them as known.
Instead: call propose_facts with the tenant's exact words as "said" (shortened only by "..." between exact pieces); in the reply, say a point is not confirmed yet only where the answer turns on it.
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
Not: "In Durene v. Alcime the court held a late notice forfeits the deposit, so your landlord forfeited yours." (a case named from memory, with no page, before get_cases printed it)
Not: "This tool has no cases on that." to "Has a court ever said anything about a notice that says cash only?" while COURT CASES THIS TOOL HAS lists "Three-day notice for nonpayment of rent".
Instead: when the tenant asks what courts or judges said, or a topic in COURT CASES THIS TOOL HAS is on the point you are applying (the same notice, deposit, repair, entry, rent, fee, or lease term), call get_cases with the topic's exact name from there, even if the topic does not name the tenant's exact point. Then, for every case it gives, not only those that help:
- its facts beside the tenant's: where they match and where they differ;
- its rule in one plain sentence with the case name and page, the court's own words in quote marks only where the point turns on them, and the statute version it read when that is not today's text;
- what the rule would mean on the tenant's facts, and whether another case distinguished it.
Say plainly when a case cuts against the tenant. Quote a case only from get_cases' result, and never say a case held anything its printed words do not.
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
    "lease": ("YOUR LEASE (only the clauses the tool reads from the tenant's lease, not the whole lease: each in plain "
              "words, with the cite to use and its words)"),
    "notes": "THE TOOL'S NOTES ON YOUR ISSUES (by issue: questions, lease checks, evidence, postures, mistakes to avoid)",
    "open": ("WHAT THE STATUTE DOES NOT SETTLE (by issue: each open question, its sections, and its readings; the "
             "stored text settles none of them, so give every reading and pick none)"),
    "statute": "THE STATUTE (the sections for your issues, Fla. Stat. ch. 83, part II)",
    "cases": "COURT CASES THIS TOOL HAS (topics for get_cases; number of cases on each)",
    "facts": "YOUR FACTS (by issue: known, changed, proposed, missing, or n/a, and where each came from)",
    "options": ("YOUR OPTIONS (checked by the program from the confirmed facts: whether each option is open, closed, "
                "not settled, or not known yet, the conditions that decide it, and how far its steps have got)"),
    # Was THE PROGRAM'S DEADLINES (item 61, 2026-10-03), until the eval the same day: read as the deadlines
    # themselves, it was answered from ("You have until the upcoming deadline shown in THE PROGRAM'S DEADLINES")
    # and get_deadlines went uncalled on 5 of 39 questions about when.
    "deadlines": ("WHICH DEADLINES HAVE PASSED (passed or upcoming, no dates: for any question about when, call "
                  "get_deadlines, which prints the dates)"),
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
            + f"\n\n{PARTS['lease']}:\n" + lease_lines(record.profile)
            + f"\n\n{PARTS['notes']}:\n" + notes
            + f"\n\n{PARTS['open']}:\n" + open_text
            + f"\n\n{PARTS['statute']}:\n" + hot
            + f"\n\n{PARTS['cases']}:\n" + case_topics_text()
            + f"\n\n{PARTS['facts']}:\n" + json.dumps(element_status(), indent=2)
            + f"\n\n{PARTS['options']}:\n" + options_status()
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
    lease_quotes = [c.quote or "" for _, c in record.profile.clauses()] if record.profile else []
    updates = [ev["text"] for ev in read_events() if ev["kind"] == "tenant_update"]
    thread = [str(m.content) for m in messages if m.type != "ai"]
    return "\n".join([system_prompt(messages), record.matter.get("description", ""), *lease_quotes, *updates, *thread])


# ---- Cases in a reply (TODO item 57). In the eval of 2026-10-02 every mold-story answer left out the three
# printed cases that went for the landlord, and one credited a case's words to another case. Code can see both:
# which printed cases a reply names, and which printed case's text holds a quote.

CASES_LEFT_OUT = ("[Check: the program printed cases above that this reply does not discuss: {}. Read them too "
                  "before relying on the reply.]")


def named_cases(text, names):
    """Where the text names each of these cases: [(start, end, name)]. A case is named by its short name
    ("Bennett v. Mattison") or its first party's name alone ("Bennett"; "Olen Properties Corp." for Olen
    Properties Corp. v. Moss (984 So. 2d 558)). A name inside a longer one is the longer one's: "Bennett" in
    "Bennett M. Lifter" names Bennett M. Lifter, Inc. v. Varnado, and "Lewis" in "Guthartz v. Lewis" names no
    Lewis case."""
    found = []
    for name in names:
        plain = name.split(" (")[0]
        first, _, second = plain.partition(" v. ")
        first = first.split(",")[0]
        forms = sorted({plain, first} | ({f"{first} v. {second.split(',')[0]}"} if second else set()), key=len, reverse=True)
        pattern = r"(?<!\w)(?:" + "|".join(re.escape(f) for f in forms) + r")(?!\w)"
        found += [(m.start(), m.end(), name) for m in re.finditer(pattern, text)]
    return [n for n in found if not any(o[0] <= n[0] and n[1] <= o[1] and o[1] - o[0] > n[1] - n[0] for o in found)]


def printed_cases(messages):
    """Each case a get_cases result in these messages printed, with its own part of the printed text:
    [(name, part)], in order (wiki.cases_printed)."""
    found = []
    for m in messages:
        printed = getattr(m, "artifact", None) if m.type == "tool" and m.name == "get_cases" else None
        heads = wiki.cases_printed(printed) if printed else []
        ends = [start for _, start in heads[1:]] + [len(printed or "")]
        found += [(name, printed[start:end]) for (name, start), end in zip(heads, ends)]
    return found


def cases_left_out(new):
    """The cases get_cases printed in a turn's new messages that no reply after the printing names, by name;
    empty when nothing was printed or no reply followed."""
    first = next((i for i, m in enumerate(new) if printed_cases([m])), None)
    replies = "\n".join(m.content for m in new[first:] if m.type == "ai") if first is not None else ""
    printed = [name for name, _ in printed_cases(new)]
    named = {name for _, _, name in named_cases(replies, printed)}
    return [name for name in printed if replies.strip() and name not in named]


def check_case_quotes(text, messages):
    """Each quote in a reply credited to a printed case whose part does not hold it while another case's part
    does: [(quote, case, problem)]. A quote is credited to the printed case the reply names last before it in
    the same paragraph (none when two cases are named at that same place). Words a statute section also holds are
    left to check_quoted."""
    cases = printed_cases(messages)
    problems = []
    for start, _, quote in quote_spans(text):
        holding = [name for name, part in cases if is_in(quote, part)]
        if not holding or any(is_in(quote, words) for words in statute.values()):
            continue
        paragraph = text[max(0, text.rfind("\n\n", 0, start)):start]
        named = named_cases(paragraph, [name for name, _ in cases])
        last = max((start for start, _, _ in named), default=None)
        at_last = {name for start, _, name in named if start == last}
        credited = at_last.pop() if len(at_last) == 1 else None
        if credited and credited not in holding:
            problems.append((quote, credited, f"is in {holding[0]}'s text, not {credited}'s"))
    return problems


# ---- The words a reply cites (TODO item 73, the author's decision of 2026-10-04): the model gives each rule in a
# plain sentence with its cite, and the program prints the cited words under the reply, from statutes/ and the lease
# profile, so the tenant has the exact text to point to and the reply does not recite it. Was, from item 54 to 66:
# every rule quoted in the reply, and a caution for a section cited without a quote (item 66's RETOLD).

# a lease cite as YOUR LEASE gives it (lease.lease_cite): "Lease Section 4.3", "Lease Article 7", "Lease, page 1"
LEASE_CITE = re.compile(r"\bLease (?:Section|Article|Paragraph) (\d+(?:\.\d+)*)|\bLease,? page (\d+)", re.I)
CITED_MAX = 1500                                         # characters of one passage printed; the rest is named
CITED_HEAD = "The words the reply above cites, printed by the program from the stored statute and your lease:"


def cited_clause(clause, number, page):
    """The clause is the one a lease cite names: its number is the cited one or holds it (Article 7 for "Lease
    Section 7.2"), or, for a page cite, it has no number and is on that page."""
    found = SECTION_NUMBER.match(clause.section or "")
    if number:
        return bool(found) and (number == found.group(2) or number.startswith(found.group(2) + "."))
    return not found and str(clause.page) == page


def cited_words(text):
    """The statute and lease words a reply cites, as the text of a block, or "" when it cites none: for each ch. 83
    cite outside quote marks that the stored statutes hold, the subsection's words (or the section's), the
    narrowest once (83.56(1) cited, 83.56 alone adds nothing), cut at CITED_MAX characters with the cite for the
    rest; then each lease clause the profile holds under a lease cite (LEASE_CITE): a numbered one, or one inside it
    ("Lease Section 7.2" in "Lease Article 7"), or, for "Lease, page 1", the clauses on that page with no number;
    each with its cite, page, and label."""
    parts = []
    cites = [c for c in cites_in(unquoted(text)) if c.partition("(")[0] in statute
             and (not c.partition("(")[2] or "(" + c.partition("(")[2] in subsections(c.partition("(")[0]))]
    for cite in [c for c in cites if not any(o != c and o.startswith(c) for o in cites)]:
        section, _, rest = cite.partition("(")
        words = statute[section][slice(*subsections(section)["(" + rest])] if rest else statute[section]
        words = " ".join(words.split()).split(" History. —")[0]
        if len(words) > CITED_MAX:
            words = words[:CITED_MAX].rsplit(" ", 1)[0] + f" ... (the rest is in Fla. Stat. {cite})"
        parts.append(f"Fla. Stat. {cite}: {words}")
    clauses = [(n, c) for n, c in record.profile.clauses() if c.present and c.quote] if record.profile else []
    for number, page in dict.fromkeys(LEASE_CITE.findall(text)):
        for quote, (name, clause) in {c.quote: (n, c) for n, c in clauses if cited_clause(c, number, page)}.items():
            cite = lease_cite(clause)
            where = cite if cite.startswith("Lease, page") else f"{cite}, page {clause.page}"
            parts.append(f"{where} ({LABELS[name]}): {' '.join(quote.split())}")
    return CITED_HEAD + "\n\n" + "\n\n".join(parts) if parts else ""


def check_reply(text, messages):
    """Check the cites and the quotes in one reply (citations.check_cites and check_quoted, and check_case_quotes
    for a quote credited to a printed case), against the chat's thread so far. Each one that fails gets a caution
    line, shown under the reply, a line in the transcript, and a cite_flagged or quote_flagged event. Returns the
    caution lines. The reply itself is not changed. A section cited without a quote is no longer cautioned
    (TODO item 73): the program prints its words (cited_words)."""
    flagged = []
    for cite, problem in check_cites(text, sections_shown(messages)):
        flagged.append((caution(cite, problem), "cite_flagged", {"cite": cite, "problem": problem}))
    for cite, problem in check_case_cites(text, given_text(messages)):
        flagged.append((caution(cite, problem), "cite_flagged", {"cite": cite, "problem": problem}))
    for quote, cite, problem in check_quoted(text, given_text(messages)) + check_case_quotes(text, messages):
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
    """READING_LINE if the reply cites or quotes the statute (a ch. 83 cite, or a quoted passage with one) or the
    lease (a lease section cited, or a quoted passage found in a lease profile quote) and does not already carry
    the line; else None. Citing counts since TODO item 73, when the reply stopped quoting."""
    lease = [c.quote for _, c in record.profile.clauses() if c.present and c.quote] if record.profile else []
    quotes_source = any(cite.startswith("83.") or any(is_in(quote, q) for q in lease)
                        for quote, cite in quoted_passages(text))
    cites_source = bool(cites_in(unquoted(text)) or LEASE_CITE.search(text))
    return READING_LINE if (quotes_source or cites_source) and READING_LINE not in text else None


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
