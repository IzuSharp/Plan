#!/usr/bin/env python3
"""Freeze/stream closed08 with the unchanged reviewed engine and per-group disk gates."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PRIOR = HERE.parent / 'supplement-04'
FIXED_SHA = 'b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c'
ORDER = ('ordinary-consumers08', 'closed-evidence08', 'actual-packages08',
         'correctness-compiler08', 'support08', 'source-snapshots08')
HEADROOM_BYTES = 4 * 1024 * 1024
if hashlib.sha256((HERE / 'streaming_archive.py').read_bytes()).hexdigest() != FIXED_SHA:
    raise ValueError('Reviewed streaming engine changed')
spec = importlib.util.spec_from_file_location('reviewed_streaming_engine06', HERE / 'streaming_archive.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.HERE, engine.ROOT, engine.OUTPUT = HERE, ROOT, HERE
engine.NOTES = [
    'Closed rejected frame08 and independent selected owner cleanup only. Four real ordinary package consumers, Binding/Relations correctness and compile failure, local03 two-process diagnosis, twelve ordinary processes and independent rejection remain separate.',
    'The user cancelled all long measurements; no pending long gate or new performance/parity credit is created. Closing08 does not close DB-Exec-Parity-01.',
    'Measured baseline69b and published selected106 share a tree; rejected ordinary13b and diagnosticc429 are different identities. Thin bundle retains all four tips with baseline2ea prerequisite.',
    'Three Binding e1f AssemblyInfo files are reconstructed-byte-identical sidecars, explicitly keyed to the original sealed full hashes. Current13b paths and original receipts remain unchanged; no silent overwrite between historical build views.',
    'Prior archives01/02/03/04 supply baseline Dapper/toolchain/fixture, integrated05 source, observer and compiler/native dependencies. Existing archive05 rejected07 history is not duplicated.',
    'Six native alias destinations use byte- and mode-identical archive04 members. Four new nupkg feeds restore independent exact raw-cache copies. Original cache trees and SDK/runtime bin duplicates are not new payloads.',
    'Physical PostgreSQL/SQLite fixtures, bytecode, excluded intermediates and runtime copies are not archived. All actual selected ELF/DBG/generated/source/metadata/raw/failures remain. No source or artifact is deleted by this archiver.',
    'Cooperative sealing plus per-file size/mtime/inode checks before and after reading is not an atomic global snapshot. Every part, compressed stream, full tar including padding and member bytes/SHA/mode is verified.',
    'Unchanged single-thread lzma engine runs on CPU8 nice19. No canonical tar.xz, full tar or extraction roundtrip copy is materialized. Per-group conservative uncompressed budget plus metadata headroom gates actual free space.',
    'Active final public-package-verification13 remains outside this archive; root publishes and checkpoints later delivery receipts separately.',
]


def write(path, value):
    engine.dump(path, value)


def free_bytes():
    s = os.statvfs(ROOT)
    return s.f_bavail * s.f_frsize


def prepare_aliases():
    assert not (HERE / 'restore-alias-manifest.json').exists()
    plan = json.loads((HERE / 'alias-source-plan-01.json').read_text())
    rb = json.loads((ROOT / 'observations/recovery/archive04-remote-readback-01/receipt.json').read_text())
    assert rb['passed'] and rb['commit'] == 'ded73d7cd90cb692bea554c5e780df0ca9e05e3f'
    prior_map = {x['path']: x for x in rb['files']}
    target = HERE / 'dependency-manifests'
    target.mkdir(exist_ok=False)
    refs, members = [], {}
    for group in ('ordinary-consumers06', 'correctness-negative06'):
        rel = 'raw-archives/' + group + '/expanded-file-manifest.json'
        source = PRIOR / rel
        expected = prior_map[rel]
        content = source.read_bytes()
        assert len(content) == expected['bytes'] and hashlib.sha256(content).hexdigest() == expected['sha256']
        name = 'archives04-' + group + '.json'
        (target / name).write_bytes(content)
        refs.append({'file': 'dependency-manifests/' + name, 'sha256': expected['sha256'],
                     'sourceCommit': rb['commit'], 'sourceArchivePath': rel,
                     'gitBlobSha': expected['gitBlobSha']})
        records = json.loads(content)['files']
        members[name] = {x['path']: x for x in records}
        assert len(members[name]) == len(records)
    aliases, corrections = [], []
    for planned in plan['aliases']:
        a = dict(planned)
        if a['destination'].startswith('experiments/frame-pool-08/correctness-relations-02/publish/'):
            old_source = a['source']
            a['source'] = a['destination'].replace('experiments/frame-pool-08/correctness-relations-02/',
                                                  'experiments/tail-completion-06/correctness-01/')
            a['dependencyManifest'] = 'archives04-correctness-negative06.json'
            corrections.append({'destination': a['destination'], 'priorDraftSource': old_source,
                                'finalSource': a['source'],
                                'reason': 'Reviewed wrapper/helper require source and destination mode to match; select already-published0644 bytes rather than weakening mode validation.'})
        elif a['source'].startswith('consumers/tail06-'):
            a['dependencyManifest'] = 'archives04-ordinary-consumers06.json'
        if 'dependencyManifest' in a:
            m = members[a['dependencyManifest']][a['source']]
            assert (m['bytes'], m['sha256'], m['mode']) == (a['bytes'], a['sha256'], a['mode'])
            a['sourcePublishedDependency'] = 'archives04'
        aliases.append(a)
    assert len(aliases) == 10 and len(corrections) == 2
    write(target / 'index.json', {'manifests': refs, 'sourcePublicationCommit': rb['commit'],
          'sourcePublicationReceipt': 'observations/recovery/archive04-remote-readback-01/receipt.json'})
    write(HERE / 'restore-alias-manifest.json', {'task': 'DB-Exec-Parity-01', 'aliases': aliases,
          'sourceModesMatchDestinations': True, 'originalCacheTreesArchived': False,
          'preparationDraftCorrections': corrections,
          'scope': 'Six prior native copies and four new feed-to-cache copies. Exact SHA/bytes/mode, independent destination inode, no differing overwrite.'})
    print(json.dumps({'aliasesPrepared': len(aliases), 'draftModeSourcesCorrected': len(corrections)}), flush=True)


def freeze():
    assert not (HERE / 'selection.json').exists()
    author = json.loads((ROOT / 'experiments/frame-pool-08/implementation-resume.json').read_text())
    actual = json.loads((ROOT / 'experiments/frame-pool-08/ordinary-screen-01/resume.json').read_text())
    review = json.loads((ROOT / 'experiments/frame-pool-08/independent-ordinary-results-review-01/review-receipt.json').read_text())
    assert author['stage'] == 'closed-rejected' and actual['passed'] and actual['stage'] == 'completed'
    assert review['passedEvidenceAudit'] and review['selection'] == 'reject08_keepownership05'
    plan = json.loads((HERE / 'selection-budget-01.json').read_text())
    selected = {}
    assert set(plan['groups']) == set(ORDER)
    for group in ORDER:
        selected[group] = []
        for item in plan['groups'][group]:
            path = ROOT / item['path']
            assert path.is_file() and not path.is_symlink() and path.resolve() == path
            s = path.stat()
            assert stat.S_ISREG(s.st_mode)
            assert (s.st_size, s.st_mtime_ns, stat.S_IMODE(s.st_mode)) == (item['bytes'], item['mtimeNs'], item['mode'])
            selected[group].append({'path': item['path'], 'stamp': engine.stamp(path)})
    paths = [x['path'] for files in selected.values() for x in files]
    assert len(paths) == len(set(paths))
    aliases = json.loads((HERE / 'restore-alias-manifest.json').read_text())['aliases']
    assert all(a['source'] in paths for a in aliases if 'dependencyManifest' not in a)
    assert all(a['destination'] not in paths for a in aliases)
    selection = {'task': 'DB-Exec-Parity-01', 'createdUtc': engine.utc(), 'root': str(ROOT),
        'stage': 'frozen', 'groups': selected, 'excludedPaths': {n: plan['exclusions'] for n in selected},
        'dereferencedSymlinks': {n: [] for n in selected}, 'notes': engine.NOTES,
        'noNewPerformanceCredit': True, 'remotePublication': False, 'candidateRejected': True,
        'selectedProductCommit': '106fe68b6f6c2537f478daf65a71ab97cc4b15ff',
        'longMeasurementsCanceled': True, 'totalFiles': len(paths),
        'expandedBytes': sum(x['stamp'][0] for files in selected.values() for x in files),
        'reviewedStreamingVerifierSha256': FIXED_SHA, 'groupOrder': ORDER}
    write(HERE / 'selection.json', selection)
    identity = {name: engine.sha(HERE / name) for name in
                ('build_closed08.py', 'select_closed08.py', 'streaming_archive.py',
                 'restore_archive06.py', 'restore_artifact_aliases.py', 'selection.json')}
    write(HERE / 'source-identity.json', identity)
    write(HERE / 'resume.json', {'task': 'DB-Exec-Parity-01', 'stage': 'selection-frozen',
          'selectionSha256': identity['selection.json'], 'compressionStarted': False,
          'remotePublication': False, 'completedGroups': [], 'updatedUtc': engine.utc()})
    print(json.dumps({'frozen': True, 'files': len(paths), 'expandedBytes': selection['expandedBytes'],
                      'selectionSha256': identity['selection.json']}), flush=True)


def build(group):
    assert group in ORDER
    identity = json.loads((HERE / 'source-identity.json').read_text())
    for name, expected in identity.items():
        assert engine.sha(HERE / name) == expected, name
    assert not (HERE / (group + '-receipt.json')).exists()
    assert not (HERE / 'raw-archives' / group).exists()
    completed = []
    for earlier in ORDER[:ORDER.index(group)]:
        receipt = json.loads((HERE / (earlier + '-receipt.json')).read_text())
        verification = json.loads((HERE / (earlier + '-verification.json')).read_text())
        assert receipt['passed'] and receipt['verification'] == verification and verification['passed']
        assert verification['name'] == earlier
        completed.append(earlier)
    selection = json.loads((HERE / 'selection.json').read_text())
    files = selection['groups'][group]
    conservative = sum(512 + ((x['stamp'][0] + 511) // 512) * 512 + 2048 for x in files) + 10240
    available = free_bytes()
    gate = {'group': group, 'checkedUtc': engine.utc(), 'actualFreeBytes': available,
            'conservativeTarBudgetBytes': conservative, 'metadataHeadroomBytes': HEADROOM_BYTES,
            'passed': available >= conservative + HEADROOM_BYTES, 'priorGroupsVerified': completed}
    write(HERE / (group + '-disk-gate.json'), gate)
    if not gate['passed']:
        write(HERE / 'resume.json', {'task': 'DB-Exec-Parity-01', 'stage': 'blocked-disk-gate',
              'nextGroup': group, 'completedGroups': completed, 'gate': gate, 'remotePublication': False})
        raise RuntimeError('Insufficient actual free space for conservative next-group budget')
    write(HERE / 'resume.json', {'task': 'DB-Exec-Parity-01', 'stage': 'group-building',
          'group': group, 'completedGroups': completed, 'gate': gate, 'remotePublication': False})
    engine.build(group)
    for name, expected in identity.items():
        assert engine.sha(HERE / name) == expected, name
    completed.append(group)
    write(HERE / 'resume.json', {'task': 'DB-Exec-Parity-01', 'stage': 'all-groups-verified' if completed == list(ORDER) else 'group-verified',
          'completedGroups': completed, 'actualFreeBytes': free_bytes(), 'updatedUtc': engine.utc(),
          'remotePublication': False, 'selectionSha256': identity['selection.json']})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('aliases', 'freeze', 'build'))
    parser.add_argument('--name', choices=ORDER)
    args = parser.parse_args()
    os.sched_setaffinity(0, {8})
    os.nice(19)
    if args.action == 'aliases':
        prepare_aliases()
    elif args.action == 'freeze':
        freeze()
    else:
        if args.name is None:
            parser.error('build requires --name')
        build(args.name)
