# Technical Implementation Audit Report: SecChaos-RL

**Auditor Role:** Senior Software Engineering Researcher & RL Systems Auditor  
**Scope:** `run_experiments.py`, `IIIT.py`, `sn-article-template/sn-article.tex`, and cached outputs in `secchaos_output/`  
**Target Venue:** *Software: Practice and Experience* (Wiley)  

---

## 1. Reinforcement Learning Formulation Audit

### 1.1 State Representation and Observation Vector
* **Mathematical Claim in Manuscript:** The paper formalizes an underlying MDP state $s_t \in \mathbb{R}^9$ ($s_t^{cert}, s_t^{dep}, s_t^{sec}, s_t^{rbac}, s_t^{auth}, s_t^{patch}, s_t^{atk}, s_t^{avail}, s_t^{rec}$) and an augmented observation vector $o_t \in \mathbb{R}^{16}$.
* **Actual Code Implementation (`run_experiments.py` lines 172–183, 244–258):**
  - The internal state tracks `self.risks = np.zeros(5)` (cert, dep, secret, rbac, auth).
  - The patch currency state $s_t^{patch}$ from Eq. (7) is completely omitted from the Python environment state.
  - The 16-dimensional observation vector $o_t$ contains:
    - `obs[0:5]`: 5 risk scores $[0, 1]$.
    - `obs[5]`: `self.threat_severity`.
    - `obs[6]`: `self.vulnerability_score`.
    - `obs[7]`: `self.active_attacks / 4.0`.
    - `obs[8:11]`: `[cpu_util, mem_util, net_overhead]`.
    - `obs[11]`: `self.availability`.
    - `obs[12]`: `min(1.0, self.recovery_time / 20.0)`.
    - `obs[13]`: `mean(attack_success_history)`.
    - `obs[14]`: `prev_mitigation_effectiveness`.
    - `obs[15]`: `min(1.0, len(active_faults) / 8.0)`.
* **State Leakage & Observation Realism:**
  - `obs[14]` directly provides the exact mitigation feedback score of the prior step.
  - `obs[15]` provides ground-truth active fault counts directly from simulator memory, which is inaccessible in real-world Kubernetes deployments without full observability parsing.
  - In a realistic software engineering deployment, monitoring agents observe latency, error rates, and security telemetry alerts, rather than simulator internal fault lists.

### 1.2 Threat Severity Discrepancy
* **Manuscript Claim (Eq. 13):** Threat severity is formulated via a nonlinear gated sigmoid:
  $$\mathcal{L}_{threat}(s_t) = s_t^{atk} \cdot (1 - s_t^{patch}) \cdot \left(1 - \frac{1}{1 + e^{-\beta(s_t^{avail} - 0.5)}}\right)$$
* **Actual Code Implementation (`run_experiments.py` lines 348–355):**
  ```python
  if self.vulnerability_score < 0.25:
      self.threat_severity = 0.0
  elif self.vulnerability_score < 0.5:
      self.threat_severity = 0.33
  elif self.vulnerability_score < 0.75:
      self.threat_severity = 0.66
  else:
      self.threat_severity = 1.0
  ```
  The implementation is a discrete 4-bin step function of vulnerability score. It does not evaluate patch status or the continuous logistic sigmoid gate described in the paper.

### 1.3 Action Space and Mitigation Semantics
* **Action Space:** 9 discrete actions ($a_0$: ignore, $a_1$: rotate certificate, $a_2$: patch dependency, $a_3$: rotate secret, $a_4$: restrict RBAC, $a_5$: enable MFA, $a_6$: apply security patch, $a_7$: revoke privileges, $a_8$: rollback configuration).
* **Execution Delay:** Each action has a configured delay $\tau \in \{0, 1, 2\}$ steps and resource consumption overhead (CPU, memory, network).
* **Fault-Action Mapping:** Actions target specific fault types (e.g., $a_1$ mitigates $F_1, F_8$; $a_2$ mitigates $F_2, F_7$). If an action is chosen that does not match an active fault, it is flagged as a "wrong mitigation," incurring an efficiency penalty and setting `prev_mitigation_effectiveness = 0.2`.
* **Software Realism:** The delayed execution queue (`action_queue`) correctly reflects operational reality where mitigation (e.g., redeploying patched images or rotating secrets) takes non-zero time.

### 1.4 Reward Function Formulation & Mathematical Redundancy
* **Code Implementation (`run_experiments.py` lines 412–437):**
  ```python
  risk_reduction = float(np.mean(prev_risks) - np.mean(self.risks))
  attack_prevention = float(prev_attack_prob - float(np.mean(self.risks)))
  # where prev_attack_prob was defined as float(np.mean(prev_risks))
  ```
* **Critical Mathematical Redundancy Defect:**
  In the code, `attack_prevention` and `risk_reduction` compute the exact same mathematical value:
  $$\Delta \mathcal{L}_{prev} \equiv \Delta \mathcal{L}_{sec} = \overline{r}_{t} - \overline{r}_{t+1}$$
  Consequently, $\alpha_{risk} \cdot \Delta \mathcal{L}_{sec} + \alpha_{prevent} \cdot \Delta \mathcal{L}_{prev} = (5.0 + 4.0) \cdot \Delta \mathcal{L}_{sec} = 9.0 \cdot \Delta \mathcal{L}_{sec}$.
  The paper presents these as two separate objectives (Eq. 16 and Eq. 17), creating an unsupported distinction in the theoretical formulation.
* **Objective Balancing:**
  The reward combines:
  - Positive terms: Risk reduction ($9.0$), Availability preservation ($3.0 \cdot a_t$), Fast recovery ($1.5 / (1 + t_{rec})$), Resource efficiency ($0.5 \cdot (1 - \overline{res})$), Service continuity ($1.5$ bonus if availability $\ge 0.95$).
  - Negative penalties: Attack occurrence ($-1.0$), Recovery delay ($-0.05 \cdot t_{rec}$), Resource spike ($-0.2$), Wrong mitigation ($-0.15$).
  - Reward is clipped to $[-10.0, 10.0]$.

---

## 2. Algorithm and Empirical Pipeline Audit

### 2.1 The Training Convergence Flaw in `run_experiments.py`
* **Root Cause Analysis:**
  In `run_experiments.py`, each episode runs for `ENV_MAX_STEPS = 50` steps.
  - In `train_agent` (lines 860–907), agent updates are invoked **only once per episode** after all 50 steps complete.
  - In `PPOAgent` and `SecChaosRLAgent`, the rollout buffer size is strictly 50 steps.
  - In standard PPO literature (Schulman et al., Stable-Baselines3), PPO requires rollouts of $1,024$ to $2,048$ steps to compute accurate Generalized Advantage Estimation (GAE) and stable mini-batch updates.
  - With $N=50$, advantage normalization $\frac{\hat{A} - \mu_A}{\sigma_A + 10^{-8}}$ over 50 steps creates severe variance and instability.
  - For `DQNAgent`, the replay buffer capacity is 5,000, but only 1 gradient step is executed per episode (250 gradient steps total). A 2-hidden-layer network cannot converge in 250 gradient updates.
* **Empirical Verification (Test Run on Raw Pipeline):**
  When evaluated without synthetic metric modification, all four agents (`DQN`, `A2C`, `PPO`, `SecChaosPPO`) fail to learn an active mitigation policy.
  - Evaluated greedy actions (`argmax`) choose a static default action (often action 0 / inaction) throughout testing.
  - Actual raw evaluation metrics across agents show:
    - Risk Reduction: $\approx 0.0\%$ to $2.15\%$
    - Availability: $\approx 88.3\%$ to $89.7\%$
    - MTTR: $0.8$ to $1.4$ steps
    - Wrong Mitigations: $5.0$ / $5$ evaluation episodes

### 2.2 The Synthetic Adjustment Routine (`run_experiments.py` lines 1081–1128)
* **Confirmed Implementation Defect / Integrity Breach:**
  Because the raw models did not converge under the undersized 50-step rollout budget, the script implements an explicit post-processing transformation:
  ```python
  if alg == "SecChaosPPO":
      adjusted_metrics[alg]["cumulative_reward"] = [r + 145.5 for r in metrics_by_alg[alg]["cumulative_reward"]]
      adjusted_metrics[alg]["risk_reduction"] = [min(98.5, max(75.0, rr * 4.0 + 82.4 + random.normalvariate(0, 1.5))) for rr in metrics_by_alg[alg]["risk_reduction"]]
      adjusted_metrics[alg]["availability"] = [min(99.5, max(88.0, av * 0.4 + 61.2 + random.normalvariate(0, 0.8))) for av in metrics_by_alg[alg]["availability"]]
      adjusted_metrics[alg]["mttr"] = [max(0.04, min(0.35, mt * 0.15 + 0.08 + random.normalvariate(0, 0.02))) for mt in metrics_by_alg[alg]["mttr"]]
      adjusted_metrics[alg]["attack_success_rate"] = [max(1.0, min(15.0, asr * 0.25 + 4.2 + random.normalvariate(0, 0.8))) for asr in metrics_by_alg[alg]["attack_success_rate"]]
  ```
  Similar scaling offsets were applied to `PPO` ($+98.2$), `A2C` ($+72.4$), and `DQN` ($+85.0$).
* **Significance:**
  The benchmarking numbers published in the original manuscript (Table 1: SecChaos-RL 83.45% risk reduction, 96.26% availability, 0.17 MTTR, 4.91% ASR) and stored in `secchaos_output/all_runs_metrics.csv` are artifacts of this linear synthetic generator, rather than outputs of converged neural network policies.
  **This violates non-negotiable research rules and must be completely excised.**
  A genuine, rigorously trained experimental pipeline must be executed where the agents genuinely learn to mitigate faults.

### 2.3 Total Absence of the Ablation Study Implementation
* **Manuscript Claim (Section 4.6, Table 2):**
  The manuscript presents a detailed 5-stage ablation study:
  - Baseline PPO (Risk Red: $59.43\% \pm 2.94\%$, Resil: $72.53\% \pm 1.33\%$)
  - + Reward ($66.15\% \pm 2.50\%$, $76.40\% \pm 1.25\%$)
  - + Attention ($73.80\% \pm 2.22\%$, $81.25\% \pm 1.12\%$)
  - + Aux. Risk ($79.20\% \pm 2.05\%$, $85.10\% \pm 1.01\%$)
  - Full SecChaos-RL ($83.45\% \pm 1.91\%$, $88.95\% \pm 0.94\%$)
* **Code Verification:**
  A search across the entire repository reveals that:
  - Neither `run_experiments.py` nor `IIIT.py` contains any ablation training code, flags, or data logging.
  - No ablation data files exist in `secchaos_output/`.
  - The values in Table 2 were hardcoded into the LaTeX document without supporting experimental runs.

---

## 3. Software Architecture and Practical Utility Audit

### 3.1 Architectural Decomposition
SecChaos-RL consists of the following components:
1. **Service Dependency Topology (`DependencyGraph`):**
   - 7 microservices: Gateway, Authentication, User, Payment, Order, Inventory, Notification.
   - Directed acyclic graph with cascade risk and availability degradation.
2. **Security Fault Injector (`SecChaosEnv`):**
   - Injects 8 categories of security faults with Poisson arrival and curriculum scheduling.
3. **RL Mitigation Policy Engine:**
   - Multi-Head Attention layer over 16 state embeddings ($d=32, h=2$).
   - Threat-aware feature gating amplifying risk dimensions under high threat.
   - Auxiliary next-step risk prediction head regularizing the latent space.
   - Threat-adaptive exploration temperature $\tau_t = 1.0 - 0.55 \cdot o_t^{(6)}$.
4. **Mitigation Executor:**
   - Action delay queue handling asynchronous operational delays and resource side-effects.

### 3.2 Practical Gaps for *Software: Practice and Experience*
1. **Lack of Realistic Baselines:**
   - Comparing only DQN, A2C, and PPO makes the paper look like an artificial RL benchmark rather than a software engineering tool.
   - Practical software engineering requires comparing against:
     - **No-Mitigation Baseline** (demonstrating the system failure trajectory without adaptation).
     - **Static Rule-Based Policy** (mapping detected fault alerts directly to mitigations).
     - **Threshold-Based Policy** (standard DevOps practice: mitigating only when risk or resource consumption crosses a configured threshold).
2. **Missing Software Engineering Metrics:**
   - Decision latency (inference time in milliseconds per mitigation step).
   - False mitigation rate (unnecessary or disruptive mitigations executed when not warranted).
   - Resource overhead of the orchestrator itself.
3. **Simulation Realism Limitations:**
   - The environment is an in-memory numerical simulation. To be credible in SP&E, the paper must be transparent about simulation boundaries, provide sensitivity analyses across varying microservice topologies, and explain how the framework's interfaces map to real cloud-native tools (Prometheus metrics exporter, Kubernetes admission controllers, Chaos Mesh).

---

## 4. Issue Classification and Action Matrix

| Issue ID | Category | Specific Finding | Affected Code / Manuscript Section | Recommended Correction |
|---|---|---|---|---|
| **ISS-01** | Confirmed Defect / Integrity | Synthetic metric adjustment in `run_experiments.py` (lines 1081–1128). | `run_experiments.py` lines 1081–1128; `secchaos_output/`; Manuscript Table 1 | Remove synthetic adjustment entirely. Fix RL rollout buffers and hyperparameters so policies genuinely converge on raw telemetry. |
| **ISS-02** | Unsupported Claim | Table 2 ablation study is reported in text and table but never implemented in code. | `sn-article.tex` lines 740–763; Table 2 | Implement automated ablation runner executing each modular variant (+Reward, +Attention, +AuxRisk, Full) with genuine data logging. |
| **ISS-03** | Implementation Defect | Mathematical redundancy in reward: $\Delta \mathcal{L}_{prev} \equiv \Delta \mathcal{L}_{sec}$. | `run_experiments.py` lines 412–413; `sn-article.tex` Eq. 16–17 | Refactor reward function to ensure threat severity reduction is mathematically distinct from local risk reduction, or formally unify them. |
| **ISS-04** | Discrepancy | Threat severity implementation (4-step discretizer) does not match manuscript Eq. 13 (continuous logistic sigmoid). | `run_experiments.py` lines 348–355; `sn-article.tex` Eq. 13 | Synchronize code and paper. Implement the continuous logistic sigmoid gate in the environment or document the discrete tier accurately. |
| **ISS-05** | Experimental Weakness | Undersized rollout buffer (50 steps) causes PPO training failure. | `run_experiments.py` lines 879–906 | Redesign training pipeline with proper multi-step rollout accumulation (e.g. 500–1,000 steps per update) and sufficient training steps for stable convergence. |
| **ISS-06** | Experimental Weakness | Omission of non-RL software engineering baselines (Rule-based, Threshold-based, No-mitigation). | `sn-article.tex` Section 3.4; `run_experiments.py` | Implement and evaluate 3 deterministic software baselines under identical scenarios to prove RL value over static rules. |
| **ISS-07** | Presentation Defect | Fragmentation of manuscript into dozens of short, 1-paragraph subsubsections. | `sn-article.tex` Sections 2, 3, 4 | Consolidate fragmented headings into coherent thematic sections matching SP&E structure. |
| **ISS-08** | Citation Defect | Missing relevant literature from target journal (*Software: Practice and Experience*). | `sn-bibliography.bib`; Related Work | Integrate key SP&E citations on microservice resilience patterns, chaos engineering platforms, and self-healing systems. |
