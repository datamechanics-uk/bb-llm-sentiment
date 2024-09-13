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

    def modules(self):
        return os.path.join(self.root, 'modules')

    def scraper(self):
        return os.path.join(self.root, 'scraper')

    def llm(self, model_name : str):
        return os.path.join(self.root, 'data', 'llm_scores', model_name)
    
    def spx_data(self):
        return os.path.join(self.root, 'data', 'spx', 'spx.xlsx')
    
    def control_vars(self, variable_name):
        return os.path.join(self.root, 'data', 'control_variables', variable_name)