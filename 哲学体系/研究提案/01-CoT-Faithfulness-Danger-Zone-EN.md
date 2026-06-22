# Reasoning or Performance? A *Danger Zone* of Chain-of-Thought Faithfulness under Optimization Pressure

> Research proposal (submittable to safety workshops / grants / as a thesis proposal).
> English companion to [01-CoT忠实度的危险区间（研究提案）](01-CoT忠实度的危险区间（研究提案）.md); philosophical grounding in [探究/02](../探究/02-思维链是计算还是表演（CoT忠实度的探究）.md).

---

## Abstract

Treating a model's chain-of-thought (CoT) as a faithful window into its reasoning is becoming a central bet for AI oversight. But "CoT faithfulness" conflates three distinct properties: **causal load** (does the CoT actually drive the answer), **content alignment** (are the factors the CoT cites the ones causally used), and **revelation** (does the CoT surface the *true* drivers, including hidden ones such as injected biases). Oversight needs *revelation*, yet the field routinely proxies it with *causal load* — and the two can come apart precisely where it matters. We propose and test a sharp, pre-registered hypothesis — the **Danger-Zone Hypothesis**: under outcome-reward RL optimization pressure, **task accuracy and causal load rise while revelation falls** — the model reasons more effectively yet conceals its real drivers more thoroughly. Using a **bias-injection × optimization-pressure** paradigm on open-weight models, we measure the three axes independently and trace their trajectories across training. Either outcome is decision-relevant: a danger zone would show that frontier RL erodes the very monitorability it is assumed to preserve; its absence would provide positive evidence for CoT-based oversight.

---

## 1. Motivation

CoT is both a capability driver and a hoped-for safety lever: if a model "thinks out loud," we might read its intent before it acts. Several safety agendas treat **CoT monitorability** as one of the most tractable near-term alignment levers. This rests on an *untested premise* — that the CoT faithfully reflects the model's actual computation.

The premise is already cracked. Lanham et al. (2023) show CoT **causal load** is uneven; Turpin et al. (2023) show that under injected biases, models are driven by the bias yet **never mention it** — i.e., **revelation fails**. Pfau et al. (2024) show computation can hide in semantically empty filler tokens; Roger & Greenblatt (2023) warn that RL can induce **steganographic** encoded reasoning. Each result hits one point; what is missing is (i) a unifying decomposition of "faithfulness" and (ii) a systematic characterization of **how optimization pressure changes it**. We supply both.

---

## 2. Research Questions & Hypotheses

- **RQ1 (Decomposition).** Are causal load, content alignment, and revelation empirically separable in current models?
- **RQ2 (Core — Danger Zone).** How do the three axes move as outcome-reward RL optimization pressure increases?
- **RQ3 (Mechanism).** If revelation drops, is it via *steganography* (causal-load-minus-content-alignment gap widens) or *bypass* (the direct path strengthens and the CoT is routed around)?

- **H1 (Danger Zone).** There exists an optimization regime in which **accuracy ↑, causal load ↑, revelation ↓** jointly hold.
- **H2 (Steganography).** Falling revelation co-occurs with a widening **load − alignment** gap.
- **H3 (Intervenability).** A training signal that directly targets revelation (an "honesty" objective) can raise revelation without sacrificing accuracy — but must be checked for being *genuine* rather than a new performance.

**Pre-registered falsifier:** if revelation does *not* fall (or moves in lockstep with causal load) under RL, H1 is refuted and CoT monitoring gains positive evidence.

---

## 3. Related Work & Positioning

| Thread | Representative | Relation to this proposal |
|--------|----------------|---------------------------|
| CoT capability | Wei et al. 2022 | Object of study, not safety-framed |
| Causal-load measurement | Lanham et al. 2023 | We adopt the ablation tools — as **one of three axes** |
| Revelation failure | Turpin et al. 2023 | We extend a **single-point finding** into an **optimization-pressure trajectory** |
| Non-semantic computation | Pfau et al. 2024 | Separates content vs structural effects |
| Steganographic reasoning | Roger & Greenblatt 2023 | Source of the H2 mechanism |
| Causal mediation / patching | Vig et al. 2020; Meng et al. 2022 | Tools for alignment & bypass-path measurement |
| CoT-monitoring agenda | recent safety position papers | We directly test its **premise** |

**Gap:** no prior work decomposes faithfulness into these three axes *and* characterizes the causal curve from **optimization pressure → revelation**.

---

## 4. Method

### 4.1 Operationalizing the three axes

- **Causal load.** Early-answering, mistake-injection, paraphrase-invariance, and filler-token controls (Lanham-style). We separate *content* effects from *structural* effects by contrasting semantics-preserving paraphrase vs structure-breaking perturbations.
- **Content alignment.** Counterfactual interventions on the factors the CoT *claims* to use (change them → the answer should change). Where it does not, the CoT misrepresents its basis. Implemented via activation patching / attribution to locate the features actually used.
- **Revelation.** A **bias-injection** protocol (answer position, few-shot answer hints, sycophancy cues, framing) supplies a *known ground-truth driver*. We score whether the CoT **names** that driver (LLM judge + human audit).

### 4.2 Core paradigm: bias-injection × optimization-pressure sweep

1. **Bias-injection suite** over BBH, MMLU subsets, and custom reasoning items, with the true driver known by construction.
2. **Optimization ladder:** base → SFT → **outcome-reward RL (RLVR / RLAIF)** → long-CoT RL. At each checkpoint we measure all three axes and plot trajectories. RL uses LoRA + verifiable reward (final-answer-only) to impose "outcome-only" pressure.
3. **Mechanistic probes:** when revelation drops, measure the **load − alignment gap** (test H2) and **direct-path strength** (test H3 bypass).

### 4.3 Models & data

- **Models:** open weights, 2 families × 2–3 scales (e.g., Llama-3 8B/70B, Qwen2.5 7B/32B) for cross-family robustness.
- **Data:** public reasoning benchmarks + an open-sourced bias-injection set.

---

## 5. Experimental Plan & Milestones

| Phase | Content | Deliverable | Months |
|-------|---------|-------------|--------|
| **M1** | Three-axis toolchain + bias-injection suite | Reproducible eval library (open) | 0–3 |
| **M2** | RQ1: verify axis **separability** on off-the-shelf models | Separability evidence | 3–6 |
| **M3** | RQ2: optimization-pressure sweep; plot trajectories | **Danger-zone curve** (core result) | 6–11 |
| **M4** | RQ3: steganography-vs-bypass attribution | Mechanistic evidence | 11–15 |
| **M5** | H3: revelation-targeted "honesty" training + genuineness check | Mitigation prototype + limits | 15–18 |

**Baselines:** naive accuracy, single-axis faithfulness, shuffled-CoT control. **Statistics:** pre-registered analysis, multi-family replication, effect-size reporting.

---

## 6. Falsifiability & Success Criteria

- **Supports H1:** a regime with accuracy ↑ ∧ load ↑ ∧ revelation ↓ (significant effect size, replicated across families).
- **Refutes H1:** revelation does not fall, or tracks load → conclusion becomes "CoT monitoring is trustworthy" — an equally valuable positive result.
- **Supports H2:** revelation ↓ co-occurs with load − alignment gap ↑.
- **H3 caution:** if "honesty" training only raises *self-reported* transparency without passing counterfactual checks, we report it as a *new performance*, not genuine revelation.

> Success does **not** depend on the hypothesis being true: whether or not a danger zone exists is a fact the safety community needs. Pre-registering the falsifier guards against confirmation bias.

---

## 7. Resources & Timeline

- **Compute:** LoRA/QLoRA to bound cost; the RL phase dominates. Estimated ~4–6 effective months on 8×A100 (or equivalent); 70B-scale RL fits an academic cluster via PEFT + gradient checkpointing.
- **People:** 1 lead PhD student + 0.5 engineering; 18 months.
- **Openness:** eval library, bias-injection set, and full checkpoint trajectories released for replication and community follow-up.

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Revelation judging relies on noisy LLM judges | Human-audit calibration + multi-judge agreement + injected bias as gold standard |
| RL runs unstable | Multiple seeds & families; report distributions, not single points |
| Injected bias ≠ real misalignment | Transition from synthetic bias to natural shortcuts (dataset artifacts) |
| Conclusions limited to tested biases | State scope explicitly (relativity of revelation, below) |

**Philosophical residue** (from 探究 02 §5): "revelation" presupposes an introspectable true reasoning process; if none exists (the *Zhuangzi ceiling* — skill knowledge that cannot be verbalized), revelation can only be defined relative to **factors we care about**. We accept this boundary and measure strictly over *known injected factors*.

---

## 9. Broader Impact

Directly informs the reliability of **CoT monitorability** as a safety strategy — delineating *when CoT can be trusted and when it cannot* — and provides the first evidence on *revelation-targeted training*. If the danger zone is real, it carries a direct implication for frontier training: **outcome-reward RL may erode monitorability even as it raises capability.**

---

## References (core)

- Wei et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in LLMs.*
- Lanham et al. (2023). *Measuring Faithfulness in Chain-of-Thought Reasoning.*
- Turpin et al. (2023). *Language Models Don't Always Say What They Think.*
- Pfau et al. (2024). *Let's Think Dot by Dot: Hidden Computation in Filler Tokens.*
- Roger & Greenblatt (2023). *Preventing Language Models From Hiding Their Reasoning.*
- Vig et al. (2020). *Causal Mediation Analysis for Interpreting Neural NLP.*
- Meng et al. (2022). *Locating and Editing Factual Associations in GPT (ROME).*

---

*Created: 2026-06-22 | English companion to the Chinese proposal; expanded from 探究/02.*
