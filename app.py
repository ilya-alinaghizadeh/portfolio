import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Portfolio Optimization Dashboard",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# Dashboard Header
# ============================================================

st.title("📈 Portfolio Optimization & Risk Analysis")

st.markdown(
    """
    **Interactive investment analytics dashboard**

    Analyze historical asset performance, construct custom portfolios,
    evaluate risk-adjusted returns, and compare portfolio strategies.
    """
)

st.info(
    "Historical analysis only. Past performance does not guarantee future results."
)


# ============================================================
# Asset Universe
# ============================================================

assets = {
    "SPY": "US Equities",
    "EFA": "International Equities",
    "IEF": "US Treasury Bonds",
    "GLD": "Gold",
    "VNQ": "Real Estate"
}

tickers = list(assets.keys())


# ============================================================
# Download Market Data
# ============================================================

prices = yf.download(
    tickers,
    start="2019-01-01",
    end="2026-01-01",
    auto_adjust=True
)["Close"]

returns = prices.pct_change().dropna()


# ============================================================
# Sidebar Controls
# ============================================================

with st.sidebar:

    st.header("Dashboard Controls")

    selected_asset = st.selectbox(
        "Select an asset",
        tickers
    )

    date_range = st.slider(
        "Select date range",
        min_value=prices.index.min().date(),
        max_value=prices.index.max().date(),
        value=(
            prices.index.min().date(),
            prices.index.max().date()
        )
    )

    st.subheader("Portfolio Weights")

    spy_weight = st.slider(
        "SPY",
        0.0, 1.0, 0.20, 0.05
    )

    efa_weight = st.slider(
        "EFA",
        0.0, 1.0, 0.20, 0.05
    )

    ief_weight = st.slider(
        "IEF",
        0.0, 1.0, 0.20, 0.05
    )

    gld_weight = st.slider(
        "GLD",
        0.0, 1.0, 0.20, 0.05
    )

    vnq_weight = st.slider(
        "VNQ",
        0.0, 1.0, 0.20, 0.05
    )

    custom_weights = np.array([
        spy_weight,
        efa_weight,
        ief_weight,
        gld_weight,
        vnq_weight
    ])

    total_weight = custom_weights.sum()

    st.write(f"Total Weight: {total_weight:.0%}")

    if total_weight > 0:
        normalized_weights = custom_weights / total_weight
    else:
        normalized_weights = np.array([
            0.2, 0.2, 0.2, 0.2, 0.2
        ])


# ============================================================
# Filtered Price Data
# ============================================================

filtered_prices = prices.loc[
    (prices.index.date >= date_range[0]) &
    (prices.index.date <= date_range[1])
]


# ============================================================
# Asset Universe
# ============================================================

st.divider()

st.subheader("Asset Universe")

st.dataframe(
    pd.DataFrame({
        "Ticker": tickers,
        "Asset Class": [assets[ticker] for ticker in tickers]
    }),
    use_container_width=True
)


# ============================================================
# Asset Price Chart
# ============================================================

st.divider()

st.subheader(f"{selected_asset} Price History")

fig_price = px.line(
    filtered_prices,
    x=filtered_prices.index,
    y=selected_asset,
    title=f"{selected_asset} Price History"
)

fig_price.update_layout(
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified"
)

st.plotly_chart(
    fig_price,
    use_container_width=True
)


# ============================================================
# Individual Asset Risk Metrics
# ============================================================

annual_returns = returns.mean() * 252
annual_volatility = returns.std() * np.sqrt(252)
sharpe_ratios = annual_returns / annual_volatility

cumulative_returns = (1 + returns).cumprod()
running_max = cumulative_returns.cummax()
drawdown = cumulative_returns / running_max - 1
max_drawdown = drawdown.min()


st.divider()

st.subheader(f"{selected_asset} Risk Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Annual Return",
    f"{annual_returns[selected_asset]:.2%}"
)

col2.metric(
    "Annual Volatility",
    f"{annual_volatility[selected_asset]:.2%}"
)

col3.metric(
    "Sharpe Ratio",
    f"{sharpe_ratios[selected_asset]:.2f}"
)

col4.metric(
    "Max Drawdown",
    f"{max_drawdown[selected_asset]:.2%}"
)


# ============================================================
# Optimized Portfolio
# ============================================================

st.divider()

st.subheader("Optimized Portfolio Allocation")

# Historical constrained optimization result
optimized_weights = pd.Series(
    [0.00, 0.40, 0.20, 0.40, 0.00],
    index=tickers
)

allocation_df = pd.DataFrame({
    "Asset": optimized_weights.index,
    "Weight": optimized_weights.values
})

fig_allocation = px.pie(
    allocation_df,
    names="Asset",
    values="Weight",
    title="Constrained Optimized Portfolio"
)

fig_allocation.update_traces(
    textinfo="percent+label"
)

st.plotly_chart(
    fig_allocation,
    use_container_width=True
)


# ============================================================
# Custom Portfolio
# ============================================================

st.divider()

st.subheader("Custom Portfolio Allocation")

custom_allocation = pd.DataFrame({
    "Asset": tickers,
    "Weight": normalized_weights
})

fig_custom_allocation = px.pie(
    custom_allocation,
    names="Asset",
    values="Weight",
    title="Your Portfolio Allocation"
)

fig_custom_allocation.update_traces(
    textinfo="percent+label"
)

st.plotly_chart(
    fig_custom_allocation,
    use_container_width=True
)


# ============================================================
# Portfolio Returns
# ============================================================

custom_portfolio_returns = returns @ normalized_weights

weights_spy = np.array([1, 0, 0, 0, 0])

weights_60_40 = np.array([
    0.6, 0.0, 0.4, 0.0, 0.0
])

weights_equal = np.array([
    0.2, 0.2, 0.2, 0.2, 0.2
])

optimized_returns = returns @ optimized_weights
spy_returns = returns @ weights_spy
returns_60_40 = returns @ weights_60_40
equal_returns = returns @ weights_equal

portfolio_returns = pd.DataFrame({
    "Custom Portfolio": custom_portfolio_returns,
    "Optimized": optimized_returns,
    "SPY": spy_returns,
    "60/40": returns_60_40,
    "Equal Weight": equal_returns
})


# ============================================================
# Filter Portfolio Returns by Selected Date Range
# ============================================================

filtered_portfolio_returns = portfolio_returns.loc[
    (portfolio_returns.index.date >= date_range[0]) &
    (portfolio_returns.index.date <= date_range[1])
]


# ============================================================
# Custom Portfolio Analysis
# ============================================================

st.divider()

st.subheader("Custom Portfolio Analysis")

custom_annual_return = (
    filtered_portfolio_returns["Custom Portfolio"].mean() * 252
)

custom_annual_volatility = (
    filtered_portfolio_returns["Custom Portfolio"].std() * np.sqrt(252)
)

custom_sharpe = (
    custom_annual_return / custom_annual_volatility
)

custom_cumulative = (
    1 + filtered_portfolio_returns["Custom Portfolio"]
).cumprod()

custom_running_max = custom_cumulative.cummax()

custom_drawdown = (
    custom_cumulative / custom_running_max - 1
)

custom_max_drawdown = custom_drawdown.min()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Annual Return",
    f"{custom_annual_return:.2%}"
)

col2.metric(
    "Annual Volatility",
    f"{custom_annual_volatility:.2%}"
)

col3.metric(
    "Sharpe Ratio",
    f"{custom_sharpe:.2f}"
)

col4.metric(
    "Max Drawdown",
    f"{custom_max_drawdown:.2%}"
)


# ============================================================
# Portfolio Growth Comparison
# ============================================================

st.divider()

st.subheader("Portfolio Growth Comparison")

growth = (
    1 + filtered_portfolio_returns
).cumprod()

fig_growth = px.line(
    growth,
    x=growth.index,
    y=growth.columns,
    title="Growth of €1"
)

fig_growth.update_layout(
    xaxis_title="Date",
    yaxis_title="Portfolio Value",
    hovermode="x unified"
)

st.plotly_chart(
    fig_growth,
    use_container_width=True
)


# ============================================================
# Portfolio Performance Comparison
# ============================================================

st.divider()

st.subheader("Portfolio Performance Comparison")

portfolio_annual_returns = (
    filtered_portfolio_returns.mean() * 252
)

portfolio_volatility = (
    filtered_portfolio_returns.std() * np.sqrt(252)
)

portfolio_sharpe = (
    portfolio_annual_returns / portfolio_volatility
)

portfolio_cumulative = (
    1 + filtered_portfolio_returns
).cumprod()

portfolio_running_max = (
    portfolio_cumulative.cummax()
)

portfolio_drawdown = (
    portfolio_cumulative / portfolio_running_max - 1
)

portfolio_max_drawdown = portfolio_drawdown.min()

portfolio_metrics = pd.DataFrame({
    "Annual Return": portfolio_annual_returns,
    "Annual Volatility": portfolio_volatility,
    "Sharpe Ratio": portfolio_sharpe,
    "Max Drawdown": portfolio_max_drawdown
})

st.dataframe(
    portfolio_metrics.style.format({
        "Annual Return": "{:.2%}",
        "Annual Volatility": "{:.2%}",
        "Sharpe Ratio": "{:.2f}",
        "Max Drawdown": "{:.2%}"
    }),
    use_container_width=True
)


# ============================================================
# Risk-Return Comparison
# ============================================================

st.divider()

st.subheader("Risk-Return Comparison")

risk_return_df = pd.DataFrame({
    "Portfolio": portfolio_annual_returns.index,
    "Return": portfolio_annual_returns.values,
    "Volatility": portfolio_volatility.values,
    "Sharpe": portfolio_sharpe.values
})

fig_risk_return = px.scatter(
    risk_return_df,
    x="Volatility",
    y="Return",
    text="Portfolio",
    size="Sharpe",
    title="Portfolio Risk vs. Return",
    hover_data=["Sharpe"]
)

fig_risk_return.update_traces(
    textposition="top center"
)

fig_risk_return.update_layout(
    xaxis_title="Annual Volatility",
    yaxis_title="Annual Return"
)

st.plotly_chart(
    fig_risk_return,
    use_container_width=True
)


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "Built with Python, Streamlit, Pandas, NumPy, Plotly, SciPy and yfinance. "
    "Developed with AI-assisted guidance for coding and project development. "
    "Portfolio optimization uses historical market data and a constrained "
    "mean-variance framework. Results are for educational purposes only."
)
