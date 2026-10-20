"""The checks shown under each reply. Every quotation of 20 or more characters must be word for word in the section
it cites or in the lease, and the program prints the words each cite points to. The reply is never blocked.
"""
import re

import law

QUOTE = re.compile(r'["“]([^"“”]{20,}?)["”]')
STATUTE_CITE = re.compile(r"\b(83\.\d+)((?:\(\w+\))*)")
LEASE_CITE = re.compile(r"\blease,?\s*(?:§|section|clause|paragraph|article|item)\s*(\d+(?:\.\d+)*)"
                        r"|\b(?:section|clause|paragraph)\s+(\d+(?:\.\d+)*)\s+of\s+(?:the|your)\s+lease"
                        r"|\blease,?\s*page\s*(\d+)", re.I)
SHOWN = 1500                                                 # characters of cited words printed under a reply


def quote_parts(quote):
    """A quotation's words to look for. Bold marks and a closing comma or period are typography; an ellipsis or a
    bracketed change ("forfeit[s]") marks a cut, so each part between them is looked for on its own."""
    quote = quote.replace("**", "").strip().rstrip(",.;:")
    return [law.squash(p).lower() for p in re.split(r"\.\.\.|…|\[[^\]]*\]", quote) if len(p.strip()) > 3]


def found_in(parts, text):
    """Whether every part of a quotation is in the text."""
    text = law.squash(text).lower()
    return bool(parts) and all(p in text for p in parts)


def check_quote(reply, match, lease):
    """One quotation: where it is word for word (the section cited just after it, or the lease), or nowhere."""
    parts = quote_parts(match.group(1))
    cite = STATUTE_CITE.search(reply[match.end():match.end() + 150])
    if cite and found_in(parts, law.cited_text(cite.group(0)) or ""):
        return {"quote": match.group(1), "ok": True, "where": f"Fla. Stat. {cite.group(0)}"}
    if found_in(parts, lease):
        return {"quote": match.group(1), "ok": True, "where": "the lease"}
    return {"quote": match.group(1), "ok": False, "where": f"not word for word in {cite.group(0) if cite else 'the lease'}"}


def lease_passage(lease, number):
    """The lease's paragraph that starts with a section number, like "7." or "Section 7", or None."""
    start = re.search(rf"(?m)^\s*(?:Section\s+|ARTICLE\s+)?{re.escape(number)}\.?\s", lease)
    if not start:
        return None
    nxt = re.search(r"(?m)^\s*(?:Section\s+|ARTICLE\s+)?\d+(?:\.\d+)*\.\s", lease[start.end():])
    return lease[start.start():start.end() + (nxt.start() if nxt else len(lease))].strip()


def cited_words(reply, pages):
    """The words each cite in the reply points to, in order and once each: [{"cite", "words"}]."""
    lease, shown, seen = "\n".join(p["text"] for p in pages), [], set()
    for m in STATUTE_CITE.finditer(reply):
        if m.group(0) not in seen:
            seen.add(m.group(0))
            shown.append({"cite": f"Fla. Stat. {m.group(0)}", "words": law.cited_text(m.group(0)) or "Not in statutes/."})
    for m in LEASE_CITE.finditer(reply):
        number, page = m.group(1) or m.group(2), m.group(3)
        label = f"Lease, page {page}" if page else f"Lease, section {number}"
        if label not in seen:
            seen.add(label)
            words = next((p["text"] for p in pages if str(p["page"]) == page), None) if page else lease_passage(lease, number)
            shown.append({"cite": label, "words": words or "The lease has no such section or page."})
    for item in shown:
        if len(item["words"]) > SHOWN:
            item["words"] = item["words"][:SHOWN].rsplit(" ", 1)[0] + " ..."
    return shown


def check_reply(reply, pages):
    """Everything shown under a reply: each quotation and where it checks out, and the cited words."""
    lease = "\n".join(p["text"] for p in pages)
    return {"quotes": [check_quote(reply, m, lease) for m in QUOTE.finditer(reply)], "cited": cited_words(reply, pages)}
