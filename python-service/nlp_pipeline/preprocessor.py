import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import logging

# Ensure NLTK data is available (run these once if not already downloaded)
# import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TextPreprocessor:
    def __init__(self, language='english'):
        self.language = language
        self.stop_words = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()
        logging.info(f"TextPreprocessor initialized for language: {language}")

    def clean_text(self, text):
        if not text or not isinstance(text, str):
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove mentions and hashtags (common in social media)
        text = re.sub(r'@\w+|#\w+', '', text)
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Convert to lowercase
        text = text.lower()
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def tokenize_and_lemmatize(self, text):
        if not text:
            return []
        
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        return lemmatized_tokens

    def remove_stopwords(self, tokens):
        if not tokens:
            return []
        
        filtered_tokens = [word for word in tokens if word not in self.stop_words]
        return filtered_tokens

    def preprocess(self, text):
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize_and_lemmatize(cleaned_text)
        filtered_tokens = self.remove_stopwords(tokens)
        return " ".join(filtered_tokens)

if __name__ == '__main__':
    preprocessor = TextPreprocessor(language='english')
    
    sample_texts = [
        "The quick brown fox jumps over the lazy dog. Visit https://example.com for more info! @user #fox",
        "This is a test sentence with some numbers like 123 and symbols!?",
        "  Another example   with   extra   spaces.  ",
        "A very short text.",
        "",
        None
    ]

    for text in sample_texts:
        processed_text = preprocessor.preprocess(text)
        print(f"Original: '{text}'\nProcessed: '{processed_text}'\n---")

    # Example for Hindi (requires 'hindi' stopwords if available in NLTK or custom list)
    # NLTK's default stopwords only include English. For other languages,
    # you'd need to provide a custom stopword list or use a library like spaCy
    # with language-specific models.
    # preprocessor_hi = TextPreprocessor(language='hindi') # This will likely fail without custom stopwords
    # hindi_text = "यह एक बहुत ही अच्छा दिन है।"
    # processed_hindi_text = preprocessor_hi.preprocess(hindi_text)
    # print(f"Original Hindi: '{hindi_text}'\nProcessed Hindi: '{processed_hindi_text}'\n---")
