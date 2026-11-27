#!/usr/bin/env python3
"""Restore exact raw-package path aliases after payload restore; never overwrite."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile


def contained(root, name):
    relative=PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('Unsafe alias member path: '+name)
    current=root
    if root.is_symlink() or root.resolve()!=root:
        raise ValueError('Alias root must be a real resolved directory')
    for part in relative.parts:
        current=current/part
        if current.is_symlink():
            raise ValueError('Alias path contains a symlink: '+str(current))
    if not current.resolve().is_relative_to(root):
        raise ValueError('Alias path escaped restore root')
    return current


def check_file(path, expected):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    with os.fdopen(fd,'rb') as f:
        before=os.fstat(f.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size!=expected['bytes']:
            raise ValueError('Alias file kind/size differs: '+str(path))
        digest=hashlib.file_digest(f,'sha256').hexdigest()
        after=os.fstat(f.fileno())
    if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):
        raise ValueError('Alias file changed while reading: '+str(path))
    if digest!=expected['sha256']:
        raise ValueError('Alias SHA256 differs: '+str(path))


def restore_aliases(root, aliases, check_only=False):
    root=Path(root).absolute()
    if not root.is_dir():
        raise ValueError('Restore payloads before creating package aliases')
    planned=[];destinations=set()
    # Complete preflight before creating any destination directory or file.
    for entry in aliases:
        if entry['destination'] in destinations:
            raise ValueError('Duplicate alias destination')
        destinations.add(entry['destination'])
        source=contained(root,entry['source']);destination=contained(root,entry['destination'])
        check_file(source,entry)
        if destination.exists():
            check_file(destination,entry)
        planned.append((entry,source,destination,destination.exists()))
    result=[]
    for entry,source,destination,exists in planned:
        if check_only:
            if not exists:
                raise ValueError('Required package alias is missing: '+str(destination))
            result.append(dict(destination=entry['destination'],action='verified-existing'))
            continue
        if exists:
            check_file(contained(root,entry['destination']),entry)
            result.append(dict(destination=entry['destination'],action='verified-existing'))
            continue
        # Check containment before mkdir, and again after it, including internal links.
        contained(root,entry['destination'])
        destination.parent.mkdir(parents=True,exist_ok=True)
        contained(root,entry['destination'])
        check_file(contained(root,entry['source']),entry)
        fd,temp=tempfile.mkstemp(prefix='.package-alias-',dir=destination.parent)
        temporary=Path(temp)
        try:
            with os.fdopen(fd,'wb') as target, source.open('rb') as original:
                for chunk in iter(lambda:original.read(1024*1024),b''):
                    target.write(chunk)
                target.flush();os.fsync(target.fileno())
            check_file(temporary,entry)
            os.chmod(temporary,0o644)
            contained(root,entry['destination'])
            # Atomic no-clobber installation of an independently byte-copied inode.
            # The source/feed inode is never hardlinked to the mutable cache.
            try:
                os.link(temporary,destination,follow_symlinks=False)
                action='created-independent-copy'
            except FileExistsError:
                check_file(contained(root,entry['destination']),entry)
                action='verified-concurrent-identical-copy'
            check_file(destination,entry)
            result.append(dict(destination=entry['destination'],source=entry['source'],action=action,
                               bytes=entry['bytes'],sha256=entry['sha256']))
        finally:
            temporary.unlink(missing_ok=True)
    return dict(passed=True,checkOnly=check_only,aliases=result,
                scope='Per-file independently verified copies; no differing destination overwritten. Not a whole-archive atomic transaction; no concurrent destination-tree mutation is assumed.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,default=Path(__file__).with_name('restore-alias-manifest.json'))
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args()
    manifest=json.loads(args.manifest.read_text())
    print(json.dumps(restore_aliases(args.root,manifest['aliases'],args.check_only),indent=2))


if __name__=='__main__':
    main()
