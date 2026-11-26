#!/usr/bin/env python3
"""Copy small completed build receipts; never build, run, or rehash binaries."""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET

BASE = Path('/workspace/scratch/4a65d70f0fe1')
OUT = Path(__file__).resolve().parent / 'public-build-inputs-01'
OUT.mkdir(exist_ok=True)
PUBLIC = '8789a45a52cc0cc0a0b62737542d9c120b753c9b'
TREE = 'c8f398ae4db2d39302335a51a6378b737409f2fb'
BEFORE = 'f0078da720e07031bc56464995af6791c41aaae8'
sha = lambda value: hashlib.sha256(value).hexdigest()
copied = []


def copy(path, relative):
    path = Path(path); value = path.read_bytes(); destination = OUT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(value)
    assert destination.read_bytes() == value
    copied.append({'path': relative, 'sourcePath': str(path), 'bytes': len(value), 'sha256': sha(value)})
    return json.loads(value) if path.suffix == '.json' else value


groups = []
for provider in ('sqlite', 'postgresql'):
    public = copy(BASE / f'artifacts/command-public-build-{provider}-01.json', f'{provider}/public-build.json')
    comparison = copy(BASE / f'artifacts/command-comparison-build-{provider}-01.json', f'{provider}/comparison-build.json')
    assert public['sourceCommit'] == comparison['sourceCommit'] == PUBLIC
    assert public['sourceTree'] == TREE and public['sourceDirty'] is False
    assert all(item['exitCode'] == 0 for item in public['records'] + comparison['records'])
    release = copy(BASE / f'artifacts/command-packages-01/{provider}/release.json', f'{provider}/release.json')
    native = copy(BASE / f'artifacts/command-native-{provider}-01/manifest.json', f'{provider}/native-manifest.json')
    assert release['source_commit'] == native['sourceCommit'] == PUBLIC
    assert release['source_tree'] == native['sourceTree'] == TREE
    assert release['source_dirty'] is False and native['sourceDirty'] is False
    assert len(release['packages']) == len(native['assets']) == 1
    package = release['packages'][0]
    assert package['native']['sha256'] == native['assets'][0]['sha256']
    consumers = []
    for kind in ('phases', 'workload'):
        folder = BASE / f'consumers/command-{provider}-{kind}-01'
        receipt = copy(folder / 'build-receipt.json', f'{provider}/candidate-{kind}-receipt.json')
        assert receipt['exit_code'] == 0 and receipt['project_references'] == 0
        assert receipt['package'] == package['id'] and receipt['version'] == '0.1.0-ci.1'
        assert list(receipt['native_images'].values()) == [package['native']['sha256']]
        consumers.append({'kind': kind, 'path': str(folder), 'packageSha256': receipt['package_sha256'],
                          'executableSha256': receipt['executable_sha256'], 'projectReferences': 0,
                          'nativeImages': receipt['native_images']})
        if kind == 'workload': candidate = receipt
    baseline_dir = BASE / f'consumers/before-current-{provider}-workload-01'
    baseline = copy(baseline_dir / 'build-receipt.json', f'{provider}/before-current-workload-receipt.json')
    assert baseline['exit_code'] == 0 and baseline['project_references'] == 0
    assert baseline['sources'] == candidate['sources']
    assert baseline['builder_sha256'] == candidate['builder_sha256']
    assert baseline['workloadManifestSha256'] == candidate['workloadManifestSha256']
    ffi_dir = BASE / f'consumers/ffi-command-{provider}-workload-01'
    ffi = copy(ffi_dir / 'diagnostic-build.json', f'{provider}/ffi-workload-receipt.json')
    assert len(ffi['symbols']) == 59 and ffi['abiSourceCommit'] == PUBLIC
    assert ffi['TimingComparisonEligible'] is False and ffi['timingCredit'] is False and ffi['allocationCredit'] is False
    assert ffi['sourceReceiptSha256'] == sha((BASE / f'consumers/command-{provider}-workload-01/build-receipt.json').read_bytes())
    assert ffi['sourceExecutableSha256'] == candidate['executable_sha256']
    assert ffi['sourcePackageSha256'] == candidate['package_sha256']
    assert ffi['nativeImagesUnchanged'] and ffi['packageUnchanged'] and ffi['ordinaryConsumerUnchanged']
    package_bindings = []
    for label, source, feed, expected in (
        ('candidate', PUBLIC, BASE / f'artifacts/command-packages-01/{provider}/feed', candidate['package_sha256']),
        ('before', BEFORE, BASE / 'worktrees/DB-Exec-02-before-f0078da7/artifacts/public/feed', baseline['package_sha256']),
    ):
        path = feed / (candidate['package'] + '.0.1.0-ci.1.nupkg')
        # Read only the small ZIP metadata entry. Binary/package hashes remain
        # the original builder observations during the measurement isolation.
        with zipfile.ZipFile(path) as archive:
            name = candidate['package'] + '.nuspec'; value = archive.read(name)
        repository = ET.fromstring(value).find('.//{*}repository')
        assert repository is not None and repository.attrib['commit'] == source
        target = f'{provider}/{label}.nuspec'; (OUT / target).write_bytes(value)
        copied.append({'path': target, 'sourcePath': str(path) + '!' + name, 'bytes': len(value), 'sha256': sha(value)})
        if label == 'candidate': assert sha(value) == package['unsigned_entries'][name]
        package_bindings.append({'role': label, 'path': str(path), 'packageSha256AsRecorded': expected,
                                 'repositoryCommit': source, 'nuspecSha256': sha(value),
                                 'packageBinaryRehashedHere': False})
    groups.append({'provider': provider, 'candidateSource': PUBLIC, 'candidateTree': TREE,
                   'publicStages': [{'stage': item['stage'], 'exitCode': item['exitCode']} for item in public['records']],
                   'comparisonStages': [{'stage': item['stage'], 'exitCode': item['exitCode']} for item in comparison['records']],
                   'candidateConsumers': consumers, 'beforePackageSource': BEFORE,
                   'beforeCurrentWorkload': {'path': str(baseline_dir), 'executableSha256': baseline['executable_sha256'],
                                             'packageSha256': baseline['package_sha256']},
                   'freshBeforeAndCandidateHarnessSourceHashesEqual': True,
                   'ffi': {'path': str(ffi_dir), 'symbols': 59, 'timingCredit': False, 'allocationCredit': False,
                           'executableSha256': ffi['outputs']['DbPerf.Korda'], 'shimSha256': ffi['outputs']['libcursor_probe.so']},
                   'packages': package_bindings})
for filename in ('build-command-public-inputs.py', 'build-command-comparisons-01.py'):
    copy(BASE / 'artifacts' / filename, filename)
record = {'schemaVersion': 1, 'scope': 'Completed package production/validation and Native AOT build input identity only. No consumer execution or performance result inferred.',
          'candidateSource': PUBLIC, 'candidateTree': TREE, 'beforePackageSource': BEFORE,
          'candidateOrdinaryConsumersBuilt': 4, 'freshBeforeWorkloadConsumersBuilt': 2,
          'ffiOverlaysBuilt': 2, 'binaryRehashPerformedDuringAssembly': False,
          'consumerExecutionPerformedDuringAssembly': False, 'buildPerformedDuringAssembly': False,
          'largeArchivePerformedDuringAssembly': False, 'groups': groups, 'files': copied,
          'recoveryBoundary': 'Small original receipts and nuspec metadata retained here. Consumer source/generated files and binaries remain at the original bound paths; complete new consumer source archival is deferred during the isolated measurement window.'}
(OUT / 'index.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'providers': len(groups), 'candidateOrdinaryConsumersBuilt': 4,
                  'freshBeforeWorkloadConsumersBuilt': 2, 'ffiOverlaysBuilt': 2,
                  'smallFilesCopied': len(copied), 'inputCreditOnly': True}, indent=2))
