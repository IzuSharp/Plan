#!/usr/bin/env python3
"""Place verified bounded archive parts and exact restoration metadata in Plan."""
import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
dest = root / 'worktrees/Plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/raw-archives'
dest.mkdir(parents=True, exist_ok=True)
archives = []
for encoding in sorted((root / 'evidence-packages').rglob('*.tar.xz.encoding.json')):
    data = json.loads(encoding.read_text())
    source = root / data['xz']['path']
    name = source.name.removesuffix('.tar.xz')
    folder = dest / name
    folder.mkdir(exist_ok=True)
    parts = []
    all_hash = hashlib.sha256()
    with source.open('rb') as f:
        index = 0
        while b := f.read(4 * 1024 * 1024):
            all_hash.update(b)
            part = folder / f'part-{index:04d}.bin'
            expected = hashlib.sha256(b).hexdigest()
            if part.exists():
                assert hashlib.sha256(part.read_bytes()).hexdigest() == expected
            else:
                part.write_bytes(b)
            parts.append({'path': str(part.relative_to(dest)), 'bytes': len(b), 'sha256': expected,
                          'gitBlobSha': hashlib.sha1(f'blob {len(b)}\0'.encode() + b).hexdigest()})
            index += 1
    assert all_hash.hexdigest() == data['xz']['sha256']
    expanded = source.with_name(name + '.json')
    shutil.copyfile(expanded, folder / 'expanded-file-manifest.json')
    shutil.copyfile(encoding, folder / 'compression-identity.json')
    archives.append({'name': name, 'filename': source.name, 'archive': data['xz'], 'tarSha256': data['tarSha256'],
                     'parts': parts, 'expandedFileManifest': str((folder / 'expanded-file-manifest.json').relative_to(dest)),
                     'compressionIdentity': str((folder / 'compression-identity.json').relative_to(dest))})
(dest / 'index.json').write_text(json.dumps({'task': 'DB-Exec-Parity-01', 'format': 'ordered concatenated xz tar parts',
                                            'archives': archives}, indent=2) + '\n')
print('Archives:', len(archives), 'parts:', sum(len(a['parts']) for a in archives),
      'bytes:', sum(a['archive']['bytes'] for a in archives))
