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
from statsmodels.stats.anova import AnovaRM
import statsmodels.stats.multicomp as mc

from secchaos_framework import (
    Config, DependencyGraph, FaultInstance, SecChaosEnv, ACTION_SPECS,
    NoMitigationAgent, RuleBasedAgent, ThresholdAgent, QueueAwareCooldownAgent,
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
    elif agent_name == "Queue-Aware Cooldown":
        agent = QueueAwareCooldownAgent()
    else:
        raise ValueError(f"Unknown deterministic agent: {agent_name}")
        
    rews, risks, avails, mttrs, asrs, fmrs, lats = [], [], [], [], [], [], []
    acts_list, wrong_list = [], []

    for _ in range(cfg.TEST_EPISODES):
        if hasattr(agent, "reset"):
            agent.reset()
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
        acts_list.append(ep_acts)
        wrong_list.append(ep_wrong)

    mean_risk_val = float(np.mean(risks))
    if agent_name == "No-Mitigation":
        risk_red = 0.0  # By definition strictly 0.00% relative to unmitigated baseline
    else:
        risk_red = float((base_risk - mean_risk_val) / max(base_risk, 1e-6) * 100.0)
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
        "total_actions": float(np.mean(acts_list)),
        "wrong_actions": float(np.mean(wrong_list)),
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
        elif ablation_cfg == "PPO + SecReward + Attention + AuxRisk + Gating":
            agent = SecChaosRLAgent(use_attn=True, use_gating=True, use_aux=True, use_temp=False)
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
    
    # Training Loop with Curriculum Difficulty Progression (250 episodes)
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

    # Evaluation Loop under Phase 3 (Critical Chaos, 20 held-out episodes)
    eval_env = SecChaosEnv(seed=seed + 500, difficulty_level=3)
    rews, risks, avails, mttrs, asrs, fmrs, lats = [], [], [], [], [], [], []
    acts_list, wrong_list = [], []
    
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
        acts_list.append(ep_acts)
        wrong_list.append(ep_wrong)

    mean_risk_val = float(np.mean(risks))
    risk_red = float((base_risk - mean_risk_val) / max(base_risk, 1e-6) * 100.0)
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
        "total_actions": float(np.mean(acts_list)),
        "wrong_actions": float(np.mean(wrong_list)),
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

    # 2. Dispatch Baseline Benchmarks (8 Algorithms x 30 Seeds = 240 Tasks)
    baseline_algs = [
        "No-Mitigation", "Rule-Based", "Threshold-Based", "Queue-Aware Cooldown",
        "DQN", "A2C", "PPO", "SecChaos-RL"
    ]
    tasks = []
    
    for alg in ["No-Mitigation", "Rule-Based", "Threshold-Based", "Queue-Aware Cooldown"]:
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

    # 3. Dispatch Intermediate Ablation Study (4 Configurations x 30 Seeds = 120 Tasks)
    # Config 1 (Baseline PPO) is copied directly from PPO benchmark results
    # Config 6 (Full SecChaos-RL) is copied directly from SecChaos-RL benchmark results
    ablation_intermediate = [
        "PPO + SecReward",
        "PPO + SecReward + Attention",
        "PPO + SecReward + Attention + AuxRisk",
        "PPO + SecReward + Attention + AuxRisk + Gating"
    ]
    ablation_tasks = []
    for cfg_name in ablation_intermediate:
        for seed in cfg.SEEDS:
            ablation_tasks.append(("ablation", cfg_name, seed, base_risks[seed]))
            
    logger.info(f"Executing {len(ablation_tasks)} ablation runs across {cfg.NUM_WORKERS} workers...")
    with mp.Pool(processes=cfg.NUM_WORKERS) as pool:
        ablation_results = pool.map(mp_worker, ablation_tasks)
        
    # Construct verified 6-stage ablation dataframe
    ablation_all = []
    # Config 1: Baseline PPO
    for r in benchmark_results:
        if r["algorithm"] == "PPO":
            r_copy = dict(r)
            r_copy["algorithm"] = "Baseline PPO"
            ablation_all.append(r_copy)
    # Configs 2-5: Intermediate variants
    ablation_all.extend(ablation_results)
    # Config 6: Full SecChaos-RL
    for r in benchmark_results:
        if r["algorithm"] == "SecChaos-RL":
            r_copy = dict(r)
            r_copy["algorithm"] = "Full SecChaos-RL"
            ablation_all.append(r_copy)

    df_ablation = pd.DataFrame(ablation_all)
    df_ablation_clean = df_ablation.drop(columns=["learning_curve"])
    df_ablation_clean.to_csv(os.path.join(cfg.OUT_DIR, "raw_ablation_metrics.csv"), index=False)
    logger.info(f"Saved raw ablation metrics to {os.path.join(cfg.OUT_DIR, 'raw_ablation_metrics.csv')}")

    # 4. Compute Summary Statistics
    metrics = [
        "cumulative_reward", "risk_reduction", "availability", "mttr",
        "attack_success_rate", "total_actions", "wrong_actions",
        "false_mitigation_rate", "decision_latency_ms", "resilience_score"
    ]
    
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

    ablation_configs = [
        "Baseline PPO",
        "PPO + SecReward",
        "PPO + SecReward + Attention",
        "PPO + SecReward + Attention + AuxRisk",
        "PPO + SecReward + Attention + AuxRisk + Gating",
        "Full SecChaos-RL"
    ]
    ablation_summary_rows = []
    for alg in ablation_configs:
        sub = df_ablation_clean[df_ablation_clean["algorithm"] == alg]
        row = {"Configuration": alg}
        for m in ["risk_reduction", "availability", "mttr", "attack_success_rate", "total_actions", "wrong_actions", "false_mitigation_rate", "resilience_score"]:
            mean = sub[m].mean()
            std = sub[m].std()
            row[m] = f"{mean:.2f} ± {std:.2f}"
            row[f"{m}_mean"] = mean
            row[f"{m}_std"] = std
        ablation_summary_rows.append(row)
    df_ablation_summary = pd.DataFrame(ablation_summary_rows)
    df_ablation_summary.to_csv(os.path.join(cfg.OUT_DIR, "summary_ablation_table.csv"), index=False)

    # 5. Statistical Significance Tests (Repeated-Measures ANOVA, Paired Tests, Holm-Bonferroni)
    logger.info("Computing rigorous repeated-measures statistical hypothesis tests...")
    
    # 5a. Repeated-Measures ANOVA across all 8 policies over 30 seeds
    rm_results = {}
    for m in ["resilience_score", "risk_reduction", "availability", "mttr", "attack_success_rate", "false_mitigation_rate"]:
        rm = AnovaRM(df_benchmark_clean, m, "seed", within=["algorithm"]).fit()
        f_val = float(rm.anova_table["F Value"].iloc[0])
        p_val = float(rm.anova_table["Pr > F"].iloc[0])
        num_df = int(rm.anova_table["Num DF"].iloc[0])
        den_df = int(rm.anova_table["Den DF"].iloc[0])
        rm_results[m] = {"F": f_val, "p": p_val, "df1": num_df, "df2": den_df}
        logger.info(f"RM-ANOVA {m}: F({num_df}, {den_df}) = {f_val:.2f}, p = {p_val:.4e}")

    # 5b. Paired tests between SecChaos-RL and 7 comparators
    sec = df_benchmark_clean[df_benchmark_clean["algorithm"] == "SecChaos-RL"].sort_values("seed").set_index("seed")
    comparators = ["Queue-Aware Cooldown", "Threshold-Based", "Rule-Based", "PPO", "A2C", "DQN", "No-Mitigation"]
    paired_results = {}
    
    for other in comparators:
        comp = df_benchmark_clean[df_benchmark_clean["algorithm"] == other].sort_values("seed").set_index("seed")
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

    # Holm-Bonferroni correction for MTTR and Resilience comparisons
    for m in ["mttr", "resilience_score"]:
        raw_p = [paired_results[c][m]["paired_p"] for c in comparators]
        # Sort indices
        sorted_indices = np.argsort(raw_p)
        m_comparisons = len(comparators)
        adj_p = np.zeros(m_comparisons)
        running_max = 0.0
        for rank, idx in enumerate(sorted_indices):
            multiplier = m_comparisons - rank
            p_val_adj = min(1.0, raw_p[idx] * multiplier)
            running_max = max(running_max, p_val_adj)
            adj_p[idx] = min(1.0, running_max)
        for idx, c in enumerate(comparators):
            paired_results[c][m]["holm_bonferroni_p"] = float(adj_p[idx])

    stat_payload = {
        "rm_anova": rm_results,
        "paired_tests_vs_secchaos": paired_results
    }
    with open(os.path.join(cfg.OUT_DIR, "statistical_tests.json"), "w") as f:
        json.dump(stat_payload, f, indent=2)

    # 6. Generate Publication-Quality Figures (DPI=300)
    logger.info("Generating publication figures...")
    sns.set_theme(style="whitegrid", font="sans-serif")
    
    # Figure 1: Box & Strip Plots
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
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

    # Figure 3: Ablation Bar Chart (6 stages)
    fig, ax = plt.subplots(figsize=(10.5, 5))
    ablation_means = [df_ablation_clean[df_ablation_clean["algorithm"] == c]["resilience_score"].mean() for c in ablation_configs]
    ablation_errs = [df_ablation_clean[df_ablation_clean["algorithm"] == c]["resilience_score"].std() for c in ablation_configs]
    x_pos = np.arange(len(ablation_configs))
    ax.bar(x_pos, ablation_means, yerr=ablation_errs, capsize=5,
           color=["#95a5a6", "#3498db", "#1abc9c", "#f39c12", "#e67e22", "#2ecc71"], edgecolor="black")
    ax.set_xticks(x_pos)
    ax.set_xticklabels([
        "PPO\n(Baseline)", "+ Reward\nEngineering", "+ Multi-Head\nAttention",
        "+ Aux. Risk\nPrediction", "+ Threat-Aware\nFeature Gating", "Full SecChaos-RL\n(+Adaptive Temp)"
    ], fontsize=9)
    ax.set_ylabel("Resilience Score (%)", fontsize=11)
    ax.set_title("Ablation Study: Incremental Contribution of Architectural Components Across 30 Seeds", fontsize=12, fontweight="bold")
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

    duration = time.time() - t_start
    logger.info(f"SecChaos-RL benchmark suite successfully completed in {duration:.1f} seconds ({duration/60.0:.2f} minutes).")

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
