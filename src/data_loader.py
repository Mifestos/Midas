# src/data_loader.py
import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS

def download_portfolio_data() -> pd.DataFrame:
    """
    Загружает исторические котировки акций из локального CSV-файла,
    полностью заменяя заблокированный yfinance.
    """
    print(f" [Локальный режим] Загрузка данных для портфеля: {PORTFOLIO_TICKERS}")
    
    csv_path = os.path.join(BASE_DIR, "data", "portfolio_prices.csv")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Файл данных не найден по пути: {csv_path}\n"
            f"Пожалуйста, убедитесь, что вы создали папку 'data' в корне и положили туда файл 'portfolio_prices.csv'."
        )
    
    data = pd.read_csv(csv_path, index_col='Date', parse_dates=True)
    
    available_tickers = [ticker for ticker in PORTFOLIO_TICKERS if ticker in data.columns]
    
    if not available_tickers:
        raise ValueError(f"Ни один из тикеров {PORTFOLIO_TICKERS} не найден в CSV-файле.")
        
    cleaned_data = data[available_tickers].dropna()
    
    print(f"Данные успешно загружены локально! Найдено торговых дней: {len(cleaned_data)}")
    return cleaned_data

if __name__ == "__main__":

    try:
        df = download_portfolio_data()
        print("\n🎉 УСПЕХ! Первые 5 строк таблицы котировок:")
        print(df.head())
    except Exception as e:
        print(f"\n❌ Ошибка при вызове функции: {e}")
