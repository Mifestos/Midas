# src/settings.py
from datetime import datetime, timedelta

# Список акций для портфеля 
PORTFOLIO_TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# Период исторических данных за последние 3 года
END_DATE = datetime.today().strftime('%Y-%m-%d')
START_DATE = (datetime.today() - timedelta(days=3*365)).strftime('%Y-%m-%d')

# Параметры оптимизации Марковица
RISK_AVERSION = 3
MINIMUM_ALLOCATION = 0.05
MAXIMUM_ALLOCATION = 0.35