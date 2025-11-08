import os
from google.cloud import translate_v2 as translate
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Translator:
    def __init__(self, config):
        self.config = config
        self.google_translate_api_key = getattr(config, "google_translate_api_key", "")
        
        if self.google_translate_api_key:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.google_translate_api_key
            self.translate_client = translate.Client()
            logging.info("Google Translate client initialized.")
        else:
            self.translate_client = None
            logging.warning("Google Translate API key not provided. Translation will be skipped.")

    def translate_text(self, text, source_language, target_language='en'):
        if not self.translate_client:
            return text # Return original text if translator not initialized
        
        if not text or not isinstance(text, str):
            return text

        if source_language == target_language:
            return text

        try:
            result = self.translate_client.translate(
                text,
                source_language=source_language,
                target_language=target_language
            )
            return result['translatedText']
        except Exception as e:
            logging.error(f"Error translating text from {source_language} to {target_language} (first 50 chars: '{text[:50]}...'): {e}")
            return text # Return original text on error

if __name__ == '__main__':
    # Example Usage (replace with actual config loading and API key)
    # For Google Cloud Translation API, you typically set GOOGLE_APPLICATION_CREDENTIALS
    # environment variable to the path of your service account key file.
    # For this example, we'll simulate it with a placeholder.
    sample_config = {
        "google_translate_api_key": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "path/to/your/google_credentials.json")
    }

    if sample_config["google_translate_api_key"] == "path/to/your/google_credentials.json":
        logging.warning("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable or update the sample_config.")
    
    translator = Translator(sample_config)
    
    texts_to_translate = [
        ("नमस्ते दुनिया", "hi"),
        ("வணக்கம் உலகம்", "ta"),
        ("హలో ప్రపంచం", "te"),
        ("হ্যালো ওয়ার্ল্ড", "bn"),
        ("નમસ્તે દુનિયા", "gu"),
        ("ಹಲೋ ವರ್ಲ್ಡ್", "kn"),
        ("ഹലോ വേൾഡ്", "ml"),
        ("नमस्कार जग", "mr"),
        ("ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਦੁਨਿਆ", "pa"),
        ("ہیلو ورلڈ", "ur"),
        ("Hello world", "en")
    ]

    for text, lang in texts_to_translate:
        translated_text = translator.translate_text(text, lang, 'en')
        print(f"Original ({lang}): '{text}' -> Translated (en): '{translated_text}'")
