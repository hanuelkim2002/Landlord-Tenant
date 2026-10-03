"""App: the tool as a web page on this computer, drawing the same blocks the terminal prints (TODO item 31).

    streamlit run app.py          # then open http://localhost:8501

The same steps as run.py, on one page. Left (the sidebar): a new matter, the saved matters, and the open
matter's issues. Middle: the front door (a new matter: tenant, lease PDF, description; a saved one: what is
new), then the intake sheet as a form, one question at a time, then the chat. Right: the timeline and the last
letter drafted, drawn from the record on every run, never by the model. In the chat, a speech bubble is the
model's words (checked by the program before they are shown); a box is printed by the program itself.

How Streamlit works, in short: it runs this whole file again, top to bottom, on every click or message. So
nothing in a plain variable survives from one run to the next. What must last is kept in st.session_state, the
page's memory for one browser tab: the open matter's ids, the session id, the stage, the agent and its thread,
the chat so far as blocks, and the sheet's skips. record.matter and record.profile stay in the record module
as always; open_record() puts this tab's matter back there at the top of every run.

The settings in .streamlit/config.toml keep the page on this computer (localhost) and turn off Streamlit's
usage statistics. One tab at a time: two tabs on two matters would take turns replacing record.matter.
"""
import re
import tempfile
import traceback
from datetime import date
from pathlib import Path

import streamlit as st

import record
from agent import (block, build_agent, command, intake, read_lease, resume, sheet_note, stop_block, thread_config,
                   turn)
from config import uf_api_key
from corpus import playbooks
from record import (active_playbooks, candidate_playbooks, end_session, list_matters, load_matter, matter_dir,
                    new_matter, new_tenant_id, read_events, start_session)
from sheet import NOT_COVERED, pending_rows, row_notes, save_answer, shown, suggestion, value_of
from timeline import render_timeline

st.set_page_config(page_title="Landlord-Tenant Organizer", layout="wide")
# The program's listings (deadlines, timeline, letters) are columns of fixed-width text: a smaller font fits
# more of a line before it scrolls sideways.
st.html("<style>[data-testid='stCode'] code {font-size: 0.75rem;}</style>")
state = st.session_state


# ---- The page's memory. Each key is set once, the first time this tab runs the file.

def reset():
    """Forget the open matter: back to the front door, with an empty chat and no agent."""
    state.stage = "door"            # door, new, update, sheet, chat, ended
    state.ids = None                # (tenant id, matter id) of the open matter
    state.session = None            # the open session's id (record.session)
    state.agent = None              # built once the first sheet is done, as in run.py
    state.config = None             # the chat thread's config
    state.history = []              # everything shown in the middle column, oldest first, as blocks
    state.pending = None            # the tenant's message, waiting for the model's turn
    state.note = ""                 # what the tenant confirmed on a sheet, for the model's next turn
    state.skipped = set()           # sheet rows skipped in this sheet
    state.saved = []                # what this sheet saved, as save_answer's pairs


if "stage" not in state:
    reset()


def open_record():
    """Put this tab's matter and session back into the record module. Another tab may have opened another matter
    in between, since the record module is shared by every tab of this one program."""
    if state.ids and (record.matter["tenant"], record.matter["id"]) != state.ids:
        load_matter(*state.ids)
    record.session = state.session


def close_session():
    """End the open session in the record, as run.py does on a normal exit, and forget the matter."""
    if state.session:
        record.session = state.session
        end_session()
    reset()


def need_key():
    """The model calls need the key in .env. Without it, say so on the page and stop this run."""
    if not uf_api_key:
        st.error("UF_API_KEY is not set. Copy .env.example to .env and put the key there.")
        st.stop()


# ---- Showing text exactly as written. Streamlit reads text as markdown, where a "$" starts math and "*" makes
# italics, so every markdown sign is escaped and each line break kept.

MARKDOWN = re.compile(r"([\\`*_{}\[\]()#+\-.!|$<>~])")


def plain(text):
    """The text as markdown that shows it exactly as written."""
    lines = [MARKDOWN.sub(r"\\\1", line.strip()) for line in text.split("\n")]
    return "  \n".join(lines)


# What each kind of the program's block is called on the page (agent.py, BLOCK KINDS).
PRINTED_BY = {
    "deadlines": "Printed by the program: deadlines computed from your confirmed facts. Not written by the model.",
    "letter": "Printed by the program from its letter tool, which builds a letter from a template and your confirmed "
              "facts. The tool never sends anything.",
    "cases": "Printed by the program from the case wiki, in the courts' own words.",
    "timeline": "Printed by the program from your record.",
    "stop": "Printed by the program.",
}


def show(b):
    """Draw one block (or one of the page's own entries: the tenant's words, a sheet answer)."""
    kind, text = b["kind"], b["text"]
    if kind == "tenant":
        with st.chat_message("user"):
            st.markdown(plain(text))
    elif kind == "reply":                                  # the only block the model wrote
        with st.chat_message("assistant"):
            st.markdown(plain(text))
    elif kind == "caution":
        st.warning(plain(text))
    elif kind in ("footer", "notice"):
        st.info(plain(text))
    elif kind == "sheet":
        st.caption(plain(text))
    else:                                                  # deadlines, letter, cases, timeline, stop
        with st.container(border=True):
            st.caption(PRINTED_BY[kind])
            if kind in ("cases", "stop"):
                st.markdown(plain(text))
            else:                                          # columns and line breaks matter here
                st.code(text, language=None, wrap_lines=kind == "letter")


# ---- The front door: a new matter, or a saved one.

def start_new(tenant, lease, description):
    """New matter, as run.start_new: the tenant, the lease read into its profile, the description through intake."""
    new_matter(tenant if tenant != "New tenant" else new_tenant_id())
    state.ids = (record.matter["tenant"], record.matter["id"])
    state.session = start_session("new")              # from here on, every event carries this session's id
    with st.spinner("Reading the lease. This takes a minute or two."):
        with tempfile.TemporaryDirectory() as folder:  # the upload, as a file for read_lease; the matter keeps its own copy
            path = Path(folder) / "lease.pdf"
            path.write_bytes(lease.getvalue())
            read_lease(path)
    with st.spinner("Reading your description."):
        intake(description)
    state.history.append(block("tenant", description))
    if "other" in record.matter["issues"] and candidate_playbooks():
        state.history.append(block("notice", NOT_COVERED))
    state.stage = "sheet"


def open_saved(m):
    """A saved matter, as run.start_existing: load it and open a session; what is new is asked next."""
    close_session()
    load_matter(m["tenant"], m["id"])
    if record.profile is None:
        st.sidebar.error("This matter has no lease profile yet. Start a new matter with the lease instead.")
        return
    state.ids = (m["tenant"], m["id"])
    state.session = start_session("existing")
    state.stage = "update"
    st.rerun()


def new_matter_form():
    st.subheader("New matter")
    tenants = sorted({m["tenant"] for m in list_matters()})
    with st.form("new_matter"):
        tenant = st.selectbox("Tenant", ["New tenant"] + tenants)
        lease = st.file_uploader("Your lease (PDF)", type="pdf")
        description = st.text_area("Describe the problem in your own words.", height=180)
        go = st.form_submit_button("Start")
    if go:
        if lease is None or not description.strip():
            st.error("Please add the lease PDF and describe the problem.")
            return
        need_key()
        try:
            start_new(tenant, lease, description.strip())
        except Exception as error:                     # the gateway or the PDF failed: nothing to open yet
            close_session()
            st.error(f"The lease or the description could not be read ({type(error).__name__}: {error}). "
                     "Please try again.")
            return
        st.rerun()


def update_form():
    st.subheader(f"Matter {state.ids[0]} / {state.ids[1]}")
    with st.form("update"):
        update = st.text_area("Anything new since last time? Write it in your own words, or leave it empty if "
                              "nothing is new.", height=150)
        go = st.form_submit_button("Continue")
    if go:
        if update.strip():
            need_key()
            with st.spinner("Reading what is new."):
                try:
                    added = resume(update.strip())    # logs the update, suggests issues and facts
                except Exception as error:            # the gateway failed: the session stays open
                    st.error(f"What is new could not be read ({type(error).__name__}). Please try again.")
                    return
            state.history.append(block("tenant", update.strip()))
            if "other" in added and candidate_playbooks():
                state.history.append(block("notice", NOT_COVERED))
        state.stage = "sheet"
        st.rerun()


# ---- The intake sheet as a form: one row at a time, asked and saved by code (sheet.py), no model.

def answer_widget(r):
    """The input for one row, filled in with the suggestion if there is one. Returns the answer as text, the
    way the terminal would read it: "" for nothing chosen."""
    offered = suggestion(r)
    if r["type"] == "bool":
        choice = st.radio("Your answer", ["yes", "no"], horizontal=True,
                          index=None if offered is None else (0 if offered else 1))
        return choice or ""
    if r["type"] == "date":
        picked = st.date_input("Date", value=date.fromisoformat(offered) if offered else None,
                               min_value=date(2000, 1, 1), max_value=date(2040, 12, 31), format="MM/DD/YYYY")
        return picked.isoformat() if picked else ""
    if r["type"] == "money":
        return st.text_input("Amount", value="" if offered is None else shown(offered), placeholder="1850 or $1,850.00")
    return st.text_area("Your answer", value=offered or "", height=90)


def sheet_form():
    rows = [r for r in pending_rows() if r["id"] not in state.skipped]
    if not rows:
        finish_sheet()
        st.rerun()
    r = rows[0]
    with st.container(border=True):
        st.caption("Facts for your matter. The program asks and saves these; the model is not involved. "
                   "A suggestion is filled in; change it if it is wrong.")
        st.markdown(f"**{plain(r['question'])}**")
        for line in row_notes(r):
            st.caption(plain(line))
        with st.form(f"row {r['id']}"):
            answer = answer_widget(r)
            save, skip = st.columns(2)
            saved = save.form_submit_button("Save", type="primary")
            skipped = skip.form_submit_button("Skip for now")
    if skipped:
        state.skipped.add(r["id"])
        st.rerun()
    if saved:
        if suggestion(r) is not None and answer == shown(suggestion(r)):
            answer = ""                                  # the suggestion accepted, logged as in the terminal
        value, expected = value_of(r, answer.strip())
        if expected:
            st.error(f"Please enter {expected}.")
            return
        pair, lines = save_answer(r, answer.strip(), value)
        state.saved.append(pair)
        state.history.append(block("sheet", "\n".join([f"{r['question']} {shown(value)}"] + lines)))
        st.rerun()


def finish_sheet():
    """No row left to ask. Mid-chat, the chat goes on and what was confirmed goes to the model with the next
    message. After the first sheet, as in run.py: the chat starts, or the tool stops if nothing it covers is left."""
    if state.skipped:
        state.history.append(block("notice", f"Skipped for now: {', '.join(sorted(state.skipped))}. "
                                             "Deadlines wait until these are answered."))
    if state.agent is not None:
        state.note = sheet_note(state.saved)
        state.stage = "chat"
    elif not active_playbooks():
        state.history.append(stop_block())
        end_session()
        state.session = None
        state.stage = "ended"
    else:
        need_key()
        state.agent = build_agent()                     # built after the sheet, so the prompt holds the confirmed facts
        state.config = thread_config()
        state.stage = "chat"
    state.skipped, state.saved = set(), []


# ---- The chat: a message goes to agent.command or agent.turn; their blocks join the history.

def take_message(text):
    """The tenant sent a message. A command is answered at once; anything else waits for the model's turn, run
    on the next pass so the message shows before the model starts."""
    if text.strip().lower() == "bye":
        close_session()
        return
    state.history.append(block("tenant", text))
    blocks = command(text)
    if blocks is None:
        state.pending = text
        return
    state.history += blocks
    if not active_playbooks():                          # a drop took out the last covered issue
        end_session()
        state.session = None
        state.stage = "ended"


def run_pending_turn():
    text, state.pending = state.pending, None
    with st.spinner("The model is working. The program checks its reply before you see it."):
        try:
            blocks, proposed = turn(state.agent, state.config, text, state.note)
        except Exception as error:                      # the gateway failed: say so, keep the page
            traceback.print_exc()                       # the whole error, for the terminal running streamlit
            state.history.append(block("caution", f"[Check: the model could not be reached ({type(error).__name__}). "
                                                  "Please ask again.]"))
            return
    state.note = ""
    state.history += blocks
    if proposed and pending_rows():                     # the tenant confirms the model's suggestions on the sheet
        state.stage = "sheet"


# ---- The right column: the record, drawn by the program on every run.

@st.dialog("Timeline", width="large")
def wide_timeline(text):
    """The timeline in a window as wide as the page: its table is wider than the right column."""
    st.caption(PRINTED_BY["timeline"])
    st.code(text, language=None)


def record_panel():
    timeline_tab, letter_tab = st.tabs(["Timeline", "Letter"])
    with timeline_tab:
        st.caption(PRINTED_BY["timeline"] + " Never written by the model.")
        pick, toggle = st.columns(2)
        covered = [i for i in record.matter["issues"] if i in playbooks]
        issue = pick.selectbox("Issue", ["all issues"] + covered)
        full = toggle.toggle("Full timeline", help="Adds the tool's own steps: facts confirmed, statute lookups, sessions.")
        text = render_timeline(None if issue == "all issues" else issue, full)
        st.code(text, language=None)
        if st.button("Show wide"):
            wide_timeline(text)
    with letter_tab:
        drafts = [ev for ev in read_events() if ev["kind"] == "draft"]
        if not drafts:
            st.caption("No letter drafted yet. Ask for one in the chat.")
            return
        last = drafts[-1]
        text = (matter_dir() / last["file"]).read_text()
        st.caption(f"{last['file']}: the last letter drafted, {last['posture']} posture. The tool never sends "
                   "anything; you do.")
        st.code(text, language=None, wrap_lines=True)
        st.download_button("Download the letter", text, file_name=last["file"])


# ---- The page, top to bottom.

open_record()

with st.sidebar:
    st.title("Landlord-Tenant Organizer")
    st.caption("Florida, Fla. Stat. ch. 83 part II. Applies the stored statute to your confirmed facts: the "
               "tool's reading, not a lawyer's advice. In development, for test matters only. Never sends "
               "anything. Runs on this computer only.")
    if st.button("New matter", width="stretch"):
        close_session()
        state.stage = "new"
        st.rerun()
    saved_matters = list_matters()
    pick = st.selectbox("Saved matters", saved_matters, index=None, placeholder="Choose a matter",
                        format_func=lambda m: f"{m['tenant']} / {m['id']}")
    if st.button("Open", disabled=pick is None, width="stretch"):
        open_saved(pick)
    if state.ids:
        st.divider()
        st.subheader(f"{state.ids[0]} / {state.ids[1]}")
        for i in record.matter["issues"]:
            st.markdown(f"**{plain(i)}**: {plain(playbooks[i].description if i in playbooks else 'not covered by this tool')}")
        for p in record.matter["proposed_issues"]:
            st.markdown(f"**{plain(p['issue'])}**: suggested, not yet confirmed")
        covered = [i for i in record.matter["issues"] if i in playbooks]
        if state.stage == "chat" and covered:
            drop = st.selectbox("Take an issue out of this matter", covered, index=None, placeholder="Choose an issue")
            if st.button("Drop", disabled=drop is None or bool(state.pending)):
                take_message(f"drop {drop}")
                st.rerun()
        if st.button("End session", width="stretch"):
            close_session()
            st.rerun()

middle, right = st.columns([3, 2], gap="large")
with middle:
    if state.stage == "door":
        st.subheader("Start")
        st.write("Choose New matter to begin with your lease, or open a saved matter from the list on the left.")
    elif state.stage == "new":
        new_matter_form()
    elif state.stage == "update":
        update_form()
    else:
        st.caption("A speech bubble is the model's words, checked by the program before you see them. A box is "
                   "printed by the program itself.")
        for b in state.history:
            show(b)
        if state.stage == "sheet":
            sheet_form()
        elif state.stage == "ended":
            st.info("This session has ended. Open the matter again from the list on the left to continue.")
        elif state.pending:
            run_pending_turn()
            st.rerun()
with right:
    if state.ids and record.profile is not None:
        record_panel()

if state.stage == "chat":
    message = st.chat_input("Write here, or type issues, timeline, or drop <issue>", disabled=bool(state.pending))
    if message:
        take_message(message)
        st.rerun()
