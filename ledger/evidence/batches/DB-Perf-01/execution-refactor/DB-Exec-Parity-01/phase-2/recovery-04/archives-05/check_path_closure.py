#!/usr/bin/env python3
"""Bind actual build identities to checked current members and prior package bytes."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PRIOR=HERE.parent/'supplement-04'
current=json.loads((HERE/'expanded-all-files.json').read_text())
members={x['path']:x for x in current['files']}
aliases={x['destination']:x for x in json.loads((HERE/'restore-alias-manifest.json').read_text())['aliases']}
prior_map={x['path']:x for x in json.loads((PRIOR/'path-to-sha-final.json').read_text())['files']}
rel='raw-archives/compiler-package-inputs06/expanded-file-manifest.json'
raw=(PRIOR/rel).read_bytes();reference=prior_map[rel]
assert len(raw)==reference['bytes'] and hashlib.sha256(raw).hexdigest()==reference['sha256']
prior_compiler={x['path']:x for x in json.loads(raw)['files']}
(HERE/'compiler-package-dependency-manifest.json').write_bytes(raw)
checks=[]

def check(name,path,expected,source=None):
    if isinstance(path,Path):path=str(path.relative_to(ROOT)) if path.is_absolute() else str(path)
    records=source if source is not None else members
    actual=records.get(path)
    if actual is None:raise ValueError('Missing path closure: '+path)
    assert actual['sha256']==expected,(path,actual['sha256'],expected)
    checks.append({'name':name,'path':path,'sha256':expected,'passed':True,'source':'prior-published-compiler' if source is prior_compiler else 'restore-alias' if source is aliases else 'current-checked-member'})

for provider in ('sqlite','postgresql'):
    base=ROOT/f'consumers/pull-local07-{provider}/korda-workload'
    b=json.loads((base/'build-receipt.json').read_text());v=json.loads((base/'binding-verification.json').read_text())
    assert b['buildCompleted'] and b['exitCode']==0 and v['passed']
    check(provider+' build receipt',base/'build-receipt.json',v['buildReceiptSha256'])
    check(provider+' preparation',base/'preparation.json',b['preparationSha256'])
    check(provider+' actual ELF',base/'out/DbPerf.Korda',b['executableSha256'])
    check(provider+' actual DBG',base/'out/DbPerf.Korda.dbg',b['debugSha256'])
    check(provider+' unique feed',Path(b['package']),b['packageSha256'])
    for name,sha in b['sources'].items():check(provider+' actual source',base/name,sha)
    for name,sha in b['generatedSources'].items():check(provider+' actual generated source',base/'generated'/name,sha)
    for name,sha in b['nativeImages'].items():check(provider+' native restored alias',base/'out'/name,sha,aliases)
    for name,pkg in b['packages'].items():
        path=Path(pkg['rawArchivePath'])
        check(provider+' raw package '+name,path,pkg['rawArchiveSha256'],aliases if name.startswith('Korda.') else prior_compiler)

correct=ROOT/'experiments/pull-local-07/correctness-02'
d=json.loads((correct/'receipt.json').read_text())
assert d['completed'] and d['runtimeCorrectnessPassed'] and d['managedCommit']=='645cfa5f184d65a67fa71455a5f7271ee8469309'
for key in ('executable','symbols'):check('finite correctness '+key,Path(d[key]['path']),d[key]['sha256'])
check('finite correctness generated manifest',correct/'generated-sources.json',d['generatedSourcesManifestSha256'])
for provider,a in d['nativeAssets'].items():check('finite correctness native '+provider,Path(a['publishedPath']),a['sha256'],aliases)

out={'task':'DB-Exec-Parity-01','passed':all(x['passed'] for x in checks),'checks':checks,'checkCount':len(checks),'currentFiles':len(members),'aliasDestinations':len(aliases),'priorCompilerManifest':{'publishedCommit':'ded73d7cd90cb692bea554c5e780df0ca9e05e3f','path':rel,'bytes':reference['bytes'],'sha256':reference['sha256'],'gitBlobSha':reference['sha']},'scope':'Actual source/generated/ELF/DBG/feed identities checked against fully streamed current payload; raw compiler identities matched to archive04 verified published members without rehashing those large prior packages. SDK/server/old05/Dapper prerequisites remain in documented earlier archives.','noNewMeasurement':True,'noNewPayloadCopy':True}
(HERE/'package-path-closure-05.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
