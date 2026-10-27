import json
import pandas as pd
import numpy as np
from scipy import stats

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
    latex.append(r"\caption{Paired Statistical Comparisons: SecChaos-RL versus Comparative Baselines Across 30 Matched Seeds with Explicit Directional Sign Convention ($\Delta = \text{SecChaos-RL} - \text{Comparator}$). In Panel A (MTTR), negative values ($\Delta < 0$) indicate faster recovery (lower recovery time) for SecChaos-RL; in Panel B (Resilience), positive values ($\Delta > 0$) indicate higher resilience for SecChaos-RL. Reporting both unadjusted and Holm-Bonferroni adjusted $p$-values to control the Family-Wise Error Rate ($\alpha=0.05$) across seven pairwise comparisons.}")
    latex.append(r"\label{tab:paired_statistical_results}")
    latex.append(r"\resizebox{\textwidth}{!}{")
    latex.append(r"\begin{tabular}{lcccccccccc}")
    latex.append(r"\toprule")
    latex.append(r" & \multicolumn{5}{c}{\textbf{Panel A: Recovery Speed (MTTR) Comparisons vs. SecChaos-RL ($\Delta = \text{Sec} - \text{Comp}$, $\Delta < 0$ favors Sec)}} & \multicolumn{5}{c}{\textbf{Panel B: Holistic Resilience Score Comparisons vs. SecChaos-RL ($\Delta = \text{Sec} - \text{Comp}$, $\Delta > 0$ favors Sec)}} \\")
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

    latex.append(r"\midrule")
    latex.append(r"\multicolumn{11}{l}{\textit{Note:} Pairwise difference is defined as $\Delta = \text{Metric}_{\text{SecChaos-RL}} - \text{Metric}_{\text{Comparator}}$. All paired confidence intervals and hypothesis tests are evaluated over identical seeds ($N=30$).} \\")
    latex.append(r"\bottomrule")
    latex.append(r"\end{tabular}}")
    latex.append(r"\end{table*}")
    latex.append("")

    # ==============================================================================
    # Table 5: 6-Stage Ablation Study Results (Panel A: Absolute Metrics, Panel B: Paired Differences)
    # ==============================================================================
    latex.append(r"% Table 5: 6-Stage Ablation Study Results")
    latex.append(r"\begin{table*}[!t]")
    latex.append(r"\centering")
    latex.append(r"\scriptsize")
    latex.append(r"\caption{Ablation Study: Architectural Component Analysis Across 30 Independent Random Seeds. Panel A presents absolute metrics (Mean $\pm$ Std. Dev.). Panel B reports paired differences between successive stages ($\Delta = \text{Stage}_k - \text{Stage}_{k-1}$) and overall (Stage 6 vs. Stage 1) with 95\% confidence intervals, paired $t$-tests ($t$, unadjusted $p$), and Cohen's $d$.}")
    latex.append(r"\label{tab:ablation_results}")
    latex.append(r"\resizebox{\textwidth}{!}{")
    latex.append(r"\begin{tabular}{lccccccc}")
    latex.append(r"\toprule")
    latex.append(r"\multicolumn{8}{c}{\textbf{Panel A: Multi-Metric Performance by Ablation Stage (Mean $\pm$ Std. Dev.)}} \\")
    latex.append(r"\midrule")
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

    latex.append(r"\midrule")
    latex.append(r"\multicolumn{8}{c}{\textbf{Panel B: Paired Statistical Differences Between Successive Stages ($\Delta = \text{Stage}_k - \text{Stage}_{k-1}$) and Overall vs. Baseline}} \\")
    latex.append(r"\midrule")
    latex.append(r"\textbf{Architectural Transition} & \textbf{$\Delta$ Resilience [95\% CI]} & \textbf{Paired $t$ ($p_{raw}, p_{adj}$)} & \textbf{$\Delta$ MTTR [95\% CI]} & \textbf{Paired $t$ ($p_{raw}, p_{adj}$)} & \textbf{$\Delta$ FMR (\%) [95\% CI]} & \textbf{Paired $t$ ($p_{raw}, p_{adj}$)} & \textbf{Cohen $d$ (Res)} \\")
    latex.append(r"\midrule")

    # Compute paired transitions
    adj_transitions = [
        ("Stage 2 vs. Stage 1 (+ SecReward)", "Baseline PPO", "PPO + SecReward"),
        ("Stage 3 vs. Stage 2 (+ Attention)", "PPO + SecReward", "PPO + SecReward + Attention"),
        ("Stage 4 vs. Stage 3 (+ AuxRisk)", "PPO + SecReward + Attention", "PPO + SecReward + Attention + AuxRisk"),
        ("Stage 5 vs. Stage 4 (+ Gating)", "PPO + SecReward + Attention + AuxRisk", "PPO + SecReward + Attention + AuxRisk + Gating"),
        ("Stage 6 vs. Stage 5 (+ Adaptive Temp)", "PPO + SecReward + Attention + AuxRisk + Gating", "Full SecChaos-RL")
    ]

    def get_stats(prev_k, curr_k, m):
        df_prev = df_a[df_a['algorithm'] == prev_k].sort_values('seed')
        df_curr = df_a[df_a['algorithm'] == curr_k].sort_values('seed')
        v_p = df_prev[m].values
        v_c = df_curr[m].values
        d = v_c - v_p
        m_d = np.mean(d)
        s_d = np.std(d, ddof=1)
        sem = s_d / np.sqrt(len(d))
        ci = stats.t.interval(0.95, df=len(d)-1, loc=m_d, scale=sem)
        t_s, p_v = stats.ttest_rel(v_c, v_p)
        cd = m_d / s_d if s_d > 1e-9 else 0.0
        return m_d, ci, t_s, p_v, cd

    adj_res = [get_stats(p, c, 'resilience_score') for _, p, c in adj_transitions]
    adj_mttr = [get_stats(p, c, 'mttr') for _, p, c in adj_transitions]
    adj_fmr = [get_stats(p, c, 'false_mitigation_rate') for _, p, c in adj_transitions]

    def holm_bonferroni(p_vals):
        m = len(p_vals)
        sorted_indices = np.argsort(p_vals)
        adj_p = np.zeros(m)
        for rank, idx in enumerate(sorted_indices):
            adj = p_vals[idx] * (m - rank)
            adj_p[idx] = min(1.0, adj)
        for i in range(1, m):
            idx_curr = sorted_indices[i]
            idx_prev = sorted_indices[i-1]
            if adj_p[idx_curr] < adj_p[idx_prev]:
                adj_p[idx_curr] = adj_p[idx_prev]
        return adj_p

    p_adj_res = holm_bonferroni([x[3] for x in adj_res])
    p_adj_mttr = holm_bonferroni([x[3] for x in adj_mttr])
    p_adj_fmr = holm_bonferroni([x[3] for x in adj_fmr])

    def fmt_p(p):
        return "< 0.0001" if p < 0.0001 else f"{p:.4f}"

    for i, (trans_label, _, _) in enumerate(adj_transitions):
        r_md, r_ci, r_t, r_p, r_cd = adj_res[i]
        m_md, m_ci, m_t, m_p, _ = adj_mttr[i]
        f_md, f_ci, f_t, f_p, _ = adj_fmr[i]
        r_padj = p_adj_res[i]
        m_padj = p_adj_mttr[i]
        f_padj = p_adj_fmr[i]

        row_str = (
            f"{trans_label} & "
            f"${r_md:+.2f}$ [${r_ci[0]:+.2f}, {r_ci[1]:+.2f}$] & $t={r_t:+.2f}$ (${fmt_p(r_p)}, {fmt_p(r_padj)}$) & "
            f"${m_md:+.2f}$ [${m_ci[0]:+.2f}, {m_ci[1]:+.2f}$] & $t={m_t:+.2f}$ (${fmt_p(m_p)}, {fmt_p(m_padj)}$) & "
            f"${f_md:+.2f}$ [${f_ci[0]:+.2f}, {f_ci[1]:+.2f}$] & $t={f_t:+.2f}$ (${fmt_p(f_p)}, {fmt_p(f_padj)}$) & "
            f"${r_cd:+.2f}$ \\\\"
        )
        latex.append(row_str)

    # Overall Transition: Stage 6 vs. Stage 1
    r_md, r_ci, r_t, r_p, r_cd = get_stats("Baseline PPO", "Full SecChaos-RL", 'resilience_score')
    m_md, m_ci, m_t, m_p, _ = get_stats("Baseline PPO", "Full SecChaos-RL", 'mttr')
    f_md, f_ci, f_t, f_p, _ = get_stats("Baseline PPO", "Full SecChaos-RL", 'false_mitigation_rate')

    row_str = (
        f"Stage 6 vs. Stage 1 (Full vs. Baseline) & "
        f"${r_md:+.2f}$ [${r_ci[0]:+.2f}, {r_ci[1]:+.2f}$] & $t={r_t:+.2f}$ (${fmt_p(r_p)}, \\text{{--}})$ & "
        f"${m_md:+.2f}$ [${m_ci[0]:+.2f}, {m_ci[1]:+.2f}$] & $t={m_t:+.2f}$ (${fmt_p(m_p)}, \\text{{--}})$ & "
        f"${f_md:+.2f}$ [${f_ci[0]:+.2f}, {f_ci[1]:+.2f}$] & $t={f_t:+.2f}$ (${fmt_p(f_p)}, \\text{{--}})$ & "
        f"${r_cd:+.2f}$ \\\\"
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
