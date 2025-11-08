"""
Real-time configuration for the NewsScope India system.
This file contains settings for the upgraded real-time AI-powered news monitoring.
"""

import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# Real-time processing configuration
class RealTimeConfig(BaseModel):
    # Change detection settings
    change_detection_interval: int = Field(30, description="Seconds between change detection checks")
    max_concurrent_scrapers: int = Field(5, description="Maximum concurrent web scrapers")
    request_timeout: int = Field(10, description="Request timeout in seconds")
    user_agent: str = Field(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description="User agent for web requests"
    )

    # Redis Streams configuration (optional - can use in-memory if Redis not available)
    redis_host: str = Field("localhost", description="Redis host")
    redis_port: int = Field(6379, description="Redis port")
    redis_db: int = Field(0, description="Redis database number")
    redis_enabled: bool = Field(False, description="Enable Redis (set to False for in-memory mode)")
    redis_stream_key: str = Field("news_stream", description="Redis stream key for news articles")
    redis_max_len: int = Field(10000, description="Maximum length of Redis stream")

    # WebSocket configuration
    websocket_host: str = Field("localhost", description="WebSocket server host")
    websocket_port: int = Field(8765, description="WebSocket server port")
    websocket_ping_interval: int = Field(30, description="WebSocket ping interval in seconds")

    # AI Model configuration
    ai_batch_size: int = Field(8, description="Batch size for AI processing")
    ai_max_length: int = Field(512, description="Maximum sequence length for transformers")
    ai_confidence_threshold: float = Field(0.7, description="Minimum confidence threshold for AI predictions")

    # News sources for real-time monitoring
    news_sources: List[Dict[str, Any]] = Field(default_factory=lambda: [
        {
            "name": "The Hindu - National",
            "url": "https://www.thehindu.com/news/national/",
            "rss_url": "https://www.thehindu.com/news/national/feeder/default.rss",
            "selectors": {
                "article_container": "article",
                "title": "h1, .title",
                "content": ".articlebodycontent, .content-body",
                "publish_date": "time, .publish-date"
            },
            "language": "en",
            "region": "National",
            "category": "Politics"
        },
        {
            "name": "Economic Times - Government",
            "url": "https://economictimes.indiatimes.com/news/economy/policy",
            "rss_url": "https://economictimes.indiatimes.com/news/economy/policy/rssfeeds/1373380680.cms",
            "selectors": {
                "article_container": ".article",
                "title": "h1, .heading",
                "content": ".article_content, .content",
                "publish_date": ".date, time"
            },
            "language": "en",
            "region": "National",
            "category": "Economy & Finance"
        },
        {
            "name": "PIB Press Releases",
            "url": "https://pib.gov.in/PressReleasePage.aspx",
            "rss_url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1",
            "selectors": {
                "article_container": ".news-list, .press-release",
                "title": "h2, .title",
                "content": ".content, .press-content",
                "publish_date": ".date, time"
            },
            "language": "en",
            "region": "National",
            "category": "Government Press Release"
        },
        {
            "name": "Hindustan Times - India",
            "url": "https://www.hindustantimes.com/india-news",
            "rss_url": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
            "selectors": {
                "article_container": ".story-card, article",
                "title": "h1, h2, .hdg",
                "content": ".story-details, .content",
                "publish_date": ".date, time"
            },
            "language": "en",
            "region": "National",
            "category": "General"
        },
        {
            "name": "NDTV India",
            "url": "https://www.ndtv.com/india",
            "rss_url": "https://feeds.feedburner.com/ndtvnews-india-news",
            "selectors": {
                "article_container": ".news_Itm, article",
                "title": "h1, h2, .newsHdng",
                "content": ".newsCont, .content",
                "publish_date": ".pst-by, time"
            },
            "language": "en",
            "region": "National",
            "category": "General"
        }
    ], description="List of news sources for real-time monitoring")

    # AI Model paths and configurations
    model_configs: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "sentiment": {
            "model_name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "task": "sentiment-analysis",
            "labels": ["negative", "neutral", "positive"]
        },
        "summarization": {
            "model_name": "facebook/bart-large-cnn",
            "task": "summarization",
            "max_length": 150,
            "min_length": 50
        },
        "ner": {
            "model_name": "dslim/bert-base-NER",
            "task": "ner",
            "aggregation_strategy": "simple"
        },
        "government_classifier": {
            "model_name": "bert-base-uncased",  # Will be fine-tuned
            "task": "text-classification",
            "labels": ["government_related", "not_government_related"],
            "fine_tuned_path": "./models/government_classifier"
        }
    }, description="Configuration for AI models")

    # Processing pipeline settings
    processing_workers: int = Field(4, description="Number of processing workers")
    queue_prefetch_count: int = Field(10, description="Number of items to prefetch from queue")
    processing_timeout: int = Field(300, description="Processing timeout in seconds")

    # Alert and notification settings
    real_time_alerts: bool = Field(True, description="Enable real-time alerts")
    alert_debounce_seconds: int = Field(60, description="Minimum seconds between similar alerts")

# Global configuration instance
realtime_config = RealTimeConfig()

# Environment variable overrides
def load_from_env():
    """Load configuration from environment variables"""
    global realtime_config

    # Redis settings
    redis_host = os.getenv("REDIS_HOST", realtime_config.redis_host)
    redis_port = int(os.getenv("REDIS_PORT", realtime_config.redis_port))

    # WebSocket settings
    websocket_port = int(os.getenv("WEBSOCKET_PORT", realtime_config.websocket_port))

    # AI settings
    ai_batch_size = int(os.getenv("AI_BATCH_SIZE", realtime_config.ai_batch_size))
    ai_confidence_threshold = float(os.getenv("AI_CONFIDENCE_THRESHOLD", realtime_config.ai_confidence_threshold))

    # Update config
    realtime_config.redis_host = redis_host
    realtime_config.redis_port = redis_port
    realtime_config.websocket_port = websocket_port
    realtime_config.ai_batch_size = ai_batch_size
    realtime_config.ai_confidence_threshold = ai_confidence_threshold

# Load environment configuration on import
load_from_env()
