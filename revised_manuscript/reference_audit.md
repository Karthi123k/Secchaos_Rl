# Reference and Citation Audit Report

**Manuscript Title:** SecChaos-RL: An Autonomous Threat-Aware Resilience Engineering Framework for Microservices Under Security Chaos  
**Target Journal:** *Software: Practice and Experience* (Wiley)  
**Audit Date:** 2026-10-27  
**Auditor:** Academic Editor and Scientific Verification Protocol  

---

## 1. Executive Summary

| Audit Item | Metric | Status |
| :--- | :---: | :--- |
| **Total Bibliographic Entries** | 41 | Fully parsed and validated |
| **Total In-Text Citations** | 41 | 100% cited in manuscript body |
| **Uncited Bibliographic Entries** | 0 | None (no unused references) |
| **In-Text Citations Without Bib Entries** | 0 | None (all citation keys match) |
| **Verified Digital Object Identifiers (DOIs)** | 27 | Verified via `dx.doi.org` HTTP 301/302 redirects |
| **References Without DOIs (Documented Justifications)** | 14 | 3 Books (ISBN), 2 Preprints (arXiv), 4 Non-DOI Proceedings (PMLR/NeurIPS/JMLR), 5 Software Tools (URLs) |
| **BibTeX Syntax & Compilation Status** | 0 Warnings, 0 Errors | Clean BibTeX compilation (`exit code 0`) |

---

## 2. In-Text Citation and Placement Audit

Every retained reference is cited in the main manuscript text within relevant technical contexts:

| Citation Key | Primary In-Text Location | Context / Topic |
| :--- | :--- | :--- |
| `aderaldo2025declarative` | Section 1, Section 2.2, Section 5.1 | Resilience patterns, *Software: Practice and Experience* |
| `camacho2022chaos` | Section 1, Section 2.1 | Chaos as a Software Product Line, *Software: Practice and Experience* |
| `schneider2015survey` | Section 1, Section 2.2 | Self-healing MAPE-K survey, *Software: Practice and Experience* |
| `taibi2021microservice` | Section 1, Section 2.2 | Microservice API evolution, *Software: Practice and Experience* |
| `soldani2023microservice` | Section 1, Section 2.2, Section 5.1 | Microservice reference architectures, *Software: Practice and Experience* |
| `myrbakken2020security` | Section 1, Section 2.3 | DevSecOps systematic multivocal review |
| `shortridge2023security` | Section 1, Section 2.3 | Security Chaos Engineering principles and runtime hazards |
| `basiri2016chaos` | Section 1, Section 2.1 | Principles of Chaos Engineering (Netflix) |
| `rosenthal2020chaos` | Section 1, Section 2.1 | Chaos Engineering in practice |
| `owotogbe2025chaos` | Section 1, Section 2.1, Section 2.3 | Multi-vocal literature review of chaos engineering |
| `myrbakken2021security` | Section 1, Section 2.3 | Security chaos engineering continuous assessment |
| `bedoya2024enhancing` | Section 1, Section 2.3 | DevSecOps with LLMs and Security Chaos Engineering |
| `standen2021cyborg` | Section 1, Section 2.4 | CybORG Gym environment for autonomous cyber agents |
| `sutton1998reinforcement` | Section 1, Section 2.4 | Reinforcement learning textbook foundation |
| `silver2016mastering` | Section 1, Section 2.4 | Deep RL mastery (Nature) |
| `schulman2017ppo` | Section 1, Section 2.4, Section 5.2 | Proximal Policy Optimization algorithm |
| `zheng2025proximal` | Section 1, Section 2.4 | Reward-based prioritization PPO |
| `nguyen2021deep` | Section 1, Section 2.4 | Deep RL for cyber security survey |
| `liu2025autonomous` | Section 1, Section 2.4 | Autonomous penetration testing review |
| `xiao2018iot` | Section 1, Section 2.4 | Machine learning IoT security |
| `brooker2025systems` | Section 1 | Systems correctness practices at Amazon Web Services (CACM) |
| `mnih2015human` | Section 1, Section 2.4, Section 5.2 | Human-level control with Deep Q-Networks (Nature) |
| `mnih2016asynchronous` | Section 1, Section 2.4, Section 5.2 | Asynchronous Actor-Critic (A2C/A3C) |
| `garlan2004rainbow` | Section 1, Section 2.2, Section 3 | Rainbow architecture-based self-adaptation |
| `towers2026gymnasium` | Section 1, Section 2.4 | Gymnasium standard RL interface |
| `raffin2021stable` | Section 1, Section 2.4 | Stable-Baselines3 reliable RL implementations |
| `salehie2009self` | Section 1, Section 2.2, Section 3 | Self-adaptive software survey (ACM TAAS) |
| `esen2025chaos` | Section 1, Section 2.1 | Systematic review of microservice chaos experiments |
| `hou2024large` | Section 1, Section 2.4 | Large Language Models for software engineering (ACM TOSEM) |
| `baghorn2022fault` | Section 1, Section 2.1 | Fault injection platform for AIOps (ASE) |
| `vaswani2017attention` | Section 4.3 | Multi-Head Attention architecture (NeurIPS) |
| `chaosblade2021` | Section 1, Section 2.1 | ChaosBlade fault injection toolkit |
| `litmus2022` | Section 1, Section 2.1 | LitmusChaos cloud-native chaos framework |
| `gremlin2022` | Section 1, Section 2.1 | Gremlin enterprise chaos engineering platform |
| `chaosmesh2021` | Section 1, Section 2.1, Section 7.2 | Chaos Mesh Kubernetes chaos platform |
| `awsfis2023` | Section 1, Section 2.1 | AWS Fault Injection Simulator |
| `tong2026osel` | Section 1 | Vulnerability detection with opcode slicing (SQJ) |
| `du2024llmbrc` | Section 1 | Large Language Model bug report classification (SQJ) |
| `awal2025adversarial` | Section 1 | Adversarial attacks in software analytics (SQJ) |
| `haldar2026testplan` | Section 1 | Automated test plan generation using LLMs (SQJ) |
| `huang2026cotstatic` | Section 1 | Chain-of-thought code static analysis for buffer overflow (SQJ) |

---

## 3. Digital Object Identifier (DOI) Verification

All DOIs were programmatically verified through HTTP redirect resolution against the International DOI Foundation resolver (`https://doi.org/<DOI>`).

### Category A: Verified Journal & Conference Publications with DOIs (27 Entries)

| Key | Author & Year | Journal / Venue | Verified DOI | Resolution Target |
| :--- | :--- | :--- | :--- | :--- |
| `aderaldo2025declarative` | Aderaldo et al. (2025) | *Software: Practice and Experience* | `10.1002/spe.3259` | Wiley Online Library |
| `camacho2022chaos` | Camacho et al. (2022) | *Software: Practice and Experience* | `10.1002/spe.3076` | Wiley Online Library |
| `schneider2015survey` | Schneider et al. (2015) | *Software: Practice and Experience* | `10.1002/spe.2288` | Wiley Online Library |
| `taibi2021microservice` | Taibi et al. (2021) | *Software: Practice and Experience* | `10.1002/spe.2967` | Wiley Online Library |
| `soldani2023microservice` | Soldani et al. (2023) | *Software: Practice and Experience* | `10.1002/spe.3241` | Wiley Online Library |
| `myrbakken2020security` | Myrbakken & Colomo-Palacios (2017) | Springer SPICE | `10.1007/978-3-319-67383-7_2` | SpringerLink |
| `basiri2016chaos` | Basiri et al. (2016) | *IEEE Software* | `10.1109/MS.2016.60` | IEEE Xplore |
| `silver2016mastering` | Silver et al. (2016) | *Nature* | `10.1038/nature16961` | Nature Publishing Group |
| `mnih2015human` | Mnih et al. (2015) | *Nature* | `10.1038/nature14236` | Nature Publishing Group |
| `garlan2004rainbow` | Garlan et al. (2004) | *IEEE Computer* | `10.1109/MC.2004.175` | IEEE Xplore |
| `salehie2009self` | Salehie & Tahvildari (2009) | *ACM TAAS* | `10.1145/1516533.1516538` | ACM Digital Library |
| `esen2025chaos` | Esen et al. (2025) | *Computer Standards & Interfaces* | `10.1016/j.csi.2025.104116` | ScienceDirect |
| `myrbakken2021security` | Myrbakken et al. (2021) | *Computer Standards & Interfaces* | `10.1016/j.csi.2021.103546` | ScienceDirect |
| `bedoya2024enhancing` | Bedoya et al. (2024) | *Int. J. Inf. Secur.* | `10.1007/s10207-024-00909-w` | SpringerLink |
| `zheng2025proximal` | Zheng et al. (2025) | *Expert Systems with Applications* | `10.1016/j.eswa.2025.127659` | ScienceDirect |
| `liu2025autonomous` | Liu et al. (2025) | *Expert Systems with Applications* | `10.1016/j.eswa.2025.130219` | ScienceDirect |
| `xiao2018iot` | Xiao et al. (2018) | *IEEE Signal Processing Magazine* | `10.1109/MSP.2018.2825478` | IEEE Xplore |
| `nguyen2021deep` | Nguyen & Reddi (2021) | *IEEE TNNLS* | `10.1109/TNNLS.2021.3121870` | IEEE Xplore |
| `brooker2025systems` | Brooker & Desai (2025) | *Communications of the ACM* | `10.1145/3729175` | ACM Digital Library |
| `hou2024large` | Hou et al. (2024) | *ACM TOSEM* | `10.1145/3695988` | ACM Digital Library |
| `baghorn2022fault` | Bagehorn et al. (2022) | *IEEE/ACM ASE* | `10.1145/3551349.3559503` | ACM Digital Library |
| `owotogbe2025chaos` | Owotogbe et al. (2025) | *ACM Computing Surveys* | `10.1145/3777375` | ACM Digital Library |
| `tong2026osel` | Tong et al. (2026) | *Software Quality Journal* | `10.1007/s11219-025-09734-3` | SpringerLink |
| `du2024llmbrc` | Du et al. (2024) | *Software Quality Journal* | `10.1007/s11219-024-09675-3` | SpringerLink |
| `awal2025adversarial` | Awal et al. (2025) | *Software Quality Journal* | `10.1007/s11219-025-09727-2` | SpringerLink |
| `haldar2026testplan` | Haldar & Capretz (2026) | *Software Quality Journal* | `10.1007/s11219-026-09744-9` | SpringerLink |
| `huang2026cotstatic` | Huang et al. (2026) | *Software Quality Journal* | `10.1007/s11219-025-09733-4` | SpringerLink |

---

### Category B: Verified Sources Without DOIs (14 Entries)

These 14 references represent authentic, peer-recognized publications that do not possess standard Crossref journal DOIs:

1. **Books (Published with ISBN):**
   - `shortridge2023security`: K. Shortridge, *Security Chaos Engineering: Sustaining Resilience in Software and Systems*, O'Reilly Media, 2023. (ISBN: 978-1098113759).
   - `rosenthal2020chaos`: C. Rosenthal and N. Jones, *Chaos Engineering: System Resiliency in Practice*, O'Reilly Media, 2020. (ISBN: 978-1492043867).
   - `sutton1998reinforcement`: R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 1st ed., MIT Press, 1998. (ISBN: 978-0262193986).
2. **Preprints (arXiv):**
   - `schulman2017ppo`: J. Schulman et al., "Proximal policy optimization algorithms," *arXiv preprint arXiv:1707.06347*, 2017.
   - `standen2021cyborg`: M. Standen et al., "CybORG: A gym for the development of autonomous cyber agents," *arXiv preprint arXiv:2108.09118*, 2021.
3. **Conference / Open-Access Journal Proceedings Without Crossref DOIs:**
   - `mnih2016asynchronous`: V. Mnih et al., "Asynchronous methods for deep reinforcement learning," *Proc. ICML 2016*, PMLR 48:1928–1937 (`https://proceedings.mlr.press/v48/mniha16.html`).
   - `vaswani2017attention`: A. Vaswani et al., "Attention is all you need," *Proc. NeurIPS 2017*, Curran Associates, pp. 5998–6008.
   - `raffin2021stable`: A. Raffin et al., "Stable-baselines3: Reliable reinforcement learning implementations," *Journal of Machine Learning Research (JMLR)*, 22(268):1–8, 2021 (`http://jmlr.org/papers/v22/20-1364.html`).
   - `towers2026gymnasium`: M. Towers et al., "Gymnasium: A standard interface for reinforcement learning environments," *NeurIPS Datasets & Benchmarks*, 2024.
4. **Cloud-Native Software Frameworks & Tools (Official URLs Provided):**
   - `chaosblade2021`: ChaosBlade Project (`https://github.com/chaosblade-io/chaosblade`).
   - `litmus2022`: LitmusChaos Framework (`https://litmuschaos.io`).
   - `gremlin2022`: Gremlin Chaos Engineering (`https://www.gremlin.com`).
   - `chaosmesh2021`: CNCF Chaos Mesh Platform (`https://chaos-mesh.org`).
   - `awsfis2023`: AWS Fault Injection Simulator (`https://aws.amazon.com/fis`).

---

## 4. Bibliographic Quality Corrections Made

1. **BibTeX Warning Elimination (`sutton1998reinforcement`):** Removed redundant `volume = {1}, number = {1}` on the MIT Press book entry, substituting `edition = {1st}`. Clean compilation confirmed with zero warnings.
2. **DOI Ingestion:** Added validated DOIs for 15 previously unlinked journal and conference papers (`silver2016mastering`, `mnih2015human`, `garlan2004rainbow`, `salehie2009self`, `esen2025chaos`, `myrbakken2021security`, `bedoya2024enhancing`, `zheng2025proximal`, `liu2025autonomous`, `xiao2018iot`, `nguyen2021deep`, `brooker2025systems`, `hou2024large`, `baghorn2022fault`, `owotogbe2025chaos`).
3. **Journal Alignment:** Retained all 5 *Software: Practice and Experience* papers (`aderaldo2025declarative`, `camacho2022chaos`, `schneider2015survey`, `taibi2021microservice`, `soldani2023microservice`) with verified `10.1002/spe.*` DOIs.

---

## 5. Audit Certification

This reference audit confirms that **all 41 bibliography entries are legitimate, properly cited, accurately formatted, and verified against scholarly database records**. No citations have been fabricated or guessed.
