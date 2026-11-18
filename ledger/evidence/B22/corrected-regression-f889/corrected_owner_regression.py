#!/usr/bin/env python3
"""Focused B21 transaction-retirement regression over corrected actual AOT."""
from pathlib import Path
import contextlib,json,subprocess,sys,time
root=Path('/workspace/scratch/58d2a6adf1c3')
source=root/'.worktree/Task-07-B22-corrected-f889-linux/NativeWeave'
sys.path.insert(0,str(source/'tests/Verification.EndToEnd'))
from harness import Database,Evidence,PostgresCluster,Service,admin,configuration,create,sha
artifact=root/'task07-runs/b22-observer-build-007-f889/artifacts/aot'
certificate=root/'task07-package-probe/final-002/tls/localhost.pem'
private_key=root/'task07-package-probe/final-002/tls/localhost.private.pem'
output=Path(sys.argv[1]).resolve()
evidence=Evidence(output,{'scope':'Only corrected CreateAsync non-transferred transaction, outbox Claim/Publish, and maintenance paths; old broad B21/API/fault acceptance is reused.','scriptSha256':sha(Path(__file__)),'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),'observerManifestSha256':sha(artifact.parent.parent/'manifest.json'),'artifactFiles':{str(p.relative_to(artifact)):sha(p)for p in artifact.rglob('*')if p.is_file()},'fullB22Acceptance':False})

def retirement(path,label):
    rows=[json.loads(line)for line in(path/'observations.jsonl').read_text().splitlines()]
    before=next(row for row in rows if row['phase']=='application-main-returned-before-finalizers')
    final=rows[-1]
    evidence.check(label+'-before-explicit-finalizers',all(all(value==0 for value in counts)for counts in before['databaseNativeOwners'].values()),counts=before['databaseNativeOwners'])
    evidence.check(label+'-final-native-and-observer',final['phase']=='observer-stop' and final['observerFailures']==0 and all(all(value==0 for value in counts)for counts in final['databaseNativeOwners'].values()),counts=final['databaseNativeOwners'])

try:
    for provider in ('sqlite','postgresql'):
        with evidence.case(provider+'-corrected-owner-paths')as path:
            path.mkdir()
            context=PostgresCluster(root/'task07-toolchain/postgres/bin',path/'postgres')if provider=='postgresql'else contextlib.nullcontext(None)
            with context as cluster:
                database=cluster.database()if cluster else str(path/'application.sqlite')
                config,token=configuration(provider,database,path,tls=(certificate,private_key))
                sql=Database(provider,database,str(cluster.binary/'psql')if cluster else None)
                modules={name:str(artifact/('libnw_database_'+name+'.so'))for name in(('sqlite','postgresql')if cluster else('sqlite',))}
                command=['env','NW_B22_DB_MODULES='+json.dumps(modules),str(artifact/'NativeWeave.Reference.TaskService')]
                with Service(command,config,path/'service',observed=True,http2=True,certificate=certificate)as service:
                    status,body,_=create(service,token,'owner-corrected','retirement')
                    evidence.check('create-confirmed',status==201)
                    operation=json.loads(body)['operationId']
                    for number in range(3):
                        reply=create(service,token,'owner-corrected','retirement')
                        evidence.check('exact-replay-'+str(number),reply[0]==201 and reply[1]==body)
                    evidence.check('different-hash-conflict',create(service,token,'owner-corrected','changed')[0]==409)
                    evidence.check('conflict-preserves-winner',create(service,token,'owner-corrected','retirement')[1]==body)
                    evidence.check('independent-operation-cardinality',int(sql.scalar('SELECT COUNT(*) FROM operations'))==1)
                retirement(path/'service','http-create-replay-conflict')
                def operator(option,label):
                    target=path/label
                    observed=['env','NW_B22_OBSERVATIONS='+str(target/'observations.jsonl'),*command]
                    admin(observed,config,option,target)
                    retirement(target,label)
                operator('--outbox-once','publish')
                evidence.check('outbox-acknowledged',int(sql.scalar('SELECT COUNT(*) FROM outbox WHERE delivery_state<>2'))==0)
                event=sql.scalar("SELECT event_id FROM outbox WHERE operation_id='"+operation+"'")
                consumer=Database('sqlite',config['consumerDatabase'])
                evidence.check('consumer-first-effect',int(consumer.scalar("SELECT effects FROM receipts WHERE event_id='"+event+"'"))==1)
                sql.sql("UPDATE outbox SET delivery_state=0,available_at=0,lease_until=0,completed_at=0 WHERE event_id='"+event+"'")
                operator('--outbox-once','redeliver')
                evidence.check('consumer-deduplicated-effect',int(consumer.scalar("SELECT effects FROM receipts WHERE event_id='"+event+"'"))==1 and int(consumer.scalar("SELECT delivery_attempts FROM receipts WHERE event_id='"+event+"'"))==2)
                old=int(time.time()*1000)-8*24*60*60*1000
                sql.sql('UPDATE operations SET completed_at='+str(old))
                sql.sql('UPDATE outbox SET completed_at='+str(old))
                operator('--maintenance-once','maintenance')
                evidence.check('expired-confirmed-operation-removed',int(sql.scalar('SELECT COUNT(*) FROM operations'))==0 and int(sql.scalar('SELECT COUNT(*) FROM outbox'))==0)
                evidence.check('consumer-effect-survives-maintenance',int(consumer.scalar('SELECT SUM(effects) FROM receipts'))==1)
    evidence.record['status']='passed'
except BaseException as error:
    evidence.record.update(status='failed',failureType=type(error).__name__)
    raise
finally:
    evidence.save();evidence.timeline.close()
    print(json.dumps({'status':evidence.record['status'],'receipt':str(output/'receipt.json')}),flush=True)
