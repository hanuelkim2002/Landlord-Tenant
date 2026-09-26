"""Schemas: print what the model sees for each tool. Run this whenever a signature or docstring changes."""
import json

from tools import tools

for t in tools:
    print(t.name)
    print("  ", t.description.split("\n")[0])
    print("  ", json.dumps(t.args))
