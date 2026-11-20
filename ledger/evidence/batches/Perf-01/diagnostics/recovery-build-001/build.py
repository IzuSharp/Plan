#!/usr/bin/env python3
"""Fresh recovery-001 producers and identity binding; no performance execution."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys

import bindings
from owner import command, enable_subreaper, public_tree, save, sha, utc

HERE = Path(__file__).resolve().parent
need = bindings.need


def source(path, expected):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(path), *args], text=True, timeout=30).strip()
    need(git('rev-parse', 'HEAD') == expected and not git('status', '--porcelain'), 'Source must be the exact clean commit: ' + str(path))
    return dict(path=str(path), commit=expected, tree=git('rev-parse', 'HEAD^{tree}'), dirty=False)


def freshness(product):
    paths = subprocess.check_output(['git', '-C', str(product), 'ls-files', '-z', '--', '*.csproj'], timeout=30).decode().split('\0')
    folders = sorted({str(Path(name).parent) for name in paths if name})
    checked = [product / folder / kind for folder in folders for kind in ('bin', 'obj')]
    need(checked and all(not os.path.lexists(p) for p in checked), 'Fresh product checkout required: tracked project bin/obj already exists')
    return [str(p) for p in checked]


def plan(stage, inputs, root, tools):
    driver = root / inputs['driver']
    output = root / inputs['output'] / stage
    python, dotnet = tools['python']['path'], tools['dotnet']['path']
    pg = str(Path(tools['postgres']['path']).parent)
    rows = []
    def add(label, relative, arguments, timeout, cwd=driver, environment=None):
        rows.append(dict(label=label, argv=[python, str(cwd / relative), *map(str, arguments)],
                         cwd=str(cwd), timeout_seconds=timeout, environment_overrides=environment or {}))
    if stage in ('before', 'after'):
        product = root / inputs['products'][stage]['path']
        version = inputs['products'][stage]['version']
        feed = output / 'packages/previous/feed'
        add('native-stable', 'eng/task07_native.py', ['--output', output / 'native-stable'], 3600,
            product, {'CARGO_TARGET_DIR': str(output / 'cargo-stable-target')})
        add('packages', 'src/Packaging.Domain/prepare.py', ['--output', output / 'packages', '--previous-version', version,
            '--candidate-version', inputs['products'][stage]['upgrade_version'], '--native-manifest', output / 'native-stable/manifest.json'], 3600, product)
        add('reference', 'tests/Reference.TaskService/package_probe.py', ['--source', driver, '--runner', driver / 'tests/Reference.TaskService/run.py',
            '--feed', feed, '--version', version, '--postgres-bin', pg, '--output', output / 'reference', '--variants', 'baseline',
            '--providers', 'sqlite', '--modes', 'jit', 'aot', '--protocols', 'http1', '--build-only'], 3600)
        add('observer', 'tests/Perf01.Database/prepare_observer.py', ['--package-probe', output / 'reference', '--output', output / 'db-observer',
            '--dotnet', dotnet], 1800, environment={'NUGET_PACKAGES': str(output / 'reference/consumer-cache')})
        add('protocols', 'tests/Perf01.Protocols/build.py', ['--feed', feed, '--version', version, '--sdk', dotnet,
            '--output', output / 'protocols', '--package-manifest', output / 'packages/manifest.json',
            '--native-manifest', output / 'native-stable/manifest.json'], 3600)
        add('codec', 'tests/Perf01.Codec/driver.py', ['prepare', '--product-root', product, '--output', output / 'codec'], 5400)
        add('shared-retirement', 'tests/Perf01.Shared/prepare.py', ['--feed', feed, '--version', version, '--output', output / 'shared-retirement'], 1800)
        add('shared-page', 'tests/Perf01.Shared/prepare.py', ['--probe', 'page', '--feed', feed, '--version', version, '--output', output / 'shared-page'], 1800)
    elif stage == 'common':
        before = root / inputs['output'] / 'before'
        add('direct-protocols', 'tests/Perf01.Protocols/build-direct.py', ['--client-build', before / 'protocols/build.json', '--output', output / 'protocols'], 3600)
        add('database-comparators', 'tests/Perf01.Database/prepare_comparators.py', ['--product-root', driver, '--output', output / 'database',
            '--compiler', tools['clang19']['path'], '--jobs', '3'], 5400)
        codec = bindings.read(before / 'codec/manifest.json')
        add('codec-corpus', 'tests/Perf01.Codec/driver.py', ['corpus', '--direct', codec['direct_executable'], '--output', output / 'codec-corpus'], 120)
    return rows


def completed(root, inputs, stage, expected):
    path = root / inputs['control'] / ('build-' + stage) / 'execution.json'
    need(expected and sha(path) == expected, 'Exact completed prerequisite receipt required: ' + stage)
    record = bindings.read(path)
    need(record['status'] == 'completed' and record['stage'] == stage and record['inputs_sha256'] == inputs['_sha256']
         and record['source_index_sha256'] == inputs['_source_index_sha256']
         and record['toolchain_sha256'] == inputs['toolchain']['sha256'] and record['freeze_sha256'] == inputs['freeze']['sha256'],
         'Wrong completed prerequisite identity')
    need(len(record['commands']) == (3 if stage == 'common' else 8), 'Prerequisite producer population differs')
    need(all(c['exit_code'] == 0 and c['retired'] for c in record['commands']), 'Prerequisite has unretired/failed command')
    need(record['planned_commands'] == plan(stage, inputs, root, inputs['_tools']), 'Prerequisite command recipe differs')
    for planned, actual in zip(record['planned_commands'], record['commands'], strict=True):
        child = Path(actual['path'])
        need(sha(child) == actual['sha256'], 'Actual producer child receipt changed')
        observed = bindings.read(child)
        need(observed['status'] == 'completed' and observed['retired'] and observed['exit_code'] == 0
             and all(observed[key] == value for key, value in planned.items()), 'Actual producer command/retirement differs')
        for name, digest in observed['logs_sha256'].items():
            need(sha(child.parent / name) == digest, 'Actual producer log changed')
    binding = path.parent / 'binding.json'
    need(sha(binding) == record['binding_sha256'], 'Prerequisite binding changed')
    value = bindings.read(binding)
    b = bindings.Binding(); b.mapping(value['files_sha256'])
    return {'execution': str(path), 'execution_sha256': expected, 'binding': str(binding), 'binding_sha256': sha(binding)}, value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--inputs-sha256', required=True)
    parser.add_argument('--source-index-sha256', required=True)
    parser.add_argument('--stage', choices=('before', 'after', 'common', 'bind-pair'), required=True)
    parser.add_argument('--before-receipt-sha256')
    parser.add_argument('--after-receipt-sha256')
    parser.add_argument('--common-receipt-sha256')
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    need(sys.version_info[:3] == (3, 12, 14) and platform.system() == 'Linux' and platform.machine() == 'x86_64', 'Pinned Python/Linux x64 required')
    need(os.sched_getaffinity(0) == {8}, 'Build owner must use the frozen controller CPU8')
    root = args.root.resolve(strict=True)
    need(sha(args.inputs) == args.inputs_sha256 and sha(HERE / 'sources.json') == args.source_index_sha256, 'Input/source index identity mismatch')
    inputs = bindings.read(args.inputs); index = bindings.read(HERE / 'sources.json')
    need(inputs['epoch'] == 'recovery-001' and inputs['products']['before']['commit'] == bindings.BEFORE
         and inputs['products']['after']['commit'] == bindings.ON, 'Wrong epoch/product roles')
    inputs['_sha256'] = args.inputs_sha256
    inputs['_source_index_sha256'] = args.source_index_sha256
    for key in ('entry_free_bytes', 'between_command_free_bytes'):
        need(type(inputs[key]) is int and inputs[key] > 0, 'Root must freeze operational free-space floors')
    for name in ('driver', 'output', 'control', 'exclusive_lock'):
        p = Path(inputs[name]); need(not p.is_absolute() and '..' not in p.parts, 'Root-relative input required: ' + name)
    driver = root / inputs['driver']
    source(driver, bindings.ON)
    def stable():
        for name, digest in index['files_sha256'].items():
            need(sha(HERE / name) == digest, 'Prepared orchestration source changed: ' + name)
        for name, digest in index['public_source_sha256'].items():
            need(sha(driver / name) == digest, 'Frozen public producer/helper changed: ' + name)
        need(sha(args.inputs) == args.inputs_sha256, 'Runtime inputs changed')
        source(driver, bindings.ON)
    stable()
    freeze_path = root / inputs['freeze']['path']
    need(sha(freeze_path) == inputs['freeze']['sha256'], 'Host/workload freeze changed')
    freeze = bindings.read(freeze_path)
    boot = hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes().strip()).hexdigest()
    need(freeze['epoch'] == 'recovery-001' and boot == freeze['machine']['kernel_boot_sha256'], 'Wrong recovery host boot')
    tool_path = root / inputs['toolchain']['path']
    need(sha(tool_path) == inputs['toolchain']['sha256'], 'Toolchain manifest changed')
    toolchain = bindings.read(tool_path)
    need(toolchain['ready'] is True, 'Actual completed toolchain prerequisite required')
    inputs['_tools'] = toolchain['tools']
    for row in toolchain['tools'].values():
        need(sha(row['path']) == row['invocation_path_sha256'] and sha(row['executable_path']) == row['executable_sha256'], 'Actual tool binary changed')
    dependencies = {}
    for rows in toolchain['actual_dynamic_dependencies_sha256'].values():
        for path, digest in rows.items():
            need(path not in dependencies or dependencies[path] == digest, 'Conflicting tool dependency identity')
            dependencies[path] = digest
    for path, digest in dependencies.items():
        need(sha(path) == digest, 'Actual tool dynamic dependency changed')
    need(Path(sys.executable).resolve() == Path(toolchain['tools']['python']['executable_path']), 'Owner interpreter differs from actual bound tool')
    control = root / inputs['control'] / ('build-' + args.stage)
    output = root / inputs['output'] / args.stage
    lock_path = root / inputs['exclusive_lock']; lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open('a+b') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        need(shutil.disk_usage(root).free >= inputs['entry_free_bytes'], 'Build entry free-space floor not met')
        need(not control.exists() and (args.stage == 'bind-pair' or not output.exists()), 'Fresh control/output required; no silent resume')
        control.mkdir(parents=True)
        record = dict(schema_version=1, task='Perf-01', epoch='recovery-001', stage=args.stage, status='running', started_utc=utc(),
            inputs_sha256=args.inputs_sha256, source_index_sha256=args.source_index_sha256,
            toolchain_sha256=inputs['toolchain']['sha256'], freeze_sha256=inputs['freeze']['sha256'], boot_sha256=boot,
            commands=[], prerequisites={}, source_identities={}, historical_credit_transferred=False, performance_credit_seconds=0)
        save(control / 'execution.json', record)
        try:
            before = after = common = None
            if args.stage != 'before':
                record['prerequisites']['before'], before = completed(root, inputs, 'before', args.before_receipt_sha256)
            if args.stage == 'bind-pair':
                record['prerequisites']['after'], after = completed(root, inputs, 'after', args.after_receipt_sha256)
                record['prerequisites']['common'], common = completed(root, inputs, 'common', args.common_receipt_sha256)
                result = dict(schema_version=1, task='Perf-01', epoch='recovery-001', status='built-and-bound',
                              pairing=bindings.paired(before, after), files_sha256={**before['files_sha256'], **after['files_sha256'], **common['files_sha256']})
            else:
                product = None
                if args.stage in ('before', 'after'):
                    selected = inputs['products'][args.stage]
                    product = root / selected['path']
                    record['source_identities']['product'] = source(product, selected['commit'])
                    record['fresh_bin_obj_absent'] = freshness(product)
                    need(not os.path.lexists(product / 'target'), 'Fresh codec product target is required')
                    for name in index['product_producer_sha256']:
                        need(sha(product / name) == index['product_producer_sha256'][name], 'EA5/ON producer implementation mismatch')
                record['source_identities']['driver'] = source(driver, bindings.ON)
                output.mkdir(parents=True)
                for folder in ('temp', 'dotnet-home'):
                    (output / folder).mkdir()
                environment = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME', 'SSL_CERT_FILE', 'SSL_CERT_DIR', 'HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY') if k in os.environ}
                environment.update(toolchain['environment'])
                environment.update(inputs['build_environment'])
                environment.update(NUGET_PACKAGES=str(output / 'producer-cache'), TMPDIR=str(output / 'temp'),
                                   DOTNET_CLI_HOME=str(output / 'dotnet-home'), PYTHONDONTWRITEBYTECODE='1')
                rows = plan(args.stage, inputs, root, toolchain['tools'])
                record['planned_commands'] = rows
                record['environment'] = {k: v for k, v in environment.items() if k not in ('HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY')}
                save(control / 'execution.json', record)
                enable_subreaper()
                tree_type = public_tree(driver)
                async def execute():
                    loop = asyncio.get_running_loop()
                    task = asyncio.current_task()
                    for sig in (signal.SIGTERM, signal.SIGINT):
                        loop.add_signal_handler(sig, task.cancel)
                    for row in rows:
                        stable()
                        if product is not None:
                            source(product, selected['commit'])
                        need(shutil.disk_usage(root).free >= inputs['between_command_free_bytes'], 'Between-producer free-space floor not met')
                        if row['label'] == 'packages':
                            record['immediately_before_packages_bin_obj_absent'] = freshness(product)
                            save(control / 'execution.json', record)
                        env = dict(environment, **row['environment_overrides'])
                        actual = await command(row, env, control / row['label'], tree_type)
                        record['commands'].append(actual)
                        save(control / 'execution.json', record)
                asyncio.run(execute())
                stable()
                if product is not None:
                    source(product, selected['commit'])
                    result = bindings.role(output, product, selected['commit'], selected['version'])
                    result['product_tree'] = record['source_identities']['product']['tree']
                else:
                    result = bindings.common(output, root / inputs['output'] / 'before', before)
            result.update(inputs_sha256=args.inputs_sha256, toolchain_sha256=inputs['toolchain']['sha256'],
                          freeze_sha256=inputs['freeze']['sha256'], source_index_sha256=args.source_index_sha256)
            save(control / 'binding.json', result)
            record.update(status='completed', binding_sha256=sha(control / 'binding.json'))
        except BaseException as error:
            record.update(status='failed', failure=type(error).__name__ + ': ' + str(error))
            raise
        finally:
            record['ended_utc'] = utc()
            save(control / 'execution.json', record)
    print(json.dumps({'stage': args.stage, 'status': record['status'], 'execution': str(control / 'execution.json'), 'sha256': sha(control / 'execution.json')}))


if __name__ == '__main__':
    main()
