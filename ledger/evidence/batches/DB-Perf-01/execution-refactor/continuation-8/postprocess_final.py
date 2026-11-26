#!/usr/bin/env python3
"""Invoke the unchanged final analyzers after the serial campaign; keep receipts."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/workspace/scratch/166b48a091b9/recovery')
MEASUREMENTS = Path('/workspace/scratch/fd78534029f7/measurements')
EVIDENCE = Path('/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor')
PRODUCT = Path('/tmp/DB-Exec-10-pack-sqlite-02')
FREEZE_SHA = 'fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a'


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def run(name, script, args):
    argv = [sys.executable, str(script), *map(str, args)]
    stdout_path = ROOT / (name + '.stdout.log')
    stderr_path = ROOT / (name + '.stderr.log')
    record = {'argv': argv, 'cwd': str(ROOT), 'scriptSha256': digest(script),
              'startedUtc': now(), 'observerAffinity': sorted(os.sched_getaffinity(0)),
              'stdoutPath': str(stdout_path), 'stderrPath': str(stderr_path),
              'scope': 'Post-campaign read-only evidence analysis; no workload execution'}
    write(ROOT / (name + '.command-start.json'), record)
    with stdout_path.open('xb') as stdout, stderr_path.open('xb') as stderr:
        result = subprocess.run(argv, cwd=ROOT, stdout=stdout, stderr=stderr, check=False)
    record.update(exitCode=result.returncode, finishedUtc=now(),
                  stdoutSha256=digest(stdout_path), stderrSha256=digest(stderr_path))
    write(ROOT / (name + '.command.json'), record)
    print(json.dumps({'command': name, 'exitCode': result.returncode,
                      'receipt': str(ROOT / (name + '.command.json'))}), flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)


def main():
    supervisor = read(ROOT / 'campaign-supervisor-01.json')
    assert [entry['provider'] for entry in supervisor['runs']] == ['sqlite', 'postgresql']
    assert all(entry['status'] == 'completed' and entry['exitCode'] == 0
               and entry.get('finishedUtc') for entry in supervisor['runs']), 'Campaign still running or failed'
    assert digest(MEASUREMENTS / 'final-freeze-01.json') == FREEZE_SHA
    write(ROOT / 'host-after-final-01.json', {
        'schemaVersion': 1, 'utc': now(), 'uname': platform.uname()._asdict(),
        'bootId': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        'observerAffinity': sorted(os.sched_getaffinity(0)),
        'cpuStat': Path('/proc/stat').read_text(), 'meminfo': Path('/proc/meminfo').read_text(),
        'loadavg': Path('/proc/loadavg').read_text(),
        'cgroupMembership': Path('/proc/self/cgroup').read_text(),
        'cgroupMountAvailable': Path('/sys/fs/cgroup/cgroup.controllers').exists(),
        'disk': {name: shutil.disk_usage(name)._asdict() for name in ('/workspace', '/tmp')},
        'supervisorSha256': digest(ROOT / 'campaign-supervisor-01.json'),
        'scope': 'Post-campaign local observation; no exclusive physical-host or invisible quota claim; namespace process enumeration is not whole-host proof',
    })
    run('final-index-01', EVIDENCE / 'continuation-5/prepare_load_index.py', [
        '--directory', MEASUREMENTS / 'sqlite-final-01',
        '--directory', MEASUREMENTS / 'postgresql-final-01',
        '--host-record', ROOT / 'host-before-final-recovery-01.json',
        '--group-prefix', 'DB-Exec-11-frozen17da', '--output', ROOT / 'final-index-01.json'])
    run('final-analysis-01', EVIDENCE / 'continuation-3/analysis/analyze_execution.py', [
        '--index', ROOT / 'final-index-01.json', '--korda-root', PRODUCT,
        '--output', ROOT / 'final-analysis-01.json'])
    run('final-identity-audit-01', EVIDENCE / 'continuation-7/local-load-tools/audit_final_identity.py', [
        'audit', '--freeze', MEASUREMENTS / 'final-freeze-01.json', '--freeze-sha256', FREEZE_SHA,
        '--analysis', ROOT / 'final-analysis-01.json', '--output', ROOT / 'final-identity-audit-01.json'])
    report = read(ROOT / 'final-analysis-01.json')
    audit = read(ROOT / 'final-identity-audit-01.json')
    assert report['finalFour']['fourCompleteRawReceipts'] is True
    assert report['finalFour']['sameHostAndSerialIncludingRecordedIdle'] is True
    assert report['inputsChangedDuringAnalysis'] == []
    assert audit['status'] == 'passed' and audit['inputsUnchanged'] is True
    result = {'schemaVersion': 1, 'scope': 'Extracted verified final metrics; original arithmetic and identity reports decide eligibility. No new threshold or gate.',
              'analysis': {'path': str(ROOT / 'final-analysis-01.json'), 'sha256': digest(ROOT / 'final-analysis-01.json')},
              'audit': {'path': str(ROOT / 'final-identity-audit-01.json'), 'sha256': digest(ROOT / 'final-identity-audit-01.json')},
              'finalFour': report['finalFour'], 'observations': []}
    for index, item in enumerate(report['observations']):
        assert item['timingCredit'] is True
        metrics = item['metrics']
        normal = metrics['measurement']['normalized']
        raw = read(item['input']['path'])
        assert digest(item['input']['path']) == item['input']['storedSha256']
        client = metrics['client']
        result['observations'].append({
            'id': item['id'], 'provider': item['provider'], 'cohort': item['cohort'],
            'sourcePointer': '/observations/' + str(index), 'rawIdentity': item['input'],
            'issues': item['issues'], 'interval': item['finalInterval'],
            'counts': normal['counts'], 'correctnessPassed': normal['correctnessPassed'],
            'oracleFailures': normal['oracleFailures'], 'fullCaseCoverage': normal['fullCaseCoverage'],
            'elapsedThroughDrainSeconds': normal['elapsedThroughDrainSeconds'],
            'successfulOperationsPerSecond': metrics['successfulThroughputThroughDrain'],
            'arrivalRate': metrics['requestedArrivalRate'], 'histograms': metrics['measurement']['histograms'],
            'cpu': client['cpu'], 'peakRssBytes': client['memory']['process_peak_rss_bytes'],
            'idle': raw['Idle'], 'idleRssBytes': metrics['idleRssBytes'], 'managed': client['managed'],
            'nativeCounters': {stage: raw[stage] for stage in ('Before', 'After', 'Drained')},
            'runtimeFfiCountsInThisOrdinaryRun': None, 'protocolReplyCountsInThisOrdinaryRun': None,
            'serverCpuScope': item.get('resources', {}).get('serverCpuScope'),
            'resourceObservation': item.get('resources'),
        })
    write(ROOT / 'final-metrics-01.json', result)
    print(json.dumps({'status': 'completed', 'observations': len(result['observations']),
                      'identityStatus': audit['status'], 'inputCount': len(audit['inputFiles']),
                      'metrics': str(ROOT / 'final-metrics-01.json')}), flush=True)


if __name__ == '__main__':
    main()
