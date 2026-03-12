"""Skill: News — RSS feeds + HackerNews API (no API key required)."""

import xml.etree.ElementTree as ET

import httpx

RSS_FEEDS: dict[str, str] = {
    "general": "https://feeds.bbci.co.uk/news/rss.xml",
    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "tech": "https://feeds.feedburner.com/TechCrunch",
    "science": "https://www.sciencedaily.com/rss/top/science.xml",
    "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "hackernews": "https://news.ycombinator.com/rss",
}


def _parse_rss(url: str, count: int) -> list[dict]:
    resp = httpx.get(url, timeout=10, follow_redirects=True)
    root = ET.fromstring(resp.text)
    items = []
    for item in root.iter("item"):
        title = item.find("title")
        link = item.find("link")
        desc = item.find("description")
        pub_date = item.find("pubDate")
        items.append({
            "title": title.text.strip() if title is not None else "",
            "link": link.text.strip() if link is not None else "",
            "description": (desc.text or "")[:200].strip() if desc is not None else "",
            "published": pub_date.text.strip() if pub_date is not None else "",
        })
        if len(items) >= count:
            break
    return items


def _hackernews_top(count: int) -> list[dict]:
    ids = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).json()
    items = []
    for story_id in ids[:count]:
        story = httpx.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=10
        ).json()
        if story and story.get("type") == "story":
            items.append({
                "title": story.get("title", ""),
                "link": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                "score": story.get("score", 0),
                "comments": story.get("descendants", 0),
            })
    return items


def get_news(topic: str = "general", count: int = 5) -> list[dict]:
    """Fetch top news stories. topic: general | world | tech | science | business | hackernews"""
    topic = topic.lower().strip()
    try:
        if topic == "hackernews":
            return _hackernews_top(count)
        feed_url = RSS_FEEDS.get(topic, RSS_FEEDS["general"])
        return _parse_rss(feed_url, count)
    except Exception as e:
        return [{"error": str(e)}]
