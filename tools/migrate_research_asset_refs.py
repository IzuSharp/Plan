"""One-shot scoped Plan update after Design research-asset migration.
Historical execution inputs are retained; executable projects are not copied into Plan.
"""
from pathlib import Path
import copy,hashlib,json,re,subprocess
P=Path.cwd();D=P.parent/'NativeWeave-Design'
BASE='f6ed91dddba62b9eba246f2af56ca5b93cc2593b'
DESIGN='c7e123a74405a92dc3de1ef450355b08d1c05ceb'
OLD_NATIVE='267364a440074a61e193cf33315f1b9d0fa8126b'
assert subprocess.check_output(['git','-C',str(D),'rev-parse','HEAD'],text=True).strip()==DESIGN
for name in ['research-graph.json','documentation-graph.json','delivery-graph.json','source-driven-baseline.json']:
 assert (P/name).read_bytes()==subprocess.check_output(['git','show',BASE+':'+name]),'preimage drift '+name
mapping=json.loads((D/'verification/native-slices/migration-map.json').read_text())
assert mapping['source_head']==OLD_NATIVE and mapping['mapped_files']==139
for item in mapping['records']:
 assert hashlib.sha256((D/item['destination_path']).read_bytes()).hexdigest()==item['destination_sha256']
fresh=json.loads((D/'verification/native-slices/migration-results.json').read_text())
assert fresh['all_six_jobs_passed'] and len(fresh['records'])==6
for r in fresh['records']:
 for f in r['files']:assert hashlib.sha256((D/f['path']).read_bytes()).hexdigest()==f['sha256']
G={k:json.loads((P/(k+'-graph.json')).read_text()) for k in ('research','documentation','delivery')};old=copy.deepcopy(G)
nodes={n['id']:n for g in G.values() for n in g['nodes']};before={n['id']:n for g in old.values() for n in g['nodes']}
direct=set()
for id,n in nodes.items():
 for entry in n.get('continuation_evidence',[]):
  if entry.get('native_evidence_commit')!=OLD_NATIVE:continue
  entry['historical_native_evidence_commit']=entry.pop('native_evidence_commit')
  entry['historical_design_commit']=entry['design_commit']
  entry.update(design_commit=DESIGN,evidence_repository='IzuSharp/NativeWeave-Design',evidence_manifest='verification/native-slices/original-pr1/manifest.json',migration_map='verification/native-slices/migration-map.json',migration_results='verification/native-slices/migration-results.json')
  direct.add(id)
assert len(direct)==12
changed=set(direct)
while True:
 more={id for id,n in nodes.items() if any(x in changed for x in n['start_dependencies']+n['acceptance_dependencies']) or any(x['task_id'] in changed for x in n['conditional_dependencies'])}
 if more<=changed:break
 changed|=more
assert len(changed)==33 and not any(x.startswith(('A','B')) for x in changed)
for id in changed:
 parts=nodes[id]['revision'].split('.');parts[-1]=str(int(parts[-1])+1);nodes[id]['revision']='.'.join(parts)
for id in changed:
 n=nodes[id];prior=before[id]
 n['dependency_pins']={x:nodes[x]['revision'] for x in n['start_dependencies']+n['acceptance_dependencies']}
 for c in n['conditional_dependencies']:c['revision']=nodes[c['task_id']]['revision']
 p=P/n['prompt'];text=p.read_text()
 text=text.replace('Revision: **'+prior['revision']+'**','Revision: **'+n['revision']+'**',1)
 deps=', '.join(x+'@'+v for x,v in n['dependency_pins'].items()) or '无'
 text=re.sub(r'精确依赖revision：[^。]*。','精确依赖revision：'+deps+'。',text)
 for c in n['conditional_dependencies']:
  prev=next((x for x in prior['conditional_dependencies'] if x['task_id']==c['task_id']),None)
  if prev:text=text.replace(c['task_id']+'@'+prev['revision'],c['task_id']+'@'+c['revision'])
 if id in direct:
  marker='## Native slice execution checkpoint';assert text.count(marker)==1
  prefix,footer=text.split(marker)
  footer=footer.replace('d4ad42df26ee9378817aa8ee94cd1853d66eb0ae',DESIGN)
  footer=footer.replace('and NativeWeave `verification/native-slices/manifest.json` at `'+OLD_NATIVE+'`','and Design `verification/native-slices/original-pr1/manifest.json` at `'+DESIGN+'`')
  text=prefix+marker+footer+'\nCurrent phase: research/design/planning only. Read Design `experiments/native-slices/README.md`, `verification/native-slices/migration-map.json` and `migration-results.json`. Historical NativeWeave source/run identities remain provenance, not current write targets. New experiments belong in Design; do not execute A/B Delivery, write product code or merge product PR1. Its closure is allowed only after verified Design/Plan migration.\n'
 p.write_text(text);n['packet_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
for kind,g in G.items():
 if g!=old[kind]:(P/(kind+'-graph.json')).write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
assert G['delivery']==old['delivery']
p=P/'source-driven-baseline.json';b=json.loads(p.read_text())
b['prior_design_merge_commit']=b['design_merge_commit'];b['prior_validated_design_head']=b['validated_design_head']
b.update(design_main=DESIGN,design_merge_commit=DESIGN,design_amendment_commit='d3db57b900cdfcc62bde85eefbd55bfbed507dd0',validated_design_head='d3db57b900cdfcc62bde85eefbd55bfbed507dd0',plan_main=BASE,design_pr=7,review_status='research_asset_migration_author_checked_independent_review_pending',current_phase='research_design_planning',product_implementation_authorized=False,user_execution_authorization='Research, executable experiments in Design, detailed specifications and future Codex planning only. Earlier product execution scope is superseded. Do not execute formal A/B Delivery; product PR1 may only be closed after both migration PRs merge.',formal_delivery_eligibility_at_merge='No formal Delivery execution in this research-only phase, even if future technical prerequisites become satisfied.',research_asset_repository='IzuSharp/NativeWeave-Design',research_asset_commit=DESIGN,research_asset_root='experiments/native-slices',research_evidence_manifest='verification/native-slices/original-pr1/manifest.json',migration_map='verification/native-slices/migration-map.json',migration_results='verification/native-slices/migration-results.json')
b['historical_native_slice_evidence_commit']=b.pop('native_slice_evidence_commit');b['historical_native_slice_pr']=b.pop('native_slice_pr')
b['contract_registry_sha256']=hashlib.sha256((D/'docs/contracts/registry.json').read_bytes()).hexdigest()
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
# Current phase overrides earlier permissions; retain future execution/acceptance requirements.
p=P/'execution-policy.md';text=p.read_text();paras=text.split('\n\n')
assert '2026-11-12用户已授权' in paras[1]
paras[1]='本政策规定未来 Codex 的正式并行实施。当前用户已明确纠正为研究、详细设计和开发规划阶段：不执行任何正式 A/B Delivery，不向 NativeWeave 产品仓库写代码；真实实验仅写入 NativeWeave-Design。研究、实验、文档修订与符合条件的 Design/Plan 合并无需逐项确认。未来产品实施须用户另行进入实施阶段，并满足精确 accepted 契约、任务依赖和实施授权记录。'
text='\n\n'.join(paras)
text=text.replace('产品实施任务仍须自己的精确accepted契约、依赖与授权记录；这是真实技术门禁，不是要求用户再次批准。','这些只允许在 Design 中执行研究 fixture。当前不执行产品任务；未来 Codex 实施另按阶段授权、精确 accepted 契约、依赖与验收记录推进。')
p.write_text(text)
phase='''# Current phase: research, design and future Codex planning

The latest user instruction supersedes previous product-execution authorization.
Research prototypes, Cargo/.NET projects, native tests, Actions and raw evidence live
in IzuSharp/NativeWeave-Design. Plan maintains the existing34 Research,32 Documentation
and48 candidate Delivery tasks and detailed future implementation instructions. Do not
copy executable projects here. Do not execute A/B Delivery or write NativeWeave product
source. The only product-repository mutation authorized now is closing PR1 AFTER the
verified Design and Plan migration has merged. Do not merge PR1 or delete its history.

Keep current and historical evidence identities distinct. The current Design asset
commit/map/results are in source-driven-baseline.json. Historical checkpoint records
and one-shot repair scripts remain historical inputs, not permission to resume product
writes. New experiments and documentation may proceed in parallel under existing R/D
IDs. Self-review and CI are not independent review; research merges do not accept product
contracts. Future Codex Worktrees retain exact file ownership, local dependencies,
platform/AOT/fault/performance acceptance and a separately authorized phase transition.
'''
(P/'CURRENT-PHASE.md').write_text(phase)
for name in ['README.md','AGENTS.md','research-policy.md','documentation-policy.md']:
 p=P/name;text=p.read_text();text='> **Current phase:** research and detailed design only; see [CURRENT-PHASE.md](CURRENT-PHASE.md). Research experiments and current evidence belong in NativeWeave-Design. No product write or A/B Delivery execution is authorized.\n\n'+text
 if name=='AGENTS.md':
  text=text.replace('旧“仅规划、当前全面不授权执行”指的是历史启动轮，不覆盖此次授权。','此段历史授权已由 CURRENT-PHASE.md 及最新用户指令收窄：只允许 Design 内的研究实验与详细设计，不允许正式产品实施。')
 p.write_text(text)
# Mark old one-shot importer as historical; do not rewrite old evidence records.
p=P/'tools/native_slices_checkpoint.py';text=p.read_text();p.write_text('# HISTORICAL one-shot importer for old fixed snapshots; current migration is tools/migrate_research_asset_refs.py.\n# Do not use historical execution authorization as current policy.\n'+text)
checkpoint={'plan_base':BASE,'design_merge':DESIGN,'design_reviewed_head':'d3db57b900cdfcc62bde85eefbd55bfbed507dd0','source_native_pr':1,'source_native_head':OLD_NATIVE,'source_native_main':'658ed6a410783de356a7b9b2cd6601336fff5148','mapped_assets':139,'byte_exact_assets':137,'adapted_drivers':2,'original_evidence_files':112,'new_design_evidence_files':sum(len(r['files']) for r in fresh['records']),'new_design_run':fresh['run_id'],'direct_tasks':sorted(direct),'changed_packets':sorted(changed),'unchanged_packets':114-len(changed),'delivery_graph_changed':False,'product_implementation_authorized':False,'original_pr_close_state':'awaiting verified Plan merge; never merge or delete history','independent_review':False}
p=P/'ledger/checkpoints/research-assets-migration.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps(checkpoint,indent=2))
