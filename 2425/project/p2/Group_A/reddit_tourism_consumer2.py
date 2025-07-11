"""
Malaysian Tourism Kafka Consumer with Real-time Sentiment Analysis
================================================================

This consumer processes tourism-related posts and comments from Kafka streams,
performing sentiment analysis and generating insights for Malaysian tourism.

Features:
- Real-time Kafka message consumption
- Multi-model sentiment analysis (TextBlob, VADER, Custom)
- Malaysian tourism-specific sentiment scoring
- Data enrichment and processing
- Real-time analytics and monitoring
- Comprehensive error handling and logging
- Dashboard-ready data output

Author: Big Data & NLP Analytics Team
Date: June 22, 2025
Course Deadline: June 27, 2025
"""

import json
import time
import warnings
import logging
import os
import re
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple
import pandas as pd
from collections import defaultdict, deque
import threading
from pathlib import Path
import pickle
import glob
import csv

# === SUPPRESS ALL WARNINGS ===
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'     # Hide TensorFlow INFO & WARN
warnings.filterwarnings("ignore")            # Hide Python warnings
logging.getLogger('tensorflow').setLevel(logging.ERROR)  # Hide TensorFlow logs

# NLP and Sentiment Analysis imports
try:
    import nltk
    import numpy as np
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.tag import pos_tag

    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.sequence import pad_sequences

    NLP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ NLP or LSTM libraries not available: {e}")
    NLP_AVAILABLE = False

# Try to import Kafka
try:
    from kafka import KafkaConsumer
    from kafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Kafka not available: {e}")
    print("📝 Running in FILE-ONLY mode - will process saved JSON files")
    KAFKA_AVAILABLE = False
    KafkaConsumer = None

# Load environment variables
load_dotenv('.env.local')

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/reddit_tourism_consumer.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class MalaysianTourismSentimentAnalyzer:
    """Advanced sentiment analysis using trained Naive Bayes model"""
    
    def __init__(self):
        """Initialize sentiment analysis with trained model"""
        self.setup_models()
        self.setup_malaysian_context()
        self.setup_nltk_preprocessing()
        self.load_trained_model()  # New: Load trained NB model
        self.lstm_model = None
        self.lstm_tokenizer = None
        self.lstm_label_encoder = None
        self.load_lstm_model()  # Load LSTM model
    
    def setup_models(self):
        """Setup sentiment analysis models - ML model only"""
        if NLP_AVAILABLE:
            # Download required NLTK data (keep for preprocessing only)
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('omw-1.4', quiet=True)
                # nltk.download('vader_lexicon', quiet=True)  # REMOVED - No more VADER
            except:
                pass
            
            # Remove VADER initialization
            # self.vader = SentimentIntensityAnalyzer()  # REMOVED
            self.vader = None  # Explicitly set to None
            logger.info("✅ NLTK preprocessing initialized (ML model only)")
        else:
            logger.warning("⚠️ NLP libraries not available")
            self.vader = None
    
    def analyze_sentiment_dual_models(self, text: str, title: str = "") -> Dict:

        print(f"\n🔍 DUAL MODEL ANALYSIS - Text: {text[:100]}...")
        print(f"🔍 DUAL MODEL ANALYSIS - Title: {title}")

        is_comment = not title or title == ""
        text_preprocessing = self.preprocess_text(text, use_lemmatization=True)
        title_preprocessing = self._empty_preprocessing_result("") if is_comment else self.preprocess_text(title, use_lemmatization=True)

        # Initialize results
        naive_bayes_result = {}
        lstm_result = {}

        # === NAIVE BAYES MODEL ===
        print("🤖 Running Naive Bayes model...")
        try:
            naive_bayes_result = self.analyze_sentiment_with_naive_bayes(text, "" if is_comment else title)
            print(f"✅ Naive Bayes: {naive_bayes_result.get('label', 'error')} ({naive_bayes_result.get('confidence', 0.0):.3f})")
        except Exception as e:
            print(f"❌ Naive Bayes failed: {e}")
            naive_bayes_result = {
                'error': str(e),
                'label': 'error',
                'confidence': 0.0,
                'sentiment_score': 0.0,
                'method': 'naive_bayes_failed'
            }

        # === LSTM MODEL ===
        print("🤖 Running LSTM model...")
        try:
            lstm_result = self.analyze_sentiment_with_lstm(text, "" if is_comment else title)
            print(f"✅ LSTM: {lstm_result.get('label', 'error')} ({lstm_result.get('confidence', 0.0):.3f})")
        except Exception as e:
            print(f"❌ LSTM failed: {e}")
            lstm_result = {
                'error': str(e),
                'label': 'error',
                'confidence': 0.0,
                'sentiment_score': 0.0,
                'method': 'lstm_failed'
            }

        # === DETERMINE BEST MODEL FOR FINAL SENTIMENT ===
        # Priority: LSTM > Naive Bayes > Error fallback
        if 'error' not in lstm_result:
            final_sentiment = {
                'score': lstm_result['sentiment_score'],
                'label': lstm_result['label'],
                'confidence': lstm_result['confidence'],
                'method': 'lstm_primary'
            }
            best_model = 'lstm'
        elif 'error' not in naive_bayes_result:
            final_sentiment = {
                'score': naive_bayes_result['sentiment_score'],
                'label': naive_bayes_result['label'],
                'confidence': naive_bayes_result['confidence'],
                'method': 'naive_bayes_primary'
            }
            best_model = 'naive_bayes'
        else:
            final_sentiment = {
                'label': 'error',
                'score': 0.0,
                'confidence': 0.0,
                'method': 'both_models_failed'
            }
            best_model = 'none'

        # === EXTRACT LINGUISTIC FEATURES ===
        try:
            linguistic_features = self.extract_linguistic_features(text_preprocessing, title_preprocessing)
        except Exception as e:
            logger.warning(f"Failed to extract linguistic features: {e}")
            linguistic_features = {
                'total_tokens': text_preprocessing.get('token_count', 0),
                'processed_tokens': text_preprocessing.get('processed_count', 0),
                'text_length': len(text)
            }

        # === MODEL AGREEMENT ANALYSIS ===
        model_agreement = {
            'labels_match': False,
            'confidence_difference': 0.0,
            'score_difference': 0.0,
            'agreement_level': 'unknown'
        }

        if 'error' not in naive_bayes_result and 'error' not in lstm_result:
            # Both models succeeded - analyze agreement
            nb_label = naive_bayes_result.get('label', 'neutral')
            lstm_label = lstm_result.get('label', 'neutral')
            nb_conf = naive_bayes_result.get('confidence', 0.0)
            lstm_conf = lstm_result.get('confidence', 0.0)
            nb_score = naive_bayes_result.get('sentiment_score', 0.0)
            lstm_score = lstm_result.get('sentiment_score', 0.0)

            model_agreement = {
                'labels_match': nb_label == lstm_label,
                'confidence_difference': abs(nb_conf - lstm_conf),
                'score_difference': abs(nb_score - lstm_score),
                'agreement_level': 'high' if nb_label == lstm_label and abs(nb_conf - lstm_conf) < 0.2 else 'low'
            }

        print(f"🔍 MODEL AGREEMENT: Labels match = {model_agreement['labels_match']}, Level = {model_agreement['agreement_level']}")

        # === RETURN DUAL MODEL RESULTS ===
        return {
            'text_length': len(text),
            'title_length': len(title) if not is_comment else 0,
            'preprocessing': {
                'text': text_preprocessing,
                'title': title_preprocessing,
                'combined_processed': text_preprocessing['processed_text']
            },
            
            # === SEPARATE MODEL RESULTS ===
            'naive_bayes_result': naive_bayes_result,
            'lstm_result': lstm_result,
            
            # === MODEL COMPARISON ===
            'model_agreement': model_agreement,
            'best_model': best_model,
            
            # === FINAL SENTIMENT (for compatibility) ===
            'final_sentiment': final_sentiment,
            
            # === METADATA ===
            'linguistic_features': linguistic_features,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'model_info': {
                'has_naive_bayes': self.trained_model is not None,
                'has_lstm': self.lstm_model is not None,
                'nb_classes': list(self.label_encoder.classes_) if self.label_encoder else [],
                'lstm_classes': list(self.lstm_label_encoder.classes_) if self.lstm_label_encoder else [],
                'analysis_type': 'dual_model_comparison'
            },
            
            # === CONFIDENCE ANALYSIS ===
            'confidence_analysis': {
                'nb_confidence': naive_bayes_result.get('confidence', 0.0),
                'lstm_confidence': lstm_result.get('confidence', 0.0),
                'average_confidence': (naive_bayes_result.get('confidence', 0.0) + lstm_result.get('confidence', 0.0)) / 2,
                'confidence_spread': abs(naive_bayes_result.get('confidence', 0.0) - lstm_result.get('confidence', 0.0))
            }
        }

    def load_trained_model(self):
        """Load the latest trained Naive Bayes model and components"""
        try:
            # ✅ FIXED: Look in the correct subdirectory
            model_dir = Path("models/naive_bayes")  # Changed from "models"
            
            if not model_dir.exists():
                logger.warning(f"[Naive Bayes] Model directory not found: {model_dir}")
                return
            
            # Look for tuned models first, then best models
            model_files = list(model_dir.glob("*tuned_model*.pkl"))
            if not model_files:
                model_files = list(model_dir.glob("*best_model*.pkl"))
            
            if not model_files:
                logger.warning("[Naive Bayes] No trained models found. Train model first.")
                return
            
            # Get the latest model file
            latest_model_file = max(model_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"[Naive Bayes] Loading model: {latest_model_file}")
            
            # ✅ FIXED: Extract timestamp from full filename
            filename = latest_model_file.name.replace('.pkl', '')
            parts = filename.split('_')
            if len(parts) >= 2:
                timestamp = f"{parts[-2]}_{parts[-1]}"  # Get date_time parts
            else:
                logger.error(f"Could not extract timestamp from filename: {filename}")
                return
            
            # ✅ FIXED: Look for supporting files in same directory
            vectorizer_file = model_dir / f"vectorizer_{timestamp}.pkl"
            label_encoder_file = model_dir / f"label_encoder_{timestamp}.pkl"
            
            # Check if supporting files exist
            if not vectorizer_file.exists():
                logger.error(f"[Naive Bayes] Vectorizer not found: {vectorizer_file}")
                return
            
            if not label_encoder_file.exists():
                logger.error(f"[Naive Bayes] Label encoder not found: {label_encoder_file}")
                return
            
            # Load the model and components
            with open(latest_model_file, 'rb') as f:
                self.trained_model = pickle.load(f)
            
            with open(vectorizer_file, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(label_encoder_file, 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            logger.info(f"✅ [Naive Bayes] Model loaded successfully from {latest_model_file.name}")
            
        except Exception as e:
            logger.error(f"❌ [Naive Bayes] Failed to load trained model: {e}")

    def load_lstm_model(self):
        """Load the trained LSTM model, tokenizer, and label encoder (clean, consistent output)"""
        model_dir = Path('models/lstm')
        self.lstm_model = None
        self.lstm_tokenizer = None
        self.lstm_label_encoder = None
        try:
            print("\n[LSTM] === Model Loading ===")
            if not model_dir.exists():
                print("[LSTM] ❌ Models directory not found!")
                logger.warning("[LSTM] Models directory not found. Train model first.")
                return
            lstm_models = sorted(model_dir.glob('lstm_model_*.h5'), key=lambda p: p.stat().st_mtime, reverse=True)
            if not lstm_models:
                print("[LSTM] ❌ No LSTM model files found!")
                logger.warning("[LSTM] No LSTM model files found. Train model first.")
                return
            model_path = lstm_models[0]
            print(f"[LSTM] Model file: {model_path.name}")
            parts = model_path.stem.split('_')
            timestamp = f"{parts[-2]}_{parts[-1]}" if len(parts) >= 2 else parts[-1]
            tokenizer_path = model_dir / f"tokenizer_{timestamp}.pkl"
            label_encoder_path = model_dir / f"label_encoder_{timestamp}.pkl"
            if not tokenizer_path.exists() or not label_encoder_path.exists():
                tokenizer_files = sorted(model_dir.glob('tokenizer_*.pkl'), key=lambda p: p.stat().st_mtime, reverse=True)
                label_files = sorted(model_dir.glob('label_encoder_*.pkl'), key=lambda p: p.stat().st_mtime, reverse=True)
                tokenizer_path = tokenizer_files[0] if tokenizer_files else None
                label_encoder_path = label_files[0] if label_files else None
            if tokenizer_path and label_encoder_path and tokenizer_path.exists() and label_encoder_path.exists():
                with open(tokenizer_path, "rb") as f:
                    self.lstm_tokenizer = pickle.load(f)
                with open(label_encoder_path, "rb") as f:
                    self.lstm_label_encoder = pickle.load(f)
                from tensorflow.keras.models import load_model
                self.lstm_model = load_model(model_path)
                print(f"[LSTM] ✅ Loaded model: {model_path.name}")
                print(f"[LSTM] ✅ Loaded tokenizer: {tokenizer_path.name}")
                print(f"[LSTM] ✅ Loaded label encoder: {label_encoder_path.name}")
                logger.info(f"[LSTM] Model, tokenizer, and label encoder loaded: {model_path.name}, {tokenizer_path.name}, {label_encoder_path.name}")
            else:
                print("[LSTM] ❌ Tokenizer or label encoder not found!")
                logger.warning("[LSTM] Tokenizer or label encoder not found. Train model first.")
                self.lstm_model = None
                self.lstm_tokenizer = None
                self.lstm_label_encoder = None
        except Exception as e:
            print(f"[LSTM] ❌ Error loading model: {e}")
            logger.error(f"[LSTM] Failed to load model: {e}")
            self.lstm_model = None
            self.lstm_tokenizer = None
            self.lstm_label_encoder = None
    
    def setup_malaysian_context(self):
        """Setup Malaysian tourism-specific context (reduced, model-based approach)"""
        # Keep only Malaysian location boosters for context enhancement
        self.malaysian_boosters = {
            'petronas towers': 0.4, 'batu caves': 0.3, 'langkawi': 0.4,
            'penang': 0.4, 'malacca': 0.3, 'cameron highlands': 0.3,
            'truly asia': 0.5, 'malaysia boleh': 0.4,
            'kuala lumpur': 0.3, 'kl': 0.3, 'johor bahru': 0.2,
            'sabah': 0.3, 'sarawak': 0.3, 'borneo': 0.3
        }
        
        # Remove hardcoded positive/negative keywords - let the model decide!
        # self.positive_keywords = {}  # REMOVED
        # self.negative_keywords = {}  # REMOVED
        
        logger.info("✅ Malaysian context setup (model-based sentiment)")
    
    def setup_nltk_preprocessing(self):
        """Setup NLTK preprocessing tools"""
        if NLP_AVAILABLE:
            # Initialize NLTK tools
            self.stemmer = PorterStemmer()
            self.lemmatizer = WordNetLemmatizer()
            
            # Load stopwords for multiple languages
            try:
                self.english_stopwords = set(stopwords.words('english'))
                # Add custom tourism-specific stopwords
                custom_stopwords = {
                    'malaysia', 'malaysian', 'kuala', 'lumpur', 'kl', 'penang', 'langkawi',
                    'go', 'going', 'went', 'visit', 'visiting', 'visited', 'trip', 'travel',
                    'place', 'places', 'time', 'day', 'days', 'week', 'month', 'year',
                    'like', 'would', 'could', 'should', 'really', 'also', 'get', 'got'
                }
                self.stopwords = self.english_stopwords.union(custom_stopwords)
                logger.info(f"✅ NLTK preprocessing initialized with {len(self.stopwords)} stopwords")
            except:
                self.stopwords = set()
                logger.warning("⚠️ Could not load stopwords")
        else:
            self.stemmer = None
            self.lemmatizer = None
            self.stopwords = set()
    def extract_linguistic_features(self, text_preprocessing, title_preprocessing):
        """Basic linguistic feature extraction (placeholder)"""
        return {
            'total_tokens': text_preprocessing.get('token_count', 0) + title_preprocessing.get('token_count', 0),
            'processed_tokens': text_preprocessing.get('processed_count', 0) + title_preprocessing.get('processed_count', 0),
            'text_length': len(text_preprocessing.get('original', "")) + len(title_preprocessing.get('original', ""))
        }
    
    def preprocess_text(self, text: str, use_stemming: bool = False, use_lemmatization: bool = True) -> Dict:
        """Advanced text preprocessing using NLTK"""
        if not text or not NLP_AVAILABLE:
            return {
                'original': text,
                'cleaned': text.lower() if text else '',
                'tokens': [],
                'processed_tokens': [],
                'processed_text': text.lower() if text else '',
                'token_count': 0,
                'filtered_count': 0,
                'processed_count': 0
            }
        
        # Store original text
        original_text = text
        
        # 1. Basic cleaning
        cleaned_text = self.basic_text_cleaning(text)
        
        # 2. Tokenization
        tokens = word_tokenize(cleaned_text.lower())
        
        # 3. Remove punctuation and non-alphabetic tokens
        alpha_tokens = [token for token in tokens if token.isalpha() and len(token) > 2]
        
        # 4. Stopword removal
        filtered_tokens = [token for token in alpha_tokens if token not in self.stopwords]
        
        # 5. POS tagging for better lemmatization
        pos_tagged = pos_tag(filtered_tokens) if filtered_tokens else []
        
        # 6. Stemming or Lemmatization
        processed_tokens = []
        if use_lemmatization and self.lemmatizer:
            for word, pos in pos_tagged:
                # Convert POS tag to WordNet format
                wordnet_pos = self.get_wordnet_pos(pos)
                lemmatized = self.lemmatizer.lemmatize(word, wordnet_pos)
                processed_tokens.append(lemmatized)
        elif use_stemming and self.stemmer:
            processed_tokens = [self.stemmer.stem(token) for token, _ in pos_tagged]
        else:
            processed_tokens = [token for token, _ in pos_tagged]
        
        # 7. Create processed text
        processed_text = ' '.join(processed_tokens)
        
        return {
            'original': original_text,
            'cleaned': cleaned_text,
            'tokens': tokens,
            'filtered_tokens': filtered_tokens,
            'pos_tagged': pos_tagged,
            'processed_tokens': processed_tokens,
            'processed_text': processed_text,
            'token_count': len(tokens),
            'filtered_count': len(filtered_tokens),
            'processed_count': len(processed_tokens)
        }
    
    def basic_text_cleaning(self, text: str) -> str:
        """Basic text cleaning before tokenization"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove Reddit-specific patterns
        text = re.sub(r'/u/\w+', '', text)  # Remove username mentions
        text = re.sub(r'/r/\w+', '', text)  # Remove subreddit mentions
        text = re.sub(r'\[deleted\]|\[removed\]', '', text)  # Remove deleted content markers
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def get_wordnet_pos(self, treebank_tag: str) -> str:
        """Convert TreeBank POS tags to WordNet format for better lemmatization"""
        if treebank_tag.startswith('J'):
            return 'a'  # adjective
        elif treebank_tag.startswith('V'):
            return 'v'  # verb
        elif treebank_tag.startswith('N'):
            return 'n'  # noun
        elif treebank_tag.startswith('R'):
            return 'r'  # adverb
        else:
            return 'n'  # default to noun
    
    def extract_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """Extract n-grams from tokens for additional feature analysis"""
        if len(tokens) < n:
            return []
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i + n])
            ngrams.append(ngram)
        
        return ngrams

    def analyze_sentiment_with_naive_bayes(self, text: str, title: str = "") -> Dict:
        """Use trained Naive Bayes model for sentiment analysis"""
        if not self.trained_model or not self.label_encoder:
            raise Exception("❌ Trained model not available! Train the model first using: python train_naive_bayes_model.py")
        
        try:
            # FIXED: Don't re-combine title if we already have cleaned comment text
            # For comments, text should already be cleaned, title should be empty
            if title:
                # For posts: combine title and text
                combined_text = f"{title} {text}".strip()
            else:
                # For comments: use only the cleaned text (no title)
                combined_text = text.strip()
            
            print(f"🔍 TEXT GOING TO ML MODEL: {combined_text}")  # Debug output
            
            if not combined_text:
                return {
                    'sentiment_score': 0.0,
                    'label': 'neutral',
                    'confidence': 0.0,
                    'method': 'trained_model',
                    'probabilities': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
                }
            
            # Preprocess text using same pipeline as training
            processed_text = self.preprocess_text(combined_text)
            
            print(f"🔍 NLTK PREPROCESSED: {processed_text['processed_text']}")  # Debug output
            
            if not processed_text['processed_text']:
                # If preprocessing results in empty text, use basic cleaning
                cleaned_text = combined_text.lower().strip()
                if not cleaned_text:
                    return {
                        'sentiment_score': 0.0,
                        'label': 'neutral', 
                        'confidence': 0.0,
                        'method': 'trained_model',
                        'probabilities': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
                    }
                input_text = cleaned_text
            else:
                input_text = processed_text['processed_text']
            
            print(f"🔍 FINAL INPUT TO ML MODEL: {input_text}")  # Debug output
            
            # Get prediction and probabilities
            prediction = self.trained_model.predict([input_text])[0]
            probabilities = self.trained_model.predict_proba([input_text])[0]
            
            # Map prediction to label
            predicted_label = self.label_encoder.classes_[prediction]
            
            # Create probability dictionary
            prob_dict = {}
            for i, label in enumerate(self.label_encoder.classes_):
                prob_dict[label] = float(probabilities[i])
            
            # Calculate sentiment score (-1 to +1)
            if predicted_label == 'positive':
                sentiment_score = prob_dict['positive'] - prob_dict['negative']
            elif predicted_label == 'negative':
                sentiment_score = prob_dict['negative'] - prob_dict['positive']
            else:  # neutral
                sentiment_score = 0.0
            
            # Calculate confidence (highest probability)
            confidence = float(max(probabilities))
            
            # Apply Malaysian context boost
            malaysian_boost = self.get_malaysian_context_boost(combined_text.lower())
            if malaysian_boost > 0:
                confidence = min(1.0, confidence + malaysian_boost * 0.1)
                logger.debug(f"Applied Malaysian boost: {malaysian_boost}")
            
            return {
                'sentiment_score': sentiment_score,
                'label': predicted_label,
                'confidence': confidence,
                'method': 'trained_model',
                'probabilities': prob_dict,
                'preprocessing_quality': processed_text.get('processing_quality', 'unknown'),
                'malaysian_boost': malaysian_boost
            }
            
        except Exception as e:
            logger.error(f"❌ Trained model prediction failed: {e}")
            raise Exception(f"Sentiment analysis failed: {e}. Ensure trained model is available.")
        
    def analyze_sentiment_with_lstm(self, text: str, title: str = "") -> Dict:
        """Use trained LSTM model for sentiment analysis"""
        if not self.lstm_model or not self.lstm_tokenizer or not self.lstm_label_encoder:
            raise Exception("❌ LSTM model not available! Train the model first using: train_lstm_sentiment_model.py")

        # Match Naive Bayes logic: combine title and text for posts, just text for comments
        if title:
            combined_text = f"{title} {text}".strip()
        else:
            combined_text = text.strip()
        print(f"🔍 TEXT GOING TO LSTM MODEL: {combined_text}")

        # Use the same preprocessing as Naive Bayes
        processed_text = self.preprocess_text(combined_text, use_lemmatization=True)
        print(f"🔍 LSTM NLTK PREPROCESSED: {processed_text['processed_text']}")  # Debug output
        # Add this line to show the final input to the LSTM model (tokenizer input)
        print(f"🔍 FINAL INPUT TO LSTM MODEL: {processed_text['processed_text']}")
        if not processed_text["processed_text"]:
            return {
                'sentiment_score': 0.0,
                'label': 'neutral',
                'confidence': 0.0,
                'method': 'lstm_model',
                'probabilities': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34}
            }

        # Use the fully preprocessed text as input to the tokenizer
        sequence = self.lstm_tokenizer.texts_to_sequences([processed_text["processed_text"]])
        padded = pad_sequences(sequence, maxlen=100)
        probabilities = self.lstm_model.predict(padded)[0]

        idx = np.argmax(probabilities)
        predicted_label = self.lstm_label_encoder.classes_[idx]
        confidence = float(probabilities[idx])
        prob_dict = {self.lstm_label_encoder.classes_[i]: float(p) for i, p in enumerate(probabilities)}

        if predicted_label == "positive":
            sentiment_score = prob_dict["positive"] - prob_dict.get("negative", 0.0)
        elif predicted_label == "negative":
            sentiment_score = prob_dict["negative"] - prob_dict.get("positive", 0.0)
        else:
            sentiment_score = 0.0

        malaysian_boost = self.get_malaysian_context_boost(combined_text.lower())
        if malaysian_boost > 0:
            confidence = min(1.0, confidence + malaysian_boost * 0.1)
            logger.debug(f"Applied Malaysian boost: {malaysian_boost}")

        return {
            'sentiment_score': sentiment_score,
            'label': predicted_label,
            'confidence': confidence,
            'method': 'lstm_model',
            'probabilities': prob_dict,
            'preprocessing_quality': processed_text.get('processing_quality', 'unknown'),
            'malaysian_boost': malaysian_boost
        }

    def get_malaysian_context_boost(self, text: str) -> float:
        """Calculate Malaysian tourism context boost"""
        boost = 0.0
        text_lower = text.lower()
        
        for keyword, value in self.malaysian_boosters.items():
            if keyword in text_lower:
                boost += value
        
        return min(boost, 1.0)  # Cap at 1.0

    def _empty_preprocessing_result(self, text: str) -> Dict:
        """Return empty preprocessing result for empty/null inputs"""
        return {
            'original': text,
            'cleaned': text.lower() if text else '',
            'tokens': [],
            'filtered_tokens': [],
            'pos_tagged': [],
            'processed_tokens': [],
            'processed_text': text.lower() if text else '',
            'token_count': 0,
            'filtered_count': 0,
            'processed_count': 0
        }
    
    def analyze_sentiment(self, text: str, title: str = "") -> Dict:
        """Run both LSTM and Naive Bayes models for every input and return both results"""
        print(f"\n🔍 ANALYZE_SENTIMENT INPUT - Text: {text[:100]}...")
        print(f"🔍 ANALYZE_SENTIMENT INPUT - Title: {title}")

        is_comment = not title or title == ""
        text_preprocessing = self.preprocess_text(text, use_lemmatization=True)
        title_preprocessing = self._empty_preprocessing_result("") if is_comment else self.preprocess_text(title, use_lemmatization=True)

        # Run both models
        try:
            nb_result = self.analyze_sentiment_with_naive_bayes(text, "" if is_comment else title)
        except Exception as e:
            nb_result = {'error': str(e)}
        try:
            lstm_result = self.analyze_sentiment_with_lstm(text, "" if is_comment else title)
        except Exception as e:
            lstm_result = {'error': str(e)}

        # Pick one as final (prefer LSTM if available)
        if 'error' not in lstm_result:
            final_sentiment = {
                'score': lstm_result['sentiment_score'],
                'label': lstm_result['label'],
                'confidence': lstm_result['confidence'],
                'method': lstm_result['method']
            }
        elif 'error' not in nb_result:
            final_sentiment = {
                'score': nb_result['sentiment_score'],
                'label': nb_result['label'],
                'confidence': nb_result['confidence'],
                'method': nb_result['method']
            }
        else:
            final_sentiment = {'label': 'error', 'score': 0.0, 'confidence': 0.0, 'method': 'none'}

        try:
            linguistic_features = self.extract_linguistic_features(text_preprocessing, title_preprocessing)
        except Exception as e:
            logger.warning(f"Failed to extract linguistic features: {e}")
            linguistic_features = {
                'total_tokens': text_preprocessing.get('token_count', 0),
                'processed_tokens': text_preprocessing.get('processed_count', 0),
                'text_length': len(text)
            }

        return {
            'text_length': len(text),
            'title_length': len(title) if not is_comment else 0,
            'preprocessing': {
                'text': text_preprocessing,
                'title': title_preprocessing,
                'combined_processed': text_preprocessing['processed_text']
            },
            'naive_bayes_result': nb_result,
            'lstm_result': lstm_result,
            'linguistic_features': linguistic_features,
            'final_sentiment': final_sentiment,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'model_info': {
                'has_trained_model': self.trained_model is not None,
                'model_classes': list(self.label_encoder.classes_) if self.label_encoder else [],
                'fallback_used': False
            }
        }


class MalaysianTourismConsumer:
    """Enhanced Kafka consumer for Malaysian tourism sentiment analysis"""
    
    def __init__(self, bootstrap_servers: str = '127.0.0.1:9092', topic_name: str = 'malaysian-tourism-sentiment', group_id: str = 'sentiment-group'):
        """Initialize consumer for REAL-TIME streaming only"""
        self.setup_directories()
        self.setup_sentiment_analyzer()
        
        # ONLY real-time mode
        self.bootstrap_servers = bootstrap_servers
        self.topic_name = topic_name
        self.group_id = group_id
        self.should_run = True
        self.real_time_mode = True
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=[bootstrap_servers],
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True
        )
        
        self.load_configuration()
        self.setup_analytics()
        self.setup_csv_output()
        self.running = False
        
        logger.info(f"✅ Real-time consumer initialized ONLY")
        logger.info(f"📊 Kafka: {bootstrap_servers} | Topic: {topic_name}")

    def setup_directories(self):
        """Create necessary directories"""
        dirs = ['logs', 'data/processed', 'data/analytics', 'data/dashboard']
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        logger.info("✅ Consumer directories created/verified")
    
    def setup_sentiment_analyzer(self):
        """Initialize sentiment analyzer"""
        self.sentiment_analyzer = MalaysianTourismSentimentAnalyzer()
        logger.info("✅ Sentiment analyzer initialized")
    
    def load_configuration(self):
        """Load configuration from environment variables"""
        self.batch_size = int(os.getenv('CONSUMER_BATCH_SIZE', 100))
        self.analytics_interval = int(os.getenv('ANALYTICS_INTERVAL', 60))  # seconds
        self.dashboard_update_interval = int(os.getenv('DASHBOARD_UPDATE_INTERVAL', 300))  # 5 minutes
        
        # Output file configuration
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.processed_file = f'data/processed/sentiment_analysis_{timestamp}.jsonl'
        self.analytics_file = f'data/analytics/tourism_sentiment_report_{timestamp}.json'
        self.dashboard_file = f'data/dashboard/realtime_dashboard_data.json'
        
        logger.info(f"📋 Consumer configuration loaded:")
        logger.info(f"  Batch size: {self.batch_size}")
        logger.info(f"  Analytics interval: {self.analytics_interval}s")
        logger.info(f"  Output file: {self.processed_file}")
    
    def setup_analytics(self):
        """Setup analytics tracking"""
        self.stats = {
            'messages_processed': 0,
            'posts_analyzed': 0,
            'comments_analyzed': 0,
            'sentiment_distribution': defaultdict(int),
            'malaysia_related_count': 0,
            'processing_errors': 0,
            'start_time': datetime.now(),
            'last_analytics_update': datetime.now()
        }
        
        # Recent sentiment trends (sliding window)
        self.recent_sentiments = deque(maxlen=1000)
        self.hourly_sentiment = defaultdict(list)
        
        logger.info("✅ Analytics tracking initialized")
    
    def setup_csv_output(self):
        """Setup CSV output for sentiment results"""
        # Create CSV filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.csv_filename = f'data/processed/sentiment_results_{timestamp}.csv'
        
        # Create CSV file with headers
        try:
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header row with both original and cleaned text
                writer.writerow([
                    'original_text',
                    'cleaned_text',  # New: Add cleaned text column
                    'final_label', 
                    'confidence_score',
                    'method_used',
                    'timestamp'
                ])
            
            logger.info(f"✅ CSV output initialized: {self.csv_filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize CSV output: {e}")
            self.csv_filename = None
    
    def save_to_csv(self, processed_message: Dict):
        """Save sentiment analysis results to CSV using unified pipeline data"""
        if not self.csv_filename:
            return
        
        try:
            # Step 1: Get original content (for human readability)
            title = processed_message.get('title', '')
            original_content = processed_message.get('original_content', '')
            original_text = f"{title} {original_content}".strip()
            
            # Step 2: Get fully processed text (comment-cleaned + NLTK-processed)
            sentiment_analysis = processed_message.get('sentiment_analysis', {})
            preprocessing = sentiment_analysis.get('preprocessing', {})
            
            # Extract the combined processed text (what the ML model actually saw)
            if preprocessing:
                cleaned_text = preprocessing.get('combined_processed', '')
            else:
                # Fallback: use the comment-cleaned content
                cleaned_content = processed_message.get('content', '')
                cleaned_text = self.basic_clean_text(cleaned_content)
            
            # Step 3: Get sentiment analysis results
            final_sentiment = sentiment_analysis.get('final_sentiment', {})
            final_label = final_sentiment.get('label', 'unknown')
            confidence_score = final_sentiment.get('confidence', 0.0)
            method_used = final_sentiment.get('method', 'unknown')
            timestamp = processed_message.get('processing_timestamp', datetime.now(timezone.utc).isoformat())
            
            # Step 4: Clean text for CSV format (remove newlines, excessive whitespace)
            original_text_cleaned = ' '.join(original_text.split())
            cleaned_text_for_csv = ' '.join(cleaned_text.split()) if cleaned_text else ''
            
            # Step 5: Truncate very long text to prevent CSV issues
            if len(original_text_cleaned) > 800:
                original_text_cleaned = original_text_cleaned[:797] + '...'
            
            if len(cleaned_text_for_csv) > 500:
                cleaned_text_for_csv = cleaned_text_for_csv[:497] + '...'
            
            # Step 6: Write to CSV with unified pipeline results
            with open(self.csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    original_text_cleaned,      # Column 1: Original Reddit content (with "Comment on:")
                    cleaned_text_for_csv,       # Column 2: Fully processed text (comment-cleaned + NLTK)
                    final_label,                # Column 3: positive/negative/neutral
                    round(confidence_score, 4), # Column 4: ML model confidence
                    method_used,                # Column 5: Always 'trained_model'
                    timestamp                   # Column 6: Processing timestamp
                ])
            
            print(f"📄 CSV SAVED - Original: {original_text_cleaned[:50]}... → Processed: {cleaned_text_for_csv[:50]}... → {final_label}")
            
        except Exception as e:
            logger.error(f"Failed to save to CSV: {e}")
    
    def basic_clean_text(self, text: str) -> str:
        """Basic text cleaning for fallback use"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove Reddit-specific patterns
        text = re.sub(r'/u/\w+', '', text)
        text = re.sub(r'/r/\w+', '', text)
        text = re.sub(r'\[deleted\]|\[removed\]', '', text)
        
        # Remove extra whitespace and convert to lowercase
        text = re.sub(r'\s+', ' ', text)
        text = text.strip().lower()
        
        return text
    
    def clean_comment_content(self, content: str) -> str:
        if not content:
            return content
        
        print(f"🔍 FULL CONTENT TO CLEAN: {content}")  # Show FULL content for debugging
        
        # Handle the specific pattern: "Comment on: [post content] ... [actual comment]"
        if content.startswith("Comment on:"):
            print("✅ Found 'Comment on:' pattern")
            
            # Look for the " ... " separator
            if " ... " in content:
                print("✅ Found ' ... ' separator")
                # Split by " ... " and take everything after it (the actual comment)
                parts = content.split(" ... ", 1)
                if len(parts) > 1:
                    actual_comment = parts[1].strip()
                    if actual_comment:  # Make sure we have actual content
                        print(f"🔍 EXTRACTED COMMENT: {actual_comment}")
                        return actual_comment
            else:
                print("❌ No ' ... ' separator found")
                print(f"🔍 Looking for other separators...")
            
            # Fallback: if no " ... " found, try other separators
            fallback_separators = [" - ", " | ", "\n"]
            for separator in fallback_separators:
                if separator in content:
                    print(f"✅ Found fallback separator: '{separator}'")
                    parts = content.split(separator, 1)
                    if len(parts) > 1:
                        potential_comment = parts[1].strip()
                        if potential_comment and len(potential_comment) > 10:
                            print(f"🔍 EXTRACTED WITH FALLBACK: {potential_comment}")
                            return potential_comment
        else:
            print("❌ Does not start with 'Comment on:'")
        
        print("❌ No cleaning applied, returning original")
        return content

    def process_message(self, message: Dict) -> Optional[Dict]:
        """Process individual message with unified sentiment analysis pipeline"""
        try:
            # Step 1: Extract original content
            original_content = message.get('content', '')
            title = message.get('title', '')
            
            print(f"🔍 PROCESSING MESSAGE: content_type = {message.get('content_type')}")
            
            # Step 2: Comment cleaning (removes "Comment on:" metadata)
            cleaned_content = original_content
            is_comment = False
            
            if message.get('content_type') == 'comment' or 'Comment on:' in original_content:
                print("🧹 CLEANING COMMENT CONTENT")
                cleaned_content = self.clean_comment_content(original_content)
                is_comment = True
                
                # Log the cleaning for debugging
                if original_content != cleaned_content:
                    print(f"✅ COMMENT CLEANING SUCCESSFUL!")
                    print(f"📝 Original: {original_content[:100]}...")
                    print(f"📝 Cleaned:  {cleaned_content[:100]}...")
                    logger.debug(f"Comment cleaned: '{original_content[:100]}...' -> '{cleaned_content[:100]}...'")
                else:
                    print(f"❌ NO COMMENT CLEANING APPLIED!")
            else:
                print("ℹ️ Not a comment, no cleaning needed")
        
            if not cleaned_content:
                return None
            
            # Step 3: Store both versions in enriched message
            enriched_message = message.copy()
            enriched_message['original_content'] = original_content  # For CSV column 1 (human-readable)
            enriched_message['content'] = cleaned_content           # For processing pipeline
            
            # Step 4: Sentiment analysis pipeline 
            # For comments: Don't pass title to avoid mixing post metadata with comment
            if is_comment:
                print(f"🤖 Running ML sentiment analysis on COMMENT ONLY (no title)...")
                sentiment_results = self.sentiment_analyzer.analyze_sentiment(cleaned_content, "")  # Empty title
            else:
                print(f"🤖 Running ML sentiment analysis on POST (with title)...")
                sentiment_results = self.sentiment_analyzer.analyze_sentiment(cleaned_content, title)
            
            # Step 5: Store results
            enriched_message['sentiment_analysis'] = sentiment_results
            enriched_message['processing_timestamp'] = datetime.now(timezone.utc).isoformat()
            enriched_message['is_comment'] = is_comment  # Track if it's a comment
            
            # Step 6: Update analytics and save to CSV
            self.update_analytics(enriched_message)
            self.save_to_csv(enriched_message)
            
            # Step 7: Real-time logging (from realtime consumer)
            if self.real_time_mode:
                final_sentiment = sentiment_results.get('final_sentiment', {})
                label = final_sentiment.get('label', 'unknown')
                confidence = final_sentiment.get('confidence', 0.0)
                method = final_sentiment.get('method', 'unknown')
                
                # Log the real-time result
                logger.info(f"[SENTIMENT] {original_content[:100]}{'...' if len(original_content) > 100 else ''} → {label.upper()} ({confidence:.2f}) [{method}]")
            
            return enriched_message
    
        except Exception as e:
            logger.error(f"Error processing message {message.get('id', 'unknown')}: {e}")
            self.stats['processing_errors'] += 1
            if "Trained model not available" in str(e):
                logger.error("❌ CRITICAL: Trained model required. Run: python train_naive_bayes_model.py")
                raise Exception(f"Consumer stopped - trained model required: {e}")
            return None
    
    def update_analytics(self, processed_message: Dict):
        """Update analytics with processed message"""
        self.stats['messages_processed'] += 1
        
        # Count content types
        if processed_message.get('content_type') == 'post':
            self.stats['posts_analyzed'] += 1
        elif processed_message.get('content_type') == 'comment':
            self.stats['comments_analyzed'] += 1
        
        # Track Malaysia-related content
        if processed_message.get('is_malaysia_related', False):
            self.stats['malaysia_related_count'] += 1
        
        # Track sentiment distribution
        sentiment_label = processed_message['sentiment_analysis']['final_sentiment']['label']
        self.stats['sentiment_distribution'][sentiment_label] += 1
        
        # Add to recent sentiments for trend analysis
        sentiment_score = processed_message['sentiment_analysis']['final_sentiment']['score']
        timestamp = datetime.now()
        self.recent_sentiments.append({
            'timestamp': timestamp,
            'score': sentiment_score,
            'label': sentiment_label
        })
        
        # Hourly aggregation
        hour_key = timestamp.strftime('%Y-%m-%d %H:00')
        self.hourly_sentiment[hour_key].append(sentiment_score)
    
    def save_processed_message(self, processed_message: Dict):
        """Save processed message to file"""
        try:
            with open(self.processed_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(processed_message, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to save processed message: {e}")
    
    def generate_analytics_report(self):
        """Generate comprehensive analytics report"""
        current_time = datetime.now()
        runtime = current_time - self.stats['start_time']
        
        # Calculate sentiment trends
        if self.recent_sentiments:
            recent_scores = [s['score'] for s in self.recent_sentiments]
            avg_sentiment = sum(recent_scores) / len(recent_scores)
            sentiment_trend = self.calculate_sentiment_trend()
        else:
            avg_sentiment = 0.0
            sentiment_trend = 'stable'
        
        # Calculate hourly averages
        hourly_averages = {}
        for hour, scores in self.hourly_sentiment.items():
            if scores:
                hourly_averages[hour] = sum(scores) / len(scores)
        
        report = {
            'timestamp': current_time.isoformat(),
            'runtime': str(runtime),
            'processing_stats': dict(self.stats),
            'sentiment_summary': {
                'total_analyzed': self.stats['messages_processed'],
                'malaysia_related_percentage': (
                    self.stats['malaysia_related_count'] / max(1, self.stats['messages_processed']) * 100
                ),
                'average_sentiment': avg_sentiment,
                'sentiment_trend': sentiment_trend,
                'distribution': dict(self.stats['sentiment_distribution'])
            },
            'hourly_sentiment_averages': hourly_averages,
            'processing_rate': {
                'messages_per_minute': self.stats['messages_processed'] / max(1, runtime.total_seconds() / 60),
                'error_rate': self.stats['processing_errors'] / max(1, self.stats['messages_processed']) * 100
            }
        }
        
        return report
    
    def calculate_sentiment_trend(self) -> str:
        """Calculate sentiment trend from recent data"""
        if len(self.recent_sentiments) < 10:
            return 'insufficient_data'
        
        # Compare first and second half of recent sentiments
        half_point = len(self.recent_sentiments) // 2
        first_half_avg = sum(s['score'] for s in list(self.recent_sentiments)[:half_point]) / half_point
        second_half_avg = sum(s['score'] for s in list(self.recent_sentiments)[half_point:]) / (len(self.recent_sentiments) - half_point)
        
        difference = second_half_avg - first_half_avg
        
        if difference > 0.1:
            return 'improving'
        elif difference < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def save_analytics_report(self):
        """Save analytics report to file"""
        try:
            report = self.generate_analytics_report()
            
            # Save detailed report
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Save dashboard data (simplified for real-time display)
            dashboard_data = {
                'last_updated': datetime.now().isoformat(),
                'total_processed': self.stats['messages_processed'],
                'malaysia_related': self.stats['malaysia_related_count'],
                'sentiment_distribution': dict(self.stats['sentiment_distribution']),
                'average_sentiment': report['sentiment_summary']['average_sentiment'],
                'sentiment_trend': report['sentiment_summary']['sentiment_trend'],
                'processing_rate': report['processing_rate']['messages_per_minute']
            }
            
            with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"📊 Analytics report saved: {self.analytics_file}")
            
        except Exception as e:
            logger.error(f"Failed to save analytics report: {e}")
    
    def log_progress(self):
        """Log current processing progress"""
        runtime = datetime.now() - self.stats['start_time']
        
        logger.info("📊 PROCESSING PROGRESS")
        logger.info(f"  Runtime: {runtime}")
        logger.info(f"  Messages processed: {self.stats['messages_processed']}")
        logger.info(f"  Posts: {self.stats['posts_analyzed']}, Comments: {self.stats['comments_analyzed']}")
        logger.info(f"  Malaysia-related: {self.stats['malaysia_related_count']}")
        logger.info(f"  Sentiment distribution: {dict(self.stats['sentiment_distribution'])}")
        logger.info(f"  Processing errors: {self.stats['processing_errors']}")
    
    def consume_from_kafka(self):
        """Consume messages from Kafka for real-time processing"""
        logger.info("🔍 Starting real-time sentiment analysis...")
        logger.info("📊 Waiting for messages...")
        
        try:
            message_count = 0
            
            for message in self.consumer:
                if not self.should_run:
                    break
                
                message_count += 1
                
                # Process the message
                reddit_data = message.value
                result = self.process_message(reddit_data)
                
                if result:
                    # Save processed message
                    self.save_processed_message(result)
                
                # Log progress every 10 messages
                if message_count % 10 == 0:
                    logger.info(f"📊 Processed {message_count} messages")
                
        except KeyboardInterrupt:
            logger.info("🛑 Consumer stopped by user")
        except Exception as e:
            logger.error(f"❌ Consumer error: {e}")
        finally:
            self.consumer.close()
            logger.info("✅ Consumer closed")
    
    def run_kafka_consumer(self):
        """Run Kafka consumer loop"""
        logger.info("🚀 Starting Kafka consumer...")
        
        try:
            processed_batch = []
            
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    processed_message = self.process_message(message.value)
                    
                    if processed_message:
                        processed_batch.append(processed_message)
                        
                        # Process in batches
                        if len(processed_batch) >= self.batch_size:
                            self.save_batch(processed_batch)
                            processed_batch = []
                    
                    # Periodic analytics update
                    if (datetime.now() - self.stats['last_analytics_update']).total_seconds() > self.analytics_interval:
                        self.save_analytics_report()
                        self.log_progress()
                        self.stats['last_analytics_update'] = datetime.now()
                        
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")
                    self.stats['processing_errors'] += 1
            
            # Save any remaining messages in batch
            if processed_batch:
                self.save_batch(processed_batch)
                
        except KeyboardInterrupt:
            logger.info("🛑 Consumer stopped by user")
        except Exception as e:
            logger.error(f"❌ Kafka consumer error: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
    
    def save_batch(self, batch: List[Dict]):
        """Save a batch of processed messages"""
        for message in batch:
            self.save_processed_message(message)
        logger.info(f"💾 Saved batch of {len(batch)} processed messages")
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.should_run = False
    
    def run(self):
        """Main consumer execution"""
        logger.info("🚀 Starting Malaysian Tourism Sentiment Consumer")
        logger.info("=" * 60)
        
        self.running = True
        
        try:
            if self.real_time_mode:
                # Real-time Kafka consumption
                self.consume_from_kafka()
            else:
                # Start analytics reporting thread
                analytics_thread = threading.Thread(
                    target=self.periodic_analytics_update,
                    daemon=True
                )
                analytics_thread.start()
                
                # Run Kafka consumer
                self.run_kafka_consumer()
            
            # Final analytics report
            self.save_analytics_report()
            self.log_progress()
            
            logger.info("✅ SENTIMENT ANALYSIS COMPLETED!")
            logger.info(f"📊 Total processed: {self.stats['messages_processed']} messages")
            logger.info(f"🇲🇾 Malaysia-related: {self.stats['malaysia_related_count']}")
            logger.info(f"📈 Sentiment distribution: {dict(self.stats['sentiment_distribution'])}")
            logger.info(f"📁 Results saved to: {self.processed_file}")
            logger.info(f"📊 Analytics report: {self.analytics_file}")
            logger.info(f"📄 CSV results: {self.csv_filename}")
            
        except Exception as e:
            logger.error(f"❌ Consumer execution failed: {e}")
            raise
        finally:
            self.running = False
            logger.info("🔚 Consumer shutdown complete")
    
    def periodic_analytics_update(self):
        """Periodic analytics update in separate thread"""
        while self.running:
            time.sleep(self.dashboard_update_interval)
            if self.running:  # Check again after sleep
                self.save_analytics_report()

    def create_index_template(self) -> bool:
        """Create Elasticsearch index template with proper mappings"""
        try:
            template_name = f"{self.index_name}-template"
            
            # Define proper field mappings
            template_body = {
                "index_patterns": [f"{self.index_name}-*"],
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "index.refresh_interval": "1s"
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {
                            "type": "date",
                            "format": "strict_date_optional_time||epoch_millis"
                        },
                        "sentiment_label": {
                            "type": "keyword"
                        },
                        "confidence_score": {
                            "type": "float"
                        },
                        "processing_timestamp": {
                            "type": "date",
                            "format": "strict_date_optional_time||epoch_millis"
                        },
                        "original_text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "method_used": {
                            "type": "keyword"
                        },
                        "content_type": {
                            "type": "keyword"
                        },
                        "is_malaysia_related": {
                            "type": "boolean"
                        },
                        "subreddit": {
                            "type": "keyword"
                        },
                        "title": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "author": {
                            "type": "keyword"
                        },
                        "score": {
                            "type": "integer"
                        },
                        "text_length": {
                            "type": "integer"
                        },
                        "created_utc": {
                            "type": "date",
                            "format": "strict_date_optional_time||epoch_millis"
                        },
                        "index_date": {
                            "type": "keyword"
                        },
                        "hour_of_day": {
                            "type": "integer"
                        },
                        "sentiment_numeric": {
                            "type": "integer"
                        }
                    }
                }
            }
            
            # Create or update template
            response = self.es.indices.put_template(
                name=template_name,
                body=template_body
            )
            
            logger.info(f"✅ Index template '{template_name}' created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create index template: {e}")
            return False
    
    def create_index_pattern_api(self) -> bool:
        """Create index pattern using Kibana API"""
        try:
            import requests
            
            # Delete existing index pattern if it exists
            delete_url = f"http://{self.kibana_host}/api/saved_objects/index-pattern/{self.index_name}-*"
            try:
                requests.delete(delete_url, headers={'kbn-xsrf': 'true'}, timeout=10)
            except:
                pass  # Ignore if doesn't exist
            
            # Create new index pattern
            pattern_data = {
                "attributes": {
                    "title": f"{self.index_name}-*",
                    "timeFieldName": "@timestamp",
                    "fields": json.dumps([
                        {"name": "@timestamp", "type": "date", "searchable": True, "aggregatable": True},
                        {"name": "sentiment_label", "type": "string", "searchable": True, "aggregatable": True},
                        {"name": "confidence_score", "type": "number", "searchable": True, "aggregatable": True},
                        {"name": "original_text", "type": "string", "searchable": True, "aggregatable": False},
                        {"name": "method_used", "type": "string", "searchable": True, "aggregatable": True},
                        {"name": "content_type", "type": "string", "searchable": True, "aggregatable": True},
                        {"name": "subreddit", "type": "string", "searchable": True, "aggregatable": True},
                        {"name": "author", "type": "string", "searchable": True, "aggregatable": True},
                        {"name": "score", "type": "number", "searchable": True, "aggregatable": True},
                        {"name": "text_length", "type": "number", "searchable": True, "aggregatable": True}
                    ])
                }
            }
            
            create_url = f"http://{self.kibana_host}/api/saved_objects/index-pattern/{self.index_name}-pattern"
            
            response = requests.post(
                create_url,
                headers={
                    'kbn-xsrf': 'true',
                    'Content-Type': 'application/json'
                },
                json=pattern_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Index pattern created via API: {self.index_name}-*")
                return True
            else:
                logger.error(f"❌ Index pattern creation failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Index pattern API creation failed: {e}")
            return False

def send_to_dashboard(consumer, dashboard, processed_message):
    """Send processed message to dashboard (NO FILTERING - same as CSV)"""
    if not dashboard:
        return False
    
    try:
        # Extract sentiment data with NO filtering
        sentiment_analysis = processed_message.get('sentiment_analysis', {})
        final_sentiment = sentiment_analysis.get('final_sentiment', {})
        
        # Get current timestamp
        current_time = datetime.now(timezone.utc)
        
        # Create dashboard document with SAME content as CSV
        dashboard_doc = {
            '@timestamp': current_time.isoformat(),
            'sentiment_label': str(final_sentiment.get('label', 'unknown')),
            'confidence_score': float(final_sentiment.get('confidence', 0.0)),
            'processing_timestamp': current_time.isoformat(),
            
            # FULL ORIGINAL TEXT (no truncation like CSV)
            'original_text': str(processed_message.get('original_content', '')),  # ✅ REMOVED LENGTH LIMIT
            'processed_text': str(processed_message.get('processed_content', '')),  # ✅ ADD PROCESSED VERSION
            
            'method_used': str(final_sentiment.get('method', 'unknown')),
            'content_type': str(processed_message.get('content_type', 'reddit_post')),
            'is_malaysia_related': bool(processed_message.get('is_malaysia_related', True)),
            'subreddit': str(processed_message.get('subreddit', 'unknown')),
            
            # FULL TITLE (no truncation like CSV)
            'title': str(processed_message.get('title', '')),  # ✅ REMOVED LENGTH LIMIT
            
            'author': str(processed_message.get('author', 'unknown')),
            'score': int(processed_message.get('score', 0)),
            'text_length': len(str(processed_message.get('original_content', ''))),
            'created_utc': current_time.isoformat(),
            'index_date': current_time.strftime('%Y-%m-%d'),
            'hour_of_day': current_time.hour,
            'sentiment_numeric': 1 if final_sentiment.get('label') == 'positive' else (-1 if final_sentiment.get('label') == 'negative' else 0),
            
            # ADD ALL FIELDS FROM CSV
            'keywords_found': processed_message.get('keywords_found', []),
            'post_id': processed_message.get('post_id', ''),
            'comment_id': processed_message.get('comment_id', ''),
            'parent_id': processed_message.get('parent_id', ''),
            'permalink': processed_message.get('permalink', ''),
            'url': processed_message.get('url', ''),
            'num_comments': processed_message.get('num_comments', 0),
            'upvote_ratio': processed_message.get('upvote_ratio', 0.0),
            'created_timestamp': processed_message.get('created_utc', ''),
            'source': 'reddit'
        }
        
        # Log comparison with CSV
        logger.info(f"📋 CSV vs Dashboard - Same content length: {len(dashboard_doc['original_text'])}")
        logger.info(f"📋 Sentiment: {dashboard_doc['sentiment_label']} ({dashboard_doc['confidence_score']:.2f})")
        
        # Send to dashboard
        result = dashboard.index_document(dashboard_doc)
        if result:
            logger.info(f"✅ Dashboard indexed (full content): {dashboard_doc['sentiment_label']} ({dashboard_doc['confidence_score']:.2f})")
            return True
        else:
            logger.error("❌ Dashboard indexing failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Dashboard send failed: {e}")
        import traceback
        logger.error(f"📋 Full error: {traceback.format_exc()}")
        return False

def main(dashboard=None):
    """Main consumer function with dashboard integration"""
    logger.info("🔍 Starting sentiment analysis consumer...")
    
    try:
        # Create consumer in real-time mode
        consumer = MalaysianTourismConsumer(
            bootstrap_servers='127.0.0.1:9092',
            topic_name='malaysian-tourism-sentiment',
            group_id='sentiment-group'
        )
        
        # Store dashboard reference in consumer
        consumer.dashboard = dashboard
        
        # Store the original process_message method
        original_process_message = consumer.process_message
        
        def enhanced_process_message(message):
            """Enhanced process message with dashboard integration"""
            # Process message normally
            processed_message = original_process_message(message)
            
            # Send to dashboard if available and message was processed successfully
            if processed_message and dashboard:
                try:
                    send_to_dashboard(consumer, dashboard, processed_message)
                except Exception as e:
                    logger.error(f"❌ Dashboard integration error: {e}")
            
            return processed_message
        
        # Replace the process_message method
        consumer.process_message = enhanced_process_message
        
        # Run the consumer
        consumer.run()
        
        return 0  # Success
        
    except Exception as e:
        logger.error(f"❌ Consumer failed: {e}")
        return 1  # Error

if __name__ == "__main__":
    exit(main())