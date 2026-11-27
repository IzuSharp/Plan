#!/usr/bin/env python3
"""Tiny native/package alias controls; no task payload copied."""
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import restore_artifact_aliases as alias

HERE=Path(__file__).resolve().parent
OUT=HERE/'alias-mode-controls-01'
OUT.mkdir(exist_ok=False)
ROOT=OUT/'fixture'
ROOT.mkdir()
(ROOT/'source').mkdir()
native=ROOT/'source/native.so';native.write_bytes(b'synthetic shared image');native.chmod(0o744)
package=ROOT/'source/package.nupkg';package.write_bytes(b'synthetic package bytes');package.chmod(0o644)
entries=[{'source':'source/native.so','destination':'out/native.so','bytes':native.stat().st_size,'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'mode':0o744},{'source':'source/package.nupkg','destination':'cache/package.nupkg','bytes':package.stat().st_size,'sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'mode':0o644}]
checks=[]
def check(name,fn,rejected=False):
    try:fn()
    except (ValueError,OSError) as e:
        if not rejected:raise
        checks.append({'name':name,'passed':True,'rejection':str(e)})
    else:
        if rejected:raise AssertionError('Expected rejection: '+name)
        checks.append({'name':name,'passed':True})
def require(v):
    if not v:raise ValueError('Control failed')

check('create-independent-native0744-and-package0644',lambda:alias.restore_aliases(ROOT,entries))
check('native-mode-and-inode',lambda:require(stat.S_IMODE((ROOT/'out/native.so').stat().st_mode)==0o744 and (ROOT/'out/native.so').stat().st_ino!=native.stat().st_ino))
check('package-mode-and-inode',lambda:require(stat.S_IMODE((ROOT/'cache/package.nupkg').stat().st_mode)==0o644 and (ROOT/'cache/package.nupkg').stat().st_ino!=package.stat().st_ino))
check('repeat-accepts-independent-identical-files',lambda:alias.restore_aliases(ROOT,entries))
check('check-only-validates-both-modes',lambda:alias.restore_aliases(ROOT,entries,True))
(ROOT/'out/native.so').chmod(0o644)
check('reject-existing-native-wrong-mode',lambda:alias.restore_aliases(ROOT,entries),True)
(ROOT/'out/native.so').chmod(0o744)
native.chmod(0o644)
check('reject-source-native-wrong-mode',lambda:alias.restore_aliases(ROOT,entries),True)
native.chmod(0o744)
for mode in (0o4744,0o2744,0o1744,0o777,0o600,True):
    changed=copy.deepcopy(entries);changed[0]['mode']=mode
    check('reject-unlisted-mode-'+str(mode),lambda:alias.restore_aliases(ROOT,changed),True)
changed=copy.deepcopy(entries);changed[0]['destination']='never-created/native.so';changed[1]['mode']=0o4744
check('all-aliases-preflight-before-writing',lambda:alias.restore_aliases(ROOT,changed),True)
check('no-first-destination-after-later-rejection',lambda:require(not (ROOT/'never-created').exists()))
(ROOT/'hardlink.so').hardlink_to(native)
changed=[dict(entries[0],destination='hardlink.so')]
check('reject-existing-source-hardlink',lambda:alias.restore_aliases(ROOT,changed),True)
(ROOT/'symlink.so').symlink_to(native)
changed=[dict(entries[0],destination='symlink.so')]
check('reject-symlink-destination',lambda:alias.restore_aliases(ROOT,changed),True)
(ROOT/'different.so').write_bytes(b'wrong')
changed=[dict(entries[0],destination='different.so')]
check('reject-differing-existing-bytes-without-overwrite',lambda:alias.restore_aliases(ROOT,changed),True)
check('differing-bytes-remain',lambda:require((ROOT/'different.so').read_bytes()==b'wrong'))
(ROOT/'linked-parent').symlink_to(OUT,target_is_directory=True)
changed=[dict(entries[0],destination='linked-parent/no-created/native.so')]
check('reject-parent-link-before-mkdir',lambda:alias.restore_aliases(ROOT,changed),True)
check('outside-directory-not-created',lambda:require(not (OUT/'no-created').exists()))
receipt={'task':'DB-Exec-Parity-01','passed':True,'checkCount':len(checks),'checks':checks,'helperSha256':hashlib.sha256((HERE/'restore_artifact_aliases.py').read_bytes()).hexdigest(),'controlSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'actualTaskPayloadCopied':False,'scope':'Synthetic file bytes only; exact optional permission mode is the only alias behavior extension'}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='checks'}))
