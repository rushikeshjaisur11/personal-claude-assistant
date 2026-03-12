---
name: research
description: Spawn a deep research subagent that performs multi-step web searches and returns a comprehensive sourced report.
user-invocable: true
context: fork
---

# Research Skill

Spawns a specialized Claude subagent (`agents/research_agent.py`) that:
1. Breaks the topic into key questions
2. Performs multiple targeted web searches
3. Cross-references and synthesizes findings
4. Returns a structured report with sources

## Arguments

`$ARGUMENTS` — topic or research question

## Example invocations

`/research impact of LLMs on software engineering jobs 2024`
`/research compare Rust vs Go for systems programming`

## Usage from code

```python
from agents.research_agent import run_research_agent
report = run_research_agent("quantum computing breakthroughs 2025")
print(report)
```

## Notes

- Uses up to 10 web searches per invocation.
- Model: `claude-sonnet-4-6` (configurable via `CLAUDE_MODEL` env var).
- For quick single-search lookups, prefer the `web-search` skill instead.
