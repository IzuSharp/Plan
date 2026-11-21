#!/usr/bin/env python3
"""Local-only selected-asset B17/B19 managed subset caller; no native build."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def need(value, message):
    if not value:
        raise RuntimeError(message)


def relative(root, name):
    path = Path(name)
    need(not path.is_absolute() and '..' not in path.parts, 'Confined relative path required')
    path = (root / path).resolve()
    need(path.is_relative_to(root), 'Path escaped its declared root')
    return path


async def mapped_server(ctx, receipt_path, stopped, expected, reader):
    """Read only; original owner's current worker identity bounds each sample."""
    result = {'status': 'not-observed', 'observations': [], 'errors': []}
    while not stopped.is_set():
        try:
            receipt = read(receipt_path) if receipt_path.exists() else {}
            worker = receipt.get('worker')
            if worker is not None:
                before = ctx.owner.proc(worker['pid'])
                if before and before['start_ticks'] == worker['start_ticks']:
                    mapping = reader.mapping_sample(worker['pid'])
                    paths = [name for name in mapping.get('modules', {})
                             if Path(name).name == 'libnativeweave_server.so']
                    if paths:
                        actual = {name: sha(name) for name in paths}
                        after = ctx.owner.proc(worker['pid'])
                        if after and after['start_ticks'] == worker['start_ticks']:
                            need(len(actual) == 1 and all(expected.get(name) == digest for name, digest in actual.items()),
                                 'Observed Server mapping differs from selected runtime copy')
                            result.update(status='observed', observations=[{
                                'pid': worker['pid'], 'start_ticks': worker['start_ticks'],
                                'observed_utc': ctx.owner.utc(), 'native_sha256': actual,
                                'method': 'Original common.mapping_sample; owner PID/start identity checked before and after hashing'}])
                            return result
        except (OSError, ValueError, RuntimeError) as error:
            result['errors'].append(type(error).__name__ + ': ' + str(error))
            return result
        await asyncio.sleep(.02)
    return result


async def command(run, label, argv, timeout, *, cwd=None, environment=None, native=None, reader=None, source=None, service=True):
    ctx = run.ctx
    if source is not None:
        ctx.build.source(source, ctx.selected)
    overrides = environment or {}
    run.record['command_environment_overrides'][label] = overrides
    run.checkpoint()
    previous, stopped, observation = ctx.environment, asyncio.Event(), None
    ctx.environment = dict(previous, **overrides)
    if native is not None:
        observation = asyncio.create_task(mapped_server(ctx, run.output / 'commands' / label / 'receipt.json', stopped, native, reader))
    try:
        actual = await run.command(label, argv, timeout, cwd=cwd, service=service)
    finally:
        ctx.environment = previous
        stopped.set()
        if observation is not None:
            value = await observation
            path = run.output / (label + '-mapped-server.json')
            ctx.owner.save(path, value)
            run.record['runtime_native_observations'][label] = {'path': str(path), 'sha256': sha(path), 'status': value['status']}
            run.checkpoint()
    if source is not None:
        ctx.build.source(source, ctx.selected)
    if observation is not None:
        need(value['status'] == 'observed' and not value['errors'], 'Actual Server mapping was not established')
    return actual


def runtime_artifacts(directory, assembly, mode, selected):
    executable = directory / (assembly + '.dll' if mode == 'jit' else assembly)
    need(executable.is_file(), 'Original fixture executable is absent')
    manifest = directory / 'NativeWeave.server.assets.json'
    metadata = read(manifest)
    need(metadata['engineId'] == 'server' and metadata['rid'] == 'linux-x64'
         and metadata['sha256'] == selected['sha256'], 'Generated facade asset identity differs')
    expected = relative(directory, metadata['outputPath'])
    need(expected.is_file() and sha(expected) == selected['sha256'], 'Declared runtime native copy differs')
    copies = {str(path.resolve()): sha(path) for path in directory.rglob('libnativeweave_server.so')}
    need(copies and all(value == selected['sha256'] for value in copies.values()), 'Runtime directory contains a different Server copy')
    return executable, {'executable': {'path': str(executable), 'sha256': sha(executable)},
                        'asset_manifest': {'path': str(manifest), 'sha256': sha(manifest)}, 'native_copies_sha256': copies}


def fixture_result(task, mode, text):
    dynamic = 'True' if mode == 'jit' else 'False'
    if task == 'b17':
        matches = re.findall(r'^PASS B17 checks=(\d+) dispatches=(\d+) dynamic=(True|False)$', text, re.M)
        required = ['PASS transport Http1 TLS=False HTTP=1.1', 'PASS transport Http2 TLS=False HTTP=2.0',
            'PASS transport Http1AndHttp2 TLS=True HTTP=2.0', 'PASS transport Http1AndHttp2 TLS=True HTTP=1.1',
            'PASS request admission and final-lease retirement HTTP/1.1 + HTTP/2 TLS']
        need(len(matches) == 1 and matches[0][2] == dynamic and all(text.splitlines().count(line) == 1 for line in required),
             'B17 required transport/retirement/final markers differ')
        checks, dispatches = map(int, matches[0][:2])
        need(checks > 0 and dispatches > 0, 'B17 did not perform actual assertions/dispatches')
        return {'checks': checks, 'dispatches': dispatches, 'dynamic': dynamic, 'required_markers': required}
    matches = re.findall(r'^B19 actual Host assertions=(\d+), managed_retirements=(\d+), dynamic=(True|False)$', text, re.M)
    need(len(matches) == 1 and matches[0][2] == dynamic, 'B19 complete default fixture marker differs')
    assertions, retirements = map(int, matches[0][:2])
    need(assertions >= 230 and retirements > 0, 'B19 assertion/retirement requirement failed')
    return {'assertions': assertions, 'managed_retirements': retirements, 'dynamic': dynamic}


async def execute(run, plan):
    ctx, output = run.ctx, run.output
    selected = next(value for value in ctx.built['after']['native_assets'] if value['engineId'] == 'server')
    ctx.pin(selected['path'], selected['sha256'])
    asset = output / 'input/libnativeweave_server.so'
    asset.parent.mkdir()
    shutil.copy2(selected['path'], asset)
    ctx.pin(asset, selected['sha256'])
    run.record['selected_server_asset'] = selected
    run.record['copied_server_asset'] = {'path': str(asset), 'sha256': sha(asset)}
    trap = output / 'no-native-build'
    trap.mkdir()
    for name in ('cargo', 'rustc', 'rustup'):
        path = trap / name
        path.write_text('#!/bin/sh\necho unexpected-native-build >&2\nexit 197\n')
        path.chmod(0o700)
    spec = importlib.util.spec_from_file_location('perf01_server_mapping_reader', ctx.driver / 'src/Benchmarks.Domain/common.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    dotnet = ctx.toolchain['tools']['dotnet']['path']
    flags = ['-p:UseSharedCompilation=false', '-nr:false', '-m:1']
    cache = ctx.build_root / 'functional-after/producer-cache'
    cache_manifest = read(run.args.dependency_cache)
    receipt_path, receipt = ctx.document(ctx.functional_inputs['after'])
    need(cache_manifest['selected_product_commit'] == ctx.selected
         and cache_manifest['cache_relative_to_build_output'] == 'functional-after/producer-cache'
         and sha(receipt_path) == cache_manifest['functional_execution_sha256']
         and receipt['environment']['NUGET_PACKAGES'] == str(cache), 'Completed B18 dependency cache differs')
    for name, digest in cache_manifest['files_sha256'].items():
        ctx.pin(relative(cache, name), digest)
    for name, digest in cache_manifest['project_closure_files_sha256'].items():
        ctx.pin(relative(ctx.products['after'], name), digest)
    run.record['dependency_cache'] = {'path': str(cache), 'manifest': str(run.args.dependency_cache), 'manifest_sha256': run.args.dependency_cache_sha256,
        'functional_execution_sha256': sha(receipt_path), 'scope': 'Exact existing dependencies; fresh source and managed outputs'}
    for task, fixture in plan['fixtures'].items():
        worktree = ctx.root / '.worktree' / ('Perf-01-server-regression-' + task + '-' + run.args.label + '-linux') / 'NativeWeave'
        need(not worktree.exists(), 'Fresh detached regression worktree required')
        worktree.parent.mkdir(parents=True, exist_ok=True)
        await command(run, task + '-source', ['git', 'worktree', 'add', '--detach', worktree, ctx.selected], 120,
                      cwd=ctx.products['after'], service=False)
        run.record['fixture_source'][task] = ctx.build.source(worktree, ctx.selected)
        run.record['fixture_source'][task]['fresh_project_output_locations_checked'] = len(ctx.build.freshness(worktree))
        project = worktree / fixture['project']
        folder = output / task
        folder.mkdir()
        environment = {'NUGET_PACKAGES': str(cache), 'DOTNET_CLI_USE_MSBUILD_SERVER': '0', 'MSBUILDDISABLENODEREUSE': '1',
                       'PATH': str(trap) + os.pathsep + ctx.environment['PATH']}
        asset_flag = '-p:NativeWeaveServerAssetPath=' + str(asset)
        results = {}
        for mode in ('jit', 'aot'):
            mode_folder = folder / mode
            mode_folder.mkdir()
            temporary, evidence = mode_folder / 'tmp', mode_folder / 'fixture-evidence'
            temporary.mkdir(mode=0o700); evidence.mkdir(mode=0o700)
            current = dict(environment, TMPDIR=str(temporary), NW_SERVER_EVIDENCE=str(evidence))
            target = [] if mode == 'jit' else ['-r', 'linux-x64', '-p:PublishAot=true']
            await command(run, task + '-restore-' + mode, [dotnet, 'restore', project, *target,
                '--locked-mode', '--ignore-failed-sources', *flags], fixture['restore_' + mode + '_timeout_seconds'],
                cwd=worktree, environment=current, source=worktree)
            if mode == 'jit':
                argv = [dotnet, 'build', project, '-c', 'Release', '--no-restore', asset_flag, *flags]
                directory = project.parent / 'bin/Release/net11.0'
            else:
                directory = mode_folder / 'publish'
                argv = [dotnet, 'publish', project, '-c', 'Release', *target, '--no-restore', asset_flag, '-o', directory, *flags]
            timeout = fixture['build_jit_timeout_seconds' if mode == 'jit' else 'publish_aot_timeout_seconds']
            await command(run, task + '-build-' + mode, argv, timeout, cwd=worktree, environment=current, source=worktree)
            executable, artifacts = runtime_artifacts(directory, fixture['assembly'], mode, selected)
            run.record['artifacts'][task + '-' + mode] = artifacts
            run.checkpoint()
            actual = await command(run, task + '-run-' + mode, [dotnet, executable] if mode == 'jit' else [executable],
                fixture['runtime_timeout_seconds'], cwd=worktree, environment=current,
                native=artifacts['native_copies_sha256'], reader=reader, source=worktree)
            receipt = Path(actual['path'])
            results[mode] = fixture_result(task, mode, (receipt.parent / 'stdout.log').read_text())
            need(runtime_artifacts(directory, fixture['assembly'], mode, selected)[1] == artifacts, 'Runtime files changed during fixture')
            run.record['fixture_results'][task + '-' + mode] = results[mode]
            run.checkpoint()
        if task == 'b19':
            need(results['jit']['assertions'] == results['aot']['assertions'], 'B19 JIT/AOT assertion counts differ')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'admission', 'final-binding', 'dependency-cache'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('admission-sha256', 'final-binding-sha256', 'dependency-cache-sha256', 'source-index-sha256', 'label'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    need(os.sched_getaffinity(0) == {8} and re.fullmatch('[a-z0-9][a-z0-9-]{0,39}', args.label), 'CPU8 and fresh short label required')
    need(sha(HERE / 'sources.json') == args.source_index_sha256, 'Local subset source index changed')
    index = read(HERE / 'sources.json')
    for name, digest in index['files_sha256'].items():
        need(sha(relative(HERE, name)) == digest, 'Local subset source/plan changed')
    measurement = HERE.parent / 'recovery-measure-002'
    need(sha(measurement / 'measurement-sources.json') == index['measurement_source_index_sha256'], 'Canonical measurement interface changed')
    source = read(measurement / 'measurement-sources.json')
    for name in ('admission.py', 'measure.py'):
        need(sha(measurement / name) == source['files_sha256'][name], 'Admission/finite caller changed')
    need(sha(args.admission) == args.admission_sha256, 'Actual baseline/common admission changed')
    root, admission = args.root.resolve(strict=True), read(args.admission)
    build_input = relative(root, admission['build_inputs']['path'])
    need(sha(build_input) == admission['build_inputs']['sha256'], 'Actual build input changed')
    reservation_path = relative(root, read(build_input)['exclusive_lock'])
    with reservation_path.open('a+b') as reservation:
        fcntl.flock(reservation.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        sys.path.insert(0, str(measurement))
        module = importlib.import_module('measure')
        ctx = module.Context(root, args.admission, args.admission_sha256, index['measurement_source_index_sha256'],
                             args.final_binding, args.final_binding_sha256)
        need(args.dependency_cache.resolve(strict=True).is_relative_to(root), 'Dependency cache descriptor must remain local')
        ctx.pin(args.dependency_cache, args.dependency_cache_sha256)
        plan = read(HERE / 'plan.json')
        need(ctx.selected == plan['selected_product_commit'] and ctx.reservation == reservation_path, 'Selected product/reservation differs')
        need(ctx.value['build_source_index']['sha256'] == plan['required_build_source_index_sha256']
             and index['measurement_source_index_sha256'] == plan['required_measurement_source_index_sha256'],
             'Reviewed build/measurement interface differs from this subset plan')
        ctx.pin(HERE / 'sources.json', args.source_index_sha256)
        for name, digest in index['files_sha256'].items():
            ctx.pin(relative(HERE, name), digest)
        for name, digest in index['selected_product_source_sha256'].items():
            ctx.pin(relative(ctx.products['after'], name), digest)
        for name, digest in index['driver_source_sha256'].items():
            ctx.pin(relative(ctx.driver, name), digest)
        os.umask(0o077)
        output = ctx.output.parent / 'server-regression-001' / args.label
        need(not output.exists() and not output.is_relative_to(ctx.output), 'Fresh separate regression output required')
        output.mkdir(parents=True)
        args.stage, args.group, args.scene, args.role = 'managed-server-regression', 'server', 'b17-b19', 'after'
        run = module.Run(ctx, args, output)
        run.record.update(scope=plan['scope'], subset_source_index_sha256=args.source_index_sha256,
            command_environment_overrides={}, runtime_native_observations={}, fixture_source={}, artifacts={}, fixture_results={},
            rust_server_build_executed=False, global_acceptance=False, formal_timing_eligible=False, performance_credit_seconds=0)
        run.checkpoint()
        try:
            ctx.owner.enable_subreaper()
            run.tree = ctx.owner.public_tree(ctx.driver)
            async def owned():
                loop, task = asyncio.get_running_loop(), asyncio.current_task()
                for sig in (signal.SIGTERM, signal.SIGINT):
                    loop.add_signal_handler(sig, task.cancel)
                await execute(run, plan)
            asyncio.run(owned())
            need(len(run.record['commands']) == len(run.record['planned_commands']) == 14,
                 'Expected two source-worktree commands and twelve original managed commands')
            ctx.stable()
            run.record['status'] = 'completed'
        except BaseException as error:
            run.record.update(status='failed', failure=type(error).__name__ + ': ' + str(error))
            raise
        finally:
            run.record.update(ended_utc=ctx.owner.utc(), duration_credit_seconds=0)
            run.checkpoint()
    print(json.dumps({'status': run.record['status'], 'execution': str(output / 'execution.json'), 'sha256': sha(output / 'execution.json')}))


if __name__ == '__main__':
    main()
