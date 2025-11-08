"""
Multilingual Language Detection and Translation Module
Supports 10+ Indian languages: Hindi, Kannada, Tamil, Telugu, Bengali, 
Gujarati, Marathi, Punjabi, Malayalam, Odia, Urdu, English
"""
from __future__ import annotations
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

# Language codes mapping
INDIAN_LANGUAGES = {
    'hi': 'Hindi',
    'kn': 'Kannada',
    'ta': 'Tamil',
    'te': 'Telugu',
    'bn': 'Bengali',
    'gu': 'Gujarati',
    'mr': 'Marathi',
    'pa': 'Punjabi',
    'ml': 'Malayalam',
    'or': 'Odia',
    'ur': 'Urdu',
    'en': 'English',
}

# Script detection patterns
SCRIPT_PATTERNS = {
    'Devanagari': ['ऀ', 'ँ', 'ं', 'ः', 'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ए', 'ऐ', 'ओ', 'औ', 'क', 'ख', 'ग', 'घ', 'ङ', 'च', 'छ', 'ज', 'झ', 'ञ', 'ट', 'ठ', 'ड', 'ढ', 'ण', 'त', 'थ', 'द', 'ध', 'न', 'प', 'फ', 'ब', 'भ', 'म', 'य', 'र', 'ल', 'व', 'श', 'ष', 'स', 'ह'],  # Hindi, Marathi
    'Kannada': ['ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ೠ', 'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಔ', 'ಕ', 'ಖ', 'ಗ', 'ಘ', 'ಙ', 'ಚ', 'ಛ', 'ಜ', 'ಝ', 'ಞ', 'ಟ', 'ಠ', 'ಡ', 'ಢ', 'ಣ', 'ತ', 'ಥ', 'ದ', 'ಧ', 'ನ', 'ಪ', 'ಫ', 'ಬ', 'ಭ', 'ಮ', 'ಯ', 'ರ', 'ಲ', 'ವ', 'ಶ', 'ಷ', 'ಸ', 'ಹ', 'ಳ'],
    'Tamil': ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ', 'க', 'ங', 'ச', 'ஜ', 'ஞ', 'ட', 'ண', 'த', 'ந', 'ன', 'ப', 'ம', 'ய', 'ர', 'ற', 'ல', 'ள', 'ழ', 'வ', 'ஶ', 'ஷ', 'ஸ', 'ஹ'],
    'Telugu': ['అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ౠ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ', 'క', 'ఖ', 'గ', 'ఘ', 'ఙ', 'చ', 'ఛ', 'జ', 'ఝ', 'ఞ', 'ట', 'ఠ', 'డ', 'ఢ', 'ణ', 'త', 'థ', 'ద', 'ధ', 'న', 'ప', 'ఫ', 'బ', 'భ', 'మ', 'య', 'ర', 'ఱ', 'ల', 'ళ', 'వ', 'శ', 'ష', 'స', 'హ'],
    'Bengali': ['অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ', 'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ', 'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন', 'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ', 'স', 'হ', 'ড়', 'ঢ়', 'য়'],
    'Gujarati': ['અ', 'આ', 'ઇ', 'ઈ', 'ઉ', 'ઊ', 'ઋ', 'એ', 'ઐ', 'ઓ', 'ઔ', 'ક', 'ખ', 'ગ', 'ઘ', 'ઙ', 'ચ', 'છ', 'જ', 'ઝ', 'ઞ', 'ટ', 'ઠ', 'ડ', 'ઢ', 'ણ', 'ત', 'થ', 'દ', 'ધ', 'ન', 'પ', 'ફ', 'બ', 'ભ', 'મ', 'ય', 'ર', 'લ', 'વ', 'શ', 'ષ', 'સ', 'હ', 'ળ'],
    'Malayalam': ['അ', 'ആ', 'ഇ', 'ഈ', 'ഉ', 'ഊ', 'ഋ', 'ൠ', 'ഌ', 'ൡ', 'എ', 'ഏ', 'ഐ', 'ഒ', 'ഓ', 'ഔ', 'ക', 'ഖ', 'ഗ', 'ഘ', 'ങ', 'ച', 'ഛ', 'ജ', 'ഝ', 'ഞ', 'ട', 'ഠ', 'ഡ', 'ഢ', 'ണ', 'ത', 'ഥ', 'ദ', 'ധ', 'ന', 'പ', 'ഫ', 'ബ', 'ഭ', 'മ', 'യ', 'ര', 'ല', 'വ', 'ശ', 'ഷ', 'സ', 'ഹ', 'ള', 'ഴ', 'റ'],
    'Odia': ['ଅ', 'ଆ', 'ଇ', 'ଈ', 'ଉ', 'ଊ', 'ଋ', 'ୠ', 'ଌ', 'ୡ', 'ଏ', 'ଐ', 'ଓ', 'ଔ', 'କ', 'ଖ', 'ଗ', 'ଘ', 'ଙ', 'ଚ', 'ଛ', 'ଜ', 'ଝ', 'ଞ', 'ଟ', 'ଠ', 'ଡ', 'ଢ', 'ଣ', 'ତ', 'ଥ', 'ଦ', 'ଧ', 'ନ', 'ପ', 'ଫ', 'ବ', 'ଭ', 'ମ', 'ଯ', 'ର', 'ଲ', 'ଳ', 'ଵ', 'ଶ', 'ଷ', 'ସ', 'ହ', 'ଡ଼', 'ଢ଼', 'ୟ'],
    'Gurmukhi': ['ਅ', 'ਆ', 'ਇ', 'ਈ', 'ਉ', 'ਊ', 'ਏ', 'ਐ', 'ਓ', 'ਔ', 'ਕ', 'ਖ', 'ਗ', 'ਘ', 'ਙ', 'ਚ', 'ਛ', 'ਜ', 'ਝ', 'ਞ', 'ਟ', 'ਠ', 'ਡ', 'ਢ', 'ਣ', 'ਤ', 'ਥ', 'ਦ', 'ਧ', 'ਨ', 'ਪ', 'ਫ', 'ਬ', 'ਭ', 'ਮ', 'ਯ', 'ਰ', 'ਲ', 'ਲ਼', 'ਵ', 'ਸ਼', 'ਸ', 'ਹ'],  # Punjabi
}


class MultilingualProcessor:
    """
    Comprehensive multilingual processing for Indian languages
    - Language detection (fasttext + langdetect + script-based)
    - Translation (IndicTrans2 for Indian languages)
    - Script detection and transliteration
    """
    
    def __init__(self):
        self._lang_detector = None
        self._translator_model = None
        self._translator_tokenizer = None
        self._transliterator = None
        
    def _ensure_detector(self):
        """Load language detector (lazy loading)."""
        if self._lang_detector is not None:
            return
            
        try:
            import langdetect
            self._lang_detector = langdetect
            logger.info("Language detector loaded successfully")
        except Exception as e:
            logger.exception("Failed to load language detector: %s", e)
    
    def _ensure_translator(self):
        """Load IndicTrans2 translation model (lazy loading)."""
        if self._translator_model is not None:
            return
            
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            import torch
            import os
            
            model_name = "ai4bharat/indictrans2-indic-en-1B"
            hf_token = os.getenv("HUGGINGFACE_TOKEN")  # Load from environment variable
            
            logger.info(f"Loading IndicTrans2 model: {model_name}")
            
            # Load tokenizer with authentication token (using 'token' parameter)
            self._translator_tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=hf_token,
                trust_remote_code=True
            )
            
            # Determine device (GPU if available)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load model with authentication token (using 'token' parameter)
            self._translator_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                token=hf_token,
                trust_remote_code=True
            ).to(device)
            
            logger.info(f"IndicTrans2 model loaded successfully on {device}")
            
        except Exception as e:
            logger.warning("IndicTrans2 model could not be loaded — using googletrans fallback")
            logger.debug(f"IndicTrans2 load error details: {e}")
            # Set to False to avoid retry and use googletrans fallback
            self._translator_model = False
            self._translator_tokenizer = False
    
    def _detect_script(self, text: str) -> Optional[str]:
        """Detect writing script based on Unicode ranges."""
        if not text:
            return None
            
        # Count characters per script
        script_counts: Dict[str, int] = {}
        for script, chars in SCRIPT_PATTERNS.items():
            count = sum(1 for c in text if c in chars)
            if count > 0:
                script_counts[script] = count
        
        if not script_counts:
            return "Latin"  # Default to Latin/English
        
        # Return script with maximum count
        return max(script_counts.items(), key=lambda x: x[1])[0]
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language using multiple methods:
        1. Script-based detection (fast, accurate for distinct scripts)
        2. langdetect library (statistical)
        3. Fallback heuristics
        
        Returns: {
            'code': 'hi',
            'name': 'Hindi',
            'script': 'Devanagari',
            'confidence': 0.95
        }
        """
        if not text or len(text.strip()) < 3:
            return {
                'code': 'unknown',
                'name': 'Unknown',
                'script': 'Unknown',
                'confidence': 0.0
            }
        
        # Script-based detection (most reliable for Indian languages)
        script = self._detect_script(text)
        
        # Map script to primary language
        script_to_lang = {
            'Devanagari': 'hi',  # Hindi is most common
            'Kannada': 'kn',
            'Tamil': 'ta',
            'Telugu': 'te',
            'Bengali': 'bn',
            'Gujarati': 'gu',
            'Malayalam': 'ml',
            'Odia': 'or',
            'Gurmukhi': 'pa',
            'Latin': 'en',
        }
        
        lang_code = script_to_lang.get(script, 'unknown')
        confidence = 0.9  # High confidence for script-based detection
        
        # Try langdetect as secondary method
        self._ensure_detector()
        if self._lang_detector:
            try:
                from langdetect import detect, detect_langs
                detected = detect(text)
                # Map langdetect codes to our codes
                langdetect_map = {
                    'hi': 'hi', 'kn': 'kn', 'ta': 'ta', 'te': 'te',
                    'bn': 'bn', 'gu': 'gu', 'mr': 'mr', 'pa': 'pa',
                    'ml': 'ml', 'or': 'or', 'ur': 'ur', 'en': 'en',
                }
                if detected in langdetect_map:
                    # If script-based and langdetect agree, increase confidence
                    if lang_code == langdetect_map[detected]:
                        confidence = 0.95
                    else:
                        # Use langdetect result if script was ambiguous
                        if lang_code == 'unknown':
                            lang_code = langdetect_map[detected]
                            confidence = 0.75
            except Exception:
                logger.debug("langdetect failed, using script-based detection")
        
        return {
            'code': lang_code,
            'name': INDIAN_LANGUAGES.get(lang_code, 'Unknown'),
            'script': script or 'Unknown',
            'confidence': confidence
        }
    
    def translate_to_english(self, text: str, source_lang: str) -> Optional[str]:
        """
        Translate Indian language text to English using IndicTrans2.
        Falls back to googletrans if IndicTrans2 not available.
        
        Args:
            text: Text to translate
            source_lang: Source language code (hi, ta, te, etc.)
        
        Returns:
            Translated English text or None if failed
        """
        # If already English, return as-is
        if source_lang == 'en':
            return text
        
        # If source language not in supported Indian languages, skip
        if source_lang not in INDIAN_LANGUAGES:
            logger.debug(f"Unsupported language for translation: {source_lang}")
            return None
        
        # Try googletrans first (simpler, more reliable)
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src=source_lang, dest='en')
            if result and result.text:
                logger.info(f"Translated using googletrans: {source_lang} -> en")
                return result.text
        except Exception as e:
            logger.debug(f"googletrans failed: {e}, trying deep-translator...")
        
        # Try deep-translator as second option
        try:
            from deep_translator import GoogleTranslator
            result = GoogleTranslator(source=source_lang, target='en').translate(text)
            if result:
                logger.info(f"Translated using deep-translator: {source_lang} -> en")
                return result
        except Exception as e:
            logger.debug(f"deep-translator failed: {e}, trying IndicTrans2...")
        
        # Fallback to IndicTrans2 if googletrans fails
        # Ensure translator is loaded
        self._ensure_translator()
        
        # If translator failed to load, return None
        if not self._translator_model or not self._translator_tokenizer:
            logger.warning("Translation not available (install googletrans, deep-translator or IndicTrans2)")
            return None
        
        try:
            import torch
            
            # IndicTrans2 language codes mapping (flores-200 format)
            lang_mapping = {
                'hi': 'hin_Deva',  # Hindi
                'kn': 'kan_Knda',  # Kannada
                'ta': 'tam_Taml',  # Tamil
                'te': 'tel_Telu',  # Telugu
                'bn': 'ben_Beng',  # Bengali
                'gu': 'guj_Gujr',  # Gujarati
                'mr': 'mar_Deva',  # Marathi
                'pa': 'pan_Guru',  # Punjabi
                'ml': 'mal_Mlym',  # Malayalam
                'or': 'ory_Orya',  # Odia
                'ur': 'urd_Arab',  # Urdu
            }
            
            flores_code = lang_mapping.get(source_lang)
            if not flores_code:
                logger.warning(f"No FLORES code mapping for {source_lang}")
                return None
            
            # Prepare input with source language tag
            input_text = f"{flores_code} {text}"
            
            # Tokenize
            inputs = self._translator_tokenizer(
                input_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Move to same device as model
            device = next(self._translator_model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                generated_tokens = self._translator_model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5,
                    num_return_sequences=1,
                    early_stopping=True
                )
            
            # Decode
            translated = self._translator_tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True
            )[0]
            
            logger.debug(f"Translated {source_lang} text to English: {text[:50]}... -> {translated[:50]}...")
            return translated.strip()
            
        except Exception as e:
            logger.exception(f"Translation failed for {source_lang}: {e}")
            return None
    
    def transliterate(self, text: str, source_script: str, target_script: str = 'Latin') -> Optional[str]:
        """
        Transliterate text from one script to another.
        Useful for: Devanagari to Latin, Tamil to Latin, etc.
        
        Args:
            text: Text to transliterate
            source_script: Source script name
            target_script: Target script name (default: Latin)
        
        Returns:
            Transliterated text or None if failed
        """
        if not text or source_script == target_script:
            return text
        
        try:
            from indic_transliteration import sanscript
            from indic_transliteration.sanscript import transliterate as trans
            
            # Map our script names to sanscript constants
            script_map = {
                'Devanagari': sanscript.DEVANAGARI,
                'Kannada': sanscript.KANNADA,
                'Tamil': sanscript.TAMIL,
                'Telugu': sanscript.TELUGU,
                'Bengali': sanscript.BENGALI,
                'Gujarati': sanscript.GUJARATI,
                'Malayalam': sanscript.MALAYALAM,
                'Odia': sanscript.ORIYA,
                'Gurmukhi': sanscript.GURMUKHI,
                'Latin': sanscript.ITRANS,  # Use ITRANS for Latin representation
            }
            
            source = script_map.get(source_script)
            target = script_map.get(target_script, sanscript.ITRANS)
            
            if not source:
                logger.warning(f"Unsupported source script for transliteration: {source_script}")
                return None
            
            result = trans(text, source, target)
            logger.debug(f"Transliterated from {source_script} to {target_script}")
            return result
            
        except Exception as e:
            logger.exception(f"Transliteration failed: {e}")
            return None
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Return dictionary of supported language codes and names."""
        return INDIAN_LANGUAGES.copy()
