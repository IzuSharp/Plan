#!/usr/bin/env python3
"""Archive only closed rejected pull-local07 bytes with unchanged streaming engine."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PRIOR=HERE.parent/'supplement-04'
BASE='2ea67ce1902f330679c3ebff4d6d5733be20f69c'
TIP='645cfa5f184d65a67fa71455a5f7271ee8469309'
FIXED_SHA='b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c'
assert hashlib.sha256((HERE/'streaming_archive.py').read_bytes()).hexdigest()==FIXED_SHA
spec=importlib.util.spec_from_file_location('reviewed_streaming_engine05',HERE/'streaming_archive.py')
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
engine.HERE,engine.ROOT,engine.OUTPUT=HERE,ROOT,HERE
engine.NOTES=[
    'Closed rejected pull-local07 only: real two ordinary NuGet consumers; successful finite correctness02 and failed correctness01 identity; actual ELF branch evidence; twelve ordinary processes with the independent rejection and 05 gap interpretation. No mixed or long measurement is added.',
    'The user cancelled every 1800-second final/before long run. All original credit boundaries and failed identities remain; archive creation creates no performance credit.',
    'Prerequisite archives01/02/03/04 remain required: baseline/Dapper/toolchain, retained integrated05 and native build identities, reviewed observer/helpers, and raw compiler package closure respectively.',
    'Four native alias destinations reuse byte- and mode-identical prior archive04 native images: ordinary outputs from ordinary-consumers06, correctness outputs from correctness-negative06. Two unique new nupkg feeds are included once and restore their exact raw cache aliases.',
    'All physical PostgreSQL and SQLite/WAL/SHM fixtures, shared package/cache trees, bytecode and reproducible compiler duplicates are excluded. Actual new ELF/debug, generated C#, unique packages, retained consumer IL/response metadata, raw and failures remain.',
    'Exactly two older stopped fixtures were separately retired after direct wait4 proof, published raw identity checks, 22 synthetic controls and independent review. All 84 surrounding raw files and twelve retained configs remain. Other eleven old proposals, four pg_ctl-only exclusions and the new07 fixture were not retired.',
    'Source snapshot is one thin bundle and net patch from integrated05 2ea67ce to 645cfa5, including all four candidate/test-correction commits. No whole repository copy.',
    'Source sealing is cooperative plus per-file size/mtime/inode checks before and after reads, not a global atomic filesystem snapshot. Each member has full SHA256/bytes/mode, every part and complete compressed/tar stream is checked.',
    'Single-thread lzma on CPU8 nice19. No full canonical compressed file, full tar, or extraction roundtrip copy is materialized. No original source/raw/actual artifact or part is deleted.',
    'CI transport review and exact cancelled job log are evidence only. No new CI performance execution or workflow trigger is performed by this archiver.',
    'Only root publishes tree/commit/ref and performs remote readback. This builder may prepare archives and blob payloads but never changes a branch or publication ref.',
]

def write(path,value):
    engine.dump(path,value)

def capture_sources():
    worktree=ROOT/'worktrees/Korda-pull-local07'
    for name in ('Korda-pull-local07','Korda-pull-local07-sqlite','Korda-pull-local07-postgresql'):
        p=ROOT/'worktrees'/name
        assert engine.git(p,'rev-parse','HEAD').decode().strip()==TIP
        assert not engine.git(p,'status','--porcelain=v1','--untracked-files=no').strip()
    output=HERE/'source-snapshots/Korda-pull-local07'
    output.mkdir(parents=True,exist_ok=False)
    patch=output/'from-2ea.patch'
    patch.write_bytes(engine.git(worktree,'diff','--binary','--full-index',BASE,TIP))
    bundle=output/'commits.bundle'
    command=['git','-C',str(worktree),'-c','pack.threads=1','bundle','create',str(bundle),'HEAD','^'+BASE]
    result=subprocess.run(command,capture_output=True,text=True,check=True)
    verified=subprocess.run(['git','-C',str(worktree),'bundle','verify',str(bundle)],capture_output=True,text=True,check=True)
    (output/'bundle-verification.txt').write_text(verified.stdout+verified.stderr)
    changed=[]
    for name in filter(None,engine.git(worktree,'diff','--name-only','-z',BASE,TIP).decode().split('\0')):
        data=engine.git(worktree,'show',TIP+':'+name)
        changed.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    commits=engine.git(worktree,'rev-list','--reverse',BASE+'..'+TIP).decode().splitlines()
    assert len(commits)==4 and commits[-1]==TIP
    assert engine.git(worktree,'rev-parse','HEAD').decode().strip()==TIP
    assert not engine.git(worktree,'status','--porcelain=v1','--untracked-files=no').strip()
    item={'headCommit':TIP,'tree':engine.git(worktree,'rev-parse',TIP+'^{tree}').decode().strip(),'prerequisiteCommit':BASE,'includedCommits':commits,'changedFiles':changed,'bundleCommand':command,'bundleBytes':bundle.stat().st_size,'bundleSha256':engine.sha(bundle),'patchBytes':patch.stat().st_size,'patchSha256':engine.sha(patch),'verificationPassed':True,'bundleCreateStdout':result.stdout,'bundleCreateStderr':result.stderr,'restore':'Restore archive02 Korda source snapshot first; in that repository verify the thin bundle, fetch its HEAD, then add a detached worktree at the recorded commit. The net binary patch is a second review route.'}
    write(output/'identity.json',item)
    write(HERE/'source-snapshots.json',{'task':'DB-Exec-Parity-01','snapshots':[item],'sameHeadWorktrees':['Korda-pull-local07','Korda-pull-local07-sqlite','Korda-pull-local07-postgresql'],'wholeRepositoryCopied':False})

def prepare_aliases(plan):
    prior_map={x['path']:x for x in json.loads((PRIOR/'path-to-sha-final.json').read_text())['files']}
    refs=[];members={}
    target=HERE/'dependency-manifests';target.mkdir(exist_ok=False)
    for group in ('ordinary-consumers06','correctness-negative06'):
        rel='raw-archives/'+group+'/expanded-file-manifest.json'
        path=PRIOR/rel;expected=prior_map[rel]
        assert engine.sha(path)==expected['sha256'] and path.stat().st_size==expected['bytes']
        name='archives04-'+group+'.json';copy=target/name;copy.write_bytes(path.read_bytes())
        assert engine.sha(copy)==expected['sha256']
        refs.append({'file':'dependency-manifests/'+name,'sha256':expected['sha256'],'sourceCommit':'ded73d7cd90cb692bea554c5e780df0ca9e05e3f','sourceArchivePath':rel,'gitBlobSha':expected['sha']})
        members[name]={x['path']:x for x in json.loads(path.read_text())['files']}
    aliases=[]
    for planned in plan['restoreAliasDraft']:
        a={k:planned[k] for k in ('source','destination','sha256','bytes')}
        dest=ROOT/a['destination'];a['mode']=dest.stat().st_mode&0o777
        assert a['mode'] in (0o644,0o744)
        if a['destination'].startswith('experiments/pull-local-07/correctness-02/publish/'):
            a['source']=a['destination'].replace('experiments/pull-local-07/correctness-02/','experiments/tail-completion-06/correctness-01/')
            a['dependencyManifest']='archives04-correctness-negative06.json'
        elif a['source'].startswith('consumers/tail06-'):
            a['dependencyManifest']='archives04-ordinary-consumers06.json'
        if 'dependencyManifest' in a:
            m=members[a['dependencyManifest']][a['source']]
            assert (m['bytes'],m['sha256'],m['mode'])==(a['bytes'],a['sha256'],a['mode'])
            a['sourcePublishedDependency']='archives04'
        aliases.append(a)
    write(target/'index.json',{'manifests':refs,'sourcePublicationReceipt':'observations/recovery/archive04-remote-readback-01/receipt.json','sourcePublicationCommit':'ded73d7cd90cb692bea554c5e780df0ca9e05e3f'})
    write(HERE/'restore-alias-manifest.json',{'task':'DB-Exec-Parity-01','aliases':aliases,'mode':'Exact SHA/bytes and explicit 0644/0744; independently byte-copied inode, no differing overwrite','sourceModesMatchDestinations':True,'originalCacheTreesArchived':False,'scope':'Four prior native images at matching byte/mode identity and two unique current feed packages; dependencies must be restored first'})

def prepare():
    assert not (HERE/'selection.json').exists()
    state=json.loads((ROOT/'experiments/pull-local-07/ordinary-screen-01/resume.json').read_text())
    decision=json.loads((ROOT/'experiments/pull-local-07/independent-ordinary-results-review-01/decision.json').read_text())
    author=json.loads((ROOT/'experiments/pull-local-07/implementation-resume.json').read_text())
    retirement=json.loads((ROOT/'experiments/recovery/legacy-pg-retirement-subset07/actual-01/receipt.json').read_text())
    assert state['passed'] and state['stage']=='completed'
    assert decision['ordinaryScreenPassed'] and decision['recommendation']=='reject candidate; retain integrated05' and decision['successfulOperations']==24576
    assert author['authorArtifactsSealed'] and author['sourceCommit']==TIP
    assert retirement['passed'] and len(retirement['deleted'])==2 and retirement['rawUnchanged']
    assert (ROOT/'experiments/pull-local-07/continuation10-independent-review-01/receipt.json').is_file()
    plan=json.loads((HERE/'selection-final-plan.json').read_text())
    capture_sources()
    prepare_aliases(plan)
    groups={n:[ROOT/f['path'] for f in files] for n,files in plan['groups'].items()}
    groups['source-snapshots07']=[p for p in (HERE/'source-snapshots').rglob('*') if p.is_file()]+[HERE/'source-snapshots.json']
    selected={}
    for name,paths in groups.items():
        selected[name]=[]
        for path in sorted(paths):
            assert path.is_file() and not path.is_symlink() and path.resolve()==path
            relative=str(path.relative_to(ROOT))
            assert '/postgres-data/' not in relative and not relative.endswith(('.db','.sqlite','.sqlite-wal','.sqlite-shm'))
            selected[name].append({'path':relative,'stamp':engine.stamp(path)})
    all_paths=[x['path'] for files in selected.values() for x in files]
    assert len(all_paths)==len(set(all_paths))
    aliases=json.loads((HERE/'restore-alias-manifest.json').read_text())['aliases']
    assert all(a['source'] in all_paths for a in aliases if 'dependencyManifest' not in a)
    assert all(a['destination'] not in all_paths for a in aliases)
    selection={'task':'DB-Exec-Parity-01','createdUtc':engine.utc(),'root':str(ROOT),'stage':'frozen','groups':selected,'excludedPaths':{n:plan['exclusions'] for n in selected},'dereferencedSymlinks':{n:[] for n in selected},'notes':engine.NOTES,'noNewPerformanceCredit':True,'remotePublication':False,'totalFiles':len(all_paths),'expandedBytes':sum(x['stamp'][0] for fs in selected.values() for x in fs),'reviewedStreamingVerifierSha256':FIXED_SHA,'candidateRejected':True,'selectedProductCommit':BASE,'longMeasurementsCanceled':True}
    write(HERE/'selection.json',selection)
    write(HERE/'source-identity.json',{'builderSha256':engine.sha(Path(__file__)),'selectorSha256':engine.sha(HERE/'select_closed07.py'),'reviewedStreamingVerifierSha256':FIXED_SHA,'aliasHelperSha256':engine.sha(HERE/'restore_artifact_aliases.py'),'restoreWrapperSha256':engine.sha(HERE/'restore_archive05.py'),'selectionSha256':engine.sha(HERE/'selection.json')})
    write(HERE/'resume.json',{'task':'DB-Exec-Parity-01','updatedUtc':engine.utc(),'stage':'selection-frozen','selectionSha256':engine.sha(HERE/'selection.json'),'compressionStarted':False,'remotePublication':False})
    print(json.dumps({'frozen':True,'groups':{n:{'files':len(fs),'expandedBytes':sum(x['stamp'][0] for x in fs)} for n,fs in selected.items()},'aliases':len(aliases),'selectionSha256':engine.sha(HERE/'selection.json')}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','build'))
    parser.add_argument('--name')
    args=parser.parse_args()
    os.sched_setaffinity(0,{8});os.nice(19)
    if args.action=='prepare':prepare()
    else:
        assert args.name and args.name in json.loads((HERE/'selection.json').read_text())['groups']
        assert not (HERE/(args.name+'-receipt.json')).exists()
        engine.build(args.name)
