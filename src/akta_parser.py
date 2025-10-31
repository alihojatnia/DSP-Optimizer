import pandas as pd
import re
from scipy.signal import find_peaks
import os

def parse_akta_res(file_path: str) -> pd.DataFrame:
    """Parse ÄKTA .res → DataFrame with peaks detected"""
    with open(file_path, 'r', encoding='latin-1') as f:
        content = f.read()

    # Extract curve data lines
    curve_lines = re.findall(r'(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)', content)
    
    if not curve_lines:
        raise ValueError("No curve data found in .res file")
    
    df = pd.DataFrame(curve_lines, columns=['Volume_ml', 'UV280_mAU', 'Conductivity_mS_cm'])
    df = df.astype({'Volume_ml': float, 'UV280_mAU': float, 'Conductivity_mS_cm': float})
    
    # Peak detection
    peaks, _ = find_peaks(df['UV280_mAU'], height=100, distance=50)
    df['Peak'] = 0
    df.loc[peaks, 'Peak'] = 1
    df['Peak_Label'] = ['Flowthrough', 'Product', 'HCP/Impurity'][min(len(peaks), 3)]
    
    # Save parsed
    os.makedirs('reports', exist_ok=True)
    df.to_csv('reports/parsed_akta.csv', index=False)
    
    return df

if __name__ == "__main__":
    df = parse_akta_res('data/sample.res')
    print(df.head(10))
    print(f"Peaks detected: {df['Peak'].sum()}")