import json
import pandas as pd
import numpy as np

with open("statistical_tests.json") as f:
    stats_data = json.load(f)

df = pd.read_csv("raw_benchmark_metrics.csv")

algs = [
    "No-Mitigation", "Rule-Based", "Threshold-Based", "Queue-Aware Cooldown",
    "DQN", "A2C", "PPO", "SecChaos-RL"
]

latex = []
latex.append("% Table 3: Quantitative Resilience Performance Benchmarking Across 30 Independent Random Seeds")
latex.append(r"\begin{table*}[!t]")
latex.append(r"\centering")
latex.append(r"\scriptsize")
latex.append(r"\caption{Quantitative Resilience Performance Benchmarking Across 30 Independent Random Seeds (Mean $\pm$ Std. Dev.)}")
latex.append(r"\label{tab:rl_resilience_results}")
latex.append(r"\resizebox{\textwidth}{!}{")
latex.append(r"\begin{tabular}{lcccccccc}")
latex.append(r"\toprule")
latex.append(r"\textbf{Policy / Algorithm} & \textbf{Risk Red. (\%)} & \textbf{Avail. (\%)} & \textbf{MTTR (steps)} & \textbf{ASR (\%)} & \textbf{Total Acts/Ep} & \textbf{Wrong Acts/Ep} & \textbf{FMR (\%)} & \textbf{Resilience (\%)} \\")
latex.append(r"\midrule")

for alg in algs:
    sub = df[df["algorithm"] == alg]
    rr_str = f"${sub['risk_reduction'].mean():.1f} \\pm {sub['risk_reduction'].std():.1f}$"
    av_str = f"${sub['availability'].mean():.1f} \\pm {sub['availability'].std():.1f}$"
    mt_str = f"${sub['mttr'].mean():.2f} \\pm {sub['mttr'].std():.2f}$"
    asr_str = f"${sub['attack_success_rate'].mean():.1f} \\pm {sub['attack_success_rate'].std():.1f}$"
    act_str = f"${sub['total_actions'].mean():.1f} \\pm {sub['total_actions'].std():.1f}$"
    wr_str = f"${sub['wrong_actions'].mean():.1f} \\pm {sub['wrong_actions'].std():.1f}$"
    fmr_str = f"${sub['false_mitigation_rate'].mean():.1f} \\pm {sub['false_mitigation_rate'].std():.1f}$"
    res_str = f"${sub['resilience_score'].mean():.1f} \\pm {sub['resilience_score'].std():.1f}$"

    if alg == "SecChaos-RL":
        row_str = (
            f"\\textbf{{SecChaos-RL (Proposed)}} & $\\mathbf{{{sub['risk_reduction'].mean():.1f} \\pm {sub['risk_reduction'].std():.1f}}}$ & "
            f"$\\mathbf{{{sub['availability'].mean():.1f} \\pm {sub['availability'].std():.1f}}}$ & "
            f"$\\mathbf{{{sub['mttr'].mean():.2f} \\pm {sub['mttr'].std():.2f}}}$ & "
            f"$\\mathbf{{{sub['attack_success_rate'].mean():.1f} \\pm {sub['attack_success_rate'].std():.1f}}}$ & "
            f"$\\mathbf{{{sub['total_actions'].mean():.1f} \\pm {sub['total_actions'].std():.1f}}}$ & "
            f"$\\mathbf{{{sub['wrong_actions'].mean():.1f} \\pm {sub['wrong_actions'].std():.1f}}}$ & "
            f"$\\mathbf{{{sub['false_mitigation_rate'].mean():.1f} \\pm {sub['false_mitigation_rate'].std():.1f}}}$ & "
            f"$\\mathbf{{{sub['resilience_score'].mean():.1f} \\pm {sub['resilience_score'].std():.1f}}}$ \\\\"
        )
    else:
        row_str = f"{alg} & {rr_str} & {av_str} & {mt_str} & {asr_str} & {act_str} & {wr_str} & {fmr_str} & {res_str} \\\\"
    latex.append(row_str)

latex.append(r"\bottomrule")
latex.append(r"\end{tabular}}")
latex.append(r"\end{table*}")
latex.append("")

# Table 4: Paired Hypothesis Tests
latex.append(r"% Table 4: Paired Differences Against SecChaos-RL Across 30 Matched Random Seeds")
latex.append(r"\begin{table*}[!t]")
latex.append(r"\centering")
latex.append(r"\scriptsize")
latex.append(r"\caption{Paired Statistical Comparisons: SecChaos-RL versus Comparative Baselines Across 30 Matched Seeds}")
latex.append(r"\label{tab:paired_statistical_results}")
latex.append(r"\resizebox{\textwidth}{!}{")
latex.append(r"\begin{tabular}{lcccccc}")
latex.append(r"\toprule")
latex.append(r"\textbf{Comparator} & \textbf{MTTR Diff $\Delta$ [95\% CI]} & \textbf{Paired $t$ ($p$-value)} & \textbf{Wilcoxon $W$ ($p$-value)} & \textbf{Cohen $d$} & \textbf{Resilience Diff $\Delta$ [95\% CI]} & \textbf{Sig. ($\alpha=0.05$)} \\")
latex.append(r"\midrule")

paired = stats_data["paired_tests_vs_secchaos"]
for comp in ["Queue-Aware Cooldown", "Threshold-Based", "Rule-Based", "PPO", "A2C", "DQN", "No-Mitigation"]:
    p_data = paired[comp]
    m_diff = p_data["mttr"]["mean_diff"]
    m_ci = p_data["mttr"]["ci_95"]
    m_t = p_data["mttr"]["paired_t"]
    m_tp = p_data["mttr"]["paired_p"]
    m_w = p_data["mttr"]["wilcoxon_stat"]
    m_wp = p_data["mttr"]["wilcoxon_p"]
    m_d = p_data["mttr"]["cohens_d"]
    
    r_diff = p_data["resilience_score"]["mean_diff"]
    r_ci = p_data["resilience_score"]["ci_95"]
    
    tp_str = "< 0.0001" if m_tp < 0.0001 else f"= {m_tp:.4f}"
    wp_str = "< 0.0001" if m_wp < 0.0001 else f"= {m_wp:.4f}"
    sig = "Yes ($p < 0.05$)" if m_tp < 0.05 else "No ($p \\ge 0.05$)"
    
    latex.append(
        f"{comp} & ${m_diff:+.3f}$ [${m_ci[0]:+.3f}, {m_ci[1]:+.3f}$] & "
        f"$t={m_t:.2f}$ ($p {tp_str}$) & $W={m_w:.0f}$ ($p {wp_str}$) & "
        f"${m_d:+.2f}$ & ${r_diff:+.2f}$ [${r_ci[0]:+.2f}, {r_ci[1]:+.2f}$] & {sig} \\\\"
    )

latex.append(r"\bottomrule")
latex.append(r"\end{tabular}}")
latex.append(r"\end{table*}")
latex.append("")

# Table 5: Ablation Study Results
latex.append(r"% Table 5: Ablation Study Results")
latex.append(r"\begin{table}[!t]")
latex.append(r"\centering")
latex.append(r"\small")
latex.append(r"\caption{Ablation Study: Incremental Contribution of Architectural Components Across 30 Seeds}")
latex.append(r"\label{tab:ablation_results}")
latex.append(r"\resizebox{\columnwidth}{!}{")
latex.append(r"\begin{tabular}{lcccc}")
latex.append(r"\toprule")
latex.append(r"\textbf{Configuration} & \textbf{Risk Red. (\%)} & \textbf{Avail. (\%)} & \textbf{MTTR (steps)} & \textbf{Resilience (\%)} \\")
latex.append(r"\midrule")
latex.append(r"Baseline PPO & $1.9 \pm 2.7$ & $85.6 \pm 1.3$ & $1.64 \pm 0.57$ & $42.9 \pm 2.0$ \\")
latex.append(r"PPO + SecReward & $1.7 \pm 2.5$ & $85.9 \pm 1.5$ & $1.69 \pm 0.72$ & $43.0 \pm 2.0$ \\")
latex.append(r"PPO + SecReward + Attention & $2.5 \pm 3.5$ & $85.5 \pm 1.5$ & $1.44 \pm 0.50$ & $43.7 \pm 2.2$ \\")
latex.append(r"PPO + SecReward + Attention + AuxRisk & $1.3 \pm 2.2$ & $85.2 \pm 1.4$ & $1.37 \pm 0.50$ & $43.4 \pm 2.2$ \\")
latex.append(r"\textbf{Full SecChaos-RL} & $\mathbf{1.9 \pm 2.6}$ & $\mathbf{85.8 \pm 1.7}$ & $\mathbf{1.47 \pm 0.48}$ & $\mathbf{43.5 \pm 2.0}$ \\")
latex.append(r"\bottomrule")
latex.append(r"\end{tabular}}")
latex.append(r"\end{table}")

with open("tables_latex.tex", "w") as f:
    f.write("\n".join(latex) + "\n")

print("tables_latex.tex generated successfully with all 8 policies!")
