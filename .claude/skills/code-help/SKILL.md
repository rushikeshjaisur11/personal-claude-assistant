---
name: code-help
description: Spawn a coding subagent that writes, executes, and iteratively debugs Python code until it works.
user-invocable: true
context: fork
---

# Code Help Skill

Spawns a specialized Claude subagent (`agents/code_agent.py`) that:
1. Understands the coding task
2. Writes clean Python code with type hints and docstrings
3. Executes it to verify correctness
4. Debugs and fixes errors iteratively (up to 6 iterations)
5. Returns the final working code with explanation

## Arguments

`$ARGUMENTS` — coding task description

## Example invocations

`/code-help write a function that parses CSV and returns a list of dicts`
`/code-help scrape the top 10 HackerNews titles and save to a file`

## Usage from code

```python
from agents.code_agent import run_code_agent
result = run_code_agent("write a binary search implementation with unit tests")
print(result)
```

## Notes

- Code runs in a sandboxed subprocess (15s timeout).
- Only Python is supported currently.
- For quick calculations, prefer `execute_python` tool directly.
