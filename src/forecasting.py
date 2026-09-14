# src/forecasting.py
import os
import sys
import pandas as pd
from prophet import Prophet

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS

def forecast_prices(data: pd.DataFrame, days_to_forecast: int = 30) -> pd.DataFrame:
    predictions = {}
    for ticker in PORTFOLIO_TICKERS:
        print(f"Обучение модели Prophet для тикера: {ticker}")
        df_ticker = data[[ticker]].reset_index()
        df_ticker.columns = ['ds', 'y']
        df_ticker['ds'] = df_ticker['ds'].dt.tz_localize(None)
        
        model = Prophet(daily_seasonality=False, yearly_seasonality=True, weekly_seasonality=True)
        model.fit(df_ticker)
        
        future = model.make_future_dataframe(periods=days_to_forecast, freq='B') 
        forecast = model.predict(future)
        predictions[ticker] = forecast.set_index('ds')['yhat']
        
    return pd.DataFrame(predictions)

def calculate_expected_returns(historical_data: pd.DataFrame, forecast_data: pd.DataFrame) -> pd.Series:
    expected_returns = {}
    for ticker in PORTFOLIO_TICKERS:
        last_real_price = historical_data[ticker].iloc[-1]
        last_predicted_price = forecast_data[ticker].iloc[-1]
        expected_returns[ticker] = (last_predicted_price / last_real_price) - 1
    return pd.Series(expected_returns)

if __name__ == "__main__":
    from src.data_loader import download_portfolio_data
    print("Старт изолированного теста Prophet")
    df_prices = download_portfolio_data()
    df_forecast = forecast_prices(df_prices, days_to_forecast=30)
    print("Ожидаемая доходность по прогнозу Prophet:")
    print(calculate_expected_returns(df_prices, df_forecast))
