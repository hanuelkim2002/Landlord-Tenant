"""The memory test's way to Claude: Anthropic's own SDK behind the one call the app makes,
chat.completions.create, so the app's code runs unchanged. Test-only; the app talks to its gateways through the
OpenAI client. The key comes from ANTHROPIC_API_KEY in the environment.
"""
import json
from types import SimpleNamespace

import anthropic

# Dollars per million tokens (the claude-api skill's model table, cached 2026-10-06; a cache write is about 1.25
# times the input price).
PRICES = {"claude-sonnet-5-5": {"input": 2.00, "output": 10.00, "cache_read": 0.20, "cache_write": 2.50}}
FINISH = {"tool_use": "tool_calls", "end_turn": "stop", "max_tokens": "length"}   # Claude's stop reasons, as the app's


class ClaudeClient:
    """Looks like the OpenAI client to the app: client.chat.completions.create(**request)."""

    def __init__(self):
        """The Anthropic client, and Claude's replies kept by their first tool call."""
        self.client = anthropic.Anthropic(timeout=300, max_retries=2)
        self.replies = {}     # why: a reply with tool calls must go back exactly as it came, thinking blocks included
        self.steps = []       # every step's text, tools, and stop reason, so the test can see where text goes
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, model, messages, tools=None, tool_choice=None, max_tokens=8000, **ignored):
        """One request in the app's shape, sent to Claude; the reply comes back in the app's shape."""
        request = {"model": model, "max_tokens": max_tokens, "system": messages[0]["content"],
                   "messages": self.claude_messages(messages[1:]),
                   "cache_control": {"type": "ephemeral"}}    # the long lease and rules are sent again every round
        if tools:
            request["tools"] = [claude_tool(t) for t in tools]
        if tool_choice == "none":
            request["tool_choice"] = {"type": "none"}
        return self.app_reply(self.client.messages.create(**request), model)

    def claude_messages(self, messages):
        """The app's chat after the system prompt, as Claude's messages: Claude's own replies go back as they came,
        and the tool results that follow one reply go back together in one message."""
        out = []
        for message in messages:
            if message["role"] == "tool":
                result = {"type": "tool_result", "tool_use_id": message["tool_call_id"], "content": message["content"]}
                if out and out[-1]["role"] == "user" and isinstance(out[-1]["content"], list):
                    out[-1]["content"].append(result)
                else:
                    out.append({"role": "user", "content": [result]})
            elif message["role"] == "assistant" and message.get("tool_calls"):
                out.append({"role": "assistant", "content": self.replies[message["tool_calls"][0]["id"]]})
            elif message.get("content"):
                out.append({"role": message["role"], "content": message["content"]})
        return out

    def app_reply(self, reply, model):
        """Claude's reply as the app reads it: the text, the tool calls, why it stopped, and the tokens used."""
        calls = [tool_call(block) for block in reply.content if block.type == "tool_use"]
        if calls:
            self.replies[calls[0].id] = reply.content
        text = "".join(block.text for block in reply.content if block.type == "text")
        self.steps.append({"text": text, "tools": [call.function.name for call in calls], "stop": reply.stop_reason,
                           "blocks": [block.type for block in reply.content],
                           "output_tokens": reply.usage.output_tokens})
        message = SimpleNamespace(content=text, tool_calls=calls or None)
        finish = FINISH.get(reply.stop_reason, reply.stop_reason)   # "refusal" stays as it is, for the record
        return SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason=finish)],
                               usage=usage(reply.usage, model))


def claude_tool(tool):
    """One of the app's tool descriptions in Claude's shape."""
    function = tool["function"]
    return {"name": function["name"], "description": function["description"], "input_schema": function["parameters"]}


def tool_call(block):
    """One of Claude's tool calls in the shape the app reads and records."""
    call = {"id": block.id, "type": "function", "function": {"name": block.name, "arguments": json.dumps(block.input)}}
    return SimpleNamespace(id=block.id, function=SimpleNamespace(**call["function"]), model_dump=lambda: call)


def usage(used, model):
    """The tokens and the cost of one request, in the shape the model test's log reads."""
    price = PRICES[model]
    read, written = used.cache_read_input_tokens or 0, used.cache_creation_input_tokens or 0
    cost = (used.input_tokens * price["input"] + read * price["cache_read"] + written * price["cache_write"]
            + used.output_tokens * price["output"]) / 1_000_000
    return SimpleNamespace(prompt_tokens=used.input_tokens + read + written, completion_tokens=used.output_tokens,
                           prompt_tokens_details=SimpleNamespace(cached_tokens=read, cache_write_tokens=written),
                           cost=cost)
