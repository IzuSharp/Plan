#!/usr/bin/env python3
"""Close manifests and receipt-bound coverage; no new measurement or archive copy."""
import datetime
import hashlib
import json
import os
from pathlib import Path
from restore_archive04 import bind_alias_sources

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dump(p,v):
    t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(v,indent=2)+'\n');os.replace(t,p)

def main():
    base=json.loads((HERE/'selection.json').read_text());extra=json.loads((HERE/'selection-addendum-01.json').read_text())
    assert sha(HERE/'selection.json')==extra['baseSelectionSha256']
    selected={f['path']:f for selection in (base,extra) for group in selection['groups'].values() for f in group}
    entries=[];members={};checks=[]
    def check(name,condition,details=None):
        checks.append({'name':name,'passed':bool(condition),'details':details})
        if not condition:raise AssertionError(name)
    names=list(base['groups'])+list(extra['groups'])
    for name in names:
        receipt=json.loads((HERE/(name+'-receipt.json')).read_text());entry=receipt['archive']
        check('verified-'+name,receipt.get('passed') and receipt['verification'].get('passed'))
        manifest=json.loads((HERE/'raw-archives'/entry['expandedFileManifest']).read_text())
        for f in manifest['files']:
            check('member-unique:'+f['path'],f['path'] not in members)
            members[f['path']]={**f,'archive':name}
        entries.append(entry)
    check('selected-and-expanded-member-set-equal',set(members)==set(selected))
    for path,f in selected.items():
        check('selected-size:'+path,members[path]['bytes']==f['stamp'][0])
        if 'expectedSha256' in f:
            check('selected-expected-sha:'+path,members[path]['sha256']==f['expectedSha256'])
    check('physical-db-and-future-paths-excluded',not any('/postgres-data/' in p or '/local-preference-options-01/' in p or 'hostpull' in p.lower() or p.endswith(('.sqlite','.sqlite-wal','.sqlite-shm','.db','.db-wal','.db-shm')) for p in members))
    aliases=json.loads((HERE/'restore-alias-manifest.json').read_text())['aliases'];by_dest={a['destination']:a for a in aliases}
    bindings=bind_alias_sources(members,aliases)
    consumer_names=['tail06-sqlite','tail06-postgresql','tail06diag-before-sqlite','tail06diag-before-postgresql','tail06diag-tail-sqlite','tail06diag-tail-postgresql']
    for name in consumer_names:
        rel='consumers/'+name+'/korda-workload';receipt=json.loads((ROOT/rel/'build-receipt.json').read_text())
        check('receipt-in-payload:'+name,members[rel+'/build-receipt.json']['sha256']==sha(ROOT/rel/'build-receipt.json'))
        for filename,key in [('DbPerf.Korda','executableSha256'),('DbPerf.Korda.dbg','debugSha256')]:
            check('actual-output:'+name+'/'+filename,members[rel+'/out/'+filename]['sha256']==receipt[key])
        check('actual-provider-package:'+name,members[str(Path(receipt['package']).relative_to(ROOT))]['sha256']==receipt['packageSha256'])
        for filename,expected in receipt['nativeImages'].items():
            check('actual-native:'+name+'/'+filename,members[rel+'/out/'+filename]['sha256']==expected)
        for filename,expected in receipt['sources'].items():
            check('actual-harness-source:'+name+'/'+filename,members[rel+'/'+filename]['sha256']==expected)
        for filename,expected in receipt['generatedSources'].items():
            check('actual-generated-source:'+name+'/'+filename,members[rel+'/generated/'+filename]['sha256']==expected)
    all_receipts=[ROOT/'consumers'/n/'korda-workload/build-receipt.json' for n in consumer_names]
    all_receipts += [ROOT/'consumers'/n/t/'build-receipt.json' for n in ['baseline-final-sqlite','baseline-final-postgresql'] for t in ['korda-workload','dapper-workload']]
    all_receipts += [ROOT/'consumers'/n/'korda-workload/build-receipt.json' for n in ['integrated05-sqlite','integrated05-postgresql']]
    dependencies=[]
    for path in all_receipts:
        receipt=json.loads(path.read_text())
        for package,dep in receipt['packages'].items():
            raw=str(Path(dep['rawArchivePath']).relative_to(ROOT));alias=by_dest.get(raw)
            if raw in members:
                source=members[raw];mode='selected exact raw-archive path'
            elif alias is not None:
                source=alias;mode='checked exact feed-to-cache copy from '+alias.get('sourcePublishedDependency','current selected payload')
            else:
                raise AssertionError('Unresolved raw package path: '+raw)
            check('raw-package:'+str(path.relative_to(ROOT))+':'+package,source['sha256']==dep['rawArchiveSha256'])
            dependencies.append({'consumerReceipt':str(path.relative_to(ROOT)),'package':package,'rawPath':raw,'sha256':dep['rawArchiveSha256'],'resolution':mode,'source':alias['source'] if alias else raw})
    retirement=json.loads((ROOT/'experiments/recovery/tail06-fixture-retirement-01.json').read_text())
    for x in retirement['receipts']:
        rel=str(Path(x['receipt']).relative_to(ROOT))
        check('closed-fixture-receipt:'+rel,members[rel]['sha256']==x['sha256'])
    for group in ['independent-ordinary-results-review-01','independent-mixed-gate-review-01','coordinator-readonly-01']:
        path='experiments/tail-completion-06/'+group+'/README.md'
        check('closed-review:'+group,path in members)
    for snapshot in json.loads((HERE/'source-snapshots.json').read_text())['snapshots']:
        check('source-sole-prerequisite:'+snapshot['worktree'],len(snapshot['bundlePrerequisites'])==1 and snapshot['bundlePrerequisites'][0].startswith('-2ea67ce1902f330679c3ebff4d6d5733be20f69c '))
    index={'task':'DB-Exec-Parity-01','format':'ordered concatenated xz tar parts','archives':entries,
        'dependencies':base['archiveDependencies'],'sourcePrerequisite':'2ea67ce1902f330679c3ebff4d6d5733be20f69c in archives02',
        'scope':'Closed rejected tail06 evidence and explicit raw-package reproducibility gaps. No HostPull candidate; no long measurement.',
        'noNewPerformanceCredit':True,'remotePublication':False}
    dump(HERE/'raw-archives/index.json',index)
    dump(HERE/'expanded-files-all.json',{'task':'DB-Exec-Parity-01','fileCount':len(members),'expandedBytes':sum(x['bytes'] for x in members.values()),'files':sorted(members.values(),key=lambda x:x['path']),'noOriginalFileDeleted':True})
    dump(HERE/'package-path-closure-final.json',{'task':'DB-Exec-Parity-01','consumerReceipts':len(all_receipts),'rawPackageReferences':len(dependencies),'distinctRawPaths':len({d['rawPath'] for d in dependencies}),
        'aliasSourceBindings':bindings,'dependencies':dependencies,'scope':'12 actual comparison consumer build-receipt raw package paths. Rebuilding still requires the separately pinned SDK/system/previous source prerequisites; this is not a full toolchain installation snapshot.','passed':True})
    result={'task':'DB-Exec-Parity-01','finishedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'checks':checks,'archives':len(entries),'parts':sum(len(e['parts']) for e in entries),
        'members':len(members),'expandedBytes':sum(x['bytes'] for x in members.values()),'compressedBytes':sum(e['archive']['bytes'] for e in entries),
        'freeBytesObserved':os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize,'indexSha256':sha(HERE/'raw-archives/index.json'),
        'expandedManifestSha256':sha(HERE/'expanded-files-all.json'),'packagePathClosureSha256':sha(HERE/'package-path-closure-final.json'),
        'noCanonicalOrRoundtripCopy':True,'noNewPerformanceCredit':True,'remotePublication':False}
    dump(HERE/'archive-completion-validation.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}|{'checks':len(checks)}))

if __name__=='__main__':main()
