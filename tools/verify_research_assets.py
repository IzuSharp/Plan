"""Verify preserved migration history and the current pair independently.

The migration's 33/81 packet assertion belongs to its merged Plan snapshot.
Later authorized research edits must not rewrite that historical checkpoint or
masquerade as reruns of its native experiments. No product code is executed.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

P=Path(__file__).resolve().parents[1]
D=P.parent/'NativeWeave-Design'

def read(root,path):return json.loads((root/path).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def git_bytes(root,commit,path):
    assert re.fullmatch('[0-9a-f]{40}',commit),commit
    return subprocess.check_output(['git','-C',str(root),'show',commit+':'+path])

b=read(P,'source-driven-baseline.json')
assert b['current_phase']=='research_design_planning' and b['product_implementation_authorized'] is False
assert b['research_asset_repository']=='IzuSharp/NativeWeave-Design'
design_head=subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()
assert design_head==b['design_merge_commit']
assert sha(D/'docs/contracts/registry.json')==b['contract_registry_sha256']

# The original assets and raw evidence remain byte-exact at their Design paths.
m=read(D,b['migration_map']);assert m['mapped_files']==139 and len(m['records'])==139
for r in m['records']:
    assert sha(D/r['destination_path'])==r['destination_sha256']
    if r['byte_exact']:assert r['source_sha256']==r['destination_sha256']
assert sum(bool(r['byte_exact']) for r in m['records'])==137
paths={r['source_path']:r['destination_path'] for r in m['records']}
old=read(D,b['research_evidence_manifest']);n_old=0
for r in old['records']:
    for f in r['files']:
        assert sha(D/paths[f['path']])==f['sha256'];n_old+=1
fresh=read(D,b['migration_results']);n_new=0
assert fresh['all_six_jobs_passed'] and len(fresh['records'])==6
for r in fresh['records']:
    for f in r['files']:
        assert sha(D/f['path'])==f['sha256'];n_new+=1
assert (n_old,n_new)==(112,90)

# Preserve the exact checkpoint, including its then-pending PR closure statement.
checkpoint_path='ledger/checkpoints/research-assets-migration.json'
checkpoint=read(P,checkpoint_path)
migration_plan=b['research_asset_plan_commit']
assert migration_plan=='04c2f043c0ec60a2d49dd3ca8ea4ad1c8c888d89'
assert (P/checkpoint_path).read_bytes()==git_bytes(P,migration_plan,checkpoint_path)
assert checkpoint['design_merge']==b['research_asset_commit']
subprocess.run(['git','-C',str(D),'merge-base','--is-ancestor',b['research_asset_commit'],design_head],check=True)
historical_changed=[];historical_ids=set();current_count=0
for kind in ('research','documentation','delivery'):
    graph_path=kind+'-graph.json'
    migration_graph=json.loads(git_bytes(P,migration_plan,graph_path))
    for node in migration_graph['nodes']:
        historical_ids.add(node['id'])
        contents=git_bytes(P,migration_plan,node['prompt'])
        assert hashlib.sha256(contents).hexdigest()==node['packet_sha256']
        if contents!=git_bytes(P,checkpoint['plan_base'],node['prompt']):historical_changed.append(node['id'])
    if kind=='delivery':
        assert git_bytes(P,migration_plan,graph_path)==git_bytes(P,checkpoint['plan_base'],graph_path)
    current=read(P,graph_path)
    assert {n['id'] for n in current['nodes']}=={n['id'] for n in migration_graph['nodes']}
    for node in current['nodes']:
        current_count+=1
        assert sha(P/node['prompt'])==node['packet_sha256']
        if kind=='delivery':assert node['implementation_authorization']['status']=='not_authorized'
        for evidence in node.get('continuation_evidence',[]):
            if evidence.get('historical_native_evidence_commit'):
                assert evidence['evidence_repository']=='IzuSharp/NativeWeave-Design'
                assert evidence['design_commit']==b['research_asset_commit']
                assert evidence['historical_native_evidence_commit']==checkpoint['source_native_head']
                assert (D/evidence['evidence_manifest']).exists()
assert sorted(historical_changed)==checkpoint['changed_packets'] and len(historical_changed)==33
assert len(historical_ids)==current_count==114

report={
    'ok':True,
    'scope':'Preserved migration history plus current research-pair integrity; no new native execution or acceptance',
    'plan_checked_commit':subprocess.check_output(['git','-C',str(P),'rev-parse','HEAD'],text=True).strip(),
    'plan_worktree_changes_included':bool(subprocess.check_output(['git','-C',str(P),'status','--porcelain'],text=True).strip()),
    'design_checked_commit':design_head,
    'historical_migration_plan_commit':migration_plan,
    'historical_migration_design_commit':b['research_asset_commit'],
    'mapped_assets':139,'byte_exact_assets':137,'adapted_drivers':2,
    'old_evidence_files':n_old,'new_design_evidence_files':n_new,
    'historical_changed_packets':33,'historical_unchanged_packets':81,
    'historical_delivery_graph_unchanged':True,'historical_checkpoint_unchanged':True,
    'current_packets_verified':current_count,'research_only':True,'independent_review':False,
}
(P/'verification/research-assets-integrity-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
