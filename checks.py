"""Checks: helpers for the smoke scripts. Named checks that print OK or FAIL, and a throwaway copy of the test
matter for code that writes to a matter (so the test matter itself is never changed by a smoke run)."""
import json
import shutil

from config import MATTERS

TEST_MATTER = MATTERS / "t-test" / "test-001"
failures = []


def check(name, condition):
    """Print one named check. Every line must be OK, like the playbook quote checks."""
    print(("OK   " if condition else "FAIL ") + name)
    if not condition:
        failures.append(name)


def summary():
    """The last line of a smoke run."""
    print(f"\n{'all checks OK' if not failures else str(len(failures)) + ' FAILED: ' + ', '.join(failures)}")


def make_scratch(tenant_id, **changes):
    """Copy the test matter to matters/<tenant_id>/m-001, without its transcripts, and change matter.json keys
    (for example facts=..., issues=...). Removes any copy a crashed run left behind first."""
    remove_scratch(tenant_id)
    folder = MATTERS / tenant_id / "m-001"
    shutil.copytree(TEST_MATTER, folder, ignore=shutil.ignore_patterns("sessions"))
    saved = json.loads((folder / "matter.json").read_text())
    saved.update({"tenant": tenant_id, "id": "m-001", **changes})
    (folder / "matter.json").write_text(json.dumps(saved, indent=2))


def remove_scratch(tenant_id):
    """Remove a throwaway tenant folder. Only names starting with t-smoke, so a test can never remove real data."""
    if not tenant_id.startswith("t-smoke"):
        raise ValueError(f"refusing to remove {tenant_id}: scratch tenants start with t-smoke")
    shutil.rmtree(MATTERS / tenant_id, ignore_errors=True)
