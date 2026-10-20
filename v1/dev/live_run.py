"""Live Run: play a whole visit from a scenario file, in this program, through visit.py, the way the web page runs one.

    python dev/live_run.py dev/scenarios/nonpayment_3day.json [--tenant <id>]

A scenario is a JSON file (the format is in DOCUMENTATION.md, Running and testing):
  "start"    a new matter, {"tenant", "lease", "description"}, or a saved one, {"tenant", "matter", "update"}.
             The description or the update is the tenant's first message, as on the page.
  "confirm"  rules for the confirmation that follows a turn in which the model proposed facts: a piece of a fact's
             label or id -> a list of answers, used in order, so a bad answer then a good one tests a correction. A
             row no rule matches is accepted (the suggestion is kept). When several rules match, the longest one
             with answers left is used. Optional.
  "chat"     the tenant's messages after the first one, one at a time.
  "expect"   what dev/eval.py scores; this driver does not read it.

--tenant replaces the scenario's tenant (dev/eval.py gives each run its own scratch tenant).

It calls the model and writes a real matter under matters/, so use a test tenant (t-test). It prints the screen as it
goes, and the visit ends when the last message has its answer. The screen:
  MATTER: <tenant>/<matter id>      the first line (dev/eval.py reads the matter id from it)
  TENANT: ...                       what the tenant typed
  MODEL: ...                        a reply of the model
  PROGRAM (<kind>): ...             any other block: sources, caution, footer, deadlines, letter, cases, sheet, notice
  CONFIRM <label>: suggested <value>; answered <the answer, or accepted>
"""
import contextlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent            # the project folder
sys.path.insert(0, str(ROOT))                            # its modules: visit, sheet, config

from config import require_key                           # noqa: E402  (after the path is set)
from sheet import shown                                  # noqa: E402
from visit import Visit                                  # noqa: E402

MAX_ANSWERS = 100                                        # a confirmation that goes past this is stuck, not slow
# What reading a lease prints that the screen leaves out: its page listing, its hash, and the agent's "skills loaded".
READING_NOISE = re.compile(r"^(p\s*\d+\s|sha256 |skills loaded)")


def say(text=""):
    """One line (or more) of the screen. Flushed, so a run that is cut off still shows how far it got."""
    print(text, flush=True)


def show(blocks):
    """The blocks as the tenant would see them, each marked by who produced it: the model's reply, or the program's."""
    for b in blocks:
        who = "MODEL" if b["kind"] == "reply" else f"PROGRAM ({b['kind']})"
        say(f"\n{who}: {b['text']}")


def pick_answer(row, rules):
    """The next answer the rules give a row: from the longest rule key found, as whole words, in the row's label or id
    that still has answers ("claim notice date" is not found in "claim notice dated"). "" (accept the suggestion) when
    no rule has an answer left."""
    text = f"{row['label']} {row['id']}".lower()
    keys = [k for k in rules if rules[k] and re.search(r"\b" + re.escape(k.lower()) + r"\b", text)]
    return rules[max(keys, key=len)].pop(0) if keys else ""


def confirm_all(visit, result, rules):
    """Answer the confirmation a row at a time, as the page does, until no row is open. An answer that does not fit
    leaves its row open and the next answer is used for it; an accepted suggestion that does not fit the row's type is
    skipped with "?" so the loop ends. Returns the last result."""
    gave_up = set()                                      # rows whose empty answer was refused: skipped next time
    for _ in range(MAX_ANSWERS):
        if not result.rows:
            return result
        row = result.rows[0]
        answer = "?" if row["id"] in gave_up else pick_answer(row, rules)
        line = f"CONFIRM {row['label']}: suggested {shown(row['suggested'])}; answered {answer or 'accepted'}"
        result = visit.confirm({row["id"]: answer})
        if row["id"] in result.refused:
            line += f"; refused, expected {result.refused[row['id']]}"
            if answer == "":
                gave_up.add(row["id"])
        say("\n" + line)
        show(result.blocks)
    raise RuntimeError(f"the confirmation went on past {MAX_ANSWERS} answers")


def play(scenario, tenant=None):
    """Play the scenario: the first message, the confirmation after each turn that proposed facts, each chat message,
    then end the visit. `tenant` replaces the scenario's. Prints the screen as it goes."""
    start = scenario["start"]
    tenant = tenant or start["tenant"]
    rules = {k: list(v) for k, v in scenario.get("confirm", {}).items()}
    if "lease" in start:                                 # a new matter; the lease is read first
        lease = ROOT / start["lease"]                    # (an absolute path stays as it is)
        if not lease.is_file():
            sys.exit(f"no lease at {lease}")
        with contextlib.redirect_stdout(io.StringIO()) as noise:    # the lease check's lines, said after the first line
            visit, result = Visit.new(tenant, lease, start["description"])
        first = start["description"]
    else:                                                # a saved matter; no update means the chat waits
        with contextlib.redirect_stdout(io.StringIO()) as noise:
            visit, result = Visit.existing(tenant, start["matter"], start.get("update", ""))
        first = start.get("update", "")
    say(f"MATTER: {visit.tenant_id}/{visit.matter_id}")
    lease_check = [line for line in noise.getvalue().splitlines() if line.strip() and not READING_NOISE.match(line)]
    if lease_check:
        say("\nPROGRAM (lease check):\n" + "\n".join(lease_check))
    if first:
        say(f"\nTENANT: {first}")
    show(result.blocks)
    result = confirm_all(visit, result, rules)
    for text in scenario["chat"]:
        say(f"\nTENANT: {text}")
        result = visit.say(text)
        show(result.blocks)
        result = confirm_all(visit, result, rules)
    visit.end()
    unused = {k: v for k, v in rules.items() if v}
    if unused:
        say(f"\nUnused confirm answers: {unused}")


def main(scenario_path, tenant=None):
    require_key()                                        # this script calls the models; stop here if the key is missing
    scenario = json.loads(Path(scenario_path).read_text())
    try:
        play(scenario, tenant)
    except Exception as error:                           # said on the screen too, for dev/eval.py's gateway signs
        say(f"\nTHE RUN STOPPED ({type(error).__name__}): {error}")
        raise


if __name__ == "__main__":
    args = sys.argv[1:]
    tenant_id = args.pop(args.index("--tenant") + 1) if "--tenant" in args else None
    if "--tenant" in args:
        args.remove("--tenant")
    main(args[0], tenant_id)
