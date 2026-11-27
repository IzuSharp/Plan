#!/usr/bin/env python3
"""Small alias dependency identity controls; no payload restore or measurement."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from restore_archive04 import bind_alias_sources

HERE=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.absolute();out.mkdir(exist_ok=False)
    checks=[]
    def check(name,passed):
        checks.append({'name':name,'passed':bool(passed)})
        if not passed:raise AssertionError(name)
    def reject(name,call):
        try:call()
        except (ValueError,OSError,KeyError):check(name,True)
        else:check(name,False)
    member={'path':'feed/current.nupkg','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}
    alias={'source':member['path'],'destination':'cache/current.nupkg','bytes':member['bytes'],'sha256':member['sha256']}
    current={member['path']:member}
    check('current-selected-payload-bound',bind_alias_sources(current,[alias],out)['currentPayloadAliasSources']==1)
    reject('missing-current-source-rejected',lambda:bind_alias_sources({},[alias],out))
    bad=copy.deepcopy(alias);bad['bytes']+=1
    reject('current-source-size-mismatch-rejected',lambda:bind_alias_sources(current,[bad],out))
    deps=out/'dependency-manifests';deps.mkdir();mp=deps/'prior.json';ip=deps/'index.json'
    prior={'path':'feed/prior.nupkg','bytes':3,'sha256':hashlib.sha256(b'def').hexdigest()}
    pa={'source':prior['path'],'destination':'cache/prior.nupkg','bytes':3,'sha256':prior['sha256'],'dependencyManifest':'prior.json'}
    def reset(records=None,filename='dependency-manifests/prior.json'):
        content=(json.dumps({'files':records if records is not None else [prior]})+'\n').encode();mp.write_bytes(content)
        ip.write_text(json.dumps({'manifests':[{'file':filename,'sha256':hashlib.sha256(content).hexdigest(),'sourceCommit':'synthetic-control-only'}]})+'\n')
    reset();result=bind_alias_sources(current,[alias,pa],out)
    check('pinned-prior-and-current-bound-separately',result=={'currentPayloadAliasSources':1,'priorPublishedAliasSources':1,'dependencyManifestIdentitiesChecked':1})
    mp.write_text('changed');reject('changed-prior-manifest-hash-rejected',lambda:bind_alias_sources(current,[pa],out))
    reset();bad=copy.deepcopy(pa);bad['sha256']='0'*64
    reject('prior-source-sha-mismatch-rejected',lambda:bind_alias_sources(current,[bad],out))
    bad=copy.deepcopy(pa);bad['dependencyManifest']='missing.json'
    reject('unbound-prior-manifest-rejected',lambda:bind_alias_sources(current,[bad],out))
    reset([prior,prior]);reject('duplicate-prior-members-rejected',lambda:bind_alias_sources(current,[pa],out))
    reset(filename='../outside.json');reject('dependency-path-traversal-rejected',lambda:bind_alias_sources(current,[pa],out))
    reset();bad=copy.deepcopy(pa);bad.pop('dependencyManifest')
    reject('prior-source-cannot-impersonate-current-payload',lambda:bind_alias_sources(current,[bad],out))
    # Only small JSON manifests, not actual package data, are read here.
    actual_members={}
    for name in ('ordinary-consumers06','diagnostic-consumers06'):
        doc=json.loads((HERE/'raw-archives'/name/'expanded-file-manifest.json').read_text())
        actual_members.update({m['path']:m for m in doc['files']})
    actual_aliases=json.loads((HERE/'restore-alias-manifest.json').read_text())['aliases']
    actual=bind_alias_sources(actual_members,actual_aliases,HERE)
    check('actual-six-current-four-prior-aliases-bound',actual=={'currentPayloadAliasSources':6,'priorPublishedAliasSources':4,'dependencyManifestIdentitiesChecked':2})
    result={'task':'DB-Exec-Parity-01','passed':all(x['passed'] for x in checks),'checks':checks,
        'fixtureOnlyExceptReadOnlyActualMetadataBinding':True,'actualPackageFilesReadOrChanged':False,
        'workloadExecuted':False,'actualBindings':actual,
        'sourceSha256':hashlib.sha256((HERE/'restore_archive04.py').read_bytes()).hexdigest(),
        'actualAliasManifestSha256':hashlib.sha256((HERE/'restore-alias-manifest.json').read_bytes()).hexdigest()}
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'checks':len(checks),'actualBindings':actual}))

if __name__=='__main__':main()
