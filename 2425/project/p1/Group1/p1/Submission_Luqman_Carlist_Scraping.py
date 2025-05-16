import urllib.request
from selectolax.parser import HTMLParser
import csv
import time
import json

# Configuration
base_url = "https://www.carlist.my/cars-for-sale/malaysia?page_number={}&page_size=25"
start_page = 1745    # Starting page number to scrape
end_page = 3488      # Ending page number to scrape
car_listings = []  # List to store car listings data

output_file = 'car_listings.csv'

def get_attr(element, attr_name):
    return element.attributes.get(attr_name, '') if element else ''

def get_text(node):
    return node.text().strip() if node else ''

def get_sales_channel(article):
    dealer_div = article.css_first('div.listing__spec--dealer')
    if dealer_div:
        channel = dealer_div.text().strip()
        # Convert "Sales" to "Sales Agent"
        return channel.replace("Sales", "Sales Agent") if "Sales" in channel else channel
    return ''

def get_mileage(article):
    icon = article.css_first('i.icon--meter')
    if icon and icon.next:
        return icon.next.text().strip()
    return ''

def get_location(article):
    icon = article.css_first('i.icon--location')
    if not icon:
        return ''
    text = ''
    current = icon.next
    while current:
        if current.tag == '-text':
            text += current.text().strip()
        elif current.tag == 'span':
            text += current.text().strip()
        else:
            break
        current = current.next
    return text.strip()

def extract_json_ld(parser):
    for script in parser.css('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.text())
            if isinstance(data, list):
                for d in data:
                    if 'itemListElement' in d:
                        return d['itemListElement']
        except:
            continue
    return None

start_time = time.time()

for page_num in range(start_page, end_page + 1):
    url = base_url.format(page_num)
    print(f"\n🔎 Extracting page {page_num} - {url}")

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req).read()
    parser = HTMLParser(html)

    articles = parser.css('article.listing')
    ld_json = extract_json_ld(parser)
    if not ld_json:
        print("⚠️ No JSON-LD found on this page.")
        continue

    page_count = 0
    for article, item in zip(articles, ld_json):
        car = item['item']

        name = get_attr(article, 'data-title')
        brand = get_attr(article, 'data-make')
        model = get_attr(article, 'data-model')
        body = get_attr(article, 'data-body-type')
        transmission = get_attr(article, 'data-transmission')
        installment = get_attr(article, 'data-installment')

        mileage = get_mileage(article)
        sales_channel = get_sales_channel(article)  # This now returns "Sales Agent" if "Sales" was found
        location = get_location(article)

        year = car.get('vehicleModelDate', '')
        fuel = car.get('fuelType', '')
        color = car.get('color', '')
        price = car.get('offers', {}).get('price', '')
        condition = car.get('itemCondition', '')
        seats = car.get('seatingCapacity', '')

        car_listings.append({
            'Car Name': name,
            'Car Brand': brand,
            'Car Model': model,
            'Manufacture Year': year,
            'Body Type': body,
            'Fuel Type': fuel,
            'Mileage': mileage,
            'Transmission': transmission,
            'Color': color,
            'Price': price,
            'Installment': installment,
            'Condition': condition,
            'Seating Capacity': seats,
            'Location': location,
            'Sales Channel': sales_channel  # Will show "Sales Agent" instead of "Sales"
        })
        page_count += 1

    time.sleep(2)

if car_listings:
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=car_listings[0].keys())
        writer.writeheader()
        writer.writerows(car_listings)
    print(f"\n✅ Saved {len(car_listings)} cars to '{output_file}'")
else:
    print("\n⚠️ No car listings found.")

end_time = time.time()
execution_time = end_time - start_time
print(f"\n🕒 Total execution time: {execution_time:.2f} seconds")
