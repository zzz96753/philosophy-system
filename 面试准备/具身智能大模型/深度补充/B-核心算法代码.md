# 深度补充 B · 核心算法代码（PyTorch）

> 面试可能让你"手写个 loss / 写个核心 forward"。以下都是**最小可读实现**，抓住骨架而非工程细节。
> 统一约定：`B`=batch，`T/H`=时间步，`A`=动作维度，`D`=特征维。

---

## 1. CLIP / InfoNCE 对比损失（M2-Q9）

```python
import torch, torch.nn.functional as F

def clip_loss(img_emb, txt_emb, logit_scale):
    # img_emb, txt_emb: (B, D);  logit_scale = exp(可学习温度参数)
    img = F.normalize(img_emb, dim=-1)
    txt = F.normalize(txt_emb, dim=-1)
    logits = logit_scale * img @ txt.t()          # (B, B) 相似度矩阵
    labels = torch.arange(len(img), device=img.device)  # 对角线为正样本
    loss_i2t = F.cross_entropy(logits, labels)
    loss_t2i = F.cross_entropy(logits.t(), labels)
    return (loss_i2t + loss_t2i) / 2
```
要点：归一化→温度缩放→对角线当 label→对称交叉熵。

---

## 2. 动作离散化 / 反离散化（RT-2、OpenVLA，M3-Q16路线A）

```python
import torch

def tokenize_action(a, a_min, a_max, n_bins=256):
    # a: (..., A) 连续动作 -> (..., A) 离散 token id
    a = torch.clamp(a, a_min, a_max)
    norm = (a - a_min) / (a_max - a_min)          # [0,1]
    return torch.clamp((norm * n_bins).long(), 0, n_bins - 1)

def detokenize_action(tok, a_min, a_max, n_bins=256):
    norm = (tok.float() + 0.5) / n_bins           # bin 中心
    return a_min + norm * (a_max - a_min)

# 训练: 对每个动作维度做分类交叉熵
# logits: (B, A, n_bins),  target: (B, A) token id
def action_ce_loss(logits, target):
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)),
                           target.reshape(-1))
```
实务：`a_min/a_max` 常用数据的 1%/99% 分位数（抗离群）。

---

## 3. Diffusion Policy —— 训练步 + 采样（M4-Q25）

```python
import torch, torch.nn as nn, torch.nn.functional as F

class DiffusionPolicy(nn.Module):
    """eps_net(noisy_action_chunk, k, obs) -> 预测噪声"""
    def __init__(self, eps_net, betas):           # betas: (K,)
        super().__init__()
        self.eps_net = eps_net
        alphas = 1.0 - betas
        self.register_buffer('betas', betas)
        self.register_buffer('alphas', alphas)
        self.register_buffer('abar', torch.cumprod(alphas, 0))  # ᾱ_k

    def loss(self, a0, obs):                       # a0: (B,H,A) 专家动作序列
        B, K = a0.size(0), self.betas.size(0)
        k = torch.randint(0, K, (B,), device=a0.device)
        eps = torch.randn_like(a0)
        abar = self.abar[k].view(B, 1, 1)
        a_k = abar.sqrt() * a0 + (1 - abar).sqrt() * eps   # 前向闭式加噪
        eps_pred = self.eps_net(a_k, k, obs)
        return F.mse_loss(eps_pred, eps)           # 预测噪声

    @torch.no_grad()
    def sample(self, obs, shape):                  # 反向去噪采样
        a = torch.randn(shape, device=obs.device)  # x_T ~ N(0,I)
        for k in reversed(range(self.betas.size(0))):
            kk = torch.full((shape[0],), k, device=obs.device)
            eps = self.eps_net(a, kk, obs)
            alpha, abar, beta = self.alphas[k], self.abar[k], self.betas[k]
            mean = (a - (1 - alpha) / (1 - abar).sqrt() * eps) / alpha.sqrt()
            a = mean + (beta.sqrt() * torch.randn_like(a) if k > 0 else 0)
        return a                                   # (B,H,A) 动作序列
# 部署: 取前几步执行, receding horizon 再重采样
```

---

## 4. Flow Matching action head（π0 思路，M3-Q21）

```python
class FlowPolicy(nn.Module):
    """v_net(x_t, t, obs) -> 速度场"""
    def __init__(self, v_net):
        super().__init__(); self.v_net = v_net

    def loss(self, a1, obs):                       # a1: (B,H,A) 数据(专家动作)
        B = a1.size(0)
        a0 = torch.randn_like(a1)                  # 噪声
        t  = torch.rand(B, 1, 1, device=a1.device) # t~U(0,1)
        x_t    = (1 - t) * a0 + t * a1             # 直线路径
        target = a1 - a0                           # 目标速度(常向量)
        return F.mse_loss(self.v_net(x_t, t.view(B), obs), target)

    @torch.no_grad()
    def sample(self, obs, shape, steps=10):        # 解 ODE: dx/dt = v
        x = torch.randn(shape, device=obs.device)
        dt = 1.0 / steps
        for i in range(steps):
            t = torch.full((shape[0],), i * dt, device=obs.device)
            x = x + self.v_net(x, t, obs) * dt     # 欧拉积分
        return x
```
对比 DiffusionPolicy：训练目标从"预测噪声"变"回归速度"，采样几步即可→更快。

---

## 5. ACT 的 CVAE（M4-Q26）

```python
class ACTPolicy(nn.Module):
    def __init__(self, obs_enc, encoder, decoder, A, H, zdim=32):
        super().__init__()
        self.obs_enc = obs_enc                     # 观测编码
        self.encoder = encoder                     # (动作序列, obs) -> mu, logvar
        self.decoder = decoder                     # (obs, z)        -> 动作序列
        self.to_mu  = nn.Linear(encoder.dim, zdim)
        self.to_lv  = nn.Linear(encoder.dim, zdim)

    def forward(self, obs, a_gt=None):
        o = self.obs_enc(obs)
        if a_gt is not None:                       # 训练: 用真值动作推 z
            h = self.encoder(a_gt, o)
            mu, logvar = self.to_mu(h), self.to_lv(h)
            z = mu + torch.exp(0.5 * logvar) * torch.randn_like(mu)  # 重参数化
            a_pred = self.decoder(o, z)
            recon = F.l1_loss(a_pred, a_gt)        # 重建(L1常用)
            kld = -0.5 * torch.mean(1 + logvar - mu**2 - logvar.exp())
            return a_pred, recon + 1e-2 * kld      # beta*KL, beta小
        else:                                      # 推理: z=0(先验均值)
            z = torch.zeros(o.size(0), self.to_mu.out_features, device=o.device)
            return self.decoder(o, z)
# temporal ensemble: 对重叠时间步的多次预测做指数加权平均(略)
```

---

## 6. PPO 损失（M5-Q31）

```python
def ppo_loss(logp, logp_old, adv, value, ret, entropy, clip=0.2, c_v=0.5, c_e=0.01):
    ratio = torch.exp(logp - logp_old)                 # r_t = π/π_old
    adv = (adv - adv.mean()) / (adv.std() + 1e-8)      # 优势归一化
    l_clip = -torch.min(ratio * adv,
                        torch.clamp(ratio, 1 - clip, 1 + clip) * adv).mean()
    l_v = c_v * F.mse_loss(value, ret)                 # 价值回归
    l_e = -c_e * entropy.mean()                        # 熵奖励(鼓励探索)
    return l_clip + l_v + l_e

def compute_gae(rewards, values, gamma=0.99, lam=0.95):
    adv, gae = torch.zeros_like(rewards), 0
    for t in reversed(range(len(rewards))):
        nxt = values[t + 1] if t + 1 < len(values) else 0
        delta = rewards[t] + gamma * nxt - values[t]
        gae = delta + gamma * lam * gae
        adv[t] = gae
    return adv
```

---

## 7. 6D 旋转 → 旋转矩阵（M3 动作姿态 / 数学篇§8）

```python
def rot6d_to_matrix(x):                            # x: (B,6) 网络输出
    a1, a2 = x[:, :3], x[:, 3:]
    b1 = F.normalize(a1, dim=-1)
    a2 = a2 - (b1 * a2).sum(-1, keepdim=True) * b1 # 去掉在 b1 上的分量
    b2 = F.normalize(a2, dim=-1)                    # Gram-Schmidt
    b3 = torch.cross(b1, b2, dim=-1)
    return torch.stack([b1, b2, b3], dim=-1)        # (B,3,3)
```
为什么不用欧拉角/四元数回归：它们到 SO(3) 不连续，网络难拟合（数学篇§8）。

---

## 8. 一个极简 VLA forward（把上面串起来，M3-Q15）

```python
class TinyVLA(nn.Module):
    def __init__(self, vision_enc, text_enc, llm, action_head):
        super().__init__()
        self.vision_enc = vision_enc      # 图像 -> visual tokens (B,Nv,D)
        self.text_enc   = text_enc        # 指令 -> text tokens   (B,Nt,D)
        self.llm        = llm             # Transformer 主干
        self.action_head = action_head    # 取最后隐状态 -> 动作(三选一表示)

    def forward(self, image, instruction, state=None):
        v = self.vision_enc(image)
        t = self.text_enc(instruction)
        tokens = torch.cat([v, t], dim=1)         # 多模态拼接(LLaVA式)
        if state is not None:
            tokens = torch.cat([tokens, state], dim=1)  # 本体状态
        h = self.llm(tokens)                       # (B, N, D)
        return self.action_head(h[:, -1])          # 动作: 离散token/diffusion/flow
```
action_head 三选一即对应 M3-Q16 三条路线：分类头(离散) / MLP(回归) / Diffusion或Flow头(生成式)。

---

### 自测（能默写骨架吗）
- [ ] InfoNCE：归一化→温度→对角label→对称CE
- [ ] 动作离散化的 tokenize/detokenize
- [ ] Diffusion Policy：前向闭式加噪 + 预测噪声loss + 反向采样
- [ ] Flow matching：直线路径 + 速度回归 + ODE采样
- [ ] CVAE：训练推z+重参数化+重建+KL，推理z=0
- [ ] PPO：ratio + clip + 价值 + 熵
- [ ] 6D→矩阵的 Gram-Schmidt
