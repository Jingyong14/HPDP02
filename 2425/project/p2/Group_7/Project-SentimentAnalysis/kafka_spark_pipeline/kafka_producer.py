#!/usr/bin/env python3
"""
Kafka Producer for Reddit Data
Renamed from reddit_raw_producer.py to match project structure
"""

import json
import time
import os
from datetime import datetime
from kafka import KafkaProducer
import praw
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env.local')

class RedditKafkaProducer:
    def __init__(self):
        """Initialize Reddit API and Kafka producer"""
        self.setup_reddit_api()
        self.setup_kafka_producer()
        
    def setup_reddit_api(self):
        """Setup Reddit API connection"""
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'python:sentimentAnalysis:v1.0.0'),
                username=os.getenv('REDDIT_USERNAME'),
                password=os.getenv('REDDIT_PASSWORD')
            )
            
            # Test the connection
            print(f"✅ Connected to Reddit as: {self.reddit.user.me()}")
            
        except Exception as e:
            print(f"❌ Reddit API setup failed: {e}")
            raise
    
    def setup_kafka_producer(self):
        """Setup Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None
            )
            print("✅ Kafka producer initialized")
            
        except Exception as e:
            print(f"❌ Kafka producer setup failed: {e}")
            raise
    
    def fetch_reddit_posts(self, subreddit_name="MalaysianFood", limit=10):
        """Fetch posts from specified subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            print(f"📡 Fetching posts from r/{subreddit_name}...")
            
            for post in subreddit.new(limit=limit):
                post_data = {
                    "id": post.id,
                    "title": post.title,
                    "content": post.selftext if post.selftext else "",
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "created_utc": int(post.created_utc),
                    "created_date": datetime.fromtimestamp(post.created_utc).isoformat(),
                    "author": str(post.author) if post.author else "deleted",
                    "subreddit": str(post.subreddit),
                    "url": post.url,
                    "timestamp": datetime.now().isoformat(),
                    "fetch_method": "reddit_api",
                    "content_type": "post",
                    "parent_post_id": None
                }
                posts.append(post_data)
            
            print(f"✅ Fetched {len(posts)} posts")
            return posts
            
        except Exception as e:
            print(f"❌ Error fetching posts: {e}")
            return []
    
    def send_to_kafka(self, data, topic="reddit-posts"):
        """Send data to Kafka topic"""
        try:
            for item in data:
                # Use post ID as key for partitioning
                key = item.get('id', '')
                
                # Send to Kafka
                self.producer.send(topic, key=key, value=item)
                
            # Ensure all messages are sent
            self.producer.flush()
            print(f"📤 Sent {len(data)} messages to Kafka topic: {topic}")
            
        except Exception as e:
            print(f"❌ Error sending to Kafka: {e}")
    
    def run_continuous(self, subreddit="MalaysianFood", interval=60):
        """Run continuous data collection"""
        print(f"🚀 Starting continuous Reddit data collection...")
        print(f"📊 Subreddit: r/{subreddit}")
        print(f"⏰ Interval: {interval} seconds")
        print("💡 Press Ctrl+C to stop")
        
        try:
            while True:
                # Fetch posts
                posts = self.fetch_reddit_posts(subreddit)
                
                if posts:
                    # Send to Kafka
                    self.send_to_kafka(posts)
                    
                    # Also save to file for backup
                    self.save_to_file(posts)
                
                print(f"⏳ Waiting {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopping data collection...")
            
        finally:
            self.producer.close()
            print("👋 Producer closed")
    
    def save_to_file(self, data, filename=None):
        """Save data to JSON file for backup"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../data/raw_data/reddit_posts_{timestamp}.jsonl"
        
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'a', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item) + '\n')
                    
            print(f"💾 Data backed up to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving to file: {e}")

def main():
    """Main execution function"""
    print("🎯 Reddit Kafka Producer for Sentiment Analysis")
    print("=" * 50)
    
    try:
        # Initialize producer
        producer = RedditKafkaProducer()
        
        # Run continuous collection
        producer.run_continuous(
            subreddit="MalaysianFood",  # Focus on Malaysian content
            interval=60  # Fetch every minute
        )
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")

if __name__ == "__main__":
    main()
