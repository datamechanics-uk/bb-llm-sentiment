import pandas as pd
import numpy as np
from sklearn.linear_model import MultiTaskLassoCV
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.paths import Paths

paths = Paths()
csv_data_path = paths.all_data_csv()

# Load and prepare data
data = pd.read_csv(csv_data_path)
data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%Y')
data = data.sort_values('Date')

# Prepare features and targets
llm_models = ["claude35sonnet", "coherecommandrplus", "metallama370b", "mistrallarge2402", "titantextpremier"]
chapters = ["atlanta", "boston", "chicago", "cleveland", "dallas", "kansas_city", "minneapolis", "new_york", "philadelphia", "richmond", "san_francisco", "st_louis", "national_summary"]

X_columns = [f"{chapter}_{model}" for chapter in chapters for model in llm_models]
X_columns += [f"average_{model}" for model in llm_models]  # Add average scores
y_columns = ['SPX1D', 'SPX3D', 'SPX7D', 'SPX14D']

X = data[X_columns]
y = data[y_columns]

# Print some diagnostic information
print("Feature statistics:")
print(X.describe())
print("\nTarget statistics:")
print(y.describe())

# Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Time series cross-validation
tscv = TimeSeriesSplit(n_splits=5)

# MultiTaskLassoCV with time series cross-validation
multi_lasso_cv = MultiTaskLassoCV(cv=tscv, n_alphas=100, max_iter=10000, random_state=42)
multi_lasso_cv.fit(X_scaled, y)

# Evaluate the model
y_pred = multi_lasso_cv.predict(X_scaled)
mse = mean_squared_error(y, y_pred, multioutput='raw_values')
r2 = r2_score(y, y_pred, multioutput='raw_values')

print(f"\nOptimal alpha: {multi_lasso_cv.alpha_}")
for i, target in enumerate(y_columns):
    print(f"\nResults for {target}:")
    print(f"Mean Squared Error: {mse[i]}")
    print(f"R-squared: {r2[i]}")

# Print all coefficients for verification
print("\nAll coefficients:")
for i, target in enumerate(y_columns):
    print(f"\nFor target variable {target}:")
    for feature, coef in zip(X_columns, multi_lasso_cv.coef_[:, i]):
        print(f"  {feature}: {coef}")

# Print non-zero coefficients
print("\nNon-zero coefficients:")
for i, target in enumerate(y_columns):
    print(f"\nFor target variable {target}:")
    for feature, coef in zip(X_columns, multi_lasso_cv.coef_[:, i]):
        if abs(coef) > 1e-5:  # Use a small threshold to account for floating-point precision
            print(f"  {feature}: {coef}")

# Calculate and print annualized Sharpe ratio for each target
print("\nAnnualized Sharpe Ratios:")
for i, target in enumerate(y_columns):
    returns = pd.Series(y_pred[:, i])
    if returns.std() != 0:
        days = int(target[3:].replace('D', ''))  # Strip 'D' and convert to integer
        sharpe_ratio = np.sqrt(252 / days) * returns.mean() / returns.std()
        print(f"{target}: {sharpe_ratio}")
    else:
        print(f"{target}: Cannot calculate (Standard deviation of returns is zero)")

# Create a DataFrame to display the coefficients
coefficients = pd.DataFrame(multi_lasso_cv.coef_.T, index=X_columns, columns=y_columns)
print("\nCoefficients Table:")
print(coefficients)

# Save the coefficients table to a CSV file
coefficients.to_csv('coefficients_table.csv')
print("\nCoefficients table saved to coefficients_table.csv")