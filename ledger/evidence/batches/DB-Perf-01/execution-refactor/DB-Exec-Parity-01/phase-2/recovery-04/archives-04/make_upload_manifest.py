#!/usr/bin/env python3
"""Refresh only verified immutable package mappings; never creates GitHub refs."""
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent


def metadata(path, target):
    content = path.read_bytes()
    return {'path': target, 'sourcePath': str(path), 'bytes': len(content),
            'sha256': hashlib.sha256(content).hexdigest(),
            'gitBlobSha': hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()}


def main():
    entries = []
    for receipt_path in sorted(HERE.glob('*-receipt.json')):
        receipt = json.loads(receipt_path.read_text())
        if not receipt.get('passed') or not receipt.get('verification', {}).get('passed'):
            continue
        archive = receipt['archive']
        for part in archive['parts']:
            entries.append({**part, 'path': 'raw-archives/' + part['path'],
                            'sourcePath': str(HERE / 'raw-archives' / part['path'])})
        for name in ['expandedFileManifest', 'compressionIdentity']:
            relative = 'raw-archives/' + archive[name]
            entries.append(metadata(HERE / relative, relative))
        for suffix in ['entry', 'verification', 'receipt']:
            name = archive['name'] + '-' + suffix + '.json'
            entries.append(metadata(HERE / name, 'records/' + name))
    path = HERE / 'blob-publication-manifest-04.json'
    value = {'task': 'DB-Exec-Parity-01', 'repository': 'IzuSharp/Plan',
             'targetPrefix': 'ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/archives-04',
             'scope': 'create_blob only; root owns tree/commit/ref publication',
             'remotePublication': False, 'files': entries}
    if (HERE / 'metadata-ready.json').exists():
        for item in json.loads((HERE / 'metadata-ready.json').read_text())['files']:
            entries.append(metadata(Path(item['sourcePath']), item['path']))
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)
    print(json.dumps({'files': len(entries), 'bytes': sum(x['bytes'] for x in entries),
                      'parts': sum(x['path'].endswith('.bin') for x in entries), 'manifestSha256': hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
