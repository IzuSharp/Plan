#!/usr/bin/env python3
"""Publish and run the untouched bc6 Orm.Relations suite, preserving both exits."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

root = Path('/workspace/scratch/4a65d70f0fe1')
worktree = root / 'worktrees/DB-Exec-04-cancel-validation'
output = Path(__file__).resolve().parent
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
stamp = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
expected = 'bc6ba1ae0ece02ecc2c0860776605f3c838f3ff8'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=worktree, text=True).strip() == expected
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=worktree, text=True).strip()
assert not (output / 'publish.log').exists(), 'Refusing to overwrite a prior attempt'
assets = {}
for provider in ['sqlite', 'postgresql']:
    manifest = root / 'artifacts' / ('close-native-' + provider) / 'manifest.json'
    data = json.loads(manifest.read_text())
    assert data['sourceCommit'] == expected and not data['sourceDirty']
    asset = data['assets'][0]
    assert sha(asset['path']) == asset['sha256']
    assets[provider] = asset
    shutil.copy2(manifest, output / ('native-' + provider + '-manifest.json'))
publish = ['dotnet', 'publish', 'tests/Orm.Relations/Korda.Orm.Relations.Tests.csproj',
           '-c', 'Release', '-r', 'linux-x64', '-p:PublishAot=true', '-p:RestoreLockedMode=true',
           '-p:IlcTreatWarningsAsErrors=true', '-p:UseSharedCompilation=false', '-m:1', '-nr:false',
           '-p:KordaSqliteAssetPath=' + assets['sqlite']['path'],
           '-p:KordaPostgresAssetPath=' + assets['postgresql']['path'], '-o', str(output / 'aot')]
receipt = {
    'scope': 'Original bc6 public-source Orm.Relations correctness reproduction; no ready-fast product or test modifications',
    'sourceHead': expected,
    'sourceTree': subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=worktree, text=True).strip(),
    'sourceDirty': False, 'startedUtc': stamp(), 'scriptSha256': sha(__file__),
    'testSources': {str(p.relative_to(worktree)): sha(p) for p in sorted((worktree / 'tests/Orm.Relations').iterdir()) if p.is_file()},
    'runnerSha256': sha(worktree / 'tests/Data.NativeHost/run.py'),
    'environmentScriptSha256': sha(root / 'tools/task-env.sh'),
    'nativeAssets': assets, 'publishCommand': publish,
    'publishOnlyEnvironment': {'DOTNET_PROCESSOR_COUNT': '1'},
}
(output / 'input-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
build_environment = os.environ.copy()
build_environment['DOTNET_PROCESSOR_COUNT'] = '1'
with (output / 'publish.log').open('w') as stream:
    built = subprocess.run(publish, cwd=worktree, env=build_environment, stdout=stream, stderr=subprocess.STDOUT)
receipt['publishExitCode'] = built.returncode
receipt['publishFinishedUtc'] = stamp()
receipt['publishLogSha256'] = sha(output / 'publish.log')
if built.returncode:
    (output / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')
    raise SystemExit(built.returncode)
executable = output / 'aot/Korda.Orm.Relations.Tests'
receipt['executableSha256Before'] = sha(executable)
assert executable.read_bytes()[:4] == b'\x7fELF'
for provider, asset in assets.items():
    assert sha(output / 'aot/runtimes/linux-x64/native' / Path(asset['path']).name) == asset['sha256']
run = ['python3', 'tests/Data.NativeHost/run.py', '--postgres-bin', os.environ['NW_POSTGRES_BIN'],
       '--output', str(output / 'providers'), '--', str(executable), '--require-aot']
receipt['runCommand'] = run
receipt['runStartedUtc'] = stamp()
with (output / 'run.log').open('w') as stream:
    result = subprocess.run(run, cwd=worktree, stdout=stream, stderr=subprocess.STDOUT)
receipt['runnerExitCode'] = result.returncode
receipt['finishedUtc'] = stamp()
receipt['executableSha256After'] = sha(executable)
receipt['logs'] = {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*.log')) if 'aot' not in p.relative_to(output).parts}
(output / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'publishExitCode': built.returncode, 'runnerExitCode': result.returncode, 'result': str(output / 'result.json')}))
raise SystemExit(result.returncode)
