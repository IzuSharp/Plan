#!/usr/bin/env python3
"""Bounded B22 descriptor ownership diagnosis; no acceptance or profile freeze."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,signal,subprocess,sys,time,types

root=Path('/workspace/scratch/58d2a6adf1c3')
source=root/'.worktree/Task-07-B22-finish-f889-linux/NativeWeave'
sys.path.insert(0,str(source/'tests/Verification.EndToEnd'))
import soak
from harness import Database,PostgresCluster,Service,configuration,require,sha,write_json,eventually

output=Path(sys.argv[1]).resolve();output.mkdir(parents=True,exist_ok=False)
args=types.SimpleNamespace(artifact_directory=root/'task07-runs/b22-observer-build-006/artifacts/aot',trace_reader=root/'.worktree/Task-07-B22-recovery-6b7401-linux/NativeWeave/src/Verification.EndToEnd/TraceReader/bin/Release/net11.0/NativeWeave.Verification.EndToEnd.TraceReader.dll',mode='aot',provider='postgresql',dotnet='dotnet',postgres_bin=root/'task07-toolchain/postgres/bin',certificate=root/'task07-package-probe/final-002/tls/localhost.pem',private_key=root/'task07-package-probe/final-002/tls/localhost.private.pem')
command,identity,providers=soak.identity(args)
receipt={'kind':'bounded diagnostic only','purpose':'observe PG descriptor owners under same workload after frozenFD24 breach; no profile adjustment or acceptance','sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),'diagnosticScriptSha256':sha(Path(__file__)),'identity':identity,'settings':{'loadSeconds':300,'idleSeconds':30,'rate':4,'concurrency':4,'seed':2200261118},'status':'running','fullB22Acceptance':False,'performanceMeasurement':False,'resourceProfileFreeze':False,'startedUnixNs':time.time_ns(),'sharedHost':'Original SQLite30m continues concurrently in separate process/data namespace; no B23timing.'}
write_json(output/'request.json',receipt)
operations=soak.Journal(output/'operations.jsonl');resources=soak.Journal(output/'descriptors.jsonl');maximum=0;last_sample=0;service=None
control=output/'observer-control.json';trace=output/'runtime.nettrace'
command=['env',*[k+'='+v for k,v in soak.TRACE_ENVIRONMENT.items()],'DOTNET_EventPipeOutputPath='+str(trace),'NW_B22_HANDLE_CONTROL=1','NW_B22_HANDLE_CONTROL_OUTPUT='+str(output/'known-handles.jsonl'),'NW_B22_OBSERVER_CONTROL='+str(control),*command]

def snapshot(phase):
 global maximum,last_sample
 started=time.monotonic_ns();descriptor_root=Path('/proc')/str(service.process.pid)/'fd';entries=list(descriptor_root.iterdir());inventory=[];vanished=0
 for entry in entries:
  try:target=os.readlink(entry)
  except FileNotFoundError:vanished+=1;continue
  if target.startswith('socket:'):category='socket';owner=target
  elif target.startswith('pipe:'):category='pipe';owner=target
  elif target.startswith('anon_inode:'):category=target;owner=target
  else:
   path=Path(target)
   try:owner=str(path.relative_to(output));category='diagnostic-fixture-file'
   except ValueError:
    if target=='/dev/null':category='null-device';owner=target
    elif target.startswith(str(args.artifact_directory)):category='immutable-application-asset';owner=path.name
    else:category='other-file';owner={'basename':path.name,'targetSha256':hashlib.sha256(target.encode()).hexdigest()}
  inventory.append({'descriptor':int(entry.name),'category':category,'owner':owner})
 counts={}
 for item in inventory:counts[item['category']]=counts.get(item['category'],0)+1
 tail.read();latest=tail.latest
 process=soak.process_sample(service.process.pid)
 value={'phase':phase,'startedMonotonicNs':started,'endedMonotonicNs':time.monotonic_ns(),'enumerated':len(entries),'resolved':len(inventory),'vanishedDuringRead':vanished,'categories':counts,'inventory':inventory,'process':process,'observationSequence':latest['sequence'],'observationUnixMilliseconds':latest['unixMilliseconds'],'nativeOwners':latest['databaseNativeOwners'],'serverMeter':latest['serverMeter'],'traceBytes':trace.stat().st_size}
 resources.write(value)
 if len(entries)>maximum:maximum=len(entries);print(json.dumps({'maximumEnumeratedFds':maximum,'categories':counts,'phase':phase}),flush=True)
 last_sample=time.monotonic()
 return value

try:
 with PostgresCluster(args.postgres_bin,output/'postgres') as cluster:
  database=cluster.database();config,token=configuration('postgresql',database,output,tls=(args.certificate,args.private_key));config.update(runWorkers=True,maxBlobBytes=256*1024**2);sql=Database('postgresql',database,str(cluster.binary/'psql'))
  with Service(command,config,output/'service',observed=True,http2=True,certificate=args.certificate) as service:
   tail=soak.Tail(output/'service/observations.jsonl');tail.read();workload=soak.Workload(service,token,sql,config,2200261118,operations)
   began=time.monotonic_ns();futures=set()
   with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    for sequence in range(1200):
     offered=began+sequence*250000000
     while time.monotonic_ns()<offered:
      if time.monotonic()-last_sample>=1.1:snapshot('load')
      time.sleep(min(.05,max(0,(offered-time.monotonic_ns())/1e9)))
     ready={f for f in futures if f.done()}
     for f in ready:f.result()
     futures-=ready;require(len(futures)<4,'Fixed diagnostic generator outstanding slots exhausted');require(time.monotonic_ns()-offered<=1000000000,'Fixed diagnostic generator lag exceeded1s')
     actual=workload.reserve();require(actual==sequence,'Diagnostic operation identity drift')
     futures.add(executor.submit(workload.cancel_upload,sequence) if sequence==0 else executor.submit(workload.perform,sequence,offered))
     if time.monotonic()-last_sample>=1.1:snapshot('load')
    for future in futures:future.result(timeout=90)
   while time.monotonic_ns()<began+300000000000:
    if time.monotonic()-last_sample>=1.1:snapshot('load')
    time.sleep(.05)
   receipt['loadElapsedSeconds']=(time.monotonic_ns()-began)/1e9
   receipt['durable']=workload.reconcile();write_json(control,{'sequence':1,'collect':True,'expectedSources':{'sqlite':1,'postgresql':1}})
   end=time.monotonic()+30
   while time.monotonic()<end:snapshot('idle');time.sleep(1.1)
   receipt['maximumEnumeratedFds']=maximum;receipt['ordinaryProtocols']=sorted(service.protocols);receipt['workloadCounts']=workload.counts
  tail.read();receipt['finalObservation']=tail.latest;receipt['finalShutdown']=service.shutdown
 soak.revalidate_inputs(args,identity);receipt['traceObservation']=soak.trace_analyze(args,output);receipt['status']='diagnostic-completed'
except BaseException as error:
 receipt['status']='diagnostic-failed';receipt['error']={'type':type(error).__name__,'message':str(error) if isinstance(error,(AssertionError,RuntimeError))else None}
 raise
finally:
 operations.close();resources.close();receipt['endedUnixNs']=time.time_ns();receipt['rawHashes']={p.name:sha(p) for p in output.iterdir() if p.is_file() and p.name!='receipt.json'};write_json(output/'receipt.json',receipt)
 print(json.dumps({'status':receipt['status'],'maximumEnumeratedFds':maximum,'receipt':str(output/'receipt.json')}),flush=True)
