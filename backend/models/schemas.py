from datetime import datetime

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    type: str = Field(pattern="^(account|subreddit)$")
    name: str = Field(min_length=1, max_length=100)


class SourceUpdate(BaseModel):
    type: str | None = Field(default=None, pattern="^(account|subreddit)$")
    name: str | None = Field(default=None, min_length=1, max_length=100)
    enabled: bool | None = None


class SourceOut(BaseModel):
    id: int
    type: str
    name: str
    enabled: bool

    class Config:
        from_attributes = True


class HashtagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class HashtagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    enabled: bool | None = None


class HashtagOut(BaseModel):
    id: int
    name: str
    enabled: bool

    class Config:
        from_attributes = True


class PostOut(BaseModel):
    id: int
    platform: str
    author: str
    content: str
    url: str
    timestamp: datetime
    engagement_score: float
    ai_category: str | None
    ai_confidence: float
    rank_score: float

    class Config:
        from_attributes = True
