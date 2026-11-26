#!/usr/bin/env python3
"""Retain a bounded local host observation; do not certify exclusive hardware."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,platform,time
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():p.error('Existing evidence is immutable; use a fresh output')
s=a.source.resolve(strict=True)/'benchmarks/db-perf/run.py';spec=importlib.util.spec_from_file_location('local_observer',s);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def read(path):
 try:return Path(path).read_text()
 except OSError as e:return {'errno':e.errno,'type':type(e).__name__}
def sample():return {'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'monotonicNs':time.monotonic_ns(),'stat':read('/proc/stat'),'loadavg':read('/proc/loadavg'),'meminfo':read('/proc/meminfo')}
x={'schemaVersion':1,'scope':'Task-local observation before serial measurement. All known local builds/tests are required to be stopped by the operator. Tool PID namespaces prevent a system-wide cross-session process proof. No exclusive physical host, no invisible cgroup quota qualification.','uname':platform.uname()._asdict(),'observerAffinity':sorted(os.sched_getaffinity(0)),'assignedAffinity':{'client':'0-3','postgres':'4-7','observer':'8'},'observerSource':{'path':str(s),'sha256':hashlib.sha256(s.read_bytes()).hexdigest()},'cpuinfo':read('/proc/cpuinfo'),'cgroup':module.cgroup_snapshot(),'idleSamples':[],'taskOverrides':{k:os.environ.get(k) for k in ['LD_PRELOAD','DOTNET_PROCESSOR_COUNT','COMPlus_ThreadPool_ForceMinWorkerThreads']}}
for i in range(12):
 x['idleSamples'].append(sample())
 if i!=11:time.sleep(.5)
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
print(json.dumps({'path':str(a.output.resolve()),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'samples':len(x['idleSamples']),'cgroupAvailable':x['cgroup']['available']}))
