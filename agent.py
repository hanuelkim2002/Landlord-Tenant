"""Agent: the rules, intake (builds the system prompt and returns an agent), and the chat loop."""
import json

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver

import record
from config import PLAYBOOKS, agent_llm
from corpus import statute
from deterministic import ROUTING, classify, fill_facts
from record import active_playbooks, element_status, save
from timeline import render_timeline
from tools import tools


# ---- Rules: the system prompt. The lease profile, the playbooks, the statute sections, and the element
# status are appended to it at intake.

RULES = """You help a Florida residential tenant organize a landlord-tenant dispute. You are not a lawyer.
You give no legal advice and make no recommendations.
Frame everything as: here is what your lease says, here is what the statute says, here are your dates.

Rules:
1. Quote the lease only from the LEASE PROFILE quotes below. Quote the statute only from the STATUTE
   SECTIONS below or from get_statute_section. Never from memory.
2. Never count, add, or compute days or dates. For any deadline, call get_deadlines and report exactly
   what it returns, including its "counting" line.
3. ELEMENT STATUS rows marked "proposed" are unconfirmed. Before anything else, show the tenant each one:
   the value, whether it was stated or inferred, and the words it rests on. Ask if it is correct. Then call
   record_facts with the confirmed value, corrected if the tenant corrected it. Rows marked "missing": ask
   that row's "ask" question, one at a time, and call record_facts with the answer. Do not call get_deadlines
   while any row is proposed or missing.
4. If the preloaded material does not answer a question, use search_statute or get_statute_section.
   If the statute does not answer it either, say so plainly. Do not fill the gap with your own view.
5. The PLAYBOOK's open_questions are unsettled. When one comes up, say the statute does not settle it.
6. You draft letters only when asked. You never send anything.
7. Never state which controls when the lease and the statute differ, and never explain how they
   interact. Show both texts side by side and say: this tool does not resolve conflicts between them.
8. Before you mention any section not in STATUTE SECTIONS, call get_statute_section for it first
   and quote from what it returns.
9. Never call record_facts with a value the tenant has not confirmed in this conversation.
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


# ---- Intake: classify the description, propose facts, build the system prompt, return an agent.

def intake(description):
    """Classify, fill facts for every matching playbook, build the hot set, return an agent."""
    matter = record.matter
    matter["description"] = description
    matter["issues"] = classify(description)["issues"]
    matter["facts"] = {}
    matter["proposed"] = {}
    for pb in active_playbooks():                          # first playbook to propose a fact wins
        for fact_id, p in fill_facts(description, pb).items():
            matter["proposed"].setdefault(fact_id, p)
    save(matter)

    sections = sorted({s for i in matter["issues"] for s in ROUTING[i]["sections"]})
    hot = "\n\n".join(f"=== {s} ===\n{statute[s]}" for s in sections)
    playbook_text = "\n\n".join((PLAYBOOKS / f"{pb.issue}.yaml").read_text() for pb in active_playbooks())

    system = (RULES
              + "\n\nLEASE PROFILE:\n" + record.profile.model_dump_json(indent=2)
              + "\n\nPLAYBOOKS:\n" + playbook_text
              + "\n\nSTATUTE SECTIONS:\n" + hot
              + "\n\nELEMENT STATUS (by issue):\n" + json.dumps(element_status(), indent=2))

    print("issues:", matter["issues"], "| playbooks:", [pb.issue for pb in active_playbooks()],
          "| proposed:", list(matter["proposed"]), "| sections:", sections)
    return create_agent(agent_llm, tools=tools, system_prompt=system, checkpointer=InMemorySaver())


# ---- Chat: read a line, run a turn, print the reply. Tool output is hidden except draft_letter, whose
# result is printed directly. The word `timeline` prints the record without the model.

def chat(agent):
    config = {"configurable": {"thread_id": str(uuid7())}}
    seen = 0            # result holds the whole thread; seen marks how much we already printed
    while True:
        q = input(">> ")
        if q in ("", "bye"):
            break
        if q.strip().lower().startswith("timeline"):
            words = q.split()[1:]
            full = "full" in words
            issue = next((w for w in words if w != "full"), None)
            if issue and issue not in record.matter["issues"]:
                print(f"No issue named {issue} in this matter. Active issues: {record.matter['issues']}\n")
                continue
            print(render_timeline(issue, full), "\n")
            continue
        result = agent.invoke({"messages": [HumanMessage(content=q)]}, config=config)
        for m in result["messages"][seen + 1:]:          # everything new this turn, minus your own message
            if m.type == "tool" and m.name == "draft_letter":
                print(m.content, "\n")
            elif m.type == "ai" and m.content:
                print(m.content, "\n")
        seen = len(result["messages"])
