# HISTORICAL one-shot importer for old fixed snapshots; current migration is tools/migrate_research_asset_refs.py.
# Do not use historical execution authorization as current policy.
"""Advance existing partial Research/Documentation tasks from actual evidence.
No new IDs, no accepted contracts, no delivery authorization shortcut.
"""
from pathlib import Path
import copy,hashlib,json,os,re,subprocess
P=Path.cwd();D=P.parent/'NativeWeave-Design';N=P.parent/'NativeWeave'
BASE='2ef12b8459e8f8905f7b288f9b58393714aedfaa';DESIGN='d4ad42df26ee9378817aa8ee94cd1853d66eb0ae';NATIVE='267364a440074a61e193cf33315f1b9d0fa8126b'
for root,sha in [(D,DESIGN),(N,NATIVE)]:assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==sha
for name in ['research-graph.json','documentation-graph.json','delivery-graph.json','source-driven-baseline.json','task-index.md']:
 assert (P/name).read_bytes()==subprocess.check_output(['git','show',BASE+':'+name]),'preimage drift: '+name
raw=json.loads((N/'verification/native-slices/manifest.json').read_text());verified=0
for record in raw['records']:
 for f in record['files']:
  q=(N/f['path']).resolve();assert q.is_relative_to(N.resolve())
  assert hashlib.sha256(q.read_bytes()).hexdigest()==f['sha256'],f['path'];verified+=1
assert sum(r['success'] for r in raw['records'])==6 and len(raw['records'])==8
assert not raw['independent_review'] and raw['not_an_experiment_rerun']
G={k:json.loads((P/f'{k}-graph.json').read_text()) for k in ['research','documentation','delivery']};old=copy.deepcopy(G)
nodes={n['id']:n for g in G.values() for n in g['nodes']}
reports={
 'R03':'docs/research/topics/R03/native-slice-validation.md',
 'R04':'docs/research/topics/R03/native-slice-validation.md',
 'R07':'docs/research/topics/R03/native-slice-validation.md',
 'R10':'docs/research/topics/R03/native-slice-validation.md',
 'R13':'docs/research/topics/R03/native-slice-validation.md',
 'R22':'docs/research/topics/R22/native-slice-validation.md',
 'R25':'docs/research/topics/R22/native-slice-validation.md',
 'R27':'docs/research/topics/R27/native-slice-validation.md',
 'R29':'docs/research/topics/R27/native-slice-validation.md',
 'D01':'docs/platforms/support-and-aot.md',
 'D02':'docs/contracts/abi-v0.1.md',
 'D07':'docs/contracts/buffer-v0.1.md'}
for id,path in reports.items():
 assert (D/path).exists(),path
 n=nodes[id];n['status']='partially_evidenced'
 ref='NativeWeave-Design:'+path
 n.setdefault('continuation_evidence',[]).append({'design_commit':DESIGN,'path':path,'native_evidence_commit':NATIVE,'evidence_manifest':'verification/native-slices/manifest.json','status':'partial_execution_or_authored_draft','independent_review':False})
 if id.startswith('R') and ref not in n.setdefault('initial_seed_refs',[]):n['initial_seed_refs'].append(ref)
 if id in ['R03','R22','R27'] and ref not in n['outputs']:n['outputs'].append(ref)
# Exact prompt/dependency revision propagation only where required, not a global rewrite.
affected=set(reports)
while True:
 more={id for id,n in nodes.items() if any(d in affected for d in n['start_dependencies']+n['acceptance_dependencies']) or any(d['task_id'] in affected for d in n['conditional_dependencies'])}
 if more<=affected:break
 affected|=more
oldnodes={n['id']:n for g in old.values() for n in g['nodes']}
for id in affected:
 v=nodes[id]['revision'].split('.');v[-1]=str(int(v[-1])+1);nodes[id]['revision']='.'.join(v)
for id,n in nodes.items():
 if id not in affected:continue
 n['dependency_pins']={d:nodes[d]['revision'] for d in n['start_dependencies']+n['acceptance_dependencies']}
 for d in n['conditional_dependencies']:d['revision']=nodes[d['task_id']]['revision']
 p=P/n['prompt'];s=p.read_text();previous=oldnodes[id]
 s=s.replace('Revision: **'+previous['revision']+'**','Revision: **'+n['revision']+'**',1)
 s=s.replace('State: **'+previous['status']+'**','State: **'+n['status']+'**',1)
 # Existing packets carry an exact dependency-revision sentence. Preserve every other section.
 deps=', '.join(d+'@'+v for d,v in n['dependency_pins'].items()) or '无'
 s=re.sub(r'精确依赖revision：[^。]*。','精确依赖revision：'+deps+'。',s)
 for d in n['conditional_dependencies']:
  before=next((x for x in previous['conditional_dependencies'] if x['task_id']==d['task_id']),None)
  if before:s=s.replace(d['task_id']+'@'+before['revision'],d['task_id']+'@'+d['revision'])
 if id in reports:
  s+='\n## Native slice execution checkpoint\n\nRead `'+reports[id]+'` at Design `'+DESIGN+'` and NativeWeave `verification/native-slices/manifest.json` at `'+NATIVE+'`. Reuse the actual Windows/Linux records; do not rerun successful fixtures merely to recover context. State is partial, not completed/accepted. Interop proves physical leases and real AOT/local NuGet; Database proves six native SQLite/binder cases; Server proves four native Service/Body cases. Preserve the first Database compile failure. Logical admission, full async retirement, PostgreSQL, clean Rust-free deployment and production acceptance remain separate obligations.\n'
 p.write_text(s);n['packet_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
for kind,g in G.items():
 if g!=old[kind]:(P/f'{kind}-graph.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
# Keep the existing index structure and update only status cells.
p=P/'task-index.md';s=p.read_text()
for id in reports:s=re.sub(r'(^\| '+id+r' \|[^\n]*\| )[^|\n]+( \|$)',r'\g<1>partially_evidenced\2',s,flags=re.M)
p.write_text(s)
p=P/'source-driven-baseline.json';b=json.loads(p.read_text())
b['plan_main']=BASE;b['design_main']='7759248e8c3bb37a99481f09c690d2c9f9b49248'
b['design_amendment_commit']=DESIGN;b['design_pr']=6
b['contract_registry_sha256']=hashlib.sha256((D/'docs/contracts/registry.json').read_bytes()).hexdigest()
b['native_slice_evidence_commit']=NATIVE;b['native_slice_pr']=1
b['review_status']='native_slice_followup_proposed_author_checked_independent_review_pending'
b['previous_merged_design_pr']=5;b['previous_merged_plan_pr']=2
b['task_revision_policy']='Only evidence-advanced packets and their actual task dependency revisions change; all other packet bytes remain unchanged.'
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
checkpoint={'plan_base':BASE,'design_main':b['design_main'],'design_followup':DESIGN,'native_evidence':NATIVE,'native_test_inputs':{'interop':'4a4adc883b80719d2a9b2bfb03be5ec86b543f3c','server':'5dd696725afe75f2b8b03b104c8275db50dcf2c7','database':'43e4fbcbe0417165c0f7df03507bfa1da8a53049'},'runs':{'interop':43363045559,'server_and_first_database_failure':43363994414,'corrected_database':43364366610,'preservation':43365053808},'partially_evidenced':sorted(reports),'changed_packets':sorted(affected),'unchanged_packets':114-len(affected),'raw_files_hash_verified':verified,'independent_review':False,'delivery_acceptance':False,'original_subagents':'six separately attributable reports not recovered','actual_interruption':'NativeWeave had two source files and no projects/consumer/runner/PR after old documentation PRs had already merged'}
q=P/'ledger/checkpoints/native-slices-2026-11-12.json';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps(checkpoint))
