---
name: news
description: Fetch latest news headlines from RSS feeds or HackerNews. No API key required.
user-invocable: true
---

# News Skill

Fetches top headlines from RSS feeds or HackerNews API. No API key needed.

## Topics

| Topic | Source |
|---|---|
| `general` | BBC News |
| `world` | BBC World |
| `tech` | TechCrunch |
| `science` | ScienceDaily |
| `business` | BBC Business |
| `hackernews` | Hacker News top stories |

## Usage

```python
from skills.news import get_news
stories = get_news(topic="tech", count=5)
```

## Arguments

`$ARGUMENTS` — topic name (e.g. `tech`, `science`, `hackernews`)

## Example invocation

`/news hackernews`
