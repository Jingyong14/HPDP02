# imdb_scraper.py
import requests
from bs4 import BeautifulSoup
import json
from kafka import KafkaProducer

# IMDb movie page with reviews (you can change movie_id)
movie_id = "tt1355683"
url = f"https://www.imdb.com/title/{movie_id}/reviews"
headers = {
    "User-Agent": "Mozilla/5.0"
}

# --- Initialize Kafka Producer ---
producer = KafkaProducer(
    bootstrap_servers=["kafka:9093"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
review_divs = soup.find_all("div", class_="text show-more__control")

count = 0
for div in review_divs:
    review_text = div.get_text(strip=True)
    if "Malaysia" in review_text or "malaysia" in review_text:
        print(f"[{count+1}] Sending review: {review_text[:80]}...")
        producer.send("imdb_topic", value={"text": review_text})
        count += 1
    if count >= 20:
        break

producer.flush()
producer.close()
print(f"\n✅ Sent {count} Malaysia-related reviews to Kafka topic 'imdb_topic'")
