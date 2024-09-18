import pandas as pd
import numpy as np
import os
import sys
import matplotlib
matplotlib.use('Agg')
from openpyxl import Workbook

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths
from modules.pls import PLSModel
from modules.logger import Logger

# Set up logging
logger = Logger('analysis.log')

class Analysis:
    def __init__(self):
        self.data_dir = Paths().all_data_csv()
        self.data = pd.read_csv(self.data_dir)
        self.models = [
            "Claude35Sonnet",
            "CohereCommandrPlus",
            "MetaLlama370B",
            "MistralLarge2402",
            "TitanTextPremier"
        ]
        self.spx_tfs = ["1D", "3D", "7D", "14D"]
        self.pls_models = {}  # To store PLSModel instances for each model

    def scores(self, llm_model):
        scores = [col for col in self.data.columns if llm_model.lower() in col.lower()]
        return self.data[scores]

    def spx_returns(self):
        returns = [col for col in self.data.columns if col.startswith("SPX")]
        return self.data[returns]
    
    def control_vars(self):
        control_vars = ["cpi", "gdp", "unemployment (seasonally adjusted)", "us3m", "us6m", "us1y", "us2y", "us5y", "us10y"]
        return self.data[control_vars]
    
    def remove_nan_rows(self, X, Y):
        # Combine X and Y to ensure we remove corresponding rows
        combined = pd.concat([X, Y], axis=1)
        # Remove rows with any NaN values
        cleaned = combined.dropna()
        return cleaned[X.columns], cleaned[Y.columns]
    
    def run_pls(self, llm_model, use_controls=True):
        x_values = self.scores(llm_model)
        y_values = self.spx_returns()
        
        if use_controls:
            control_values = self.control_vars()
            X = pd.concat([x_values, control_values], axis=1)
        else:
            X = x_values
        
        # Remove NaN rows
        X, y_values = self.remove_nan_rows(X, y_values)
        
        logger.info(f"Shape of X after removing NaNs: {X.shape}")
        logger.info(f"Shape of Y after removing NaNs: {y_values.shape}")
        
        pls = PLSModel(max_components=13, n_splits=5)
        pls.fit(X.values, y_values.values)
        y_pred = pls.predict(X.values)
        metrics = pls.get_metrics(y_values.values, y_pred)
        q2 = pls.calculate_q2(X.values, y_values.values)
        
        logger.debug(f"Metrics for {llm_model} ({'with' if use_controls else 'without'} controls): {metrics}")
        
        pls.plot_relationship(
            Y_true=y_values.values,
            Y_pred=y_pred,
            llm_model=f"{llm_model}_{'with' if use_controls else 'without'}_controls",
            y_vars=self.spx_tfs,
            results_dir='results/controls' if use_controls else 'results/no_controls'
        )
        
        return {
            'metrics': metrics,
            'q2': q2
        }

def main():
    analysis = Analysis()
    results_with_controls = {}
    results_without_controls = {}
    
    for model in analysis.models:
        logger.info(f"Running PLS analysis for {model} with controls")
        results_with_controls[model] = analysis.run_pls(model, use_controls=True)
        
        logger.info(f"Running PLS analysis for {model} without controls")
        results_without_controls[model] = analysis.run_pls(model, use_controls=False)
    
    # Convert results to DataFrames
    df_with_controls = pd.DataFrame(results_with_controls).T
    df_without_controls = pd.DataFrame(results_without_controls).T
    
    # Save results to Excel file
    with pd.ExcelWriter('pls_results.xlsx') as writer:
        df_with_controls.to_excel(writer, sheet_name='With Controls')
        df_without_controls.to_excel(writer, sheet_name='Without Controls')
    
    logger.info("PLS analysis completed. Results saved in 'pls_results_comparison.xlsx'.")

if __name__ == "__main__":
    main()