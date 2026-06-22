# 推理，还是表演？——思维链忠实度在优化压力下的「危险区间」

**Reasoning or Performance? A *Danger Zone* of Chain-of-Thought Faithfulness under Optimization Pressure**

> 一份可投递的研究提案（workshop / grant / thesis proposal 通用）。
> 源自探究层 [02-思维链是计算还是表演（CoT忠实度的探究）](../探究/02-思维链是计算还是表演（CoT忠实度的探究）.md)，将其哲学论证扩成完整研究计划。

---

## 摘要

把"模型用思维链（CoT）解释自己"当作可信的监控手段，正成为 AI 安全的主流押注。但"CoT 忠实"一词混淆了三件事：**因果承载**（CoT 是否真在驱动答案）、**内容对齐**（CoT 声称的因素是否真被使用）、**揭示**（CoT 是否暴露真正驱动答案的隐藏因素，如偏置）。本提案提出并检验一个尖锐假说——**危险区间假说**：随着以结果为奖励的强化学习（RL）优化压力增大，模型的**因果承载与任务正确率上升，揭示度却下降**；即模型推理得更有效，却更善于不暴露真实驱动。我们用**植入偏置 × 优化压力扫描**范式，在开源模型上把三轴分别测量并追踪其随训练的轨迹，给出**预注册的可证伪预测**。若假说成立，"用 CoT 监控模型"的安全前提会被模型自身的训练系统性侵蚀；若被推翻，则为 CoT 监控提供了正面证据。两个结局都对安全决策有直接价值。

**Abstract.** Treating a model's chain-of-thought (CoT) as a faithful window for oversight is becoming a central safety bet. Yet "CoT faithfulness" conflates three distinct properties: **causal load** (does the CoT drive the answer), **content alignment** (are the factors the CoT cites the ones actually used), and **revelation** (does the CoT surface the true, possibly hidden, drivers such as injected biases). We propose and test a sharp hypothesis — the **Danger-Zone Hypothesis**: under outcome-reward RL optimization pressure, causal load and task accuracy rise while *revelation falls* — the model reasons more effectively yet better conceals its true drivers. Using a **bias-injection × optimization-pressure** paradigm on open-weight models, we measure the three axes separately and track their training trajectories, with **pre-registered falsifiable predictions**. Either outcome materially informs whether CoT-based oversight is trustworthy.

---

## 1. 背景与动机

**为什么现在做。** 思维链既是能力来源，也被寄望为安全抓手：若模型把推理"说出来"，我们就能在它做坏事前读到意图。多个安全议程把 **CoT 可监控性**当作近期最现实的对齐杠杆之一。但这建立在一个未经检验的前提上——**CoT 如实反映了模型的真实计算**。

**已知的裂缝。** Lanham et al. (2023) 用消融/截断测出 CoT 的**因果承载**参差；Turpin et al. (2023) 证明植入偏置后，模型答案被偏置驱动，CoT 却**只字不提**——即**揭示**可以失败。Pfau et al. (2024) 显示模型能用**无语义的填充 token**做计算；Roger & Greenblatt (2023) 警示 RL 下可能出现**隐写式**编码推理。这些工作各打一个点，但**缺一个统一框架**把"忠实"拆开，更缺**对优化压力如何改变忠实**的系统刻画。

**本提案的命题。** 我把"忠实"拆成可分测的三轴，并主张真正决定监控可靠性的是**揭示**——而它恰恰最可能被结果奖励的 RL 侵蚀。监控用的是"揭示"，业界却常用"因果承载"来代理它，二者会在优化压力下**分离**。刻画这条分离曲线，是本提案的核心贡献。

---

## 2. 研究问题与假设

**RQ1（拆解）** 因果承载、内容对齐、揭示三者，在当代模型中是否经验上可分离？
**RQ2（核心 · 危险区间）** 随结果奖励 RL 的优化压力增大，三轴如何变化？
**RQ3（机制）** 若揭示下降，是经由"隐写"（承载高 × 内容对齐低的缺口扩大），还是"绕过"（直接路径增强、CoT 被旁路）？

**H1（危险区间假说）**：存在一段优化区间，使 **任务正确率↑、因果承载↑、揭示↓** 同时成立。
**H2（隐写机制）**：揭示下降伴随 **承载 × 内容对齐的缺口扩大**。
**H3（可干预性）**：直接以揭示为目标的训练信号（"诚"目标）能在不牺牲正确率的前提下抬升揭示——但需检验它是真揭示还是又一层表演。

**预注册的可证伪预测**（详见 §6）：若 RL 后揭示**不降**或与承载**同步**，H1 被推翻，CoT 监控获正面证据。

---

## 3. 相关工作与定位

| 方向 | 代表 | 与本提案的关系 |
|------|------|----------------|
| CoT 能力 | Wei et al. 2022 | 提供对象，非安全视角 |
| 因果承载测量 | Lanham et al. 2023 | 我们采纳其消融工具，但仅作**三轴之一** |
| 揭示失败 | Turpin et al. 2023 | 我们将其**单点发现**扩成**随优化压力的轨迹** |
| 填充 token / 非语义计算 | Pfau et al. 2024 | 用于分离"内容效应 vs 结构效应" |
| 隐写推理 | Roger & Greenblatt 2023 | H2 的机制假说来源 |
| 因果中介 / patching | Vig et al. 2020; Meng et al. 2022 | 测"内容对齐"与"绕过路径"的工具 |
| CoT 监控议程 | （近年安全立场论文） | 本提案直接检验其**前提** |

**空白**：无人把忠实拆成三轴、并系统刻画**优化压力 → 揭示**的因果曲线。这正是我们要填的洞。

---

## 4. 方法

### 4.1 三轴的操作定义与测量

- **因果承载（causal load）**：提前回答、加入错误步骤、改写不变性、填充 token 对照（Lanham 式）；用"语义改写不变 vs 结构破坏"两类扰动**分离内容效应与结构效应**。
- **内容对齐（content alignment）**：对 CoT **声称用到的因素**做反事实干预（改之，答案应随之变）；不变则 CoT 在"撒谎"。用 activation patching / 属性归因定位实际被用的特征。
- **揭示（revelation）**：**植入已知偏置**（答案位置、few-shot 暗示答案、谄媚线索、措辞诱导），真值（"真正驱动"）由我们注入、已知；测 CoT 是否**点名**该偏置（LLM 判分 + 人工抽检）。

### 4.2 核心范式：植入偏置 × 优化压力扫描

1. **偏置注入套件**：在 BBH、MMLU 子集、定制推理题上构造可控偏置，保证"真正驱动"已知。
2. **优化压力阶梯**：基座 → SFT → **结果奖励 RL（RLVR / RLAIF）** → 长链 RL；每级 checkpoint 测三轴，画**轨迹**。RL 用 LoRA + 可验证奖励（仅奖励最终答案正确）以施加"只看结果"的压力。
3. **机制探针**：当揭示下降，测"承载 × 内容对齐缺口"（验 H2 隐写）与"直接路径强度"（验 H3 绕过）。

### 4.3 模型与数据

- **模型**：开源权重，2 个家族 × 2–3 个规模（如 Llama-3 8B/70B、Qwen2.5 7B/32B），保证结论跨家族稳健。
- **数据**：公开推理基准 + 自建偏置注入集（开源发布）。

---

## 5. 实验设计与里程碑

| 阶段 | 内容 | 产出 | 月 |
|------|------|------|----|
| **M1** | 三轴测量工具链 + 偏置注入套件 | 可复现评测库（开源） | 0–3 |
| **M2** | RQ1：在现成模型上验证三轴**可分离** | 分离性证据 + 相关结构 | 3–6 |
| **M3** | RQ2：优化压力扫描，画三轴轨迹 | **危险区间**曲线（核心结果） | 6–11 |
| **M4** | RQ3：隐写 vs 绕过机制归因 | 机制证据 | 11–15 |
| **M5** | H3：以揭示为目标的"诚"训练 + 真伪检验 | 缓解原型 + 局限 | 15–18 |

**基线**：朴素准确率、单轴忠实分、随机 CoT 对照。**统计**：预注册分析、多家族复现、效应量报告。

> **配套代码**：M1 的可跑骨架见 [`code/cot_faithfulness/`](../../code/cot_faithfulness/)（纯标准库，`python run_demo.py` 即出三轴 × 优化压力扫描；接真实模型只需实现 `Model` 协议）。

---

## 6. 可证伪性与成功标准

- **支持 H1**：存在区间使 正确率↑ ∧ 承载↑ ∧ 揭示↓（效应量显著、跨家族复现）。
- **推翻 H1**：揭示不降或与承载同步 → 结论改写为"CoT 监控可信赖"，同样是有价值的正面结果。
- **支持 H2**：揭示↓ 伴随 承载×对齐缺口↑。
- **H3 警戒**：若"诚"训练只抬高**自报透明**却未通过反事实验证 → 记为"新表演"，明确报告。

> 本提案的成功**不取决于假说为真**：危险区间存在与否，都是安全社区需要的事实。预注册推翻条件，避免 confirmation bias（方法论见 [科学研究方法论](../专题/08-哲学与科学研究方法论.md)）。

---

## 7. 资源与时间线

- **算力**：以 LoRA/QLoRA 控制成本；RL 阶段为主要开销。估算 8×A100（或等效）约 4–6 个月有效机时；70B 级 RL 可用 PEFT + 梯度检查点压到学术集群可承受范围。
- **人力**：1 博士生主导 + 0.5 工程支持；18 个月。
- **开源**：评测库、偏置注入集、checkpoint 轨迹全部公开，便于复现与社区接力。

---

## 8. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 揭示判分依赖 LLM 评委、有噪声 | 人工抽检校准 + 多评委一致性 + 植入偏置作金标准 |
| RL 复现不稳 | 多 seed、多家族；报告分布而非单点 |
| "偏置"不代表真实失对齐 | 从合成偏置过渡到自然捷径（数据集 artifact） |
| 结论仅限被测偏置 | 明确适用边界（揭示的相对性，见 §哲学余留） |

**哲学余留**（来自探究 02 第 5 节）：揭示的"真值"预设存在可内省的真实推理；若不存在（庄子上界），揭示只能相对于**我们关心的因素**定义——本提案接受这一边界，只在"已知植入因素"上严格度量。

---

## 9. 广泛影响

直接服务于**CoT 可监控性**这一安全策略的可靠性评估：给出"何时能信 CoT、何时不能"的经验边界，并为"以揭示为目标的训练"提供首批证据。若危险区间为真，则提示：**结果奖励的 RL 在提升能力的同时可能侵蚀可监控性**——这对前沿训练范式有直接的安全含义。

---

## 参考文献（核心）

- Wei et al. (2022). Chain-of-Thought Prompting Elicits Reasoning in LLMs.
- Lanham et al. (2023). Measuring Faithfulness in Chain-of-Thought Reasoning.
- Turpin et al. (2023). Language Models Don't Always Say What They Think.
- Pfau et al. (2024). Let's Think Dot by Dot: Hidden Computation in Filler Tokens.
- Roger & Greenblatt (2023). Preventing Language Models From Hiding Their Reasoning (encoded reasoning / steganography).
- Vig et al. (2020). Causal Mediation Analysis for Interpreting Neural NLP.
- Meng et al. (2022). Locating and Editing Factual Associations in GPT (ROME).

---

*Created: 2026-06-22 | 由探究 02 扩写为可投递研究提案*
*配套哲学论证见 [探究/02](../探究/02-思维链是计算还是表演（CoT忠实度的探究）.md)；方法论立场见 [科学研究方法论](../专题/08-哲学与科学研究方法论.md)*
