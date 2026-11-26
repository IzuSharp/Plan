#!/usr/bin/env python3
"""Run B04 actual product packages without Cargo, reusing the accepted A14 packer/task."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--sqlite', type=Path, required=True)
parser.add_argument('--postgresql', type=Path, required=True)
parser.add_argument('--postgres-bin', type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
logs = out / 'logs'; logs.mkdir()
env = os.environ.copy()
commands = []

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def run(label, command, cwd=ROOT, environment=None):
    result = subprocess.run(list(map(str, command)), cwd=cwd, env=environment or env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
    path = logs / (label + '.log'); path.write_bytes(result.stdout)
    commands.append({'label': label, 'argv': list(map(str, command)), 'exit_code': result.returncode, 'log_sha256': sha(path)})
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    print(label, result.returncode, flush=True)
    if result.returncode:
        raise RuntimeError(result.stdout.decode(errors='replace')[-6000:])
    return result.stdout.decode()

common = ['-p:UseSharedCompilation=false', '-nr:false', '-m:1']
assets = ['-p:KordaSqliteAssetPath=' + str(args.sqlite.resolve()), '-p:KordaPostgresAssetPath=' + str(args.postgresql.resolve())]
run('sdk', ['dotnet', '--version'])
source_commit = run('source-commit', ['git', 'rev-parse', 'HEAD']).strip()
run('sample-restore', ['dotnet', 'restore', ROOT / 'samples/api/data-nativehost/Korda.Data.NativeHost.Sample.csproj', '--ignore-failed-sources', *common])
run('sample-build', ['dotnet', 'build', ROOT / 'samples/api/data-nativehost/Korda.Data.NativeHost.Sample.csproj', '-c', 'Release', '--no-restore', *common, *assets])
run('di-restore', ['dotnet', 'restore', ROOT / 'src/Data.NativeHost/DependencyInjection/Korda.Database.DependencyInjection.csproj', '--ignore-failed-sources', *common])
run('di-build', ['dotnet', 'build', ROOT / 'src/Data.NativeHost/DependencyInjection/Korda.Database.DependencyInjection.csproj', '-c', 'Release', '--no-restore', *common])
task_project = ROOT / 'src/Packaging.Release/BuildTasks/Korda.Packaging.Tasks.csproj'
run('closure-task-restore', ['dotnet', 'restore', task_project, '--locked-mode', '--ignore-failed-sources', *common])
run('closure-task-build', ['dotnet', 'build', task_project, '-c', 'Release', '--no-restore', *common])
spec = importlib.util.spec_from_file_location('b04_existing_pack', ROOT / 'src/Packaging.Linux/packages.py')
packing = importlib.util.module_from_spec(spec); spec.loader.exec_module(packing)
version = '0.1.0-preview.1'
registry = {
    'Korda.Interop.Abi': ('src/Interop.Abi', []),
    'Korda.Core': ('src/Korda.Core', ['Korda.Interop.Abi']),
    'Korda.Data': ('src/Data.Abstractions', []),
    'Korda.Database.Transactions': ('src/Data.Transactions', ['Korda.Data']),
    'Korda.Data.Streaming': ('src/Data.Streaming', ['Korda.Data']),
    'Korda.Query.Binding': ('src/Query.Binding', ['Korda.Data', 'Korda.Interop.Abi']),
    'Korda.Query.Generator': ('src/Query.Generator', []),
    'Korda.Database': ('src/Data.NativeHost', ['Korda.Core', 'Korda.Data', 'Korda.Database.Transactions', 'Korda.Data.Streaming', 'Korda.Query.Binding']),
    'Korda.Database.Sqlite': ('src/Data.Sqlite', ['Korda.Core', 'Korda.Data', 'Korda.Database', 'Korda.Query.Generator']),
    'Korda.Database.PostgreSql': ('src/Data.Postgres', ['Korda.Core', 'Korda.Data', 'Korda.Database', 'Korda.Query.Generator']),
    'Korda.Database.DependencyInjection': ('src/Data.NativeHost/DependencyInjection', ['Korda.Database']),
}
capabilities = ['db.metadata.v1','db.query.v1','db.transactions.v1','db.savepoints.v1','db.streaming.v1','db.migrations.v1','db.schema.read.v1','db.returning.v1','db.upsert.v1','db.cte.v1','db.window.v1','db.row-lock.v1','db.null-safe-equality.v1','db.json.v1','db.decimal.numeric.v1','db.decimal.text.v1','db.fixed-money.v1','db.relationships.explicit.v1','db.prepared-shape.v1','db.bulk-batches.v1','db.dynamic-fields.v1','db.recursive-cte.v1','db.set-operations.v1','db.scalar-codecs.v1','db.sql.expert.v1','db.schema.draft.v1','db.query.command.v1', 'db.cursor.pull.v1']
provider = {
    'Korda.Database.Sqlite': ('database.sqlite', args.sqlite.resolve(), 'libnw_database_sqlite.so'),
    'Korda.Database.PostgreSql': ('database.postgresql', args.postgresql.resolve(), 'libnw_database_postgresql.so'),
}

def record(identity):
    item = {'id': identity, 'version': version, 'dependencies': {name: version for name in registry[identity][1]}}
    if identity in provider:
        engine, native, basename = provider[identity]
        item['nativeAssets'] = [{'engineId': engine, 'facadePackageId': identity, 'facadePackageVersion': version,
            'rid': 'linux-x64', 'sourcePath': 'runtimes/linux-x64/native/' + basename, 'sha256': sha(native),
            'abiMajor': 1, 'abiMinor': 0, 'capabilities': {name: bit for bit, name in enumerate(capabilities)}, 'cpuBaseline': 'x86-64'}]
    return item

def closure(identity):
    selected = set()
    def visit(name):
        if name in selected: return
        selected.add(name)
        for dependency in registry[name][1]: visit(dependency)
    visit(identity)
    return {'schemaVersion': 1, 'packages': [record(name) for name in sorted(selected)]}

feed = out / 'feed'; feed.mkdir()
packages = {}
for identity, (folder, dependencies) in registry.items():
    entries = {'LICENSE': ROOT / 'LICENSE'}
    directory = ROOT / folder
    if identity == 'Korda.Query.Generator':
        entries['tools/roslyn/' + identity + '.dll'] = directory / 'bin/Release/netstandard2.0' / (identity + '.dll')
        entries['buildTransitive/' + identity + '.targets'] = directory / 'buildTransitive' / (identity + '.targets')
    else:
        for suffix in ['.dll', '.xml']:
            entries['lib/net11.0/' + identity + suffix] = directory / 'bin/Release/net11.0' / (identity + suffix)
    if identity in provider or identity == 'Korda.Database':
        entries['buildTransitive/' + identity + '.targets'] = ROOT / 'src/Packaging.Release/buildTransitive/Korda.Packaging.targets'
        entries['korda/closure.json'] = json.dumps(closure(identity), sort_keys=True).encode()
        for suffix in ['.dll', '.xml']:
            entries['tools/net11.0/Korda.Packaging.Tasks' + suffix] = task_project.parent / 'bin/Release/net11.0' / ('Korda.Packaging.Tasks' + suffix)
    if identity in provider:
        _, native, basename = provider[identity]
        entries['runtimes/linux-x64/native/' + basename] = native
    artifact = packing.pack(feed, identity, version, entries, {name: version for name in dependencies}, ('https://github.com/IzuSharp/Korda', source_commit))
    packages[identity] = {'path': str(artifact), 'sha256': sha(artifact)}
(out / 'packages.json').write_text(json.dumps(packages, indent=2) + '\n')
# Each provider's closure has exactly one native module and no other provider edge.
for identity in provider:
    assert sum(len(item.get('nativeAssets', [])) for item in closure(identity)['packages']) == 1

consumer = out / 'consumer'; consumer.mkdir()
shutil.copy2(ROOT / 'global.json', consumer)
shutil.copy2(ROOT / 'samples/api/data-nativehost/Program.cs', consumer / 'Program.cs')
(consumer / 'Generated.cs').write_text('''using Korda.Data;
[DbTable("generated_host")]
public sealed class GeneratedHostRow { [DbKey] public long Id { get; set; } public string Name { get; set; } = ""; }
internal static class GeneratedProbe { internal static void Assert() { if (GeneratedHostRowMapping.Table.MetadataHash.Length != 64 || GeneratedHostRowMapping.Row is null) throw new System.InvalidOperationException("Transitive generator mapping failed."); } }
''')
program = (consumer / 'Program.cs').read_text().replace('var builder =', 'GeneratedProbe.Assert();\nvar builder =')
(consumer / 'Program.cs').write_text(program)
(consumer / 'Consumer.csproj').write_text('''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>
<OutputType>Exe</OutputType><TargetFramework>net11.0</TargetFramework><LangVersion>15.0</LangVersion><Nullable>enable</Nullable><ImplicitUsings>enable</ImplicitUsings>
<AssemblyName>HostConsumer</AssemblyName><IsAotCompatible>true</IsAotCompatible><TreatWarningsAsErrors>true</TreatWarningsAsErrors><RestorePackagesWithLockFile>true</RestorePackagesWithLockFile><NuGetAudit>true</NuGetAudit>
<NuGetLockFilePath Condition="'$(PublishAot)' == 'true'">$(MSBuildProjectDirectory)/packages.aot.lock.json</NuGetLockFilePath>
</PropertyGroup><ItemGroup>
<PackageReference Include="Korda.Database.Sqlite" Version="[0.1.0-preview.1]" />
<PackageReference Include="Korda.Database.PostgreSql" Version="[0.1.0-preview.1]" />
</ItemGroup></Project>''')
configuration = ET.Element('configuration'); sources = ET.SubElement(configuration, 'packageSources'); ET.SubElement(sources, 'clear')
ET.SubElement(sources, 'add', key='candidate', value=str(feed)); ET.SubElement(sources, 'add', key='nuget.org', value='https://api.nuget.org/v3/index.json')
mapping = ET.SubElement(configuration, 'packageSourceMapping'); ET.SubElement(mapping, 'clear')
ET.SubElement(ET.SubElement(mapping, 'packageSource', key='candidate'), 'package', pattern='Korda.*')
ET.SubElement(ET.SubElement(mapping, 'packageSource', key='nuget.org'), 'package', pattern='*')
ET.ElementTree(configuration).write(consumer / 'NuGet.Config')
consumer_env = env.copy(); consumer_env['NUGET_PACKAGES'] = str(consumer / 'packages')
traps = consumer / 'rust-traps'; traps.mkdir(); marker = consumer / 'unexpected-rust.txt'
for name in ['cargo', 'rustc', 'rustup']:
    executable = traps / name; executable.write_text("#!/bin/sh\nprintf 'unexpected Rust invocation\\n' >> " + shlex.quote(str(marker)) + '\nexit 197\n'); executable.chmod(0o755)
consumer_env['PATH'] = str(traps) + os.pathsep + consumer_env['PATH']
project = consumer / 'Consumer.csproj'
run('consumer-restore', ['dotnet', 'restore', project, '--ignore-failed-sources', *common], consumer, consumer_env)
run('consumer-build', ['dotnet', 'build', project, '-c', 'Release', '--no-restore', *common], consumer, consumer_env)
consumer_dll = consumer / 'bin/Release/net11.0/HostConsumer.dll'
runner = ROOT / 'tests/Data.NativeHost/run.py'
run('consumer-aot-publish', ['dotnet', 'publish', project, '-c', 'Release', '-r', 'linux-x64', '-p:PublishAot=true', '--ignore-failed-sources', *common, '-o', consumer / 'publish'], consumer, consumer_env)
for selected in ['sqlite', 'postgresql']:
    run('consumer-aot-' + selected, ['python3', runner, '--postgres-bin', args.postgres_bin, '--output', out / ('aot-' + selected), '--', consumer / 'publish/HostConsumer', selected], consumer, consumer_env)
# An ordinary DTO edit recompiles only managed code against identical packaged assets.
(consumer / 'Program.cs').write_text(program.replace('internal sealed record Person(long Id, string Name);', 'internal sealed record Person(long Id, string Name) { public string Label => Name; }'))
run('consumer-dto-edit', ['dotnet', 'build', project, '-c', 'Release', '--no-restore', *common], consumer, consumer_env)
assert not marker.exists(), 'A normal consumer invoked Rust'
records = {}
for mode, path in [('aot', consumer / 'publish')]:
    for identity, (engine, native, basename) in provider.items():
        value = json.loads((path / ('Korda.' + engine + '.assets.json')).read_text())
        assert value['sha256'] == sha(native) == sha(path / value['outputPath'])
        records[mode + '-' + engine] = value
(out / 'summary.json').write_text(json.dumps({'source_commit': source_commit, 'native_dependency_lock_sha256': sha(ROOT / 'native/dependencies.lock.json'), 'packages': packages,
    'independent_provider_closures': True, 'transitive_generator_compiled_and_executed': True, 'no_consumer_rust': True,
    'aot_actual_providers': ['SQLite', 'PostgreSQL18'], 'dto_edit_native_hashes_unchanged': True,
    'sdk_output_records': records, 'aot_executable_sha256': sha(consumer / 'publish/HostConsumer')}, indent=2) + '\n')
print('B04 exact-package Linux Native AOT consumer passed; no Cargo/rustc/rustup invocation', flush=True)
