import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
import time
import joblib
import warnings
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
import logging
import os

warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set style for plots
plt.style.use('default')
sns.set_palette("husl")

class SentimentAnalysisMLComparison:
    def __init__(self, data_path=None):
        """Initialize the sentiment analysis comparison class"""
        # Try YouTube dataset first, then fall back to sentiment dataset
        if data_path is None:
            # Check if running in Docker container (data mounted at /app/data)
            if os.path.exists("/app/data"):
                youtube_data = "/app/data/youtube_comments.csv"
                fallback_data = "/app/data/sentiment_dataset.csv"
            else:
                # Local development paths
                youtube_data = "../data/youtube_comments.csv"
                fallback_data = "../data/sentiment_dataset.csv"
            
            if os.path.exists(youtube_data):
                self.data_path = youtube_data
                logger.info("Using YouTube comments dataset for training")
            elif os.path.exists(fallback_data):
                self.data_path = fallback_data
                logger.info("YouTube dataset not found, using fallback sentiment dataset")
            else:
                raise FileNotFoundError("Neither YouTube comments nor sentiment dataset found")
        else:
            self.data_path = data_path
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.results = {}
        self.trained_pipelines = {}
        self.vectorizer = None
        
        # Create model directory if it doesn't exist
        os.makedirs("model", exist_ok=True)
        
    def load_and_preprocess_data(self):
        """Load and preprocess the sentiment dataset"""
        logger.info(f"Loading data from {self.data_path}...")
        
        try:
            self.df = pd.read_csv(self.data_path)
            logger.info(f"Dataset loaded successfully. Shape: {self.df.shape}")
            
            # Check for required columns
            if 'text' not in self.df.columns or ('label' not in self.df.columns and 'sentiment' not in self.df.columns):
                # Try different column names
                text_cols = ['comment_text', 'Comment', 'text', 'review']
                label_cols = ['label', 'sentiment', 'Sentiment', 'rating']
                
                text_col = None
                label_col = None
                
                for col in text_cols:
                    if col in self.df.columns:
                        text_col = col
                        break
                        
                for col in label_cols:
                    if col in self.df.columns:
                        label_col = col
                        break
                
                if text_col and label_col:
                    self.df = self.df[[text_col, label_col]].rename(columns={text_col: 'text', label_col: 'label'})
                else:
                    raise ValueError(f"Could not find text and label columns. Available columns: {self.df.columns.tolist()}")
            elif 'sentiment' in self.df.columns and 'label' not in self.df.columns:
                # Rename sentiment to label for consistency
                self.df = self.df.rename(columns={'sentiment': 'label'})
            
            # Clean the data
            self.df = self.df[['text', 'label']].dropna()
            
            # Remove empty texts
            self.df = self.df[self.df['text'].str.strip() != '']
            
            logger.info(f"Data after cleaning. Shape: {self.df.shape}")
            logger.info(f"Label distribution:\n{self.df['label'].value_counts()}")
            
            return self.df
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def split_data(self, test_size=0.2, random_state=42):
        """Split data into training and testing sets"""
        logger.info("Splitting data into train and test sets...")
        
        X = self.df['text']
        y = self.df['label']
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        logger.info(f"Training set size: {len(self.X_train)}")
        logger.info(f"Test set size: {len(self.X_test)}")
        
    def initialize_models(self):
        """Initialize the two most suitable machine learning models for sentiment analysis"""
        logger.info("Initializing models...")
        
        self.models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Naive Bayes': MultinomialNB()
        }
        
        logger.info(f"Initialized {len(self.models)} models: {list(self.models.keys())}")
        
    def train_and_evaluate_models(self):
        """Train and evaluate all models"""
        logger.info("Training and evaluating models...")
        
        # Initialize results storage
        self.results = {
            'Model': [],
            'Accuracy': [],
            'Precision': [],
            'Recall': [],
            'F1_Score': [],
            'Training_Time': [],
            'Prediction_Time': [],
            'CV_Accuracy': []
        }
        
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            
            # Create pipeline with TF-IDF vectorizer
            pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000, ngram_range=(1, 2))),
                ('classifier', model)
            ])
            
            # Measure training time
            start_time = time.time()
            pipeline.fit(self.X_train, self.y_train)
            training_time = time.time() - start_time
            
            # Measure prediction time
            start_time = time.time()
            y_pred = pipeline.predict(self.X_test)
            prediction_time = time.time() - start_time
            
            # Calculate metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='weighted')
            recall = recall_score(self.y_test, y_pred, average='weighted')
            f1 = f1_score(self.y_test, y_pred, average='weighted')
            
            # Cross-validation
            cv_scores = cross_val_score(pipeline, self.X_train, self.y_train, cv=5, scoring='accuracy')
            cv_accuracy = cv_scores.mean()
            
            # Store results
            self.results['Model'].append(name)
            self.results['Accuracy'].append(accuracy)
            self.results['Precision'].append(precision)
            self.results['Recall'].append(recall)
            self.results['F1_Score'].append(f1)
            self.results['Training_Time'].append(training_time)
            self.results['Prediction_Time'].append(prediction_time)
            self.results['CV_Accuracy'].append(cv_accuracy)
            
            # Store trained pipeline
            self.trained_pipelines[name] = pipeline
            
            logger.info(f"{name} - Accuracy: {accuracy:.4f}, F1: {f1:.4f}, Training Time: {training_time:.4f}s")
        
        # Convert results to DataFrame
        self.results_df = pd.DataFrame(self.results)
        logger.info("Model training and evaluation completed!")
        
    def save_best_model(self):
        """Save the best performing model"""
        best_idx = np.argmax(self.results['Accuracy'])
        best_model_name = self.results['Model'][best_idx]
        best_pipeline = self.trained_pipelines[best_model_name]
        
        # Save the best model
        model_path = f"model/best_sentiment_model_{best_model_name.replace(' ', '_').lower()}.pkl"
        joblib.dump(best_pipeline, model_path)
        
        # Extract and save the TF-IDF vectorizer separately for Spark streaming
        tfidf_vectorizer = best_pipeline.named_steps['tfidf']
        vectorizer_path = "model/tfidf_vectorizer.pkl"
        joblib.dump(tfidf_vectorizer, vectorizer_path)
        
        # Extract and save the classifier separately
        classifier = best_pipeline.named_steps['classifier']
        classifier_path = f"model/{best_model_name.replace(' ', '_').lower()}_classifier.pkl"
        joblib.dump(classifier, classifier_path)
        
        # Save model metadata
        metadata = {
            'model_name': best_model_name,
            'accuracy': self.results['Accuracy'][best_idx],
            'f1_score': self.results['F1_Score'][best_idx],
            'precision': self.results['Precision'][best_idx],
            'recall': self.results['Recall'][best_idx],
            'training_time': self.results['Training_Time'][best_idx],
            'model_path': model_path,
            'vectorizer_path': vectorizer_path,
            'classifier_path': classifier_path
        }
        
        import json
        with open(f"model/best_model_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Best model ({best_model_name}) saved to {model_path}")
        logger.info(f"TF-IDF vectorizer saved to {vectorizer_path}")
        logger.info(f"Classifier saved to {classifier_path}")
        logger.info(f"Best model accuracy: {self.results['Accuracy'][best_idx]:.4f}")
        
        return best_model_name, model_path
        
    def create_visualizations(self):
        """Create comprehensive visualizations comparing the two models"""
        logger.info("Creating visualizations...")
        
        # Set up the figure with subplots (2x2 layout for 2 models)
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('Sentiment Analysis Model Comparison: Logistic Regression vs Naive Bayes', fontsize=16, fontweight='bold')
        
        # 1. Model Accuracy Comparison
        ax1 = plt.subplot(2, 2, 1)
        bars1 = ax1.bar(self.results_df['Model'], self.results_df['Accuracy'], 
                       color=['#ff9999', '#66b3ff'])
        ax1.set_title('Model Accuracy Comparison', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Models')
        ax1.set_ylabel('Accuracy')
        ax1.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 2. F1-Score Comparison
        ax2 = plt.subplot(2, 2, 2)
        bars2 = ax2.bar(self.results_df['Model'], self.results_df['F1_Score'], 
                       color=['#99ff99', '#ffcc99'])
        ax2.set_title('F1-Score Comparison', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Models')
        ax2.set_ylabel('F1 Score')
        ax2.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 3. Training Time Comparison
        ax3 = plt.subplot(2, 2, 3)
        bars3 = ax3.bar(self.results_df['Model'], self.results_df['Training_Time'], 
                       color=['#ff99cc', '#c2c2f0'])
        ax3.set_title('Training Time Comparison', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Models')
        ax3.set_ylabel('Time (seconds)')
        
        # Add value labels on bars
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.3f}s', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # 4. Training Data Label Distribution
        ax4 = plt.subplot(2, 2, 4)
        label_counts = self.df['label'].value_counts()
        colors = ['#ff9999', '#66b3ff', '#99ff99'][:len(label_counts)]
        wedges, texts, autotexts = ax4.pie(label_counts.values, labels=label_counts.index, 
                                         autopct='%1.1f%%', startangle=90, colors=colors)
        ax4.set_title('Training Data Label Distribution', fontsize=14, fontweight='bold')
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig('model/sentiment_analysis_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()  # Close the figure to free memory
        
        logger.info("Visualizations saved to 'model/sentiment_analysis_comparison.png'")
        
    def print_detailed_results(self):
        """Print detailed results for all models"""
        logger.info("\n" + "="*80)
        logger.info("DETAILED MODEL COMPARISON RESULTS")
        logger.info("="*80)
        
        # Sort by accuracy for better presentation
        sorted_df = self.results_df.sort_values('Accuracy', ascending=False)
        
        for idx, row in sorted_df.iterrows():
            logger.info(f"\n{row['Model']}:")
            logger.info(f"  Accuracy:        {row['Accuracy']:.4f}")
            logger.info(f"  Precision:       {row['Precision']:.4f}")
            logger.info(f"  Recall:          {row['Recall']:.4f}")
            logger.info(f"  F1-Score:        {row['F1_Score']:.4f}")
            logger.info(f"  CV Accuracy:     {row['CV_Accuracy']:.4f}")
            logger.info(f"  Training Time:   {row['Training_Time']:.4f}s")
            logger.info(f"  Prediction Time: {row['Prediction_Time']:.4f}s")
        
        logger.info("\n" + "="*80)
        
    def run_full_analysis(self):
        """Run the complete sentiment analysis comparison"""
        logger.info("Starting comprehensive sentiment analysis model comparison...")
        
        # Load and preprocess data
        self.load_and_preprocess_data()
        
        # Split data
        self.split_data()
        
        # Initialize models
        self.initialize_models()
        
        # Train and evaluate all models
        self.train_and_evaluate_models()
        
        # Save best model
        best_model_name, model_path = self.save_best_model()
        
        # Create visualizations
        self.create_visualizations()
        
        # Print detailed results
        self.print_detailed_results()
        
        logger.info("\n🎉 Analysis completed successfully!")
        logger.info(f"Best model: {best_model_name}")
        logger.info(f"Model saved to: {model_path}")
        logger.info("Visualizations saved to: model/sentiment_analysis_comparison.png")
        
        return self.results_df


def main():
    """Main function to run the sentiment analysis comparison"""
    try:
        # Initialize the analysis
        analyzer = SentimentAnalysisMLComparison()  # Will auto-detect best available dataset
        
        # Run the complete analysis
        results = analyzer.run_full_analysis()
        
        return results
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    results = main()
