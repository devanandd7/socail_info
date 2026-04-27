from __future__ import annotations

from datetime import datetime, timezone

import requests

from services.config import settings


API_BASE = "https://api.twitter.com/2"


def _headers() -> dict[str, str]:
    if not settings.TWITTER_BEARER_TOKEN:
        raise ValueError("TWITTER_BEARER_TOKEN is not configured")
    return {"Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"}


def _resolve_user_id(handle: str) -> str:
    clean = handle.lstrip("@")
    res = requests.get(f"{API_BASE}/users/by/username/{clean}", headers=_headers(), timeout=15)
    res.raise_for_status()
    return res.json()["data"]["id"]


def fetch_profile_posts(handle: str, limit: int = 10) -> list[dict]:
    user_id = _resolve_user_id(handle)
    params = {
        "max_results": min(max(limit, 5), 100),
        "tweet.fields": "created_at,public_metrics",
        "exclude": "retweets,replies",
    }
    res = requests.get(f"{API_BASE}/users/{user_id}/tweets", headers=_headers(), params=params, timeout=15)
    res.raise_for_status()

    posts: list[dict] = []
    for t in res.json().get("data", []):
        metrics = t.get("public_metrics", {})
        engagement = float(metrics.get("like_count", 0) + metrics.get("retweet_count", 0) * 2 + metrics.get("reply_count", 0) * 2)
        created = datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")).astimezone(timezone.utc)
        posts.append(
            {
                "platform": "twitter",
                "author": handle.lstrip("@"),
                "content": t.get("text", ""),
                "url": f"https://x.com/{handle.lstrip('@')}/status/{t['id']}",
                "timestamp": created,
                "engagement_score": engagement,
            }
        )
    return posts
