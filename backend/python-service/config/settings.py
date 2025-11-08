import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Dict, Any

class Settings(BaseSettings):
    app_name: str = "NewsScope India Backend"
    admin_email: str = "admin@newsscope.gov.in"
    environment: str = Field("development", env="ENVIRONMENT")

    # Database settings
    database_url: str = Field("sqlite:///./sql_app.db", env="DATABASE_URL")

    # API Keys and Tokens (use environment variables for production)
    google_translate_api_key: str = Field("", env="GOOGLE_APPLICATION_CREDENTIALS") # Path to credentials file
    youtube_api_key: str = Field("", env="YOUTUBE_API_KEY")
    twitter_bearer_token: str = Field("", env="TWITTER_BEARER_TOKEN")
    facebook_app_id: str = Field("", env="FACEBOOK_APP_ID")
    facebook_app_secret: str = Field("", env="FACEBOOK_APP_SECRET")
    facebook_access_token: str = Field("", env="FACEBOOK_ACCESS_TOKEN")

    # Collector configurations
    rss_feeds: List[Dict[str, Any]] = [
        {"name": "The Hindu", "url": "https://www.thehindu.com/feeder/default.rss", "language": "en", "category": "National", "region": "India"},
        {"name": "NDTV News", "url": "https://feeds.feedburner.com/ndtvnews-latest", "language": "en", "category": "National", "region": "India"},
        # Add more RSS feeds for regional languages here
        # Example for Hindi (requires finding actual RSS feeds)
        # {"name": "Dainik Jagran", "url": "http://feeds.feedburner.com/DainikJagran-National", "language": "hi", "category": "National", "region": "India"},
    ]
    web_scrape_sources: List[Dict[str, Any]] = [
        # Example, in a real scenario, these would be dynamic and point to index pages
        # {"name": "Example News Site", "url": "https://www.example.com/news/article-1", "language": "en", "category": "Technology", "region": "Global"}
    ]
    youtube_channels: List[Dict[str, Any]] = [
        {"name": "Narendra Modi", "language": "hi", "category": "Politics", "region": "India"},
        {"name": "DD News", "language": "en", "category": "News", "region": "India"}
    ]
    twitter_queries: List[Dict[str, Any]] = [
        {"query": "Government of India", "max_results": 10},
        {"query": "#IndianPolitics", "max_results": 10},
        {"query": "PMOIndia", "max_results": 10},
    ]
    facebook_pages: List[Dict[str, Any]] = [
        # {"page_id": "100064820000000", "max_results": 10} # Example: Government of India official page ID
    ]
    scrape_delay: int = 2 # seconds between scraping requests

    # Alert configurations
    alert_thresholds: Dict[str, Any] = {
        "negative_sentiment_score": -0.7, # Trigger alert if sentiment score is below this
        "keywords": ["scandal", "corruption", "crisis", "protest", "misinformation"],
        "min_trending_score": 5 # Minimum score for a topic to be considered trending for alerts
    }
    government_officials_emails: List[str] = ["official1@gov.in", "official2@gov.in"]
    government_officials_phones: List[str] = [] # E.g., ["+919876543210"]

    # Notification settings
    email_notifications: Dict[str, Any] = {
        "enabled": False, # Set to True to enable email alerts
        "sender_email": "your_email@example.com",
        "sender_password": "your_email_password", # Use environment variables or secure storage
        "smtp_server": "smtp.example.com",
        "smtp_port": 587
    }
    sms_notifications: Dict[str, Any] = {
        "enabled": False, # Set to True and configure Twilio for actual SMS
        # "twilio_account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        # "twilio_auth_token": "your_auth_token",
        # "twilio_phone_number": "+15017122661"
    }

    # Celery Beat Schedule (example, actual schedule defined in main app)
    celery_beat_schedule: Dict[str, Any] = {
        "collect-news-every-2-hours": {
            "task": "app.tasks.collect_news_task",
            "schedule": "*/2 * * * *", # Every 2 hours
        },
        "analyze-daily-sentiment": {
            "task": "app.tasks.analyze_daily_sentiment_task",
            "schedule": "0 0 * * *", # Every day at midnight
        },
        "generate-weekly-reports": {
            "task": "app.tasks.generate_weekly_reports_task",
            "schedule": "0 9 * * 0", # Every Sunday at 9 AM
        }
    }

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

def get_settings() -> Settings:
    return Settings()
