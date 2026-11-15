# Paragraph value audit — 15 November 2026

The paper has useful evidence, but several execution details and repeated warnings
still occupy space that should explain the factory and its results. The clearest
cuts are six standalone paragraphs: the repeated accounting lesson (P34), the
generic table warning (P36), the special railway recap (P39), the case-section
preface (P41), the Seattle stopping-rule story (P44), and the probe-debugging story
(P45). Removing these paragraphs does **not** mean hiding missing results or
unresolved dataset concerns: the necessary disclosures have better locations.

This is an audit, not an applied prose revision. Each of the 62 prose paragraphs
is assessed below in manuscript order, including the abstract and AI disclosure.
The four captions are assessed separately. Bibliographic entries, headings and
the table header are not prose paragraphs. References are not re-verified here.

Manuscript SHA-256: `659f487c7c7f33d88e6e8a661376deae0499a25bd2976fa631320e22d09d2403`.
Repository at audit: `d219d6646f19443f313984ee58d3d625f1c166f7`. Line numbers and opening phrases identify the
reviewed version; later authorized result integration can change those positions.

Test: does the paragraph help readers understand the system, assess a result, or
apply a supported lesson? Precision that changes interpretation stays. Filenames,
Boolean fields, repeated caveats and recovery chronology usually belong in the
evidence. Draft-status notices remain pending the separately agreed final pass.

## Paragraph-by-paragraph decisions

### P01 — KEEP — Abstract

Opening: “Building prediction benchmarks from public data requires finding suitable sources, defining meaningful…” ([source line 16](draft/main.tex#L16)).

The rewritten abstract gives the problem, integrated system, bounded cost, consumer evidence and one concrete defect. It is not an execution diary.

### P02 — KEEP — Introduction

Opening: “Public data does not arrive as a usable prediction benchmark. Researchers must…” ([source line 22](draft/main.tex#L22)).

Establishes the actual work the factory addresses and grounds it in research on analytical work. This is necessary motivation.

### P03 — KEEP — Introduction

Opening: “We built Dataset Factory to make this a continuing process for a…” ([source line 24](draft/main.tex#L24)).

Defines the system and the scope of autonomy. The distinction between automatic releases and human system development changes what the deployment claim means.

### P04 — TRIM — Introduction

Opening: “AutoData collects web records from requests~\cite{autodata-web}; DatasetResearch evaluates discovery~\cite{datasetresearch}; MLE-Smith constructs tasks…” ([source line 26](draft/main.tex#L26)).

The four-system catalogue duplicates Related Work. Retain the integration gap and the concrete contribution here; leave individual comparisons in Section VI.

### P05 — MERGE — Introduction

Opening: “We observed 12 releases across courts, utilities, safety regulation, funding, transport, and…” ([source line 28](draft/main.tex#L28)).

A brief overview of domains and evaluation is useful. Merge it into the introduction; the three different interim denominators belong together in Methods.

### P06 — KEEP — Introduction

Opening: “We organize the experience around three questions. RQ1---Operation: What does the deployed…” ([source line 30](draft/main.tex#L30)).

The three research questions provide the structure of this experience report. The final warning repeats the discussion and can be cut.

### P07 — DRAFT STATUS — Introduction

Opening: “Observation boundaries. Production accounting ends on 15 November 2026 at 14:24 UTC;…” ([source line 32](draft/main.tex#L32)).

Keep for the requested final cleanup. At submission, consolidate observation boundaries in Methods; minute-level recovery chronology does not need its own introduction paragraph.

### P08 — TRIM — The product and its boundaries

Opening: “Each release defines a binary prediction task from real public records. It…” ([source line 36](draft/main.tex#L36)).

Defining the released product and its two public destinations is essential. Shorten the file inventory to task definition, data, construction code and provenance; the release manifest lists the rest.

### P09 — KEEP — The product and its boundaries

Opening: “The task contract distinguishes retrospective research from historical forecasting. A current administrative…” ([source line 38](draft/main.tex#L38)).

Retrospective modeling versus historical forecasting changes the intended use of these datasets. This is substantive scope, not bookkeeping.

### P10 — KEEP — Known procedures run in code

Opening: “A scheduled controller advances durable SQLite state through \emph{discover}, \emph{build}, \emph{evaluate}, and…” ([source line 47](draft/main.tex#L47)).

Durable state, one coordinator, workers and cleanup explain the architecture and failure recovery. These implementation choices are relevant to an agent-engineering audience.

### P11 — TRIM — Known procedures run in code

Opening: “Bounded model tasks interpret sources, propose prediction tasks, generate code, and review…” ([source line 49](draft/main.tex#L49)).

Keep the model/code division and model identity. Proposal reuse and transfer checks add little after the controller description; merge these into the architecture explanation.

### P12 — MERGE — Known procedures run in code

Opening: “Failures leave attempt records and diagnostics for reconciliation. Bounded retries and deferrals…” ([source line 51](draft/main.tex#L51)).

Failure records and bounded retries matter, but do not require a separate paragraph. Fold them into the controller description and avoid presenting a three-item example list as a measured failure taxonomy.

### P13 — KEEP — Acceptance and publication

Opening: “Construction runs artifact checks on the worker. These include file and schema…” ([source line 54](draft/main.tex#L54)).

Readers need to know what the factory checked before publishing, especially because later reviews found a defect. This paragraph explains the acceptance mechanism.

### P14 — KEEP — Acceptance and publication

Opening: “A manifest binds accepted bytes. Publication transfers matching files to both platforms,…” ([source line 56](draft/main.tex#L56)).

Matching public artifacts, anonymous access and preserved versions distinguish the factory from task-generation experiments. Explain the manifest in plain language, but retain the mechanism.

### P15 — TRIM — Production record and cohort

Opening: “Production accounting spans 12 November 2026 at 21:27:59 UTC to 15 November…” ([source line 60](draft/main.tex#L60)).

Keep the observation interval and data sources. Exact seconds belong in the evidence export. Preserve the pending cutoff notice until the final update, as requested.

### P16 — TRIM — Production record and cohort

Opening: “At the interim export, the ledger includes 42 candidate records created before…” ([source line 62](draft/main.tex#L62)).

Keep the distinction between search slots, candidates and completed work, so readers do not infer an invalid success rate. Consolidate the inventory counts with the production funnel instead of scattering them across Methods and Results.

### P17 — TRIM — Production record and cohort

Opening: “Consumers select the first 12 new dataset identities by publication-verification time, breaking…” ([source line 64](draft/main.tex#L64)).

Publication-order selection, fixed versions and inclusion of failures are essential. Identifier tie-breaking and the precise arrival time of release twelve are reproducibility details; the final cohort needs a much shorter description.

### P18 — MERGE — Production record and cohort

Opening: “Discovery continues during consumer evaluation, without consumer feedback to selection or acceptance.…” ([source line 66](draft/main.tex#L66)).

Keeping consumer outcomes out of factory selection is useful methodology. One sentence in the cohort paragraph is enough; the separate intervention sentence is covered elsewhere.

### P19 — TRIM — Cost accounting

Opening: “We estimate recurring production expenditure as inference plus workers plus allocated hosting.…” ([source line 69](draft/main.tex#L69)).

Keep the three cost components, rate basis and estimated rather than invoiced nature of the numbers. Cache categories, IPv4, tax, currency retrieval and hourly-rounding mechanics belong in the calculation record.

### P20 — TRIM — Cost accounting

Opening: “Recorded resource use from all production attempts in the window contributes, including…” ([source line 71](draft/main.tex#L71)).

Including unsuccessful work and defining the publication denominator are central. The exact two-session/one-worker boundary exception belongs in the accounting evidence, with its effect retained in the reported estimate.

### P21 — KEEP — Cost accounting

Opening: “The estimate excludes development, author and operator labor, paper preparation, upstream data…” ([source line 73](draft/main.tex#L73)).

Cost exclusions and the absence of a measured human-labor comparison materially constrain the paper’s cost claim. Retain these clearly in one place, without repeating them in every later paragraph.

### P22 — TRIM — Independent prediction experiments

Opening: “Separate Fable 5.2 consumers run under the same operator as the factory;…” ([source line 76](draft/main.tex#L76)).

Keep fresh sessions, common operator, model, repetitions, time and fitting resources. Sequential dataset scheduling and model-ID bookkeeping can move to the protocol artifact. The model-ranking warning is not needed when no ranking is claimed.

### P23 — KEEP — Independent prediction experiments

Opening: “Consumers can change XGBoost~\cite{xgboost} preprocessing, feature transformations, and hyperparameters, using training and…” ([source line 78](draft/main.tex#L78)).

Permitted inputs, the untuned baseline and CPU-budgeted tuning control are necessary to interpret the results. This is technical detail that earns its space. Long feature-exclusion lists and exact overshoot accounting can be shortened without obscuring the control budget.

### P24 — TRIM — Independent prediction experiments

Opening: “Selection uses replayed validation area under the ROC curve (AUC), with ties…” ([source line 80](draft/main.tex#L80)).

Keep validation-based selection, freezing before holdout and the row-wise interface. Exact tie handling and the sentence explaining why validation alone is not the result can move out; the former is in the protocol and the latter follows from the design.

### P25 — SPLIT / MOVE — Independent prediction experiments

Opening: “Holdouts are publicly available. Consumers are instructed not to access them, other…” ([source line 82](draft/main.tex#L82)).

Public holdouts and procedural isolation deserve a short clear paragraph. The quota reset, dataset-by-dataset recovery history and repeated no-selection assurances interrupt that explanation. Retain one recovery-method sentence; move the chronology into the evidence record.

### P26 — KEEP — Source review, uncertainty, and artifact probes

Opening: “A separate bounded Fable review precedes scoring. It examines the task contract,…” ([source line 85](draft/main.tex#L85)).

Explains who reviewed task meaning, what evidence was examined and how that review differs from production acceptance. These distinctions are needed to understand the findings.

### P27 — TRIM — Source review, uncertainty, and artifact probes

Opening: “Where a grouping is available, paired bootstrap intervals resample whole groups 2,000…” ([source line 87](draft/main.tex#L87)).

Keep paired group resampling, replicate count, interval type, conditional scope and multiplicity policy. The seed derivation is a reproducibility detail for the analysis code, not an interpretive requirement.

### P28 — TRIM — Source review, uncertainty, and artifact probes

Opening: “Derived probes inspect row-order behavior, batch-versus-single-row preparation, external activity during preparation, and…” ([source line 89](draft/main.tex#L89)).

Keep what the probes test and their limited coverage. The last sentence describes how we inspected diagnostic files rather than a distinct study method; detailed execution-status interpretation belongs in the review record.

### P29 — KEEP — Operation: production across sources

Opening: “The window contains 394 started stage attempts. Forty-one candidates completed discovery, 14…” ([source line 93](draft/main.tex#L93)).

The factory funnel and repeated-work denominator are direct evidence for the central deployment question. Retain the warning that these are milestones, not a completed-cohort yield.

### P30 — KEEP — Operation: production across sources

Opening: “Table~\ref{tab:scores} identifies the tasks. For the eleven releases in the accounting window,…” ([source line 95](draft/main.tex#L95)).

Time from admission to publication is useful operational evidence. The exclusion of unsuccessful candidates is necessary to interpret it.

### P31 — MERGE — Operation: production across sources

Opening: “The ledger records 76 discovery retries, 184 build retries, and 14 semantic…” ([source line 97](draft/main.tex#L97)).

Retry and repair counts matter, but combine them with the production funnel and Figure 2 discussion. Keep the distinction between attempts and defects; it prevents a misleading failure-rate claim.

### P32 — TRIM — Operation: production across sources

Opening: “On 14 November, an intervention corrected worker-budget accounting that retained worst-case reservations…” ([source line 105](draft/main.tex#L105)).

This is a relevant factory failure, unlike the consumer warning-file incident. Keep cause, effect and repair in plain terms. Reservation arithmetic and rounding are not needed here. Preserve the unfinished intervention-reconciliation notice until the final cleanup.

### P33 — TRIM — Operation: recurring expenditure

Opening: “Estimated expenditure is \$27.84--\$27.94 over 64.93 hours: \$13.84--\$13.95 inference, \$12.19 workers, and…” ([source line 108](draft/main.tex#L108)).

Keep total recurring cost, the publication denominator and pricing sensitivity. Figure 2 already gives the component amounts; the comparison with MLE-Smith and AutoSDT belongs in Related Work.

### P34 — REMOVE STANDALONE — Operation: recurring expenditure

Opening: “The practical accounting lesson is that short-lived workers incur rounded charges, whereas…” ([source line 110](draft/main.tex#L110)).

Repeats the worker-accounting repair and its effect immediately after they were explained. Keep the evidence link elsewhere; this paragraph adds no new observation or interpretation.

### P35 — TRIM — Use: independent experiments and modeling headroom

Opening: “The first eleven releases have scores from the factory baseline and the…” ([source line 113](draft/main.tex#L113)).

Keep completed coverage and the number of unsuccessful attempts. The original-to-retry arithmetic and blocker-file narration are a recovery diary. Replace with a concise outcome summary when the authorized retry is integrated.

### P36 — REMOVE STANDALONE — Use: independent experiments and modeling headroom

Opening: “Table~\ref{tab:scores} reports the raw saved-model results across all scored attempts. Holdout size…” ([source line 115](draft/main.tex#L115)).

The table caption identifies the scores; Methods and Threats explain their limits. This paragraph adds another generic warning without a new result. Introduce the table in the substantive results paragraph.

### P37 — TRIM — Use: independent experiments and modeling headroom

Opening: “Headroom over the fixed model. On nine of ten scored tasks, all…” ([source line 126](draft/main.tex#L126)).

The untuned comparison is central. Keep the aggregate result and important exceptions, but avoid spelling out every positive task already shown in Figure 3. Consolidate repeated limitations in the case discussion and Threats.

### P38 — KEEP — Use: independent experiments and modeling headroom

Opening: “Added benefit over conventional tuning. Against tuned random search, all three intervals…” ([source line 128](draft/main.tex#L128)).

The tuned comparison answers a different question and must remain visible. Retain the result and its interpretation; the final task-validity warning repeats the adjacent section.

### P39 — REMOVE STANDALONE — Use: independent experiments and modeling headroom

Opening: “Railway-hazmat consumers reach AUC 0.784--0.791 versus 0.731 untuned and 0.747--0.751 for random…” ([source line 130](draft/main.tex#L130)).

Railway score ranges duplicate the table and receive special prominence mainly because the recovery was newly integrated. Move the retrospective-use and repeated-entity limitations to the existing scope/uncertainty discussion; no separate railway result paragraph is justified.

### P40 — MERGE — Use: independent experiments and modeling headroom

Opening: “Pipeline-enforcement penalties lacks the operator identifier needed for its main dependence structure.…” ([source line 132](draft/main.tex#L132)).

The absent pipeline-operator key explains a missing uncertainty estimate. Keep this as a specific table note or uncertainty limitation, not another full results paragraph.

### P41 — REMOVE STANDALONE — Validity: what execution and scores do not check

Opening: “The cases below distinguish a confirmed discrepancy, a conditional access limitation, and…” ([source line 141](draft/main.tex#L141)).

Announces the categories of the coming cases without adding evidence. Clear case headings and descriptions can make the distinction directly.

### P42 — TRIM — Validity: what execution and scores do not check

Opening: “Selection logic can contradict the declared population. In the SBIR research-grant task,…” ([source line 143](draft/main.tex#L143)).

This confirmed mismatch is one of the strongest cases. Retain how later records affect selection, the conflicting population claim and the consequence. Detailed phase-year and ambiguity-set mechanics can move to the code audit; do not imply a measured score effect.

### P43 — TRIM — Validity: what execution and scores do not check

Opening: “A history feature needs an access contract. Wastewater uses the previous year's…” ([source line 145](draft/main.tex#L145)).

The history-feature case earns space because it shows why the scoring interface changes benchmark interpretation. Explain that future rows can contain past labels. The 11,800-match count and probe recap can move to the evidence; retain the row-access assumption.

### P44 — REMOVE STANDALONE — Validity: what execution and scores do not check

Opening: “A concern and a stopping rule are different. Seattle run 1 linked…” ([source line 147](draft/main.tex#L147)).

The Seattle paragraph mixes an unverified timing concern, a runner implementation quirk and a grouping limitation. Keep the timing concern in limitations, the recovered execution in the outcome record and the grouping limit with uncertainty. BLOCKER.json, its Boolean and file-presence logic do not justify a main-text case study.

### P45 — REMOVE STANDALONE — Validity: what execution and scores do not check

Opening: “Completing a check is not passing it. All 29 preparations passed batch/order…” ([source line 149](draft/main.tex#L149)).

The heading promotes a debugging lesson into a finding. Keep the number and scope of completed versus unresolved probes in a concise review-status statement. Move wrapper exit behavior and the temporary Seattle probe view to the evidence repository; unresolved checks must remain disclosed.

### P46 — KEEP — Integration makes failures inspectable

Opening: “The factory repeatedly moved from discovery to artifacts that separate consumers could…” ([source line 153](draft/main.tex#L153)).

Draws an operational lesson from the factory record: durable attempts make failures inspectable and resumable. That is relevant to the venue. Avoid recounting the accounting bug a third time.

### P47 — TRIM — Recurring expenditure informs operation

Opening: “The ratio covers exploration, unsuccessful work, and public delivery. The repair also…” ([source line 156](draft/main.tex#L156)).

Keep what low recurring expenditure means for a group that already has the system. The cost scope and reservation repair repeat Results and Methods. Merge this short interpretation with the human-work discussion.

### P48 — KEEP — Recurring expenditure informs operation

Opening: “Analyst interviews describe discovery, wrangling, modeling, and reporting~\cite{kandel}; curation logs record transformation…” ([source line 158](draft/main.tex#L158)).

This is the requested connection to human analytical work, grounded in literature and limited to analogy. It matters to the motivation; preserve the distinction between recurring machine cost and unmeasured labor displacement.

### P49 — KEEP — Performance and validity need separate evidence

Opening: “Consumers demonstrated artifact use and conditional headroom. Tuned search tested added agent…” ([source line 161](draft/main.tex#L161)).

Explains why a competitive tuned control does not erase dataset usefulness. This is interpretation that the numerical table cannot supply. Avoid another broad validity disclaimer at the end if the next paragraph provides the specific checks.

### P50 — KEEP — Performance and validity need separate evidence

Opening: “The cases suggest three practices: compare population declarations with selection code, preserve…” ([source line 163](draft/main.tex#L163)).

Gives three concrete engineering practices tied to observed cases. Keep them proportional to the evidence. The incomplete-review disclosure remains until the final completion pass.

### P51 — KEEP — Discovery, construction, and operating cost

Opening: “AutoData~\cite{autodata-web} and DatasetResearch~\cite{datasetresearch} address collection and discovery. MLE-Smith~\cite{qiang2026mlesmith} generates competition-style tasks from…” ([source line 167](draft/main.tex#L167)).

Locates the contribution among systems for discovery and task construction. Keep the distinction between supplied datasets and autonomous source discovery; reduce the duplicate catalogue in the introduction instead.

### P52 — KEEP — Discovery, construction, and operating cost

Opening: “Reported costs have different boundaries. MLE-Smith's first arXiv version reports \$0.78 per…” ([source line 169](draft/main.tex#L169)).

Makes the cost comparison interpretable and prevents an unsupported cheapest-system claim. Different output units and accounting boundaries are substantive, not administrative.

### P53 — TRIM — Artifact quality and independent use

Opening: “The Agentic Benchmark Checklist separates task validity, outcome validity, and reporting~\cite{abc}; AgentSuite's…” ([source line 172](draft/main.tex#L172)).

Keep the connection from our cases to benchmark-auditing work. The sentence about failing one checklist recommendation reads as a compliance assessment we did not conduct and repeats the isolation limitation; state the actual limitation once in Methods/Threats.

### P54 — MERGE — Artifact quality and independent use

Opening: “AutoDataBench evaluates generated executable tasks for validity and other quality dimensions~\cite{autodatabench}; CurationBench…” ([source line 174](draft/main.tex#L174)).

The artifact-quality literature is relevant, but three one-sentence summaries read as a citation catalogue. Combine with the preceding paragraph and explain the specific connection to evaluating produced datasets.

### P55 — TRIM — Artifact quality and independent use

Opening: “MLAgentBench and MLE-bench evaluate agents on machine-learning work~\cite{mlagentbench,mlebench}. Here, consumer agents evaluate…” ([source line 176](draft/main.tex#L176)).

Keep the producer-versus-consumer distinction from MLAgentBench and MLE-bench. Repeating the entire rationale for trials, controls, freezing and source checks belongs in neither this paragraph nor a second Methods summary.

### P56 — KEEP — Threats to Validity and Evidence Availability

Opening: “This short, single-factory study uses one production-model family and consumer configuration. The…” ([source line 179](draft/main.tex#L179)).

Short duration, one factory/model setup and repeated attempts on a small number of tasks restrict generalization. This is an essential limitation, not defensive filler.

### P57 — KEEP — Threats to Validity and Evidence Availability

Opening: “All tasks draw on existing public records. Packaging does not establish that…” ([source line 181](draft/main.tex#L181)).

Prior data exposure, public holdouts and incomplete semantic review affect what the evaluation establishes. Keep the concrete limits; do not imply that automatic flags prove compliance.

### P58 — KEEP — Threats to Validity and Evidence Availability

Opening: “Dependence keys are imperfect. FDA product codes miss some firm and recall-event…” ([source line 183](draft/main.tex#L183)).

The imperfect groupings directly affect the reported intervals. Retain the important dependence structures and conditional interpretation, with less duplication in individual results paragraphs.

### P59 — MERGE — Threats to Validity and Evidence Availability

Opening: “Costs use measured resources and published rates, not reconciled invoices, with the…” ([source line 185](draft/main.tex#L185)).

Estimated prices and excluded waiting time are material, but are already explained in Methods and Results. Consolidate there. Retain the single point that routing/accounting changed during the window when describing the deployed configuration.

### P60 — KEEP — Threats to Validity and Evidence Availability

Opening: “Release pins, attempts, models, predictions, transcripts, reviews, and analysis code are retained…” ([source line 187](draft/main.tex#L187)).

Public evidence availability and the distinction between artifact replay and a new stochastic agent run are necessary for the reproducibility claim. Keep the planned-publication notice until the final pass.

### P61 — TRIM — Conclusion

Opening: “Dataset Factory connected source discovery, construction, checks, and public delivery across 12…” ([source line 190](draft/main.tex#L190)).

Keep the integrated deployment, bounded operating cost and interpretation of consumer use. Reduce the count and caveat catalogue; the conclusion should state what was learned rather than repeat every result category.

### P62 — KEEP — AI Assistance

Opening: “AI systems assisted implementation, literature search, review briefs, source and transcript review,…” ([source line 193](draft/main.tex#L193)).

The AI-assistance disclosure is substantive transparency and submission information. It is not the editorial-history clutter targeted by this audit.

## Captions

- **Figure 1 — keep.** The short title identifies the diagram. The unnecessary no-feedback annotation has already been removed; its methodological meaning remains in the body.
- **Figure 2 — keep.** The panel meanings and midpoint convention help readers interpret the display. No operational diary remains.
- **Table I — keep the reading keys.** Ranges versus intervals, group counts and missing-value notation matter. Update the pending-result sentence with the final evidence; do not add a retry history.
- **Figure 3 — keep.** Symbols, interval meaning and group counts are sufficient. Do not add sorting explanations or another catalogue of caveats.

## What I would change first, if approved

1. Remove the six standalone paragraphs named above; preserve their necessary
   result/limitation facts in the specified locations.
2. Compress cost mechanics and recovery chronology into artifact references.
3. Tighten the two useful source cases to their cause, consequence and evidence.
4. Consolidate limitations once, close to the claims they qualify or in Threats.
5. Preserve the system architecture, both controls, cost boundaries, related-work
   comparisons, human-work discussion and actual scientific limitations.

The main issue is misplaced detail, not the existence of technical detail. The
factory architecture, comparison protocol and confirmed source/code discrepancy
earn space. Consumer-runner debugging does not become a contribution merely
because it was difficult to resolve.
