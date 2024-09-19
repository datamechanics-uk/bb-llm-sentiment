import pandas as pd
import os
import sys
import matplotlib
matplotlib.use('Agg')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths
from modules.pls import NIPALSModel

class Analysis:
    def __init__(self):
        self.data_dir = Paths().all_data_csv()
        self.data = pd.read_csv(self.data_dir, usecols=lambda x: x != 'Unnamed: 0')
        self.models = [
            "Claude35Sonnet",
            "CohereCommandrPlus",
            "MetaLlama370B",
            "MistralLarge2402",
            "TitanTextPremier"
        ]
        self.spx_tfs = ["1D", "3D", "7D", "14D"]
        self.pls_models = {}

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
        
        X, y_values = self.remove_nan_rows(X, y_values)

        pls = NIPALSModel(max_components=13, n_splits=5)
        pls.fit(X.values, y_values.values)
        y_pred = pls.predict(X.values)
        metrics_df = pls.get_metrics(y_values.values, y_pred, y_values.columns)

        pls.plot_relationship(
            Y_true=y_values.values,
            Y_pred=y_pred,
            llm_model=f"{llm_model}_{'with' if use_controls else 'without'}_controls",
            y_vars=self.spx_tfs,
            results_dir='results/controls' if use_controls else 'results/no_controls'
        )
    
        return metrics_df
        
    def add_confidence_sheet(self, writer):
        confidence_data = {}
        for model in self.models:
            scores = self.data[[col for col in self.data.columns if model.lower() in col.lower()]]
            extreme_scores = (scores.abs() == 1).sum().sum()
            total_scores = scores.count().sum()
            confidence = extreme_scores / total_scores
            confidence_data[model] = [confidence]
        
        confidence_df = pd.DataFrame(confidence_data, index=['Confidence Level'])
        confidence_df.to_excel(writer, sheet_name='LLM Confidence')

def main():
    analysis = Analysis()
    results_with_controls = {}
    results_without_controls = {}
    
    for model in analysis.models:
        results_with_controls[model] = analysis.run_pls(model, use_controls=True)
        results_without_controls[model] = analysis.run_pls(model, use_controls=False)
    
    # Restructure the data for better Excel output
    def restructure_results(results_dict):
        restructured_data = []
        for model, metrics in results_dict.items():
            for i, row in metrics.iterrows():
                row_data = {
                    'Model': model,
                    'Dependent Variable': "SPX"+analysis.spx_tfs[i],
                    **row.to_dict()
                }
                restructured_data.append(row_data)
        return pd.DataFrame(restructured_data)

    df_with_controls = restructure_results(results_with_controls)
    df_without_controls = restructure_results(results_without_controls)
    
    with pd.ExcelWriter('pls_results.xlsx') as writer:
        df_with_controls.to_excel(writer, sheet_name='With Controls', index=False)
        df_without_controls.to_excel(writer, sheet_name='Without Controls', index=False)

        # Generate and save correlation matrix
        pls = NIPALSModel(max_components=13, n_splits=5)
        correlation_matrix = pls.plot_correlation_matrix(analysis.data)
        correlation_matrix.to_excel(writer, sheet_name='Correlation Matrix', index=False)
        
        # Save descriptive statistics
        pls.descriptive_statistics(data=analysis.data, writer=writer)
        
        # Add confidence sheet
        analysis.add_confidence_sheet(writer)

if __name__ == "__main__":
    main()