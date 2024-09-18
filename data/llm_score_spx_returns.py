import pandas as pd
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths

paths = Paths()

# Load Beige Book dates
bb_dates = pd.read_excel(paths.bb_dates(), names=['Year', 'Month', 'Day'])
bb_dates = bb_dates.apply(lambda x: x.astype(str).str.strip())
bb_dates['Date'] = pd.to_datetime(bb_dates[['Year', 'Month', 'Day']]).dt.date
bb_dates = bb_dates[['Date']].set_index('Date')

# Creating LLM Scores Dataframes
llm_score_files = ["Claude35Sonnet_scores.csv", "CohereCommandRPlus_scores.csv", "MetaLlama370B_scores.csv", "MistralLarge2402_scores.csv", "TitanTextPremier_scores.csv"]
llm_scores = {}
for file in llm_score_files:
    df = pd.read_csv(os.path.join(paths.llm_scores_folder(), file))
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m').dt.to_period('M')
    df.set_index('Date', inplace=True)
    llm_scores[file.split('_')[0]] = df
    
# Creating SPX Dataframe
spx_data = pd.read_excel(paths.spx_data_csv(), skiprows=6, parse_dates=["Date"])
spx_data.set_index('Date', inplace=True)
spx_data.sort_index(ascending=True, inplace=True)

# Creating Control Variables Dataframes
control_var_files = ["cpi.xlsx", "gdp.xlsx", "unemployment (seasonally adjusted).xlsx", "us3m.xlsx", "us6m.xlsx", "us1y.xlsx", "us2y.xlsx", "us5y.xlsx", "us10y.xlsx"]
control_vars = {}
for file in control_var_files:
    df = pd.read_excel(os.path.join(paths.control_vars_folder(), file), skiprows=5)
    df.columns = ['Date', 'PX_LAST', 'PX_MID']
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(ascending=True, inplace=True)
    control_vars[file.split(".")[0]] = df
    
# Merge Dataframes
merged_df = bb_dates.reset_index()
merged_df['YearMonth'] = pd.to_datetime(merged_df['Date']).dt.to_period('M')

for llm, scores_df in llm_scores.items():
    for district in scores_df.columns:
        merged_df[f"{district}_{llm}"] = merged_df['YearMonth'].map(scores_df[district])

merged_df = merged_df.drop('YearMonth', axis=1)


def add_spx_returns_to_merged(spx_data):
    merged_df['Date'] = pd.to_datetime(merged_df['Date'])
    spx_dates = spx_data.index.tolist()
    control_var_dfs = control_vars
    control_var_names = list(control_var_dfs.keys())
    
    def process_row(bb_date):
        base_idx = spx_dates.index(next(date for date in spx_dates if date >= bb_date))
        base_spx_date = spx_dates[base_idx]
        base_value = spx_data.iloc[base_idx]['PX_LAST']
        
        returns = {}
        offsets = {'SPX1D': 1, 'SPX3D': 3, 'SPX7D': 7, 'SPX14D': 14}
        
        for label, offset in offsets.items():
            future_idx = base_idx + offset
            if future_idx < len(spx_data):
                future_value = spx_data.iloc[future_idx]['PX_LAST']
                returns[label] = (future_value / base_value) - 1

        # Add control variables to merged df
        controls = {}
        for var, df in control_var_dfs.items():
            control_series = df[df.index <= base_spx_date]['PX_LAST']
            controls[var] = control_series.iloc[-1] if not control_series.empty else np.nan
        
        return pd.Series({**returns, **controls})
    
    results = merged_df['Date'].apply(process_row)
    return pd.concat([merged_df, results], axis=1)

# Print spx returns from merged df
added_df = add_spx_returns_to_merged(spx_data)
print(added_df[['Date', 'SPX1D', 'SPX3D', 'SPX7D', 'SPX14D']].head())
print(added_df)


added_df.to_csv('all_data.csv')

