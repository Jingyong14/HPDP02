# File: fake_streaming.py

import json
from kafka import KafkaProducer
import time
import random

# --- Preset IMDB-style Sentences (positive + negative) ---
PRESET_REVIEWS = [
    "This movie was absolutely fantastic! I loved every moment.",
    "Terrible acting and weak plot. Completely disappointed.",
    "A masterpiece of storytelling and direction.",
    "I wouldn't recommend this movie to anyone.",
    "Great performances by the cast. Very enjoyable!",
    "The storyline was so boring I fell asleep halfway.",
    "Visually stunning and emotionally touching.",
    "Waste of time. Poor script and poor execution.",
    "One of the best movies I've seen this year!",
    "I regret watching it. Total nonsense."
]

# --- Kafka Configuration ---
KAFKA_SERVER = "kafka:9093"
KAFKA_TOPIC = "imdb_topic"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print(f"✅ IMDB streaming sending to topic '{KAFKA_TOPIC}'")

try:
    while True:
        review = random.choice(PRESET_REVIEWS)
        message = {'text': review}
        print(f"📤 Sending: {message}")
        producer.send(KAFKA_TOPIC, value=message)
        time.sleep(5)  # Adjust frequency as needed

except KeyboardInterrupt:
    print("\n🛑 Stopping streaming producer.")

finally:
    producer.close()
