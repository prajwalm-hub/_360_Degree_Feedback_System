from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))
from models.database_models import *
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
import settings
get_settings = settings.get_settings

router = APIRouter()

# Dependency to get DB session
def get_db():
    settings = get_settings()
    db_manager = DatabaseManager(settings.database_url)
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response (simplified for brevity)
class ArticleResponse(BaseModel):
    id: str
    title: str
    source: str
    language: str
    category: Optional[str] = None
    region: Optional[str] = None
    publish_date: Optional[datetime] = None
    collected_date: datetime
    url: str
    author: Optional[str] = None
    sentiment: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    is_government_related: bool = False
    departments: Optional[List[Dict[str, Any]]] = None
    government_scheme: Optional[str] = None
    government_entity: Optional[str] = None
    policy_type: Optional[str] = None
    confidence_score: float = 0.0

    class Config:
        from_attributes = True

class VideoResponse(BaseModel):
    id: str
    title: str
    channel: str
    upload_date: datetime = None
    views: int = None
    likes: int = None
    comments: int = None
    url: str
    sentiment: Dict[str, Any] = None
    summary: str = None

    class Config:
        from_attributes = True

class SocialMediaPostResponse(BaseModel):
    id: str
    platform: str
    content: str
    account: str = None
    post_date: datetime = None
    likes: int = None
    shares: int = None
    comments: int = None
    sentiment: Dict[str, Any] = None
    language: str = None

    class Config:
        from_attributes = True

class EntityResponse(BaseModel):
    id: int
    name: str
    type: str = None
    mentions_count: int
    positive_sentiment_count: int
    negative_sentiment_count: int
    neutral_sentiment_count: int
    last_updated: datetime

    class Config:
        from_attributes = True

class TopicResponse(BaseModel):
    id: int
    topic_name: str
    article_count: int
    sentiment_distribution: Dict[str, Any] = None
    trending_score: float
    last_updated: datetime

    class Config:
        from_attributes = True

class SentimentAnalyticResponse(BaseModel):
    id: int
    date: datetime
    source_type: str
    category: str = None
    region: str = None
    language: str = None
    positive_count: int
    negative_count: int
    neutral_count: int
    avg_sentiment_score: float
    total_count: int

    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    content: str
    threshold_triggered: str = None
    created_date: datetime
    status: str
    original_data_id: str = None
    original_data_type: str = None

    class Config:
        from_attributes = True

class GovernmentFeedbackResponse(BaseModel):
    id: int
    topic: str = None
    sentiment_summary: Dict[str, Any] = None
    key_issues: List[str] = None
    public_perception: str = None
    recommendations: str = None
    generated_date: datetime

    class Config:
        from_attributes = True

class DashboardStatsResponse(BaseModel):
    total_articles: int
    total_sources: int
    total_languages: int
    sentiment_distribution: Dict[str, int]
    regional_coverage: List[Dict[str, Any]]
    trending_topics: List[str]
    recent_alerts: List[Dict[str, Any]]

    class Config:
        from_attributes = True


# --- API Endpoints ---

@router.get("/articles/", response_model=List[ArticleResponse])
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = db.query(Article).offset(skip).limit(limit).all()
    return articles

@router.get("/articles/{article_id}", response_model=ArticleResponse)
def read_article(article_id: str, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.get("/videos/", response_model=List[VideoResponse])
def read_videos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    videos = db.query(Video).offset(skip).limit(limit).all()
    return videos

@router.get("/social_media_posts/", response_model=List[SocialMediaPostResponse])
def read_social_media_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = db.query(SocialMediaPost).offset(skip).limit(limit).all()
    return posts

@router.get("/entities/", response_model=List[EntityResponse])
def read_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entities = db.query(Entity).offset(skip).limit(limit).all()
    return entities

@router.get("/topics/", response_model=List[TopicResponse])
def read_topics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    topics = db.query(Topic).offset(skip).limit(limit).all()
    return topics

@router.get("/sentiment_analytics/", response_model=List[SentimentAnalyticResponse])
def read_sentiment_analytics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    analytics = db.query(SentimentAnalytic).offset(skip).limit(limit).all()
    return analytics

@router.get("/alerts/", response_model=List[AlertResponse])
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alerts = db.query(Alert).offset(skip).limit(limit).all()
    return alerts

@router.get("/government_feedback/", response_model=List[GovernmentFeedbackResponse])
def read_government_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feedback = db.query(GovernmentFeedback).offset(skip).limit(limit).all()
    return feedback

# Example of a POST endpoint for data ingestion (simplified)
# In a real system, this would be handled by internal services, not direct API calls
# from the frontend for raw data.
class ArticleCreate(BaseModel):
    id: str
    title: str
    content: str
    source: str
    language: str
    url: str
    category: str = None
    region: str = None
    publish_date: datetime = None
    author: str = None

@router.post("/articles/", response_model=ArticleResponse)
def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    db_article = Article(**article.dict(), collected_date=datetime.now())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

# Government-specific endpoints
@router.get("/articles/government/", response_model=List[ArticleResponse])
def read_government_articles(skip: int = 0, limit: int = 100, department: str = None, db: Session = Depends(get_db)):
    """
    Get government-related articles, optionally filtered by department.
    """
    query = db.query(Article).filter(Article.is_government_related == True)

    if department:
        # Filter by department in the departments JSON field
        from sqlalchemy import text
        query = query.filter(text(f"JSON_EXTRACT(departments, '$[*].department') LIKE '%{department}%'"))

    articles = query.offset(skip).limit(limit).all()
    return articles

@router.get("/government/departments/")
def get_department_analytics(db: Session = Depends(get_db)):
    """
    Get analytics for government departments.
    """
    # This is a simplified implementation - in production you'd want more sophisticated aggregation
    from sqlalchemy import func, text

    # Get department counts
    department_counts = {}
    articles = db.query(Article).filter(Article.is_government_related == True).all()

    for article in articles:
        if article.departments:
            for dept_info in article.departments:
                dept = dept_info.get('department', 'unknown')
                if dept not in department_counts:
                    department_counts[dept] = {'count': 0, 'sentiment': {'positive': 0, 'negative': 0, 'neutral': 0}}
                department_counts[dept]['count'] += 1

                # Add sentiment info
                if article.sentiment:
                    sentiment = article.sentiment.get('sentiment', 'neutral')
                    department_counts[dept]['sentiment'][sentiment] += 1

    return {
        'departments': department_counts,
        'total_government_articles': len(articles)
    }

@router.get("/government/dashboard/stats/")
def get_government_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics for government news.
    """
    government_articles = db.query(Article).filter(Article.is_government_related == True).all()

    total_government = len(government_articles)
    sentiment_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}

    for article in government_articles:
        if article.sentiment:
            sentiment = article.sentiment.get('sentiment', 'neutral')
            sentiment_distribution[sentiment] += 1

    return {
        'total_articles': total_government,
        'total_sources': len(set(a.source for a in government_articles)),
        'total_languages': len(set(a.language for a in government_articles)),
        'sentiment_distribution': sentiment_distribution,
        'regional_coverage': [],  # Placeholder for regional data
        'trending_topics': [],  # Placeholder for trending topics
        'recent_alerts': []  # Placeholder for alerts
    }

@router.get("/dashboard/stats/", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get general dashboard statistics for all news.
    """
    all_articles = db.query(Article).all()

    total_articles = len(all_articles)
    total_sources = len(set(a.source for a in all_articles))
    total_languages = len(set(a.language for a in all_articles))

    sentiment_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
    regional_coverage = {}
    trending_topics = []
    recent_alerts = []

    for article in all_articles:
        # Sentiment distribution
        if article.sentiment:
            sentiment = article.sentiment.get('sentiment', 'neutral')
            sentiment_distribution[sentiment] += 1

        # Regional coverage
        region = article.region or 'Unknown'
        if region not in regional_coverage:
            regional_coverage[region] = 0
        regional_coverage[region] += 1

        # Trending topics (simplified - just collect keywords)
        if article.keywords:
            trending_topics.extend(article.keywords)

    # Convert regional_coverage to list format
    regional_coverage_list = [{'region': region, 'count': count} for region, count in regional_coverage.items()]

    # Get recent alerts
    alerts = db.query(Alert).order_by(Alert.created_date.desc()).limit(5).all()
    for alert in alerts:
        recent_alerts.append({
            'id': alert.id,
            'title': alert.alert_type,
            'content': alert.content,
            'severity': alert.severity
        })

    # Limit trending topics to top 10 most common
    from collections import Counter
    trending_topics = [topic for topic, _ in Counter(trending_topics).most_common(10)]

    return {
        'total_articles': total_articles,
        'total_sources': total_sources,
        'total_languages': total_languages,
        'sentiment_distribution': sentiment_distribution,
        'regional_coverage': regional_coverage_list,
        'trending_topics': trending_topics,
        'recent_alerts': recent_alerts
    }
