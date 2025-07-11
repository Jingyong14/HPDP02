"""
Reddit Tourism Data Producer for Malaysian Tourism Sentiment Analysis
=====================================================================

This producer collects tourism-related posts and comments from multiple Reddit
subreddits, focusing on Malaysian tourism destinations and experiences.

Features:
- Multi-subreddit data collection
- Keyword-based filtering for Malaysian tourism content
- Multiple fetching strategies (hot, new, top, search)
- Real-time Kafka streaming
- Comprehensive error handling and rate limiting
- Progress tracking and logging

Author: Big Data & NLP Analytics Team
Date: June 22, 2025
Course Deadline: June 27, 2025
"""

import praw
import json
import time
import logging
import os
import re
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import List, Dict, Set, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Try to import Kafka, but continue without it if not available
try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Kafka not available: {e}")
    print("📝 Running in FILE-ONLY mode - data will be saved to JSON files")
    KAFKA_AVAILABLE = False
    KafkaProducer = None

# Load environment variables
load_dotenv('.env.local')

# Ensure logs directory exists for logging
os.makedirs('logs', exist_ok=True)

# Setup comprehensive logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/reddit_tourism_producer.log'))
    ]
)
logger = logging.getLogger(__name__)

class MalaysianTourismProducer:
    """Enhanced Reddit producer for Malaysian tourism sentiment analysis"""
    
    def __init__(self, bootstrap_servers: str = None, topic_name: str = None, fetch_interval: int = 60, posts_per_fetch: int = 50):
        """Initialize Reddit API and Kafka connections"""
        self.setup_directories()
        self.setup_reddit()
        self.setup_kafka()
        self.load_configuration()
        self.processed_posts = set()
        self.stats = {
            'posts_collected': 0,
            'comments_collected': 0,
            'malaysia_related': 0,
            'filtered_out': 0,
            'api_errors': 0,
            'start_time': datetime.now()
        }
        
        # Real-time streaming parameters
        if bootstrap_servers:
            self.bootstrap_servers = bootstrap_servers
            self.topic_name = topic_name
            self.fetch_interval = fetch_interval
            self.posts_per_fetch = posts_per_fetch
            self.should_run = True
            
            # DISABLE FILE SAVING IN STREAMING MODE
            self.file_mode = False
            self.streaming_mode = True
            
            # Initialize Kafka producer for real-time streaming
            self.producer = KafkaProducer(
                bootstrap_servers=[bootstrap_servers],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            
            logger.info(f"✅ Real-time producer initialized - STREAMING ONLY")
            logger.info(f"📊 Kafka server: {bootstrap_servers}")
            logger.info(f"📊 Topic: {topic_name}")
            logger.info(f"📊 Fetch interval: {fetch_interval} seconds")
            logger.info(f"📊 Posts per fetch: {posts_per_fetch}")
            logger.info(f"⚠️  NO FILE SAVING - Pure streaming mode")
        else:
            # Regular mode - use files
            self.streaming_mode = False
    
    def setup_directories(self):
        """Create necessary directories"""
        dirs = ['logs', 'data/raw', 'data/processed', 'data/analytics']
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
        logger.info("✅ Project directories created/verified")
        
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
            
        except Exception as e:
            logger.error(f"❌ Reddit API connection failed: {e}")
            raise
            
    def setup_kafka(self):
        """Setup Kafka producer with Docker-optimized settings"""
        if not KAFKA_AVAILABLE:
            logger.info("⚠️ Kafka not available - using file-based storage")
            self.producer = None
            self.file_mode = True
            self.setup_file_output()
            return
            
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],  # Docker Kafka
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                batch_size=16384,
                linger_ms=10,
                retries=5,
                acks='all',
                request_timeout_ms=30000,
                api_version=(2, 8, 0),  # Updated API version
                connections_max_idle_ms=540000,
                max_in_flight_requests_per_connection=5
            )
            self.topic = 'malaysian-tourism-sentiment'
            self.file_mode = False
            logger.info(f"✅ Kafka producer connected to Docker Kafka: {self.topic}")
            
        except Exception as e:
            logger.error(f"❌ Kafka connection failed: {e}")
            logger.info("📝 Falling back to file-based storage")
            self.producer = None
            self.file_mode = True
            self.setup_file_output()
    
    def setup_file_output(self):
        """Setup file-based output when Kafka is not available"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.posts_file = f'data/raw/malaysia_tourism_posts_{timestamp}.jsonl'
        self.comments_file = f'data/raw/malaysia_tourism_comments_{timestamp}.jsonl'
        logger.info(f"📁 File mode enabled:")
        logger.info(f"  Posts: {self.posts_file}")
        logger.info(f"  Comments: {self.comments_file}")
    
    def load_configuration(self):
        """Load configuration from environment variables"""
        self.subreddits = os.getenv('SUBREDDITS', 'malaysia,travel').split(',')
        self.keywords = [kw.strip().lower() for kw in os.getenv('SEARCH_KEYWORDS', 'malaysia').split(',')]
        self.max_posts = int(os.getenv('MAX_POSTS', 800))
        self.max_comments = int(os.getenv('MAX_COMMENTS_PER_POST', 15))
        self.max_search_results = int(os.getenv('MAX_SEARCH_RESULTS', 200))
        self.strategies = os.getenv('FETCH_STRATEGIES', 'hot,new,top,search').split(',')
        self.time_filter = os.getenv('TIME_FILTER', 'month')
        self.request_delay = float(os.getenv('REDDIT_REQUEST_DELAY', 1))
        
        logger.info(f"📋 Configuration loaded:")
        logger.info(f"  Subreddits: {self.subreddits}")
        logger.info(f"  Keywords: {len(self.keywords)} Malaysian tourism terms")
        logger.info(f"  Max posts: {self.max_posts}, Max comments per post: {self.max_comments}")
        logger.info(f"  Strategies: {self.strategies}")
    
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
            r'\bbatu caves\b', r'\bklcc\b', r'\bpetronas\b'
        ]
        
        for pattern in malaysia_patterns:
            if re.search(pattern, combined_text):
                return True
                
        return False
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text content"""
        if not text:
            return ""
            
        # Remove URLs if configured
        if os.getenv('REMOVE_URLS', 'true').lower() == 'true':
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions if configured
        if os.getenv('REMOVE_MENTIONS', 'true').lower() == 'true':
            text = re.sub(r'@\w+', '', text)
        
        # Basic cleaning
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = text.strip()
        
        # Length filtering
        min_length = int(os.getenv('MIN_TEXT_LENGTH', 10))
        max_length = int(os.getenv('MAX_TEXT_LENGTH', 5000))
        
        if len(text) < min_length or len(text) > max_length:
            return ""
            
        return text
    
    def format_post_data(self, post) -> Optional[Dict]:
        """Format Reddit post data with enhanced metadata"""
        try:
            content = self.clean_text(post.selftext) or self.clean_text(post.title)
            
            if not content:
                return None
                
            # Check if Malaysia-related
            is_relevant = self.is_malaysia_related(content, post.title)
            
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
                'collection_strategy': getattr(post, '_collection_strategy', 'unknown'),
                'collection_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error formatting post {post.id}: {e}")
            self.stats['api_errors'] += 1
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
            
            comment_data = {
                'id': comment.id,
                'title': f"Comment on: {post_title[:100]}...",
                'content': content,
                'content_type': 'comment',
                'parent_post_id': parent_post_id,
                'score': comment.score,
                'created_date': datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat(),
                'author': str(comment.author) if comment.author else '[deleted]',
                'subreddit': str(comment.subreddit),
                'permalink': f"https://reddit.com{comment.permalink}",
                'is_malaysia_related': is_relevant,
                'text_length': len(content),
                'is_stickied': getattr(comment, 'stickied', False),
                'parent_comment_id': getattr(comment.parent(), 'id', None) if comment.parent() != parent_post_id else None,
                'collection_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return comment_data
            
        except Exception as e:
            logger.error(f"Error formatting comment {comment.id}: {e}")
            self.stats['api_errors'] += 1
            return None
    
    def publish_to_kafka(self, message: Dict) -> bool:
        """Publish message to Kafka topic"""
        try:
            # Use message ID as key for partitioning
            key = message.get('id', str(datetime.now().timestamp()))
            
            # Send to Kafka
            future = self.producer.send(self.topic_name, key=key, value=message)
            
            # Wait for confirmation (optional, for reliability)
            future.get(timeout=10)
            
            logger.debug(f"📤 Published: {message.get('content_type')} - {message.get('content', '')[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish to Kafka: {e}")
            return False
    
    def send_to_kafka(self, data: Dict) -> bool:
        """Send data to Kafka topic or save to file with error handling"""
        
        # If in streaming mode, ONLY send to Kafka (no file fallback)
        if hasattr(self, 'streaming_mode') and self.streaming_mode:
            try:
                future = self.producer.send(
                    self.topic_name,  # Use streaming topic name
                    key=data['id'], 
                    value=data
                )
                future.get(timeout=10)  # Wait for confirmation
                return True
            except Exception as e:
                logger.error(f"❌ Kafka streaming failed: {e}")
                return False
        
        # Regular mode - try Kafka first, then file fallback
        if self.file_mode:
            return self.save_to_file(data)
        
        try:
            future = self.producer.send(
                self.topic, 
                key=data['id'], 
                value=data
            )
            future.get(timeout=10)  # Wait for confirmation
            return True
            
        except Exception as e:
            logger.error(f"Failed to send to Kafka: {e}")
            logger.info("📝 Falling back to file storage for this item")
            return self.save_to_file(data)
    
    def save_to_file(self, data: Dict) -> bool:
        """Save data to appropriate file based on content type"""
        try:
            if data['content_type'] == 'post':
                with open(self.posts_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
            elif data['content_type'] == 'comment':
                with open(self.comments_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
            return True
        except Exception as e:
            logger.error(f"Failed to save to file: {e}")
            return False
    
    def collect_posts_and_comments(self, limit: int = 50) -> List[Dict]:
        """Collect posts and comments using ALL strategies for real-time streaming"""
        posts_data = []
        
        try:
            # Calculate posts per strategy and subreddit
            posts_per_strategy = limit // len(self.strategies)
            posts_per_subreddit = max(1, posts_per_strategy // len(self.subreddits))
            
            logger.info(f"🔍 Using {len(self.strategies)} strategies: {self.strategies}")
            logger.info(f"📊 Posts per strategy: {posts_per_strategy}, per subreddit: {posts_per_subreddit}")
            
            # Loop through ALL strategies (like producer2.py)
            for strategy in self.strategies:
                strategy = strategy.strip()
                logger.info(f"🔄 Strategy: {strategy.upper()}")
                
                for subreddit_name in self.subreddits:
                    subreddit_name = subreddit_name.strip()
                    
                    try:
                        subreddit = self.reddit.subreddit(subreddit_name)
                        logger.info(f"📊 Collecting {strategy} posts from r/{subreddit_name} (limit: {posts_per_subreddit})")
                        
                        # Apply the SAME strategy logic as producer2.py
                        if strategy == 'hot':
                            posts = subreddit.hot(limit=posts_per_subreddit)
                        elif strategy == 'new':
                            posts = subreddit.new(limit=posts_per_subreddit)
                        elif strategy == 'top':
                            posts = subreddit.top(time_filter=self.time_filter, limit=posts_per_subreddit)
                        elif strategy == 'search':
                            # Search for Malaysian tourism keywords (like producer2.py)
                            search_query = ' OR '.join(self.keywords[:5])  # Use top 5 keywords
                            logger.info(f"🔍 Searching r/{subreddit_name} for: {search_query}")
                            posts = subreddit.search(search_query, limit=posts_per_subreddit, time_filter=self.time_filter)
                        else:
                            logger.warning(f"Unknown strategy: {strategy}")
                            continue
                        
                        # Process posts from this strategy
                        strategy_posts = 0
                        for post in posts:
                            if post.id in self.processed_posts:
                                continue
                                
                            self.processed_posts.add(post.id)
                            setattr(post, '_collection_strategy', strategy)  # Track which strategy found this
                            
                            # Process post
                            post_data = self.format_post_data(post)
                            if post_data:
                                posts_data.append(post_data)
                                strategy_posts += 1
                                
                                if post_data['is_malaysia_related']:
                                    logger.info(f"🇲🇾 {strategy.upper()}: {post.title[:60]}...")
                                
                                # Collect comments (limited for real-time)
                                try:
                                    post.comments.replace_more(limit=0)
                                    comments = post.comments.list()[:5]  # Limit comments for real-time
                                    
                                    for comment in comments:
                                        comment_data = self.format_comment_data(comment, post.id, post.title)
                                        if comment_data:
                                            posts_data.append(comment_data)
                                            
                                except Exception as e:
                                    logger.error(f"Error collecting comments for post {post.id}: {e}")
                        
                            # Rate limiting
                            time.sleep(self.request_delay)
                            
                            # Stop if we have enough for this strategy/subreddit
                            if strategy_posts >= posts_per_subreddit:
                                break
                        
                        logger.info(f"✅ {strategy.upper()} r/{subreddit_name}: {strategy_posts} posts collected")
                        
                    except Exception as e:
                        logger.error(f"❌ Error with {strategy} from r/{subreddit_name}: {e}")
                        continue
        
            logger.info(f"📊 TOTAL COLLECTED: {len(posts_data)} items using all strategies")
            return posts_data

        except Exception as e:
            logger.error(f"❌ Error in collect_posts_and_comments: {e}")
            return posts_data
    
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
                setattr(post, '_collection_strategy', strategy)
                
                # Process post
                post_data = self.format_post_data(post)
                if post_data:
                    if self.send_to_kafka(post_data):
                        collected += 1
                        self.stats['posts_collected'] += 1
                        
                        if post_data['is_malaysia_related']:
                            self.stats['malaysia_related'] += 1
                            logger.info(f"🇲🇾 Malaysia-related post: {post.title[:60]}...")
                        else:
                            self.stats['filtered_out'] += 1
                        
                        # Collect comments
                        comment_count = self.collect_comments(post, post_data['title'])
                        self.stats['comments_collected'] += comment_count
                else:
                    self.stats['filtered_out'] += 1
                
                # Rate limiting
                time.sleep(self.request_delay)
                
                # Progress reporting
                if collected % 50 == 0 and collected > 0:
                    self.log_progress()
                    
            return collected
            
        except Exception as e:
            logger.error(f"Error collecting from r/{subreddit_name} ({strategy}): {e}")
            self.stats['api_errors'] += 1
            return 0
    
    def collect_comments(self, post, post_title: str) -> int:
        """Collect comments from a post"""
        try:
            post.comments.replace_more(limit=1)  # Expand comment threads
            comments = post.comments.list()[:self.max_comments]  # Use configured limit instead of 5
            # OR: comments = post.comments.list()  # For ALL comments
            collected = 0
            
            for comment in comments:
                comment_data = self.format_comment_data(comment, post.id, post_title)
                if comment_data and self.send_to_kafka(comment_data):
                    collected += 1
                    
            return collected
            
        except Exception as e:
            logger.error(f"Error collecting comments for post {post.id}: {e}")
            return 0
    
    def log_progress(self):
        """Log current progress and statistics"""
        elapsed = datetime.now() - self.stats['start_time']
        
        logger.info("📊 PROGRESS REPORT")
        logger.info(f"  Runtime: {elapsed}")
        logger.info(f"  Posts collected: {self.stats['posts_collected']}")
        logger.info(f"  Comments collected: {self.stats['comments_collected']}")
        logger.info(f"  Malaysia-related: {self.stats['malaysia_related']}")
        logger.info(f"  Filtered out: {self.stats['filtered_out']}")
        logger.info(f"  API errors: {self.stats['api_errors']}")
        logger.info(f"  Total items: {self.stats['posts_collected'] + self.stats['comments_collected']}")
    
    def start_streaming(self):
        """Start real-time streaming to Kafka"""
        logger.info("🚀 Starting real-time Reddit streaming...")
        
        try:
            while self.should_run:
                start_time = time.time()
                
                logger.info(f"📡 Fetching {self.posts_per_fetch} posts...")
                
                # Fetch posts and comments
                posts_data = self.collect_posts_and_comments(limit=self.posts_per_fetch)
                
                if posts_data:
                    # Publish each message to Kafka
                    published_count = 0
                    for message in posts_data:
                        if self.publish_to_kafka(message):
                            published_count += 1
                    
                    logger.info(f"📤 Published {published_count}/{len(posts_data)} messages to Kafka")
                    
                    # Log sample of what was published
                    if posts_data:
                        sample = posts_data[0]
                        logger.info(f"📊 Sample: {sample.get('content_type')} - {sample.get('content', '')[:100]}...")
                else:
                    logger.warning("⚠️ No posts collected this cycle")
                
                # Wait for next fetch cycle
                elapsed = time.time() - start_time
                sleep_time = max(0, self.fetch_interval - elapsed)
                
                if sleep_time > 0:
                    logger.info(f"⏱️ Waiting {sleep_time:.1f} seconds until next fetch...")
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("🛑 Streaming stopped by user")
        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
        finally:
            self.producer.close()
            logger.info("✅ Producer closed")
    
    def stop_streaming(self):
        """Stop streaming"""
        self.should_run = False
    
    def run_collection(self):
        """Main collection process"""
        logger.info("🚀 Starting Malaysian Tourism Data Collection")
        logger.info("=" * 60)
        
        try:
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
            
            # Final statistics
            self.log_progress()
            
            logger.info("✅ COLLECTION COMPLETED!")
            logger.info(f"🎯 Target achieved: {self.stats['posts_collected']}/{self.max_posts} posts")
            logger.info(f"💬 Bonus comments: {self.stats['comments_collected']}")
            logger.info(f"🇲🇾 Malaysia relevance: {self.stats['malaysia_related']}/{self.stats['posts_collected'] + self.stats['comments_collected']} items")
            
        except KeyboardInterrupt:
            logger.info("🛑 Collection stopped by user")
        except Exception as e:
            logger.error(f"❌ Collection failed: {e}")
            raise
        finally:
            if self.producer:
                self.producer.close()
            logger.info("🔚 Producer closed")

def main():
    """Main execution function"""
    try:
        producer = MalaysianTourismProducer()
        producer.run_collection()
        
    except Exception as e:
        logger.error(f"❌ Application failed: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())