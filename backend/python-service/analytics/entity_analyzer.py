import pandas as pd
from collections import defaultdict
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EntityAnalyzer:
    def __init__(self):
        self.entity_data = defaultdict(lambda: {
            'mentions_count': 0,
            'positive_sentiment_count': 0,
            'negative_sentiment_count': 0,
            'neutral_sentiment_count': 0,
            'last_mentioned': None,
            'type': 'UNKNOWN' # Will try to infer from NER labels
        })
        logging.info("EntityAnalyzer initialized.")

    def process_entities(self, entities, sentiment_result, timestamp=None):
        """
        Processes extracted entities and their associated sentiment.
        
        Args:
            entities (list): List of entity dictionaries (e.g., from NER output).
            sentiment_result (dict): Dictionary containing 'sentiment' and 'score'.
            timestamp (datetime): The datetime when the entities were extracted. Defaults to now.
        """
        if not timestamp:
            timestamp = datetime.now()

        if not entities:
            return

        sentiment = sentiment_result.get('sentiment', 'neutral')

        for entity in entities:
            entity_text = entity['text'].strip()
            entity_label = entity['label'].strip()

            self.entity_data[entity_text]['mentions_count'] += 1
            self.entity_data[entity_text]['last_mentioned'] = timestamp
            
            # Update sentiment counts
            if sentiment == 'positive':
                self.entity_data[entity_text]['positive_sentiment_count'] += 1
            elif sentiment == 'negative':
                self.entity_data[entity_text]['negative_sentiment_count'] += 1
            else:
                self.entity_data[entity_text]['neutral_sentiment_count'] += 1
            
            # Try to infer entity type if not already set or if UNKNOWN
            if self.entity_data[entity_text]['type'] == 'UNKNOWN' and entity_label:
                self.entity_data[entity_text]['type'] = self._map_ner_label_to_type(entity_label)
        
        logging.debug(f"Processed {len(entities)} entities with sentiment '{sentiment}'.")

    def _map_ner_label_to_type(self, label):
        # Map common spaCy NER labels to our defined types
        if label in ['PERSON', 'PER']:
            return 'Person'
        elif label in ['ORG', 'ORGANIZATION']:
            return 'Organization'
        elif label in ['GPE', 'LOC', 'LOCATION']:
            return 'Location'
        elif label in ['EVENT']:
            return 'Event'
        elif label in ['NORP', 'FAC', 'LAW', 'PRODUCT', 'WORK_OF_ART', 'LANGUAGE', 'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
            return label # Keep specific if useful, or generalize further
        return 'Other'

    def get_entity_mentions(self):
        """
        Returns a list of all tracked entities with their aggregated data.
        """
        results = []
        for name, data in self.entity_data.items():
            results.append({
                'name': name,
                'type': data['type'],
                'mentions_count': data['mentions_count'],
                'positive_sentiment_count': data['positive_sentiment_count'],
                'negative_sentiment_count': data['negative_sentiment_count'],
                'neutral_sentiment_count': data['neutral_sentiment_count'],
                'last_mentioned': data['last_mentioned']
            })
        
        # Sort by mentions count descending
        results.sort(key=lambda x: x['mentions_count'], reverse=True)
        logging.info(f"Retrieved {len(results)} unique entities.")
        return results

if __name__ == '__main__':
    analyzer = EntityAnalyzer()

    # Sample NER output and sentiment results
    sample_data = [
        {
            'entities': [{'text': 'Narendra Modi', 'label': 'PERSON'}, {'text': 'India', 'label': 'GPE'}],
            'sentiment': {'sentiment': 'positive', 'score': 0.8},
            'timestamp': datetime(2025, 10, 15, 10, 0, 0)
        },
        {
            'entities': [{'text': 'Ministry of Finance', 'label': 'ORG'}, {'text': 'New Delhi', 'label': 'GPE'}],
            'sentiment': {'sentiment': 'neutral', 'score': 0.1},
            'timestamp': datetime(2025, 10, 15, 10, 30, 0)
        },
        {
            'entities': [{'text': 'Narendra Modi', 'label': 'PERSON'}, {'text': 'Government of India', 'label': 'ORG'}],
            'sentiment': {'sentiment': 'positive', 'score': 0.9},
            'timestamp': datetime(2025, 10, 15, 11, 0, 0)
        },
        {
            'entities': [{'text': 'Opposition Party', 'label': 'ORG'}],
            'sentiment': {'sentiment': 'negative', 'score': -0.7},
            'timestamp': datetime(2025, 10, 15, 11, 15, 0)
        },
        {
            'entities': [{'text': 'India', 'label': 'GPE'}, {'text': 'Economy', 'label': 'MISC'}], # MISC for a general topic
            'sentiment': {'sentiment': 'positive', 'score': 0.6},
            'timestamp': datetime(2025, 10, 15, 12, 0, 0)
        },
    ]

    for data in sample_data:
        analyzer.process_entities(data['entities'], data['sentiment'], data['timestamp'])

    print("--- Entity Mentions and Sentiment ---")
    entities_report = analyzer.get_entity_mentions()
    for entity in entities_report:
        print(f"Entity: {entity['name']} (Type: {entity['type']})")
        print(f"  Mentions: {entity['mentions_count']}")
        print(f"  Positive: {entity['positive_sentiment_count']}, Negative: {entity['negative_sentiment_count']}, Neutral: {entity['neutral_sentiment_count']}")
        print(f"  Last Mentioned: {entity['last_mentioned']}")
        print("-" * 20)
