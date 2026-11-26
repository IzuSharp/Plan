#!/usr/bin/env python3
"""Retain the completed Go comparison; this never executes a workload."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/scratch/166b48a091b9/go-comparison-01')
OUT = ROOT.parent / 'go-final-evidence-01'
TOOL = ROOT.parent / 'worktrees/DB-Go-01-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/tools/archive_measurement_evidence.py'
TOOL_SHA = '0e3d18c4c67072c119cba0477fc2ead22f60ab6c0c722a40dbee1960f195be3b'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_new(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')

assert sha(TOOL) == TOOL_SHA
assert not OUT.exists(), 'Never overwrite an evidence archive'
state = json.loads((ROOT / 'campaign-state.json').read_text())
assert state['kind'] == 'campaign-finished' and state['exitCode'] == 0 and state['inputsUnchanged'] is True
for provider in ('sqlite', 'postgresql'):
    verdict = json.loads((ROOT / 'analysis' / (provider + '-final-01.json')).read_text())
    assert verdict['accepted'] is True and verdict['finalThirtyMinuteAccepted'] is True
for name in ('final-report.md', 'comparison.json', 'final-independent-review.json',
             'final-independent-review.md', 'cleanup-inventory-addendum-01.json'):
    assert (ROOT / name).is_file(), 'Missing completed review: ' + name

freeze = json.loads((ROOT / 'freeze.json').read_text())
inputs = {}
for row in freeze['files']:
    path = Path(row['path'])
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], str(path)
    inputs[str(path)] = row['sha256']

# Immediate task control/review files are retained. The separately published
# supplemental legacy archive is not embedded a second time.
for path in sorted(ROOT.iterdir()):
    if path.is_file() and path.name != 'legacy-extra-evidence.tar.gz':
        inputs[str(path)] = sha(path)
for path in sorted((ROOT / 'toolchain').iterdir()):
    if path.is_file():
        inputs[str(path)] = sha(path)
for name in ('publication-product-01', 'publication-plan-01'):
    path = ROOT / name / 'receipt.json'
    inputs[str(path)] = sha(path)
inputs[str(ROOT / 'build/source-history.bundle')] = sha(ROOT / 'build/source-history.bundle')

inventory = ROOT / 'go-archive-inputs-01.json'
write_new(inventory, {
    'schemaVersion': 1,
    'scope': 'Completed Go cells, exact source/manifest identities, validation, failures, reports and cleanup inventory. Historical four cells are referenced, not rerun.',
    'inputFiles': dict(sorted(inputs.items())),
    'separateLegacyArchive': {'path': str(ROOT / 'legacy-extra-evidence.tar.gz'),
        'sha256': sha(ROOT / 'legacy-extra-evidence.tar.gz')},
    'omissions': 'SDK/module/build caches and database/build binaries are not distributed; measurements retain actual identities and this task will delete the local copies after remote readback. No binary recovery claim.',
})
args = [sys.executable, str(TOOL), '--measurements', str(ROOT / 'measurements'),
        '--inventory', str(inventory), '/inputFiles', sha(inventory)]
for child in ('analysis', 'build', 'plans', 'harness'):
    args += ['--retain-root', str(ROOT / child)]
for path in sorted((ROOT / 'measurements').glob('postgresql-*/postgres-data')):
    args += ['--exclude-root', 'database', str(path)]
args += ['--scope', 'DB-Go-01 completed two serial 1800-second Go-only cells; record-only draft PRs, no merge; retains source, actual results, failures, reports and cleanup evidence; excludes reproducible binaries/caches/databases with no binary recovery claim',
         '--output-dir', str(OUT)]
record = {'schemaVersion': 1, 'argv': args, 'toolSha256': TOOL_SHA,
          'inventorySha256': sha(inventory), 'startedUtc': datetime.now(timezone.utc).isoformat(),
          'workloadsExecuted': 0}
write_new(ROOT / 'archive-command-start.json', record)
with (ROOT / 'archive-stdout.log').open('xb') as out, (ROOT / 'archive-stderr.log').open('xb') as err:
    completed = subprocess.run(args, stdout=out, stderr=err, check=False)
record.update(exitCode=completed.returncode, finishedUtc=datetime.now(timezone.utc).isoformat())
write_new(ROOT / 'archive-command.json', record)
print(json.dumps({'exitCode': completed.returncode, 'output': str(OUT),
                  'inventoryEntries': len(inputs), 'command': str(ROOT / 'archive-command.json')}))
raise SystemExit(completed.returncode)
