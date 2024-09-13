import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths

paths = Paths()

bb_dates = pd.read_excel(os.path.join(paths.data(), "bb_dates.xlsx"))
bb_dates.columns = bb_dates.columns.str.strip()
for col in ['Year', 'Month', 'Day']:
    bb_dates[col] = bb_dates[col].astype(str).str.strip()

bb_dates['Date'] = pd.to_datetime(bb_dates['Year'] + '-' + bb_dates['Month'] + '-' + bb_dates['Day'], errors='coerce')
bb_dates['YearMonth'] = bb_dates['Date'].dt.to_period('M')

llm_files = ["Claude35Sonnet_scores.csv", "CohereCommandRPlus_scores.csv", "MetaLlama370B_scores.csv", "MistralLarge2402_scores.csv", "TitanTextPremier_scores.csv"]
llm_scores = [pd.read_csv(os.path.join(paths.data(), "llm_scores", file)) for file in llm_files]

for df in llm_scores:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.to_period('M')

all_scores = bb_dates[['Date']].copy()

chapters = ["atlanta", "boston", "chicago", "cleveland", "dallas", "kansas_city", "minneapolis", "new_york", "philadelphia", "richmond", "san_francisco", "st_louis", "national_summary"]

for chapter in chapters:
    combined_scores = []
    for year_month in bb_dates['YearMonth']:
        scores = [
            str(df.loc[df['Date'] == year_month, chapter].values[0])
            if not df.loc[df['Date'] == year_month, chapter].empty else ''
            for df in llm_scores
        ]
        combined_scores.append(', '.join(scores))
    all_scores[chapter] = combined_scores

spx_returns = pd.read_excel(paths.spx_data(), skiprows=6)
spx_returns.columns = spx_returns.columns.str.strip()
spx_returns['Date'] = pd.to_datetime(spx_returns['Date'], errors='coerce')

# Function to find the next available date
def find_next_available_date(df, start_date, days):
    current_date = start_date
    while days >= 0:
        if current_date in df['Date'].values:
            if days == 0:
                return current_date
            days -= 1
        current_date += pd.Timedelta(days=1)
    return None

# Calculate SPX changes
def calculate_spx_changes(df, all_scores):
    spx_changes = {'SPX1D': [], 'SPX3D': [], 'SPX7D': [], 'SPX14D': []}
    for date in all_scores['Date']:
        date_zero = find_next_available_date(df, date, 0)
        if date_zero is not None:
            date_zero_price = df.loc[df['Date'] == date_zero, 'PX_LAST'].values[0]
            for days in [1, 3, 7, 14]:
                target_date = find_next_available_date(df, date_zero, days)
                if target_date is not None:
                    target_price = df.loc[df['Date'] == target_date, 'PX_LAST'].values[0]
                    spx_changes[f'SPX{days}D'].append(target_price - date_zero_price)
                else:
                    spx_changes[f'SPX{days}D'].append(None)
        else:
            spx_changes['SPX1D'].append(None)
            spx_changes['SPX3D'].append(None)
            spx_changes['SPX7D'].append(None)
            spx_changes['SPX14D'].append(None)
    return spx_changes

spx_changes = calculate_spx_changes(spx_returns, all_scores)
all_scores['SPX1D'] = spx_changes['SPX1D']
all_scores['SPX3D'] = spx_changes['SPX3D']
all_scores['SPX7D'] = spx_changes['SPX7D']
all_scores['SPX14D'] = spx_changes['SPX14D']

print(all_scores.head())
all_scores.to_csv(os.path.join(paths.data(), "all_data.csv"), index=False)