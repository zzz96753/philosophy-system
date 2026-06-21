# M10 · 经典论文与 SOTA — 逐题精讲

> 面试官常问"最近读了什么论文""讲讲 XX 工作"。每篇要能讲清：motivation → 方法 → 关键结论 → 局限。

---

## Q59 ★ RT-1 → RT-2 → RT-X 演进脉络

- **RT-1 (2022, Google)**：Robotics Transformer。
  - 做法：Transformer 把图像(EfficientNet+FiLM)+指令 → **离散化动作 token**，模仿学习训练。
  - 数据：13万真机轨迹、700+任务。
  - 贡献：证明 Transformer + 大规模真机数据能学**多任务**策略，有一定泛化。解决"能否用一个模型做很多任务"。
- **RT-2 (2023)**：Vision-Language-Action。
  - 做法：把动作 token 接到**预训练 VLM**（PaLI-X/PaLM-E）上，co-fine-tuning。
  - 贡献：迁移互联网视觉语言知识→**语义泛化与推理**（懂新概念、常识）。解决"如何获得开放世界泛化"。
- **RT-X / Open X-Embodiment (2023)**：
  - 做法：联合 22 种本体、100万+轨迹共训 RT-1-X / RT-2-X。
  - 贡献：证明**跨本体共训正迁移**。解决"如何扩大数据规模"。
- 主线：**多任务(RT-1) → 语义泛化(RT-2) → 跨本体规模化(RT-X)**。

---

## Q60 ★ OpenVLA

- **Motivation**：RT-2 闭源巨大，社区需要开源可复现的 VLA。
- **方法**：Prismatic VLM = **SigLIP + DINOv2 双视觉编码器**（语义+空间细节）+ Llama2-7B；动作走离散 token 自回归；在 Open X-Embodiment 97万轨迹训练。
- **结论**：7B 超 55B RT-2-X 成功率；支持 LoRA 高效微调、量化部署。
- **局限**：离散动作、推理慢、单步预测（无 chunking 原版）。成了学术最常用 baseline。

---

## Q61 ★ π0 / π0.5（Physical Intelligence）

- **π0**：VLM(PaliGemma) + **action expert**，用 **flow matching** 输出连续高频动作 chunk（50Hz）。在大规模多样数据上预训练，能做叠衣服、打包等灵巧长程任务。卖点：通用 + 连续动作 + 快。
- **π0.5**：强调**开放世界泛化**（到没见过的家庭环境），用分层（高层语义子任务 + 低层 flow 动作）+ co-training 异构数据。
- 意义：代表"VLM 语义 + 生成式连续动作 + 分层"的工业 SOTA 路线。

---

## Q62 RDT-1B（清华）

- **Motivation**：双臂灵巧操作 + 扩大模型与数据。
- **方法**：**Diffusion + Transformer** 的 1.2B 大模型（当时最大扩散策略），统一异构机器人动作空间，多机器人数据预训练 + 少量双臂数据微调。
- **贡献**：扩散策略 scale 到 10亿级、双臂协调、强 zero-shot 泛化。

---

## Q63 Octo

- **方法**：开源**通用机器人策略 Transformer**，在 Open X-Embodiment 80万轨迹训练；**模块化设计**——支持灵活接入不同观测（多相机、本体）和动作空间，用 **diffusion action head**。
- **取舍**：相对轻量、易微调适配新机器人；偏 generalist policy，不依赖大 VLM backbone。

---

## Q64 ☆ 其他前沿（卖点速记）

- **Gemini Robotics (DeepMind)**：基于 Gemini 多模态，强语义推理 + VLA；Gemini Robotics-ER 强空间推理（embodied reasoning）。
- **GR00T (NVIDIA)**：人形机器人通用基础模型，配 Isaac 仿真 + 合成数据生成；双系统架构。
- **Helix (Figure)**：人形 VLA，**system1/system2**——S2(7-9Hz语义) + S1(200Hz控制)，单网络控制上半身高自由度。
- **Genie / world models**：交互式可玩世界模型，生成可控环境。

---

## Q65 ☆ Diffusion Policy & ACT（必须默写，详见 M4）

- **Diffusion Policy**：条件去噪扩散生成动作序列，建模多模态分布，receding horizon。
- **ACT**：Transformer CVAE + action chunking + temporal ensemble，ALOHA 精细操作。

---

## Q66 ◆ 讲一篇你最近读的论文（答题框架）

四段式，务必准备 1-2 篇能深聊：
1. **Motivation**：它要解决什么问题，之前方法的缺陷。
2. **Method**：核心方法（一句话抓本质 + 关键设计）。
3. **Experiments**：在什么 benchmark、和谁比、关键结论数字。
4. **批判**：局限、你的质疑、可改进点、你会怎么 follow up。
> 加分：能把它放进领域脉络（"它是 RT-2 之后解决推理慢的尝试"），并联系你自己的项目。

---

### 本模块自测
- [ ] RT-1/2/X 每步解决什么（多任务/语义/跨本体）
- [ ] OpenVLA 双编码器 + 关键结论
- [ ] π0 的 flow matching action expert
- [ ] RDT 的 diffusion+大模型 + 双臂
- [ ] Octo 的模块化 generalist 设计
- [ ] 准备好 1-2 篇论文用四段式深聊
