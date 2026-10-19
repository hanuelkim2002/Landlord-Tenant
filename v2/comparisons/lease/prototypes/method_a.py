"""Method A: the whole lease in the prompt, page by page. No tools. Run: python method_a.py"""
import common


def setup(lease):
    """The lease's whole text, with a marker at the start of each page."""
    return "\n\n".join(f"=== Page {p['page']} ===\n{p['text']}" for p in common.lease_pages(lease))


def lease_part(text):
    """The system prompt's lease part: all of it."""
    return f"THE LEASE (the tenant's whole lease, page by page):\n\n{text}"


if __name__ == "__main__":
    common.run("A", setup, lease_part, lambda state: [], lambda state, name, arguments: "")
