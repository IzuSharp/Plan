#!/usr/bin/env python3
"""Stream-check/restore closed frame08 and common owner cleanup, then reconstruct verified artifact aliases."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath

from restore_artifact_aliases import restore_aliases

HERE=Path(__file__).resolve().parent
FIXED_SHA='b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c'


def bind_alias_sources(members, aliases, dependency_root=HERE):
    external={}
    index_path=dependency_root/'dependency-manifests/index.json'
    if any('dependencyManifest' in a for a in aliases):
        references=json.loads(index_path.read_text())['manifests']
        for reference in references:
            relative=PurePosixPath(reference['file'])
            if relative.is_absolute() or '..' in relative.parts or not relative.parts:
                raise ValueError('Unsafe dependency manifest path')
            content=(dependency_root/reference['file']).read_bytes()
            if hashlib.sha256(content).hexdigest()!=reference['sha256']:
                raise ValueError('Published dependency manifest identity differs')
            records=json.loads(content)['files'];by_path={m['path']:m for m in records}
            if len(by_path)!=len(records):
                raise ValueError('Duplicate dependency manifest members')
            key=relative.name
            if key in external:
                raise ValueError('Duplicate dependency manifest name')
            external[key]=by_path
    for alias in aliases:
        if 'dependencyManifest' in alias:
            member=external.get(alias['dependencyManifest'],{}).get(alias['source'])
        else:
            member=members.get(alias['source'])
        if member is None or (member['bytes'],member['sha256'])!=(alias['bytes'],alias['sha256']):
            raise ValueError('Alias source is not the selected or pinned prior payload: '+alias['source'])
        if 'mode' in alias and member['mode']!=alias['mode']:
            raise ValueError('Alias source mode differs from pinned payload: '+alias['source'])
    return {'currentPayloadAliasSources':sum('dependencyManifest' not in a for a in aliases),
            'priorPublishedAliasSources':sum('dependencyManifest' in a for a in aliases),
            'dependencyManifestIdentitiesChecked':len(external)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index',type=Path,default=HERE/'raw-archives/index.json')
    parser.add_argument('--extract',type=Path)
    parser.add_argument('--replace-existing',action='store_true')
    args=parser.parse_args()
    source=HERE/'streaming_archive.py'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=FIXED_SHA:
        raise ValueError('Reviewed streaming verifier identity changed')
    spec=importlib.util.spec_from_file_location('reviewed_archive06_streaming_verifier',source)
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
    bindings=bind_alias_sources(members,aliases)
    for entry in index['archives']:
        result=engine.verify_archive(raw,entry,args.extract,args.replace_existing)
        results.append(result);print(json.dumps(result),flush=True)
    if args.extract is not None:
        print(json.dumps(restore_aliases(args.extract,aliases)),flush=True)
    print(json.dumps(dict(passed=True,archives=len(results),members=len(members),
        packageAliasSourcesBound=True,aliasSourceBindings=bindings,
        extracted=args.extract is not None,noNewPerformanceCredit=True)),flush=True)


if __name__=='__main__':
    main()
