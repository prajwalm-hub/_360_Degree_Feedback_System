import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentimentAggregator:
    def __init__(self):
        logging.info("SentimentAggregator initialized.")

    def aggregate_sentiment(self, articles, videos, social_media_posts):
        """
        Aggregates sentiment data from various sources.
        
        Args:
            articles (list): List of article dictionaries.
            videos (list): List of video dictionaries.
            social_media_posts (list): List of social media post dictionaries.
            
        Returns:
            pd.DataFrame: Aggregated sentiment data.
        """
        all_data = []

        # Process articles
        for article in articles:
            if article.get('sentiment') and article['sentiment'].get('sentiment'):
                all_data.append({
                    'date': article['publish_date'].date() if article.get('publish_date') else datetime.now().date(),
                    'source_type': 'article',
                    'category': article.get('category', 'General'),
                    'region': article.get('region', 'N/A'),
                    'language': article.get('language', 'en'),
                    'sentiment': article['sentiment']['sentiment'],
                    'score': article['sentiment']['score'],
                    'is_government_related': article.get('is_government_related', False),
                    'departments': article.get('departments', []),
                    'government_entity': article.get('government_entity', ''),
                    'government_scheme': article.get('government_scheme', ''),
                    'policy_type': article.get('policy_type', '')
                })

        # Process videos
        for video in videos:
            if video.get('sentiment') and video['sentiment'].get('sentiment'):
                all_data.append({
                    'date': video['upload_date'].date() if video.get('upload_date') else datetime.now().date(),
                    'source_type': 'video',
                    'category': video.get('category', 'Government'),
                    'region': video.get('region', 'India'),
                    'language': video.get('language', 'en'),
                    'sentiment': video['sentiment']['sentiment'],
                    'score': video['sentiment']['score']
                })

        # Process social media posts
        for post in social_media_posts:
            if post.get('sentiment') and post['sentiment'].get('sentiment'):
                all_data.append({
                    'date': post['post_date'].date() if post.get('post_date') else datetime.now().date(),
                    'source_type': 'social_media',
                    'category': 'Social Media', # Social media posts might not have explicit categories
                    'region': 'N/A', # Region might be harder to determine for social media
                    'language': post.get('language', 'en'),
                    'sentiment': post['sentiment']['sentiment'],
                    'score': post['sentiment']['score']
                })

        if not all_data:
            logging.info("No sentiment data to aggregate.")
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        
        # Convert sentiment to numerical for aggregation
        sentiment_mapping = {'positive': 1, 'neutral': 0, 'negative': -1}
        df['sentiment_value'] = df['sentiment'].map(sentiment_mapping)

        # Aggregate by date, category, region, language
        aggregated_df = df.groupby(['date', 'source_type', 'category', 'region', 'language']).agg(
            positive_count=('sentiment', lambda x: (x == 'positive').sum()),
            negative_count=('sentiment', lambda x: (x == 'negative').sum()),
            neutral_count=('sentiment', lambda x: (x == 'neutral').sum()),
            avg_sentiment_score=('score', 'mean'),
            total_count=('sentiment', 'count'),
            government_related_count=('is_government_related', lambda x: x.sum() if x.dtype == bool else 0)
        ).reset_index()

        logging.info(f"Aggregated sentiment data for {len(aggregated_df)} entries.")
        return aggregated_df

if __name__ == '__main__':
    aggregator = SentimentAggregator()

    # Sample data
    sample_articles = [
        {'publish_date': datetime(2025, 10, 15), 'category': 'Economy', 'region': 'North', 'language': 'en', 'sentiment': {'sentiment': 'positive', 'score': 0.8}},
        {'publish_date': datetime(2025, 10, 15), 'category': 'Economy', 'region': 'North', 'language': 'en', 'sentiment': {'sentiment': 'negative', 'score': -0.6}},
        {'publish_date': datetime(2025, 10, 15), 'category': 'Politics', 'region': 'South', 'language': 'hi', 'sentiment': {'sentiment': 'neutral', 'score': 0.1}},
        {'publish_date': datetime(2025, 10, 14), 'category': 'Economy', 'region': 'North', 'language': 'en', 'sentiment': {'sentiment': 'positive', 'score': 0.9}},
    ]
    sample_videos = [
        {'upload_date': datetime(2025, 10, 15), 'category': 'Government', 'region': 'India', 'language': 'en', 'sentiment': {'sentiment': 'positive', 'score': 0.7}},
        {'upload_date': datetime(2025, 10, 15), 'category': 'Government', 'region': 'India', 'language': 'hi', 'sentiment': {'sentiment': 'negative', 'score': -0.5}},
    ]
    sample_social_media_posts = [
        {'post_date': datetime(2025, 10, 15), 'language': 'en', 'sentiment': {'sentiment': 'positive', 'score': 0.6}},
        {'post_date': datetime(2025, 10, 15), 'language': 'en', 'sentiment': {'sentiment': 'neutral', 'score': 0.0}},
    ]

    aggregated_results = aggregator.aggregate_sentiment(sample_articles, sample_videos, sample_social_media_posts)
    print("\nAggregated Sentiment Results:")
    print(aggregated_results)
