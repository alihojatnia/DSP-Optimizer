# src/chrom_model.py
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import os


def langmuir_breakthrough(
    load_mg_ml: float = 50,
    qmax: float = 120,
    kd: float = 2.0,
    flow_rate_ml_min: float = 1.0,
    column_cv_ml: float = 1.0,
    t_max_min: float = 100,
) -> dict:
    """
    Simulate breakthrough curve using Transport Dispersive Model (simplified)
    """
    C0 = load_mg_ml  # inlet concentration
    void = 0.4  # void fraction
    tau = column_cv_ml * void / flow_rate_ml_min  # residence time

    def ode(t, y):
        C, q = y
        dCdt = (C0 - C) / tau - (1 - void) / void * (qmax * C / (kd + C) - q)
        dqdt = qmax * C / (kd + C) - q
        return [dCdt, dqdt]

    sol = solve_ivp(
        ode,
        [0, t_max_min],
        [0, 0],
        method="LSODA",
        t_eval=np.linspace(0, t_max_min, 500),
    )

    # Plot
    os.makedirs("reports", exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(sol.t, sol.y[0] / C0, label="C/C₀", color="blue")
    ax.set_xlabel("Column Volumes (CV)")
    ax.set_ylabel("Normalized Concentration")
    ax.set_title(f"Breakthrough: Load={load_mg_ml}, qmax={qmax}, Kd={kd}")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("reports/breakthrough.png", dpi=300)
    plt.close()

    return {
        "time_min": sol.t.tolist(),
        "C_norm": (sol.y[0] / C0).tolist(),
        "q_mg_ml": sol.y[1].tolist(),
    }


# import numpy as np

# def langmuir_breakthrough(load, qmax, kd, column_cv_ml=1.0):
#     """Simple normalized Langmuir breakthrough curve"""
#     t = np.linspace(0, 20, 200)  # minutes
#     C0 = load / column_cv_ml
#     # Langmuir isotherm approximation
#     C = C0 * t / (t + (kd * column_cv_ml / qmax))
#     return {
#         "time_min": t,
#         "C_norm": np.clip(C / C0, 0, 1.1)  # Normalize and cap
#     }
