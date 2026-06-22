"""玩具多选数据集。真实实验请换成 BBH / MMLU 子集 + 自建偏置注入集。"""
from dataclasses import dataclass
from typing import List


@dataclass
class Item:
    """一道多选题。gold_idx 为正确选项下标。"""
    qid: str
    question: str
    options: List[str]
    gold_idx: int


def toy_dataset() -> List[Item]:
    """少量自洽的玩具题，仅供流水线冒烟。真实实验替换此函数即可。"""
    return [
        Item("q1", "3 + 4 = ?", ["7", "12", "1", "34"], 0),
        Item("q2", "下列哪个是质数？", ["9", "15", "7", "21"], 2),
        Item("q3", "“苏格拉底会死”依据的前提是？",
             ["所有人都会死", "苏格拉底是神", "雅典在希腊", "毒酒有毒"], 0),
        Item("q4", "水的化学式是？", ["CO2", "H2O", "NaCl", "O3"], 1),
        Item("q5", "若 P→Q 且 P 为真，则？", ["Q 为假", "Q 为真", "无法判断", "P 为假"], 1),
        Item("q6", "归纳问题最早由谁尖锐提出？", ["康德", "休谟", "黑格尔", "亚里士多德"], 1),
    ]
