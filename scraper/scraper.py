import os
import re
import requests
from bs4 import BeautifulSoup
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.logger import Logger
from modules.paths import Paths

class Scraper:
    def __init__(self):
        self.header = "https://www.minneapolisfed.org/beige-book-reports/"
        self.years = list(range(1970, 2024))
        self.months = list(range(1, 13))
        self.regions = {
            "atlanta": "at",
            "boston": "bo",
            "chicago": "ch",
            "cleveland": "cl",
            "dallas": "da",
            "kansas_city": "kc",
            "minneapolis": "mi",
            "new_york": "ny",
            "philadelphia": "ph",
            "richmond": "ri",
            "san_francisco": "sf",
            "st_louis": "sl",
            "national_summary": "su"
        }
        paths = Paths()
        self.beige_books_folder = paths.bb_raw_scraped()
        self.logger = Logger(os.path.join(paths.scraper(), "scraper_log"))
    
    def ensure_dir(self, file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def scrape_and_save_text(self):
        for year in self.years:
            for month in self.months:
                if not self.check_month_data(year, month):
                    self.logger.info(f"No data for {year}-{month:02d}, skipping this month.")
                    continue

                for name, code in self.regions.items():
                    file_path = os.path.join(self.beige_books_folder, str(year), f"{month:02d}", f"{name}.txt")
                    
                    # Skip if file already exists
                    if os.path.exists(file_path):
                        print(f"File already exists: {file_path}")
                        continue

                    # Try both URL formats for all regions
                    urls = [
                        f"{self.header}{year}/{year}-{month:02d}-{code}",
                        f"{self.header}{year}/{year}-{month:02d}-{name.replace('_', '-')}"
                    ]

                    for url in urls:
                        try:
                            r = requests.get(url)
                            if r.status_code == 200:
                                soup = BeautifulSoup(r.text, features="html5lib")
                                div = soup.find("div", class_="col-sm-12 col-lg-8 offset-lg-1")
                                raw = re.sub(r"\s*\n\s*", "\n", div.text).strip()
                                raw = raw.split("\n", 3)[3] if len(raw.split("\n", 3))>3 else raw
                                
                                self.ensure_dir(file_path)
                                
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(raw)
                                self.logger.info(f"Data scraped for {url.split('/')[-1]}.")
                                break
                            else:
                                self.logger.info(f"No data for {url.split('/')[-1]}")
                        except Exception as e:
                            self.logger.error(f"Error fetching {url.split('/')[-1]}: {e}")

    def check_month_data(self, year, month):
        # Check if data exists for this month using the first region (atlanta)
        urls = [
            f"{self.header}{year}/{year}-{month:02d}-at",
            f"{self.header}{year}/{year}-{month:02d}-atlanta"
        ]
        for url in urls:
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    return True
            except:
                pass
        return False

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_and_save_text()