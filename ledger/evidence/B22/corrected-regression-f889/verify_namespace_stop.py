#!/usr/bin/env python3
"""Finite subprocess signal control test; no product workload or stage acceptance."""
from pathlib import Path
import json,sys,threading,time,hashlib
root=Path('/workspace/scratch/58d2a6adf1c3')
source=root/'.worktree/Task-07-B22-corrected-f889-linux/NativeWeave'
sys.path.insert(0,str(source/'tests/Verification.EndToEnd'))
import descriptor_profile as monitor
fixture=Path(sys.argv[1]).resolve();fixture.mkdir(parents=True,exist_ok=False)
(fake:=fixture/'soak.py').write_text('''from pathlib import Path
import json,signal,sys,time
output=Path(sys.argv[sys.argv.index('--output')+1]);output.mkdir()
def stop(signum,frame):
 (output/'receipt.json').write_text(json.dumps({'status':'interrupted','receivedSignal':signum}))
 sys.exit(1)
signal.signal(signal.SIGTERM,stop)
(output/'ready.json').write_text('{}')
while True:time.sleep(.1)
''')
profile=fixture/'profile.json'
profile.write_text(json.dumps({'status':'frozen','identity':{'provider':'postgresql'},'fdThresholdSupplement':{'descriptorMonitorSha256':hashlib.sha256(Path(monitor.__file__).read_bytes()).hexdigest()}}))
run=fixture/'child';sidecar=fixture/'child-descriptors'
def request_stop():
    deadline=time.monotonic()+10
    while not(run/'ready.json').exists()and time.monotonic()<deadline:time.sleep(.05)
    assert(run/'ready.json').exists()
    (sidecar/'stop-request.json').write_text(json.dumps({'action':'stop','reason':'Synthetic supervisor signal-control verification only.'}))
thread=threading.Thread(target=request_stop);thread.start()
monitor.HERE=fixture
sys.argv=['descriptor_profile.py','--profile',str(profile),'--output',str(run),'--artifact-directory',str(fixture),'--trace-reader',str(fake),'--postgres-bin',str(fixture),'--certificate',str(fake),'--private-key',str(fake)]
started=time.monotonic();result=monitor.main();thread.join()
receipt=json.loads((sidecar/'receipt.json').read_text());child=json.loads((run/'receipt.json').read_text())
assert result==1 and receipt['status']=='interrupted'and child['receivedSignal']==15 and not receipt.get('forcedControllerKill')
summary={'status':'control-test-passed','scope':'Only actual owned-subprocess SIGTERM and interrupted receipt handling; no reference application, calibration, steady stage or retirement claim.','monitorSha256':hashlib.sha256(Path(monitor.__file__).read_bytes()).hexdigest(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'elapsedSeconds':time.monotonic()-started,'childReceivedSignal':child['receivedSignal'],'monitorStatus':receipt['status'],'controllerExitCode':receipt['controllerExitCode'],'fullB22Acceptance':False}
(fixture/'control-test.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
