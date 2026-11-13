"""Offline cross-repository verification; does not execute or copy product code."""
from pathlib import Path
import hashlib,json,subprocess
P=Path.cwd();D=P.parent/'NativeWeave-Design'
def read(root,path):return json.loads((root/path).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
b=read(P,'source-driven-baseline.json')
assert b['current_phase']=='research_design_planning' and b['product_implementation_authorized'] is False
assert b['research_asset_repository']=='IzuSharp/NativeWeave-Design'
assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()==b['design_merge_commit']
assert sha(D/'docs/contracts/registry.json')==b['contract_registry_sha256']
m=read(D,b['migration_map']);assert m['mapped_files']==139
for r in m['records']:
 assert sha(D/r['destination_path'])==r['destination_sha256']
 if r['byte_exact']:assert r['source_sha256']==r['destination_sha256']
paths={r['source_path']:r['destination_path'] for r in m['records']}
old=read(D,b['research_evidence_manifest']);n_old=0
for r in old['records']:
 for f in r['files']:assert sha(D/paths[f['path']])==f['sha256'];n_old+=1
fresh=read(D,b['migration_results']);n_new=0
assert fresh['all_six_jobs_passed'] and len(fresh['records'])==6
for r in fresh['records']:
 for f in r['files']:assert sha(D/f['path'])==f['sha256'];n_new+=1
assert (n_old,n_new)==(112,90)
checkpoint=read(P,'ledger/checkpoints/research-assets-migration.json')
assert checkpoint['design_merge']==b['research_asset_commit']
changed=[]
for kind in ('research','documentation','delivery'):
 for node in read(P,kind+'-graph.json')['nodes']:
  contents=(P/node['prompt']).read_bytes();assert hashlib.sha256(contents).hexdigest()==node['packet_sha256']
  prior=subprocess.check_output(['git','show',checkpoint['plan_base']+':'+node['prompt']])
  if contents!=prior:changed.append(node['id'])
  if kind=='delivery':assert node['implementation_authorization']['status']=='not_authorized'
  for e in node.get('continuation_evidence',[]):
   if e.get('historical_native_evidence_commit'):
    assert e['evidence_repository']=='IzuSharp/NativeWeave-Design'
    assert e['design_commit']==b['research_asset_commit']
    assert (D/e['evidence_manifest']).exists()
assert sorted(changed)==checkpoint['changed_packets'] and len(changed)==33
assert (P/'delivery-graph.json').read_bytes()==subprocess.check_output(['git','show',checkpoint['plan_base']+':delivery-graph.json'])
report={'ok':True,'plan_checked_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'design_merge':b['design_merge_commit'],'mapped_assets':139,'old_evidence_files':n_old,'new_design_evidence_files':n_new,'changed_packets':33,'unchanged_packets':81,'delivery_graph_unchanged':True,'research_only':True,'independent_review':False}
(P/'verification/research-assets-migration-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
