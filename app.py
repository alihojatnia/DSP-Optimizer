# app.py
import streamlit as st
from src.akta_parser import parse_akta_res
from src.chrom_model import langmuir_breakthrough
from src.doe_generator import generate_doe_smart
import pandas as pd
import matplotlib.pyplot as plt
import os

# Page config
st.set_page_config(page_title="DSP-Optimizer", layout="wide")
st.title("DSP-Optimizer: ÄKTA + DoE + Breakthrough")

# Tabs
tab1, tab2, tab3 = st.tabs(["ÄKTA Parser", "Breakthrough Model", "DoE Generator"])

# ────────────────────────────────
# TAB 1: ÄKTA Parser
# ────────────────────────────────
with tab1:
    st.header("Upload ÄKTA UNICORN .res File")
    uploaded = st.file_uploader("Choose a .res file", type=["res", "txt"])

    if uploaded:
        with open("temp.res", "wb") as f:
            f.write(uploaded.getbuffer())

        try:
            df = parse_akta_res("temp.res")
            peaks_count = df["Is_Peak"].sum()
            st.success(
                f"Parsed {len(df)} data points | **{peaks_count} peaks detected**"
            )

            chart_data = df[["Volume_ml", "UV_mAU", "Conductivity_mS_cm"]].set_index(
                "Volume_ml"
            )
            st.line_chart(chart_data)

            peaks = df[df["Is_Peak"] == 1]
            if not peaks.empty:
                st.subheader("Detected Peaks")
                st.dataframe(
                    peaks[["Volume_ml", "UV_mAU", "Peak_Label", "Peak_Height"]],
                    use_container_width=True,
                )
            else:
                st.info("No peaks above threshold.")

        except Exception as e:
            st.error(f"Parsing error: {e}")

# ────────────────────────────────
# TAB 2: Breakthrough Model
# ────────────────────────────────
with tab2:
    st.header("Langmuir Breakthrough Curve")
    col1, col2 = st.columns(2)

    with col1:
        load = st.slider("Load (mg/mL)", 10, 120, 50, step=5)
        qmax = st.slider("q_max (mg/mL)", 50, 200, 120, step=10)
    with col2:
        kd = st.slider("K_d (mg/mL)", 0.1, 10.0, 2.0, step=0.1)
        cv = st.number_input("Column Volume (mL)", 0.1, 10.0, 1.0, step=0.1)

    if st.button("Simulate Breakthrough", type="primary"):
        try:
            result = langmuir_breakthrough(load, qmax, kd, column_cv_ml=cv)
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(result["time_min"], result["C_norm"], color="blue", linewidth=2)
            ax.set_xlabel("Time (min)")
            ax.set_ylabel("C / C₀")
            ax.set_title("Breakthrough Curve")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"Simulation error: {e}")

# ────────────────────────────────
# TAB 3: DoE Generator (NO DOWNLOAD — JUST DISPLAY)
# ────────────────────────────────
with tab3:
    st.header("Design of Experiments (DoE)")
    st.write("Define factor ranges:")

    with st.form("doe_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            pH = st.slider("pH", 5.0, 9.0, (6.0, 8.0))
        with col2:
            salt = st.slider("NaCl (mM)", 0, 1000, (50, 500))
        with col3:
            load = st.slider("Load (mg/mL)", 10, 120, (20, 80))

        method = st.selectbox(
            "DoE Type",
            ["fullfact", "fracfact", "ccd"],
            format_func=lambda x: {
                "fullfact": "Full Factorial (2ᵏ)",
                "fracfact": "Fractional Factorial (2ᵏ⁻ᵖ)",
                "ccd": "Central Composite Design (CCD)",
            }[x],
        )

        submitted = st.form_submit_button("Generate DoE Plan", type="primary")

        if submitted:
            factors = {"pH": list(pH), "NaCl_mM": list(salt), "Load_mg_ml": list(load)}

            try:
                doe = generate_doe_smart(factors, method=method)
                runs = len(doe)
                st.success(f"**{runs} runs generated** using **{method.upper()}**")
                st.dataframe(doe, use_container_width=True)

                # REMOVED: st.download_button() — No download needed
                st.info("DoE plan displayed above. Copy or screenshot as needed.")

            except Exception as e:
                st.error(f"DoE generation failed: {e}")

# ────────────────────────────────
# Footer
# ────────────────────────────────
