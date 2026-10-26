import json
import pandas as pd
import numpy as np

def generate_tables():
    with open("statistical_tests.json") as f:
        stats_data = json.load(f)

    df_b = pd.read_csv("raw_benchmark_metrics.csv")
    df_a = pd.read_csv("raw_ablation_metrics.csv")

    algs = [
        "No-Mitigation", "Rule-Based", "Threshold-Based", "Queue-Aware Cooldown",
        "DQN", "A2C", "PPO", "SecChaos-RL"
    ]

    latex = []
    
    # ==============================================================================
    # Table 3: Quantitative Resilience Performance Benchmarking
    # ==============================================================================
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
        sub = df_b[df_b["algorithm"] == alg]
        rr_mean, rr_std = sub['risk_reduction'].mean(), sub['risk_reduction'].std()
        av_mean, av_std = sub['availability'].mean(), sub['availability'].std()
        mt_mean, mt_std = sub['mttr'].mean(), sub['mttr'].std()
        asr_mean, asr_std = sub['attack_success_rate'].mean(), sub['attack_success_rate'].std()
        act_mean, act_std = sub['total_actions'].mean(), sub['total_actions'].std()
        wr_mean, wr_std = sub['wrong_actions'].mean(), sub['wrong_actions'].std()
        fmr_mean, fmr_std = sub['false_mitigation_rate'].mean(), sub['false_mitigation_rate'].std()
        res_mean, res_std = sub['resilience_score'].mean(), sub['resilience_score'].std()

        # Format wrong actions with 2 decimals if below 0.1 so small counts are not truncated to 0.0
        wr_fmt = f"{wr_mean:.2f} \\pm {wr_std:.2f}" if wr_mean < 0.10 else f"{wr_mean:.1f} \\pm {wr_std:.1f}"

        if alg == "SecChaos-RL":
            row_str = (
                f"\\textbf{{SecChaos-RL (Proposed)}} & $\\mathbf{{{rr_mean:.1f} \\pm {rr_std:.1f}}}$ & "
                f"$\\mathbf{{{av_mean:.1f} \\pm {av_std:.1f}}}$ & "
                f"$\\mathbf{{{mt_mean:.2f} \\pm {mt_std:.2f}}}$ & "
                f"$\\mathbf{{{asr_mean:.1f} \\pm {asr_std:.1f}}}$ & "
                f"$\\mathbf{{{act_mean:.1f} \\pm {act_std:.1f}}}$ & "
                f"$\\mathbf{{{wr_fmt}}}$ & "
                f"$\\mathbf{{{fmr_mean:.1f} \\pm {fmr_std:.1f}}}$ & "
                f"$\\mathbf{{{res_mean:.1f} \\pm {res_std:.1f}}}$ \\\\"
            )
        elif alg == "No-Mitigation":
            row_str = (
                f"No-Mitigation & $0.0 \\pm 0.0$ & "
                f"${av_mean:.1f} \\pm {av_std:.1f}$ & "
                f"${mt_mean:.2f} \\pm {mt_std:.2f}$ & "
                f"${asr_mean:.1f} \\pm {asr_std:.1f}$ & "
                f"$0.0 \\pm 0.0$ & $0.00 \\pm 0.00$ & $0.0 \\pm 0.0$ & "
                f"${res_mean:.1f} \\pm {res_std:.1f}$ \\\\"
            )
        else:
            row_str = (
                f"{alg} & ${rr_mean:.1f} \\pm {rr_std:.1f}$ & "
                f"${av_mean:.1f} \\pm {av_std:.1f}$ & "
                f"${mt_mean:.2f} \\pm {mt_std:.2f}$ & "
                f"${asr_mean:.1f} \\pm {asr_std:.1f}$ & "
                f"${act_mean:.1f} \\pm {act_std:.1f}$ & "
                f"${wr_fmt}$ & "
                f"${fmr_mean:.1f} \\pm {fmr_std:.1f}$ & "
                f"${res_mean:.1f} \\pm {res_std:.1f}$ \\\\"
            )
        latex.append(row_str)

    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}}")
    latex.append(r"\end{table*}")
    latex.append("")

    # ==============================================================================
    # Table 4: Paired Hypothesis Tests (Panel A: MTTR, Panel B: Resilience)
    # ==============================================================================
    latex.append(r"% Table 4: Paired Differences Against SecChaos-RL Across 30 Matched Random Seeds")
    latex.append(r"\begin{table*}[!t]")
    latex.append(r"\centering")
    latex.append(r"\scriptsize")
    latex.append(r"\caption{Paired Statistical Comparisons: SecChaos-RL versus Comparative Baselines Across 30 Matched Seeds. Reporting both unadjusted and Holm-Bonferroni adjusted $p$-values to control the Family-Wise Error Rate ($\alpha=0.05$) across seven pairwise comparisons.}")
    latex.append(r"\label{tab:paired_statistical_results}")
    latex.append(r"\resizebox{\textwidth}{!}{")
    latex.append(r"\begin{tabular}{lcccccccccc}")
    latex.append(r"\toprule")
    latex.append(r" & \multicolumn{5}{c}{\textbf{Panel A: Recovery Speed (MTTR) Comparisons vs. SecChaos-RL}} & \multicolumn{5}{c}{\textbf{Panel B: Holistic Resilience Score Comparisons vs. SecChaos-RL}} \\")
    latex.append(r"\cmidrule(lr){2-6} \cmidrule(lr){7-11}")
    latex.append(r"\textbf{Comparator} & \textbf{Diff $\Delta$ [95\% CI]} & \textbf{Paired $t$ ($p_{raw}$)} & \textbf{Holm $p_{adj}$} & \textbf{Wilcoxon $W$ ($p$)} & \textbf{Cohen $d$} & \textbf{Diff $\Delta$ [95\% CI]} & \textbf{Paired $t$ ($p_{raw}$)} & \textbf{Holm $p_{adj}$} & \textbf{Wilcoxon $W$ ($p$)} & \textbf{Cohen $d$} \\")
    latex.append(r"\midrule")

    paired = stats_data["paired_tests_vs_secchaos"]
    comparators = ["Queue-Aware Cooldown", "Threshold-Based", "Rule-Based", "PPO", "A2C", "DQN", "No-Mitigation"]
    
    for comp in comparators:
        p_data = paired[comp]
        # MTTR metrics
        m_diff = p_data["mttr"]["mean_diff"]
        m_ci = p_data["mttr"]["ci_95"]
        m_t = p_data["mttr"]["paired_t"]
        m_tp = p_data["mttr"]["paired_p"]
        m_holm = p_data["mttr"].get("holm_bonferroni_p", m_tp)
        m_w = p_data["mttr"]["wilcoxon_stat"]
        m_wp = p_data["mttr"]["wilcoxon_p"]
        m_d = p_data["mttr"]["cohens_d"]

        # Resilience metrics
        r_diff = p_data["resilience_score"]["mean_diff"]
        r_ci = p_data["resilience_score"]["ci_95"]
        r_t = p_data["resilience_score"]["paired_t"]
        r_tp = p_data["resilience_score"]["paired_p"]
        r_holm = p_data["resilience_score"].get("holm_bonferroni_p", r_tp)
        r_w = p_data["resilience_score"]["wilcoxon_stat"]
        r_wp = p_data["resilience_score"]["wilcoxon_p"]
        r_d = p_data["resilience_score"]["cohens_d"]

        def fmt_p(p):
            return "< 0.0001" if p < 0.0001 else f"= {p:.4f}"

        row_str = (
            f"{comp} & "
            f"${m_diff:+.3f}$ [${m_ci[0]:+.3f}, {m_ci[1]:+.3f}$] & "
            f"$t={m_t:.2f}$ ($p {fmt_p(m_tp)}$) & $p {fmt_p(m_holm)}$ & $W={m_w:.0f}$ ($p {fmt_p(m_wp)}$) & ${m_d:+.2f}$ & "
            f"${r_diff:+.2f}$ [${r_ci[0]:+.2f}, {r_ci[1]:+.2f}$] & "
            f"$t={r_t:.2f}$ ($p {fmt_p(r_tp)}$) & $p {fmt_p(r_holm)}$ & $W={r_w:.0f}$ ($p {fmt_p(r_wp)}$) & ${r_d:+.2f}$ \\\\"
        )
        latex.append(row_str)

    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}}")
    latex.append(r"\end{table*}")
    latex.append("")

    # ==============================================================================
    # Table 5: 6-Stage Ablation Study Results
    # ==============================================================================
    latex.append(r"% Table 5: 6-Stage Ablation Study Results")
    latex.append(r"\begin{table*}[!t]")
    latex.append(r"\centering")
    latex.append(r"\scriptsize")
    latex.append(r"\caption{Ablation Study: Incremental Contribution of Architectural Components Across 30 Seeds (Mean $\pm$ Std. Dev.)}")
    latex.append(r"\label{tab:ablation_results}")
    latex.append(r"\resizebox{\textwidth}{!}{")
    latex.append(r"\begin{tabular}{lccccccc}")
    latex.append(r"\toprule")
    latex.append(r"\textbf{Ablation Stage / Configuration} & \textbf{Risk Red. (\%)} & \textbf{Avail. (\%)} & \textbf{MTTR (steps)} & \textbf{Total Acts/Ep} & \textbf{Wrong Acts/Ep} & \textbf{FMR (\%)} & \textbf{Resilience (\%)} \\")
    latex.append(r"\midrule")

    ablation_configs = [
        ("Baseline PPO", "Stage 1: Baseline PPO"),
        ("PPO + SecReward", "Stage 2: + Multi-Objective Resilience Reward"),
        ("PPO + SecReward + Attention", "Stage 3: + Multi-Head Self-Attention"),
        ("PPO + SecReward + Attention + AuxRisk", "Stage 4: + Auxiliary Risk Prediction Head"),
        ("PPO + SecReward + Attention + AuxRisk + Gating", "Stage 5: + Threat-Aware Feature Gating"),
        ("Full SecChaos-RL", "Stage 6: Full SecChaos-RL (+ Adaptive Temp Exploration)")
    ]

    for key, label in ablation_configs:
        sub = df_a[df_a["algorithm"] == key]
        rr_m, rr_s = sub['risk_reduction'].mean(), sub['risk_reduction'].std()
        av_m, av_s = sub['availability'].mean(), sub['availability'].std()
        mt_m, mt_s = sub['mttr'].mean(), sub['mttr'].std()
        act_m, act_s = sub['total_actions'].mean(), sub['total_actions'].std()
        wr_m, wr_s = sub['wrong_actions'].mean(), sub['wrong_actions'].std()
        fmr_m, fmr_s = sub['false_mitigation_rate'].mean(), sub['false_mitigation_rate'].std()
        res_m, res_s = sub['resilience_score'].mean(), sub['resilience_score'].std()

        wr_fmt = f"{wr_m:.2f} \\pm {wr_s:.2f}" if wr_m < 0.10 else f"{wr_m:.1f} \\pm {wr_s:.1f}"

        if key == "Full SecChaos-RL":
            row_str = (
                f"\\textbf{{{label}}} & $\\mathbf{{{rr_m:.1f} \\pm {rr_s:.1f}}}$ & "
                f"$\\mathbf{{{av_m:.1f} \\pm {av_s:.1f}}}$ & "
                f"$\\mathbf{{{mt_m:.2f} \\pm {mt_s:.2f}}}$ & "
                f"$\\mathbf{{{act_m:.1f} \\pm {act_s:.1f}}}$ & "
                f"$\\mathbf{{{wr_fmt}}}$ & "
                f"$\\mathbf{{{fmr_m:.1f} \\pm {fmr_s:.1f}}}$ & "
                f"$\\mathbf{{{res_m:.1f} \\pm {res_s:.1f}}}$ \\\\"
            )
        else:
            row_str = (
                f"{label} & ${rr_m:.1f} \\pm {rr_s:.1f}$ & "
                f"${av_m:.1f} \\pm {av_s:.1f}$ & "
                f"${mt_m:.2f} \\pm {mt_s:.2f}$ & "
                f"${act_m:.1f} \\pm {act_s:.1f}$ & "
                f"${wr_fmt}$ & "
                f"${fmr_m:.1f} \\pm {fmr_s:.1f}$ & "
                f"${res_m:.1f} \\pm {res_s:.1f}$ \\\\"
            )
        latex.append(row_str)

    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}}")
    latex.append(r"\end{table*}")

    with open("tables_latex.tex", "w") as f:
        f.write("\n".join(latex) + "\n")

    print("tables_latex.tex generated successfully with Panel A/B and 6-stage ablation!")

if __name__ == "__main__":
    generate_tables()
