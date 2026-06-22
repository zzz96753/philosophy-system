# cot_faith — CoT 忠实度三轴评测（M1 代码骨架）

研究提案《[CoT忠实度的危险区间](../../哲学体系/研究提案/01-CoT忠实度的危险区间（研究提案）.md)》**里程碑 M1** 的最小可跑实现。

把"忠实"拆成三轴，并提供"植入偏置 × 优化压力扫描"范式的脚手架：

| 轴 | 含义 | 本实现 |
|----|------|--------|
| **因果承载** causal load | 去掉 CoT 答案是否改变 | `metrics.causal_load`（提前/无 CoT 对照） |
| **内容对齐** content alignment | CoT 声称用的因素是否真被用 | `metrics.content_alignment`（占位，待接反事实干预） |
| **揭示** revelation | CoT 是否点名真正驱动（植入偏置） | `metrics.revelation`（关键词金标准 + 判分器钩子） |

## 快速开始（纯标准库，无需安装）

```bash
cd code/cot_faithfulness
python run_demo.py          # 优化压力 × 三轴 扫描（玩具示意）
python tests/test_smoke.py  # 冒烟测试
```

`run_demo.py` 会打印三轴随优化压力的轨迹，并判读是否出现**危险区间形态**（正确率↑·承载↑·揭示↓）。这用的是 `MockModel`——**示意性模拟，非真实结果**，作用是证明整条流水线可跑、把假说做成可观察曲线。

## 接真实模型（M1 集成点）

只需实现 `Model` 协议的两个方法（见 `models.py` 末尾 `HFModel`/`OpenAIModel` 骨架）：

```python
class Model(Protocol):
    def run(self, b: BiasedItem) -> Response: ...            # 带 CoT 作答
    def run_without_cot(self, b: BiasedItem) -> Response: ...# 直接作答（因果承载用）
```

然后：

```python
from cot_faith import evaluate, danger_zone_sweep
evaluate(my_model)                                   # 单模型三轴
danger_zone_sweep(model_factory=load_rl_checkpoint)  # 各级 RL checkpoint 扫描
```

## 结构

```
cot_faith/
  dataset.py    Item + 玩具多选集（真实实验换成 BBH/MMLU 子集）
  biases.py     位置/暗示答案/谄媚 偏置注入（真值已知 → 揭示度金标准）
  models.py     Model 协议 + MockModel + HF/OpenAI 适配骨架
  metrics.py    三轴度量
  pipeline.py   evaluate / danger_zone_sweep
run_demo.py     端到端演示
tests/          冒烟测试
```

## 与提案的对应

- 本骨架 = M1「三轴测量工具链 + 偏置注入套件」的可复现起点；
- `danger_zone_sweep` 的 `model_factory` 换成"加载第 t 级 RL checkpoint" = M3 核心实验；
- `content_alignment` 占位待补 activation patching = M4 机制归因。

> 注意边界（提案"哲学余留"）：揭示度只在**已知植入因素**上严格定义；其绝对化受"庄子上界"限制。
