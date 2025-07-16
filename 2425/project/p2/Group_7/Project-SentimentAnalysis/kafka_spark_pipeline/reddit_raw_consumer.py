import json
import os
from kafka import KafkaConsumer
from datetime import datetime

class RedditRawConsumer:
    def __init__(self):
        # Use environment variable for Kafka servers (Docker compatibility)
        kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        
        self.consumer = KafkaConsumer(
            'reddit-posts',  # Corrected topic
            bootstrap_servers=[kafka_servers],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='reddit-consumer-group'
        )
        
        # Ensure raw data directory exists
        os.makedirs('data/raw_data', exist_ok=True)
    
    def consume_and_save(self):
        """Save raw Reddit data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reddit_malaysianfood_{timestamp}.jsonl"  # Updated filename
        filepath = os.path.join('data', 'raw_data', filename)
        
        print(f"Starting Reddit consumer...")
        print(f"Saving Reddit data to: {filepath}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for message in self.consumer:
                    data = message.value
                    f.write(json.dumps(data, ensure_ascii=False) + '\n')
                    f.flush()
                    print(f"Saved Reddit post: {data.get('title', 'No title')[:50]}...")
                    
        except KeyboardInterrupt:
            print("Stopping Reddit consumer...")

if __name__ == "__main__":
    consumer = RedditRawConsumer()
    consumer.consume_and_save()
