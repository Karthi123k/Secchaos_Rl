import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.anova import AnovaRM
import json

df = pd.read_csv("raw_benchmark_metrics.csv")

# 1. Repeated-Measures ANOVA across 8 policies over 30 seeds
metrics = ["resilience_score", "risk_reduction", "availability", "mttr", "attack_success_rate", "false_mitigation_rate"]
rm_results = {}
print("=== REPEATED-MEASURES ANOVA (8 POLICIES, 30 SEEDS) ===")
for m in metrics:
    rm = AnovaRM(df, m, "seed", within=["algorithm"]).fit()
    f_val = float(rm.anova_table["F Value"].iloc[0])
    p_val = float(rm.anova_table["Pr > F"].iloc[0])
    num_df = int(rm.anova_table["Num DF"].iloc[0])
    den_df = int(rm.anova_table["Den DF"].iloc[0])
    rm_results[m] = {"F": f_val, "p": p_val, "df1": num_df, "df2": den_df}
    print("RM-ANOVA %-22s: F(%d, %d) = %8.2f, p = %.4e" % (m, num_df, den_df, f_val, p_val))

# 2. Paired tests between SecChaos-RL and other 7 policies
sec = df[df["algorithm"] == "SecChaos-RL"].sort_values("seed").set_index("seed")
paired_results = {}
comparators = [
    "Rule-Based", "Threshold-Based", "Queue-Aware Cooldown",
    "PPO", "A2C", "DQN", "No-Mitigation"
]

print("\n=== PAIRED STATISTICAL COMPARISONS (SecChaos-RL vs Comparators) ===")
for other in comparators:
    comp = df[df["algorithm"] == other].sort_values("seed").set_index("seed")
    paired_results[other] = {}
    for m in ["mttr", "resilience_score", "risk_reduction", "availability", "false_mitigation_rate"]:
        diff = sec[m] - comp[m]
        mean_d = float(np.mean(diff))
        std_d = float(np.std(diff, ddof=1))
        ci = stats.t.interval(0.95, len(diff)-1, loc=mean_d, scale=stats.sem(diff))
        t_stat, t_p = stats.ttest_rel(sec[m], comp[m])
        w_stat, w_p = stats.wilcoxon(sec[m], comp[m])
        d = mean_d / (std_d + 1e-8)
        paired_results[other][m] = {
            "mean_diff": mean_d,
            "ci_95": [float(ci[0]), float(ci[1])],
            "paired_t": float(t_stat),
            "paired_p": float(t_p),
            "wilcoxon_stat": float(w_stat),
            "wilcoxon_p": float(w_p),
            "cohens_d": float(d)
        }
    m_data = paired_results[other]["mttr"]
    print("%-22s: MTTR delta = %+6.3f [%+6.3f, %+6.3f], t=%+5.2f (p=%.4f), W=%3.0f (p=%.4f)" % (
        other, m_data["mean_diff"], m_data["ci_95"][0], m_data["ci_95"][1],
        m_data["paired_t"], m_data["paired_p"], m_data["wilcoxon_stat"], m_data["wilcoxon_p"]
    ))

# Save to statistical_tests.json
with open("statistical_tests.json", "w") as f:
    json.dump({"rm_anova": rm_results, "paired_tests_vs_secchaos": paired_results}, f, indent=2)
print("\nstatistical_tests.json successfully updated!")
