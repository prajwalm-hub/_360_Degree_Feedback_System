import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from models import RSSSource, NewsArticle, ProcessingJob, Alert, JobStatus, SentimentLabel
import os
DATABASE_PATH = os.getenv('DATABASE_PATH', '../.wrangler/state/v3/d1/miniflare-D1DatabaseObject/0a63475064ba0fef38489ee0454cb2d789b28a906ef12161e40ea6ea13385173.sqlite')

class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    # RSS Sources
    def get_active_rss_sources(self) -> List[RSSSource]:
        query = "SELECT * FROM rss_sources WHERE is_active = 1"
        rows = self.execute_query(query)
        return [self._row_to_rss_source(row) for row in rows]
    
    def insert_rss_source(self, source: RSSSource) -> int:
        query = """
        INSERT INTO rss_sources (name, url, language, region, category, is_active, fetch_frequency_minutes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (
            source.name, source.url, source.language, source.region,
            source.category, source.is_active, source.fetch_frequency_minutes
        ))
    
    def update_rss_source_last_fetched(self, source_id: int):
        query = "UPDATE rss_sources SET last_fetched_at = ?, updated_at = ? WHERE id = ?"
        now = datetime.now().isoformat()
        self.execute_update(query, (now, now, source_id))
    
    # News Articles
    def insert_news_article(self, article: NewsArticle) -> int:
        query = """
        INSERT INTO news_articles (
            title, content, source, source_url, language, translated_content,
            author, publish_date, region, category, sentiment_score, sentiment_label,
            emotions, keywords, summary, entities, is_government_related, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        sentiment_label_str = article.sentiment_label.value if article.sentiment_label else None
        
        return self.execute_update(query, (
            article.title, article.content, article.source, article.source_url,
            article.language, article.translated_content, article.author,
            article.publish_date.isoformat() if article.publish_date else now,
            article.region, article.category, article.sentiment_score,
            sentiment_label_str, article.emotions, article.keywords,
            article.summary, article.entities, article.is_government_related,
            now, now
        ))
    
    def get_recent_articles(self, limit: int = 100) -> List[NewsArticle]:
        query = """
        SELECT * FROM news_articles 
        ORDER BY publish_date DESC, created_at DESC 
        LIMIT ?
        """
        rows = self.execute_query(query, (limit,))
        return [self._row_to_news_article(row) for row in rows]
    
    def article_exists(self, title: str, source: str) -> bool:
        query = "SELECT COUNT(*) as count FROM news_articles WHERE title = ? AND source = ?"
        result = self.execute_query(query, (title, source))
        return result[0]['count'] > 0
    
    # Processing Jobs
    def create_processing_job(self, job: ProcessingJob) -> int:
        query = """
        INSERT INTO processing_jobs (job_type, status, article_id, source_id, metadata)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (
            job.job_type, job.status.value, job.article_id, job.source_id,
            json.dumps(job.metadata) if job.metadata else None
        ))
    
    def update_job_status(self, job_id: int, status: JobStatus, error_message: str = None):
        now = datetime.now().isoformat()
        if status == JobStatus.PROCESSING:
            query = "UPDATE processing_jobs SET status = ?, started_at = ?, updated_at = ? WHERE id = ?"
            self.execute_update(query, (status.value, now, now, job_id))
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            query = """
            UPDATE processing_jobs SET status = ?, completed_at = ?, updated_at = ?, error_message = ? 
            WHERE id = ?
            """
            self.execute_update(query, (status.value, now, now, error_message, job_id))
    
    def get_pending_jobs(self, job_type: str = None) -> List[ProcessingJob]:
        if job_type:
            query = "SELECT * FROM processing_jobs WHERE status = ? AND job_type = ? ORDER BY created_at ASC"
            params = (JobStatus.PENDING.value, job_type)
        else:
            query = "SELECT * FROM processing_jobs WHERE status = ? ORDER BY created_at ASC"
            params = (JobStatus.PENDING.value,)
        
        rows = self.execute_query(query, params)
        return [self._row_to_processing_job(row) for row in rows]
    
    # Alerts
    def create_alert(self, alert: Alert) -> int:
        query = """
        INSERT INTO alerts (alert_type, severity, title, content, article_id, threshold_triggered)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (
            alert.alert_type, alert.severity, alert.title, alert.content,
            alert.article_id, alert.threshold_triggered
        ))
    
    # Helper methods to convert rows to objects
    def _row_to_rss_source(self, row: Dict) -> RSSSource:
        return RSSSource(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            language=row['language'],
            region=row.get('region'),
            category=row.get('category'),
            is_active=bool(row['is_active']),
            last_fetched_at=datetime.fromisoformat(row['last_fetched_at']) if row.get('last_fetched_at') else None,
            fetch_frequency_minutes=row['fetch_frequency_minutes'],
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else None
        )
    
    def _row_to_news_article(self, row: Dict) -> NewsArticle:
        sentiment_label = None
        if row.get('sentiment_label'):
            try:
                sentiment_label = SentimentLabel(row['sentiment_label'])
            except ValueError:
                pass
        
        return NewsArticle(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            source=row['source'],
            source_url=row.get('source_url'),
            language=row['language'],
            translated_content=row.get('translated_content'),
            author=row.get('author'),
            publish_date=datetime.fromisoformat(row['publish_date']) if row.get('publish_date') else None,
            region=row.get('region'),
            category=row.get('category'),
            sentiment_score=row.get('sentiment_score'),
            sentiment_label=sentiment_label,
            emotions=row.get('emotions'),
            keywords=row.get('keywords'),
            summary=row.get('summary'),
            entities=row.get('entities'),
            is_government_related=bool(row.get('is_government_related', True)),
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else None
        )
    
    def _row_to_processing_job(self, row: Dict) -> ProcessingJob:
        return ProcessingJob(
            id=row['id'],
            job_type=row['job_type'],
            status=JobStatus(row['status']),
            article_id=row.get('article_id'),
            source_id=row.get('source_id'),
            started_at=datetime.fromisoformat(row['started_at']) if row.get('started_at') else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row.get('completed_at') else None,
            error_message=row.get('error_message'),
            metadata=json.loads(row['metadata']) if row.get('metadata') else None,
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row.get('updated_at') else None
        )
