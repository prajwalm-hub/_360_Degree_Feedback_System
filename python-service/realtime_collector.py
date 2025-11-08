"""
Real-time news collector with change detection.
Replaces the polling-based RSS collector with web scraping and change detection.
"""

import asyncio
import hashlib
import json
import logging
import time
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import aiohttp
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    # Fallback in-memory implementation
    class MockRedis:
        def __init__(self):
            self.data = {}
            self.streams = {}

        async def get(self, key):
            return self.data.get(key)

        async def setex(self, key, ttl, value):
            self.data[key] = value
            return True

        async def xadd(self, stream, data, maxlen=None):
            if stream not in self.streams:
                self.streams[stream] = []
            self.streams[stream].append(data)
            if maxlen and len(self.streams[stream]) > maxlen:
                self.streams[stream] = self.streams[stream][-maxlen:]
            return "mock_id"

        async def xread(self, streams, block=None):
            # Mock implementation - return empty for now
            return []

    redis = MockRedis()

from bs4 import BeautifulSoup
from newspaper import Article as NewspaperArticle

from config.realtime_config import realtime_config
# Import database models directly
from database_models import Article, Video, SocialMediaPost, Entity, Topic, SentimentAnalytic, GovernmentFeedback, Alert

logger = logging.getLogger(__name__)

class ChangeDetector:
    """Detects changes in web pages using content hashing"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.hash_key_prefix = "page_hash:"

    async def get_page_hash(self, url: str) -> Optional[str]:
        """Get stored hash for a URL"""
        key = f"{self.hash_key_prefix}{hashlib.md5(url.encode()).hexdigest()}"
        return await self.redis.get(key)

    async def set_page_hash(self, url: str, content_hash: str):
        """Store hash for a URL with expiration"""
        key = f"{self.hash_key_prefix}{hashlib.md5(url.encode()).hexdigest()}"
        await self.redis.setex(key, 86400 * 7, content_hash)  # 7 days expiration

    async def has_changed(self, url: str, new_content: str) -> bool:
        """Check if page content has changed"""
        new_hash = hashlib.md5(new_content.encode('utf-8')).hexdigest()
        old_hash = await self.get_page_hash(url)

        if old_hash != new_hash:
            await self.set_page_hash(url, new_hash)
            return True
        return False

class RealTimeCollector:
    """Real-time news collector with change detection"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.change_detector = ChangeDetector(redis_client)
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.last_check_times: Dict[str, datetime] = {}

        # Setup headers
        self.headers = {
            'User-Agent': realtime_config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def start_collection(self):
        """Start the real-time collection process"""
        self.running = True
        logger.info("Starting real-time news collection...")

        while self.running:
            try:
                await self._collect_from_all_sources()
                await asyncio.sleep(realtime_config.change_detection_interval)
            except Exception as e:
                logger.error(f"Error in collection cycle: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    def stop_collection(self):
        """Stop the collection process"""
        self.running = False
        logger.info("Stopping real-time news collection...")

    async def _collect_from_all_sources(self):
        """Collect from all configured news sources"""
        tasks = []
        semaphore = asyncio.Semaphore(realtime_config.max_concurrent_scrapers)

        for source in realtime_config.news_sources:
            # Rate limiting: don't check too frequently
            if self._should_check_source(source['name']):
                tasks.append(self._collect_from_source(source, semaphore))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _should_check_source(self, source_name: str) -> bool:
        """Check if source should be checked based on timing"""
        now = datetime.now()
        last_check = self.last_check_times.get(source_name)

        if not last_check or (now - last_check).seconds >= realtime_config.change_detection_interval:
            self.last_check_times[source_name] = now
            return True
        return False

    async def _collect_from_source(self, source: Dict[str, Any], semaphore: asyncio.Semaphore):
        """Collect news from a single source"""
        async with semaphore:
            try:
                logger.debug(f"Checking source: {source['name']}")

                # First try RSS feed for quick updates
                rss_articles = await self._collect_from_rss(source)
                if rss_articles:
                    await self._queue_articles(rss_articles)
                    return

                # Fall back to web scraping
                articles = await self._scrape_website(source)
                if articles:
                    await self._queue_articles(articles)

            except Exception as e:
                logger.error(f"Error collecting from {source['name']}: {e}")

    async def _collect_from_rss(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect articles from RSS feed"""
        if 'rss_url' not in source:
            return []

        try:
            async with self.session.get(source['rss_url'], timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return []

                import feedparser
                content = await response.text()
                feed = feedparser.parse(content)

                articles = []
                for entry in feed.entries[:10]:  # Limit to recent entries
                    article_data = self._parse_rss_entry(entry, source)
                    if article_data:
                        articles.append(article_data)

                return articles

        except Exception as e:
            logger.warning(f"RSS collection failed for {source['name']}: {e}")
            return []

    async def _scrape_website(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape website for new articles"""
        try:
            async with self.session.get(source['url'], timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return []

                html = await response.text()

                # Check if page has changed
                if not await self.change_detector.has_changed(source['url'], html):
                    logger.debug(f"No changes detected for {source['name']}")
                    return []

                # Parse HTML and extract articles
                soup = BeautifulSoup(html, 'html.parser')
                articles = []

                # Find article containers
                containers = soup.select(source['selectors'].get('article_container', 'article'))
                for container in containers[:5]:  # Limit to 5 most recent
                    article_data = self._extract_article_from_container(container, source)
                    if article_data:
                        articles.append(article_data)

                return articles

        except Exception as e:
            logger.error(f"Web scraping failed for {source['name']}: {e}")
            return []

    def _parse_rss_entry(self, entry, source: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse RSS entry into article data"""
        try:
            title = getattr(entry, 'title', '').strip()
            link = getattr(entry, 'link', '')

            if not title or not link:
                return None

            # Extract publish date
            publish_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                publish_date = datetime(*entry.published_parsed[:6])
            else:
                publish_date = datetime.now()

            return {
                'title': title,
                'url': link,
                'source': source['name'],
                'language': source.get('language', 'en'),
                'category': source.get('category', 'General'),
                'region': source.get('region', 'National'),
                'publish_date': publish_date.isoformat(),
                'collected_date': datetime.now().isoformat(),
                'content': getattr(entry, 'summary', ''),
                'is_government_related': False,  # Will be determined by AI
                'metadata': {
                    'source_type': 'rss',
                    'selectors': source.get('selectors', {})
                }
            }

        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None

    def _extract_article_from_container(self, container, source: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract article data from HTML container"""
        try:
            selectors = source.get('selectors', {})

            # Extract title
            title_elem = container.select_one(selectors.get('title', 'h1, h2, .title'))
            title = title_elem.get_text().strip() if title_elem else ""

            # Extract URL
            url = ""
            link_elem = container.find('a', href=True)
            if link_elem:
                url = urljoin(source['url'], link_elem['href'])

            # Extract publish date
            date_elem = container.select_one(selectors.get('publish_date', 'time, .date'))
            publish_date = datetime.now()
            if date_elem:
                # Try to parse various date formats
                date_text = date_elem.get_text() or date_elem.get('datetime', '')
                # Basic parsing - could be enhanced
                publish_date = datetime.now()  # Placeholder

            if not title or not url:
                return None

            return {
                'title': title,
                'url': url,
                'source': source['name'],
                'language': source.get('language', 'en'),
                'category': source.get('category', 'General'),
                'region': source.get('region', 'National'),
                'publish_date': publish_date.isoformat(),
                'collected_date': datetime.now().isoformat(),
                'content': '',  # Will be fetched later
                'is_government_related': False,
                'metadata': {
                    'source_type': 'scrape',
                    'selectors': selectors
                }
            }

        except Exception as e:
            logger.error(f"Error extracting article from container: {e}")
            return None

    async def _queue_articles(self, articles: List[Dict[str, Any]]):
        """Queue articles for processing"""
        try:
            for article in articles:
                # Add to Redis stream
                await self.redis.xadd(
                    realtime_config.redis_stream_key,
                    {'data': json.dumps(article)},
                    maxlen=realtime_config.redis_max_len
                )

            logger.info(f"Queued {len(articles)} articles for processing")

        except Exception as e:
            logger.error(f"Error queuing articles: {e}")

async def main():
    """Main function for testing"""
    redis_client = redis.Redis(
        host=realtime_config.redis_host,
        port=realtime_config.redis_port,
        db=realtime_config.redis_db,
        decode_responses=True
    )

    async with RealTimeCollector(redis_client) as collector:
        try:
            await collector.start_collection()
        except KeyboardInterrupt:
            collector.stop_collection()

if __name__ == "__main__":
    asyncio.run(main())
