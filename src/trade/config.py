import pandas as pd
ETFS = {
    'value': 'VTV',   
    'growth': 'VUG',  
    'quality': 'SPHQ', 
    'momentum': 'PDP', 
    'low_vol': 'USMV'  
}

START_DATE = pd.to_datetime("2005-01-01")

WEIGHTS = {
    "Expansion": {"value": 0.4, "growth": 0.4, "quality": 0.2, "momentum": 0.0, "low_vol": 0.0},
    "Contraction": {"value": 0.0, "growth": 0.3, "quality": 0.2, "momentum": 0.2, "low_vol": 0.3}
}

EQUAL_WEIGHTS = {"value": 0.2, "growth": 0.2, "quality": 0.2, "momentum": 0.2, "low_vol": 0.2}