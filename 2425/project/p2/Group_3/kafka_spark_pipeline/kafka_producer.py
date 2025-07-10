#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from newspaper import Article
import json
import time
import logging
import hashlib
import os
import csv
import nltk

nltk.data.path.append("C:/Users/Admin/AppData/Roaming/nltk_data")

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("KafkaProducer")

# Kafka config
KAFKA_BOOTSTRAP_SERVERS = 'localhost:29092'
KAFKA_TOPIC = 'fmtnews'

# RSS Feeds
RSS_FEEDS = {
    "FMT_Columns": "https://www.freemalaysiatoday.com/feeds/rss/columns",
    "FMT_Travel": "https://www.freemalaysiatoday.com/feeds/rss/travel",
    "FMT_Entertainment": "https://www.freemalaysiatoday.com/feeds/rss/entertainment",
    "FMT_Money": "https://www.freemalaysiatoday.com/feeds/rss/money",
    "FMT_Tech": "https://www.freemalaysiatoday.com/feeds/rss/tech",
    "FMT_Nation": "https://www.freemalaysiatoday.com/feeds/rss/nation",
    "FMT_LocalBusiness": "https://www.freemalaysiatoday.com/feeds/rss/local-business",
    "FMT_Education": "https://www.freemalaysiatoday.com/feeds/rss/education",
    "FMT_Food": "https://www.freemalaysiatoday.com/feeds/rss/food",
    "FMT_Opinion": "https://www.freemalaysiatoday.com/feeds/rss/opinion",
    "FMT_Editorial": "https://www.freemalaysiatoday.com/feeds/rss/editorial"
}

# Output CSV
RAW_DATA_FILE_PATH = 'realtime_data.csv'
SAVE_TO_FILE = True
DEBUG_MODE = True

# Init CSV (overwrite on start)
if SAVE_TO_FILE:
    with open(RAW_DATA_FILE_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'source', 'category_rss', 'title', 'link',
            'summary', 'full_content', 'authors'
        ])
        writer.writeheader()

# Load processed IDs to avoid duplicates
PROCESSED_ARTICLE_IDS = set()
if os.path.exists(RAW_DATA_FILE_PATH):
    with open(RAW_DATA_FILE_PATH, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'id' in row:
                PROCESSED_ARTICLE_IDS.add(row['id'])

def on_send_error(excp):
    logger.error('❌ Failed to send message to Kafka', exc_info=excp)

def get_article_data_newspaper3k(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        return {
            'content': article.text or '',
            'authors': ', '.join(article.authors) if article.authors else '',
            'title': article.title or '',
            'summary': article.summary or ''
        }
    except Exception as e:
        logger.warning(f"⚠️ Error scraping article: {url} — {e}")
        return None

def fetch_and_produce_articles(producer):
    for feed_name, rss_url in RSS_FEEDS.items():
        logger.info(f"🌐 Fetching RSS feed from {feed_name}: {rss_url}")
        article_count = 0

        try:
            response = requests.get(rss_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')

            for item in items:
                title_rss = item.find('title').text.strip() if item.find('title') else 'No Title'
                link = item.find('link').text.strip() if item.find('link') else None
                description_rss = item.find('description').text.strip() if item.find('description') else 'No Description'

                if not link:
                    logger.warning(f"[{feed_name}] ⚠️ Skipped article with no link.")
                    continue

                article_id = hashlib.sha256(link.encode('utf-8')).hexdigest()
                if article_id in PROCESSED_ARTICLE_IDS:
                    logger.info(f"[{feed_name}] 🔁 Skipped duplicate article.")
                    continue

                data = get_article_data_newspaper3k(link)
                if not data:
                    logger.warning(f"[{feed_name}] ❌ Skipped - scraping failed: {link}")
                    continue
                if not data['content'].strip():
                    logger.warning(f"[{feed_name}] ❌ Skipped - empty content: {link}")
                    continue

                article_data = {
                    'id': article_id,
                    'source': feed_name.split('_')[0],
                    'category_rss': feed_name.split('_')[1] if '_' in feed_name else 'unknown',
                    'title': data['title'] or title_rss,
                    'link': link,
                    'summary': data['summary'] or description_rss,
                    'full_content': data['content'],
                    'authors': data['authors']
                }

                if DEBUG_MODE:
                    logger.info(f"[{feed_name}] ✅ {article_data['title'][:60]}...")

                future = producer.send(KAFKA_TOPIC, value=article_data)
                future.add_errback(on_send_error)
                producer.flush()

                PROCESSED_ARTICLE_IDS.add(article_id)
                article_count += 1

                if SAVE_TO_FILE:
                    try:
                        with open(RAW_DATA_FILE_PATH, 'a', encoding='utf-8', newline='') as f:
                            writer = csv.DictWriter(f, fieldnames=article_data.keys())
                            writer.writerow(article_data)
                    except Exception as e:
                        logger.error(f"❌ Failed to write to CSV: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to fetch from {feed_name}: {e}")

        logger.info(f"[{feed_name}] ✅ {article_count} articles pushed to Kafka.")

if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logger.info("🚀 Kafka Producer started.")
    try:
        while True:
            fetch_and_produce_articles(producer)
            time.sleep(300)
    except KeyboardInterrupt:
        logger.info("🛑 Kafka Producer stopped manually.")
    finally:
        producer.close()
