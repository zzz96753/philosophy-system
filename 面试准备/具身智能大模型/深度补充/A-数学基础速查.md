# 深度补充 A · 数学基础速查（具身大模型）

> 面试常被追问"推导一下""为什么是这个公式"。本篇覆盖必须能手推的核心数学。
> 记号：x 向量，⊙ 逐元素乘，‖·‖ L2 范数，E 期望，∼ 采样自。

---

## 1. 注意力机制（Attention）

$$\text{Attn}(Q,K,V)=\text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

- Q,K,V 由输入线性投影：$Q=XW_Q$ 等，形状 $(n, d_k)$。
- **为什么除 $\sqrt{d_k}$**：若 q,k 各维独立、均值0方差1，则点积 $q\cdot k=\sum_{i=1}^{d_k} q_i k_i$ 的方差为 $d_k$。不缩放则 softmax 进入饱和区、梯度消失。除以 $\sqrt{d_k}$ 使方差回到 1。
- **复杂度** $O(n^2 d)$：这就是为什么 visual token 多了会爆（M2-Q11）。
- 多头：把 $d$ 切成 $h$ 份并行做注意力再拼接，让模型关注不同子空间。

---

## 2. 对比学习 / InfoNCE（CLIP 的数学）

一个 batch 有 $N$ 个图文对。图像、文本各自编码并 **L2 归一化** 得 $\{u_i\},\{v_i\}$。相似度用余弦（归一化后即点积），温度 $\tau$：

$$\ell_i^{\text{(i2t)}}=-\log\frac{\exp(u_i\!\cdot\! v_i/\tau)}{\sum_{j=1}^{N}\exp(u_i\!\cdot\! v_j/\tau)}$$

对称地再算文本→图像 $\ell_i^{\text{(t2i)}}$，总损失：

$$\mathcal{L}=\frac{1}{2N}\sum_{i=1}^{N}\big(\ell_i^{\text{(i2t)}}+\ell_i^{\text{(t2i)}}\big)$$

- 本质是 **N 分类的交叉熵**，正样本是对角线（label = i），负样本是 batch 内其它。
- **温度 $\tau$**：小→分布尖锐、强调难负样本；CLIP 用可学习的 $\log(1/\tau)$ 并裁剪。
- 这是 M2-Q9。负样本越多（大 batch）效果越好。

---

## 3. 扩散模型（DDPM）—— Diffusion Policy 的地基

**前向加噪**（固定，无参数），方差表 $\{\beta_t\}_{t=1}^T$，记 $\alpha_t=1-\beta_t,\ \bar\alpha_t=\prod_{s=1}^t\alpha_s$：

$$q(x_t\mid x_{t-1})=\mathcal N(\sqrt{\alpha_t}\,x_{t-1},\ \beta_t I)$$

闭式（任意 t 一步到位，训练关键）：

$$\boxed{x_t=\sqrt{\bar\alpha_t}\,x_0+\sqrt{1-\bar\alpha_t}\,\varepsilon,\quad \varepsilon\sim\mathcal N(0,I)}$$

**训练目标**（预测噪声，DDPM 简化损失）：

$$\mathcal L=\mathbb E_{x_0,\varepsilon,t}\big\|\varepsilon-\varepsilon_\theta(x_t,t)\big\|^2$$

**反向去噪采样**（从 $x_T\sim\mathcal N(0,I)$ 迭代到 $x_0$）：

$$x_{t-1}=\frac{1}{\sqrt{\alpha_t}}\Big(x_t-\frac{1-\alpha_t}{\sqrt{1-\bar\alpha_t}}\,\varepsilon_\theta(x_t,t)\Big)+\sigma_t z,\quad z\sim\mathcal N(0,I)$$

- **用在 Diffusion Policy**：把 $x$ 换成**动作序列** $a_{t:t+H}$，网络额外条件于**观测** $o$：$\varepsilon_\theta(a^k, k, o)$（$k$ 是去噪步）。
- 与 **score** 的关系：$\nabla_x\log q(x_t)\approx-\varepsilon_\theta/\sqrt{1-\bar\alpha_t}$，所以"预测噪声"≈"学分数"（score matching）。
- 为什么能建模**多模态动作分布**（M4-Q27）：扩散是从噪声采样的生成模型，能覆盖多峰，而 MSE 回归只给条件均值。
- 加速：DDIM（确定性、跳步）、一致性模型、或直接换 flow matching。

---

## 4. Flow Matching（π0 的动作生成）

学一个**速度场** $v_\theta(x,t)$，把噪声分布连续地"流"成数据分布。用**条件最优传输路径**（直线插值），$x_0\sim\mathcal N(0,I)$ 噪声、$x_1$ 数据：

$$x_t=(1-t)\,x_0+t\,x_1,\qquad t\in[0,1]$$

该直线路径的**目标速度**是常向量 $x_1-x_0$。**训练损失**（回归速度）：

$$\mathcal L=\mathbb E_{t,x_0,x_1}\big\|v_\theta(x_t,t)-(x_1-x_0)\big\|^2$$

**采样**：解 ODE $\dfrac{dx}{dt}=v_\theta(x,t)$，从 $x_0$ 积分到 $t=1$（欧拉法几步即可）。

- 相比 diffusion：路径是直线、采样步数少→**推理快**（M3-Q21）。
- 用在 VLA：$x$=动作 chunk，$v_\theta$ 额外条件于观测/语言 token。

---

## 5. VAE / CVAE（ACT 的数学）

**ELBO**（证据下界）：

$$\log p(x)\ge \underbrace{\mathbb E_{q(z|x)}[\log p(x|z)]}_{\text{重建}}-\underbrace{\mathrm{KL}\big(q(z|x)\,\|\,p(z)\big)}_{\text{正则到先验}}$$

- 先验 $p(z)=\mathcal N(0,I)$；编码器输出 $\mu,\sigma$。
- **重参数化技巧**（让采样可导）：$z=\mu+\sigma\odot\varepsilon,\ \varepsilon\sim\mathcal N(0,I)$。
- 两高斯 KL 闭式：$\mathrm{KL}=\tfrac12\sum_i(\mu_i^2+\sigma_i^2-\log\sigma_i^2-1)$。
- **CVAE（ACT）**：编码器/解码器都**条件于观测** $o$。训练时 encoder 用动作序列推 $z$（捕捉人类示范多模态/风格），decoder $p(a_{t:t+H}\mid o,z)$ 重建；**推理时 $z=0$（先验均值）**，只跑 decoder。$z$ 的作用就是吸收"同一观测下不同人的不同动作"这种多模态性，避免回归取平均（M4-Q26/Q27）。

---

## 6. 强化学习核心公式

**回报与价值**：$G_t=\sum_{k\ge0}\gamma^k r_{t+k}$，$V^\pi(s)=\mathbb E[G_t|s_t=s]$，$Q^\pi(s,a)=\mathbb E[G_t|s_t=s,a_t=a]$。

**Bellman**：$Q^\pi(s,a)=\mathbb E_{s'}[r+\gamma\,\mathbb E_{a'\sim\pi}Q^\pi(s',a')]$。

**策略梯度**（REINFORCE/Actor-Critic）：

$$\nabla_\theta J=\mathbb E\big[\nabla_\theta\log\pi_\theta(a|s)\,A(s,a)\big],\quad A=Q-V\ (\text{优势})$$

**GAE**（优势估计）：$\hat A_t=\sum_{l\ge0}(\gamma\lambda)^l\delta_{t+l}$，$\delta_t=r_t+\gamma V(s_{t+1})-V(s_t)$。

**PPO 裁剪目标**（on-policy，M5-Q31）：令 $r_t(\theta)=\dfrac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}$，

$$L^{\text{CLIP}}=\mathbb E\big[\min\big(r_t\hat A_t,\ \text{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t\big)\big]$$

裁剪防止单步更新过大，是 PPO 稳定的关键。

**SAC 最大熵**（off-policy，样本高效）：目标加熵项 $\mathbb E[\sum_t r_t+\alpha\,\mathcal H(\pi(\cdot|s_t))]$，鼓励探索，$\alpha$ 可自动调。

---

## 7. 行为克隆的复合误差界（BC 为什么 $O(\epsilon T^2)$）

设策略在专家分布下每步犯错概率 $\le\epsilon$（0-1 损失）。一旦犯错就可能进入训练never见过的状态，后续不再有保证。Ross & Bagnell 的结论：

$$J(\pi_{\text{BC}})-J(\pi^*)=O(\epsilon T^2)$$

直觉：第 t 步首次出错的概率 $\sim\epsilon$，之后 $\sim(T-t)$ 步全程"自由落体"，求和得 $T^2$ 量级。**DAgger** 让训练分布覆盖策略自身访问的状态，把界改善到 $O(\epsilon T)$（M4-Q23/Q24）。这是"为什么要 action chunking / DAgger / 闭环"的理论根。

---

## 8. 旋转表示（动作里最容易被深挖的数学）

机器人动作含姿态，神经网络**怎么表示旋转**很关键。

| 表示 | 维度 | 优点 | 坑 |
|------|------|------|----|
| 欧拉角 | 3 | 直观 | **万向锁(gimbal lock)**、不连续 |
| 轴角/旋转向量 | 3 | 紧凑、指数映射 | $2\pi$ 处不连续 |
| 四元数 | 4 | 无万向锁、插值好(slerp) | 单位约束、**双重覆盖** $q\equiv-q$ |
| 旋转矩阵 | 9 | 无歧义 | 需正交约束 |
| **6D 表示** | 6 | **连续、适合网络回归** | 需 Gram-Schmidt 还原 |

- **为什么网络回归旋转推荐 6D**（Zhou et al. 2019）：欧拉角/四元数在 SO(3) 上的映射**不连续**，网络难拟合（输出突变）。6D 表示取旋转矩阵前两列 $[a_1,a_2]$，用 **Gram-Schmidt** 正交化还原：

$$b_1=\frac{a_1}{\|a_1\|},\quad b_2=\frac{a_2-(b_1\!\cdot\!a_2)b_1}{\|a_2-(b_1\!\cdot\!a_2)b_1\|},\quad b_3=b_1\times b_2,\quad R=[b_1\,b_2\,b_3]$$

  这个映射连续，回归误差更小。很多操作策略/抓取网络用它。
- **四元数双重覆盖**：$q$ 和 $-q$ 表示同一旋转，做回归 loss 时要取 $\min(\|q-\hat q\|,\|q+\hat q\|)$ 或用测地距离。
- **指数映射**：轴角 $\boldsymbol\omega$（轴×角）↔ 旋转矩阵 $R=\exp([\boldsymbol\omega]_\times)$（Rodrigues 公式），SE(3)/李代数在控制与位姿优化里常用。

---

## 9. 动作离散化（tokenization）的数学（RT-2/OpenVLA）

把连续动作维度 $a\in[a_{\min},a_{\max}]$ 均匀分成 $B$ 个 bin：

$$\text{token}(a)=\left\lfloor \frac{a-a_{\min}}{a_{\max}-a_{\min}}\cdot B\right\rfloor,\quad \hat a=a_{\min}+\frac{\text{token}+0.5}{B}(a_{\max}-a_{\min})$$

- 量化误差 $\le\frac{a_{\max}-a_{\min}}{2B}$，所以 bin 越多越精但词表越大。OpenVLA 用 256 bin，并常用**分位数归一化**（按数据分布的 1%~99% 分位裁剪）抵抗离群值。
- 训练就是对 token 做**交叉熵**（分类），而非回归——这让动作能复用 LLM 的词表与自回归框架（M3-Q16 路线A）。

---

### 自测（能手推/手画吗）
- [ ] attention 为何除 $\sqrt{d_k}$（方差论证）
- [ ] 写出 InfoNCE 对称损失
- [ ] DDPM 前向闭式 + 噪声预测损失 + 反向采样
- [ ] flow matching 的直线路径、目标速度、ODE 采样
- [ ] CVAE 的 ELBO + 重参数化 + ACT 里 z 的作用
- [ ] PPO 裁剪目标，r_t 是什么
- [ ] BC 为何 $O(\epsilon T^2)$，DAgger 为何 $O(\epsilon T)$
- [ ] 6D 旋转表示为何连续、Gram-Schmidt 还原
