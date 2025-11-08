from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Summarizer:
    def __init__(self):
        # Initialize Hugging Face pipeline for summarization
        # Using a general multilingual summarization model.
        # 'csebuetnlp/mT5_multilingual_XLSum' is a good option for abstractive summarization.
        try:
            self.summarization_pipeline = pipeline('summarization', model='csebuetnlp/mT5_multilingual_XLSum')
            logging.info("Hugging Face multilingual summarization pipeline initialized.")
        except Exception as e:
            self.summarization_pipeline = None
            logging.error(f"Could not load Hugging Face summarization model: {e}. Summarization will be skipped.")

    def summarize_text(self, text, min_length=30, max_length=150):
        if not self.summarization_pipeline or not text or not isinstance(text, str):
            return text # Return original text if summarizer not initialized or input is invalid

        try:
            # The summarization pipeline expects a list of texts
            summary = self.summarization_pipeline(text, min_length=min_length, max_length=max_length, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            logging.error(f"Error during summarization for text (first 50 chars: '{text[:50]}...'): {e}")
            return text # Return original text on error

if __name__ == '__main__':
    summarizer = Summarizer()
    
    sample_texts = [
        "The Indian government announced a new policy aimed at boosting agricultural productivity and supporting farmers. The policy includes subsidies for modern farming equipment, access to low-interest loans, and training programs on sustainable farming practices. This initiative is expected to significantly improve the livelihoods of millions of farmers across the country and ensure food security. Experts have lauded the move as a crucial step towards agricultural reform.",
        "भारत सरकार ने कृषि उत्पादकता बढ़ाने और किसानों का समर्थन करने के उद्देश्य से एक नई नीति की घोषणा की। इस नीति में आधुनिक कृषि उपकरणों के लिए सब्सिडी, कम ब्याज वाले ऋण तक पहुंच और टिकाऊ खेती के तरीकों पर प्रशिक्षण कार्यक्रम शामिल हैं। इस पहल से देश भर के लाखों किसानों की आजीविका में उल्लेखनीय सुधार होने और खाद्य सुरक्षा सुनिश्चित होने की उम्मीद है। विशेषज्ञों ने इस कदम को कृषि सुधार की दिशा में एक महत्वपूर्ण कदम बताया है।", # Hindi
        "A very short text that might not be summarized effectively.",
        "",
        None
    ]

    for text in sample_texts:
        summary = summarizer.summarize_text(text)
        print(f"Original (first 100 chars): '{text[:100]}...'\nSummary: '{summary}'\n---")
