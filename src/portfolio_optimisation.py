import os
import sys
import pandas as pd
import numpy as np
from scipy.optimize import minimize

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS
from src.data_loader import download_portfolio_data
from src.forecasting import forecast_prices, calculate_expected_returns

def calculate_historical_covariance(historical_data: pd.DataFrame) -> pd.DataFrame:
    daily_returns = historical_data.pct_change().dropna()
    cov_matrix = daily_returns.cov() * 252
    return cov_matrix

def optimize_portfolio(expected_returns: pd.Series, cov_matrix: pd.DataFrame, risk_aversion: float, min_bounds: np.array, max_bounds: np.array) -> pd.Series:
    num_assets = len(PORTFOLIO_TICKERS)
    
    def objective_function(weights):
        portfolio_return = np.sum(expected_returns * weights)
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        utility = portfolio_return - 0.5 * risk_aversion * portfolio_variance
        return -utility

    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1.0})
    bounds = tuple((min_bounds[i], max_bounds[i]) for i in range(num_assets))
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
