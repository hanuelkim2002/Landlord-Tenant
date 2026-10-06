# Standing in for the chatbot's model

The tool under test is a Florida landlord-tenant chatbot (the repository at /home/user/Landlord-Tenant). In normal use
its model is nemotron-3-super-120b on the University of Florida AI gateway, which cannot be reached here. You stand in
for that model: the real program runs, and every time it calls its model, you write the answer. A student is using the
tool on the other side; you never talk to them except through your answers.

## The loop (RUN is your run folder, H is the harness command)

    H="/home/user/Landlord-Tenant/venv/bin/python <this eval>/method/harness.py RUN"
    $H status

1. If the status line says `NEED_MODEL`, read `RUN/model/pending.txt`. Its head says what kind of request it is:
   - a one-shot prompt (the program classifying the tenant's story or pulling facts out of it): answer with "content"
     only, exactly the JSON the prompt asks for.
   - a chat call: it names the system prompt file (read it whenever the head says NEW; it is rebuilt from the record,
     so it changes when facts change), and the tool list `RUN/model/tools.txt` (read it once). Below the head are the
     conversation's messages so far. Answer as the model: either call tools (you then get a new request holding their
     results) or write your reply to the tenant as "content" with no tool calls.
2. Write your answer as JSON to a file, using Python so the escaping is right, e.g.

       /home/user/Landlord-Tenant/venv/bin/python - <<'PY'
       import json
       json.dump({"content": "...", "tool_calls": [{"name": "get_deadlines", "args": {}}]},
                 open("RUN/model/answer_7.json", "w"))
       PY

   then `$H respond RUN/model/answer_7.json`. "tool_calls" may be left out or empty. "content" is a string.
3. Repeat until the status says `NEED_INPUT` (the student's turn) or `DONE`. Then end your turn with one short line:
   which requests you answered and which tools you called. Do not summarize your replies.

## How to answer

- Be the model the program expects: follow the system prompt's rules exactly and do what the request asks, no more.
  Use only what is in the requests and in the results of the tools you call.
- Do not open the lease PDF, `RUN/program/`, `my_lease.txt`, `persona.md`, `notes.md`, the screen files, or the
  repository's code, playbooks, statutes, or wiki. Your knowledge of the tenant and the law comes only through the
  requests and the tools (search_lease, get_statute_section, search_statute, get_cases, get_deadlines, ...).
- Do not try to pass the program's checks by studying them; just answer well under the rules.
- You will be messaged again each time the student has typed something new; then run `$H status` and continue.
