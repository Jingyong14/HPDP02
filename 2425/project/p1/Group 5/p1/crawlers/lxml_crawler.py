#!/usr/bin/env python3
import requests
from lxml import html
import csv
import time
import random

# ----------- BATCH SETTINGS --------------
start_id = 105500
end_id = 140000
output_file = 'pets_batch_full.csv'  # <-- Add output file
# -----------------------------------------

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/115.0.0.0 Safari/537.36'
    )
}

def scrape_batch(start_id, end_id, output_file):
    print(f"\n=== Scraping {start_id} → {end_id} → {output_file} ===\n")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Pet ID', 'Name', 'Type', 'Species', 'Profile', 'Amount', 'Vaccinated', 'Dewormed',
            'Spayed', 'Condition', 'Body', 'Color', 'Location', 'Posted', 'Price',
            'Uploader Type', 'Uploader Name', 'Status'
        ])

        for pet_id in range(start_id, end_id + 1):
            url = f"https://www.petfinder.my/pets/{pet_id}/"
            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
            except Exception as e:
                print(f"[{pet_id}] request error: {e}")
                time.sleep(5)
                continue

            if response.status_code == 404:
                print(f"[{pet_id}] 404 not found")
                time.sleep(random.uniform(3, 6))
                continue

            tree = html.fromstring(response.content)

            # Extract Name
            name_list = tree.xpath('//div[@class="pet_title"]//td[@align="center"]/text()')
            pet_name = name_list[0].strip() if name_list else 'N/A'

            # Extract details table
            details = {}
            rows = tree.xpath('//table[@class="pet_box"]//tr')
            for tr in rows:
                key = tr.xpath('.//td[1]//b/text()')
                val = tr.xpath('.//td[2]//text()')
                if key:
                    k = key[0].replace(':','').strip()
                    v = ' '.join([t.strip() for t in val if t.strip()]) or 'N/A'
                    details[k] = v

            # Extract real price (Adoption Fee)
            pet_price = 'N/A'
            for tr in rows:
                key = tr.xpath('.//td[1]//b/text()')
                if key and 'Adoption Fee' in key[0]:
                    bold = tr.xpath('.//td[2]/b/text()')
                    if bold:
                        pet_price = bold[0].strip()
                    else:
                        txt = tr.xpath('.//td[2]/text()')
                        pet_price = txt[0].strip() if txt else 'N/A'
                    break
            if pet_price in ['N/A', '']:
                pet_price = 'Free'

            # Extract uploader info
            uploader_td = tree.xpath('//td[@align="left" and @width="130" and @valign="middle"]')
            if uploader_td:
                ut = uploader_td[0].xpath('.//font/text()')
                pet_uploader_type = ut[0].strip() if ut else 'N/A'
                un = uploader_td[0].xpath('.//a[@class="darkgrey"]/text()')
                pet_uploader_name = un[0].strip() if un else 'N/A'
            else:
                pet_uploader_type = 'N/A'
                pet_uploader_name = 'N/A'

            # Extract status
            status = tree.xpath('//div[@class="pet_label"]/text()')
            pet_status = status[0].strip() if status else 'N/A'

            # Map other fields
            pet_type       = details.get('Type', 'N/A')
            pet_species    = details.get('Species', 'N/A')
            pet_profile    = details.get('Profile', 'N/A')
            pet_amount     = details.get('Amount', 'N/A')
            pet_vaccinated = details.get('Vaccinated', 'N/A')
            pet_dewormed   = details.get('Dewormed', 'N/A')
            pet_spayed     = details.get('Spayed / Neutered', 'N/A')
            pet_condition  = details.get('Condition', 'N/A')
            pet_body       = details.get('Body', 'N/A')
            pet_color      = details.get('Color', 'N/A')
            pet_location   = details.get('Location', 'N/A')
            pet_posted     = details.get('Posted', 'N/A')

            writer.writerow([
                pet_id, pet_name, pet_type, pet_species, pet_profile, pet_amount,
                pet_vaccinated, pet_dewormed, pet_spayed, pet_condition,
                pet_body, pet_color, pet_location, pet_posted, pet_price,
                pet_uploader_type, pet_uploader_name, pet_status
            ])

            print(f"Scraped {pet_id}: {pet_name}")
            time.sleep(random.uniform(3, 6))

if __name__ == '__main__':
    scrape_batch(start_id, end_id, output_file='pets_batch_full.csv')
