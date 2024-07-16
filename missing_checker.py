import os
import csv
import calendar

class BeigeBookChecker:
    def __init__(self, base_path="beige_books"):
        self.base_path = base_path
        self.years = range(1970, 2024)
        self.expected_releases = 8
        self.expected_chapters = 13
        self.months = [calendar.month_abbr[i] for i in range(1, 13)]

    def count_files(self):
        counts = {}
        missing = {
            "releases": [],
            "chapters": []
        }

        for year in self.years:
            year_path = os.path.join(self.base_path, str(year))
            if not os.path.exists(year_path):
                continue

            releases = [f for f in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, f))]
            counts[year] = {'releases': len(releases)}

            if len(releases) != self.expected_releases:
                missing["releases"].append(f"Year {year}: {len(releases)} releases (expected {self.expected_releases})")

            for release in releases:
                release_path = os.path.join(year_path, release)
                chapters = [f for f in os.listdir(release_path) if f.endswith('.txt')]
                month_index = int(release) - 1  # Convert '01' to 0, '02' to 1, etc.
                counts[year][self.months[month_index]] = len(chapters)

                if len(chapters) != self.expected_chapters:
                    missing["chapters"].append(f"Year {year}, {self.months[month_index]}: {len(chapters)} chapters (expected {self.expected_chapters})")

        return counts, missing

    def write_count_results_to_csv(self, output_file="beige_book_count_results.csv"):
        counts, missing = self.count_files()
        count_release_missing = len(missing["releases"])
        count_chapter_missing = len(missing["chapters"])
        count_total_missing = count_release_missing + count_chapter_missing

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(["Year"] + self.months + ["Total Releases"])
            
            # Counts
            for year in sorted(counts.keys()):
                row = [year, counts[year]['releases']]
                for month in self.months:
                    row.append(counts[year].get(month, "N/A"))
                writer.writerow(row)
            
            # missing
            writer.writerow([])
            writer.writerow([f"Release missing: {count_release_missing}"])
            for anomaly in missing["releases"]:
                writer.writerow([anomaly])
            writer.writerow([])
            writer.writerow([f"Chapter missing {count_chapter_missing}"])
            for anomaly in missing["chapters"]:
                writer.writerow([anomaly])
            writer.writerow([])
            writer.writerow([f"Total missing: {count_total_missing}"])
                

        print(f"Results written to {output_file}")

if __name__ == "__main__":
    checker = BeigeBookChecker()
    checker.write_count_results_to_csv()