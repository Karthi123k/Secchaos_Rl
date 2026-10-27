# Author Verification and Pre-Submission Checklist

**Manuscript Title:** SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos  
**Target Journal:** *Software: Practice and Experience* (Wiley)  
**Document Purpose:** Mandatory verification checklist for authors prior to journal portal upload  
**Date:** 2026-10-27  

---

## Instructions for Authors
Before uploading the revised manuscript package to the Wiley submission system for *Software: Practice and Experience*, please review and confirm each of the following verification checkpoints. All items have been checked during the comprehensive revision; this checklist ensures alignment across all co-authors.

---

## 1. Author Metadata and Affiliations

- [ ] **Author Names and Order:**
  - Karthik S. (Lead Researcher)
  - Co-authors / Research Advisors
- [ ] **Affiliations:**
  - Department of Computer Applications / Computer Science and Engineering, National Institute of Technology Tiruchirappalli, Tamil Nadu, India
  - Department of Computer Science and Engineering, National Institute of Technology Warangal, Telangana, India
- [ ] **Corresponding Author Information:**
  - Corresponding author name, active institutional email address (`@nitt.edu.in` / `@nitw.ac.in`), and postal address are correctly specified in `secchaos_wiley.tex` (`\author[1]{...}`, `\corres{...}`).
- [ ] **ORCID Identifiers:**
  - Ensure all authors' 16-digit ORCID iDs are registered and linked in the Wiley submission system.

---

## 2. Abstract and Manuscript Metadata

- [ ] **Abstract Word Count Compliance:**
  - Target: $\le 250$ words (Strict Wiley guideline; our revised abstract is **EXACTLY 200 words**).
  - Location: Verified in `revised_manuscript/revised_abstract.txt` and embedded in `secchaos_wiley.tex`.
  - Structure: Clearly separated into *Background*, *Gap*, *Objective*, *Methodology*, *Key Results*, and *Practical Impact*.
  - Verification: Run `python3 -c "print(len(open('revised_abstract.txt').read().split()))"` $\rightarrow$ `200`.
- [ ] **Keywords:**
  - Exactly 6 descriptive keywords compliant with Wiley format:
    `Security Chaos Engineering | Microservice Resilience | Reinforcement Learning | Self-Adaptive Systems | Fault Injection | DevSecOps`
- [ ] **Manuscript Title:**
  - Confirmed as non-promotional and technically descriptive: *SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos*.

---

## 3. Mathematical and Theoretical Formulations

- [ ] **Resilience Score Calculation & Jensen's Inequality (Section 5.5):**
  - Verify that the manuscript explicitly distinguishes the **per-seed mean resilience score** ($45.21\% \pm 2.26\%$) from the score evaluated at **aggregate metric means** ($44.94\%$).
  - Confirm the non-linear composite formulation:
    $$\mathcal{R} = w_R \cdot \bar{R}_{\mathrm{sec}} + w_A \cdot \bar{A} + w_M \cdot \left(1 - \frac{\mathrm{MTTR}}{\mathrm{MTTR}_{\max}}\right)$$
  - Confirm that per-seed calculation is used for all reported 95% confidence intervals and paired statistical hypothesis tests.
- [ ] **Signed Risk Reduction (Section 5.5, Equation 15):**
  - Verify that negative risk reduction is no longer clipped by $\max(0, \cdot)$.
  - Confirm that policies worsening security risk exhibit negative values (e.g., No-Mitigation reports baseline $0.00\% \pm 0.00\%$).
- [ ] **State Space Dimension (Section 4.2.1):**
  - Verify Table 2 details the exact 16-feature vector $s_t \in \mathbb{R}^{16}$ across latency, error rate, queue occupancy, threat level, CPU, memory, and mitigation status.
- [ ] **Action Space Consistency (Section 4.2.2 vs. Section 7.2):**
  - Confirm the exact 1-to-1 mapping between the formal Markov Decision Process discrete action set $\mathcal{A} = \{0, 1, \dots, 8\}$ in Section 4.2.2 and the Kubernetes operator deployment architecture in Section 7.2:
    - $a=0$: No-Op / Idle
    - $a=1$: Rotate Service Certificate (`cert-manager` TLS Secret rotation)
    - $a=2$: Patch Dependency (`k8s` Pod rolling update / hotfix patch)
    - $a=3$: Rotate Access Secret (Vault secret renewal / injection)
    - $a=4$: Restrict RBAC Permissions (`RoleBinding` scope lockdown)
    - $a=5$: Enable Multi-Factor Authentication / Session Invalidation (Redis session purge)
    - $a=6$: Apply Security Patch (Base image tag update)
    - $a=7$: Revoke Privilege (ServiceAccount privilege de-escalation)
    - $a=8$: Rollback Deployment (`helm rollback` / ReplicaSet rollback)

---

## 4. Algorithmic and Operational Safety Guarantees

- [ ] **Algorithm 1 Specification (Section 4.4):**
  - Verify that Algorithm 1 explicitly models:
    1. Action validation against dependency topology constraints.
    2. The transient 8% queue-admission failure probability ($\epsilon_{\mathrm{queue}} = 0.08$).
    3. The distinction between unnecessary dispatches (mitigation applied when unnecessary) and queue redundancies (identical action already in-flight).
    4. Execution verification step prior to updating mitigation state.

---

## 5. Experimental Data and Numerical Consistency

Confirm that all numbers in the revised manuscript match the verified experimental logs:

- [ ] **Main Comparative Benchmark (Table 3):**
  - **No Mitigation:** Risk Red: $0.00\% \pm 0.00\%$, Availability: $67.4\% \pm 1.8\%$, MTTR: $4.85 \pm 0.42$, Resilience: $24.8\% \pm 1.2\%$.
  - **Random Policy:** Risk Red: $12.4\% \pm 3.1\%$, Availability: $71.2\% \pm 2.0\%$, MTTR: $3.92 \pm 0.38$, Resilience: $29.5\% \pm 1.5\%$.
  - **Rule-Based Alert:** Risk Red: $55.5\% \pm 4.8\%$, Availability: $78.2\% \pm 2.5\%$, MTTR: $2.85 \pm 0.35$, Resilience: $38.4\% \pm 1.8\%$, Total Acts: $50.0 \pm 0.1$, Wrong Acts: $15.4 \pm 2.5$, FMR: $30.8\% \pm 4.9\%$.
  - **Threshold-Based:** Risk Red: $19.8\% \pm 3.4\%$, Availability: $84.5\% \pm 2.1\%$, MTTR: $2.29 \pm 0.30$, Resilience: $38.7\% \pm 1.6\%$, Total Acts: $41.2 \pm 2.8$, Wrong Acts: $10.1 \pm 2.1$, FMR: $24.5\% \pm 4.6\%$.
  - **Queue-Aware Cooldown:** Risk Red: $26.3\% \pm 2.9\%$, Availability: $86.1\% \pm 1.9\%$, MTTR: $2.24 \pm 0.23$, Resilience: $40.5\% \pm 1.4\%$, Total Acts: $38.6 \pm 2.4$, Wrong Acts: $8.9 \pm 1.8$, FMR: $23.1\% \pm 4.2\%$.
  - **DQN:** Risk Red: $4.2\% \pm 3.8\%$, Availability: $89.8\% \pm 2.2\%$, MTTR: $1.72 \pm 0.51$, Resilience: $45.1\% \pm 2.2\%$.
  - **Standard PPO:** Risk Red: $4.8\% \pm 3.5\%$, Availability: $90.6\% \pm 2.1\%$, MTTR: $1.68 \pm 0.52$, Resilience: $45.9\% \pm 2.3\%$.
  - **SecChaos-RL:** Risk Red: $3.9\% \pm 4.1\%$, Availability: $90.6\% \pm 2.2\%$, MTTR: $1.79 \pm 0.53$, Resilience: $45.2\% \pm 2.3\%$, Total Acts: $35.3 \pm 3.0$, Wrong Acts: $7.5 \pm 1.9$, FMR: $20.9\% \pm 4.4\%$.
- [ ] **Statistical Significance Tests (Table 4 & Table 5):**
  - Sign convention explicitly stated: $\Delta = \text{SecChaos-RL} - \text{Comparator}$.
  - SecChaos-RL vs. Threshold-Based: Recovery MTTR $\Delta = -0.50$ steps, paired $t = -3.82$, $p_{\mathrm{holm}} = 0.0013$, Cohen's $d = -0.78$ (statistically significant faster recovery).
  - SecChaos-RL vs. Queue-Aware Cooldown: Recovery MTTR $\Delta = -0.45$ steps, paired $t = -3.76$, $p_{\mathrm{holm}} = 0.0013$, Cohen's $d = -0.78$ (statistically significant faster recovery).
  - SecChaos-RL vs. Standard PPO: Resilience score difference $\Delta = -0.70\%$, paired $t = -1.30$, $p = 0.2044$ (non-significant; SecChaos-RL matches PPO resilience while providing threat-awareness, auxiliary risk forecasting, and lower action churn).
- [ ] **Ablation Study Consistency (Table 6):**
  - All 5 ablation variants (Vanilla PPO, +MHSA, +Threat Gating, +Aux Risk Head, Full Framework) match exactly between Table 3 and Table 6.
- [ ] **Inference Latency Microbenchmarks (Section 6.4):**
  - Online runtime decision latency: $0.44 \pm 0.15$\,ms per step.
  - Offline CPU single-thread benchmark (1,000 steps): Mean $0.46 \pm 0.52$\,ms, $p_{50} = 0.32$\,ms, $p_{95} = 0.81$\,ms, $p_{99} = 1.04$\,ms.

---

## 6. Citations and Bibliography Audit

- [ ] **Reference Count:** Exactly 41 references in `references.bib`.
- [ ] **In-Text Citation Check:** All 41 entries are cited in the manuscript (`0` uncited entries, `0` missing entries).
- [ ] **DOI Verification:** 27 references possess verified, resolving Crossref DOIs (see `revised_manuscript/reference_audit.md`).
- [ ] **Non-DOI Justifications:** 14 references without DOIs have verified alternative persistent identifiers (ISBNs for standard books, arXiv preprints, PMLR/NeurIPS official proceedings, and official software documentation URLs).
- [ ] **BibTeX Warnings/Errors:** Clean compilation with `bibtex secchaos_wiley` (0 errors, 0 warnings).

---

## 7. Journal Formatting and Styling (*Software: Practice and Experience*)

- [ ] **Wiley Template Compliance:**
  - Layout built on `USG.cls` (`\documentclass[oupdoi]{USG}`).
  - BibTeX style: `wileyNJD-Chicago.bst`.
- [ ] **Floating Bodies and Page Budget:**
  - No orphaned headers or runaway table rows.
  - Section 1 begins cleanly on page 1 without blank page overflows.
  - Total manuscript length: 19 pages (compact, standard journal length for comprehensive research).
- [ ] **Mandatory End-Matter Sections:**
  - `\section*{Acknowledgements}`: Funding and lab compute infrastructure acknowledgements.
  - `\section*{Conflict of Interest}`: Explicit declaration of no competing financial or personal interests.
  - `\section*{Data Availability Statement}`: Repository URL provided for open-source reproducibility.
  - `\section*{Author Contributions}`: CRediT taxonomy roles explicitly documented for all authors.

---

## 8. Artifact and Deliverables Checklist

Confirm the presence of all required files in `revised_manuscript/`:

| File Name | Description | Status |
| :--- | :--- | :---: |
| `secchaos_wiley.tex` | Master LaTeX source file using Wiley design layout | [ ] Present |
| `secchaos_wiley.pdf` | Cleanly compiled 19-page PDF | [ ] Present |
| `references.bib` | Updated BibTeX file with verified DOIs and clean syntax | [ ] Present |
| `revised_abstract.txt` | Standalone abstract text (**EXACTLY 200 words**) | [ ] Present |
| `reference_audit.md` | Comprehensive citation and DOI verification report | [ ] Present |
| `revision_report.md` | Section-by-section improvements and AI-phrasing elimination report | [ ] Present |
| `author_verification_checklist.md` | This pre-submission confirmation checklist | [ ] Present |
| `USG.cls` & style files | Wiley NJD journal class and supporting macro packages | [ ] Present |
| `figs/` & `images/` | All architecture diagrams, flowcharts, and evaluation plots | [ ] Present |

---

## Author Sign-Off
I confirm that the revised manuscript has been reviewed against the above criteria, all numerical results and theoretical formulations are verified, and the package is ready for final journal submission to *Software: Practice and Experience*.

**Lead / Corresponding Author Signature:** ___________________________  
**Date:** ___________________________  
