import typer
from ingress import core as data_core, config as data_config
from trade import core as trade_core
import pandas as pd

app = typer.Typer()


@app.command()
def fetch(macro: bool = False, 
          trade: bool = False):
    """
    Fetch data for all indicators or a specific indicator.
    """
    if macro:
        data = data_core.fetch_all_data()
        data_core.save_df_to_s3(data, "macro_indicators.csv")
        typer.echo("Fetched macro data and saved to S3")
    if trade:
        data = data_core.compile_etf_data()
        data_core.save_df_to_s3(data, "etf_data.csv")
        typer.echo("Fetched etf data and saved to S3")
        



@app.command()
def business_cycle():
    """
    Run analytics on the fetched macroeconomic indicators.
    """
    try:
        df = data_core.read_csv_from_s3("macro_indicators.csv")
        data_core.save_df_to_s3(trade_core.calculate_cycle(df), "business_cycle_indicator.csv")
        typer.echo("Business Cycle Indicator analysis completed and saved to s3")
    except Exception as e:
        typer.echo(f"An error occurred: {e}")


if __name__ == "__main__":
    app()
