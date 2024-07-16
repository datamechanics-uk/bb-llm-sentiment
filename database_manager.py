import csv
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, file_path='beige_book_analysis.csv'):
        self.file_path = file_path
        self.headers = ['id', 'date', 'chapter', 'model_name', 'metric', 'rating', 'justification']
        
        if not os.path.exists(self.file_path):
            self.create_csv()

    def create_csv(self):
        with open(self.file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)

    def add_analysis(self, chapter, model_name, metric, rating, justification):
        with open(self.file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                self.generate_id(),
                datetime.now().strftime('%Y-%m-%d'),
                chapter,
                model_name,
                metric,
                rating,
                justification
            ])

    def generate_id(self):
        with open(self.file_path, 'r') as file:
            return sum(1 for line in file)

    # ... (other methods remain the same)