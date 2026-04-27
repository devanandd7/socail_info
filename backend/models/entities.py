from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.db import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(20), index=True)  # account | subreddit
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="source")


class Hashtag(Base):
    __tablename__ = "hashtags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("url", name="uq_post_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform: Mapped[str] = mapped_column(String(20), index=True)  # twitter | reddit
    author: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(400), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    rank_score: Mapped[float] = mapped_column(Float, default=0.0)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True)

    source: Mapped[Source | None] = relationship(back_populates="posts")
