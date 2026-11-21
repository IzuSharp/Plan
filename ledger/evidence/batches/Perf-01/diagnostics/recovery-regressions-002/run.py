#!/usr/bin/env python3
"""Finite B17/B15/B19/B20 selected-native regression subsets; no timing credit."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'recovery-build-001'
ORIGINAL_INDEX = 'c7526f08d3c50c6d58f7336adae6ebab5fb82b606cce140108a48f6b54b3d0ab'
BEFORE = 'ea5fa528035d025bd7a28698ee7c71194432236c'
DRIVER = '2e3995df8d86583ee9443348276ca8d918056bfc'
DESIGN = 'c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9'
PYTHON_VERSIONS = {'anyio': '4.14.2', 'certifi': '2026.10.19', 'h11': '0.16.0', 'h2': '4.4.1',
                   'hpack': '4.2.0', 'httpcore': '1.0.9', 'httpx': '0.28.1', 'hyperframe': '6.1.0',
                   'idna': '3.18', 'typing_extensions': '4.16.0'}


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def relative(root, value):
    path = Path(value)
    need(not path.is_absolute() and '..' not in path.parts, 'Task-root-relative path required')
    result = (root / path).resolve()
    need(result.is_relative_to(root), 'Path escapes task root')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'build-inputs', 'build-source-index'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('build-inputs-sha256', 'build-source-index-sha256', 'source-index-sha256',
                 'before-receipt-sha256', 'after-receipt-sha256', 'selected-final-sha', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    need(sys.version_info[:3] == (3, 12, 14) and platform.system() == 'Linux' and platform.machine() == 'x86_64', 'Pinned Python/Linux x64 required')
    need(os.sched_getaffinity(0) == {8}, 'Finite owner must use CPU8')
    need(re.fullmatch('[0-9a-f]{40}', args.selected_final_sha), 'Explicit full selected product commit required')
    root = args.root.resolve(strict=True)
    for path in (args.build_inputs, args.build_source_index):
        need(path.is_absolute() and path.resolve() == path and path.is_relative_to(root), 'Canonical task-local input required')
    # Read only the small input map needed to locate the existing orchestration
    # lock. Acquire it before tool, source, receipt or artifact admission hashes.
    need(sha(args.build_inputs) == args.build_inputs_sha256, 'Build input identity differs')
    inputs = read(args.build_inputs)
    lock_path = relative(root, inputs['exclusive_lock'])
    need(lock_path.is_file(), 'Existing orchestration timing lock required')
    with lock_path.open('r+b') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        need(sha(HERE / 'sources.json') == args.source_index_sha256, 'Regression source index differs')
        index = read(HERE / 'sources.json')
        need(sha(ORIGINAL / 'sources.json') == ORIGINAL_INDEX, 'Original c752 source index differs')
        for base, mapping in ((HERE, index['files_sha256']), (ORIGINAL, index['reused_control_sha256'])):
            for name, digest in mapping.items():
                need(sha(base / name) == digest, 'Control source changed: ' + name)
        sys.path.insert(0, str(ORIGINAL))
        spec = importlib.util.spec_from_file_location('perf01_original_build', ORIGINAL / 'build.py')
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        owner, bindings = sys.modules['owner'], build.bindings
        from recipes import plan
        from results import binary_inputs, collect

        output = relative(root, args.output)
        driver, design = (relative(root, inputs[key]) for key in ('driver', 'design'))
        product = relative(root, inputs['products']['after']['path'])
        need(not any(output.is_relative_to(path) for path in (product, driver, design)), 'Output must be outside product/driver/Design checkouts')
        need(not output.exists(), 'Fresh regression output required; preserve prior attempts')
        output.mkdir(parents=True)
        control = output / 'control'
        control.mkdir()
        record = dict(task='Perf-01', epoch='recovery-002', status='running', started_utc=owner.utc(),
                      selected_final_commit=args.selected_final_sha, owner_affinity=[8], timing_lock=str(lock_path),
                      build_inputs=str(args.build_inputs), build_inputs_sha256=args.build_inputs_sha256,
                      build_source_index=str(args.build_source_index), build_source_index_sha256=args.build_source_index_sha256,
                      source_index_sha256=args.source_index_sha256, commands=[], prerequisites={}, binary_inventories=[],
                      historical_credit_transferred=False, performance_credit_seconds=0)
        owner.save(control / 'execution.json', record)
        try:
            need(inputs['task'] == 'Perf-01' and inputs['epoch'] == 'recovery-002'
                 and inputs['products']['before']['commit'] == BEFORE and inputs['products']['after']['commit'] is None,
                 'Immutable epoch-002 build inputs required')
            need(sha(args.build_source_index) == args.build_source_index_sha256, 'Original build caller source index differs')
            build_index, original_index = read(args.build_source_index), read(ORIGINAL / 'sources.json')
            need(build_index['epoch'] == 'recovery-002' and build_index['baseline_commit'] == BEFORE
                 and build_index['driver_commit'] == DRIVER and build_index['reused_control_sha256'] == index['reused_control_sha256'],
                 'Original build caller control/source roles differ')
            b = bindings.Binding()
            b.pin(args.build_inputs, args.build_inputs_sha256)
            b.pin(args.build_source_index, args.build_source_index_sha256)
            b.pin(HERE / 'sources.json', args.source_index_sha256)
            b.mapping(index['files_sha256'], HERE)
            b.mapping(index['reused_control_sha256'], ORIGINAL)
            b.mapping(build_index['files_sha256'], args.build_source_index.parent)
            for key in ('freeze', 'toolchain', 'python_dependencies'):
                descriptor = inputs[key]
                b.pin(relative(root, descriptor['path']), descriptor['sha256'])
            freeze = read(relative(root, inputs['freeze']['path']))
            toolchain = read(relative(root, inputs['toolchain']['path']))
            dependencies = read(relative(root, inputs['python_dependencies']['path']))
            boot = hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes().strip()).hexdigest()
            need(freeze['epoch'] == 'recovery-002' and freeze['baseline_product_commit'] == BEFORE
                 and freeze['driver_checkout_commit'] == DRIVER and freeze['design_commit'] == DESIGN
                 and freeze['machine']['kernel_boot_sha256'] == boot
                 and freeze['selected_final_runtime_commit'] in (None, args.selected_final_sha), 'Frozen source roles or boot differ')
            tools = toolchain['tools']
            need(toolchain['ready'] is True and {'python', 'dotnet', 'postgres', 'clang19'} <= tools.keys(), 'Complete admitted toolchain required')
            for row in tools.values():
                need(sha(row['path']) == row['invocation_path_sha256'] and sha(row['executable_path']) == row['executable_sha256'], 'Tool executable changed')
            for mapping in toolchain['actual_dynamic_dependencies_sha256'].values():
                b.mapping(mapping)
            need(Path(sys.executable).resolve() == Path(tools['python']['executable_path']), 'Owner Python differs')
            need({k: v['version'] for k, v in dependencies['metadata'].items()} == PYTHON_VERSIONS, 'Python dependency versions differ')
            python_path = Path(dependencies['environment']['PYTHONPATH'])
            need(python_path.resolve().is_relative_to(root), 'Task-local Python dependencies required')
            b.mapping(dependencies['installed_files_sha256'], python_path)
            b.mapping(dependencies.get('runtime_files_sha256', {}))
            b.mapping(original_index['public_source_sha256'], driver)
            b.mapping(original_index['product_producer_sha256'], product)
            b.mapping(index['recipe_source_sha256'], product)
            b.mapping(freeze['product_locks_sha256'], product)
            record['source_identities'] = dict(product=build.source(product, args.selected_final_sha),
                                               driver=build.source(driver, DRIVER), design=build.source(design, DESIGN))
            prefixes = ('src/Server.', 'src/Interop.', 'src/NativeWeave.Core/', 'src/Protocols.Mcp/', 'src/Packaging.',
                        'tests/Server.Native/', 'tests/Server.Application/', 'tests/Protocols.Mcp/', 'tests/Server.Diagnostics/',
                        'samples/api/server-application/', 'samples/api/protocols-mcp/', 'samples/api/server-diagnostics/')
            names = subprocess.check_output(['git', '-C', str(product), 'ls-files', '-z'], timeout=30).decode().split('\0')
            source_files = {name: sha(product / name) for name in names if name and (name.startswith(prefixes)
                            or name in ('Cargo.lock', 'Cargo.toml', 'global.json', 'Directory.Build.props', 'Directory.Build.targets', 'NuGet.Config', 'rust-toolchain.toml'))}
            b.mapping(source_files, product)
            # This is the BUILD caller index, deliberately not this runner's index.
            inputs['_sha256'], inputs['_source_index_sha256'], inputs['_tools'] = args.build_inputs_sha256, args.build_source_index_sha256, tools
            for role in ('before', 'after'):
                receipt, bound = build.completed(root, inputs, role, getattr(args, role + '_receipt_sha256'))
                need(bound['product_commit'] == (BEFORE if role == 'before' else args.selected_final_sha), 'Build role product differs')
                record['prerequisites'][role] = receipt
                if role == 'after':
                    after = bound
            assets = [asset for asset in after['native_assets'] if asset['engineId'] == 'server']
            need(len(assets) == 1, 'Exactly one bound Server native asset required')
            native = assets[0]
            b.pin(native['path'], native['sha256'])
            record.update(native_asset=native, boot_sha256=boot, source_files_sha256=source_files,
                          toolchain_sha256=inputs['toolchain']['sha256'], freeze_sha256=inputs['freeze']['sha256'])
            for name in ('entry_free_bytes', 'between_command_free_bytes'):
                need(type(inputs[name]) is int and inputs[name] > 0, 'Positive frozen disk floor required')
            need(shutil.disk_usage(root).free >= inputs['entry_free_bytes'], 'Entry free-space floor not met')
            for name in ('temp', 'dotnet-home', 'inventories'):
                (output / name).mkdir()
            environment = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME', 'SSL_CERT_FILE', 'SSL_CERT_DIR', 'HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY') if k in os.environ}
            environment.update(toolchain['environment'])
            environment.update(inputs['build_environment'])
            environment.update(NUGET_PACKAGES=str(output / 'producer-cache'), TMPDIR=str(output / 'temp'),
                               DOTNET_CLI_HOME=str(output / 'dotnet-home'), PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(python_path))
            # Original verifiers invoke python3/dotnet by name inside the finite owner.
            environment['PATH'] = str(Path(tools['python']['path']).parent) + os.pathsep + environment['PATH']
            for name, key in (('python3', 'python'), ('dotnet', 'dotnet')):
                need(Path(shutil.which(name, path=environment['PATH']) or '').resolve() == Path(tools[key]['executable_path']), 'Nested executable differs: ' + name)
            rows, binaries = plan(product, output, native, tools, design)
            need(len(rows) == 29 and len({row['label'] for row in rows}) == 29, 'Selected command population differs')
            record['planned_commands'] = rows
            record['environment'] = {k: v for k, v in environment.items() if k not in ('HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY')}
            owner.save(output / 'admission.json', dict(files_sha256=b.files, source_identities=record['source_identities'], prerequisites=record['prerequisites']))
            owner.save(control / 'execution.json', record)
            owner.enable_subreaper()
            tree_type = owner.public_tree(driver)

            def stable():
                # Recheck immutable source/admission inputs and the selected asset;
                # do not re-hash whole prior build outputs on every fixture command.
                for path, digest in b.files.items():
                    need(sha(path) == digest, 'Admitted file changed: ' + path)
                for path, commit in ((product, args.selected_final_sha), (driver, DRIVER), (design, DESIGN)):
                    build.source(path, commit)

            async def execute():
                loop, task = asyncio.get_running_loop(), asyncio.current_task()
                for sig in (signal.SIGINT, signal.SIGTERM):
                    loop.add_signal_handler(sig, task.cancel)
                for row in rows:
                    stable()
                    need(shutil.disk_usage(root).free >= inputs['between_command_free_bytes'], 'Between-command free-space floor not met')
                    label = row['label']
                    if label in binaries:
                        before = binary_inputs(native=native, **binaries[label])
                        inventory = output / 'inventories' / (label + '.json')
                        owner.save(inventory, dict(label=label, phase='immediately-before-execution', files_sha256=before))
                        record['binary_inventories'].append(str(inventory))
                    record['active_command'] = label
                    owner.save(control / 'execution.json', record)
                    actual = await owner.command(row, dict(environment, **row['environment_overrides']), control / label, tree_type)
                    record['commands'].append(actual)
                    if label in binaries:
                        need(binary_inputs(native=native, **binaries[label]) == before, 'Fixture changed its executable/native inputs')
                        owner.save(inventory, dict(label=label, phase='immediately-before-execution', files_sha256=before,
                                                   identical_after=True, rechecked_after_utc=owner.utc()))
                    record.pop('active_command')
                    owner.save(control / 'execution.json', record)

            asyncio.run(execute())
            stable()
            result = collect(output, product, args.selected_final_sha, native, record['commands'], record['binary_inventories'])
            result.update(build_inputs_sha256=args.build_inputs_sha256, build_source_index_sha256=args.build_source_index_sha256,
                          source_index_sha256=args.source_index_sha256, prerequisites=record['prerequisites'],
                          admission_sha256=sha(output / 'admission.json'))
            owner.save(output / 'result.json', result)
            record.update(status='completed', result=str(output / 'result.json'), result_sha256=sha(output / 'result.json'))
        except BaseException as error:
            record.update(status='failed', failure=type(error).__name__ + ': ' + str(error))
            if record.get('active_command'):
                path = control / record['active_command'] / 'receipt.json'
                if path.is_file():
                    record['failed_command_receipt'] = dict(path=str(path), sha256=sha(path))
            raise
        finally:
            record['ended_utc'] = owner.utc()
            owner.save(control / 'execution.json', record)
    print(json.dumps(dict(status=record['status'], execution=str(control / 'execution.json'), sha256=sha(control / 'execution.json'))))


if __name__ == '__main__':
    main()
