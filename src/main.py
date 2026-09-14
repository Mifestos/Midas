# src/main.py
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS
from src.data_loader import download_portfolio_data
from src.forecasting import forecast_prices, calculate_expected_returns
from src.portfolio_optimisation import calculate_historical_covariance, optimize_portfolio

def run_pipeline():
    print(f"ЗАПУСК ИНВЕСТИЦИОННОЙ СИСТЕМЫ MIDAS | {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    print("Чтение исторических рыночных данных")
    try:
        historical_prices = download_portfolio_data()
    except Exception as e:
        print(f"Ошибка на этапе загрузки данных: {e}")
        return

    print("Запуск ИИ-модели Prophet (генерация прогнозов на 30 дней)")
    try:
        forecasted_prices = forecast_prices(historical_prices, days_to_forecast=30)
        expected_returns = calculate_expected_returns(historical_prices, forecasted_prices)
    except Exception as e:
        print(f"Ошибка на этапе прогнозирования Prophet: {e}")
        return

    print("Квадратичная оптимизация портфеля Марковица")
    try:
        cov_matrix = calculate_historical_covariance(historical_prices)
        optimized_weights = optimize_portfolio(expected_returns, cov_matrix)
    except Exception as e:
        print(f"Ошибка на этапе оптимизации: {e}")
        return

    print("ФИНАЛЬНЫЙ СГЕНЕРИРОВАННЫЙ ОТЧЕТ ПОРТФЕЛЯ MIDAS")
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
