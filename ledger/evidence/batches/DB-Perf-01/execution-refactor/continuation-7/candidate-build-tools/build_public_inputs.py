#!/usr/bin/env python3
"""Build one exact, independent provider and external AOT inputs; no load runs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--tree', required=True)
    parser.add_argument('--provider', choices=('sqlite', 'postgresql'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--postgres-bin', type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if output.exists() or output == source or source in output.parents:
        parser.error('Choose a fresh output outside the producer checkout')
    for value in (args.commit, args.tree):
        if len(value) != 40 or any(c not in '0123456789abcdef' for c in value):
            parser.error('Pass exact commit and tree object IDs')

    def git(*argv):
        return subprocess.check_output(['git', *argv], cwd=source, text=True).strip()

    def unchanged():
        return (git('rev-parse', 'HEAD') == args.commit and
                git('rev-parse', 'HEAD^{tree}') == args.tree and
                not git('status', '--porcelain'))

    if not unchanged():
        raise RuntimeError('Exact clean published producer required')
    if (source / 'artifacts/public').exists():
        raise RuntimeError('Use a fresh independent producer worktree for each package attempt')
    if Path(os.environ.get('NW_POSTGRES_BIN', '')).resolve() != args.postgres_bin.resolve():
        raise RuntimeError('Native libpq provenance and test server must use the same pinned installation')
    output.mkdir(parents=True)
    (output / 'logs').mkdir()
    receipt = {'schemaVersion': 1, 'source': str(source), 'sourceCommit': args.commit,
               'sourceTree': args.tree, 'sourceDirty': False, 'provider': args.provider,
               'script': str(Path(__file__).resolve()), 'scriptSha256': sha(__file__),
               'startedUtc': now(), 'performanceCredit': False, 'records': []}

    def save():
        (output / 'build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')

    def run(stage, argv, dotnet=False):
        argv = list(map(str, argv))
        log = output / 'logs' / (stage + '.log')
        environment = os.environ.copy()
        if dotnet:
            environment.update(DOTNET_PROCESSOR_COUNT='1', UseSharedCompilation='false',
                               MSBUILDDISABLENODEREUSE='1', NuGetAudit='false')
        record = {'stage': stage, 'argv': argv, 'cwd': str(source), 'startedUtc': now(),
                  'buildOnlyProcessorCount': 1 if dotnet else None,
                  'buildOnlyNuGetAudit': False if dotnet else None}
        receipt['records'].append(record)
        save()
        with log.open('xb') as stream:
            result = subprocess.run(argv, cwd=source, env=environment,
                                    stdout=stream, stderr=subprocess.STDOUT)
        record.update(exitCode=result.returncode, finishedUtc=now(), log=str(log),
                      logSha256=sha(log), sourceUnchanged=unchanged())
        save()
        print(json.dumps({'provider': args.provider, 'stage': stage,
                          'exitCode': result.returncode, 'log': str(log)}), flush=True)
        if result.returncode or not record['sourceUnchanged']:
            raise SystemExit(result.returncode or 1)

    def pg(command, label):
        return [sys.executable, 'tests/Data.NativeHost/run.py', '--postgres-bin',
                args.postgres_bin.resolve(), '--output', output / label, '--', *command]

    save()
    run('impact', [sys.executable, 'eng/ci/impact.py', 'origin/main', '--output', 'artifacts/plan.json'])
    plan_path = source / 'artifacts/plan.json'
    plan = json.loads(plan_path.read_text())
    if (set(plan['actions']) != {'interop', 'linux', 'postgresql', 'sqlite'} or
            plan['run_steps'] or set(plan['public_checks']) != {'postgresql', 'sqlite'}):
        raise RuntimeError('Unexpected CI selection; explain before proceeding')
    shutil.copyfile(plan_path, output / 'ci-plan.json')
    version = plan['versions'][args.provider]
    receipt.update(version=version, ciPlanSha256=sha(plan_path))
    save()
    native = output / 'native'
    run('native', [sys.executable, 'eng/task07_native.py', '--provider', args.provider,
                   '--output', native])
    native_tests = ['ctest', '--preset', 'linux-x64-' + args.provider, '--output-on-failure']
    run('native-correctness', pg(native_tests, 'native-postgres')
        if args.provider == 'postgresql' else native_tests)
    run('bundle', [sys.executable, 'eng/ci/bundles.py', '--provider', args.provider,
                   '--plan', plan_path, '--version', version, '--native', native / 'manifest.json'], True)
    consume = [sys.executable, 'eng/ci/consume.py', 'artifacts/public/release.json', plan_path]
    run('public-consume-aot', pg(consume, 'consumer-postgres')
        if args.provider == 'postgresql' else consume, True)
    run('public-validate', [sys.executable, 'eng/ci/validate_public.py', 'artifacts/public',
                           plan_path, version, '--module', args.provider])
    package = output / 'public'
    shutil.copytree(source / 'artifacts/public', package)
    for kind in ('query-phases', 'workload'):
        run('consumer-' + kind, [sys.executable, 'benchmarks/db-perf/managed/build.py',
            '--provider', args.provider, '--feed', package / 'feed', '--version', version,
            '--kind', kind, '--output', output / ('consumer-' + kind)], True)
    receipt.update(finishedUtc=now(), passed=True,
                   nativeManifestSha256=sha(native / 'manifest.json'),
                   releaseReceiptSha256=sha(package / 'release.json'))
    save()
    print(json.dumps({'receipt': str(output / 'build-receipt.json'),
                      'sha256': sha(output / 'build-receipt.json')}), flush=True)


if __name__ == '__main__':
    main()
