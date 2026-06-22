"""cot_faith — 思维链忠实度三轴评测最小实现.

对应研究提案《CoT忠实度的危险区间》M1 里程碑：
三轴 = 因果承载(causal load) · 内容对齐(content alignment) · 揭示(revelation)。
范式 = 植入偏置 × 优化压力扫描。

设计原则：纯标准库即可端到端跑（用 MockModel）；接真实模型只需实现 Model 接口。
"""
from .models import Model, MockModel, Response
from .dataset import Item, toy_dataset
from .biases import BiasedItem, apply_bias, BIASES
from .pipeline import evaluate, danger_zone_sweep

__all__ = [
    "Model", "MockModel", "Response",
    "Item", "toy_dataset",
    "BiasedItem", "apply_bias", "BIASES",
    "evaluate", "danger_zone_sweep",
]
