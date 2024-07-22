import os
import csv
from playwright.sync_api import sync_playwright
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths

def tokenize_text(page, text, is_first):
    page.fill('textarea.text-input', text)
    
    if is_first:
        page.wait_for_timeout(1000)
    else:
        page.wait_for_timeout(300)
    
    page.wait_for_selector('.tokenizer-stat-val', state='visible', timeout=10000)
    return int(page.inner_text('.tokenizer-stat-val').replace(',', ''))

def process_beige_books(root_dir):
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://platform.openai.com/tokenizer')
        page.wait_for_load_state('networkidle')

        is_first = True
        for year in sorted(os.listdir(root_dir)):
            year_path = os.path.join(root_dir, year)
            for month in os.listdir(year_path):
                date_key = f"{year}-{month}"
                results[date_key] = {}
                month_path = os.path.join(year_path, month)
                for file in os.listdir(month_path):
                    with open(os.path.join(month_path, file), 'r', encoding='utf-8') as f:
                        text = f.read()
                    token_count = tokenize_text(page, text, is_first)
                    district = file.split('.')[0]
                    results[date_key][district] = token_count
                    print(f"Processed {date_key} - {district}: {token_count} tokens")
                    is_first = False

        browser.close()
    return results

def save_to_csv(results, output_file):
    districts = ['atlanta', 'boston', 'chicago', 'cleveland', 'dallas', 'kansas_city',
                 'minneapolis', 'new_york', 'philadelphia', 'richmond', 'san_francisco',
                 'st_louis', 'national_summary']
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date'] + districts)
        for date, counts in sorted(results.items()):
            writer.writerow([date] + [counts.get(district, 0) for district in districts])

if __name__ == "__main__":
    paths = Paths()
    root_dir = paths.beige_books_raw_scraped()
    output_file = os.path.join(paths.master(), "data", "bb_tokens_table.csv")

    results = process_beige_books(root_dir)
    save_to_csv(results, output_file)
    print(f"Results saved to {output_file}")
