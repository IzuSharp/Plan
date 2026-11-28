#!/usr/bin/env python3
"""Read existing Native Image artifacts and finite receipts only; no Java or database execution."""
from pathlib import Path
import argparse,datetime,hashlib,json,struct,tarfile,zipfile
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
TASK=Path('/workspace/scratch/4a4a6f01f129/DB-Runtime-Compare-01');JAVA=TASK/'toolchains/java';e=args.evidence;a=args.artifacts
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((e/'build-identity.json').read_text());life=json.loads((e/'verification-lifecycle.json').read_text());retained=json.loads((e/'retained-artifacts.json').read_text());manifest_path=Path('/workspace/scratch/4a4a6f01f129/baseline-research/Korda/benchmarks/db-perf/workload/queries-v3.json');m=json.loads(manifest_path.read_text());expect={q['name']:(q['expectedRows'],int(q['expectedDigest'])) for q in m['queries']}
archive=a/'source.tar.gz';source_checks={}
with tarfile.open(archive,'r:gz') as tar:
 members={member.name.lstrip('./'):member for member in tar.getmembers() if member.isfile()}
 for name,h in b['sourceHashes'].items():
  data=tar.extractfile(members[name]).read();source_checks[name]={'expected':h,'archiveSha256':hashlib.sha256(data).hexdigest(),'matches':hashlib.sha256(data).hexdigest()==h}
 script=tar.extractfile(members['maven_build.py']).read() if 'maven_build.py' in members else None
jar=a/'runtime-comparison-java-1.0.0.jar';exe=a/'runtime-comparison-java';head=exe.read_bytes()[:64]
out={'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only frozen source/JAR/ELF/dependency/log and existing dual-provider finite Native receipts; not formal duration acceptance','evidenceDirectory':str(e),'artifactDirectory':str(a),'buildIdentityHashMatches':sha(e/'build-identity.json')==life['buildIdentitySha256'],'sourceArchiveHashMatches':sha(archive)==retained['sourceArchiveSha256'],'buildScriptArchiveHashMatches':None if script is None else hashlib.sha256(script).hexdigest()==b['buildScriptSha256'],'buildScriptCurrentHashMatches':sha(TASK/'worktree-Plan/ledger/evidence/batches/DB-Perf-01/runtime-comparison-01/clients/java/maven_build.py')==b['buildScriptSha256'],'sourceChecks':source_checks,'elfSha256':sha(exe),'elfIdentityMatches':sha(exe)==b['executableSha256']==life['nativeExecutableSha256'],'elfMagic':head[:4].hex(),'elfClass':head[4],'elfMachine':struct.unpack_from('<H',head,18)[0],'jarIdentityMatches':sha(jar)==b['jarSha256'],'jdkReleaseHashMatches':sha(JAVA/'graalvm-community-25.6.5.1+2.1/release')==b['jdkReleaseSha256'],'nativeImageVersion':b['nativeImageVersion'],'buildFlags':b['buildFlags'],'dependencyChecks':{},'metadataArchiveChecks':{},'commands':[],'providers':[],'formalLongRunAcceptanceCompleted':False}
for item in b['runtimeArtifactHashes']:
 candidates=list((JAVA/'m2').rglob(item['name']));out['dependencyChecks'][item['name']]={'matches':len(candidates)==1 and sha(candidates[0])==item['sha256'],'expected':item['sha256'],'paths':[str(q) for q in candidates]}
for name,h in b['reachabilityMetadataArchives'].items():
 candidates=list((JAVA/'m2').rglob(name));out['metadataArchiveChecks'][name]={'matches':len(candidates)==1 and sha(candidates[0])==h,'expected':h}
with zipfile.ZipFile(jar) as z:
 metadata='META-INF/native-image/org.korda.compare/runtime-comparison-java/reachability-metadata.json';out['applicationMetadataInJarMatches']=hashlib.sha256(z.read(metadata)).hexdigest()==b['sourceHashes']['src/main/resources/'+metadata]
 out['applicationClassVersions']=sorted(set(struct.unpack('>H',z.read(n)[6:8])[0] for n in z.namelist() if n.startswith('org/korda/compare/') and n.endswith('.class')))
for c in life['commands']:out['commands'].append({'label':c['label'],'exitCode':c['exitCode'],'logHashMatches':sha(e/(c['label']+'.txt'))==c['outputSha256']})
for provider in ['sqlite','postgresql']:
 rp=e/f'{provider}-native.json';r=json.loads(rp.read_text());row={'provider':provider,'receiptHashMatches':sha(rp)==life[provider]['receiptSha256'],'nativeAot':r['NativeAot'],'receiptElfMatches':r['ExecutableSha256']==b['executableSha256'],'verificationOnly':r['VerificationOnly'],'verifiedCasesPerWorker':r['VerifiedCasesPerWorker'],'warmupPerWorker':r['WarmupPerWorker'],'concurrency':r['Concurrency'],'mode':r['Mode'],'session':r['SessionMode'],'oracleFailures':r['OracleFailures'],'timingEligible':r['TimingComparisonEligible'],'manifestHashMatches':r['ContractSha256']==sha(manifest_path),'all35ManifestOraclesMatch':len(r['ExpectedResults'])==35 and all((r['ExpectedResults'][n]['Rows'],r['ExpectedResults'][n]['Digest'])==value for n,value in expect.items()),'database':r['Database'],'backendPids':r['BackendPids'],'gcIdentity':r['GcIdentity']}
 if provider=='sqlite':
  row['mappedImagesHashMatch']=all(sha(Path(name))==h for name,h in r['Database']['LoadedSQLiteImages'].items())
  row['baselineEngineHashMatch']=r['Database']['LoadedSQLiteImages'].get(str(TASK/'toolchains/native-db/sqlite/lib/libsqlite3.so'))=='ad64754d771625bc16b482962d453341f95e4619c3c42e501c5c93b38318e738'
  row['pragmasMatch']=r['Database']['Pragmas']=={'journal_mode':'wal','synchronous':2,'foreign_keys':1,'busy_timeout':5000}
 out['providers'].append(row)
out['serverStopped']=life['postgresServerStopped'];out['lifecycleStatus']=life['status'];out['sqliteSeedHashMatches']=life['sqliteSeedCopySha256']=='384c185015624e35579b95b49f03bd101af5d4936def6b611b0a588bd71da0bd'
out['identityChecksAllMatch']=all(out[k] for k in ['buildIdentityHashMatches','sourceArchiveHashMatches','buildScriptCurrentHashMatches','elfIdentityMatches','jarIdentityMatches','jdkReleaseHashMatches','applicationMetadataInJarMatches']) and all(c['matches'] for c in out['sourceChecks'].values()) and all(c['matches'] for c in out['dependencyChecks'].values()) and all(c['matches'] for c in out['metadataArchiveChecks'].values()) and out['elfMagic']=='7f454c46' and out['elfClass']==2 and out['elfMachine']==62 and out['applicationClassVersions']==[69]
out['dualProviderFiniteChecksVerified']=life['status']=='passed' and out['serverStopped'] is True and all(c['exitCode']==0 and c['logHashMatches'] for c in out['commands']) and all(r['receiptHashMatches'] and r['nativeAot'] is True and r['receiptElfMatches'] and r['verificationOnly'] is True and r['verifiedCasesPerWorker']==35 and r['warmupPerWorker']==64 and r['concurrency']==1 and r['mode']=='prepared' and r['session']=='persistent' and r['oracleFailures']==0 and r['timingEligible'] is False and r['manifestHashMatches'] and r['all35ManifestOraclesMatch'] for r in out['providers']) and all(out['providers'][0][k] for k in ['mappedImagesHashMatch','baselineEngineHashMatch','pragmasMatch'])
args.output.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['elfSha256','identityChecksAllMatch','dualProviderFiniteChecksVerified','formalLongRunAcceptanceCompleted','serverStopped']},ensure_ascii=False))
