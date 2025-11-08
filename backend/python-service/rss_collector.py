import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from urllib.parse import urljoin
import re
import time
import logging
from bs4 import BeautifulSoup

from models import RSSSource, NewsArticle, ProcessingJob, JobStatus
from database import DatabaseManager
import sys
import os
sys.path.append(os.path.dirname(__file__))
import config
RSS_SOURCES = getattr(config, 'RSS_SOURCES', [])
GOVERNMENT_KEYWORDS = getattr(config, 'GOVERNMENT_KEYWORDS', [])
MAX_ARTICLES_PER_FETCH = getattr(config, 'MAX_ARTICLES_PER_FETCH', 50)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSSCollector:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def initialize_rss_sources(self):
        """Initialize RSS sources from config if they don't exist"""
        existing_sources = self.db.get_active_rss_sources()
        existing_urls = {source.url for source in existing_sources}
        
        for source_config in RSS_SOURCES:
            if source_config['url'] not in existing_urls:
                source = RSSSource(
                    id=None,
                    name=source_config['name'],
                    url=source_config['url'],
                    language=source_config['language'],
                    region=source_config.get('region'),
                    category=source_config.get('category')
                )
                source_id = self.db.insert_rss_source(source)
                logger.info(f"Added RSS source: {source.name} (ID: {source_id})")
    
    def fetch_all_sources(self):
        """Fetch articles from all active RSS sources"""
        sources = self.db.get_active_rss_sources()
        total_new_articles = 0
        
        for source in sources:
            try:
                if self._should_fetch_source(source):
                    new_articles = self.fetch_source(source)
                    total_new_articles += len(new_articles)
                    self.db.update_rss_source_last_fetched(source.id)
                    logger.info(f"Fetched {len(new_articles)} new articles from {source.name}")
                    
                    # Small delay between sources to be respectful
                    time.sleep(2)
                else:
                    logger.debug(f"Skipping {source.name} - not due for fetch")
            except Exception as e:
                logger.error(f"Error fetching from {source.name}: {str(e)}")
        
        logger.info(f"Total new articles collected: {total_new_articles}")
        return total_new_articles
    
    def fetch_source(self, source: RSSSource) -> List[NewsArticle]:
        """Fetch articles from a single RSS source"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(source.url)
            
            if feed.bozo:
                logger.warning(f"RSS feed {source.name} has parsing issues: {feed.bozo_exception}")
            
            new_articles = []
            processed_count = 0
            
            for entry in feed.entries[:MAX_ARTICLES_PER_FETCH]:
                try:
                    # Check if article already exists
                    if self.db.article_exists(entry.title, source.name):
                        continue
                    
                    # Extract article content
                    article = self._parse_feed_entry(entry, source)
                    
                    # Filter for government-related content
                    if self._is_government_related(article):
                        article_id = self.db.insert_news_article(article)
                        article.id = article_id
                        new_articles.append(article)
                        
                        # Create processing job for AI/ML analysis
                        job = ProcessingJob(
                            id=None,
                            job_type="analyze_article",
                            article_id=article_id,
                            source_id=source.id
                        )
                        self.db.create_processing_job(job)
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing entry from {source.name}: {str(e)}")
                    continue
            
            return new_articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed {source.name}: {str(e)}")
            return []
    
    def _should_fetch_source(self, source: RSSSource) -> bool:
        """Check if source should be fetched based on frequency"""
        if not source.last_fetched_at:
            return True
        
        next_fetch = source.last_fetched_at + timedelta(minutes=source.fetch_frequency_minutes)
        return datetime.now() >= next_fetch
    
    def _parse_feed_entry(self, entry, source: RSSSource) -> NewsArticle:
        """Parse a single RSS feed entry into a NewsArticle"""
        
        # Extract content
        content = ""
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        # Clean HTML content
        content = self._clean_html_content(content)
        
        # Extract publish date
        publish_date = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            publish_date = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            publish_date = datetime(*entry.updated_parsed[:6])
        else:
            publish_date = datetime.now()
        
        # Extract author
        author = None
        if hasattr(entry, 'author'):
            author = entry.author
        elif hasattr(entry, 'authors') and entry.authors:
            author = entry.authors[0].get('name', '')
        
        return NewsArticle(
            id=None,
            title=entry.title.strip(),
            content=content,
            source=source.name,
            source_url=entry.link if hasattr(entry, 'link') else None,
            language=source.language,
            author=author,
            publish_date=publish_date,
            region=source.region,
            category=source.category or "General",
            is_government_related=True  # Will be validated by _is_government_related
        )
    
    def _clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and extract plain text"""
        if not html_content:
            return ""
        
        # Use BeautifulSoup to clean HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean whitespace
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _is_government_related(self, article: NewsArticle) -> bool:
        """Check if article is related to government based on keywords"""
        
        # Combine title and content for keyword search
        text_to_check = f"{article.title} {article.content}".lower()
        
        # Check for government keywords
        for keyword in GOVERNMENT_KEYWORDS:
            if keyword.lower() in text_to_check:
                return True
        
        # Additional heuristics based on source category
        if article.category in ["Government Press Release", "Politics", "Policy & Legislation"]:
            return True
        
        return False
    
    def get_full_article_content(self, url: str) -> Optional[str]:
        """Attempt to fetch full article content from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common article content selectors
            selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main'
            ]
            
            for selector in selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove unwanted elements
                    for unwanted in content_elem.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        unwanted.decompose()
                    
                    text = content_elem.get_text()
                    if len(text.strip()) > 200:  # Only return if substantial content
                        return self._clean_html_content(str(content_elem))
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not fetch full content from {url}: {str(e)}")
            return None
