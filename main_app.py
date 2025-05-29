import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from app.data_loader import load_sample_returns
from app.backtesting import backtest_portfolio
from app.portfolio_model import build_portfolio, portfolio_volatility
from app.scorecard import generate_scorecard

# This adds a single password gate to access the app.
#def login():
#    st.title("Login")
#    password = st.text_input("Enter password:", type="password")
#    if password == st.secrets["app_password"]:
#        st.session_state["authenticated"] = True
#        st.rerun()
#    elif password:
#        st.error("Incorrect password.")

# Protect the app
#if "authenticated" not in st.session_state:
#    login()
#elif not st.session_state["authenticated"]:
#    login()
#else:

# The rest of your app goes here

# Load current scores CSV once at startup
score_df = pd.read_csv("data/current_scores.csv", sep=',')
score_df.columns = score_df.columns.str.strip()

def load_sample_returns():
    df = pd.read_csv("data/sample_returns.csv", parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    return df

# Title
st.title("Portfolio Builder")
st.write("Design your suite of model portfolios based on your specifications. " \
"Select stocks, bonds, and ETFs.")
# User inputs
client_name = st.text_input("Enter Client Name")
risk_level = st.select_slider("Select Risk Level", options=["Low", "Medium", "High"])

max_stocks = st.number_input("Max Number of Stocks in Portfolio", min_value=10, max_value=100, value=50, step=5)



# Asset Allocation Preferences
st.subheader("Asset Allocation Preferences")

DEFAULT_ALLOCATION = {
"CdnEquity": 0.3,
"UsEquity": 0.3,
"IntEquity": 0.2,
"CoreIncome": 0.1,
"EnhancedIncome": 0.1
}

asset_classes = list(DEFAULT_ALLOCATION.keys())
alloc_inputs = {}

for asset in asset_classes:
    alloc_inputs[asset] = st.slider(
        f"{asset} Allocation (%)", min_value=0, max_value=100,
        value=int(DEFAULT_ALLOCATION[asset]*100),
        step=5
)

# Normalize to sum to 1
total = sum(alloc_inputs.values())
alloc_normalized = {k: v / total for k, v in alloc_inputs.items()}



# Style tilts and portfolio constraints
st.subheader("Customize Portfolio")
tilt = st.selectbox("Select Style Tilt", options=["None", "Value", "Growth", "Quality", "Momentum"])
max_sector_exposure = st.slider(
"Max Sector Exposure (%)", min_value=10, max_value=100, value=30
) / 100.0  # Convert to decimal



if st.button("Generate Portfolio", key="button_top"):

    #st.write("Score DF columns:", score_df.columns.tolist())
    #st.write(score_df.head())

    portfolio = build_portfolio(
        risk_level, 
        max_stocks, 
        tilt, 
        max_sector_exposure,
        score_df=score_df,
        asset_allocation=DEFAULT_ALLOCATION
    )
    portfolio = generate_scorecard(portfolio)

    # Add a "Download Portfolio" button
    csv = portfolio.to_csv(index=False).encode('utf-8')
    st.download_button("Download Portfolio CSV", csv, "portfolio.csv", "text/csv")

    st.dataframe(portfolio)

    # Dummy covariance matrix for volatility calc (identity * small variance)
    cov_matrix = np.identity(len(portfolio)) * 0.0001

    vol = portfolio_volatility(portfolio['Weight'].values, cov_matrix)
    st.write(f"Estimated Annualized Volatility: {vol:.2%}")

    # Pie chart of stock weights
    st.subheader("Securities")
    fig, ax = plt.subplots()
    ax.pie(portfolio['Weight'], labels=portfolio['Ticker'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # Bar chart of sector weights
    st.subheader("Sector")
    sector_weights = portfolio.groupby("Sector")["Weight"].sum()
    st.bar_chart(sector_weights)

    # Bar chart of asset class weights
    st.subheader("Asset Class")
    asset_class_weights = portfolio.groupby("Asset Class")["Weight"].sum()
    st.bar_chart(asset_class_weights)

if st.button("Run Backtest", key="button_bottom"):
    st.write(f"Generating portfolio for client: **{client_name}** with risk level: **{risk_level}**")
    st.write(f"Maximum stocks allowed: {max_stocks}")

    # Here you can call your portfolio construction function
    # portfolio = build_portfolio(risk_level, max_stocks)
    # st.write(portfolio)


st.title("Investment Model Backtest Demo")

# Load data
returns = load_sample_returns()

# Simple equal weight portfolio (weights sum to 1)
tickers = list(returns.columns)
equal_weight = 1 / len(tickers)
weights = {ticker: equal_weight for ticker in tickers}

# Run backtest
# Convert weights dict to a DataFrame with 'Ticker' and 'Weight' columns
portfolio_df = pd.DataFrame(list(weights.items()), columns=["Ticker", "Weight"])
cum_returns = backtest_portfolio(portfolio_df, returns)

# Show cumulative return chart
st.line_chart(cum_returns)

# Compliance disclaimer
st.markdown("""
---
**Compliance Disclaimer:**  
This model is for use by licensed investment advisors only. It is a tool to assist portfolio construction and backtesting using historical data.  
Past performance is not indicative of future results.  
Bond returns are simulated using ETFs when actual bond data is limited.  
This tool does not provide discretionary advice or trade execution.  
Users must ensure compliance with all applicable regulations.
""")
