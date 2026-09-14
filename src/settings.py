# src/settings.py
from datetime import datetime, timedelta

# Задаем российские тикеры (акции)
PORTFOLIO_TICKERS = ["SBER", "GAZP", "LKOH", "YDEX", "ROSN"]

# Временной интервал (за последние 3 года)
END_DATE = datetime.today().strftime('%Y-%m-%d')
START_DATE = (datetime.today() - timedelta(days=3*365)).strftime('%Y-%m-%d')

# Параметры оптимизации
RISK_AVERSION = 3
RUN_BACKTEST = True

# Базовые параметры модели CAPM для рынка РФ (для автоматического расчета лимитов)
MARKET_RETURN = 0.15          # Ожидаемая доходность Индекса Мосбиржи
RISK_FREE_RATE = 0.18         # Текущая высокая безрисковая ставка (ОФЗ/ключевая)
MARKET_VOLATILITY = 0.22      # Волатильность индекса Мосбиржи
