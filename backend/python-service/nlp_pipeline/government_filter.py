import re
from typing import Dict, List, Set, Tuple
from nlp_pipeline.language_detector import LanguageDetector

# Government-related keywords for each language
GOVERNMENT_KEYWORDS = {
    'en': {
        'government', 'ministry', 'minister', 'cabinet', 'parliament', 'lok sabha', 'rajya sabha',
        'bjp', 'congress', 'nda', 'upa', 'pm', 'prime minister', 'cm', 'chief minister',
        'policy', 'scheme', 'program', 'initiative', 'reform', 'bill', 'act', 'law',
        'budget', 'finance', 'tax', 'subsidy', 'allocation', 'fund', 'grant',
        'election', 'voting', 'democracy', 'constitution', 'amendment',
        'governance', 'administration', 'bureaucracy', 'civil service',
        'public sector', 'psu', 'government enterprise', 'railways', 'air india',
        'defence', 'army', 'navy', 'air force', 'military', 'security', 'intelligence',
        'foreign affairs', 'diplomacy', 'embassy', 'consulate', 'treaty', 'agreement',
        'health', 'education', 'agriculture', 'infrastructure', 'transport', 'energy',
        'environment', 'climate', 'disaster', 'relief', 'welfare', 'poverty', 'employment'
    },
    'hi': {
        'सरकार', 'मंत्रालय', 'मंत्री', 'कैबिनेट', 'संसद', 'लोकसभा', 'राज्यसभा',
        'भाजपा', 'कांग्रेस', 'एनडीए', 'यूपीए', 'प्रधानमंत्री', 'मुख्यमंत्री',
        'नीति', 'योजना', 'कार्यक्रम', 'पहल', 'सुधार', 'विधेयक', 'अधिनियम', 'कानून',
        'बजट', 'वित्त', 'कर', 'सब्सिडी', 'आवंटन', 'निधि', 'अनुदान',
        'चुनाव', 'मतदान', 'लोकतंत्र', 'संविधान', 'संशोधन',
        'शासन', 'प्रशासन', 'नौकरशाही', 'सिविल सेवा',
        'सार्वजनिक क्षेत्र', 'सरकारी उद्यम', 'रेलवे', 'एयर इंडिया',
        'रक्षा', 'सेना', 'नौसेना', 'वायुसेना', 'सैन्य', 'सुरक्षा', 'खुफिया',
        'विदेश मामले', 'कूटनीति', 'दूतावास', 'कांसुलेट', 'संधि', 'समझौता',
        'स्वास्थ्य', 'शिक्षा', 'कृषि', 'बुनियादी ढांचा', 'परिवहन', 'ऊर्जा',
        'पर्यावरण', 'जलवायु', 'आपदा', 'राहत', 'कल्याण', 'गरीबी', 'रोजगार'
    },
    # Add other languages similarly...
    'bn': {'সরকার', 'মন্ত্রক', 'মন্ত্রী', 'ক্যাবিনেট', 'সংসদ', 'লোকসভা', 'রাজ্যসভা'},
    'te': {'ప్రభుత్వం', 'మంత్రిత్వ శాఖ', 'మంత్రి', 'క్యాబినెట్', 'పార్లమెంట్', 'లోక్ సభ', 'రాజ్య సభ'},
    'mr': {'सरकार', 'मंत्रालय', 'मंत्री', 'कॅबिनेट', 'संसद', 'लोकसभा', 'राज्यसभा'},
    'ta': {'அரசு', 'அமைச்சகம்', 'அமைச்சர்', 'அமைச்சரவை', 'பாராளுமன்றம்', 'லோக் சபை', 'ராஜ்ய சபை'},
    'ur': {'حکومت', 'وزارت', 'وزیر', 'کابینہ', 'پارلیمنٹ', 'لوک سبھا', 'راجیا سبھا'},
    'gu': {'સરકાર', 'મંત્રાલય', 'મંત્રી', 'કેબિનેટ', 'સંસદ', 'લોકસભા', 'રાજ્યસભા'},
    'kn': {'ಸರ್ಕಾರ', 'ಮಂತ್ರಾಲಯ', 'ಮಂತ್ರಿ', 'ಕ್ಯಾಬಿನೆಟ್', 'ಪಾರ್ಲಮೆಂಟ್', 'ಲೋಕ್ ಸಭಾ', 'ರಾಜ್ಯ ಸಭಾ'},
    'or': {'ସରକାର', 'ମନ୍ତ୍ରଣାଳୟ', 'ମନ୍ତ୍ରୀ', 'କ୍ୟାବିନେଟ୍', 'ସଂସଦ', 'ଲୋକସଭା', 'ରାଜ୍ୟସଭା'}
}

GOVERNMENT_ENTITIES = {
    'en': {
        'narendra modi', 'modi', 'amit shah', 'rajnath singh', 'nirmala sitharaman',
        'smriti irani', 'nitish kumar', 'mamata banerjee', 'arvind kejriwal',
        'rahul gandhi', 'sonia gandhi', 'manmohan singh', 'atal bihari vajpayee',
        'indian government', 'government of india', 'ministry of home affairs',
        'ministry of finance', 'ministry of defence', 'ministry of external affairs',
        'ministry of health', 'ministry of education', 'ministry of agriculture'
    },
    'hi': {
        'नरेंद्र मोदी', 'मोदी', 'अमित शाह', 'राजनाथ सिंह', 'निर्मला सीतारमण',
        'स्मृति ईरानी', 'नीतीश कुमार', 'ममता बनर्जी', 'अरविंद केजरीवाल',
        'राहुल गांधी', 'सोनिया गांधी', 'मनमोहन सिंह', 'अटल बिहारी वाजपेयी',
        'भारतीय सरकार', 'भारत सरकार', 'गृह मंत्रालय', 'वित्त मंत्रालय',
        'रक्षा मंत्रालय', 'विदेश मंत्रालय', 'स्वास्थ्य मंत्रालय', 'शिक्षा मंत्रालय', 'कृषि मंत्रालय'
    },
    # Add other languages...
}

class GovernmentFilter:
    def __init__(self):
        self.keywords = GOVERNMENT_KEYWORDS
        self.entities = GOVERNMENT_ENTITIES

    def is_government_related(self, text: str, language: str = None) -> tuple[bool, float]:
        """
        Determine if text is government-related and return confidence score.
        Returns: (is_government_related, confidence_score)
        """
        if not text:
            return False, 0.0

        # Detect language if not provided
        if not language:
            detector = LanguageDetector()
            language = detector.detect_language(text)

        # Get language-specific keywords and entities
        keywords = self.keywords.get(language, self.keywords.get('en', set()))
        entities = self.entities.get(language, self.entities.get('en', set()))

        # Convert text to lowercase for matching
        text_lower = text.lower()

        # Count matches
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        entity_matches = sum(1 for entity in entities if entity.lower() in text_lower)

        # Calculate confidence score
        total_keywords = len(keywords)
        total_entities = len(entities)

        keyword_score = keyword_matches / max(total_keywords, 1)
        entity_score = entity_matches / max(total_entities, 1)

        # Weighted score: entities have higher weight
        confidence = (keyword_score * 0.6) + (entity_score * 0.4)

        # Threshold for classification
        is_government = confidence > 0.1  # Adjust threshold as needed

        return is_government, confidence

    def extract_government_entities(self, text: str, language: str = None) -> List[str]:
        """
        Extract government-related entities from text.
        """
        if not language:
            detector = LanguageDetector()
            language = detector.detect_language(text)

        entities = self.entities.get(language, self.entities.get('en', set()))
        text_lower = text.lower()

        found_entities = [entity for entity in entities if entity.lower() in text_lower]
        return found_entities
