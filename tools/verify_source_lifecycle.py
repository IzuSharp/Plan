#!/usr/bin/env python3
"""Read-only verification of the paired lifecycle research and candidate packet delta.

This invokes the Design integrity verifier, which reads preserved source/logs;
it does not rebuild or rerun the native experiments and grants no acceptance.
"""
from collections import Counter
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import subprocess
import sys

P=Path(__file__).resolve().parents[1]
D=P.parent/'NativeWeave-Design'

def read(path):return json.loads(path.read_bytes())
def digest(raw):return hashlib.sha256(raw).hexdigest()
def git_bytes(root,commit,path):
    assert re.fullmatch('[0-9a-f]{40}',commit),commit
    parts=PurePosixPath(path)
    assert not parts.is_absolute() and '..' not in parts.parts
    return subprocess.check_output(['git','-C',str(root),'show',commit+':'+path])

def verify_ci_manifest(checkpoint,design_root):
    expected=checkpoint['native_research_ci']
    path='verification/source-lifecycle/results.json'
    assert expected['manifest_path']==path
    entries=[entry for entry in checkpoint['design_input_files'] if entry['path']==path]
    assert len(entries)==1
    raw=(design_root/path).read_bytes()
    assert digest(raw)==expected['manifest_sha256']==entries[0]['sha256']
    assert len(raw)==entries[0]['bytes']
    manifest=json.loads(raw)
    assert manifest['tested_source_commit']==expected['tested_source_commit']
    assert str(manifest['run_id'])==expected['run_id']
    assert manifest['successful_jobs']==4 and manifest['preserved_raw_files']==56
    assert manifest['distinct_tests']==12 and manifest['platform_test_executions']==24
    assert manifest['formal_contract_accepted'] is manifest['product_delivery_executed'] is False
    return manifest

def verify_ci_result(manifest,result):
    assert result['passed'] is True
    assert result['tested_source_commit']==manifest['tested_source_commit']
    assert result['raw_files']==manifest['preserved_raw_files']
    assert result['platform_test_executions']==manifest['platform_test_executions']
    assert result['accepted_contracts']==0 and result['product_delivery_executed'] is False

def main():
    baseline=read(P/'source-driven-baseline.json')
    checkpoint=read(P/baseline['source_lifecycle_checkpoint'])
    assert checkpoint['record_kind']=='research_source_lifecycle_plan_pair'
    assert baseline['current_phase']=='research_design_planning'
    assert baseline['product_implementation_authorized'] is checkpoint['product_implementation_authorized'] is False
    head=subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()
    assert head==baseline['design_merge_commit']==checkpoint['design_commit']
    registry_bytes=(D/'docs/contracts/registry.json').read_bytes()
    assert digest(registry_bytes)==baseline['contract_registry_sha256']==checkpoint['contract_registry_sha256']
    assert registry_bytes==git_bytes(D,head,'docs/contracts/registry.json')
    registry={c['id']:c for c in json.loads(registry_bytes)['contracts']}
    assert all(c['status']=='proposed' for c in registry.values())
    for expected in checkpoint['contracts']:
        contract=registry[expected['id']]
        assert all(contract[key]==expected[key] for key in ('version','spec_path','content_sha256'))
        assert digest((D/contract['spec_path']).read_bytes())==contract['content_sha256']
    for entry in checkpoint['design_input_files']:
        path=(D/entry['path']).resolve()
        assert path.is_relative_to(D.resolve())
        raw=path.read_bytes()
        assert len(raw)==entry['bytes'] and digest(raw)==entry['sha256'],entry['path']
        assert raw==git_bytes(D,head,entry['path']),entry['path']

    manifest=verify_ci_manifest(checkpoint,D)
    # Design owns source/checkout identity (including explicit LF -> CRLF), raw
    # logs, command outcomes and independent scoped review archives.
    command=[sys.executable,str(D/'verification/source-lifecycle/verify.py')]
    run=subprocess.run(command,capture_output=True,text=True,check=True)
    design_result=json.loads(run.stdout)
    verify_ci_result(manifest,design_result)

    prior=checkpoint['plan_base'];all_ids=set();changed=[];counts={};state_counts={}
    declared={item['id']:item for item in checkpoint['changed_packets']}
    for kind in ('research','documentation','delivery'):
        path=kind+'-graph.json'
        old={n['id']:n for n in json.loads(git_bytes(P,prior,path))['nodes']}
        current=read(P/path)['nodes'];counts[kind]=len(current);state_counts[kind]=dict(Counter(n['status'] for n in current))
        assert set(old)=={n['id'] for n in current}
        for node in current:
            nid=node['id'];all_ids.add(nid);previous=old[nid]
            for key in ('status','acceptance_evidence','independent_reviewers','outputs','write_scopes'):
                assert node[key]==previous[key],(nid,key)
            if kind=='delivery':
                assert node['implementation_authorization']==previous['implementation_authorization']
                assert node['implementation_authorization']['status']=='not_authorized'
            contents=(P/node['prompt']).read_bytes()
            assert digest(contents)==node['packet_sha256']
            before=git_bytes(P,prior,node['prompt'])
            if contents!=before:
                changed.append(nid);record=declared[nid]
                assert node['revision']!=previous['revision']
                assert record=={'id':nid,'path':node['prompt'],'before_revision':previous['revision'],'after_revision':node['revision'],
                                'before_sha256':digest(before),'after_sha256':digest(contents)}
            else:
                assert node==previous,(nid,'unexpected graph-only change')
    assert counts==checkpoint['task_counts']=={'research':34,'documentation':32,'delivery':48}
    assert state_counts==checkpoint['state_counts']
    assert set(changed)==set(declared) and len(changed)==checkpoint['changed_packet_count']
    assert all_ids-set(changed)==set(checkpoint['unchanged_packet_ids'])
    assert checkpoint['accepted_contract_count']==0 and checkpoint['native_research_ci']['product_native_aot_evidence'] is False

    report={'ok':True,'scope':'Current paired research integrity and candidate packet bindings; no native rerun, product execution or acceptance',
            'plan_base':prior,'plan_checked_commit':subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip(),
            'worktree_changes_included':bool(subprocess.check_output(['git','-C',str(P),'status','--porcelain'],text=True).strip()),
            'design_commit':head,'registry_sha256':digest(registry_bytes),'design_input_files_verified':len(checkpoint['design_input_files']),
            'design_integrity_result':design_result,'design_integrity_command':command,'design_integrity_stdout_sha256':digest(run.stdout.encode()),
            'counts':counts,'state_counts':state_counts,'changed_packets':len(changed),'unchanged_packets':len(all_ids)-len(changed),
            'all_task_statuses_preserved':True,'acceptance_arrays_preserved':True,'delivery_authorizations_preserved':True,
            'accepted_contracts':0,'independent_review':False}
    (P/'verification/source-lifecycle-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
