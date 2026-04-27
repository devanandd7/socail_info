from models.entities import Post

KEYWORDS = ["launch", "announcing", "introducing", "funding", "release"]


def keyword_match(content: str, extra_keywords: list[str] | None = None) -> bool:
    terms = KEYWORDS + (extra_keywords or [])
    lowered = content.lower()
    return any(term.lower() in lowered for term in terms)


def is_high_signal(
    post: Post,
    min_engagement: float,
    use_ai: bool = True,
    extra_keywords: list[str] | None = None,
) -> bool:
    keyword_or_ai = keyword_match(post.content, extra_keywords)
    if use_ai and post.ai_category in {"Product Launch", "Funding News", "Important Update"}:
        keyword_or_ai = True
    return keyword_or_ai and post.engagement_score >= min_engagement
