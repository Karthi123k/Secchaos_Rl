import os
import time
import json
import numpy as np
import pandas as pd
import multiprocessing as mp
from scipy import stats
from statsmodels.stats.anova import AnovaRM

from secchaos_framework import (
    SecChaosEnv, NoMitigationAgent, RuleBasedAgent, ThresholdAgent,
    DQNAgent, A2CAgent, PPOAgent, SecChaosRLAgent, Config
)

cfg = Config()

class QueueAwareCooldownAgent:
    def __init__(self, cooldown_steps: int = 2):
        self.cooldown_steps = cooldown_steps
        self.cooldowns = {a: 0 for a in range(1, 9)}

    def reset(self):
        self.cooldowns = {a: 0 for a in range(1, 9)}

    def select_action(self, state: np.ndarray, env: SecChaosEnv) -> int:
        for a in self.cooldowns:
            if self.cooldowns[a] > 0:
                self.cooldowns[a] -= 1
        pending_actions = [act for _, act in env.action_queue]
        domain_to_action = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}
        for domain, act in domain_to_action.items():
            if state[domain] > 0.35:
                if act in pending_actions or self.cooldowns[act] > 0:
                    continue
                self.cooldowns[act] = self.cooldown_steps
                return act
        return 0

def evaluate_seed_policy(args):
    alg_name, seed = args
    if alg_name == "No-Mitigation":
        agent = NoMitigationAgent()
    elif alg_name == "Rule-Based":
        agent = RuleBasedAgent()
    elif alg_name == "Threshold-Based":
        agent = ThresholdAgent()
    elif alg_name == "Queue-Aware Cooldown":
        agent = QueueAwareCooldownAgent()
    elif alg_name == "DQN":
        agent = DQNAgent()
    elif alg_name == "A2C":
        agent = A2CAgent()
    elif alg_name == "PPO":
        agent = PPOAgent()
    elif alg_name == "SecChaos-RL":
        agent = SecChaosRLAgent()
    else:
        raise ValueError(f"Unknown agent: {alg_name}")

    # Baseline risk for seed: strictly identical unmitigated run
    base_env = SecChaosEnv(seed=seed + 500, difficulty_level=3)
    base_risks = []
    for _ in range(cfg.TEST_EPISODES):
        s = base_env.reset()
        done = False
        while not done:
            sn, r, term, trunc, info = base_env.step(0)
            done = term or trunc
            base_risks.append(np.mean(sn[0:5]))
    base_risk = float(np.mean(base_risks))

    eval_env = SecChaosEnv(seed=seed + 500, difficulty_level=3)
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
            if alg_name in ["No-Mitigation", "Rule-Based", "Threshold-Based", "Queue-Aware Cooldown"]:
                a = agent.select_action(s, eval_env)
            else:
                a = agent.select_action(s, evaluate=True)[0] if alg_name in ["PPO", "SecChaos-RL"] else agent.select_action(s, evaluate=True)
            lat = (time.perf_counter() - t0) * 1000.0
            lats.append(lat)
            sn, r, term, trunc, info = eval_env.step(a)
            done = term or trunc
            ep_r += r
            ep_risks.append(np.mean(sn[0:5]))
            ep_avails.append(sn[11])
            if info["attack_occurred"]:
                ep_attacks += 1
            if a != 0:
                ep_acts += 1
                if info["wrong_action"]:
                    ep_wrong += 1
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
    if alg_name == "No-Mitigation":
        risk_red = 0.0  # By definition exactly 0.0 relative to unmitigated baseline
    else:
        risk_red = ((base_risk - mean_risk_val) / max(base_risk, 1e-6)) * 100.0
    mean_avail = float(np.mean(avails))
    mean_mttr = float(np.mean(mttrs))
    resil = 0.4 * risk_red + 0.4 * mean_avail + 0.2 * (100.0 / (1.0 + mean_mttr))

    return {
        "algorithm": alg_name,
        "seed": seed,
        "cumulative_reward": float(np.mean(rews)),
        "risk_reduction": float(risk_red),
        "availability": mean_avail,
        "mttr": mean_mttr,
        "attack_success_rate": float(np.mean(asrs)),
        "total_actions": float(np.mean(acts_list)),
        "wrong_actions": float(np.mean(wrong_list)),
        "false_mitigation_rate": float(np.mean(fmrs)),
        "decision_latency_ms": float(np.mean(lats)),
        "resilience_score": resil
    }

if __name__ == "__main__":
    algs = [
        "No-Mitigation", "Rule-Based", "Threshold-Based", "Queue-Aware Cooldown",
        "DQN", "A2C", "PPO", "SecChaos-RL"
    ]
    tasks = [(alg, s) for alg in algs for s in range(2026, 2056)]
    print(f"Executing {len(tasks)} tasks across 16 worker processes...")
    with mp.Pool(16) as pool:
        all_results = pool.map(evaluate_seed_policy, tasks)

    df_unified = pd.DataFrame(all_results)
    df_unified.to_csv("raw_benchmark_metrics.csv", index=False)
    print("raw_benchmark_metrics.csv written successfully!")

    # Summary table
    summary_rows = []
    for alg in algs:
        sub = df_unified[df_unified["algorithm"] == alg]
        rr_mean = sub["risk_reduction"].mean()
        rr_std = sub["risk_reduction"].std()
        av_mean = sub["availability"].mean()
        av_std = sub["availability"].std()
        mt_mean = sub["mttr"].mean()
        mt_std = sub["mttr"].std()
        asr_mean = sub["attack_success_rate"].mean()
        asr_std = sub["attack_success_rate"].std()
        act_mean = sub["total_actions"].mean()
        act_std = sub["total_actions"].std()
        wr_mean = sub["wrong_actions"].mean()
        wr_std = sub["wrong_actions"].std()
        fmr_mean = sub["false_mitigation_rate"].mean()
        fmr_std = sub["false_mitigation_rate"].std()
        lat_mean = sub["decision_latency_ms"].mean()
        lat_std = sub["decision_latency_ms"].std()
        res_mean = sub["resilience_score"].mean()
        res_std = sub["resilience_score"].std()

        row = {
            "Algorithm": alg,
            "Risk Red. (%)": f"{rr_mean:.1f} ± {rr_std:.1f}",
            "Avail. (%)": f"{av_mean:.1f} ± {av_std:.1f}",
            "MTTR (steps)": f"{mt_mean:.2f} ± {mt_std:.2f}",
            "ASR (%)": f"{asr_mean:.1f} ± {asr_std:.1f}",
            "Total Acts/Ep": f"{act_mean:.1f} ± {act_std:.1f}",
            "Wrong Acts/Ep": f"{wr_mean:.1f} ± {wr_std:.1f}",
            "FMR (%)": f"{fmr_mean:.1f} ± {fmr_std:.1f}",
            "Resilience (%)": f"{res_mean:.1f} ± {res_std:.1f}"
        }
        summary_rows.append(row)
        print(f"{alg:<22}: RiskRed={rr_mean:5.2f}±{rr_std:.2f}, Avail={av_mean:5.2f}±{av_std:.2f}, MTTR={mt_mean:4.2f}±{mt_std:.2f}, Acts={act_mean:4.1f}, Wrong={wr_mean:4.1f}, FMR={fmr_mean:5.1f}%, Resil={res_mean:5.2f}±{res_std:.2f}")

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv("summary_benchmark_table.csv", index=False)
