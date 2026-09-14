import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS, RUN_BACKTEST
from src.data_loader import download_portfolio_data
from src.forecasting import forecast_prices

def plot_ticker_forecasts(historical_data: pd.DataFrame, days_back: int = 30):
    num_tickers = len(PORTFOLIO_TICKERS)
    fig, axes = plt.subplots(num_tickers, 1, figsize=(12, 3 * num_tickers))
    
    if num_tickers == 1:
        axes = [axes]
        
    if RUN_BACKTEST:
        train_data = historical_data.iloc[:-days_back]
        test_data = historical_data.iloc[-days_back:]
        forecast_data = forecast_prices(train_data, days_to_forecast=days_back)
    else:
        train_data = historical_data
        forecast_data = forecast_prices(historical_data, days_to_forecast=days_back)
        
    for i, ticker in enumerate(PORTFOLIO_TICKERS):
        ax = axes[i]
        
        hist_series = train_data[ticker]
        ax.plot(hist_series.index, hist_series.values, label="История обучения", color="blue", lw=1.5)
        
        fore_series = forecast_data[ticker]
        future_series = fore_series[fore_series.index > hist_series.index[-1]]
        ax.plot(future_series.index, future_series.values, label="Прогноз Prophet", color="red", lw=2, linestyle="--")
        
        if RUN_BACKTEST:
            real_future_series = test_data[ticker]
            ax.plot(real_future_series.index, real_future_series.values, label="Реальный факт рынка", color="green", lw=1.5, alpha=0.8)
            ax.set_title(f"Бэктест: Сравнение прогноза и реальности для {ticker}")
        else:
            ax.set_title(f"Боевой прогноз будущего для {ticker}")
            
        ax.set_ylabel("Цена ($)")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper left")
        
    plt.tight_layout()
    
    plots_dir = os.path.join(BASE_DIR, "src", "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    save_path = os.path.join(plots_dir, "portfolio_forecasts.png")
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"График сохранен по пути: {save_path}")

if __name__ == "__main__":
    print("Запуск модуля визуализации графиков")
    historical_prices = download_portfolio_data()
    plot_ticker_forecasts(historical_prices, days_back=30)
