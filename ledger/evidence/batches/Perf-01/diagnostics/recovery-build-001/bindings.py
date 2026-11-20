"""Actual producer/consumer identities for recovery builds; no timing reader."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

from owner import sha

BEFORE = 'ea5fa528035d025bd7a28698ee7c71194432236c'
ON = '2e3995df8d86583ee9443348276ca8d918056bfc'
MANAGED = (
    'Interop.Abi', 'Core', 'Data', 'Database.Transactions', 'Data.Streaming',
    'Query.Binding', 'Query.Generator', 'Server.Generator', 'Database',
    'Database.Sqlite', 'Database.PostgreSql', 'Server', 'Server.Grpc', 'Server.Mcp')
IDS = {'NativeWeave.' + name for name in MANAGED} | {
    'NativeWeave.Database.Sqlite.Native', 'NativeWeave.Database.PostgreSql.Native', 'NativeWeave.Server.Native'}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def digest512(path):
    with Path(path).open('rb') as stream:
        return base64.b64encode(hashlib.file_digest(stream, 'sha512').digest()).decode()


def content_hash(value):
    need(isinstance(value, str), 'Missing NuGet content hash')
    value = value.removeprefix('sha512-')
    need(len(base64.b64decode(value, validate=True)) == 64, 'Malformed NuGet SHA-512 content hash')
    return value


class Binding:
    def __init__(self):
        self.files = {}

    def pin(self, path, expected=None):
        path = Path(path)
        need(path.is_absolute() and path.is_file() and str(path.resolve()) == str(path), 'Noncanonical/missing bound file: ' + str(path))
        actual = sha(path)
        need(expected is None or actual == expected, 'Actual file identity changed: ' + str(path))
        need(str(path) not in self.files or self.files[str(path)] == actual, 'Conflicting file identity')
        self.files[str(path)] = actual
        return actual

    def document(self, path):
        self.pin(path)
        return read(path)

    def mapping(self, rows, base=None):
        need(isinstance(rows, dict), 'Missing producer file map')
        for name, digest in rows.items():
            self.pin(Path(base) / name if base is not None else Path(name), digest)

    def nuget(self, assets_path, cache, selected, saved=None):
        """Bind actual ZIP bytes separately from NuGet's signed content hash.

        Successful original restore/publish is checked by the caller. We do not
        implement signature verification or treat metadata as a raw ZIP hash.
        Paired external identities must subsequently match byte-for-byte.
        """
        assets = self.document(assets_path)
        cache = Path(cache)
        need(str(cache.resolve()) == str(cache), 'Cache alias/symlink is not permitted')
        folders = list(assets['packageFolders'])
        need(len(folders) == 1 and folders[0] in (str(cache), str(cache) + '/'), 'Consumer used a different package folder')
        rows = {}
        for identity, library in assets['libraries'].items():
            need(library.get('type') == 'package', 'Independent consumer has a project/nonpackage reference: ' + identity)
            relative = PurePosixPath(library['path'])
            need(not relative.is_absolute() and '..' not in relative.parts and len(relative.parts) == 2, 'Invalid resolved package path')
            folder = cache / str(relative)
            need(str(folder.resolve()) == str(folder), 'Resolved package alias/symlink')
            archives = list(folder.glob('*.nupkg'))
            need(len(archives) == 1, 'Expected one actual resolved archive: ' + identity)
            archive = archives[0]
            raw256, raw512 = self.pin(archive), digest512(archive)
            sidecar = archive.with_name(archive.name + '.sha512')
            metadata_path = folder / '.nupkg.metadata'
            self.pin(sidecar)
            metadata = self.document(metadata_path)
            reported = content_hash(library['sha512'])
            need(content_hash(sidecar.read_text().strip()) == raw512, 'Raw archive SHA-512 differs from its restored sidecar: ' + identity)
            need(content_hash(metadata['contentHash']) == reported, 'NuGet assets and extraction contentHash differ: ' + identity)
            with zipfile.ZipFile(archive) as package:
                signed = '.signature.p7s' in package.namelist()
            name, version = identity.rsplit('/', 1)
            key = (name.lower(), version)
            own = name.startswith('NativeWeave.')
            if own:
                need(key in selected and selected[key] == raw256, 'Resolved NativeWeave archive differs from the actual selected feed: ' + identity)
                need(not signed and reported == raw512, 'Unexpected local NativeWeave signature/content identity: ' + identity)
            elif not signed:
                need(reported == raw512, 'Unsigned external content hash differs from archive bytes: ' + identity)
            if saved is not None:
                need(identity in saved and saved[identity]['sha256'] == raw256
                     and content_hash(saved[identity]['lock_sha512']) == reported,
                     'Resolved bytes differ from original successful builder snapshot: ' + identity)
            rows[identity] = dict(archive=str(archive), archive_sha256=raw256, archive_raw_sha512=raw512,
                nuget_content_hash_sha512=reported, signature_entry_present=signed,
                raw_equals_content=raw512 == reported, source=metadata.get('source'), nativeweave=own)
        need(saved is None or set(saved) == set(rows), 'Original resolved archive snapshot population changed')
        return rows


def role(root, product, expected_commit, version):
    root, product = Path(root), Path(product)
    b = Binding()
    native = b.document(root / 'native-stable/manifest.json')
    need(native['sourceCommit'] == expected_commit and native['sourceDirty'] is False, 'Native producer source mismatch')
    need({a['engineId'] for a in native['assets']} == {'database.sqlite', 'database.postgresql', 'server'}, 'Incomplete native set')
    for asset in native['assets']:
        b.pin(asset['path'], asset['sha256'])
    b.mapping(native['inputSha256'], product)
    for build in native['builds']:
        b.pin(build['buildMessagesPath'], build['buildMessagesSha256'])
        b.pin(build['metadataPath'], build['metadataSha256'])
    package_root = root / 'packages'
    packages = b.document(package_root / 'manifest.json')
    need(packages['sourceCommit'] == expected_commit and packages['nativeSourceCommit'] == expected_commit
         and packages['sourceDirty'] is False and packages['nativeInputManifestSha256'] == sha(root / 'native-stable/manifest.json'),
         'Managed/native B24 producer mismatch')
    selected = {}
    for which in ('previous', 'candidate'):
        closure = packages[which]
        need({p['id'] for p in closure['packages']} == IDS and len(closure['packages']) == 17, 'B24 is not a full seventeen-package closure')
        b.document(package_root / closure['buildClosure'])
        b.document(package_root / closure['releaseRecord'])
        for item in closure['packages']:
            need(item['sourceCommit'] == expected_commit, 'Mixed B24 source')
            b.pin(package_root / item['path'], item['sha256'])
            if which == 'previous':
                need(item['version'] == version, 'Selected B24 version mismatch')
                selected[(item['id'].lower(), item['version'])] = item['sha256']
    commands = b.document(package_root / 'commands.json')
    need(len(commands) == 44 and all(c['exitCode'] == 0 for c in commands), 'B24 producer did not complete all 44 commands')
    for c in commands:
        for suffix in ('stdout', 'stderr'):
            b.pin(package_root / 'logs' / (c['label'] + '.' + suffix), c[suffix + 'Sha256'])
    inventory = b.document(package_root / 'source-inventory.json')
    need(inventory['sourceCommit'] == expected_commit, 'B24 source inventory mismatch')
    b.mapping(inventory['files'], product)
    b.document(package_root / 'native-build-input.json')

    reference_root = root / 'reference'
    reference = b.document(reference_root / 'progress.json')
    need(reference['status'] == 'partial' and not reference['failures'] and not reference['rows']
         and reference['no_consumer_rust_invocation'] is True, 'Reference build-only state differs')
    need(reference['source_repository']['commit'] == ON and reference['runner_repository']['commit'] == ON,
         'Reference application/driver source changed')
    need(len(reference['commands']) == 5 and all(c['status'] == 'passed' and c['exit_code'] == 0 for c in reference['commands']),
         'Five reference producer commands must pass')
    need(set(reference['builds']) == {'baseline-jit', 'baseline-aot'}, 'Reference JIT/AOT pair missing')
    b.mapping(reference['consumer_sources']['baseline'], reference_root / 'consumers/baseline')
    resolutions = {}
    for key, build in reference['builds'].items():
        need(build['status'] == 'passed', 'Reference build failed')
        b.mapping(build['artifacts_sha256'], reference_root / build['artifact_directory'])
        metadata = reference_root / build['metadata_directory']
        b.mapping(build['metadata_sha256'], metadata)
        resolutions[key] = b.nuget(metadata / 'project.assets.json', reference_root / 'consumer-cache', selected,
                                  b.document(metadata / 'resolved-archive-hashes.json'))
    for row in reference['commands']:
        b.pin(reference_root / row['log'], row['log_sha256'])
    observer = b.document(root / 'db-observer/manifest.json')
    need(observer['state'] == 'built' and len(observer['commands']) == 2 and all(c['exit_code'] == 0 for c in observer['commands']),
         'Observer restore/publish incomplete')
    need(observer['native_sha256'] == reference['inputs']['native_sha256'], 'Observer native identity differs')
    b.mapping(observer['copied_source_sha256'], root / 'db-observer/consumer')
    b.mapping(observer['artifacts'])
    for c in observer['commands']:
        b.pin(root / 'db-observer' / c['log'], c['sha256'])
    resolutions['observer'] = b.nuget(root / 'db-observer/consumer/obj/project.assets.json', reference_root / 'consumer-cache', selected)
    need(resolutions['observer'] == resolutions['baseline-aot'], 'Observer resolved package graph/bytes differ from actual reference AOT')

    protocol = b.document(root / 'protocols/build.json')
    need(protocol['product_source_commit'] == expected_commit and protocol['product_source_dirty'] is False
         and protocol['driver_source_commit'] == ON and protocol['driver_dirty'] is False
         and protocol['eligible_for_measurement'] is True and protocol['toolchain']['aot'] is True,
         'Protocol producer identity/AOT mismatch')
    for key in ('artifacts_sha256', 'source_files_sha256', 'package_archives_sha256', 'resolved_package_archives_sha256',
                'producer_manifests_sha256', 'lock_hashes'):
        b.mapping(protocol[key])
    commands = b.document(root / 'protocols/commands.json')
    need(len(commands) == 6 and all(c['exit_code'] == 0 for c in commands), 'Protocol six-command producer incomplete')
    for c in commands:
        b.pin(root / 'protocols' / (c['label'] + '.log'), c['log_sha256'])
    for name in ('Server', 'Client'):
        resolutions['protocol-' + name.lower()] = b.nuget(root / 'protocols/source' / name / 'obj/project.assets.json',
                                                         root / 'protocols/packages', selected)

    codec = b.document(root / 'codec/manifest.json')
    need(codec['source_commit'] == expected_commit and codec['source_dirty'] is False and codec['driver_commit'] == ON
         and codec['executed_performance'] is False, 'Codec identity mismatch')
    b.mapping(codec['artifacts']); b.mapping(codec['consumer_inputs'])
    commands = b.document(root / 'codec/commands.json')
    for c in commands:
        need(c['exit'] == (1 if c['label'] in ('negative-null-limit', 'negative-span-escape') else 0), 'Codec actual command outcome changed')
        for suffix in ('stdout', 'stderr'):
            b.pin(root / 'codec/logs' / (c['label'] + '.' + suffix), c[suffix + '_sha256'])
    receipt = b.document(root / 'codec/package-consumption.json')
    need(receipt == codec['package_receipt'] and receipt['rust_trap_fired'] is False
         and receipt['native_unchanged_after_managed_change'] is True and receipt['packaging_source_stable'] is True,
         'Codec original package proof differs')
    b.pin(root / 'codec/package-aot/NativeWeave.Engines.SyncProof.Tests', receipt['executable_sha256'])
    jit = [c for c in commands if c['label'] == 'package-managed-change-jit']
    need(len(jit) == 1, 'Missing actual codec JIT proof')
    b.pin(jit[0]['argv'][1], receipt['jit_assembly_sha256'])
    b.mapping(receipt['source_snapshots'], root / 'codec/independent-consumer')
    codec_selected = {('nativeweave.core', '0.1.0-proof.1'): receipt['package_sha256']['NativeWeave.Core.0.1.0-proof.1.nupkg'],
                      ('nativeweave.engines.syncproof', '0.1.0-proof.1'): receipt['package_sha256']['NativeWeave.Engines.SyncProof.0.1.0-proof.1.nupkg']}
    resolutions['codec'] = b.nuget(root / 'codec/consumer/obj/project.assets.json', root / 'codec/consumer-cache', codec_selected)
    for kind, folder in (('retirement', 'shared-retirement'), ('page', 'shared-page')):
        shared = b.document(root / folder / 'manifest.json')
        need(shared['probe'] == kind and shared['version'] == version and shared['executed'] is False
             and len(shared['commands']) == 2 and all(c['exitCode'] == 0 for c in shared['commands']), 'Shared producer incomplete')
        b.mapping(shared['artifacts'], root / folder); b.mapping(shared['consumerInputs'], root / folder)
        for label, c in zip(('restore', 'publish'), shared['commands'], strict=True):
            b.pin(root / folder / (label + '.log'), c['logSha256'])
        resolutions['shared-' + kind] = b.nuget(root / folder / 'consumer/obj/project.assets.json', root / folder / 'packages', selected)
    return dict(schema_version=1, task='Perf-01', epoch='recovery-001', status='built-and-bound',
                product_commit=expected_commit, driver_commit=ON, selected_b24_version=version,
                files_sha256=b.files, resolved_packages=resolutions, native_assets=native['assets'],
                functional_acceptance=False, performance_credit_seconds=0,
                identity_note='New actual artifacts; no historical binary, noise or long-test identity is substituted.')


def common(root, before_root, before_binding):
    root, before_root = Path(root), Path(before_root)
    b = Binding()
    b.mapping(before_binding['files_sha256'])
    direct = b.document(root / 'protocols/build.json')
    need(direct['route'] == 'direct-rust' and direct['eligible_for_measurement'] is True
         and direct['client_build_sha256'] == sha(before_root / 'protocols/build.json'), 'Direct protocol/common client binding differs')
    for key in ('artifacts_sha256', 'source_files_sha256', 'lock_hashes'):
        b.mapping(direct[key])
    comparators = b.document(root / 'database/comparators.json')
    need(set(comparators['routes']) == {'direct-rust', 'managed-aot'}, 'Missing database comparators')
    for value in comparators['routes'].values():
        need(value['source_identity']['base_commit'] == ON and value['instrumented'] is False, 'Comparator source mismatch')
        b.mapping(value['artifacts']); b.mapping(value['lock_hashes']); b.mapping(value['source_identity']['files'])
        progress = b.document(value['build_receipts']['path'])
        need(progress['state'] == 'built' and progress['executed_performance'] is False
             and all(c['exit_code'] == 0 for c in progress['commands']), 'Comparator build/golden proof incomplete')
        need(sha(value['build_receipts']['path']) == value['build_receipts']['sha256'], 'Comparator receipt changed')
    resolved = b.nuget(root / 'database/source/src/Benchmarks.Domain/comparators/managed/obj/project.assets.json',
                       root / 'database/nuget-packages', {})
    corpus = b.document(root / 'codec-corpus/manifest.json')
    codec = b.document(before_root / 'codec/manifest.json')
    need(corpus['producer_sha256'] == sha(codec['direct_executable']) and len(corpus['cases']) == 8, 'Corpus/direct producer mismatch')
    for row in corpus['cases']:
        b.pin(root / 'codec-corpus' / (str(row['id']) + '.raw'), row['raw_sha256'])
        b.pin(root / 'codec-corpus' / (str(row['id']) + '.zlib'), row['encoded_sha256'])
    return dict(schema_version=1, task='Perf-01', epoch='recovery-001', status='built-and-bound', files_sha256=b.files,
                resolved_packages={'database-managed-comparator': resolved},
                performance_credit_seconds=0, scope='Fresh common client, direct/managed comparators and deterministic codec corpus')


def paired(before, after):
    need(before['product_commit'] == BEFORE and after['product_commit'] == ON, 'Paired actual source roles differ')
    need(set(before['resolved_packages']) == set(after['resolved_packages']), 'Consumer populations differ')
    count = 0
    for consumer, rows in before['resolved_packages'].items():
        old = {k: {n: v[n] for n in ('archive_sha256', 'archive_raw_sha512', 'nuget_content_hash_sha512', 'signature_entry_present', 'source')}
               for k, v in rows.items() if not v['nativeweave']}
        new = {k: {n: v[n] for n in ('archive_sha256', 'archive_raw_sha512', 'nuget_content_hash_sha512', 'signature_entry_present', 'source')}
               for k, v in after['resolved_packages'][consumer].items() if not v['nativeweave']}
        need(old == new, 'External restored archive/content population changed: ' + consumer)
        count += len(old)
    return dict(external_consumer_package_pairs=count, exact_external_archive_and_content_equality=True,
                historical_evidence_transferred=False, performance_credit_seconds=0)
