# Literature synthesis checked 2026-11-15

Use these corrections before the incoming reviews. The Downloads review and its
BibTeX are retained as supplied, not certified in full. The other review was
pasted in the conversation and emphasized DatasetResearch, repository-level
benchmark generation, MLAgentBench, AgentCoder and industrial code review.

## Positioning for this paper

Use an empirical experience report on this deployed factory, its source-to-public
prediction-task workflow, and independent consumer evaluation of its artifacts.
Automated collection, task construction, agent experimentation and random-search
controls all have prior work. Compare the actual workflow boundaries and measured
outcomes, without a first-system claim or a claim that no predecessor publishes
artifacts. Newly assembled tasks are not evidence of contamination-free sources.
Report what the controls actually match: primary-trial fitting CPU, not total
agent inference cost or all exploratory computation. No extra experiments are
required merely to broaden this literature comparison.

## Nearest task/data systems

- **MLE-Smith**: https://arxiv.org/abs/2510.07307 and
  https://arxiv.org/html/2510.07307v1 . The generate/verify/execute method and supplied
  raw-data starting point are directly relevant. ICLR 2026 publication is supported
  by https://iclr.cc/Downloads/2026 and the accepted-paper search record at
  https://openreview.net/pdf?id=mXQslpfSU5 . The forum itself returned browser
  verification, so the final PDF has not been independently read here. Do not mix
  arXiv counts with final-paper counts. Do not copy the review's 'no explicit
  leakage test' implication: the arXiv appendix explicitly instructs renaming files
  that reveal labels. That is not a comprehensive leakage audit, but it is a
  concrete leakage precaution. I have not established absence of a public release.
- **AutoData**: official NeurIPS 2025 proceedings:
  https://proceedings.nips.cc/paper_files/paper/2025/hash/fd489a44f3bcb9f122e4931ef21d0c43-Abstract-Conference.html .
  Collects web data from a natural-language dataset request. The primary abstract
  supports collection and the human-specified request, not a verified claim about
  every capability the system lacks. It is published, not merely a 2025 preprint.
- **DatasetResearch**: https://arxiv.org/abs/2508.06960 . Relevant to requested
  dataset discovery; it is not itself our full operational comparison. Metadata
  and abstract checked, not a full-method replication.
- **TAM-Bench**: https://arxiv.org/abs/2509.09321 and
  https://arxiv.org/html/2509.09321v1 . Browser/LLM acquisition of existing platform
  competitions. Useful distinction from constructing tasks from agency records.
- **AutoSDT**, retained from the older bibliography:
  https://aclanthology.org/2025.emnlp-main.1546/ . Published EMNLP 2025. Searches
  diverse sources and synthesizes discovery tasks and executable solutions. Its
  existence makes a broad 'no source-to-task automation predecessor' claim unsafe.
- **DataMaster**, retained from the older bibliography:
  https://arxiv.org/abs/2605.10906 . Task-conditioned external-data discovery and
  transformation with a fixed learning algorithm and downstream feedback. This is
  an important comparison omitted from both new shortlists.
- **AutoDataBench**, also already in refs.bib:
  https://arxiv.org/abs/2609.35025 . Artifact-level acceptance of synthesized
  executable tasks, a close evaluation connection. Its tasks and purpose differ
  from agency-record prediction benchmarks; explain that scope rather than omit it.
- Two additional existing references remain relevant:
  https://aclanthology.org/2026.emnlp-main.2330/ (autonomous data engineering for
  model specialization) and https://aclanthology.org/2026.emnlp-main.815/
  (Curation-Bench). Both official proceedings pages checked; do not discard these
  to make the new review's four-system gap claim appear stronger.

## Consumer methods and interpretation

- **MLAgentBench**: published ICML 2024, not just a 2023 arXiv entry:
  https://proceedings.mlr.press/v235/huang24y.html .
- **Agentic Search Spaces for Tabular Machine Learning**:
  https://arxiv.org/abs/2609.16309 . Agents propose module implementations and
  classical HPO searches over them. The abstract reports positive average gains;
  do not group it as a null result. Distinguish expansion of a model's search space
  from our iterative consumer trajectories. Abstract/metadata checked here.
- **Can LLMs Beat Classical Hyperparameter Optimization Algorithms? A Study on
  autoresearch**: https://arxiv.org/abs/2603.24647 . This concerns tuning a small
  language model. Its classical-versus-agent comparisons are relevant methodology,
  not direct evidence of tabular-classifier performance.
- **When Is an LLM Worth It for Hyperparameter Optimization?**:
  https://arxiv.org/abs/2606.21641 . Tabular study explicitly examines default-seed
  confounding and seeded search. Cite its own experimental scope, not a universal
  statement that LLM-assisted research is ineffective. Assess methods, not author
  affiliations or perceived prestige.
- **The More You Automate, the Less You See**:
  https://arxiv.org/abs/2509.08713v2 . Author abstract identifies benchmark selection,
  leakage, metric misuse and post-hoc selection, and supports inspecting logs/code.
  Listed as a NeurIPS 2025 AI4Science spotlight, not a main-conference publication.
- **AI Agents That Matter**: https://arxiv.org/abs/2407.01502 and author-group
  publication listing https://sage.cs.princeton.edu/ . TMLR 2025 publication is
  supported by the author group. Use for baseline, cost and holdout rationale.

## Operations and metadata corrections

- **Measuring Agents in Production**, current v4:
  https://arxiv.org/abs/2512.04123v4 . The abstract reports 20 case studies and 86
  surveyed deployed-systems practitioners, and says accepted ICML 2026 oral. The
  incoming review's 306-survey count and preprint-only status are stale. Preserve
  the exact version if quoting numbers. No extrapolation from its autonomy figures
  to this factory's intervention rate.
- **TheBotCompany**, current title/version:
  https://arxiv.org/abs/2603.25928v2 . Abstract title includes TheBotCompany. Do not
  quote its runtime totals without checking the actual version's methods/table.
- **Automated Code Review In Practice**:
  https://arxiv.org/abs/2412.18531v2 . Abstract notes ICSE 2025 SEIP presentation.
  It is industrial PR review, not direct evidence about the speed or validity of
  our scientific artifact review. The pasted review's metadata needs venue updates.
- The pasted Data Interpreter author list omits authors present on its current
  abstract page: https://arxiv.org/abs/2402.18679 . Copy metadata from primary pages.
- Citation counts supplied by the pasted review have no captured source/date and
  are not evidence of relevance or correctness. Omit them.

## Scope of this verification

Primary abstracts, official proceedings metadata and targeted HTML method passages
were checked. This is not a certification of every number, negative claim, title,
or author list in either incoming review. The manuscript should use the selected
sources only for the claims these checked passages support; inspect the full
method before making a finer comparison. Existing REFERENCES.md records earlier
checks, and these notes supersede conflicts in that older record.
