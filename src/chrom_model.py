import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

def breakthrough_curve(t_span=30, qmax=100, kd=1):
    """Simple Langmuir breakthrough simulator"""
    def langmuir(c): return qmax * c / (kd + c)
    
    def model(t, y):
        c, q = y
        dc_dt = 1 - c - (langmuir(c) - q)  # Simplified TDR
        dq_dt = langmuir(c) - q
        return [dc_dt, dq_dt]
    
    sol = solve_ivp(model, [0, t_span], [0, 0], t_eval=np.linspace(0, t_span, 300))
    
    # Plot & Save
    fig, ax = plt.subplots()
    ax.plot(sol.t, sol.y[0], label='C_out')
    ax.set_xlabel('Time (min)'); ax.set_ylabel('Concentration')
    ax.legend(); plt.tight_layout()
    plt.savefig('reports/breakthrough.png', dpi=300)
    plt.close()
    
    return sol

if __name__ == "__main__":
    breakthrough_curve()
    print("Breakthrough plot saved!")