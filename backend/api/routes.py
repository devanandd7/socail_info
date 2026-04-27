from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
import re

from models.db import get_db
from models.entities import Hashtag, Post, Source
from models.schemas import HashtagCreate, HashtagOut, HashtagUpdate, PostOut, SourceCreate, SourceOut, SourceUpdate
from services.collector import collect_once
from services.config import settings
from services.filtering import is_high_signal, keyword_match

router = APIRouter()


@router.get("/posts", response_model=list[PostOut])
def get_posts(limit: int = Query(default=100, le=500), db: Session = Depends(get_db)):
    stmt = select(Post).order_by(Post.rank_score.desc(), Post.timestamp.desc()).limit(limit)
    return db.scalars(stmt).all()


@router.get("/filtered", response_model=list[PostOut])
def get_filtered_posts(
    platform: str | None = None,
    keyword: str | None = None,
    ai_category: str | None = None,
    min_engagement: float = Query(default=settings.DEFAULT_MIN_ENGAGEMENT),
    use_ai: bool = True,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    tracked_terms = [f"#{tag.name}" for tag in db.scalars(select(Hashtag).where(Hashtag.enabled.is_(True))).all()]
    stmt = select(Post).order_by(Post.rank_score.desc(), Post.timestamp.desc())
    posts = db.scalars(stmt).all()

    filtered: list[Post] = []
    for post in posts:
        if platform and post.platform != platform:
            continue
        if ai_category and (post.ai_category or "") != ai_category:
            continue
        if keyword and not keyword_match(post.content, [keyword] + tracked_terms):
            continue
        if not is_high_signal(
            post,
            min_engagement=min_engagement,
            use_ai=use_ai,
            extra_keywords=([keyword] if keyword else []) + tracked_terms,
        ):
            continue
        filtered.append(post)
    return filtered[:limit]


@router.post("/sources", response_model=SourceOut)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Source).where(Source.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="Source already exists")

    source = Source(type=payload.type, name=payload.name)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.put("/sources/{source_id}", response_model=SourceOut)
def update_source(source_id: int, payload: SourceUpdate, db: Session = Depends(get_db)):
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    if payload.name and payload.name != source.name:
        existing = db.scalar(select(Source).where(Source.name == payload.name))
        if existing:
            raise HTTPException(status_code=409, detail="Source already exists")
        source.name = payload.name

    if payload.type:
        source.type = payload.type
    if payload.enabled is not None:
        source.enabled = payload.enabled

    db.commit()
    db.refresh(source)
    return source


@router.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    source = db.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(source)
    db.commit()
    return {"deleted": True, "id": source_id}


@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.scalars(select(Source).order_by(Source.type, Source.name)).all()


@router.get("/hashtags", response_model=list[HashtagOut])
def list_hashtags(db: Session = Depends(get_db)):
    return db.scalars(select(Hashtag).order_by(Hashtag.name)).all()


@router.post("/hashtags", response_model=HashtagOut)
def create_hashtag(payload: HashtagCreate, db: Session = Depends(get_db)):
    name = payload.name.strip().lstrip("#")
    existing = db.scalar(select(Hashtag).where(Hashtag.name == name))
    if existing:
        raise HTTPException(status_code=409, detail="Hashtag already exists")

    hashtag = Hashtag(name=name)
    db.add(hashtag)
    db.commit()
    db.refresh(hashtag)
    return hashtag


@router.put("/hashtags/{hashtag_id}", response_model=HashtagOut)
def update_hashtag(hashtag_id: int, payload: HashtagUpdate, db: Session = Depends(get_db)):
    hashtag = db.get(Hashtag, hashtag_id)
    if hashtag is None:
        raise HTTPException(status_code=404, detail="Hashtag not found")

    if payload.name and payload.name != hashtag.name:
        clean = payload.name.strip().lstrip("#")
        existing = db.scalar(select(Hashtag).where(Hashtag.name == clean))
        if existing:
            raise HTTPException(status_code=409, detail="Hashtag already exists")
        hashtag.name = clean
    if payload.enabled is not None:
        hashtag.enabled = payload.enabled

    db.commit()
    db.refresh(hashtag)
    return hashtag


@router.delete("/hashtags/{hashtag_id}")
def delete_hashtag(hashtag_id: int, db: Session = Depends(get_db)):
    hashtag = db.get(Hashtag, hashtag_id)
    if hashtag is None:
        raise HTTPException(status_code=404, detail="Hashtag not found")

    db.delete(hashtag)
    db.commit()
    return {"deleted": True, "id": hashtag_id}


@router.get("/trending")
def trending(limit: int = Query(default=10, le=50), db: Session = Depends(get_db)):
    posts = db.scalars(select(Post).order_by(Post.timestamp.desc()).limit(200)).all()
    tracked_hashtags = db.scalars(select(Hashtag).where(Hashtag.enabled.is_(True)).order_by(Hashtag.name)).all()
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "your", "have", "are", "was", "were",
        "you", "not", "but", "our", "will", "can", "has", "had", "its", "all", "any", "more",
        "about", "into", "out", "use", "using", "when", "what", "who", "why", "how", "been",
        "their", "there", "they", "them", "then", "than", "after", "before", "over", "under",
    }

    counts: dict[str, int] = {}
    for tag in tracked_hashtags:
        counts[f"#{tag.name}"] = counts.get(f"#{tag.name}", 0) + 3

    for post in posts:
        text = post.content.lower()
        for raw in re.findall(r"#[a-z0-9_]+|[a-z][a-z0-9_']+", text):
            token = raw.strip(".,:;!?()[]{}\"'<>|/")
            if not token:
                continue
            if token.startswith("#") and len(token) > 1:
                key = token
            else:
                if len(token) < 4 or token in stopwords:
                    continue
                key = token
            counts[key] = counts.get(key, 0) + 1 + int(post.engagement_score // 100)

    trending_terms = [
        {"name": name, "score": score}
        for name, score in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]
    return {"items": trending_terms}


@router.post("/collect")
def collect_now(db: Session = Depends(get_db)):
    return collect_once(db)
