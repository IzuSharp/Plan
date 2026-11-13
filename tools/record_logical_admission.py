"""Integrate/check one research study using existing task IDs; never start Delivery."""
from pathlib import Path
import copy,hashlib,json,subprocess,sys
P=Path.cwd();D=P.parent/'NativeWeave-Design'
BASE='04c2f043c0ec60a2d49dd3ca8ea4ad1c8c888d89';DESIGN='3767f3c932ebf95bd82f6ed1c9bafc9eec1c5b1e'
def j(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()==DESIGN
primary=j(D/'verification/logical-admission/primary-results.json');latest=j(D/'verification/logical-admission/results.json')
assert primary['run_id']=='43373306474' and latest['run_id']=='43374127432'
raw_count=0
for report in (primary,latest):
 assert report['both_platforms_passed']
 for record in report['records']:
  result=record['result'];assert result['success'] and result['managed_assertions_per_execution']==653 and result['positive_gate_rounds_per_execution']==64
  for path,digest in result['source_files'].items():assert sha(D/path)==digest,path
  for f in record['files']:assert sha(D/f['path'])==f['sha256'];raw_count+=1
assert raw_count==64
for source in j(D/'verification/logical-admission/source-review.json'):
 assert sha(D/source['excerpt_path'])==source['excerpt_sha256']
assert sha(D/primary['source_review']['path'])==primary['source_review']['sha256']
closure=j(D/'docs/traceability/research-asset-closure.json')
assert closure['state']=='closed' and closure['merged'] is False and closure['unchanged_main']=='658ed6a410783de356a7b9b2cd6601336fff5148'
checkpoint=P/'ledger/checkpoints/logical-admission-r07.json'
if '--check' not in sys.argv:
 assert not checkpoint.exists(),'already integrated; run --check'
 G={k:j(P/(k+'-graph.json')) for k in ('research','documentation','delivery')};old=copy.deepcopy(G)
 for k in G:assert (P/(k+'-graph.json')).read_bytes()==subprocess.check_output(['git','show',BASE+':'+k+'-graph.json'])
 nodes={n['id']:n for g in G.values() for n in g['nodes']};oldnodes={n['id']:n for g in old.values() for n in g['nodes']}
 direct={'R07','D04'};affected=set(direct)
 for id in direct:
  nodes[id]['status']='partially_evidenced'
  nodes[id].setdefault('continuation_evidence',[]).append({'design_commit':DESIGN,'path':'docs/research/topics/R07/logical-admission.md','evidence_repository':'IzuSharp/NativeWeave-Design','evidence_manifest':'verification/logical-admission/primary-results.json','run_id':'43373306474','scope':'synchronous logical admission only','independent_review':False})
 while True:
  more={id for id,n in nodes.items() if any(x in affected for x in n['start_dependencies']+n['acceptance_dependencies']) or any(x['task_id'] in affected for x in n['conditional_dependencies'])}
  if more<=affected:break
  affected|=more
 assert not any(x.startswith(('A','B')) for x in affected)
 for id in affected:
  v=nodes[id]['revision'].split('.');v[-1]=str(int(v[-1])+1);nodes[id]['revision']='.'.join(v)
 import re
 for id in affected:
  n=nodes[id];prior=oldnodes[id];n['dependency_pins']={x:nodes[x]['revision'] for x in n['start_dependencies']+n['acceptance_dependencies']}
  for c in n['conditional_dependencies']:c['revision']=nodes[c['task_id']]['revision']
  p=P/n['prompt'];text=p.read_text().replace('Revision: **'+prior['revision']+'**','Revision: **'+n['revision']+'**',1).replace('State: **'+prior['status']+'**','State: **'+n['status']+'**',1)
  deps=', '.join(x+'@'+v for x,v in n['dependency_pins'].items()) or '无'
  text=re.sub(r'精确依赖revision：[^。]*。','精确依赖revision：'+deps+'。',text)
  for c in n['conditional_dependencies']:
   prev=next((x for x in prior['conditional_dependencies'] if x['task_id']==c['task_id']),None)
   if prev:text=text.replace(c['task_id']+'@'+prev['revision'],c['task_id']+'@'+c['revision'])
  if id in direct:text+='\n## Executed logical-admission research input\n\nRead Design `docs/research/topics/R07/logical-admission.md` and `verification/logical-admission/primary-results.json` at `'+DESIGN+'`, and Plan `verification/logical-admission-obligations.md`. Windows/Linux normal+AOT each passed653 assertions and64 guided rounds. Preserve the SafeHandle-only negative control; distinguish business admission, physical lifetime, native mutation and async retirement. No product task is authorized. The study resolves this bounded local design question, not complete C-LIFETIME acceptance. Continue remaining parent/child, GC/finalizer, mutable and async checks rather than rerunning unchanged successful scenarios.\n'
  p.write_text(text);n['packet_sha256']=sha(p)
 for k,g in G.items():
  if g!=old[k]:(P/(k+'-graph.json')).write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
 assert G['delivery']==old['delivery']
 p=P/'task-index.md';s=p.read_text();s=re.sub(r'(^\| D04 \|[^\n]*\| )[^|\n]+( \|$)',r'\g<1>partially_evidenced\2',s,flags=re.M);p.write_text(s)
 p=P/'source-driven-baseline.json';b=j(p)
 b['prior_design_merge_commit']=b['design_merge_commit'];b['prior_validated_design_head']=b['validated_design_head']
 b.update(design_main=DESIGN,design_merge_commit=DESIGN,design_amendment_commit='523a2f6543d3a8770cb3379f8fd7001abd6d8233',validated_design_head='523a2f6543d3a8770cb3379f8fd7001abd6d8233',plan_main=BASE,design_pr=8,contract_registry_sha256=sha(D/'docs/contracts/registry.json'),logical_admission_study={'design_commit':DESIGN,'report':'docs/research/topics/R07/logical-admission.md','evidence':'verification/logical-admission/primary-results.json','future_obligations':'verification/logical-admission-obligations.md','primary_run':'43373306474','scope':'research only; no formal Delivery execution'})
 assert b['product_implementation_authorized'] is False and b['current_phase']=='research_design_planning'
 p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
 # Historical migration snapshot stays pinned even as current Design research advances.
 p=P/'tools/verify_research_assets.py';s=p.read_text()
 s=s.replace("checkpoint['design_merge']==b['design_merge_commit']","checkpoint['design_merge']==b['research_asset_commit']")
 s=s.replace("e['design_commit']==b['design_merge_commit']","e['design_commit']==b['research_asset_commit']")
 p.write_text(s)
 p=P/'README.md';s=p.read_text();p.write_text(s+'\n## Detailed logical-admission research input\n\nSee [future Codex acceptance supplement](verification/logical-admission-obligations.md) for existing A03/A20/A06/A07/B11/B16/B17/B20 steps and missing verification, based on executed R07/D04 research. This is planning detail, not permission to implement product code. The current Design pin and historical migration pin remain separate in `source-driven-baseline.json`.\n')
 record={'plan_base':BASE,'design_merge':DESIGN,'direct_tasks':sorted(direct),'changed_packets':sorted(affected),'unchanged_packet_count':114-len(affected),'primary_run':'43373306474','incidental_run':'43374127432','verified_raw_files':raw_count,'future_delivery_tasks_clarified':['A03','A06','A07','A20','B11','B16','B17','B20'],'formal_delivery_executed':False,'delivery_graph_unchanged':True,'contract_acceptance_changed':False,'migration_asset_commit':b['research_asset_commit']}
 checkpoint.write_text(json.dumps(record,indent=2)+'\n')
record=j(checkpoint);b=j(P/'source-driven-baseline.json')
assert b['design_merge_commit']==DESIGN and sha(D/'docs/contracts/registry.json')==b['contract_registry_sha256']
assert b['product_implementation_authorized'] is False
subprocess.run(['git','-C',str(D),'merge-base','--is-ancestor',b['research_asset_commit'],DESIGN],check=True)
changed=[]
for k in ('research','documentation','delivery'):
 for n in j(P/(k+'-graph.json'))['nodes']:
  assert sha(P/n['prompt'])==n['packet_sha256']
  if (P/n['prompt']).read_bytes()!=subprocess.check_output(['git','show',BASE+':'+n['prompt']]):changed.append(n['id'])
assert sorted(changed)==record['changed_packets']
assert (P/'delivery-graph.json').read_bytes()==subprocess.check_output(['git','show',BASE+':delivery-graph.json'])
result={'ok':True,'checked_plan_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'design_merge':DESIGN,'verified_raw_files':raw_count,'changed_packets':len(changed),'unchanged_packets':114-len(changed),'independent_review':False,'product_execution_authorized':False}
(P/'verification/logical-admission-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
