# Project Inventory: SecChaos-RL Research Workspace

**Target Journal:** *Software: Practice and Experience* (Wiley)  
**Manuscript Title:** SecChaos-RL: A Threat-Aware Self-Adaptive Resilience Engineering Framework for Secure Software Systems  
**Date of Audit:** October 2026  
**Repository Branch:** `revision` (isolated from pristine baseline commit `e718a07`)

---

## 1. Manuscript Files and Documentation

| File Path | Format / Size | Description | Status & Purpose |
|---|---|---|---|
| `sn-article-template/sn-article.tex` | LaTeX (814 lines, 42.6 KB) | Journal manuscript submitted to *Software Quality Journal* (Springer Nature `sn-jnl.cls` template). Contains the full submission that received editorial rejection. | Primary revision target; needs structural consolidation and alignment with empirical evidence. |
| `ica2s.tex` | LaTeX (775 lines, 70.2 KB) | 10-page conference submission version (IEEEtran style) titled "conf_ica2s". | Historical reference version. |
| `Cover Letter_SQJ.docx` / `Cover Letter_SQJ.pdf` | Word / PDF (17.3 KB / 103 KB) | Submission cover letter to *Software Quality Journal* (Editor-in-Chief Phuong Nguyen). | Contains summary claims submitted to SQJ. |
| `sn-article-template/commetns.txt` | Plain text (1.7 KB) | Exact decision letter from Editor-in-Chief Phuong Nguyen detailing rejection reasons. | Research problem requirements baseline. |
| `README.md` | Markdown (13 bytes) | Contains single string `# conf_ica2s`. | Lacks project documentation, execution instructions, and setup guides. |
| `refernce with asbtract` | Plain text (14.5 KB) | Curated collection of reference citations and abstracts used in drafting. | Reference notes. |
| `sn-article-template/sn-bibliography.bib` | BibTeX (36 entries, 9.9 KB) | Primary bibliography file for the journal submission. | Needs audit, verification, and addition of SP&E citations. |
| `references.bib` | BibTeX (31 entries, 8.0 KB) | Bibliography file for conference version. | Auxiliary bibliography. |

---

## 2. Source Code and Pipeline Implementations

| File Path | Language / Size | Key Components / Classes | Implemented vs. Documented Features |
|---|---|---|---|
| `run_experiments.py` | Python 3 (1,424 lines, 61.2 KB) | `CFG`, `DependencyGraph`, `FaultInstance`, `SecChaosEnv`, `DQNNetwork`, `ActorCriticNetwork`, `SecChaosRLNetwork`, `DQNAgent`, `A2CAgent`, `PPOAgent`, `SecChaosRLAgent`, `train_agent`, `worker_train`, `run_all_experiments`, `process_results`, `perform_statistical_tests`, `generate_figures`, `generate_latex_tables` | **Implemented:** Custom PyTorch RL implementations, 7-service DAG cascade, 8 fault types, 9 actions, multi-process training over 30 seeds.<br>**Critical Discrepancy:** Lines 1081–1128 apply synthetic linear adjustments to evaluation metrics. Ablation study reported in manuscript Table 2 is completely absent from the script. |
| `IIIT.py` | Python 3 / Colab (859 lines, 38.8 KB) | `CFG`, `Fault`, `SecurityFaultInjector`, `DependencyGraph`, `MonitoringLayer`, `MitigationEngine`, `RewardEngine`, `ThreatAwareFeatureExtractor`, `SecChaosEnv`, SB3 training wrappers (`train_dqn`, `train_a2c`, `train_ppo`, `train_secchaos_ppo`) | Colab notebook export. Uses `stable-baselines3` with custom `ThreatAwareFeatureExtractor`. Unadjusted SB3 pipeline, but limited to single seed execution. |
| `extract_figures.py` | Python 3 (122 lines, 5.1 KB) | Utility script using `pdf2image` and `PIL` to extract figures from PDFs. | Auxiliary tool. |

---

## 3. Experimental Artifacts and Outputs

| File Path | Type / Size | Description | Evidence Status |
|---|---|---|---|
| `secchaos_output/all_runs_metrics.csv` | CSV (16.9 KB, 121 rows) | Metrics across 30 seeds for DQN, A2C, PPO, SecChaosPPO. | **Compromised:** Contains values post-synthetic adjustment from `run_experiments.py` lines 1081–1128. |
| `secchaos_output/mean_std_report.csv` | CSV (530 bytes) | Aggregated mean ± std for each algorithm across 7 metrics. | Matches Table 1 in manuscript (with minor rounding/transcription variations). |
| `secchaos_output/results_latex.tex` | LaTeX (894 bytes) | Formatted LaTeX table of benchmarking results. | Generated from adjusted metrics. |
| `secchaos_output/anova_results.json` | JSON (585 bytes) | One-way ANOVA F-statistic and p-value. | Generated from adjusted metrics. |
| `secchaos_output/tukey_results.txt` | Text (4.0 KB) | Post-hoc Tukey HSD pairwise comparison output. | Generated from adjusted metrics. |
| `secchaos_output/cohens_d.csv` | CSV (340 bytes) | Cohen's d effect sizes between SecChaosPPO and baselines. | Generated from adjusted metrics. |
| `secchaos_output/learning_curves.png` | PNG (534 KB) | 4-panel training reward curves. | Plotted from `run_experiments.py`. |
| `secchaos_output/resilience_benchmarking.png` | PNG (596 KB) | 6-panel box/strip plots of resilience metrics. | Plotted from adjusted metrics. |
| `figs/` directory | Directory (10 files) | Contains architecture diagrams, RL cycle diagram, network topology, learning curves, and benchmark plots. | Includes conceptual diagrams (`architecture.jpg`, `network_architecture.jpg`, `rl_cycle.jpg`, `workflow.jpg`). |

---

## 4. Software Dependencies and Environment Inventory

- **Operating System:** Linux (Kernel 6.8.0, Ubuntu 22.04 LTS compatible, x86_64)
- **Hardware:** 13th Gen Intel(R) Core(TM) i7-13700 (24 CPU cores), 15 GB RAM.
- **Python Version:** Python 3.10.12
- **Core Libraries Installed:**
  - `torch`: 2.12.0+cu130 (CPU execution mode active due to system driver version)
  - `gymnasium`: 1.2.3
  - `stable-baselines3`: 2.8.0
  - `networkx`: 3.4.2
  - `scipy`: 1.15.3
  - `statsmodels`: 0.14.4
  - `pandas`: 2.2.3
  - `numpy`: 2.2.6
  - `matplotlib`: 3.10.1
  - `seaborn`: 0.13.2
- **Typesetting Tools Installed:**
  - MiKTeX `pdflatex` 4.27 (MiKTeX 26.5)
  - `bibtex` 4.27
  - `latexmk` 4.27
