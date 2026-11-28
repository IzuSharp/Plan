#!/usr/bin/env python3
"""Read-only identity/oracle/PDB audit of the existing EF attempt03 candidate."""
from pathlib import Path
import ast,datetime,hashlib,json,struct,uuid,zipfile
ROOT=Path('/workspace/scratch/4a4a6f01f129/DB-Runtime-Compare-01/worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/efcore')
OUT=Path('/workspace/scratch/4a4a6f01f129/baseline-research/review-02')
# Reuse only the previously reviewed pure Portable-PDB reader, not its executable audit body.
old_reader=Path('/workspace/scratch/4a4a6f01f129/baseline-research/review-01/review-ef-binding.py').read_text()
node=next(n for n in ast.parse(old_reader).body if isinstance(n,ast.FunctionDef) and n.name=='documents')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<reviewed-pdb-reader>','exec'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v=ROOT/'verification';s=json.loads((v/'attempt03-summary.json').read_text());old=json.loads((v/'attempt02-summary.json').read_text())
m=json.loads(Path('/workspace/scratch/4a4a6f01f129/baseline-research/Korda/benchmarks/db-perf/workload/queries-v3.json').read_text());expect={q['name']:(q['expectedRows'],int(q['expectedDigest'])) for q in m['queries']}
out={'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Existing attempt03 identity/receipt/source/PDB read only. No builds, runtime execution or database work.','summarySha256':sha(v/'attempt03-summary.json'),'sourceChecks':{},'lanes':[],'oldAttempt02ArtifactChecks':{},'formalLongRunAcceptanceCompleted':False,'memoryEnforcementProven':False}
with zipfile.ZipFile(v/'attempt03-source.zip') as z:
 for name,h in {**s['sourceFilesSha256'],**s['lockFilesSha256']}.items():
  out['sourceChecks'][name]={'expected':h,'current':sha(ROOT/name),'archive':hashlib.sha256(z.read(name)).hexdigest(),'match':sha(ROOT/name)==h==hashlib.sha256(z.read(name)).hexdigest()}
out['sourceArchiveHashMatches']=sha(v/'attempt03-source.zip')==s['sourceArchiveSha256']
out['oldSourceArchiveHashMatches']=sha(v/'attempt02-source.zip')==s['historicalAttempt02SourceArchiveSha256']
for lane in old['lanes']:
 out['oldAttempt02ArtifactChecks'][lane['lane']]={file:sha(ROOT/'bin/publish'/lane['lane']/file)==h for file,h in lane['publishedArtifacts'].items()}
for lane in s['lanes']:
 name=lane['lane'];published=Path(lane['publishedDirectory']);rpath=v/f'{name}-result-attempt03.json';r=json.loads(rpath.read_text());ri=r['RuntimeIdentity'];run=json.loads((v/f'{name}-run-attempt03.json').read_text());build=json.loads((v/f'{name}-build-attempt03.json').read_text());compiler=v/f'{name}-compiler-attempt03.txt';docs=documents(published/'DbPerf.EfCore.pdb');dchecks=[]
 for file,h in s['sourceFilesSha256'].items():
  if not file.endswith('.cs'):continue
  matches=[d for d in docs if Path(d['path']).resolve()==(ROOT/file).resolve()]
  dchecks.append({'path':file,'expected':h,'pdb':matches,'match':len(matches)==1 and matches[0]['algorithm']=='8829d00f-11b8-4213-878b-770e8597ac16' and matches[0]['checksum']==h})
 row={'lane':name,'publishedDirectory':str(published),'sourcePdbChecks':dchecks,'artifactChecks':{f:sha(published/f)==h for f,h in lane['publishedArtifacts'].items()},'runtimeImageChecks':{i['Path']:sha(Path(i['Path']))==i['Sha256'] for i in ri['RuntimeImages']},'runAssemblyHashMatch':ri['ManagedAssemblySha256']==run['managedAssemblySha256']==sha(published/'DbPerf.EfCore.dll'),'receiptHashMatch':sha(rpath)==lane['receiptSha256'],'compilerHashMatch':sha(compiler)==lane['compilerArgumentsSha256'],'runtimeAsyncCompilerFlagObserved':'/features:runtime-async=on' in compiler.read_text().splitlines(),'runtimeAsyncMethodCount':ri['RuntimeAsyncMethodCount'],'publishExit':build['exitCode'],'runExit':run['exitCode'],'all35ManifestOraclesMatch':all((r['ExpectedResults'][n]['Rows'],r['ExpectedResults'][n]['Digest'])==e for n,e in expect.items()),'all35SucceededOnce':len(r['Cases'])==35 and all(c['Started']==c['Succeeded']==1 and c['Failed']==0 and c['Rows']==expect[c['Name']][0] for c in r['Cases']),'completed':r['Completed'],'failed':r['Failed'],'oracleFailures':r['OracleFailures'],'independentStateChecks':r['IndependentPersistedStateChecksBeforeTiming'],'connectionsZero':r['ApplicationConnectionsReturnedToZero'],'TimingComparisonEligible':r['TimingComparisonEligible'],'finiteOperationsOnly':run['formalBenchmark'] is False and '--operations' in run['command'] and '--seconds' not in run['command'],'memoryPolicy':{k:ri[k] for k in ['RequestedClientBudgetBytes','RequestedGcHeapBudgetBytes','ObservedConfiguredGcHeapHardLimitBytes','GcTotalAvailableMemoryBytesAtStartup','GcHeapBudgetEnforcementProven','ClientMemoryBudgetEnforced','OwnerAcceptedUnenforcedMemoryPolicy']},'runHeapEnvironment':run['environmentOverrides']['DOTNET_GCHeapHardLimit'],'runtimeConfigHeapBytes':json.loads((published/'DbPerf.EfCore.runtimeconfig.json').read_text())['runtimeOptions']['configProperties']['System.GC.HeapHardLimit']}
 row['memoryPolicyMatchesOwner']=all(ri[k]==201326592 for k in ['RequestedClientBudgetBytes','RequestedGcHeapBudgetBytes','ObservedConfiguredGcHeapHardLimitBytes']) and ri['GcHeapBudgetEnforcementProven'] is False and ri['ClientMemoryBudgetEnforced'] is False and ri['OwnerAcceptedUnenforcedMemoryPolicy'] is True and row['runHeapEnvironment']=='0xC000000' and row['runtimeConfigHeapBytes']==201326592
 out['lanes'].append(row)
out['allIdentityChecksMatch']=out['sourceArchiveHashMatches'] and out['oldSourceArchiveHashMatches'] and all(c['match'] for c in out['sourceChecks'].values()) and all(all(c.values()) for c in out['oldAttempt02ArtifactChecks'].values()) and all(all(c['match'] for c in l['sourcePdbChecks']) and all(l['artifactChecks'].values()) and all(l['runtimeImageChecks'].values()) and l['runAssemblyHashMatch'] and l['receiptHashMatch'] and l['compilerHashMatch'] and l['runtimeAsyncCompilerFlagObserved'] and l['runtimeAsyncMethodCount']==19 for l in out['lanes'])
out['finiteCorrectnessVerified']=all(l['all35ManifestOraclesMatch'] and l['all35SucceededOnce'] and l['publishExit']==l['runExit']==l['failed']==l['oracleFailures']==0 and l['completed']==35 and l['connectionsZero'] and l['independentStateChecks']==4 and l['finiteOperationsOnly'] for l in out['lanes'])
out['ownerAcceptedMemoryPolicyMatches']=all(l['memoryPolicyMatchesOwner'] for l in out['lanes'])
(OUT/'ef-attempt03-binding.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['allIdentityChecksMatch','finiteCorrectnessVerified','ownerAcceptedMemoryPolicyMatches','formalLongRunAcceptanceCompleted','memoryEnforcementProven']},ensure_ascii=False))
