#!/usr/bin/env python3
"""Verify a published evidence subtree with a bounded, disposable Git cache."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cached-only', action='store_true',
                        help='Require every published blob already present; disable lazy fetching')
    args = parser.parse_args()
    repo, source, output = [p.resolve() for p in (args.repo, args.manifest, args.output)]
    require(len(args.commit) == 40 and all(c in '0123456789abcdef' for c in args.commit), 'Invalid commit')
    require(not output.exists(), 'Output must be new')
    output.mkdir(parents=True)
    manifest_bytes = source.read_bytes()
    manifest = json.loads(manifest_bytes)
    require(manifest['task'] == 'DB-Exec-Parity-01', 'Wrong task')
    prefix = manifest['targetPrefix'].rstrip('/')
    require(prefix.startswith('ledger/evidence/batches/DB-Perf-01/'), 'Wrong target prefix')
    require('..' not in PurePosixPath(prefix).parts, 'Unsafe target prefix')
    entries = manifest['files']
    require(len({e['path'] for e in entries}) == len(entries), 'Duplicate file')
    for entry in entries:
        p = PurePosixPath(entry['path'])
        require(not p.is_absolute() and '..' not in p.parts, 'Unsafe file path')
        require(entry['mode'] == '100644', 'Unexpected file mode')
        require(type(entry['bytes']) is int and entry['bytes'] >= 0, 'Invalid byte length')
        require(entry['bytes'] <= 8 * 1024 * 1024, 'One blob exceeds the requested group payload limit')

    def git(*argv):
        return subprocess.check_output(['git', *argv], cwd=repo)

    tree = git('rev-parse', args.commit + '^{tree}').decode().strip()
    subtree = git('rev-parse', args.commit + ':' + prefix).decode().strip()
    actual = {}
    for record in git('ls-tree', '-rz', args.commit, '--', prefix).split(b'\0'):
        if record:
            metadata, path = record.split(b'\t', 1)
            actual[path.decode()] = tuple(metadata.decode().split())
    expected = {prefix + '/' + e['path']: ('100644', 'blob', e['gitBlobSha']) for e in entries}
    require(actual == expected, 'Published subtree differs from exact manifest')
    original = Path(git('rev-parse', '--git-path', 'objects').decode().strip())
    if not original.is_absolute():
        original = repo / original
    original = original.resolve()
    cache = output / 'temporary-object-cache'
    env = os.environ.copy()
    env.update(GIT_OBJECT_DIRECTORY=str(cache), GIT_ALTERNATE_OBJECT_DIRECTORIES=str(original),
               GIT_TERMINAL_PROMPT='0')
    if args.cached_only:
        probe_env = os.environ.copy()
        probe_env['GIT_NO_LAZY_FETCH'] = '1'
        probe = subprocess.run(['git', '--no-lazy-fetch', 'cat-file',
                                '--batch-check=%(objectname) %(objecttype) %(objectsize)'],
                               cwd=repo, env=probe_env, text=True, capture_output=True,
                               input=''.join(e['gitBlobSha'] + '\n' for e in entries), check=True)
        require(probe.stdout.splitlines() == [f"{e['gitBlobSha']} blob {e['bytes']}" for e in entries],
                'Cached-only preflight found a missing or incorrect object')
        env['GIT_NO_LAZY_FETCH'] = '1'
    receipt = {
        'task': 'DB-Exec-Parity-01', 'startedUtc': utc(), 'commit': args.commit,
        'tree': tree, 'subtree': subtree, 'targetPrefix': prefix,
        'manifestSha256': hashlib.sha256(manifest_bytes).hexdigest(),
        'readerSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'freeBefore': shutil.disk_usage(output).free, 'passed': False, 'files': [],
        'readMode': 'cached-only-no-lazy-fetch' if args.cached_only else 'bounded-promisor-fetch',
        'preflightAllObjectsPresent': bool(args.cached_only),
        'groupsCompleted': 0, 'maxGroupPayloadBytes': 8 * 1024 * 1024,
        'scope': 'Read every actual Git blob resolved from the published commit and verify SHA256, Git SHA1, length, mode and exact subtree membership. Existing immutable Git objects may be reused. Missing blobs are fetched from the configured promisor origin into a private cache. The private cache is removed after its reader exits successfully at each bounded group; no original object, source or evidence file is deleted.'}

    def save():
        temporary = output / 'receipt.json.tmp'
        temporary.write_text(json.dumps(receipt, indent=2) + '\n')
        temporary.replace(output / 'receipt.json')

    groups, current, count = [], [], 0
    for entry in entries:
        if current and count + entry['bytes'] > receipt['maxGroupPayloadBytes']:
            groups.append(current)
            current, count = [], 0
        current.append(entry)
        count += entry['bytes']
    if current:
        groups.append(current)
    save()
    child = None
    try:
        with (output / 'git-fetch.log').open('wb') as log:
            for group in groups:
                require(not cache.exists(), 'Previous cache still exists')
                required_free = (2 * 1024 * 1024 if args.cached_only else
                                 16 * 1024 * 1024 + sum(e['bytes'] for e in group))
                require(shutil.disk_usage(output).free > required_free,
                        'Insufficient bounded readback space')
                cache.mkdir()
                command = ['git', '--no-lazy-fetch'] if args.cached_only else ['git']
                child = subprocess.Popen(command + ['cat-file', '--batch'], cwd=repo, env=env,
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
                for entry in group:
                    child.stdin.write((entry['gitBlobSha'] + '\n').encode())
                    child.stdin.flush()
                    header = child.stdout.readline().decode().strip().split()
                    require(header == [entry['gitBlobSha'], 'blob', str(entry['bytes'])], 'Unexpected blob header')
                    sha256 = hashlib.sha256()
                    sha1 = hashlib.sha1(b'blob ' + str(entry['bytes']).encode() + b'\0')
                    remaining = entry['bytes']
                    while remaining:
                        block = child.stdout.read(min(1024 * 1024, remaining))
                        require(bool(block), 'Truncated blob: ' + entry['path'])
                        sha256.update(block)
                        sha1.update(block)
                        remaining -= len(block)
                    require(child.stdout.read(1) == b'\n', 'Missing blob delimiter')
                    require(sha256.hexdigest() == entry['sha256'], 'SHA256 mismatch: ' + entry['path'])
                    require(sha1.hexdigest() == entry['gitBlobSha'], 'Git SHA mismatch: ' + entry['path'])
                    receipt['files'].append({k: entry[k] for k in ('path', 'bytes', 'mode', 'gitBlobSha', 'sha256')})
                    save()
                child.stdin.close()
                require(child.wait(timeout=30) == 0, 'Git reader failed')
                child = None
                require(cache.parent == output and cache.is_dir() and not cache.is_symlink(), 'Unsafe private cache')
                require(shutil.rmtree.avoids_symlink_attacks, 'Unsafe cache removal platform')
                shutil.rmtree(cache)
                receipt['groupsCompleted'] += 1
                save()
                print(json.dumps({'verified': len(receipt['files']), 'total': len(entries),
                                  'groupsCompleted': receipt['groupsCompleted']}), flush=True)
        require(source.read_bytes() == manifest_bytes, 'Manifest changed during readback')
        receipt.update(passed=True, completedUtc=utc(), totalBytes=sum(e['bytes'] for e in entries),
                       verifiedFiles=len(entries), temporaryCacheRemoved=not cache.exists(),
                       freeAfter=shutil.disk_usage(output).free)
        save()
        print(json.dumps({'passed': True, 'files': len(entries), 'bytes': receipt['totalBytes']}), flush=True)
    except BaseException as error:
        if child is not None and child.poll() is None:
            child.terminate()
            child.wait(timeout=30)
        receipt.update(passed=False, failedUtc=utc(), error={'type': type(error).__name__, 'message': str(error)},
                       temporaryCacheRetained=cache.exists())
        save()
        raise


if __name__ == '__main__':
    main()
