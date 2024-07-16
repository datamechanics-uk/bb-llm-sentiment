import os

class BeigeBookSearcher:
    def __init__(self, base_path='beige_books'):
        self.base_path = base_path

    def get_chapter_text(self, year, sequence, chapter):
        """
        Retrieve the text of a specific Beige Book chapter based on its release sequence in the year.

        :param year: Year of the Beige Book (e.g., 2023)
        :param sequence: Sequence of the release in the year (1 for first release, 2 for second, etc.)
        :param chapter: Name of the chapter (e.g., 'national_summary', 'boston')
        :return: Text content of the chapter
        """
        
        year_path = os.path.join(self.base_path, str(year))
        month_folders = sorted([f for f in os.listdir(year_path) if f.isdigit()])
        month_folder = month_folders[sequence - 1]
        file_path = os.path.join(year_path, month_folder, f"{chapter}.txt")

        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def get_available_releases(self, year):
        year_path = os.path.join(self.base_path, str(year))
        
        return len([f for f in os.listdir(year_path) if f.isdigit()])
    
    def get_available_chapters(self, year, sequence):
        year_path = os.path.join(self.base_path, str(year))
        month_folders = sorted([f for f in os.listdir(year_path) if f.isdigit()])
        month_folder = month_folders[sequence - 1]
        release_path = os.path.join(year_path, month_folder)
        return [f.split(".")[0] for f in os.listdir(release_path) if f.endswith(".txt")]

# Example usage
if __name__ == '__main__':
    searcher = BeigeBookSearcher()

    year = 1973
    release_number = 1
    chapter = "national_summary"

    chapter_text = searcher.get_chapter_text(year, release_number, chapter)
    print(f"Release {release_number} of {year}, {chapter.capitalize()} (first 100 characters):")
    print(chapter_text[:100] + "...")
    
    available_chapters = searcher.get_available_chapters(year, release_number)
    print(f"\nAvailable chapters for year {year}, release {release_number}:")
    print(", ".join(available_chapters))

    releases = searcher.get_available_releases(year)
    print(f"\nNumber of available releases for {year}: {releases}")