# src/settings.py
import os
from datetime import datetime, timedelta
import pandas as pd

# Возвращаем американские тикеры, которые находятся в твоем CSV
PORTFOLIO_TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# Временной интервал (можно оставить текущий или подстроить под CSV)
END_DATE = datetime.today().strftime('%Y-%m-%d')
START_DATE = (datetime.today() - timedelta(days=3*365)).strftime('%Y-%m-%d')

# Параметры оптимизации
RISK_AVERSION = 3
RUN_BACKTEST = True

# Базовые параметры модели CAPM для рынка США (так как акции американские)
MARKET_RETURN = 0.10          # Ожидаемая доходность индекса S&P 500 (~10%)
RISK_FREE_RATE = 0.045        # Безрисковая ставка США (Treasuries ~4.5%)
MARKET_VOLATILITY = 0.16      # Волатильность индекса S&P 500

# --- БЛОК ДЛЯ РАБОТЫ С ЛОКАЛЬНЫМ CSV ---

# Автоматически находим путь к файлу данных в проекте
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "src", "data", "portfolio_prices.csv")

def load_local_data() -> pd.DataFrame:
    """Загружает исторические данные по американским акциям из локального CSV-файла."""
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Критическая ошибка: Файл не найден по пути {CSV_PATH}\n"
            f"Пожалуйста, убедись, что файл лежит в src/data/portfolio_prices.csv"
        )
    
    # Читаем CSV, делая колонку Date индексом
    df = pd.read_csv(CSV_PATH, index_col='Date', parse_dates=True)
    return df.sort_index()
