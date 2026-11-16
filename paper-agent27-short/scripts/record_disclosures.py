"""Preserve pinned documents and the manual finding-by-finding disclosure review.

Run in the original study checkout where the pinned release cache is present.
Judgments below are editorial readings, not keyword-based automated verdicts.
"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'paper-agent27-short'
rows = json.loads((OUT/'analysis/release-records.json').read_text())['records'][:12]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def item(category, finding, status, rationale, *evidence):
    return dict(category=category, finding=finding, disclosure=status,
                rationale=rationale, evidence=list(evidence))
def desc(pointer): return {'file':'reproduction/construction.json', 'pointer':pointer}
def card(substring): return {'file':'README.md','contains':substring}

judgments = {
'fjc-civil-trial-36m': [item('condition','Post-filing jury information; retrospective use','stated',
 'The card explicitly warns that JURY may reflect later corrections and does not establish historical availability.',
 card('filing-time fields such as JURY may reflect later corrections'),desc('/quality/evaluation_contract/limitations/0'))],
'eia861-reliability-deterioration': [item('condition','Lagged outcomes require restricted scoring access','stated',
 'The descriptor expressly requires isolated_rows. This states the access restriction, although it does not explain recovery of earlier targets from later rows.',
 desc('/quality/evaluation_contract/access'),desc('/quality/evaluation_contract/cross_row_audit/rationale'))],
'phmsa-pipeline-penalty-reduction': [item('concern','Original-notice timing is unverified','partly_stated',
 'Historical notice-date availability is expressly assumed and revisions after closure are disclosed. The specific original-or-most-recent meaning of Notice_Sent_Date is not stated in either document.',
 desc('/quality/evaluation_contract/limitations/0'),desc('/quality/evaluation_contract/limitations/6'),desc('/quality/task/prediction_time'))],
'fda-510k-five-year-recall': [item('concern','Undated recalls can become negatives; incidence unverified','not_found',
 'The documents describe missing recall linkage, date boundaries and parse checks, but do not state that an undated linked recall can leave a clearance negative. A date-parse check is not disclosure of this label consequence.',
 desc('/quality/evaluation_contract/limitations/0'),desc('/quality/evaluation_contract/limitations/2'),desc('/source_access_recipe'))],
 't100-new-route-survival': [item('condition','Carrier-code changes can count as entries or exits','partly_stated',
 'Both documents explicitly disclose the exit side; neither spells out inherited routes appearing as new entries. This agrees with review R2.',
 card("Corporate events are confounded with route failure:"),desc('/quality/evaluation_contract/limitations/6'))],
'sbir-phase1-to-phase2-conversion': [item('contradiction','Selection declaration conflicts with later-record exclusions','conflicting_statements',
 'The release discloses missing-phase and agency exclusions, while its selection rule asserts that no outcome field selects rows. Disclosure does not reconcile these statements. The broad any-year exclusion behavior is not fully described.',
 desc('/quality/evaluation_contract/limitations/7'),desc('/quality/timing/row_selection/rule'),card('Phase II records with missing agency or an unknown or missing phase')),
 item('concern','Award-amount timing','partly_stated',
 'The card says award amounts may have been corrected after the award. It does not describe the reviewer\'s unverified Phase I option mechanism or resolve that mechanism. The feature evidence calls the amount verified.',
 card('award_amount and number_employees are as-published values that may have been corrected after the award'),desc('/quality/evaluation_contract/feature_evidence/award_amount'))],
'caa-fce-hpv-escalation': [item('concern','Earliest episode-resolution rule; incidence unverified','not_found',
 'Construction notes describe collapsing resolved episodes but omit the choice of the earliest date when dates differ. Neither document states the resulting possibility that an active episode passes the exclusion.',
 desc('/construction_notes'),desc('/quality/task/population'))],
'wser-effluent-exceedance': [item('condition','Prior-year outcome requires restricted scoring access','stated',
 'The descriptor explicitly requires isolated_rows. The access restriction is stated; the reverse-label exposure mechanism across years is not explained. This does not validate an unrestricted batch interface.',
 desc('/quality/evaluation_contract/access'),desc('/quality/evaluation_contract/limitations/11'),desc('/quality/evaluation_contract/cross_row_audit/rationale'))],
'faa-wildlife-strike-substantial-damage': [item('condition','Retrospective reports with known damage outcomes','stated',
 'The card expressly describes retrospective reconstruction and the post-event known-damage filter.',
 card('The label is an adjudicated code selected by the NWSD manager'),card('Dropping rows with blank DAMAGE'))],
'seattle-building-permit-completion': [item('concern','Post-issuance field updates are unverified','stated',
 'The card names mutable cost and housing fields, and the descriptor says issuance-time availability is assumed, not proven. This states the concern; it does not resolve it.',
 card('Current-vintage retrospectivity: EstProjectCost and HousingUnits'),card('Feature availability at issuance is assumed'))],
'fra-form54-hazmat-release': [item('condition','Retrospective accident-report fields','stated',
 'Both documents state that first-notification availability is inferred and that no field timestamps separate initial knowledge from the final report.',
 desc('/quality/evaluation_contract/limitations/1'),card('The label comes from the same retrospective form'))],
'sdwis-lcr-lead-action-level-next-period': [item('concern','Older-history overlap','not_found',
 'The descriptor instead asserts that all contributing historical records end before the target period. Neither document states that older periods are admitted by start order without an end-date test; incidence remains unverified.',
 desc('/quality/evaluation_contract/feature_evidence/ever_exceeded_before'),desc('/quality/task/prediction_time')),
 item('concern','Implausible unit magnitudes','not_found',
 'The descriptor specifies conversion to mg/L but neither document identifies the implausible high magnitudes or the unverified unit-label explanation observed by review.',
 desc('/quality/measurements/0'),desc('/quality/external_threshold')),
 item('concern','Embargo narrows the scored population','partly_stated',
 'The split policy explicitly requires the prior period to end before the split starts. The documents do not explain its consequence: only first post-boundary periods survive and some monitoring cycles disappear from scoring.',
 desc('/quality/task/split_policy'),desc('/quality/task/population'))],
}
records=[]
for row in rows:
    ds=row['dataset']; selected=Path(row['review_path']).parent.name
    cache=ROOT/'.local/studies'/selected/'evidence/releases'/ds
    pin_path=ROOT/'evidence/reviews'/selected/'pinned-release.json'
    pin=json.loads(pin_path.read_text()); manifest=json.loads((cache/'MANIFEST.json').read_text())
    assert pin[0]==ds and pin[1]==manifest['version'] and sha(cache/'MANIFEST.json')==pin[3]
    dest=OUT/'analysis/disclosure-documents'/ds
    for name in ['MANIFEST.json','README.md','reproduction/construction.json']:
        if name!='MANIFEST.json': assert sha(cache/name)==manifest['assets'][name]['sha256']
        (dest/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(cache/name,dest/name)
    findings=judgments[ds]
    for finding in findings:
        for evidence in finding['evidence']:
            path=dest/evidence['file']; text=path.read_text()
            if 'pointer' in evidence:
                value=json.loads(text)
                for part in evidence['pointer'].strip('/').split('/'):
                    value=value[int(part)] if isinstance(value,list) else value[part]
                evidence['value']=value
            else:
                matches=[(i,line) for i,line in enumerate(text.splitlines(),1) if evidence['contains'] in line]
                assert len(matches)==1, (ds,evidence,matches)
                evidence['line'],evidence['quote']=matches[0]
    records.append({'dataset':ds,'version':pin[1],'huggingface_commit':pin[2],
      'pin_path':str(pin_path.relative_to(ROOT)),'pin_sha256':sha(pin_path),
      'review_path':row['review_path'],'review_sha256':row['review_sha256'],
      'documents':{name:{'path':str((dest/name).relative_to(ROOT)),'sha256':sha(dest/name)}
                   for name in ['MANIFEST.json','README.md','reproduction/construction.json']},'findings':findings})
conditions=[f for r in records for f in r['findings'] if f['category']=='condition']
report={'scope':'Manual comparison of each selected table finding with the complete pinned README and construction descriptor. Not a new source-validity audit. Not found is restricted to these two documents. Stated restrictions need not explain the failure mechanism or establish that an implementation enforces them.',
 'definitions':{'stated':'The specific restriction or uncertainty is explicit.',
 'partly_stated':'Related limitation or rule is explicit, but part of the selected finding is not.',
 'not_found':'The specific selected concern was not found in either inspected document.',
 'conflicting_statements':'Relevant exclusions are disclosed alongside the contradictory selection declaration.'},
 'condition_counts':{'total':len(conditions),'stated':sum(f['disclosure']=='stated' for f in conditions),'partly_stated':sum(f['disclosure']=='partly_stated' for f in conditions)},'records':records}
assert report['condition_counts']=={'total':6,'stated':5,'partly_stated':1}
(OUT/'analysis/disclosure-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report['condition_counts']))
