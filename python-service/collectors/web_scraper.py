import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebScraper:
    def __init__(self, config):
        self.config = config
        self.news_sources = config.get("web_scrape_sources", [])
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def scrape_article(self, url, source_name, language='en', category='General', region='N/A'):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            title = self._extract_title(soup)
            content = self._extract_content(soup)
            publish_date = self._extract_publish_date(soup)
            author = self._extract_author(soup)

            if not title or not content:
                logging.warning(f"Could not extract title or content from {url}")
                return None

            return {
                'title': title,
                'url': url,
                'source': source_name,
                'language': language,
                'category': category,
                'region': region,
                'publish_date': publish_date,
                'collected_date': datetime.now(),
                'author': author,
                'content': content
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"Error scraping article from {url}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error during scraping {url}: {e}")
            return None

    def _extract_title(self, soup):
        title = soup.find('h1')
        if title:
            return title.get_text(strip=True)
        meta_title = soup.find('meta', attrs={'property': 'og:title'}) or soup.find('meta', attrs={'name': 'title'})
        if meta_title and meta_title.get('content'):
            return meta_title['content'].strip()
        return None

    def _extract_content(self, soup):
        # Common article content containers
        content_divs = soup.find_all(['div', 'article', 'main'], class_=[
            'article-content', 'story-content', 'entry-content', 'post-content',
            'td-post-content', 'single-post-content', 'body-content', 'content-main'
        ])
        
        if content_divs:
            for div in content_divs:
                paragraphs = div.find_all('p')
                if paragraphs:
                    return ' '.join([p.get_text(strip=True) for p in paragraphs])

        # Fallback to all paragraphs if specific containers not found
        paragraphs = soup.find_all('p')
        if paragraphs:
            return ' '.join([p.get_text(strip=True) for p in paragraphs])
        return None

    def _extract_publish_date(self, soup):
        # Common patterns for publication dates
        date_tags = soup.find_all(['time', 'span', 'div'], class_=[
            'article-date', 'published-date', 'post-date', 'entry-date',
            'td-post-date', 'date', 'timestamp'
        ])
        for tag in date_tags:
            date_str = tag.get('datetime') or tag.get_text(strip=True)
            if date_str:
                try:
                    # Attempt to parse various date formats
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        return datetime.strptime(date_str, '%B %d, %Y %I:%M %p')
                    except ValueError:
                        try:
                            return datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')
                        except ValueError:
                            pass # Try next format
        return None

    def _extract_author(self, soup):
        author_tag = soup.find('meta', attrs={'name': 'author'}) or soup.find('span', class_='author')
        if author_tag:
            return author_tag.get('content', author_tag.get_text(strip=True))
        return 'N/A'

    def collect_news(self):
        collected_articles = []
        for source in self.news_sources:
            logging.info(f"Scraping news from web source: {source['name']} ({source['url']})")
            # For simplicity, this example assumes the 'url' is a direct article link.
            # In a real scenario, you'd need to scrape an index page for multiple article links.
            article = self.scrape_article(
                source['url'],
                source['name'],
                source.get('language', 'en'),
                source.get('category', 'General'),
                source.get('region', 'N/A')
            )
            if article:
                collected_articles.append(article)
            time.sleep(self.config.get("scrape_delay", 2)) # Be polite to websites
        return collected_articles

if __name__ == '__main__':
    # Example Usage (replace with actual config loading)
    sample_config = {
        "web_scrape_sources": [
            {"name": "Example News Site", "url": "https://www.example.com/news/article-1", "language": "en", "category": "Technology", "region": "Global"}
            # Add more specific URLs for testing if needed
        ],
        "scrape_delay": 2
    }
    
    scraper = WebScraper(sample_config)
    articles = scraper.collect_news()
    for article in articles:
        print(f"Title: {article['title']}\nURL: {article['url']}\nSource: {article['source']}\nContent Snippet: {article['content'][:200]}...\n")
