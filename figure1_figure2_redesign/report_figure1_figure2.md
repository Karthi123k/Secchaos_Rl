# Scientific Redesign Report: Figure 1 and Figure 2

**Manuscript Title:** SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos  
**Target Venue:** *Software: Practice and Experience* (Wiley) / IEEE TSE / ACM TOSEM  
**Date:** 2026-10-27  
**Design Lead:** Senior Scientific Visualization Designer & Software Security Researcher  

---

## 1. Executive Summary

This report documents the graphical redesign of **Figure 1** (Overall Framework Architecture) and **Figure 2** (Deep Policy Network Architecture) for the SecChaos-RL manuscript.

### Identified Weaknesses in Earlier Diagrams:
1. **Infographic Style:** Earlier figures relied on raster images with paragraphs of text enclosed inside rectangular containers, resembling marketing slides rather than peer-reviewed scientific systems schematics.
2. **Obscured Control vs. Data Plane:** The physical telemetry stream, chaos fault ingress, action dispatch, and offline policy training were not clearly separated.
3. **Lack of Native Vector Scalability:** Earlier diagrams suffered from font blurring and unreadable labels at normal two-column journal widths.

### Redesign Approach:
Both figures were completely reconstructed in **native LaTeX TikZ**, strictly following the implementation in [`secchaos_framework.py`](file:///home/karthik/Desktop/Secchaos_Rl/revised_manuscript/experiments/secchaos_framework.py) and the mathematical formulations in the manuscript. They have been compiled to standalone vector PDFs and W3C-compliant SVGs, and fully integrated into the revised Wiley manuscript.

---

## 2. Redesign Details for Figure 1: Overall SecChaos-RL Framework

Figure 1 (`figure1_secchaos_framework.pdf`) presents the full closed-loop methodology across five horizontal functional regions:

```
[ Region A: System Under Test ]  --> [ Region B: Security Chaos ]  --> [ Region C: DRL Controller ]  --> [ Region D: Mitigation & Queue ]  --> [ Region E: Evaluation & PPO ]
             ^                                                                                                   |                                           |
             |================================ Active Service Healing Loop ======================================|                                           |
             |                                                                                                                                               |
             |----------------------------------- PPO Policy Gradient Parameter Updates ---------------------------------------------------------------------|
```

### Visual Enhancements by Region:
- **Region A (Microservices & Telemetry):**
  - Modeled as a connected Directed Acyclic Graph (DAG) consisting of the exact 7 services from `DependencyGraph`: `Gateway`, `Authentication`, `User`, `Order`, `Payment`, `Inventory`, and `Notification`.
  - Directed arrows represent synchronous REST/gRPC API invocations.
  - Cascading failure propagation is explicitly marked: $\gamma = 0.50$ when upstream risk $r(u) > 0.35$.
  - Compact telemetry probe cards capture ingress latency ($\mu$), Istio 5xx errors ($\epsilon$), and host CPU/RAM utilization ($\rho$).
- **Region B (Security Chaos & Threat Assessment):**
  - Renders the Security Chaos Engine (SCE) generating faults via Poisson processes ($\lambda_k \in [0.05, 0.25]$) with durations $\Delta t$ and severities $\sigma$.
  - Replaced descriptive paragraphs with a compact graphical taxonomy of 8 standardized security faults ($F_1$--$F_8$): TLS expiration, vulnerable dependency, secret leak, RBAC misconfiguration, weak authentication, root privilege, unpatched CVE, and open debug API.
  - Dynamic Threat Evaluator computes cluster vulnerability $V_t$ and continuous logistic severity $\mathcal{L}_{\mathrm{threat}} \in [0, 1]$.
  - State Monitor aggregates microservice telemetry and threat level into the standardized 16-D state vector $\mathbf{s}_t \in \mathbb{R}^{16}$.
- **Region C: Threat-Aware RL Controller:**
  - Visual signal pipeline: Observation vector $\mathbf{s}_t \to$ Linear projection $\to$ Threat-aware gating $\to$ 2-Head Self-Attention ($H=2$) $\to$ Dense latent layers ($512 \to 256 \to 128$) $\to$ Three decoupled output heads.
  - Clearly distinguishes Actor policy $\pi_\theta(a|\mathbf{s}_t)$ with adaptive temperature $\tau_t$, Critic baseline $V_\phi(\mathbf{s}_t)$, and Auxiliary risk forecaster $\hat{\mathbf{r}}_{t+1}$.
- **Region D: Mitigation and Recovery:**
  - Operational safety checks modeled as an explicit guardrail shield: (1) Dispatch Validation (active fault / $r > 0.30$) and (2) Transient queue drop filter ($\epsilon_{\mathrm{queue}} = 0.08$).
  - Asynchronous Execution Queue with tokenized action dispatches, delays $\tau \in \{0, 1, 2\}$, and resource overhead ($\Delta\mathrm{CPU}, \Delta\mathrm{RAM}$).
  - Nine supported actions ($a_0$--$a_8$) mapped to Kubernetes actuators (`cert-manager`, rolling patch, HashiCorp Vault, OPA/Gatekeeper, Redis cache flush).
  - **Active Service Healing Loop:** Bold dashed green feedback loop routing directly from actuators back to Region A, suppressing node risk ($-80\%\sigma$) and restoring availability ($+15\%\sigma$).
- **Region E: Evaluation and Policy Feedback:**
  - SRE Real-time metrics panel: Availability ($A_t \ge 90\%$), MTTR recovery steps, Risk Reduction ($\Delta R_t$), and False Mitigation Rate (FMR).
  - Scalarized multi-objective reward formulation $r_t$.
  - **PPO Closed Learning Loop:** Dotted purple parameter update path routing trajectory rollouts $\mathcal{D}$ through the clipped surrogate loss $\nabla_\theta \mathcal{L}_{\mathrm{PPO}}$ back to Region C.
- **Dedicated Legend:**
  - Explicitly distinguishes runtime telemetry (solid blue), chaos ingress (dashed orange), action dispatch (solid purple), active healing (dashed green), and offline policy updates (dotted purple).

---

## 3. Redesign Details for Figure 2: Deep Policy Architecture

Figure 2 (`figure2_secchaos_policy.pdf`) provides a mathematically rigorous, left-to-right view of the neural network policy:

### Stage-by-Stage Architecture:
- **Stage A (Observation State $\mathbf{s}_t \in \mathbb{R}^{16}$):**
  - Partitioned into 5 semantic feature groups:
    1. *Security Risk Channels ($s_0$--$s_4$):* TLS, dependency, secret, RBAC, and authentication risks.
    2. *Threat Dynamics ($s_5$--$s_7$):* Global severity $\mathcal{L}_{\mathrm{threat}}$, vulnerability score, active attacks.
    3. *Cluster Telemetry ($s_8$--$s_{10}$):* Host CPU, memory, and network utilization.
    4. *Resilience QoS ($s_{11}$--$s_{12}$):* Availability $A_t$ and MTTR tracking.
    5. *Status & History ($s_{13}$--$s_{15}$):* Attack success history, mitigation effectiveness factor, and active fault count.
- **Stage B (Linear Feature Projection):**
  - 16 independent linear projection layers transforming scalar features into $32$-dimensional token embeddings: $\mathbf{e}_t^{(i)} = \mathbf{W}_e^{(i)} s_t^{(i)} + \mathbf{b}_e^{(i)} \in \mathbb{R}^{32}$.
- **Stage C (Threat-Aware Feature Gating):**
  - Multiplicative gating node driven by threat severity input $s_5 = \mathcal{L}_{\mathrm{threat}}$:
    $$\mathbf{g}_t^{(i)} = \mathbf{e}_t^{(i)} \cdot (1.0 + \mathcal{L}_{\mathrm{threat}}) \quad \text{for } i \le 4$$
  - Leaves operational channels ($i \ge 5$) unaffected, dynamically prioritizing security features during attacks.
- **Stage D (Multi-Head Self-Attention, $H=2$):**
  - Parallel Head 1 and Head 2 paths ($d_k = 16$) computing query, key, and value transformations to capture cross-service failure propagation across tokens.
- **Stage E (Latent Dense MLP):**
  - Flattening ($16 \times 32 = 512$) followed by dense layers $\mathbb{R}^{512} \to \mathbb{R}^{256} \to \mathbb{R}^{128}$ with Tanh activation functions.
- **Stage F (Three Decoupled Multi-Task Output Heads):**
  - *Actor Head:* $\pi_\theta(a|\mathbf{s}_t)$ over 9 discrete mitigation actions with threat-adaptive temperature $\tau_t = \tau_0 \exp(-\beta \mathcal{L}_{\mathrm{threat}})$.
  - *Critic Head:* State-value baseline $V_\phi(\mathbf{s}_t)$ for generalized advantage estimation.
  - *Auxiliary Risk Head:* Predicts next-step risk vector $\hat{\mathbf{r}}_{t+1} \in \mathbb{R}^6$ (active during training, detached during inference).
- **Stage G (PPO Policy Optimization):**
  - Illustrates the multi-task loss $\mathcal{L}_{\mathrm{Total}} = \mathcal{L}_{\mathrm{CLIP}} + c_1 \mathcal{L}_{\mathrm{VF}} - c_2 \mathcal{H} + \lambda_{\mathrm{aux}} \mathcal{L}_{\mathrm{aux}}$.
  - Dashed return arrow indicates backpropagation and policy gradient parameter updates.
  - Callout badge notes that the auxiliary head is detached during online inference, ensuring a $0.44$\,ms per-step decision latency.

---

## 4. Visual Styling and Journal Compliance

- **Palette:** Color-blind conscious, semantic palette:
  - System Components & Telemetry: Slate Blue (`#1A5276`)
  - Security Chaos & Threats: Amber/Orange (`#D35400`)
  - Policy Controller & Optimization: Purple/Violet (`#5B2C6F`)
  - Mitigation & Recovery: Emerald Green (`#196F3D`)
- **Typography:** Standard document sans-serif font (`\sffamily`) matching Wiley NJD style.
- **Geometric Regularity:** Strict grid alignment, balanced whitespace, thin line widths ($0.55\text{--}0.75$\,pt), uniform LaTeX arrowheads (`Latex`).
- **No Text Bloat:** Zero full sentences inside figure nodes; all detailed descriptions are preserved in the text and refined captions.
