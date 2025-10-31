# NEW (add this)
from doepy import build
import pandas as pd
import numpy as np


def generate_doe(factors: dict, n_runs: int = 8) -> pd.DataFrame:
    """factors: {'pH': [6.0, 8.0], 'NaCl_mM': [0, 500]}"""
    # doepy uses DataFrame directly
    df = build.full_fact({name: [low, high] for name, (low, high) in factors.items()})
    df.insert(0, "Run", range(1, len(df) + 1))

    # Save
    df.to_csv("reports/doe_plan.csv", index=False)
    return df


if __name__ == "__main__":
    factors = {"pH": [6.0, 8.0], "NaCl_mM": [50, 500], "Load_mg_ml": [20, 100]}
    doe_df = generate_doe(factors)
    print(doe_df)
