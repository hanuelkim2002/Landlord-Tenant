"""Setup: paths, models, and the one string helper every other module uses.

Replaces the Colab cells that read the key from userdata and mounted Drive.
The key now comes from a .env file next to this module (see .env.example). It is needed only to call a model.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()                                   # reads .env in the current folder into os.environ

ROOT = Path(__file__).resolve().parent          # the project folder, wherever it lives
MATTERS = ROOT / "matters"
STATUTES = ROOT / "statutes"
CASES = ROOT / "cases"                          # court opinions, the court's text only (dev/build_cases.py)
WIKI = ROOT / "wiki"                            # the case wiki: case and topic pages written from cases/ (wiki.py)
# Development runs only: WIKI_UNVERIFIED=1 lets the chat show case pages the author has not verified yet, each
# marked as such, so the wiring can be tried before verification. Never set for a tenant.
WIKI_UNVERIFIED = os.environ.get("WIKI_UNVERIFIED") == "1"
PLAYBOOKS = ROOT / "playbooks"
SKILLS = ROOT / "skills"                        # the model's instructions, one markdown file per situation (skills.py)

UF_BASE_URL = "https://api.ai.it.ufl.edu"
uf_api_key = os.environ.get("UF_API_KEY")

# AGENT_MODEL can be set in the environment to try another gateway model for one run, e.g.
# AGENT_MODEL=gpt-oss-120b python dev/live_run.py ... ; it drives the chat, classify, and fill_facts.
AGENT_MODEL   = os.environ.get("AGENT_MODEL", "nemotron-3-super-120b-a12b")   # LOCAL, text only
EXTRACT_MODEL = "gemma-4-31b-it"               # LOCAL, text + image

# The model clients exist only when the key is set. Without it they are None, so the offline checks
# (smoke.py, the playbook quote check, schemas.py) still import and run. Anything that calls a model
# calls require_key() first.
if uf_api_key:
    # 8000 since applied answers (rules version G, cases set beside the facts) run longer; at 4000 one stopped
    # mid-sentence (TODO item 47). agent.turn_blocks warns the tenant when a reply still stops at the limit.
    agent_llm   = ChatOpenAI(model=AGENT_MODEL,   base_url=UF_BASE_URL, api_key=uf_api_key, temperature=0, max_tokens=8000)
    extract_llm = ChatOpenAI(model=EXTRACT_MODEL, base_url=UF_BASE_URL, api_key=uf_api_key, temperature=0, max_tokens=8000)
else:
    agent_llm = extract_llm = None


def require_key():
    """Stop with a clear message if the key is missing. Called at the top of every script that calls a model."""
    if not uf_api_key:
        raise RuntimeError("UF_API_KEY is not set. Copy .env.example to .env and put the key there.")


def squash(text):
    """Collapse all whitespace to single spaces, lowercase. For comparing quotes."""
    return " ".join(text.split()).lower()


def shorten(text, limit, rest=""):
    """The text as is, or, when it runs past `limit` characters, its words up to there, then " ..." and `rest` (where
    to read the rest, e.g. "(the rest is in Fla. Stat. 83.49(3)(a))"). For a passage printed or shown in full."""
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + " ..." + (f" {rest}" if rest else "")
