
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

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

def calculate(df: pd.DataFrame): 
    X = construct_cycle_indicator(df)
    X = cycle_classifier(X) 
    return X