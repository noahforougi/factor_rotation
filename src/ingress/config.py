from dotenv import load_dotenv
import os
import pandas as pd


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

ETFS = {
    'value': 'VTV',   
    'growth': 'VUG',  
    'quality': 'SPHQ', 
    'momentum': 'PDP', 
    'low_vol': 'USMV'  
}

START_DATE = pd.to_datetime("2005-01-01")
OUTPUT_DIR = "/Users/noahforougi/research/factor_rotation/src/data"
