import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RSSCollector:
    def __init__(self, config):
        self.config = config
        self.rss_feeds = config.get("rss_feeds", [])
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def fetch_rss_feed(self, url):
        try:
            feed = feedparser.parse(url)
            return feed.entries
        except Exception as e:
            logging.error(f"Error fetching RSS feed from {url}: {e}")
            return []

    def scrape_article_content(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])
            return article_text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error scraping article from {url}: {e}")
            return None

    def collect_news(self):
        collected_articles = []
        for feed_source in self.rss_feeds:
            logging.info(f"Collecting news from RSS feed: {feed_source['name']} ({feed_source['url']})")
            entries = self.fetch_rss_feed(feed_source['url'])
            for entry in entries:
                article = self._parse_rss_entry(entry, feed_source)
                if article:
                    full_content = self.scrape_article_content(article['url'])
                    if full_content:
                        article['content'] = full_content
                        collected_articles.append(article)
                time.sleep(self.config.get("scrape_delay", 1)) # Be polite to websites
        return collected_articles

    def _parse_rss_entry(self, entry, feed_source):
        try:
            title = entry.get('title')
            link = entry.get('link')
            published_date_str = entry.get('published') or entry.get('updated')
            
            published_date = None
            if published_date_str:
                try:
                    # Attempt to parse various date formats
                    published_date = datetime.strptime(published_date_str, '%a, %d %b %Y %H:%M:%S %z')
                except ValueError:
                    try:
                        published_date = datetime.strptime(published_date_str, '%Y-%m-%dT%H:%M:%S%z')
                    except ValueError:
                        try:
                            published_date = datetime.strptime(published_date_str, '%Y-%m-%dT%H:%M:%SZ')
                        except ValueError:
                            logging.warning(f"Could not parse date format: {published_date_str}")

            author = entry.get('author', 'N/A')
            
            return {
                'title': title,
                'url': link,
                'source': feed_source['name'],
                'language': feed_source.get('language', 'en'), # Default to English if not specified
                'category': feed_source.get('category', 'General'),
                'region': feed_source.get('region', 'N/A'),
                'publish_date': published_date,
                'collected_date': datetime.now(),
                'author': author,
                'content': None # Will be filled by scraping
            }
        except Exception as e:
            logging.error(f"Error parsing RSS entry: {e} - Entry: {entry}")
            return None

if __name__ == '__main__':
    # Example Usage (replace with actual config loading)
    sample_config = {
        "rss_feeds": [
            {"name": "The Hindu", "url": "https://www.thehindu.com/feeder/default.rss", "language": "en", "category": "National", "region": "India"},
            {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml", "language": "en", "category": "International", "region": "Global"}
        ],
        "scrape_delay": 2
    }
    
    collector = RSSCollector(sample_config)
    articles = collector.collect_news()
    for article in articles[:5]: # Print first 5 articles
        print(f"Title: {article['title']}\nURL: {article['url']}\nSource: {article['source']}\nContent Snippet: {article['content'][:200]}...\n")
