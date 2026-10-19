"""Baseline: v1's lease method, run with v1's own code, imported from v1/ and never edited. PyPDF2 reads the PDF,
Gemma 4 fills v1's form of four clauses (each quote checked), and nemotron gets those clauses and v1's exact-phrase
search_lease. Needs v1's packages (LangChain), so run it with v1's venv: ../../../../venv/bin/python v1_baseline.py
"""
import ast
import contextlib
import io
import os
import sys
import tempfile
from pathlib import Path

from dotenv import dotenv_values

import common

V1 = common.LEASE_DIR.parents[2] / "v1"
SAMPLE = Path(os.environ.get("SAMPLE_LEASE", common.LEASE_DIR.parents[1] / "lease.pdf"))
os.environ["UF_API_KEY"] = dotenv_values(common.ENV_FILE)["UF_API_KEY"]    # v1's config reads the key from here
sys.path.insert(0, str(V1))
import lease as v1_lease                                                    # noqa: E402  (v1's own module)
from config import shorten                                                  # noqa: E402

SEARCH_SHOWN = 1500                       # v1's SEARCH_SHOWN: characters of one clause the model gets
# v1's lease part of the system prompt (v1/prompt.py, PARTS["lease"]), word for word.
YOUR_LEASE = ("YOUR LEASE (only the clauses the tool reads from the tenant's lease, not the whole lease: the landlord, "
              "the tenants, the unit, and where and how notices go, each in plain words, with the cite to use and its "
              "words; search_lease searches the whole lease's text, so use it for anything else in the lease, such as "
              "the rent, the term, the deposit, or repairs)")


def v1_search_description():
    """v1's search_lease docstring, read from v1/tools.py without running it: the description its model saw."""
    tree = ast.parse((V1 / "tools.py").read_text())
    found = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "search_lease")
    return " ".join(ast.get_docstring(found).split())


TOOLS = [{"type": "function", "function": {
    "name": "search_lease", "description": v1_search_description(),
    "parameters": {"type": "object", "properties": {"phrase": {"type": "string"}}, "required": ["phrase"]}}}]


def pdf_of(lease):
    """Where the lease's PDF is: v1 starts from the PDF, not from step 1's text."""
    return SAMPLE if lease == "sample_v1" else common.LEASE_DIR / "leases" / f"{lease}.pdf"


def setup(lease):
    """v1's intake: PyPDF2's pages, then Gemma 4's four-clause form, then v1's quote check."""
    with contextlib.redirect_stdout(io.StringIO()):                        # v1 prints a line per page
        pages = v1_lease.ingest_pdf(pdf_of(lease), Path(tempfile.mkdtemp()))
        try:
            profile = v1_lease.extract_profile(pages)
            v1_lease.check_quotes(profile, pages)
        except Exception:                                                  # Gemma's form could not be read
            profile = None
    return {"pages": pages, "profile": profile}


def lease_part(state):
    """v1's YOUR LEASE block: the four clauses, as v1's prompt showed them."""
    if state["profile"] is None:
        return f"{YOUR_LEASE}:\n- the tool's reading of the lease failed; use search_lease"
    return f"{YOUR_LEASE}:\n{v1_lease.lease_lines(state['profile'])}"


def search_lease(state, name, arguments):
    """v1's search_lease reply, built as v1/tools.py builds it, from v1's find_in_lease."""
    phrase, pages = str(arguments.get("phrase", "")), state["pages"]
    clauses, outside = v1_lease.find_in_lease(phrase, pages)
    if not clauses and not outside:
        return (f"No clause or page of the lease's text ({len(pages)} pages) holds \"{phrase}\". The lease may say it in "
                "other words: try another wording before you say the lease has no such term. If no wording is found, "
                "the tool found nothing on it in the lease's text.")
    lines = [f"\"{phrase}\" is in the lease's text ({len(pages)} pages searched):"]
    for c in clauses:
        lines.append(f"- Lease Section {c['number']}, {c['title']}, page {c['page']}: \"{shorten(c['text'], SEARCH_SHOWN)}\"")
    lines += [f"- Lease, page {pg}, outside any numbered clause: \"...{words}...\"" for pg, words in outside]
    lines.append("Cite a clause as given here; the program prints its words under your reply.")
    return "\n".join(lines)


if __name__ == "__main__":
    common.run("v1", setup, lease_part, lambda state: TOOLS, search_lease)
