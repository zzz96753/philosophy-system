# 01 · Transformer 与注意力机制

> 大模型面试的绝对核心。能不能讲清楚 Attention，基本决定第一印象。

---

## 一、核心概念

### Self-Attention（自注意力）

对每个 token，用它的 Query 去和所有 token 的 Key 算相似度，得到注意力权重，再对 Value 加权求和。

$$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

- $Q = XW_Q,\ K = XW_K,\ V = XW_V$
- $QK^\top$：token 两两相似度，形状 $(n, n)$
- $\sqrt{d_k}$：缩放因子，防止点积过大导致 softmax 梯度消失
- softmax 沿 key 维度归一化为权重

### Multi-Head Attention（多头）

把 $d_{model}$ 拆成 $h$ 个头，每个头在低维子空间独立做 attention，再拼接经线性层融合。
直觉：不同头可学习不同的关系（句法、指代、距离等）。

$$\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1,...,\text{head}_h)W_O$$

### Transformer Block 组成

```
x → LayerNorm → Multi-Head Attention → 残差相加
  → LayerNorm → FFN(两层MLP, 中间维度4d) → 残差相加
```

- **残差连接**：缓解深层梯度消失，保证信息直通
- **LayerNorm**：稳定训练（现代 LLM 多用 Pre-LN：先 Norm 再进子层，更稳）
- **FFN**：逐位置的非线性变换，参数量大头所在

---

## 二、面试高频问答

**Q1：为什么 attention 要除以 √d_k？**
点积 $QK^\top$ 的方差随维度 $d_k$ 线性增长。维度大时点积数值大，softmax 进入饱和区（一个值接近 1，其余接近 0），梯度趋近 0，难以训练。除以 √d_k 把方差归一化回 1 量级，保持梯度健康。

**Q2：为什么要多头，而不是一个大头？**
- 让模型在多个表示子空间并行关注不同类型的信息
- 单头容易把所有关系平均掉；多头提供「集成」效果
- 计算量与单个大头相当（总维度不变），但表达更丰富

**Q3：self-attention 的时间/空间复杂度？**
$O(n^2 d)$，其中 $n$ 是序列长度。注意力矩阵 $n \times n$ 是长上下文的瓶颈，催生了 FlashAttention（IO 优化，不降复杂度）、稀疏/线性注意力等。

**Q4：FlashAttention 解决了什么？**
标准实现要把 $n\times n$ 的注意力矩阵写回显存（HBM），IO 开销大。FlashAttention 用分块（tiling）+ online softmax，在 SRAM 内计算，不显式存储完整矩阵，显著减少 HBM 读写，加速且省显存。**复杂度不变，但常数和显存大幅下降。**

**Q5：Encoder 和 Decoder 的 attention 有何不同？**
- Encoder：双向自注意力，每个 token 可看全序列
- Decoder：因果（causal）掩码自注意力，只能看自己及之前的 token（防止信息泄露）；外加 cross-attention 关注 encoder 输出
- GPT 类是 Decoder-only，BERT 类是 Encoder-only，T5 是 Encoder-Decoder

**Q6：为什么现代 LLM 普遍用 Pre-LN 而非原始的 Post-LN？**
Post-LN（残差后归一化）深层时梯度不稳，需要 warmup 才能训。Pre-LN（子层前归一化）让残差路径是「干净」的恒等映射，梯度更稳，可去掉/减少 warmup，更易 scale 到很深。代价是表达能力略有损失，部分工作用 DeepNorm 等折中。

---

## 三、追问陷阱

- **「softmax 之后为什么乘 V 而不是别的？」** → V 是「内容/信息」，权重决定从哪些 token 取多少信息，加权求和即上下文聚合。
- **「causal mask 具体怎么实现？」** → 在 $QK^\top$ 上对未来位置加 $-\infty$，softmax 后权重为 0。
- **「多头拼接后维度怎么对齐？」** → 每头维度 $d_k = d_{model}/h$，拼接后恰好回到 $d_{model}$，再过 $W_O$。
- **「LayerNorm 和 BatchNorm 为什么 NLP 用前者？」** → 序列长度可变、batch 内样本不同长，BN 的 batch 统计量不稳；LN 对单样本特征维归一化，与 batch 无关。

---

## 四、手撕准备

能在白板写出：
- scaled dot-product attention 的前向（含 mask）
- multi-head 的 reshape / transpose 维度变换
- 见 `04-高频面试题/03-手撕代码题.md`
