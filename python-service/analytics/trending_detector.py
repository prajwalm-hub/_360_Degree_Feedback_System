import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrendingDetector:
    def __init__(self, time_window_hours=24, min_mentions=5):
        self.time_window_hours = time_window_hours
        self.min_mentions = min_mentions
        self.topic_mentions = defaultdict(lambda: []) # Stores (timestamp, topic_name)
        logging.info(f"TrendingDetector initialized with time window: {time_window_hours} hours, min mentions: {min_mentions}.")

    def add_topics(self, topics_list, timestamp=None):
        """
        Adds topics from new articles/posts to the tracking system.
        topics_list: A list of topic strings.
        timestamp: The datetime object when the topics were observed. Defaults to now.
        """
        if not timestamp:
            timestamp = datetime.now()

        for topic in topics_list:
            self.topic_mentions[topic].append(timestamp)
        logging.debug(f"Added {len(topics_list)} topics at {timestamp}.")

    def detect_trending_topics(self):
        """
        Detects topics that are currently trending based on frequency within a time window.
        Returns a list of dictionaries with 'topic_name' and 'trending_score'.
        """
        trending_topics = []
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=self.time_window_hours)

        for topic, timestamps in self.topic_mentions.items():
            # Filter out old mentions
            recent_mentions = [ts for ts in timestamps if ts > cutoff_time]
            
            # Update the stored mentions to only keep recent ones
            self.topic_mentions[topic] = recent_mentions

            if len(recent_mentions) >= self.min_mentions:
                # A simple trending score could be just the count of recent mentions,
                # or a more complex one considering recency (e.g., exponential decay).
                trending_score = len(recent_mentions)
                trending_topics.append({
                    'topic_name': topic,
                    'trending_score': trending_score,
                    'last_updated': current_time
                })
        
        # Sort by trending score in descending order
        trending_topics.sort(key=lambda x: x['trending_score'], reverse=True)
        logging.info(f"Detected {len(trending_topics)} trending topics.")
        return trending_topics

if __name__ == '__main__':
    detector = TrendingDetector(time_window_hours=1, min_mentions=3)

    # Simulate topic additions over time
    now = datetime.now()

    # Topics added recently
    detector.add_topics(["Economy", "Infrastructure"], now - timedelta(minutes=5))
    detector.add_topics(["Economy", "Digital India"], now - timedelta(minutes=10))
    detector.add_topics(["Infrastructure", "Healthcare"], now - timedelta(minutes=15))
    detector.add_topics(["Economy"], now - timedelta(minutes=20))
    detector.add_topics(["Digital India"], now - timedelta(minutes=25))
    detector.add_topics(["Economy"], now - timedelta(minutes=30))
    detector.add_topics(["Healthcare"], now - timedelta(minutes=35))

    # Old topics (should be filtered out by 1-hour window)
    detector.add_topics(["Old Policy"], now - timedelta(hours=2))
    detector.add_topics(["Old Policy"], now - timedelta(hours=2, minutes=30))

    print("--- Initial Trending Topics ---")
    trending = detector.detect_trending_topics()
    for topic in trending:
        print(f"Topic: {topic['topic_name']}, Score: {topic['trending_score']}")

    # Add more mentions to make another topic trend
    detector.add_topics(["Education"], now - timedelta(minutes=1))
    detector.add_topics(["Education"], now - timedelta(minutes=2))
    detector.add_topics(["Education"], now - timedelta(minutes=3))
    detector.add_topics(["Education"], now - timedelta(minutes=4))

    print("\n--- Trending Topics after more additions ---")
    trending = detector.detect_trending_topics()
    for topic in trending:
        print(f"Topic: {topic['topic_name']}, Score: {topic['trending_score']}")

    # Simulate time passing (e.g., 1 hour and 1 minute later)
    print("\n--- Trending Topics after time passes (old topics should disappear) ---")
    # To simulate, we'd re-initialize or manually clear old data.
    # For this example, we'll just call detect_trending_topics again,
    # which will internally filter based on the current `datetime.now()`.
    # If `now` was fixed, we'd need to advance it.
    # Let's re-run with a new 'now' to show filtering.
    detector_after_time = TrendingDetector(time_window_hours=1, min_mentions=3)
    detector_after_time.add_topics(["Economy", "Infrastructure"], now - timedelta(minutes=5))
    detector_after_time.add_topics(["Economy", "Digital India"], now - timedelta(minutes=10))
    detector_after_time.add_topics(["Infrastructure", "Healthcare"], now - timedelta(minutes=15))
    detector_after_time.add_topics(["Economy"], now - timedelta(minutes=20))
    detector_after_time.add_topics(["Digital India"], now - timedelta(minutes=25))
    detector_after_time.add_topics(["Economy"], now - timedelta(minutes=30))
    detector_after_time.add_topics(["Healthcare"], now - timedelta(minutes=35))
    detector_after_time.add_topics(["Education"], now - timedelta(minutes=1))
    detector_after_time.add_topics(["Education"], now - timedelta(minutes=2))
    detector_after_time.add_topics(["Education"], now - timedelta(minutes=3))
    detector_after_time.add_topics(["Education"], now - timedelta(minutes=4))

    # Now, if we call detect_trending_topics, it will use the current `datetime.now()`
    # which is effectively "later" than the `now` variable used above.
    # This will naturally filter out topics that are now older than 1 hour.
    trending_after_time = detector_after_time.detect_trending_topics()
    for topic in trending_after_time:
        print(f"Topic: {topic['topic_name']}, Score: {topic['trending_score']}")
