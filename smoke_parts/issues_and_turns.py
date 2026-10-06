"""Smoke, part: issues as suggestions, and the chat's turns, on a second scratch copy with one issue. A confirmed
fact suggests a related issue, which the sheet asks; a no is logged and not asked again unless the fact is confirmed
anew; an active issue can be dropped. Then turns with a stand-in model: an empty reply asked again, the reading line
under a reply, a turn's blocks, a whole turn, get_deadlines not ending the turn, the deadlines printed when the
tenant asks when, and the same letter twice.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import contextlib
import io
import json
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langgraph.checkpoint.memory import InMemorySaver
import record
from checks import check, make_scratch, remove_scratch
from config import MATTERS
from record import end_session, load_matter, matter_dir, read_events, start_session
from sheet import run_sheet
from timeline import render_deadlines, render_timeline
from prompt import system_prompt
from replies import READING_LINE
from agent import command, print_blocks, retry_empty, sheet_note, thread_config, turn, turn_blocks
from tools import deadline_listing, draft_letter, get_cases, get_deadlines
from tools import tools as model_tools
from smoke_parts.common import FORFEIT, StandIn, prompt_part, screen, stated

# ---- Issues as suggestions, on a second scratch copy with one issue. Confirming "received a notice: yes" on
# the sheet suggests deposit_claim_received; the tenant says yes to it and its questions and guidance follow.
# Then: a rejected issue is not suggested again by its rule unless the fact is confirmed anew, a classifier
# suggestion asks again, and an active issue can be dropped. Nothing leaves the history.
make_scratch("t-smoke-related", issues=["deposit_not_returned"], facts={"claim_notice_received": False},
             proposed={"claim_notice_received": stated(True, "I got a letter from the landlord")})
try:
    load_matter("t-smoke-related", "m-001")
    sid = start_session("existing")
    check("a related issue is not suggested before its fact is confirmed", record.add_related_issues() == []
          and record.matter["issues"] == ["deposit_not_returned"] and record.matter["proposed_issues"] == [])
    shown_sheet = io.StringIO()
    def accept_notice_and_issue(prompt):
        """Answer by the question on screen: accept the change to "received a notice", say yes to the suggested
        issue, skip the rest."""
        last_question = [line for line in shown_sheet.getvalue().splitlines() if line.startswith("  ") and
                         not line.startswith("    ")][-1]
        if "received any written notice" in last_question:
            return ""
        return "yes" if "Is that part of your situation?" in last_question else "?"
    with contextlib.redirect_stdout(shown_sheet):
        run_sheet(accept_notice_and_issue)
    events = read_events()
    proposed = [e for e in events if e["kind"] == "issue_proposed"]
    check("confirming the fact suggests the related issue, with its source and reason", proposed
          and proposed[-1]["issue"] == "deposit_claim_received" and proposed[-1]["source"] == "related"
          and proposed[-1]["because"] == "claim_notice_received is true" and proposed[-1]["session"] == sid)
    check("the sheet asks about the suggested issue before its facts, and yes makes it active",
          "Suggested for your matter: deposit_claim_received" in shown_sheet.getvalue()
          and "This looks like: Tenant has received the landlord's written notice" in shown_sheet.getvalue()
          and shown_sheet.getvalue().index("Is that part of your situation?") < shown_sheet.getvalue().index("What date is printed on the landlord's notice?")
          and record.matter["issues"] == ["deposit_not_returned", "deposit_claim_received"]
          and any(e["kind"] == "issue_confirmed" and e["issue"] == "deposit_claim_received" for e in events))
    check("the model's next prompt has the new issue's guidance", "issue: deposit_claim_received" in system_prompt())
    check("the prompt carries the sections the active playbooks name", "=== 83.49 ===" in system_prompt())
    sections_before = prompt_part("statute")
    record.add_issues(["other"], "classify", "a smoke check")        # "other" is the one label with no playbook
    check("an issue with no playbook is recorded at once and adds no sections", "other" in record.matter["issues"]
          and prompt_part("statute") == sections_before)
    check("add_issues never adds an issue twice", record.add_issues(["deposit_claim_received"], "classify", "x") == [])
    check("timeline full shows the suggestion and the confirmation", "issue suggested: deposit claim received"
          in render_timeline(full=True) and "issue confirmed: deposit claim received" in render_timeline(full=True))
    # deadlines per issue: deposit_not_returned complete, deposit_claim_received still open (its facts skipped)
    record.matter["facts"].update(tenancy_terminated="2026-07-31", vacated="2026-07-30", claim_notice_date="2026-09-25",
                                  forwarding_address_given=True, early_or_periodic=False)
    per_issue = json.loads(deadline_listing())
    check("an issue with open facts does not block another issue's deadlines",
          {d["clock"] for d in per_issue["deadlines"]} == {"return_if_no_claim", "claim_notice_deadline"}
          and all(d["issues"] == ["deposit_not_returned"] for d in per_issue["deadlines"])
          and "deposit_claim_received" in per_issue["waiting"] and "deposit_not_returned" not in per_issue["waiting"])
    check("printed deadlines show one issue's dates and the other issue waiting",
          "return if no claim" in render_deadlines(json.dumps(per_issue, default=str))
          and "waiting [deposit_claim_received]: " in render_deadlines(json.dumps(per_issue, default=str)))
    # dropping, rejecting, and asking again
    record.matter["proposed"]["claim_amount"] = stated(400, "keeping $400")
    record.reject_issue("deposit_claim_received", "issue_dropped")
    check("drop takes an issue out, logs it, and clears its pending suggestions",
          "deposit_claim_received" not in record.matter["issues"] and "claim_amount" not in record.matter["proposed"]
          and read_events()[-1]["kind"] == "issue_dropped")
    check("the rule does not suggest a dropped issue again on its own", record.add_related_issues() == [])
    record.confirm_fact("claim_notice_received", False, "sheet")
    record.confirm_fact("claim_notice_received", True, "sheet")        # the notice fact confirmed anew
    check("the rule suggests it again when its fact is confirmed anew",
          [p["issue"] for p in record.matter["proposed_issues"]] == ["deposit_claim_received"])
    record.reject_issue("deposit_claim_received")
    check("no on the sheet rejects a suggestion and logs it", record.matter["proposed_issues"] == []
          and read_events()[-1]["kind"] == "issue_rejected" and "deposit_claim_received" in record.matter["rejected_issues"])
    record.add_issues(["deposit_claim_received"], "classify", "the tenant's update")
    check("a later classification suggests a rejected issue again",
          [p["issue"] for p in record.matter["proposed_issues"]] == ["deposit_claim_received"]
          and "deposit_claim_received" not in record.matter["rejected_issues"])

    # an empty reply (m-018): the model is asked once more; a stand-in agent plays the model's second turn
    class Again:
        def __init__(self, reply):
            self.reply = reply
        def invoke(self, inputs, config):
            return {"messages": first["messages"] + inputs["messages"] + [AIMessage(content=self.reply)]}
    first = {"messages": [HumanMessage(content="What are my deadlines?"), AIMessage(content="\n")]}
    shown_first = turn_blocks(first["messages"][1:], first["messages"])
    _, _, shown_again = retry_empty(Again("The deadlines appear above."), {}, first)
    check("a turn with only blank text shows nothing, and the model's second reply is shown", shown_first == []
          and shown_again == [{"kind": "reply", "text": "The deadlines appear above."}]
          and read_events()[-1]["kind"] == "reply_empty" and read_events()[-1]["recovered"] is True)
    _, _, shown_again = retry_empty(Again(""), {}, first)
    check("a second empty reply tells the tenant and is logged, with why each answer stopped",
          [b["kind"] for b in shown_again] == ["caution"] and "[Check: no reply came back" in screen(shown_again)
          and read_events()[-1]["recovered"] is False
          and read_events()[-1]["finish"] == [None, None])

    # the tool's own line under a reply that quotes the statute without it (TODO item 30): printed by the program
    # and kept in the transcript; not under a reply that has it, nor under one quoting only the tenant
    bare = AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"')
    shown_bare = turn_blocks([bare], [bare])
    shown_others = (turn_blocks([AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"\n{READING_LINE}')], [])
                    + turn_blocks([AIMessage(content='You said: "I paid the whole rent for September myself."')], []))
    session_lines = (record.matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()
    footers = [json.loads(line) for line in session_lines if json.loads(line)["role"] == "footer"]
    check("item 46: a reply that quotes the statute gets the program's reading line, once, in the transcript; "
          "none under one that already has it or quotes only the tenant",
          shown_bare[-1] == {"kind": "footer", "text": READING_LINE} and screen(shown_others).count(READING_LINE) == 1
          and [f["text"] for f in footers] == [READING_LINE])
    lease_words = next(c.quote for _, c in record.profile.clauses() if c.present and c.quote and len(c.quote) > 60)[:60]
    cut = AIMessage(content="You confirmed you moved out on", response_metadata={"finish_reason": "length"})
    check("item 47: a reply stopped at the length limit gets a caution saying it was cut off",
          [b["kind"] for b in turn_blocks([cut], [cut])] == ["reply", "caution"]
          and "cut off at the model's length limit" in screen(turn_blocks([cut], [cut])))
    check("a lease quote gets the program's reading line too (eval, 2026-10-01)",
          screen(turn_blocks([AIMessage(content=f'Lease Section 4.3, page 2: "{lease_words}"')], [])).count(READING_LINE) == 1)

    # blocks (TODO item 31): what the tenant sees from a turn or a command, the model's words apart from the
    # program's, for the terminal and the web page alike
    bad_cite = AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"\nSee also 83.64.')
    check("a reply's blocks: the model's words, the words it cites, then the program's cautions, then its line",
          [b["kind"] for b in turn_blocks([bad_cite], [bad_cite])] == ["reply", "sources", "caution", "footer"])
    with contextlib.redirect_stdout(io.StringIO()) as printed:
        print_blocks([{"kind": "reply", "text": "One."}, {"kind": "footer", "text": "Two."}])
    check("the terminal prints each block's text with an empty line after it", printed.getvalue() == "One.\n\nTwo.\n\n")
    commands_before = [json.loads(line)["role"] for line in
                       (record.matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()].count("command")
    issues_shown, timeline_shown = command("issues"), command("timeline full")
    check("chat commands come back as the program's blocks, and words that are not one go to the model",
          [b["kind"] for b in issues_shown] == ["notice"] and "deposit_not_returned: " in screen(issues_shown)
          and [b["kind"] for b in timeline_shown] == ["timeline"] and "DATE" in screen(timeline_shown)
          and command("timeline nonsense")[0]["text"].startswith("No issue named nonsense")
          and command("What issues do I have?") is None and command("drop") is None)
    check("each command goes to the transcript", [json.loads(line)["role"] for line in
          (record.matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()].count("command")
          == commands_before + 3)
    check("what the tenant confirmed on a sheet goes to the model with the next message",
          sheet_note([("vacated", "2026-07-28"), ("issue deposit_claim_received", "confirmed")])
          == "[Program note: the tenant confirmed on the sheet: vacated = 2026-07-28, issue deposit_claim_received = confirmed]\n"
          and sheet_note([]) == "")
    # one whole turn through an agent: a stand-in model proposes a fact, then replies; the turn's blocks are the
    # reply only, it says facts were proposed, and a second turn starts after the first one's messages
    class Proposes(GenericFakeChatModel):
        def bind_tools(self, tools, **kwargs):
            return self
    said = "I got a letter from the landlord"
    proposes = Proposes(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": "p1", "args": {"facts_json": json.dumps(
            {"claim_notice_received": {"value": True, "how": "stated", "said": said}})}}]),
        AIMessage(content=f'You said: "{said}"'), AIMessage(content="Second turn.")]))
    agent_now = create_agent(proposes, tools=model_tools, checkpointer=InMemorySaver())
    config_now = thread_config()
    first_blocks, first_proposed = turn(agent_now, config_now, said)
    second_blocks, second_proposed = turn(agent_now, config_now, "And?", note="[Program note: x]\n")
    check("turn: the reply is shown, the proposal noted, and the next turn shows only its own reply",
          first_blocks == [{"kind": "reply", "text": f'You said: "{said}"'}] and first_proposed
          and second_blocks == [{"kind": "reply", "text": "Second turn."}] and not second_proposed
          and config_now["configurable"]["thread_id"] == record.session)

    # get_deadlines and get_cases no longer end the model's turn (items 47 and 51; get_deadlines did from item 19):
    # a stand-in model calls get_deadlines, then applies the status; the reply comes after the printed listing
    applies = "The program's listing above shows the 7-day period has not passed yet."
    stand_in = StandIn(messages=iter([AIMessage(content="", tool_calls=[{"name": "get_deadlines", "args": {}, "id": "d1"}]),
                                      AIMessage(content=applies)]))
    ended = create_agent(stand_in, tools=model_tools).invoke(
        {"messages": [HumanMessage(content="If I get rid of the dog by Friday, am I safe?")]})
    check("item 51: neither get_deadlines nor get_cases ends the turn; the model's answer follows the printed listing",
          not get_deadlines.return_direct and not get_cases.return_direct
          and [m.type for m in ended["messages"][-2:]] == ["tool", "ai"] and ended["messages"][-1].content == applies
          and "your instructions say which have passed" in ended["messages"][-2].content)

    # item 65: a question about when, answered without get_deadlines: the program prints the deadlines above the
    # reply; when the model calls it, the listing is printed once, not twice
    events_now = len(read_events())
    skips = StandIn(messages=iter([AIMessage(content="It is seven days before you move out."),
                                   AIMessage(content="", tool_calls=[{"name": "get_deadlines", "args": {}, "id": "d2"}]),
                                   AIMessage(content="The listing is above.")]))
    agent_when = create_agent(skips, tools=model_tools, checkpointer=InMemorySaver())
    when_blocks, _ = turn(agent_when, thread_config(), "When do I have to tell them?")
    asked_blocks, _ = turn(agent_when, thread_config(), "When is the last day?")
    session_lines = [json.loads(line) for line in
                     (matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()]
    check("item 65: asked when, a turn without get_deadlines gets the deadlines printed by the program first, logged "
          "and transcribed; a turn that calls it gets one listing",
          [b["kind"] for b in when_blocks] == ["deadlines", "reply"]
          and when_blocks[0]["text"] == render_deadlines(deadline_listing())
          and [b["kind"] for b in asked_blocks] == ["deadlines", "reply"]
          and any(e["kind"] == "deadlines_computed" for e in read_events()[events_now:])
          and sum(line.get("what") == "deadlines" for line in session_lines) == 1)

    # the same letter twice in one session (m-026): drafted once; a changed letter is drafted again
    letter_args = {"issue": "deposit_not_returned", "posture": "preserve", "ask": "Return the deposit",
                   "respond_within_days": 10, "delivery_method": "certified mail"}
    draft_letter.invoke(letter_args)
    again = draft_letter.invoke(letter_args)
    changed = draft_letter.invoke({**letter_args, "respond_within_days": 14})
    drafts = [e for e in read_events() if e["kind"] == "draft" and e.get("session") == record.session]
    check("the same letter twice in a session is drafted once", again.startswith("[The same letter was already drafted")
          and len(drafts) == 2 and "Please respond by" in changed)
    dropped = command("drop deposit_not_returned")                 # the last covered issue: the chat ends
    check("drop as a command takes the issue out, logs it, and says the chat ends when no covered issue is left",
          [b["text"] for b in dropped] == ["Dropped deposit_not_returned from this matter. It is logged, and it can be "
                                           "suggested again later.", "No issue this tool covers is left in this matter, "
                                           "so the chat ends here."]
          and read_events()[-1]["kind"] == "issue_dropped" and not record.active_playbooks())
    end_session()
finally:
    remove_scratch("t-smoke-related")
check("the second scratch matter is removed", not (MATTERS / "t-smoke-related").exists())
print()
