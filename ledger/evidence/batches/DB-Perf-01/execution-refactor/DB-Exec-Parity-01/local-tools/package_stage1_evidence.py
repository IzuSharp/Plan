#!/usr/bin/env python3
"""Freeze actual local evidence; preserve byte identities and explicit exclusions."""
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

root = Path(__file__).resolve().parents[1]
destination = root / 'evidence-packages/stage1'
destination.mkdir(parents=True, exist_ok=True)

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def package(name, paths, excluded):
    archive = destination / (name + '.tar.gz')
    manifest = destination / (name + '.json')
    if archive.exists() or manifest.exists():
        raise SystemExit('Immutable package already exists: ' + name)
    items = [{'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
             for p in sorted(set(paths))]
    with archive.open('xb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=6, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w', dereference=True) as tar:
            for item in items:
                p = root / item['path']
                info = tar.gettarinfo(p, arcname=item['path'])
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ''
                with p.open('rb') as f:
                    tar.addfile(info, f)
    with tarfile.open(archive, 'r:gz') as tar:
        observed = {m.name: {'bytes': m.size, 'sha256': hashlib.file_digest(tar.extractfile(m), 'sha256').hexdigest()}
                    for m in tar if m.isfile()}
    assert len(observed) == len(items)
    assert all(observed[x['path']] == {k: x[k] for k in ('bytes', 'sha256')} for x in items)
    result = {'task': 'DB-Exec-Parity-01', 'scope': name, 'archiveByteVerificationPassed': True,
              'archive': {'path': archive.name, 'bytes': archive.stat().st_size, 'sha256': sha(archive)},
              'files': items, 'exclusions': excluded}
    manifest.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'archive': result['archive'], 'files': len(items)}), flush=True)

measurements = []
for p in (root / 'measurements').rglob('*'):
    if not p.is_file() or 'postgres-data' in p.parts:
        continue
    if p.name.endswith(('.sqlite', '.sqlite-wal', '.sqlite-shm')):
        continue
    measurements.append(p)
package('baseline-measurements-and-traces', measurements,
        ['Ephemeral PostgreSQL data directories and SQLite database/WAL/SHM files are not archived. Exact seed fixture, SQL/oracles, settings, commands, logs and receipts remain. They are not binary consumer artifacts.'])

support = []
for folder in ('analysis', 'diagnostics', 'environment'):
    support.extend(p for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
# Preserve the actual independent instrumentation patches and source commit histories.
package('source-diagnostics-machine-code', support, [])

artifacts = []
for family in ('diagnostic-sqlite-02', 'diagnostic-postgresql', 'allocation-baseline-sqlite', 'allocation-baseline-postgresql'):
    for consumer in (root / 'consumers' / family).iterdir():
        if not consumer.is_dir():
            continue
        artifacts.extend(p for p in consumer.iterdir() if p.is_file())
        for folder in ('out', 'generated', 'generated-original', 'generated-instrumented'):
            artifacts.extend(p for p in (consumer / folder).rglob('*') if p.is_file())
        for p in (consumer / 'obj').glob('*.json'):
            artifacts.append(p)
for folder in ('diagnostic-sqlite-01', 'diagnostic-sqlite-02'):
    artifacts.extend(p for p in (root / 'builds' / folder).rglob('*') if p.is_file())
package('independent-diagnostic-artifacts', artifacts,
        ['NuGet cache and reproducible compilation intermediates excluded; actual published ELF/debug/native images, generated C#, build receipts and restore assets retained.'])
