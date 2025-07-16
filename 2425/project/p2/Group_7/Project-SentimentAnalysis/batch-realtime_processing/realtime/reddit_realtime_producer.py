#!/usr/bin/env python3
"""
Reddit Real-Time Producer for Live Sentiment Analysis
Continuously fetches recent Reddit data from the last 3 hours
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
    """Initialize Kafka producer for real-time processing"""
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    try:
        producer = KafkaProducer(
            bootstrap_servers=[kafka_servers],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            retry_backoff_ms=1000
        )
        producer.bootstrap_connected()
        print("✅ Kafka Producer connected successfully for real-time processing.")
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
            user_agent='script:realtime-sentiment-analysis:v1.0',
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD')
        )
        print(f"✅ Authenticated with Reddit as: {reddit.user.me()}")
        return reddit
    except Exception as e:
        print(f"❌ Failed to authenticate with Reddit: {e}")
        return None

def fetch_realtime_data(producer, reddit):
    """
    Continuously fetch posts and comments from the last 3 hours
    """
    subreddit_names = ['malaysia', 'MalaysianFood', 'malaysiauni']
    
    print(f"🔄 Starting real-time monitoring of: {subreddit_names}")
    print("⏱️  Fetching posts from last 3 hours every 1 minute")
    
    seen_posts = set()
    cycle_count = 0
    
    while True:
        cycle_count += 1
        # Calculate 3-hour window
        now = datetime.now(timezone.utc)
        three_hours_ago = now - timedelta(hours=3)
        
        print(f"\n🔍 Cycle {cycle_count}: Scanning for posts newer than: {three_hours_ago.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        current_batch_count = 0
        
        for subreddit_name in subreddit_names:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                
                # Get new posts
                for submission in subreddit.new(limit=100):
                    post_date = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
                    
                    # Only process posts from last 3 hours that we haven't seen
                    if post_date >= three_hours_ago and submission.id not in seen_posts:
                        seen_posts.add(submission.id)
                        
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
                            'processing_mode': 'realtime'
                        }
                        
                        producer.send('reddit-posts', value=post_data)
                        current_batch_count += 1
                        
                        print(f"  ✓ Sent post from {post_date.strftime('%H:%M')}: {submission.title[:50]}...")
                        
                        # Fetch recent comments
                        submission.comments.replace_more(limit=2)
                        for comment in submission.comments.list()[:10]:
                            comment_date = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)
                            
                            if (comment_date >= three_hours_ago and 
                                len(comment.body) > 10 and 
                                comment.id not in seen_posts):
                                
                                seen_posts.add(comment.id)
                                
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
                                    'processing_mode': 'realtime'
                                }
                                
                                producer.send('reddit-posts', value=comment_data)
                                current_batch_count += 1
                                
                                print(f"    ↳ Sent comment from {comment_date.strftime('%H:%M')}: {comment.body[:30]}...")
                
            except Exception as e:
                print(f"❌ Error processing r/{subreddit_name}: {e}")
        
        print(f"📊 Sent {current_batch_count} new items in cycle {cycle_count}")
        producer.flush()
        
        # Clean up old seen posts to prevent memory bloat
        if len(seen_posts) > 10000:
            # Keep only posts from last 6 hours to prevent re-processing
            six_hours_ago = now - timedelta(hours=6)
            old_posts = [post_id for post_id in seen_posts if len(post_id) > 0]  # Simple cleanup
            if len(old_posts) > 5000:
                seen_posts.clear()
                print("🧹 Cleared seen posts cache")
        
        # Wait 1 minute before next scan
        print("⏰ Waiting 1 minute for next scan...")
        time.sleep(60)  # 1 minute

def main():
    print("🚀 Starting Reddit Real-Time Data Collection")
    print("⏱️  Monitoring last 3 hours of posts every 1 minute")
    print("🎯 Subreddits: malaysia, MalaysianFood, malaysiauni")

    # Wait for Kafka to be ready
    time.sleep(10)

    producer = get_kafka_producer()
    reddit = get_reddit_instance()

    if producer and reddit:
        try:
            fetch_realtime_data(producer, reddit)
        except KeyboardInterrupt:
            print("\n⏹️  Real-time processing stopped by user")
        finally:
            producer.close()
            print("✅ Real-time producer shut down gracefully")
    else:
        print("❌ Failed to initialize Kafka producer or Reddit client")

if __name__ == "__main__":
    main()
