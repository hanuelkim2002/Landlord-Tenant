"""Method C: a ranked word search over the lease's clauses (BM25). Run: python method_c.py"""
import math
import re

import common

TOOLS = [{"type": "function", "function": {
    "name": "search_lease",
    "description": "Search the tenant's lease. Returns the clauses that best match your words, best first, each "
                   "with its title, page, and full words.",
    "parameters": {"type": "object", "properties": {"words": {"type": "string",
                                                              "description": "Words to look for, like \"late fee\""}},
                   "required": ["words"]}}}]
SHOWN = 5                    # clauses returned per search
STOP = {"the", "a", "an", "of", "to", "and", "or", "in", "on", "for", "is", "be", "by", "my", "i", "can", "do", "does"}


def words(text):
    """The text's words, lowercase, without the most common small words."""
    return [w for w in re.findall(r"[a-z0-9$]+", text.lower()) if w not in STOP]


def setup(lease):
    """The clauses, and the counts BM25 needs: each clause's words and how many clauses hold each word."""
    clauses = common.split_clauses(common.lease_pages(lease))
    bags = [words(c["title"] + " " + c["text"]) for c in clauses]
    holding = {}
    for bag in bags:
        for w in set(bag):
            holding[w] = holding.get(w, 0) + 1
    return {"clauses": clauses, "bags": bags, "holding": holding,
            "average": sum(map(len, bags)) / max(len(bags), 1)}


def score(index, bag, query):
    """BM25: a word counts more if it is rare in the lease and common in this clause; long clauses count less."""
    n, total = len(index["bags"]), 0.0
    for w in query:
        f = bag.count(w)
        if f:
            idf = math.log(1 + (n - index["holding"][w] + 0.5) / (index["holding"][w] + 0.5))
            total += idf * f * 2.5 / (f + 1.5 * (0.25 + 0.75 * len(bag) / index["average"]))
    return total


def search_lease(index, name, arguments):
    """The best-matching clauses for the words, best first."""
    query = words(str(arguments.get("words", "")))
    ranked = sorted(range(len(index["bags"])), key=lambda i: -score(index, index["bags"][i], query))
    best = [index["clauses"][i] for i in ranked[:SHOWN] if score(index, index["bags"][i], query) > 0]
    if not best:
        return "No clause of the lease uses any of those words. Try other words."
    return "\n\n".join(f"{c['title']} (page {c['page']}):\n{c['text']}" for c in best)


def lease_part(index):
    """The system prompt's lease part: how to search, with no lease text."""
    return ("THE LEASE: you cannot see the tenant's lease directly. Call search_lease with words to find the clauses "
            "that bear on the question; it returns the best-matching clauses, best first. Search before you answer, "
            "and try other words before you say the lease does not address it.")


if __name__ == "__main__":
    common.run("C", setup, lease_part, lambda state: TOOLS, search_lease)
