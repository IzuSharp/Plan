#!/usr/bin/env python3
"""Remove only inventoried stale CLR endpoints and task cleanup controls."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import stat

WORK = Path('/workspace/scratch/2dfe9fb1bc53')
OUT = WORK / 'residual-temporary-cleanup-receipt.json'

def fingerprint(path):
    s = Path(path).lstat()
    return {'path':str(path),'device':s.st_dev,'inode':s.st_ino,'uid':s.st_uid,'modeBits':s.st_mode,'mtimeNs':s.st_mtime_ns,'ctimeNs':s.st_ctime_ns,'bytes':s.st_size}

def main():
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled')
    assert not OUT.exists()
    inv = json.loads((WORK/'residual-temporary-inventory.json').read_text())
    fifos = inv['fifos']
    assert len(fifos)==12
    for row in fifos:
        now=fingerprint(row['path'])
        assert all(now[k]==row[k] for k in now)
        assert stat.S_ISFIFO(now['modeBits']) and now['uid']==os.getuid()
    identities={(x['device'],x['inode']) for x in fifos}
    lifetimes={(x['encodedPid'],x['encodedStartTicks']) for x in fifos}
    observed=[]
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit(): continue
        try:
            raw=(proc/'stat').read_text(); fields=raw[raw.rfind(')')+2:].split()
            name=(proc/'comm').read_text().strip()
            assert (int(proc.name),int(fields[19])) not in lifetimes
            assert name not in {'dotnet','go','MSBuild','postgres','pg_ctl','gcc','clang','cargo','rustc'}
            for fd in (proc/'fd').iterdir():
                try:
                    s=fd.stat(); assert (s.st_dev,s.st_ino) not in identities
                except FileNotFoundError: pass
            observed.append({'pid':int(proc.name),'name':name,'startTicks':int(fields[19])})
        except (FileNotFoundError,ProcessLookupError): pass
    telemetry=Path('/home/agent/.config/go/telemetry')
    expected={'local/upload.token','local/go@go1.27.4-go1.27.4-linux-amd64-2026-11-26.v1.count','local/weekends'}
    files=[p for p in telemetry.rglob('*') if p.is_file()]
    assert {str(p.relative_to(telemetry)) for p in files}==expected
    telemetry_rows=[]
    for p in files:
        assert not p.is_symlink() and str(p.resolve())==str(p)
        row=fingerprint(p); assert row['uid']==os.getuid() and stat.S_ISREG(row['modeBits'])
        row['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();telemetry_rows.append(row)
    controls=[]
    for name in ['DB-Go-01-final-cleanup-state.json','DB-Go-01-final-cleanup-acceptance.json']:
        p=Path('/tmp')/name; expected_sha=hashlib.sha256((WORK/('preserved-'+name)).read_bytes()).hexdigest()
        row=fingerprint(p); assert row['uid']==os.getuid() and stat.S_ISREG(row['modeBits'])
        assert hashlib.sha256(p.read_bytes()).hexdigest()==expected_sha;row['sha256']=expected_sha;controls.append(row)
    p=Path('/tmp/DB-Go-01-final-cleanup.py');row=fingerprint(p)
    row['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();assert row['sha256']=='79088224364dd5b1321e83c30aa462a2e3bd79efc7e1a692b3638257b4cdabb7'
    assert row['uid']==os.getuid() and stat.S_ISREG(row['modeBits']);controls.append(row)
    receipt={'schemaVersion':1,'task':'DB-Go-01 residual cleanup','startedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observedProcesses':observed,'staleFifos':fifos,'telemetryRecreatedByOfficialGoCacheCleanup':telemetry_rows,'preservedThenRemovedPrimaryControls':controls,'actions':[],'processSignalsSent':0,'platformPermissionsChanged':False}
    def save(): OUT.write_text(json.dumps(receipt,indent=2)+'\n')
    save()
    for row in [*fifos,*telemetry_rows,*controls]:
        current=fingerprint(row['path']);assert all(current[k]==row[k] for k in current)
        os.unlink(row['path']);receipt['actions'].append({'path':row['path'],'action':'unlinked-exact-reviewed-file'});save()
    directories=[x['path'] for x in inv['advertisingDirectoriesEmptyRemovalOrder']]
    wrappers=[str(telemetry/'local'),str(telemetry/'upload'),str(telemetry),str(telemetry.parent)]
    for path in directories+wrappers:
        p=Path(path);assert not p.is_symlink() and str(p.resolve())==str(p) and p.stat().st_uid==os.getuid()
        if path in directories:
            row=next(x for x in inv['advertisingDirectoriesEmptyRemovalOrder'] if x['path']==path)
            current=fingerprint(p);assert current['device']==row['device'] and current['inode']==row['inode'] and current['modeBits']==row['modeBits']
        assert not list(p.iterdir());p.rmdir();receipt['actions'].append({'path':path,'action':'removed-empty-reviewed-directory'});save()
    receipt.update(status='completed',finishedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),allResidualTargetsAbsent=True)
    save();print(json.dumps({'status':receipt['status'],'actions':len(receipt['actions']),'fifosRemoved':12,'recreatedTelemetryFilesRemoved':3,'primaryControlsRemoved':3,'emptyDirectoriesRemoved':6}))

if __name__=='__main__': main()
