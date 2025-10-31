# src/doe_generator.py
from doepy import build
import pandas as pd


def generate_doe_smart(
    factors: dict,
    method: str = "frac_fact_res",  # or 'full_fact', 'plackett_burman'
    n_center: int = 1
) -> pd.DataFrame:
    """
    Generate efficient DoE
    factors = {'pH': [6.0, 8.0], 'NaCl_mM': [50, 500], 'Load': [20, 80]}
    """
    if method == "frac_fact_res":
        df = build.frac_fact_res(
            {k: v for k, v in factors.items()},
            n_center=n_center
        )
    elif method == "plackett_burman":
        df = build.plackett_burman({k: v for k, v in factors.items()})
    else:
        df = build.full_fact({k: [low, high] for k, (low, high) in factors.items()})

    df.insert(0, "Run", range(1, len(df) + 1))
    df = df.round(2)

    # Save
    import os
    os.makedirs("reports", exist_ok=True)
    df.to_csv("reports/doe_plan.csv", index=False)

    print(f"DoE generated: {len(df)} runs ({method})")
    return df