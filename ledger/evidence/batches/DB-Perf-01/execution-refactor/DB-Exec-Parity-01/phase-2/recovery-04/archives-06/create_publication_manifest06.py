#!/usr/bin/env python3
"""Freeze bounded metadata plus uploaded payload parts; no remote write."""
import hashlib
import json
import os
import stat
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXCLUDE = {
    'blob-upload-receipts-06.json', 'upload-resume-06.json',
    'blob-publication-manifest-06.json', 'path-to-sha-final.json',
    'remote-readback-manifest-final.json', 'blob-publication-ready-final.json',
    'expected-subtrees-final.json', 'publication-log-upload-manifest.json',
    'publication-log-upload-receipts.json', 'publication-finalization.json',
    'uploader-active-06.json', 'uploader-completed-06.json',
    'remote-readback-receipt-06.json', 'remote-readback-progress-06.json'}


def record(path):
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and not path.is_symlink()
    data = path.read_bytes()
    after = path.lstat()
    assert (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    return {'path': path.relative_to(BASE).as_posix(), 'sourcePath': str(path),
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'gitBlobSha': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
            'mode': '100644'}


parts = json.loads((BASE / 'upload-parts-manifest-06.json').read_text())['parts']
receipt = json.loads((BASE / 'blob-upload-receipts-06.json').read_text())
done = {r['path']: r for r in receipt['uploads']}
for part in parts:
    assert part['path'] in done and all(part[k] == done[part['path']][k]
                                       for k in ('sha256', 'gitBlobSha', 'bytes', 'mode'))
    assert done[part['path']]['sha'] == part['gitBlobSha']
    assert Path(part['sourcePath']).stat().st_size == part['bytes']
files = [dict(p) for p in parts]
selected = [p for p in BASE.iterdir() if p.is_file() and p.name not in EXCLUDE and not p.name.endswith('.tmp')]
selected += [p for p in (BASE / 'raw-archives').rglob('*') if p.is_file() and not p.name.startswith('part-')]
selected += [p for p in (BASE / 'dependency-manifests').rglob('*') if p.is_file()]
files += [record(p) for p in sorted(selected)]
assert len(parts) == 21 and sum(p['bytes'] for p in parts) == 71202192
assert len(files) == len({f['path'] for f in files})
assert not any('/fixture/' in f['path'] or '__pycache__' in f['path'] for f in files)
value = {'task': 'DB-Exec-Parity-01', 'repository': 'IzuSharp/Plan',
         'targetPrefix': 'ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/archives-06',
         'scope': 'create_blob only; root owns tree/commit/ref and remote actual-byte readback',
         'remotePublication': False, 'files': sorted(files, key=lambda f: f['path']),
         'fileCount': len(files), 'bytes': sum(f['bytes'] for f in files),
         'payloadParts': len(parts), 'payloadBytes': sum(f['bytes'] for f in parts),
         'excludedLocalMetadata': ['source-snapshots and historical-generated directories already represented by payload',
             'mutable upload logs, lock marker, final mappings, readback logs and temporary bytecode'],
         'publicationLogs': 'Three immutable primary-upload snapshots appended after all listed blobs pass.'}
out = BASE / 'blob-publication-manifest-06.json'
data = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
if out.exists():
    assert out.read_bytes() == data, 'Frozen publication manifest would change'
else:
    temp = out.with_suffix('.tmp'); temp.write_bytes(data); os.replace(temp, out)
print(json.dumps({'fileCount': value['fileCount'], 'bytes': value['bytes'],
                  'payloadParts': len(parts), 'sha256': hashlib.sha256(data).hexdigest()}))
