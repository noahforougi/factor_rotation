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
        data.to_csv(data_config.OUTPUT_DIR + "/macro_indicators.csv")
        typer.echo("Fetched macro data and saved")
    if trade:
        data = data_core.compile_etf_data()
        data.to_csv(data_config.OUTPUT_DIR + "/etf_data.csv")
        typer.echo("Fetched etf data and saved")
        



@app.command()
def business_cycle():
    """
    Run analytics on the fetched macroeconomic indicators.
    """
    try:
        df = pd.read_csv(data_config.OUTPUT_DIR + "/macro_indicators.csv")
        trade_core.calculate(df).to_csv(
            data_config.OUTPUT_DIR + "/business_cycle_indicator.csv"
        )
        typer.echo("Business Cycle Indicator analysis completed and saved")
    except Exception as e:
        typer.echo(f"An error occurred: {e}")


if __name__ == "__main__":
    app()
