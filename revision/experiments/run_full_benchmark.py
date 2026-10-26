# -*- coding: utf-8 -*-
"""
SecChaos-RL: Comprehensive Empirical Benchmarking and Ablation Suite
For Wiley: Software: Practice and Experience
Executes across 30 independent seeds with multiprocessing.
Zero synthetic manipulation. Raw telemetry saved directly to disk.
"""

import os
import sys
import time
import json
import random
import logging
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.multiprocessing as mp
from scipy import stats
import statsmodels.stats.multicomp as mc

from secchaos_framework import (
    Config, DependencyGraph, FaultInstance, SecChaosEnv, ACTION_SPECS,
    NoMitigationAgent, RuleBasedAgent, ThresholdAgent,
    DQNAgent, A2CAgent, PPOAgent, SecChaosRLAgent
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("benchmark_runner")

cfg = Config()
os.makedirs(cfg.OUT_DIR, exist_ok=True)
os.makedirs(cfg.FIG_DIR, exist_ok=True)

# Precompute baseline unmitigated risk per seed for standardized risk reduction
def get_unmitigated_baseline_risk(seed: int) -> float:
    env = SecChaosEnv(seed=seed + 500, difficulty_level=3)
    agent = NoMitigationAgent()
    ep_risks = []
    for _ in range(cfg.TEST_EPISODES):
        s = env.reset()
        done = False
        while not done:
            a = agent.select_action(s, env)
            s, r, term, trunc, info = env.step(a)
            done = term or trunc
            ep_risks.append(np.mean(s[0:5]))
    return float(np.mean(ep_risks))

# ==============================================================================
# Worker Functions
# ==============================================================================
def run_deterministic_worker(agent_name: str, seed: int, base_risk: float) -> Dict[str, Any]:
    torch.set_num_threads(1)
    eval_env = SecChaosEnv(seed=seed + 500, difficulty_level=3)
    if agent_name == "No-Mitigation":
        agent = NoMitigationAgent()
    elif agent_name == "Rule-Based":
        agent = RuleBasedAgent()
    elif agent_name == "Threshold-Based":
        agent = ThresholdAgent()
    else:
        raise ValueError(f"Unknown deterministic agent: {agent_name}")
        
    rews, risks, avails, mttrs, asrs, fmrs, lats = [], [], [], [], [], [], []
    for _ in range(cfg.TEST_EPISODES):
        s = eval_env.reset()
        done = False
        ep_r, ep_risks, ep_avails, ep_attacks, ep_wrong, ep_acts = 0, [], [], 0, 0, 0
        while not done:
            t0 = time.perf_counter()
            a = agent.select_action(s, eval_env)
            lat = (time.perf_counter() - t0) * 1000.0
            lats.append(lat)
            
            sn, r, term, trunc, info = eval_env.step(a)
            done = term or trunc
            ep_r += r
            ep_risks.append(np.mean(sn[0:5]))
            ep_avails.append(sn[11])
            if info["attack_occurred"]: ep_attacks += 1
            if a != 0:
                ep_acts += 1
                if info["wrong_action"]: ep_wrong += 1
            s = sn
            
        rews.append(ep_r)
        risks.append(np.mean(ep_risks))
        avails.append(np.mean(ep_avails) * 100.0)
        mttrs.append(info["mttr"])
        asrs.append((ep_attacks / eval_env.step_count) * 100.0)
        fmrs.append((ep_wrong / max(1, ep_acts)) * 100.0)

    mean_risk_val = float(np.mean(risks))
    risk_red = max(0.0, (base_risk - mean_risk_val) / max(base_risk, 1e-6)) * 100.0
    mean_avail = float(np.mean(avails))
    mean_mttr = float(np.mean(mttrs))
    resil = 0.4 * risk_red + 0.4 * mean_avail + 0.2 * (100.0 / (1.0 + mean_mttr))
    
    return {
        "algorithm": agent_name,
        "seed": seed,
        "cumulative_reward": float(np.mean(rews)),
        "risk_reduction": risk_red,
        "availability": mean_avail,
        "mttr": mean_mttr,
        "attack_success_rate": float(np.mean(asrs)),
        "false_mitigation_rate": float(np.mean(fmrs)),
        "decision_latency_ms": float(np.mean(lats)),
        "resilience_score": resil,
        "learning_curve": [float(np.mean(rews))] * cfg.TRAIN_EPISODES
    }

def run_rl_worker(agent_type: str, seed: int, base_risk: float, ablation_cfg: Optional[str] = None) -> Dict[str, Any]:
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    
    env = SecChaosEnv(seed=seed, difficulty_level=0)
    
    # Initialize appropriate agent architecture
    if ablation_cfg is not None:
        if ablation_cfg == "Baseline PPO":
            agent = PPOAgent()
        elif ablation_cfg == "PPO + SecReward":
            agent = SecChaosRLAgent(use_attn=False, use_gating=False, use_aux=False, use_temp=False)
        elif ablation_cfg == "PPO + SecReward + Attention":
            agent = SecChaosRLAgent(use_attn=True, use_gating=False, use_aux=False, use_temp=False)
        elif ablation_cfg == "PPO + SecReward + Attention + AuxRisk":
            agent = SecChaosRLAgent(use_attn=True, use_gating=False, use_aux=True, use_temp=False)
        elif ablation_cfg == "Full SecChaos-RL":
            agent = SecChaosRLAgent(use_attn=True, use_gating=True, use_aux=True, use_temp=True)
        else:
            raise ValueError(f"Unknown ablation config: {ablation_cfg}")
        label = ablation_cfg
    else:
        if agent_type == "DQN": agent = DQNAgent()
        elif agent_type == "A2C": agent = A2CAgent()
        elif agent_type == "PPO": agent = PPOAgent()
        elif agent_type == "SecChaos-RL": agent = SecChaosRLAgent(use_attn=True, use_gating=True, use_aux=True, use_temp=True)
        else: raise ValueError(f"Unknown agent type: {agent_type}")
        label = agent_type

    learning_curve = []
    
    # Training Loop with Curriculum Difficulty Progression
    for ep in range(cfg.TRAIN_EPISODES):
        if ep < 40: env.difficulty_level = 0
        elif ep < 90: env.difficulty_level = 1
        elif ep < 150: env.difficulty_level = 2
        else: env.difficulty_level = 3
        
        s = env.reset()
        done = False
        ep_rew = 0.0
        
        while not done:
            if isinstance(agent, (PPOAgent, SecChaosRLAgent)):
                a, log_p, v = agent.select_action(s)
                sn, r, term, trunc, info = env.step(a)
                done = term or trunc
                if isinstance(agent, PPOAgent):
                    agent.store(s, a, r, log_p, v, done)
                else:
                    agent.store(s, a, r, log_p, v, done, sn)
            elif isinstance(agent, DQNAgent):
                a = agent.select_action(s)
                sn, r, term, trunc, info = env.step(a)
                done = term or trunc
                agent.store(s, a, r, sn, done)
                if len(agent.buffer) >= 64 and env.step_count % 5 == 0:
                    agent.update()
            elif isinstance(agent, A2CAgent):
                a = agent.select_action(s)
                sn, r, term, trunc, info = env.step(a)
                done = term or trunc
                agent.update(s, a, r, sn, done)
                
            s = sn
            ep_rew += r
            
        if isinstance(agent, (PPOAgent, SecChaosRLAgent)):
            agent.update()
        elif isinstance(agent, DQNAgent):
            agent.update()
            
        learning_curve.append(ep_rew)

    # Evaluation Loop under Phase 3 (Critical Chaos)
    eval_env = SecChaosEnv(seed=seed + 500, difficulty_level=3)
    rews, risks, avails, mttrs, asrs, fmrs, lats = [], [], [], [], [], [], []
    
    for _ in range(cfg.TEST_EPISODES):
        s = eval_env.reset()
        done = False
        ep_r, ep_risks, ep_avails, ep_attacks, ep_wrong, ep_acts = 0, [], [], 0, 0, 0
        while not done:
            t0 = time.perf_counter()
            if isinstance(agent, (PPOAgent, SecChaosRLAgent)):
                a, _, _ = agent.select_action(s, evaluate=True)
            else:
                a = agent.select_action(s, evaluate=True)
            lat = (time.perf_counter() - t0) * 1000.0
            lats.append(lat)
            
            sn, r, term, trunc, info = eval_env.step(a)
            done = term or trunc
            ep_r += r
            ep_risks.append(np.mean(sn[0:5]))
            ep_avails.append(sn[11])
            if info["attack_occurred"]: ep_attacks += 1
            if a != 0:
                ep_acts += 1
                if info["wrong_action"]: ep_wrong += 1
            s = sn
            
        rews.append(ep_r)
        risks.append(np.mean(ep_risks))
        avails.append(np.mean(ep_avails) * 100.0)
        mttrs.append(info["mttr"])
        asrs.append((ep_attacks / eval_env.step_count) * 100.0)
        fmrs.append((ep_wrong / max(1, ep_acts)) * 100.0)

    mean_risk_val = float(np.mean(risks))
    risk_red = max(0.0, (base_risk - mean_risk_val) / max(base_risk, 1e-6)) * 100.0
    mean_avail = float(np.mean(avails))
    mean_mttr = float(np.mean(mttrs))
    resil = 0.4 * risk_red + 0.4 * mean_avail + 0.2 * (100.0 / (1.0 + mean_mttr))
    
    return {
        "algorithm": label,
        "seed": seed,
        "cumulative_reward": float(np.mean(rews)),
        "risk_reduction": risk_red,
        "availability": mean_avail,
        "mttr": mean_mttr,
        "attack_success_rate": float(np.mean(asrs)),
        "false_mitigation_rate": float(np.mean(fmrs)),
        "decision_latency_ms": float(np.mean(lats)),
        "resilience_score": resil,
        "learning_curve": learning_curve
    }

# Multiprocessing Dispatcher
def mp_worker(args):
    task_type, alg, seed, base_risk = args
    if task_type == "deterministic":
        return run_deterministic_worker(alg, seed, base_risk)
    elif task_type == "rl":
        return run_rl_worker(alg, seed, base_risk)
    elif task_type == "ablation":
        return run_rl_worker("PPO", seed, base_risk, ablation_cfg=alg)

# ==============================================================================
# Main Orchestration Pipeline
# ==============================================================================
def main():
    logger.info("Starting SecChaos-RL Comprehensive Empirical Benchmark...")
    t_start = time.time()
    
    # 1. Precompute unmitigated baseline risk per seed
    logger.info("Precomputing unmitigated baseline degradation per seed...")
    base_risks = {seed: get_unmitigated_baseline_risk(seed) for seed in cfg.SEEDS}
    logger.info(f"Mean baseline unmitigated risk across {len(cfg.SEEDS)} seeds: {np.mean(list(base_risks.values())):.3f}")

    # 2. Dispatch Baseline Benchmarks (7 Algorithms x 30 Seeds)
    baseline_algs = ["No-Mitigation", "Rule-Based", "Threshold-Based", "DQN", "A2C", "PPO", "SecChaos-RL"]
    tasks = []
    
    for alg in ["No-Mitigation", "Rule-Based", "Threshold-Based"]:
        for seed in cfg.SEEDS:
            tasks.append(("deterministic", alg, seed, base_risks[seed]))
            
    for alg in ["DQN", "A2C", "PPO", "SecChaos-RL"]:
        for seed in cfg.SEEDS:
            tasks.append(("rl", alg, seed, base_risks[seed]))
            
    logger.info(f"Executing {len(tasks)} benchmark runs across {cfg.NUM_WORKERS} parallel workers...")
    with mp.Pool(processes=cfg.NUM_WORKERS) as pool:
        benchmark_results = pool.map(mp_worker, tasks)
        
    df_benchmark = pd.DataFrame(benchmark_results)
    df_benchmark_clean = df_benchmark.drop(columns=["learning_curve"])
    df_benchmark_clean.to_csv(os.path.join(cfg.OUT_DIR, "raw_benchmark_metrics.csv"), index=False)
    logger.info(f"Saved raw benchmark metrics to {os.path.join(cfg.OUT_DIR, 'raw_benchmark_metrics.csv')}")

    # 3. Dispatch Ablation Study (5 Configurations x 30 Seeds)
    ablation_configs = [
        "Baseline PPO",
        "PPO + SecReward",
        "PPO + SecReward + Attention",
        "PPO + SecReward + Attention + AuxRisk",
        "Full SecChaos-RL"
    ]
    ablation_tasks = []
    for cfg_name in ablation_configs:
        for seed in cfg.SEEDS:
            ablation_tasks.append(("ablation", cfg_name, seed, base_risks[seed]))
            
    logger.info(f"Executing {len(ablation_tasks)} ablation runs across {cfg.NUM_WORKERS} workers...")
    with mp.Pool(processes=cfg.NUM_WORKERS) as pool:
        ablation_results = pool.map(mp_worker, ablation_tasks)
        
    df_ablation = pd.DataFrame(ablation_results)
    df_ablation_clean = df_ablation.drop(columns=["learning_curve"])
    df_ablation_clean.to_csv(os.path.join(cfg.OUT_DIR, "raw_ablation_metrics.csv"), index=False)
    logger.info(f"Saved raw ablation metrics to {os.path.join(cfg.OUT_DIR, 'raw_ablation_metrics.csv')}")

    # 4. Compute Summary Statistics and LaTeX Tables
    metrics = ["cumulative_reward", "risk_reduction", "availability", "mttr", "attack_success_rate", "false_mitigation_rate", "decision_latency_ms", "resilience_score"]
    
    summary_rows = []
    for alg in baseline_algs:
        sub = df_benchmark_clean[df_benchmark_clean["algorithm"] == alg]
        row = {"Algorithm": alg}
        for m in metrics:
            mean = sub[m].mean()
            std = sub[m].std()
            ci = 1.96 * (std / np.sqrt(len(sub)))
            row[m] = f"{mean:.2f} ± {std:.2f}"
            row[f"{m}_mean"] = mean
            row[f"{m}_std"] = std
            row[f"{m}_ci"] = ci
        summary_rows.append(row)
    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(os.path.join(cfg.OUT_DIR, "summary_benchmark_table.csv"), index=False)

    ablation_summary_rows = []
    for alg in ablation_configs:
        sub = df_ablation_clean[df_ablation_clean["algorithm"] == alg]
        row = {"Configuration": alg}
        for m in ["risk_reduction", "availability", "mttr", "attack_success_rate", "resilience_score"]:
            mean = sub[m].mean()
            std = sub[m].std()
            row[m] = f"{mean:.2f} ± {std:.2f}"
        ablation_summary_rows.append(row)
    df_ablation_summary = pd.DataFrame(ablation_summary_rows)
    df_ablation_summary.to_csv(os.path.join(cfg.OUT_DIR, "summary_ablation_table.csv"), index=False)

    # 5. Statistical Significance Tests (ANOVA, Tukey HSD, Cohen's d)
    logger.info("Computing rigorous statistical hypothesis tests...")
    stat_results = {}
    
    for test_metric in ["resilience_score", "risk_reduction", "availability", "mttr"]:
        samples = [df_benchmark_clean[df_benchmark_clean["algorithm"] == alg][test_metric].values for alg in baseline_algs]
        f_stat, p_val = stats.f_oneway(*samples)
        stat_results[f"anova_{test_metric}"] = {"f_statistic": float(f_stat), "p_value": float(p_val)}
        
    tukey = mc.pairwise_tukeyhsd(endog=df_benchmark_clean["resilience_score"], groups=df_benchmark_clean["algorithm"], alpha=0.05)
    with open(os.path.join(cfg.OUT_DIR, "tukey_results.txt"), "w") as f:
        f.write(str(tukey))
        
    def cohens_d(x, y):
        nx, ny = len(x), len(y)
        dof = nx + ny - 2
        pool_std = np.sqrt(((nx - 1) * np.std(x, ddof=1) ** 2 + (ny - 1) * np.std(y, ddof=1) ** 2) / dof)
        return float((np.mean(x) - np.mean(y)) / (pool_std + 1e-8))

    sec_resil = df_benchmark_clean[df_benchmark_clean["algorithm"] == "SecChaos-RL"]["resilience_score"].values
    stat_results["cohens_d_vs_ppo"] = cohens_d(sec_resil, df_benchmark_clean[df_benchmark_clean["algorithm"] == "PPO"]["resilience_score"].values)
    stat_results["cohens_d_vs_rule"] = cohens_d(sec_resil, df_benchmark_clean[df_benchmark_clean["algorithm"] == "Rule-Based"]["resilience_score"].values)
    stat_results["cohens_d_vs_threshold"] = cohens_d(sec_resil, df_benchmark_clean[df_benchmark_clean["algorithm"] == "Threshold-Based"]["resilience_score"].values)
    stat_results["cohens_d_vs_dqn"] = cohens_d(sec_resil, df_benchmark_clean[df_benchmark_clean["algorithm"] == "DQN"]["resilience_score"].values)

    with open(os.path.join(cfg.OUT_DIR, "statistical_tests.json"), "w") as f:
        json.dump(stat_results, f, indent=2)

    # 6. Generate Publication-Quality Figures (DPI=300)
    logger.info("Generating publication figures...")
    sns.set_theme(style="whitegrid", font="sans-serif")
    
    # Figure 1: Box & Strip Plots
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    plot_defs = [
        ("risk_reduction", "Risk Reduction (%)", axes[0, 0]),
        ("availability", "Service Availability (%)", axes[0, 1]),
        ("mttr", "Mean Time to Recovery (steps)", axes[0, 2]),
        ("attack_success_rate", "Attack Success Rate (%)", axes[1, 0]),
        ("false_mitigation_rate", "False Mitigation Rate (%)", axes[1, 1]),
        ("resilience_score", "Holistic Resilience Score (%)", axes[1, 2])
    ]
    for col, title, ax in plot_defs:
        sns.boxplot(data=df_benchmark_clean, x="algorithm", y=col, ax=ax, palette="Set2", showmeans=True,
                    meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black"})
        sns.stripplot(data=df_benchmark_clean, x="algorithm", y=col, ax=ax, color="black", alpha=0.3, jitter=0.2, size=3)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    fig.savefig(os.path.join(cfg.FIG_DIR, "resilience_benchmarking.png"), dpi=300)
    plt.close()

    # Figure 2: Convergence Curves
    fig, ax = plt.subplots(figsize=(8, 5))
    rl_algs = ["DQN", "A2C", "PPO", "SecChaos-RL"]
    colors = {"DQN": "#e74c3c", "A2C": "#9b59b6", "PPO": "#3498db", "SecChaos-RL": "#2ecc71"}
    
    for alg in rl_algs:
        sub_curves = [r["learning_curve"] for r in benchmark_results if r["algorithm"] == alg]
        arr = np.array(sub_curves)
        mean_c = np.mean(arr, axis=0)
        std_c = np.std(arr, axis=0)
        smooth_m = pd.Series(mean_c).rolling(window=10, min_periods=1).mean()
        smooth_s = pd.Series(std_c).rolling(window=10, min_periods=1).mean()
        x = np.arange(1, cfg.TRAIN_EPISODES + 1)
        ax.plot(x, smooth_m, label=alg, color=colors[alg], lw=2)
        ax.fill_between(x, smooth_m - 0.5 * smooth_s, smooth_m + 0.5 * smooth_s, color=colors[alg], alpha=0.15)
        
    ax.set_title("Training Convergence Across 30 Seeds (Curriculum Stages 0-3)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Training Episode", fontsize=11)
    ax.set_ylabel("Episode Reward", fontsize=11)
    ax.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    fig.savefig(os.path.join(cfg.FIG_DIR, "learning_curves.png"), dpi=300)
    plt.close()

    # Figure 3: Ablation Bar Chart
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ablation_means = [df_ablation_clean[df_ablation_clean["algorithm"] == c]["resilience_score"].mean() for c in ablation_configs]
    ablation_errs = [df_ablation_clean[df_ablation_clean["algorithm"] == c]["resilience_score"].std() for c in ablation_configs]
    x_pos = np.arange(len(ablation_configs))
    ax.bar(x_pos, ablation_means, yerr=ablation_errs, capsize=5, color=["#95a5a6", "#3498db", "#1abc9c", "#f39c12", "#2ecc71"], edgecolor="black")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(["PPO\n(Baseline)", "+ Reward\nEngineering", "+ Multi-Head\nAttention", "+ Aux. Risk\nPrediction", "Full SecChaos-RL\n(+Gating & Temp)"], fontsize=9.5)
    ax.set_ylabel("Resilience Score (%)", fontsize=11)
    ax.set_title("Ablation Study: Incremental Contribution of Architectural Components", fontsize=12, fontweight="bold")
    ax.set_ylim(40, 100)
    for i, v in enumerate(ablation_means):
        ax.text(i, v + 2.5, f"{v:.1f}%", ha="center", fontweight="bold", fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(cfg.FIG_DIR, "ablation_study.png"), dpi=300)
    plt.close()

    # Figure 4: Pareto Trade-off
    fig, ax = plt.subplots(figsize=(7, 5))
    for alg in baseline_algs:
        sub = df_benchmark_clean[df_benchmark_clean["algorithm"] == alg]
        ax.scatter(sub["risk_reduction"], sub["availability"], label=alg, alpha=0.6, s=40)
        ax.scatter([sub["risk_reduction"].mean()], [sub["availability"].mean()], s=120, edgecolors="black", linewidths=1.5)
    ax.set_title("Pareto Trade-off: Security Risk Reduction vs Service Availability", fontsize=12, fontweight="bold")
    ax.set_xlabel("Security Risk Reduction (%)", fontsize=11)
    ax.set_ylabel("Service Availability (%)", fontsize=11)
    ax.legend(loc="lower left", frameon=True)
    plt.tight_layout()
    fig.savefig(os.path.join(cfg.FIG_DIR, "pareto_tradeoff.png"), dpi=300)
    plt.close()

    # 7. Format LaTeX Tables
    with open(os.path.join(cfg.OUT_DIR, "tables_latex.tex"), "w") as f:
        f.write("% Table 1: Quantitative Benchmarking Results\n")
        f.write("\\begin{table*}[!t]\n\\centering\n\\small\n")
        f.write("\\caption{Quantitative Resilience Performance Benchmarking Across 30 Independent Random Seeds}\n")
        f.write("\\label{tab:rl_resilience_results}\n")
        f.write("\\resizebox{\\textwidth}{!}{\n")
        f.write("\\begin{tabular}{lccccccc}\n\\toprule\n")
        f.write("\\textbf{Policy / Algorithm} & \\textbf{Reward} & \\textbf{Risk Red. (\\%)} & \\textbf{Avail. (\\%)} & \\textbf{MTTR (steps)} & \\textbf{ASR (\\%)} & \\textbf{FMR (\\%)} & \\textbf{Resilience (\\%)} \\\\\n\\midrule\n")
        for alg in baseline_algs:
            sub = df_benchmark_clean[df_benchmark_clean["algorithm"] == alg]
            r_str = f"${sub['cumulative_reward'].mean():.1f} \\pm {sub['cumulative_reward'].std():.1f}$"
            rr_str = f"${sub['risk_reduction'].mean():.1f} \\pm {sub['risk_reduction'].std():.1f}$"
            av_str = f"${sub['availability'].mean():.1f} \\pm {sub['availability'].std():.1f}$"
            mt_str = f"${sub['mttr'].mean():.2f} \\pm {sub['mttr'].std():.2f}$"
            asr_str = f"${sub['attack_success_rate'].mean():.1f} \\pm {sub['attack_success_rate'].std():.1f}$"
            fmr_str = f"${sub['false_mitigation_rate'].mean():.1f} \\pm {sub['false_mitigation_rate'].std():.1f}$"
            res_str = f"${sub['resilience_score'].mean():.1f} \\pm {sub['resilience_score'].std():.1f}$"
            if alg == "SecChaos-RL":
                r_b = f"$\\mathbf{{{sub['cumulative_reward'].mean():.1f} \\pm {sub['cumulative_reward'].std():.1f}}}$"
                rr_b = f"$\\mathbf{{{sub['risk_reduction'].mean():.1f} \\pm {sub['risk_reduction'].std():.1f}}}$"
                av_b = f"$\\mathbf{{{sub['availability'].mean():.1f} \\pm {sub['availability'].std():.1f}}}$"
                mt_b = f"$\\mathbf{{{sub['mttr'].mean():.2f} \\pm {sub['mttr'].std():.2f}}}$"
                asr_b = f"$\\mathbf{{{sub['attack_success_rate'].mean():.1f} \\pm {sub['attack_success_rate'].std():.1f}}}$"
                fmr_b = f"$\\mathbf{{{sub['false_mitigation_rate'].mean():.1f} \\pm {sub['false_mitigation_rate'].std():.1f}}}$"
                res_b = f"$\\mathbf{{{sub['resilience_score'].mean():.1f} \\pm {sub['resilience_score'].std():.1f}}}$"
                f.write(f"\\textbf{{{alg} (Proposed)}} & {r_b} & {rr_b} & {av_b} & {mt_b} & {asr_b} & {fmr_b} & {res_b} \\\\\n")
            else:
                f.write(f"{alg} & {r_str} & {rr_str} & {av_str} & {mt_str} & {asr_str} & {fmr_str} & {res_str} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}}\n\\end{table*}\n\n")

        f.write("% Table 2: Ablation Study Results\n")
        f.write("\\begin{table}[!t]\n\\centering\n\\small\n")
        f.write("\\caption{Ablation Study: Incremental Contribution of SecChaos-RL Architectural Components (30 Seeds)}\n")
        f.write("\\label{tab:ablation_results}\n")
        f.write("\\begin{tabular}{lcccc}\n\\toprule\n")
        f.write("\\textbf{Configuration} & \\textbf{Risk Red. (\\%)} & \\textbf{Avail. (\\%)} & \\textbf{MTTR (steps)} & \\textbf{Resilience (\\%)} \\\\\n\\midrule\n")
        for alg in ablation_configs:
            sub = df_ablation_clean[df_ablation_clean["algorithm"] == alg]
            rr_str = f"${sub['risk_reduction'].mean():.1f} \\pm {sub['risk_reduction'].std():.1f}$"
            av_str = f"${sub['availability'].mean():.1f} \\pm {sub['availability'].std():.1f}$"
            mt_str = f"${sub['mttr'].mean():.2f} \\pm {sub['mttr'].std():.2f}$"
            res_str = f"${sub['resilience_score'].mean():.1f} \\pm {sub['resilience_score'].std():.1f}$"
            if "Full" in alg:
                rr_b = f"$\\mathbf{{{sub['risk_reduction'].mean():.1f} \\pm {sub['risk_reduction'].std():.1f}}}$"
                av_b = f"$\\mathbf{{{sub['availability'].mean():.1f} \\pm {sub['availability'].std():.1f}}}$"
                mt_b = f"$\\mathbf{{{sub['mttr'].mean():.2f} \\pm {sub['mttr'].std():.2f}}}$"
                res_b = f"$\\mathbf{{{sub['resilience_score'].mean():.1f} \\pm {sub['resilience_score'].std():.1f}}}$"
                f.write(f"\\textbf{{{alg}}} & {rr_b} & {av_b} & {mt_b} & {res_b} \\\\\n")
            else:
                f.write(f"{alg} & {rr_str} & {av_str} & {mt_str} & {res_str} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    t_elapsed = time.time() - t_start
    logger.info(f"All benchmark & ablation experiments completed successfully in {t_elapsed:.1f} seconds ({t_elapsed/60.0:.2f} mins)!")

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
