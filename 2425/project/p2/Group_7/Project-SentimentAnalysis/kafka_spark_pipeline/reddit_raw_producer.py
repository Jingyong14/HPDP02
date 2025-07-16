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
    try:
        producer = KafkaProducer(
            bootstrap_servers=[kafka_servers],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            retry_backoff_ms=1000
        )
        # Test connection
        producer.bootstrap_connected()
        print("Kafka Producer connected successfully.")
        return producer
    except Exception as e:
        print(f"Failed to connect to Kafka: {e}")
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
    """
    Fetches posts from a specific subreddit within a given date range.
    """
    subreddit_name = 'MalaysiaPolitics'
    
    # Fix: Use proper past dates for historical data
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    # Convert to UTC timestamps
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    print(f"Starting Reddit data fetch for r/{subreddit_name}")
    print(f"Date Range: {start_date.date()} to {end_date.date()}")
    print(f"Timestamp range: {start_timestamp} to {end_timestamp}")

    posts_sent = 0
    seen_posts = set()  # Avoid duplicates
    
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        # 1. Get more recent posts from 'new' with higher limit
        print("Fetching from 'new' posts...")
        for post in subreddit.new(limit=500):  # Increased limit
            if start_timestamp <= post.created_utc <= end_timestamp:
                if post.id not in seen_posts:
                    if send_post_to_kafka(producer, post, subreddit_name):
                        posts_sent += 1
                        seen_posts.add(post.id)
                        
        # 2. Get posts from 'hot' 
        print("Fetching from 'hot' posts...")
        for post in subreddit.hot(limit=100):
            if start_timestamp <= post.created_utc <= end_timestamp:
                if post.id not in seen_posts:
                    if send_post_to_kafka(producer, post, subreddit_name):
                        posts_sent += 1
                        seen_posts.add(post.id)
                        
        # 3. Get posts from 'top' for different time periods
        print("Fetching from 'top' posts...")
        for time_filter in ['month', 'week']:
            for post in subreddit.top(time_filter=time_filter, limit=100):
                if start_timestamp <= post.created_utc <= end_timestamp:
                    if post.id not in seen_posts:
                        if send_post_to_kafka(producer, post, subreddit_name):
                            posts_sent += 1
                            seen_posts.add(post.id)
                    
        # 4. Try broader search with food-related keywords
        print("Fetching from search with keywords...")
        search_terms = ['food', 'makan', 'lunch', 'dinner', 'restaurant', 'recipe']
        for term in search_terms:
            try:
                for post in subreddit.search(term, sort='new', time_filter='month', limit=50):
                    if start_timestamp <= post.created_utc <= end_timestamp:
                        if post.id not in seen_posts:
                            if send_post_to_kafka(producer, post, subreddit_name):
                                posts_sent += 1
                                seen_posts.add(post.id)
            except Exception as e:
                print(f"Search error for term '{term}': {e}")
    
    except Exception as e:
        print(f"An error occurred during fetch: {e}")
    
    finally:
        print(f"\n--- Fetch complete. Total unique posts sent: {posts_sent} ---")
        print(f"Date range actually covered: {start_date.date()} to {end_date.date()}")

def send_post_to_kafka(producer, post, subreddit_name):
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
            'content_type': 'post'  # Add content type
        }

        future = producer.send('reddit-posts', value=post_data)
        # Wait for send to complete
        future.get(timeout=10)
        
        post_date = post_datetime.strftime('%Y-%m-%d')
        print(f"  ✓ Sent post from {post_date}: {post.title[:60]}...")
        
        # Fetch comments for this post
        send_comments_to_kafka(producer, post, subreddit_name)
        
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
    # Load environment variables from parent directory
    load_dotenv('../../.env.local')
    
    producer = get_kafka_producer()
    reddit = get_reddit_instance()

    if producer and reddit:
        try:
            fetch_reddit_posts(producer, reddit)
        except KeyboardInterrupt:
            print("Stopping Reddit producer...")
        finally:
            if producer:
                print("Flushing and closing Kafka producer.")
                producer.flush()
                producer.close()
                print("Kafka producer closed.")

if __name__ == "__main__":
    main()
