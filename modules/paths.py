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

    def data(self):
        return os.path.join(self.root, 'data')
    
    def bb_dates(self):
        return os.path.join(self.root, 'data', 'bb_dates.xlsx')

    def all_data_csv(self):
        return os.path.join(self.root, 'data', 'all_data.csv')

    def modules(self):
        return os.path.join(self.root, 'modules')

    def scraper(self):
        return os.path.join(self.root, 'scraper')

    def llm_scores_folder(self):
        return os.path.join(self.root, 'data', 'llm_scores')
    
    def spx_data_csv(self):
        return os.path.join(self.root, 'data', 'spx', 'spx.xlsx')
    
    def control_vars_folder(self):
        return os.path.join(self.root, 'data', 'control variables')
    
    def figures(self):
        figures_path = os.path.join(self.root, 'figures')
        if not os.path.exists(figures_path):
            os.makedirs(figures_path)
        return figures_path