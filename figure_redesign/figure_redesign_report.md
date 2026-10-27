# Scientific Figure Redesign Report: SecChaos-RL

**Manuscript Title:** SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos  
**Target Venue:** *Software: Practice and Experience* (Wiley) / IEEE TSE / ACM TOSEM  
**Date:** 2026-10-27  
**Design Lead:** Senior Scientific Visualization Designer & Software Security Researcher  

---

## 1. Executive Summary and Motivation

In the previous revision, Figures 1 and 2 relied on raster JPEG images (`workflow.jpg` and `network_architecture.jpg`). A detailed review revealed that these diagrams exhibited characteristics of AI-generated infographics:
- **Text-Heavy Rectangles:** Large paragraphs of explanatory text, numbered lists, and bullet points were embedded directly inside graphic containers, mimicking presentation slides rather than rigorous scientific schematics.
- **Unclear Architectural Relationships:** Crucial operational distinctions—such as the difference between the physical data path (service telemetry, cascade propagation) and the control plane (action dispatch, asynchronous execution queues, and active service healing)—were obscured.
- **Lack of Vector Scalability:** Raster JPEGs suffered from compression artifacts, unreadable small text at journal column scales, and non-standardized typography.

To meet the rigorous publication standards of top-tier SCIE Q1 software engineering journals, we completely redesigned the methodology diagrams into **native, fully editable vector graphics** in LaTeX TikZ, compiled them to vector PDFs and scalable SVG files, and updated the manuscript integration.

---

## 2. Comprehensive Figure Audit and Classification

Each figure in the manuscript was systematically evaluated and classified into one of four actions:

| Figure ID | Original Source | Caption / Topic | Assessment | Action Taken & Justification |
| :---: | :---: | :--- | :--- | :--- |
| **Figure 1** | `figs/workflow.jpg` | Closed-Loop Methodology & Architecture | **Flawed AI Infographic:** Contained paragraphs of text inside boxed "phases", lacked DAG dependency topology, and hid feedback loops. | **Complete Vector Redesign (`secchaos_main_methodology.tex` $\to$ `.pdf`, `.svg`):** Built a 5-region left-to-right closed-loop architecture strictly grounded in `secchaos_framework.py`. |
| **Figure 2** | `figs/network_architecture.jpg` | Threat-Aware Neural Network Architecture | **Text-Heavy & Cluttered:** Displayed dense text inside layer boxes; failed to clearly delineate tensor shapes and feature grouping. | **Complete Vector Redesign (`secchaos_network_architecture.tex` $\to$ `.pdf`, `.svg`):** Crisp tensor-flow diagram showing 16-D grouped state, feature projections, threat gating, 2-head attention, and 3 decoupled heads. |
| **Figure 3** | `figs/resilience_benchmarking.png` | 30-Seed Empirical Resilience Benchmarking | **High-Quality Empirical Plot:** Authentic Python/matplotlib multi-panel boxplots/violin distributions across all 8 policies. | **Retain with Caption Refinement:** Verified high resolution (300 DPI, 4800x2700); updated caption to define IQR, medians, and statistical metrics. |
| **Figure 4** | `figs/pareto_tradeoff.png` | Risk vs. Availability Pareto Frontier | **High-Quality Empirical Plot:** Authentic scatter plot illustrating the operational boundary between heuristics and RL. | **Retain:** Essential for answering RQ2; verified high resolution (2100x1500). |
| **Figure 5** | `figs/ablation_study.png` | 5-Stage Ablation Component Analysis | **High-Quality Empirical Plot:** Multi-panel bar and step charts evaluating incremental architectural contributions. | **Retain:** Verified alignment with Table 6; crisp resolution (3150x1500). |
| **Figure 6** | `figs/learning_curves.png` | PPO Curriculum Training Curves | **High-Quality Empirical Plot:** Shows episode return, entropy, and auxiliary loss stabilization with 95% CIs across 30 seeds. | **Retain:** Essential for demonstrating training convergence and stability. |

---

## 3. Detailed Architecture of the Redesigned Main Methodology Figure

The main methodology diagram (`secchaos_main_methodology.pdf`) was created from the ground up to allow any software engineering researcher or peer reviewer to understand the full SecChaos-RL framework within seconds:

### Region A: System Under Test (Monitored Microservices)
- **Topological DAG:** Concretely visualizes the 7 microservices implemented in `DependencyGraph` (`Gateway`, `Authentication`, `User`, `Order`, `Payment`, `Inventory`, `Notification`).
- **Dependency Paths:** Shows directional synchronous REST/gRPC API invocations.
- **Cascading Failure Modeling:** Formally indicates downstream cascade propagation: when an upstream service exceeds critical risk ($r(u) > 0.35$), degraded availability and elevated risk propagate downstream with infection rate $\gamma = 0.50$.
- **Telemetry Probes:** Replaces descriptive paragraphs with small monitoring metric symbols representing latency ($\mu$), Istio 5xx errors ($\epsilon$), and host CPU/RAM utilization ($\rho$).

### Region B: Security Chaos & Threat Assessment
- **Chaos Ingress Points:** Displays the Security Chaos Engine generating standardized faults ($F_1$--$F_8$) according to Poisson processes ($\lambda_k \in [0.05, 0.25]$) and injecting them directly into the targeted microservices.
- **Threat Intelligence Evaluator:** Formulates dynamic cluster vulnerability $V_t = \bar{r}_t + 0.03 N_{\mathrm{fault}}$ and the continuous logistic threat severity $\mathcal{L}_{\mathrm{threat}} = \sigma(6.0(V_t - 0.40)) \in [0, 1]$.
- **State Aggregator:** Synthesizes service risks, cluster QoS, and threat metrics into the standardized 16-dimensional observation vector $\mathbf{s}_t \in \mathbb{R}^{16}$.

### Region C: Threat-Aware Deep RL Controller
- **Tensor Processing Pipeline:** Ingests $\mathbf{s}_t$ and $\mathcal{L}_{\mathrm{threat}}$, passing them through 16 independent linear feature projections ($\mathbf{e}_t^{(i)} \in \mathbb{R}^{32}$), threat-aware feature gating ($\mathbf{g}_t^{(i)} = \mathbf{e}_t^{(i)} \cdot (1 + \mathcal{L}_{\mathrm{threat}})$ for security risk channels $i \le 4$), and 2-head self-attention ($H=2$).
- **Latent Encoder:** Dense MLP layers ($512 \to 256 \to 128$, Tanh).
- **Decoupled Output Heads:**
  1. **Actor Head $\pi_\theta(a|\mathbf{s}_t)$:** Policy logits modulated by threat-adaptive exploration temperature $\tau_t = \tau_0 \exp(-\beta \mathcal{L}_{\mathrm{threat}})$.
  2. **Critic Head $V_\phi(\mathbf{s}_t)$:** State-value baseline for variance reduction.
  3. **Auxiliary Risk Prediction Head $\hat{\mathbf{r}}_{t+1}$:** Forecasts next-step risk vector (active during PPO updates, detached at runtime).

### Region D: Mitigation, Queue & Recovery
- **Dual Operational Safety Guardrails:**
  - *Gate 1 (Dispatch Validation):* Confirms action targets an active fault code or risk $> 0.30$; invalid dispatches are flagged as unnecessary dispatches (driving FMR).
  - *Gate 2 (Transient Drop Filter):* Stochastically models transient cloud API drop with probability $\epsilon_{\mathrm{queue}} = 0.08$.
- **Asynchronous Execution Queue:** Enforces action delays $\tau \in \{0, 1, 2\}$ and tracks transient resource footprints ($\Delta\mathrm{CPU}, \Delta\mathrm{RAM}$).
- **Actuator Layer:** Maps abstract actions $a_1$--$a_8$ to concrete cloud-native controllers (`cert-manager`, Kubernetes rolling updates, HashiCorp Vault, OPA/Gatekeeper admission policies, and Redis cache purges).
- **Active Service Healing Path (Operational Loop):** A prominent dashed green feedback path directly routes from the actuators back to the microservices in Region A, modeling node risk reduction ($-80\%\sigma$) and availability restoration ($+15\%\sigma$).

### Region E: Performance Evaluation & RL Feedback Loop
- **Real-Time SRE Metrics:** Displays the 4 quantitative evaluation metrics (Availability $A_t \ge 90\%$, MTTR recovery steps, Risk Reduction $\Delta R_t$, and False Mitigation Rate FMR).
- **Scalarized Multi-Objective Reward:** Formulates the reward balancing risk reduction, availability, recovery speed, and resource efficiency against operational penalties.
- **Policy Gradient Adaptation Path (Learning Loop):** A distinct dotted teal arrow routes from the PPO optimization block back to the RL Controller in Region C, representing the experience replay trajectory buffer and policy gradient parameter updates ($\nabla_\theta \mathcal{L}_{\mathrm{PPO}}$).

---

## 4. Detailed Architecture of the Redesigned Neural Policy Figure

The companion neural architecture diagram (`secchaos_network_architecture.pdf`) provides an exact, mathematically rigorous representation of Section 4.3:
1. **Semantic Categorization of $\mathbf{s}_t \in \mathbb{R}^{16}$:** Grouped into 5 shaded panels (Security Risks, Threat Metrics, Cluster Telemetry, Resilience QoS, and Execution Status).
2. **Feature Embedding & Gating:** Explicitly shows the $16 \times 32$ linear transformation and the multiplicative gating connection driven by threat input $s_5 = \mathcal{L}_{\mathrm{threat}}$.
3. **Multi-Head Self-Attention:** Formulates the $H=2$ attention mechanism with query, key, and value matrices ($d_k=16$).
4. **Three Decoupled Heads:** Shows the distinct linear projections from latent vector $\mathbf{z}_t \in \mathbb{R}^{128}$ to Actor, Critic, and Auxiliary heads, with explicit notes highlighting that the Auxiliary Head is detached during online inference ($0.44$\,ms latency).

---

## 5. Visual Design Guidelines Followed

In strict adherence to the visual styling requirements:
- **Clean Flat Vector Graphics:** Pure white background, thin uniform line widths ($0.55\text{--}0.75$\,pt), uniform LaTeX arrowheads (`Latex`).
- **Restrained Color Palette:** Uses 5 semantic, color-blind conscious hues (Slate Blue `#1A5276`, Deep Crimson `#922B21`, Deep Teal `#0E6655`, Amber Ochre `#B9770E`, Forest Green `#1E8449`).
- **Zero Decorative AI Clutter:** No 3D effects, gradients, shadows, cartoon avatars, robot illustrations, or unnecessary marketing icons.
- **Typography:** Standard document sans-serif font matching the journal class hierarchy.
- **Editable Source Files:** Maintained full `.tex` source files for both diagrams, accompanied by compiled vector `.pdf` and standards-compliant `.svg` files.

---

## 6. Verification and Integration Status

- Both vector diagrams compile cleanly via `pdflatex` with 0 errors and 0 warnings.
- Converted to pure SVG vector format via `pdftocairo -svg`.
- Embedded into the Wiley LaTeX manuscript source `secchaos_wiley.tex`.
- The complete manuscript compiles with `pdflatex + bibtex` into a publication-ready 19-page PDF with 0 undefined references and 0 missing citation keys.
