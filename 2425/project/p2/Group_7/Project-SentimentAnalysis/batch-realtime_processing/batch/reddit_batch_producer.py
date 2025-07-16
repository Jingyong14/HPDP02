#!/usr/bin/env python3
"""
Reddit Batch Producer for Historical Data Analysis
Fetches historical Reddit data from January 1-31, 2025 for batch processing
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta
from kafka import KafkaProducer
import praw
from dotenv import load_dotenv

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Load environment variables
load_dotenv()

def get_kafka_producer():
    """Initialize Kafka producer for batch processing"""
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    try:
        producer = KafkaProducer(
            bootstrap_servers=[kafka_servers],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            retry_backoff_ms=1000
        )
        producer.bootstrap_connected()
        print("✅ Kafka Producer connected successfully for batch processing.")
        return producer
    except Exception as e:
        print(f"❌ Failed to connect to Kafka: {e}")
        return None

def get_reddit_instance():
    """Initialize Reddit instance"""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent='script:batch-sentiment-analysis:v1.0',
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD')
        )
        print(f"✅ Authenticated with Reddit as: {reddit.user.me()}")
        return reddit
    except Exception as e:
        print(f"❌ Failed to authenticate with Reddit: {e}")
        return None

def fetch_batch_data(producer, reddit):
    """
    Fetch historical data from January 1-31, 2025
    """
    subreddit_names = ['malaysia', 'MalaysianFood', 'malaysiauni']
    
    # Define date range for January 2025
    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 1, 31, 23, 59, 59, tzinfo=timezone.utc)
    
    print(f"🔍 Starting batch data collection for: {subreddit_names}")
    print(f"📅 Date range: {start_date.date()} to {end_date.date()}")
    
    total_posts_sent = 0
    
    for subreddit_name in subreddit_names:
        print(f"\n📊 Processing r/{subreddit_name}...")
        
        try:
            subreddit = reddit.subreddit(subreddit_name)
            posts_from_subreddit = 0
            
            # Fetch top posts from different time periods to maximize coverage
            for time_filter in ['month', 'week']:
                print(f"  Fetching {time_filter} posts...")
                
                for submission in subreddit.top(time_filter=time_filter, limit=500):
                    post_date = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
                    
                    # Filter by date range
                    if start_date <= post_date <= end_date:
                        # Send post data
                        post_data = {
                            'id': submission.id,
                            'title': submission.title,
                            'content': submission.selftext if submission.selftext else submission.title,
                            'author': str(submission.author) if submission.author else '[deleted]',
                            'subreddit': subreddit_name,
                            'score': submission.score,
                            'created_utc': submission.created_utc,
                            'created_date': post_date.isoformat(),
                            'type': 'post',
                            'processing_mode': 'batch'
                        }
                        
                        producer.send('reddit-posts', value=post_data)
                        posts_from_subreddit += 1
                        total_posts_sent += 1
                        
                        print(f"  ✓ Sent post from {post_date.date()}: {submission.title[:50]}...")
                        
                        # Also fetch comments for this post
                        submission.comments.replace_more(limit=3)
                        for comment in submission.comments.list()[:15]:  # Limit comments per post
                            comment_date = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                            
                            if start_date <= comment_date <= end_date and len(comment.body) > 10:
                                comment_data = {
                                    'id': comment.id,
                                    'title': f"Comment on: {submission.title[:50]}...",
                                    'content': comment.body,
                                    'author': str(comment.author) if comment.author else '[deleted]',
                                    'subreddit': subreddit_name,
                                    'score': comment.score,
                                    'created_utc': comment.created_utc,
                                    'created_date': comment_date.isoformat(),
                                    'type': 'comment',
                                    'processing_mode': 'batch'
                                }
                                
                                producer.send('reddit-posts', value=comment_data)
                                posts_from_subreddit += 1
                                total_posts_sent += 1
                                
                                print(f"    ↳ Sent comment from {comment_date.date()}: {comment.body[:30]}...")
                        
                        # Progress indicator
                        if posts_from_subreddit % 50 == 0:
                            print(f"    📈 Sent {posts_from_subreddit} items from r/{subreddit_name}")
                            producer.flush()  # Ensure data is sent
            
            print(f"✅ Completed r/{subreddit_name}: {posts_from_subreddit} items sent")
            
        except Exception as e:
            print(f"❌ Error processing r/{subreddit_name}: {e}")
    
    print(f"\n🎉 Batch processing completed!")
    print(f"📊 Total items sent: {total_posts_sent}")
    producer.flush()

def main():
    print("🚀 Starting Reddit Batch Data Collection")
    print("📅 Target: January 1-31, 2025")
    print("🎯 Subreddits: malaysia, MalaysianFood, malaysiauni")
    
    # Wait for Kafka to be ready
    time.sleep(10)
    
    producer = get_kafka_producer()
    reddit = get_reddit_instance()
    
    if producer and reddit:
        fetch_batch_data(producer, reddit)
        producer.close()
        print("✅ Batch processing completed successfully!")
    else:
        print("❌ Failed to initialize Kafka producer or Reddit client")

if __name__ == "__main__":
    main()
