import os
import csv
import tiktoken
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths

def count_tokens(text):
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def save_to_csv(results, output_file):
    districts = ['atlanta', 'boston', 'chicago', 'cleveland', 'dallas', 'kansas_city',
                 'minneapolis', 'new_york', 'philadelphia', 'richmond', 'san_francisco',
                 'st_louis', 'national_summary']
    
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Date'] + districts)
        
        for date, counts in sorted(results.items()):
            row = [date] + [counts.get(district, '') for district in districts]
            writer.writerow(row)

def process_beige_books(root_dir, output_file):
    for year in sorted(os.listdir(root_dir)):
        year_path = os.path.join(root_dir, year)
        for month in os.listdir(year_path):
            date_key = f"{year}-{month}"
            results = {date_key: {}}
            month_path = os.path.join(year_path, month)
            for file in os.listdir(month_path):
                with open(os.path.join(month_path, file), 'r', encoding='utf-8') as f:
                    text = f.read()
                token_count = count_tokens(text)
                district = file.split('.')[0]
                results[date_key][district] = token_count
                print(f"Processed {date_key} - {district}: {token_count} tokens")
            
            # Save results after processing each month
            save_to_csv(results, output_file)

if __name__ == "__main__":
    paths = Paths()
    root_dir = paths.beige_books_raw_scraped()
    output_file = os.path.join(paths.master(), "data", "bb_tokens_table.csv")
    
    process_beige_books(root_dir, output_file)
    print(f"Results saved to {output_file}")