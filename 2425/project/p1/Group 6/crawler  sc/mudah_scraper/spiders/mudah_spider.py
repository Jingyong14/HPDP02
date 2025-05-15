import scrapy
import random
import re
from scrapy_playwright.page import PageMethod
from datetime import datetime, UTC

class CarsSpider(scrapy.Spider):
    name = "cars"
    max_pages = 168  # Number of pages per URL

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/113.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/112.0.1722.64",
    ]

    custom_settings = {
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'LOG_LEVEL': 'INFO'
    }

    def start_requests(self):
        base_urls = [
            "https://www.ebay.com.my/b/Collectibles/1/bn_1858810?_pgn=1&_sop=10&mag=1&rt=nc",
            "https://www.ebay.com.my/b/Stamps/260/bn_1865095?_pgn=1&_sop=10&mag=1&rt=nc",
            "https://www.ebay.com.my/b/Dolls-Teddy-Bears/237/bn_1865477?_pgn=1&_sop=10&mag=1&rt=nc"
        ]
        for base_url in base_urls:
            yield scrapy.Request(
                base_url,
                callback=self.parse,
                headers={"User-Agent": random.choice(self.user_agents)},
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context": "stealth",
                    "playwright_page_methods": [
                        PageMethod('wait_for_selector', 'div.brwrvr__item-card__signals', state='visible', timeout=45000),
                    ],
                    "current_page": 1,
                    "base_url": base_url
                }
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        current_page = response.meta["current_page"]
        base_url = response.meta["base_url"]

        try:
            self.logger.info(f"--- Parsing Page {current_page} of {base_url} ---")
            await page.wait_for_timeout(2000)

            listings = response.css('div.brwrvr__item-card__signals')
            category_title = response.css('h1.page-title::text').get()
            if category_title:
                category_title = category_title.strip()

            self.logger.info(f"Found {len(listings)} listings on page {current_page}")

            for listing in listings:
                condition_texts = listing.css("span.bsig__listingCondition > span::text").getall()
                condition_texts = [text.strip() for text in condition_texts if text.strip() != "·"]

                yield {
                    'category': category_title,
                    'title': listing.css('h3.textual-display.bsig__title__text::text').get(),
                    'brand': condition_texts[1] if len(condition_texts) > 1 else None,
                    'price': listing.css('span.textual-display.bsig__price.bsig__price--displayprice::text').get(),
                    'status': condition_texts[0] if condition_texts else None,
                    'shipping': listing.css('span.textual-display.bsig__generic.bsig__logisticsCost::text').get(),
                    'link': listing.css('a::attr(href)').get(),
                    "scraped_at": datetime.now(UTC)
                }

            # Continue to next page if limit not reached
            if current_page < self.max_pages:
                next_page = current_page + 1
                next_url = re.sub(r"_pgn=\d+", f"_pgn={next_page}", base_url)

                delay = random.uniform(2, 5)
                self.logger.info(f"Waiting {delay:.2f} seconds before requesting page {next_page}")
                await page.wait_for_timeout(delay * 1000)

                yield scrapy.Request(
                    next_url,
                    callback=self.parse,
                    headers={"User-Agent": random.choice(self.user_agents)},
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_context": "stealth",
                        "playwright_page_methods": [
                            PageMethod('wait_for_selector', 'div.brwrvr__item-card__signals', state='visible', timeout=45000),
                        ],
                        "current_page": next_page,
                        "base_url": base_url
                    }
                )

        except Exception as e:
            self.logger.error(f"Error on page {current_page} of {base_url}: {e}")
            screenshot_path = f"error_page_{current_page}.png"
            await page.screenshot(path=screenshot_path)
            self.logger.info(f"Screenshot saved to {screenshot_path}")
        finally:
            await page.close()
