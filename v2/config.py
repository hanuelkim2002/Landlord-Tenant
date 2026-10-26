"""Settings in one place: where things live, which gateway each model comes from, its key, and the models.
Keys come from .env next to this file. GATEWAY, AGENT_MODEL, READER_GATEWAY, and VISION_MODEL in the environment
change the defaults.
"""
import os
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

HERE = Path(__file__).resolve().parent
STATUTES = HERE / "statutes"
SKILLS = HERE / "skills"
MATTERS = HERE / "matters"

# "uf" keeps the data at UF. "openrouter" reaches outside models (Claude, Gemini). "anthropic" is Claude straight
# from Anthropic, through its OpenAI-compatible endpoint, so the same code works; Anthropic calls that endpoint a
# testing tool, and it has no prompt caching.
GATEWAYS = {
    "uf": {"url": "https://api.ai.it.ufl.edu/v1", "key": "UF_API_KEY",
           "agent": "nemotron-3-super-120b-a12b", "vision": "gemma-4-31b-it"},
    "openrouter": {"url": "https://openrouter.ai/api/v1", "key": "OPENROUTER_API_KEY",
                   "agent": "google/gemini-3.8-flash", "vision": "anthropic/claude-haiku-5.5"},
    "anthropic": {"url": "https://api.anthropic.com/v1/", "key": "ANTHROPIC_API_KEY",
                  "agent": "claude-sonnet-5-5", "vision": "claude-haiku-5-5"},
}

# The chat: Claude Sonnet 5.5 from Anthropic (the author's choice, 2026-10-23, to use the Anthropic API credit; in
# comparisons/models/ Sonnet answered every settled deposit story right). AGENT_MODEL=claude-haiku-5-5 is the cheaper
# choice. So the chat, with the tenant's facts, goes to Anthropic.
GATEWAY = os.environ.get("GATEWAY", "anthropic")
AGENT_MODEL = os.environ.get("AGENT_MODEL", GATEWAYS[GATEWAY]["agent"])

# The lease reader: every page is read from its image by Haiku 5.5 (the author's choice, 2026-10-21, after
# comparisons/models/, where it read every typed-in value and check box), from Anthropic since 2026-10-23. So every
# lease goes to Anthropic.
READER_GATEWAY = os.environ.get("READER_GATEWAY", "anthropic")
VISION_MODEL = os.environ.get("VISION_MODEL", GATEWAYS[READER_GATEWAY]["vision"])


def temperature(gateway):
    """What to add to a request on this gateway. Temperature 0 keeps the UF models' answers steady. Claude 4.7 and
    later rejects a temperature below 1, and Google advises against it for Gemini 3, so on OpenRouter each model keeps
    its own default."""
    return {"temperature": 0} if gateway == "uf" else {}


def client(gateway=None):
    """A gateway (the chat's, unless named), using its key from .env (or from the environment)."""
    gateway = gateway or GATEWAY
    name = GATEWAYS[gateway]["key"]
    key = os.environ.get(name) or dotenv_values(HERE / ".env").get(name)
    if not key:
        raise RuntimeError(f"{name} is not set. Copy .env.example to .env and put the key there.")
    return OpenAI(base_url=GATEWAYS[gateway]["url"], api_key=key)
