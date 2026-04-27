from datetime import datetime, timezone
import math


def compute_rank(engagement_score: float, timestamp: datetime, ai_confidence: float) -> float:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    age_hours = max((now - timestamp).total_seconds() / 3600, 0.0)

    engagement_component = min(engagement_score / 1000.0, 1.0)
    recency_component = math.exp(-age_hours / 24.0)
    ai_component = max(min(ai_confidence, 1.0), 0.0)

    return (0.5 * engagement_component) + (0.3 * recency_component) + (0.2 * ai_component)
