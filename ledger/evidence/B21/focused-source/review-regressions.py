#!/usr/bin/env python3
"""Focused B21 maintenance/lifecycle regressions; seeded fixtures are not crash acceptance."""
import base64
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import time
import uuid

ROOT = Path('/workspace/scratch/58d2a6adf1c3')
APP = ROOT / '.worktree/Task-07-B21-linux/NativeWeave'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.worktree/Task-07-linux/NativeWeave/tests/Reference.TaskService'))
from run import Service, create
from golden import attachment_hash, create_hash, scope_hash

COMMAND = [str(ROOT / 'dotnet-sdk/dotnet'), str(APP / 'src/Reference.TaskService/bin/Release/net11.0/NativeWeave.Reference.TaskService.dll')]
CASES = []
TENANT, PRINCIPAL = 'tenant-a', 'alice'
CREATE, ATTACH = 'POST /v1/items', 'PUT /v1/items/{id}/attachment'

def check(name, predicate, detail=None):
    CASES.append({'case': name, 'passed': bool(predicate), 'detail': detail})
    (HERE / 'cases.json').write_text(json.dumps(CASES, indent=2) + '\n')
    if not predicate:
        raise AssertionError(name)
    print('PASS ' + name, flush=True)

def config_at(path):
    path.mkdir(parents=True)
    return {'provider': 'sqlite', 'database': str(path / 'service.db'),
            'consumerDatabase': str(path / 'consumer.db'), 'blobDirectory': str(path / 'storage'),
            'cursorKey': base64.b64encode(secrets.token_bytes(32)).decode(),
            'principals': [{'token': secrets.token_hex(20), 'tenant': TENANT, 'principal': PRINCIPAL, 'canWrite': True}],
            'port': 0, 'runWorkers': False, 'maxUploads': 16, 'orphanGraceSeconds': 60}

def admin(config_path, option, label):
    result = subprocess.run([*COMMAND, '--config', str(config_path), option], capture_output=True, text=True, timeout=90)
    (HERE / (label + '.log')).write_text(result.stdout + result.stderr)
    check(label + '-exit', result.returncode == 0, {'exit': result.returncode})
    return result.stdout

def ident(number):
    return str(uuid.UUID(int=number))

def main():
    cfg = config_at(HERE / 'maintenance-fixtures')
    config_path = HERE / 'maintenance.private.json'
    config_path.write_text(json.dumps(cfg)); config_path.chmod(0o600)
    admin(config_path, '--migrate-only', 'migrate')
    root = Path(cfg['blobDirectory'])
    for directory in ['staging', 'recovery', 'blobs']:
        (root / directory).mkdir(parents=True)
    now = int(time.time() * 1000); old = now - 8 * 24 * 60 * 60 * 1000
    digest = hashlib.sha256(b'abc').hexdigest()
    (root / 'blobs' / digest).write_bytes(b'abc')
    os.utime(root / 'blobs' / digest, ((old / 1000), (old / 1000)))

    def seed_create(db, number, key, completed, delivered):
        op = ident(number); item = ident(number + 10000); title = 'seeded-' + key
        response = json.dumps({'responseVersion': 1, 'operationId': op, 'itemId': item,
                               'title': title, 'createdAt': completed, 'version': 1}, separators=(',', ':')).encode()
        db.execute('INSERT INTO operations VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                   (scope_hash(TENANT, PRINCIPAL, CREATE), key, create_hash(TENANT, PRINCIPAL, title), op,
                    TENANT, PRINCIPAL, CREATE, 1, 201, response, completed))
        db.execute('INSERT INTO items VALUES(?,?,?,?,?,?)', (TENANT, item, op, title, completed, 1))
        db.execute('INSERT INTO outbox VALUES(?,?,?,?,?,?,?,?,?,?)',
                   (str(uuid.uuid4()), TENANT, op, 1, response, 2 if delivered else 0, 0, 0, 0, completed if delivered else 0))
        return op, item, title

    def recovery(op, key, title):
        return {'version': 1, 'operationId': op, 'scope': scope_hash(TENANT, PRINCIPAL, CREATE),
                'requestKey': key, 'requestHash': create_hash(TENANT, PRINCIPAL, title), 'createdAt': now}

    def upload(op, key, item):
        return {'version': 1, 'operationId': op, 'tenant': TENANT, 'principal': PRINCIPAL,
                'itemId': item, 'requestKey': key, 'expectedVersion': 1, 'contentHash': digest,
                'contentLength': 3, 'state': 'prepared', 'createdAt': old}

    with sqlite3.connect(cfg['database']) as db:
        # Coherent old operations/items/outbox. The first 101 must stay because publication is unresolved.
        for index in range(101):
            seed_create(db, 1000 + index, 'retained-' + str(index), old + index, False)
        for index in range(5):
            seed_create(db, 2000 + index, 'eligible-' + str(index), old + 1000 + index, True)
        confirmed_op, _, confirmed_title = seed_create(db, 10**30, 'confirmed-recovery', now, False)
        (root / 'recovery' / (confirmed_op + '.json')).write_text(json.dumps(recovery(confirmed_op, 'confirmed-recovery', confirmed_title)))
        for index in range(101):
            op = ident(1 + index)
            (root / 'recovery' / (op + '.json')).write_text(json.dumps(recovery(op, 'absent-' + str(index), 'unconfirmed')))
        # A second valid durable operation confirms one upload behind 101 unknown prepared manifests.
        creation_op, item, _ = seed_create(db, 3000, 'upload-item', now, False)
        attachment_op = ident(10**30 + 1); attachment_key = 'confirmed-upload'
        response = json.dumps({'responseVersion': 1, 'operationId': attachment_op, 'itemId': item,
                               'contentHash': digest, 'contentLength': 3, 'version': 2}, separators=(',', ':')).encode()
        db.execute('INSERT INTO operations VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                   (scope_hash(TENANT, PRINCIPAL, ATTACH), attachment_key,
                    attachment_hash(TENANT, PRINCIPAL, item, digest, 3, 1), attachment_op,
                    TENANT, PRINCIPAL, ATTACH, 1, 200, response, now))
        db.execute('UPDATE items SET version=2 WHERE item_id=?', (item,))
        db.execute('INSERT INTO attachments VALUES(?,?,?,?,?,?)', (TENANT, item, digest, 3, attachment_op, 2))
        db.execute('INSERT INTO outbox VALUES(?,?,?,?,?,?,?,?,?,?)', (str(uuid.uuid4()), TENANT, attachment_op, 1, response, 0, 0, 0, 0, 0))
        (root / 'staging' / (attachment_op + '.json')).write_text(json.dumps(upload(attachment_op, attachment_key, item)))
        for index in range(101):
            op = ident(500 + index)
            (root / 'staging' / (op + '.json')).write_text(json.dumps(upload(op, 'unknown-upload-' + str(index), item)))

    temporary_paths = [root / 'staging' / (ident(9000) + '.part'),
                       root / 'staging' / (ident(9001) + '.json.new'),
                       root / 'staging' / (ident(500) + '.json.new'),
                       root / 'recovery' / (ident(9002) + '.json.new')]
    for path in temporary_paths:
        path.write_bytes(b'{incomplete-temporary'); os.utime(path, (old / 1000, old / 1000))
    protected_part = root / 'staging' / (ident(500) + '.part')
    protected_part.write_bytes(b'abc'); os.utime(protected_part, (old / 1000, old / 1000))
    fresh_part = root / 'staging' / (ident(9003) + '.part'); fresh_part.write_bytes(b'fresh')

    first = json.loads(admin(config_path, '--maintenance-once', 'maintenance-pass-1'))
    with sqlite3.connect(cfg['database']) as db:
        check('protected-oldest-101-retained', db.execute("SELECT COUNT(*) FROM operations WHERE request_key LIKE 'retained-%'").fetchone()[0] == 101)
        check('first-batch-cursor-does-not-skip-unscanned-eligible', db.execute("SELECT COUNT(*) FROM operations WHERE request_key LIKE 'eligible-%'").fetchone()[0] == 5)
    progress = json.loads((root / 'maintenance.json').read_text())
    (HERE / 'maintenance-progress-1.json').write_text(json.dumps(progress, indent=2) + '\n')
    check('bounded-phases-persist-first-page-cursors', progress['operations'] is not None and progress['recovery'] is not None and progress['uploads'] is not None)
    check('temporary-orphans-collected-after-grace', all(not path.exists() for path in temporary_paths))
    check('fresh-or-protected-part-preserved', fresh_part.exists() and protected_part.exists())
    check('confirmed-records-behind-first-100-not-falsely-skipped',
          (root / 'recovery' / (confirmed_op + '.json')).exists() and (root / 'staging' / (attachment_op + '.json')).exists())

    second = json.loads(admin(config_path, '--maintenance-once', 'maintenance-pass-2'))
    with sqlite3.connect(cfg['database']) as db:
        check('later-eligible-operations-removed-on-second-pass', db.execute("SELECT COUNT(*) FROM operations WHERE request_key LIKE 'eligible-%'").fetchone()[0] == 0, second)
        check('undelivered-operations-and-outbox-still-retained',
              db.execute("SELECT COUNT(*) FROM operations WHERE request_key LIKE 'retained-%'").fetchone()[0] == 101 and
              db.execute("SELECT COUNT(*) FROM outbox WHERE operation_id IN (SELECT operation_id FROM operations WHERE request_key LIKE 'retained-%')").fetchone()[0] == 101)
        check('business-items-survive-replay-expiry', db.execute("SELECT COUNT(*) FROM items WHERE title LIKE 'seeded-eligible-%'").fetchone()[0] == 5)
    check('later-confirmed-recovery-and-upload-reconciled',
          not (root / 'recovery' / (confirmed_op + '.json')).exists() and not (root / 'staging' / (attachment_op + '.json')).exists())
    check('all-101-unconfirmed-recovery-and-upload-records-retained',
          len(list((root / 'recovery').glob('*.json'))) == 101 and len(list((root / 'staging').glob('*.json'))) == 101)
    check('referenced-and-recovery-protected-blob-retained', (root / 'blobs' / digest).read_bytes() == b'abc')
    progress = json.loads((root / 'maintenance.json').read_text())
    (HERE / 'maintenance-progress-2.json').write_text(json.dumps(progress, indent=2) + '\n')
    check('short-pages-wrap-maintenance-cursors', all(progress[key] is None for key in ['operations', 'recovery', 'uploads']))

    # Live conflict requests exercise actual native rollback and application cleanup; no fault is simulated.
    cfg2 = config_at(HERE / 'shutdown-fixture')
    token = cfg2['principals'][0]['token']
    with Service(COMMAND, cfg2, HERE / 'shutdown-service') as service:
        status, raw, _ = create(service, token, 'base-item', 'rollback lifecycle')
        check('lifecycle-base-create', status == 201)
        item = json.loads(raw)['itemId']
        def conflict(index):
            return service.request('PUT', '/v1/items/' + item + '/attachment', b'abc',
                {'Content-Length': '3', 'If-Match': '999', 'Idempotency-Key': 'conflict-' + str(index)}, token)[0]
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            statuses = list(pool.map(conflict, range(16)))
        check('concurrent-stale-bindings-report-conflict', statuses == [412] * 16, statuses)
        shutdown_started = time.monotonic()
    shutdown_seconds = time.monotonic() - shutdown_started
    check('graceful-shutdown-joined-source-owners', service.shutdown['databaseResourcesReleased'] and service.shutdown['consumerResourcesReleased'],
          {'seconds': shutdown_seconds, 'receipt': service.shutdown})
    check('known-rollback-protections-retired-before-process-exit',
          not list((Path(cfg2['blobDirectory']) / 'staging').glob('*.json')) and
          not list((Path(cfg2['blobDirectory']) / 'recovery').glob('*.json')))
    with sqlite3.connect(cfg2['database']) as db:
        check('rollback-conflicts-added-no-durable-effects', db.execute('SELECT COUNT(*) FROM operations').fetchone()[0] == 1 and
              db.execute('SELECT COUNT(*) FROM items').fetchone()[0] == 1 and db.execute('SELECT COUNT(*) FROM outbox').fetchone()[0] == 1 and
              db.execute('SELECT COUNT(*) FROM attachments').fetchone()[0] == 0)
    source_hashes = {str(path.relative_to(APP)): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in sorted((APP / 'src/Reference.TaskService').glob('*.cs'))}
    (HERE / 'result.json').write_text(json.dumps({'passed': True, 'cases': len(CASES),
        'purpose': 'B21 focused seeded maintenance and actual native rollback/shutdown regressions; not crash or soak acceptance',
        'sourceHashes': source_hashes, 'executableSha256': hashlib.sha256(Path(COMMAND[1]).read_bytes()).hexdigest(),
        'firstMaintenance': first, 'secondMaintenance': second, 'shutdownSeconds': shutdown_seconds}, indent=2) + '\n')

if __name__ == '__main__':
    main()
