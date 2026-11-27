#!/usr/bin/env python3
"""Freeze and stream-archive the closed, rejected tail06 experiment only."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXED = HERE.parent / 'supplement-03/streaming_archive.py'
EXPECTED_FIXED_SHA = 'b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c'
BASE = '2ea67ce1902f330679c3ebff4d6d5733be20f69c'
SOURCE_HEADS = {
    'Korda-tail-completion06': '4a9e4435ea5c836be44fb00dc4219301567072c6',
    'Korda-tail06-diag-before': '197f0d3444cf3cfc120982273d48d1dcf74f60db',
    'Korda-tail06-diag-tail': 'ba4e7ec9bf93ad313dbbb167457189a5f95429da',
    'Korda-tail06-negative': '4efce12ff6c1ece1f059e5b209e4e6a02a38acce',
}
assert hashlib.sha256(FIXED.read_bytes()).hexdigest() == EXPECTED_FIXED_SHA
spec = importlib.util.spec_from_file_location('fixed_archive_engine', FIXED)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.HERE, engine.ROOT, engine.OUTPUT = HERE, ROOT, HERE

def relatives(paths):
    return [str(p.relative_to(ROOT)) for p in paths]

ordinary = ['tail06-sqlite', 'tail06-postgresql']
diagnostic = ['tail06diag-before-sqlite', 'tail06diag-before-postgresql',
              'tail06diag-tail-sqlite', 'tail06diag-tail-postgresql']
recovery_names = ['run_verified_mixed_cell06.py', 'freeze_verified_mixed_inputs06.py',
    'run_verified_series06.py', 'check_verified_wrapper06.py', 'verified-wrapper06-review-01',
    'verified-wrapper06-independent-review-01', 'closed-build-cleanup-proposal-06',
    'tail06diag-intermediate-cleanup-01', 'legacy-pg-retirement-proposal-06',
    'tail06-fixture-retirement-01.json']
plan = json.loads((HERE / 'selection-plan-02.json').read_text())
GROUPS = {
    'ordinary-consumers06': [prefix + name for name in ordinary for prefix in ('consumers/', 'builds/')],
    'diagnostic-consumers06': [prefix + name for name in diagnostic for prefix in ('consumers/', 'builds/')],
    'correctness-negative06': ['experiments/tail-completion-06/' + n for n in ('correctness-01', 'negative-control-01')],
    'tail-evidence06': ['experiments/tail-completion-06'],
    'wrapper-recovery06': ['experiments/recovery/' + n for n in recovery_names] + [
        'observations/recovery/archive03-published.json',
        'experiments/recovery/archive-recovery-04/pending-worker-d-diagnostic-packages-06.json'],
    'legacy-worker-diag-packages06': [f['path'] for f in plan['groups']['legacy-worker-diag-packages06']],
    'compiler-package-inputs06': [f['path'] for f in plan['groups']['compiler-package-inputs06']],
    'source-snapshots06': relatives([HERE / 'source-snapshots', HERE / 'source-snapshots.json']),
}
engine.GROUPS = GROUPS
engine.NOTES = [
    'Closed tail06 experiment only: ordinary two and diagnostic four real consumers, correctness and expected negative control, four mechanism runs, 114 ordinary short processes and twelve 30-second mixed cells. Tail06 was rejected for unified adoption; integrated05 remains selected.',
    'The user cancelled every 1800-second final/before long measurement for this round. Short runs, diagnostic runs and controls retain their original credit/limitations; this archive adds no performance or parity credit.',
    'Prerequisites: archives-01 at Plan b54054bd1f3befe94e1817cc29f494bd782854b9; archives-02 at 27e0f35709036b0737ed101ba6472ce1461c0538; archives-03 at d7e2d96db38e2879e0318692e00575158db42a77. Restore their documented Stage1 foundation dependencies first.',
    'Source snapshots are one thin bundle plus binary patch per distinct head, excluding reachable objects of 2ea67ce1902f330679c3ebff4d6d5733be20f69c already captured in archives-02/source-snapshots/Korda. No whole repository or duplicate changed-files directory is copied.',
    'Physical PostgreSQL data and SQLite database/WAL/SHM fixtures, reproducible obj/bin/cache outputs and .o/.a files are excluded. Actual publish/out ELF, DBG, native libraries, nupkg, generated C#, assets/response/export files, commands, every raw result and failure identity remain.',
    'Six completed mixed PostgreSQL fixtures were separately retired by the reviewed helper. Their full configuration copies and retirement inventories/receipts are included; the thirteen older proposed retirements remain paused and were not performed.',
    'Six provider raw-archive cache paths are explicitly restored from byte-identical selected feed nupkg via a checked copy hook. Their original cache tree was not archived. Three compiler raw nupkg and four old Worker-D diagnostic nupkg gaps are now included exactly once.',
    'Source freeze is cooperative sealing plus per-file selected size/mtime/inode checked before and after reading, not a filesystem-wide atomic snapshot. Each expanded member has SHA256/mode; every part and whole compressed/tar stream is verified.',
    'No canonical tar.xz or extraction roundtrip copy is created. Single-thread lzma and verification run on CPU 8 at nice 19 outside measurement windows. Original files are never deleted by this archiver.',
    'No future HostPull source or experiment is selected. No tree, commit, branch, ref or remote publication is created by this archiver.',
]

def capture_sources():
    folder = HERE / 'source-snapshots'
    folder.mkdir(exist_ok=False)
    records = []
    for name, expected in SOURCE_HEADS.items():
        worktree = ROOT / 'worktrees' / name
        head = engine.git(worktree, 'rev-parse', 'HEAD').decode().strip()
        status = engine.git(worktree, 'status', '--porcelain=v1', '--untracked-files=no').decode()
        if head != expected or status:
            raise RuntimeError('Expected sealed tracked source changed: ' + name)
        target = folder / name
        target.mkdir()
        patch = target / 'from-2ea.patch'
        patch.write_bytes(engine.git(worktree, 'diff', '--binary', '--full-index', BASE, head))
        bundle = target / 'commits.bundle'
        argv = ['git', '-C', str(worktree), '-c', 'pack.threads=1', 'bundle', 'create', str(bundle), 'HEAD', '^' + BASE]
        created = subprocess.run(argv, capture_output=True, text=True, check=True)
        verified = subprocess.run(['git', '-C', str(worktree), 'bundle', 'verify', str(bundle)], capture_output=True, text=True, check=True)
        (target / 'bundle-verification.txt').write_text(verified.stdout + verified.stderr)
        prerequisites = []
        with bundle.open('rb') as stream:
            for line in stream:
                if line == b'\n':
                    break
                if line.startswith(b'-'):
                    prerequisites.append(line.decode().rstrip())
        changed = []
        for relative in filter(None, engine.git(worktree, 'diff', '--name-only', '-z', BASE, head).decode().split('\0')):
            exists = subprocess.run(['git', '-C', str(worktree), 'cat-file', '-e', head + ':' + relative], capture_output=True)
            if exists.returncode:
                changed.append({'path': relative, 'deleted': True})
            else:
                data = engine.git(worktree, 'show', head + ':' + relative)
                changed.append({'path': relative, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        if engine.git(worktree, 'rev-parse', 'HEAD').decode().strip() != head or engine.git(worktree, 'status', '--porcelain=v1', '--untracked-files=no').decode() != status:
            raise RuntimeError('Source changed while capturing: ' + name)
        record = {'worktree': name, 'originalWorktreePath': str(worktree), 'headCommit': head,
            'tree': engine.git(worktree, 'rev-parse', head + '^{tree}').decode().strip(),
            'excludedBaseCommit': BASE, 'statusAtSnapshot': status, 'untrackedFilesExcluded': True,
            'bundlePrerequisites': prerequisites, 'patchBytes': patch.stat().st_size,
            'patchSha256': engine.sha(patch), 'bundleBytes': bundle.stat().st_size,
            'bundleSha256': engine.sha(bundle), 'changedFiles': changed,
            'bundleCommand': argv, 'bundleCreateStdout': created.stdout, 'bundleCreateStderr': created.stderr,
            'bundleVerificationPassed': True,
            'restore': 'Restore archives-02 source bundle first. In a repository containing its prerequisite commits, git bundle verify then git fetch commits.bundle HEAD; use git worktree add --detach at the recorded head. The binary patch is a second review route.'}
        engine.dump(target / 'identity.json', record)
        records.append(record)
    engine.dump(HERE / 'source-snapshots.json', {'task': 'DB-Exec-Parity-01', 'excludedBaseCommit': BASE,
        'snapshots': records, 'sameHeadWorktreeMappings': {
            'Korda-tail06-sqlite': {'canonicalSnapshot': 'Korda-tail-completion06', 'headCommit': SOURCE_HEADS['Korda-tail-completion06']},
            'Korda-tail06-postgresql': {'canonicalSnapshot': 'Korda-tail-completion06', 'headCommit': SOURCE_HEADS['Korda-tail-completion06']}},
        'noWholeRepositoryCopy': True, 'changedFileBytesStoredInBundleAndPatchOnly': True})

def prepare():
    if (HERE / 'selection.json').exists():
        raise RuntimeError('Selection already frozen; do not overwrite; resume individual builds')
    (HERE / 'streaming_archive.py').write_bytes(FIXED.read_bytes())
    for campaign in ['ordinary-screen-01', 'zero-cost-06']:
        p = ROOT / 'experiments/tail-completion-06' / campaign
        if campaign == 'zero-cost-06':
            state = json.loads((p / 'series-01.plan.resume.json').read_text())
            if not state.get('passed') or state.get('stage') != 'completed':
                raise RuntimeError('Mixed campaign is not closed')
    retired = json.loads((ROOT / 'experiments/recovery/tail06-fixture-retirement-01.json').read_text())
    if len(retired['receipts']) != 6 or not all(x['rawEvidenceUnchanged'] and not x['dataExistsAfter'] for x in retired['receipts']):
        raise RuntimeError('Six completed mixed fixture retirement receipts are required')
    for required in ['independent-mixed-gate-review-01/README.md', 'independent-ordinary-results-review-01/README.md', 'coordinator-readonly-01/README.md']:
        if not (ROOT / 'experiments/tail-completion-06' / required).is_file():
            raise RuntimeError('Closed review missing: ' + required)
    if not (HERE / 'source-snapshots.json').exists():
        capture_sources()
    selection = engine.select()
    duplicate_prefixes = tuple('experiments/tail-completion-06/' + n + '/' for n in ('correctness-01', 'negative-control-01'))
    old = selection['groups']['tail-evidence06']
    selection['groups']['tail-evidence06'] = [f for f in old if not f['path'].startswith(duplicate_prefixes)]
    selection['excludedPaths']['tail-evidence06'] += [{'path': p.rstrip('/'), 'reason': 'included once in correctness-negative06'} for p in duplicate_prefixes]
    future_prefix = 'experiments/tail-completion-06/local-preference-options-01/'
    selection['groups']['tail-evidence06'] = [f for f in selection['groups']['tail-evidence06'] if not f['path'].startswith(future_prefix)]
    selection['excludedPaths']['tail-evidence06'].append({'path': future_prefix.rstrip('/'), 'reason': 'active future HostPull design draft explicitly excluded; subsequent work is outside this archive scope'})
    all_paths = [f['path'] for files in selection['groups'].values() for f in files]
    if len(all_paths) != len(set(all_paths)):
        raise RuntimeError('Cross-group duplicate member path')
    if any('hostpull' in p.lower() or '/postgres-data/' in p or p.endswith(('.sqlite', '.db', '.sqlite-wal', '.sqlite-shm')) for p in all_paths):
        raise RuntimeError('Future or physical database input selected')
    aliases = json.loads((HERE / 'restore-alias-plan-01.json').read_text())['aliases']
    for alias in aliases:
        if alias['source'] not in all_paths:
            raise RuntimeError('Alias source is not selected: ' + alias['source'])
    engine.dump(HERE / 'restore-alias-manifest.json', {'task': 'DB-Exec-Parity-01',
        'aliases': [{k:v for k,v in a.items() if k != 'methodPlanned'} for a in aliases],
        'mode': 'independent byte copy of exact selected payload, never hardlink the source',
        'originalCacheTreesArchived': False, 'existingDifferentDestination': 'fail without overwrite'})
    selection.update({'stage': 'frozen', 'closedRootGroups': GROUPS,
        'reviewedStreamingVerifierSha256': EXPECTED_FIXED_SHA,
        'scopeDecision': 'Tail06 rejected; integrated05 retained. Short evidence only; all long measurements cancelled.',
        'archiveDependencies': {'archives01': 'b54054bd1f3befe94e1817cc29f494bd782854b9',
            'archives02': '27e0f35709036b0737ed101ba6472ce1461c0538',
            'archives03': 'd7e2d96db38e2879e0318692e00575158db42a77'},
        'totalFiles': len(all_paths), 'expandedBytes': sum(f['stamp'][0] for v in selection['groups'].values() for f in v)})
    engine.dump(HERE / 'selection.json', selection)
    engine.dump(HERE / 'source-identity.json', {'builderPath': str(Path(__file__).resolve()),
        'builderSha256': engine.sha(Path(__file__)), 'reviewedEnginePath': str(FIXED),
        'reviewedEngineSha256': EXPECTED_FIXED_SHA, 'excludedSourceBase': BASE,
        'noNewPerformanceCredit': True})
    engine.dump(HERE / 'resume.json', {'task': 'DB-Exec-Parity-01', 'updatedUtc': engine.utc(),
        'stage': 'selection-frozen-ready-for-streaming-build', 'selectionSha256': engine.sha(HERE / 'selection.json'),
        'selectionFrozen': True, 'compressionStarted': False, 'remotePublication': False,
        'longMeasurementsCancelledByUser': True, 'legacy13FixtureRetirement': 'paused and unperformed'})
    print(json.dumps({'groups': {n: {'files': len(v), 'expandedBytes': sum(x['stamp'][0] for x in v)} for n,v in selection['groups'].items()},
        'freeBytes': os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'build'])
    parser.add_argument('--name', choices=list(GROUPS))
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
    else:
        if not args.name:
            parser.error('--name required')
        receipt = HERE / (args.name + '-receipt.json')
        if receipt.exists() and json.loads(receipt.read_text()).get('passed'):
            print(json.dumps({'alreadyVerified': args.name, 'receipt': str(receipt)}))
        else:
            engine.build(args.name)
