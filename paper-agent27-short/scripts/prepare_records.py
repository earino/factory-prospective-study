"""Render the short paper's release rows from the frozen final study inputs."""
from pathlib import Path
import hashlib
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'paper-agent27-short'
snapshot_path = ROOT / 'paper/analysis/final-inputs-2026-11-16.json'
snapshot = json.loads(snapshot_path.read_text())
# Editorial summaries of existing reviews, not new acceptance verdicts.
labels = {
 'fjc-civil-trial-36m': ('Trial within 36 months (courts)', 'Condition: post-filing jury information; retrospective use.', ['condition'], 'Summary; R1'),
 'eia861-reliability-deterioration': ('Reliability deterioration (electricity)', 'Condition: lagged outcomes require restricted scoring access.', ['condition'], '6; R1'),
 'phmsa-pipeline-penalty-reduction': ('Penalty reduction (pipelines)', 'Concern: original-notice timing is unverified.', ['concern'], 'R1'),
 'fda-510k-five-year-recall': ('Five-year recall (medical devices)', 'Concern: undated recalls can become negatives; incidence unverified.', ['concern'], 'R5'),
 't100-new-route-survival': ('Route survival (aviation)', 'Condition: carrier-code changes can count as entries or exits.', ['condition'], 'R2'),
 'sbir-phase1-to-phase2-conversion': ('Phase I to II award (research grants)', 'Contradiction: selection declaration; concern: award-amount timing.', ['contradiction','concern'], 'Summary; 8.1; 8.3'),
 'caa-fce-hpv-escalation': ('Violation escalation (air regulation)', 'Concern: episode-resolution rule; incidence unverified.', ['concern'], 'R1'),
 'wser-effluent-exceedance': ('Exceedance (wastewater)', 'Condition: prior-year outcome requires restricted scoring access.', ['condition'], 'Summary; R1'),
 'faa-wildlife-strike-substantial-damage': ('Strike damage (aviation)', 'Condition: retrospective reports with known damage outcomes.', ['condition'], 'Summary; M4; M6'),
 'seattle-building-permit-completion': ('Permit completion (construction)', 'Concern: post-issuance field updates are unverified.', ['concern'], 'R1'),
 'fra-form54-hazmat-release': ('Hazmat release (railways)', 'Condition: retrospective accident-report fields.', ['condition'], '3; 7'),
 'sdwis-lcr-lead-action-level-next-period': ('Next-period lead exceedance (water)', 'Concerns: older-history overlap, unit magnitudes, embargo selection.', ['concern'], '8.2; 8.3; 8.5'),
 'usgs-streamgage-record-survival': ('Record survival (streamgages)', 'Not evaluated.', ['not_evaluated'], None),
 'ca-beach-advisory-duration': ('Advisory duration (beaches)', 'Not evaluated.', ['not_evaluated'], None),
}
records=[]
for row in snapshot['production_cohort']:
 ds=row['dataset']; label,finding,categories,sections=labels[ds]
 selected=snapshot['analysis_selection'].get(ds)
 report=f'evidence/reviews/{selected}/PRE-REVIEW.md' if selected else None
 latency=(datetime.fromisoformat(row['published_at'])-datetime.fromisoformat(row['created'])).total_seconds()/60
 records.append({**row,'label':label,'latency_minutes':latency,'latency_rounded':round(latency),
   'consumer':'Completed' if selected else 'Not evaluated','finding':finding,'finding_categories':categories,
   'review_path':report,'review_sections':sections,
   'review_sha256':hashlib.sha256((ROOT/report).read_bytes()).hexdigest() if report else None})
assert len(records)==14 and sum(r['consumer']=='Completed' for r in records)==12
(OUT/'analysis/release-records.json').write_text(json.dumps({'snapshot':str(snapshot_path.relative_to(ROOT)),
 'snapshot_sha256':hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
 'scope':'Selected findings from existing bounded reviews; not an exhaustive or uniform audit. No review performed for the final two releases.',
 'records':records},indent=2)+'\n')
def tex(s):
 return s.replace('&',r'\&').replace('%',r'\%').replace('_',r'\_')
lines=[]
for r in records:
 lines.append(f"{tex(r['label'])} & {r['latency_rounded']} & {r['consumer']} & {tex(r['finding'])} \\\\")
(OUT/'draft/generated/release-rows.tex').write_text('\n'.join(lines)+'\n')
print('Prepared 14 release rows from frozen timestamps and 12 retained reviews.')
