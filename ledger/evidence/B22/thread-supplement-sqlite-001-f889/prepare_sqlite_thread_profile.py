#!/usr/bin/env python3
"""Derive a prospective classified-thread supplement, preserving failed inputs."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys

ROOT = Path('/workspace/scratch/58d2a6adf1c3')
RUNS = ROOT / 'task07-runs'
SOURCE = ROOT / '.worktree/Task-07-B22-threads-f889-linux/NativeWeave'
STAGE = RUNS / 'b22-finish-evidence-f889'
REVIEW = Path('/workspace/scratch/f889f7506370/recovery-release-audit')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bound(path):
    return {'path': str(path), 'sha256': sha(path)}


def main():
    output = RUNS / 'b22-corrected-thread-supplement-001-f889'
    output.mkdir(exist_ok=True)
    assert not (output / 'sqlite-frozen.json').exists(), 'A frozen profile may not be regenerated'
    parent_path = RUNS / 'b22-corrected-frozen-profiles-001-f889/sqlite-aot.json'
    parent = json.loads(parent_path.read_text())
    profile = copy.deepcopy(parent)
    for key in ('frozenUnixNs', 'reviewNote', 'candidateSha256'):
        profile.pop(key)
    profile['status'] = 'candidate-from-passed-calibration'
    profile['parentFrozenProfile'] = bound(parent_path)
    assert parent['peakCaps']['threads'] == 24 and parent['idleCaps']['threads'] == 21
    diagnostic = RUNS / 'b22-thread-diagnosis-sqlite-001-f889'
    receipt = json.loads((diagnostic / 'receipt.json').read_text())
    assert receipt['status'] == 'diagnostic-completed' and receipt['identity'] == parent['identity']
    rows = [json.loads(line) for line in (diagnostic / 'thread-owners.jsonl').read_text().splitlines()]
    names = rows[-1]['threads']['countsByName']
    fixed_idle = {name: count for name, count in names.items()
                  if name not in ('.NET TP Worker', 'sqlx-sqlite-wor', 'nw-db-worker')}
    fixed_count = sum(fixed_idle.values()) + 4
    minimum_sqlx = min(row['threads']['countsByName'].get('sqlx-sqlite-wor', 0) for row in rows)
    assert fixed_count == 14 and minimum_sqlx == 1
    peak_residual = parent['peakCaps']['threads'] - fixed_count - minimum_sqlx
    idle_residual = parent['idleCaps']['threads'] - fixed_count - minimum_sqlx
    assert (peak_residual, idle_residual) == (9, 6)
    monitor = SOURCE / 'tests/Verification.EndToEnd/descriptor_profile.py'
    policy = {
        'monitorSha256': sha(monitor),
        'interpretation': 'Finite observational budgets for the exact four-slot/four-arrival-per-second workload, not global .NET ThreadPool bounds. ProcessorCount2 and physical pool permits do not cap adaptive managed workers.',
        'derivation': 'Original measured total peak24 / idle21 minus observed fixed14 and minimum witnessed SQLx1 gives shared dynamic residual9 /6. Reserve all18 configured physical SQLite connections separately: total peak41 / idle38. Managed workers and database workers beyond4async share the residual; no independent blocking reserve can mask managed growth.',
        'classCaps': {**fixed_idle, 'nw-db-worker': 12, 'sqlx-sqlite-wor': 18, '.NET TP Worker': peak_residual},
        'fixedIdleCounts': fixed_idle,
        'fixedObservedThreadCount': fixed_count,
        'asyncDatabaseWorkers': 4,
        'maximumDatabaseBlockingWorkers': 8,
        'configuredSqlitePhysicalConnectionSlots': 18,
        'peakDynamicResidualCap': peak_residual,
        'idleDynamicResidualCap': idle_residual,
        'originalPeakThreads': parent['peakCaps']['threads'],
        'originalIdleThreads': parent['idleCaps']['threads'],
        'minimumWitnessedSqlxWorkers': minimum_sqlx,
        'historicalFailed25thThreadAttributed': False,
        'diagnosticPeak25Reproduced': False,
        'idleSqlxRule': 'Exact equality between SQLx worker count and contemporaneous application.sqlite plus consumer.sqlite main-file descriptors, with no thread/descriptor read races.',
        'closureRule': 'Retain every thread sample; adjudicate pre-closure samples by their endedMonotonicNs against the ordinary stageCompletedBeforeClosureNs. The same truncated Server close-helper name must not be misclassified as a steady thread. A fresh classified live idle witness must precede closure by at most3.3 seconds.',
        'diagnosticReceipt': bound(diagnostic / 'receipt.json'),
        'diagnosticThreadOwners': bound(diagnostic / 'thread-owners.jsonl'),
        'diagnosticScript': bound(STAGE / 'diagnose_threads.py'),
        'diagnosticReview': bound(REVIEW / 'b22-sqlite-thread-diagnostic-review-001.json'),
        'runtimeSourceReview': bound(STAGE / 'threadpool-source-review.json'),
        'failedAttemptReceipt': bound(RUNS / 'b22-corrected-steady-sqlite-001-f889/receipt.json'),
        'failedAttemptStatus': 'failed; no predecessor time credited and no retrospective pass',
        'sourceFiles': {str(path.relative_to(SOURCE)): sha(path) for path in [
            SOURCE / 'native/database/host/src/runtime.rs',
            SOURCE / 'native/server/host/src/engine.rs',
            SOURCE / 'src/Reference.TaskService/ServiceConfiguration.cs',
            SOURCE / 'src/Verification.EndToEnd/Observer/ReferenceObserver.cs',
            SOURCE / 'src/Verification.EndToEnd/Observer/ObserverEntryPoint.cs']},
        'unchangedGates': 'Every RSS, managed GCHandle, native owner, Server, file-descriptor and duration limit remains identical to the prior frozen profile; the exact ordinary controller/application/observer/native bytes are unchanged.',
    }
    profile['threadThresholdSupplement'] = policy
    profile['peakCaps']['threads'] = fixed_count + 18 + peak_residual
    profile['idleCaps']['threads'] = fixed_count + 18 + idle_residual
    profile['fdThresholdSupplement']['priorDescriptorMonitor'] = {
        'path': parent['fdThresholdSupplement']['descriptorMonitorSource'],
        'sha256': parent['fdThresholdSupplement']['descriptorMonitorSha256']}
    profile['fdThresholdSupplement']['descriptorMonitorSource'] = str(monitor)
    profile['fdThresholdSupplement']['descriptorMonitorSha256'] = sha(monitor)
    profile['thresholdDerivation'] += '; independently reviewed classified thread residual supplement preserves original failed total-band evidence and reserves configured physical pool growth'
    for band in ('peakCaps', 'idleCaps'):
        assert {k: v for k, v in profile[band].items() if k != 'threads'} == {k: v for k, v in parent[band].items() if k != 'threads'}
    sys.path.insert(0, str(SOURCE / 'tests/Verification.EndToEnd'))
    import descriptor_profile
    assert all(descriptor_profile.thread_within_band(row['threads'], policy) for row in rows)
    assert descriptor_profile.thread_within_band(rows[-1]['threads'], policy, idle=True)
    assert descriptor_profile.sqlx_workers_match_files(rows[-1]['threads'], rows[-1]['descriptors'])
    path = output / 'sqlite-candidate.json'
    path.write_text(json.dumps(profile, indent=2) + '\n')
    print(json.dumps({'path': str(path), 'sha256': sha(path), 'monitorSha256': sha(monitor),
                      'peakThreads': profile['peakCaps']['threads'], 'idleThreads': profile['idleCaps']['threads'],
                      'diagnosticRowsWithinProspectiveClassBands': len(rows)}))


if __name__ == '__main__':
    main()
