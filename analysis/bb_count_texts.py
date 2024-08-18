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
total_bbs, scraped_chapters = bb_properties(Paths().beige_books_raw_scraped())

# Count for manually obtained Beige Book chapters
_, manual_chapters = bb_properties(Paths().beige_books_raw_manual())

# Count total chapters
total_chapters = scraped_chapters + manual_chapters

# Prepare data for CSV
csv_data = [
    ['Total Beige Books', total_bbs],
    ['Total Chapters', total_chapters],
    ['Scraped Chapters', scraped_chapters],
    ['Manual Chapters', manual_chapters]
]

# Write to csv
WriteCSV().write(path=Paths().data() + '/bb_count.csv', data=csv_data)

print(f"Total Beige Books: {total_bbs}")
print(f"Total Chapters: {total_chapters}")
print(f"Scraped Chapters: {scraped_chapters}")
print(f"Manual Chapters: {manual_chapters}")