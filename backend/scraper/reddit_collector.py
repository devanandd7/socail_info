from __future__ import annotations

from datetime import datetime, timezone

import requests

from services.config import settings


def _via_json(subreddit: str, limit: int = 20) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    headers = {"User-Agent": settings.REDDIT_USER_AGENT}
    res = requests.get(url, headers=headers, timeout=15)
    res.raise_for_status()
    items = res.json().get("data", {}).get("children", [])

    posts: list[dict] = []
    for child in items:
        data = child.get("data", {})
        created = datetime.fromtimestamp(data.get("created_utc", 0), tz=timezone.utc)
        posts.append(
            {
                "platform": "reddit",
                "author": data.get("author", "unknown"),
                "content": f"{data.get('title', '')}\n\n{data.get('selftext', '')}".strip(),
                "url": f"https://reddit.com{data.get('permalink', '')}",
                "timestamp": created,
                "engagement_score": float(data.get("score", 0)) + float(data.get("num_comments", 0) * 2),
            }
        )
    return posts


def fetch_subreddit_posts(subreddit: str, limit: int = 20) -> list[dict]:
    # Prefer PRAW when credentials are available; fallback to public JSON endpoint.
    if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
        try:
            import praw

            reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT,
            )
            items = reddit.subreddit(subreddit).new(limit=limit)
            posts: list[dict] = []
            for item in items:
                ts = datetime.fromtimestamp(item.created_utc, tz=timezone.utc)
                posts.append(
                    {
                        "platform": "reddit",
                        "author": item.author.name if item.author else "unknown",
                        "content": f"{item.title}\n\n{item.selftext}".strip(),
                        "url": f"https://reddit.com{item.permalink}",
                        "timestamp": ts,
                        "engagement_score": float(item.score + (item.num_comments * 2)),
                    }
                )
            return posts
        except Exception:
            return _via_json(subreddit, limit)

    return _via_json(subreddit, limit)
