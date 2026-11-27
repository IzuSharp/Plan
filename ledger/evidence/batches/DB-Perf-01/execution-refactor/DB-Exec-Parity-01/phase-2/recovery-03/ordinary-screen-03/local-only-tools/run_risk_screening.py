#!/usr/bin/env python3
"""Repeat only concrete risks from the first exclusive ordinary A/B window."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
def now(): return datetime.now(timezone.utc).isoformat()
def exe(family, provider): return root / f'consumers/{family}-{provider}/korda-workload/out/DbPerf.Korda'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
jobs = [
    ('workerd-sqlite-early-stop', 'sqlite', 'workerd03', ['early-stop:32:prepared']),
    ('codec-postgresql-small', 'postgresql', 'codec03', ['numeric:32:prepared', 'money:1:prepared']),
    ('sqliteprepare-text', 'sqlite', 'sqliteprepare03', ['text:32:prepared', 'text:1000:prepared']),
]
record = {'task': 'DB-Exec-Parity-01', 'startedUtc': now(),
          'scope': 'Exclusive serial local ordinary risk follow-up; no build/compression/SQL/sampling by peers.',
          'reason': 'Resolve inconsistent WorkerD early-stop and observed codec single-row / SQLite prepare text CPU regressions.',
          'operations': 8192, 'rounds': 4, 'warmup': 256,
          'runtimeKnobs': 'defaults', 'finalCellCredit': False,
          'driverSha256': sha(__file__), 'commands': []}
def save(): (out / 'window.json').write_text(json.dumps(record, indent=2) + '\n')
save()
for name, provider, family, scenarios in jobs:
    argv = ['python3', root / 'local-tools/run_causal_ab.py', '--provider', provider,
            '--baseline', exe('baseline-final', provider), '--candidate', exe(family, provider),
            '--operations', '8192', '--warmup', '256', '--rounds', '4', '--output', out / name]
    for scenario in scenarios: argv += ['--scenario', scenario]
    item = {'name': name, 'startedUtc': now(), 'argv': list(map(str, argv)),
            'comparisonHelperSha256': sha(argv[1])}
    record['commands'].append(item)
    save()
    log_path = out / (name + '.log')
    with log_path.open('w') as log:
        result = subprocess.run(list(map(str, argv)), stdout=log, stderr=subprocess.STDOUT)
    item.update(finishedUtc=now(), exitCode=result.returncode, logSha256=sha(log_path))
    save()
    print(name, result.returncode, flush=True)
    if result.returncode: raise SystemExit(result.returncode)
record.update(finishedUtc=now(), allAccountingAndOraclesPassed=True)
save()
