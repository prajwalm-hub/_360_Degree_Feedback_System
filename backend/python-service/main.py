from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
import os
import sys

# Add the current directory to the path to allow relative imports
sys.path.insert(0, os.path.dirname(__file__))

# Local imports
from config.settings import get_settings, Settings
from database import DatabaseManager
import sys
import os
sys.path.append(os.path.dirname(__file__))
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))
import database_models
DatabaseManager = database_models.DatabaseManager
Article = database_models.Article
Video = database_models.Video
SocialMediaPost = database_models.SocialMediaPost
Entity = database_models.Entity
Topic = database_models.Topic
SentimentAnalytic = database_models.SentimentAnalytic
GovernmentFeedback = database_models.GovernmentFeedback
Alert = database_models.Alert
from api.endpoints import router as api_router, get_db

# Collectors
from collectors.rss_collector import RSSCollector
from collectors.web_scraper import WebScraper
from collectors.youtube_collector import YouTubeCollector
from collectors.social_media_collector import SocialMediaCollector

# NLP Pipeline
from nlp_pipeline.language_detector import LanguageDetector
from nlp_pipeline.translator import Translator
from nlp_pipeline.preprocessor import TextPreprocessor
from nlp_pipeline.sentiment_analyzer import SentimentAnalyzer
from nlp_pipeline.ner import NamedEntityRecognizer
from nlp_pipeline.summarizer import Summarizer
from nlp_pipeline.keyword_extractor import KeywordExtractor
from nlp_pipeline.classifier import TextClassifier

# Analytics
from analytics.sentiment_aggregator import SentimentAggregator
from analytics.trending_detector import TrendingDetector
from analytics.entity_analyzer import EntityAnalyzer
from analytics.report_generator import ReportGenerator

# Services
from services.alert_service import AlertService
from services.notification_service import NotificationService

# Celery (placeholder for actual Celery setup)
# from celery import Celery
# from celery.schedules import crontab

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NewsScope India API",
    description="API for real-time news monitoring and analysis for the Government of India.",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api/v1")

# Global instances of services
db_manager: DatabaseManager = None
settings: Settings = None

# NLP Pipeline instances
language_detector: LanguageDetector = None
translator: Translator = None
preprocessor: TextPreprocessor = None
sentiment_analyzer: SentimentAnalyzer = None
ner_recognizer: NamedEntityRecognizer = None
summarizer: Summarizer = None
keyword_extractor: KeywordExtractor = None
text_classifier: TextClassifier = None

# Analytics instances
sentiment_aggregator: SentimentAggregator = None
trending_detector: TrendingDetector = None
entity_analyzer: EntityAnalyzer = None
report_generator: ReportGenerator = None

# Service instances
alert_service: AlertService = None
notification_service: NotificationService = None

@app.on_event("startup")
async def startup_event():
    global db_manager, settings
    global language_detector, translator, preprocessor, sentiment_analyzer, ner_recognizer, summarizer, keyword_extractor, text_classifier
    global sentiment_aggregator, trending_detector, entity_analyzer, report_generator
    global alert_service, notification_service

    settings = get_settings()
    logger.info(f"Starting up NewsScope India Backend in {settings.environment} environment.")

    # Initialize Database
    db_manager = DatabaseManager(settings.database_url)
    db_manager.create_all_tables()
    logger.info("Database tables checked/created.")

    # Initialize NLP Pipeline components
    language_detector = LanguageDetector()
    translator = Translator(settings)
    preprocessor = TextPreprocessor(language='english') # Default to English, can be dynamic
    sentiment_analyzer = SentimentAnalyzer()
    ner_recognizer = NamedEntityRecognizer()
    summarizer = Summarizer()
    keyword_extractor = KeywordExtractor()
    text_classifier = TextClassifier()
    # In a real app, you'd load a pre-trained classifier model here:
    # if not text_classifier.load_model("path/to/your/classifier_model.joblib"):
    #     logger.warning("Text classifier model not found. Classification will be limited or require training.")

    # Initialize Analytics components
    sentiment_aggregator = SentimentAggregator()
    trending_detector = TrendingDetector() # Default time window and min mentions
    entity_analyzer = EntityAnalyzer()
    report_generator = ReportGenerator()

    # Initialize Services
    alert_service = AlertService(settings.alert_thresholds)
    notification_service = NotificationService(settings)

    logger.info("All backend services initialized.")

    # TODO: Initialize Celery app and tasks here if using Celery
    # app.celery_app = Celery(
    #     'news_tasks',
    #     broker=settings.celery_broker_url,
    #     backend=settings.celery_backend_url
    # )
    # app.celery_app.conf.beat_schedule = settings.celery_beat_schedule
    # app.celery_app.conf.timezone = 'Asia/Calcutta' # Or appropriate timezone
    # logger.info("Celery app initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down NewsScope India Backend.")
    # Perform any cleanup here, e.g., close database connections if not handled by sessionmaker


@app.get("/")
async def root():
    return {"message": "Welcome to NewsScope India API"}

# Example of a processing endpoint (this would typically be triggered by a collector or scheduler)
@app.post("/process_article/")
async def process_article_data(article_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Processes a single article through the NLP pipeline and stores it.
    This is a simplified endpoint for demonstration.
    """
    try:
        # 1. Language Detection
        detected_lang = language_detector.detect_language(article_data['content'])
        article_data['language'] = detected_lang if detected_lang else article_data.get('language', 'en')

        # 2. Translation (if not English)
        if article_data['language'] != 'en':
            translated_content = translator.translate_text(article_data['content'], article_data['language'], 'en')
            article_data['translated_content'] = translated_content
        else:
            article_data['translated_content'] = article_data['content']

        # 3. Text Preprocessing
        preprocessed_text = preprocessor.preprocess(article_data['translated_content'])

        # 4. Sentiment Analysis
        sentiment_result = sentiment_analyzer.analyze_sentiment(article_data['translated_content'], 'en')
        article_data['sentiment'] = sentiment_result
        article_data['emotions'] = sentiment_result.get('emotions', {})

        # 5. Named Entity Recognition
        entities = ner_recognizer.extract_entities(article_data['translated_content'])
        article_data['entities'] = entities

        # 6. Text Classification
        categories = text_classifier.classify_article(preprocessed_text)
        article_data['category'] = categories[0] if categories else 'Uncategorized' # Take first category for simplicity
        article_data['topics'] = categories # Store all categories as topics

        # 7. Keyword Extraction
        keywords = keyword_extractor.extract_keywords_gensim(preprocessed_text)
        article_data['keywords'] = keywords

        # 8. Summarization
        summary = summarizer.summarize_text(article_data['translated_content'])
        article_data['summary'] = summary

        # Store in database
        db_article = Article(
            id=article_data.get('id'),
            title=article_data.get('title'),
            content=article_data.get('content'),
            source=article_data.get('source'),
            language=article_data.get('language'),
            category=article_data.get('category'),
            region=article_data.get('region'),
            publish_date=article_data.get('publish_date'),
            collected_date=article_data.get('collected_date'),
            url=article_data.get('url'),
            author=article_data.get('author'),
            sentiment=article_data.get('sentiment'),
            emotions=article_data.get('emotions'),
            entities=article_data.get('entities'),
            summary=article_data.get('summary'),
            keywords=article_data.get('keywords'),
            topics=article_data.get('topics')
        )
        db.add(db_article)
        db.commit()
        db.refresh(db_article)

        # Update analytics (these would typically be batched or run by scheduled tasks)
        entity_analyzer.process_entities(entities, sentiment_result, db_article.collected_date)
        trending_detector.add_topics(article_data['topics'], db_article.collected_date)

        # Check for alerts
        alerts = alert_service.check_for_alerts('article', article_data)
        for alert in alerts:
            db_alert = Alert(**alert)
            db.add(db_alert)
            db.commit()
            db.refresh(db_alert)
            if alert_service.should_notify(alert['alert_type']):
                notification_service.notify_officials(alert)

        return {"message": "Article processed and stored successfully", "article_id": db_article.id}
    except Exception as e:
        logger.error(f"Error processing article: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing article: {e}")

# TODO: Define Celery tasks in a separate file (e.g., tasks.py) and import them here
# @app.celery_app.task(name="app.tasks.collect_news_task")
# def collect_news_task():
#     # Instantiate collectors and run them
#     settings = get_settings()
#     rss_collector = RSSCollector(settings)
#     web_scraper = WebScraper(settings)
#     youtube_collector = YouTubeCollector(settings)
#     social_media_collector = SocialMediaCollector(settings)
#
#     articles = rss_collector.collect_news()
#     articles.extend(web_scraper.collect_news())
#     # videos = youtube_collector.collect_videos()
#     # social_posts = social_media_collector.collect_social_media()
#
#     # Process collected data (e.g., send to /process_article/ endpoint or directly process)
#     # For simplicity, we'll just log here. In a real system, this would push to a queue
#     # or call the processing logic.
#     logger.info(f"Collected {len(articles)} articles.")
#     # logger.info(f"Collected {len(videos)} videos.")
#     # logger.info(f"Collected {len(social_posts)} social media posts.")
#
# @app.celery_app.task(name="app.tasks.analyze_daily_sentiment_task")
# def analyze_daily_sentiment_task():
#     # Logic to fetch data from DB, aggregate sentiment, and store
#     logger.info("Running daily sentiment analysis.")
#
# @app.celery_app.task(name="app.tasks.generate_weekly_reports_task")
# def generate_weekly_reports_task():
#     # Logic to generate reports
#     logger.info("Generating weekly reports.")
