# from gensim.summarization import keywords as gensim_keywords  # Deprecated in newer gensim versions
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KeywordExtractor:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        logging.info("KeywordExtractor initialized.")

    def extract_keywords_gensim(self, text, ratio=0.1, words=10):
        """
        Extracts keywords using a simple fallback since Gensim's summarization is deprecated.
        For now, returns TF-IDF based keywords for single text.
        """
        if not text or not isinstance(text, str):
            return []
        try:
            # Fallback: Use TF-IDF on single document
            return self.extract_keywords_tfidf([text], top_n=words)[0]
        except Exception as e:
            logging.error(f"Error extracting keywords (first 50 chars: '{text[:50]}...'): {e}")
            return []

    def extract_keywords_tfidf(self, documents, top_n=10):
        """
        Extracts keywords using TF-IDF.
        Best for a collection of documents to find important terms across the corpus.
        `documents` should be a list of preprocessed text strings.
        """
        if not documents or not isinstance(documents, list) or not all(isinstance(d, str) for d in documents):
            return []
        
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # For each document, get the top N keywords
            all_keywords = []
            for i, doc in enumerate(documents):
                feature_array = tfidf_matrix[i].toarray()
                tfidf_sorting = feature_array.argsort()[0][::-1]
                
                top_n_keywords = []
                for ind in tfidf_sorting[:top_n]:
                    top_n_keywords.append(feature_names[ind])
                all_keywords.append(top_n_keywords)
            
            return all_keywords
        except Exception as e:
            logging.error(f"Error extracting keywords with TF-IDF: {e}")
            return []

if __name__ == '__main__':
    extractor = KeywordExtractor()
    
    sample_text_single = "The Indian government announced a new policy aimed at boosting agricultural productivity and supporting farmers. The policy includes subsidies for modern farming equipment, access to low-interest loans, and training programs on sustainable farming practices. This initiative is expected to significantly improve the livelihoods of millions of farmers across the country and ensure food security. Experts have lauded the move as a crucial step towards agricultural reform."
    
    sample_texts_multiple = [
        "The government's new agricultural policy focuses on farmer welfare and food security. Subsidies for equipment are a key part.",
        "Technology innovation is driving growth in the Indian economy. Startups are receiving significant funding.",
        "Climate change is a global concern. India is committed to renewable energy targets and environmental protection."
    ]

    print("--- Gensim Keyword Extraction (single document) ---")
    gensim_kws = extractor.extract_keywords_gensim(sample_text_single, words=5)
    print(f"Text: '{sample_text_single[:100]}...'\nKeywords: {gensim_kws}\n")

    print("--- TF-IDF Keyword Extraction (multiple documents) ---")
    tfidf_kws = extractor.extract_keywords_tfidf(sample_texts_multiple, top_n=3)
    for i, kws in enumerate(tfidf_kws):
        print(f"Document {i+1} Keywords: {kws}")
