"""The web page, on this computer only: start a matter (a lease PDF and a description) or open a saved one, chat
with the tool, confirm the facts it noted, and read the timeline it keeps. Run from this folder: streamlit run app.py
"""
import tempfile

import streamlit as st

import chat
import lease
import record

st.set_page_config(page_title="Landlord-Tenant v2", layout="wide")


def safe(text):
    """Text for the page as written: a "$" would otherwise start a math formula in Streamlit's markdown."""
    return text.replace("$", "\\$")


def open_matter():
    """The matter open in this browser tab, read fresh from its folder, or None."""
    key = st.session_state.get("open")
    return record.load(*key) if key else None


def start_matter(tenant, description, upload):
    """Make a matter from the form: store and read the lease, then answer the description as the first message."""
    m = record.new_matter(tenant, description)
    with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf:
        pdf.write(upload.getvalue())
        pdf.flush()
        with st.spinner("Reading the lease..."):
            lease.read_lease(m, pdf.name)
    st.session_state["open"] = (m["tenant"], m["matter"])
    with st.spinner("Answering..."):
        chat.reply(m, description)


def choose_matter():
    """The sidebar's choice: open a saved matter, or start one from a lease PDF and a description."""
    with st.sidebar:
        st.header("Matter")
        saved = {f"{t} / {mid}: {d[:40]}": (t, mid) for t, mid, d in record.saved_matters()}
        if saved:
            choice = st.selectbox("Open a saved matter", list(saved))
            if st.button("Open"):
                st.session_state["open"] = saved[choice]
                st.rerun()
        with st.form("new"):
            st.subheader("New matter")
            tenant = st.text_input("Tenant id (lowercase, like t-jordan)")
            description = st.text_area("What happened")
            upload = st.file_uploader("The lease (PDF)", type="pdf")
            if st.form_submit_button("Start"):
                if not (tenant.strip() and description.strip() and upload):
                    st.error("Give a tenant id, what happened, and the lease.")
                else:
                    try:
                        start_matter(tenant.strip(), description.strip(), upload)
                        st.rerun()
                    except ValueError as problem:
                        st.error(str(problem))


def confirm_facts(m):
    """The sidebar's facts: each one the tool noted, with a box to correct it and a Confirm button; then the confirmed."""
    with st.sidebar:
        st.header("Facts to confirm")
        if not m["pending"]:
            st.caption("None waiting.")
        for name, fact in list(m["pending"].items()):
            st.markdown(f"**{name}**")
            st.caption(safe(f"You said: {fact['tenant_words']}"))
            value = st.text_input("Value (correct it if it is wrong)", fact["value"], key=f"value-{name}")
            if st.button("Confirm", key=f"confirm-{name}"):
                record.confirm_fact(m, name, value.strip())
                st.rerun()
        st.header("Confirmed facts")
        if not m["confirmed"]:
            st.caption("None yet.")
        for name, fact in m["confirmed"].items():
            st.markdown(safe(f"**{name}**: {fact['value']}"))


def show_timeline(m):
    """The sidebar's timeline, to read only: to fix a line, the tenant tells the tool."""
    with st.sidebar:
        st.header("Timeline")
        if not m["lines"]:
            st.caption("None yet.")
        for number, line in m["lines"].items():
            st.markdown(safe(f"**{number}.** {line['date'] or 'no date'}: {line['what']}")
                        + (" *(open)*" if line["open"] else ""))


def show_reply(text):
    """A reply from the tool: the short answer first, then each point behind a click, so the reasons cost no wait."""
    short, points = chat.split_reply(text)
    st.markdown(safe(short))
    for title, body in points:
        with st.expander(safe(title)):
            st.markdown(safe(body))


def show_checks(shown):
    """Under a reply: whether each quotation checks out word for word, and the words each cite points to."""
    if not shown or not (shown["quotes"] or shown["cited"]):
        return
    with st.expander("Quotes checked, and the cited words"):
        for q in shown["quotes"]:
            verdict = "Checks out" if q["ok"] else "**Does not check out**"
            st.markdown(safe(f"{verdict} ({q['where']}): “{q['quote']}”"))
        for c in shown["cited"]:
            st.markdown(f"**{c['cite']}**")
            st.caption(safe(c["words"]))


choose_matter()
st.title("Landlord-Tenant tool, v2")
st.caption("In development, on test matters only.")
m = open_matter()
if m is None:
    st.info("Start a new matter or open a saved one in the sidebar.")
    st.stop()
confirm_facts(m)
show_timeline(m)
pages = lease.lease_pages(m)
from_images = sum(p["read_by"] == "image" for p in pages)
st.caption(f"{m['tenant']} / {m['matter']}. Lease: {len(pages)} pages"
           + (f", {from_images} read from page images" if from_images else "")
           + f". Skills loaded: {', '.join(m['skills']) or 'none yet'}.")
for message in record.chat(m):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            show_reply(message["text"])
            show_checks(message["checks"])
        else:
            st.markdown(safe(message["text"]))
if text := st.chat_input("Write to the tool"):
    with st.spinner("Answering..."):
        chat.reply(m, text)
    st.rerun()
