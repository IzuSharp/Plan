#!/usr/bin/env python3
"""Own two exact B22 calibration children and cooperative stop in this namespace."""
from pathlib import Path
import hashlib,json,os,signal,subprocess,sys,time
from urllib.parse import urlsplit
request_path=Path(sys.argv[1]).resolve()
request=json.loads(request_path.read_text())
source=Path(request['sourceWorktree'])
sys.path.insert(0,str(source/'tests/Verification.EndToEnd'))
from harness import require,sha,write_json
from soak import Journal,Tail
from descriptor_profile import process_identity,snapshot
require(sha(Path(__file__))==request['launcherSha256'],'Launcher input changed')
for value in request['boundFiles']:
    require(sha(Path(value['path']))==value['sha256'],'A reviewed launch input changed')
for name,value in request['environment'].items():
    require(os.environ.get(name)==value,'Expected launch environment differs: '+name)
output=Path(request['launchDirectory']);output.mkdir(parents=True,exist_ok=False)
state={'schemaVersion':1,'task':'B22','status':'running','requestPath':str(request_path),'requestSha256':sha(request_path),'launchMonotonicNs':time.monotonic_ns(),'startedUnixNs':time.time_ns(),'sharedHost':'Two B22 providers have isolated service/database directories and processes on this same host; no B23 performance load.','runs':{},'fullB22Acceptance':False}
write_json(output/'request.json',request)
children={};logs={};journals={};tails={};targets={};peaks={};stopped=set()
try:
    for job in request['jobs']:
        name=job['provider'];run=Path(job['output'])
        require(not run.exists(),'Calibration output already exists')
        logs[name]=(output/(name+'.log')).open('wb')
        children[name]=subprocess.Popen(job['argv'],cwd=source,stdout=logs[name],stderr=subprocess.STDOUT)
        state['runs'][name]={'controller':process_identity(children[name].pid),'output':str(run),'status':'running','launchedMonotonicNs':time.monotonic_ns()}
        journals[name]=(Journal(output/(name+'-descriptor-counts.jsonl')),Journal(output/(name+'-descriptor-inventories.jsonl')))
        tails[name]=Tail(run/'resources.jsonl');peaks[name]=0
    write_json(output/'live.json',state)
    while any(child.poll()is None for child in children.values()):
        for name,child in children.items():
            run=Path(state['runs'][name]['output'])
            stop=output/('stop-request-'+name+'.json')
            if not stop.exists():stop=output/'stop-request.json'
            if child.poll()is None and stop.exists()and name not in stopped:
                with stop.open('rb')as stream:payload=stream.read(4097)
                require(len(payload)<=4096,'Stop request exceeds bound')
                value=json.loads(payload)
                require(value.get('action')=='stop'and isinstance(value.get('reason'),str)and 0<len(value['reason'])<=512,'Invalid bounded stop request')
                stopped.add(name);state['runs'][name]['stopRequest']={'reason':value['reason'],'sha256':hashlib.sha256(payload).hexdigest(),'monotonicNs':time.monotonic_ns()}
                child.send_signal(signal.SIGTERM)
            progress=run/'progress.json'
            if progress.exists():
                observed=json.loads(progress.read_text())
                state['runs'][name].update({key:observed.get(key)for key in('status','stageElapsedSeconds','error','observedMax','workloadCounts')})
                pid=observed.get('serviceProcessId')
                if child.poll()is None and pid is not None:
                    try:
                        actual=process_identity(pid)
                        if name not in targets:
                            require(actual['parentPid']==child.pid,'Observed target is not this controller child')
                            config=json.loads((run/'service/config.private.json').read_text())
                            ready=next(line[6:]for line in(run/'service/service.log').read_text().splitlines()if line.startswith('READY '))
                            targets[name]=(actual,urlsplit(ready).port,urlsplit(config['database']).port)
                            state['runs'][name]['serviceTarget']=actual
                        target,http_port,postgres_port=targets[name]
                        require(actual==target,'Application PID identity changed')
                        tails[name].read();phase=tails[name].latest['phase']if tails[name].latest else'startup'
                        row=snapshot(target,run,http_port,postgres_port,phase)
                        journals[name][0].write({key:value for key,value in row.items()if key!='inventory'})
                        if row['enumerated']>peaks[name]or phase=='idle':journals[name][1].write(row)
                        peaks[name]=max(peaks[name],row['enumerated'])
                    except FileNotFoundError:
                        state['runs'][name]['procReadRaces']=state['runs'][name].get('procReadRaces',0)+1
            if child.poll()is not None:state['runs'][name]['exitCode']=child.returncode
        write_json(output/'live.json',state)
        time.sleep(1.1)
    for name,child in children.items():
        run=Path(state['runs'][name]['output']);receipt=json.loads((run/'receipt.json').read_text())
        state['runs'][name].update(exitCode=child.wait(),status=receipt['status'],receiptSha256=sha(run/'receipt.json'))
    state['status']='calibrations-completed'if all(value['exitCode']==0 and value['status']=='calibration-passed'for value in state['runs'].values())else'interrupted'if stopped else'failed'
except BaseException as error:
    state.update(status='launcher-failed',error={'type':type(error).__name__,'message':str(error)})
    for name,child in children.items():
        if child.poll()is None:
            child.terminate()
            try:child.wait(timeout=45)
            except subprocess.TimeoutExpired:
                child.kill();child.wait(timeout=5)
                state['runs'][name]['cleanup']='forced controller kill; target/descendant retirement unobserved, root must resolve before load-slot reuse'
finally:
    for values in journals.values():
        for journal in values:journal.close()
    for log in logs.values():log.close()
    state['endedUnixNs']=time.time_ns()
    state['evidenceHashes']={p.name:sha(p)for p in output.glob('*.jsonl')}
    write_json(output/'receipt.json',state)
    print(json.dumps({'status':state['status'],'receipt':str(output/'receipt.json')}),flush=True)
sys.exit(0 if state['status'] == 'calibrations-completed' else 1)
