"""Run: load the lease profile (extracting it with Gemma the first time), then intake and chat.

    python run.py
"""
from config import ROOT, require_key
require_key()                   # this script calls the models; stop here if the key is missing

import record
from agent import chat, intake
from lease import LeaseProfile, check_quotes, extract_profile, ingest_pdf
from record import matter_dir

# ---- Lease intake. Gemma runs once per matter; after that the saved profile is reused.
profile_path = matter_dir() / "lease_profile.json"
if profile_path.exists():
    record.profile = LeaseProfile.model_validate_json(profile_path.read_text())
    print("loaded", profile_path)
else:
    pages = ingest_pdf(ROOT / "lease.pdf", matter_dir())
    record.profile = extract_profile(pages)
    check_quotes(record.profile, pages)
    profile_path.write_text(record.profile.model_dump_json(indent=2))

# ---- The dispute.
description = """I rented a house in Gainesville. My lease ended July 31, 2026 and I moved out
and gave the keys back on July 30, 2026. I emailed the property manager my new address the same
day. It's September now and I haven't gotten my $1,850 deposit back or any letter about it."""

agent = intake(description)
chat(agent)
