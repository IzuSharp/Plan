#!/usr/bin/env python3
"""Stream-check/restore closed tail06, then reconstruct verified package aliases."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from restore_package_aliases import restore_aliases

HERE=Path(__file__).resolve().parent
FIXED_SHA='b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index',type=Path,default=HERE/'raw-archives/index.json')
    parser.add_argument('--extract',type=Path)
    parser.add_argument('--replace-existing',action='store_true')
    args=parser.parse_args()
    source=HERE/'streaming_archive.py'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=FIXED_SHA:
        raise ValueError('Reviewed streaming verifier identity changed')
    spec=importlib.util.spec_from_file_location('reviewed_archive04_streaming_verifier',source)
    engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    index=json.loads(args.index.read_text());raw=args.index.parent
    members={};results=[]
    for entry in index['archives']:
        manifest=json.loads((raw/entry['expandedFileManifest']).read_text())
        for member in manifest['files']:
            if member['path'] in members:
                raise ValueError('Duplicate cross-package member: '+member['path'])
            members[member['path']]=member
    aliases=json.loads((HERE/'restore-alias-manifest.json').read_text())['aliases']
    for alias in aliases:
        member=members.get(alias['source'])
        if member is None or (member['bytes'],member['sha256'])!=(alias['bytes'],alias['sha256']):
            raise ValueError('Alias source is not the verified selected payload: '+alias['source'])
    for entry in index['archives']:
        result=engine.verify_archive(raw,entry,args.extract,args.replace_existing)
        results.append(result);print(json.dumps(result),flush=True)
    if args.extract is not None:
        print(json.dumps(restore_aliases(args.extract,aliases)),flush=True)
    print(json.dumps(dict(passed=True,archives=len(results),members=len(members),
        packageAliasSourcesBound=True,extracted=args.extract is not None,noNewPerformanceCredit=True)),flush=True)


if __name__=='__main__':
    main()
