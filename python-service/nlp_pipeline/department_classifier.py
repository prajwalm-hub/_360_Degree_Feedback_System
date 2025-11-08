import re
from typing import Dict, List, Set, Tuple
from nlp_pipeline.language_detector import LanguageDetector

# Department keywords for classification
DEPARTMENT_KEYWORDS = {
    'health': {
        'en': {'health', 'medical', 'hospital', 'doctor', 'nurse', 'pharmacy', 'medicine', 'disease', 'pandemic', 'covid', 'vaccine', 'ayushman bharat', 'health ministry', 'medical college', 'healthcare', 'sanitation', 'hygiene', 'nutrition', 'malnutrition', 'immunization', 'maternal health', 'child health', 'mental health', 'telemedicine'},
        'hi': {'स्वास्थ्य', 'चिकित्सा', 'अस्पताल', 'डॉक्टर', 'नर्स', 'फार्मेसी', 'दवा', 'बीमारी', 'महामारी', 'कोविड', 'टीका', 'आयुष्मान भारत', 'स्वास्थ्य मंत्रालय', 'मेडिकल कॉलेज', 'स्वास्थ्य सेवा', 'स्वच्छता', 'स्वास्थ्य', 'पोषण', 'कुपोषण', 'टीकाकरण', 'मातृ स्वास्थ्य', 'बाल स्वास्थ्य', 'मानसिक स्वास्थ्य', 'टेलीमेडिसिन'},
        # Add other languages...
    },
    'education': {
        'en': {'education', 'school', 'college', 'university', 'student', 'teacher', 'curriculum', 'exam', 'education ministry', 'literacy', 'skill development', 'vocational training', 'higher education', 'primary education', 'secondary education', 'digital education', 'online learning', 'scholarship', 'education policy'},
        'hi': {'शिक्षा', 'स्कूल', 'कॉलेज', 'विश्वविद्यालय', 'छात्र', 'शिक्षक', 'पाठ्यक्रम', 'परीक्षा', 'शिक्षा मंत्रालय', 'साक्षरता', 'कौशल विकास', 'व्यावसायिक प्रशिक्षण', 'उच्च शिक्षा', 'प्राथमिक शिक्षा', 'माध्यमिक शिक्षा', 'डिजिटल शिक्षा', 'ऑनलाइन सीखना', 'छात्रवृत्ति', 'शिक्षा नीति'},
        # Add other languages...
    },
    'finance': {
        'en': {'finance', 'budget', 'tax', 'revenue', 'expenditure', 'deficit', 'surplus', 'gst', 'income tax', 'finance ministry', 'economic survey', 'monetary policy', 'banking', 'insurance', 'pension', 'investment', 'foreign investment', 'fdi', 'remittance'},
        'hi': {'वित्त', 'बजट', 'कर', 'राजस्व', 'व्यय', 'घाटा', 'अतिरिक्त', 'जीएसटी', 'आयकर', 'वित्त मंत्रालय', 'आर्थिक सर्वेक्षण', 'मौद्रिक नीति', 'बैंकिंग', 'बीमा', 'पेंशन', 'निवेश', 'विदेशी निवेश', 'एफडीआई', 'रिमिटेंस'},
        # Add other languages...
    },
    'defence': {
        'en': {'defence', 'army', 'navy', 'air force', 'military', 'security', 'border', 'terrorism', 'intelligence', 'defence ministry', 'armed forces', 'national security', 'cyber security', 'coast guard', 'paramilitary', 'defence production', 'missile', 'nuclear'},
        'hi': {'रक्षा', 'सेना', 'नौसेना', 'वायुसेना', 'सैन्य', 'सुरक्षा', 'सीमा', 'आतंकवाद', 'खुफिया', 'रक्षा मंत्रालय', 'सशस्त्र बल', 'राष्ट्रीय सुरक्षा', 'साइबर सुरक्षा', 'तटरक्षक', 'अर्धसैनिक', 'रक्षा उत्पादन', 'मिसाइल', 'परमाणु'},
        # Add other languages...
    },
    'agriculture': {
        'en': {'agriculture', 'farmer', 'crop', 'irrigation', 'fertilizer', 'pesticide', 'seed', 'harvest', 'agriculture ministry', 'food security', 'pm kisan', 'rural development', 'dairy', 'fisheries', 'horticulture', 'organic farming', 'agricultural credit'},
        'hi': {'कृषि', 'किसान', 'फसल', 'सिंचाई', 'उर्वरक', 'कीटनाशक', 'बीज', 'फसल कटाई', 'कृषि मंत्रालय', 'खाद्य सुरक्षा', 'पीएम किसान', 'ग्रामीण विकास', 'डेयरी', 'मत्स्य पालन', 'बागवानी', 'जैविक खेती', 'कृषि ऋण'},
        # Add other languages...
    },
    'infrastructure': {
        'en': {'infrastructure', 'road', 'highway', 'railway', 'airport', 'port', 'bridge', 'tunnel', 'metro', 'smart city', 'housing', 'urban development', 'rural infrastructure', 'power', 'electricity', 'renewable energy', 'solar', 'wind'},
        'hi': {'बुनियादी ढांचा', 'सड़क', 'राजमार्ग', 'रेलवे', 'हवाई अड्डा', 'बंदरगाह', 'पुल', 'टनल', 'मेट्रो', 'स्मार्ट सिटी', 'आवास', 'शहरी विकास', 'ग्रामीण बुनियादी ढांचा', 'बिजली', 'बिजली', 'नवीकरणीय ऊर्जा', 'सौर', 'पवन'},
        # Add other languages...
    },
    'environment': {
        'en': {'environment', 'climate', 'pollution', 'forest', 'wildlife', 'conservation', 'green energy', 'sustainable', 'ecology', 'biodiversity', 'water conservation', 'air quality', 'waste management', 'plastic ban', 'carbon emission', 'global warming'},
        'hi': {'पर्यावरण', 'जलवायु', 'प्रदूषण', 'वन', 'वन्यजीव', 'संरक्षण', 'हरित ऊर्जा', 'टिकाऊ', 'परिस्थितिकी', 'जैव विविधता', 'जल संरक्षण', 'वायु गुणवत्ता', 'कचरा प्रबंधन', 'प्लास्टिक प्रतिबंध', 'कार्बन उत्सर्जन', 'ग्लोबल वार्मिंग'},
        # Add other languages...
    },
    'social_welfare': {
        'en': {'welfare', 'poverty', 'employment', 'unemployment', 'social security', 'women empowerment', 'child development', 'senior citizen', 'disabled', 'minority', 'tribal', 'backward classes', 'reservation', 'social justice', 'rural employment', 'mgnrega'},
        'hi': {'कल्याण', 'गरीबी', 'रोजगार', 'बेरोजगारी', 'सामाजिक सुरक्षा', 'महिला सशक्तिकरण', 'बाल विकास', 'वरिष्ठ नागरिक', 'विकलांग', 'अल्पसंख्यक', 'आदिवासी', 'पिछड़े वर्ग', 'आरक्षण', 'सामाजिक न्याय', 'ग्रामीण रोजगार', 'मनरेगा'},
        # Add other languages...
    },
    'technology': {
        'en': {'technology', 'digital', 'internet', 'cyber', 'ai', 'artificial intelligence', 'blockchain', 'startup', 'innovation', 'research', 'development', 'it ministry', 'digital india', 'e-governance', 'smart governance', 'data protection', 'privacy'},
        'hi': {'प्रौद्योगिकी', 'डिजिटल', 'इंटरनेट', 'साइबर', 'एआई', 'कृत्रिम बुद्धिमत्ता', 'ब्लॉकचेन', 'स्टार्टअप', 'नवाचार', 'अनुसंधान', 'विकास', 'आईटी मंत्रालय', 'डिजिटल इंडिया', 'ई-गovernance', 'स्मार्ट गवर्नेंस', 'डेटा सुरक्षा', 'गोपनीयता'},
        # Add other languages...
    },
    'foreign_affairs': {
        'en': {'foreign', 'diplomacy', 'embassy', 'consulate', 'treaty', 'agreement', 'international', 'united nations', 'summit', 'bilateral', 'multilateral', 'visa', 'immigration', 'foreign policy', 'neighbour', 'border dispute'},
        'hi': {'विदेश', 'कूटनीति', 'दूतावास', 'कांसुलेट', 'संधि', 'समझौता', 'अंतर्राष्ट्रीय', 'संयुक्त राष्ट्र', 'शिखर सम्मेलन', 'द्विपक्षीय', 'बहुपक्षीय', 'वीजा', 'आप्रवासन', 'विदेश नीति', 'पड़ोसी', 'सीमा विवाद'},
        # Add other languages...
    },
    'home_affairs': {
        'en': {'home', 'police', 'law order', 'internal security', 'terrorism', 'naxalism', 'maoism', 'insurgency', 'intelligence', 'central armed police', 'census', 'election commission', 'delimitation', 'citizenship', 'passport', 'immigration'},
        'hi': {'गृह', 'पुलिस', 'कानून व्यवस्था', 'आंतरिक सुरक्षा', 'आतंकवाद', 'नक्सलवाद', 'माओवाद', 'विद्रोह', 'खुफिया', 'केंद्रीय सशस्त्र पुलिस', 'जनगणना', 'चुनाव आयोग', 'सीमांकन', 'नागरिकता', 'पासपोर्ट', 'आप्रवासन'},
        # Add other languages...
    },
    'transport': {
        'en': {'transport', 'road transport', 'railway', 'aviation', 'shipping', 'metro', 'bus', 'truck', 'traffic', 'highway', 'national highway', 'expressway', 'railway safety', 'aviation safety', 'shipping ministry', 'transport ministry'},
        'hi': {'परिवहन', 'सड़क परिवहन', 'रेलवे', 'विमानन', 'नौवहन', 'मेट्रो', 'बस', 'ट्रक', 'ट्रैफिक', 'राजमार्ग', 'राष्ट्रीय राजमार्ग', 'एक्सप्रेसवे', 'रेलवे सुरक्षा', 'विमानन सुरक्षा', 'नौवहन मंत्रालय', 'परिवहन मंत्रालय'},
        # Add other languages...
    },
    'commerce': {
        'en': {'commerce', 'trade', 'export', 'import', 'tariff', 'duty', 'commerce ministry', 'industry', 'manufacturing', 'textile', 'steel', 'automobile', 'pharmaceutical', 'chemical', 'fmcg', 'retail', 'e-commerce', 'msme'},
        'hi': {'वाणिज्य', 'व्यापार', 'निर्यात', 'आयात', 'शुल्क', 'कर', 'वाणिज्य मंत्रालय', 'उद्योग', 'विनिर्माण', 'टेक्सटाइल', 'स्टील', 'ऑटोमोबाइल', 'फार्मास्यूटिकल', 'रासायनिक', 'एफएमसीजी', 'रिटेल', 'ई-कॉमर्स', 'एमएसएमई'},
        # Add other languages...
    },
    'labour': {
        'en': {'labour', 'employment', 'worker', 'trade union', 'minimum wage', 'social security', 'labour law', 'industrial dispute', 'strike', 'lockout', 'labour ministry', 'skill development', 'vocational training', 'apprenticeship', 'migrant worker'},
        'hi': {'श्रम', 'रोजगार', 'मजदूर', 'ट्रेड यूनियन', 'न्यूनतम मजदूरी', 'सामाजिक सुरक्षा', 'श्रम कानून', 'औद्योगिक विवाद', 'हड़ताल', 'लॉकआउट', 'श्रम मंत्रालय', 'कौशल विकास', 'व्यावसायिक प्रशिक्षण', 'प्रशिक्षुता', 'प्रवासी मजदूर'},
        # Add other languages...
    },
    'law_justice': {
        'en': {'law', 'justice', 'court', 'supreme court', 'high court', 'judiciary', 'legal', 'constitution', 'amendment', 'bill', 'act', 'law ministry', 'attorney general', 'solicitor general', 'legal aid', 'judicial reform'},
        'hi': {'कानून', 'न्याय', 'न्यायालय', 'सर्वोच्च न्यायालय', 'उच्च न्यायालय', 'न्यायपालिका', 'कानूनी', 'संविधान', 'संशोधन', 'विधेयक', 'अधिनियम', 'कानून मंत्रालय', 'एटॉर्नी जनरल', 'सॉलिसिटर जनरल', 'कानूनी सहायता', 'न्यायिक सुधार'},
        # Add other languages...
    },
    'petroleum': {
        'en': {'petroleum', 'oil', 'gas', 'natural gas', 'refinery', 'petrol', 'diesel', 'fuel', 'energy', 'petroleum ministry', 'ongc', 'gail', 'indian oil', 'bpcl', 'hpcl', 'energy security', 'renewable energy'},
        'hi': {'पेट्रोलियम', 'तेल', 'गैस', 'प्राकृतिक गैस', 'रिफाइनरी', 'पेट्रोल', 'डीजल', 'ईंधन', 'ऊर्जा', 'पेट्रोलियम मंत्रालय', 'ओएनजीसी', 'गेल', 'इंडियन ऑयल', 'बीपीसीएल', 'एचपीसीएल', 'ऊर्जा सुरक्षा', 'नवीकरणीय ऊर्जा'},
        # Add other languages...
    },
    'coal': {
        'en': {'coal', 'mining', 'miner', 'coal india', 'thermal power', 'coal ministry', 'coal production', 'coal import', 'clean coal', 'coal gasification', 'underground mining', 'open cast mining', 'coal washery'},
        'hi': {'कोयला', 'खनन', 'खनिक', 'कोल इंडिया', 'थर्मल पावर', 'कोयला मंत्रालय', 'कोयला उत्पादन', 'कोयला आयात', 'क्लीन कोयला', 'कोयला गैसीकरण', 'भूमिगत खनन', 'ओपन कास्ट खनन', 'कोयला वॉशरी'},
        # Add other languages...
    },
    'new_renewable_energy': {
        'en': {'renewable', 'solar', 'wind', 'hydro', 'geothermal', 'biomass', 'nuclear', 'energy', 'power', 'electricity', 'grid', 'transmission', 'distribution', 'smart grid', 'energy efficiency', 'conservation'},
        'hi': {'नवीकरणीय', 'सौर', 'पवन', 'जलविद्युत', 'भूतापीय', 'जैविक पदार्थ', 'परमाणु', 'ऊर्जा', 'बिजली', 'बिजली', 'ग्रिड', 'ट्रांसमिशन', 'वितरण', 'स्मार्ट ग्रिड', 'ऊर्जा दक्षता', 'संरक्षण'},
        # Add other languages...
    },
    'civil_aviation': {
        'en': {'aviation', 'airport', 'airline', 'air india', 'flight', 'pilot', 'air traffic control', 'aviation ministry', 'civil aviation', 'regional connectivity', 'udaan scheme', 'airport development', 'air safety', 'drone', 'helicopter'},
        'hi': {'विमानन', 'हवाई अड्डा', 'एयरलाइन', 'एयर इंडिया', 'उड़ान', 'पायलट', 'एयर ट्रैफिक कंट्रोल', 'विमानन मंत्रालय', 'सिविल एविएशन', 'क्षेत्रीय कनेक्टिविटी', 'उड़ान योजना', 'हवाई अड्डा विकास', 'वायु सुरक्षा', 'ड्रोन', 'हेलीकॉप्टर'},
        # Add other languages...
    },
    'heavy_industry': {
        'en': {'industry', 'manufacturing', 'steel', 'shipbuilding', 'defence production', 'heavy industry', 'industrial policy', 'make in india', 'industrial corridor', 'special economic zone', 'industrial park', 'factory', 'production'},
        'hi': {'उद्योग', 'विनिर्माण', 'स्टील', 'जहाज निर्माण', 'रक्षा उत्पादन', 'भारी उद्योग', 'औद्योगिक नीति', 'मेक इन इंडिया', 'औद्योगिक कॉरिडोर', 'विशेष आर्थिक क्षेत्र', 'औद्योगिक पार्क', 'फैक्टरी', 'उत्पादन'},
        # Add other languages...
    },
    'food_processing': {
        'en': {'food', 'processing', 'food processing', 'agri business', 'cold chain', 'food safety', 'fssai', 'nutrition', 'food ministry', 'food security', 'public distribution', 'ration', 'food subsidy', 'organic food', 'processed food'},
        'hi': {'खाद्य', 'प्रसंस्करण', 'खाद्य प्रसंस्करण', 'कृषि व्यवसाय', 'कोल्ड चेन', 'खाद्य सुरक्षा', 'एफएसएसएआई', 'पोषण', 'खाद्य मंत्रालय', 'खाद्य सुरक्षा', 'सार्वजनिक वितरण', 'राशन', 'खाद्य सब्सिडी', 'जैविक खाद्य', 'प्रसंस्कृत खाद्य'},
        # Add other languages...
    },
    'textiles': {
        'en': {'textile', 'cotton', 'silk', 'wool', 'synthetic', 'handloom', 'powerloom', 'khadi', 'textile ministry', 'textile industry', 'garment', 'apparel', 'fashion', 'textile park', 'textile cluster', 'weaving'},
        'hi': {'टेक्सटाइल', 'कपास', 'रेशम', 'ऊन', 'सिंथेटिक', 'हस्तशिल्प', 'पावरलूम', 'खादी', 'टेक्सटाइल मंत्रालय', 'टेक्सटाइल इंड्योग', 'गारमेंट', 'अपैरल', 'फैशन', 'टेक्सटाइल पार्क', 'टेक्सटाइल क्लस्टर', 'बुनाई'},
        # Add other languages...
    },
    'tourism': {
        'en': {'tourism', 'tourist', 'travel', 'heritage', 'culture', 'archaeology', 'museum', 'monument', 'temple', 'fort', 'palace', 'beach', 'hill station', 'wildlife sanctuary', 'national park', 'eco tourism', 'medical tourism'},
        'hi': {'पर्यटन', 'पर्यटक', 'यात्रा', 'विरासत', 'संस्कृति', 'पुरातत्व', 'संग्रहालय', 'स्मारक', 'मंदिर', 'किला', 'महल', 'बीच', 'हिल स्टेशन', 'वन्यजीव अभयारण्य', 'राष्ट्रीय उद्यान', 'इको पर्यटन', 'मेडिकल पर्यटन'},
        # Add other languages...
    },
    'youth_sports': {
        'en': {'youth', 'sports', 'athlete', 'olympic', 'commonwealth', 'asian games', 'cricket', 'hockey', 'football', 'kabaddi', 'wrestling', 'badminton', 'tennis', 'boxing', 'athletics', 'swimming', 'youth ministry', 'sports ministry'},
        'hi': {'युवा', 'खेल', 'एथलीट', 'ओलंपिक', 'कॉमनवेल्थ', 'एशियाई खेल', 'क्रिकेट', 'हॉकी', 'फुटबॉल', 'कबड्डी', 'कुश्ती', 'बैडमिंटन', 'टेनिस', 'मुक्केबाजी', 'एथलेटिक्स', 'स्विमिंग', 'युवा मंत्रालय', 'खेल मंत्रालय'},
        # Add other languages...
    }
}

class DepartmentClassifier:
    def __init__(self):
        self.departments = DEPARTMENT_KEYWORDS
        self.detector = LanguageDetector()

    def classify_department(self, text: str, language: str = None) -> List[Tuple[str, float]]:
        """
        Classify text into government departments and return confidence scores.
        Returns: List of (department, confidence_score) tuples, sorted by confidence.
        """
        if not text:
            return []

        # Detect language if not provided
        if not language:
            language = self.detector.detect_language(text)

        text_lower = text.lower()
        department_scores = {}

        for department, lang_keywords in self.departments.items():
            keywords = lang_keywords.get(language, lang_keywords.get('en', set()))

            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            total_keywords = len(keywords)

            # Calculate confidence score
            if total_keywords > 0:
                confidence = matches / total_keywords
                if confidence > 0.05:  # Minimum threshold
                    department_scores[department] = confidence

        # Sort by confidence score (descending)
        sorted_departments = sorted(department_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_departments

    def get_top_department(self, text: str, language: str = None) -> Tuple[str, float]:
        """
        Get the top matching department for the text.
        Returns: (department, confidence_score)
        """
        classifications = self.classify_department(text, language)
        if classifications:
            return classifications[0]
        return ('unknown', 0.0)

    def get_department_keywords(self, department: str, language: str = 'en') -> Set[str]:
        """
        Get keywords for a specific department and language.
        """
        if department in self.departments:
            return self.departments[department].get(language, self.departments[department].get('en', set()))
        return set()
