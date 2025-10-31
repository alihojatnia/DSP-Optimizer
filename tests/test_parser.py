import pandas as pd
import os
from src.akta_parser import parse_akta_res


def test_parser():
    df = parse_akta_res("data/sample.res")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 5
    assert "UV280_mAU" in df.columns
    assert df["Peak"].sum() >= 1
    assert os.path.exists("reports/parsed_akta.csv")
    print("test_parser PASSED")
