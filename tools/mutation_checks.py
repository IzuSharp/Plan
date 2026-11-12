#!/usr/bin/env python3
"""Narrow negative checks for graph corruption and false acceptance gates."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import tempfile
import shutil
import sys

PLAN=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validator',PLAN/'tools/validate_graphs.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)


def change_graph(root,name,fn):
 p=root/(name+'-graph.json');d=json.loads(p.read_text());fn(d);p.write_text(json.dumps(d,ensure_ascii=False))


def base_copy(dst):
 bundle=dst/'bundle';shutil.copytree(PLAN,bundle/'Plan',ignore=shutil.ignore_patterns('__pycache__'))
 source=PLAN.parent/'NativeWeave-Design/docs/contracts/registry.json'
 target=bundle/'NativeWeave-Design/docs/contracts/registry.json';target.parent.mkdir(parents=True);target.write_bytes(source.read_bytes())
 return bundle/'Plan'


def run_case(name,mutate,expected):
 with tempfile.TemporaryDirectory(prefix='nativeweave-graph-check-') as td:
  root=base_copy(Path(td));mutate(root);result=v.Validator(root).run()
  codes={e['code'] for e in result['errors']}
  passed=not result['ok'] and bool(codes & set(expected)) and not any(result['ready'].values())
  return {'case':name,'passed':passed,'expected_any_error':expected,'actual_errors':sorted(codes),'ready_fail_closed':not any(result['ready'].values())}


def cycle(root):
 def mutate(d):
  d['nodes'][0]['start_dependencies']=['R02'];d['nodes'][0]['dependency_pins']={'R02':'0.1.0'}
  d['nodes'][1]['start_dependencies']=['R01'];d['nodes'][1]['dependency_pins']={'R01':'0.1.0'}
 change_graph(root,'research',mutate)


def missing(root):
 def mutate(d):d['nodes'][0]['start_dependencies']=['R999'];d['nodes'][0]['dependency_pins']={'R999':'0.1.0'}
 change_graph(root,'research',mutate)


def overlap(root):
 def mutate(d):d['nodes'][1]['write_scopes']=d['nodes'][0]['write_scopes'];d['nodes'][1]['outputs']=d['nodes'][0]['outputs']
 change_graph(root,'research',mutate)


def stale_prompt(root):
 p=root/'research-tasks/R01.md';p.write_text(p.read_text()+'\nChanged after review.\n')


def fake_contract(root):
 p=root.parent/'NativeWeave-Design/docs/contracts/registry.json';d=json.loads(p.read_text());c=d['contracts'][0];c['status']='accepted';c['evidence']=[{'manifest_path':'Plan:missing.json','sha256':'0'*64}];c['reviews']=[{'manifest_path':'Plan:missing-review.json','sha256':'0'*64}];p.write_text(json.dumps(d))


def oversized_output(root):
 def mutate(d):d['nodes'][0]['write_scopes']=['NativeWeave:src/Only/'];d['nodes'][0]['outputs']=['NativeWeave:src/']
 change_graph(root,'research',mutate)


def pin_drift(root):
 def mutate(d):d['nodes'][1]['dependency_pins']['A01']='9.9.9'
 change_graph(root,'delivery',mutate)


def accept_state(state):
 return lambda root: change_graph(root,'research',lambda d:d['nodes'][0].update(status=state))


def duplicate(root):
 change_graph(root,'research',lambda d:d['nodes'].append(deepcopy(d['nodes'][0])))


cases=[
 ('cycle',cycle,['DEPENDENCY_CYCLE']),
 ('missing_dependency',missing,['MISSING_DEPENDENCY']),
 ('duplicate_id',duplicate,['DUPLICATE_ID']),
 ('shared_write_scope',overlap,['WRITE_SCOPE_CONFLICT']),
 ('unowned_parent_output',oversized_output,['OUTPUT_NOT_OWNED']),
 ('task_packet_changed',stale_prompt,['HASH_MISMATCH']),
 ('dependency_version_drift',pin_drift,['DEPENDENCY_VERSION']),
 ('forged_accepted_contract',fake_contract,['HASH_REQUIRED','FILE_MISSING']),
]+[(f'empty_evidence_{s}',accept_state(s),['EVIDENCE_REQUIRED','INDEPENDENT_REVIEW_REQUIRED']) for s in sorted(v.TERMINAL)]
results=[run_case(*c) for c in cases]
baseline=v.Validator(PLAN).run()
report={'scope':'Graph safety gate tests only; not NativeWeave product verification','baseline_ok':baseline['ok'],'results':results,'all_passed':baseline['ok'] and all(x['passed'] for x in results)}
out=PLAN/'verification/mutation-checks.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(0 if report['all_passed'] else 1)
