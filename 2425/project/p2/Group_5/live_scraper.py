import asyncio
import json
from kafka import KafkaProducer
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

KAFKA_BOOTSTRAP = 'kafka:9092'
KAFKA_TOPIC = 'live_news_stream'

async def scrape_latest_articles(page):
    url = 'https://www.nst.com.my/news/nation'
    print(f"[Scraper] Navigating to {url}")
    await page.goto(url, wait_until="domcontentloaded")
    print("[Scraper] Page loaded, waiting for articles selector...")
    await page.wait_for_selector('a.d-flex.article.listing.mb-3.pb-3')
    print("[Scraper] Articles selector found, getting HTML content.")
    content = await page.content()
    print(f"[Scraper] Length of HTML content: {len(content)}")
    soup = BeautifulSoup(content, 'html.parser')
    articles = soup.find_all('a', class_=['d-flex', 'article', 'listing', 'mb-3', 'pb-3'])
    print(f"[Scraper] Found {len(articles)} article elements in HTML.")
    article_details = []
    for idx, article in enumerate(articles):
        try:
            link = article['href']
            if link and link.startswith('/'):
                link = "https://www.nst.com.my" + link
            title = article.find('h6', class_='field-title').text.strip()
            description = article.find('div', class_='d-block article-teaser').text.strip()
            print(f"[Scraper] Article {idx+1}: {title} ({link})")
            article_details.append({
                'title': title,
                'description': description,
                'link': link
            })
        except Exception as e:
            print(f"[Scraper] Skipped an article due to error: {e}")
            continue
    print(f"[Scraper] Returning {len(article_details)} articles from this scrape.")
    return article_details


async def stream_scrape():
    producer = None
    browser = None
    try:
        print("[Kafka] Connecting to Kafka producer...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        seen_links = set()
        print("[Playwright] Launching browser...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            while True:
                print("\n[Main Loop] Checking for new articles...")
                try:
                    articles = await scrape_latest_articles(page)
                except Exception as e:
                    print(f"[Main Loop] Error during scraping: {e}")
                    await asyncio.sleep(60)
                    continue
                new_articles = [a for a in articles if a['link'] not in seen_links]
                print(f"[Main Loop] Found {len(new_articles)} new articles this round.")
                for article in new_articles:
                    try:
                        producer.send(KAFKA_TOPIC, value=article)
                        print(f"[Kafka] Sent: {article['title']} ({article['link']})", flush=True)
                        seen_links.add(article['link'])
                    except Exception as e:
                        print(f"[Kafka] Failed to send article to Kafka: {e}")
                producer.flush()
                print(f"[Main Loop] Sleeping for 60 seconds before next check.")
                await asyncio.sleep(60)  # Async sleep!
    finally:
        print("[Shutdown] Closing browser and Kafka producer.")
        if browser:
            await browser.close()
        if producer:
            producer.close()

if __name__ == '__main__':
    print("[Startup] Starting the news scraper.")
    asyncio.run(stream_scrape())
