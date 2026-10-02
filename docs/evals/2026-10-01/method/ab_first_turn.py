"""Ask one first-turn question on a copy of a saved eval matter with this copy of the code (run with cwd = the
project copy). Prints, per try: finish_reason, content length, reasoning length, and the tools called."""
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import record                                                  # noqa: E402
from agent import build_agent                                 # noqa: E402
from langchain.messages import HumanMessage                   # noqa: E402

src, question, tries = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
tenant = "t-smoke-ab"
dest = Path.cwd() / "matters" / tenant / "m-001"
shutil.rmtree(dest.parent, ignore_errors=True)
shutil.copytree(src, dest, ignore=shutil.ignore_patterns("sessions"))
saved = json.loads((dest / "matter.json").read_text()); saved.update({"tenant": tenant, "id": "m-001"})
(dest / "matter.json").write_text(json.dumps(saved))
record.load_matter(tenant, "m-001")
for i in range(tries):
    agent = build_agent()
    t = time.time()
    out = agent.invoke({"messages": [HumanMessage(content=question)]}, config={"configurable": {"thread_id": f"ab{i}"}})
    ai = [m for m in out["messages"] if m.type == "ai"]
    last = ai[-1]
    meta = last.response_metadata or {}
    reasoning = (last.additional_kwargs or {}).get("reasoning_content") or ""
    print(f"try {i}: {round(time.time()-t)}s finish={meta.get('finish_reason')} content={len(last.content)} "
          f"reasoning={len(reasoning)} usage={meta.get('token_usage', {}).get('completion_tokens')} "
          f"tools={[c['name'] for m in ai for c in m.tool_calls]}", flush=True)
shutil.rmtree(dest.parent, ignore_errors=True)
