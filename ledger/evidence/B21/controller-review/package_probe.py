#!/usr/bin/env python3
"""B21 standalone NuGet/JIT/NativeAOT matrix over already built domain packages.

The producer feed is an input: this controller never builds Rust or reaccepts an
earlier component. Successful cells are immutable and resumable for the exact
same app, packages, controller and runner inputs.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import traceback
import xml.etree.ElementTree as ET
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSEMBLY = 'NativeWeave.Reference.TaskService'
PROJECT = 'Reference.TaskService.csproj'
PROVIDERS = ('sqlite', 'postgresql')
MODES = ('jit', 'aot')
PROTOCOLS = ('http1', 'http1-tls', 'http2-tls')
VARIANTS = ('baseline', 'edited')
NATIVE_NAMES = ('libnw_database_sqlite.so', 'libnw_database_postgresql.so',
                'libnativeweave_server.so')
DIRECT_PACKAGES = {'NativeWeave.Database.Sqlite', 'NativeWeave.Database.PostgreSql',
                   'NativeWeave.Server'}
COMMON = ['-m:1', '-nr:false', '-p:UseSharedCompilation=false']


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    """Each checkpoint replaces only its JSON index, never earlier run artifacts."""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    temporary.replace(path)


def inventory(directory):
    return {str(path.relative_to(directory)): sha(path)
            for path in sorted(directory.rglob('*')) if path.is_file()}


def verify_inventory(directory, expected):
    for relative, digest in expected.items():
        path = directory / relative
        if not path.is_file() or sha(path) != digest:
            raise RuntimeError('A retained artifact changed: ' + str(path))


def git_identity(directory):
    def read(*arguments):
        result = subprocess.run(['git', '-C', str(directory), *arguments],
            capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    return {'root': read('rev-parse', '--show-toplevel'),
            'commit': read('rev-parse', 'HEAD'),
            'scope_status': read('status', '--porcelain', '--', str(directory))}


def package_inputs(feed, version):
    result, native = {}, {}
    for path in sorted(feed.glob('*.nupkg')):
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith('.nuspec')]
            if len(names) != 1:
                raise ValueError('Expected exactly one nuspec in ' + path.name)
            spec = ET.fromstring(archive.read(names[0]))
            identity = spec.findtext('.//{*}metadata/{*}id')
            selected_version = spec.findtext('.//{*}metadata/{*}version')
            if not identity or not identity.startswith('NativeWeave.') or selected_version != version:
                continue
            if identity in result:
                raise ValueError('Duplicate exact package identity: ' + identity)
            repository = spec.find('.//{*}repository')
            result[identity] = {'filename': path.name, 'version': version,
                'sha256': sha(path), 'bytes': path.stat().st_size,
                'repository': dict(repository.attrib) if repository is not None else {}}
            for name in archive.namelist():
                basename = Path(name).name
                if basename in NATIVE_NAMES:
                    digest = hashlib.sha256(archive.read(name)).hexdigest()
                    if basename in native and native[basename] != digest:
                        raise ValueError('Conflicting native module bytes: ' + basename)
                    native[basename] = digest
    if not DIRECT_PACKAGES.issubset(result) or set(native) != set(NATIVE_NAMES):
        raise ValueError('The feed needs the exact Database.Sqlite/PostgreSql/Server package closure and three native modules.')
    return result, native


def source_inputs(source):
    paths = [path for path in sorted(source.rglob('*'))
        if path.is_file() and path.suffix in ('.cs', '.csproj', '.sql')
        and not {'bin', 'obj'}.intersection(path.relative_to(source).parts)]
    if not (source / PROJECT).is_file() or not paths:
        raise ValueError('Missing src/Reference.TaskService application source.')
    return {str(path.relative_to(source)): sha(path) for path in paths}


def required_rows():
    return [(variant, provider, mode, protocol)
        for variant in VARIANTS for provider in PROVIDERS for mode in MODES
        for protocol in (PROTOCOLS if variant == 'baseline' else ('http2-tls',))]


def row_key(row):
    return '-'.join(row)


class Probe:
    def __init__(self, args):
        self.args, self.output = args, args.output.resolve()
        source = args.source.resolve()
        self.source = source / 'src/Reference.TaskService' if (source / 'src/Reference.TaskService').is_dir() else source
        self.source_git = git_identity(self.source)
        self.runner = args.runner.resolve()
        runner_git = git_identity(self.runner.parent)
        for root in (self.source_git['root'], runner_git['root'], str(ROOT)):
            if root and self.output.is_relative_to(Path(root).resolve()):
                raise ValueError('--output must be outside the source worktrees; the consumer is independent.')
        if self.output.exists() and not args.resume:
            raise ValueError('Preserve this attempt; use a new output directory or --resume for unchanged inputs.')
        self.output.mkdir(parents=True, exist_ok=True)
        self.progress_path = self.output / 'progress.json'
        self.progress = json.loads(self.progress_path.read_text()) if self.progress_path.exists() else {
            'schema_version': 1, 'task': 'B21', 'platform': 'linux-x64',
            'required_rows': [row_key(row) for row in required_rows()],
            'builds': {}, 'rows': {}, 'failures': [], 'commands': [], 'attempts': []}
        self.attempt = len(self.progress['attempts']) + 1
        self.progress['attempts'].append({'number': self.attempt,
            'started_utc': datetime.now(timezone.utc).isoformat(), 'status': 'running',
            'selection': {'variants': args.variants, 'providers': args.providers,
                          'modes': args.modes, 'protocols': args.protocols,
                          'build_only': args.build_only}})
        self.logs = self.output / 'logs' / f'attempt-{self.attempt:03d}'
        self.logs.mkdir(parents=True, exist_ok=False)
        self.cache = self.output / 'consumer-cache'
        self.marker = self.output / 'unexpected-rust.txt'
        self.environment = os.environ.copy()
        # The cache is isolated; ordinary package imports remain the only build integration.
        self.environment['NUGET_PACKAGES'] = str(self.cache)
        self.environment['DOTNET_CLI_HOME'] = str(self.output / 'dotnet-home')
        self.environment['DOTNET_CLI_TELEMETRY_OPTOUT'] = '1'
        self.environment['DOTNET_SKIP_FIRST_TIME_EXPERIENCE'] = '1'
        self.environment['DOTNET_NOLOGO'] = '1'
        traps = self.output / 'rust-traps'
        traps.mkdir(exist_ok=True)
        for name in ('cargo', 'rustc', 'rustup'):
            path = traps / name
            path.write_text('#!/bin/sh\nprintf "%s\\n" ' + shlex.quote(name) + ' >> ' + shlex.quote(str(self.marker)) + '\nexit 197\n')
            path.chmod(0o755)
        inherited = [entry for entry in os.environ.get('PATH', '').split(os.pathsep)
            if entry and not any((Path(entry) / name).exists() for name in ('cargo', 'rustc', 'rustup'))]
        self.environment['PATH'] = str(traps) + os.pathsep + os.pathsep.join(inherited)
        self.packages, self.native = package_inputs(args.feed.resolve(), args.version)
        self.app_sources = source_inputs(self.source)
        self.runner_sources = {path.name: sha(path) for path in sorted(self.runner.parent.iterdir())
            if path.is_file() and path.name != 'package_probe.py'
            and (path.suffix == '.py' or path.name in ('golden-v1.json', 'requirements.txt'))}
        global_path = Path(self.source_git['root']) / 'global.json' if self.source_git['root'] else self.source / 'global.json'
        if not global_path.is_file():
            raise ValueError('The source needs its exact global.json SDK pin.')
        self.global_path = global_path
        self.inputs = {'application': self.app_sources, 'global_json': sha(global_path),
            'runner': self.runner_sources, 'package_probe': sha(__file__),
            'packages': self.packages, 'native_sha256': self.native, 'version': args.version}
        if 'inputs' in self.progress and self.progress['inputs'] != self.inputs:
            raise ValueError('Inputs differ from the retained attempt. Use a new output; successful earlier cells remain tied to their original bytes.')
        self.progress['inputs'] = self.inputs
        self.progress.setdefault('source_repository', self.source_git)
        self.progress.setdefault('runner_repository', runner_git)
        self.progress['attempts'][-1]['source_repository'] = self.source_git
        self.progress['attempts'][-1]['runner_repository'] = runner_git
        self.progress['environment'] = {'os': platform.platform(), 'machine': platform.machine(),
            'python': platform.python_version(), 'httpx': importlib.metadata.version('httpx'),
            'h2': importlib.metadata.version('h2'),
            'dotnet_processor_count': self.environment.get('DOTNET_PROCESSOR_COUNT'),
            'pristine_machine': False, 'isolated_nuget_cache': str(self.cache)}
        self.controller = self.output / 'controller'
        self.controller.mkdir(exist_ok=True)
        for name, digest in self.runner_sources.items():
            destination = self.controller / name
            if destination.exists() and sha(destination) != digest:
                raise RuntimeError('A frozen runner changed: ' + name)
            shutil.copy2(self.runner.parent / name, destination)
            if sha(destination) != digest:
                raise RuntimeError('Runner input changed during snapshot: ' + name)
        shutil.copy2(__file__, self.controller / 'package_probe.executed.py')
        self.feed = self.output / 'feed'
        self.feed.mkdir(exist_ok=True)
        for entry in self.packages.values():
            destination = self.feed / entry['filename']
            if destination.exists() and sha(destination) != entry['sha256']:
                raise RuntimeError('A frozen package changed: ' + destination.name)
            shutil.copy2(args.feed / entry['filename'], destination)
            if sha(destination) != entry['sha256']:
                raise RuntimeError('Package input changed during snapshot: ' + destination.name)
        self.checkpoint()

    def validate_retained(self):
        """A partial selection cannot accidentally endorse stale unselected results."""
        for variant in self.progress.get('consumer_sources', {}):
            self.consumer(variant)
        for record in self.progress['builds'].values():
            directory = self.output / record['artifact_directory']
            if inventory(directory) != record['artifacts_sha256']:
                raise RuntimeError('A retained build output changed: ' + str(directory))
            verify_inventory(self.output / record['metadata_directory'], record['metadata_sha256'])
            self.native_outputs(directory)
        for key, record in self.progress['rows'].items():
            if key not in self.progress['required_rows'] or record['build_key'] not in self.progress['builds']:
                raise RuntimeError('Invalid retained matrix binding: ' + key)
            verify_inventory(self.output, record['evidence_sha256'])
        self.no_rust()

    def checkpoint(self):
        self.progress['completed_rows'] = sorted(self.progress['rows'])
        self.progress['remaining_rows'] = sorted(set(self.progress['required_rows']) - set(self.progress['rows']))
        save(self.progress_path, self.progress)

    def command(self, label, argv, *, cwd=None, timeout=900, environment=None):
        ordinal = len(self.progress['commands']) + 1
        log = self.logs / f'{ordinal:03d}-{label}.log'
        command = list(map(str, argv))
        record = {'label': label, 'argv': command, 'cwd': str(cwd or self.output),
            'timeout_seconds': timeout, 'log': str(log.relative_to(self.output)), 'status': 'running'}
        self.progress['commands'].append(record)
        self.checkpoint()
        print(label, flush=True)
        with log.open('wb') as stream:
            process = subprocess.Popen(command, cwd=cwd or self.output,
                env=environment or self.environment, stdout=stream, stderr=subprocess.STDOUT,
                start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except BaseException:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                record.update(status='interrupted', exit_code=process.returncode, log_sha256=sha(log))
                self.checkpoint()
                raise
        record.update(status='passed' if code == 0 else 'failed', exit_code=code, log_sha256=sha(log))
        self.checkpoint()
        self.no_rust()
        if code:
            raise RuntimeError(label + ' failed; retained log: ' + str(log) + '\n' + log.read_text(errors='replace')[-5000:])
        return log.read_text(errors='replace')

    def no_rust(self):
        if self.marker.exists():
            raise AssertionError('A consumer attempted a Rust tool; the trap receipt is retained.')

    def consumer(self, variant):
        directory = self.output / 'consumers' / variant
        if directory.exists():
            expected = self.progress.get('consumer_sources', {}).get(variant)
            if not expected:
                raise RuntimeError('An incomplete consumer snapshot is retained; use a new output directory.')
            verify_inventory(directory, expected)
            expected_code = {name: digest for name, digest in expected.items()
                if Path(name).suffix in ('.cs', '.csproj', '.sql')}
            if source_inputs(directory) != expected_code:
                raise RuntimeError('Unrecorded executable source entered the copied consumer.')
            return directory
        directory.mkdir(parents=True)
        for relative, digest in self.app_sources.items():
            original = self.source / relative
            if sha(original) != digest:
                raise RuntimeError('Application source changed during snapshot: ' + relative)
            destination = directory / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, destination)
            if sha(destination) != digest:
                raise RuntimeError('Application input changed during snapshot: ' + relative)
        shutil.copy2(self.global_path, directory / 'global.json')
        if sha(directory / 'global.json') != self.inputs['global_json']:
            raise RuntimeError('The SDK pin changed during snapshot.')
        tree = ET.parse(directory / PROJECT)
        if any(node.tag in ('ProjectReference', 'Import') for node in tree.iter()):
            raise AssertionError('Standalone consumers cannot import a source project or repository build file.')
        references = list(tree.iter('PackageReference'))
        if {node.attrib.get('Include') for node in references} != DIRECT_PACKAGES:
            raise AssertionError('Unexpected reference application package surface.')
        for node in references:
            node.set('Version', '[' + self.args.version + ']')
        properties = tree.getroot().find('PropertyGroup')
        for key, value in {'TargetFramework': 'net11.0', 'LangVersion': '15.0',
            'Nullable': 'enable', 'ImplicitUsings': 'enable', 'TreatWarningsAsErrors': 'true',
            'RestorePackagesWithLockFile': 'true', 'NuGetAudit': 'true',
            'NuGetAuditMode': 'all', 'Deterministic': 'true', 'IsPackable': 'false'}.items():
            old = properties.find(key)
            (old if old is not None else ET.SubElement(properties, key)).text = value
        tree.write(directory / PROJECT, encoding='unicode')
        (directory / 'Directory.Build.props').write_text('<Project />\n')
        (directory / 'Directory.Build.targets').write_text('<Project />\n')
        configuration = ET.Element('configuration')
        sources = ET.SubElement(configuration, 'packageSources')
        ET.SubElement(sources, 'clear')
        ET.SubElement(sources, 'add', key='candidate', value=str(self.feed))
        ET.SubElement(sources, 'add', key='nuget.org', value='https://api.nuget.org/v3/index.json')
        mapping = ET.SubElement(configuration, 'packageSourceMapping')
        ET.SubElement(mapping, 'clear')
        ET.SubElement(ET.SubElement(mapping, 'packageSource', key='candidate'), 'package', pattern='NativeWeave.*')
        ET.SubElement(ET.SubElement(mapping, 'packageSource', key='nuget.org'), 'package', pattern='*')
        ET.ElementTree(configuration).write(directory / 'NuGet.Config')
        (directory / 'PackageRuntimeIdentity.cs').write_text('''using System.Runtime.CompilerServices;
namespace NativeWeave.Reference.TaskService;
internal static class PackageRuntimeIdentity
{
    [ModuleInitializer]
    internal static void Report() => Console.Error.WriteLine("B21_RUNTIME dynamic=" + RuntimeFeature.IsDynamicCodeSupported);
}
''')
        if variant == 'edited':
            self.edit_consumer(directory)
        self.progress.setdefault('consumer_sources', {})[variant] = inventory(directory)
        self.checkpoint()
        return directory

    @staticmethod
    def edit_consumer(directory):
        """Real ordinary application changes; the feed and all native bytes stay fixed."""
        replacements = {
            'Models.cs': [(r'(internal sealed record Item\([^;]+\));',
                r'\1 { internal string DisplayTitle => Title; }')],
            'Protocol.cs': [(r'(internal sealed record ItemView\([^;]+\));',
                r'\1 { public string ManagedEdition => "b21-edited"; }')],
            'DatabaseService.cs': [(r'new ItemView\(row\.ItemId,\s*row\.Title,',
                'new ItemView(row.ItemId, row.DisplayTitle,')],
            'Program.cs': [(r'(application\.MapGet\("/v1/items", async \(context, token\) =>\s*\{)',
                r'\1\n            context.Response.Headers.Set("X-NativeWeave-Managed-Edit", "b21-edited");')],
        }
        for filename, changes in replacements.items():
            path = directory / filename
            text = path.read_text()
            for pattern, replacement in changes:
                text, count = re.subn(pattern, replacement, text)
                if count != 1:
                    raise AssertionError('Ordinary-edit fixture needs one explicit application site: ' + filename)
            path.write_text(text)

    def native_outputs(self, directory):
        result = {}
        for name, expected in self.native.items():
            files = list(directory.rglob(name))
            if not files or any(sha(path) != expected for path in files):
                raise AssertionError('Consumer native bytes differ from the immutable package: ' + name)
            result[name] = {'sha256': expected, 'outputs': [str(path.relative_to(directory)) for path in files]}
        return result

    def build(self, variant, mode):
        key = variant + '-' + mode
        directory = self.consumer(variant)
        if key in self.progress['builds']:
            record = self.progress['builds'][key]
            destination = self.output / record['artifact_directory']
            verify_inventory(destination, record['artifacts_sha256'])
            if inventory(destination) != record['artifacts_sha256']:
                raise RuntimeError('Unrecorded files entered a retained build output.')
            verify_inventory(self.output / record['metadata_directory'], record['metadata_sha256'])
            self.native_outputs(destination)
            print('REUSE build ' + key, flush=True)
            return destination
        project = directory / PROJECT
        rid = ['-r', 'linux-x64', '-p:PublishAot=true'] if mode == 'aot' else []
        self.command(key + '-restore', ['dotnet', 'restore', project, '--configfile', directory / 'NuGet.Config',
            '--disable-parallel', *rid, *COMMON], cwd=directory)
        # Preserve the actual resolved graph before the next runtime restore replaces it.
        destination = self.output / 'artifacts' / key / f'attempt-{self.attempt:03d}'
        metadata = self.output / 'build-records' / key / f'attempt-{self.attempt:03d}'
        metadata.mkdir(parents=True, exist_ok=False)
        assets = directory / 'obj/project.assets.json'
        resolved = json.loads(assets.read_text())
        if any(library.get('type') == 'project' for library in resolved.get('libraries', {}).values()):
            raise AssertionError('A ProjectReference entered the independent NuGet consumer.')
        if any(Path(folder).resolve() != self.cache for folder in resolved.get('packageFolders', {})):
            raise AssertionError('The consumer used an unexpected global package folder.')
        nativeweave = {name for name in resolved.get('libraries', {}) if name.startswith('NativeWeave.')}
        expected = {identity + '/' + self.args.version for identity in self.packages}
        if not nativeweave.issubset(expected) or not {name + '/' + self.args.version for name in DIRECT_PACKAGES}.issubset(nativeweave):
            raise AssertionError('The resolved domain package versions differ from the fixed feed.')
        shutil.copy2(assets, metadata / 'project.assets.json')
        package_hashes = {}
        for identity, library in resolved.get('libraries', {}).items():
            if library.get('type') != 'package':
                continue
            archives = list((self.cache / library['path']).glob('*.nupkg'))
            if len(archives) != 1:
                raise AssertionError('Missing resolved package archive: ' + identity)
            digest = sha(archives[0])
            name = identity.rsplit('/', 1)[0]
            if name in self.packages and digest != self.packages[name]['sha256']:
                raise AssertionError('Resolved NativeWeave package bytes differ from the frozen feed.')
            package_hashes[identity] = {'sha256': digest, 'lock_sha512': library.get('sha512')}
        save(metadata / 'resolved-archive-hashes.json', package_hashes)
        for lock in directory.glob('packages*.lock.json'):
            shutil.copy2(lock, metadata / lock.name)
        operation = 'publish' if mode == 'aot' else 'build'
        self.command(key + '-' + operation, ['dotnet', operation, project, '-c', 'Release',
            '--no-restore', *rid, '-o', destination, *COMMON], cwd=directory, timeout=1800)
        executable = destination / (ASSEMBLY if mode == 'aot' else ASSEMBLY + '.dll')
        if not executable.is_file():
            raise AssertionError('The ordinary SDK build did not produce the expected application.')
        self.progress['builds'][key] = {'status': 'passed', 'mode': mode, 'variant': variant,
            'artifact_directory': str(destination.relative_to(self.output)),
            'metadata_directory': str(metadata.relative_to(self.output)),
            'executable': str(executable.relative_to(self.output)), 'executable_sha256': sha(executable),
            'artifacts_sha256': inventory(destination), 'metadata_sha256': inventory(metadata),
            'native': self.native_outputs(destination), 'resolved_nativeweave': sorted(nativeweave)}
        self.checkpoint()
        return destination

    def certificate(self):
        directory = self.output / 'tls'
        certificate, private_key = directory / 'localhost.pem', directory / 'localhost.private.pem'
        if 'tls_certificate' in self.progress:
            verify_inventory(directory, self.progress['tls_certificate']['files_sha256'])
            return certificate, private_key
        directory.mkdir(exist_ok=True)
        self.command('localhost-certificate', ['openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-sha256', '-nodes', '-days', '30', '-subj', '/CN=localhost',
            '-addext', 'subjectAltName=DNS:localhost,IP:127.0.0.1',
            '-addext', 'extendedKeyUsage=serverAuth', '-keyout', private_key, '-out', certificate])
        private_key.chmod(0o600)
        self.progress['tls_certificate'] = {'validation': 'Explicit private test CA; hostname/IP and ALPN validated by httpx',
            'files_sha256': inventory(directory), 'private_test_key_do_not_publish': str(private_key.relative_to(self.output))}
        self.checkpoint()
        return certificate, private_key

    @contextmanager
    def postgres(self):
        directory = self.output / 'postgres' / f'attempt-{self.attempt:03d}'
        directory.mkdir(parents=True, exist_ok=False)
        binary = self.args.postgres_bin.resolve()
        version = self.command('postgres-identity', [binary / 'postgres', '--version']).strip()
        if not version.endswith(' 18.0'):
            raise AssertionError('The accepted provider profile requires PostgreSQL 18.0.')
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        data = directory / 'data'
        self.command('postgres-init', [binary / 'initdb', '-D', data, '-U', 'nativeweave',
            '--auth=trust', '--no-locale', '--encoding=UTF8'])
        self.command('postgres-start', [binary / 'pg_ctl', '-D', data, '-l', directory / 'server.log',
            '-o', f"-h 127.0.0.1 -p {port} -k ''", '-w', 'start'])
        base = f'postgresql://nativeweave@127.0.0.1:{port}/postgres'
        self.progress.setdefault('postgres_runs', []).append({'attempt': self.attempt,
            'version': version, 'postgres_binary_sha256': sha(binary / 'postgres'),
            'psql_binary_sha256': sha(binary / 'psql'), 'loopback_port': port,
            'directory': str(directory.relative_to(self.output))})
        self.checkpoint()
        try:
            yield binary, base
        finally:
            self.command('postgres-stop', [binary / 'pg_ctl', '-D', data, '-m', 'fast', '-w', 'stop'])

    def edited_wire_probe(self, command, row_output, certificate, http2):
        config = json.loads((row_output / 'service/config.private.json').read_text())
        token = next(principal['token'] for principal in config['principals'] if principal['principal'] == 'alice')
        sys.path.insert(0, str(self.controller))
        try:
            spec = importlib.util.spec_from_file_location('b21_package_external_runner', self.controller / 'run.py')
            runner = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(runner)
        finally:
            sys.path.pop(0)
        original_environment = os.environ.copy()
        try:
            # The imported runner launches its service with its inherited environment.
            os.environ.clear()
            os.environ.update(self.environment)
            with runner.Service(command, config, row_output / 'edited-wire', http2=http2, certificate=certificate) as service:
                status, data, headers = service.request('GET', '/v1/items?limit=1', token=token)
                value = json.loads(data)
                if status != 200 or headers.get('x-nativeweave-managed-edit') != 'b21-edited':
                    raise AssertionError('The rebuilt ordinary C# handler edit was not observed over HTTP.')
                if not value['items'] or value['items'][0].get('managedEdition') != 'b21-edited':
                    raise AssertionError('The rebuilt Entity/DTO projection edit was not observed over HTTP.')
                return {'status': status, 'handler_header': headers['x-nativeweave-managed-edit'],
                    'dto_property': value['items'][0]['managedEdition'], 'protocols': sorted(service.protocols)}
        finally:
            os.environ.clear()
            os.environ.update(original_environment)

    def run_row(self, row, postgres=None):
        variant, provider, mode, protocol = row
        key = row_key(row)
        if key in self.progress['rows']:
            record = self.progress['rows'][key]
            verify_inventory(self.output, record['evidence_sha256'])
            print('REUSE row ' + key, flush=True)
            return
        artifact = self.build(variant, mode)
        command = [str(artifact / ASSEMBLY)] if mode == 'aot' else ['dotnet', str(artifact / (ASSEMBLY + '.dll'))]
        row_parent = self.output / 'rows' / key / f'attempt-{self.attempt:03d}'
        row_parent.mkdir(parents=True, exist_ok=False)
        row_output = row_parent / 'oracle'
        database = str(row_parent / 'application.sqlite')
        pg_options = []
        specialized = variant == 'baseline' and provider == 'postgresql' and protocol == 'http1'
        if provider == 'postgresql':
            binary, base = postgres
            # Every cell receives a new database in this invocation's isolated cluster.
            database_name = 'b21_' + key.replace('-', '_')
            self.command(key + '-database', [binary / 'psql', base, '-X', '-v', 'ON_ERROR_STOP=1',
                '-c', 'CREATE DATABASE ' + database_name])
            database = base.rsplit('/', 1)[0] + '/' + database_name
            pg_options = ['--psql', binary / 'psql'] + (['--postgres-oracles'] if specialized else [])
        tls_options, certificate = [], None
        if protocol != 'http1':
            certificate, private_key = self.certificate()
            tls_options = ['--tls-certificate', certificate, '--tls-private-key', private_key]
        self.command(key + '-oracle', [sys.executable, self.controller / 'run.py', '--provider', provider,
            '--database', database, '--output', row_output, *pg_options, *tls_options,
            *(['--http2'] if protocol == 'http2-tls' else []), '--', *command], timeout=1200)
        summary = json.loads((row_output / 'summary.json').read_text())
        cases = json.loads((row_output / 'cases.json').read_text())
        if not cases or len(cases) != summary.get('cases_passed') or not all(case.get('passed') is True for case in cases):
            raise AssertionError('The row summary does not match its actual passed case receipts.')
        if summary.get('provider') != provider or summary.get('tls') != (protocol != 'http1'):
            raise AssertionError('The executed row does not match the requested matrix cell.')
        if summary.get('http_protocol') != ('HTTP/2' if protocol == 'http2-tls' else 'HTTP/1.1'):
            raise AssertionError('HTTP protocol negotiation did not match the matrix cell.')
        if summary.get('postgres_fault_oracles') != specialized:
            raise AssertionError('The selected PostgreSQL correctness oracles did not execute.')
        marker = 'B21_RUNTIME dynamic=' + ('False' if mode == 'aot' else 'True')
        if marker not in (row_output / 'service/service.log').read_text():
            raise AssertionError('The runtime identity witness is absent from actual service execution.')
        edited = self.edited_wire_probe(command, row_output, certificate, protocol == 'http2-tls') if variant == 'edited' else None
        self.no_rust()
        self.native_outputs(artifact)
        # Private bearer/cursor/TLS material and mutable database storage are not exported as public evidence.
        evidence = {str(path.relative_to(self.output)): sha(path)
            for path in sorted(row_output.rglob('*')) if path.is_file()
            and path.suffix in ('.json', '.log') and '.private.' not in path.name
            and not {'blobs'}.intersection(path.relative_to(row_output).parts)}
        self.progress['rows'][key] = {'status': 'passed', 'variant': variant, 'provider': provider,
            'mode': mode, 'protocol': protocol, 'summary': summary, 'edited_wire': edited,
            'native_sha256': self.native, 'runtime_witness': marker,
            'source_sha256': self.progress['consumer_sources'][variant],
            'build_key': variant + '-' + mode, 'evidence_sha256': evidence}
        self.checkpoint()

    def finish(self, status):
        self.progress['attempts'][-1].update(status=status, ended_utc=datetime.now(timezone.utc).isoformat())
        self.progress['status'] = 'passed' if not self.progress['remaining_rows'] else 'partial'
        if status == 'failed':
            self.progress['status'] = 'failed_with_retained_progress'
        self.progress['no_consumer_rust_invocation'] = not self.marker.exists()
        self.progress['other_platforms'] = 'not_executed'
        self.progress['b22_soak_acceptance'] = False
        self.progress['b24_pristine_release_acceptance'] = False
        self.checkpoint()
        save(self.output / 'summary.json', {key: self.progress[key] for key in
            ('task', 'platform', 'status', 'completed_rows', 'remaining_rows',
             'no_consumer_rust_invocation', 'other_platforms', 'b22_soak_acceptance', 'b24_pristine_release_acceptance')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feed', type=Path, required=True)
    parser.add_argument('--postgres-bin', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=ROOT)
    parser.add_argument('--runner', type=Path, default=HERE / 'run.py')
    parser.add_argument('--version', default='0.1.0-preview.1')
    parser.add_argument('--modes', nargs='+', choices=MODES, default=list(MODES))
    parser.add_argument('--providers', nargs='+', choices=PROVIDERS, default=list(PROVIDERS))
    parser.add_argument('--protocols', nargs='+', choices=PROTOCOLS, default=list(PROTOCOLS))
    parser.add_argument('--variants', nargs='+', choices=VARIANTS, default=list(VARIANTS))
    parser.add_argument('--build-only', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if sys.platform != 'linux' or platform.machine().lower() != 'x86_64':
        parser.error('This evidence runner is scoped to Linux x64.')
    probe = None
    try:
        probe = Probe(args)
        probe.validate_retained()
        sdk = probe.command('sdk-identity', ['dotnet', '--version']).strip()
        expected_sdk = json.loads(probe.global_path.read_text())['sdk']['version']
        if sdk != expected_sdk:
            raise AssertionError('Use the pinned SDK ' + expected_sdk + ', observed ' + sdk)
        for variant in args.variants:
            for mode in args.modes:
                probe.build(variant, mode)
        selected = [row for row in required_rows()
            if row[0] in args.variants and row[1] in args.providers
            and row[2] in args.modes and row[3] in args.protocols]
        if not args.build_only:
            for row in selected:
                if row[1] == 'sqlite':
                    probe.run_row(row)
            postgres_rows = [row for row in selected if row[1] == 'postgresql'
                and row_key(row) not in probe.progress['rows']]
            # Reused PG rows need no database service, but their evidence is still verified.
            for row in selected:
                if row[1] == 'postgresql' and row_key(row) in probe.progress['rows']:
                    probe.run_row(row)
            if postgres_rows:
                with probe.postgres() as postgres:
                    for row in postgres_rows:
                        probe.run_row(row, postgres)
        probe.validate_retained()
        probe.finish('completed_selected_work')
        print(json.dumps(json.loads((probe.output / 'summary.json').read_text()), indent=2))
    except BaseException as error:
        if probe is not None:
            failure = probe.logs / 'failure.txt'
            failure.write_text(traceback.format_exc())
            probe.progress['failures'].append({'attempt': probe.attempt, 'type': type(error).__name__,
                'log': str(failure.relative_to(probe.output)), 'sha256': sha(failure)})
            probe.finish('failed')
        raise


if __name__ == '__main__':
    main()
