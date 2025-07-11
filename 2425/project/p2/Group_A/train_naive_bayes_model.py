"""
Malaysian Tourism Naive Bayes Sentiment Model Trainer
====================================================

This script trains a Naive Bayes classifier on the tourism dataset with
text, language, and label columns. Filters for English text and maps
uncertainty to neutral.

Features:
- Language filtering (English only)
- Three-class sentiment: positive, negative, neutral (uncertainty→neutral)
- Naive Bayes model training with cross-validation
- Text preprocessing using NLTK (same as consumer)
- Model evaluation and performance metrics
- Model persistence for integration with consumer

Author: Big Data & NLP Analytics Team
Date: July 2, 2025
"""
import os
import warnings
import pandas as pd
import numpy as np
import pickle
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any  # Add 'Any'
import subprocess
import sys

# === SUPPRESS ALL WARNINGS ===
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'     # Hide TensorFlow INFO & WARN
warnings.filterwarnings("ignore")            # Hide Python warnings
logging.getLogger('tensorflow').setLevel(logging.ERROR)  # Hide TensorFlow logs

# Scikit-learn imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.naive_bayes import MultinomialNB, GaussianNB, ComplementNB
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import (classification_report, confusion_matrix, 
                           accuracy_score, precision_recall_fscore_support)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

# Import NLTK preprocessing from your consumer
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.tag import pos_tag
    import re
    NLP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ NLTK not available: {e}")
    NLP_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/naive_bayes_training.log')
    ]
)
logger = logging.getLogger(__name__)

class MalaysianTourismNBTrainer:
    """Naive Bayes model trainer for Malaysian tourism sentiment analysis"""
    
    def __init__(self, dataset_path: str = "data/raw/malaysia_tourism_data.csv"):  # ✅ CHANGED
        """Initialize the trainer"""
        self.dataset_path = dataset_path
        self.setup_directories()
        self.setup_preprocessing()
        self.models = {}
        self.vectorizers = {}
        self.label_encoder = LabelEncoder()
        self.pipeline_stats = {
            'naive_bayes_trained': False,
            'lstm_trained': False
        }
        
    def setup_directories(self):
        """Create necessary directories"""
        dirs = ['models', 'logs', 'reports', 'data/processed']
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info("✅ Training directories created/verified")
    
    def setup_preprocessing(self):
        """Setup text preprocessing (same as consumer)"""
        if NLP_AVAILABLE:
            # Download NLTK resources
            resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
            for resource in resources:
                try:
                    nltk.download(resource, quiet=True)
                except:
                    pass
            
            self.stemmer = PorterStemmer()
            self.lemmatizer = WordNetLemmatizer()
            
            # Load stopwords (same as consumer)
            try:
                english_stopwords = set(stopwords.words('english'))
                custom_stopwords = {
                    'malaysia', 'malaysian', 'kuala', 'lumpur', 'kl', 'penang', 'langkawi',
                    'go', 'going', 'went', 'visit', 'visiting', 'visited', 'trip', 'travel',
                    'place', 'places', 'time', 'day', 'days', 'week', 'month', 'year',
                    'like', 'would', 'could', 'should', 'really', 'also', 'get', 'got'
                }
                self.stopwords = english_stopwords.union(custom_stopwords)
                logger.info(f"✅ Preprocessing setup with {len(self.stopwords)} stopwords")
            except:
                self.stopwords = set()
                logger.warning("⚠️ Could not load stopwords")
        else:
            self.stemmer = None
            self.lemmatizer = None
            self.stopwords = set()
    
    def load_dataset(self) -> pd.DataFrame:
        """Load and validate the CSV dataset (content, sentiment_label columns)"""
        try:
            logger.info(f"📂 Loading dataset from {self.dataset_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(self.dataset_path, encoding=encoding)
                    logger.info(f"✅ Dataset loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not load dataset with any encoding")
            
            logger.info(f"📊 Dataset shape: {df.shape}")
            logger.info(f"📋 Columns: {list(df.columns)}")
            
            # Validate required columns for new CSV structure
            required_columns = ['content', 'sentiment_label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # Try to find similar column names
                available_cols = df.columns.tolist()
                logger.warning(f"⚠️ Missing required columns: {missing_columns}")
                logger.info(f"📋 Available columns: {available_cols}")
                
                # Auto-detect similar column names
                column_mapping = {}
                for req_col in required_columns:
                    for avail_col in available_cols:
                        if req_col.lower() in avail_col.lower() or avail_col.lower() in req_col.lower():
                            column_mapping[req_col] = avail_col
                            break
                
                # Check for old column names and map them
                if 'text' in available_cols and 'content' not in available_cols:
                    column_mapping['content'] = 'text'
                if 'label' in available_cols and 'sentiment_label' not in available_cols:
                    column_mapping['sentiment_label'] = 'label'
                
                if column_mapping:
                    logger.info(f"🔍 Auto-detected column mapping: {column_mapping}")
                    df = df.rename(columns={v: k for k, v in column_mapping.items()})
                else:
                    raise ValueError(f"Required columns not found: {missing_columns}")
            
            # Display basic info
            logger.info("📈 Dataset info:")
            logger.info(f"  Total rows: {len(df)}")
            logger.info(f"  Missing values: {df.isnull().sum().sum()}")
            
            # Show sentiment label distribution
            if 'sentiment_label' in df.columns:
                label_counts = df['sentiment_label'].value_counts()
                logger.info("🏷️ Sentiment label distribution:")
                for label, count in label_counts.items():
                    logger.info(f"  {label}: {count} ({count/len(df)*100:.1f}%)")
            
            # Show content length statistics
            if 'content' in df.columns:
                df['content_length'] = df['content'].astype(str).str.len()
                logger.info("📝 Content length statistics:")
                logger.info(f"  Mean: {df['content_length'].mean():.1f} characters")
                logger.info(f"  Median: {df['content_length'].median():.1f} characters")
                logger.info(f"  Max: {df['content_length'].max():.0f} characters")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            raise
    
    def filter_and_map_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize sentiment labels (no language filtering needed)"""
        logger.info("🔧 Cleaning and mapping sentiment labels...")
        
        original_size = len(df)
        df_filtered = df.copy()
        
        # Clean and standardize labels
        df_filtered['sentiment_label'] = df_filtered['sentiment_label'].astype(str).str.lower().str.strip()
        
        # Show original label distribution
        original_labels = df_filtered['sentiment_label'].value_counts()
        logger.info("🏷️ Original sentiment label distribution:")
        for label, count in original_labels.items():
            logger.info(f"  {label}: {count} ({count/len(df_filtered)*100:.1f}%)")
        
        # Standardize sentiment labels to positive, negative, neutral
        label_mapping = {
            # Standard labels
            'positive': 'positive',
            'negative': 'negative',
            'neutral': 'neutral',
            
            # Common variations
            'pos': 'positive',
            'neg': 'negative',
            'neu': 'neutral',
            
            # VADER output variations
            'compound_positive': 'positive',
            'compound_negative': 'negative',
            'compound_neutral': 'neutral',
            
            # Numeric labels
            '1': 'positive',
            '0': 'neutral', 
            '-1': 'negative',
            '2': 'positive',  # Sometimes 2 is very positive
            
            # Other common sentiment labels
            'uncertainty': 'neutral',  # Map uncertainty to neutral
            'uncertain': 'neutral',
            'mixed': 'neutral'
        }
        
        # Apply label mapping
        df_filtered['original_sentiment_label'] = df_filtered['sentiment_label'].copy()
        df_filtered['sentiment_label'] = df_filtered['sentiment_label'].map(label_mapping)
        
        # Remove rows with unmapped labels
        unmapped_mask = df_filtered['sentiment_label'].isna()
        unmapped_labels = df_filtered[unmapped_mask]['original_sentiment_label'].unique()
        
        if len(unmapped_labels) > 0:
            logger.warning(f"⚠️ Found unmapped sentiment labels (will be removed): {unmapped_labels}")
            logger.warning("💡 Consider adding these labels to the mapping if they're valid")
        
        df_filtered = df_filtered[~unmapped_mask].copy()
        
        # Show final label distribution
        final_labels = df_filtered['sentiment_label'].value_counts()
        logger.info("🎯 Final sentiment label distribution:")
        for label, count in final_labels.items():
            logger.info(f"  {label}: {count} ({count/len(df_filtered)*100:.1f}%)")
        
        # Check for class balance
        min_class_size = final_labels.min()
        max_class_size = final_labels.max()
        imbalance_ratio = max_class_size / min_class_size if min_class_size > 0 else float('inf')
        
        if imbalance_ratio > 10:
            logger.warning(f"⚠️ High class imbalance detected (ratio: {imbalance_ratio:.1f})")
            logger.warning("   Consider data balancing techniques if model performance is poor")
        elif imbalance_ratio > 3:
            logger.info(f"ℹ️ Moderate class imbalance (ratio: {imbalance_ratio:.1f}) - should be manageable")
        else:
            logger.info(f"✅ Good class balance (ratio: {imbalance_ratio:.1f})")
        
        removed_count = original_size - len(df_filtered)
        logger.info(f"✅ Data cleaning complete: {len(df_filtered)} samples retained ({removed_count} removed)")
        
        return df_filtered
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text (same logic as consumer)"""
        if not isinstance(text, str) or not text.strip():
            return ""
        
        # Basic cleaning
        text = self.basic_text_cleaning(text)
        
        if not NLP_AVAILABLE:
            return text.lower()
        
        try:
            # Tokenization
            tokens = word_tokenize(text.lower())
            
            # Remove non-alphabetic tokens (FIXED LINE)
            alpha_tokens = [token for token in tokens if token.isalpha() and len(token) > 2]  # ✅ FIXED
            
            # Remove stopwords
            filtered_tokens = [token for token in alpha_tokens if token not in self.stopwords]
            
            # POS tagging and lemmatization
            if filtered_tokens and self.lemmatizer:
                pos_tagged = pos_tag(filtered_tokens)
                processed_tokens = []
                
                for word, pos in pos_tagged:
                    wordnet_pos = self.get_wordnet_pos(pos)
                    lemmatized = self.lemmatizer.lemmatize(word, wordnet_pos)
                    processed_tokens.append(lemmatized)
                
                return ' '.join(processed_tokens)
            else:
                return ' '.join(filtered_tokens)
                
        except Exception as e:
            logger.warning(f"Text preprocessing failed: {e}")
            return text.lower()
    
    def basic_text_cleaning(self, text: str) -> str:
        """Basic text cleaning (same as consumer)"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove Reddit-specific patterns
        text = re.sub(r'/u/\w+', '', text)
        text = re.sub(r'/r/\w+', '', text)
        text = re.sub(r'\[deleted\]|\[removed\]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def get_wordnet_pos(self, treebank_tag: str) -> str:
        """Convert TreeBank POS tags to WordNet format"""
        if treebank_tag.startswith('J'):
            return 'a'
        elif treebank_tag.startswith('V'):
            return 'v'
        elif treebank_tag.startswith('N'):
            return 'n'
        elif treebank_tag.startswith('R'):
            return 'r'
        else:
            return 'n'
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Prepare and clean the filtered dataset using content and sentiment_label"""
        logger.info("🧹 Preparing and cleaning data...")
        
        # Remove rows with missing content or sentiment_label
        df_clean = df.dropna(subset=['content', 'sentiment_label']).copy()
        logger.info(f"After removing NaN: {len(df_clean)} rows")
        
        # Remove empty content
        df_clean = df_clean[df_clean['content'].astype(str).str.strip() != '']
        logger.info(f"After removing empty content: {len(df_clean)} rows")
        
        # Preprocess content texts
        logger.info("🔧 Preprocessing content texts...")
        texts = []
        labels = df_clean['sentiment_label'].tolist()
        
        for i, content in enumerate(df_clean['content']):
            if i % 1000 == 0 and i > 0:
                logger.info(f"Processed {i}/{len(df_clean)} content texts")
            
            processed_text = self.preprocess_text(str(content))
            texts.append(processed_text)
        
        # Remove empty processed texts
        valid_indices = [i for i, text in enumerate(texts) if text.strip()]
        texts = [texts[i] for i in valid_indices]
        labels = [labels[i] for i in valid_indices]
        
        logger.info(f"Final preprocessed dataset: {len(texts)} samples")
        
        # Final class distribution
        from collections import Counter
        final_distribution = Counter(labels)
        logger.info("📊 Final class distribution:")
        for label, count in final_distribution.items():
            logger.info(f"  {label}: {count} ({count/len(labels)*100:.1f}%)")
        
        # Check minimum samples per class
        min_samples = min(final_distribution.values())
        if min_samples < 10:
            logger.warning(f"Very few samples for some classes (min: {min_samples})")
            logger.warning("   Model training may be unreliable")
        elif min_samples < 50:
            logger.warning(f"Limited samples for some classes (min: {min_samples})")
            logger.warning("   Consider collecting more data for better performance")
    
        return texts, labels
    
    def train_models(self, texts: List[str], labels: List[str]) -> Dict:
        """Train multiple Naive Bayes models with different configurations"""
        logger.info("🚀 Starting model training...")
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(labels)
        
        logger.info(f"Label encoding: {dict(zip(self.label_encoder.classes_, range(len(self.label_encoder.classes_))))}")
        
        # Split data with stratification to maintain class balance
        X_train, X_test, y_train, y_test = train_test_split(
            texts, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        logger.info(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
        
        # Show train/test distribution
        from collections import Counter
        train_dist = Counter([self.label_encoder.classes_[y] for y in y_train])
        test_dist = Counter([self.label_encoder.classes_[y] for y in y_test])
        
        logger.info("📈 Training set distribution:")
        for label, count in train_dist.items():
            logger.info(f"  {label}: {count} ({count/len(y_train)*100:.1f}%)")
        
        # Model configurations optimized for 3-class sentiment
        configurations = {
            'multinomial_tfidf': {
                'vectorizer': TfidfVectorizer(
                    max_features=15000, 
                    ngram_range=(1, 2), 
                    min_df=2,
                    max_df=0.95
                ),
                'classifier': MultinomialNB(alpha=0.5)
            },
            'multinomial_count': {
                'vectorizer': CountVectorizer(
                    max_features=15000, 
                    ngram_range=(1, 2), 
                    min_df=2,
                    max_df=0.95
                ),
                'classifier': MultinomialNB(alpha=0.5)
            },
            'complement_tfidf': {
                'vectorizer': TfidfVectorizer(
                    max_features=15000, 
                    ngram_range=(1, 2), 
                    min_df=2,
                    max_df=0.95
                ),
                'classifier': ComplementNB(alpha=0.5)
            }
        }
        
        results = {}
        
        for name, config in configurations.items():
            logger.info(f"Training {name} model...")
            
            # Create pipeline
            pipeline = Pipeline([
                ('vectorizer', config['vectorizer']),
                ('classifier', config['classifier'])
            ])
            
            # Train model
            pipeline.fit(X_train, y_train)
            
            # Predictions
            y_pred = pipeline.predict(X_test)
            
            # Evaluation
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
            
            # Cross-validation
            cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='f1_weighted')
            
            results[name] = {
                'pipeline': pipeline,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'classification_report': classification_report(
                    y_test, y_pred, 
                    target_names=self.label_encoder.classes_,
                    output_dict=True
                ),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            }
            
            logger.info(f"{name}: Accuracy={accuracy:.3f}, F1={f1:.3f}, CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}")
        
        # Find best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['f1_score'])
        logger.info(f"Best model: {best_model_name}")
        
        return results, best_model_name, (X_test, y_test)
    
    def hyperparameter_tuning(self, texts: List[str], labels: List[str]) -> Dict:
        """Perform hyperparameter tuning for the best model"""
        logger.info("🎯 Starting hyperparameter tuning...")
        
        y_encoded = self.label_encoder.transform(labels)
        X_train, X_test, y_train, y_test = train_test_split(
            texts, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Parameter grid for MultinomialNB with TF-IDF
        param_grid = {
            'classifier__alpha': [0.1, 1.0, 2.0]  # Only tune alpha
        }
        
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer()),
            ('classifier', MultinomialNB())
        ])
        
        # Grid search with cross-validation
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=5, scoring='f1_weighted', 
            n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Best model evaluation
        best_pipeline = grid_search.best_estimator_
        y_pred = best_pipeline.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        tuned_results = {
            'pipeline': best_pipeline,
            'best_params': grid_search.best_params_,
            'best_cv_score': grid_search.best_score_,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'classification_report': classification_report(
                y_test, y_pred, 
                target_names=self.label_encoder.classes_,
                output_dict=True
            )
        }
        
        logger.info(f"Tuned model: Accuracy={accuracy:.3f}, F1={f1:.3f}")
        logger.info(f"Best parameters: {grid_search.best_params_}")
        
        return tuned_results
    
    def save_models(self, results: Dict, best_model_name: str, tuned_results: Dict):
        """Save trained models and generate comprehensive reports for all configurations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create models/naive_bayes directory
        Path('models/naive_bayes').mkdir(parents=True, exist_ok=True)
        
        # Save best model
        best_model_path = f'models/naive_bayes/naive_bayes_best_model_{timestamp}.pkl'
        with open(best_model_path, 'wb') as f:
            pickle.dump(results[best_model_name]['pipeline'], f)
        
        # Save tuned model (this is our final best model)
        tuned_model_path = f'models/naive_bayes/naive_bayes_tuned_model_{timestamp}.pkl'
        with open(tuned_model_path, 'wb') as f:
            pickle.dump(tuned_results['pipeline'], f)
        
        # Save label encoder
        label_encoder_path = f'models/naive_bayes/label_encoder_{timestamp}.pkl'
        with open(label_encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        # Save vectorizer
        vectorizer_path = f'models/naive_bayes/vectorizer_{timestamp}.pkl'
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(tuned_results['pipeline'].named_steps['vectorizer'], f)
           
        # ✅ NEW: Generate comparison report between configurations
        self.generate_configuration_comparison_report(results, timestamp)
        
        # Create main report (for backward compatibility)
        report_data = {
            "timestamp": timestamp,
            "model_path": tuned_model_path,
            "label_encoder": label_encoder_path,
            "vectorizer": vectorizer_path,
            "labels": list(self.label_encoder.classes_),
            "test_accuracy": float(tuned_results['accuracy']),
            "confusion_matrix": results[best_model_name]['confusion_matrix'],
            "classification_report": tuned_results['classification_report'],
            "strategy": "CSV with VADER sentiment labels",
            "input_format": {
                "file_type": "CSV",
                "content_column": "content",
                "label_column": "sentiment_label"
            },
            "data_source": "malaysia_tourism_data_collector_with_vader",
            "model_type": "naive_bayes",
            "best_model_name": best_model_name,
            "hyperparameters": tuned_results['best_params'],
            "cv_score": float(tuned_results['best_cv_score']),
            "f1_score": float(tuned_results['f1_score']),
            "precision": float(tuned_results['precision']),
            "recall": float(tuned_results['recall'])
        }
        
        # Save main report
        report_path = f'reports/naive_bayes_training_report_{timestamp}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Models and reports saved:")
        logger.info(f"  Best model: {best_model_path}")
        logger.info(f"  Tuned model: {tuned_model_path}")
        logger.info(f"  Label encoder: {label_encoder_path}")
        logger.info(f"  Vectorizer: {vectorizer_path}")
        logger.info(f"  Main report: {report_path}")
        logger.info(f"  Detailed reports: reports/naive_bayes_*_{timestamp}.json")

        # Return metadata
        metadata = {
            'timestamp': timestamp,
            'file_paths': {
                'best_model': best_model_path,
                'tuned_model': tuned_model_path,
                'report': report_path
            },
            'test_accuracy': tuned_results['accuracy'],
            'f1_score': tuned_results['f1_score'],
            'precision': tuned_results['precision'],
            'recall': tuned_results['recall']
        }
        
        return metadata

    def generate_configuration_comparison_report(self, results: Dict, timestamp: str):
        """Generate comparison report between different configurations"""
        logger.info("📋 Generating configuration comparison report...")
        
        # Extract metrics for comparison
        comparison_data = {
            "timestamp": timestamp,
            "comparison_type": "naive_bayes_configurations",
            "configurations": {},
            "best_configuration": {},
            "summary": {}
        }
        
        # Process each configuration
        best_f1 = 0
        best_config = None
        
        for config_name, config_results in results.items():
            config_summary = {
                "test_accuracy": float(config_results['accuracy']),
                "precision": float(config_results['precision']),
                "recall": float(config_results['recall']),
                "f1_score": float(config_results['f1_score']),
                "cv_mean": float(config_results['cv_mean']),
                "cv_std": float(config_results['cv_std']),
                "vectorizer_type": "tfidf" if "tfidf" in config_name else "count",
                "classifier_type": "multinomial" if "multinomial" in config_name else "complement"
            }
            
            comparison_data["configurations"][config_name] = config_summary
            
            # Track best configuration
            if config_results['f1_score'] > best_f1:
                best_f1 = config_results['f1_score']
                best_config = config_name
        
        # Best configuration details
        comparison_data["best_configuration"] = {
            "name": best_config,
            "f1_score": best_f1,
            "details": comparison_data["configurations"][best_config]
        }
        
        # Generate summary statistics
        all_accuracies = [config["test_accuracy"] for config in comparison_data["configurations"].values()]
        all_f1_scores = [config["f1_score"] for config in comparison_data["configurations"].values()]
        all_precisions = [config["precision"] for config in comparison_data["configurations"].values()]
        all_recalls = [config["recall"] for config in comparison_data["configurations"].values()]
        
        comparison_data["summary"] = {
            "total_configurations": len(results),
            "metrics_summary": {
                "accuracy": {
                    "min": min(all_accuracies),
                    "max": max(all_accuracies),
                    "mean": sum(all_accuracies) / len(all_accuracies),
                    "std": np.std(all_accuracies)
                },
                "f1_score": {
                    "min": min(all_f1_scores),
                    "max": max(all_f1_scores),
                    "mean": sum(all_f1_scores) / len(all_f1_scores),
                    "std": np.std(all_f1_scores)
                },
                "precision": {
                    "min": min(all_precisions),
                    "max": max(all_precisions),
                    "mean": sum(all_precisions) / len(all_precisions),
                    "std": np.std(all_precisions)
                },
                "recall": {
                    "min": min(all_recalls),
                    "max": max(all_recalls),
                    "mean": sum(all_recalls) / len(all_recalls),
                    "std": np.std(all_recalls)
                }
            },
            "configuration_ranking": sorted(
                [(name, config["f1_score"]) for name, config in comparison_data["configurations"].items()],
                key=lambda x: x[1], reverse=True
            )
        }
        
        # Save comparison report
        comparison_report_path = f'reports/naive_bayes_comparison_report_{timestamp}.json'
        with open(comparison_report_path, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved comparison report: {comparison_report_path}")
    
    def train(self) -> Dict:
        """Main training pipeline with Option A implementation"""
        logger.info("🚀 Starting Naive Bayes model training pipeline")
        logger.info("🎯 Option A: uncertainty → neutral mapping")
        logger.info("=" * 60)
        
        try:
            # Load dataset
            df = self.load_dataset()
            
            # Filter for English and map labels (Option A)
            df_filtered = self.filter_and_map_data(df)
            
            # Prepare data
            texts, labels = self.prepare_data(df_filtered)
            
            if len(texts) < 100:
                raise ValueError(f"Insufficient data: only {len(texts)} samples")
            
            # Ensure we have all three classes
            unique_labels = set(labels)
            expected_labels = {'positive', 'negative', 'neutral'}
            
            if not expected_labels.issubset(unique_labels):
                missing = expected_labels - unique_labels
                logger.warning(f"Missing expected labels: {missing}")
            
            # Train multiple models
            results, best_model_name, test_data = self.train_models(texts, labels)
            
            # Hyperparameter tuning
            tuned_results = self.hyperparameter_tuning(texts, labels)
            
            # Save models (report is generated here now)
            metadata = self.save_models(results, best_model_name, tuned_results)
            
            # ✅ REMOVED: No separate report generation
            # report_path = self.generate_report(results, tuned_results, metadata)
            
            logger.info("✅ TRAINING COMPLETED SUCCESSFULLY!")
            logger.info(f"🏷️ Classes: {self.label_encoder.classes_}")
            logger.info(f"🏆 Best model F1-score: {results[best_model_name]['f1_score']:.3f}")
            logger.info(f"🎯 Tuned model F1-score: {tuned_results['f1_score']:.3f}")
            logger.info(f"📊 Report: {metadata['file_paths']['report']}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            raise
    
    def train_naive_bayes_model(self) -> bool:
        """Train the Naive Bayes model (only if not exists)"""
        logger.info("🧠 STEP 1: Checking/Training Naive Bayes Model")
        logger.info("=" * 50)
        
        # Check if model already exists
        model_status = self.check_models_exist()
        
        if model_status['naive_bayes']:
            logger.info("✅ Naive Bayes model already exists - skipping training")
            self.pipeline_stats['naive_bayes_trained'] = True
            return True
        
        logger.info("🔄 Naive Bayes model not found - starting training...")
        
        try:
            result = subprocess.run([sys.executable, 'train_naive_bayes_model.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Naive Bayes training completed")
                self.pipeline_stats['naive_bayes_trained'] = True
                return True
            else:
                logger.error(f"❌ Naive Bayes training failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Naive Bayes training error: {e}")
            return False

if __name__ == "__main__":
    """Main execution for training"""
    try:
        logger.info("🚀 Starting Malaysian Tourism Naive Bayes Training")
        
        # Initialize trainer with CSV format
        trainer = MalaysianTourismNBTrainer(
            dataset_path="data/raw/malaysia_tourism_data.csv"
        )
        
        # Run training pipeline
        metadata = trainer.train()
        
        logger.info("✅ Training completed successfully!")
        logger.info(f"📊 Model metadata: {metadata['file_paths']}")
        
    except FileNotFoundError:
        logger.error("❌ Dataset file not found: data/raw/malaysia_tourism_data.csv")
        logger.error("💡 Make sure to run the data collector first to generate the CSV")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback
        logger.error(f"📋 Full error: {traceback.format_exc()}")


"""
Malaysian Tourism Naive Bayes Sentiment Model Trainer
====================================================

This script trains a Naive Bayes classifier on the tourism dataset with
text, language, and label columns. Filters for English text and maps
uncertainty to neutral.

Features:
- Language filtering (English only)
- Three-class sentiment: positive, negative, neutral (uncertainty→neutral)
- Naive Bayes model training with cross-validation
- Text preprocessing using NLTK (same as consumer)
- Model evaluation and performance metrics
- Model persistence for integration with consumer

Author: Big Data & NLP Analytics Team
Date: July 2, 2025
"""
import os
import warnings
import pandas as pd
import numpy as np
import pickle
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any  # Add 'Any'
import subprocess
import sys

# === SUPPRESS ALL WARNINGS ===
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'     # Hide TensorFlow INFO & WARN
warnings.filterwarnings("ignore")            # Hide Python warnings
logging.getLogger('tensorflow').setLevel(logging.ERROR)  # Hide TensorFlow logs

# Scikit-learn imports
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.naive_bayes import MultinomialNB, GaussianNB, ComplementNB
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import (classification_report, confusion_matrix, 
                           accuracy_score, precision_recall_fscore_support)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

# Import NLTK preprocessing from your consumer
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.tag import pos_tag
    import re
    NLP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ NLTK not available: {e}")
    NLP_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/naive_bayes_training.log')
    ]
)
logger = logging.getLogger(__name__)

class MalaysianTourismNBTrainer:
    """Naive Bayes model trainer for Malaysian tourism sentiment analysis"""
    
    def __init__(self, dataset_path: str = "data/raw/malaysia_tourism_data.csv"):  # ✅ CHANGED
        """Initialize the trainer"""
        self.dataset_path = dataset_path
        self.setup_directories()
        self.setup_preprocessing()
        self.models = {}
        self.vectorizers = {}
        self.label_encoder = LabelEncoder()
        self.pipeline_stats = {
            'naive_bayes_trained': False,
            'lstm_trained': False
        }
        
    def setup_directories(self):
        """Create necessary directories"""
        dirs = ['models', 'logs', 'reports', 'data/processed']
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info("✅ Training directories created/verified")
    
    def setup_preprocessing(self):
        """Setup text preprocessing (same as consumer)"""
        if NLP_AVAILABLE:
            # Download NLTK resources
            resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
            for resource in resources:
                try:
                    nltk.download(resource, quiet=True)
                except:
                    pass
            
            self.stemmer = PorterStemmer()
            self.lemmatizer = WordNetLemmatizer()
            
            # Load stopwords (same as consumer)
            try:
                english_stopwords = set(stopwords.words('english'))
                custom_stopwords = {
                    'malaysia', 'malaysian', 'kuala', 'lumpur', 'kl', 'penang', 'langkawi',
                    'go', 'going', 'went', 'visit', 'visiting', 'visited', 'trip', 'travel',
                    'place', 'places', 'time', 'day', 'days', 'week', 'month', 'year',
                    'like', 'would', 'could', 'should', 'really', 'also', 'get', 'got'
                }
                self.stopwords = english_stopwords.union(custom_stopwords)
                logger.info(f"✅ Preprocessing setup with {len(self.stopwords)} stopwords")
            except:
                self.stopwords = set()
                logger.warning("⚠️ Could not load stopwords")
        else:
            self.stemmer = None
            self.lemmatizer = None
            self.stopwords = set()
    
    def load_dataset(self) -> pd.DataFrame:
        """Load and validate the CSV dataset (content, sentiment_label columns)"""
        try:
            logger.info(f"📂 Loading dataset from {self.dataset_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(self.dataset_path, encoding=encoding)
                    logger.info(f"✅ Dataset loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not load dataset with any encoding")
            
            logger.info(f"📊 Dataset shape: {df.shape}")
            logger.info(f"📋 Columns: {list(df.columns)}")
            
            # Validate required columns for new CSV structure
            required_columns = ['content', 'sentiment_label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # Try to find similar column names
                available_cols = df.columns.tolist()
                logger.warning(f"⚠️ Missing required columns: {missing_columns}")
                logger.info(f"📋 Available columns: {available_cols}")
                
                # Auto-detect similar column names
                column_mapping = {}
                for req_col in required_columns:
                    for avail_col in available_cols:
                        if req_col.lower() in avail_col.lower() or avail_col.lower() in req_col.lower():
                            column_mapping[req_col] = avail_col
                            break
                
                # Check for old column names and map them
                if 'text' in available_cols and 'content' not in available_cols:
                    column_mapping['content'] = 'text'
                if 'label' in available_cols and 'sentiment_label' not in available_cols:
                    column_mapping['sentiment_label'] = 'label'
                
                if column_mapping:
                    logger.info(f"🔍 Auto-detected column mapping: {column_mapping}")
                    df = df.rename(columns={v: k for k, v in column_mapping.items()})
                else:
                    raise ValueError(f"Required columns not found: {missing_columns}")
            
            # Display basic info
            logger.info("📈 Dataset info:")
            logger.info(f"  Total rows: {len(df)}")
            logger.info(f"  Missing values: {df.isnull().sum().sum()}")
            
            # Show sentiment label distribution
            if 'sentiment_label' in df.columns:
                label_counts = df['sentiment_label'].value_counts()
                logger.info("🏷️ Sentiment label distribution:")
                for label, count in label_counts.items():
                    logger.info(f"  {label}: {count} ({count/len(df)*100:.1f}%)")
            
            # Show content length statistics
            if 'content' in df.columns:
                df['content_length'] = df['content'].astype(str).str.len()
                logger.info("📝 Content length statistics:")
                logger.info(f"  Mean: {df['content_length'].mean():.1f} characters")
                logger.info(f"  Median: {df['content_length'].median():.1f} characters")
                logger.info(f"  Max: {df['content_length'].max():.0f} characters")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            raise
    
    def filter_and_map_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize sentiment labels (no language filtering needed)"""
        logger.info("🔧 Cleaning and mapping sentiment labels...")
        
        original_size = len(df)
        df_filtered = df.copy()
        
        # Clean and standardize labels
        df_filtered['sentiment_label'] = df_filtered['sentiment_label'].astype(str).str.lower().str.strip()
        
        # Show original label distribution
        original_labels = df_filtered['sentiment_label'].value_counts()
        logger.info("🏷️ Original sentiment label distribution:")
        for label, count in original_labels.items():
            logger.info(f"  {label}: {count} ({count/len(df_filtered)*100:.1f}%)")
        
        # Standardize sentiment labels to positive, negative, neutral
        label_mapping = {
            # Standard labels
            'positive': 'positive',
            'negative': 'negative',
            'neutral': 'neutral',
            
            # Common variations
            'pos': 'positive',
            'neg': 'negative',
            'neu': 'neutral',
            
            # VADER output variations
            'compound_positive': 'positive',
            'compound_negative': 'negative',
            'compound_neutral': 'neutral',
            
            # Numeric labels
            '1': 'positive',
            '0': 'neutral', 
            '-1': 'negative',
            '2': 'positive',  # Sometimes 2 is very positive
            
            # Other common sentiment labels
            'uncertainty': 'neutral',  # Map uncertainty to neutral
            'uncertain': 'neutral',
            'mixed': 'neutral'
        }
        
        # Apply label mapping
        df_filtered['original_sentiment_label'] = df_filtered['sentiment_label'].copy()
        df_filtered['sentiment_label'] = df_filtered['sentiment_label'].map(label_mapping)
        
        # Remove rows with unmapped labels
        unmapped_mask = df_filtered['sentiment_label'].isna()
        unmapped_labels = df_filtered[unmapped_mask]['original_sentiment_label'].unique()
        
        if len(unmapped_labels) > 0:
            logger.warning(f"⚠️ Found unmapped sentiment labels (will be removed): {unmapped_labels}")
            logger.warning("💡 Consider adding these labels to the mapping if they're valid")
        
        df_filtered = df_filtered[~unmapped_mask].copy()
        
        # Show final label distribution
        final_labels = df_filtered['sentiment_label'].value_counts()
        logger.info("🎯 Final sentiment label distribution:")
        for label, count in final_labels.items():
            logger.info(f"  {label}: {count} ({count/len(df_filtered)*100:.1f}%)")
        
        # Check for class balance
        min_class_size = final_labels.min()
        max_class_size = final_labels.max()
        imbalance_ratio = max_class_size / min_class_size if min_class_size > 0 else float('inf')
        
        if imbalance_ratio > 10:
            logger.warning(f"⚠️ High class imbalance detected (ratio: {imbalance_ratio:.1f})")
            logger.warning("   Consider data balancing techniques if model performance is poor")
        elif imbalance_ratio > 3:
            logger.info(f"ℹ️ Moderate class imbalance (ratio: {imbalance_ratio:.1f}) - should be manageable")
        else:
            logger.info(f"✅ Good class balance (ratio: {imbalance_ratio:.1f})")
        
        removed_count = original_size - len(df_filtered)
        logger.info(f"✅ Data cleaning complete: {len(df_filtered)} samples retained ({removed_count} removed)")
        
        return df_filtered
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text (same logic as consumer)"""
        if not isinstance(text, str) or not text.strip():
            return ""
        
        # Basic cleaning
        text = self.basic_text_cleaning(text)
        
        if not NLP_AVAILABLE:
            return text.lower()
        
        try:
            # Tokenization
            tokens = word_tokenize(text.lower())
            
            # Remove non-alphabetic tokens (FIXED LINE)
            alpha_tokens = [token for token in tokens if token.isalpha() and len(token) > 2]  # ✅ FIXED
            
            # Remove stopwords
            filtered_tokens = [token for token in alpha_tokens if token not in self.stopwords]
            
            # POS tagging and lemmatization
            if filtered_tokens and self.lemmatizer:
                pos_tagged = pos_tag(filtered_tokens)
                processed_tokens = []
                
                for word, pos in pos_tagged:
                    wordnet_pos = self.get_wordnet_pos(pos)
                    lemmatized = self.lemmatizer.lemmatize(word, wordnet_pos)
                    processed_tokens.append(lemmatized)
                
                return ' '.join(processed_tokens)
            else:
                return ' '.join(filtered_tokens)
                
        except Exception as e:
            logger.warning(f"Text preprocessing failed: {e}")
            return text.lower()
    
    def basic_text_cleaning(self, text: str) -> str:
        """Basic text cleaning (same as consumer)"""
        if not text:
            return ""
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove Reddit-specific patterns
        text = re.sub(r'/u/\w+', '', text)
        text = re.sub(r'/r/\w+', '', text)
        text = re.sub(r'\[deleted\]|\[removed\]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def get_wordnet_pos(self, treebank_tag: str) -> str:
        """Convert TreeBank POS tags to WordNet format"""
        if treebank_tag.startswith('J'):
            return 'a'
        elif treebank_tag.startswith('V'):
            return 'v'
        elif treebank_tag.startswith('N'):
            return 'n'
        elif treebank_tag.startswith('R'):
            return 'r'
        else:
            return 'n'
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Prepare and clean the filtered dataset using content and sentiment_label"""
        logger.info("🧹 Preparing and cleaning data...")
        
        # Remove rows with missing content or sentiment_label
        df_clean = df.dropna(subset=['content', 'sentiment_label']).copy()
        logger.info(f"After removing NaN: {len(df_clean)} rows")
        
        # Remove empty content
        df_clean = df_clean[df_clean['content'].astype(str).str.strip() != '']
        logger.info(f"After removing empty content: {len(df_clean)} rows")
        
        # Preprocess content texts
        logger.info("🔧 Preprocessing content texts...")
        texts = []
        labels = df_clean['sentiment_label'].tolist()
        
        for i, content in enumerate(df_clean['content']):
            if i % 1000 == 0 and i > 0:
                logger.info(f"Processed {i}/{len(df_clean)} content texts")
            
            processed_text = self.preprocess_text(str(content))
            texts.append(processed_text)
        
        # Remove empty processed texts
        valid_indices = [i for i, text in enumerate(texts) if text.strip()]
        texts = [texts[i] for i in valid_indices]
        labels = [labels[i] for i in valid_indices]
        
        logger.info(f"Final preprocessed dataset: {len(texts)} samples")
        
        # Final class distribution
        from collections import Counter
        final_distribution = Counter(labels)
        logger.info("📊 Final class distribution:")
        for label, count in final_distribution.items():
            logger.info(f"  {label}: {count} ({count/len(labels)*100:.1f}%)")
        
        # Check minimum samples per class
        min_samples = min(final_distribution.values())
        if min_samples < 10:
            logger.warning(f"Very few samples for some classes (min: {min_samples})")
            logger.warning("   Model training may be unreliable")
        elif min_samples < 50:
            logger.warning(f"Limited samples for some classes (min: {min_samples})")
            logger.warning("   Consider collecting more data for better performance")
    
        return texts, labels
    
    def train_models(self, texts: List[str], labels: List[str]) -> Dict:
        """Train multiple Naive Bayes models with different configurations"""
        logger.info("🚀 Starting model training...")
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(labels)
        
        logger.info(f"Label encoding: {dict(zip(self.label_encoder.classes_, range(len(self.label_encoder.classes_))))}")
        
        # Split data with stratification to maintain class balance
        X_train, X_test, y_train, y_test = train_test_split(
            texts, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        logger.info(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
        
        # Show train/test distribution
        from collections import Counter
        train_dist = Counter([self.label_encoder.classes_[y] for y in y_train])
        test_dist = Counter([self.label_encoder.classes_[y] for y in y_test])
        
        logger.info("📈 Training set distribution:")
        for label, count in train_dist.items():
            logger.info(f"  {label}: {count} ({count/len(y_train)*100:.1f}%)")
        
        # Model configurations optimized for 3-class sentiment
        configurations = {
            'multinomial_tfidf': {
                'vectorizer': TfidfVectorizer(
                    max_features=15000, 
                    ngram_range=(1, 2), 
                    min_df=2,
                    max_df=0.95
                ),
                'classifier': MultinomialNB(alpha=0.5)
            },
            'multinomial_count': {
                'vectorizer': CountVectorizer(
                    max_features=15000, 
                    ngram_range=(1, 2), 
                    min_df=2,
                    max_df=0.95
                ),
                'classifier': MultinomialNB(alpha=0.5)
            },
            'complement_tfidf': {
                'vectorizer': TfidfVectorizer(
                    max_features=15000, 
                    ngram_range=(1, 2), 
                    min_df=2,
                    max_df=0.95
                ),
                'classifier': ComplementNB(alpha=0.5)
            }
        }
        
        results = {}
        
        for name, config in configurations.items():
            logger.info(f"Training {name} model...")
            
            # Create pipeline
            pipeline = Pipeline([
                ('vectorizer', config['vectorizer']),
                ('classifier', config['classifier'])
            ])
            
            # Train model
            pipeline.fit(X_train, y_train)
            
            # Predictions
            y_pred = pipeline.predict(X_test)
            
            # Evaluation
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
            
            # Cross-validation
            cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='f1_weighted')
            
            results[name] = {
                'pipeline': pipeline,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'classification_report': classification_report(
                    y_test, y_pred, 
                    target_names=self.label_encoder.classes_,
                    output_dict=True
                ),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            }
            
            logger.info(f"{name}: Accuracy={accuracy:.3f}, F1={f1:.3f}, CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}")
        
        # Find best model
        best_model_name = max(results.keys(), key=lambda k: results[k]['f1_score'])
        logger.info(f"Best model: {best_model_name}")
        
        return results, best_model_name, (X_test, y_test)
    
    def hyperparameter_tuning(self, texts: List[str], labels: List[str]) -> Dict:
        """Perform hyperparameter tuning for the best model"""
        logger.info("🎯 Starting hyperparameter tuning...")
        
        y_encoded = self.label_encoder.transform(labels)
        X_train, X_test, y_train, y_test = train_test_split(
            texts, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Parameter grid for MultinomialNB with TF-IDF
        param_grid = {
            'classifier__alpha': [0.1, 1.0, 2.0]  # Only tune alpha
        }
        
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer()),
            ('classifier', MultinomialNB())
        ])
        
        # Grid search with cross-validation
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=5, scoring='f1_weighted', 
            n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Best model evaluation
        best_pipeline = grid_search.best_estimator_
        y_pred = best_pipeline.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        tuned_results = {
            'pipeline': best_pipeline,
            'best_params': grid_search.best_params_,
            'best_cv_score': grid_search.best_score_,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'classification_report': classification_report(
                y_test, y_pred, 
                target_names=self.label_encoder.classes_,
                output_dict=True
            )
        }
        
        logger.info(f"Tuned model: Accuracy={accuracy:.3f}, F1={f1:.3f}")
        logger.info(f"Best parameters: {grid_search.best_params_}")
        
        return tuned_results
    
    def save_models(self, results: Dict, best_model_name: str, tuned_results: Dict):
        """Save trained models and generate comprehensive reports for all configurations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create models/naive_bayes directory
        Path('models/naive_bayes').mkdir(parents=True, exist_ok=True)
        
        # Save best model
        best_model_path = f'models/naive_bayes/naive_bayes_best_model_{timestamp}.pkl'
        with open(best_model_path, 'wb') as f:
            pickle.dump(results[best_model_name]['pipeline'], f)
        
        # Save tuned model (this is our final best model)
        tuned_model_path = f'models/naive_bayes/naive_bayes_tuned_model_{timestamp}.pkl'
        with open(tuned_model_path, 'wb') as f:
            pickle.dump(tuned_results['pipeline'], f)
        
        # Save label encoder
        label_encoder_path = f'models/naive_bayes/label_encoder_{timestamp}.pkl'
        with open(label_encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        
        # Save vectorizer
        vectorizer_path = f'models/naive_bayes/vectorizer_{timestamp}.pkl'
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(tuned_results['pipeline'].named_steps['vectorizer'], f)
           
        # ✅ NEW: Generate comparison report between configurations
        self.generate_configuration_comparison_report(results, timestamp)
        
        # Create main report (for backward compatibility)
        report_data = {
            "timestamp": timestamp,
            "model_path": tuned_model_path,
            "label_encoder": label_encoder_path,
            "vectorizer": vectorizer_path,
            "labels": list(self.label_encoder.classes_),
            "test_accuracy": float(tuned_results['accuracy']),
            "confusion_matrix": results[best_model_name]['confusion_matrix'],
            "classification_report": tuned_results['classification_report'],
            "strategy": "CSV with VADER sentiment labels",
            "input_format": {
                "file_type": "CSV",
                "content_column": "content",
                "label_column": "sentiment_label"
            },
            "data_source": "malaysia_tourism_data_collector_with_vader",
            "model_type": "naive_bayes",
            "best_model_name": best_model_name,
            "hyperparameters": tuned_results['best_params'],
            "cv_score": float(tuned_results['best_cv_score']),
            "f1_score": float(tuned_results['f1_score']),
            "precision": float(tuned_results['precision']),
            "recall": float(tuned_results['recall'])
        }
        
        # Save main report
        report_path = f'reports/naive_bayes_training_report_{timestamp}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Models and reports saved:")
        logger.info(f"  Best model: {best_model_path}")
        logger.info(f"  Tuned model: {tuned_model_path}")
        logger.info(f"  Label encoder: {label_encoder_path}")
        logger.info(f"  Vectorizer: {vectorizer_path}")
        logger.info(f"  Main report: {report_path}")
        logger.info(f"  Detailed reports: reports/naive_bayes_*_{timestamp}.json")

        # Return metadata
        metadata = {
            'timestamp': timestamp,
            'file_paths': {
                'best_model': best_model_path,
                'tuned_model': tuned_model_path,
                'report': report_path
            },
            'test_accuracy': tuned_results['accuracy'],
            'f1_score': tuned_results['f1_score'],
            'precision': tuned_results['precision'],
            'recall': tuned_results['recall']
        }
        
        return metadata

    def generate_configuration_comparison_report(self, results: Dict, timestamp: str):
        """Generate comparison report between different configurations"""
        logger.info("📋 Generating configuration comparison report...")
        
        # Extract metrics for comparison
        comparison_data = {
            "timestamp": timestamp,
            "comparison_type": "naive_bayes_configurations",
            "configurations": {},
            "best_configuration": {},
            "summary": {}
        }
        
        # Process each configuration
        best_f1 = 0
        best_config = None
        
        for config_name, config_results in results.items():
            config_summary = {
                "test_accuracy": float(config_results['accuracy']),
                "precision": float(config_results['precision']),
                "recall": float(config_results['recall']),
                "f1_score": float(config_results['f1_score']),
                "cv_mean": float(config_results['cv_mean']),
                "cv_std": float(config_results['cv_std']),
                "vectorizer_type": "tfidf" if "tfidf" in config_name else "count",
                "classifier_type": "multinomial" if "multinomial" in config_name else "complement"
            }
            
            comparison_data["configurations"][config_name] = config_summary
            
            # Track best configuration
            if config_results['f1_score'] > best_f1:
                best_f1 = config_results['f1_score']
                best_config = config_name
        
        # Best configuration details
        comparison_data["best_configuration"] = {
            "name": best_config,
            "f1_score": best_f1,
            "details": comparison_data["configurations"][best_config]
        }
        
        # Generate summary statistics
        all_accuracies = [config["test_accuracy"] for config in comparison_data["configurations"].values()]
        all_f1_scores = [config["f1_score"] for config in comparison_data["configurations"].values()]
        all_precisions = [config["precision"] for config in comparison_data["configurations"].values()]
        all_recalls = [config["recall"] for config in comparison_data["configurations"].values()]
        
        comparison_data["summary"] = {
            "total_configurations": len(results),
            "metrics_summary": {
                "accuracy": {
                    "min": min(all_accuracies),
                    "max": max(all_accuracies),
                    "mean": sum(all_accuracies) / len(all_accuracies),
                    "std": np.std(all_accuracies)
                },
                "f1_score": {
                    "min": min(all_f1_scores),
                    "max": max(all_f1_scores),
                    "mean": sum(all_f1_scores) / len(all_f1_scores),
                    "std": np.std(all_f1_scores)
                },
                "precision": {
                    "min": min(all_precisions),
                    "max": max(all_precisions),
                    "mean": sum(all_precisions) / len(all_precisions),
                    "std": np.std(all_precisions)
                },
                "recall": {
                    "min": min(all_recalls),
                    "max": max(all_recalls),
                    "mean": sum(all_recalls) / len(all_recalls),
                    "std": np.std(all_recalls)
                }
            },
            "configuration_ranking": sorted(
                [(name, config["f1_score"]) for name, config in comparison_data["configurations"].items()],
                key=lambda x: x[1], reverse=True
            )
        }
        
        # Save comparison report
        comparison_report_path = f'reports/naive_bayes_comparison_report_{timestamp}.json'
        with open(comparison_report_path, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved comparison report: {comparison_report_path}")
    
    def train(self) -> Dict:
        """Main training pipeline with Option A implementation"""
        logger.info("🚀 Starting Naive Bayes model training pipeline")
        logger.info("🎯 Option A: uncertainty → neutral mapping")
        logger.info("=" * 60)
        
        try:
            # Load dataset
            df = self.load_dataset()
            
            # Filter for English and map labels (Option A)
            df_filtered = self.filter_and_map_data(df)
            
            # Prepare data
            texts, labels = self.prepare_data(df_filtered)
            
            if len(texts) < 100:
                raise ValueError(f"Insufficient data: only {len(texts)} samples")
            
            # Ensure we have all three classes
            unique_labels = set(labels)
            expected_labels = {'positive', 'negative', 'neutral'}
            
            if not expected_labels.issubset(unique_labels):
                missing = expected_labels - unique_labels
                logger.warning(f"Missing expected labels: {missing}")
            
            # Train multiple models
            results, best_model_name, test_data = self.train_models(texts, labels)
            
            # Hyperparameter tuning
            tuned_results = self.hyperparameter_tuning(texts, labels)
            
            # Save models (report is generated here now)
            metadata = self.save_models(results, best_model_name, tuned_results)
            
            # ✅ REMOVED: No separate report generation
            # report_path = self.generate_report(results, tuned_results, metadata)
            
            logger.info("✅ TRAINING COMPLETED SUCCESSFULLY!")
            logger.info(f"🏷️ Classes: {self.label_encoder.classes_}")
            logger.info(f"🏆 Best model F1-score: {results[best_model_name]['f1_score']:.3f}")
            logger.info(f"🎯 Tuned model F1-score: {tuned_results['f1_score']:.3f}")
            logger.info(f"📊 Report: {metadata['file_paths']['report']}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            raise
    
    def train_naive_bayes_model(self) -> bool:
        """Train the Naive Bayes model (only if not exists)"""
        logger.info("🧠 STEP 1: Checking/Training Naive Bayes Model")
        logger.info("=" * 50)
        
        # Check if model already exists
        model_status = self.check_models_exist()
        
        if model_status['naive_bayes']:
            logger.info("✅ Naive Bayes model already exists - skipping training")
            self.pipeline_stats['naive_bayes_trained'] = True
            return True
        
        logger.info("🔄 Naive Bayes model not found - starting training...")
        
        try:
            result = subprocess.run([sys.executable, 'train_naive_bayes_model.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Naive Bayes training completed")
                self.pipeline_stats['naive_bayes_trained'] = True
                return True
            else:
                logger.error(f"❌ Naive Bayes training failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Naive Bayes training error: {e}")
            return False

if __name__ == "__main__":
    """Main execution for training"""
    try:
        logger.info("🚀 Starting Malaysian Tourism Naive Bayes Training")
        
        # Initialize trainer with CSV format
        trainer = MalaysianTourismNBTrainer(
            dataset_path="data/raw/malaysia_tourism_data.csv"
        )
        
        # Run training pipeline
        metadata = trainer.train()
        
        logger.info("✅ Training completed successfully!")
        logger.info(f"📊 Model metadata: {metadata['file_paths']}")
        
    except FileNotFoundError:
        logger.error("❌ Dataset file not found: data/raw/malaysia_tourism_data.csv")
        logger.error("💡 Make sure to run the data collector first to generate the CSV")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        import traceback
        logger.error(f"📋 Full error: {traceback.format_exc()}")

