import pandas as pd
import numpy as np

def load_sample_returns():
    np.random.seed(42)
    dates = pd.date_range(start='2015-04-30', end='2025-04-30', freq='ME')
    stocks = [f'STOCK{i+1}' for i in range(50)]
    bonds = [f'BOND{i+1}' for i in range(10)]
    
    # Simulate monthly returns: stocks (mean=0.01, std=0.05), bonds (mean=0.003, std=0.01)
    stock_returns = pd.DataFrame(np.random.normal(0.01, 0.05, size=(len(dates), 50)),
                                 index=dates, columns=stocks)
    bond_returns = pd.DataFrame(np.random.normal(0.003, 0.01, size=(len(dates), 10)),
                                index=dates, columns=bonds)
    
    # Combine into one DataFrame with MultiIndex columns
    stock_returns.columns = pd.MultiIndex.from_product([['Stock'], stock_returns.columns])
    bond_returns.columns = pd.MultiIndex.from_product([['Bond'], bond_returns.columns])
    
    returns = pd.concat([stock_returns, bond_returns], axis=1)
    return returns


def load_scores_and_metadata(score_path='data/current_scores.csv', metadata_path='data/stock_metadata.csv'):
    scores_df = pd.read_csv(score_path)
    metadata_df = pd.read_csv(metadata_path)
    
    # Merge scorecard and metadata (adds sector and asset class info)
    combined_df = pd.merge(scores_df, metadata_df, on='Ticker', how='left')
    
    return combined_df