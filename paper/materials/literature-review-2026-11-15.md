# Literature review for the Dataset Factory AGENT'27 paper

Nov 15, 2026 · @Eduardo

## Bottom line

The paper has a narrow, real space: an operational account of a pipeline that starts at source discovery and ends at publication, plus a controlled check of what coding agents add on the resulting tasks. Two things it can't claim are already taken.

- **Automated task construction is published.** [MLE-Smith](https://arxiv.org/abs/2510.07307) (ICLR 2026) turns raw datasets into verified ML tasks with a multi-agent pipeline, and [TAM-Bench](https://arxiv.org/abs/2509.09321) uses a browser agent to acquire benchmark tasks.
- **The consumer-study question is contested.** Three 2026 preprints compare LLM agents with classical tuning at matched budgets and report small gains or none ([Sergazinov et al.](https://arxiv.org/abs/2609.16309), [Ferreira et al.](https://arxiv.org/abs/2603.24647), [Rodrigues et al.](https://arxiv.org/abs/2606.21641)).

I found no published system that covers discovery, task construction, validation and publication end to end. That's a search result, so treat it as "to our knowledge" and name the four nearest systems.

Below: 15 essential references (7 peer-reviewed, 8 preprints), the five closest papers compared, claims advice, verification notes, and BibTeX. The [AGENT'27 call](https://conf.researchr.org/home/icse-2027/agent-2027) lists a deadline extended to 20 November 2026 and 8 pages including references for full experience papers, so the reference list has to stay near this size.

## Essential references

Fifteen references cover the five areas; "Area" uses your numbering. Status separates peer-reviewed publications from preprints.

| # | Reference | Area | Status | Why it's essential |
| --- | --- | --- | --- | --- |
| 1 | [Ma et al., AutoData: A Multi-Agent System for Open Web Data Collection](https://neurips.cc/virtual/2025/poster/115276) | 1 | Published, NeurIPS 2025 | Eight-agent system that builds a dataset from the open web given a one-sentence instruction. The nearest published "agent collects data" system. |
| 2 | [Li et al., DatasetResearch](https://arxiv.org/abs/2508.06960) | 1 | Preprint, arXiv Aug 2025 | Benchmark of 208 dataset demands. The best deep-research systems score 22% on the hard subset, which supports treating discovery as the hard step. |
| 3 | [Qiang et al., MLE-Smith](https://arxiv.org/abs/2510.07307) | 2 | Published, [ICLR 2026](https://iclr.cc/virtual/2026/poster/10007561) | Closest system. Generate, verify, execute pipeline that produced 606 tasks from 224 datasets. |
| 4 | [Jia et al., TAM-Bench](https://arxiv.org/abs/2509.09321) | 2 | Preprint, arXiv Sep 2025 | Browser agent scrapes and normalizes competitions from Kaggle, AIcrowd and Biendata into 150 tasks, with checks on reconstructed splits. |
| 5 | [Erickson et al., TabArena](https://proceedings.neurips.cc/paper_files/paper/2025/hash/1697e3fb412da11dc9488249f9e7bbc9-Abstract-Datasets_and_Benchmarks_Track.html) | 2 | Published, NeurIPS 2025 Datasets and Benchmarks | The human counterpoint. Experts screened 1,053 datasets and kept 51, which sets the bar for "validated" in tabular benchmarks. |
| 6 | [Bordt et al., Elephants Never Forget](https://arxiv.org/abs/2404.06209) | 2 | Published, COLM 2024 | LLMs have memorized popular tabular datasets verbatim and score better on seen data. Your motivation, with a test package (tabmemcheck) attached. |
| 7 | [Chan et al., MLE-bench](https://proceedings.iclr.cc/paper_files/paper/2025/hash/7e3767db483c942b883eb4f8cfb74e31-Abstract-Conference.html) | 3 | Published, ICLR 2025 | Reference benchmark for ML-engineering agents: 75 Kaggle competitions, with an analysis of pre-training contamination. |
| 8 | [Toledo et al., AI Research Agents for Machine Learning](https://proceedings.neurips.cc/paper_files/paper/2025/hash/328b81881da145412f2bc56c998dfb6a-Abstract-Conference.html) | 3 | Published, NeurIPS 2025 | Frames agents as search policies over candidate solutions and argues evaluation methodology matters alongside search. Supports the frozen holdout. |
| 9 | [Sergazinov et al., Agentic Search Spaces for Tabular Machine Learning](https://arxiv.org/abs/2609.16309) | 3 | Preprint, arXiv Sep 2026 | Closest to the consumer study. Claude Code writes modules that are tuned at matched budgets; average single-model gains are under 1%. |
| 10 | [Ferreira et al., Can LLMs Beat Classical Hyperparameter Optimization Algorithms?](https://arxiv.org/abs/2603.24647) | 3 | Preprint, arXiv Mar 2026 | Challenge. Classical HPO beats LLM agents in a fixed search space; code-editing agents narrow the gap and don't close it. |
| 11 | [Rodrigues et al., When Is an LLM Worth It for Hyperparameter Optimization?](https://arxiv.org/abs/2606.21641) | 3 | Preprint, arXiv Jun 2026 | Challenge. On eight tabular tasks the LLM advisor's lead traces to its default starting configuration; seeded random search catches up within a few evaluations. |
| 12 | [Luo, Kasirzadeh and Shah, The More You Automate, the Less You See](https://arxiv.org/abs/2509.08713) | 4 | Preprint, arXiv Sep 2025; [NeurIPS 2025 workshop spotlight](https://neurips.cc/virtual/2025/126015) | Finds benchmark cherry-picking, leakage, metric misuse and selection bias in two AI-scientist systems. Logs and code expose them far better than the final paper. |
| 13 | [Kapoor et al., AI Agents That Matter](https://arxiv.org/abs/2407.01502) | 4 | Published, TMLR 2025 | Simple baselines, cost-controlled comparison and real holdouts as the minimum for agent claims. The standard citation for your control design. |
| 14 | [Pan et al., Measuring Agents in Production](https://arxiv.org/abs/2512.04123) | 5 | Preprint, arXiv Dec 2025 | Survey of 306 practitioners and 20 case studies. Reliability is the top challenge, and 68% of deployed agents run at most ten steps before a human steps in. |
| 15 | [Lyu et al., TheBotCompany](https://arxiv.org/abs/2603.25928) | 5 | Preprint, arXiv Mar 2026 | Nearest single-system operations report: multi-day unattended runs with per-project cost, failure categories and recovery. |

Second tier, cut for space and worth citing if a reviewer asks: [Zhu et al., Agentic Benchmark Checklist](https://proceedings.neurips.cc/paper_files/paper/2025/hash/f316275b44ee2de533102913828a8107-Abstract-Datasets_and_Benchmarks_Track.html) (NeurIPS 2025), [Cemri et al., Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) (NeurIPS 2025), [Rubachev et al., TabReD](https://proceedings.iclr.cc/paper_files/paper/2025/hash/571799482291411607c54984153190b0-Abstract-Conference.html) (ICLR 2025, time-based splits), [Li et al., AutoBencher](https://proceedings.iclr.cc/paper_files/paper/2025/hash/eb216114f3eaad22506fd1bc7bbff0ca-Abstract-Conference.html) (ICLR 2025), [Szeider, ContReAct](https://researchr.org/publication/Szeider26) (AGENT '26, the same workshop's first edition), [Wu, When Errors Become Narratives](https://arxiv.org/abs/2606.14589) (preprint, eight-week incident record of one agent runtime), and [Safdar and Saadeldin](https://arxiv.org/html/2608.01995) (preprint, ten-week autonomous run with an intervention log).

## Five closest papers

Three papers overlap with the factory, one with the consumer study, and one with the review method. None combines source discovery, task construction, publication and an operations record.

| Paper | What it does | Where it overlaps with yours | What it leaves open |
| --- | --- | --- | --- |
| [MLE-Smith](https://arxiv.org/abs/2510.07307) (ICLR 2026) | Three generation agents design and refactor a task from a raw dataset. Checks combine deterministic assertions, an LLM review and an execution run. Quality is argued by rank agreement of eight LLMs with human-designed tasks. | Automated construction and layered verification of prediction tasks. Reports cost and time per task. | Inputs are Kaggle datasets the authors sampled, so discovery is out of scope. In my read it reports no overall rejection rate, no explicit leakage test, and no public release of the tasks. |
| [TAM-Bench](https://arxiv.org/abs/2509.09321) (preprint) | A browser agent collects competitions from three platforms and maps them to one schema. Filters require public data, labels and reproducible splits; rebuilt splits are checked against leaderboard scores. | Agent-driven acquisition from the web plus rule-based filtering. | The tasks were already formulated by competition hosts. Nothing new is turned into a prediction problem. |
| [AutoData](https://neurips.cc/virtual/2025/poster/115276) (NeurIPS 2025) | Research and development agent squads plan and code a collector for a dataset a user describes in one sentence. A cache design targets token cost. | Agents browse sources, write collection code and assemble a dataset. | A human names the dataset wanted. No target definition, splits, baselines or benchmark validation. |
| [Sergazinov et al.](https://arxiv.org/abs/2609.16309) (preprint) | Claude Code writes preprocessing, architecture and training modules that become choices in each model's tuning space. Tuning budgets are matched, splits are fixed, and test scores average 15 seeds. | Coding agents improving tabular predictors under a matched budget with a held-out test set. | Uses established public benchmarks, which carry exposure risk. The agent proposes a search space; it doesn't iterate on one predictor. I saw no transcript review. |
| [Luo, Kasirzadeh and Shah](https://arxiv.org/abs/2509.08713) (preprint) | Controlled probes of two AI-scientist systems for four methodological failures. Access to logs and code detects failures much better than reading the output paper. | The case for code and transcript review, and for releasing both. | Studies paper-writing systems with planted probes. It isn't a field study of agents tuning predictors on new tasks. |

Read the last column as the candidate gap list. Each entry is only a gap for your paper if your own records cover it.

## Defensible contributions and claims to avoid

Frame the paper as an experience report on one deployed system with a controlled downstream check. That framing fits the venue and survives the closest prior work. Each contribution below is conditional on evidence only you hold.

### Contributions the literature leaves room for

1. **A wider pipeline boundary.** MLE-Smith starts from datasets its authors sampled, TAM-Bench from existing competitions, and AutoData from a human request. DatasetResearch reports that agents find requested datasets poorly. A system that also chooses its sources differs in scope. Claim the scope difference and cite all four.
2. **The operations record.** MLE-Smith gives cost per task and first-pass assertion rates. I found no paper in this cluster that reports the full funnel: candidates considered, rejections with reasons, repairs, publications, and human interventions. [Pan et al.](https://arxiv.org/abs/2512.04123) note how little is public about how deployed agents are built. Your candidate, rejection and repair logs are the asset here, and they're what an AGENT reviewer can't get elsewhere.
3. **A downstream check with controls.** Baselines, a matched random-search arm and a frozen holdout follow what [Kapoor et al.](https://arxiv.org/abs/2407.01502) ask for and what [Toledo et al.](https://proceedings.neurips.cc/paper_files/paper/2025/hash/328b81881da145412f2bc56c998dfb6a-Abstract-Conference.html) flag about evaluation methodology. The design is the contribution. It's reportable whichever way the comparison comes out.
4. **Review beyond execution.** [Luo et al.](https://arxiv.org/abs/2509.08713) recommend that venues require trace logs and code. A paper that applies that standard to its own agents, and releases both, makes a methods point by example.
5. **Tasks with lower prior exposure.** [Bordt et al.](https://arxiv.org/abs/2404.06209) give the motivation. Newly packaged tasks plausibly reduce exposure. Say "plausibly" unless you run a memorization test such as tabmemcheck on a sample.

### Claims to avoid

| Claim | Why it's exposed | Safer wording |
| --- | --- | --- |
| "First" automated benchmark or task construction system | MLE-Smith makes that claim for raw datasets to ML tasks and is published. TAM-Bench and AutoData cover acquisition. | "To our knowledge, no prior report covers discovery through publication", with the four systems named. |
| "Fully autonomous" or "no human intervention" | MLE-Smith says this while humans picked its inputs, and a reviewer will check yours the same way. Pan et al. show human checkpoints are the norm. | Report intervention counts, types and timing. Let the numbers describe the autonomy. |
| "Contamination-free" | Public sources may already be in training data. Only the task packaging is new. | "Not previously published as a prediction task", plus a memorization check if you have one. |
| "Validated benchmarks" as a quality claim | TabArena kept 51 of 1,053 datasets after expert review. TabReD shows time-based splits change model rankings. | "Passes these checks", with the list, and a stated list of what isn't checked. |
| "Coding agents improve predictors" in general | Ferreira et al. and Rodrigues et al. find classical search matches or beats LLM methods at equal budget. Sergazinov et al. report gains under 1% on average. | Per-dataset effects with intervals, inside this study, on these tasks. |
| "Agents beat the baseline" without saying which | Rodrigues et al. trace an apparent LLM lead to the default configuration. Beating defaults and beating matched search are different results. | Report the two comparisons separately. State what "matched" equalizes: evaluations, wall-clock or cost. |
| Random search as a sufficient control | It's a floor. Ferreira et al. use TPE and CMA-ES, and a reviewer may ask for a default-seeded arm. | Call it a lower bound and list stronger optimizers as a limitation. |
| "Frozen holdout" as proof of generalization | A holdout only protects if agents never saw it and it was scored rarely. | State who could access it and how many times it was scored per task. |
| "Review found no leakage" | Luo et al. show review finds more than outputs do. Absence in a review still depends on reviewer, rubric and coverage. | State who reviewed, against what rubric, how many transcripts, and whether blind to the arm. |
| Lessons that generalize to deployed agents | Pan et al. draw on 306 practitioners. Yours is one system and one operator. | "In this deployment", with the limits stated up front. |

Open question: reviewers will ask whether the factory's tasks have external validity. MLE-Smith answers with rank agreement against human-designed tasks. Decide whether you have a comparable check or will list its absence as a limitation.

## Verification notes

Titles, authors, venues and dates for all 15 references were checked against an arXiv abstract page or an official proceedings page. Where both exist, the BibTeX follows the proceedings. The items below are what I could not verify or where sources disagree.

**How much I read.** My descriptions rest on abstracts plus partial full-text reads through an automated page reader. Only MLE-Smith and TheBotCompany got a targeted full-text read. Treat every characterization as a pointer to check, and check any number against the PDF before you cite it.

**Not verified**

- **Your system.** I couldn't open the Dataset Factory site, so the advice rests on your description alone. I haven't seen your draft or results.
- **The negative result.** "No end-to-end system found" reflects searches of arXiv and major proceedings in English. It's evidence of absence in my search only.
- **Preprint status.** I found no venue for TAM-Bench, DatasetResearch, Pan et al., Lyu et al., Ferreira et al., Rodrigues et al. or Sergazinov et al. Some may have been accepted since. Recheck at camera-ready.
- **Page numbers and volumes.** None captured for any proceedings entry, so the BibTeX omits them.
- **Kapoor et al.** A TMLR digest lists acceptance in June 2025 and ML Anthology gives 2025. I didn't capture the OpenReview URL.
- **Luo et al.** The NeurIPS listing is a spotlight at the workshop "AI for Science: The Reach and Limits of AI for Scientific Discovery", titled with "The Hidden Pitfalls". I didn't confirm whether that workshop is archival, so the BibTeX cites arXiv.
- **Sergazinov et al.** Exact submission day not captured. The arXiv identifier implies September 2026.
- **Lyu et al.** The PDF title starts "TheBotCompany:" and the HTML version shows only "Self-Organizing Multi-Agent Systems for Continuous Software Development". No submission date line captured; the identifier implies March 2026. Confirm the title on the abstract page.
- **Rodrigues et al.** Metadata verified; I couldn't establish the authors' affiliations or track record. Weigh it below Ferreira et al., which comes from an established AutoML group.

**Discrepancies between sources**

- **MLE-Smith counts.** The abstract says 224 datasets and 606 tasks. My full-text read also found 300 source datasets and 807 tasks in one section. Quote the abstract figures.
- **TheBotCompany hours.** My read found 137 wall-clock hours in the text against about 142 summed from its table.
- **MLE-bench author order.** The ICLR proceedings page ends with Madry, Weng; the PDF ends with Weng, Madry. BibTeX follows the proceedings page.
- **TabArena author name.** The proceedings list "Prateek Desai"; arXiv and the project repository list "Prateek Mutalik Desai".
- **Agentic Benchmark Checklist.** NeurIPS titles it "Establishing Best Practices in Building"; arXiv says "for Building". The NeurIPS author list adds Arvind Narayanan.
- **MLE-Smith title casing.** ICLR writes "Multi-agent"; arXiv writes "Multi-Agent".

**Venue facts.** Deadline, page limits and paper types come from the [AGENT'27 page](https://conf.researchr.org/home/icse-2027/agent-2027) as retrieved on 15 November 2026. It says accepted papers are published by IEEE.

## Verified BibTeX

Entries 1 to 15 match the table above; four second-tier entries follow. Fields I couldn't verify are left out, and `note` fields flag open points from the verification notes.

```bibtex
% ---- Area 1: dataset discovery, preparation, publication ----

@inproceedings{ma2025autodata,
  title     = {{AutoData}: A Multi-Agent System for Open Web Data Collection},
  author    = {Ma, Tianyi and Qian, Yiyue and Zhang, Zheyuan and Wang, Zehong and Qian, Xiaoye and Bai, Feifan and Ding, Yifan and Luo, Xuwei and Zhang, Shinan and Murugesan, Keerthiram and Zhang, Chuxu and Ye, Yanfang},
  booktitle = {Advances in Neural Information Processing Systems 38 (NeurIPS 2025)},
  year      = {2025},
  url       = {https://neurips.cc/virtual/2025/poster/115276},
  note      = {arXiv:2505.15859}
}

@misc{li2025datasetresearch,
  title         = {{DatasetResearch}: Benchmarking Agent Systems for Demand-Driven Dataset Discovery},
  author        = {Li, Keyu and Jiang, Mohan and Fu, Dayuan and Wu, Yunze and Hu, Xiangkun and Wang, Dequan and Liu, Pengfei},
  year          = {2025},
  eprint        = {2508.06960},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url           = {https://arxiv.org/abs/2508.06960},
  note          = {Preprint}
}

% ---- Area 2: automated construction and validation of benchmarks ----

@inproceedings{qiang2026mlesmith,
  title     = {{MLE-Smith}: Scaling {MLE} Tasks with Automated Multi-Agent Pipeline},
  author    = {Qiang, Rushi and Zhuang, Yuchen and Singh, Anikait and Liang, Percy and Zhang, Chao and Yang, Sherry and Dai, Bo},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2026},
  url       = {https://iclr.cc/virtual/2026/poster/10007561},
  note      = {arXiv:2510.07307}
}

@misc{jia2025tambench,
  title         = {Towards Adaptive {ML} Benchmarks: Web-Agent-Driven Construction, Domain Expansion, and Metric Optimization},
  author        = {Jia, Hangyi and Qian, Yuxi and Tong, Hanwen and Wu, Xinhui and Chen, Lin and Wei, Feng},
  year          = {2025},
  eprint        = {2509.09321},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url           = {https://arxiv.org/abs/2509.09321},
  note          = {Preprint}
}

@inproceedings{erickson2025tabarena,
  title     = {{TabArena}: A Living Benchmark for Machine Learning on Tabular Data},
  author    = {Erickson, Nick and Purucker, Lennart and Tschalzev, Andrej and Holzm{\"u}ller, David and Desai, Prateek Mutalik and Salinas, David and Hutter, Frank},
  booktitle = {Advances in Neural Information Processing Systems 38 (NeurIPS 2025), Datasets and Benchmarks Track},
  year      = {2025},
  doi       = {10.52202/085713-0519},
  url       = {https://proceedings.neurips.cc/paper_files/paper/2025/hash/1697e3fb412da11dc9488249f9e7bbc9-Abstract-Datasets_and_Benchmarks_Track.html},
  note      = {arXiv:2506.16791}
}

@inproceedings{bordt2024elephants,
  title     = {Elephants Never Forget: Memorization and Learning of Tabular Data in Large Language Models},
  author    = {Bordt, Sebastian and Nori, Harsha and Rodrigues, Vanessa and Nushi, Besmira and Caruana, Rich},
  booktitle = {Conference on Language Modeling (COLM)},
  year      = {2024},
  url       = {https://arxiv.org/abs/2404.06209},
  note      = {arXiv:2404.06209}
}

% ---- Area 3: autonomous ML experimentation and research agents ----

@inproceedings{chan2025mlebench,
  title     = {{MLE-bench}: Evaluating Machine Learning Agents on Machine Learning Engineering},
  author    = {Chan, Jun Shern and Chowdhury, Neil and Jaffe, Oliver and Aung, James and Sherburn, Dane and Mays, Evan and Starace, Giulio and Liu, Kevin and Maksin, Leon and Patwardhan, Tejal and Madry, Aleksander and Weng, Lilian},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2025},
  url       = {https://proceedings.iclr.cc/paper_files/paper/2025/hash/7e3767db483c942b883eb4f8cfb74e31-Abstract-Conference.html},
  note      = {arXiv:2410.07095}
}

@inproceedings{toledo2025airesearchagents,
  title     = {{AI} Research Agents for Machine Learning: Search, Exploration, and Generalization in {MLE-bench}},
  author    = {Toledo, Edan and Hambardzumyan, Karen and Josifoski, Martin and Hazra, Rishi and Baldwin, Nicolas and Audran-Reiss, Alexis and Kuchnik, Michael and Magka, Despoina and Jiang, Minqi and Lupidi, Alisia and Lupu, Andrei and Raileanu, Roberta and Shavrina, Tatiana and Niu, Kelvin and Gagnon-Audet, Jean-Christophe and Shvartsman, Michael and Sodhani, Shagun and Miller, Alexander and Charnalia, Abhishek and Dunfield, Derek and Wu, Carole-Jean and Stenetorp, Pontus Lars Erik Saito and Cancedda, Nicola and Foerster, Jakob and Bachrach, Yoram},
  booktitle = {Advances in Neural Information Processing Systems 38 (NeurIPS 2025)},
  year      = {2025},
  doi       = {10.52202/085713-1186},
  url       = {https://proceedings.neurips.cc/paper_files/paper/2025/hash/328b81881da145412f2bc56c998dfb6a-Abstract-Conference.html},
  note      = {arXiv:2507.02554}
}

@misc{sergazinov2026agentic,
  title         = {Agentic Search Spaces for Tabular Machine Learning},
  author        = {Sergazinov, Renat and Chistyakov, Artem and Pankevich, Sergey and Babenko, Artem},
  year          = {2026},
  eprint        = {2609.16309},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/2609.16309},
  note          = {Preprint. Submission day and primary class not verified}
}

@misc{ferreira2026llmhpo,
  title         = {Can {LLMs} Beat Classical Hyperparameter Optimization Algorithms? {A} Study on autoresearch},
  author        = {Ferreira, Fabio and Wobbe, Lucca and Krishnakumar, Arjun and Hutter, Frank and Zela, Arber},
  year          = {2026},
  eprint        = {2603.24647},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/2603.24647},
  note          = {Preprint}
}

@misc{rodrigues2026llmworth,
  title         = {When Is an {LLM} Worth It for Hyperparameter Optimization? {A} Budget-Matched Study on Tabular Data Finds the Warm-Start Is a Default Configuration, Not the Model},
  author        = {Rodrigues, Carson and Vas, Oysturn and DCosta, Isaiah Abner and Prabhakaran, Nithish Kumar},
  year          = {2026},
  eprint        = {2606.21641},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/2606.21641},
  note          = {Preprint}
}

% ---- Area 4: evaluating agent-generated artifacts beyond execution ----

@misc{luo2025moreyouautomate,
  title         = {The More You Automate, the Less You See: Hidden Pitfalls of {AI} Scientist Systems},
  author        = {Luo, Ziming and Kasirzadeh, Atoosa and Shah, Nihar B.},
  year          = {2025},
  eprint        = {2509.08713},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url           = {https://arxiv.org/abs/2509.08713},
  note          = {Preprint. Spotlight at the NeurIPS 2025 workshop AI for Science: The Reach and Limits of AI for Scientific Discovery; archival status not verified}
}

@article{kapoor2025aiagents,
  title   = {{AI} Agents That Matter},
  author  = {Kapoor, Sayash and Stroebl, Benedikt and Siegel, Zachary S. and Nadgir, Nitya and Narayanan, Arvind},
  journal = {Transactions on Machine Learning Research},
  year    = {2025},
  url     = {https://arxiv.org/abs/2407.01502},
  note    = {arXiv:2407.01502. OpenReview URL not captured}
}

% ---- Area 5: engineering experience with deployed agents ----

@misc{pan2025measuringagents,
  title         = {Measuring Agents in Production},
  author        = {Pan, Melissa Z. and Arabzadeh, Negar and Cogo, Riccardo and Zhu, Yuxuan and Xiong, Alexander and Agrawal, Lakshya A and Mao, Huanzhi and Shen, Emma and Pallerla, Sid and Patel, Liana and Liu, Shu and Shi, Tianneng and Liu, Xiaoyuan and Davis, Jared Quincy and Lacavalla, Emmanuele and Basile, Alessandro and Yang, Shuyi and Castro, Paul and Kang, Daniel and Sen, Koushik and Song, Dawn and Gonzalez, Joseph E. and Stoica, Ion and Zaharia, Matei and Ellis, Marquita},
  year          = {2025},
  eprint        = {2512.04123},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CY},
  url           = {https://arxiv.org/abs/2512.04123},
  note          = {Preprint}
}

@misc{lyu2026thebotcompany,
  title         = {Self-Organizing Multi-Agent Systems for Continuous Software Development},
  author        = {Lyu, Wenhan and Zhang, Yixuan and Xiao, Yue and Sun, Yifan},
  year          = {2026},
  eprint        = {2603.25928},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/2603.25928},
  note          = {Preprint. PDF title is prefixed ``TheBotCompany:''; confirm the title on the abstract page}
}

% ---- Second tier ----

@inproceedings{zhu2025abc,
  title     = {Establishing Best Practices in Building Rigorous Agentic Benchmarks},
  author    = {Zhu, Yuxuan and Jin, Tengjun and Pruksachatkun, Yada and Zhang, Andy and Liu, Shu and Cui, Sasha and Kapoor, Sayash and Longpre, Shayne and Meng, Kevin and Weiss, Rebecca and Barez, Fazl and Gupta, Rahul and Dhamala, Jwala and Merizian, Jacob and Giulianelli, Mario and Coppock, Harry and Ududec, Cozmin and Kellermann, Antony and Sekhon, Jasjeet and Steinhardt, Jacob and Schwettmann, Sarah and Narayanan, Arvind and Zaharia, Matei A. and Stoica, Ion and Liang, Percy and Kang, Daniel},
  booktitle = {Advances in Neural Information Processing Systems 38 (NeurIPS 2025), Datasets and Benchmarks Track},
  year      = {2025},
  url       = {https://proceedings.neurips.cc/paper_files/paper/2025/hash/f316275b44ee2de533102913828a8107-Abstract-Datasets_and_Benchmarks_Track.html},
  note      = {arXiv:2507.02825, where the title reads ``for Building''}
}

@inproceedings{cemri2025mast,
  title     = {Why Do Multi-Agent {LLM} Systems Fail?},
  author    = {Cemri, Mert and Pan, Melissa Z. and Yang, Shuyi and Agrawal, Lakshya A. and Chopra, Bhavya and Tiwari, Rishabh and Keutzer, Kurt and Parameswaran, Aditya and Klein, Dan and Ramchandran, Kannan and Zaharia, Matei and Gonzalez, Joseph E. and Stoica, Ion},
  booktitle = {Advances in Neural Information Processing Systems 38 (NeurIPS 2025), Datasets and Benchmarks Track},
  year      = {2025},
  url       = {https://neurips.cc/virtual/2025/poster/121528},
  note      = {arXiv:2503.13657}
}

@inproceedings{rubachev2025tabred,
  title     = {{TabReD}: Analyzing Pitfalls and Filling the Gaps in Tabular Deep Learning Benchmarks},
  author    = {Rubachev, Ivan and Kartashev, Nikolay and Gorishniy, Yury and Babenko, Artem},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2025},
  url       = {https://proceedings.iclr.cc/paper_files/paper/2025/hash/571799482291411607c54984153190b0-Abstract-Conference.html},
  note      = {arXiv:2406.19380}
}

@inproceedings{szeider2026contreact,
  title     = {{ContReAct}: A Feedback-Based Architecture for Continuous Agentic Operation},
  author    = {Szeider, Stefan},
  booktitle = {Proceedings of the 2026 International Workshop on Agentic Engineering (AGENT '26)},
  pages     = {56--62},
  publisher = {ACM},
  address   = {Rio de Janeiro, Brazil},
  year      = {2026},
  url       = {https://researchr.org/publication/Szeider26},
  note      = {Paper DOI not captured}
}
```
