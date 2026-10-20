"""Visit: one tenant's visit to one matter, from opening it to ending it. The steps the web page ran in app.py (and the
terminal in agent.chat) are here once, so the web page and the eval driver run a visit the same way.

    visit, result = Visit.new(tenant_id, pdf_path, description)    # a new matter: read the lease, then the first turn
    visit, result = Visit.existing(tenant_id, matter_id, update)   # a saved matter: the update, if any, is the first turn
    result = visit.say(text)           # one tenant message
    result = visit.confirm(answers)    # the tenant's answers to the confirmation's rows
    visit.end()                        # the session ends (the caller decides what "bye" means; it is not handled here)

A Result is what the caller shows and asks: `blocks` (agent.py's BLOCK KINDS, in order; a "sheet" block is an answer
just saved), `rows` (the confirmation rows to answer now, sheet.pending_rows, empty when there are none), and `refused`
(an answer that did not fit its row, with what it expects, so the caller asks that row again).

The flow after a turn in which the model proposed facts: the tenant answers the rows (confirm, one call per row or all
at once); when every row is answered or skipped, the model replies at once to what was confirmed (agent.after_confirmation),
once per tenant message. If that reply proposes facts again, the rows come again, but what the tenant confirms then waits
and goes with their next message (`note`), so the loop cannot run on.

Every record the visit touches is shared by every visit in this program (record.matter, record.profile, record.session),
so each method first puts its own matter and session back (use), as the web page did at the top of every run.
"""
import traceback
from dataclasses import dataclass, field

import agent
import record
from sheet import pending_rows, save_answer, shown, skipped_note, value_of


@dataclass
class Result:
    """What one call returns for the caller to show and ask."""
    blocks: list = field(default_factory=list)       # what to show, in order: agent.py's blocks
    rows: list = field(default_factory=list)         # the confirmation rows to answer now (sheet.pending_rows)
    refused: dict = field(default_factory=dict)      # {fact id: what is expected} for each answer that did not fit


def failed(error):
    """The caution shown when the model could not be reached. The whole error goes to the terminal running the page."""
    traceback.print_exc()
    return agent.block("caution", f"[Check: the model could not be reached ({type(error).__name__}). Please ask again.]")


class Visit:
    def __init__(self, tenant_id, matter_id):
        self.tenant_id, self.matter_id = tenant_id, matter_id
        self.session_id = None          # this visit's session (record.session while the visit is in use)
        self.agent = self.config = None  # the model's agent and its chat thread, built by start
        self.note = ""                  # what the tenant confirmed after the automatic reply: goes with their next message
        self.replied = False            # the model has already replied to a confirmation of this tenant message
        self.skipped = set()            # fact ids skipped in the confirmation now open
        self.saved = []                 # (fact id, value) pairs saved in the confirmation now open
        self.ended = False

    # ---- Beginning a visit. Both return the visit and the result of its first turn.

    @classmethod
    def new(cls, tenant_id, pdf_path, description):
        """A new matter for the tenant ("" for a new tenant): open a session, read the lease into its profile, save the
        description, and run the first turn with the description as the tenant's first message."""
        record.new_matter(tenant_id or record.new_tenant_id())
        visit = cls(record.matter["tenant"], record.matter["id"])
        visit.session_id = record.start_session("new")      # from here on, every event carries this session's id
        try:
            agent.read_lease(pdf_path)
        except Exception:
            record.end_session()                            # a lease that could not be read leaves no session open
            raise
        agent.intake(description)
        visit.start()
        return visit, visit.say(description)

    @classmethod
    def existing(cls, tenant_id, matter_id, update=""):
        """A saved matter, which must have a lease profile: open a session, log the update if there is one, and run
        the first turn with the update as the tenant's first message. With no update the result is empty."""
        record.load_matter(tenant_id, matter_id)
        if record.profile is None:
            raise ValueError("This matter has no lease profile yet. Start a new matter with the lease instead.")
        visit = cls(tenant_id, matter_id)
        visit.session_id = record.start_session("existing")  # before the update, so the update belongs to this session
        if update:
            agent.resume(update)
        visit.start()
        return visit, (visit.say(update) if update else Result())

    def start(self):
        """Build the agent and its chat thread. No model call."""
        self.use()
        self.agent = agent.build_agent()
        self.config = agent.thread_config()

    def use(self):
        """Put this visit's matter and session back into the record module. Another visit may have opened another
        matter in between."""
        if (record.matter["tenant"], record.matter["id"]) != (self.tenant_id, self.matter_id):
            record.load_matter(self.tenant_id, self.matter_id)
        record.session = None if self.ended else self.session_id

    # ---- The tenant's turn.

    def say(self, text):
        """One tenant message: the model's turn on it, with the note the last confirmation left in front of it. When
        the model proposed facts, the result holds the rows to confirm."""
        self.use()
        self.replied, self.skipped, self.saved = False, set(), []
        try:
            blocks, proposed = agent.turn(self.agent, self.config, text, self.note)
        except Exception as error:                      # the gateway failed: the note stays for the next message
            return Result([failed(error)])
        self.note = ""
        return self.result(blocks, proposed)

    def rows(self):
        """The confirmation rows still to answer: each pending row not skipped in the confirmation now open."""
        self.use()
        return [r for r in pending_rows() if r["id"] not in self.skipped]

    def result(self, blocks, proposed):
        """The result of a turn: its blocks, and the rows to confirm when the model proposed facts."""
        return Result(blocks, self.rows() if proposed else [])

    def confirm(self, answers):
        """The tenant's answers to the confirmation's rows, {fact id: answer}: "" accepts the suggestion, "?" skips the
        row for now (its proposal stays pending), anything else is the tenant's correction, parsed by the row's type
        (sheet.value_of). An answer that does not fit is not saved: it is in `refused` with what is expected, and its
        row stays open for the caller to ask again. A row not in `answers` stays open. When no row is open (all answered
        or skipped) the tenant is told what was skipped and the model replies at once to what was confirmed, once per
        tenant message; otherwise the result holds the rows still open."""
        self.use()
        blocks, refused = [], {}
        for r in self.rows():
            if r["id"] not in answers:
                continue
            answer = answers[r["id"]].strip()
            if answer == "?":
                self.skipped.add(r["id"])
                continue
            value, expected = value_of(r, answer)
            if expected:
                refused[r["id"]] = expected
                continue
            self.saved.append(save_answer(r, answer, value))
            blocks.append(agent.block("sheet", f"{r['label']}: {shown(value)}"))
        rows = self.rows()
        if rows:
            return Result(blocks, rows, refused)
        return self.finish(blocks)

    def finish(self, blocks):
        """Every row is answered or skipped: say what was skipped, and let the model reply to what was confirmed."""
        skipped, saved = self.skipped, self.saved
        self.skipped, self.saved = set(), []
        if skipped:
            blocks.append(agent.block("notice", skipped_note(skipped)))
        if not saved or self.replied:                   # nothing to tell the model, or it already replied to this message
            self.note = agent.sheet_note(saved)
            return Result(blocks)
        self.replied = True
        try:
            more, proposed = agent.after_confirmation(self.agent, self.config, saved)
        except Exception as error:                      # the model has not heard it: it goes with the next message
            self.note = agent.sheet_note(saved)
            return Result(blocks + [failed(error)])
        return self.result(blocks + more, proposed)

    def end(self):
        """End the session. Does nothing the second time."""
        if self.ended:
            return
        self.use()
        record.end_session()
        self.ended = True
