import pyDOE2 as pyDOE
import pandas as pd
import numpy as np

def generate_doe(factors: dict, n_runs: int = 8) -> pd.DataFrame:
    """factors: {'pH': [6.0, 8.0], 'NaCl_mM': [0, 500]}"""
    names = list(factors.keys())
    n_factors = len(names)
    
    # Full factorial or Box-Behnken
    if n_factors <= 3:
        design = pyDOE.ff2n(n_factors)
    else:
        design = pyDOE.bbdesign(n_factors)
    
    # Scale to levels
    scaled = np.zeros((len(design), n_factors))
    for i, (name, levels) in enumerate(factors.items()):
        scaled[:, i] = np.linspace(levels[0], levels[1], len(design))
    
    df = pd.DataFrame(scaled, columns=names)
    df.insert(0, 'Run', range(1, len(df) + 1))
    
    # Save
    df.to_csv('reports/doe_plan.csv', index=False)
    return df

if __name__ == "__main__":
    factors = {
        'pH': [6.0, 8.0],
        'NaCl_mM': [50, 500],
        'Load_mg_ml': [20, 100]
    }
    doe_df = generate_doe(factors)
    print(doe_df)