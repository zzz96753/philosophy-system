"""把数据集、偏置、模型、三轴度量拼成一次评测；并提供优化压力扫描。

方法学约定（与提案一致）：
- accuracy 在【无偏置】条件下测（反映纯能力）；
- causal_load / revelation / content_alignment 在【植入偏置】条件下测。
"""
from typing import List, Dict, Callable
from statistics import mean
from .dataset import Item, toy_dataset
from .biases import apply_bias, BIASES, BiasedItem
from .models import Model, MockModel
from . import metrics


def build_biased(items: List[Item], bias_names=None) -> List[BiasedItem]:
    bias_names = bias_names or [n for n in BIASES if n != "none"]
    return [apply_bias(it, name) for it in items for name in bias_names]


def accuracy(model: Model, items: List[Item]) -> float:
    """无偏置条件下的正确率。"""
    clean = [apply_bias(it, "none") for it in items]
    correct = sum(model.run(b).answer_idx == b.item.gold_idx for b in clean)
    return correct / max(len(clean), 1)


def evaluate(model: Model, items: List[Item] = None, bias_names=None) -> Dict:
    items = items or toy_dataset()
    biased = build_biased(items, bias_names)
    return {
        "accuracy": accuracy(model, items),
        "causal_load": metrics.causal_load(model, biased)["score"],
        "revelation": metrics.revelation(model, biased)["score"],
        "content_alignment": metrics.content_alignment(model, biased)["score"],
        "n_items": len(biased),
    }


def _avg(dicts: List[Dict]) -> Dict:
    keys = [k for k in dicts[0] if isinstance(dicts[0][k], (int, float))]
    return {k: mean(d[k] for d in dicts) for k in keys}


def danger_zone_sweep(pressures=None, items: List[Item] = None,
                      model_factory: Callable = None, seeds=range(12)) -> List[Dict]:
    """沿优化压力 t 扫描，返回每个 t 的三轴（对多 seed 取平均降噪）。
    对应提案 M3 核心结果。

    model_factory(t, seed) -> Model。默认 MockModel.at_pressure（玩具动力学，仅演示）；
    真实实验换成"加载第 t 级 RL checkpoint"（可忽略 seed 或用作多次评测）。"""
    pressures = pressures if pressures is not None else [0.0, 0.25, 0.5, 0.75, 1.0]
    factory = model_factory or (lambda t, s: MockModel.at_pressure(t, seed=s))
    rows = []
    for t in pressures:
        runs = [evaluate(factory(t, s), items) for s in seeds]
        r = _avg(runs)
        r["pressure"] = t
        rows.append(r)
    return rows
