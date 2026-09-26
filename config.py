"""Setup: paths, models, and the one string helper every other module uses.

Replaces the Colab cells that read the key from userdata and mounted Drive.
The key now comes from a .env file next to this module (see .env.example).
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()                                   # reads .env in the current folder into os.environ

ROOT = Path(__file__).resolve().parent          # the project folder, wherever it lives
MATTERS = ROOT / "matters"
STATUTES = ROOT / "statutes"
PLAYBOOKS = ROOT / "playbooks"

UF_BASE_URL = "https://api.ai.it.ufl.edu"
uf_api_key = os.environ.get("UF_API_KEY")
if not uf_api_key:
    raise RuntimeError("UF_API_KEY is not set. Copy .env.example to .env and put the key there.")

AGENT_MODEL   = "nemotron-3-super-120b-a12b"   # LOCAL, text only
EXTRACT_MODEL = "gemma-4-31b-it"               # LOCAL, text + image

agent_llm   = ChatOpenAI(model=AGENT_MODEL,   base_url=UF_BASE_URL, api_key=uf_api_key, temperature=0, max_tokens=4000)
extract_llm = ChatOpenAI(model=EXTRACT_MODEL, base_url=UF_BASE_URL, api_key=uf_api_key, temperature=0, max_tokens=8000)


def squash(text):
    """Collapse all whitespace to single spaces, lowercase. For comparing quotes."""
    return " ".join(text.split()).lower()
