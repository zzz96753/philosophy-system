#!/usr/bin/env python3
"""端到端演示：优化压力扫描，复现提案 H1 的"危险区间"形态（玩具）。

    python run_demo.py

输出三轴随压力的轨迹。注意：MockModel 是**示意性模拟**，不是真实结果；
其作用是验证整条评测流水线可跑，并把"危险区间假说"做成可观察的曲线。
真实实验把 danger_zone_sweep 的 model_factory 换成各级 RL checkpoint 即可。
"""
from cot_faith import danger_zone_sweep


def main():
    rows = danger_zone_sweep()
    cols = ["pressure", "accuracy", "causal_load", "revelation", "content_alignment"]
    print("\n优化压力 × 三轴（玩具示意，MockModel）\n")
    print("  ".join(f"{c:>16}" for c in cols))
    print("-" * 90)
    for r in rows:
        print("  ".join(f"{r[c]:>16.3f}" for c in cols))

    first, last = rows[0], rows[-1]
    print("\n判读：")
    print(f"  accuracy   {first['accuracy']:.2f} -> {last['accuracy']:.2f}  "
          f"({'↑' if last['accuracy'] > first['accuracy'] else '↓'})")
    print(f"  causal_load{first['causal_load']:.2f} -> {last['causal_load']:.2f}  "
          f"({'↑' if last['causal_load'] > first['causal_load'] else '↓'})")
    print(f"  revelation {first['revelation']:.2f} -> {last['revelation']:.2f}  "
          f"({'↓' if last['revelation'] < first['revelation'] else '↑'})")
    danger = (last["accuracy"] >= first["accuracy"]
              and last["causal_load"] >= first["causal_load"]
              and last["revelation"] < first["revelation"])
    print(f"\n  危险区间形态（正确率↑·承载↑·揭示↓）= {'出现' if danger else '未出现'}"
          "  —— 真实模型上能否复现，正是本研究要回答的。")


if __name__ == "__main__":
    main()
