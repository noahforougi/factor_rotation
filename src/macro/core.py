from fredapi import Fred
import pandas as pd
from macro import config
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

fred = Fred(api_key=config.API_KEY)


def fetch_data(series_id):
    """Fetch data for a given series ID."""
    data = fred.get_series(series_id)
    return data


def fetch_all_data():
    """Fetch all data based on the indicators dictionary and return in long format."""
    long_data = []
    for name, series_id in config.INDICATORS.items():
        series_data = fetch_data(series_id)
        if series_data is not None:
            # Create a DataFrame for each series and reset the index
            df = pd.DataFrame(series_data, columns=["value"])
            df["indicator"] = name
            df.reset_index(inplace=True)
            df.rename(columns={"index": "date"}, inplace=True)
            long_data.append(df)

    # Concatenate all dataframes
    long_df = pd.concat(long_data)

    return long_df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess data: Convert to monthly, interpolate, and compute rolling average."""
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y%m01")
    df = df.groupby(["month", "indicator"], as_index=False)["value"].mean()
    df["date"] = pd.to_datetime(df["month"])
    wide_df = df.pivot(index="date", values="value", columns="indicator").interpolate(
        method="linear"
    )
    return wide_df


def calculate_growth_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate yearly growth rates from the data."""
    return df.pct_change(periods=12).dropna()


def perform_pca(df: pd.DataFrame) -> pd.DataFrame:
    """Perform PCA and return the first principal component."""
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    pca = PCA(n_components=1)
    return pd.DataFrame(pca.fit_transform(scaled_data), index=df.index, columns=["BCI"])


def calculate_business_cycle_indicator(df):
    processed_data = preprocess_data(df)
    growth_rates = calculate_growth_rates(processed_data)
    bci = perform_pca(growth_rates)
    return bci
