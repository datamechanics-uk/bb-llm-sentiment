import os
from tqdm import tqdm
import time
from database_manager import DatabaseManager
from llm_analyser import LLMAnalyser
from beige_book_searcher import BeigeBookSearcher
import random

def mock_analyze_text(text, model_id):
    metrics = ['gdp', 'interest_rate', 'inflation', 'employment', 'stock_market']
    return {metric: {'rating': random.choice([-1, 0, 1]), 'justification': f"Mock justification for {metric}"} for metric in metrics}

def main(start_year=1973, end_year=2023, dry_run=True):
    analysis_folder = 'analysis'
    os.makedirs(analysis_folder, exist_ok=True)
    
    csv_path = os.path.join(analysis_folder, 'beige_book_analysis.csv')
    db_manager = DatabaseManager(csv_path)
    llm_analyzer = LLMAnalyser()
    beige_book_searcher = BeigeBookSearcher()

    models = llm_analyzer.get_available_models()[:2]  # Limit to first 2 models for testing

    total_analyses = 0
    for year in range(start_year, end_year + 1):
        releases = beige_book_searcher.get_available_releases(year)
        for release in range(1, releases + 1):
            chapters = beige_book_searcher.get_available_chapters(year, release)
            total_analyses += len(chapters) * len(models)

    pbar = tqdm(total=total_analyses, unit='analysis')
    start_time = time.time()

    for year in range(start_year, end_year + 1):
        releases = beige_book_searcher.get_available_releases(year)

        for release in range(1, releases + 1):
            chapters = beige_book_searcher.get_available_chapters(year, release)

            for chapter in chapters:
                text = beige_book_searcher.get_chapter_text(year, release, chapter)

                for model in models:
                    try:
                        if dry_run:
                            analysis = mock_analyze_text(text, model)
                        else:
                            analysis = llm_analyzer.analyze_text(text, model)
                        
                        for metric, data in analysis.items():
                            db_manager.add_analysis(f"{year}-{release}-{chapter}", model, metric, data['rating'], data['justification'])
                        
                        pbar.update(1)
                        
                        elapsed_time = time.time() - start_time
                        analyses_completed = pbar.n
                        analyses_remaining = total_analyses - analyses_completed
                        time_per_analysis = elapsed_time / analyses_completed
                        estimated_time_remaining = analyses_remaining * time_per_analysis
                        
                        pbar.set_postfix({'Estimated Time Remaining': f'{estimated_time_remaining:.2f}s'})

                    except Exception as e:
                        print(f"\nError analyzing {year}-{release}-{chapter} with {model}: {str(e)}")

    pbar.close()
    print("\nAnalysis complete")

if __name__ == "__main__":
    main(start_year=1973, end_year=1975, dry_run=True)  # Set dry_run to False when ready to use actual LLM API