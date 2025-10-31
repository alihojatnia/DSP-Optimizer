import pandas as pd
import os


# from src.doe_generator import generate_doe_smart   # <-- NEW NAME
from src.doe_generator import generate_doe_smart

def test_doe():
    factors = {"pH": [6.0, 8.0], "NaCl_mM": [0, 500]}
    df = generate_doe_smart(factors, method="fullfact")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 4                     # 2^2 = 4 runs
    assert "Run" in df.columns
    assert os.path.exists("reports/doe_plan.csv")
    print("test_doe PASSED")
