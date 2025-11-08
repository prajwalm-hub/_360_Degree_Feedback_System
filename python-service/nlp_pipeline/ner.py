import spacy
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NamedEntityRecognizer:
    def __init__(self):
        # Load a multilingual or English spaCy model.
        # 'xx_ent_wiki_sm' is a good choice for multilingual entity recognition.
        # For better performance, consider language-specific models if the language is known.
        try:
            self.nlp = spacy.load('xx_ent_wiki_sm')
            logging.info("spaCy multilingual NER model 'xx_ent_wiki_sm' loaded.")
        except Exception as e:
            self.nlp = None
            logging.error(f"Could not load spaCy model 'xx_ent_wiki_sm': {e}. NER will be skipped.")

    def extract_entities(self, text):
        if not self.nlp or not text or not isinstance(text, str):
            return []

        entities = []
        try:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start_char': ent.start_char,
                    'end_char': ent.end_char
                })
            logging.debug(f"Extracted {len(entities)} entities from text (first 50 chars: '{text[:50]}...').")
        except Exception as e:
            logging.error(f"Error during NER for text (first 50 chars: '{text[:50]}...'): {e}")
        return entities

if __name__ == '__main__':
    ner_recognizer = NamedEntityRecognizer()
    
    sample_texts = [
        "Narendra Modi, the Prime Minister of India, visited New Delhi for a meeting with the Ministry of Finance.",
        "Google announced its new AI project in California.",
        "The United Nations held a summit in Geneva.",
        "Dr. Abdul Kalam was a great scientist.",
        "भारत के प्रधानमंत्री नरेंद्र मोदी ने नई दिल्ली में वित्त मंत्रालय के साथ एक बैठक के लिए दौरा किया।", # Hindi
        "Google ने कैलिफ़ोर्निया में अपनी नई AI परियोजना की घोषणा की।", # Hindi
        "A short sentence.",
        "",
        None
    ]

    for text in sample_texts:
        entities = ner_recognizer.extract_entities(text)
        print(f"Original: '{text}'\nEntities: {entities}\n---")
