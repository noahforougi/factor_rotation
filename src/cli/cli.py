import typer
from macro import core, config
from typing import Optional
import pandas as pd

app = typer.Typer()


@app.command()
def fetch(indicator: Optional[str] = None):
    """
    Fetch data for all indicators or a specific indicator.
    """
    if indicator:
        data = core.fetch_all_data(indicators=[indicator])
    else:
        data = core.fetch_all_data()

    data.to_csv(config.OUTPUT_DIR + "/macro_indicators.csv")
    typer.echo("Fetched macro data and saved")



@app.command()
def business_cycle():
    """
    Run analytics on the fetched macroeconomic indicators.
    """
    try:
        df = pd.read_csv(config.OUTPUT_DIR + "/macro_indicators.csv")
        core.calculate(df).to_csv(
            config.OUTPUT_DIR + "/business_cycle_indicator.csv"
        )
        typer.echo("Business Cycle Indicator analysis completed and saved")
    except Exception as e:
        typer.echo(f"An error occurred: {e}")


if __name__ == "__main__":
    app()
