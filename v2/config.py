"""Settings in one place: where things live, the gateway key, and the models.
The key comes from .env next to this file. The chat model can be changed with AGENT_MODEL in the environment.
"""
import os
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

HERE = Path(__file__).resolve().parent
STATUTES = HERE / "statutes"
SKILLS = HERE / "skills"
MATTERS = HERE / "matters"

GATEWAY = "https://api.ai.it.ufl.edu/v1"
AGENT_MODEL = os.environ.get("AGENT_MODEL", "nemotron-3-super-120b-a12b")
VISION_MODEL = "gemma-4-31b-it"          # reads lease pages that have no usable text (scans, broken PDFs)


def client():
    """The UF gateway, using the key in .env (or UF_API_KEY in the environment)."""
    key = os.environ.get("UF_API_KEY") or dotenv_values(HERE / ".env").get("UF_API_KEY")
    if not key:
        raise RuntimeError("UF_API_KEY is not set. Copy .env.example to .env and put the key there.")
    return OpenAI(base_url=GATEWAY, api_key=key)
