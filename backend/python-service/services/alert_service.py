import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AlertService:
    def __init__(self, config):
        self.config = config
        self.alert_thresholds = config.get("alert_thresholds", {})
        self.recent_alerts = {} # Stores {alert_type: last_triggered_time} to prevent spamming
        logging.info("AlertService initialized.")

    def check_for_alerts(self, data_type, data):
        """
        Checks incoming data for conditions that trigger alerts.
        
        Args:
            data_type (str): Type of data (e.g., 'article', 'video', 'social_media').
            data (dict): The processed data item (e.g., an article with sentiment).
            
        Returns:
            list: A list of triggered alerts.
        """
        triggered_alerts = []
        
        if data_type == 'article' or data_type == 'video' or data_type == 'social_media':
            sentiment_info = data.get('sentiment', {})
            sentiment = sentiment_info.get('sentiment')
            score = sentiment_info.get('score', 0.0)
            
            if sentiment == 'negative' and score <= self.alert_thresholds.get('negative_sentiment_score', -0.5):
                alert_content = f"Strong negative sentiment detected in {data_type} '{data.get('title', data.get('id', 'N/A'))}' from {data.get('source', data.get('channel', data.get('platform', 'N/A')))}. Score: {score:.2f}"
                triggered_alerts.append(self._create_alert('Negative Sentiment', 'High', alert_content, data))
            
            # Example: Check for specific keywords in content that might trigger alerts
            alert_keywords = self.alert_thresholds.get('keywords', [])
            content = data.get('content', data.get('description', ''))
            for keyword in alert_keywords:
                if keyword.lower() in content.lower():
                    alert_content = f"Keyword '{keyword}' detected in {data_type} '{data.get('title', data.get('id', 'N/A'))}'."
                    triggered_alerts.append(self._create_alert('Keyword Alert', 'Medium', alert_content, data))

        # Add more alert conditions as needed (e.g., for trending topics, entity mentions)
        
        return triggered_alerts

    def _create_alert(self, alert_type, severity, content, original_data):
        """Helper to create an alert dictionary."""
        alert = {
            'alert_type': alert_type,
            'severity': severity,
            'content': content,
            'threshold_triggered': 'N/A', # This could be more specific
            'created_date': datetime.now(),
            'status': 'new',
            'original_data_id': original_data.get('id'),
            'original_data_type': original_data.get('source_type', 'N/A')
        }
        logging.info(f"Created alert: {alert_type} - {content[:100]}...")
        return alert

    def should_notify(self, alert_type, cooldown_minutes=5):
        """
        Checks if a notification for a given alert type should be sent,
        respecting a cooldown period to prevent spam.
        """
        last_triggered = self.recent_alerts.get(alert_type)
        if last_triggered:
            if (datetime.now() - last_triggered) < timedelta(minutes=cooldown_minutes):
                logging.debug(f"Notification for {alert_type} on cooldown.")
                return False
        self.recent_alerts[alert_type] = datetime.now()
        return True

if __name__ == '__main__':
    sample_config = {
        "alert_thresholds": {
            "negative_sentiment_score": -0.7,
            "keywords": ["scandal", "corruption", "crisis"]
        }
    }
    alert_service = AlertService(sample_config)

    # Sample data for testing
    positive_article = {
        'id': 'art1', 'title': 'New Policy Benefits Farmers', 'source': 'The Hindu',
        'content': 'The government announced a new policy that will greatly benefit farmers.',
        'sentiment': {'sentiment': 'positive', 'score': 0.9}
    }
    negative_article = {
        'id': 'art2', 'title': 'Corruption Scandal Rocks Ministry', 'source': 'NDTV',
        'content': 'A major corruption scandal has been uncovered in the Ministry of X.',
        'sentiment': {'sentiment': 'negative', 'score': -0.8}
    }
    neutral_video = {
        'id': 'vid1', 'title': 'Budget Discussion', 'channel': 'DD News',
        'description': 'A detailed discussion on the annual budget.',
        'sentiment': {'sentiment': 'neutral', 'score': 0.0}
    }
    mild_negative_social = {
        'id': 'sm1', 'content': 'Not happy with the recent decision.', 'platform': 'Twitter',
        'sentiment': {'sentiment': 'negative', 'score': -0.4}
    }
    strong_negative_social = {
        'id': 'sm2', 'content': 'This is an absolute crisis! Government failed.', 'platform': 'Twitter',
        'sentiment': {'sentiment': 'negative', 'score': -0.9}
    }

    print("--- Checking for alerts ---")
    alerts1 = alert_service.check_for_alerts('article', positive_article)
    print(f"Alerts for positive article: {alerts1}")

    alerts2 = alert_service.check_for_alerts('article', negative_article)
    print(f"Alerts for negative article: {alerts2}")

    alerts3 = alert_service.check_for_alerts('video', neutral_video)
    print(f"Alerts for neutral video: {alerts3}")

    alerts4 = alert_service.check_for_alerts('social_media', mild_negative_social)
    print(f"Alerts for mild negative social post: {alerts4}")

    alerts5 = alert_service.check_for_alerts('social_media', strong_negative_social)
    print(f"Alerts for strong negative social post: {alerts5}")

    # Test cooldown
    print("\n--- Testing Cooldown ---")
    alert_type_test = 'Negative Sentiment'
    if alert_service.should_notify(alert_type_test, cooldown_minutes=1):
        print(f"Notification for '{alert_type_test}' should be sent.")
    else:
        print(f"Notification for '{alert_type_test}' is on cooldown.")
    
    # Try again immediately, should be on cooldown
    if alert_service.should_notify(alert_type_test, cooldown_minutes=1):
        print(f"Notification for '{alert_type_test}' should be sent (ERROR: should be on cooldown).")
    else:
        print(f"Notification for '{alert_type_test}' is on cooldown (Correct).")
