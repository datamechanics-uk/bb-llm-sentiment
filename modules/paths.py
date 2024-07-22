import os

class Paths:
    def __init__(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    def master(self):
        return self.root

    def beige_books_processed_all(self):
        return os.path.join(self.root, 'beige_books', 'processed_all')

    def beige_books_raw_manual(self):
        return os.path.join(self.root, 'beige_books', 'raw_manual')

    def beige_books_raw_scraped(self):
        return os.path.join(self.root, 'beige_books', 'raw_scraped')

    def modules(self):
        return os.path.join(self.root, 'modules')

    def scraper(self):
        return os.path.join(self.root, 'scraper')
