#!/usr/bin/env python3
"""Epoch-002 build/B18 caller over public producers and the unchanged c752 owner.

This entry point does not run performance workloads or award measurement credit.
The final product commit is an explicit invocation input, not the common driver.
"""
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
import sys

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'recovery-build-001'
BEFORE = 'ea5fa528035d025bd7a28698ee7c71194432236c'
DRIVER = '2e3995df8d86583ee9443348276ca8d918056bfc'
DESIGN = 'c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9'
PYTHON_VERSIONS = {
    'anyio': '4.14.2', 'certifi': '2026.10.19', 'h11': '0.16.0',
    'h2': '4.4.1', 'hpack': '4.2.0', 'httpcore': '1.0.9',
    'httpx': '0.28.1', 'hyperframe': '6.1.0', 'idna': '3.18',
    'typing_extensions': '4.16.0',
}


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
    need(not path.is_absolute() and '..' not in path.parts, 'Root-relative input required: ' + value)
    result = (root / path).resolve()
    need(result.is_relative_to(root), 'Input escapes task root: ' + value)
    return result


def pinned(root, descriptor):
    path = relative(root, descriptor['path'])
    need(sha(path) == descriptor['sha256'], 'Input identity changed: ' + descriptor['path'])
    return path, read(path)


def paired(before, after, selected):
    # Original bindings.paired equality rule; only the after commit is parameterized.
    need(before['product_commit'] == BEFORE and after['product_commit'] == selected, 'Wrong actual paired product commits')
    need(set(before['resolved_packages']) == set(after['resolved_packages']), 'Consumer populations differ')
    count = 0
    fields = ('archive_sha256', 'archive_raw_sha512', 'nuget_content_hash_sha512', 'signature_entry_present', 'source')
    for consumer, rows in before['resolved_packages'].items():
        old = {k: {n: v[n] for n in fields} for k, v in rows.items() if not v['nativeweave']}
        new = {k: {n: v[n] for n in fields} for k, v in after['resolved_packages'][consumer].items() if not v['nativeweave']}
        need(old == new, 'External restored archive/content population changed: ' + consumer)
        count += len(old)
    return dict(external_consumer_package_pairs=count, exact_external_archive_and_content_equality=True,
                historical_evidence_transferred=False, performance_credit_seconds=0)


def functional_plan(product, selected, output, bound, tools, design):
    assets = [x for x in bound['native_assets'] if x['engineId'] == 'server']
    need(len(assets) == 1, 'Exactly one role-bound Server asset required')
    native = assets[0]
    need(sha(native['path']) == native['sha256'], 'Role-bound Server asset changed')
    python = tools['python']['path']
    rows = [dict(label='native-component', argv=[python, str(product / 'native/protocols/grpc/verify-native.py'),
                '--output', str(output / 'native-component')], cwd=str(product), timeout_seconds=5400, environment_overrides={}),
            dict(label='assembled-b18', argv=[python, str(product / 'tests/Protocols.Grpc/verify.py'),
                '--output', str(output / 'assembled'), '--design', str(design),
                '--sdk', str(Path(tools['dotnet']['executable_path']).parent),
                '--native', native['path'], '--expected-native-sha256', native['sha256'],
                '--native-source-commit', selected,
                '--native-component-receipt', str(output / 'native-component/result.json')],
                cwd=str(product), timeout_seconds=5400, environment_overrides={})]
    return rows, native


def functional_binding(output, product, selected, native, bindings):
    b = bindings.Binding()
    component = b.document(output / 'native-component/result.json')
    assembled = b.document(output / 'assembled/result.json')
    need(component['task'] == assembled['task'] == 'B18'
         and component['platform'] == assembled['platform'] == 'linux-x64'
         and component['status'] == assembled['status'] == 'passed', 'Original B18 result did not pass')
    need(component['commit'] == assembled['source_commit'] == assembled['native_source_commit'] == selected
         and assembled['source_clean'] is True, 'B18 source differs from selected clean product')
    need(assembled['native']['sha256'] == native['sha256']
         and assembled['accepted_native_component']['sha256'] == sha(output / 'native-component/result.json'),
         'B18 did not use this role asset/component receipt')
    b.pin(native['path'], native['sha256'])
    b.pin(assembled['native']['path'], native['sha256'])
    b.pin(product / component['native']['path'], component['native']['sha256'])
    b.mapping(component['source_sha256'], product)
    b.mapping(assembled['source_sha256'], product)
    for row in component['commands']:
        need(row['exit_code'] == 0, 'Failed native component command')
        b.pin(output / 'native-component' / row['log'], row['sha256'])
    commands = b.document(output / 'assembled/commands.json')
    need(sha(output / 'assembled/commands.json') == assembled['command_receipt_sha256']
         and commands == assembled['commands'], 'Assembled command receipt differs')
    for row in commands:
        need(row['exit_code'] == 0, 'Failed assembled B18 command')
        b.pin(output / 'assembled' / row['log'], row['log_sha256'])
    for mode in ('jit', 'aot'):
        inventory = output / 'assembled' / ('actual-' + mode + '-inputs.json')
        b.pin(inventory, assembled[mode]['binary_inventory_sha256'])
        b.mapping(b.document(inventory), output / 'assembled' / mode)
    package = b.document(assembled['package']['path'])
    need(sha(assembled['package']['path']) == assembled['package']['sha256']
         and package['native_sha256'] == native['sha256']
         and package['native_source_commit'] == selected, 'Ordinary B18 package asset differs')
    package_root = Path(assembled['package']['path']).parent
    package_commands = package_root / 'commands.json'
    b.pin(package_commands, package['command_receipt_sha256'])
    for row in b.document(package_commands):
        need(row['exit_code'] == 0, 'Failed ordinary B18 package command')
        b.pin(package_root / 'logs' / (row['label'] + '.log'), row['log_sha256'])
    for row in package['packages'].values():
        b.pin(row['path'], row['sha256'])
    # The original assembled verifier validates package command logs, snapshots,
    # exact native selection and the ordinary edited JIT/AOT consumers.
    return dict(schema_version=1, task='Perf-01', epoch='recovery-002', status='functional-bound',
                product_commit=selected, native_asset=native, files_sha256=b.files,
                original_component_result=str(output / 'native-component/result.json'),
                original_assembled_result=str(output / 'assembled/result.json'),
                original_package_summary=assembled['package'], functional_scope='B18 only',
                other_changed_module_regressions='Separate original module gates remain required as applicable',
                performance_credit_seconds=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--inputs-sha256', required=True)
    parser.add_argument('--source-index-sha256', required=True)
    parser.add_argument('--stage', choices=('before', 'after', 'common', 'bind-pair', 'functional-before', 'functional-after'), required=True)
    parser.add_argument('--selected-final-sha')
    for role in ('before', 'after', 'common'):
        parser.add_argument('--' + role + '-receipt-sha256')
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    need(sys.version_info[:3] == (3, 12, 14) and platform.system() == 'Linux' and platform.machine() == 'x86_64', 'Pinned Python/Linux x64 required')
    need(os.sched_getaffinity(0) == {8}, 'Outer owner must use CPU8')
    root = args.root.resolve(strict=True)
    need(sha(args.inputs) == args.inputs_sha256 and sha(HERE / 'sources.json') == args.source_index_sha256, 'Input/source index mismatch')
    inputs, index = read(args.inputs), read(HERE / 'sources.json')
    need(inputs['epoch'] == 'recovery-002' and inputs['products']['before']['commit'] == BEFORE
         and inputs['products']['after']['commit'] is None, 'Use immutable epoch-002 inputs and an explicit final-SHA argument')
    if args.stage in ('after', 'bind-pair', 'functional-after'):
        need(isinstance(args.selected_final_sha, str) and re.fullmatch('[0-9a-f]{40}', args.selected_final_sha), 'Explicit full selected final commit required')
    paths = {key: relative(root, inputs[key]) for key in ('driver', 'design', 'output', 'control', 'exclusive_lock')}
    for role in ('before', 'after'):
        relative(root, inputs['products'][role]['path'])
    for key in ('entry_free_bytes', 'between_command_free_bytes'):
        need(type(inputs[key]) is int and inputs[key] > 0, 'Positive frozen disk floor required')
    for name, digest in index['files_sha256'].items():
        need(sha(HERE / name) == digest, 'Caller source changed: ' + name)
    for name, digest in index['reused_control_sha256'].items():
        need(sha(ORIGINAL / name) == digest, 'Original control source changed: ' + name)
    # No producer or workload module is imported here. These three unchanged
    # control modules are loaded only after their source hashes have matched.
    sys.path.insert(0, str(ORIGINAL))
    spec = importlib.util.spec_from_file_location('perf01_original_build', ORIGINAL / 'build.py')
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    bindings = build.bindings
    owner = sys.modules['owner']
    original_index = read(ORIGINAL / 'sources.json')
    inputs['_sha256'], inputs['_source_index_sha256'] = args.inputs_sha256, args.source_index_sha256
    _, freeze = pinned(root, inputs['freeze'])
    boot = hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes().strip()).hexdigest()
    need(freeze['epoch'] == 'recovery-002' and freeze['baseline_product_commit'] == BEFORE
         and freeze['driver_checkout_commit'] == DRIVER and freeze['design_commit'] == DESIGN
         and boot == freeze['machine']['kernel_boot_sha256'], 'Wrong epoch, source roles or host boot')
    need(freeze['selected_final_runtime_commit'] in (None, args.selected_final_sha), 'Selected final commit conflicts with freeze')
    _, toolchain = pinned(root, inputs['toolchain'])
    need(toolchain['ready'] is True and {'python', 'dotnet', 'postgres', 'clang19'} <= toolchain['tools'].keys(), 'Complete restored toolchain required')
    inputs['_tools'] = toolchain['tools']
    for row in toolchain['tools'].values():
        need(sha(row['path']) == row['invocation_path_sha256'] and sha(row['executable_path']) == row['executable_sha256'], 'Actual tool binary changed')
    for rows in toolchain['actual_dynamic_dependencies_sha256'].values():
        for path, digest in rows.items():
            need(sha(path) == digest, 'Actual tool dependency changed')
    need(Path(sys.executable).resolve() == Path(toolchain['tools']['python']['executable_path']), 'Owner interpreter differs from bound Python')
    _, dependencies = pinned(root, inputs['python_dependencies'])
    need({k: v['version'] for k, v in dependencies['metadata'].items()} == PYTHON_VERSIONS, 'Python dependency versions differ')
    python_path = Path(dependencies['environment']['PYTHONPATH'])
    need(python_path.resolve().is_relative_to(root), 'Python bundle must be task-local')
    def stable():
        need(sha(args.inputs) == args.inputs_sha256 and sha(HERE / 'sources.json') == args.source_index_sha256, 'Runtime admission source/input changed')
        pinned(root, inputs['freeze']); pinned(root, inputs['toolchain']); pinned(root, inputs['python_dependencies'])
        for base, hashes in ((HERE, index['files_sha256']), (ORIGINAL, index['reused_control_sha256']),
                             (paths['driver'], original_index['public_source_sha256'])):
            for name, digest in hashes.items():
                need(sha(base / name) == digest, 'Source changed: ' + name)
        for name, digest in dependencies['installed_files_sha256'].items():
            need(sha(python_path / name) == digest, 'Python bundle file changed: ' + name)
        for name, digest in dependencies.get('runtime_files_sha256', {}).items():
            need(sha(name) == digest, 'Base Python dependency changed: ' + name)
        build.source(paths['driver'], DRIVER)
        build.source(paths['design'], DESIGN)
    stable()
    functional = args.stage.startswith('functional-')
    role = args.stage.removeprefix('functional-')
    selected = BEFORE if role == 'before' else args.selected_final_sha
    control = paths['control'] / (args.stage if functional else 'build-' + args.stage)
    output = paths['output'] / args.stage
    paths['exclusive_lock'].parent.mkdir(parents=True, exist_ok=True)
    with paths['exclusive_lock'].open('a+b') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        need(shutil.disk_usage(root).free >= inputs['entry_free_bytes'], 'Entry free-space floor not met')
        need(not control.exists() and (args.stage == 'bind-pair' or not output.exists()), 'Fresh output/control required; no silent resume')
        control.mkdir(parents=True)
        record = dict(schema_version=1, task='Perf-01', epoch='recovery-002', stage=args.stage, status='running', started_utc=owner.utc(),
                      inputs_sha256=args.inputs_sha256, source_index_sha256=args.source_index_sha256,
                      toolchain_sha256=inputs['toolchain']['sha256'], freeze_sha256=inputs['freeze']['sha256'], boot_sha256=boot,
                      selected_final_commit=args.selected_final_sha, commands=[], prerequisites={}, source_identities={},
                      historical_credit_transferred=False, performance_credit_seconds=0)
        owner.save(control / 'execution.json', record)
        try:
            before = after = common = None
            if args.stage != 'before':
                record['prerequisites']['before'], before = build.completed(root, inputs, 'before', args.before_receipt_sha256)
                need(before['product_commit'] == BEFORE, 'Before prerequisite is not EA5')
            if args.stage in ('bind-pair', 'functional-after'):
                record['prerequisites']['after'], after = build.completed(root, inputs, 'after', args.after_receipt_sha256)
                need(after['product_commit'] == args.selected_final_sha, 'After prerequisite differs from explicit selected SHA')
            if args.stage == 'bind-pair':
                record['prerequisites']['common'], common = build.completed(root, inputs, 'common', args.common_receipt_sha256)
                result = dict(schema_version=1, task='Perf-01', epoch='recovery-002', status='built-and-bound',
                              pairing=paired(before, after, args.selected_final_sha),
                              files_sha256={**before['files_sha256'], **after['files_sha256'], **common['files_sha256']},
                              performance_credit_seconds=0)
            else:
                product = relative(root, inputs['products'][role]['path']) if role in ('before', 'after') else None
                if product is not None:
                    record['source_identities']['product'] = build.source(product, selected)
                    for name, digest in freeze['product_locks_sha256'].items():
                        need(sha(product / name) == digest, 'Locked product dependency input changed: ' + name)
                    for name, digest in original_index['product_producer_sha256'].items():
                        need(sha(product / name) == digest, 'Original product producer changed: ' + name)
                    if not functional:
                        record['fresh_bin_obj_absent'] = build.freshness(product)
                        need(not os.path.lexists(product / 'target'), 'Fresh product target required for role build')
                record['source_identities']['driver'] = build.source(paths['driver'], DRIVER)
                output.mkdir(parents=True)
                for folder in ('temp', 'dotnet-home'):
                    (output / folder).mkdir()
                environment = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME', 'SSL_CERT_FILE', 'SSL_CERT_DIR', 'HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY') if k in os.environ}
                environment.update(toolchain['environment'])
                environment.update(inputs['build_environment'])
                environment.update(NUGET_PACKAGES=str(output / 'producer-cache'), TMPDIR=str(output / 'temp'),
                                   DOTNET_CLI_HOME=str(output / 'dotnet-home'), PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(python_path))
                if functional:
                    # The original native component verifier reads product/target;
                    # its own cargo commands must therefore use that directory.
                    environment.pop('CARGO_TARGET_DIR', None)
                    rows, native = functional_plan(product, selected, output, before if role == 'before' else after,
                                                   toolchain['tools'], paths['design'])
                else:
                    rows = build.plan(args.stage, inputs, root, toolchain['tools'])
                record['planned_commands'] = rows
                record['environment'] = {k: v for k, v in environment.items() if k not in ('HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY')}
                owner.save(control / 'execution.json', record)
                owner.enable_subreaper()
                tree_type = owner.public_tree(paths['driver'])
                async def execute():
                    loop, task = asyncio.get_running_loop(), asyncio.current_task()
                    for sig in (signal.SIGTERM, signal.SIGINT):
                        loop.add_signal_handler(sig, task.cancel)
                    for row in rows:
                        stable()
                        if product is not None:
                            build.source(product, selected)
                        need(shutil.disk_usage(root).free >= inputs['between_command_free_bytes'], 'Between-command free-space floor not met')
                        if row['label'] == 'packages':
                            record['immediately_before_packages_bin_obj_absent'] = build.freshness(product)
                        actual = await owner.command(row, dict(environment, **row['environment_overrides']), control / row['label'], tree_type)
                        record['commands'].append(actual)
                        owner.save(control / 'execution.json', record)
                asyncio.run(execute())
                stable()
                if product is not None:
                    build.source(product, selected)
                    result = functional_binding(output, product, selected, native, bindings) if functional else bindings.role(output, product, selected, inputs['products'][role]['version'])
                    result['product_tree'] = record['source_identities']['product']['tree']
                else:
                    result = bindings.common(output, paths['output'] / 'before', before)
                if not functional:
                    result['reader_schema_epoch'] = result.pop('epoch')
                    result['epoch'] = 'recovery-002'
            result.update(inputs_sha256=args.inputs_sha256, toolchain_sha256=inputs['toolchain']['sha256'],
                          freeze_sha256=inputs['freeze']['sha256'], source_index_sha256=args.source_index_sha256)
            owner.save(control / 'binding.json', result)
            record.update(status='completed', binding_sha256=sha(control / 'binding.json'))
        except BaseException as error:
            record.update(status='failed', failure=type(error).__name__ + ': ' + str(error))
            raise
        finally:
            record['ended_utc'] = owner.utc()
            owner.save(control / 'execution.json', record)
    print(json.dumps(dict(stage=args.stage, status=record['status'], execution=str(control / 'execution.json'), sha256=sha(control / 'execution.json'))))


if __name__ == '__main__':
    main()
