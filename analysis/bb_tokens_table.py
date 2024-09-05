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
                 'st_louis', 'national_summary', 'total']
    
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Date'] + districts)
        
        for date, counts in sorted(results.items()):
            total_tokens = sum(counts.get(district, 0) for district in districts[:-1])
            row = [date] + [counts.get(district, '') for district in districts[:-1]] + [total_tokens]
            writer.writerow(row)

def process_beige_books(root_dir, output_file):
    total_tokens_all = 0
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
                total_tokens_all += token_count
                print(f"Processed {date_key} - {district}: {token_count} tokens")

            save_to_csv(results, output_file)
            
    print(f"Total tokens processed: {total_tokens_all}")

if __name__ == "__main__":
    paths = Paths()
    root_dir = paths.beige_books_processed_all()
    output_file = os.path.join(paths.master(), "data", "bb_tokens_table.csv")
    process_beige_books(root_dir, output_file)
    print(f"Results saved to {output_file}")