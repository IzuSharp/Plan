#!/usr/bin/env python3
"""Read-only review of existing EF receipts and Portable-PDB source checksums. No database or CLR execution."""
from pathlib import Path
import hashlib,json,struct,uuid,datetime
BASE=Path('/workspace/scratch/4a4a6f01f129/DB-Runtime-Compare-01/worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/efcore')
OUT=Path('/workspace/scratch/4a4a6f01f129/baseline-research/review-01')
MANIFEST=Path('/workspace/scratch/4a4a6f01f129/baseline-research/Korda/benchmarks/db-perf/workload/queries-v3.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def documents(p):
 b=p.read_bytes();assert b[:4]==b'BSJB'
 vl=struct.unpack_from('<I',b,12)[0];pos=(16+vl+3)&~3
 flags,n=struct.unpack_from('<HH',b,pos);pos+=4;streams={}
 for _ in range(n):
  off,size=struct.unpack_from('<II',b,pos);pos+=8;end=b.index(0,pos);name=b[pos:end].decode();pos=(end+4)&~3;streams[name]=b[off:off+size]
 t=streams['#~'];valid=struct.unpack_from('<Q',t,8)[0];pos=24;counts={}
 for i in range(64):
  if valid&(1<<i):counts[i]=struct.unpack_from('<I',t,pos)[0];pos+=4
 assert all(i>=48 for i in counts),'Unexpected non-PDB table before Document'
 bs=4 if t[6]&4 else 2;gs=4 if t[6]&2 else 2
 blobs=streams['#Blob'];guids=streams['#GUID']
 def compressed(buf,at):
  first=buf[at]
  if first<128:return first,at+1
  if first<192:return ((first&63)<<8)|buf[at+1],at+2
  if first<224:return ((first&31)<<24)|(buf[at+1]<<16)|(buf[at+2]<<8)|buf[at+3],at+4
  raise ValueError('Invalid compressed integer')
 def blob(index):
  size,start=compressed(blobs,index);return blobs[start:start+size]
 def cell(size):
  nonlocal pos
  value=int.from_bytes(t[pos:pos+size],'little');pos+=size;return value
 result=[]
 for _ in range(counts.get(48,0)):
  ni,ai,hi,li=cell(bs),cell(gs),cell(bs),cell(gs)
  name=blob(ni);parts=[];at=1
  while at<len(name):index,at=compressed(name,at);parts.append(blob(index).decode())
  full=chr(name[0]).join(parts)
  algorithm=str(uuid.UUID(bytes_le=guids[(ai-1)*16:ai*16])) if ai else None
  result.append({'path':full,'algorithm':algorithm,'checksum':blob(hi).hex()})
 return result
summary=json.loads((BASE/'verification/attempt02-summary.json').read_text())
manifest=json.loads(MANIFEST.read_text())['queries']
expected={x['name']:(x['expectedRows'],int(x['expectedDigest'])) for x in manifest}
checks={'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only existing receipt, binary, compiler-argument and PDB source-checksum verification; no new build/runtime/database execution','summarySha256':sha(BASE/'verification/attempt02-summary.json'),'sourceHashes':{},'lockHashes':{},'lanes':[],'formalComparisonEligible':False}
for name,h in summary['sourceFilesSha256'].items():checks['sourceHashes'][name]={'expected':h,'actual':sha(BASE/name),'match':sha(BASE/name)==h}
for name,h in summary['lockFilesSha256'].items():checks['lockHashes'][name]={'expected':h,'actual':sha(BASE/name),'match':sha(BASE/name)==h}
for lane in summary['lanes']:
 name=lane['lane'];v=BASE/'verification';published=BASE/'bin/publish'/name
 rp=v/f'{name}-result-attempt02.json';r=json.loads(rp.read_text());runtime=r['RuntimeIdentity'];compiler=v/f'{name}-compiler-attempt02.txt'
 build=json.loads((v/f'{name}-build-attempt02.json').read_text());run=json.loads((v/f'{name}-run-attempt02.json').read_text())
 docs=documents(published/'DbPerf.EfCore.pdb');source_docs=[]
 for s in summary['sourceFilesSha256']:
  if not s.endswith('.cs'):continue
  entries=[d for d in docs if Path(d['path']).resolve()==(BASE/s).resolve()]
  source_docs.append({'path':s,'count':len(entries),'sha256':sha(BASE/s),'pdbEntries':entries,'matches':len(entries)==1 and entries[0]['algorithm']=='8829d00f-11b8-4213-878b-770e8597ac16' and entries[0]['checksum']==sha(BASE/s)})
 row={'lane':name,'receiptSha256Matches':sha(rp)==lane['receiptSha256'],'compilerArgumentSha256Matches':sha(compiler)==lane['compilerArgumentsSha256'],'actualCompilerRuntimeAsyncFlag':'/features:runtime-async=on' in compiler.read_text().splitlines(),'buildExit':build['exitCode'],'runExit':run['exitCode'],'sourceDocumentChecksums':source_docs,'artifactHashes':{},'runtimeImageHashes':{},'all35OracleConstantsMatch':all((r['ExpectedResults'].get(n,{}).get('Rows'),r['ExpectedResults'].get(n,{}).get('Digest'))==e for n,e in expected.items()),'all35SucceededOnce':len(r['Cases'])==35 and all(c['Started']==1 and c['Succeeded']==1 and c['Failed']==0 and c['Rows']==expected[c['Name']][0] for c in r['Cases']),'failed':r['Failed'],'oracleFailures':r['OracleFailures'],'completed':r['Completed'],'independentStateChecks':r['IndependentPersistedStateChecksBeforeTiming'],'connectionsZero':r['ApplicationConnectionsReturnedToZero'],'timingEligible':r['TimingComparisonEligible'],'memoryLimitProven':runtime['ClientMemoryBudgetEnforced'],'runtimeAsyncMethodCount':runtime['RuntimeAsyncMethodCount'],'sourceAssemblyMatchesRun':sha(published/'DbPerf.EfCore.dll')==runtime['ManagedAssemblySha256']==run['managedAssemblySha256'],'satori':runtime['SatoriGc'],'isServerGc':runtime['IsServerGc'],'databaseVersion':r['DatabaseVersion']}
 for file,h in lane['publishedArtifacts'].items():row['artifactHashes'][file]={'expected':h,'actual':sha(published/file),'match':sha(published/file)==h}
 for image in runtime['RuntimeImages']:row['runtimeImageHashes'][image['Path']]={'expected':image['Sha256'],'actual':sha(Path(image['Path'])),'match':sha(Path(image['Path']))==image['Sha256']}
 checks['lanes'].append(row)
admissions=json.loads((BASE/'verification/admission-attempt02.json').read_text());ac=[]
for a in admissions:
 name=a['lane'];stderr=(BASE/f'verification/{name}-admission-attempt02.stderr.log').read_text();stdout=(BASE/f'verification/{name}-admission-attempt02.stdout.log').read_text()
 ac.append({'lane':name,'exitCode':a['exitCode'],'elapsedSeconds':a['elapsedSeconds'],'deniedObserved':'DB_PERF_ADMISSION_DENIED ' in stderr,'resultAbsent':'DB_PERF_RESULT ' not in stdout and 'DB_PERF_RESULT ' not in stderr,'sqliteFileCreated':a['sqliteFileCreated'],'formalBenchmark':a['formalBenchmark']})
checks['admissionValidationShaMatches']=sha(BASE/'verification/admission-attempt02.json')==summary['admissionValidationReceiptSha256']
checks['admissions']=ac
checks['sourceAndBinaryChecksAllMatch']=all(v['match'] for v in checks['sourceHashes'].values()) and all(v['match'] for v in checks['lockHashes'].values()) and all(l['receiptSha256Matches'] and l['compilerArgumentSha256Matches'] and l['actualCompilerRuntimeAsyncFlag'] and l['sourceAssemblyMatchesRun'] and all(d['matches'] for d in l['sourceDocumentChecksums']) and all(a['match'] for a in l['artifactHashes'].values()) and all(a['match'] for a in l['runtimeImageHashes'].values()) for l in checks['lanes'])
(OUT/'review-ef-attempt02-binding.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'allSourceAndBinaryBindingsMatch':checks['sourceAndBinaryChecksAllMatch'],'lanes':[{k:l[k] for k in ['lane','all35OracleConstantsMatch','all35SucceededOnce','completed','failed','oracleFailures','connectionsZero','runtimeAsyncMethodCount','timingEligible']} for l in checks['lanes']],'pdbSourceDocumentsChecked':sum(len(l['sourceDocumentChecksums']) for l in checks['lanes']),'admissions':ac},ensure_ascii=False))
