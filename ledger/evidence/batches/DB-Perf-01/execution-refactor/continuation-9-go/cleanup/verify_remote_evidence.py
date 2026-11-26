#!/usr/bin/env python3
"""Read immutable GitHub evidence bytes and verify against the reviewed local tree."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path('/workspace/scratch/166b48a091b9/worktrees/DB-Go-01-plan')
PREFIX = 'ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-9-go'
COMMIT = '3aef334c5c44aac364ca500d9bafffd66a8152b1'
OUT = Path('/workspace/scratch/2dfe9fb1bc53/remote-evidence-readback.json')

def verify(line):
    metadata, path = line.split('\t', 1)
    mode, kind, expected_blob = metadata.split()
    local = (ROOT / path).read_bytes()
    local_sha = hashlib.sha256(local).hexdigest()
    assert hashlib.sha1(b'blob ' + str(len(local)).encode() + b'\0' + local).hexdigest() == expected_blob
    url = f'https://raw.githubusercontent.com/IzuSharp/Plan/{COMMIT}/{path}'
    with urllib.request.urlopen(url, timeout=45) as response:
        remote = response.read()
        status = response.status
    remote_sha = hashlib.sha256(remote).hexdigest()
    actual_blob = hashlib.sha1(b'blob ' + str(len(remote)).encode() + b'\0' + remote).hexdigest()
    ok = status == 200 and remote_sha == local_sha and actual_blob == expected_blob and len(remote) == len(local)
    return {'path': path, 'url': url, 'httpStatus': status, 'expectedGitBlob': expected_blob,
            'observedGitBlob': actual_blob, 'expectedBytes': len(local), 'readbackBytes': len(remote),
            'expectedSha256': local_sha, 'readbackSha256': remote_sha, 'matched': ok}

def main():
    lines = subprocess.check_output(['git', 'ls-tree', '-r', 'HEAD', '--', PREFIX], cwd=ROOT, text=True).splitlines()
    rows = []
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        tasks = {pool.submit(verify, line): line.split('\t', 1)[1] for line in lines}
        for future in concurrent.futures.as_completed(tasks):
            path = tasks[future]
            try:
                row = future.result()
            except Exception as exc:
                row = {'path': path, 'matched': False, 'errorType': type(exc).__name__, 'error': str(exc)}
            rows.append(row)
            print(json.dumps({'checked': len(rows), 'of': len(lines), 'matched': row['matched'], 'path': path}), flush=True)
    result = {'schemaVersion': 1, 'task': 'DB-Go-01', 'repository': 'IzuSharp/Plan', 'fixedCommit': COMMIT,
              'startedAtUtc': started, 'finishedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'method': 'Independent HTTPS raw-file readback; compare every byte via SHA-256, length, and Git blob SHA-1 against the exact reviewed local tree.',
              'benchmarkRerun': False, 'filesChecked': len(rows), 'filesMatched': sum(x['matched'] for x in rows),
              'allMatched': len(rows) == len(lines) and all(x['matched'] for x in rows),
              'totalReadbackBytes': sum(x.get('readbackBytes', 0) for x in rows),
              'files': sorted(rows, key=lambda x: x['path'])}
    OUT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'files'}), flush=True)
    raise SystemExit(0 if result['allMatched'] else 1)

if __name__ == '__main__':
    main()
