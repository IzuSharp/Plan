#!/usr/bin/env python3
"""Source-bound verification for the B03 CI cancellation-fixture repair only."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
OUT = BASE / 'formal-001'
OUT.mkdir(exist_ok=False)
old_path = ROOT / 'artifacts/B03/attempt-003/result.json'
old = json.loads(old_path.read_text())
spec = importlib.util.spec_from_file_location('b03_verify', ROOT / 'tests/Data.Sqlite/verify.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


initial = verify.source_identity()
changed = {p for p, digest in initial.items() if old['sourceSha256'].get(p) != digest}
assert changed == {'native/database/sqlite/tests/support/scenarios.rs', 'docs/guides/data-sqlite.md'}
assert not git('status', '--porcelain')
assert platform.system() == 'Linux' and platform.machine() == 'x86_64'
expected_aot = ROOT / 'artifacts/B03/attempt-003/publish/NativeWeave.Data.Sqlite.Tests'
assert sha(expected_aot) == old['artifacts'][str(expected_aot)]
product_native = ROOT / 'target/release/libnativeweave_data_sqlite.so'
assert sha(product_native) == old['artifacts'][str(product_native)]
env = os.environ.copy()
env.update(DOTNET_CLI_USE_MSBUILD_SERVER='0', DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_NOLOGO='1')
commands = []
manifest = {
    'schema': 1,
    'scope': 'B03 Linux x64 CI cancellation fixture repair; no production or API change',
    'status': 'running',
    'sourceCommit': git('rev-parse', 'HEAD'),
    'sourceDirty': False,
    'sourceSha256': initial,
    'changedSinceAcceptedB03': sorted(changed),
    'productManagedAndNativeSourcesUnchanged': True,
    'priorAcceptedReceipt': {'path': str(old_path), 'sha256': sha(old_path), 'sourceCommit': old['sourceCommit']},
    'reusedNativeAotConsumer': {'path': str(expected_aot), 'sha256': sha(expected_aot), 'sourceCommit': old['sourceCommit'], 'reason': 'Managed consumer and import declarations are unchanged; actual execution loads the newly rebuilt native fixture.'},
    'retainedProductNative': {'path': str(product_native), 'sha256': sha(product_native)},
    'runnerSha256': sha(Path(__file__)),
    'commands': commands,
    'artifacts': {},
    'allPlatformAcceptance': False,
    'independentReview': False,
}


def save():
    (OUT / 'result.json').write_text(json.dumps(manifest, indent=2) + '\n')


def run(label, command, extra=None):
    actual_env = env | (extra or {})
    stdout = OUT / (label + '.stdout.log')
    stderr = OUT / (label + '.stderr.log')
    begin = time.monotonic()
    with stdout.open('w') as out, stderr.open('w') as err:
        result = subprocess.run([str(a) for a in command], cwd=ROOT, env=actual_env, stdout=out, stderr=err, timeout=300)
    commands.append({'label': label, 'command': [str(a) for a in command], 'environmentOverrides': extra or {}, 'exitCode': result.returncode, 'seconds': round(time.monotonic() - begin, 3), 'stdoutSha256': sha(stdout), 'stderrSha256': sha(stderr)})
    save()
    print(label, result.returncode, flush=True)
    if result.returncode:
        raise RuntimeError(label + ' failed; original logs retained')
    return stdout.read_text()


try:
    save()
    run('source-diff-check', ['git', 'diff', '--check'])
    run('provider-format', ['cargo', 'fmt', '-p', 'nativeweave-data-sqlite', '--', '--check'])
    fixture = 'tests/Data.Sqlite/native-fixture/Cargo.toml'
    run('fixture-format', ['cargo', 'fmt', '--manifest-path', fixture, '--', '--check'])
    run('provider-clippy', ['cargo', 'clippy', '-p', 'nativeweave-data-sqlite', '--all-targets', '--locked', '--offline', '--', '-D', 'warnings'])
    run('fixture-clippy', ['cargo', 'clippy', '--manifest-path', fixture, '--all-targets', '--locked', '--offline', '--', '-D', 'warnings'])
    native_result = run('focused-release', ['cargo', 'test', '-p', 'nativeweave-data-sqlite', '--test', 'provider', '--release', '--locked', '--offline', 'actual_sqlite_provider_and_transaction_composition', '--', '--exact', '--nocapture'])
    markers = ['B03 cancellation before next fetch:', 'B03 cancellation inside worker:', 'B03 stale cancellation generation:']
    assert all(marker in native_result for marker in markers)
    fixture_output = run('fixture-build', ['cargo', 'build', '--manifest-path', fixture, '--release', '--locked', '--offline', '--message-format=json'])
    fixtures = [Path(f) for line in fixture_output.splitlines() if line.startswith('{') for item in [json.loads(line)] if item.get('reason') == 'compiler-artifact' and item['target']['name'] == 'nativeweave_sqlite_fixture' for f in item['filenames'] if f.endswith('.so')]
    assert len(fixtures) == 1
    native_fixture = fixtures[0]
    dotnet = shutil.which('dotnet')
    project = 'tests/Data.Sqlite/NativeWeave.Data.Sqlite.Tests.csproj'
    flags = ['-p:UseSharedCompilation=false', '-nr:false', '-m:1']
    run('jit-locked-restore', [dotnet, 'restore', project, '--locked-mode', '--configfile', '/workspace/scratch/0898a75257bc/task02-toolchain/NuGet.Offline.Config', '-p:NuGetAudit=false', *flags])
    run('jit-build', [dotnet, 'build', project, '-c', 'Release', '--no-restore', *flags])
    managed = ROOT / 'tests/Data.Sqlite/bin/Release/net11.0/NativeWeave.Data.Sqlite.Tests.dll'
    extra = {'LD_LIBRARY_PATH': str(native_fixture.parent), 'NATIVEWEAVE_B03_TEST_ROOT': str(OUT / 'jit-data')}
    jit = run('actual-jit', [dotnet, managed], extra)
    extra['NATIVEWEAVE_B03_TEST_ROOT'] = str(OUT / 'aot-data')
    aot = run('actual-native-aot', [expected_aot, '--aot'], extra)
    for label, text in [('jit', jit), ('aot', aot)]:
        assert all(marker in text for marker in markers), label
        assert all(f'PASS B03 native scenario {case}' in text for case in range(1, 15)), label
        assert 'PASS B03 36 assertions' in text, label
    assert 'NativeAOT=False' in jit and 'NativeAOT=True' in aot
    final = verify.source_identity()
    assert final == initial and not git('status', '--porcelain')
    assert sha(product_native) == old['artifacts'][str(product_native)]
    assert sha(expected_aot) == old['artifacts'][str(expected_aot)]
    manifest['artifacts'] = {str(path): sha(path) for path in [native_fixture, product_native, managed, expected_aot]}
    manifest.update(status='passed', sourceStable=True, exactCancellationLegs=['one retained row then stopped EOF before the next fetch', 'actual worker comparison then explicit release and exact Interrupted', 'fresh 5000-step recursive query unaffected by old cancellation'], nativeReleaseCases=12, fixtureCasesPerMode=14, managedAssertionsPerMode=36, actualNativeAotExecuted=True, nativeAotRecompiled=False, otherModuleSuitesRerun=False)
except Exception as error:
    manifest.update(status='failed', failure=str(error))
    save()
    raise
save()
print('PASS focused B03 repair; source and reused product/AOT bytes unchanged', flush=True)
