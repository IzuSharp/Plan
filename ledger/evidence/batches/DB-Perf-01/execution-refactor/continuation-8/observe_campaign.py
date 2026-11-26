#!/usr/bin/env python3
"""Read small tails of the frozen campaign; this is not an acceptance analyzer."""
import datetime
import json
from pathlib import Path
import shutil

root = Path('/workspace/scratch/fd78534029f7/measurements')
result = {'observedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'Lightweight progress only; no performance acceptance',
          'completedCommands': [], 'activeSamples': [],
          'workspaceFreeBytes': shutil.disk_usage('/workspace').free}
for provider, concurrency in [('sqlite', 4), ('postgresql', 8)]:
    directory = root / (provider + '-final-01')
    if not directory.exists():
        continue
    for cohort in ['candidate', 'dapper']:
        name = f'{cohort}-c{concurrency}'
        receipt = directory / (name + '.command.json')
        samples = directory / (name + '.resources.jsonl')
        if receipt.exists():
            data = json.loads(receipt.read_text())
            result['completedCommands'].append({
                'provider': provider, 'cohort': cohort, 'success': data['success'],
                'exitCode': data['exitCode'], 'finishedUtc': data['finishedUtc']})
        elif samples.exists() and samples.stat().st_size:
            with samples.open('rb') as stream:
                first = json.loads(stream.readline())
                stream.seek(max(0, samples.stat().st_size - 65536))
                lines = stream.read().splitlines()
            # A concurrent writer may have emitted an incomplete final line.
            latest = None
            for line in reversed(lines):
                try:
                    latest = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
            if latest:
                result['activeSamples'].append({
                    'provider': provider, 'cohort': cohort, 'utc': latest['utc'],
                    'observedCommandSeconds': round((latest['monotonicNs'] - first['monotonicNs']) / 1e9, 2),
                    'client': latest['clientTotals'], 'server': latest['serverTotals'],
                    'sampleFileBytes': samples.stat().st_size})
print(json.dumps(result, separators=(',', ':')))
