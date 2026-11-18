#!/usr/bin/env python3
"""Actual minimum PackageReference sample journey; not clean-machine acceptance."""
import base64
import hashlib
import json
from pathlib import Path
import secrets
import sys

ROOT = Path('/workspace/scratch/58d2a6adf1c3')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.worktree/Task-07-linux/NativeWeave/tests/Reference.TaskService'))
from run import Service, create

storage = HERE / 'minimum-fixture'
storage.mkdir()
cfg = {'provider': 'sqlite', 'database': str(storage / 'main.db'), 'consumerDatabase': str(storage / 'consumer.db'),
       'blobDirectory': str(storage / 'storage'), 'cursorKey': base64.b64encode(secrets.token_bytes(32)).decode(),
       'principals': [{'token': secrets.token_hex(20), 'tenant': 'tenant-a', 'principal': 'alice', 'canWrite': True}],
       'port': 0, 'runWorkers': False}
token = cfg['principals'][0]['token']
binary = HERE / 'minimum/NativeWeave.Reference.TaskService.Sample.dll'
with Service([str(ROOT / 'dotnet-sdk/dotnet'), str(binary)], cfg, HERE / 'minimum-service') as service:
    first = create(service, token, 'minimum-key', 'Minimum packed journey')
    replay = create(service, token, 'minimum-key', 'Minimum packed journey')
    listing = service.request('GET', '/v1/items', token=token)
    mappings = Path('/proc/' + str(service.process.pid) + '/maps').read_text()
    checks = {'create': first[0] == 201, 'stableReplay': replay[0] == 201 and replay[1] == first[1],
              'typedList': listing[0] == 200 and len(json.loads(listing[1])['items']) == 1,
              'nativeSqliteLoaded': 'libnw_database_sqlite.so' in mappings,
              'nativeServerLoaded': 'libnativeweave_server.so' in mappings,
              'unusedPostgreSqlAbsent': 'libnw_database_postgresql.so' not in mappings}
    if not all(checks.values()):
        raise AssertionError(checks)
result = {'passed': True, 'checks': checks, 'shutdown': service.shutdown,
          'binarySha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
          'purpose': 'Actual minimum SQLite+Server package consumer; no explicit RID; no pristine-machine claim'}
(HERE / 'minimum-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
