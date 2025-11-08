from langdetect import detect, DetectorFactory
import logging

# Ensure consistent results for langdetect
DetectorFactory.seed = 0

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LanguageDetector:
    def __init__(self):
        logging.info("LanguageDetector initialized.")

    def detect_language(self, text):
        if not text or not isinstance(text, str):
            return None
        try:
            lang = detect(text)
            return lang
        except Exception as e:
            logging.warning(f"Could not detect language for text (first 50 chars: '{text[:50]}...'): {e}")
            return None

if __name__ == '__main__':
    detector = LanguageDetector()
    
    texts = [
        "This is a sample English text.",
        "यह एक नमूना हिंदी पाठ है।",
        "இது ஒரு மாதிரி தமிழ் உரை.",
        "తెలుగులో ఇది ఒక నమూనా వచనం.",
        "এটি একটি নমুনা বাংলা পাঠ।",
        "આ એક નમૂના ગુજરાતી લખાણ છે.",
        "ಇದು ಒಂದು ಮಾದರಿ ಕನ್ನಡ ಪಠ್ಯ.",
        "ഇതൊരു മാതൃക മലയാളം പാഠമാണ്.",
        "हा एक नमुना मराठी मजकूर आहे.",
        "ਇਹ ਇੱਕ ਨਮੂਨਾ ਪੰਜਾਬੀ ਪਾਠ ਹੈ।",
        "یہ ایک نمونہ اردو متن ہے۔",
        "A short text.",
        "",
        None
    ]

    for text in texts:
        lang = detector.detect_language(text)
        print(f"Text: '{text[:50]}...' -> Detected Language: {lang}")
