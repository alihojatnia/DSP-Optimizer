# src/doe_generator.py
from doepy import build
import pandas as pd
import os


# def generate_doe_smart(
#     factors: dict,
#     method: str = "frac_fact_res",  # or 'full_fact', 'plackett_burman'
#     n_center: int = 1
# ) -> pd.DataFrame:
#     """
#     Generate efficient DoE
#     factors = {'pH': [6.0, 8.0], 'NaCl_mM': [50, 500], 'Load': [20, 80]}
#     """
#     if method == "frac_fact_res":
#         df = build.frac_fact_res(
#             {k: v for k, v in factors.items()},
#             n_center=n_center
#         )
#     elif method == "plackett_burman":
#         df = build.plackett_burman({k: v for k, v in factors.items()})
#     else:
#         df = build.full_fact({k: [low, high] for k, (low, high) in factors.items()})

#     df.insert(0, "Run", range(1, len(df) + 1))
#     df = df.round(2)

#     # Save
#     import os
#     os.makedirs("reports", exist_ok=True)
#     df.to_csv("reports/doe_plan.csv", index=False)

#     print(f"DoE generated: {len(df)} runs ({method})")
#     return df


def generate_doe_smart(
    factors: dict, method: str = "fullfact", n_center: int = 3
) -> pd.DataFrame:
    """
    Smart DoE: fullfact, fracfact, or ccd
    """
    os.makedirs("reports", exist_ok=True)

    if method == "fullfact":
        df = build.full_fact(factors)
    elif method == "fracfact":
        # FIXED: frac_fact (no _res!)
        df = build.frac_fact(factors)
    elif method == "ccd":
        df = build.ccdesign(len(factors), center=n_center)
        df.columns = list(factors.keys())
        # Scale to actual levels
        for i, (name, (low, high)) in enumerate(factors.items()):
            df[name] = np.interp(df[name], [-1, 1], [low, high])
    else:
        raise ValueError("Method must be fullfact, fracfact, or ccd")

    df.insert(0, "Run", range(1, len(df) + 1))
    df.to_csv("reports/doe_plan.csv", index=False)
    return df
