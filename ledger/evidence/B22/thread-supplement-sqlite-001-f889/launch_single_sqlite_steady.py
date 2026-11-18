#!/usr/bin/env python3
"""Own a declared immutable B22 descriptor-supervised stage in one live exec."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
request_path=Path(sys.argv[1]).resolve()
request=json.loads(request_path.read_text())
source=Path(request['sourceWorktree'])
sys.path.insert(0,str(source/'tests/Verification.EndToEnd'))
from harness import require,sha,write_json
from descriptor_profile import process_identity
require(sha(Path(__file__))==request['launcherSha256'],'Launcher source differs from request')
for item in request['boundFiles']:require(sha(Path(item['path']))==item['sha256'],'Frozen stage input changed')
for name,value in request['environment'].items():require(os.environ.get(name)==value,'Launch environment differs: '+name)
output=Path(request['launchDirectory']);output.mkdir(parents=True,exist_ok=False)
state={'schemaVersion':1,'task':'B22','status':'running','requestPath':str(request_path),'requestSha256':sha(request_path),'startedUnixNs':time.time_ns(),'launchMonotonicNs':time.monotonic_ns(),'runs':{},'fullB22Acceptance':False,'multiDayAcceptance':False,'sharedHost':request['sharedHost']}
write_json(output/'request.json',request)
children={};logs={};stopped=set()
try:
    for job in request['jobs']:
        name=job['provider'];run=Path(job['output']);sidecar=run.with_name(run.name+'-descriptors')
        require(not run.exists()and not sidecar.exists(),'Immutable run output already exists')
        logs[name]=(output/(name+'.log')).open('wb')
        child=subprocess.Popen(job['argv'],cwd=source,stdout=logs[name],stderr=subprocess.STDOUT)
        children[name]=child
        state['runs'][name]={'monitor':process_identity(child.pid),'output':str(run),'descriptorOutput':str(sidecar),'status':'running','launchedMonotonicNs':time.monotonic_ns()}
    write_json(output/'live.json',state)
    while any(child.poll()is None for child in children.values()):
        for name,child in children.items():
            run=Path(state['runs'][name]['output']);sidecar=Path(state['runs'][name]['descriptorOutput'])
            stop=output/('stop-request-'+name+'.json')
            if not stop.exists():stop=output/'stop-request.json'
            if child.poll()is None and stop.exists()and name not in stopped and sidecar.exists():
                with stop.open('rb')as stream:payload=stream.read(4097)
                require(len(payload)<=4096,'Stop request exceeds bound')
                value=json.loads(payload)
                require(value.get('action')=='stop'and isinstance(value.get('reason'),str)and 0<len(value['reason'])<=512,'Invalid explicit stop reason')
                write_json(sidecar/'stop-request.json',value)
                stopped.add(name);state['runs'][name]['stopRequest']={'reason':value['reason'],'sha256':hashlib.sha256(payload).hexdigest(),'monotonicNs':time.monotonic_ns()}
            if(run/'progress.json').exists():
                progress=json.loads((run/'progress.json').read_text())
                state['runs'][name].update({key:progress.get(key)for key in('status','stageElapsedSeconds','error','observedMax','workloadCounts','serviceProcessId')})
            if(sidecar/'request.json').exists():
                monitor=json.loads((sidecar/'request.json').read_text())
                state['runs'][name].update({key:monitor[key]for key in('target','controllerPid','profileSha256','monitorSha256')if key in monitor})
            if child.poll()is not None:state['runs'][name]['exitCode']=child.returncode
        write_json(output/'live.json',state)
        time.sleep(1.1)
    for name,child in children.items():
        run=Path(state['runs'][name]['output']);sidecar=Path(state['runs'][name]['descriptorOutput'])
        ordinary=json.loads((run/'receipt.json').read_text());monitor=json.loads((sidecar/'receipt.json').read_text())
        state['runs'][name].update(exitCode=child.wait(),status=ordinary['status'],monitorStatus=monitor['status'],ordinaryReceiptSha256=sha(run/'receipt.json'),monitorReceiptSha256=sha(sidecar/'receipt.json'),completedStageSeconds=ordinary.get('completedStageSeconds'),steadyLoadElapsedSeconds=ordinary.get('steadyLoadElapsedSeconds'))
    passed=all(value['exitCode']==0 and value['status']=='stage-passed'and value['monitorStatus']=='supplemented-stage-passed'for value in state['runs'].values())
    state['status']='steady-stages-completed'if passed else'interrupted'if stopped else'failed'
except BaseException as error:
    state.update(status='launcher-failed',error={'type':type(error).__name__,'message':str(error)})
    for name,child in children.items():
        if child.poll()is None:
            sidecar=Path(state['runs'][name]['descriptorOutput'])
            if sidecar.exists():write_json(sidecar/'stop-request.json',{'action':'stop','reason':'Parent steady launcher encountered an error; cooperative child cleanup required.'})
            else:child.terminate()
            try:child.wait(timeout=45)
            except subprocess.TimeoutExpired:
                child.kill();child.wait(timeout=5)
                state['runs'][name]['cleanup']='forced monitor kill; controller/target retirement unknown, root must resolve before load-slot reuse'
finally:
    for log in logs.values():log.close()
    state['endedUnixNs']=time.time_ns();write_json(output/'receipt.json',state)
    print(json.dumps({'status':state['status'],'receipt':str(output/'receipt.json')}),flush=True)
sys.exit(0 if state['status']=='steady-stages-completed' else 1)
