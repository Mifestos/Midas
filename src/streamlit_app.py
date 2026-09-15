# src/streamlit_app.py
import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.settings import PORTFOLIO_TICKERS, MARKET_RETURN, RISK_FREE_RATE, MARKET_VOLATILITY
from src.settings import load_local_data
from src.forecasting import forecast_prices, calculate_expected_returns
from src.portfolio_optimisation import calculate_historical_covariance, optimize_portfolio

st.set_page_config(page_title="Midas Portfolio Asset Allocation", layout="wide")
st.title("Midas Portfolio Asset Allocation")

st.sidebar.header("Параметры системы")
run_backtest = st.sidebar.checkbox("Включить режим бэктестинга", value=True)

st.sidebar.subheader("Настройка риска")
risk_mode = st.sidebar.selectbox("Расчет неприятия риска (γ)", ["Ручной ползунок", "Математический CAPM"])

if risk_mode == "Ручной ползунок":
    risk_aversion = st.sidebar.slider("Неприятие риска (Risk Aversion)", 1.0, 5.0, 3.0, 0.5)
else:
    # Защита от отрицательного или нулевого значения из-за аномалий рынка (например, RISK_FREE_RATE > MARKET_RETURN)
    gamma_capm = (MARKET_RETURN - RISK_FREE_RATE) / (MARKET_VOLATILITY ** 2)
    if gamma_capm <= 0:
        gamma_capm = 3.0  # Безопасный дефолт, если безрисковая ставка выше доходности рынка
    
    st.sidebar.metric("Рассчитанный γ (CAPM)", f"{gamma_capm:.2f}")
    risk_aversion = gamma_capm

st.sidebar.subheader("Стратегия риск-лимитов")
allocation_strategy = st.sidebar.selectbox(
    "Выберите стратегию лимитов", 
    ["Без лимитов (0% - 100%)", "Равномерный лимит (1/N)", "Предельный вклад в риск"]
)

historical_prices = load_local_data()
cov_matrix = calculate_historical_covariance(historical_prices)
num_assets = len(PORTFOLIO_TICKERS)

min_bounds = np.zeros(num_assets)
max_bounds = np.ones(num_assets)

if allocation_strategy == "Равномерный лимит (1/N)":
    equal_weight = 1.0 / num_assets
    min_bounds = np.full(num_assets, equal_weight * 0.25)
    max_bounds = np.full(num_assets, equal_weight * 1.75)
elif allocation_strategy == "Предельный вклад в риск":
    asset_vols = np.sqrt(np.diag(cov_matrix))
    total_vol = np.sum(asset_vols)
    for i in range(num_assets):
        risk_share = asset_vols[i] / total_vol
        if risk_share > 0.25:
            max_bounds[i] = 0.20
            min_bounds[i] = 0.02
        else:
            max_bounds[i] = 0.45
            min_bounds[i] = 0.05

st.sidebar.subheader("Текущие лимиты активов")
limits_data = []
for i, ticker in enumerate(PORTFOLIO_TICKERS):
    limits_data.append([ticker, f"{min_bounds[i]*100:.1f}%", f"{max_bounds[i]*100:.1f}%"])
df_limits = pd.DataFrame(limits_data, columns=["Актив", "Мин. вес", "Макс. вес"])
st.sidebar.dataframe(df_limits, hide_index=True)

days_to_forecast = 30

if run_backtest:
    st.subheader("Режим работы: Исторический бэктестинг")
    train_data = historical_prices.iloc[:-days_to_forecast]
    test_data = historical_prices.iloc[-days_to_forecast:]
    
    forecasted_prices = forecast_prices(train_data, days_to_forecast=days_to_forecast)
    expected_returns = calculate_expected_returns(train_data, forecasted_prices)
    cov_matrix_train = calculate_historical_covariance(train_data)
    
    # Исправлено: Явное приведение np.array к спискам .tolist() для корректной распаковки в цикле функции
    optimized_weights = optimize_portfolio(
        expected_returns, 
        cov_matrix_train, 
        risk_aversion, 
        min_bounds.tolist(), 
        max_bounds.tolist()
    )
    
    real_asset_returns = (test_data.iloc[-1] / train_data.iloc[-1]) - 1
    midas_return = np.sum(real_asset_returns * optimized_weights)
    benchmark_return = np.sum(real_asset_returns * (1.0 / num_assets))
    
    col1, col2 = st.columns(2)
    col1.metric("Доходность Midas (ИИ)", f"{midas_return * 100:+.2f}%")
    col2.metric("Доходность Бенчмарка (Рынок)", f"{benchmark_return * 100:+.2f}%")
    
    accuracy_data = []
    for ticker in PORTFOLIO_TICKERS:
        last_price = train_data[ticker].iloc[-1]
        pred_price = forecasted_prices[ticker].iloc[-1]
        real_price = test_data[ticker].iloc[-1]
        error = ((pred_price - real_price) / real_price) * 100
        accuracy_data.append([ticker, f"${last_price:.2f}", f"${pred_price:.2f}", f"${real_price:.2f}", f"{error:+.2f}%"])
        
    df_accuracy = pd.DataFrame(accuracy_data, columns=["Тикер", "Последняя цена", "Прогноз Prophet", "Реальная цена", "Ошибка (%)"])
    st.dataframe(df_accuracy, use_container_width=True)

else:
    st.subheader("Режим работы: Реальное прогнозирование")
    forecasted_prices = forecast_prices(historical_prices, days_to_forecast=days_to_forecast)
    expected_returns = calculate_expected_returns(historical_prices, forecasted_prices)
    
    # Исправлено: Явное приведение np.array к спискам .tolist() для корректной распаковки в цикле функции
    optimized_weights = optimize_portfolio(
        expected_returns, 
        cov_matrix, 
        risk_aversion, 
        min_bounds.tolist(), 
        max_bounds.tolist()
    )
    
    report_data = []
    for ticker in PORTFOLIO_TICKERS:
        ret = expected_returns[ticker] * 100
        weight = optimized_weights[ticker] * 100
        ret_str = f"+{ret:.2f}%" if ret > 0 else f"{ret:.2f}%"
        report_data.append([ticker, ret_str, f"{weight:.2f}%"])
        
    df_report = pd.DataFrame(report_data, columns=["Тикер", "Прогноз Prophet (30д)", "Рекомендуемая доля"])
    st.dataframe(df_report, use_container_width=True)

st.subheader("Оптимальное распределение весов портфеля")
fig_pie = go.Figure(data=[go.Pie(
    labels=list(optimized_weights.index), 
    values=list(optimized_weights.values), 
    hole=.3,
    textinfo='label+percent',
    insidetextorientation='radial'
)])
fig_pie.update_layout(margin=dict(t=30, b=30, l=30, r=30))
st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("Визуальный анализ трендов и прогнозов")
forecast_img_path = o   s.path.join(BASE_DIR, "src", "plots", "portfolio_forecasts.png")
if os.path.exists(forecast_img_path):
    st.image(forecast_img_path, use_container_width=True)
