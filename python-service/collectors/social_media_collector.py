import os
import tweepy # For Twitter/X
# import facebook_sdk # Placeholder for Facebook (requires proper SDK setup)
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SocialMediaCollector:
    def __init__(self, config):
        self.config = config
        self.twitter_bearer_token = config.get("twitter_bearer_token")
        self.facebook_app_id = config.get("facebook_app_id")
        self.facebook_app_secret = config.get("facebook_app_secret")
        self.facebook_access_token = config.get("facebook_access_token") # User or Page access token

        self.twitter_client = self._init_twitter_client()
        # self.facebook_graph = self._init_facebook_graph() # Placeholder

    def _init_twitter_client(self):
        if self.twitter_bearer_token:
            try:
                client = tweepy.Client(self.twitter_bearer_token)
                logging.info("Twitter client initialized successfully.")
                return client
            except Exception as e:
                logging.error(f"Error initializing Twitter client: {e}")
        else:
            logging.warning("Twitter Bearer Token not provided. Twitter collection will be skipped.")
        return None

    # def _init_facebook_graph(self):
    #     if self.facebook_access_token:
    #         try:
    #             # This is a placeholder. Actual Facebook SDK setup is more complex.
    #             # Requires 'pip install facebook-sdk' or similar.
    #             graph = facebook_sdk.GraphAPI(self.facebook_access_token)
    #             logging.info("Facebook Graph API initialized successfully.")
    #             return graph
    #         except Exception as e:
    #             logging.error(f"Error initializing Facebook Graph API: {e}")
    #     else:
    #         logging.warning("Facebook Access Token not provided. Facebook collection will be skipped.")
    #     return None

    def collect_twitter_posts(self, query, max_results=10):
        collected_posts = []
        if not self.twitter_client:
            return collected_posts

        logging.info(f"Collecting Twitter posts for query: '{query}'")
        try:
            response = self.twitter_client.search_recent_tweets(query, tweet_fields=["created_at", "author_id", "public_metrics"], max_results=max_results)
            if response.data:
                for tweet in response.data:
                    collected_posts.append({
                        'id': tweet.id,
                        'platform': 'Twitter',
                        'content': tweet.text,
                        'author_id': tweet.author_id,
                        'post_date': tweet.created_at,
                        'likes': tweet.public_metrics.get('like_count', 0),
                        'retweets': tweet.public_metrics.get('retweet_count', 0),
                        'replies': tweet.public_metrics.get('reply_count', 0),
                        'quotes': tweet.public_metrics.get('quote_count', 0),
                        'url': f"https://twitter.com/{tweet.author_id}/status/{tweet.id}", # This author_id needs to be resolved to username
                        'language': 'en', # Twitter API can provide language, but for simplicity, default
                        'sentiment': None
                    })
            logging.info(f"Collected {len(collected_posts)} Twitter posts.")
        except Exception as e:
            logging.error(f"Error collecting Twitter posts for query '{query}': {e}")
        return collected_posts

    # Placeholder for Facebook collection
    def collect_facebook_posts(self, page_id, max_results=10):
        collected_posts = []
        # if not self.facebook_graph:
        #     return collected_posts

        logging.info(f"Collecting Facebook posts for page ID: '{page_id}'")
        try:
            # Example: Fetch posts from a public page
            # posts = self.facebook_graph.get_connections(page_id, 'posts', limit=max_results)
            # for post in posts['data']:
            #     collected_posts.append({
            #         'id': post['id'],
            #         'platform': 'Facebook',
            #         'content': post.get('message', post.get('story', '')),
            #         'account': page_id,
            #         'post_date': datetime.fromisoformat(post['created_time'].replace('Z', '+00:00')),
            #         'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
            #         'shares': post.get('shares', {}).get('count', 0),
            #         'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
            #         'url': f"https://www.facebook.com/{post['id']}",
            #         'language': 'en',
            #         'sentiment': None
            #     })
            logging.warning("Facebook collection is a placeholder and requires proper SDK setup and authentication.")
        except Exception as e:
            logging.error(f"Error collecting Facebook posts for page '{page_id}': {e}")
        return collected_posts

    def collect_social_media(self):
        all_posts = []
        
        # Twitter collection
        twitter_queries = self.config.get("twitter_queries", [])
        for query_info in twitter_queries:
            all_posts.extend(self.collect_twitter_posts(query_info['query'], query_info.get('max_results', 10)))

        # Facebook collection
        facebook_pages = self.config.get("facebook_pages", [])
        for page_info in facebook_pages:
            all_posts.extend(self.collect_facebook_posts(page_info['page_id'], page_info.get('max_results', 10)))

        return all_posts

if __name__ == '__main__':
    # Example Usage (replace with actual config loading and API keys)
    sample_config = {
        "twitter_bearer_token": os.environ.get("TWITTER_BEARER_TOKEN", "YOUR_TWITTER_BEARER_TOKEN"),
        "twitter_queries": [
            {"query": "Government of India", "max_results": 5},
            {"query": "#IndianPolitics", "max_results": 5}
        ],
        "facebook_app_id": os.environ.get("FACEBOOK_APP_ID", "YOUR_FACEBOOK_APP_ID"),
        "facebook_app_secret": os.environ.get("FACEBOOK_APP_SECRET", "YOUR_FACEBOOK_APP_SECRET"),
        "facebook_access_token": os.environ.get("FACEBOOK_ACCESS_TOKEN", "YOUR_FACEBOOK_ACCESS_TOKEN"),
        "facebook_pages": [
            {"page_id": "100064820000000", "max_results": 5} # Example: Government of India official page ID
        ]
    }

    if sample_config["twitter_bearer_token"] == "YOUR_TWITTER_BEARER_TOKEN":
        logging.warning("Please set your TWITTER_BEARER_TOKEN environment variable or update the sample_config.")
    
    if sample_config["facebook_access_token"] == "YOUR_FACEBOOK_ACCESS_TOKEN":
        logging.warning("Please set your FACEBOOK_ACCESS_TOKEN environment variable or update the sample_config.")

    collector = SocialMediaCollector(sample_config)
    social_posts = collector.collect_social_media()
    for post in social_posts:
        print(f"Platform: {post['platform']}\nContent: {post['content'][:100]}...\nLikes: {post.get('likes', 'N/A')}\n")
