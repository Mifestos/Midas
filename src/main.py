# src/main.py
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS, RUN_BACKTEST
from src.data_loader import download_portfolio_data
from src.forecasting import forecast_prices, calculate_expected_returns
from src.portfolio_optimisation import calculate_historical_covariance, optimize_portfolio

def run_pipeline():
    print(f"ЗАПУСК ИНВЕСТИЦИОННОЙ СИСТЕМЫ MIDAS | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    try:
        full_data = download_portfolio_data()
    except Exception as e:
        print(f"Ошибка на этапе загрузки данных: {e}")
        return

    days_to_forecast = 30

    if RUN_BACKTEST:
        print("РЕЖИМ РАБОТЫ: ИСТОРИЧЕСКИЙ БЭКТЕСТИНГ (СРАВНЕНИЕ С РЕАЛЬНЫМ БУДУЩИМ)")
        train_data = full_data.iloc[:-days_to_forecast]
        test_data = full_data.iloc[-days_to_forecast:]
        
        print(f"Размер обучающей выборки: {len(train_data)} дней")
        print(f"Размер тестовой проверки: {len(test_data)} дней")
        print(f"Период проверки: с {test_data.index[0].strftime('%Y-%m-%d')} по {test_data.index[-1].strftime('%Y-%m-%d')}")
        print("-" * 85)
        
        forecasted_prices = forecast_prices(train_data, days_to_forecast=days_to_forecast)
        expected_returns = calculate_expected_returns(train_data, forecasted_prices)
        cov_matrix = calculate_historical_covariance(train_data)
        optimized_weights = optimize_portfolio(expected_returns, cov_matrix)
        
        real_asset_returns = (test_data.iloc[-1] / train_data.iloc[-1]) - 1
        midas_portfolio_return = np.sum(real_asset_returns * optimized_weights)
        
        equal_weights = np.array([1.0 / len(PORTFOLIO_TICKERS)] * len(PORTFOLIO_TICKERS))
        benchmark_return = np.sum(real_asset_returns * equal_weights)
        
        print("\nАНАЛИЗ ТОЧНОСТИ ПРОГНОЗИРОВАНИЯ ЦЕН ЦЕЛЬНОГО ПЕРИОДА")
        print("-" * 85)
        print(f"{'Тикер':<10} | {'Последняя цена':<15} | {'Прогноз Prophet':<15} | {'Реальная цена':<15} | {'Ошибка (%)':<12}")
        print("-" * 85)
        
        for ticker in PORTFOLIO_TICKERS:
            last_train_price = train_data[ticker].iloc[-1]
            predicted_price = forecasted_prices[ticker].iloc[-1]
            real_price = test_data[ticker].iloc[-1]
            error_pct = ((predicted_price - real_price) / real_price) * 100
            print(f"{ticker:<10} | {last_train_price:<15.2f} | {predicted_price:<15.2f} | {real_price:<15.2f} | {error_pct:<+12.2f}%")
        
        print("-" * 85)
        print("СРАВНИТЕЛЬНЫЙ АНАЛИТИЧЕСКИЙ ОТЧЕТ ЭФФЕКТИВНОСТИ ПОРТФЕЛЯ")
        print("-" * 85)
        print(f"РЕАЛЬНАЯ ДОХОДНОСТЬ ПОРТФЕЛЯ MIDAS:   {midas_portfolio_return * 100:+.2f}%")
        print(f"ДОХОДНОСТЬ СТРАТЕГИИ БЕНЧМАРКА (Рынок): {benchmark_return * 100:+.2f}%")
        print("-" * 85)
        
        alpha = (midas_portfolio_return - benchmark_return) * 100
        if alpha > 0:
            print(f"Результат: Модель Midas ОБЫГРАЛА рынок на {alpha:.2f}% за счет ИИ-прогнозов")
        else:
            print(f"Результат: В этот раз рынок оказался сильнее на {abs(alpha):.2f}%")
        print("-" * 85)

    else:
        print("РЕЖИМ РАБОТЫ: РЕАЛЬНОЕ ПРОГНОЗИРОВАНИЕ (БОЕВОЙ ВЫГЛЯД В БУДУЩЕЕ)")
        print("-" * 85)
        
        forecasted_prices = forecast_prices(full_data, days_to_forecast=days_to_forecast)
        expected_returns = calculate_expected_returns(full_data, forecasted_prices)
        cov_matrix = calculate_historical_covariance(full_data)
        optimized_weights = optimize_portfolio(expected_returns, cov_matrix)
        
        print("\nФИНАЛЬНЫЙ СГЕНЕРИРОВАННЫЙ ОТЧЕТ ПОРТФЕЛЯ MIDAS")
        print(f"Активные тикеры в анализе: {PORTFOLIO_TICKERS}")
        print("-" * 60)
        print(f"{'Тикер':<10} | {'Прогноз Prophet (30д)':<22} | {'Рекомендуемая доля':<18}")
        print("-" * 60)
        
        for ticker in PORTFOLIO_TICKERS:
            ret = expected_returns[ticker] * 100
            weight = optimized_weights[ticker] * 100
            ret_str = f"+{ret:.2f}%" if ret > 0 else f"{ret:.2f}%"
            weight_str = f"{weight:.2f}%"
            print(f"{ticker:<10} | {ret_str:<22} | {weight_str:<18}")
            
        print("-" * 60)
        print(f"Итоговая сумма весов: {optimized_weights.sum() * 100:.1f}%")

if __name__ == "__main__":
    run_pipeline()
