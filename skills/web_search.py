"""Skill: Web Search — DuckDuckGo (no API key required)."""

import time

from ddgs import DDGS


def web_search(query: str, max_results: int = 5, retries: int = 3) -> list[dict]:
    """Search the web and return title, url, and snippet for each result."""
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            if results:
                return results
        except Exception as e:
            last_error = e
        if attempt < retries - 1:
            time.sleep(2 ** attempt)  # 0s, 2s, 4s back-off
    if last_error:
        return [{"error": str(last_error)}]
    return []
