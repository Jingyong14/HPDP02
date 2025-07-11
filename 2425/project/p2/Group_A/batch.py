#!/usr/bin/env python3
"""
Integrated Batch Pipeline for Malaysian Tourism Sentiment Analysis
================================================================

This unified pipeline combines data collection and model training:
1. Reddit Data Collection with VADER sentiment analysis
2. Train Naive Bayes sentiment model 
3. Train LSTM sentiment model
4. Generate performance comparison

Features:
- Integrated data collection and training
- VADER sentiment analysis during collection
- Sequential execution with dependency checking
- Comprehensive error handling and logging
- Progress tracking and timing
- Data validation between stages
- Configurable execution modes

Author: Big Data & NLP Analytics Team
Date: July 10, 2025
"""

import os
import sys
import time
import logging
import subprocess
import traceback
import praw
import json
import re
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Set
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import reddit_tourism_consumer2 as consumer2

# Load environment variables
load_dotenv('.env.local')

# Ensure proper encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    # Only redirect if not already redirected
    if hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        except (AttributeError, ValueError):
            pass  # Keep original stdout if redirection fails
    
    if hasattr(sys.stderr, 'buffer'):
        try:
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
        except (AttributeError, ValueError):
            pass  # Keep original stderr if redirection fails

# Setup logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/batch_integrated_pipeline.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class MalaysianTourismIntegratedPipeline:
    """Complete integrated pipeline for Malaysian tourism sentiment analysis"""
    
    def __init__(self, skip_collection: bool = False, skip_naive_bayes: bool = False, skip_lstm: bool = False, skip_predictions: bool = False):
        """Initialize the integrated pipeline"""
        self.skip_collection = skip_collection
        self.skip_naive_bayes = skip_naive_bayes
        self.skip_lstm = skip_lstm
        self.skip_predictions = skip_predictions  # ✅ NEW
        
        self.pipeline_start_time = datetime.now()
        self.stage_times = {}
        self.stage_results = {}
        
        # File paths
        self.data_file = 'data/raw/malaysia_tourism_data.csv'
        self.predicted_data_file = 'data/processed/predicted_malaysia_tourism_data.csv'  # ✅ NEW
        self.nb_model_dir = 'models/naive_bayes'
        self.lstm_model_dir = 'models/lstm'
        
        # Minimum data requirements
        self.min_data_samples = 100
        self.min_samples_per_class = 10
        
        # Data collection configuration
        self.processed_posts = set()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.collection_stats = {
            'posts_collected': 0,
            'comments_collected': 0,
            'malaysia_related': 0,
            'filtered_out': 0,
            'api_errors': 0,
            'start_time': datetime.now()
        }
        
        self.setup_directories()
        self.load_collection_configuration()
        
    def setup_directories(self):
        """Create necessary directories for the pipeline"""
        dirs = [
            'logs', 'data/raw', 'data/processed', 'data/analytics',
            'models', 'models/naive_bayes', 'models/lstm', 'reports'
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
        logger.info("SETUP: Pipeline directories created/verified")
    
    def load_collection_configuration(self):
        """Load data collection configuration from environment variables"""
        self.subreddits = os.getenv('SUBREDDITS', 'malaysia,travel,backpacking,solotravel,TravelNoPics').split(',')
        self.keywords = [kw.strip().lower() for kw in os.getenv('SEARCH_KEYWORDS', 
            'malaysia,kuala lumpur,penang,langkawi,cameron highlands,malacca,kota kinabalu,johor bahru,ipoh,genting highlands').split(',')]
        self.max_posts = int(os.getenv('MAX_POSTS', 800))
        self.max_comments = int(os.getenv('MAX_COMMENTS_PER_POST', 15))
        self.max_search_results = int(os.getenv('MAX_SEARCH_RESULTS', 200))
        self.strategies = os.getenv('FETCH_STRATEGIES', 'hot,new,top,search').split(',')
        self.time_filter = os.getenv('TIME_FILTER', 'month')
        self.request_delay = float(os.getenv('REDDIT_REQUEST_DELAY', 1))
        
        logger.info(f"📋 Collection Configuration loaded:")
        logger.info(f"  Subreddits: {self.subreddits}")
        logger.info(f"  Keywords: {len(self.keywords)} Malaysian tourism terms")
        logger.info(f"  Max posts: {self.max_posts}, Max comments per post: {self.max_comments}")
        logger.info(f"  Strategies: {self.strategies}")
    
    def log_stage_start(self, stage_name: str):
        """Log the start of a pipeline stage"""
        logger.info("=" * 60)
        logger.info(f"STAGE START: {stage_name}")
        logger.info("=" * 60)
        self.stage_times[stage_name] = {'start': datetime.now()}
        
    def log_stage_end(self, stage_name: str, success: bool = True, details: str = ""):
        """Log the end of a pipeline stage"""
        end_time = datetime.now()
        start_time = self.stage_times[stage_name]['start']
        duration = end_time - start_time
        
        self.stage_times[stage_name]['end'] = end_time
        self.stage_times[stage_name]['duration'] = duration
        self.stage_times[stage_name]['success'] = success
        
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"STAGE END: {stage_name} - {status}")
        logger.info(f"Duration: {duration}")
        if details:
            logger.info(f"Details: {details}")
        logger.info("=" * 60)
    
    def setup_reddit(self):
        """Setup Reddit API connection with enhanced error handling"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                username=os.getenv('REDDIT_USERNAME'),
                password=os.getenv('REDDIT_PASSWORD'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'Malaysian Tourism Sentiment Analysis Bot v2.0'),
                ratelimit_seconds=300  # Handle rate limiting gracefully
            )            
            # Test connection
            test_user = self.reddit.user.me()
            logger.info(f"✅ Reddit API connected successfully as: {test_user.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Reddit API connection failed: {e}")
            return False
    
    def is_malaysia_related(self, text: str, title: str = "") -> bool:
        """Check if content is related to Malaysian tourism"""
        combined_text = f"{title} {text}".lower()
        
        # Check for Malaysian keywords
        for keyword in self.keywords:
            if keyword in combined_text:
                return True
                
        # Additional patterns for Malaysian content
        malaysia_patterns = [
            r'\bkl\b', r'\bmalaysia\b', r'\bmalaysian\b', 
            r'\bringgit\b', r'\brm\d+\b', r'\bmyr\b',
            r'\bbatu caves\b', r'\bklcc\b', r'\bpetronas\b',
            r'\btwin towers\b', r'\bgenting\b', r'\bpinang\b'
        ]
        
        for pattern in malaysia_patterns:
            if re.search(pattern, combined_text):
                return True
                
        return False
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text content"""
        if not text:
            return ""
            
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions
        text = re.sub(r'@\w+', '', text)
        
        # Basic cleaning
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = text.strip()
        
        # Length filtering
        min_length = 10
        max_length = 5000
        
        if len(text) < min_length or len(text) > max_length:
            return ""
            
        return text
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """Analyze sentiment using VADER"""
        try:
            if not text or len(text.strip()) < 3:
                return {'sentiment_label': 'neutral', 'sentiment_compound': 0.0}
            
            # Get VADER scores
            scores = self.sentiment_analyzer.polarity_scores(text)
            compound = scores['compound']
            
            # Determine label based on compound score
            if compound >= 0.05:
                label = 'positive'
            elif compound <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'sentiment_label': label,
                'sentiment_compound': round(compound, 4)
            }
            
        except Exception as e:
            logger.error(f"❌ Sentiment analysis failed: {e}")
            return {'sentiment_label': 'neutral', 'sentiment_compound': 0.0}
    
    def format_post_data(self, post, strategy: str) -> Optional[Dict]:
        """Format Reddit post data with enhanced metadata"""
        try:
            content = self.clean_text(post.selftext) or self.clean_text(post.title)
            
            if not content:
                return None
                
            # Check if Malaysia-related
            is_relevant = self.is_malaysia_related(content, post.title)
            
            # Analyze sentiment
            sentiment_result = self.analyze_sentiment(content)
            
            post_data = {
                'id': post.id,
                'title': post.title,
                'content': content,
                'content_type': 'post',
                'parent_post_id': post.id,
                'score': post.score,
                'upvote_ratio': getattr(post, 'upvote_ratio', 0),
                'num_comments': post.num_comments,
                'created_date': datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                'author': str(post.author) if post.author else '[deleted]',
                'subreddit': str(post.subreddit),
                'url': post.url,
                'permalink': f"https://reddit.com{post.permalink}",
                'is_malaysia_related': is_relevant,
                'text_length': len(content),
                'flair': getattr(post, 'link_flair_text', None),
                'is_nsfw': post.over_18,
                'is_spoiler': post.spoiler,
                'collection_strategy': strategy,
                'collection_timestamp': datetime.now(timezone.utc).isoformat(),
                **sentiment_result
            }
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error formatting post {post.id}: {e}")
            self.collection_stats['api_errors'] += 1
            return None
    
    def format_comment_data(self, comment, parent_post_id: str, post_title: str) -> Optional[Dict]:
        """Format Reddit comment data with enhanced metadata"""
        try:
            if not hasattr(comment, 'body') or comment.body in ['[deleted]', '[removed]']:
                return None
                
            content = self.clean_text(comment.body)
            if not content:
                return None
                
            # Check if Malaysia-related
            is_relevant = self.is_malaysia_related(content, post_title)
            
            # Analyze sentiment
            sentiment_result = self.analyze_sentiment(content)
            
            comment_data = {
                'id': comment.id,
                'title': f"Comment on: {post_title[:100]}...",
                'content': content,
                'content_type': 'comment',
                'parent_post_id': parent_post_id,
                'score': comment.score,
                'upvote_ratio': 0,  # Comments don't have upvote ratio
                'num_comments': 0,  # Comments don't have num_comments
                'created_date': datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat(),
                'author': str(comment.author) if comment.author else '[deleted]',
                'subreddit': str(comment.subreddit),
                'url': '',  # Comments don't have separate URLs
                'permalink': f"https://reddit.com{comment.permalink}",
                'is_malaysia_related': is_relevant,
                'text_length': len(content),
                'flair': None,  # Comments don't have flair
                'is_nsfw': False,  # Comments inherit from post
                'is_spoiler': False,  # Comments inherit from post
                'collection_strategy': 'comment',
                'collection_timestamp': datetime.now(timezone.utc).isoformat(),
                **sentiment_result
            }
            
            return comment_data
            
        except Exception as e:
            logger.error(f"Error formatting comment {comment.id}: {e}")
            self.collection_stats['api_errors'] += 1
            return None
    
    def get_csv_headers(self) -> List[str]:
        """Define CSV column headers"""
        return [
            'id', 'content_type', 'title', 'content', 'sentiment_label', 
            'sentiment_compound', 'subreddit', 'score', 'author', 'created_date',
            'is_malaysia_related', 'text_length', 'collection_strategy', 
            'url', 'permalink', 'num_comments', 'upvote_ratio'
        ]
    
    def setup_csv_file(self):
        """Initialize CSV file with headers"""
        try:
            headers = self.get_csv_headers()
            with open(self.data_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            logger.info("✅ CSV file initialized with headers")
        except Exception as e:
            logger.error(f"❌ Failed to setup CSV file: {e}")
    
    def save_to_csv(self, data: Dict) -> bool:
        """Save data to CSV"""
        try:
            headers = self.get_csv_headers()
            row = []
            
            for header in headers:
                value = data.get(header, '')
                # Handle special cases
                if value is None:
                    value = ''
                elif isinstance(value, bool):
                    value = str(value).lower()
                elif isinstance(value, (list, dict)):
                    value = str(value)
                row.append(value)
            
            # Write to CSV
            with open(self.data_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save to CSV: {e}")
            return False
    
    def collect_from_subreddit(self, subreddit_name: str, strategy: str, limit: int) -> int:
        """Collect posts from a subreddit using specified strategy"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            collected = 0
            
            logger.info(f"📊 Collecting {strategy} posts from r/{subreddit_name} (limit: {limit})")
            
            if strategy == 'hot':
                posts = subreddit.hot(limit=limit)
            elif strategy == 'new':
                posts = subreddit.new(limit=limit)
            elif strategy == 'top':
                posts = subreddit.top(time_filter=self.time_filter, limit=limit)
            elif strategy == 'search':
                # Search for Malaysian tourism keywords
                search_query = ' OR '.join(self.keywords[:5])  # Use top 5 keywords
                posts = subreddit.search(search_query, limit=limit, time_filter=self.time_filter)
            else:
                logger.warning(f"Unknown strategy: {strategy}")
                return 0
            
            for post in posts:
                if post.id in self.processed_posts:
                    continue
                    
                self.processed_posts.add(post.id)
                
                # Process post
                post_data = self.format_post_data(post, strategy)
                if post_data:
                    if self.save_to_csv(post_data):
                        collected += 1
                        self.collection_stats['posts_collected'] += 1
                        
                        if post_data['is_malaysia_related']:
                            self.collection_stats['malaysia_related'] += 1
                            logger.info(f"🇲🇾 Malaysia-related post: {post.title[:60]}...")
                        else:
                            self.collection_stats['filtered_out'] += 1
                        
                        # Collect comments
                        comment_count = self.collect_comments(post, post_data['title'])
                        self.collection_stats['comments_collected'] += comment_count
                else:
                    self.collection_stats['filtered_out'] += 1
                
                # Rate limiting
                time.sleep(self.request_delay)
                
                # Progress reporting
                if collected % 50 == 0 and collected > 0:
                    self.log_collection_progress()
                    
            return collected
            
        except Exception as e:
            logger.error(f"Error collecting from r/{subreddit_name} ({strategy}): {e}")
            self.collection_stats['api_errors'] += 1
            return 0
    
    def collect_comments(self, post, post_title: str) -> int:
        """Collect comments from a post"""
        try:
            post.comments.replace_more(limit=0)
            comments = post.comments.list()[:self.max_comments]
            collected = 0
            
            for comment in comments:
                comment_data = self.format_comment_data(comment, post.id, post_title)
                if comment_data and self.save_to_csv(comment_data):
                    collected += 1
                    
            return collected
            
        except Exception as e:
            logger.error(f"Error collecting comments for post {post.id}: {e}")
            return 0
    
    def log_collection_progress(self):
        """Log current collection progress and statistics"""
        elapsed = datetime.now() - self.collection_stats['start_time']
        
        logger.info("📊 COLLECTION PROGRESS REPORT")
        logger.info(f"  Runtime: {elapsed}")
        logger.info(f"  Posts collected: {self.collection_stats['posts_collected']}")
        logger.info(f"  Comments collected: {self.collection_stats['comments_collected']}")
        logger.info(f"  Malaysia-related: {self.collection_stats['malaysia_related']}")
        logger.info(f"  Filtered out: {self.collection_stats['filtered_out']}")
        logger.info(f"  API errors: {self.collection_stats['api_errors']}")
        logger.info(f"  Total items: {self.collection_stats['posts_collected'] + self.collection_stats['comments_collected']}")
    
    def run_data_collection(self) -> bool:
        """Run the integrated data collection stage"""
        self.log_stage_start("Data Collection (Integrated)")
        
        try:
            # Check if data already exists and is recent
            if os.path.exists(self.data_file):
                file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(self.data_file))
                
                if file_age < timedelta(hours=24):  # Data is less than 24 hours old
                    logger.info(f"SKIP: Recent data file exists (age: {file_age})")
                    logger.info("Use --force-collection to override")
                    
                    # Still check data quality
                    is_quality_ok, quality_stats = self.check_data_quality(self.data_file)
                    
                    if is_quality_ok:
                        self.log_stage_end("Data Collection (Integrated)", True, f"Using existing data: {quality_stats['total_samples']} samples")
                        self.stage_results['data_collection'] = quality_stats
                        return True
                    else:
                        logger.warning("QUALITY: Existing data has quality issues, collecting new data")
                        logger.warning(f"Issues: {quality_stats.get('issues', quality_stats.get('error'))}")
            
            # Setup Reddit API
            if not self.setup_reddit():
                self.log_stage_end("Data Collection (Integrated)", False, "Reddit API setup failed")
                return False
            
            # Initialize CSV file
            self.setup_csv_file()
            
            logger.info("🚀 Starting Integrated Malaysian Tourism Data Collection")
            logger.info("=" * 60)
            
            total_collected = 0
            posts_per_strategy = self.max_posts // len(self.strategies)
            posts_per_subreddit = posts_per_strategy // len(self.subreddits)
            
            for strategy in self.strategies:
                logger.info(f"🔄 Strategy: {strategy.upper()}")
                
                for subreddit_name in self.subreddits:
                    collected = self.collect_from_subreddit(
                        subreddit_name.strip(), 
                        strategy.strip(), 
                        posts_per_subreddit
                    )
                    total_collected += collected
                    
                    if total_collected >= self.max_posts:
                        logger.info(f"✅ Reached maximum posts limit: {self.max_posts}")
                        break
                        
                if total_collected >= self.max_posts:
                    break
            
            # Final collection statistics
            self.log_collection_progress()
            
            logger.info("✅ INTEGRATED COLLECTION COMPLETED!")
            logger.info(f"🎯 Target achieved: {self.collection_stats['posts_collected']}/{self.max_posts} posts")
            logger.info(f"💬 Bonus comments: {self.collection_stats['comments_collected']}")
            logger.info(f"🇲🇾 Malaysia relevance: {self.collection_stats['malaysia_related']}/{self.collection_stats['posts_collected'] + self.collection_stats['comments_collected']} items")
            
            # Validate collected data
            is_quality_ok, quality_stats = self.check_data_quality(self.data_file)
            
            if is_quality_ok:
                self.log_stage_end("Data Collection (Integrated)", True, f"Collected {quality_stats['total_samples']} samples")
                self.stage_results['data_collection'] = quality_stats
                
                # Log data statistics
                logger.info("DATA STATS:")
                logger.info(f"  Total samples: {quality_stats['total_samples']}")
                logger.info(f"  Malaysia-related: {quality_stats['malaysia_related']} ({quality_stats['malaysia_percentage']:.1f}%)")
                logger.info(f"  Sentiment distribution: {quality_stats['sentiment_distribution']}")
                
                return True
            else:
                error_msg = f"Data quality check failed: {quality_stats.get('issues', quality_stats.get('error'))}"
                self.log_stage_end("Data Collection (Integrated)", False, error_msg)
                return False
                
        except KeyboardInterrupt:
            logger.info("🛑 Collection stopped by user")
            self.log_stage_end("Data Collection (Integrated)", False, "Interrupted by user")
            return False
        except Exception as e:
            error_msg = f"Integrated data collection error: {e}"
            self.log_stage_end("Data Collection (Integrated)", False, error_msg)
            return False
    
    def check_data_quality(self, file_path: str) -> Tuple[bool, Dict]:
        """Check if collected data meets quality requirements"""
        try:
            if not os.path.exists(file_path):
                return False, {"error": "Data file does not exist"}
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Basic statistics
            total_samples = len(df)
            
            # Check required columns
            required_columns = ['content', 'sentiment_label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, {"error": f"Missing required columns: {missing_columns}"}
            
            # Check data quality
            non_empty_content = df[df['content'].notna() & (df['content'].astype(str).str.strip() != '')].shape[0]
            valid_sentiments = df[df['sentiment_label'].notna()].shape[0]
            
            # Sentiment distribution
            sentiment_counts = df['sentiment_label'].value_counts().to_dict()
            min_class_samples = min(sentiment_counts.values()) if sentiment_counts else 0
            
            # Malaysia-related content
            malaysia_related = df[df.get('is_malaysia_related', False) == True].shape[0] if 'is_malaysia_related' in df.columns else 0
            
            quality_stats = {
                'total_samples': total_samples,
                'non_empty_content': non_empty_content,
                'valid_sentiments': valid_sentiments,
                'sentiment_distribution': sentiment_counts,
                'min_class_samples': min_class_samples,
                'malaysia_related': malaysia_related,
                'malaysia_percentage': (malaysia_related / total_samples * 100) if total_samples > 0 else 0
            }
            
            # Quality checks
            quality_issues = []
            
            if total_samples < self.min_data_samples:
                quality_issues.append(f"Insufficient total samples: {total_samples} < {self.min_data_samples}")
            
            if min_class_samples < self.min_samples_per_class:
                quality_issues.append(f"Insufficient samples per class: {min_class_samples} < {self.min_samples_per_class}")
            
            if non_empty_content < total_samples * 0.8:
                quality_issues.append(f"Too many empty content fields: {non_empty_content}/{total_samples}")
            
            if len(sentiment_counts) < 3:
                quality_issues.append(f"Missing sentiment classes: only {list(sentiment_counts.keys())}")
            
            is_quality_ok = len(quality_issues) == 0
            
            if quality_issues:
                quality_stats['issues'] = quality_issues
            
            return is_quality_ok, quality_stats
            
        except Exception as e:
            return False, {"error": f"Data quality check failed: {e}"}
    
    def run_naive_bayes_training(self) -> bool:
        """Run the Naive Bayes model training stage"""
        self.log_stage_start("Naive Bayes Training")
        
        try:
            # Check if model already exists
            model_files = list(Path(self.nb_model_dir).glob('*.pkl'))
            
            if model_files:
                latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
                model_age = datetime.now() - datetime.fromtimestamp(latest_model.stat().st_mtime)
                
                if model_age < timedelta(hours=12):  # Model is less than 12 hours old
                    logger.info(f"SKIP: Recent Naive Bayes model exists (age: {model_age})")
                    logger.info("Use --force-training to override")
                    self.log_stage_end("Naive Bayes Training", True, f"Using existing model: {latest_model.name}")
                    return True
            
            # Run Naive Bayes training
            logger.info("EXECUTING: Running train_naive_bayes_model.py...")
            
            result = subprocess.run(
                [sys.executable, 'train_naive_bayes_model.py'],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("SUCCESS: Naive Bayes training completed")
                
                # Check if model files were created
                new_model_files = list(Path(self.nb_model_dir).glob('*.pkl'))
                
                if new_model_files:
                    latest_model = max(new_model_files, key=lambda p: p.stat().st_mtime)
                    self.log_stage_end("Naive Bayes Training", True, f"Model saved: {latest_model.name}")
                    self.stage_results['naive_bayes'] = {"model_path": str(latest_model)}
                    return True
                else:
                    self.log_stage_end("Naive Bayes Training", False, "No model files created")
                    return False
            else:
                error_msg = f"Naive Bayes training failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f"\nSTDERR: {result.stderr[-1000:]}"
                
                self.log_stage_end("Naive Bayes Training", False, error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "Naive Bayes training timed out after 30 minutes"
            self.log_stage_end("Naive Bayes Training", False, error_msg)
            return False
            
        except Exception as e:
            error_msg = f"Naive Bayes training error: {e}"
            self.log_stage_end("Naive Bayes Training", False, error_msg)
            return False
    
    def run_lstm_training(self) -> bool:
        """Run the LSTM model training stage"""
        self.log_stage_start("LSTM Training")
        
        try:
            # Check if model already exists
            model_files = list(Path(self.lstm_model_dir).glob('*.h5'))
            
            if model_files:
                latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
                model_age = datetime.now() - datetime.fromtimestamp(latest_model.stat().st_mtime)
                
                if model_age < timedelta(hours=12):  # Model is less than 12 hours old
                    logger.info(f"SKIP: Recent LSTM model exists (age: {model_age})")
                    logger.info("Use --force-training to override")
                    self.log_stage_end("LSTM Training", True, f"Using existing model: {latest_model.name}")
                    return True
            
            # Run LSTM training
            logger.info("EXECUTING: Running train_lstm_sentiment_model.py...")
            
            # Set environment variables to handle TensorFlow issues
            env = os.environ.copy()
            env['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings
            env['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations
            
            result = subprocess.run(
                [sys.executable, 'train_lstm_sentiment_model.py'],
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour timeout for LSTM training
                env=env
            )
            
            if result.returncode == 0:
                logger.info("SUCCESS: LSTM training completed")
                
                # Check if model files were created
                new_model_files = list(Path(self.lstm_model_dir).glob('*.h5'))
                
                if new_model_files:
                    latest_model = max(new_model_files, key=lambda p: p.stat().st_mtime)
                    self.log_stage_end("LSTM Training", True, f"Model saved: {latest_model.name}")
                    self.stage_results['lstm'] = {"model_path": str(latest_model)}
                    return True
                else:
                    self.log_stage_end("LSTM Training", False, "No model files created")
                    return False
            else:
                error_msg = f"LSTM training failed with return code {result.returncode}"
                if result.stderr:
                    stderr_msg = result.stderr[-1000:]
                    
                    # Check for common TensorFlow errors
                    if "DLL load failed" in stderr_msg or "_pywrap_tensorflow" in stderr_msg:
                        logger.warning("⚠️ TensorFlow DLL error detected")
                        logger.warning("💡 Try: pip install tensorflow==2.13.0")
                        logger.warning("💡 Install Visual C++ Redistributables")
                        self.log_stage_end("LSTM Training", True, "Skipped due to TensorFlow DLL issues")
                        return True  # Don't fail pipeline for TensorFlow issues
                    
                    error_msg += f"\nSTDERR: {stderr_msg}"
                
                self.log_stage_end("LSTM Training", False, error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "LSTM training timed out after 1 hour"
            self.log_stage_end("LSTM Training", False, error_msg)
            return False
            
        except Exception as e:
            error_msg = f"LSTM training error: {e}"
            self.log_stage_end("LSTM Training", False, error_msg)
            return False

    def generate_model_comparison(self):
        """Generate performance comparison between Naive Bayes and LSTM models"""
        try:
            logger.info("=" * 70)
            logger.info("MODEL PERFORMANCE COMPARISON")
            logger.info("=" * 70)
            
            # Load Naive Bayes results
            nb_metrics = self.load_model_metrics('naive_bayes')
            
            # Load LSTM results  
            lstm_metrics = self.load_model_metrics('lstm')
            
            # Display performance comparison
            self.display_performance_comparison(nb_metrics, lstm_metrics)
            
            # Save comparison data
            self.save_performance_comparison(nb_metrics, lstm_metrics)
            
        except Exception as e:
            logger.error(f"Failed to generate model comparison: {e}")

    def load_model_metrics(self, model_type: str) -> Dict:
        """Load performance metrics from model report files"""
        try:
            # Find the latest report file
            if model_type == 'naive_bayes':
                report_pattern = "*naive_bayes*training*report*.json"
            else:
                report_pattern = "*lstm*training*report*.json"
                
            report_files = list(Path('reports').glob(report_pattern))
            
            if not report_files:
                logger.warning(f"No {model_type} report files found")
                return {'status': 'No report found'}
            
            latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"Loading {model_type} metrics from: {latest_report.name}")
            
            import json
            with open(latest_report, 'r') as f:
                data = json.load(f)
            
            # Unified structure for both models
            return {
                'accuracy': data.get('test_accuracy', 'N/A'),
                'f1_score': data.get('f1_score', self.extract_f1_from_report(data.get('classification_report', ''))),
                'precision': data.get('precision', self.extract_precision_from_report(data.get('classification_report', ''))),
                'recall': data.get('recall', self.extract_recall_from_report(data.get('classification_report', ''))),
                'status': 'available'
            }
            
        except Exception as e:
            logger.warning(f"Could not load {model_type} metrics: {e}")
            return {'status': f'Error loading metrics: {e}'}

    def extract_f1_from_report(self, report_text: str) -> float:
        """Extract weighted average F1 score from classification report"""
        try:
            import re
            lines = str(report_text).split('\n')
            for line in lines:
                if 'weighted avg' in line:
                    numbers = re.findall(r'\d+\.\d+', line)
                    if len(numbers) >= 3:
                        return float(numbers[2])
            return 'N/A'
        except:
            return 'N/A'

    def extract_precision_from_report(self, report_text: str) -> float:
        """Extract weighted average precision from classification report"""
        try:
            import re
            lines = str(report_text).split('\n')
            for line in lines:
                if 'weighted avg' in line:
                    numbers = re.findall(r'\d+\.\d+', line)
                    if len(numbers) >= 1:
                        return float(numbers[0])
            return 'N/A'
        except:
            return 'N/A'

    def extract_recall_from_report(self, report_text: str) -> float:
        """Extract weighted average recall from classification report"""
        try:
            import re
            lines = str(report_text).split('\n')
            for line in lines:
                if 'weighted avg' in line:
                    numbers = re.findall(r'\d+\.\d+', line)
                    if len(numbers) >= 2:
                        return float(numbers[1])
            return 'N/A'
        except:
            return 'N/A'

    def display_performance_comparison(self, nb_metrics: Dict, lstm_metrics: Dict):
        """Display performance comparison table"""
        logger.info("PERFORMANCE METRICS:")
        logger.info("-" * 25)
        logger.info(f"{'Metric':<12} {'Naive Bayes':<12} {'LSTM':<12} {'Winner':<10}")
        logger.info("-" * 50)
        
        metrics = ['accuracy', 'f1_score', 'precision', 'recall']
        winners = {}
        
        for metric in metrics:
            nb_value = nb_metrics.get(metric, 'N/A')
            lstm_value = lstm_metrics.get(metric, 'N/A')
            
            # Determine winner
            winner = "N/A"
            if nb_value != 'N/A' and lstm_value != 'N/A':
                try:
                    nb_float = float(nb_value)
                    lstm_float = float(lstm_value)
                    if nb_float > lstm_float:
                        winner = "NB"
                        winners[metric] = 'naive_bayes'
                    elif lstm_float > nb_float:
                        winner = "LSTM"
                        winners[metric] = 'lstm'
                    else:
                        winner = "Tie"
                        winners[metric] = 'tie'
                except:
                    winner = "N/A"
            
            # Format values
            nb_display = f"{nb_value:.3f}" if isinstance(nb_value, (int, float)) else str(nb_value)
            lstm_display = f"{lstm_value:.3f}" if isinstance(lstm_value, (int, float)) else str(lstm_value)
            
            logger.info(f"{metric.title():<12} {nb_display:<12} {lstm_display:<12} {winner:<10}")
        
        logger.info("-" * 50)
        
        # Overall winner
        if winners:
            nb_wins = sum(1 for w in winners.values() if w == 'naive_bayes')
            lstm_wins = sum(1 for w in winners.values() if w == 'lstm')
            ties = sum(1 for w in winners.values() if w == 'tie')
            
            logger.info(f"WINS: Naive Bayes({nb_wins}) | LSTM({lstm_wins}) | Ties({ties})")
            
            if nb_wins > lstm_wins:
                logger.info("OVERALL WINNER: Naive Bayes")
            elif lstm_wins > nb_wins:
                logger.info("OVERALL WINNER: LSTM")
            else:
                logger.info("OVERALL RESULT: Tie")
        
        logger.info("=" * 70)

    def save_performance_comparison(self, nb_metrics: Dict, lstm_metrics: Dict):
        """Save performance comparison to JSON file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            comparison_file = f"reports/performance_comparison_integrated_{timestamp}.json"
            
            comparison_data = {
                'timestamp': datetime.now().isoformat(),
                'naive_bayes': nb_metrics,
                'lstm': lstm_metrics,
                'pipeline_duration': str(datetime.now() - self.pipeline_start_time),
                'data_source': 'integrated_collection_with_vader'
            }
            
            import json
            with open(comparison_file, 'w') as f:
                json.dump(comparison_data, f, indent=2, default=str)
            
            logger.info(f"Performance comparison saved to: {comparison_file}")
            
        except Exception as e:
            logger.error(f"Failed to save performance comparison: {e}")
    
    def run_pipeline(self) -> bool:
        """Run the complete integrated pipeline"""
        logger.info("STARTING: Malaysian Tourism Sentiment Analysis Integrated Pipeline")
        logger.info("=" * 80)
        logger.info(f"Pipeline Configuration:")
        logger.info(f"  Skip Data Collection: {self.skip_collection}")
        logger.info(f"  Skip Naive Bayes: {self.skip_naive_bayes}")
        logger.info(f"  Skip LSTM: {self.skip_lstm}")
        logger.info(f"  Skip Predictions: {self.skip_predictions}")
        logger.info(f"  Data File: {self.data_file}")
        logger.info(f"  Minimum Samples: {self.min_data_samples}")
        logger.info(f"  Collection Strategy: Integrated with VADER sentiment analysis")
        logger.info("=" * 80)
        
        try:
            success = True
            
            # Stage 1: Integrated Data Collection
            if not self.skip_collection:
                if not self.run_data_collection():
                    logger.error("FAILED: Integrated data collection stage failed")
                    success = False
            else:
                logger.info("SKIPPED: Integrated data collection stage")
                
                # Still validate existing data
                if os.path.exists(self.data_file):
                    is_quality_ok, quality_stats = self.check_data_quality(self.data_file)
                    if is_quality_ok:
                        self.stage_results['data_collection'] = quality_stats
                        logger.info(f"VALIDATED: Existing data has {quality_stats['total_samples']} samples")
                    else:
                        logger.error(f"INVALID: Existing data has quality issues: {quality_stats.get('issues', quality_stats.get('error'))}")
                        success = False
                else:
                    logger.error("MISSING: No data file found and collection skipped")
                    success = False
        
            # Stage 2: Naive Bayes Training
            if success and not self.skip_naive_bayes:
                if not self.run_naive_bayes_training():
                    logger.error("FAILED: Naive Bayes training stage failed")
                    success = False
            else:
                logger.info("SKIPPED: Naive Bayes training stage")

            # Stage 3: LSTM Training
            if success and not self.skip_lstm:
                if not self.run_lstm_training():
                    logger.error("FAILED: LSTM training stage failed")
                    success = False
            else:
                logger.info("SKIPPED: LSTM training stage")

            # Stage 4: Dual Model Predictions
            if success and not self.skip_predictions:
                if not self.run_dual_model_predictions():
                    logger.error("FAILED: Dual model predictions stage failed")
                    success = False
            else:
                logger.info("SKIPPED: Dual model predictions stage")

            # ✅ SWITCHED: Stage 5: Generate final comparison report (MOVED BEFORE dashboard)
            self.generate_model_comparison()

            # ✅ SWITCHED: Stage 6: Elasticsearch Dashboard (MOVED_AFTER comparison)
            if success:
                if not self.run_elasticsearch_dashboard_stage():
                    logger.warning("WARNING: Elasticsearch dashboard stage failed (non-critical)")
                    # Don't fail the entire pipeline for dashboard issues
        
            # Final status
            total_duration = datetime.now() - self.pipeline_start_time
            
            if success:
                logger.info("SUCCESS: Integrated pipeline completed successfully!")
                logger.info(f"Total execution time: {total_duration}")
                logger.info("All stages completed. Models are ready for deployment.")
                logger.info(f"🇲🇾 Malaysia-related items collected: {self.collection_stats['malaysia_related']}")
                logger.info(f"📊 Total items processed: {self.collection_stats['posts_collected'] + self.collection_stats['comments_collected']}")
                if not self.skip_predictions:
                    logger.info(f"🔮 Predictions saved to: {self.predicted_data_file}")
                    logger.info(f"📊 Dashboard URL: http://localhost:5601")
            else:
                logger.error("FAILED: Integrated pipeline completed with errors!")
                logger.error(f"Total execution time: {total_duration}")
                logger.error("Check logs and reports for details.")

            return success

        except KeyboardInterrupt:
            logger.info("INTERRUPTED: Integrated Pipeline stopped by user")
            return False
            
        except Exception as e:
            logger.error(f"FATAL: Integrated Pipeline failed with unexpected error: {e}")
            logger.error(f"Full error: {traceback.format_exc()}")
            return False

    def run_dual_model_predictions(self) -> bool:
        """Run predictions using both Naive Bayes and LSTM models separately"""
        self.log_stage_start("Dual Model Predictions")
        
        try:
            # ✅ NEW: Check if predicted data already exists
            if os.path.exists(self.predicted_data_file):
                file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(self.predicted_data_file))
                
                # Check if file is recent (less than 6 hours old)
                if file_age < timedelta(hours=6):
                    logger.info(f"SKIP: Recent predicted data file exists (age: {file_age})")
                    logger.info(f"File: {self.predicted_data_file}")
                    
                    # Validate the existing file structure
                    try:
                        df = pd.read_csv(self.predicted_data_file)
                        required_columns = ['id', 'content', 'sentiment_label', 'predicted_nb', 'nb_confidence', 'predicted_lstm', 'lstm_confidence']
                        
                        if all(col in df.columns for col in required_columns):
                            logger.info(f"✅ Existing file has {len(df)} prediction records with correct structure")
                            logger.info(f"📋 Columns: {list(df.columns)}")
                            self.log_stage_end("Dual Model Predictions", True, f"Using existing predictions: {len(df)} records")
                            return True
                        else:
                            missing_cols = [col for col in required_columns if col not in df.columns]
                            logger.warning(f"❌ Existing file missing columns: {missing_cols}")
                            logger.info("🔄 Regenerating predictions with correct structure...")
                    except Exception as e:
                        logger.warning(f"❌ Error reading existing file: {e}")
                        logger.info("🔄 Regenerating predictions...")
                else:
                    logger.info(f"OUTDATED: Predicted data file is old (age: {file_age})")
                    logger.info("🔄 Regenerating fresh predictions...")
        
            # Check if data file exists
            if not os.path.exists(self.data_file):
                self.log_stage_end("Dual Model Predictions", False, "Data file not found")
                return False
            
            # ✅ Initialize consumer2's sentiment analyzer
            logger.info("🔄 Loading dual model sentiment analyzer...")
            try:
                sentiment_analyzer = consumer2.MalaysianTourismSentimentAnalyzer()
            except Exception as e:
                logger.error(f"❌ Failed to initialize sentiment analyzer: {e}")
                self.log_stage_end("Dual Model Predictions", False, "Sentiment analyzer initialization failed")
                return False
            
            # ✅ IMPROVED: Check model availability more thoroughly
            models_available = []
            
            # Check Naive Bayes model
            try:
                if (hasattr(sentiment_analyzer, 'trained_model') and 
                    sentiment_analyzer.trained_model is not None and
                    hasattr(sentiment_analyzer, 'vectorizer') and
                    sentiment_analyzer.vectorizer is not None and
                    hasattr(sentiment_analyzer, 'label_encoder') and
                    sentiment_analyzer.label_encoder is not None):
                    models_available.append("Naive Bayes")
                    logger.info("✅ Naive Bayes model loaded successfully")
                else:
                    logger.warning("❌ Naive Bayes model not available (missing model/vectorizer/encoder)")
            except Exception as e:
                logger.warning(f"❌ Naive Bayes model check failed: {e}")
            
            # Check LSTM model
            try:
                if (hasattr(sentiment_analyzer, 'lstm_model') and 
                    sentiment_analyzer.lstm_model is not None and
                    hasattr(sentiment_analyzer, 'lstm_tokenizer') and
                    sentiment_analyzer.lstm_tokenizer is not None and
                    hasattr(sentiment_analyzer, 'lstm_label_encoder') and
                    sentiment_analyzer.lstm_label_encoder is not None):
                    models_available.append("LSTM")
                    logger.info("✅ LSTM model loaded successfully")
                else:
                    logger.warning("❌ LSTM model not available (missing model/tokenizer/encoder)")
            except Exception as e:
                logger.warning(f"❌ LSTM model check failed: {e}")
            
            # ✅ STOP if no models are available
            if not models_available:
                logger.warning("🛑 NO MODELS AVAILABLE FOR PREDICTION")
                logger.info("📋 To train models first, run:")
                logger.info("   python batch.py --skip-collection --skip-predictions")
                logger.info("📋 Model file locations to check:")
                logger.info(f"   Naive Bayes: {self.nb_model_dir}/")
                logger.info(f"   LSTM: {self.lstm_model_dir}/")
                
                self.log_stage_end("Dual Model Predictions", True, "Skipped - No models available")
                return True  # ✅ Return True to not fail the pipeline, just skip
        
            logger.info(f"📊 Available models: {', '.join(models_available)}")
            
            # Load data
            logger.info("📊 Loading data for dual model prediction...")
            df = pd.read_csv(self.data_file)
            logger.info(f"Data loaded: {len(df)} rows")
            
            # ✅ SIMPLIFIED: Create results list for CSV export
            results_list = []
            
            # Track prediction statistics
            prediction_stats = {
                'total_predictions': len(df),
                'nb_successful': 0,
                'lstm_successful': 0,
                'both_successful': 0,
                'agreements': 0,
                'disagreements': 0,
                'start_time': datetime.now()
            }
            
            logger.info("🚀 Starting dual model predictions...")
            
            # Process each row with both models
            for idx, row in df.iterrows():
                content = str(row.get('content', ''))
                row_id = row.get('id', idx)  # Use 'id' column or index as fallback
                sentiment_label = row.get('sentiment_label', 'unknown')
                
                # Skip empty content
                if not content or content.strip() == '':
                    continue
                
                # ✅ Initialize default values
                predicted_nb = 'neutral'
                nb_confidence = 0.0
                predicted_lstm = 'neutral'
                lstm_confidence = 0.0
                
                try:
                    # ✅ Use the dual model analysis function from consumer2.py
                    dual_results = sentiment_analyzer.analyze_sentiment_dual_models(content, "")
                    
                    # Extract Naive Bayes results
                    nb_result = dual_results.get('naive_bayes_result', {})
                    if 'error' not in nb_result:
                        predicted_nb = nb_result.get('label', 'neutral')
                        nb_confidence = nb_result.get('confidence', 0.0)
                        prediction_stats['nb_successful'] += 1
                    
                    # Extract LSTM results
                    lstm_result = dual_results.get('lstm_result', {})
                    if 'error' not in lstm_result:
                        predicted_lstm = lstm_result.get('label', 'neutral')
                        lstm_confidence = lstm_result.get('confidence', 0.0)
                        prediction_stats['lstm_successful'] += 1
                    
                    # Track agreement statistics
                    if 'error' not in nb_result and 'error' not in lstm_result:
                        prediction_stats['both_successful'] += 1
                        model_agreement = dual_results.get('model_agreement', {})
                        if model_agreement.get('labels_match', False):
                            prediction_stats['agreements'] += 1
                        else:
                            prediction_stats['disagreements'] += 1
            
                except Exception as e:
                    logger.error(f"Dual prediction error for row {idx}: {e}")
                
                # ✅ SIMPLIFIED: Add result to list with ONLY required columns
                results_list.append({
                    'id': row_id,
                    'content': content,
                    'sentiment_label': sentiment_label,
                    'predicted_nb': predicted_nb,
                    'nb_confidence': round(nb_confidence, 4),
                    'predicted_lstm': predicted_lstm,
                    'lstm_confidence': round(lstm_confidence, 4)
                })
                
                # Progress reporting every 500 rows
                if (idx + 1) % 500 == 0:
                    elapsed = datetime.now() - prediction_stats['start_time']
                    logger.info(f"Progress: {idx + 1}/{len(df)} dual predictions completed ({elapsed})")
        
            # ✅ SIMPLIFIED: Create CSV with ONLY required columns
            results_df = pd.DataFrame(results_list)
            
            # Create output directory
            Path('data/processed').mkdir(parents=True, exist_ok=True)
            
            # ✅ Save SIMPLIFIED CSV with exact columns requested
            results_df.to_csv(self.predicted_data_file, index=False, encoding='utf-8')
            
            # Log final statistics
            elapsed = datetime.now() - prediction_stats['start_time']
            logger.info("🎯 DUAL MODEL PREDICTION RESULTS:")
            logger.info(f"  Total rows processed: {prediction_stats['total_predictions']}")
            logger.info(f"  Available models: {', '.join(models_available)}")
            logger.info(f"  Naive Bayes successful: {prediction_stats['nb_successful']}")
            logger.info(f"  LSTM successful: {prediction_stats['lstm_successful']}")
            logger.info(f"  Both models successful: {prediction_stats['both_successful']}")
            logger.info(f"  Model agreements: {prediction_stats['agreements']}")
            logger.info(f"  Model disagreements: {prediction_stats['disagreements']}")
            if prediction_stats['both_successful'] > 0:
                agreement_rate = prediction_stats['agreements'] / prediction_stats['both_successful'] * 100
                logger.info(f"  Agreement rate: {agreement_rate:.1f}%")
            logger.info(f"  Processing time: {elapsed}")
            logger.info(f"  Output file: {self.predicted_data_file}")
            logger.info(f"📋 CSV columns: {list(results_df.columns)}")
            
            self.log_stage_end("Dual Model Predictions", True, f"Dual predictions saved to {self.predicted_data_file}")
            return True
        
        except Exception as e:
            error_msg = f"Dual model predictions error: {e}"
            logger.error(f"Full error: {traceback.format_exc()}")
            self.log_stage_end("Dual Model Predictions", False, error_msg)
            return False

    def run_elasticsearch_dashboard_stage(self) -> bool:
        self.log_stage_start("Elasticsearch Dashboard")
        
        try:
            # Check if predicted data file exists
            if not os.path.exists(self.predicted_data_file):
                logger.warning("🛑 NO PREDICTED DATA FOUND")
                logger.info("📋 Run predictions first:")
                logger.info("   python batch.py --skip-collection --skip-naive-bayes --skip-lstm")
                self.log_stage_end("Elasticsearch Dashboard", True, "Skipped - No predicted data available")
                return True
            
            # Import Elasticsearch directly
            try:
                from elasticsearch import Elasticsearch
                from elasticsearch.helpers import bulk
            except ImportError:
                logger.error("❌ Elasticsearch library not available. Install with: pip install elasticsearch")
                self.log_stage_end("Elasticsearch Dashboard", False, "Elasticsearch library missing")
                return False
            
            # Check if Elasticsearch is running
            if not self.check_service_running("localhost", 9200):
                logger.error("❌ Elasticsearch not running on localhost:9200")
                logger.info("💡 Make sure Elasticsearch is running:")
                logger.info("   docker-compose up -d elasticsearch kibana")
                self.log_stage_end("Elasticsearch Dashboard", False, "Elasticsearch not accessible")
                return False
            
            logger.info("✅ Elasticsearch detected on localhost:9200")
            
            # Create Elasticsearch client
            try:
                es_client = Elasticsearch(
                    hosts=["http://localhost:9200"],
                    basic_auth=("elastic", "changeme"),
                    verify_certs=False,
                    ssl_show_warn=False,
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                
                # Test connection
                if not es_client.ping():
                    logger.error("❌ Cannot connect to Elasticsearch")
                    self.log_stage_end("Elasticsearch Dashboard", False, "Elasticsearch connection failed")
                    return False
                
                logger.info("✅ Elasticsearch connection established")
                
            except Exception as e:
                logger.error(f"❌ Elasticsearch client creation failed: {e}")
                self.log_stage_end("Elasticsearch Dashboard", False, f"Connection error: {e}")
                return False
            
            # Index configuration
            index_base = "malaysia-tourism-predictions"
            date_suffix = datetime.now().strftime('%Y-%m')
            index_name = f"{index_base}-{date_suffix}"
            
            logger.info(f"📊 Elasticsearch Configuration:")
            logger.info(f"  Index: {index_name}")
            logger.info(f"  Data file: {self.predicted_data_file}")
            
            # Create index template
            self.create_prediction_index_template(es_client, index_base)
            
            # Load predicted data
            logger.info("📊 Loading predicted data for dashboard...")
            df = pd.read_csv(self.predicted_data_file)
            logger.info(f"Loaded {len(df)} prediction records")
            
            # ✅ FIXED: Prepare ALL documents first, then upload in batches
            all_documents = []
            current_time = datetime.now(timezone.utc)
            
            logger.info("🔄 Preparing documents for upload...")
            
            for idx, row in df.iterrows():
                # Create document
                doc = {
                    '_index': index_name,
                    '_source': {
                        'record_id': str(row.get('id', idx)),
                        'content': str(row.get('content', ''))[:1000],  # Limit content length
                        'original_sentiment': str(row.get('sentiment_label', 'unknown')),
                        
                        # Naive Bayes predictions
                        'nb_prediction': str(row.get('predicted_nb', 'neutral')),
                        'nb_confidence': float(row.get('nb_confidence', 0.0)),
                        
                        # LSTM predictions
                        'lstm_prediction': str(row.get('predicted_lstm', 'neutral')),
                        'lstm_confidence': float(row.get('lstm_confidence', 0.0)),
                        
                        # Accuracy fields (if original sentiment available)
                        'nb_correct': str(row.get('sentiment_label', 'unknown')) == str(row.get('predicted_nb', 'neutral')) if row.get('sentiment_label', 'unknown') != 'unknown' else None,
                        'lstm_correct': str(row.get('sentiment_label', 'unknown')) == str(row.get('predicted_lstm', 'neutral')) if row.get('sentiment_label', 'unknown') != 'unknown' else None,
                        
                        # Timestamp
                        '@timestamp': current_time.isoformat()
                    }
                }
                
                all_documents.append(doc)
            
            logger.info(f"✅ Prepared {len(all_documents)} documents for upload")
            
            # ✅ FIXED: Upload in batches with proper error handling
            batch_size = 1000
            total_uploaded = 0
            
            for i in range(0, len(all_documents), batch_size):
                batch = all_documents[i:i + batch_size]
                
                try:
                    # Upload batch
                    success, failed = bulk(
                        es_client, 
                        batch, 
                        chunk_size=500, 
                        request_timeout=60,
                        max_retries=3,
                        initial_backoff=2,
                        max_backoff=600
                    )
                    
                    total_uploaded += len(batch) - len(failed) if failed else len(batch)
                    
                    if failed:
                        logger.warning(f"⚠️ Batch {i//batch_size + 1}: {len(failed)} documents failed")
                    else:
                        logger.info(f"📤 Batch {i//batch_size + 1}: {len(batch)} documents uploaded successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Batch {i//batch_size + 1} upload failed: {e}")
            
            # ✅ FIXED: Force index refresh to make documents immediately searchable
            try:
                es_client.indices.refresh(index=index_name)
                logger.info("✅ Index refreshed - documents are now searchable")
            except Exception as e:
                logger.warning(f"⚠️ Failed to refresh index: {e}")
            
            # ✅ FIXED: Verify upload by checking document count
            try:
                count_response = es_client.count(index=index_name)
                actual_count = count_response['count']
                logger.info(f"✅ Verification: {actual_count} documents found in index")
                
                if actual_count == 0:
                    logger.error("❌ No documents found in index after upload!")
                    # Try a simple test document
                    test_doc = {
                        '_index': index_name,
                        '_source': {
                            'record_id': 'test_001',
                            'content': 'Test document for Malaysia tourism predictions',
                            'original_sentiment': 'positive',
                            'nb_prediction': 'positive',
                            'nb_confidence': 0.8,
                            'lstm_prediction': 'positive', 
                            'lstm_confidence': 0.9,
                            '@timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    }
                    
                    try:
                        es_client.index(index=index_name, body=test_doc['_source'])
                        es_client.indices.refresh(index=index_name)
                        logger.info("✅ Test document uploaded successfully")
                    except Exception as test_e:
                        logger.error(f"❌ Even test document failed: {test_e}")
                        
            except Exception as e:
                logger.warning(f"⚠️ Could not verify document count: {e}")
            
            # Generate dashboard statistics
            dashboard_stats = self.generate_dashboard_statistics(df)
            
            # ✅ NEW: Import Kibana dashboards and visualizations
            logger.info("🎨 Setting up Kibana dashboards...")

            # Import dashboard from NDJSON file
            if os.path.exists("export_batch.ndjson"):
                self.import_kibana_objects("export_batch.ndjson")
            else:
                logger.warning("❌ export_batch.ndjson not found")
                logger.info("💡 Place export_batch.ndjson in the project root for automatic dashboard import")

            # Wait a moment for Kibana to process
            import time
            time.sleep(3)

            # Log final statistics
            logger.info("🎯 ELASTICSEARCH DASHBOARD RESULTS:")
            logger.info(f"  Documents prepared: {len(all_documents)}")
            logger.info(f"  Documents uploaded: {total_uploaded}")
            logger.info(f"  Index name: {index_name}")
            logger.info(f"  Elasticsearch host: localhost:9200")
            logger.info(f"  Model agreement rate: {dashboard_stats['agreement_rate']:.1f}%")
            logger.info(f"  NB accuracy: {dashboard_stats['nb_accuracy']:.1f}%")
            logger.info(f"  LSTM accuracy: {dashboard_stats['lstm_accuracy']:.1f}%")
            logger.info(f"  🐳 Kibana URL: http://localhost:5601")
            logger.info(f"  📈 Index pattern: {index_base}-*")
            logger.info("🎨 DASHBOARDS:")
            logger.info("   → Go to Kibana → Dashboard")
            logger.info("   → Look for 'Malaysia Tourism Sentiment Analysis' dashboard")
            logger.info("   → Automatic visualizations ready!")

            self.log_stage_end("Elasticsearch Dashboard", True, f"{total_uploaded} documents uploaded to {index_name} with dashboards")
            return True

        except Exception as e:
            error_msg = f"Elasticsearch dashboard error: {e}"
            logger.error(f"Full error: {traceback.format_exc()}")
            self.log_stage_end("Elasticsearch Dashboard", False, error_msg)
            return False
            
    def create_prediction_index_template(self, es_client, index_base: str) -> bool:
        """Create Elasticsearch index template for prediction data with simplified mapping"""
        try:
            template_name = f"{index_base}-template"
            
            template_body = {
                "index_patterns": [f"{index_base}-*"],
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "index.refresh_interval": "5s"
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "record_id": {"type": "keyword"},
                        "content": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword", "ignore_above": 256}
                            }
                        },
                        "original_sentiment": {"type": "keyword"},
                        "nb_prediction": {"type": "keyword"},
                        "nb_confidence": {"type": "float"},
                        "lstm_prediction": {"type": "keyword"},
                        "lstm_confidence": {"type": "float"},
                        "nb_correct": {"type": "boolean"},
                        "lstm_correct": {"type": "boolean"}
                    }
                }
            }
            
            # Create or update template
            response = es_client.indices.put_template(
                name=template_name,
                body=template_body
            )
            
            logger.info(f"✅ Index template created: {template_name}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to create index template: {e}")
            return False

    def check_service_running(self, host: str, port: int) -> bool:
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                result = s.connect_ex((host, port))
                return result == 0
        except Exception as e:
            logger.error(f"❌ Service check failed for {host}:{port} - {e}")
            return False

    def generate_dashboard_statistics(self, df: pd.DataFrame) -> Dict:
        """Generate statistics for dashboard logging"""
        try:
            total_records = len(df)
            
            # Model agreement
            agreements = (df['predicted_nb'] == df['predicted_lstm']).sum()
            agreement_rate = (agreements / total_records * 100) if total_records > 0 else 0
            
            # Accuracy calculation (if ground truth available)
            nb_accuracy = 0
            lstm_accuracy = 0
            
            if 'sentiment_label' in df.columns:
                valid_labels = df[df['sentiment_label'] != 'unknown']
                if len(valid_labels) > 0:
                    nb_correct = (valid_labels['sentiment_label'] == valid_labels['predicted_nb']).sum()
                    lstm_correct = (valid_labels['sentiment_label'] == valid_labels['predicted_lstm']).sum()
                    nb_accuracy = (nb_correct / len(valid_labels) * 100)
                    lstm_accuracy = (lstm_correct / len(valid_labels) * 100)
            
            return {
                'total_records': total_records,
                'agreements': agreements,
                'agreement_rate': agreement_rate,
                'nb_accuracy': nb_accuracy,
                'lstm_accuracy': lstm_accuracy
            }
            
        except Exception as e:
            logger.warning(f"Failed to generate dashboard statistics: {e}")
            return {
                'total_records': len(df),
                'agreements': 0,
                'agreement_rate': 0,
                'nb_accuracy': 0,
                'lstm_accuracy': 0
            }
        
    def import_kibana_objects(self, ndjson_file: str = "export_batch.ndjson") -> bool:
        logger.info("📊 Importing Kibana index patterns and dashboards...")
        
        try:
            import requests
            
            # Check if export file exists
            if not os.path.exists(ndjson_file):
                logger.error(f"❌ {ndjson_file} not found in current directory")
                logger.info("💡 Please ensure export_batch.ndjson is in the project root")
                
                # Try alternative names
                alternative_files = ["export.ndjson", "kibana_export.ndjson", "dashboard_export.ndjson"]
                for alt_file in alternative_files:
                    if os.path.exists(alt_file):
                        logger.info(f"✅ Found alternative file: {alt_file}")
                        ndjson_file = alt_file
                        break
                else:
                    return False
            
            # Wait for Kibana to be ready
            kibana_url = "http://localhost:5601"
            max_wait = 60  # 1 minute
            wait_time = 0
            
            while wait_time < max_wait:
                try:
                    response = requests.get(f"{kibana_url}/api/status", timeout=5)
                    if response.status_code == 200:
                        logger.info("✅ Kibana is ready for import")
                        break
                except:
                    pass
                
                logger.info("⏱️ Waiting for Kibana to be ready...")
                time.sleep(5)
                wait_time += 5
            else:
                logger.error("❌ Kibana not ready for import")
                return False
            
            # Read the export file
            with open(ndjson_file, 'r', encoding='utf-8') as f:
                ndjson_content = f.read()
            
            logger.info(f"📁 File size: {len(ndjson_content)} bytes")
            logger.info(f"📋 File content preview: {ndjson_content[:200]}...")
            
            # Import objects using Kibana API
            import_url = f"{kibana_url}/api/saved_objects/_import"
            
            # Prepare the request
            files = {
                'file': (ndjson_file, ndjson_content, 'application/ndjson')
            }
            
            headers = {
                'kbn-xsrf': 'true'
            }
            
            # Add overwrite parameter
            params = {
                'overwrite': 'true'  # Overwrite existing objects
            }
            
            logger.info("📤 Uploading index patterns and dashboards to Kibana...")
            
            response = requests.post(
                import_url,
                files=files,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                success_count = result.get('successCount', 0)
                errors = result.get('errors', [])
                
                logger.info(f"✅ Successfully imported {success_count} Kibana objects")
                
                if errors:
                    logger.warning(f"⚠️ Import warnings: {len(errors)} objects had issues")
                    for error in errors[:3]:  # Show first 3 errors
                        error_msg = error.get('error', {}).get('message', 'Unknown error')
                        error_type = error.get('meta', {}).get('type', 'unknown')
                        logger.warning(f"  - {error_type}: {error_msg}")
                
                # Log what was imported
                success_results = result.get('successResults', [])
                if success_results:
                    logger.info("🎯 Successfully imported objects:")
                    for obj in success_results[:10]:  # Show first 10
                        obj_type = obj.get('meta', {}).get('type', 'unknown')
                        obj_title = obj.get('meta', {}).get('title', 'untitled')
                        logger.info(f"  ✅ {obj_type}: {obj_title}")
                
                return True
            else:
                logger.error(f"❌ Failed to import objects: HTTP {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Kibana import failed: {e}")
            import traceback
            logger.error(f"Full error: {traceback.format_exc()}")
            return False

    def start_dashboard_connection_only(self, es_client) -> bool:
        try:
            logger.info("📊 Setting up dashboard connection...")
            
            # Check if Elasticsearch is running
            if not self.check_service_running("localhost", 9200):
                logger.error("❌ Elasticsearch not running")
                return False
            
            logger.info("✅ Elasticsearch detected")
            
            # Test ES client connection
            if not es_client.ping():
                logger.error("❌ Cannot connect to Elasticsearch")
                return False
            
            logger.info("✅ Dashboard connection established")
            
            # Create index template (but NOT index patterns - they come from NDJSON)
            self.create_prediction_index_template(es_client, "malaysia-tourism-predictions")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Dashboard initialization failed: {e}")
            return False
def main():
    """Main function to run the integrated pipeline with command line arguments"""
    import argparse
    
    # Setup command line arguments
    parser = argparse.ArgumentParser(
        description='Malaysian Tourism Sentiment Analysis Integrated Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch.py                                    # Run complete pipeline
  python batch.py --skip-collection                  # Skip data collection
  python batch.py --skip-naive-bayes                 # Skip Naive Bayes training
  python batch.py --skip-lstm                        # Skip LSTM training
  python batch.py --skip-predictions                 # Skip dual model predictions
  python batch.py --skip-collection --skip-naive-bayes --skip-lstm    # Only run predictions + dashboard
        """
    )
    
    parser.add_argument('--skip-collection', 
                       action='store_true',
                       help='Skip the data collection stage')
    
    parser.add_argument('--skip-naive-bayes',
                       action='store_true', 
                       help='Skip the Naive Bayes training stage')
    
    parser.add_argument('--skip-lstm',
                       action='store_true',
                       help='Skip the LSTM training stage')
    
    parser.add_argument('--skip-predictions',
                       action='store_true',
                       help='Skip the dual model predictions stage')
    
    parser.add_argument('--force-collection',
                       action='store_true',
                       help='Force data collection even if recent data exists')
    
    parser.add_argument('--force-training',
                       action='store_true',
                       help='Force model training even if recent models exist')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable verbose logging')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("🔍 Verbose logging enabled")
    
    # Display startup banner
    logger.info("=" * 80)
    logger.info("🇲🇾 MALAYSIAN TOURISM SENTIMENT ANALYSIS - INTEGRATED PIPELINE")
    logger.info("=" * 80)
    logger.info("🚀 Starting integrated pipeline with following configuration:")
    logger.info(f"   Skip Data Collection: {args.skip_collection}")
    logger.info(f"   Skip Naive Bayes Training: {args.skip_naive_bayes}")
    logger.info(f"   Skip LSTM Training: {args.skip_lstm}")
    logger.info(f"   Skip Dual Predictions: {args.skip_predictions}")
    logger.info(f"   Force Collection: {args.force_collection}")
    logger.info(f"   Force Training: {args.force_training}")
    logger.info(f"   Verbose Mode: {args.verbose}")
    logger.info("=" * 80)
    
    try:
        # Initialize and run the integrated pipeline
        pipeline = MalaysianTourismIntegratedPipeline(
            skip_collection=args.skip_collection,
            skip_naive_bayes=args.skip_naive_bayes,
            skip_lstm=args.skip_lstm,
            skip_predictions=args.skip_predictions
        )
        
        # Handle force options
        if args.force_collection and os.path.exists(pipeline.data_file):
            logger.info("🔄 Force collection enabled - removing existing data file")
            os.remove(pipeline.data_file)
        
        if args.force_training:
            logger.info("🔄 Force training enabled - removing existing model files")
            import shutil
            if os.path.exists(pipeline.nb_model_dir):
                shutil.rmtree(pipeline.nb_model_dir)
                Path(pipeline.nb_model_dir).mkdir(parents=True, exist_ok=True)
            if os.path.exists(pipeline.lstm_model_dir):
                shutil.rmtree(pipeline.lstm_model_dir)
                Path(pipeline.lstm_model_dir).mkdir(parents=True, exist_ok=True)
        
        # Run the pipeline
        success = pipeline.run_pipeline()
        
        # Final status and exit
        if success:
            logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("🎯 All stages completed. Check reports/ directory for results.")
            logger.info("📊 Dashboard available at: http://localhost:5601")
            return 0
        else:
            logger.error("❌ PIPELINE FAILED!")
            logger.error("🔍 Check logs for detailed error information.")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Pipeline interrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    exit(main())