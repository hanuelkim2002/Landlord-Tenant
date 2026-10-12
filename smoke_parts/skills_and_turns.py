"""Smoke, part: skills and the chat's turns. The model loads skills (load_skill: an unknown name refused, one already
loaded said so, one loaded saved, logged, and in the next prompt); an old matter's issues come out as skills; intake
and resume call no model and the description is the first turn; then, on a scratch copy with two skills, turns with a
stand-in model: an empty reply asked again, the reading line under a reply, a turn's blocks, a whole turn,
get_deadlines not ending the turn, the deadlines printed when the tenant asks when, and the same letter twice.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import contextlib
import io
import json
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langgraph.checkpoint.memory import InMemorySaver
import agent
import deterministic
import record
from checks import TEST_MATTER, check, make_scratch, remove_scratch
from config import MATTERS
from lease import LeaseProfile
from record import end_session, list_matters, load_matter, matter_dir, new_matter, read_events, start_session
from sheet import pending_rows
from skills import skills
from timeline import render_deadlines, render_timeline
from prompt import system_prompt
from replies import READING_LINE
from agent import intake, print_blocks, resume, retry_empty, sheet_note, thread_config, turn, turn_blocks
from tools import deadline_listing, draft_letter, get_cases, get_deadlines, load_skill
from tools import tools as model_tools
from smoke_parts.common import FORFEIT, StandIn, prompt_part, screen, stated

# ---- The model loads skills (TODO item 111), on a scratch copy with none loaded: load_skill refuses a name that is not a
# skill and lists the ones there are, says so for one already loaded, and loads one: matter.json has it, a skill_loaded
# event is logged, and the next system prompt marks it loaded in SKILLS, holds its instructions in LOADED SKILLS and its
# sections in THE STATUTE.
make_scratch("t-smoke-skills", skills=[])
try:
    load_matter("t-smoke-skills", "m-001")
    sid = start_session("existing")
    check("before any skill is loaded: the menu lists every skill with none marked, LOADED SKILLS says none, THE STATUTE is empty",
          prompt_part("skills").splitlines() == [f"- {name}: {skill.description}" for name, skill in skills.items()]
          and prompt_part("loaded") == "none loaded yet" and prompt_part("statute") == "")
    unknown = load_skill.invoke({"name": "not_a_skill"})
    check("load_skill refuses a name that is not a skill, and lists the skills there are",
          unknown.startswith("No skill named 'not_a_skill'") and all(name in unknown for name in skills)
          and record.matter["skills"] == [] and not any(e["kind"] == "skill_loaded" for e in read_events()))
    said_loaded = load_skill.invoke({"name": "repair_not_made"})
    repair = skills["repair_not_made"]
    saved_now = json.loads((matter_dir() / "matter.json").read_text())
    check("load_skill loads a skill: matter.json has it and a skill_loaded event is logged with the session",
          said_loaded.startswith("Loaded repair_not_made.") and saved_now["skills"] == ["repair_not_made"]
          and record.matter["skills"] == ["repair_not_made"] and read_events()[-1]["kind"] == "skill_loaded"
          and read_events()[-1]["skill"] == "repair_not_made" and read_events()[-1]["session"] == sid)
    check("the next system prompt marks the skill loaded in SKILLS, holds its instructions in LOADED SKILLS and its sections in "
          "THE STATUTE",
          [line for line in prompt_part("skills").splitlines() if line.endswith(" (loaded)")]
          == [f"- repair_not_made: {repair.description} (loaded)"]
          and prompt_part("loaded") == f"# repair_not_made\n{repair.body}"
          and all(f"=== {section} ===\n" in prompt_part("statute") for section in repair.sections)
          and "=== 83.49 ===" not in prompt_part("statute"))
    events_now = len(read_events())
    again = load_skill.invoke({"name": "repair_not_made"})
    check("load_skill says a skill is already loaded, and loads it once",
          again.startswith("The skill repair_not_made is already loaded") and record.matter["skills"] == ["repair_not_made"]
          and len(read_events()) == events_now)
    load_skill.invoke({"name": "deposit_not_returned"})
    check("a second skill is added after the first: its instructions follow the first's, its sections join THE STATUTE once",
          record.matter["skills"] == ["repair_not_made", "deposit_not_returned"]
          and prompt_part("loaded") == f"# repair_not_made\n{repair.body}\n\n# deposit_not_returned\n{skills['deposit_not_returned'].body}"
          and prompt_part("statute").count("=== 83.505 ===") == 1 and "=== 83.49 ===" in prompt_part("statute"))
    check("timeline full shows the skill loaded; the plain timeline does not", "skill loaded: repair not made" in render_timeline(full=True)
          and "skill loaded" not in render_timeline() and "skill loaded: repair not made" not in render_timeline("deposit_not_returned", True))
    end_session()
finally:
    remove_scratch("t-smoke-skills")
check("the skills scratch matter is removed", not (MATTERS / "t-smoke-skills").exists())

# ---- A matter saved before skills (TODO item 111): load_matter turns its issues into skills (an issue that is not a
# skill, "other", is left out) and drops the three old keys; list_matters reads them the same way.
make_scratch("t-smoke-old", issues=["deposit_not_returned", "other", "repair_not_made"],
             proposed_issues=[{"issue": "lease_ending", "source": "classify", "because": "x"}], rejected_issues=["rent_increased"])
try:
    load_matter("t-smoke-old", "m-001")
    check("load_matter turns an old matter's issues into skills, in order, and drops the old keys",
          record.matter["skills"] == ["deposit_not_returned", "repair_not_made"]
          and not {"issues", "proposed_issues", "rejected_issues"} & set(record.matter)
          and [p.issue for p in record.active_playbooks()] == ["deposit_not_returned", "repair_not_made"]
          and [s.name for s in record.active_skills()] == ["deposit_not_returned", "repair_not_made"])
    check("list_matters lists an old matter's skills", next(m for m in list_matters() if m["tenant"] == "t-smoke-old")["skills"]
          == ["deposit_not_returned", "repair_not_made"])
    saved_old = json.loads((MATTERS / "t-smoke-old" / "m-001" / "matter.json").read_text())
    check("the old matter.json is not rewritten until the matter is saved", "issues" in saved_old and "skills" not in saved_old)
    record.save(record.matter)
    check("once saved, matter.json holds skills and none of the old keys",
          json.loads((MATTERS / "t-smoke-old" / "m-001" / "matter.json").read_text())["skills"] == ["deposit_not_returned", "repair_not_made"]
          and "issues" not in json.loads((MATTERS / "t-smoke-old" / "m-001" / "matter.json").read_text()))
finally:
    remove_scratch("t-smoke-old")
check("the old-matter scratch matter is removed", not (MATTERS / "t-smoke-old").exists())

# ---- Intake and resume call no model (TODO item 111), and the description is the first turn: a new matter's intake only
# saves the description; the stand-in model, given the description as the tenant's first message, loads a skill and
# proposes a fact; an update is logged as typed and sent the same way. A tripwire stands in for the model clients.
class Tripwire:
    called = False
    def invoke(self, *args, **kwargs):
        Tripwire.called = True
        raise AssertionError("the model was called")
real_llm = (agent.agent_llm, deterministic.agent_llm)
agent.agent_llm = deterministic.agent_llm = Tripwire()
try:
    new_matter("t-smoke-intake")
    record.profile = LeaseProfile.model_validate_json((TEST_MATTER / "lease_profile.json").read_text())
    start_session("new")
    description = "My lease ended July 31, 2026. I moved out and I got a letter from the landlord about my deposit."
    intake(description)
    check("intake saves the description and nothing else, and calls no model",
          json.loads((matter_dir() / "matter.json").read_text()) ==
          {"id": "m-001", "tenant": "t-smoke-intake", "skills": [], "facts": {}, "proposed": {}, "description": description}
          and not Tripwire.called and [e["kind"] for e in read_events()] == ["session_started"])
    said_first = "I got a letter from the landlord"
    first_turns = StandIn(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "load_skill", "id": "s1", "args": {"name": "deposit_not_returned"}}]),
        AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": "s2", "args": {"facts_json": json.dumps(
            {"claim_notice_received": {"value": True, "how": "stated", "said": said_first}})}}]),
        AIMessage(content="That sounds like a deposit claim."), AIMessage(content="Second turn.")]))
    agent_first = create_agent(first_turns, tools=model_tools, checkpointer=InMemorySaver())
    config_first = thread_config()
    blocks, proposed = turn(agent_first, config_first, description)
    thread = agent_first.get_state(config_first).values["messages"]
    transcript = [json.loads(line) for line in (matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()]
    check("the description is the tenant's first message: the model answers it first, loads the skill that fits, and "
          "proposes a fact from the tenant's own words",
          thread[0].type == "human" and thread[0].content == description
          and transcript[0]["role"] == "tenant" and transcript[0]["text"] == description
          and [b["kind"] for b in blocks] == ["reply"] and proposed and record.matter["skills"] == ["deposit_not_returned"]
          and record.matter["proposed"]["claim_notice_received"]["basis"] == said_first and pending_rows()
          and [t["name"] for t in transcript if t["role"] == "tool"] == ["load_skill", "propose_facts"])
    update = "The landlord emailed me again today about the cleaning charge."
    resume(update)
    logged = [e for e in read_events() if e["kind"] == "tenant_update"]
    blocks_two, _ = turn(agent_first, config_first, update)
    check("resume logs the update as typed and calls no model; the update goes to the model as a turn",
          len(logged) == 1 and logged[0]["text"] == update and not Tripwire.called
          and [b["kind"] for b in blocks_two] == ["reply"] and record.matter["description"] == description
          and agent_first.get_state(config_first).values["messages"][-2].content == update)
    end_session()
finally:
    agent.agent_llm, deterministic.agent_llm = real_llm
    remove_scratch("t-smoke-intake")
check("the intake scratch matter is removed", not (MATTERS / "t-smoke-intake").exists())

# ---- The chat's turns, on a second scratch copy with two skills: deposit_not_returned loaded at the start, and
# deposit_claim_received loaded through load_skill, as the model would. Nothing leaves the history.
make_scratch("t-smoke-related", skills=["deposit_not_returned"], facts={"claim_notice_received": False},
             proposed={"claim_notice_received": stated(True, "I got a letter from the landlord")})
try:
    load_matter("t-smoke-related", "m-001")
    sid = start_session("existing")
    load_skill.invoke({"name": "deposit_claim_received"})
    check("the model's next prompt has the new skill's instructions", "# deposit_claim_received\n" in prompt_part("loaded"))
    check("the prompt carries the sections the loaded skills name", "=== 83.49 ===" in system_prompt())
    # deadlines per skill: deposit_not_returned complete, deposit_claim_received still open (its facts skipped)
    record.confirm_fact("claim_notice_received", True, "sheet")        # the tenant's yes, as on the sheet
    record.matter["facts"].update(tenancy_terminated="2026-07-31", vacated="2026-07-30", claim_notice_date="2026-09-25",
                                  claim_delivery="certified mail", forwarding_address_given=True, early_or_periodic=False)
    per_issue = json.loads(deadline_listing())
    check("a skill with open facts does not block another skill's deadlines",
          {d["clock"] for d in per_issue["deadlines"]} == {"return_if_no_claim", "claim_notice_deadline"}
          and all(d["issues"] == ["deposit_not_returned"] for d in per_issue["deadlines"])
          and "deposit_claim_received" in per_issue["waiting"] and "deposit_not_returned" not in per_issue["waiting"])
    check("printed deadlines show one skill's dates and the other waiting",
          "return if no claim" in render_deadlines(json.dumps(per_issue, default=str))
          and "waiting [deposit_claim_received]: " in render_deadlines(json.dumps(per_issue, default=str)))

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
    check("what the tenant confirmed on a sheet goes to the model with the next message",
          sheet_note([("vacated", "2026-07-28"), ("claim_amount", 400)])
          == "[Program note: the tenant confirmed on the sheet: vacated = 2026-07-28, claim_amount = 400]\n"
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
    letter_args = {"issue": "deposit_not_returned", "posture": "preserve", "account": "", "request": "Please return the deposit.",
                   "respond_within_days": 10, "delivery_method": "certified mail", "signed_by": "Jordan Ellis"}
    draft_letter.invoke(letter_args)
    again = draft_letter.invoke(letter_args)
    changed = draft_letter.invoke({**letter_args, "respond_within_days": 14})
    drafts = [e for e in read_events() if e["kind"] == "draft" and e.get("session") == record.session]
    check("the same letter twice in a session is drafted once", again.startswith("[The same letter was already drafted")
          and len(drafts) == 2 and "Please respond by" in changed)
    end_session()
finally:
    remove_scratch("t-smoke-related")
check("the second scratch matter is removed", not (MATTERS / "t-smoke-related").exists())
print()
