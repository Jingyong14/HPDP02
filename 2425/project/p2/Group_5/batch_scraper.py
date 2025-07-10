# batch_scraper.py

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers, NotFoundError

ES_HOST   = 'http://elasticsearch:9200'
ES_INDEX  = 'news_articles'
PAGE_LIMIT = 20000
MAX_BAD_PAGES = 20

async def scrape_articles(limit=PAGE_LIMIT):
    all_articles = []
    total = 0
    page_num = 1
    bad_pages = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        while total < limit and bad_pages < MAX_BAD_PAGES:
            print(f"[Scraping] Page {page_num} (total scraped: {total}). Bad pages so far: {bad_pages}", flush=True)
            try:
                url = f'https://www.nst.com.my/news/nation?page={page_num}'
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_selector('a.d-flex.article.listing.mb-3.pb-3', timeout=10000)

                soup = BeautifulSoup(await page.content(), 'html.parser')
                articles = soup.find_all(
                    'a',
                    class_='d-flex article listing mb-3 pb-3'
                )

                if not articles:
                    # no articles found ⇒ count as a bad page
                    bad_pages += 1
                    print(f"[Warning] No articles found on page {page_num}.", flush=True)
                else:
                    # successfully scraped at least one article ⇒ reset bad_pages
                    bad_pages = 0
                    for art in articles:
                        if total >= limit:
                            break
                        try:
                            title = art.find('h6', class_='field-title').text.strip()
                            description = art.find(
                                'div', class_='d-block article-teaser'
                            ).text.strip()
                            all_articles.append({
                                'title': title,
                                'description': description
                            })
                            total += 1
                        except Exception:
                            # skip faulty article
                            continue

                page_num += 1

            except (PlaywrightTimeoutError, Exception) as e:
                bad_pages += 1
                print(f"[Error] Failed to scrape page {page_num}: {e!r}", flush=True)
                page_num += 1
                # go on to next page

        await browser.close()

    print(f"[Scraping] Finished: scraped {len(all_articles)} articles; stopped after {bad_pages} consecutive bad pages.", flush=True)
    return all_articles

def save_to_elasticsearch(docs):
    es = Elasticsearch(ES_HOST)
    try:
        es.indices.delete(index=ES_INDEX)
        print(f"Deleted old index '{ES_INDEX}'", flush=True)
    except NotFoundError:
        print(f"Index '{ES_INDEX}' did not exist, skipping delete.", flush=True)

    es.indices.create(index=ES_INDEX)
    print(f"Created index '{ES_INDEX}'", flush=True)

    actions = [
        {"_index": ES_INDEX, "_source": doc}
        for doc in docs
    ]
    helpers.bulk(es, actions)
    print(f"Saved {len(docs)} articles to Elasticsearch.", flush=True)

if __name__ == "__main__":
    articles = asyncio.run(scrape_articles())
    save_to_elasticsearch(articles)
    print("Batch scraping and upload complete!")
