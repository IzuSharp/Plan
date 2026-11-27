#!/usr/bin/env python3
"""Verify/restore a DB-Exec-Parity-01 archive from exact ordered Git parts."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

parser = argparse.ArgumentParser()
parser.add_argument('name', help='Archive name from raw-archives/index.json, or all')
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--extract', action='store_true')
args = parser.parse_args()
root = Path(__file__).resolve().parent / 'raw-archives'
index = json.loads((root / 'index.json').read_text())
selected = [a for a in index['archives'] if args.name in ('all', a['name'])]
if not selected:
    raise SystemExit('No matching archive')
args.output.mkdir(parents=True, exist_ok=True)
for archive in selected:
    target = args.output / archive['filename']
    if target.exists():
        raise SystemExit('Refuse to overwrite: ' + str(target))
    digest = hashlib.sha256()
    with target.open('xb') as dest:
        for part in archive['parts']:
            source = root / part['path']
            b = source.read_bytes()
            if len(b) != part['bytes'] or hashlib.sha256(b).hexdigest() != part['sha256']:
                raise SystemExit('Part identity mismatch: ' + str(source))
            dest.write(b)
            digest.update(b)
    assert target.stat().st_size == archive['archive']['bytes']
    assert digest.hexdigest() == archive['archive']['sha256']
    manifest = json.loads((root / archive['expandedFileManifest']).read_text())
    expected = {x['path']: x for x in manifest['files']}
    with tarfile.open(target, 'r:xz') as tar:
        actual = {m.name: {'bytes': m.size, 'sha256': hashlib.file_digest(tar.extractfile(m), 'sha256').hexdigest()}
                  for m in tar if m.isfile()}
    assert len(actual) == len(expected)
    assert all(actual[p] == {k: x[k] for k in ('bytes', 'sha256')} for p, x in expected.items())
    if args.extract:
        with tarfile.open(target, 'r:xz') as tar:
            tar.extractall(args.output, filter='data')
    print(archive['name'], 'verified files:', len(actual), 'archive sha256:', digest.hexdigest())
