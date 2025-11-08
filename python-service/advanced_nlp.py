"""
Advanced NLP pipeline using Hugging Face transformers.
Provides high-accuracy AI models for sentiment analysis, summarization, NER, and government classification.
"""

import asyncio
import logging
import torch
from typing import Dict, List, Optional, Any, Tuple
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    BartForConditionalGeneration,
    BertTokenizer,
    BertForSequenceClassification
)
import numpy as np

from config.realtime_config import realtime_config

logger = logging.getLogger(__name__)

class AdvancedNLPProcessor:
    """Advanced NLP processor using Hugging Face transformers"""

    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.models = {}
        self.pipelines = {}
        self._load_models()

    def _load_models(self):
        """Load all AI models"""
        try:
            logger.info("Loading advanced NLP models...")

            # Sentiment Analysis Pipeline
            self.pipelines['sentiment'] = pipeline(
                "sentiment-analysis",
                model=realtime_config.model_configs['sentiment']['model_name'],
                device=self.device,
                top_k=None,
                truncation=True,
                max_length=realtime_config.ai_max_length
            )

            # Summarization Pipeline
            self.pipelines['summarization'] = pipeline(
                "summarization",
                model=realtime_config.model_configs['summarization']['model_name'],
                device=self.device,
                truncation=True,
                max_length=realtime_config.ai_max_length
            )

            # NER Pipeline
            self.pipelines['ner'] = pipeline(
                "ner",
                model=realtime_config.model_configs['ner']['model_name'],
                device=self.device,
                aggregation_strategy="simple"
            )

            # Government Classifier (will be fine-tuned)
            self._load_government_classifier()

            logger.info("All NLP models loaded successfully")

        except Exception as e:
            logger.error(f"Error loading NLP models: {e}")
            raise

    def _load_government_classifier(self):
        """Load or create government classifier"""
        try:
            # For now, use a basic BERT model - in production, this would be fine-tuned
            model_name = realtime_config.model_configs['government_classifier']['model_name']

            self.models['government_tokenizer'] = AutoTokenizer.from_pretrained(model_name)
            self.models['government_model'] = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=2  # government_related, not_government_related
            )

            # Move to GPU if available
            if self.device >= 0:
                self.models['government_model'] = self.models['government_model'].to(self.device)

        except Exception as e:
            logger.warning(f"Could not load government classifier: {e}")
            # Fallback to keyword-based classification
            self.models['government_classifier'] = None

    async def process_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of articles through the NLP pipeline"""
        try:
            processed_articles = []

            # Process in batches for efficiency
            batch_size = realtime_config.ai_batch_size

            for i in range(0, len(articles), batch_size):
                batch = articles[i:i + batch_size]
                processed_batch = await self._process_batch_async(batch)
                processed_articles.extend(processed_batch)

            return processed_articles

        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            return articles  # Return original articles if processing fails

    async def _process_batch_async(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch asynchronously"""
        # Run CPU-intensive tasks in thread pool
        loop = asyncio.get_event_loop()

        tasks = []
        for article in batch:
            tasks.append(loop.run_in_executor(None, self._process_single_article, article))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_batch = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing article {i}: {result}")
                processed_batch.append(batch[i])  # Return original
            else:
                processed_batch.append(result)

        return processed_batch

    def _process_single_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single article through all NLP steps"""
        try:
            text = article.get('content', '') or article.get('title', '')
            if not text:
                return article

            # 1. Sentiment Analysis
            sentiment_result = self._analyze_sentiment(text)

            # 2. Summarization
            summary = self._generate_summary(text)

            # 3. Named Entity Recognition
            entities = self._extract_entities(text)

            # 4. Government Classification
            is_government, gov_confidence = self._classify_government_related(text)

            # 5. Keyword Extraction (simplified)
            keywords = self._extract_keywords(text)

            # Update article with AI results
            article.update({
                'sentiment': sentiment_result,
                'summary': summary,
                'entities': entities,
                'is_government_related': is_government,
                'government_confidence': gov_confidence,
                'keywords': keywords,
                'ai_processed': True,
                'ai_confidence_score': min(sentiment_result.get('confidence', 0),
                                         gov_confidence) if gov_confidence else sentiment_result.get('confidence', 0)
            })

            return article

        except Exception as e:
            logger.error(f"Error processing single article: {e}")
            return article

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using RoBERTa model"""
        try:
            if len(text.strip()) < 10:
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.5,
                    'scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
                }

            results = self.pipelines['sentiment'](text)

            if not results:
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.5,
                    'scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
                }

            # Handle nested list structure (e.g., [[{...}, {...}, {...}]])
            if isinstance(results, list) and len(results) == 1 and isinstance(results[0], list):
                results = results[0]

            # Results should be a list of dicts with 'label' and 'score' keys
            if not isinstance(results, list) or not all(isinstance(r, dict) for r in results):
                logger.error(f"Unexpected sentiment results format: {type(results)}, value: {results}")
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.5,
                    'scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
                }

            # Map LABEL_0, LABEL_1, LABEL_2 to sentiment labels
            label_mapping = {
                'label_0': 'negative',
                'label_1': 'neutral',
                'label_2': 'positive'
            }

            # Get the result with highest score
            result = results[0]
            raw_label = result['label'].lower()
            sentiment = label_mapping.get(raw_label, raw_label)
            confidence = result['score']

            # Convert to our format with mapped labels
            scores = {}
            for res in results:
                raw_label = res['label'].lower()
                mapped_label = label_mapping.get(raw_label, raw_label)
                scores[mapped_label] = res['score']

            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': scores
            }

        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
            }

    def _generate_summary(self, text: str) -> str:
        """Generate summary using BART model"""
        try:
            if len(text.strip()) < 50:
                return text[:200] + "..." if len(text) > 200 else text

            config = realtime_config.model_configs['summarization']
            summary = self.pipelines['summarization'](
                text,
                max_length=config['max_length'],
                min_length=config['min_length'],
                do_sample=False
            )[0]['summary_text']

            return summary

        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return text[:300] + "..." if len(text) > 300 else text

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using BERT NER"""
        try:
            if len(text.strip()) < 20:
                return []

            entities = self.pipelines['ner'](text)

            # Format entities
            formatted_entities = []
            for entity in entities:
                formatted_entities.append({
                    'entity': entity['word'],
                    'label': entity['entity_group'],
                    'confidence': entity['score'],
                    'start': entity['start'],
                    'end': entity['end']
                })

            return formatted_entities

        except Exception as e:
            logger.error(f"NER error: {e}")
            return []

    def _classify_government_related(self, text: str) -> Tuple[bool, Optional[float]]:
        """Classify if text is government-related using BERT"""
        try:
            if self.models.get('government_classifier') is None:
                # Fallback to keyword-based classification
                return self._keyword_based_government_classification(text)

            # Use BERT model
            tokenizer = self.models['government_tokenizer']
            model = self.models['government_model']

            inputs = tokenizer(
                text[:512],  # Limit input length
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )

            if self.device >= 0:
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()

            is_government = predicted_class == 1  # Assuming 1 is government_related
            return is_government, confidence

        except Exception as e:
            logger.error(f"Government classification error: {e}")
            return self._keyword_based_government_classification(text)

    def _keyword_based_government_classification(self, text: str) -> Tuple[bool, Optional[float]]:
        """Fallback keyword-based government classification"""
        government_keywords = [
            'government', 'minister', 'ministry', 'parliament', 'policy', 'budget',
            'cabinet', 'bjp', 'congress', 'modi', 'pib', 'press information bureau',
            'supreme court', 'high court', 'legislation', 'bill', 'act'
        ]

        text_lower = text.lower()
        matches = sum(1 for keyword in government_keywords if keyword in text_lower)

        # Simple scoring based on keyword matches
        if matches >= 3:
            confidence = min(0.9, 0.5 + (matches * 0.1))
            return True, confidence
        elif matches >= 1:
            confidence = 0.6 + (matches * 0.1)
            return True, confidence
        else:
            return False, 0.8  # High confidence for non-government

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simplified implementation)"""
        try:
            # Simple keyword extraction based on frequency and length
            words = text.lower().split()
            words = [word.strip('.,!?()[]{}') for word in words if len(word) > 3]

            # Count frequency
            from collections import Counter
            word_counts = Counter(words)

            # Get top keywords
            keywords = [word for word, count in word_counts.most_common(10)]
            return keywords

        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return []

    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'device': 'cuda' if self.device >= 0 else 'cpu',
            'models': {
                'sentiment': realtime_config.model_configs['sentiment']['model_name'],
                'summarization': realtime_config.model_configs['summarization']['model_name'],
                'ner': realtime_config.model_configs['ner']['model_name'],
                'government_classifier': realtime_config.model_configs['government_classifier']['model_name']
            },
            'batch_size': realtime_config.ai_batch_size,
            'max_length': realtime_config.ai_max_length,
            'confidence_threshold': realtime_config.ai_confidence_threshold
        }

# Global instance
nlp_processor = AdvancedNLPProcessor()

async def process_articles_batch(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to process a batch of articles"""
    return await nlp_processor.process_batch(articles)

if __name__ == "__main__":
    # Test the NLP processor
    async def test():
        test_articles = [
            {
                'title': 'Government announces new policy',
                'content': 'The Ministry of Finance has announced a new economic policy that will help boost the economy. Prime Minister Narendra Modi stated that this policy will create jobs and improve infrastructure.',
                'url': 'https://example.com/gov-policy'
            }
        ]

        processed = await process_articles_batch(test_articles)
        print("Processed article:", processed[0])

    asyncio.run(test())
