from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

root = Path('/workspace/scratch/166b48a091b9')
recovery = root / 'recovery'
measurements = Path('/workspace/scratch/fd78534029f7/measurements')
tool = Path('/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/tools/archive_measurement_evidence.py')
expected_tool = '0e3d18c4c67072c119cba0477fc2ead22f60ab6c0c722a40dbee1960f195be3b'
assert hashlib.sha256(tool.read_bytes()).hexdigest() == expected_tool
inventory = recovery / 'final-evidence-inputs-01.json'
inventory_sha = hashlib.sha256(inventory.read_bytes()).hexdigest()
output = root / 'final-evidence-01'
control = root / 'archive-control-01'
assert not output.exists() and not control.exists(), 'Fresh destinations required'
control.mkdir(mode=0o700)
argv = [
    sys.executable, str(tool),
    '--measurements', str(measurements / 'sqlite-final-01'),
    '--retain-root', str(measurements / 'postgresql-final-01'),
    '--retain-root', str(recovery),
    '--inventory', str(inventory), '/inputFiles', inventory_sha,
    '--exclude-root', 'database', str(measurements / 'postgresql-final-01/pgdata'),
    '--exclude-root', 'package-cache', '/workspace/scratch/4a65d70f0fe1/tools/nuget-packages',
    '--exclude-root', 'package-cache', '/workspace/scratch/fd78534029f7/builds/candidate-sqlite-02/consumer-workload/packages',
    '--exclude-root', 'package-cache', '/workspace/scratch/fd78534029f7/builds/candidate-postgresql-02/consumer-workload/packages',
    '--scope', 'Original final 17da four-cell local evidence and completed analysis/identity/recovery reviews; historical pre-final archive retained separately by identity; retention does not grant performance or binary-recovery credit',
    '--output-dir', str(output),
]
record = {'argv': argv, 'toolSha256': expected_tool, 'inventorySha256': inventory_sha,
          'startedUtc': datetime.now(timezone.utc).isoformat(),
          'wrapperAffinity': [8], 'productExecutions': 0,
          'stdoutPath': str(control / 'stdout.log'), 'stderrPath': str(control / 'stderr.log')}
with (control / 'command-start.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
with (control / 'stdout.log').open('xb') as stdout, (control / 'stderr.log').open('xb') as stderr:
    completed = subprocess.run(argv, stdout=stdout, stderr=stderr, check=False)
record.update(exitCode=completed.returncode, finishedUtc=datetime.now(timezone.utc).isoformat())
with (control / 'command.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'exitCode': completed.returncode, 'commandReceipt': str(control / 'command.json'),
                  'outputDirectory': str(output)}))
raise SystemExit(completed.returncode)
