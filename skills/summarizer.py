"""Skill: URL Summarizer — fetches and extracts readable text from a URL."""

import httpx
from bs4 import BeautifulSoup


def fetch_url_content(url: str, max_chars: int = 8000) -> dict:
    """
    Fetch a URL and return its readable text content.
    The actual summarization is done by the Claude orchestrator using this content.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = httpx.get(url, follow_redirects=True, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            tag.decompose()

        # Try to find main article content
        main = (
            soup.find("article")
            or soup.find("main")
            or soup.find(id="content")
            or soup.find(class_="content")
            or soup.body
        )

        text = (main or soup).get_text(separator="\n", strip=True)

        # Collapse blank lines
        lines = [line for line in text.splitlines() if line.strip()]
        clean = "\n".join(lines)[:max_chars]

        return {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "",
            "content": clean,
            "truncated": len(clean) >= max_chars,
        }

    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code} fetching {url}"}
    except Exception as e:
        return {"error": str(e)}
