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

st.title("DSP-Optimizer: ÄKTA + DoE + Breakthrough")

tab1, tab2, tab3 = st.tabs(["ÄKTA Parser", "Breakthrough Model", "DoE Generator"])

with tab1:
    uploaded = st.file_uploader("Upload .res file", type="res")
    if uploaded:
        with open("temp.res", "wb") as f:
            f.write(uploaded.getbuffer())
        df = parse_akta_res("temp.res")
        st.dataframe(df.head(20))
        st.line_chart(df[["UV_mAU"]])

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        load = st.slider("Load (mg/mL)", 10, 120, 50)
        qmax = st.slider("qmax (mg/mL)", 50, 200, 120)
    with col2:
        kd = st.slider("Kd (mg/mL)", 0.1, 10.0, 2.0)
        cv = st.number_input("Column CV (mL)", 0.1, 10.0, 1.0)

    if st.button("Simulate Breakthrough"):
        result = langmuir_breakthrough(load, qmax, kd, column_cv_ml=cv)
        fig, ax = plt.subplots()
        ax.plot(result["time_min"], result["C_norm"])
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("C/C₀")
        st.pyplot(fig)

with tab3:
    st.write("Define factor ranges:")
    factors = {}
    with st.form("doe_form"):
        pH = st.slider("pH", 5.0, 9.0, (6.0, 8.0))
        salt = st.slider("NaCl (mM)", 0, 1000, (50, 500))
        load = st.slider("Load (mg/mL)", 10, 120, (20, 80))
        method = st.selectbox("DoE Type", ["frac_fact_res", "plackett_burman"])
        submitted = st.form_submit_button("Generate DoE")
        if submitted:
            factors = {"pH": list(pH), "NaCl_mM": list(salt), "Load_mg_ml": list(load)}
            doe = generate_doe_smart(factors, method=method)
            st.dataframe(doe)
            st.download_button("Download DoE", doe.to_csv(index=False), "doe_plan.csv")