#!/usr/bin/env python3
"""Archive an existing read-only source audit without executing product code."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile

BASE = Path('/workspace/scratch/4a65d70f0fe1')
SOURCE = BASE / 'artifacts/sql-parity-and-find-audit-01'
OUT = Path(__file__).resolve().parent
PREFIX = 'sql-parity-and-find-audit-01'
sha = lambda value: hashlib.sha256(value).hexdigest()
receipt_bytes = (SOURCE / 'audit-receipt.json').read_bytes()
assert sha(receipt_bytes) == '85bf5bf8ee3883cf1980dc5da902bba1c7715a957f6875eb146073b15df9d07f'
receipt = json.loads(receipt_bytes)
contents = {str(path.relative_to(SOURCE)): path.read_bytes()
            for path in sorted(SOURCE.rglob('*')) if path.is_file()}
assert len(contents) == 41
for item in receipt['files']:
    assert sha(contents[item['path']]) == item['sha256']
    assert len(contents[item['path']]) == item['bytes']
assert all(not value.startswith(b'\x7fELF') for value in contents.values())
contents['assemble.py'] = Path(__file__).read_bytes()
contents['SHA256SUMS'] = ''.join(f'{sha(value)}  {name}\n' for name, value in sorted(contents.items())).encode()


def encode():
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as archive:
            for name, value in sorted(contents.items()):
                member = tarfile.TarInfo(name)
                member.size = len(value); member.mode = 0o644
                member.uid = member.gid = member.mtime = 0
                member.uname = member.gname = ''
                archive.addfile(member, io.BytesIO(value))
    return output.getvalue()


packed = encode(); assert packed == encode()
target = OUT / (PREFIX + '.tar.gz'); target.write_bytes(packed)
with tempfile.TemporaryDirectory(prefix='sql-audit-verify-', dir=BASE / 'artifacts') as temporary:
    with tarfile.open(target, 'r:gz') as archive:
        assert set(archive.getnames()) == set(contents)
        assert all(member.isfile() and member.uid == member.gid == member.mtime == 0 for member in archive.getmembers())
        archive.extractall(temporary, filter='data')
    for name, value in contents.items():
        assert (Path(temporary) / name).read_bytes() == value
manifest = {'schemaVersion': 1, 'archive': target.name, 'bytes': len(packed), 'sha256': sha(packed),
            'members': len(contents), 'originalReceiptSha256': sha(receipt_bytes),
            'twoEncodingsByteIdentical': True, 'allExtractedBytesVerified': True,
            'scope': 'Read-only upstream/consumer source audit and unselected proposals; no product, runtime, timing or allocation credit.',
            'files': [{'path': name, 'bytes': len(value), 'sha256': sha(value)} for name, value in sorted(contents.items())]}
(OUT / (PREFIX + '.manifest.json')).write_text(json.dumps(manifest, indent=2) + '\n')
for name in ('sql-and-probe-audit.md', 'find-fixed-shape-proposal.md'):
    (OUT / name).write_bytes(contents[name])
(OUT / 'source-audit-receipt.json').write_bytes(receipt_bytes)
print(json.dumps({key: manifest[key] for key in manifest if key != 'files'}, indent=2))
