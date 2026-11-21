#!/usr/bin/env python3
"""Diagnostic-only common application producer for explicit managed/native sources.

Derived from the reviewed a5748 adapter f8a81d5a5354b2d67673e0a2ec09c2cde758c67b34bb570a482266ddf2af6862
from the unmodified common2e protocol producer, SHA256
068e0f356ee8af3b18df3b5b480b5c3b94b3e296540727c95687ab21852682d3.
Only input provenance and experiment metadata differ; application, package
resolution, build flags and native-loaded checks remain with existing tools.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

DRIVER_COMMIT = '2e3995df8d86583ee9443348276ca8d918056bfc'
MANAGED_COMMIT = '092e5e2c74d7419772f2455a2922ae4238f389de'
BASE_COMMIT = 'a5748ad4e03825e3da7706d074887952da6c2d43'
NATIVE_COMMIT = '2f40348c3db80a4fbee7a99e721b374a597b16df'
BUILDER_SHA256 = '068e0f356ee8af3b18df3b5b480b5c3b94b3e296540727c95687ab21852682d3'
CANDIDATE_INDEX_SHA256 = 'b276f92c52a7edc9c467bf7cd3a2f8bfb1422256d40a6b1e2ef28a7ef106ed4f'
SERVER_SHA256 = '8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0'
LEAVES = {'NativeWeave.Database.PostgreSql.Native': 'database.postgresql',
          'NativeWeave.Database.Sqlite.Native': 'database.sqlite', 'NativeWeave.Server.Native': 'server'}
HERE = ROOT = None


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def require(value, message):
    if not value:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True, timeout=30).strip()


def relative(base, value):
    name = Path(value)
    require(not name.is_absolute() and '..' not in name.parts, 'Expected repository-relative source path')
    path = (base / name).resolve(strict=True)
    require(path.is_relative_to(base), 'Source path escaped its declared root')
    return path


def validate_sources(product, producer, native_producer, package_manifest, native_manifest):
    require(git(ROOT, 'rev-parse', 'HEAD') == DRIVER_COMMIT and not git(ROOT, 'status', '--porcelain'),
            'Use the unchanged clean common2e driver')
    require(sha(HERE / 'build.py') == BUILDER_SHA256, 'Original common producer changed')
    require(git(product, 'rev-parse', 'HEAD') == MANAGED_COMMIT and not git(product, 'status', '--porcelain'),
            'Use the clean committed 092e5e2 prefix experiment product')
    candidate_index = Path(__file__).resolve().with_name('candidate-sources.json')
    require(sha(candidate_index) == CANDIDATE_INDEX_SHA256, 'Reviewed Plan candidate index changed')
    candidate = json.loads(candidate_index.read_text())
    require(candidate['product_commit'] == MANAGED_COMMIT
            and candidate['comparison_base_commit'] == BASE_COMMIT
            and candidate['native_commit'] == NATIVE_COMMIT
            and candidate['product_tree'] == git(product, 'rev-parse', MANAGED_COMMIT + '^{tree}'),
            'Candidate source identity differs')
    changed = ['src/Interop.Callbacks/CallbackCoordinator.cs', 'tests/Interop.Callbacks/Program.cs']
    require(candidate['changed_files'] == changed
            and git(product, 'diff', '--name-only', BASE_COMMIT, MANAGED_COMMIT).splitlines() == changed,
            'Only the declared coordinator-prefix and callback regression files may differ from a5748')
    for name, digest in candidate['files_sha256'].items():
        require(sha(relative(product, name)) == digest, 'Plan candidate source changed: ' + name)
    require(producer['sourceCommit'] == MANAGED_COMMIT and producer['sourceDirty'] is False
            and producer['nativeSourceCommit'] == NATIVE_COMMIT
            and producer['nativeInputManifestSha256'] == sha(native_manifest)
            and native_producer['sourceCommit'] == NATIVE_COMMIT and native_producer['sourceDirty'] is False,
            'Managed/native provenance must be explicit 092e5e2/2f with the actual native manifest')
    native_paths = ('native', '.cargo', 'Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml')
    require(not git(product, 'diff', '--name-only', NATIVE_COMMIT, MANAGED_COMMIT, '--', *native_paths),
            'This experiment permits no changed native input')
    native_names = set(git(product, 'ls-tree', '-r', '--name-only', NATIVE_COMMIT, '--', *native_paths).splitlines())
    require(native_names == set(native_producer['inputSha256']), 'Native producer input inventory differs')
    for name, digest in native_producer['inputSha256'].items():
        require(sha(relative(product, name)) == digest, 'Current native source differs: ' + name)
    source_path = relative(package_manifest.parent, producer['sourceInventory'])
    inventory = json.loads(source_path.read_text())
    require(inventory['sourceCommit'] == MANAGED_COMMIT, 'Managed source inventory identifies another product')
    for name, digest in inventory['files'].items():
        require(sha(relative(product, name)) == digest, 'B24 managed producer source changed: ' + name)
    assets = {row['engineId']: row for row in native_producer['assets']}
    require(set(assets) == set(LEAVES.values()) and len(native_producer['assets']) == 3,
            'Expected the three unchanged actual native assets')
    for row in assets.values():
        require(sha(row['path']) == row['sha256'], 'Original supplied native asset changed')
    require(assets['server']['sha256'] == SERVER_SHA256, 'Experiment must reuse selected 8b726 Server bytes')
    return assets


def main():
    global HERE, ROOT
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--driver', type=Path, required=True, help='Unchanged common2e checkout')
    p.add_argument('--product', type=Path, required=True, help='Clean reviewed 092e5e2 checkout')
    p.add_argument('--feed', type=Path, required=True)
    p.add_argument('--version', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--sdk', type=Path, required=True, help='Exact dotnet executable, SDK 11.0.100')
    p.add_argument('--packages', type=Path, help='Optional shared package download cache')
    p.add_argument('--package-manifest', type=Path, help='B24 manifest; defaults to FEED/../../manifest.json')
    p.add_argument('--native-manifest', type=Path, help='Native producer manifest; defaults to B24 parent/native-stable/manifest.json')
    p.add_argument('--compile-only', action='store_true', help='Compile diagnostics only; output is not eligible for measurement')
    args = p.parse_args()
    ROOT = args.driver.resolve(strict=True); HERE = ROOT / 'tests/Perf01.Protocols'
    product = args.product.resolve(strict=True)
    package_manifest = (args.package_manifest or args.feed.resolve().parent.parent / 'manifest.json').resolve()
    native_manifest = (args.native_manifest or package_manifest.parent.parent / 'native-stable/manifest.json').resolve()
    producer = json.loads(package_manifest.read_text()); native_producer = json.loads(native_manifest.read_text())
    native_assets = validate_sources(product, producer, native_producer, package_manifest, native_manifest)
    closures = [value for value in producer.values() if isinstance(value, dict) and 'feed' in value and (package_manifest.parent / value['feed']).resolve() == args.feed.resolve()]
    if len(closures) != 1: raise ValueError('Supplied feed is not exactly one declared B24 closure')
    closure = closures[0]
    expected_packages = {(row['id'].lower(), row['version']): row for row in closure['packages']}
    require(len(expected_packages) == len(closure['packages']), 'Duplicate package identity')
    require({row['id'] for row in closure['packages'] if 'native' in row} == set(LEAVES),
            'Expected exactly the B24 native runtime leaves')
    for row in closure['packages']:
        archive = relative(package_manifest.parent, row['path'])
        expected_source = NATIVE_COMMIT if row['id'] in LEAVES else MANAGED_COMMIT
        require(row['sourceCommit'] == expected_source and sha(archive) == row['sha256'],
                'Producer package provenance mismatch: ' + row['id'])
        if row['id'] in LEAVES:
            engine = LEAVES[row['id']]; native = row['native']; asset = native_assets[engine]
            require(native['engineId'] == engine and native['sha256'] == asset['sha256']
                    and native['rid'] == 'linux-x64', 'Runtime package descriptor differs')
            with zipfile.ZipFile(archive) as package:
                record = json.loads(package.read('nativeweave/manifest.json'))
                require(record['sourceCommit'] == NATIVE_COMMIT and record['sourceDirty'] is False
                        and record['packagingProducerCommit'] == MANAGED_COMMIT
                        and record['nativePath'] == native['path'] and record['nativeSha256'] == asset['sha256'],
                        'Embedded runtime package provenance differs')
                require(hashlib.sha256(package.read(native['path'])).hexdigest() == asset['sha256'],
                        'Runtime package contains different native bytes')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    source = out / 'source'; source.mkdir()
    copied = []
    for name in ['Server', 'Client']:
        shutil.copytree(HERE / name, source / name, ignore=shutil.ignore_patterns('bin', 'obj', 'packages*.json'))
        copied += [path for path in (source / name).rglob('*') if path.is_file()]
    for name in ['Shared.cs', 'perf01.proto']:
        shutil.copy2(HERE / name, source / name); copied.append(source / name)
    shutil.copy2(ROOT / 'global.json', source / 'global.json')
    (source / 'Directory.Build.props').write_text('<Project><PropertyGroup><RestorePackagesWithLockFile>true</RestorePackagesWithLockFile><Deterministic>true</Deterministic><ContinuousIntegrationBuild>true</ContinuousIntegrationBuild></PropertyGroup></Project>\n')
    configuration = ET.Element('configuration')
    sources = ET.SubElement(configuration, 'packageSources'); ET.SubElement(sources, 'clear')
    ET.SubElement(sources, 'add', key='candidate', value=str(args.feed.resolve()))
    ET.SubElement(sources, 'add', key='nuget.org', value='https://api.nuget.org/v3/index.json')
    mapping = ET.SubElement(configuration, 'packageSourceMapping')
    candidate = ET.SubElement(mapping, 'packageSource', key='candidate'); ET.SubElement(candidate, 'package', pattern='NativeWeave.*')
    external = ET.SubElement(mapping, 'packageSource', key='nuget.org'); ET.SubElement(external, 'package', pattern='*')
    ET.ElementTree(configuration).write(source / 'NuGet.Config', encoding='unicode', xml_declaration=False)
    environment = dict(os.environ, DOTNET_ROOT=str(args.sdk.resolve().parent), DOTNET_CLI_TELEMETRY_OPTOUT='1',
                       DOTNET_CLI_USE_MSBUILD_SERVER='0', MSBUILDDISABLENODEREUSE='1')
    commands = []
    def command(label, argv):
        with (out / (label + '.log')).open('w') as log:
            process = subprocess.run([str(x) for x in argv], cwd=source, env=environment, stdout=log, stderr=subprocess.STDOUT)
        commands.append({'label': label, 'argv': [str(x) for x in argv], 'exit_code': process.returncode, 'log_sha256': sha(out / (label + '.log'))})
        save(out / 'commands.json', commands)
        if process.returncode: raise RuntimeError('Build failed: ' + label)
    sdk_version = subprocess.check_output([str(args.sdk), '--version'], cwd=source, env=environment, text=True).strip()
    if sdk_version != '11.0.100': raise ValueError('Pinned SDK 11.0.100 is required, observed ' + sdk_version)
    cache = (args.packages or out / 'packages').resolve()
    for name in ['Server', 'Client']:
        project = source / name / (name + '.csproj')
        properties = ['-p:NativeWeavePackageVersion=' + args.version, '-p:UseSharedCompilation=false', '-p:RestorePackagesPath=' + str(cache)]
        target = [] if args.compile_only else ['-r', 'linux-x64', '-p:PublishAot=true', '-p:IlcInstructionSet=x86-64-v2']
        command(name.lower() + '-restore', [args.sdk, 'restore', project, '--configfile', source / 'NuGet.Config', *target, *properties])
        command(name.lower() + '-locked-restore', [args.sdk, 'restore', project, '--locked-mode', '--configfile', source / 'NuGet.Config', *target, *properties])
        command(name.lower() + '-publish', [args.sdk, 'publish', project, '-c', 'Release', '--no-restore', '-o', out / name.lower(), *target, *properties])
    files = {str(path): sha(path) for name in ['server', 'client'] for path in sorted((out / name).rglob('*')) if path.is_file()}
    locks = {str(path): sha(path) for path in source.rglob('packages.lock.json')}
    package_files = {}
    for path in args.feed.resolve().glob('*.nupkg'):
        package_files[str(path)] = sha(path)
    resolved_packages = {}
    for path in source.rglob('project.assets.json'):
        for identity in json.loads(path.read_text())['libraries']:
            name, version = identity.rsplit('/', 1)
            if not name.startswith('NativeWeave.'): continue
            row = expected_packages.get((name.lower(), version))
            if row is None: raise ValueError('Consumer resolved a package outside the selected closure: ' + identity)
            archive = cache / name.lower() / version / (name.lower() + '.' + version + '.nupkg')
            if sha(archive) != row['sha256']: raise ValueError('NuGet cache bytes differ from producing closure: ' + identity)
            resolved_packages[str(archive)] = row['sha256']
    validate_sources(product, producer, native_producer, package_manifest, native_manifest)
    server_native = {str(path): sha(path) for path in (out / 'server').rglob('*nativeweave*.so')}
    require(args.compile_only or len(server_native) == 1 and set(server_native.values()) == {SERVER_SHA256},
            'Published AOT server must carry the same selected 8b726 native library')
    provenance = {str(package_manifest): sha(package_manifest), str(native_manifest): sha(native_manifest),
                  str(Path(__file__).resolve()): sha(__file__), str(HERE / 'build.py'): BUILDER_SHA256,
                  str(Path(__file__).resolve().with_name('candidate-sources.json')): CANDIDATE_INDEX_SHA256}
    for key in ['sourceInventory']:
        if producer.get(key): provenance[str(package_manifest.parent / producer[key])] = sha(package_manifest.parent / producer[key])
    if closure.get('buildClosure'): provenance[str(package_manifest.parent / closure['buildClosure'])] = sha(package_manifest.parent / closure['buildClosure'])
    manifest = {'schema_version': 1, 'task': 'Perf-01', 'platform': 'linux-x64', 'nativeweave_package_version': args.version,
                'product_source_commit': producer['sourceCommit'], 'product_source_dirty': False,
                'native_source_commit': NATIVE_COMMIT, 'formal_timing_eligible': False,
                'experiment_only': True, 'performance_credit_seconds': 0,
                'experiment_provenance': {'managed_commit': MANAGED_COMMIT, 'native_commit': NATIVE_COMMIT,
                    'native_recompiled': False, 'server_native_sha256': SERVER_SHA256,
                    'builder_source_sha256': sha(__file__), 'original_builder_sha256': BUILDER_SHA256,
                    'scope': 'Diagnostic ablation only; this does not satisfy any formal final-role admission'},
                'driver_source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'driver_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
                'driver_source_sha256': {str(path.relative_to(source)): sha(path) for path in copied},
                'source_files_sha256': {str(path): sha(path) for path in copied + [source / 'global.json', source / 'Directory.Build.props', source / 'NuGet.Config']},
                'package_archives_sha256': package_files, 'resolved_package_archives_sha256': resolved_packages,
                'producer_manifests_sha256': provenance, 'artifacts_sha256': files, 'lock_hashes': locks,
                'toolchain': {'sdk': sdk_version, 'dotnet_sha256': sha(args.sdk), 'configuration': 'Release', 'aot': not args.compile_only, 'isa': 'x86-64-v2'},
                'eligible_for_measurement': not args.compile_only,
                'server': str(out / 'server/Perf01.ProtocolServer'), 'client': str(out / 'client/Perf01.ProtocolClient'),
                'server_native_sha256': server_native,
                'commands_sha256': sha(out / 'commands.json')}
    save(out / 'build.json', manifest)
    print(out / 'build.json')


if __name__ == '__main__':
    main()
