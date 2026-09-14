# src/backtest.py
import os
import sys
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS
from src.data_loader import download_portfolio_data
from src.forecasting import forecast_prices, calculate_expected_returns
from src.portfolio_optimisation import calculate_historical_covariance, optimize_portfolio

def run_backtest(days_back: int = 30):
    print("ЗАПУСК ИСТОРИЧЕСКОГО БЭКТЕСТИНГА ПОРТФЕЛЯ MIDAS")
    full_data = download_portfolio_data()
    
    train_data = full_data.iloc[:-days_back]
    test_data = full_data.iloc[-days_back:]
    
    print(f"Размер обучающей выборки: {len(train_data)} дней")
    print(f"Размер тестовой проверки: {len(test_data)} дней")
    
    print("Шаг 1: Обучение Prophet на исторических данных")
    forecasted_prices = forecast_prices(train_data, days_to_forecast=days_back)
    expected_returns = calculate_expected_returns(train_data, forecasted_prices)
    
    print("Шаг 2: Расчет ковариации и оптимизация Марковица")
    cov_matrix = calculate_historical_covariance(train_data)
    midas_weights = optimize_portfolio(expected_returns, cov_matrix)
    
    real_asset_returns = (test_data.iloc[-1] / train_data.iloc[-1]) - 1
    midas_portfolio_return = np.sum(real_asset_returns * midas_weights)
    
    equal_weights = np.array([1.0 / len(PORTFOLIO_TICKERS)] * len(PORTFOLIO_TICKERS))
    benchmark_return = np.sum(real_asset_returns * equal_weights)
    
    print("СРАВНИТЕЛЬНЫЙ АНАЛИТИЧЕСКИЙ ОТЧЕТ БЭКТЕСТА")
    print("-" * 60)
    print(f"РЕАЛЬНАЯ ДОХОДНОСТЬ ПОРТФЕЛЯ MIDAS:   {midas_portfolio_return * 100:+.2f}%")
    print(f"ДОХОДНОСТЬ СТРАТЕГИИ БЕНЧМАРКА (Рынок): {benchmark_return * 100:+.2f}%")
    print("-" * 60)

    
    alpha = (midas_portfolio_return - benchmark_return) * 100
    if alpha > 0:
        print(f"Результат: Модель Midas ОБЫГРАЛА рынок на {alpha:.2f}% за счет ИИ-прогнозов")
    else:
        print(f"Результат: В этот раз рынок оказался сильнее на {abs(alpha):.2f}%")

if __name__ == "__main__":
    run_backtest(days_back=30)
