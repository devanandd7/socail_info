from __future__ import annotations

import json

import requests

from services.config import settings


def _heuristic_classify(text: str) -> tuple[str, float]:
    t = text.lower()
    if any(k in t for k in ["raise", "raised", "funding", "series a", "series b", "seed round"]):
        return "Funding News", 0.75
    if any(k in t for k in ["launch", "released", "announcing", "introducing", "now live"]):
        return "Product Launch", 0.75
    if any(k in t for k in ["update", "roadmap", "partnership", "milestone"]):
        return "Important Update", 0.65
    return "Noise", 0.55


def classify_text(text: str) -> tuple[str | None, float]:
    if not settings.ENABLE_AI_FILTER:
        return None, 0.0

    if not settings.LLM_API_KEY or not settings.LLM_API_URL:
        return _heuristic_classify(text)

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Classify post into one of: Product Launch, Funding News, Important Update, Noise. "
                    "Return strict JSON with keys category and confidence (0..1)."
                ),
            },
            {"role": "user", "content": text[:2000]},
        ],
        "temperature": 0,
    }

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        res = requests.post(settings.LLM_API_URL, headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        data = res.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        category = parsed.get("category", "Noise")
        confidence = float(parsed.get("confidence", 0.5))
        return category, max(0.0, min(confidence, 1.0))
    except Exception:
        return _heuristic_classify(text)
