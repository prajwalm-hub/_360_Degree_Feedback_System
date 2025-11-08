import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    pipeline, AutoModel
)
from langdetect import detect, DetectorFactory
import numpy as np
import re
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from models.database_models import Article
from models import SentimentLabel, Alert
import sys
import os
sys.path.append(os.path.dirname(__file__))
import config
from nlp_pipeline.government_filter import GovernmentFilter
from nlp_pipeline.department_classifier import DepartmentClassifier
SENTIMENT_MODEL = getattr(config, 'SENTIMENT_MODEL', 'cardiffnlp/twitter-roberta-base-sentiment-latest')
CATEGORY_KEYWORDS = getattr(config, 'CATEGORY_KEYWORDS', {})
GOVERNMENT_KEYWORDS = getattr(config, 'GOVERNMENT_KEYWORDS', [])
NEGATIVE_SENTIMENT_THRESHOLD = getattr(config, 'NEGATIVE_SENTIMENT_THRESHOLD', -0.3)
CRITICAL_SENTIMENT_THRESHOLD = getattr(config, 'CRITICAL_SENTIMENT_THRESHOLD', -0.7)
LANGUAGE_REGION_MAP = getattr(config, 'LANGUAGE_REGION_MAP', {})

# Set seed for consistent language detection
DetectorFactory.seed = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.sentiment_analyzer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.government_filter = GovernmentFilter()
        self.department_classifier = DepartmentClassifier()
        logger.info(f"Using device: {self.device}")
        self._load_models()
    
    def _load_models(self):
        """Load AI/ML models"""
        try:
            # Load sentiment analysis model
            logger.info(f"Loading sentiment model: {SENTIMENT_MODEL}")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=SENTIMENT_MODEL,
                device=0 if torch.cuda.is_available() else -1,
                return_all_scores=True
            )
            logger.info("Sentiment analysis model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            # Fallback to a simpler model
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1,
                    return_all_scores=True
                )
                logger.info("Loaded fallback sentiment model")
            except Exception as fallback_error:
                logger.error(f"Failed to load fallback model: {str(fallback_error)}")
    
    def process_article(self, article: Article) -> Tuple[Article, List[Alert]]:
        """Process article with AI/ML analysis"""
        alerts = []

        try:
            # Detect language if not set or verify existing
            article.language = self._detect_language(article.content, article.language)

            # Set region based on language if not set
            if not article.region and article.language in LANGUAGE_REGION_MAP:
                article.region = LANGUAGE_REGION_MAP[article.language]

            # Translate content if needed (placeholder for now)
            if article.language != 'en':
                article.translated_content = self._translate_content(article.content, article.language)

            # Use translated content for analysis if available
            analysis_text = article.translated_content or article.content

            # Government filtering and classification
            self._classify_government_content(article, analysis_text)

            # Sentiment analysis
            sentiment_result = self._analyze_sentiment(analysis_text)
            article.sentiment = {
                'sentiment': sentiment_result['label'].value.lower(),
                'score': sentiment_result['score'],
                'emotions': {}
            }

            # Extract keywords and entities
            article.keywords = self._extract_keywords(analysis_text)
            article.entities = self._extract_entities(analysis_text)

            # Categorize article
            article.category = self._categorize_article(analysis_text, article.category)

            # Generate summary
            article.summary = self._generate_summary(analysis_text)

            # Check for alerts
            alerts = self._generate_alerts(article)

            logger.info(f"Processed article: {article.title[:50]}... | Sentiment: {article.sentiment['sentiment']} ({article.sentiment['score']:.3f}) | Government: {article.is_government_related}")

        except Exception as e:
            logger.error(f"Error processing article {article.id}: {str(e)}")

        return article, alerts
    
    def _detect_language(self, text: str, current_lang: str = None) -> str:
        """Detect language of the text"""
        try:
            # Clean text for detection
            clean_text = re.sub(r'[^\w\s]', ' ', text[:1000])  # Use first 1000 chars
            
            if len(clean_text.strip()) < 10:
                return current_lang or 'en'
            
            detected = detect(clean_text)
            
            # Validate against supported languages
            supported_langs = ['en', 'hi', 'ta', 'te', 'bn', 'gu', 'kn', 'ml', 'mr', 'pa', 'ur']
            
            if detected in supported_langs:
                return detected
            else:
                # Map some common variations
                lang_mapping = {
                    'ne': 'hi',  # Nepali -> Hindi
                    'or': 'hi',  # Odia -> Hindi
                    'as': 'bn',  # Assamese -> Bengali
                }
                return lang_mapping.get(detected, current_lang or 'en')
                
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return current_lang or 'en'
    
    def _translate_content(self, content: str, source_lang: str) -> str:
        """Translate content to English (placeholder implementation)"""
        # TODO: Implement IndicTrans2 or Google Translate
        # For now, return original content with a note
        if source_lang == 'en':
            return content
        
        # Placeholder: In a real implementation, you would use IndicTrans2 here
        logger.info(f"Translation needed for {source_lang} -> en")
        return f"[Translation from {source_lang}] {content}"
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the text"""
        if not self.sentiment_analyzer:
            return {'score': 0.0, 'label': SentimentLabel.NEUTRAL}
        
        try:
            # Truncate text if too long
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            # Get sentiment scores
            results = self.sentiment_analyzer(text)
            
            # Parse results based on model output format
            if isinstance(results[0], list):
                scores = results[0]
            else:
                scores = results
            
            # Convert to our sentiment labels
            sentiment_map = {}
            for item in scores:
                label = item['label'].lower()
                score = item['score']
                
                # Map different model labels to our standard labels
                if 'pos' in label or 'good' in label or label == 'label_2':
                    sentiment_map['positive'] = score
                elif 'neg' in label or 'bad' in label or label == 'label_0':
                    sentiment_map['negative'] = score
                else:
                    sentiment_map['neutral'] = score
            
            # Determine dominant sentiment
            max_label = max(sentiment_map.keys(), key=lambda k: sentiment_map[k])
            max_score = sentiment_map[max_label]
            
            # Convert to our scale (-1 to 1)
            if max_label == 'positive':
                final_score = max_score
                sentiment_label = SentimentLabel.POSITIVE
            elif max_label == 'negative':
                final_score = -max_score
                sentiment_label = SentimentLabel.NEGATIVE
            else:
                final_score = 0.0
                sentiment_label = SentimentLabel.NEUTRAL
            
            return {
                'score': final_score,
                'label': sentiment_label
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {'score': 0.0, 'label': SentimentLabel.NEUTRAL}
    
    def _extract_keywords(self, text: str) -> str:
        """Extract key terms from the text"""
        try:
            # Simple keyword extraction based on frequency and government relevance
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Filter for government-related keywords
            relevant_keywords = []
            for word in words:
                if word in [kw.lower() for kw in GOVERNMENT_KEYWORDS]:
                    relevant_keywords.append(word)
            
            # Get most frequent keywords
            from collections import Counter
            keyword_counts = Counter(relevant_keywords)
            top_keywords = [kw for kw, count in keyword_counts.most_common(10)]
            
            return ', '.join(top_keywords) if top_keywords else ''
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return ''
    
    def _extract_entities(self, text: str) -> str:
        """Extract named entities (placeholder implementation)"""
        try:
            # Simple entity extraction using regex patterns
            entities = []
            
            # Find person names (basic pattern)
            person_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b'
            persons = re.findall(person_pattern, text)
            entities.extend([f"PERSON:{p}" for p in persons[:5]])
            
            # Find organizations
            org_keywords = ['ministry', 'department', 'commission', 'authority', 'corporation']
            for keyword in org_keywords:
                pattern = rf'\b([A-Z][^.]*{keyword}[^.]*)\b'
                orgs = re.findall(pattern, text, re.IGNORECASE)
                entities.extend([f"ORG:{org.strip()}" for org in orgs[:3]])
            
            return ', '.join(entities[:10]) if entities else ''
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return ''
    
    def _categorize_article(self, text: str, current_category: str = None) -> str:
        """Categorize article based on content"""
        if current_category and current_category != "General":
            return current_category
        
        try:
            text_lower = text.lower()
            category_scores = {}
            
            for category, keywords in CATEGORY_KEYWORDS.items():
                score = 0
                for keyword in keywords:
                    score += text_lower.count(keyword.lower())
                category_scores[category] = score
            
            # Return category with highest score if above threshold
            if category_scores:
                best_category = max(category_scores.keys(), key=lambda k: category_scores[k])
                if category_scores[best_category] > 0:
                    return best_category
            
            return "General"
            
        except Exception as e:
            logger.error(f"Categorization failed: {str(e)}")
            return current_category or "General"
    
    def _generate_summary(self, text: str) -> str:
        """Generate article summary (simple extractive approach)"""
        try:
            # Simple extractive summary - take first few sentences
            sentences = re.split(r'[.!?]+', text)
            summary_sentences = []
            
            for sentence in sentences[:3]:
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 20:  # Skip very short sentences
                    summary_sentences.append(clean_sentence)
                    if len(' '.join(summary_sentences)) > 200:
                        break
            
            return '. '.join(summary_sentences) + '.' if summary_sentences else text[:200] + '...'
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return text[:200] + '...'
    
    def _classify_government_content(self, article: Article, text: str):
        """Classify if article is government-related and extract relevant information"""
        try:
            # Check if government-related
            is_gov, gov_confidence = self.government_filter.is_government_related(text)
            article.is_government_related = is_gov
            article.confidence_score = gov_confidence

            if is_gov:
                # Classify departments
                departments = self.department_classifier.classify_departments(text)
                article.departments = departments

                # Extract government entities and schemes
                entities = self.government_filter.extract_government_entities(text)
                if entities:
                    article.government_entity = entities.get('entity', '')
                    article.government_scheme = entities.get('scheme', '')
                    article.policy_type = entities.get('policy_type', '')

                logger.info(f"Government classification: {article.title[:30]}... | Depts: {[d['department'] for d in departments[:2]]}")

        except Exception as e:
            logger.error(f"Government classification failed: {str(e)}")
            article.is_government_related = False
            article.confidence_score = 0.0

    def _generate_alerts(self, article: Article) -> List[Alert]:
        """Generate alerts based on article analysis"""
        alerts = []

        try:
            # Check for negative sentiment alerts
            if article.sentiment and article.sentiment.get('score', 0) < NEGATIVE_SENTIMENT_THRESHOLD:
                severity = "critical" if article.sentiment['score'] < CRITICAL_SENTIMENT_THRESHOLD else "high"

                alert = Alert(
                    id=None,
                    alert_type="negative_sentiment",
                    severity=severity,
                    title=f"Negative sentiment detected in {article.source}",
                    content=f"Article '{article.title}' shows {article.sentiment['sentiment']} sentiment (score: {article.sentiment['score']:.3f})",
                    article_id=article.id,
                    threshold_triggered=article.sentiment['score']
                )
                alerts.append(alert)

            # Check for critical keywords
            critical_keywords = ['crisis', 'scandal', 'corruption', 'protest', 'controversy']
            text_lower = f"{article.title} {article.content}".lower()

            for keyword in critical_keywords:
                if keyword in text_lower:
                    alert = Alert(
                        id=None,
                        alert_type="critical_keyword",
                        severity="medium",
                        title=f"Critical keyword detected: {keyword}",
                        content=f"Article '{article.title}' contains potentially sensitive content",
                        article_id=article.id
                    )
                    alerts.append(alert)
                    break  # Only one keyword alert per article

        except Exception as e:
            logger.error(f"Alert generation failed: {str(e)}")

        return alerts
