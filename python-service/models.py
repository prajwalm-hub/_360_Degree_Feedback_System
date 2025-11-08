from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SentimentLabel(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class RSSSource:
    id: Optional[int]
    name: str
    url: str
    language: str
    region: Optional[str]
    category: Optional[str]
    is_active: bool = True
    last_fetched_at: Optional[datetime] = None
    fetch_frequency_minutes: int = 30
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class NewsArticle:
    id: Optional[int]
    title: str
    content: str
    source: str
    source_url: Optional[str]
    language: str
    translated_content: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    region: Optional[str] = None
    category: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[SentimentLabel] = None
    emotions: Optional[str] = None
    keywords: Optional[str] = None
    summary: Optional[str] = None
    entities: Optional[str] = None
    is_government_related: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class ProcessingJob:
    id: Optional[int]
    job_type: str
    status: JobStatus = JobStatus.PENDING
    article_id: Optional[int] = None
    source_id: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Alert:
    id: Optional[int]
    alert_type: str
    severity: str
    title: str
    content: str
    article_id: Optional[int] = None
    threshold_triggered: Optional[float] = None
    is_read: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class ProcessingResult:
    success: bool
    article: Optional[NewsArticle] = None
    error: Optional[str] = None
    alerts: List[Alert] = None
