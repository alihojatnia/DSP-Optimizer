# # src/akta_parser.py
import pandas as pd
import re
import os
from scipy.signal import find_peaks
from typing import Tuple, Optional


# def parse_akta_res(
#     file_path: str,
#     uv_col: str = "UV1_280nm",
#     cond_col: str = "Conductivity",
#     min_height: float = 50,
#     min_distance: float = 30,
# ) -> pd.DataFrame:
#     """
#     Parse ÄKTA .res file → DataFrame with auto peak detection
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"File not found: {file_path}")

#     with open(file_path, "r", encoding="latin-1") as f:
#         content = f.read()

#     # Find curve data block
#     curve_block = re.search(r"Curve Data:.*?(?=\n\w+:|$)", content, re.DOTALL)
#     if not curve_block:
#         raise ValueError("No 'Curve Data' block found in .res file")

#     lines = curve_block.group(0).splitlines()
#     data_lines = [line for line in lines if re.match(r"^\s*\d+\.?\d*", line)]

#     if not data_lines:
#         raise ValueError("No numeric data lines found")

#     # Extract all numeric columns
#     rows = [re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line) for line in data_lines]
#     df = pd.DataFrame(rows).astype(float)
#     df.columns = [f"Col_{i}" for i in range(len(df.columns))]

#     # Try to map known columns
#     header_match = re.search(r"Sample Name.*?Curve.*?Unit", content)
#     if header_match:
#         header_line = header_match.group(0)
#         if uv_col.replace(" ", "") in header_line.replace(" ", ""):
#             uv_idx = [i for i, h in enumerate(header_line.split()) if uv_col.replace(" ", "") in h.replace(" ", "")]
#             if uv_idx:
#                 df = df.rename(columns={f"Col_{uv_idx[0]}": "UV_mAU"})

#     if "UV_mAU" not in df.columns:
#         df["UV_mAU"] = df["Col_1"]  # fallback

#     df = df[["UV_mAU"]].copy()
#     df["Volume_ml"] = df.index * 0.1  # assume 0.1 mL intervals (adjust later)

#     # === Peak Detection ===
#     peaks, props = find_peaks(
#         df["UV_mAU"],
#         height=min_height,
#         distance=min_distance,
#         prominence=20
#     )

#     df["Is_Peak"] = 0
#     df.loc[peaks, "Is_Peak"] = 1
#     df["Peak_Height"] = 0.0
#     df.loc[peaks, "Peak_Height"] = props["peak_heights"]

#     # Label peaks by volume zones
#     labels = []
#     for i, idx in enumerate(peaks):
#         vol = df.loc[idx, "Volume_ml"]
#         if vol < df["Volume_ml"].max() * 0.3:
#             labels.append("Flowthrough")
#         elif vol < df["Volume_ml"].max() * 0.7:
#             labels.append("Product")
#         else:
#             labels.append("Wash/Strip")
#     df["Peak_Label"] = ""
#     df.loc[peaks, "Peak_Label"] = labels

#     # Save
#     os.makedirs("reports", exist_ok=True)
#     df.to_csv("reports/parsed_akta.csv", index=False)

#     print(f"Parsed {len(df)} points, {len(peaks)} peaks detected")
#     return df


# src/akta_parser.py
def parse_akta_res(
    file_path: str,
    uv_col: str = "UV1_280nm",
    cond_col: str = "Conductivity",
    min_height: float = 50,
    min_distance: float = 30,
) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="latin-1") as f:
        content = f.read()

    # FLEXIBLE BLOCK DETECTION
    curve_block = (
        re.search(r"Curve Data:.*?(?=\n\w+:|$)", content, re.DOTALL) or
        re.search(r"\[Curve Data.*?\].*?(?=\n\[|\Z)", content, re.DOTALL)
    )
    if not curve_block:
        raise ValueError("No 'Curve Data' block found in .res file")

    lines = curve_block.group(0).splitlines()
    data_lines = [line for line in lines if re.match(r"^\s*-?\d+\.?\d*", line)]

    if not data_lines:
        raise ValueError("No numeric data lines found")

    rows = [re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", line) for line in data_lines]
    df = pd.DataFrame(rows).astype(float)

    # DYNAMIC COLUMN MAPPING
    header_line = next((l for l in lines if "Volume" in l and "UV" in l), None)
    if header_line:
        cols = re.findall(r"\b\w+(?:\s*\(\w+\))?", header_line)
        if len(cols) >= 3:
            df.columns = [c.strip() for c in cols[:3]]
        else:
            df.columns = ["Volume_ml", "UV_mAU", "Conductivity_mS_cm"]
    else:
        df.columns = ["Volume_ml", "UV_mAU", "Conductivity_mS_cm"]

    # RENAME UV COLUMN
    uv_candidates = [c for c in df.columns if "UV" in c and ("mAU" in c or "280" in c)]
    if uv_candidates:
        df = df.rename(columns={uv_candidates[0]: "UV_mAU"})
    if "UV_mAU" not in df.columns:
        df["UV_mAU"] = df.iloc[:, 1]

    # RENAME OTHER COLUMNS TO STANDARD
    rename_map = {
        col: "Volume_ml" for col in df.columns if "Volume" in col
    }
    rename_map.update({
        col: "Conductivity_mS_cm" for col in df.columns if "Conductivity" in col and col != "UV_mAU"
    })
    df = df.rename(columns=rename_map)

    # NOW SAFE TO SELECT
    df = df[["Volume_ml", "UV_mAU", "Conductivity_mS_cm"]].copy()

    # PEAK DETECTION
    peaks, props = find_peaks(
        df["UV_mAU"],
        height=min_height,
        distance=min_distance,
        prominence=20
    )

    df["Is_Peak"] = 0
    df.loc[peaks, "Is_Peak"] = 1
    df["Peak_Height"] = 0.0
    df.loc[peaks, "Peak_Height"] = props["peak_heights"]

    # LABEL PEAKS
    labels = []
    for i, idx in enumerate(peaks):
        vol = df.loc[idx, "Volume_ml"]
        if vol < df["Volume_ml"].max() * 0.3:
            labels.append("Flowthrough")
        elif vol < df["Volume_ml"].max() * 0.7:
            labels.append("Product")
        else:
            labels.append("Wash/Strip")
    df["Peak_Label"] = ""
    df.loc[peaks, "Peak_Label"] = labels

    # SAVE
    os.makedirs("reports", exist_ok=True)
    df.to_csv("reports/parsed_akta.csv", index=False)

    print(f"Parsed {len(df)} points, {len(peaks)} peaks detected")
    return df
