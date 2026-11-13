#!/usr/bin/env python3
"""Run immutable old checks against their actual paired commits, not current design state."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,datetime
P=Path(__file__).resolve().parents[1];D=P.parent/'NativeWeave-Design'
P_SHA='5b346ebb5acdb387077d0faae16b00bbc77cb299';D_SHA='ba21ecb5c2299b303584b120f2e6bd1c6d74783a'
out=P/'verification/frozen-history';out.mkdir(parents=True,exist_ok=True)
commands=['verify_research_assets.py','verify_logical_admission_history.py','verify_source_lifecycle.py','source_lifecycle_binding_checks.py','host_selection_checks.py','rust1100_checks.py','mutation_checks.py']
records=[]
with tempfile.TemporaryDirectory(prefix='nw-frozen-history-') as tmp:
 base=Path(tmp);created=[]
 try:
  for repo,sha in [(P,P_SHA),(D,D_SHA)]:
   target=base/repo.name
   result=subprocess.run(['git','worktree','add','--detach',str(target),sha],cwd=repo,capture_output=True,timeout=60)
   assert result.returncode==0,result.stderr.decode(errors='replace');created.append((repo,target))
   assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=target,text=True).strip()==sha
  for tool in commands:
   started=datetime.datetime.now(datetime.timezone.utc).isoformat()
   result=subprocess.run(['python3','tools/'+tool],cwd=base/'Plan',capture_output=True,timeout=180)
   stdout=out/(tool+'.stdout');stderr=out/(tool+'.stderr');stdout.write_bytes(result.stdout);stderr.write_bytes(result.stderr)
   row={'tool':tool,'source_sha256':hashlib.sha256((base/'Plan/tools'/tool).read_bytes()).hexdigest(),'exit_code':result.returncode,'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest()};records.append(row)
   if result.returncode:raise RuntimeError(tool+': '+result.stderr[-1800:].decode(errors='replace')+result.stdout[-600:].decode(errors='replace'))
 finally:
  for repo,target in reversed(created):subprocess.run(['git','worktree','remove','--force',str(target)],cwd=repo,capture_output=True,timeout=60,check=True)
report={'scope':'Historical immutable checks at original paired commits. These old statuses/host choices do not describe current acceptance.','plan_commit':P_SHA,'design_commit':D_SHA,'passed':all(x['exit_code']==0 for x in records) and len(records)==len(commands),'records':records}
(out/'results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'historical_checks':len(records),'plan_commit':P_SHA,'design_commit':D_SHA}))
