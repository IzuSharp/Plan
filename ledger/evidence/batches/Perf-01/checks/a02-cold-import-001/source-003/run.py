#!/usr/bin/env python3
"""Finite diagnostic only; compile once, preserve every fresh-process outcome."""
import datetime, hashlib, json, os, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/scratch/01c249676f47')
OUT = ROOT / 'perf01-evidence/diagnostic/a02-import-controls-003'
FIXTURE = ROOT / 'perf01-evidence/functional/before-A02-001/fixtures/libnw_a02_alpha.so'
DOTNET = Path('/workspace/scratch/58d2a6adf1c3/dotnet-sdk/dotnet')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path, value): path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    records=[]
    fixture_sha=sha(FIXTURE)
    save(OUT/'initial.json', {'start_utc':now(),'affinity':sorted(os.sched_getaffinity(0)), 'fixture_sha256':fixture_sha, 'performance_claim':False})
    def run(name, argv, timeout):
        start=now(); clock=time.monotonic()
        stdout=OUT/(name+'.stdout'); stderr=OUT/(name+'.stderr')
        with stdout.open('xb') as so, stderr.open('xb') as se:
            try:
                result=subprocess.run(argv,cwd=HERE,stdout=so,stderr=se,timeout=timeout,check=False)
                code=result.returncode; error=None
            except subprocess.TimeoutExpired as ex:
                code=None; error=type(ex).__name__
        row={'name':name,'command':[str(x) for x in argv],'cwd':str(HERE),'start_utc':start,'end_utc':now(),'elapsed_seconds':time.monotonic()-clock,'exit_code':code,'error':error,'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr),'affinity':sorted(os.sched_getaffinity(0))}
        records.append(row); save(OUT/'commands.json',records)
        print(json.dumps(row),flush=True)
        return code
    restore=[str(DOTNET),'restore','ImportRace.csproj','--locked-mode','-r','linux-x64','-p:PublishAot=true','-p:UseSharedCompilation=false','-nr:false','-m:1']
    publish=[str(DOTNET),'publish','ImportRace.csproj','-c','Release','-r','linux-x64','-p:PublishAot=true','--no-restore','-o',str(HERE/'aot'),'-p:UseSharedCompilation=false','-nr:false','-m:1']
    if run('restore',restore,120)!=0 or run('publish',publish,180)!=0: return 1
    for mode in ('borrowed','owned','owned-unlink'):
        run(mode,[str(HERE/'aot/ImportRace'),mode,str(FIXTURE),str(OUT/(mode+'-fixture')),'--require-aot'],45)
    if sha(FIXTURE)!=fixture_sha: raise RuntimeError('Original fixture changed')
    files=[HERE/name for name in ('Program.cs','ImportRace.csproj','global.json','packages.linux-x64.aot.lock.json','run.py')]+[HERE/'aot/ImportRace',OUT/'commands.json']
    save(OUT/'manifest.json',{'kind':'finite forced-overlap Native AOT callback ownership controls; no NativeWeave managed reference','completed_utc':now(),'performance_claim':False,'source_and_artifact_sha256':{str(p):sha(p) for p in files},'fixture_sha256':fixture_sha})
    return 0

if __name__=='__main__': raise SystemExit(main())
