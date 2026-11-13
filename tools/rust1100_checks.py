#!/usr/bin/env python3
"""Cross-repository integrity and continuation regression tests. No reviewer authentication."""
from pathlib import Path
import copy,hashlib,importlib.util,json,re,shutil,tempfile
P=Path(__file__).resolve().parents[1];D=P.parent/'NativeWeave-Design'
spec=importlib.util.spec_from_file_location('v',P/'tools/validate_graphs.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def contracts(root):
    d=root.parent/'NativeWeave-Design';reg=json.loads((d/'docs/contracts/registry.json').read_text());errors=[]
    for c in reg['contracts']:
        p=c.get('spec_path');h=c.get('content_sha256')
        if p is None and h is None:continue
        if not isinstance(p,str) or not isinstance(h,str):errors.append(c['id']+':partial record');continue
        q=(d/p).resolve()
        if not q.is_relative_to(d.resolve()) or not q.is_file() or hashlib.sha256(q.read_bytes()).hexdigest()!=h:errors.append(c['id']+':hash/path')
    return errors
base=v.Validator(P).run();assert base['ok'],base['errors'];assert not contracts(P)
assert {'R01','R25','R27'}<=set(base['continuable']['research'])
assert not base['ready']['delivery'] and not base['continuable']['delivery']
assert base['accepted_contracts']==0
baseline=json.loads((P/'source-driven-baseline.json').read_text())
assert baseline['contract_registry_sha256']==hashlib.sha256((D/'docs/contracts/registry.json').read_bytes()).hexdigest()
allnodes={n['id']:n for k in ('research','documentation','delivery') for n in json.loads((P/(k+'-graph.json')).read_text())['nodes']}
for id,n in allnodes.items():
    s=(P/n['prompt']).read_text();assert 'Revision: **'+n['revision']+'**' in s,id
    assert hashlib.sha256(s.encode()).hexdigest()==n['packet_sha256'],id
    for c in n['contract_inputs']:assert c['id']+'@'+c['version'] in s,(id,c)
assert not allnodes['B04']['selection_required']
for id in ['B21','B22','B23','B24']:assert 'B04' in allnodes[id]['start_dependencies']+allnodes[id]['acceptance_dependencies'],id
assert 'B04原生PostgreSQL、B17' not in (P/'execution-policy.md').read_text()
results=[]
def case(name,mutate,check):
    with tempfile.TemporaryDirectory(prefix='nw1100-') as td:
        root=Path(td)/'Plan';shutil.copytree(P,root,ignore=shutil.ignore_patterns('.git','__pycache__'))
        shutil.copytree(D/'docs',Path(td)/'NativeWeave-Design/docs')
        mutate(root);r=v.Validator(root).run();assert check(root,r),(name,r['errors']);results.append({'case':name,'passed':True})
def graph(root,fn):
    p=root/'research-graph.json';g=json.loads(p.read_text());fn(g);p.write_text(json.dumps(g))
def tamper(root):
    p=root/'research-tasks/R01.md';p.write_text(p.read_text()+'tampered\n')
def fake(root):graph(root,lambda g:next(n for n in g['nodes'] if n['id']=='R01').update(status='accepted'))
def wait(root):
    def change(g):
        a=next(n for n in g['nodes'] if n['id']=='R01');b=next(n for n in g['nodes'] if n['id']=='R25')
        b['start_dependencies']=['R01'];b['dependency_pins']={'R01':a['revision']}
    graph(root,change)
def badspec(root):
    p=root.parent/'NativeWeave-Design/docs/platforms/build-package-release.md';p.write_text(p.read_text()+'tampered\n')
closed=lambda root,r:not r['ok'] and not any(r['ready'].values()) and not any(r['continuable'].values())
case('packet_tampering_closes_start_and_resume',tamper,closed)
case('partial_research_not_fake_accepted',fake,closed)
case('partial_dependency_does_not_unblock_dependent',wait,lambda root,r:r['ok'] and 'R25' not in r['continuable']['research'] and not r['ready']['delivery'])
case('proposed_spec_hash_mismatch_is_detected',badspec,lambda root,r:bool(contracts(root)))
# Check exact byte preservation separately from normalized subprocess capture hashes.
e=D/'docs/research/topics/R01/rust-1100-evidence';m=json.loads((e/'preservation.json').read_text())
for row in m['preserved_files']:assert hashlib.sha256((D/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
for osname in ['linux','windows']:
    r=json.loads((e/osname/'evidence/result.json').read_text());assert r['all_expected_results']
    assert hashlib.sha256((e/osname/'executed-stable_tests.rs').read_bytes()).hexdigest()==r['test_source_sha256']
    for cmd in r['commands']:
        for stream in ['stdout','stderr']:
            text=(e/osname/'evidence'/(cmd['name']+'.'+stream)).read_text()
            assert hashlib.sha256(text.encode()).hexdigest()==cmd[stream+'_sha256'],(osname,cmd['name'],stream)
report={'scope':'Structural/self-review evidence; not independent review or production acceptance','ok':True,'counts':base['counts'],'accepted_contracts':base['accepted_contracts'],'ready':base['ready'],'continuable':base['continuable'],'regressions':results,'packet_count':len(allnodes),'preserved_raw_files_verified':len(m['preserved_files']),'two_platform_rust_results_verified':True}
out=P/'verification/rust1100-checks.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(out.read_text())
