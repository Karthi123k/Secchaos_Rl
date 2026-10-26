# Rigorous Experimental Redesign and Evaluation Plan: SecChaos-RL

**Target Journal:** *Software: Practice and Experience* (Wiley)  
**Execution Environment:** 13th Gen Intel Core i7-13700 (24 CPU cores), 15 GB RAM, Python 3.10, PyTorch, Gymnasium, NetworkX.

---

## 1. Research Questions

To provide a rigorous, software-engineering-grounded evaluation that directly addresses the previous editorial concerns, the revised experiments are structured around four core Research Questions:

* **RQ1 (Resilience and Recovery Efficacy):** How effectively does SecChaos-RL reduce systemic security risk and minimize recovery time (MTTR) compared to deterministic software policies (No-Mitigation, Static Rule-Based, Threshold-Based) and standard RL algorithms (DQN, A2C, standard PPO)?
* **RQ2 (Availability and Operational Trade-offs):** How well does SecChaos-RL preserve live microservice availability and avoid service-disrupting false mitigations when subjected to concurrent security faults and cascading dependencies?
* **RQ3 (Architectural Ablation):** What are the isolated contributions of the individual framework components—multi-objective reward design, multi-head self-attention, auxiliary risk prediction, threat-aware gating, and adaptive policy temperature—to overall system survivability?
* **RQ4 (Computational Overhead & Practical Feasibility):** What is the runtime decision latency and resource footprint of SecChaos-RL, and how does it scale as microservice topologies increase in complexity?

---

## 2. Compared Baselines

Rather than evaluating only reinforcement learning algorithms, our evaluation incorporates standard software engineering practices alongside classic and modern RL algorithms:

1. **No-Mitigation Baseline (Passive Degradation):**
   - Represents unmanaged systems where faults accumulate until complete service collapse. Quantifies the raw destructive potential of the security chaos injection.
2. **Static Rule-Based Policy (Greedy Alert Matching):**
   - Implements a deterministic mapping from active security alerts directly to the corresponding mitigation action without considering service state, downstream dependencies, or resource availability. Represents naive automation.
3. **Threshold-Based Policy (DevOps Operational Heuristic):**
   - Triggers mitigation actions only when monitored service risk or resource utilization exceeds predefined operational thresholds ($\theta_{risk} > 0.4$, $\theta_{res} > 0.8$). Represents standard cloud-native SRE alert policies.
4. **Deep Q-Network (DQN):**
   - Classic off-policy value-based RL agent with experience replay and target network.
5. **Advantage Actor-Critic (A2C):**
   - Synchronous on-policy actor-critic algorithm.
6. **Standard Proximal Policy Optimization (PPO):**
   - Standard clipped policy gradient actor-critic without domain-specific attention or gating.
7. **SecChaos-RL (Proposed Architecture):**
   - Full framework incorporating multi-head self-attention, threat-aware feature gating, auxiliary risk prediction, and threat-adaptive temperature exploration.

---

## 3. Experimental Scenarios and Environmental Configurations

### 3.1 Microservice Dependency Topologies
* **Default Topology:** 7-service microservice DAG modeled after industry standards (Google Online Boutique / Sock Shop):
  - Services: Gateway, Authentication, User, Order, Payment, Inventory, Notification.
  - Inter-service dependency edges: Gateway $\rightarrow$ Authentication, Authentication $\rightarrow$ User, User $\rightarrow$ Order, Order $\rightarrow$ Payment, Payment $\rightarrow$ Inventory, Inventory $\rightarrow$ Notification, User $\rightarrow$ Payment.
  - Cascading parameter: $\gamma_{cascade} = 0.6$. When an upstream service risk exceeds $0.4$, degradation propagates downstream.
* **Extended Topology (Sensitivity Analysis):** 12-service complex DAG with redundant paths and cross-tier dependencies to test structural generalizability.

### 3.2 Security Fault Taxonomy
Eight standardized security fault categories injected with Poisson arrival rates:
- $F_1$: Expired TLS Certificate (affects Gateway; mitigation: rotate certificate).
- $F_2$: Vulnerable Dependency with known CVE (affects User; mitigation: patch dependency).
- $F_3$: Secret / Credential Leakage in logs (affects User; mitigation: rotate secret).
- $F_4$: RBAC Misconfiguration (affects Authentication; mitigation: restrict RBAC).
- $F_5$: Weak Authentication / Disabled MFA (affects Authentication; mitigation: enable MFA).
- $F_6$: Excessive Privileges (affects Order; mitigation: revoke privileges).
- $F_7$: Missing Security Patch (affects Inventory; mitigation: apply security patch).
- $F_8$: Exposed Internal API Endpoint (affects Gateway; mitigation: rollback configuration).

### 3.3 Curriculum Difficulty Progression
To ensure stable training convergence across all algorithms:
- **Phase 0 (Episodes 0–50):** Baseline threat ($\lambda_f = 0.15$, faults $F_1, F_5$, 0 concurrent attacks, no cascade).
- **Phase 1 (Episodes 50–100):** Moderate threat ($\lambda_f = 0.25$, faults $F_1, F_3, F_4, F_5$, 1 concurrent attack).
- **Phase 2 (Episodes 100–150):** Severe threat ($\lambda_f = 0.35$, faults $F_1 \dots F_6$, 2 concurrent attacks).
- **Phase 3 (Episodes 150–250+):** Critical Chaos ($\lambda_f = 0.45$, all faults $F_1 \dots F_8$, 4 concurrent attacks, full DAG cascading propagation).
- **Evaluation Benchmark:** 20 held-out evaluation episodes per seed evaluated strictly under **Critical Chaos (Phase 3)** to test maximum resilience capacity.

---

## 4. Quantitative Metrics and Measurement Definitions

| Metric | Formal Definition | Unit | Operational Significance |
|---|---|---|---|
| **Cumulative Reward** | $R_{total} = \sum_{t=0}^{T} r_t$ | Scalar | Overall optimization objective performance. |
| **Risk Reduction** | $\Delta \mathcal{L}_{sec} = \max\left(0, 1 - \frac{\overline{r}_{final}}{r_{initial}}\right) \times 100\%$ | % | Effectiveness in neutralizing injected security vulnerabilities. |
| **Service Availability** | $\bar{A} = \frac{1}{T} \sum_{t=0}^{T} a_t \times 100\%$ | % | Percentage of uptime and request fulfillment across all services. |
| **Mean Time to Recovery (MTTR)** | $\text{MTTR} = \frac{1}{|E_{rec}|} \sum_{e \in E_{rec}} \Delta t_e$ | Steps | Speed at which system restores normal availability ($\ge 0.90$) and low risk ($\le 0.50$). |
| **Attack Success Rate (ASR)** | $\text{ASR} = \frac{N_{successful\_attacks}}{N_{total\_steps}} \times 100\%$ | % | Vulnerability window exploited by active adversaries during chaos. |
| **False Mitigation Rate (FMR)** | $\text{FMR} = \frac{N_{unnecessary\_actions}}{N_{total\_actions}} \times 100\%$ | % | Rate of deploying mitigations when no matching vulnerability was present. |
| **Decision Latency** | $\Delta t_{decision} = t_{action\_selected} - t_{obs\_received}$ | Milliseconds | Computational delay introduced by the decision engine per step. |
| **Resilience Score** | $\mathcal{R} = 0.4 \Delta \mathcal{L}_{sec} + 0.4 \bar{A} + 0.2 \left(\frac{1}{1 + \text{MTTR}}\right)$ | % | Composite holistic metric measuring overall survivability. |

---

## 5. Architectural Ablation Design

To scientifically substantiate the design claims, 5 distinct configurations will be trained and evaluated across 30 seeds under identical environmental conditions:

1. **Config A (Baseline PPO):** Standard PPO with vanilla multi-layer perceptron (MLP) and standard unweighted reward.
2. **Config B (PPO + Security Reward):** Standard PPO using our multi-objective security resilience reward function.
3. **Config C (PPO + Reward + Multi-Head Attention):** Incorporating 2-head self-attention over the 16 state embeddings ($d=32$).
4. **Config D (PPO + Reward + Attention + Auxiliary Risk Head):** Adding the auxiliary next-step risk prediction head with MSE regularization loss ($\mathcal{L}_{aux}$).
5. **Config E (Full SecChaos-RL):** Complete architecture adding Threat-Aware Feature Gating (amplifying risk dimensions under high threat) and Threat-Adaptive Policy Temperature Exploration ($\tau_t = 1.0 - 0.55 \cdot o_t^{(6)}$).

---

## 6. Statistical Rigor Protocol

- **Independent Seeds:** Exactly 30 independent random seeds (`range(2026, 2056)`).
- **Data Integrity:** Raw step-level trajectories will be saved directly to disk. No synthetic transformations or post-processing adjustments will be applied.
- **Reporting Metrics:** Mean, Standard Deviation, and 95% Confidence Intervals:
  $$\text{CI}_{95\%} = \bar{x} \pm 1.96 \cdot \frac{s}{\sqrt{n}}$$
- **Hypothesis Testing:**
  - One-Way ANOVA across all baseline algorithms to verify overall variance significance ($F$-statistic, $p < 0.001$).
  - Post-Hoc Tukey HSD test for pairwise comparisons with family-wise error rate control ($\alpha = 0.05$).
  - Cohen's $d$ Effect Size to quantify practical significance:
    $$d = \frac{\bar{x}_1 - \bar{x}_2}{s_{pooled}}$$
    where $d > 0.8$ denotes a large practical effect size.

---

## 7. Computational Cost and Resource Budget

- **CPU Cores Utilized:** 20 parallel worker processes on the 24-core Intel i7-13700.
- **Training Budget per Seed:** 300 episodes with proper rollout accumulation (sufficient for full convergence).
- **Evaluation Budget per Seed:** 20 episodes under critical full-chaos conditions.
- **Estimated Execution Time:**
  - Benchmarking 7 algorithms across 30 seeds: $\approx 8$–12 minutes with 20 parallel workers.
  - 5-stage Ablation study across 30 seeds: $\approx 6$–10 minutes.
  - Total compute time: $\approx 15$–22 minutes.
- **Output Artifacts Generated:**
  - `revision/experiments/raw_metrics_benchmark.csv` (unadjusted raw metrics across 30 seeds).
  - `revision/experiments/raw_metrics_ablation.csv` (unadjusted raw ablation metrics).
  - `revision/experiments/anova_tukey_results.json` (genuine statistical test results).
  - High-resolution vector and raster publication plots.
