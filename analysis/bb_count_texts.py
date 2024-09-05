import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths
from modules.write_csv import WriteCSV

def bb_properties(directory):
    total_bbs = 0
    total_chapters = 0

    for year in os.listdir(directory):
        year_path = os.path.join(directory, year)
        if os.path.isdir(year_path):
            months = [m for m in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, m))]
            total_bbs += len(months)
            
            for month in months:
                month_path = os.path.join(year_path, month)
                chapters = [f for f in os.listdir(month_path) if f.endswith('.txt')]
                total_chapters += len(chapters)

    return total_bbs, total_chapters

# Count for scraped Beige Books chapters and reports
bbs_scraped, chapters_scraped = bb_properties(Paths().beige_books_raw_scraped())

# Count for manually obtained Beige Book chapters
bbs_manual, chapters_manual = bb_properties(Paths().beige_books_raw_manual())

# Count for processed Beige Books chapters
bbs_processed, chapters_processed = bb_properties(Paths().beige_books_processed_all())

# Prepare data for CSV
csv_data = [
    ['Beige Books Scraped', bbs_scraped],
    ['Chapters Scraped', chapters_scraped],
    ['Chapters Manually Obtained', chapters_manual],
    ['Beige Books Processed', bbs_processed],
    ['Chapters Processed', chapters_processed]
]

# Write to csv
WriteCSV().write(path=Paths().data() + '/bb_count.csv', data=csv_data)

print(f"Scraped Beige Books: {bbs_scraped}")
print(f"Scraped Chapters: {chapters_scraped}")
print(f"Manually Obtained Chapters: {chapters_manual}")
print(f"Processed Chapters: {chapters_processed}")
print(f"Processed Beige Books: {bbs_processed}")