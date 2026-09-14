import os
import sys
import pandas as pd
import numpy as np
from scipy.optimize import minimize

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS, RISK_AVERSION, MINIMUM_ALLOCATION, MAXIMUM_ALLOCATION
from src.data_loader import download_portfolio_data
from src.forecasting import forecast_prices, calculate_expected_returns

def calculate_historical_covariance(historical_data: pd.DataFrame) -> pd.DataFrame:
    daily_returns = historical_data.pct_change().dropna()
    cov_matrix = daily_returns.cov() * 252
    return cov_matrix

def optimize_portfolio(expected_returns: pd.Series, cov_matrix: pd.DataFrame) -> pd.Series:
    num_assets = len(PORTFOLIO_TICKERS)
    
    def objective_function(weights):
        portfolio_return = np.sum(expected_returns * weights)
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        utility = portfolio_return - 0.5 * RISK_AVERSION * portfolio_variance
        return -utility

    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1.0})
    bounds = tuple((MINIMUM_ALLOCATION, MAXIMUM_ALLOCATION) for _ in range(num_assets))
    initial_weights = np.array([1.0 / num_assets] * num_assets)
    
    result = minimize(
        fun=objective_function,
        x0=initial_weights,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    optimized_weights = pd.Series(result.x, index=PORTFOLIO_TICKERS)
    return np.round(optimized_weights, 4)

if __name__ == "__main__":
    print("Старт теста оптимизатора Марковица")
    historical_prices = download_portfolio_data()
    print("Расчет ожидаемой доходности через Prophet")
    forecasted_prices = forecast_prices(historical_prices, days_to_forecast=30)
    expected_returns = calculate_expected_returns(historical_prices, forecasted_prices)
    cov_matrix = calculate_historical_covariance(historical_prices)
    weights = optimize_portfolio(expected_returns, cov_matrix)
    
    print("ОПТИМАЛЬНЫЕ ВЕСА ПОРТФЕЛЯ MIDAS:")
    print("-----------------------------------------")
    for ticker, weight in weights.items():
        print(f"Доля {ticker}: {weight * 100:.2f}%")
    print("-----------------------------------------")
    print(f"Проверка суммы весов: {weights.sum() * 100:.1f}%")
