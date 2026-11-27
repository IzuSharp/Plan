#!/usr/bin/env python3
"""Tiny owned fixtures only; no database, workload or bulk archive extraction."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from restore_package_aliases import restore_aliases


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.absolute()
    if out.exists():raise ValueError('Fresh control directory required')
    out.mkdir(parents=True);checks=[]
    def check(name,passed):
        checks.append(dict(name=name,passed=bool(passed)))
        if not passed:raise AssertionError(name)
    def rejected(name,action):
        try:action()
        except (ValueError,OSError):check(name,True)
        else:check(name,False)
    def fixture(name):
        root=out/name;root.mkdir();(root/'feed').mkdir();payload=b'synthetic nupkg bytes; not an actual package\n'
        (root/'feed/a.nupkg').write_bytes(payload)
        entry=dict(source='feed/a.nupkg',destination='cache/a/a.nupkg',bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())
        return root,entry
    root,e=fixture('positive');r=restore_aliases(root,[e]);target=root/e['destination']
    check('missing-alias-created-byte-identically',r['passed'] and target.read_bytes()==(root/e['source']).read_bytes())
    check('cache-copy-has-independent-inode',target.stat().st_ino!=(root/e['source']).stat().st_ino)
    ino=target.stat().st_ino;r=restore_aliases(root,[e]);check('existing-identical-alias-idempotent',r['passed'] and target.stat().st_ino==ino)
    check('check-only-existing-passes',restore_aliases(root,[e],True)['passed'])
    root,e=fixture('missing-check');rejected('check-only-missing-fails',lambda:restore_aliases(root,[e],True));check('check-only-no-created-parent',not (root/'cache').exists())
    root,e=fixture('bad-source');(root/e['source']).write_bytes(b'changed');rejected('changed-source-fails',lambda:restore_aliases(root,[e]));check('bad-source-no-created-parent',not (root/'cache').exists())
    root,e=fixture('bad-destination');(root/'cache/a').mkdir(parents=True);target=root/e['destination'];target.write_bytes(b'preserve user bytes');old=target.read_bytes();rejected('different-existing-destination-fails',lambda:restore_aliases(root,[e]));check('different-existing-destination-preserved',target.read_bytes()==old)
    root,e=fixture('outside-link');outside=out/'outside';outside.mkdir();(root/'cache').symlink_to(outside,target_is_directory=True);rejected('outside-parent-symlink-fails',lambda:restore_aliases(root,[e]));check('outside-subdirectory-never-created',not (outside/'a').exists())
    root,e=fixture('inside-link');(root/'internal').mkdir();(root/'cache').symlink_to(root/'internal',target_is_directory=True);rejected('inside-parent-symlink-fails',lambda:restore_aliases(root,[e]));check('inside-target-never-created',not (root/'internal/a').exists())
    root,e=fixture('traversal');e['destination']='../escaped.nupkg';rejected('parent-traversal-fails',lambda:restore_aliases(root,[e]));check('no-traversal-output',not (out/'escaped.nupkg').exists())
    root,e=fixture('batch-preflight');bad=copy.deepcopy(e);bad['destination']='other/bad.nupkg';bad['sha256']='0'*64
    rejected('all-aliases-preflight-before-first-write',lambda:restore_aliases(root,[e,bad]));check('valid-first-alias-not-created-on-later-error',not (root/'cache').exists())
    root,e=fixture('duplicate');rejected('duplicate-destination-fails',lambda:restore_aliases(root,[e,e]));check('duplicate-preflight-no-write',not (root/'cache').exists())
    root,e=fixture('same-path');e['destination']=e['source'];rejected('source-destination-same-path-fails',lambda:restore_aliases(root,[e]));check('same-path-source-preserved',hashlib.sha256((root/e['source']).read_bytes()).hexdigest()==e['sha256'])
    root,e=fixture('existing-hardlink');(root/'cache/a').mkdir(parents=True);(root/e['destination']).hardlink_to(root/e['source'])
    rejected('existing-source-hardlink-fails',lambda:restore_aliases(root,[e]));rejected('check-only-source-hardlink-fails',lambda:restore_aliases(root,[e],True));check('rejected-hardlink-source-preserved',hashlib.sha256((root/e['source']).read_bytes()).hexdigest()==e['sha256'])
    result=dict(task='DB-Exec-Parity-01',passed=all(x['passed'] for x in checks),checks=checks,
        fixtureOnly=True,workloadExecuted=False,actualPackageAliasesWritten=False,
        sourceSha256=hashlib.sha256(Path(__file__).with_name('restore_package_aliases.py').read_bytes()).hexdigest())
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=result['passed'],checks=len(checks))))


if __name__=='__main__':main()
