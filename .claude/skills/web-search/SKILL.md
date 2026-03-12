---
name: web-search
description: Search the web using DuckDuckGo and return results. No API key required.
user-invocable: true
---

# Web Search Skill

Searches the web via DuckDuckGo. No API key needed.

## Usage

```python
from skills.web_search import web_search

results = web_search("latest Claude AI news", max_results=5)
for r in results:
    print(r["title"], r["href"], r["body"])
```

## Arguments

`$ARGUMENTS` — search query string

## Example invocation

`/web-search latest developments in quantum computing`

## Script

Run directly:

```bash
python -c "from skills.web_search import web_search; import json; print(json.dumps(web_search('$ARGUMENTS', 5), indent=2))"
```
