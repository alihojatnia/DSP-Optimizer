# import os
# from src.chrom_model import breakthrough_curve


# def test_model():
#     sol = breakthrough_curve(t_span=10)
#     assert len(sol.t) > 100
#     assert os.path.exists("reports/breakthrough.png")
#     print("test_model PASSED")


# tests/test_model.py
import os
from src.chrom_model import langmuir_breakthrough  # <-- NEW NAME


def test_model():
    result = langmuir_breakthrough(t_max_min=10)
    assert len(result["time_min"]) > 100
    assert os.path.exists("reports/breakthrough.png")
    print("test_model PASSED")
