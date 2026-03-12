"""
Subagent: Research Agent
A specialized Claude subagent that performs deep multi-step web research.
Uses extended thinking + iterative search to produce comprehensive reports.
"""

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from skills.web_search import web_search

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM = """You are a specialist research agent. Your ONLY job is to research topics deeply and produce comprehensive, well-structured reports.

Process:
1. Break the topic into 3-5 key questions that need answering.
2. Search for each question (use multiple queries per question if needed).
3. Cross-reference and synthesize findings.
4. Produce a clear, structured report with sources.

Always cite sources. Acknowledge uncertainty. Prefer recent information."""

_TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web. Call multiple times with different queries for thorough research.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    }
]


def run_research_agent(topic: str, max_searches: int = 10) -> str:
    """
    Spawn a research subagent that iteratively searches the web and returns a report.
    """
    messages = [
        {"role": "user", "content": f"Research this topic and produce a comprehensive report:\n\n{topic}"}
    ]

    searches_done = 0

    while searches_done < max_searches:
        response = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=6000,
            system=SYSTEM,
            tools=_TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            parts = [b.text for b in response.content if hasattr(b, "text")]
            return "\n".join(parts) or "Research complete but no report was generated."

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "web_search":
                        results = web_search(
                            block.input["query"],
                            block.input.get("max_results", 5),
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(results),
                        })
                        searches_done += 1
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    # Force a summary if we hit the search cap
    messages.append({
        "role": "user",
        "content": "You have reached the search limit. Synthesize everything gathered so far into your final report now.",
    })
    final = _client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=6000,
        system=SYSTEM,
        messages=messages,
    )
    parts = [b.text for b in final.content if hasattr(b, "text")]
    return "\n".join(parts) or "Research complete."
