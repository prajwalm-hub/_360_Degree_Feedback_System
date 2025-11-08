from transformers import pipeline
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging

# Ensure NLTK data is available (run this once if not already downloaded)
# import nltk
# nltk.download('vader_lexicon')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SentimentAnalyzer:
    def __init__(self):
        # Initialize Hugging Face pipeline for multilingual sentiment analysis
        # Using a general BERT-based model for sentiment.
        # For more specific emotion detection, a different model might be needed.
        try:
            self.hf_sentiment_pipeline = pipeline('sentiment-analysis', model='nlptown/bert-base-multilingual-uncased-sentiment')
            logging.info("Hugging Face multilingual sentiment pipeline initialized.")
        except Exception as e:
            self.hf_sentiment_pipeline = None
            logging.error(f"Could not load Hugging Face sentiment model: {e}. HF sentiment analysis will be skipped.")

        # Initialize NLTK VADER for English-specific sentiment (lexicon-based)
        self.vader_analyzer = SentimentIntensityAnalyzer()
        logging.info("NLTK VADER SentimentIntensityAnalyzer initialized.")

    def analyze_sentiment(self, text, language='en'):
        if not text or not isinstance(text, str):
            return {"sentiment": "neutral", "score": 0.0, "emotions": {}}

        sentiment_result = {"sentiment": "neutral", "score": 0.0, "emotions": {}}

        if language == 'en':
            # Use VADER for English for a quick, lexicon-based analysis
            vs = self.vader_analyzer.polarity_scores(text)
            if vs['compound'] >= 0.05:
                sentiment_result['sentiment'] = 'positive'
            elif vs['compound'] <= -0.05:
                sentiment_result['sentiment'] = 'negative'
            else:
                sentiment_result['sentiment'] = 'neutral'
            sentiment_result['score'] = vs['compound']
            # VADER doesn't directly provide emotions, so this remains empty or can be extended
            sentiment_result['emotions'] = {
                'positive': vs['pos'],
                'negative': vs['neg'],
                'neutral': vs['neu']
            }
            logging.debug(f"VADER sentiment for English text: {sentiment_result}")
        
        if self.hf_sentiment_pipeline:
            try:
                # Use Hugging Face for multilingual sentiment and potentially more nuanced results
                # The 'nlptown/bert-base-multilingual-uncased-sentiment' model outputs 5 labels:
                # '1 star' (very negative) to '5 stars' (very positive)
                hf_result = self.hf_sentiment_pipeline(text)
                label = hf_result[0]['label']
                score = hf_result[0]['score']

                # Map 5-star labels to positive/negative/neutral
                if '5 stars' in label or '4 stars' in label:
                    sentiment_result['sentiment'] = 'positive'
                elif '1 star' in label or '2 stars' in label:
                    sentiment_result['sentiment'] = 'negative'
                else:
                    sentiment_result['sentiment'] = 'neutral'
                
                # Adjust score to be between -1 and 1 for consistency
                # 1 star -> -1, 2 stars -> -0.5, 3 stars -> 0, 4 stars -> 0.5, 5 stars -> 1
                star_mapping = {'1 star': -1.0, '2 stars': -0.5, '3 stars': 0.0, '4 stars': 0.5, '5 stars': 1.0}
                sentiment_result['score'] = star_mapping.get(label, 0.0) * score # Scale by confidence

                # Emotion detection is not directly provided by this model.
                # For emotion detection (Joy, Anger, Fear, etc.), a dedicated emotion classification model is needed.
                # Placeholder for emotion detection if a suitable model is integrated later.
                # For now, we can infer basic emotions from sentiment.
                if sentiment_result['sentiment'] == 'positive':
                    sentiment_result['emotions']['joy'] = score
                elif sentiment_result['sentiment'] == 'negative':
                    sentiment_result['emotions']['anger'] = score # Simplified
                
                logging.debug(f"HF sentiment for {language} text: {sentiment_result}")

            except Exception as e:
                logging.error(f"Error during Hugging Face sentiment analysis for {language} text (first 50 chars: '{text[:50]}...'): {e}")
        
        # If HF pipeline failed or not available, and it's not English, we might return a default or try another method.
        # For now, if HF fails for non-English, it will return the default neutral.
        return sentiment_result

if __name__ == '__main__':
    analyzer = SentimentAnalyzer()
    
    texts_to_analyze = [
        ("The government's new policy is excellent and will benefit many citizens.", "en"),
        ("This is a terrible decision, I am very angry about it.", "en"),
        ("The news report was factual and presented both sides.", "en"),
        ("यह सरकार की एक शानदार पहल है।", "hi"), # This is a fantastic initiative of the government.
        ("यह बहुत बुरा फैसला है, मैं इससे बहुत नाराज़ हूँ।", "hi"), # This is a very bad decision, I am very angry about it.
        ("सरकार की नई नीति तटस्थ है।", "hi"), # The government's new policy is neutral.
        ("The new infrastructure project is a huge success, bringing joy to the community.", "en"),
        ("The recent economic downturn has caused widespread fear and sadness.", "en")
    ]

    for text, lang in texts_to_analyze:
        result = analyzer.analyze_sentiment(text, lang)
        print(f"Original ({lang}): '{text}'\nSentiment: {result['sentiment']}, Score: {result['score']:.2f}, Emotions: {result['emotions']}\n---")
