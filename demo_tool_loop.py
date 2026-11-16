"""
Try the tools with a local model running in llama-server.

1. Start a model (in another terminal), with tool support turned on:
     llama-server.exe -m models\\qwen3.5-4b\\Qwen3.5-4B-Q4_K_M.gguf --jinja -c 8192 --port 8080
2. Run:
     python demo_tool_loop.py "I want a formal steel watch for my dad under 15000"

Needs: pip install openai
"""

import json
import sys

from openai import OpenAI

from tools.mock_tools import call_tool, load_schemas

SYSTEM = (
    "You are the shopping assistant on an in-store kiosk for Veyra watches. "
    "Use the tools to look up products, stock and alternatives; never invent product IDs, prices or stock. "
    "Ask one short follow-up question when the request is too vague to search. "
    "If you cannot answer from the tools, call staff. Keep replies under 80 words."
)


def run(user_text, base_url="http://127.0.0.1:8080/v1", max_rounds=4):
    client = OpenAI(base_url=base_url, api_key="none")
    tools = load_schemas()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user_text}]
    for _ in range(max_rounds):
        resp = client.chat.completions.create(model="local", messages=messages, tools=tools, temperature=0.2)
        msg = resp.choices[0].message
        if not msg.tool_calls:
            print("\nASSISTANT:", msg.content)
            return
        messages.append(msg.model_dump(exclude_none=True))
        for tc in msg.tool_calls:
            result = call_tool(tc.function.name, tc.function.arguments)
            print(f"TOOL {tc.function.name}({tc.function.arguments}) -> {json.dumps(result, ensure_ascii=False)[:300]}...")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result, ensure_ascii=False)})
    print("\n(stopped after", max_rounds, "tool rounds)")


if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or "Do you have a blue diver's watch for swimming?")
