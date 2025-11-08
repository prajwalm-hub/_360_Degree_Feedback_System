from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer
import logging
import joblib # For model persistence

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TextClassifier:
    def __init__(self):
        self.model = None
        self.mlb = MultiLabelBinarizer()
        self.categories = [
            "Policy & Legislation", "Healthcare & Pandemic", "Education",
            "Infrastructure", "Economy & Finance", "Defense & Security",
            "Environment & Climate", "Agriculture", "Technology & Innovation",
            "Social Welfare"
        ]
        logging.info("TextClassifier initialized.")

    def train_model(self, X_train, y_train):
        """
        Trains the multi-label text classification model.
        X_train: list of preprocessed text documents
        y_train: list of lists, where each inner list contains categories for a document
        """
        if not X_train or not y_train:
            logging.warning("No training data provided for classifier.")
            return

        logging.info(f"Training classifier with {len(X_train)} samples.")
        
        # Fit MultiLabelBinarizer on all possible categories
        self.mlb.fit([self.categories])
        y_train_binarized = self.mlb.transform(y_train)

        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000)),
            ('clf', MultinomialNB())
        ])
        
        try:
            self.model.fit(X_train, y_train_binarized)
            logging.info("Text classification model trained successfully.")
        except Exception as e:
            logging.error(f"Error training text classification model: {e}")
            self.model = None

    def classify_article(self, text):
        """
        Classifies a single article into one or more categories.
        Returns a list of predicted categories.
        """
        if not self.model:
            logging.warning("Model not trained. Cannot classify article.")
            return []
        if not text or not isinstance(text, str):
            return []

        try:
            # Predict probabilities
            probabilities = self.model.predict_proba([text])
            
            # Convert probabilities to binary predictions (e.g., using a threshold)
            # For simplicity, let's assume a threshold of 0.1 for multi-label classification
            threshold = 0.1
            predictions_binarized = (probabilities > threshold).astype(int)
            
            # Inverse transform to get category names
            predicted_categories = self.mlb.inverse_transform(predictions_binarized)
            
            # Since inverse_transform returns a list of lists (one for each sample),
            # we take the first (and only) element for a single article.
            return list(predicted_categories[0])
        except Exception as e:
            logging.error(f"Error classifying article (first 50 chars: '{text[:50]}...'): {e}")
            return []

    def save_model(self, path="classifier_model.joblib"):
        if self.model:
            try:
                joblib.dump((self.model, self.mlb), path)
                logging.info(f"Model saved to {path}")
            except Exception as e:
                logging.error(f"Error saving model to {path}: {e}")
        else:
            logging.warning("No model to save.")

    def load_model(self, path="classifier_model.joblib"):
        try:
            self.model, self.mlb = joblib.load(path)
            logging.info(f"Model loaded from {path}")
            return True
        except FileNotFoundError:
            logging.warning(f"Model file not found at {path}. Please train the model first.")
            return False
        except Exception as e:
            logging.error(f"Error loading model from {path}: {e}")
            return False

if __name__ == '__main__':
    classifier = TextClassifier()
    
    # Dummy training data (in a real scenario, this would come from a dataset)
    X_train_data = [
        "Government introduces new healthcare policy for rural areas.",
        "Budget allocation for education sector increased by 15%.",
        "New highway project to connect major cities, boosting infrastructure.",
        "RBI announces measures to control inflation and stabilize economy.",
        "Defense ministry signs deal for new fighter jets.",
        "India pledges to reduce carbon emissions, focusing on climate change.",
        "Farmers protest against new agricultural laws.",
        "Launch of new satellite by ISRO for technology advancement.",
        "Social welfare schemes launched for underprivileged sections.",
        "Parliament passes new legislation on data privacy.",
        "Pandemic response includes vaccine distribution and hospital upgrades.",
        "Digital literacy program for students in remote villages."
    ]
    y_train_data = [
        ["Healthcare & Pandemic", "Policy & Legislation"],
        ["Education", "Economy & Finance"],
        ["Infrastructure", "Economy & Finance"],
        ["Economy & Finance"],
        ["Defense & Security"],
        ["Environment & Climate"],
        ["Agriculture", "Policy & Legislation"],
        ["Technology & Innovation"],
        ["Social Welfare"],
        ["Policy & Legislation"],
        ["Healthcare & Pandemic"],
        ["Education", "Technology & Innovation", "Social Welfare"]
    ]

    classifier.train_model(X_train_data, y_train_data)
    classifier.save_model("temp_classifier_model.joblib")

    # Load the model for classification
    new_classifier = TextClassifier()
    if new_classifier.load_model("temp_classifier_model.joblib"):
        sample_texts_to_classify = [
            "Prime Minister inaugurates new hospital in remote region.",
            "Economic growth projected to be 7% next fiscal year.",
            "New bill passed to protect forests and wildlife.",
            "Indian army conducts joint exercise with friendly nation.",
            "Startup ecosystem thrives with government support."
        ]

        for text in sample_texts_to_classify:
            categories = new_classifier.classify_article(text)
            print(f"Text: '{text}'\nPredicted Categories: {categories}\n---")
    
    # Clean up dummy model file
    try:
        os.remove("temp_classifier_model.joblib")
        logging.info("Cleaned up temporary model file.")
    except OSError as e:
        logging.warning(f"Error removing temporary model file: {e}")
