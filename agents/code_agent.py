"""
Subagent: Code Agent
A specialized Claude subagent that writes, tests, and iteratively debugs Python code.
"""

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from skills.code_executor import execute_python

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM = """You are a specialist coding agent. Your job is to write correct, clean Python code.

Process:
1. Understand the task fully.
2. Write the code.
3. Execute it to verify it works.
4. If there are errors, debug and fix them.
5. Repeat until the code works correctly.
6. Return the final code + brief explanation + sample output.

Write production-quality code: handle edge cases, add docstrings, use type hints."""

_TOOLS = [
    {
        "name": "execute_python",
        "description": "Execute Python code and see stdout/stderr. Use to test your code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"},
            },
            "required": ["code"],
        },
    }
]


def run_code_agent(task: str, max_iterations: int = 6) -> str:
    """
    Spawn a coding subagent that writes and iteratively tests Python code.
    """
    messages = [
        {"role": "user", "content": f"Complete this coding task:\n\n{task}"}
    ]

    for _ in range(max_iterations):
        response = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=6000,
            system=SYSTEM,
            tools=_TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            parts = [b.text for b in response.content if hasattr(b, "text")]
            return "\n".join(parts) or "Task complete."

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "execute_python":
                    result = execute_python(block.input["code"])
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result),
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Coding task completed (hit iteration limit — partial result returned)."
