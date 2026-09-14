# src/data_loader.py
import os
import sys
import requests
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS, START_DATE, END_DATE

def get_moex_candles(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    all_candles = []
    start_index = 0
    url = f"https://moex.com{ticker}.json"
    
    while True:
        params = {
            'from': start_date,
            'till': end_date,
            'start': start_index,
            'history_columns': 'TRADEDATE,CLOSE'
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ConnectionError(f"Ошибка подключения к MOEX ISS для тикера {ticker}")
            
        data = response.json()
        rows = data['history']['data']
        if not rows:
            break
            
        all_candles.extend(rows)
        start_index += 100 
        
    df = pd.DataFrame(all_candles, columns=['Date', ticker])
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df

def download_portfolio_data() -> pd.DataFrame:
    print(f"Загрузка реальных исторических данных с Московской Биржи для: {PORTFOLIO_TICKERS}")
    portfolio_frames = []
    for ticker in PORTFOLIO_TICKERS:
        try:
            print(f"Запрос истории для {ticker}...")
            df_ticker = get_moex_candles(ticker, START_DATE, END_DATE)
            portfolio_frames.append(df_ticker)
        except Exception as e:
            print(f"Не удалось загрузить данные для {ticker}: {e}")
            
    if not portfolio_frames:
        raise ValueError("Не удалось загрузить данные ни по одному тикеру РФ.")
        
    combined_data = pd.concat(portfolio_frames, axis=1, join='inner')
    combined_data = combined_data.dropna()
    
    csv_dir = os.path.join(BASE_DIR, "src", "data")
    os.makedirs(csv_dir, exist_ok=True)
    combined_data.to_csv(os.path.join(csv_dir, "portfolio_prices.csv"))
    
    print(f"Данные успешно обновлены с MOEX! Торговых дней: {len(combined_data)}")
    return combined_data

if __name__ == "__main__":
    df = download_portfolio_data()
    print(df.head())
