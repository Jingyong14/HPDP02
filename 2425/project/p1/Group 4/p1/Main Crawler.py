from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random

class ScrapeLazada():

    def Scrape(self, urls):

        #define user agent
        options = webdriver.ChromeOptions()
        options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(options=options)
        
        products=[]

        for url in urls:
            driver.get(url)

            # Wait while page load
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#root")))
            time.sleep(random.uniform(2.5, 4.5))

            # Get total number of pages
            soup = BeautifulSoup(driver.page_source, "html.parser")
            pagination = soup.select(".ant-pagination-item")
            total_pages = int(pagination[-1].text) if pagination else 1
            print(f"Scraping {total_pages} pages from: {url}")

            for page in range(total_pages):
                print(f"Scraping page {page+1} of {total_pages}")

                # Catch capcha to be solved
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "captcha"))  # Adjust if Lazada uses different selector
                    )
                    input("⚠️ CAPTCHA detected. Please solve it manually in the browser, then press Enter to continue...")
                except:
                    pass

                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#root")))
                # time.sleep(random.uniform(2.5, 4.5))

                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")

                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                # Extract data
                for item in soup.findAll('div', class_='Bm3ON'):
                    product_name = item.find('div', class_='RfADt').text
                    price = float(item.find('span', class_='ooOxS').text.replace('RM', '').replace(',', ''))
                    location = item.find('span', class_='oa6ri').text
                    numbersold = item.find('span', class_='_1cEkb')
                    numbersold = numbersold.text.strip() if numbersold else 'N/A'
                    rating = item.find('span', class_='qzqFw')
                    rating = rating.text.strip() if rating else 'N/A'
                    
                    products.append((product_name, price, location, numbersold, rating))

                # Click next page button
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, ".ant-pagination-next > button")
                    time.sleep(random.uniform(3, 5))  # Simulate reading delay
                    next_button.click()
                except:
                    print("Next button not found or last page reached.")
                    break

        # Create dataframe
        df = pd.DataFrame(products, columns=['Product Name', 'Price', 'Location', 'Quantity Sold', 'Number of Ratings'])

        # Export to excel
        df.to_excel("Lazada (Toys).xlsx", index=False)
        print("Data saved in local disk")


        driver.close()

# URLs to be crawl
urls = [
    'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=0-1',
    'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=1-6',
    'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=6-11',
    'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=11-20',
    'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=20-38',
    'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=38-82',
    'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=82-'
]

# Create obj and call function
sl = ScrapeLazada()
sl.Scrape(urls)



# Target URL
# URLs (Stationery)
#'https://www.lazada.com.my/catalog/?q=Stationery&price=0-1',
#'https://www.lazada.com.my/catalog/?q=Stationery&price=1-3',
#'https://www.lazada.com.my/catalog/?q=Stationery&price=3-5',
#'https://www.lazada.com.my/catalog/?q=Stationery&price=5-8',
#'https://www.lazada.com.my/catalog/?q=Stationery&price=8-13',
#'https://www.lazada.com.my/catalog/?q=Stationery&price=13-26',
#'https://www.lazada.com.my/catalog/?q=Stationery&price=26-'

# URLs (Grocery)
#'https://www.lazada.com.my/tag/grocery/?q=grocery&price=0-1',
#'https://www.lazada.com.my/tag/grocery/?q=grocery&price=1-9',
#'https://www.lazada.com.my/tag/grocery/?q=grocery&price=9-16',
#'https://www.lazada.com.my/tag/grocery/?q=grocery&price=16-27',
#'https://www.lazada.com.my/tag/grocery/?q=grocery&price=27-50',
#'https://www.lazada.com.my/tag/grocery/?q=grocery&price=50-'

# URLs (Smartphone)
#'https://www.lazada.com.my/tag/smartphone/?q=smartphone&price=0-1,
#'https://www.lazada.com.my/tag/smartphone/?q=smartphone&price=1-500',
#'https://www.lazada.com.my/tag/smartphone/?q=smartphone&price=500-1300',
#'https://www.lazada.com.my/tag/smartphone/?q=smartphone&price=1300-3800',
#'https://www.lazada.com.my/tag/smartphone/?q=smartphone&price=3800-'

# URLs (Food)
#'https://www.lazada.com.my/tag/food/?q=food&price=0-1',
#'https://www.lazada.com.my/tag/food/?q=food&price=1-5',
#'https://www.lazada.com.my/tag/food/?q=food&price=5-15',
#'https://www.lazada.com.my/tag/food/?q=food&price=15-32',
#'https://www.lazada.com.my/tag/food/?q=food&price=32-68',
#'https://www.lazada.com.my/tag/food/?q=food&price=68-135',
#'https://www.lazada.com.my/tag/food/?q=food&price=135-300',
#'https://www.lazada.com.my/tag/food/?q=food&price=300-'

# URLs (Sport)
#'https://www.lazada.com.my/tag/sport/?q=sport&price=0-1',
#'https://www.lazada.com.my/tag/sport/?q=sport&price=1-10',
#'https://www.lazada.com.my/tag/sport/?q=sport&price=10-19',
#'https://www.lazada.com.my/tag/sport/?q=sport&price=19-31',
#'https://www.lazada.com.my/tag/sport/?q=sport&price=31-62',
#'https://www.lazada.com.my/tag/sport/?q=sport&price=62-135',
#'https://www.lazada.com.my/tag/sport/?q=sport&price=135-228',
#'https://www.lazada.com.my/tag/sport/?q=sport&price=228-430',
#'https://www.lazada.com.my/tag/sport/?q=sport&price=430-'

# URLs (Toys)
#'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=0-6',
#'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=6-11',
#'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=11-20',
#'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=20-38',
#'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=38-82',
#'https://www.lazada.com.my/tag/toys/?catalog_redirect_tag=true&q=toys&price=82-'