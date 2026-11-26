#!/usr/bin/env python3
"""Narrow continuation after the original helper stopped at platform metadata.

Preserves the original helper and its refusal record. No permission changes,
process signals, root-directory deletion, or expansion of the accepted scope.
"""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys

WORK = Path('/workspace/scratch/2dfe9fb1bc53')
ROOTS = ['/workspace/scratch/fd78534029f7', '/workspace/scratch/4a65d70f0fe1', '/workspace/scratch/166b48a091b9']
HELPER = Path('/tmp/DB-Go-01-final-cleanup.py')
HELPER_SHA = '79088224364dd5b1321e83c30aa462a2e3bd79efc7e1a692b3638257b4cdabb7'
OUT = WORK / 'primary-resumed-cleanup-receipt.json'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def check_row(row):
    p = Path(row['path'])
    s = p.lstat()
    assert (s.st_dev, s.st_ino, stat.S_IFMT(s.st_mode), s.st_uid) == (row['device'], row['inode'], row['mode'], row['uid']), str(p)
    assert not p.is_symlink() and os.path.realpath(p) == str(p), str(p)

def main():
    assert not OUT.exists(), 'Inspect prior receipt before any retry'
    sys.dont_write_bytecode = True
    assert sha(HELPER) == HELPER_SHA
    spec = importlib.util.spec_from_file_location('original_cleanup', HELPER)
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    state = json.loads(Path(original.STATE).read_text())
    gate_path = Path(original.ACCEPTANCE)
    gate = json.loads(gate_path.read_text())
    assert state['helperSha256'] == HELPER_SHA and state['acceptanceSha256'] == sha(gate_path)
    assert state['archivalChecksPassed'] is True
    failed = json.loads((WORK / 'primary-cleanup-receipt.json').read_text())
    assert failed['status'] == 'refused-or-partially-completed' and failed['executed'] is True
    assert len(state['actions']) == 94 and not state['processActions']
    assert all(not Path(x).exists() for x in state['plan']['temporaryTargets'])
    for bare in original.BARES:
        assert not original.registered_paths(bare), bare
    verified = original.validate_gate(gate, HELPER_SHA, gate['cleanupInventory'], gate['cleanupInventorySha256'], state)
    inv_path = WORK / 'primary-residual-inventory.json'
    inv = json.loads(inv_path.read_text())
    assert [x['path'] for x in inv['roots']] == ROOTS
    targets = []
    preserved = []
    for root in inv['roots']:
        p = Path(root['path'])
        assert original.identity(str(p)) == state['plan']['targetIdentities'][str(p)]
        assert set(map(str, p.iterdir())) == {x['path'] for x in root['children']}
        for row in root['children']:
            check_row(row)
            if row['path'] == str(p / '.codex'):
                assert row['uid'] == 65534 and row['mode'] == stat.S_IFDIR
                preserved.append({'root': str(p), 'role': 'platform-owned control metadata', 'device': row['device'], 'inode': row['inode'], 'uid': row['uid']})
            else:
                assert row['uid'] == os.geteuid() and row['mode'] in (stat.S_IFDIR, stat.S_IFREG)
                targets.append(row)
    assert len(preserved) == 3 and len(targets) == 25
    assert shutil.rmtree.avoids_symlink_attacks
    original.mount_guard([x['path'] for x in targets])
    process = subprocess.run(['python3', str(WORK / 'additional_cleanup.py'), '--process-check-only'], cwd='/tmp', text=True, capture_output=True)
    observation = json.loads(process.stdout)
    (WORK / 'combined-process-check-before-resume.json').write_text(process.stdout)
    assert process.returncode == 0 and not observation['processes']['blockers']
    before = os.statvfs('/workspace/scratch')
    receipt = {'schemaVersion': 1, 'task': 'DB-Go-01 narrower project-content cleanup', 'startedAtUtc': now(), 'status': 'executing', 'executed': True, 'originalHelperStatus': failed['status'], 'originalRefusalPreserved': True, 'originalAcceptanceSha256': sha(gate_path), 'originalHelperSha256': HELPER_SHA, 'residualInventorySha256': sha(inv_path), 'verifiedOriginalSourceChecks': len(verified), 'actions': [], 'preservedPlatformMetadata': preserved, 'processSignalsSent': 0, 'permissionChangesByThisHelper': 0, 'platformPermissionsChanged': False, 'goModuleCacheCleanupReceiptSha256': sha(WORK / 'go-module-cache-cleanup.json'), 'filesystemAvailableBytesBefore': before.f_bavail * before.f_frsize}
    def save():
        OUT.write_text(json.dumps(receipt, indent=2) + '\n')
    save()
    try:
        for row in targets:
            check_row(row)
            original.mount_guard([row['path']])
            receipt['inProgress'] = row['path']
            save()
            if row['mode'] == stat.S_IFDIR:
                shutil.rmtree(row['path'])
            else:
                os.unlink(row['path'])
            receipt['actions'].append({'path': row['path'], 'action': 'removed-exact-task-child', 'finishedAtUtc': now()})
            receipt.pop('inProgress')
            save()
        remaining = []
        for root in ROOTS:
            children = list(Path(root).iterdir())
            assert len(children) == 1 and children[0].name == '.codex'
            remaining.append({'root': root, 'projectChildrenRemaining': 0, 'platformControlDirectoriesRetained': 1})
        after = os.statvfs('/workspace/scratch')
        receipt.update(status='completed-project-content-cleanup', finishedAtUtc=now(), allReviewedProjectContentAbsent=True, rootsRemoved=False, postCheck=remaining, filesystemAvailableBytesAfter=after.f_bavail * after.f_frsize, filesystemAvailableBytesDelta=after.f_bavail * after.f_frsize - receipt['filesystemAvailableBytesBefore'], byteAccounting='Observed filesystem availability change for this narrower continuation only; earlier worktree/cache removal is not counted again.')
        save()
        print(json.dumps({k: receipt[k] for k in ('status','allReviewedProjectContentAbsent','rootsRemoved','permissionChangesByThisHelper','processSignalsSent','filesystemAvailableBytesDelta')}))
    except Exception as error:
        receipt.update(status='refused-or-partially-completed', errorType=type(error).__name__, error=str(error), finishedAtUtc=now())
        save()
        raise

if __name__ == '__main__':
    main()
