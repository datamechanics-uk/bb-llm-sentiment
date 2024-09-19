import numpy as np
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error
import logging

class NIPALSModel:
    def __init__(self, max_components=13, n_splits=5):
        self.max_components = max_components
        self.n_splits = n_splits
        self.optimal_n_components = None
        self.pls = None
        self.X_scaler = StandardScaler()
        self.y_scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)

    def remove_nan_rows(self, X, Y):
        combined = np.hstack((X, Y))
        valid_rows = ~np.isnan(combined).any(axis=1)
        return X[valid_rows], Y[valid_rows]

    def select_optimal_components(self, X, Y):
        X, Y = self.remove_nan_rows(X, Y)
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        mse_scores = np.zeros((self.max_components, self.n_splits))

        for n_comp in range(1, self.max_components + 1):
            split_scores = []
            for train_index, test_index in tscv.split(X):
                X_train, X_test = X[train_index], X[test_index]
                Y_train, Y_test = Y[train_index], Y[test_index]

                pls = PLSRegression(n_components=n_comp, scale=False, max_iter=10000)
                pls.fit(X_train, Y_train)
                Y_pred = pls.predict(X_test)
                
                mse = np.mean(mean_squared_error(Y_test, Y_pred, multioutput='raw_values'))
                split_scores.append(mse)
            
            mse_scores[n_comp-1] = split_scores

        mean_mse_scores = np.mean(mse_scores, axis=1)
        self.optimal_n_components = np.argmin(mean_mse_scores) + 1
        
        self.logger.info(f"Optimal number of components: {self.optimal_n_components}")
        return self.optimal_n_components

    def fit(self, X, Y):
        X, Y = self.remove_nan_rows(X, Y)
        X_scaled = self.X_scaler.fit_transform(X)
        Y_scaled = self.y_scaler.fit_transform(Y)

        self.optimal_n_components = self.select_optimal_components(X_scaled, Y_scaled)
        
        self.pls = PLSRegression(n_components=self.optimal_n_components, scale=False, max_iter=10000)
        self.pls.fit(X_scaled, Y_scaled)

    def predict(self, X):
        X_scaled = self.X_scaler.transform(X)
        Y_pred_scaled = self.pls.predict(X_scaled)
        return self.y_scaler.inverse_transform(Y_pred_scaled)

    def get_metrics(self, Y_true, Y_pred, y_vars):
        metrics_list = []
        for i, y_var in enumerate(y_vars):
            y_true = Y_true[:, i]
            y_pred = Y_pred[:, i]
            
            ss_total = np.sum((y_true - np.mean(y_true))**2)
            ss_residual = np.sum((y_true - y_pred)**2)
            ss_regression = max(0, ss_total - ss_residual)
            
            n = len(y_true)
            df_regression = self.optimal_n_components
            df_residual = max(1, n - df_regression - 1)
            
            mse = ss_residual / n
            r2 = max(0, 1 - (ss_residual / ss_total)) if ss_total > 0 else 0
            r2_adj = max(0, 1 - ((1 - r2) * (n - 1) / (n - df_regression - 1)))
            
            if ss_regression > 0 and ss_residual > 0:
                f_statistic = (ss_regression / df_regression) / (ss_residual / df_residual)
                p_value = 1 - stats.f.cdf(f_statistic, df_regression, df_residual)
            else:
                f_statistic = 0
                p_value = 1
            
            metrics_list.append({
                'Dependent Variable': y_var,
                'MSE': mse,
                'R²': r2,
                'Adjusted R²': r2_adj,
                'F-Statistic': f_statistic,
                'P-Value': p_value,
                'SS Total': ss_total,
                'SS Residual': ss_residual,
                'SS Regression': ss_regression,
                'DF Regression (Optimal Components)': df_regression,
                'DF Residual': df_residual
            })
        
        return pd.DataFrame(metrics_list)
    
    def plot_correlation_matrix(self, data):
        numeric_data = data.select_dtypes(include=[np.number])
        correlation_matrix = numeric_data.corr()

        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', square=True, cbar_kws={"shrink": .8})
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig('results/correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return correlation_matrix
        
    def descriptive_statistics(self, data, writer):
        numeric_data = data.select_dtypes(include=[np.number])
        
        stats = {
            'Mean': numeric_data.mean(),
            'Min': numeric_data.min(),
            'Max': numeric_data.max(),
            'Standard Deviation': numeric_data.std(),
            'N (Observations)': numeric_data.count(),
            'Missing Values': numeric_data.isnull().sum(),
        }
        
        descriptive_stats = pd.DataFrame(stats)
        descriptive_stats = descriptive_stats.reset_index().rename(columns={'index': 'Variable Name'})
        descriptive_stats.to_excel(writer, sheet_name='Descriptive Statistics', index=False)

    def plot_relationship(self, Y_true, Y_pred, llm_model, y_vars, results_dir):
        os.makedirs(results_dir, exist_ok=True)
        for i, y_var in enumerate(y_vars):
            df = pd.DataFrame({'Predicted': Y_pred[:, i], 'Actual': Y_true[:, i]})
            
            g = sns.jointplot(x='Predicted', y='Actual', data=df, kind='reg', height=7, ratio=5)
            
            min_val = min(df['Predicted'].min(), df['Actual'].min())
            max_val = max(df['Predicted'].max(), df['Actual'].max())
            g.ax_joint.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')
            
            r2 = r2_score(df['Actual'], df['Predicted'])
            g.ax_joint.text(0.05, 0.95, f'R² = {r2:.2f}', transform=g.ax_joint.transAxes, 
                            verticalalignment='top')
            
            g.set_axis_labels('Predicted SPX Returns', 'Actual SPX Returns')
            plt.suptitle(f'PLS: {llm_model} vs {y_var}', y=1.02)
            
            g.ax_joint.legend()
            
            plt.savefig(os.path.join(results_dir, f'{llm_model}_{y_var}_relationship.png'), bbox_inches='tight')
            plt.close()