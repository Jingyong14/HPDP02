import praw
import json
import time
from kafka import KafkaProducer
from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta
from collections import deque

def get_kafka_producer():
    """Initializes and returns a KafkaProducer instance."""
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    print(f"🔍 Using Kafka servers: {kafka_servers}")
    try:
        producer = KafkaProducer(
            bootstrap_servers=[kafka_servers],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            retry_backoff_ms=1000,
            request_timeout_ms=30000,
            api_version=(0, 11, 5)
        )
        # Test connection
        producer.bootstrap_connected()
        print("✅ Kafka Producer connected successfully.")
        return producer
    except Exception as e:
        print(f"❌ Failed to connect to Kafka: {e}")
        return None

def get_reddit_instance():
    """Initializes and returns a PRAW Reddit instance."""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=f'script:pyspark-stream-test:v1.0 (by /u/{os.getenv("REDDIT_USERNAME")})',
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD')
        )
        print(f"Authenticated with Reddit as: {reddit.user.me()}")
        return reddit
    except Exception as e:
        print(f"Failed to authenticate with Reddit: {e}")
        return None

def fetch_reddit_posts(producer, reddit):
    """Fetches Reddit posts based on mode (batch or realtime)"""
    mode = os.getenv('MODE', 'realtime')  # Default to realtime mode
    
    if mode == 'batch':
        fetch_batch_posts(producer, reddit)
    else:
        fetch_realtime_posts(producer, reddit)

def fetch_batch_posts(producer, reddit):
    """Fetch historical posts from January 1-31, 2025"""
    subreddit_names = ['malaysia', 'MalaysianFood', 'malaysiauni']
    
    print(f"📅 Starting BATCH mode: January 1-31, 2025")
    print(f"🎯 Subreddits: {subreddit_names}")
    
    # Define date range for January 2025
    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
    
    total_posts_sent = 0
    
    for subreddit_name in subreddit_names:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            print(f"Fetching from r/{subreddit_name}...")
            
            # Fetch posts from different time periods to get January data
            for time_filter in ['month', 'week']:
                for post in subreddit.top(time_filter=time_filter, limit=200):
                    post_date = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                    
                    # Only send posts from January 2025
                    if start_date <= post_date <= end_date:
                        if send_post_to_kafka(producer, post, subreddit_name, 'batch'):
                            total_posts_sent += 1
                            
                        # Also fetch comments for this post
                        post.comments.replace_more(limit=3)
                        for comment in post.comments.list()[:10]:
                            comment_date = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                            if start_date <= comment_date <= end_date and len(comment.body) > 10:
                                if send_comment_to_kafka(producer, comment, post, subreddit_name, 'batch'):
                                    total_posts_sent += 1
                                    
        except Exception as e:
            print(f"❌ Error fetching from r/{subreddit_name}: {e}")
    
    print(f"✅ Batch mode completed. Total items sent: {total_posts_sent}")

def fetch_realtime_posts(producer, reddit):
    """Fetch posts from last 3 hours continuously"""
    subreddit_names = ['malaysia', 'MalaysianFood', 'malaysiauni']
    
    print(f"⏱️  Starting REALTIME mode: Last 3 hours")
    print(f"🎯 Subreddits: {subreddit_names}")
    print("🔄 Will refresh every 5 minutes...")
    
    seen_posts = set()
    cycle = 0
    
    while True:
        cycle += 1
        three_hours_ago = datetime.now(timezone.utc) - timedelta(hours=3)
        
        print(f"\n🔍 Cycle {cycle}: Scanning posts newer than {three_hours_ago.strftime('%H:%M:%S UTC')}")
        
        current_batch_count = 0
        
        for subreddit_name in subreddit_names:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                
                # Get new posts from last 3 hours
                for post in subreddit.new(limit=100):
                    post_date = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                    
                    if post_date >= three_hours_ago and post.id not in seen_posts:
                        if send_post_to_kafka(producer, post, subreddit_name, 'realtime'):
                            seen_posts.add(post.id)
                            current_batch_count += 1
                            
                        # Fetch recent comments
                        post.comments.replace_more(limit=2)
                        for comment in post.comments.list()[:5]:
                            comment_date = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                            if (comment_date >= three_hours_ago and 
                                len(comment.body) > 10 and 
                                comment.id not in seen_posts):
                                if send_comment_to_kafka(producer, comment, post, subreddit_name, 'realtime'):
                                    seen_posts.add(comment.id)
                                    current_batch_count += 1
                                    
            except Exception as e:
                print(f"❌ Error fetching from r/{subreddit_name}: {e}")
        
        print(f"📊 Cycle {cycle}: Sent {current_batch_count} new items")
        
        # Clean up seen_posts periodically
        if len(seen_posts) > 10000:
            seen_posts.clear()
            print("🧹 Cleared seen posts cache")
        
        print("⏰ Waiting 5 minutes for next scan...")
        time.sleep(300)  # 5 minutes

def send_comment_to_kafka(producer, comment, parent_post, subreddit_name, mode):
    """Helper function to send a comment to Kafka"""
    try:
        comment_datetime = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
        
        comment_data = {
            'id': comment.id,
            'title': f"Comment on: {parent_post.title[:50]}...",
            'content': comment.body,
            'score': comment.score,
            'created_utc': comment.created_utc,
            'created_date': comment_datetime.isoformat(),
            'author': str(comment.author) if comment.author else '[deleted]',
            'subreddit': subreddit_name,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content_type': 'comment',
            'processing_mode': mode
        }
        
        producer.send('reddit-posts', value=comment_data)
        print(f"    ↳ Sent comment: {comment.body[:30]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error sending comment to Kafka: {e}")
        return False

def send_post_to_kafka(producer, post, subreddit_name, mode='realtime'):
    """Helper function to send a single post to Kafka"""
    try:
        # Fix: Use proper timezone handling
        post_datetime = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
        
        post_data = {
            'id': post.id,
            'title': post.title,
            'content': post.selftext,
            'score': post.score,
            'num_comments': post.num_comments,
            'created_utc': post.created_utc,
            'created_date': post_datetime.isoformat(),
            'author': str(post.author) if post.author else '[deleted]',
            'subreddit': subreddit_name,
            'url': post.url,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'fetch_method': 'reddit_api',
            'content_type': 'post',
            'processing_mode': mode  # Add processing mode
        }

        future = producer.send('reddit-posts', value=post_data)
        # Wait for send to complete
        future.get(timeout=10)
        
        post_date = post_datetime.strftime('%Y-%m-%d')
        print(f"  ✓ Sent post from {post_date}: {post.title[:60]}...")
        
        time.sleep(0.1)  # Respect API limits
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to send post {post.id}: {e}")
        return False

def send_comments_to_kafka(producer, post, subreddit_name):
    """Fetch and send comments for a specific post"""
    try:
        post.comments.replace_more(limit=0)  # Remove "more comments" placeholders
        
        for comment in post.comments.list()[:10]:  # Limit to top 10 comments per post
            if hasattr(comment, 'body') and comment.body != '[deleted]':
                comment_datetime = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                
                comment_data = {
                    'id': comment.id,
                    'title': f"Comment on: {post.title[:50]}...",  # Reference to parent post
                    'content': comment.body,
                    'score': comment.score,
                    'num_comments': 0,  # Comments don't have sub-comments in this context
                    'created_utc': comment.created_utc,
                    'created_date': comment_datetime.isoformat(),
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'subreddit': subreddit_name,
                    'url': f"https://reddit.com{comment.permalink}",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'fetch_method': 'reddit_api',
                    'content_type': 'comment',  # Mark as comment
                    'parent_post_id': post.id  # Link to parent post
                }
                
                future = producer.send('reddit-posts', value=comment_data)
                future.get(timeout=10)
                
                comment_date = comment_datetime.strftime('%Y-%m-%d')
                print(f"    ↳ Sent comment from {comment_date}: {comment.body[:40]}...")
                
    except Exception as e:
        print(f"    ↳ Failed to fetch comments for post {post.id}: {e}")

def main():
    # Load environment variables from parent directory (commented out for Docker)
    # load_dotenv('../../.env.local')

    mode = os.getenv('MODE', 'realtime')
    print(f"[DEBUG] MODE: {mode}")
    producer = get_kafka_producer()
    reddit = get_reddit_instance()

    if producer and reddit:
        try:
            if mode == 'batch':
                print("🚀 Starting BATCH Reddit data collection")
                print("📅 Target: January 1-31, 2025")
            else:
                print("🚀 Starting REAL-TIME Reddit data collection")
                print("⏱️  Target: Last 3 hours (refreshing every 5 minutes)")
            print("🎯 Subreddits: malaysia, MalaysianFood, malaysiauni")
            print("=" * 70)
            fetch_reddit_posts(producer, reddit)
            print("✅ Data collection completed successfully!")
        except KeyboardInterrupt:
            print("\n⏹️  Data collection stopped by user")
        except Exception as e:
            import traceback
            print(f"❌ An error occurred during data collection: {e}")
            traceback.print_exc()
        finally:
            if producer:
                print("Flushing Kafka producer...")
                producer.flush()
                producer.close()
                print("Kafka producer closed.")
    else:
        print("❌ Failed to initialize Kafka producer or Reddit client")

if __name__ == "__main__":
    main()
