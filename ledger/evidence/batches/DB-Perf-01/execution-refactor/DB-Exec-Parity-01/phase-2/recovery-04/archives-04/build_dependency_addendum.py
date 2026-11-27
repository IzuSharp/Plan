#!/usr/bin/env python3
"""Build the frozen six-package addendum without editing the original selection."""
import hashlib
import importlib.util
import json
from pathlib import Path
import os

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
NAME='prior-dapper-package-inputs06'
FIXED=HERE/'streaming_archive.py'
assert hashlib.sha256(FIXED.read_bytes()).hexdigest()=='b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c'
spec=importlib.util.spec_from_file_location('fixed_dependency_archive_engine',FIXED)
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
stage=HERE/'addendum-build-01'
engine.HERE,engine.ROOT,engine.OUTPUT=HERE,ROOT,stage
engine.NOTES=[
    'Exact six raw upstream nupkg used by the preserved baseline Dapper consumers, newly closing a historical raw-cache reproducibility gap; no full package cache tree is selected.',
    'Three compiler raw nupkg are already selected once in compiler-package-inputs06. Four baseline/integrated05 provider feed payloads already exist in archives01/02 and are restored via explicit SHA-bound aliases, not duplicated here.',
    'This addendum leaves the original eight-group selection.json bytes unchanged. All original raw, ELF, symbols and source remain in place. No performance credit or remote ref is created.',
]

def main():
    target=HERE/(NAME+'-receipt.json')
    if target.exists() and json.loads(target.read_text()).get('passed'):
        print(json.dumps({'alreadyVerified':NAME}));return
    selection=json.loads((HERE/'selection-addendum-01.json').read_text())
    if hashlib.sha256((HERE/'selection.json').read_bytes()).hexdigest()!=selection['baseSelectionSha256']:
        raise ValueError('Original frozen selection identity changed')
    stage.mkdir(exist_ok=False)
    engine.dump(stage/'selection.json',selection)
    engine.build(NAME)
    # Same-filesystem rename: no second large copy. Retain stage selection/index as history.
    (stage/'raw-archives'/NAME).rename(HERE/'raw-archives'/NAME)
    for suffix in ['entry','verification','receipt']:
        (stage/(NAME+'-'+suffix+'.json')).rename(HERE/(NAME+'-'+suffix+'.json'))
    engine.dump(stage/'relocation-receipt.json',{'passed':True,'method':'same-filesystem directory/file rename, no copied payload',
        'finalRawRoot':str(HERE/'raw-archives'/NAME),'finalReceipt':str(target),'retainedOriginalSelection':True,
        'finishedUtc':engine.utc(),'freeBytes':os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize})

if __name__=='__main__':main()
