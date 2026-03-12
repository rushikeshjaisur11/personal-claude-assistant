---
name: summarize
description: Fetch and extract readable text from a URL, then summarize it using Claude.
user-invocable: true
---

# Summarize Skill

Fetches a URL, strips noise (nav, scripts, ads), extracts main text, then Claude summarizes it.

## Usage

```python
from skills.summarizer import fetch_url_content
content = fetch_url_content("https://example.com/article")
# Claude then summarizes content["content"]
```

## Arguments

`$ARGUMENTS` — URL to summarize

## Example invocation

`/summarize https://en.wikipedia.org/wiki/Claude_(language_model)`
