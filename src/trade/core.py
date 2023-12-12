
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from trade import config

def construct_cycle_indicator(df: pd.DataFrame) -> pd.DataFrame:
    """Format data to wide format and interpolate missing values.
    
    Args: 
        df: 
    
    Return: 
        pd.DataFrame
    """
    # Convert to monthly and interpolate
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y%m01")
    X = df.groupby(["month", "indicator"], as_index=False)["value"].mean()
    X["date"] = pd.to_datetime(X["month"])
    X = X.pivot(index="date", values="value", columns="indicator").interpolate(
        method="linear"
    )

    # Caclulate percentage change
    X = X.pct_change(periods=12).dropna()
    
    # Perform PCA 
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(X)
    pca = PCA(n_components=1)
    return pd.DataFrame(pca.fit_transform(scaled_data), index=X.index, columns=["BCI"])




def cycle_classifier(df: pd.DataFrame):
    # Turn BCI into rolling 3 month average
    X = df.assign(BCI=lambda x: x.BCI.rolling(3).mean())

    # Calculate peaks and troughs
    peaks, _ = find_peaks(X['BCI'])
    troughs, _ = find_peaks(-X['BCI'])

    # Initialize a column for the business cycle phase
    X['Cycle_Phase'] = np.nan

    # Assign values for expansion and contraction
    for i in range(len(peaks)):
        if i == 0 and troughs[0] < peaks[0]:
            X.iloc[troughs[0]:peaks[0], X.columns.get_loc('Cycle_Phase')] = 'Expansion'
        elif i < len(troughs):
            X.iloc[troughs[i]:peaks[i], X.columns.get_loc('Cycle_Phase')] = 'Expansion'
            X.iloc[peaks[i]:troughs[i+1] if i+1 < len(troughs) else len(X), X.columns.get_loc('Cycle_Phase')] = 'Contraction'

    X['Cycle_Phase'].fillna(method='ffill', inplace=True)

    return X

def calculate_cycle(df: pd.DataFrame): 
    X = construct_cycle_indicator(df)
    X = cycle_classifier(X) 
    return X


def convert_to_monthly_returns(df):
    """
    Convert daily asset prices to monthly returns.
    
    Args:
        df (pd.DataFrame): DataFrame with daily asset prices and a 'Date' column.
    
    Returns:
        pd.DataFrame: DataFrame with monthly returns.
    """
    monthly_returns = (
        df.assign(date=lambda x: pd.to_datetime(x.Date.str.slice(0, 10)))
        .set_index("date")
        .resample("M")
        .last()
        .drop(columns=["Date"])
        .pct_change()
        .dropna()
        .reset_index()
        .assign(date=lambda x: pd.to_datetime(x.date.dt.strftime("%Y-%m-01")))
    )
    return monthly_returns

def apply_cycle_weights(df, cycle_weights):
    """
    Apply weights to the assets based on the business cycle phase.
    
    Args:
        df (pd.DataFrame): DataFrame with asset returns and 'Cycle_Phase' column.
        cycle_weights (dict): Dictionary with weights for each asset in different cycle phases.
    
    Returns:
        pd.DataFrame: DataFrame with weighted returns.
    """
    # Initialize a DataFrame to store weighted returns
    weighted_returns = pd.DataFrame(index=df.index)

    # Iterate over the DataFrame and apply the correct weights based on the cycle phase
    for index, row in df.iterrows():
        phase = row['Cycle_Phase']
        weights = cycle_weights[phase]
        for asset in weights.keys():
            weighted_returns.loc[index, asset] = row[asset] * weights[asset]

    return weighted_returns


def calculate_portfolio_returns(asset_returns, cycle_weights, equal_weights):
    """
    Calculate and compare the portfolio returns for cycle-based and equal-weight strategies.
    
    Args:
        asset_returns (pd.DataFrame): DataFrame with asset returns.
        cycle_weights (dict): Dictionary with weights for expansion and contraction phases.
        equal_weights (dict): Dictionary with equal weights for each asset.
    
    Returns:
        pd.DataFrame: DataFrame comparing the two strategies.
    """
    # Apply cycle weights
    weighted_returns = apply_cycle_weights(asset_returns, cycle_weights)
    weighted_returns['Strategy_Portfolio_Returns'] = weighted_returns.sum(axis=1)

    # Calculate equal weight portfolio returns
    equal_weighted_returns = asset_returns[list(equal_weights.keys())] * pd.Series(equal_weights)
    equal_weighted_returns['Equal_Weight_Portfolio_Returns'] = equal_weighted_returns.sum(axis=1)

    # Comparing the two strategies
    comparison = pd.DataFrame({
        'Date': asset_returns['date'],
        'Strategy_Returns': weighted_returns['Strategy_Portfolio_Returns'],
        'Equal_Weight_Returns': equal_weighted_returns['Equal_Weight_Portfolio_Returns']
    })

    return comparison

def create_strategy(factor_prices: pd.DataFrame, bci: pd.DataFrame) -> pd.DataFrame: 
    
    # Calculate factor returns
    monthly_factor_returns = convert_to_monthly_returns(factor_prices)

    # Link business cycle with asset returns
    X = bci.assign(date=lambda x: pd.to_datetime(x.date)).merge(monthly_factor_returns, on="date", how="inner")

    
    # Calculate and compare the returns 
    comparison = calculate_portfolio_returns(X, config.WEIGHTS, config.EQUAL_WEIGHTS)

    return comparison
