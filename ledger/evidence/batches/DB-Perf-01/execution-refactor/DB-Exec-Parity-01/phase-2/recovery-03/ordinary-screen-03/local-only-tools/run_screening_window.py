#!/usr/bin/env python3
"""Run the six selected comparison groups in one exclusive local window."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1];out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
def now():return datetime.now(timezone.utc).isoformat()
def exe(family,provider,route='korda'):
    return root/f'consumers/{family}-{provider}/{route}-workload/out/DbPerf.{route.capitalize()}'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
workerd=['numeric:1:prepared','text:32:prepared','text:100:prepared','text:1000:prepared',
         'early-stop:32:prepared','wide:32:prepared','optional-filter:32:dynamic','related:32:prepared']
jobs=[]
for provider in ['sqlite','postgresql']:
    jobs.append(('workerd-'+provider,provider,exe('baseline-final',provider),exe('workerd03',provider),exe('baseline-final',provider,'dapper'),workerd))
jobs.append(('codec-postgresql','postgresql',exe('baseline-final','postgresql'),exe('codec03','postgresql'),exe('baseline-final','postgresql','dapper'),
             ['numeric:32:prepared','money:1:prepared','money:32:prepared','money:1000:prepared','wide:32:prepared','customer-totals:32:prepared']))
jobs.append(('sqliteprepare-sqlite','sqlite',exe('baseline-final','sqlite'),exe('sqliteprepare03','sqlite'),exe('baseline-final','sqlite','dapper'),
             ['numeric:1:prepared','text:32:prepared','text:1000:prepared','wide:32:prepared']))
for provider in ['sqlite','postgresql']:
    parent=root/'experiments/relations-recovery-03/ordinary'
    jobs.append(('relations-'+provider,provider,parent/f'baseline/{provider}/consumer/out/DbPerf.Korda',
                 parent/f'candidate/{provider}/consumer/out/DbPerf.Korda',None,['related:32:prepared','union-all:32:prepared']))
record={'task':'DB-Exec-Parity-01','startedUtc':now(),'scope':'Exclusive serial local ordinary candidate A/B; all peers acknowledge no build/compression/SQL/sampling. Root can read small source/evidence files.',
        'clientCpus':'0-3','serverCpus':'4-7','observerCpus':'8','availableCpus':sorted(os.sched_getaffinity(0)),
        'runtimeKnobs':'defaults','finalCellCredit':False,'driverSha256':sha(__file__),'commands':[]}
def save(): (out/'window.json').write_text(json.dumps(record,indent=2)+'\n')
save()
for label,provider,baseline,candidate,dapper,scenarios in jobs:
    command=['python3',root/'local-tools/run_causal_ab.py','--provider',provider,'--baseline',baseline,
             '--candidate',candidate,'--output',out/label]
    if dapper:command+=['--dapper',dapper]
    for scenario in scenarios:command+=['--scenario',scenario]
    item={'name':label,'startedUtc':now(),'argv':list(map(str,command)),'comparisonHelperSha256':sha(command[1])}
    record['commands'].append(item);save()
    with (out/(label+'.log')).open('w') as log:
        result=subprocess.run(list(map(str,command)),stdout=log,stderr=subprocess.STDOUT)
    item.update(finishedUtc=now(),exitCode=result.returncode,logSha256=sha(out/(label+'.log')));save()
    print(label,result.returncode,flush=True)
    if result.returncode:raise SystemExit(result.returncode)
record.update(finishedUtc=now(),commandsCompleted=len(jobs),allAccountingAndOraclesPassed=True);save()
