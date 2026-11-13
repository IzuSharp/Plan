#!/usr/bin/env python3
"""Read-only PR6/PR8 history verification, independent of later packet changes.

The original record_logical_admission.py and its output remain historical. This
does not rerun native/AOT tests or require today's graph to equal the old six-file delta.
"""
from pathlib import Path
import hashlib,json,re,subprocess

P=Path(__file__).resolve().parents[1];D=P.parent/'NativeWeave-Design'
PLAN='886fec7e6c702372e3b5f8dee2c85f039844b462'
DESIGN='3767f3c932ebf95bd82f6ed1c9bafc9eec1c5b1e'

def digest(raw):return hashlib.sha256(raw).hexdigest()
def git_bytes(root,commit,path):
    assert re.fullmatch('[0-9a-f]{40}',commit)
    return subprocess.check_output(['git','-C',str(root),'show',commit+':'+path])
def historical(path):return json.loads(git_bytes(D,DESIGN,path))

def main():
    baseline=json.loads((P/'source-driven-baseline.json').read_bytes())
    assert baseline['logical_admission_plan_commit']==PLAN
    assert baseline['logical_admission_study']['design_commit']==DESIGN
    assert baseline['product_implementation_authorized'] is False
    head=subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()
    assert head==baseline['design_merge_commit']
    subprocess.run(['git','-C',str(D),'merge-base','--is-ancestor',DESIGN,head],check=True)
    checkpoint_path='ledger/checkpoints/logical-admission-r07.json'
    raw=(P/checkpoint_path).read_bytes();assert raw==git_bytes(P,PLAN,checkpoint_path)
    checkpoint=json.loads(raw);assert checkpoint['design_merge']==DESIGN
    assert checkpoint['plan_base']=='04c2f043c0ec60a2d49dd3ca8ea4ad1c8c888d89'
    # Preserve both the one-shot initializer and its original successful check record.
    for path in ('tools/record_logical_admission.py','verification/logical-admission-checks.json','verification/logical-admission-obligations.md'):
        assert (P/path).read_bytes()==git_bytes(P,PLAN,path),path

    reports=[];raw_files=set()
    for path,run_id in [('verification/logical-admission/primary-results.json','43373306474'),
                        ('verification/logical-admission/results.json','43374127432')]:
        old=git_bytes(D,DESIGN,path);assert (D/path).read_bytes()==old
        report=json.loads(old);assert report['run_id']==run_id and report['both_platforms_passed'] is True
        for record in report['records']:
            result=record['result']
            assert result['success'] is True and result['managed_assertions_per_execution']==653 and result['positive_gate_rounds_per_execution']==64
            for source,sha in result['source_files'].items():
                assert digest(git_bytes(D,DESIGN,source))==sha,source
            for entry in record['files']:
                assert entry['path'] not in raw_files;raw_files.add(entry['path'])
                assert digest((D/entry['path']).read_bytes())==entry['sha256'],entry['path']
        reports.append(report)
    assert len(raw_files)==checkpoint['verified_raw_files']==64
    for source in historical('verification/logical-admission/source-review.json'):
        assert digest((D/source['excerpt_path']).read_bytes())==source['excerpt_sha256']
    primary=reports[0]
    assert digest((D/primary['source_review']['path']).read_bytes())==primary['source_review']['sha256']
    closure=historical('docs/traceability/research-asset-closure.json')
    assert closure['state']=='closed' and closure['merged'] is False
    assert closure['unchanged_main']=='658ed6a410783de356a7b9b2cd6601336fff5148'

    changed=[];count=0
    for kind in ('research','documentation','delivery'):
        path=kind+'-graph.json';graph=json.loads(git_bytes(P,PLAN,path))
        for node in graph['nodes']:
            count+=1;packet=git_bytes(P,PLAN,node['prompt'])
            assert digest(packet)==node['packet_sha256']
            if packet!=git_bytes(P,checkpoint['plan_base'],node['prompt']):changed.append(node['id'])
        if kind=='delivery':assert git_bytes(P,PLAN,path)==git_bytes(P,checkpoint['plan_base'],path)
    assert count==114 and sorted(changed)==checkpoint['changed_packets'] and len(changed)==6
    assert checkpoint['unchanged_packet_count']==108 and checkpoint['formal_delivery_executed'] is False
    result={'ok':True,'scope':'Historical PR6/PR8 source/log preservation only; no current packet delta assertion, no rerun or acceptance',
            'historical_plan_commit':PLAN,'historical_design_commit':DESIGN,'current_design_commit':head,
            'primary_run':'43373306474','incidental_run':'43374127432','verified_raw_files':64,
            'historical_changed_packets':6,'historical_unchanged_packets':108,'historical_delivery_graph_unchanged':True,
            'historical_checkpoint_and_record_preserved':True,'independent_review':False,'product_execution_authorized':False}
    (P/'verification/logical-admission-history-checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
