import re
import os

with open('revision/revised_manuscript.tex', 'r', encoding='utf-8') as f:
    orig = f.read()

# Preamble
preamble = r"""\documentclass[ASNA,twocolumn]{USG}
\usepackage{anyfontsize}
\usepackage{colortbl}
\usepackage{xcolor}
\usepackage{steinmetz}
\usepackage{booktabs}
\usepackage{amsmath,amsfonts,amsthm}
\usepackage{multirow}
\usepackage{array}
\usepackage{algpseudocode}
\usepackage{url}
\usepackage{xurl}

\graphicspath{{./images/}{./figs/}}

\articletype{RESEARCH ARTICLE}
\journal{Software: Practice and Experience}
\received{20 January 2026}
\revised{21 January 2026}
\accepted{22 January 2026}
\volume{0}
\copyyear{2026}
\startpage{1}
\articledoi{10.1002/spe.0000}

\begin{document}

\title{SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos}

\author[1]{Thurbilli Karthik}
\author[1]{Michael Arock}
\author[2]{Vinay Raj}

\authormark{KARTHIK \textsc{et al.}}
\titlemark{SecChaos-RL: Threat-Aware Resilience Engineering Framework}

\address[1]{\orgdiv{Department of Computer Applications}, \orgname{National Institute of Technology}, \orgaddress{\state{Tiruchirappalli 620015, Tamil Nadu}, \country{India}}}
\address[2]{\orgdiv{Department of Computational \& Data Science}, \orgname{National Institute of Technology}, \orgaddress{\state{Warangal 506004, Telangana}, \country{India}}}

\corres{Thurbilli Karthik (\email{405124053@nitt.edu})}

\fundingInfo{The authors received no external funding for this study.}

\keywords{Security Chaos Engineering | Microservice Resilience | Reinforcement Learning | Self-Adaptive Systems | Fault Injection | DevSecOps}
"""

# Streamlined Abstract for Wiley 2-column layout (fits in header box on page 1)
abstract_text = r"""Distributed cloud-native microservices expand the operational attack surface and introduce complex dependency failure cascades. While Security Chaos Engineering (SCE) proactively exposes vulnerabilities via intentional fault injection, contemporary SCE remains an open-loop, manual practice. Automating runtime remediation introduces a severe dilemma: aggressive security interventions frequently induce cascading transaction timeouts and availability collapse. This paper presents \textbf{SecChaos-RL}, an autonomous closed-loop resilience framework unifying SCE with deep reinforcement learning. Formulated as a multi-objective Markov Decision Process, SecChaos-RL balances security risk suppression, availability preservation, Mean Time to Recovery (MTTR), and operational churn. The framework incorporates Multi-Head Self-Attention over dependency telemetry, Threat-Aware Feature Gating, an Auxiliary Risk Prediction Head, and Threat-Adaptive Temperature Exploration. Across 30 independent random seeds under multi-stage security chaos, empirical results demonstrate critical operational trade-offs: while static alert-matching rules achieve high local risk reduction ($55.5\% \pm 4.8\%$), they trigger severe mitigation storms ($30.8\% \pm 4.9\%$ false mitigation rate; $15.4 \pm 2.5$ wrong actions/ep). SecChaos-RL balances multi-objective stability, achieving significantly faster recovery under cascading failure than conservative DevOps heuristics ($\text{MTTR} = 1.79 \pm 0.53$ steps vs. $2.29 \pm 0.30$ for Threshold-Based, paired $p_{holm} = 0.0013$; and $2.24 \pm 0.23$ for Queue-Aware Cooldown, paired $p_{holm} = 0.0013$), halving unnecessary dispatches compared to greedy rules ($7.5 \pm 1.9$ vs. $15.4 \pm 2.5$ wrong actions/ep; $\text{FMR} = 20.9\% \pm 4.4\%$), and executing decisions with sub-millisecond latency ($0.44 \pm 0.15$\,ms per-step; $1.04$\,ms $p_{99}$ on CPU). A six-stage ablation study substantiates each architectural component and delineates practical deployment boundaries between deterministic heuristics and reinforcement learning control."""

abstract_block = f"\\abstract[ABSTRACT]{{{abstract_text}}}\n\n\\maketitle\n"

# Extract body from \section{Introduction} to \section*{Declarations}
body_start = orig.find(r'\section{Introduction}')
body_end = orig.find(r'\section*{Declarations}')
body_text = orig[body_start:body_end].strip()

# Adjust figure heights/widths for two-column Wiley layout
# fig 1: workflow.jpg
body_text = body_text.replace(
    r'\includegraphics[height=0.38\textheight, keepaspectratio]{figs/workflow.jpg}',
    r'\includegraphics[width=\columnwidth, keepaspectratio]{figs/workflow.jpg}'
)
# fig 2: network_architecture.jpg
body_text = body_text.replace(
    r'\includegraphics[width=0.78\columnwidth]{figs/network_architecture.jpg}',
    r'\includegraphics[width=\columnwidth, keepaspectratio]{figs/network_architecture.jpg}'
)

# Table 1: fault taxonomy - make it table* and tabular*
body_text = body_text.replace(
    r"""\begin{table}[!t]
\centering
\small
\caption{SecChaos-RL Security Fault Taxonomy}
\label{tab:fault_categories}
\begin{tabular}{cllp{4.2cm}}
\toprule
\textbf{ID} & \textbf{Fault Type} & \textbf{Target Service} & \textbf{Operational Impact} \\
\midrule
$F_1$ & Expired TLS Certificate & Gateway & Insecure channel; enables Man-in-the-Middle (MITM). \\
$F_2$ & Vulnerable Dependency & User & Known CVE in library; remote code execution risk. \\
$F_3$ & Secret / Token Leakage & User & Exposed credentials in log telemetry or environment. \\
$F_4$ & RBAC Misconfiguration & Authentication & Overly permissive role mappings; privilege escalation. \\
$F_5$ & Weak Authentication / MFA & Authentication & Brute-force susceptibility; bypassed credential checks. \\
$F_6$ & Excessive Privileges & Order & Service account running as root with unnecessary capabilities. \\
$F_7$ & Missing Security Patch & Inventory & Unpatched operating system or runtime vulnerability. \\
$F_8$ & Exposed Internal API & Gateway & Unauthenticated internal endpoint accessible externally. \\
\bottomrule
\end{tabular}
\end{table}""",
    r"""\begin{table*}[!t]
\centering
\small
\caption{SecChaos-RL Security Fault Taxonomy}
\label{tab:fault_categories}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}cllp{8.5cm}@{\extracolsep{\fill}}}
\toprule
\textbf{ID} & \textbf{Fault Type} & \textbf{Target Service} & \textbf{Operational Impact} \\
\midrule
$F_1$ & Expired TLS Certificate & Gateway & Insecure channel; enables Man-in-the-Middle (MITM). \\
$F_2$ & Vulnerable Dependency & User & Known CVE in library; remote code execution risk. \\
$F_3$ & Secret / Token Leakage & User & Exposed credentials in log telemetry or environment. \\
$F_4$ & RBAC Misconfiguration & Authentication & Overly permissive role mappings; privilege escalation. \\
$F_5$ & Weak Authentication / MFA & Authentication & Brute-force susceptibility; bypassed credential checks. \\
$F_6$ & Excessive Privileges & Order & Service account running as root with unnecessary capabilities. \\
$F_7$ & Missing Security Patch & Inventory & Unpatched operating system or runtime vulnerability. \\
$F_8$ & Exposed Internal API & Gateway & Unauthenticated internal endpoint accessible externally. \\
\bottomrule
\end{tabular*}
\end{table*}"""
)

# fig 4: pareto_tradeoff.png
body_text = body_text.replace(
    r'\includegraphics[width=0.62\columnwidth]{figs/pareto_tradeoff.png}',
    r'\includegraphics[width=\columnwidth, keepaspectratio]{figs/pareto_tradeoff.png}'
)
# fig 5: ablation_study.png - make it figure* across two columns
body_text = body_text.replace(
    r'\begin{figure}[!htbp]' + '\n' + r'\centering' + '\n' + r'\includegraphics[width=0.75\columnwidth]{figs/ablation_study.png}' + '\n' + r'\caption{Ablation Study: Incremental contribution of SecChaos-RL architectural components across 30 random seeds.}' + '\n' + r'\label{fig:ablation_study}' + '\n' + r'\end{figure}',
    r'\begin{figure*}[!t]' + '\n' + r'\centering' + '\n' + r'\includegraphics[width=0.88\textwidth]{figs/ablation_study.png}' + '\n' + r'\caption{Ablation Study: Incremental contribution of SecChaos-RL architectural components across 30 random seeds.}' + '\n' + r'\label{fig:ablation_study}' + '\n' + r'\end{figure*}'
)
# fig 6: learning_curves.png
body_text = body_text.replace(
    r'\includegraphics[width=0.72\columnwidth]{figs/learning_curves.png}',
    r'\includegraphics[width=\columnwidth, keepaspectratio]{figs/learning_curves.png}'
)

# Backmatter
backmatter = r"""
\bmsubsection*{Author Contributions}
\textbf{Thurbilli Karthik:} Conceptualization, methodology, software, investigation, formal analysis, writing -- original draft. \textbf{Michael Arock:} Supervision, methodology, validation, writing -- review \& editing. \textbf{Vinay Raj:} Validation, formal analysis, writing -- review \& editing.

\bmsubsection*{Financial Disclosure}
The authors received no external funding for this study.

\bmsubsection*{Conflict of Interest}
The authors declare that they have no competing financial or non-financial interests.

\bmsubsection*{Data and Code Availability Statement}
The full replication package supporting the findings of this study, including the SecChaos-RL simulation environment, baseline agent implementations, trained neural checkpoints, raw per-step and per-seed CSV telemetry across all 30 seeds, and automated analysis scripts, is provided as Supplementary Material and is available for replication.

\bibliography{references}

\end{document}
"""

full_tex = preamble + "\n" + abstract_block + "\n" + body_text + "\n" + backmatter

with open('revision/wiley_design/secchaos_wiley.tex', 'w', encoding='utf-8') as f:
    f.write(full_tex)

print("secchaos_wiley.tex updated.")
