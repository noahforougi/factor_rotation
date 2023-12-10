from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ.get("FRED_API_KEY")

INDICATORS = {
    "INDPRO": "INDPRO",
    "UNRATE": "UNRATE",
    "CPI": "CPIAUCSL",
    "PPI": "PPIACO",
    "RETAILSALES": "RSXFS",
    "HOUST": "HOUST",
    "PCE": "PCE",
    "PAYEMS": "PAYEMS",
    "AHE": "CES0500000003",
    "GDP": "GDP",
    "TEN_YEAR_TREASURY": "DGS10",
}


OUTPUT_DIR = "/Users/noahforougi/research/factor_rotation/src/data"
