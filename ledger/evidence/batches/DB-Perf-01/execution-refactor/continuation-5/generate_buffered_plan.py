#!/usr/bin/env python3
"""Freeze paired public buffered-terminal consumers without starting a process."""
from pathlib import Path
import argparse,hashlib,json,shlex
p=argparse.ArgumentParser(description=__doc__)
for n in ['source','before-dir','candidate-dir','plan','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--provider',choices=['sqlite','postgresql'],required=True);p.add_argument('--postgres-bin',type=Path);a=p.parse_args()
def ident(f,want=None):
 f=Path(f).resolve(strict=True);h=hashlib.sha256(f.read_bytes()).hexdigest()
 if want is not None and want!=h:raise ValueError('Changed input '+str(f))
 return {'path':str(f),'sha256':h}
planpath=a.plan.resolve();out=a.output.resolve()
if planpath.exists() or out.exists() or planpath.is_relative_to(out):p.error('Use new independent plan/output paths')
inputs={};receipts={}
for cohort in ['before','candidate']:
 d=getattr(a,cohort+'_dir').resolve(strict=True);rp=d.parent/'build-receipt.json';r=json.loads(rp.read_text());receipts[cohort]=r
 if r['kind']!='buffered-query-phases' or r['provider']!=a.provider or r['exit_code'] or r['project_references'] or r['abi_wrapper_instrumentation'] or not r['ordinary_consumer_unchanged'] or not r['package_unchanged']:raise ValueError('Invalid consumer receipt')
 inputs[cohort]={'buildReceipt':ident(rp),'executable':ident(d/'DbPerf.QueryPhases',r['executable_sha256']),'packageSourceCommit':r['package_source_commit'],'packageSha256':r['package_sha256'],'program':ident(d.parent/'Program.cs',r['sources']['Program.cs']),'native':{n:ident(d/n,h) for n,h in r['native_images'].items()}}
for key in ['sources','project_sha256','business_contract_sha256','tools']:
 if receipts['before'][key]!=receipts['candidate'][key]:raise ValueError('Paired consumer contract differs: '+key)
runner=ident(a.source/'benchmarks/db-perf/run.py');commands=[]
def add(name,cohort,rows,fixture=False):
 argv=[inputs[cohort]['executable']['path'],'{connection}','{output}/'+name+'.json','1' if fixture else '256','1' if fixture else '3']
 if fixture:argv+=['initialize']
 argv+=['--rows',str(rows)]
 commands.append({'name':name,'cohort':cohort,'phase':'fixture' if fixture else 'buffered','rows':rows,'timingRequested':not fixture,'longRunAcceptance':False,'instrumented':False,'argv':argv,'cpus':'0-3','timeoutSeconds':600})
add('fixture-buffered','candidate',1,True)
for rows in [1,100,1000]:
 for cohort in (['candidate','before'] if rows==100 else ['before','candidate']):add(cohort+'-rows'+str(rows),cohort,rows)
x={'schemaVersion':1,'provider':a.provider,'lane':'buffered','scope':'Paired whole-operation buffered public terminals; no observable first row and no framework-only allocation attribution. No execution or long-run acceptance by generation.','longRunAcceptance':False,'firstRowObservable':False,'inputs':{'generator':ident(__file__),'runner':runner,'consumers':inputs},'phaseDataset':{'tenants':2,'rowsPerTenant':1000,'batchRows':32},'affinity':{'client':'0-3','postgres':'4-7','observer':'8'},'commands':commands}
if a.provider=='sqlite':x['connection']=str(out/'fixture.sqlite')
else:
 if a.postgres_bin is None:p.error('--postgres-bin is required')
 x['inputs']['postgresTools']={n:ident(a.postgres_bin/n) for n in ['initdb','postgres','pg_isready','psql']}
 x['postgres']={'bin':str(a.postgres_bin.resolve()),'data':str(out/'pgdata'),'cpus':'4-7','maxConnections':64,'maxClientConcurrency':1}
x['runnerCommand']=['taskset','-c','8','python3',runner['path'],str(planpath),'--output',str(out)]
planpath.parent.mkdir(parents=True,exist_ok=True)
with planpath.open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
print(shlex.join(x['runnerCommand']))
