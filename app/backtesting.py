import pandas as pd
import numpy as np

def backtest_portfolio(portfolio_df, returns_df):
    tickers = portfolio_df['Ticker'].tolist()
    # Find which tickers are actually in returns_df columns
    available_tickers = [t for t in tickers if t in returns_df.columns]

    if len(available_tickers) < len(tickers):
        missing = set(tickers) - set(available_tickers)
        print(f"Warning: These tickers missing in returns data and will be skipped: {missing}")

    # Subset returns_df to only available tickers
    relevant_returns = returns_df[available_tickers]

    # Align weights to available tickers
    weights = portfolio_df.set_index('Ticker').loc[available_tickers, 'Weight'].values

    weighted_returns = relevant_returns.multiply(weights, axis=1)
    portfolio_returns = weighted_returns.sum(axis=1)
    cumulative_returns = (1 + portfolio_returns).cumprod() - 1

    return cumulative_returns