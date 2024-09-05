import csv
import calendar
from collections import defaultdict
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths
from modules.assets import Assets

class Table:
    def __init__(self):
        paths = Paths()
        self.base_path = paths.beige_books_raw_scraped()
        self.years = range(2013, 2024)
        self.expected_releases = 8
        self.expected_chapters = 13
        self.months = [calendar.month_abbr[i] for i in range(1, 13)]
        self.expected_chapter_names = Assets().chapters()

    def generate_table(self):
        table = defaultdict(lambda: defaultdict(int))
        missing_releases = []
        missing_chapters = []

        for year in self.years:
            year_path = os.path.join(self.base_path, str(year))
            if not os.path.exists(year_path):
                continue

            releases = [f for f in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, f))]
            table[year]['releases'] = len(releases)

            if len(releases) != self.expected_releases:
                missing_releases.append(f"{year}: {len(releases)} releases (expected {self.expected_releases})")

            for release in releases:
                release_path = os.path.join(year_path, release)
                chapters = [f.split('.')[0] for f in os.listdir(release_path) if f.endswith('.txt')]
                month = self.months[int(release) - 1]
                table[year][month] = len(chapters)

                if len(chapters) != self.expected_chapters:
                    missing = set(self.expected_chapter_names) - set(chapters)
                    missing_chapters.append(f"{year} {month}: {len(chapters)} chapters, Missing: {', '.join(sorted(missing))}")

        return table, missing_releases, missing_chapters

    def write_table_to_csv(self, output_file=None):
        if output_file is None:
            output_file = os.path.join(os.path.dirname(__file__), "..", "data", "bb_anomalies_table.csv")

        table, missing_releases, missing_chapters = self.generate_table()
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Year", "Total Releases"] + self.months)

            for year in sorted(table.keys()):
                row = [year, table[year]['releases']] + [table[year].get(month, "N/A") for month in self.months]
                writer.writerow(row)

            writer.writerow([])
            writer.writerow(["Missing Releases:"])
            for item in missing_releases:
                writer.writerow([item])

            writer.writerow([])
            writer.writerow(["Missing Chapters:"])
            for item in missing_chapters:
                writer.writerow([item])

        print(f"table written to {output_file}")

if __name__ == "__main__":
    table = Table()
    table.write_table_to_csv()
