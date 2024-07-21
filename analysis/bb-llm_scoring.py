import csv
import os
import random
from typing import List, Dict

class MockLLMAnalyser:
    def __init__(self):
        self.metrics = ["gdp", "interest_rates", "inflation", "employment", "stock_market"]

    def analyse_text(self, text: str, model_id: str) -> Dict[str, int]:
        mock_analysis = {}
        for metric in self.metrics:
            rating = random.choice([-1, 0, 1])
            mock_analysis[metric] = rating
        return mock_analysis
    
    def analyse_and_fill_csv(self, text: str, csv_filename: str, models: List[str]):
        headers = ["Metrics"] + models
        
        results: Dict[str, Dict[str, int]] = {}
        for model in models:
            results[model] = self.analyse_text(text, model)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, '..', 'data')
        
        os.makedirs(data_dir, exist_ok=True)
        
        csv_path = os.path.join(data_dir, csv_filename)
        
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            
            for metric in self.metrics:
                row = [metric.replace("_", " ").title()]
                for model in models:
                    row.append(results[model][metric])
                writer.writerow(row)

        print(f"CSV file created: {csv_path}")

    def get_models(self):
        return ['mock.model-1', 'mock.model-2', 'mock.model-3']

def main():
    analyser = MockLLMAnalyser()
    models = analyser.get_models()
    beige_book_text = "This is a sample Beige Book text for testing purposes."
    
    csv_filename = "analysis_results.csv"

    analyser.analyse_and_fill_csv(beige_book_text, csv_filename, models)

if __name__ == "__main__":
    main()