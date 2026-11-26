#!/usr/bin/env python3
"""Build a read-only-object SQLite case 4 diagnostic, never a formal artifact."""
from pathlib import Path
import difflib
import hashlib
import json
import os
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
BASE = Path('/workspace/scratch/17ac3f8f2fbf/worktrees/DB-Exec-02-retirement-fence')
BUILD = BASE / 'artifacts/cmake/linux-x64-release'
NINJA = Path('/workspace/scratch/17ac3f8f2fbf/tools/toolchain/ninja-1.13.2/ninja')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)

original = (BASE / 'native/cpp/tests/fixtures/sqlite.cpp').read_text()
source = replace_once(original, 'std::atomic<std::size_t> assertions{0};', '''std::atomic<std::size_t> assertions{0};
std::weak_ptr<Source> diagnostic_source;
std::weak_ptr<Session> diagnostic_session;
std::weak_ptr<Transaction> diagnostic_transaction;
''')
source = replace_once(source,
    'explicit Scope(HostConfig config) : source(Source::create(std::move(config))) {}',
    'explicit Scope(HostConfig config) : source(Source::create(std::move(config))) { diagnostic_source = source; }')
source = replace_once(source, 'sessions.push_back(session);',
    'sessions.push_back(session);\n        diagnostic_session = session;')
source = replace_once(source,
    'return Transaction::begin(session, std::move(options), token(), session->admit(true));',
    'auto value = Transaction::begin(session, std::move(options), token(), session->admit(true));\n'
    '    diagnostic_transaction = value;\n    return value;')
source = replace_once(source, 'for (std::uint32_t i = 1; i <= 14; ++i)\n    {',
    'for (std::uint32_t diagnostic_round = 0; diagnostic_round < 300; ++diagnostic_round)\n    {\n'
    '        const std::uint32_t i = 4;')
source = replace_once(source,
    'const auto file = root / ("case-" + std::to_string(i) + ".db");',
    'const auto file = root / ("case-" + std::to_string(i) + "-round-" + std::to_string(diagnostic_round) + ".db");')
source = replace_once(source,
    '''check(source_count == 0 && session_count == 0 && cursor_count == 0 && buffer_count == 0 && operation_count == 0,
              "scenario leaked native owners");''',
    '''const auto sources = source_count.load();
        const auto sessions = session_count.load();
        const auto cursors = cursor_count.load();
        const auto buffers = buffer_count.load();
        const auto operations = operation_count.load();
        const bool clean = sources == 0 && sessions == 0 && cursors == 0 && buffers == 0 && operations == 0;
        if (!clean)
        {
            std::cerr << "DIAGNOSTIC failure round=" << diagnostic_round << " counts=" << sources << ',' << sessions
                      << ',' << cursors << ',' << buffers << ',' << operations << std::endl;
            if (auto tx = diagnostic_transaction.lock())
            {
                std::lock_guard lock(tx->mutex);
                std::cerr << "DIAGNOSTIC transaction retained=" << tx.use_count() << " retired=" << tx->retired
                          << " primary_ready=" << tx->primary_ready << " finishing=" << tx->finishing << std::endl;
            }
            if (auto session = diagnostic_session.lock())
                std::cerr << "DIAGNOSTIC session retained=" << session.use_count() << " retired=" << session->retired.load()
                          << " active=" << session->active.load() << " connection=" << bool(session->connection) << std::endl;
            if (auto source = diagnostic_source.lock())
                std::cerr << "DIAGNOSTIC source retained=" << source.use_count() << " retired=" << source->retired.load()
                          << " leased=" << source->leased << " pending=" << source->pending.load() << std::endl;
            const auto until = Clock::now() + 100ms;
            while ((source_count || session_count || cursor_count || buffer_count || operation_count) && Clock::now() < until)
                std::this_thread::yield();
            std::cerr << "DIAGNOSTIC after bounded observation counts=" << source_count << ',' << session_count << ','
                      << cursor_count << ',' << buffer_count << ',' << operation_count << " tx_expired="
                      << diagnostic_transaction.expired() << std::endl;
        }
        check(clean, "scenario leaked native owners");''')
source = replace_once(source, '                savepoint_worker_epilogues(root);', '                // Dedicated epilogue gates ran in the formal native target; this is the natural case 4 loop.')
variant = ROOT / 'fixed-natural'
variant.mkdir(parents=True, exist_ok=True)
src = variant / 'sqlite.cpp'
src.write_text(source)
(variant / 'sqlite.original.cpp').write_text(original)
(variant / 'instrumentation.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True), source.splitlines(True),
    fromfile='native/cpp/tests/fixtures/sqlite.cpp', tofile='diagnostic/sqlite.cpp')))

commands = json.loads((BUILD / 'compile_commands.json').read_text())
entry = next(c for c in commands if c['file'].endswith('/native/cpp/tests/fixtures/sqlite.cpp') and 'korda_sqlite_fixture' in c['command'])
compile_args = shlex.split(entry['command'])
compile_args[compile_args.index('-o') + 1] = str(variant / 'sqlite.cpp.o')
compile_args[compile_args.index('-c') + 1] = str(src)
compile_args += ['-I' + str(BASE / 'native/cpp/tests/fixtures')]
raw = subprocess.check_output([str(NINJA), '-t', 'commands', 'fixtures/libkorda_sqlite_fixture.so'], cwd=BUILD, text=True).splitlines()[-1]
link_args = shlex.split(raw.removeprefix(': && ').removesuffix(' && :'))
inputs = []
copied = variant / 'original-objects'
copied.mkdir(exist_ok=True)
for index, arg in enumerate(link_args):
    if arg.startswith('--dependency-file='):
        link_args[index] = '--dependency-file=' + str(variant / 'link.d')
    elif arg.endswith('.cpp.o') or arg.endswith('.a'):
        path = (BUILD / arg).resolve()
        if arg.endswith('/fixtures/sqlite.cpp.o'):
            link_args[index] = str(variant / 'sqlite.cpp.o')
        else:
            target = copied / (str(len(inputs)) + '-' + path.name)
            shutil.copy2(path, target)
            link_args[index] = str(target)
            inputs.append({'source': str(path), 'copy': str(target), 'sha256': sha(target)})
    elif arg.startswith('--version-script='):
        original_map = Path(arg.split('=', 1)[1])
        copy_map = variant / 'exports.map'
        shutil.copy2(original_map, copy_map)
        link_args[index] = '--version-script=' + str(copy_map)
link_args[link_args.index('-o') + 1] = str(variant / 'libkorda_sqlite_fixture.so')
runner = variant / 'nw_sqlite_fixture_tests'
shutil.copy2(BUILD / 'tests/nw_sqlite_fixture_tests', runner)
manifest = {'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=BASE, text=True).strip(),
    'scope': 'Diagnostic only; case 4 repeated up to 300 times, original owner-zero predicate retained from immediate snapshot. No formal files modified.',
    'sourceOriginalSha256': hashlib.sha256(original.encode()).hexdigest(),
    'sourceDiagnosticSha256': sha(src), 'patchSha256': sha(variant / 'instrumentation.patch'),
    'formalExecutableSha256': sha(BUILD / 'tests/nw_sqlite_fixture_tests'),
    'formalFixtureSha256': sha(BUILD / 'fixtures/libkorda_sqlite_fixture.so'),
    'compileArgs': compile_args, 'linkArgs': link_args, 'reusedInputs': inputs}
(variant / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
with (variant / 'build.log').open('w') as log:
    for args in (compile_args, link_args):
        result = subprocess.run(args, cwd=variant, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise SystemExit(result.returncode)
manifest['diagnosticFixtureSha256'] = sha(variant / 'libkorda_sqlite_fixture.so')
(variant / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'variant': str(variant), 'fixtureSha256': manifest['diagnosticFixtureSha256'], 'build': 'passed'}))
