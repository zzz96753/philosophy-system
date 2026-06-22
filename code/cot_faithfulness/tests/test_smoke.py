"""冒烟测试：流水线可跑，且玩具动力学复现"危险区间"趋势。
运行： python -m pytest -q   或   python tests/test_smoke.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cot_faith import evaluate, MockModel, danger_zone_sweep


def test_evaluate_keys():
    r = evaluate(MockModel.at_pressure(0.0))
    for k in ["accuracy", "causal_load", "revelation", "content_alignment", "n_items"]:
        assert k in r
    assert 0.0 <= r["accuracy"] <= 1.0


def test_danger_zone_trend():
    rows = danger_zone_sweep([0.0, 1.0])
    lo, hi = rows[0], rows[-1]
    # 玩具动力学：高压力下揭示应下降、正确率不降
    assert hi["revelation"] <= lo["revelation"] + 1e-9
    assert hi["accuracy"] >= lo["accuracy"] - 1e-9


if __name__ == "__main__":
    test_evaluate_keys()
    test_danger_zone_trend()
    print("smoke tests passed")
