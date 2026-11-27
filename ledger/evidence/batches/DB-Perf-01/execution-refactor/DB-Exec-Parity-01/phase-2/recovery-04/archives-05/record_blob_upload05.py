#!/usr/bin/env python3
"""Record one verified content-addressed blob without publishing a git ref."""
import datetime
import json
import os
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent

def atom(path, value):
    temporary = path.with_name(path.name + '.tmp')
    data = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    with open(temporary, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    assert path.read_bytes() == data

item = json.loads(sys.argv[1])
assert item['sha'] == item['gitBlobSha']
assert len(item['sha']) == 40 and len(item['sha256']) == 64
assert item['mode'] == '100644'
path = BASE / 'blob-upload-receipts-05.json'
receipt = json.loads(path.read_text()) if path.exists() else {
    'task': 'DB-Exec-Parity-01', 'repository': 'IzuSharp/Plan',
    'remotePublication': False, 'uploads': [], 'failures': [],
    'scope': 'Verified create_blob responses only; no tree, commit, or ref created by this uploader.'}
old = next((r for r in receipt['uploads'] if r['path'] == item['path']), None)
if old:
    assert all(old[k] == item[k] for k in ('sha', 'sha256', 'bytes', 'mode'))
else:
    item['completedUtc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt['uploads'].append(item)
receipt['count'] = len(receipt['uploads'])
receipt['bytes'] = sum(r['bytes'] for r in receipt['uploads'])
receipt['updatedUtc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
atom(path, receipt)
parts = json.loads((BASE / 'upload-parts-manifest-05.json').read_text())['parts']
done = {r['path'] for r in receipt['uploads']}
pending = [r['path'] for r in parts if r['path'] not in done]
atom(BASE / 'upload-resume-05.json', {
    'task': 'DB-Exec-Parity-01', 'remotePublication': False,
    'uploadedCount': receipt['count'], 'uploadedBytes': receipt['bytes'],
    'partCount': len(parts), 'partsUploaded': len(parts)-len(pending),
    'nextPart': pending[0] if pending else None,
    'pendingPartPaths': pending,
    'metadataState': 'Finalize metadata manifest and upload before root publication.',
    'updatedUtc': receipt['updatedUtc']})
print(json.dumps({'count': receipt['count'], 'partsUploaded': len(parts)-len(pending),
                  'nextPart': pending[0] if pending else None, 'remotePublication': False}))
