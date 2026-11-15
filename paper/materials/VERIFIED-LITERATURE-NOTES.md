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

## Additional cost-literature reviews — 15 November 2026

Eduardo supplied two PDFs from Downloads, read on 15 November:

- `Dataset Factory literature review cost, time, and accessibility of agent-driven.pdf`
  (14 pages).
- `Literature Review on Agent-Driven Dataset Factories.pdf` (3 pages; Gemini export).

These are secondary research notes, not sources to cite as evidence. The longer
review is the stronger foundation because it separates starting points, outputs,
cost boundaries, and missing information. Neither review is certified in full.

### Agreed interpretation

Low marginal artifact-generation cost already has precedents. The contribution
of this experience paper is the complete operating factory: discovery through
public release, measured production outcomes and recurring costs, and independent
evaluation of the outputs. Explain failures, recovery, and documented intervention
alongside successful releases. There is no need for an invented human savings ratio.

Suggested framing, subject to the final evidence:

> Prior work shows that agents can construct data and benchmark tasks at low
> marginal cost. We examine what happens when these capabilities are connected
> into an operating factory, from source discovery through public release. We
> report production outcomes and recurring costs, then independently test whether
> the released artifacts support useful prediction work.

### Corrections that must reach the manuscript

1. **Our interim denominator:** approximately $28 is the estimated recurring cost
   of the observation window that produced 11 releases, about $2.54 per release.
   It is not $28 per release, as the shorter review says twice, and is not each
   release's complete lifetime construction cost. Use
   [the pinned calculation](../../evidence/costs/2026-11-15/REPORT.md), then update
   at the final cutoff. Keep independent consumer-study spending outside factory
   production costs; the consumer study is covered by Eduardo's subscription.
2. **MLE-Smith cost:** the shorter review calls $11.73/$13.51 a correction to the
   reported $0.78 main result. A targeted primary-source search of the ICLR paper
   identifies those larger figures in Table 6, an ablation comparing separated
   versus merged Designer–Refactor agents on ten sampled datasets. This does not
   establish a replacement for the main average or a common denominator. The
   final PDF's direct endpoint returned a browser challenge; the table passage
   was accessible through indexed primary-PDF text. Retain this verification
   limit and reconcile the main and ablation accounting before any detailed
   numerical comparison: https://openreview.net/pdf?id=mXQslpfSU5 .
3. **Human effort:** the reviews' hours concern particular activities, including
   adapting scientific programs and curating deposited survey data. They do not
   establish a universal minimum of 2.5–3 hours per dataset, a matched human
   baseline, or labor eliminated by this factory. Gábor Békés's observation is
   personal motivation, not a measured baseline.
4. **Workflow theory:** use Demirer et al. as an interpretive connection, not proof
   that our human effort is one fixed final check or that intermediate costs
   disappear. The longer review also incorrectly maps the consumer study to the
   factory's sole verification step. Factory checks occur before publication;
   independent consumers separately test the published artifacts.
5. **Do not copy the short review's proposed paragraph:** it combines the wrong
   factory denominator, unsupported cost reconciliation, and broad labor claims.
   Its uncited “Cost Does Not Buy Impact” lead is unverified and must not support
   a claim without finding and reading the primary source.

### Useful evidence and limits

- **AutoData, Table 1:** primary-PDF table text reports 5.58 minutes for AutoData
  versus 186.98 minutes for human preparation. The caption defines time as the
  interval from instruction to **starting collection**, not completing and
  publishing a dataset. This supports a specific preparation-step comparison:
  https://openreview.net/pdf?id=x2Rk0lSQra .
- **Lafia et al., Table III:** primary paper reports mean curation hours of
  51, 79, and 165 per study at three curation levels, across 566 studies. This is
  archival curation of deposited data, not equivalent construction of our
  prediction benchmarks. Use only as context for substantive human data work:
  https://bibliography.icpsr.umich.edu/bibliography/citations/data/170058/fileDownload .
- **Perry and Netscher (2022)** and **ScienceAgentBench** are useful additional
  human-effort leads in the longer review. Their specific hours still need a
  primary-method check before use here. Do not transfer a result from one activity
  into a general dataset-construction time or dollar estimate.

For the seven-page paper, use a few close comparisons and a short human-work
discussion. Low recurring cost may make projects practical for small groups once
the system exists; this remains an implication, not a measured accessibility or
labor-market effect. Do not add experiments or delay writing for a larger survey.

## Literature integration revision — 15 November 2026

The revised seven-page draft cites 20 works (previously 12). References now support
specific statements in the introduction, method, discussion, and related work.
The evidence snapshot, figures, scores, cost calculation, and unresolved findings
are unchanged. Repeated explanations were cut; type size and margins were not.

Primary sources checked for the eight added citations:

- **Ariño de la Rubia and Pafka, Identical Runs, Different Results**:
  https://arxiv.org/abs/2609.33812 . Correct author order and title. This is distinct
  from the `pafka` working-library entry for *One Run Is Not Enough*. Supports
  repeated attempts and separate compliance review; does not establish that three
  attempts suffice for rankings or prescribe our 85-minute allowance.
- **Chen and Guestrin, XGBoost**: https://arxiv.org/abs/1603.02754 . The primary
  record identifies KDD 2016 and DOI 10.1145/2939672.2939785. Updated the bibliography
  from the preprint-only entry and cited the method at first technical use.
- **Pan et al., Measuring Agents in Production**, v4:
  https://arxiv.org/abs/2512.04123v4 . Primary abstract records acceptance to ICML
  2026, identifies reliability as a central challenge, and reports controllable
  designs. Used as deployment context, not evidence that our architecture is best.
- **Kandel et al., Enterprise Data Analysis and Visualization**:
  https://vis.csail.mit.edu/classes/6.859/readings/pdfs/Kandel-EnterpriseDataAnalysisAndVisualization.pdf .
  Primary paper identifies discovery, wrangling, profiling, modeling, and reporting
  in interviews with 35 analysts at 25 organizations. Bibliography omits page and
  DOI fields because secondary records disagreed; title, authors, journal, and
  year were checked. No human-time ratio is imported.
- **Lafia et al., Leveraging Machine Learning to Detect Data Curation Activities**:
  https://arxiv.org/abs/2105.00030 and the linked ICPSR primary PDF already recorded
  above. DOI 10.1109/eScience51609.2021.00025 is supplied by the arXiv record.
  Supports transformation and quality-check work. Archival curation is explicitly
  not a matched human benchmark for our releases; no hours are used in the paper.
- **AutoDataBench**: https://arxiv.org/abs/2609.35025 . Supports artifact-level
  checks of generated executable tasks. It is not presented as public-source
  prediction-dataset discovery or as having no prior validation.
- **CurationBench / Can Generalist Agents Automate Data Curation?**:
  https://aclanthology.org/2026.emnlp-main.815/ . Uses the published EMNLP 2026
  version. Its data-selection setting has a fixed training/evaluation recipe;
  it is not equivalent to our source-to-public-release workflow.
- **Exploring Autonomous Agentic Data Engineering for Model Specialization**:
  https://aclanthology.org/2026.emnlp-main.2330/ . Uses the published EMNLP 2026
  version; downstream model feedback guides data engineering. This is a close
  precedent, so the revised text avoids an invented claim of first integration.

These additions complement the earlier verified references. They do not support
new claims of labor displacement, causal architecture benefits, or superior cost.
