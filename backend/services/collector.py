from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.entities import Hashtag, Post, Source
from scraper.reddit_collector import fetch_subreddit_posts
from scraper.twitter_api import fetch_profile_posts
from scraper.twitter_selenium import scrape_profile
from services.classifier import classify_text
from services.config import settings
from services.filtering import is_high_signal
from services.notifier import send_telegram_alert
from services.ranking import compute_rank


def _collect_for_source(source: Source) -> list[dict]:
    if source.type == "subreddit":
        return fetch_subreddit_posts(source.name, limit=20)

    if source.type == "account":
        if settings.USE_TWITTER_API:
            if not settings.TWITTER_BEARER_TOKEN:
                return []
            return fetch_profile_posts(source.name, limit=20)
        if not settings.ENABLE_SELENIUM_X:
            return []
        return scrape_profile(source.name, max_scrolls=3)

    return []


def collect_once(db: Session) -> dict[str, int]:
    sources = db.scalars(select(Source).where(Source.enabled.is_(True))).all()
    tracked_terms = [f"#{tag.name}" for tag in db.scalars(select(Hashtag).where(Hashtag.enabled.is_(True))).all()]
    inserted = 0
    skipped = 0
    failed = 0

    for source in sources:
        try:
            items = _collect_for_source(source)
        except Exception:
            failed += 1
            continue

        if not items:
            skipped += 1
            continue

        for item in items:
            category, confidence = classify_text(item["content"])
            rank = compute_rank(item["engagement_score"], item["timestamp"], confidence)

            post = Post(
                platform=item["platform"],
                author=item["author"],
                content=item["content"],
                url=item["url"],
                timestamp=item["timestamp"],
                engagement_score=item["engagement_score"],
                ai_category=category,
                ai_confidence=confidence,
                rank_score=rank,
                source_id=source.id,
            )

            db.add(post)
            try:
                db.commit()
                inserted += 1

                if is_high_signal(post, settings.DEFAULT_MIN_ENGAGEMENT, use_ai=True, extra_keywords=tracked_terms):
                    msg = (
                        f"SignalFeed alert ({post.platform})\n"
                        f"{post.author}: {post.content[:240]}\n"
                        f"{post.url}"
                    )
                    send_telegram_alert(msg)
            except IntegrityError:
                db.rollback()

    return {"sources": len(sources), "inserted": inserted, "skipped": skipped, "failed": failed}
