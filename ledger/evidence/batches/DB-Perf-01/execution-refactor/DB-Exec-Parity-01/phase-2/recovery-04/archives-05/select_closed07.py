#!/usr/bin/env python3
"""Read exact closed 07 path metadata only; no compression or big-file hashing."""
import datetime
import json
import os
from pathlib import Path
import stat

ROOT = Path('/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01')
HERE = Path(__file__).parent
groups = {}
excluded = []
aliases = []
all_files = set()

def add(group,p):
    assert p.is_relative_to(ROOT) and not p.is_symlink()
    s = p.lstat()
    assert stat.S_ISREG(s.st_mode)
    rel = str(p.relative_to(ROOT))
    if rel in all_files:
        return
    all_files.add(rel)
    groups.setdefault(group,[]).append({'path':rel,'bytes':s.st_size,'mode':stat.S_IMODE(s.st_mode),'mtimeNs':s.st_mtime_ns})

def skip(p,reason):
    excluded.append({'path':str(p.relative_to(ROOT)),'reason':reason})

def walk(group,base,skip_dirs=(),skip_files=None):
    assert base.is_dir()
    for parent,dirs,files in os.walk(base,followlinks=False):
        parent=Path(parent)
        keep=[]
        for n in sorted(dirs):
            p=parent/n
            assert not p.is_symlink()
            if n in set(skip_dirs)|{'__pycache__','postgres-data','packages','sdk-cache'}:
                skip(p,'rebuildable physical fixture/cache or redundant intermediates; original remains')
            else:keep.append(n)
        dirs[:]=keep
        for n in sorted(files):
            p=parent/n
            assert not p.is_symlink()
            if n.endswith(('.pyc','.sqlite','.sqlite-wal','.sqlite-shm','.db','.db-wal','.db-shm')):
                skip(p,'rebuildable physical database or bytecode; original remains')
            elif skip_files and skip_files(p):
                continue
            else:add(group,p)

def native_alias(destination,provider):
    d=json.loads((ROOT/f'consumers/pull-local07-{provider}/korda-workload/build-receipt.json').read_text())
    name='libnw_database_'+provider+'.so'
    aliases.append({'source':f'consumers/tail06-{provider}/korda-workload/out/{name}','destination':str(destination.relative_to(ROOT)),'sha256':d['nativeImages'][name],'bytes':destination.stat().st_size,'sourceArchive':'archives-04/ordinary-consumers06','sourceCommit':'ded73d7cd90cb692bea554c5e780df0ca9e05e3f','proofKind':'actual receipt identity and published expanded member; final pack must verify the exact source/destination bytes'})
    skip(destination,'unchanged native bytes reused through exact SHA/size restore alias; original remains')

def experiment_skip(p):
    if p.name in ('libnw_database_sqlite.so','libnw_database_postgresql.so') and '/correctness-02/publish/' in str(p):
        native_alias(p,'sqlite' if p.name.endswith('_sqlite.so') else 'postgresql')
        return True
    return False

walk('closed-evidence07',ROOT/'experiments/pull-local-07',skip_files=experiment_skip)
for provider in ('sqlite','postgresql'):
    base=ROOT/f'consumers/pull-local07-{provider}/korda-workload'
    def consumer_skip(p):
        if p.name == 'libnw_database_'+provider+'.so':
            native_alias(p,provider)
            return True
        return False
    walk('ordinary-consumers07',base,skip_dirs=('bin','obj'),skip_files=consumer_skip)
    obj=base/'obj'
    allowed={'.json','.props','.targets','.rsp','.exports','.cs','.editorconfig','.txt'}
    for parent,dirs,files in os.walk(obj,followlinks=False):
        dirs[:]=[d for d in dirs if d not in ('generated','ref','refint')]
        for name in files:
            p=Path(parent)/name
            if p.suffix in allowed or name in ('DbPerf.Korda.dll','DbPerf.Korda.pdb'):
                add('ordinary-consumers07',p)
    walk('actual-packages07',ROOT/f'builds/pull-local07-{provider}/package-consumer')
    b=json.loads((base/'build-receipt.json').read_text())
    name='Korda.Database.Sqlite' if provider=='sqlite' else 'Korda.Database.PostgreSql'
    package=Path(b['package'])
    aliases.append({'source':str(package.relative_to(ROOT)),'destination':str(Path(b['packages'][name+'/0.1.0-parity07.1']['rawArchivePath']).relative_to(ROOT)),'sha256':b['packageSha256'],'bytes':package.stat().st_size,'sourceArchive':'supplement05/actual-packages07','proofKind':'actual build/binding receipt; final closure must verify both raw paths'})

for name in ('run_verified_mixed_cell07.py','freeze_verified_mixed_inputs07.py'):
    add('support07',ROOT/'experiments/recovery'/name)
for name in ('remaining-space-review-07','retained05-gap-summary-01','legacy-pg-retirement-subset07','legacy-pg-retirement-subset07-independent-review-01','plan-checkout-filter-review-07'):
    walk('support07',ROOT/'experiments/recovery'/name)
for name in ('pull-local07-sqlite-intermediates-01','pull-local07-postgresql-intermediates-01','archive04-ci-cancelled-01'):
    walk('support07',ROOT/'observations/recovery'/name)

summary={name:{'fileCount':len(files),'expandedBytes':sum(x['bytes'] for x in files)} for name,files in groups.items()}
total=sum(x['expandedBytes'] for x in summary.values())
fs=os.statvfs(ROOT)
result={'task':'DB-Exec-Parity-01','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'selection-budget-not-packed-not-published','groups':groups,'summary':summary,'selectedFileCount':len(all_files),'expandedBytes':total,'exclusions':excluded,'restoreAliasDraft':aliases,'sourceBundle':{'repository':'Korda','prerequisite':'2ea67ce1902f330679c3ebff4d6d5733be20f69c','tip':'645cfa5f184d65a67fa71455a5f7271ee8469309','commits':['3fb88246b2fee303578f0527970e3d084d89ab40','c5b1ddb48e4e4c16d8b61404d2a5a5d032fc350b','8d400ecc02990a9c0b4b6056973a93326c214aa8','645cfa5f184d65a67fa71455a5f7271ee8469309'],'state':'planned-thin-bundle-and-net-patch; not created yet','conservativeAdditionalBudgetBytes':1048576},'compressionEstimate':{'estimatedBytesLow':25000000,'estimatedBytesHigh':45000000,'scope':'planning estimate based on retained ELF/DBG/text plus already-zipped nupkg; no new compression sample or actual compressed result claimed','conservativeUpperBudgetBytes':total+2097152},'freeBytesObserved':fs.f_bavail*fs.f_frsize,'futureClosureAdditions':['independent old2 retirement review and actual config/receipt when completed','final source thin bundle and restore/alias metadata','root publication/checkpoint receipts if closed before freeze'],'dependencies':['archives-01 baseline/Dapper/runtime/toolchain','archives-02 integrated05 actual outputs and native build identities','archives-03 reviewed wrapper/proc-observer support','archives-04 raw compiler-package gap closure and reused same-byte native images'],'noDatabaseStarted':True,'noArchiveCompressed':True,'noBigFileHash':True}
(HERE/'selection-final-plan.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['summary','selectedFileCount','expandedBytes','compressionEstimate','freeBytesObserved']}))
