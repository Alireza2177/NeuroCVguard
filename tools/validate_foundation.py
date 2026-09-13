"""Validate foundation artifacts, NOT the unimplemented NeuroCVguard application.

Requires jsonschema. Reads only local files and writes a scoped QA record.
"""
from __future__ import annotations
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
checks=[]

def read_json(path: str):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def check(name: str, condition: bool, detail: str = '') -> None:
    checks.append({'check':name,'passed':bool(condition),'detail':detail})

def main() -> int:
    schemas={}
    for p in sorted((ROOT/'contracts').glob('*.schema.json')):
        schema=json.loads(p.read_text(encoding='utf-8'))
        try:
            Draft202012Validator.check_schema(schema)
            schemas[str(p.relative_to(ROOT))]=schema
            check('schema:'+p.name,True)
        except Exception as exc:
            check('schema:'+p.name,False,str(exc))
    for item in read_json('fixtures/manifest.json'):
        errors=list(Draft202012Validator(schemas[item['schema']]).iter_errors(read_json(item['path'])))
        actual=not errors
        check('fixture:'+item['path'],actual==item['valid'],
              'Expected structurally '+('valid' if item['valid'] else 'invalid')+'; '+str(len(errors))+' schema error(s).')
    stages=read_json('state/stage_plan.json')
    case_rows=read_json('qa/acceptance_cases.json')
    requirements=read_json('qa/requirements.json')
    rules=read_json('qa/rule_catalog.json')
    status=read_json('state/PROJECT_STATUS.json')
    stageids={s['id'] for s in stages}
    check('stage-count',len(stages)==18)
    check('stage-order',[s['id'] for s in stages]==[f'S{i:02d}' for i in range(18)])
    check('work-package-count',sum(len(s['packages']) for s in stages)==54)
    check('unique-cases',len({c['id'] for c in case_rows})==len(case_rows))
    check('unique-rules',len({r['id'] for r in rules})==len(rules))
    check('unique-requirements',len({r['id'] for r in requirements})==len(requirements))
    check('case-stages',all(c['stage'] in stageids for c in case_rows))
    check('rule-stages',all(r['stage'] in stageids for r in rules))
    check('case-reqs',all(c['requirement'] in {r['id'] for r in requirements} for c in case_rows))
    check('all-stages-have-cases',all(any(c['stage']==s for c in case_rows) for s in stageids))
    check('all-required-cases-unrun',all(c['execution_status']=='NOT_RUN' for c in case_rows))
    check('software-not-claimed',status['software_status']=='NOT_IMPLEMENTED' and not status['public_release_authorized'])
    check('no-invented-stage-passes',all(s['status']=='NOT_STARTED' and not s['human_accepted'] for s in status['stages']))
    for i,s in enumerate(stages):
        check('prompt:'+s['id'],(ROOT/s['prompt_file']).is_file())
        check('readings:'+s['id'],all((ROOT/p).is_file() for p in s['spec_files']))
        check('predecessor:'+s['id'],s['predecessor']==(None if i==0 else f'S{i-1:02d}'))
        prompt=(ROOT/s['prompt_file']).read_text(encoding='utf-8')
        check('prompt-cases:'+s['id'],all(c['id'] in prompt for c in case_rows if c['stage']==s['id']))
    agents=(ROOT/'AGENTS.md').read_bytes()
    check('agents-size',len(agents)<8000,f'{len(agents)} bytes; intentionally below 8,000 bytes and the cited default instruction limit.')
    with (ROOT/'fixtures/cohort_clean.tsv').open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f,delimiter='\t'))
    ids={r['observation_id'] for r in rows};subjects={r['subject_id'] for r in rows}
    subject_of={r['observation_id']:r['subject_id'] for r in rows}
    check('cohort-known-counts',len(rows)==36 and len(ids)==36 and len(subjects)==18)
    check('cohort-two-visits',set(Counter(r['subject_id'] for r in rows).values())=={2})
    for name,expected_overlap in [('splits_clean.json',0),('splits_participant_overlap.json',18)]:
        plan=read_json('fixtures/'+name);tested=Counter()
        for fold in plan['folds']:
            tr=set(fold['train_ids']);te=set(fold['test_ids']);tested.update(te)
            check(name+':coverage:'+fold['fold_id'],tr|te==ids and not tr&te)
            overlap={subject_of[o] for o in tr}&{subject_of[o] for o in te}
            check(name+':participant-oracle:'+fold['fold_id'],len(overlap)==expected_overlap)
        check(name+':complete-cv',set(tested)==ids and set(tested.values())=={1})
    unknown=read_json('fixtures/splits_unknown_id.json')
    check('unknown-ID-fixture-intent',any(set(f['test_ids'])-ids for f in unknown['folds']))
    with (ROOT/'fixtures/features_shuffled.tsv').open(encoding='utf-8',newline='') as f:
        features=list(csv.DictReader(f,delimiter='\t'))
    check('features-complete-keys',{r['observation_id'] for r in features}==ids)
    check('features-really-shuffled',[r['observation_id'] for r in features]!=[r['observation_id'] for r in rows])
    check('features-formula-oracle',all(abs(float(r['feature_1'])-round((int(r['observation_id'].split('-')[1])%5)*.2+int(r['observation_id'].split('-')[2])*.01,4))<1e-12 for r in features))
    references={f'R{i:02d}' for i in range(1,25)}
    allspec='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'spec').glob('*.md'))
    used=set(re.findall(r'\bR\d{2}\b',allspec))
    check('reference-identifiers',used<=references,str(sorted(used)))
    idx=read_json('state/document_index.json')
    check('chapter-count',len(idx['sections'])==22)
    check('chapter-paths',all((ROOT/x['path']).is_file() for x in idx['sections']))
    master=ROOT/'NeuroCVguard_MASTER_SPEC.md'
    if master.exists():
        txt=master.read_text(encoding='utf-8')
        check('master-has-all-stages',all(s['title'] in txt for s in stages))
        check('master-has-all-cases',all(c['id'] in txt for c in case_rows))
        check('master-has-all-rules',all(r['id'] in txt for r in rules))
        check('master-code-fences-balanced',sum(1 for l in txt.splitlines() if l.startswith('```'))%2==0)
        check('no-chat-citation-tokens','\ue200cite' not in txt and '\ue200filecite' not in txt)
    else:
        check('master-exists',False)
    failed=[c for c in checks if not c['passed']]
    report={'scope':'Foundation document/schema/fixture consistency only. No NeuroCVguard implementation or application tests are validated here.','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'planned_application_acceptance_cases':len(case_rows),'application_tests_executed':0,'software_status':'NOT_IMPLEMENTED','checks':checks}
    out=ROOT/'qa/foundation_validation.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(report['scope'])
    print(f"Foundation checks: {len(checks)-len(failed)}/{len(checks)} passed; application tests executed: 0.")
    for f in failed: print('FAIL:',f['check'],f['detail'])
    return 1 if failed else 0

if __name__=='__main__':
    raise SystemExit(main())
