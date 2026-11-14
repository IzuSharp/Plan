#!/usr/bin/env python3
"""Keep the original English/acceptance gates at their exact accepted input pair.

The current API refinement is a semantic revision, not an English-only migration.
Nothing in this gate grants current acceptance or reruns native experiments.
"""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys
import tempfile

P=Path(__file__).resolve().parents[1]
D=P.parent/'NativeWeave-Design'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def git_bytes(root,commit,path):return subprocess.check_output(['git','show',commit+':'+path],cwd=root)

def verify_preservation():
    manifest=json.loads((P/'ledger/public-api-2026-11-14/prior-acceptance.json').read_bytes())
    assert manifest['product_implementation_authorized'] is False
    for row in manifest['files']:
        root=P if row['repository']=='Plan' else D
        raw=git_bytes(root,row['source_commit'],row['path'])
        assert sha(raw)==row['sha256']
        assert (P/row['snapshot_path']).read_bytes()==raw, row['snapshot_path']
    count=0
    for repository,prefixes in manifest['immutable_evidence_prefixes'].items():
        root=P if repository=='Plan' else D
        commit=manifest['sources'][repository]
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit],cwd=root,text=True).splitlines()
        for path in paths:
            if path.startswith(tuple(prefixes)):
                assert (root/path).read_bytes()==git_bytes(root,commit,path), ('historical evidence changed',repository,path)
                count+=1
    return manifest,count

def main():
    manifest,preserved=verify_preservation()
    output=P/'verification/public-api-history/current'
    output.mkdir(parents=True,exist_ok=True)
    commands=[('design-english','NativeWeave-Design',['tools/verify_english_translation.py']),
              ('plan-english','Plan',['tools/verify_english_translation.py']),
              ('english-contract-bindings','Plan',['tools/migrate_english_acceptance.py','verify-contracts']),
              ('english-task-bindings','Plan',['tools/migrate_english_acceptance.py','verify-tasks']),
              ('original-completion','Plan',['tools/verify_completion.py','--require-complete'])]
    created=[];rows=[]
    with tempfile.TemporaryDirectory(prefix='nw-public-api-history-') as temp:
        base=Path(temp)
        try:
            for repository,commit in manifest['accepted_history_pair'].items():
                root=P if repository=='Plan' else D
                target=base/repository
                subprocess.run(['git','worktree','add','--detach',str(target),commit],cwd=root,check=True,capture_output=True,timeout=60)
                created.append((root,target))
            for name,repository,args in commands:
                started=datetime.datetime.now(datetime.timezone.utc).isoformat()
                run=subprocess.run([sys.executable,*args],cwd=base/repository,capture_output=True,timeout=180)
                (output/(name+'.stdout')).write_bytes(run.stdout)
                (output/(name+'.stderr')).write_bytes(run.stderr)
                rows.append({'name':name,'repository':repository,'command':[sys.executable,*args],
                             'exit_code':run.returncode,'started_at_utc':started,
                             'stdout_sha256':sha(run.stdout),'stderr_sha256':sha(run.stderr),
                             'source_tool_sha256':sha((base/repository/args[0]).read_bytes())})
                if run.returncode:raise RuntimeError(name+': '+run.stderr[-4000:].decode(errors='replace'))
        finally:
            for root,target in reversed(created):
                subprocess.run(['git','worktree','remove','--force',str(target)],cwd=root,check=True,capture_output=True,timeout=60)
            report={'ok':len(rows)==len(commands) and all(r['exit_code']==0 for r in rows),
                    'pair':manifest['accepted_history_pair'],'preserved_original_records':preserved,
                    'scope':'Original complete translation and acceptance gates at their immutable accepted pair; current API semantics require separate actual review.',
                    'product_delivery_executed':False,'native_experiments_rerun':False,'checks':rows}
            (output/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'ok':True,'historical_checks':len(rows),'preserved_original_records':preserved}))

if __name__=='__main__':main()
