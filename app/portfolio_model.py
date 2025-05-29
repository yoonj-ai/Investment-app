import pandas as pd
import numpy as np

def build_portfolio(risk_level, max_stocks, tilt="None", max_sector_exposure=1.0, 
                    score_df=None, asset_allocation=None):
    
    np.random.seed(42)  # reproducibility

    # Default mock universe if score_df not provided
    if score_df is None:
        stock_universe = [f"Stock{i}" for i in range(1, 101)]
        sectors = ["Tech", "Finance", "Healthcare", "Energy", "Industrials"]
        asset_classes = ["Equity", "Bond"]
        score_df = pd.DataFrame({
            "Ticker": stock_universe,
            "Sector": np.random.choice(sectors, len(stock_universe)),
            "Asset Class": np.random.choice(asset_classes, len(stock_universe))
        })

    # Default equal asset allocation if None
    if asset_allocation is None:
        unique_classes = score_df["Asset Class"].unique()
        alloc_pct_default = 1.0 / len(unique_classes)
        asset_allocation = {cls: alloc_pct_default for cls in unique_classes}

    portfolio_rows = []

    for asset_class, alloc_pct in asset_allocation.items():
        class_df = score_df[score_df["Asset Class"] == asset_class].copy()
        if class_df.empty:
            continue

        # Apply style tilt sorting if applicable
        if tilt in ["Quality", "Value", "Momentum"] and f"{tilt} Score" in class_df.columns:
            class_df = class_df.sort_values(f"{tilt} Score", ascending=False)
        else:
            class_df = class_df.sample(frac=1, random_state=42).reset_index(drop=True)

        sector_counts = {}
        sector_limit = int(max_stocks * max_sector_exposure * alloc_pct)
        selected_stocks = []

        for idx, row in class_df.iterrows():
            sector = row["Sector"]
            if sector not in sector_counts:
                sector_counts[sector] = 0

            if sector_counts[sector] < sector_limit:
                selected_stocks.append(row)
                sector_counts[sector] += 1

            if len(selected_stocks) >= int(max_stocks * alloc_pct):
                break

        selected_df = pd.DataFrame(selected_stocks)
        n = len(selected_df)

        if n == 0:
            continue

        # Assign weights by risk level
        if risk_level == "Low":
            weights = np.random.dirichlet(np.ones(n) * 10)
        elif risk_level == "Medium":
            weights = np.random.dirichlet(np.ones(n) * 5)
        else:
            weights = np.random.dirichlet(np.ones(n) * 1)

        selected_df["Weight"] = weights * alloc_pct  # scale weights by asset allocation %

        portfolio_rows.append(selected_df)

    if portfolio_rows:
        final_portfolio = pd.concat(portfolio_rows).sort_values("Weight", ascending=False).reset_index(drop=True)
        return final_portfolio
    else:
        # Return empty dataframe with expected columns
        cols = list(score_df.columns) + ["Weight"] if score_df is not None else ["Ticker", "Weight", "Sector", "Asset Class"]
        return pd.DataFrame(columns=cols)


def portfolio_volatility(weights, cov_matrix):
    """
    weights: np.array of portfolio weights
    cov_matrix: covariance matrix of returns
    """
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)  # annualized

print("portfolio_model.py loaded successfully.")