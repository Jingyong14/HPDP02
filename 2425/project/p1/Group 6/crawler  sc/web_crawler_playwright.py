from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import random
import time
import csv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# MongoDB setup
uri = "mongodb+srv://qiaoying:abc12345abc@hpdp-ebay.l78ixmr.mongodb.net/?retryWrites=true&w=majority&appName=HPDP-eBay"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB!")
except Exception as e:
    print("❌ Failed to connect:", e)

db = client['HPDP-eBay']
collection = db['eBay_ToysHobbies']

# --- Scraper setup ---
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/113.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/112.0.1722.64",
]

category_urls = {
    "Action Figures & Accessories": "https://www.ebay.com.my/b/Action-Figures-Accessories/246/bn_1648288",
    "Beanbag Plushies": "https://www.ebay.com.my/b/Beanbag-Plushies/49019/bn_1865544",
    "Building Toys": "https://www.ebay.com.my/b/Building-Toys/183446/bn_1865257",
    "Classic Toys": "https://www.ebay.com.my/b/Classic-Toys/19016/bn_1852070",
    "Collectible Card Games & Accessories": "https://www.ebay.com.my/b/Collectible-Card-Games-Accessories/2536/bn_1852210",
    "Diecast & Toy Vehicles": "https://www.ebay.com.my/b/Diecast-Toy-Vehicles/222/bn_1850842",
    "Educational Toys": "https://www.ebay.com.my/b/Educational-Toys/11731/bn_1850489",
    "Electronic, Battery & Wind-Up Toys": "https://www.ebay.com.my/b/Electronic-Battery-Wind-Up-Toys/19071/bn_1865242",
    "Fast Food & Cereal Toys": "https://www.ebay.com.my/b/Fast-Food-Cereal-Toys/19077/bn_1852214",
    "Games": "https://www.ebay.com.my/b/Games/233/bn_1849806",
    "Toy Marbles": "https://www.ebay.com.my/b/Toy-Marbles/58799/bn_1865515",
    "Model Trains": "https://www.ebay.com.my/b/Model-Trains/180250/bn_1642683",
    "Toy Models & Kits": "https://www.ebay.com.my/b/Toy-Models-Kits/1188/bn_1852447",
    "Outdoor Toys & Structures": "https://www.ebay.com.my/b/Outdoor-Toys-Structures/11743/bn_1849278",
    "Preschool Toys & Pretend Play": "https://www.ebay.com.my/b/Preschool-Toys-Pretend-Play/19169/bn_1864380",
    "Puzzles": "https://www.ebay.com.my/b/Puzzles/2613/bn_1865244",
    "RC Model Vehicles, Toys & Control Line": "https://www.ebay.com.my/b/RC-Model-Vehicles-Toys-Control-Line/2562/bn_1851704",
    "Robot, Monster & Space Toys": "https://www.ebay.com.my/b/Robot-Monster-Space-Toys/19192/bn_1849094",
    "Slot Cars": "https://www.ebay.com.my/b/Slot-Cars/2616/bn_1865407",
    "Stuffed Animals": "https://www.ebay.com.my/b/Stuffed-Animals/436/bn_1850590",
    "Toy Soldiers": "https://www.ebay.com.my/b/Toy-Soldiers/2631/bn_1865422",
    "Baby Toys": "https://www.ebay.com.my/b/Baby-Toys/19068/bn_1865476",
    "Video Games": "https://www.ebay.com.my/b/Video-Games/139973/bn_320034",
    "Vintage & Antique Toys": "https://www.ebay.com.my/b/Vintage-Antique-Toys/717/bn_1860860",
    "Toys & Hobbies Wholesale Lots": "https://www.ebay.com.my/b/Toys-Hobbies-Wholesale-Lots/40149/bn_1862259"
}

def get_browser(playwright):
    user_agent = random.choice(user_agents)
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(user_agent=user_agent)
    return context

def safe_inner_text(element):
    try:
        return element.inner_text().strip() if element else ''
    except:
        return ''

def scrape_ebay_by_category():
    max_pages = 21  # Change as needed
    scraped_at = datetime.utcnow()

    with sync_playwright() as p:
        context = get_browser(p)
        page = context.new_page()

        try:
            for category_name, base_url in category_urls.items():
                print(f"\n🧸 Category: {category_name}")
                for page_num in range(1, max_pages + 1):
                    url = f"{base_url}?_pgn={page_num}&_sop=12"
                    print(f"🔗 Scraping: {url}")
                    try:
                        page.goto(url, timeout=60000)
                        page.wait_for_selector('div.brwrvr__item-card__signals', timeout=45000)
                        listings = page.query_selector_all('div.brwrvr__item-card__signals')

                        if not listings:
                            print("⚠️ No listings — ending category early.")
                            break

                        for listing in listings:
                            condition_elements = listing.query_selector_all("span.bsig__listingCondition > span")
                            condition_texts = [el.inner_text().strip() for el in condition_elements if el.inner_text().strip() != "·"]

                            shipping_el = (
                                listing.query_selector('span.textual-display.bsig__generic.bsig__logisticsCost') or
                                listing.query_selector('span.s-item__shipping.s-item__logisticsCost')
                            )
                            raw_shipping = safe_inner_text(shipping_el)
                            shipping_fee = raw_shipping.replace('+', '').strip() if raw_shipping else None

                            data = {
                                'category': category_name,
                                'title': safe_inner_text(listing.query_selector('h3.textual-display.bsig__title__text')),
                                'price': safe_inner_text(listing.query_selector('span.textual-display.bsig__price.bsig__price--displayprice')),
                                'shippingfee': shipping_fee,
                                'condition': condition_texts[0] if condition_texts else None,
                                'brand': condition_texts[1] if len(condition_texts) > 1 else None,
                                'link': listing.query_selector('a').get_attribute('href') if listing.query_selector('a') else None,
                                'scraped_at': scraped_at
                            }

                            collection.insert_one(data)

                        time.sleep(random.uniform(2, 5))

                    except PlaywrightTimeoutError as te:
                        print(f"⛔ Timeout: {te}")
                        continue
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        continue

        finally:
            context.close()
    print("\n✅ Scraping complete. Data saved to MongoDB.")

if __name__ == "__main__":
    scrape_ebay_by_category()



