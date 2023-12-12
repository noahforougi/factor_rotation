from fredapi import Fred
from ingress import config
import pandas as pd
import yfinance as yf
import boto3
from io import StringIO, BytesIO


fred = Fred(api_key=config.API_KEY)


def fetch_data(series_id):
    """Get series for FRED.

    Args:
        series_id: a str indicating the series from FRED to download

    """
    data = fred.get_series(series_id)
    return data


def fetch_all_data() -> pd.DataFrame:
    """Get all relevant series for business cycle indicator.

    Args:
        None

    Return: a pd.DataFrame
    """
    long_data = []
    for name, series_id in config.INDICATORS.items():
        series_data = fred.get_series(series_id)
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


def fetch_etf_data(etf_ticker, start_date):
    """
    Fetch historical data for a given ETF ticker from Yahoo Finance.
    """
    ticker_yahoo = yf.Ticker(etf_ticker)
    data = ticker_yahoo.history(start=start_date)
    return data["Close"]


def compile_etf_data(start_date=config.START_DATE):
    """
    Compile historical price data for a dictionary of ETFs.
    """
    price_data = pd.DataFrame()
    for etf_name, etf_ticker in config.ETFS.items():
        price_data[etf_name] = fetch_etf_data(etf_ticker, start_date)
    return price_data


def save_df_to_s3(df, object_name: str, bucket_name: str = "factor-rotation"):
    """
    Save a DataFrame to an S3 bucket as CSV.

    Args:
    - df (pd.DataFrame): DataFrame to save.
    - bucket_name (str): Name of the S3 bucket.
    - object_name (str): S3 object name. Include the file name and extension.
    """
    # Create an S3 client
    s3_client = boto3.client("s3")

    # Convert DataFrame to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)

    # Upload CSV to S3
    s3_client.put_object(
        Bucket=bucket_name, Key=object_name, Body=csv_buffer.getvalue()
    )


def read_csv_from_s3(object_key, bucket_name: str = "factor-rotation"):
    """
    Read a CSV file from S3 into a Pandas DataFrame.

    Args:
        bucket_name (str): Name of the S3 bucket.
        object_key (str): Key of the object in the S3 bucket (file path in S3).

    Returns:
        pd.DataFrame: DataFrame containing the data from the CSV file.
    """
    # Create an S3 client
    s3_client = boto3.client("s3")

    # Get object from S3
    obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)

    # Read data into Pandas DataFrame
    df = pd.read_csv(BytesIO(obj["Body"].read()))

    return df
