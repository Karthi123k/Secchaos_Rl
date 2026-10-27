# Comprehensive Manuscript Revision Report

**Manuscript Title:** SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos  
**Target Journal:** *Software: Practice and Experience* (Wiley)  
**Revision Date:** 2026-10-27  
**Auditor / Editor:** Academic Language and Editorial Review Protocol  

---

## 1. Executive Summary

This report documents the systematic, section-by-section revision of the SecChaos-RL manuscript for submission to *Software: Practice and Experience* (Wiley). The revision addressed four primary objectives:
1. **Preserving 100% of the Scientific Contribution:** Retained all verified mathematical formulations, algorithms, experimental configurations, raw benchmark data, and statistical conclusions without modification or fabrication.
2. **Abstract Condensation:** Rewrote the abstract into clear, authentic academic English containing **exactly 200 words** (verified programmatically), adhering to the standard Background $\rightarrow$ Gap $\rightarrow$ Objective $\rightarrow$ Methodology $\rightarrow$ Results $\rightarrow$ Conclusion structure.
3. **Addressing AI-Style Text and Improving Originality:** Comprehensively removed repetitive formulas, inflated vocabulary ("revolutionary", "groundbreaking", "paramount", "profound dilemma", "landmark"), overused discourse markers ("Crucially,", "Furthermore,", "Moreover,", "It is worth noting that,"), and passive constructions, replacing them with direct, natural, authentic academic English.
4. **Complete Citation and DOI Verification:** Audited all 41 references in `references.bib`, confirming 100% in-text citation, updating 27 verified Crossref DOIs with genuine resolving URLs, and fully documenting the 14 legitimate non-DOI entries (books, preprints, software tools).

---

## 2. Section-by-Section Revision Summary

### Title, Abstract, and Keywords
- **Title:** Maintained the precise technical title: *SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos*.
- **Abstract:** Reduced from 402 words to **exactly 200 words** (`revised_manuscript/revised_abstract.txt`). Structured into six logical components:
  1. *Background:* Growth of distributed cloud-native microservices and cascading failure risks.
  2. *Gap:* Manual, open-loop nature of existing Security Chaos Engineering (SCE) practices.
  3. *Objective:* Autonomous closed-loop resilience framework combining SCE with deep reinforcement learning.
  4. *Methodology:* Multi-objective MDP balancing risk, availability, MTTR, and mitigation churn, featuring multi-head self-attention, threat gating, auxiliary risk head, and adaptive temperature exploration.
  5. *Results:* Exact verified figures across 30 seeds: rule-based churn (55.5% risk reduction vs. 30.8% FMR); SecChaos-RL's recovery speed ($\text{MTTR} = 1.79$ vs. $2.29$ steps, $p = 0.0013$), halved false dispatches (20.9% FMR), and 0.44 ms per-step decision latency.
  6. *Conclusion:* Establishing practical operational boundaries between deterministic heuristics and reinforcement learning control.
- **Keywords:** Formatted in Wiley style (`Security Chaos Engineering | Microservice Resilience | Reinforcement Learning | Self-Adaptive Systems | Fault Injection | DevSecOps`).

### Section 1: Introduction
- **Clarity & Language Improvements:** Removed formulaic, dramatic phrases ("foundational paradigm", "paramount challenge", "fundamentally blind", "profound operational dilemma"). Replaced with direct, concrete descriptions of enterprise microservices in banking, healthcare, and retail.
- **Problem Formulation:** Articulated the dual challenges: (1) the operational trade-off between aggressive security mitigations and service availability timeouts, and (2) the failure of deterministic alert-matching scripts under concurrent chaos due to mitigation storms.
- **Literature Integration:** Contextualized runtime emergence against build-time testing methods, including automated test planning~\cite{haldar2026testplan}, buffer overflow vulnerability detection~\cite{huang2026cotstatic}, bug report classification~\cite{du2024llmbrc}, and opcode slicing learning~\cite{tong2026osel}, as well as adversarial model testing~\cite{awal2025adversarial}.
- **Research Questions:** Preserved the 4 core RQs (RQ1: Recovery and Resilience, RQ2: Availability and FMR, RQ3: Architectural Ablation, RQ4: Computational Feasibility).
- **Contributions:** Streamlined the 6 primary software engineering and algorithmic contributions.

### Section 2: Background and Related Work
- **Tone Adjustments:** Removed promotional framing of published literature ("landmark study", "seminal survey"). Retained factual attribution to prior studies in *Software: Practice and Experience* (Aderaldo et al.~\cite{aderaldo2025declarative}, Camacho et al.~\cite{camacho2022chaos}, Schneider et al.~\cite{schneider2015survey}, Taibi et al.~\cite{taibi2021microservice}, Soldani et al.~\cite{soldani2023microservice}).
- **Systematic Comparison Table (Table 1):** Verified that all 7 compared approaches (Chaos Monkey, CoSPL, ResilienceBench, Self-Healing Survey, CybORG, LLM-SCE, and SecChaos-RL) are accurately summarized across target domain, control loop, fault scenarios, and mitigation strategies.
- **Identified Gap:** Formulated the gap clearly: existing chaos tools inject faults without automated mitigation, whereas existing RL cyber defense agents evaluate abstract network topologies without microservice availability SLAs.

### Section 3: SecChaos-RL Framework Architecture
- **Component Precision:** Formatted the 5 modular components (`DependencyTopology`, `ChaosEngine`, `StateMonitor`, `ThreatAwareOrchestrator`, `MitigationExecutor`) under the classic MAPE-K self-adaptation model.
- **Figure 1 (`workflow.jpg`):** Sized cleanly to single-column width (`\columnwidth`), aligning with the two-column layout.

### Section 4: Threat Model and Decision Methodology
- **Fault Taxonomy (Table 2):** Maintained the 8 fault classes ($F_1 \dots F_8$) mapped across Gateway, Authentication, User, Order, and Inventory services, along with cascading propagation equations ($\alpha_{casc} = 0.22, \gamma_{coupl} = 0.5$).
- **Observation Space (Table 3):** Maintained the complete 16-dimensional continuous state vector, clarifying that active fault count enters both as a normalized scalar ($|\mathcal{F}_{act}|/8.0$) in Index 15 and as an additive component in systemic vulnerability score $\mathcal{V}_{score}$ (Index 6).
- **Action Space & Execution Queue:** Formally delineated the 9 actions ($a_0 \dots a_8$), execution delays ($d_k \in \{0, 1, 2\}$), invocation costs, and transient resource overheads. Preserved the mutual exclusivity of the three non-success operational outcomes:
  1. *Unnecessary Dispatch ($N_{wrong}$):* Intercepted before queue admission when no active fault matches.
  2. *Transient Execution Drop ($N_{drop}$):* 8% transient cloud-native RPC/scheduling drop rate on valid dispatches.
  3. *Queue Redundancy ($N_{redundant}$):* Action valid at admission, but fault naturally cleared before maturity.
- **Multi-Objective Reward Function (Eq. 7):** Preserved exact reward weights ($\alpha_1 = 4.5, \alpha_2 = 3.5, \alpha_3 = 3.0, \alpha_4 = 1.5, \alpha_5 = 0.5, \alpha_6 = 1.5$) and penalties ($\beta_1 = 1.2, \beta_2 = 0.05, \beta_3 = 0.25, \beta_4 = 0.30$) with intermediate step feedback $\mathcal{R}_{mit}$ and $[-8.0, 8.0]$ clipping.
- **Deep Architecture:** Detail preserved for 2-head self-attention ($d_k = 16$), threat-aware feature gating, auxiliary risk prediction head ($c_2 = 0.25$), and threat-adaptive temperature exploration ($\tau_{temp} = \max(0.2, 1.0 - 0.50 \mathcal{L}_{threat})$).
- **Algorithms 1 & 2:** Verified algorithmic completeness, mathematical notation, and float alignment.

### Section 5: Experimental Setup
- **Topology:** 7-service benchmark modeled after Google Online Boutique and Sock Shop.
- **Evaluated Policies:** 8 policies evaluated under identical environmental seeds (No-Mitigation, Rule-Based, Threshold-Based, Queue-Aware Cooldown Heuristic, DQN, A2C, PPO, SecChaos-RL).
- **Curriculum Protocol:** 4 stages across 250 episodes ($12,500$ steps), evaluated over 20 held-out Phase 3 episodes per seed ($1,000$ decisions per seed) across 30 independent random seeds (`range(2026, 2056)`).
- **Metric Definitions:** Signed risk reduction without zero-clipping (Eq. 11), availability, MTTR, ASR, FMR (Eq. 12), latency, and holistic resilience score (Eqs. 13–14).
- **Jensen's Inequality Verification:** Preserved the mathematical explanation demonstrating that evaluating composite resilience per-seed yields $45.21\% \pm 2.26\%$, whereas naively evaluating aggregate means yields $44.94\%$.

### Section 6: Results and Analysis
- **Tables 4, 5, 6:** Cleanly included via `experiments/tables_latex.tex`.
- **Directional Sign Convention:** Prominently stated that $\Delta = \text{SecChaos-RL} - \text{Comparator}$; therefore, $\Delta < 0$ favors SecChaos-RL for MTTR (lower is faster), while $\Delta > 0$ favors SecChaos-RL for resilience.
- **RQ1:** Detailed paired statistical findings showing SecChaos-RL's recovery speed advantage over conservative heuristics ($\text{MTTR} = 1.79 \pm 0.53$ vs. $2.29 \pm 0.30$ for Threshold-Based, $p_{holm} = 0.0013$; and $2.24 \pm 0.23$ for Queue-Aware Cooldown, $p_{holm} = 0.0013$). Reported Repeated-Measures ANOVA across all metrics ($p < 0.0001$).
- **RQ2:** Analyzed mitigation churn, demonstrating that while greedy rules achieve high nominal risk reduction ($55.5\%$), they deploy actions at every step with an FMR of $30.8\%$ ($15.4$ wrong actions/ep). SecChaos-RL halves wrong dispatches to $7.5$ per episode ($\text{FMR} = 20.9\%$) while preserving $90.6\%$ availability.
- **RQ3:** Documented the 6-stage ablation, explicitly acknowledging that architectural components govern specific operational trade-offs (e.g., self-attention reduces FMR by $1.47\%$) rather than claiming universal, monotonic increases in composite scalar resilience over standard PPO ($\Delta = -0.70\%$, $p = 0.2044$, non-significant).
- **RQ4:** Clarified the dual latency reporting: online benchmark latency ($0.44 \pm 0.15$\,ms) versus dedicated CPU microbenchmark ($0.46 \pm 0.52$\,ms mean, $1.04$\,ms $p_{99}$), showing feasibility within Kubernetes 10–50 ms reconciliation loops.

### Section 7: Discussion and Operational Safeguards
- **Clear Operational Boundaries:** Explicitly stated when deterministic alert scripts suffice (low turbulence, independent services) versus when autonomous RL is warranted (concurrent faults, deep dependency cascades).
- **Kubernetes Action Mapping:** Verified exact 1-to-1 mapping between formal MDP actions ($a_0 \dots a_8$) and production Kubernetes controller operations (Cert-Manager, Deployment patch, Secret rotation, RBAC rolebinding, Istio AuthorizationPolicy, pod security admission, Rollout undo).
- **Safeguard Scope Transparency:** Separated simulation-evaluated safeguards (pre-dispatch verification, 8% transient drops, queue redundancy suppression) from prospective production safeguards (retry budgets, circuit breakers, automated deployment rollbacks, break-glass webhook latches).

### Section 8: Threats to Validity
- Comprehensive treatment of Construct, Internal, External, and Conclusion validity, including matched-seed experimental design, ANOVA testing, and simulation-to-production boundaries.

### Section 9: Conclusion and Future Work
- Concise summary of primary empirical conclusions and outlined roadmap for packaging SecChaos-RL as a cloud-native Kubernetes Operator.

---

## 3. Verification of Formatting and Quality Requirements

1. **Target Journal Layout:** Formatted strictly in Wiley NJD (`USG.cls`, twocolumn, ASNA).
2. **Page Count & Visual Balance:** The revised PDF compiles cleanly to **19 pages** with balanced text density across all pages and zero blank pages.
3. **BibTeX Verification:** 0 errors, 0 warnings.
4. **DOI Verification:** 27 verified DOIs with active resolution links; 14 non-DOI entries verified with ISBNs, arXiv IDs, or official project URLs.
5. **Word Count Compliance:** `revised_abstract.txt` verified at **exactly 200 words**.
