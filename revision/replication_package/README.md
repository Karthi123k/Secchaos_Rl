# SecChaos-RL: Replication Package

This replication package contains the complete source code, experimental harness, raw telemetry datasets, and automated statistical analysis scripts for reproducing all results, tables, and figures published in the manuscript:

> **"SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos"**  
> Target Journal: *Software: Practice and Experience* (Wiley)

---

## 1. Directory Structure

```
replication_package/
├── README.md                      # This reproduction guide
├── requirements.txt               # Python package dependencies
├── secchaos_framework.py          # Core framework: ChaosEngine, DependencyTopology, agents, environments
├── run_full_benchmark.py          # Master benchmark runner (8 policies + 6 ablation configs over 30 seeds)
├── generate_latex_tables.py       # Table generator reconciling raw CSVs with Tables 3, 4, 5
├── raw_benchmark_metrics.csv      # Raw per-seed evaluation metrics across 8 policies (240 rows)
├── raw_ablation_metrics.csv       # Raw per-seed evaluation metrics across 6 ablation stages (180 rows)
├── summary_benchmark_table.csv    # Aggregated summary statistics for 8 policies (mean, std, 95% CI)
├── summary_ablation_table.csv     # Aggregated summary statistics for 6 ablation stages (mean, std)
├── statistical_tests.json         # Repeated-measures ANOVA, paired t-tests, Holm-Bonferroni p-values
└── tables_latex.tex               # LaTeX tables 3, 4 (Panel A/B), and 5 (Panel A/B)
```

---

## 2. Environment Setup

Python 3.10+ and PyTorch 2.0+ are recommended. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Immediate Reproduction of Tables and Statistical Tests

To verify all published tables and statistical tests from the raw telemetry CSVs without re-running the 250-episode training runs:

```bash
python generate_latex_tables.py
```

This script reads `raw_benchmark_metrics.csv` and `raw_ablation_metrics.csv`, calculates paired $t$-tests, Wilcoxon signed-rank tests, Holm-Bonferroni adjusted $p$-values, and Cohen's $d$ effect sizes, and outputs `tables_latex.tex`.

---

## 4. Re-running the Complete Empirical Benchmark (30 Seeds)

To train and evaluate all eight baseline policies and the six ablation stages from scratch across all 30 random seeds (`range(2026, 2056)`):

```bash
python run_full_benchmark.py
```

*Note:* This script utilizes Python `multiprocessing` pinned to 1 thread per worker to execute 420 independent training and evaluation runs. On a 16-core workstation (e.g., Intel Core i7-13700), execution completes in approximately 6 to 8 minutes.

---

## 5. Contact & Zenodo DOI Reservation

- Author: Thurbilli Karthik (`405124053@nitt.edu`)
- Persistent Zenodo Archive Reservation: `10.5281/zenodo.1492026`
- GitHub Organization: `https://github.com/SecChaos-RL/SecChaos-RL-Artifacts`
