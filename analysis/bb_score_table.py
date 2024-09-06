import os
import csv
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths
from modules.llm_score import LLM

def read_beige_book_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def load_existing_rows(output_file):
    existing_rows = set()
    if os.path.isfile(output_file):
        with open(output_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    existing_rows.add((row[0], row[1]))
    return existing_rows

def save_to_csv(results, output_file):
    districts = ['atlanta', 'boston', 'chicago', 'cleveland', 'dallas', 'kansas_city',
                 'minneapolis', 'new_york', 'philadelphia', 'richmond', 'san_francisco',
                 'st_louis', 'national_summary']
    
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Date', 'Metric'] + districts)
        
        for date, counts in sorted(results.items()):
            gdp_row = [date, 'GDP']
            sp500_row = [date, 'SP500']
            for district in districts:
                gdp_score, sp500_score = counts.get(district, ('', ''))
                gdp_row.append(gdp_score)
                sp500_row.append(sp500_score)
            writer.writerow(gdp_row)
            writer.writerow(sp500_row)
            csvfile.flush() # Ensures data is written immediately

def process_beige_books(root_dir, model):
    output_file = os.path.join(Paths().master(), "data/llm_scores", f"{model.__name__}_scores.csv")
    existing_rows = load_existing_rows(output_file)

    for year in sorted(os.listdir(root_dir)):
        year_path = os.path.join(root_dir, year)
        for month in os.listdir(year_path):
            date_key = f"{year}-{month}"
            if (date_key, 'GDP') in existing_rows and (date_key, 'SP500') in existing_rows:
                print(f"Skipping {date_key} as it already exists in the CSV.")
                continue
            
            results = {date_key: {}}
            month_path = os.path.join(year_path, month)
            for file in os.listdir(month_path):
                file_path = os.path.join(month_path, file)
                chapter = read_beige_book_text(file_path)
                district = file.split('.')[0]
                try:
                    gdp_score, sp500_score = model(chapter=chapter)
                    results[date_key][district] = (gdp_score, sp500_score)
                    print(f"Processed {date_key} - {district}: GDP score {gdp_score}, SP500 score {sp500_score}")
                except ValueError as e:
                    print(f"Error scoring text for {date_key} - {district}: {e}")
                except Exception as e:
                    print(f"Unexpected error for {date_key} - {district}: {e}")
            
            # Save results after processing each month
            save_to_csv(results, output_file)

if __name__ == "__main__":
    paths = Paths()
    llm = LLM()

    models = [
        llm.TitanTextPremier,
        llm.MistralLarge2402,
        llm.CohereCommandRPlus,
        llm.MetaLlama370B,
        llm.Claude35Sonnet
    ]

    for model in models:
        print(f"Processing with model: {model.__name__}")
        process_beige_books(root_dir=paths.beige_books_processed_all(), model=model)
        print(f"Results saved for model: {model.__name__}")