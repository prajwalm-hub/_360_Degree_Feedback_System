from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    language = Column(String, nullable=False)
    category = Column(String)
    region = Column(String)
    publish_date = Column(DateTime)
    collected_date = Column(DateTime, default=datetime.now)
    url = Column(String, unique=True, nullable=False)
    author = Column(String)
    sentiment = Column(JSON) # Stores {'sentiment': 'positive', 'score': 0.8, 'emotions': {}}
    emotions = Column(JSON) # Redundant if sentiment stores it, but kept for schema clarity
    entities = Column(JSON) # Stores list of {'text': 'Narendra Modi', 'label': 'PERSON'}
    summary = Column(Text)
    keywords = Column(JSON) # Stores list of strings
    topics = Column(JSON) # Stores list of strings
    is_government_related = Column(Boolean, default=False)
    departments = Column(JSON) # Stores list of {'department': str, 'confidence': float}
    government_scheme = Column(String)
    government_entity = Column(String)
    policy_type = Column(String)
    confidence_score = Column(Float, default=0.0)

    def __repr__(self):
        return f"<Article(title='{self.title}', source='{self.source}')>"

class Video(Base):
    __tablename__ = 'videos'
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    transcript = Column(Text)
    channel = Column(String)
    upload_date = Column(DateTime)
    views = Column(Integer)
    likes = Column(Integer)
    comments = Column(Integer)
    duration = Column(String) # ISO 8601 format string
    url = Column(String, unique=True, nullable=False)
    sentiment = Column(JSON)
    emotions = Column(JSON)
    entities = Column(JSON)
    summary = Column(Text)

    def __repr__(self):
        return f"<Video(title='{self.title}', channel='{self.channel}')>"

class SocialMediaPost(Base):
    __tablename__ = 'social_media_posts'
    id = Column(String, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    account = Column(String)
    post_date = Column(DateTime)
    likes = Column(Integer)
    shares = Column(Integer)
    comments = Column(Integer)
    sentiment = Column(JSON)
    language = Column(String)

    def __repr__(self):
        return f"<SocialMediaPost(platform='{self.platform}', id='{self.id}')>"

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String) # Person, Organization, Location, Event, Other
    mentions_count = Column(Integer, default=0)
    positive_sentiment_count = Column(Integer, default=0)
    negative_sentiment_count = Column(Integer, default=0)
    neutral_sentiment_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Entity(name='{self.name}', type='{self.type}')>"

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic_name = Column(String, unique=True, nullable=False)
    article_count = Column(Integer, default=0)
    sentiment_distribution = Column(JSON) # {'positive': X, 'negative': Y, 'neutral': Z}
    trending_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Topic(topic_name='{self.topic_name}')>"

class SentimentAnalytic(Base):
    __tablename__ = 'sentiment_analytics'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    source_type = Column(String, nullable=False) # 'article', 'video', 'social_media'
    category = Column(String)
    region = Column(String)
    language = Column(String)
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    avg_sentiment_score = Column(Float, default=0.0)
    total_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<SentimentAnalytic(date='{self.date.date()}', category='{self.category}', region='{self.region}')>"

class GovernmentFeedback(Base):
    __tablename__ = 'government_feedback'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic = Column(String)
    sentiment_summary = Column(JSON) # Summary of sentiment for the topic
    key_issues = Column(JSON) # List of key issues identified
    public_perception = Column(Text)
    recommendations = Column(Text)
    generated_date = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<GovernmentFeedback(topic='{self.topic}', generated_date='{self.generated_date.date()}')>"

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False) # e.g., 'Low', 'Medium', 'High', 'Critical'
    content = Column(Text, nullable=False)
    threshold_triggered = Column(String) # e.g., '-0.7 sentiment score'
    created_date = Column(DateTime, default=datetime.now)
    status = Column(String, default='new') # 'new', 'acknowledged', 'resolved'
    original_data_id = Column(String) # ID of the article/video/post that triggered it
    original_data_type = Column(String) # 'article', 'video', 'social_media'

    def __repr__(self):
        return f"<Alert(type='{self.alert_type}', severity='{self.severity}', status='{self.status}')>"

class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        logging.info(f"DatabaseManager initialized for {database_url}")

    def create_all_tables(self):
        Base.metadata.create_all(self.engine)
        logging.info("All database tables created (if they didn't exist).")

    def get_session(self):
        return self.Session()

if __name__ == '__main__':
    # Example Usage
    # For PostgreSQL, use a URL like: "postgresql://user:password@host:port/database_name"
    # For SQLite (for local testing): "sqlite:///./test.db"
    DATABASE_URL = "sqlite:///./test.db" 
    db_manager = DatabaseManager(DATABASE_URL)
    db_manager.create_all_tables()

    # Example of adding an article
    session = db_manager.get_session()
    try:
        new_article = Article(
            id="test_article_1",
            title="Sample News Article",
            content="This is the content of a sample news article.",
            source="Example News",
            language="en",
            url="http://example.com/article/1",
            sentiment={'sentiment': 'neutral', 'score': 0.0},
            keywords=['sample', 'news']
        )
        session.add(new_article)
        session.commit()
        logging.info(f"Added article: {new_article.title}")

        # Querying
        articles = session.query(Article).all()
        for article in articles:
            print(f"Found article: {article.title} from {article.source}")

    except Exception as e:
        session.rollback()
        logging.error(f"Error during database operation: {e}")
    finally:
        session.close()
