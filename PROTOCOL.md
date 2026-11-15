# Prospective factory study: paper ready 16 November 2026

Status: initially registered before the new consumer outcomes; the observation
window ends on November 16 for the author’s submission schedule.
See evidence/protocol-amendments/2026-11-15-deadline.json.
Author: Eduardo Ariño de la Rubia. Target: AGENT 2027 experience/research paper.
The earlier five-release study and two subsequently published releases are pilot
material. Their outcomes will not be pooled with this cohort.

## Question

Over a fixed operating window, what prediction benchmarks does the deployed
factory produce, how often does construction/publication succeed, and what does
independent consumer evaluation reveal about usability, predictive value and
concrete defects? Publication, task validity, improvement and protocol compliance
are separate outcomes. A consumer failing to improve does not invalidate a task.

## Window and denominator

Exact UTC times and model/resource settings are in protocol.json. Observe from
registration through 16 November 08:00 Europe/Paris. Run consumer work as releases
arrive. Finish remaining research by 16 November 11:00 Paris; final analysis begins then.
Draft the narrative while collection continues; finalize results and an author-review
package on November 16 in time for afternoon submission.
This administrative amendment accommodates Eduardo’s travel on November 17–20.
Retain every selected outcome. State the actual observation window and evaluated
cohort in the paper; schedule changes remain in the project history.
This is our working deadline, earlier than the venue deadline. No automatic submission.
The factory's resource increase still expires at the end of November 20.

Capture the public operating snapshot every 30 minutes, including errors,
candidate states, budgets, schedules and release identities. Retain the complete
candidate denominator. Separate candidates already active at registration from
new admissions; neither unresolved records nor carry-in releases establish a
completed-cohort yield. Request a final compact transactional attempt ledger from
Scout. Snapshot timing is not continuous observation and cannot establish every
intermediate failure without that ledger.

Include the first 12 newly published modern dataset IDs, ordered by their first
publication verification timestamp and dataset ID, within the window. New versions
of a pilot ID do not count as new datasets. Record every release, including those
beyond the consumer capacity cap. Pin the first accepted version; do not substitute
later repairs. Each included dataset keeps its place if loading, fitting, audit or
scoring fails. Do not replace failures with a later, more favorable dataset.
No selection on baseline AUC, consumer gains, country or perceived interestingness.

The factory runs at a recorded commit with normal automatic repair. No deliberate
engine tuning during the observation window. Necessary defect repairs are allowed
but dated, justified and reported; do not hide them to preserve an autonomy claim.
Scout remains the only worker-launching coordinator; the Mac runs consumers.

## Consumer experiment

Reuse the pilot's runner, pinned Python/ML dependencies, saved-model selection and
row-wise inference. Fable 5.2 at high effort; record requested/reported IDs. Three
fresh attempts per dataset, each with an 85-minute research allowance, three
concurrent attempts and five fitting threads per attempt. One dataset at a time.
Maximum 36 attempts. Explicit time/resource limits remain; no replacement model
or extra attempts after seeing an unfavorable result. Successful invocations that
exit in under ten seconds have up to a 60-second cooldown charged to the research
allowance, preventing the pilot's rapid resume loop. Failed CLI retries retain
the existing bounded policy. Report actual active invocation and waiting times.

Train/validation only during research. All three attempts and controls for a
dataset freeze before its holdout is fetched. Later dataset sessions cannot read
prior results, other sessions or the coordinator's files. Public holdouts remain
reachable; isolation is procedural, not an OS security boundary. Do not send
results to the production factory as optimization feedback during this window.

Same permissible raw predictor set for consumer, ordinary scaffold and random
search: quality.features in pinned reproduction/construction.json, excluding IDs,
carry columns, post-hoc and label-source columns. Learned encodings fit only on
training; own labels must not enter target-encoding priors. No external labels,
ensembles, validation refit or alternate model family. The released baseline is
reproduced separately as a release usability check, with its own feature policy.
Missing/inconsistent contracts are recorded failures, not silently guessed inputs.

Primary selection: maximum replayed validation AUC, ties within 1e-9 resolved to
first trial. Score exact saved models once on holdout after the barrier. Preserve
all trials, selected source, fitted artifacts, predictions, transcripts and errors.
Compare ordinary XGBoost and the existing per-run random hyperparameter control;
report CPU-matching shortfall/overshoot and excluded diagnostic/inference costs.
A six-hour per-dataset orchestration bound and the global cutoff preserve unfinished
work as incomplete. Host downtime, capacity and provider failures are separate from
dataset defects. No outcome-dependent extensions.

## Review and inference

Before consumer research, a separate bounded review reads source code and
train/validation metadata (no holdout). Record target meaning, feature timing,
selection/vintage assumptions, label-derived cross-row exposure mechanisms and
an uncertainty cluster key with a reason. If entity dependence is unresolved,
report that limitation; do not silently call row resampling independent evidence.
This reviewer does not approve publication or choose which datasets get evaluated.

After freeze, review all selected source files and flagged transcript requests.
Probe own-label dependence, row/batch/order behavior and concrete producer exposure
mechanisms where applicable. Record coverage and unperformed checks explicitly.
Automatic flags and LLM reviews are not proof of compliance or exhaustive absence
of leakage. Keep raw and protocol-qualified results distinct; no repaired refit
may replace a registered result.

Use 2,000 paired whole-entity bootstrap draws when the predeclared cluster key is
available; fixed seed derived from dataset ID. Compare each consumer against both
controls on identical resampled rows. Report cluster count, largest cluster,
positives, invalid draws, point estimate and pointwise percentile 95% interval.
These intervals condition on fitted models/cohort and chosen dependence structure;
they exclude run variation and temporal shift. No universal row-count gate, no
pooled success probability from 12 selected releases, no significance claims from
positive point estimates alone. If analysis is incomplete, mark it incomplete.

## Reporting and stop rule

All operational attempts and all selected consumer outcomes enter the report.
Separate measured use, configured allowances and estimated billing; never call
CLI cumulative cost sums actual spend. Report interruptions and engineering fixes.
Write the paper around the observed findings, including null or negative findings.
Do not manufacture a strong submission if few releases or incomplete review leave
only weak evidence. An honest experience/short-paper draft is an acceptable outcome.

Use standard technical English, inverted-pyramid structure, precise bounded claims
and vector figures. Reuse verified literature and the IEEE template; eight pages
including references is the maximum. Have the author review prose and claims.
Keep the evidence private while drafting and prepare public release at submission.
No change to pilot files, frozen releases, production candidates or credentials.
