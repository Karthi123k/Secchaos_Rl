# Figure 1 & Figure 2 Validation and Visual Inspection Checklist

**Manuscript Title:** SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos  
**Target Journal:** *Software: Practice and Experience* (Wiley)  
**Verification Date:** 2026-10-27  

---

## 1. Technical & Architectural Fidelity Checklist

- [x] **Microservice Topology (Region A):**
  - Confirmed: 7 nodes (`Gateway`, `Authentication`, `User`, `Order`, `Payment`, `Inventory`, `Notification`) matching `DependencyGraph` in `secchaos_framework.py`.
  - Confirmed: REST/gRPC API invocation dependencies accurately shown.
  - Confirmed: Cascade threshold $r(u) > 0.35$ and propagation factor $\gamma = 0.50$ correctly annotated.
- [x] **Fault Injection Taxonomy (Region B):**
  - Confirmed: 8 standardized security fault codes ($F_1$--$F_8$) matching `FAULT_DEFS` in `secchaos_framework.py`.
  - Confirmed: Poisson arrival process ($\lambda_k \in [0.05, 0.25]$) and duration/severity distributions noted without paragraphs.
  - Confirmed: Dynamic threat evaluator formula $\mathcal{L}_{\mathrm{threat}} = \sigma(6.0(V_t - 0.40))$ depicted.
- [x] **DRL Controller & Gating (Region C & Figure 2):**
  - Confirmed: 16-D state vector matches `_get_obs()` in `secchaos_framework.py`.
  - Confirmed: 16 independent linear embeddings $\mathbf{e}_t^{(i)} \in \mathbb{R}^{32}$.
  - Confirmed: Multiplicative gating $(1 + \mathcal{L}_{\mathrm{threat}})$ applied exclusively to security channels $s_0$--$s_4$.
  - Confirmed: Multi-Head Self-Attention ($H=2, d_k=16$) captures inter-service dependencies.
  - Confirmed: Dense latent layer dimensions: $512 \to 256 \to 128$ (Tanh).
  - Confirmed: Three decoupled heads (Actor $128 \to 9$, Critic $128 \to 1$, Auxiliary $128 \to 6$).
  - Confirmed: Actor threat-adaptive temperature $\tau_t = \tau_0 \exp(-\beta \mathcal{L}_{\mathrm{threat}})$.
  - Confirmed: Auxiliary head marked as detached during online inference.
- [x] **Mitigation & Execution Queue (Region D):**
  - Confirmed: Dual safety guardrails (dispatch validation and 8% transient drop).
  - Confirmed: Asynchronous queue with delays $\tau \in \{0, 1, 2\}$ and CPU/RAM contention.
  - Confirmed: 9 discrete actions ($a_0$--$a_8$) mapped to Kubernetes actuators.
  - Confirmed: Active service healing control loop feeds back into Region A ($-80\%\sigma$ risk, $+15\%\sigma$ availability).
- [x] **Evaluation & Feedback (Region E & Stage G):**
  - Confirmed: SRE metrics (Availability $\ge 90\%$, MTTR, Risk Reduction, FMR).
  - Confirmed: Multi-objective scalar reward formula.
  - Confirmed: PPO policy gradient parameter update loop closing the feedback cycle.
  - Confirmed: Computational latency ($0.44 \pm 0.15$\,ms per step) clearly documented.

---

## 2. Visual & Typography Quality Checklist

- [x] **Elimination of AI Infographic Artifacts:**
  - Removed all paragraphs, numbered text blocks, and bulleted text from containers.
  - Replaced text blocks with meaningful graphical relationships, connected DAG nodes, and mathematical symbols.
- [x] **Vector Format Scalability:**
  - Authored in 100% native LaTeX TikZ.
  - Compiled to vector PDF and SVG; zero pixelation when zoomed to 400%.
- [x] **Color-Blind Conscious Palette:**
  - System Telemetry: Slate Blue (`#1A5276`)
  - Chaos & Threats: Amber/Orange (`#D35400`)
  - Policy Controller: Purple/Violet (`#5B2C6F`)
  - Mitigation & Recovery: Emerald Green (`#196F3D`)
  - High grayscale contrast confirmed across all functional regions.
- [x] **Arrow & Routing Geometry:**
  - Clean horizontal data flow from left to right.
  - Zero overlapping or intersecting arrows through intervening boxes.
  - Legend explicitly defines all line styles (telemetry, chaos, control, healing, learning).
- [x] **Page Budget & Sizing:**
  - Figures 1 and 2 span double columns (`\begin{figure*}`) fitting neatly across the text spread without margin overflow.
  - Figure captions are concise, self-contained, and define all abbreviations.

---

## 3. LaTeX Compilation Audit

| Item | Command / Check | Result |
| :--- | :--- | :---: |
| Standalone Figure 1 Compilation | `pdflatex figure1_secchaos_framework.tex` | **Exit code 0** (0 errors) |
| Standalone Figure 2 Compilation | `pdflatex figure2_secchaos_policy.tex` | **Exit code 0** (0 errors) |
| SVG Conversion Figure 1 | `pdftocairo -svg figure1_secchaos_framework.pdf` | **Success** (534 KB) |
| SVG Conversion Figure 2 | `pdftocairo -svg figure2_secchaos_policy.pdf` | **Success** (484 KB) |
| Master Manuscript Compilation | `pdflatex secchaos_wiley.tex` (in `revised_manuscript/`) | **Exit code 0** (19 pages) |
| Undefined Citations / References | `grep -i "undefined" secchaos_wiley.log` | **0 Found** |
| Floating Bodies & Page Spacing | Visual inspection of `secchaos_wiley.pdf` | **Section 1 starts on Page 1** |

---

## Author Verification Sign-Off
I confirm that the redesigned Figures 1 and 2 meet the visual, technical, and architectural requirements for submission to *Software: Practice and Experience*.

**Lead Researcher / Designer:** ___________________________  
**Date:** 2026-10-27  
