"""App: the tool as a web page on this computer (TODO item 31), the only front end since TODO item 115.

    streamlit run app.py          # then open http://localhost:8501

One page. Left (the sidebar): a new matter, the saved matters, and what the open matter is about. Middle: the front door
(a new matter: tenant, lease PDF, description; a saved one: what is new), then the chat, which starts with the description
or the update as the tenant's first message; after a turn in which the model proposed facts, the confirmation as a form,
one fact at a time, and then the model's reply to what was confirmed, at once. Right: the timeline and the last letter
drafted, drawn from the record on every run, never by the model. In the chat, a speech bubble is the model's words
(checked by the program before they are shown); a box is printed by the program itself.

The visit itself (the lease, the turns, the confirmation, the session) is run by visit.py, which the eval driver
calls too; this file draws what comes back and keeps the page's own state.

How Streamlit works, in short: it runs this whole file again, top to bottom, on every click or message. So
nothing in a plain variable survives from one run to the next. What must last is kept in st.session_state, the
page's memory for one browser tab: the open matter's ids, the stage, the visit (its session, agent, and thread), and the
chat so far as blocks. record.matter and record.profile stay in the record module as always; open_record() puts this
tab's matter back there at the top of every run.

The settings in .streamlit/config.toml keep the page on this computer (localhost) and turn off Streamlit's
usage statistics. One tab at a time: two tabs on two matters would take turns replacing record.matter.
"""
import re
import tempfile
from datetime import date
from pathlib import Path

import streamlit as st

import record
from agent import block
from config import uf_api_key
from record import list_matters, load_matter, matter_dir, read_events
from sheet import row_notes, shown, suggestion
from skills import skills
from timeline import render_timeline
from visit import Visit

st.set_page_config(page_title="Landlord-Tenant Organizer", layout="wide")
# The program's listings (deadlines, timeline, letters) are columns of fixed-width text: a smaller font fits
# more of a line before it scrolls sideways.
st.html("<style>[data-testid='stCode'] code {font-size: 0.75rem;}</style>")
state = st.session_state


# ---- The page's memory. Each key is set once, the first time this tab runs the file.

def reset():
    """Forget the open matter: back to the front door, with an empty chat and no visit."""
    state.stage = "door"            # door, new, update, sheet, chat
    state.ids = None                # (tenant id, matter id) of the open matter
    state.visit = None              # the visit (visit.py): its session, agent, and thread; made when the visit begins
    state.history = []              # everything shown in the middle column, oldest first, as blocks
    state.pending = None            # the tenant's message, waiting for the model's turn


if "stage" not in state:
    reset()


def open_record():
    """Put this tab's matter and session back into the record module. Another tab may have opened another matter
    in between, since the record module is shared by every tab of this one program."""
    if state.visit:
        state.visit.use()
    elif state.ids:                                    # a saved matter chosen, its visit not begun yet
        if (record.matter["tenant"], record.matter["id"]) != state.ids:
            load_matter(*state.ids)
        record.session = None


def close_session():
    """End the open visit's session (End session, or the tenant writing bye) and forget the matter."""
    if state.visit:
        state.visit.end()
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
    "letter": "Printed by the program from its letter tool. The date, the addresses, the reply-by date, the quotes, and "
              "the signature are the program's; the account and the request are the model's wording of what you said. "
              "Read every line before you send it. The tool never sends anything.",
    "cases": "Printed by the program from the case wiki, in the courts' own words.",
    "timeline": "Printed by the program from your record.",
    "sources": "Printed by the program: the statute's and your lease's own words that the reply above cites.",
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
    elif kind == "sources":                                # the cited words, folded away until opened (item 73)
        with st.expander("The statute and lease words cited above"):
            st.caption(PRINTED_BY[kind])
            st.markdown(plain(text.split("\n\n", 1)[1]))
    else:                                                  # deadlines, letter, cases
        with st.container(border=True):
            st.caption(PRINTED_BY[kind])
            if kind == "cases":
                st.markdown(plain(text))
            else:                                          # columns and line breaks matter here
                st.code(text, language=None, wrap_lines=kind == "letter")


# ---- The front door: a new matter, or a saved one.

def open_chat(visit, result, first=""):
    """Go to the chat with the visit begun: show the tenant's first message, if any, then what came back from the
    model's turn on it. first: the description of a new matter, or what is new."""
    state.visit = visit
    state.ids = (visit.tenant_id, visit.matter_id)
    if first:
        state.history.append(block("tenant", first))
    state.history += result.blocks
    state.stage = "sheet" if result.rows else "chat"


def start_new(tenant, lease, description):
    """New matter (Visit.new): the tenant, the lease read into its profile, the description saved, and the model's first
    turn on it. The chat opens with the description as the tenant's first message."""
    with st.spinner("Reading the lease and your description. This takes a minute or two."):
        with tempfile.TemporaryDirectory() as folder:  # the upload, as a file for the visit; the matter keeps its own copy
            path = Path(folder) / "lease.pdf"
            path.write_bytes(lease.getvalue())
            visit, result = Visit.new("" if tenant == "New tenant" else tenant, path, description)
    open_chat(visit, result, description)


def open_saved(m):
    """A saved matter: what is new is asked next, and the visit begins when the tenant continues."""
    close_session()
    state.ids = (m["tenant"], m["id"])
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
            st.error(f"The lease could not be read ({type(error).__name__}: {error}). Please try again.")
            return
        st.rerun()


def update_form():
    st.subheader(f"Matter {state.ids[0]} / {state.ids[1]}")
    with st.form("update"):
        update = st.text_area("Anything new since last time? Write it in your own words, or leave it empty if "
                              "nothing is new.", height=150)
        go = st.form_submit_button("Continue")
    if go:
        need_key()                                     # before the update is logged
        try:
            with st.spinner("The model is working. The program checks its reply before you see it."):
                visit, result = Visit.existing(*state.ids, update.strip())     # logs the update; the model reads it first
        except ValueError as error:                    # the matter has no lease profile
            st.error(str(error))
            return
        open_chat(visit, result, update.strip())
        st.rerun()


# ---- The confirmation as a form: one fact at a time, asked and saved by code (sheet.py, run by the visit), no model for
# the answers. It follows a turn in which the model proposed facts: the tenant confirms what they said, or corrects it.

def answer_widget(r):
    """The input for one row, filled in with the suggestion if there is one. Returns the answer as text: "" for
    nothing chosen. By the row's type: a date picker, yes/no, a county in a line, any other fact in words."""
    offered = suggestion(r)
    if r["type"] == "bool":
        choice = st.radio("Your answer", ["yes", "no"], horizontal=True,
                          index=None if offered is None else (0 if offered else 1))
        return choice or ""
    if r["type"] == "date":
        picked = st.date_input("Date", value=date.fromisoformat(offered) if offered else None,
                               min_value=date(2000, 1, 1), max_value=date(2040, 12, 31), format="MM/DD/YYYY")
        return picked.isoformat() if picked else ""
    if r["type"] == "county":
        return st.text_input("County", value=offered or "")
    return st.text_area("Your answer", value=offered or "", height=90)


def sheet_form():
    rows = state.visit.rows()
    if not rows:
        state.stage = "chat"
        st.rerun()
    r = rows[0]
    with st.container(border=True):
        st.caption("Please confirm what you told me. The program saves these; the model is not involved. "
                   "The suggestion is filled in; change it if it is wrong.")
        st.markdown(f"**{plain(r['label'])}**")
        for line in row_notes(r):
            st.caption(plain(line))
        with st.form(f"row {r['id']}"):
            answer = answer_widget(r)
            save, skip = st.columns(2)
            saved = save.form_submit_button("Save", type="primary")
            skipped = skip.form_submit_button("Skip for now")
    if saved or skipped:
        if saved and suggestion(r) is not None and answer == shown(suggestion(r)):
            answer = ""                                  # the suggestion accepted, logged as typed ""
        # the last row also brings the model's reply to what was confirmed (Visit.confirm), so this can take a while
        with st.spinner("The model is working. The program checks its reply before you see it."):
            result = state.visit.confirm({r["id"]: "?" if skipped else answer.strip()})
        if result.refused:
            st.error(f"Please enter {result.refused[r['id']]}.")
            return
        state.history += result.blocks
        state.stage = "sheet" if result.rows else "chat"
        st.rerun()


# ---- The chat: a message goes to the visit (Visit.say); its blocks join the history.

def take_message(text):
    """The tenant sent a message. It waits for the model's turn, run on the next pass so the message shows before
    the model starts. bye ends the session."""
    if text.strip().lower() == "bye":
        close_session()
        return
    state.history.append(block("tenant", text))
    state.pending = text


def run_pending_turn():
    text, state.pending = state.pending, None
    with st.spinner("The model is working. The program checks its reply before you see it."):
        result = state.visit.say(text)                  # a gateway error comes back as a caution
    state.history += result.blocks
    if result.rows:                                     # the tenant confirms the model's proposals
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
        loaded = [skill.name for skill in record.active_skills()]
        about = pick.selectbox("Part of the matter", ["all"] + loaded,
                               format_func=lambda name: "all" if name == "all" else skills[name].description)
        full = toggle.toggle("Full timeline", help="Adds the tool's own steps: skills loaded, facts confirmed, statute lookups, sessions.")
        text = render_timeline(None if about == "all" else about, full)
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
        loaded = record.active_skills()
        if loaded:                                      # what the model has loaded, in the skills' own words (no ids)
            st.markdown("**What this matter is about**")
            for skill in loaded:
                st.markdown(f"- {plain(skill.description)}")
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
        elif state.pending:
            run_pending_turn()
            st.rerun()
with right:
    if state.ids and record.profile is not None:
        record_panel()

if state.stage == "chat":
    message = st.chat_input("Write here", disabled=bool(state.pending))
    if message:
        take_message(message)
        st.rerun()
