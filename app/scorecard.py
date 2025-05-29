# app/scorecard.py
import pandas as pd
import numpy as np

def generate_scorecard(portfolio_df):
    np.random.seed(42)  # consistent mock scores

    portfolio_df['Quality Score'] = np.random.uniform(0, 100, size=len(portfolio_df)).round(1)
    portfolio_df['Value Score'] = np.random.uniform(0, 100, size=len(portfolio_df)).round(1)
    portfolio_df['Momentum Score'] = np.random.uniform(0, 100, size=len(portfolio_df)).round(1)
    
    return portfolio_df
