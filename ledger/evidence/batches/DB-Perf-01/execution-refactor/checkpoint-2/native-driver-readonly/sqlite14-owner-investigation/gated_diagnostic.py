#!/usr/bin/env python3
"""Pause exact detached-thread epilogues; never replace the owner-zero oracle."""
from pathlib import Path
import difflib
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent
BASE = Path('/workspace/scratch/17ac3f8f2fbf/worktrees/DB-Exec-02-korda')
BUILD = BASE / 'artifacts/cmake/linux-x64-release'
VARIANT = ROOT / 'epilogue-gates'
VARIANT.mkdir(exist_ok=True)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)

host_original = (BASE / 'native/cpp/src/host.cpp').read_text()
host = replace_once(host_original, 'namespace nw\n{', '''namespace nw
{
void diagnostic_transaction_worker_exit(Transaction*, bool);
''')
host = replace_once(host,
    'std::thread([self, commit, gate] { self->finish_worker(commit, gate); }).detach();',
    'std::thread([self, commit, gate] { self->finish_worker(commit, gate); diagnostic_transaction_worker_exit(self.get(), false); }).detach();')
host = replace_once(host,
    'std::thread([self] { self->deadline_worker(); }).detach();',
    'std::thread([self] { self->deadline_worker(); diagnostic_transaction_worker_exit(self.get(), true); }).detach();')
host = replace_once(host,
    'std::thread([self, gate] { self->finish_worker(false, gate); }).detach();',
    'std::thread([self, gate] { self->finish_worker(false, gate); diagnostic_transaction_worker_exit(self.get(), false); }).detach();')

fixture_original = (ROOT / 'natural/sqlite.cpp').read_text()
fixture = replace_once(fixture_original, 'namespace nw\n{', '''namespace nw
{
std::mutex diagnostic_worker_mutex;
std::condition_variable diagnostic_worker_changed;
bool diagnostic_worker_entered = false, diagnostic_worker_released = false;
unsigned diagnostic_worker_mode = 0;
void diagnostic_transaction_worker_exit(Transaction* tx, bool deadline)
{
    if (diagnostic_worker_mode != (deadline ? 2U : 1U))
        return;
    std::unique_lock lock(diagnostic_worker_mutex);
    diagnostic_worker_entered = true;
    diagnostic_worker_changed.notify_all();
    diagnostic_worker_changed.wait_for(lock, std::chrono::seconds(15), [] { return diagnostic_worker_released; });
    (void)tx;
}
''')
fixture = replace_once(fixture,
    'std::filesystem::create_directories(root);\n    for (std::uint32_t diagnostic_round',
    'std::filesystem::create_directories(root);\n    diagnostic_worker_mode = static_cast<unsigned>(std::stoi(std::getenv("KORDA_DIAGNOSTIC_EPILOGUE")));\n    for (std::uint32_t diagnostic_round')
fixture = replace_once(fixture, 'const auto until = Clock::now() + 100ms;', '''{
                std::unique_lock lock(diagnostic_worker_mutex);
                diagnostic_worker_changed.wait_for(lock, 5s, [] { return diagnostic_worker_entered; });
                std::cerr << "DIAGNOSTIC epilogue gate mode=" << diagnostic_worker_mode << " entered=" << diagnostic_worker_entered << std::endl;
                diagnostic_worker_released = true;
            }
            diagnostic_worker_changed.notify_all();
            const auto until = Clock::now() + 100ms;''')
for name, original, changed in [('host.cpp', host_original, host), ('sqlite.cpp', fixture_original, fixture)]:
    (VARIANT / name).write_text(changed)
    (VARIANT / (name + '.original')).write_text(original)
    (VARIANT / (name + '.patch')).write_text(''.join(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
        fromfile='original/' + name, tofile='diagnostic/' + name)))

commands = json.loads((BUILD / 'compile_commands.json').read_text())
compile_commands = []
for suffix, output in [('/native/cpp/src/host.cpp', 'host.cpp'), ('/native/cpp/tests/fixtures/sqlite.cpp', 'sqlite.cpp')]:
    command = next(c for c in commands if c['file'].endswith(suffix) and 'korda_sqlite_fixture' in c['command'])
    args = shlex.split(command['command'])
    args[args.index('-o') + 1] = str(VARIANT / (output + '.o'))
    args[args.index('-c') + 1] = str(VARIANT / output)
    args += ['-I' + str(BASE / 'native/cpp/tests/fixtures')]
    compile_commands.append(args)

manifest = json.loads((ROOT / 'natural/build-manifest.json').read_text())
link_args = manifest['linkArgs'][:]
for i, arg in enumerate(link_args):
    if arg == str(ROOT / 'natural/sqlite.cpp.o'):
        link_args[i] = str(VARIANT / 'sqlite.cpp.o')
    elif arg.endswith('-host.cpp.o'):
        link_args[i] = str(VARIANT / 'host.cpp.o')
    elif arg.startswith('--dependency-file='):
        link_args[i] = '--dependency-file=' + str(VARIANT / 'link.d')
link_args[link_args.index('-o') + 1] = str(VARIANT / 'libkorda_sqlite_fixture.so')
shutil.copy2(ROOT / 'natural/nw_sqlite_fixture_tests', VARIANT / 'nw_sqlite_fixture_tests')
with (VARIANT / 'build.log').open('w') as log:
    for args in [*compile_commands, link_args]:
        result = subprocess.run(args, cwd=VARIANT, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise SystemExit(result.returncode)
output = {'sourceCommit': manifest['sourceCommit'], 'diagnosticOnly': True,
    'scope': 'Pause after detached finish_worker or deadline_worker returns, before lambda captures release. This models preemption at an existing source location. Original owner-zero predicate must still fail.',
    'originalHostSha256': hashlib.sha256(host_original.encode()).hexdigest(),
    'diagnosticHostSha256': sha(VARIANT / 'host.cpp'), 'diagnosticFixtureSourceSha256': sha(VARIANT / 'sqlite.cpp'),
    'hostPatchSha256': sha(VARIANT / 'host.cpp.patch'), 'fixturePatchSha256': sha(VARIANT / 'sqlite.cpp.patch'),
    'fixtureSha256': sha(VARIANT / 'libkorda_sqlite_fixture.so'),
    'compileArgs': compile_commands, 'linkArgs': link_args, 'reusedNaturalManifest': str(ROOT / 'natural/build-manifest.json')}
(VARIANT / 'build-manifest.json').write_text(json.dumps(output, indent=2) + '\n')
for mode in (1, 2):
    run = VARIANT / ('finish' if mode == 1 else 'deadline')
    run.mkdir(exist_ok=True)
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = str(VARIANT)
    env['TMPDIR'] = str(run)
    env['KORDA_DIAGNOSTIC_EPILOGUE'] = str(mode)
    start = time.time()
    result = subprocess.run([str(VARIANT / 'nw_sqlite_fixture_tests')], env=env, text=True, capture_output=True, timeout=30)
    (run / 'run.log').write_text(result.stdout + result.stderr)
    receipt = {'mode': mode, 'exit': result.returncode, 'durationSeconds': time.time() - start,
        'fixtureSha256': output['fixtureSha256'], 'exeSha256': sha(VARIANT / 'nw_sqlite_fixture_tests'),
        'ldLibraryPath': env['LD_LIBRARY_PATH'], 'tmpdir': env['TMPDIR']}
    (run / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))
    print(result.stdout + result.stderr)
