import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ReportGenerator:
    def __init__(self):
        logging.info("ReportGenerator initialized.")

    def generate_sentiment_report(self, aggregated_sentiment_df):
        """
        Generates a summary report of sentiment distribution.
        
        Args:
            aggregated_sentiment_df (pd.DataFrame): DataFrame from SentimentAggregator.
            
        Returns:
            dict: A dictionary containing various sentiment statistics.
        """
        if aggregated_sentiment_df.empty:
            logging.warning("No aggregated sentiment data to generate report.")
            return {"message": "No data available for sentiment report."}

        total_items = aggregated_sentiment_df['total_count'].sum()
        total_positive = aggregated_sentiment_df['positive_count'].sum()
        total_negative = aggregated_sentiment_df['negative_count'].sum()
        total_neutral = aggregated_sentiment_df['neutral_count'].sum()

        sentiment_distribution = {
            'positive_percentage': (total_positive / total_items * 100) if total_items > 0 else 0,
            'negative_percentage': (total_negative / total_items * 100) if total_items > 0 else 0,
            'neutral_percentage': (total_neutral / total_items * 100) if total_items > 0 else 0,
        }

        # Sentiment by category
        sentiment_by_category = aggregated_sentiment_df.groupby('category').agg(
            total_count=('total_count', 'sum'),
            positive_count=('positive_count', 'sum'),
            negative_count=('negative_count', 'sum'),
            neutral_count=('neutral_count', 'sum'),
            avg_sentiment_score=('avg_sentiment_score', 'mean')
        ).to_dict('index')

        # Sentiment by region
        sentiment_by_region = aggregated_sentiment_df.groupby('region').agg(
            total_count=('total_count', 'sum'),
            positive_count=('positive_count', 'sum'),
            negative_count=('negative_count', 'sum'),
            neutral_count=('neutral_count', 'sum'),
            avg_sentiment_score=('avg_sentiment_score', 'mean')
        ).to_dict('index')

        report = {
            "report_date": datetime.now().isoformat(),
            "total_items_analyzed": int(total_items),
            "overall_sentiment_distribution": sentiment_distribution,
            "sentiment_by_category": sentiment_by_category,
            "sentiment_by_region": sentiment_by_region,
            "raw_aggregated_data_preview": aggregated_sentiment_df.head().to_dict('records')
        }
        logging.info("Generated sentiment report.")
        return report

    def generate_entity_report(self, entity_mentions_list):
        """
        Generates a report on named entity mentions and their associated sentiment.
        
        Args:
            entity_mentions_list (list): List of entity dictionaries from EntityAnalyzer.
            
        Returns:
            dict: A dictionary containing entity statistics.
        """
        if not entity_mentions_list:
            logging.warning("No entity data to generate report.")
            return {"message": "No data available for entity report."}

        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame(entity_mentions_list)

        # Top entities by mentions
        top_entities = df.sort_values(by='mentions_count', ascending=False).head(10).to_dict('records')

        # Sentiment distribution for top entities
        entity_sentiment_summary = []
        for entity in top_entities:
            total_mentions = entity['mentions_count']
            positive_percent = (entity['positive_sentiment_count'] / total_mentions * 100) if total_mentions > 0 else 0
            negative_percent = (entity['negative_sentiment_count'] / total_mentions * 100) if total_mentions > 0 else 0
            neutral_percent = (entity['neutral_sentiment_count'] / total_mentions * 100) if total_mentions > 0 else 0
            entity_sentiment_summary.append({
                'name': entity['name'],
                'type': entity['type'],
                'mentions_count': total_mentions,
                'sentiment_distribution': {
                    'positive': positive_percent,
                    'negative': negative_percent,
                    'neutral': neutral_percent
                }
            })

        report = {
            "report_date": datetime.now().isoformat(),
            "total_unique_entities": len(entity_mentions_list),
            "top_10_entities_by_mentions": top_entities,
            "entity_sentiment_summary": entity_sentiment_summary
        }
        logging.info("Generated entity report.")
        return report

    def generate_topic_report(self, trending_topics_list):
        """
        Generates a report on trending topics.
        
        Args:
            trending_topics_list (list): List of trending topic dictionaries from TrendingDetector.
            
        Returns:
            dict: A dictionary containing trending topic statistics.
        """
        if not trending_topics_list:
            logging.warning("No trending topic data to generate report.")
            return {"message": "No data available for topic report."}

        report = {
            "report_date": datetime.now().isoformat(),
            "total_trending_topics": len(trending_topics_list),
            "trending_topics": trending_topics_list
        }
        logging.info("Generated topic report.")
        return report

    def generate_comprehensive_feedback_report(self, aggregated_sentiment_df, entity_mentions_list, trending_topics_list):
        """
        Generates a comprehensive 360-degree feedback report.
        """
        sentiment_report = self.generate_sentiment_report(aggregated_sentiment_df)
        entity_report = self.generate_entity_report(entity_mentions_list)
        topic_report = self.generate_topic_report(trending_topics_list)

        comprehensive_report = {
            "title": "360-Degree Feedback Report - Government of India News Monitoring",
            "generated_date": datetime.now().isoformat(),
            "sections": {
                "overall_sentiment_analysis": sentiment_report,
                "key_entity_tracking": entity_report,
                "trending_topics_analysis": topic_report,
                # Add more sections as needed, e.g., geographic analysis, specific policy feedback
            },
            "summary": "This report provides a comprehensive overview of public perception, sentiment, and key discussions related to government initiatives across various media sources."
        }
        logging.info("Generated comprehensive feedback report.")
        return comprehensive_report

if __name__ == '__main__':
    generator = ReportGenerator()

    # Sample aggregated sentiment data (from SentimentAggregator)
    sample_aggregated_sentiment_df = pd.DataFrame([
        {'date': datetime(2025, 10, 15).date(), 'source_type': 'article', 'category': 'Economy', 'region': 'North', 'language': 'en', 'positive_count': 5, 'negative_count': 2, 'neutral_count': 3, 'avg_sentiment_score': 0.3, 'total_count': 10},
        {'date': datetime(2025, 10, 15).date(), 'source_type': 'video', 'category': 'Government', 'region': 'India', 'language': 'en', 'positive_count': 3, 'negative_count': 1, 'neutral_count': 1, 'avg_sentiment_score': 0.5, 'total_count': 5},
        {'date': datetime(2025, 10, 14).date(), 'source_type': 'article', 'category': 'Politics', 'region': 'South', 'language': 'hi', 'positive_count': 2, 'negative_count': 4, 'neutral_count': 2, 'avg_sentiment_score': -0.2, 'total_count': 8},
    ])

    # Sample entity mentions list (from EntityAnalyzer)
    sample_entity_mentions_list = [
        {'name': 'Narendra Modi', 'type': 'Person', 'mentions_count': 15, 'positive_sentiment_count': 10, 'negative_sentiment_count': 2, 'neutral_sentiment_count': 3, 'last_mentioned': datetime(2025, 10, 15, 12, 0, 0)},
        {'name': 'Ministry of Finance', 'type': 'Organization', 'mentions_count': 8, 'positive_sentiment_count': 3, 'negative_sentiment_count': 1, 'neutral_sentiment_count': 4, 'last_mentioned': datetime(2025, 10, 15, 11, 30, 0)},
        {'name': 'New Delhi', 'type': 'Location', 'mentions_count': 12, 'positive_sentiment_count': 6, 'negative_sentiment_count': 3, 'neutral_sentiment_count': 3, 'last_mentioned': datetime(2025, 10, 15, 10, 0, 0)},
        {'name': 'Indian Economy', 'type': 'Other', 'mentions_count': 20, 'positive_sentiment_count': 12, 'negative_sentiment_count': 5, 'neutral_sentiment_count': 3, 'last_mentioned': datetime(2025, 10, 15, 13, 0, 0)},
    ]

    # Sample trending topics list (from TrendingDetector)
    sample_trending_topics_list = [
        {'topic_name': 'Economy', 'trending_score': 10, 'last_updated': datetime(2025, 10, 15, 13, 0, 0)},
        {'topic_name': 'Infrastructure', 'trending_score': 7, 'last_updated': datetime(2025, 10, 15, 12, 45, 0)},
        {'topic_name': 'Digital India', 'trending_score': 5, 'last_updated': datetime(2025, 10, 15, 12, 30, 0)},
    ]

    print("--- Generating Sentiment Report ---")
    sentiment_report = generator.generate_sentiment_report(sample_aggregated_sentiment_df)
    print(sentiment_report)

    print("\n--- Generating Entity Report ---")
    entity_report = generator.generate_entity_report(sample_entity_mentions_list)
    print(entity_report)

    print("\n--- Generating Topic Report ---")
    topic_report = generator.generate_topic_report(sample_trending_topics_list)
    print(topic_report)

    print("\n--- Generating Comprehensive Feedback Report ---")
    comprehensive_report = generator.generate_comprehensive_feedback_report(
        sample_aggregated_sentiment_df,
        sample_entity_mentions_list,
        sample_trending_topics_list
    )
    print(comprehensive_report)
