# import sys
# import os

# sys.path.insert(0, "src")  # Import src/

# import streamlit as st
# from akta_parser import parse_akta_res
# from doe_generator import generate_doe
# from chrom_model import breakthrough_curve

# st.set_page_config(page_title="DSP-Optimizer", layout="wide")

# st.title(" **DSP-Optimizer**")
# st.markdown("**ÄKTA → DoE → Model → Optimize** |")

# tab1, tab2, tab3 = st.tabs(["Parse ÄKTA", " DoE Planner", "Simulator"])

# with tab1:
#     uploaded = st.file_uploader("Upload .res file", type="res")
#     if uploaded:
#         with open("temp.res", "wb") as f:
#             f.write(uploaded.getbuffer())
#         df = parse_akta_res("temp.res")
#         st.line_chart(df.set_index("Volume_ml")[["UV280_mAU", "Conductivity_mS_cm"]])
#         st.dataframe(df[df["Peak"] == 1])  # Show peaks only
#         st.success(f" **{df['Peak'].sum()} peaks detected**")

# with tab2:
#     st.header("Design Experiments")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         ph = st.slider("pH", 5.0, 9.0, 7.0)
#     with col2:
#         nacl = st.slider("NaCl (mM)", 0, 1000, 250)
#     with col3:
#         load = st.slider("Load (mg/ml)", 10, 150, 50)

#     if st.button(" Generate DoE Plan", type="primary"):
#         factors = {
#             "pH": [ph - 0.5, ph + 0.5],
#             "NaCl_mM": [nacl - 100, nacl + 100],
#             "Load_mg_ml": [load - 20, load + 20],
#         }
#         doe_df = generate_doe(factors)
#         st.dataframe(doe_df)
#         st.download_button("Download CSV", doe_df.to_csv(index=False), "doe_plan.csv")

# with tab3:
#     qmax = st.slider("q_max (mg/ml)", 50, 200, 100)
#     kd = st.slider("K_d", 0.1, 5.0, 1.0)
#     if st.button("Simulate Breakthrough"):
#         breakthrough_curve(qmax=qmax, kd=kd)
#         st.image("reports/breakthrough.png", use_column_width=True)

# if st.button("Generate Full Report"):
#     st.balloons()
#     st.success("PDF saved to reports/report.pdf!")
# st.markdown("---")
# st.info(
#     "**Fork & Star**"
# )




# app.py
import streamlit as st
from src.akta_parser import parse_akta_res
from src.chrom_model import langmuir_breakthrough
from src.doe_generator import generate_doe_smart
import pandas as pd
import matplotlib.pyplot as plt
import os

# st.title("DSP-Optimizer: ÄKTA + DoE + Breakthrough")

# tab1, tab2, tab3 = st.tabs(["ÄKTA Parser", "Breakthrough Model", "DoE Generator"])

# with tab1:
#     uploaded = st.file_uploader("Upload .res file", type="res")
#     if uploaded:
#         with open("temp.res", "wb") as f:
#             f.write(uploaded.getbuffer())
#         df = parse_akta_res("temp.res")
#         st.dataframe(df.head(20))
#         st.line_chart(df[["UV_mAU"]])

# with tab2:
#     col1, col2 = st.columns(2)
#     with col1:
#         load = st.slider("Load (mg/mL)", 10, 120, 50)
#         qmax = st.slider("qmax (mg/mL)", 50, 200, 120)
#     with col2:
#         kd = st.slider("Kd (mg/mL)", 0.1, 10.0, 2.0)
#         cv = st.number_input("Column CV (mL)", 0.1, 10.0, 1.0)

#     if st.button("Simulate Breakthrough"):
#         result = langmuir_breakthrough(load, qmax, kd, column_cv_ml=cv)
#         fig, ax = plt.subplots()
#         ax.plot(result["time_min"], result["C_norm"])
#         ax.set_xlabel("Time (min)")
#         ax.set_ylabel("C/C₀")
#         st.pyplot(fig)

# with tab3:
#     st.write("Define factor ranges:")
#     factors = {}
#     with st.form("doe_form"):
#         pH = st.slider("pH", 5.0, 9.0, (6.0, 8.0))
#         salt = st.slider("NaCl (mM)", 0, 1000, (50, 500))
#         load = st.slider("Load (mg/mL)", 10, 120, (20, 80))
#         method = st.selectbox("DoE Type", ["frac_fact_res", "plackett_burman"])
#         submitted = st.form_submit_button("Generate DoE")
#         if submitted:
#             factors = {"pH": list(pH), "NaCl_mM": list(salt), "Load_mg_ml": list(load)}
#             doe = generate_doe_smart(factors, method=method)
#             st.dataframe(doe)
#             st.download_button("Download DoE", doe.to_csv(index=False), "doe_plan.csv")



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
            st.success(f"Parsed {len(df)} data points | {df['Peak'].sum()} peaks detected")
            
            # Plot UV + Conductivity
            chart_data = df[["Volume_ml", "UV280_mAU", "Conductivity_mS_cm"]].set_index("Volume_ml")
            st.line_chart(chart_data)
            
            # Show peak table
            peaks = df[df["Peak"] == 1]
            if not peaks.empty:
                st.subheader("Detected Peaks")
                st.dataframe(peaks[["Volume_ml", "UV280_mAU", "Peak_Label"]])
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
        load = st.slider("Load Concentration (mg/mL)", 10, 120, 50, step=5)
        qmax = st.slider("q_max (mg/mL resin)", 50, 200, 120, step=10)
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
# TAB 3: DoE Generator
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
        
        # CORRECT METHOD NAMES
        method = st.selectbox(
            "DoE Type",
            ["fullfact", "fracfact", "ccd"],
            format_func=lambda x: {
                "fullfact": "Full Factorial (2ᵏ)",
                "fracfact": "Fractional Factorial (2ᵏ⁻ᵖ)",
                "ccd": "Central Composite Design (CCD)"
            }[x]
        )
        
        submitted = st.form_submit_button("Generate DoE Plan", type="primary")
        
        if submitted:
            factors = {
                "pH": list(pH),
                "NaCl_mM": list(salt),
                "Load_mg_ml": list(load)
            }
            
            try:
                doe = generate_doe_smart(factors, method=method)
                runs = len(doe)
                st.success(f"Generated **{runs} experimental runs** using **{method.upper()}**")
                st.dataframe(doe, use_container_width=True)
                
                csv = doe.to_csv(index=False)
                st.download_button(
                    label="Download DoE Plan (CSV)",
                    data=csv,
                    file_name="doe_plan.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"DoE generation failed: {e}")

# ────────────────────────────────
# Footer
# ────────────────────────────────

