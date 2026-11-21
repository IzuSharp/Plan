#!/usr/bin/env python3
"""Original 29 selected-native Server commands, using actual final-role admission."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent
MEASUREMENT = HERE.parent / 'recovery-measure-002'
PREVIOUS = HERE.parent / 'recovery-regressions-002'
ORIGINAL = HERE.parent / 'recovery-build-001'
DESIGN = 'c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9'


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def confined(root, value):
    path = Path(value)
    need(not path.is_absolute() and '..' not in path.parts, 'Task-root-relative path required')
    result = (root / path).resolve()
    need(result.is_relative_to(root), 'Path escapes task root')
    return result


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'admission', 'final-binding'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('admission-sha256', 'final-binding-sha256',
                 'measurement-source-index-sha256', 'source-index-sha256', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    need(os.sched_getaffinity(0) == {8}, 'Finite owner must use CPU8')
    root = args.root.resolve(strict=True)
    for path in (args.admission, args.final_binding):
        need(path.is_absolute() and path.resolve() == path and path.is_relative_to(root),
             'Canonical task-local admission/final binding required')
    # Only read the small maps required to locate the existing reservation.
    # No context import, producer hashing or fixture work precedes this lock.
    need(sha(args.admission) == args.admission_sha256, 'Immutable baseline admission changed')
    admission = read(args.admission)
    build_input = confined(root, admission['build_inputs']['path'])
    need(sha(build_input) == admission['build_inputs']['sha256'], 'Baseline build input changed')
    lock_path = confined(root, read(build_input)['exclusive_lock'])
    need(lock_path.is_file(), 'Existing orchestration timing lock required')
    with lock_path.open('r+b') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        need(sha(HERE / 'sources.json') == args.source_index_sha256, 'Regression source index differs')
        index = read(HERE / 'sources.json')
        for base, mapping in ((HERE, index['files_sha256']),
                              (PREVIOUS, index['reused_regression_sha256']),
                              (ORIGINAL, index['reused_control_sha256'])):
            for name, digest in mapping.items():
                need(sha(confined(base, name)) == digest, 'Reviewed source changed: ' + name)
        need(sha(MEASUREMENT / 'measurement-sources.json') == args.measurement_source_index_sha256
             == index['measurement_source_index_sha256'], 'Reviewed final-role admission differs')
        measured = read(MEASUREMENT / 'measurement-sources.json')
        need(sha(MEASUREMENT / 'admission.py') == measured['files_sha256']['admission.py'],
             'Context source changed before import')
        need(sha(args.final_binding) == args.final_binding_sha256, 'Final binding identity differs')
        final = read(args.final_binding)
        need(final['after_build_source_index']['sha256'] == index['after_build_source_index_sha256']
             and 'after_build_inputs' in final, 'Actual fresh-after producer descriptors required')
        context_module = module('perf01_regression003_admission', MEASUREMENT / 'admission.py')
        ctx = context_module.Context(root, args.admission, args.admission_sha256,
                                     args.measurement_source_index_sha256,
                                     args.final_binding, args.final_binding_sha256)
        need(ctx.reservation == lock_path and ctx.after_rebuild
             and ctx.selected == index['recipe_reference_commit'], 'Reviewed final product/reservation differs')
        owner, product = ctx.owner, ctx.products['after']
        inputs, tools = ctx.role_inputs['after'], ctx.toolchain['tools']
        design = confined(root, inputs['design'])
        ctx.pin(HERE / 'sources.json', args.source_index_sha256)
        for base, mapping in ((HERE, index['files_sha256']),
                              (PREVIOUS, index['reused_regression_sha256']),
                              (ORIGINAL, index['reused_control_sha256']),
                              (product, index['recipe_source_sha256'])):
            for name, digest in mapping.items():
                ctx.pin(confined(base, name), digest)
        recipes = module('perf01_regression003_original_recipes', PREVIOUS / 'recipes.py')
        results = module('perf01_regression003_results', HERE / 'results.py')
        assets = [asset for asset in ctx.built['after']['native_assets'] if asset['engineId'] == 'server']
        need(len(assets) == 1, 'Exactly one actual after-bound Server asset required')
        native = assets[0]
        ctx.pin(native['path'], native['sha256'])
        output = confined(root, args.output)
        protected = [*ctx.products.values(), ctx.driver, design, ctx.plan, HERE.parents[5],
                     *ctx.build_roots.values(), ctx.output,
                     *(confined(root, value['control']) for value in ctx.role_inputs.values())]
        need(all(not output.is_relative_to(path) and not path.is_relative_to(output) for path in protected),
             'Fresh regression output overlaps an admitted checkout/build/measurement destination')
        need(not output.exists(), 'Fresh regression output required; preserve prior attempts')
        output.mkdir(parents=True)
        control = output / 'control'
        control.mkdir()
        record = dict(task='Perf-01', epoch='recovery-002', kind='final-selected-native-server-regressions',
                      status='running', started_utc=owner.utc(), selected_final_commit=ctx.selected,
                      owner_affinity=[8], timing_lock=str(lock_path), source_index_sha256=args.source_index_sha256,
                      admission=dict(path=str(args.admission), sha256=args.admission_sha256),
                      measurement_source_index_sha256=ctx.index_sha256, final_binding=ctx.final_binding,
                      producer_inputs=dict(before=ctx.value['build_inputs'], common=ctx.value['build_inputs'],
                                           after=final['after_build_inputs']),
                      producer_source_indices=dict(before=ctx.value['build_source_index'],
                                                   common=ctx.value['build_source_index'],
                                                   after=final['after_build_source_index']),
                      prerequisites=ctx.build_proofs, functional_prerequisites=ctx.functional_inputs,
                      native_asset=native, commands=[], binary_inventories=[],
                      historical_credit_transferred=False, performance_credit_seconds=0)
        owner.save(control / 'execution.json', record)
        try:
            record['source_identities'] = dict(product=ctx.build.source(product, ctx.selected),
                                               driver=ctx.build.source(ctx.driver, context_module.DRIVER),
                                               design=ctx.build.source(design, DESIGN))
            prefixes = ('src/Server.', 'src/Interop.', 'src/NativeWeave.Core/', 'src/Protocols.Mcp/', 'src/Packaging.',
                        'tests/Server.Native/', 'tests/Server.Application/', 'tests/Protocols.Mcp/', 'tests/Server.Diagnostics/',
                        'samples/api/server-application/', 'samples/api/protocols-mcp/', 'samples/api/server-diagnostics/')
            names = subprocess.check_output(['git', '-C', str(product), 'ls-files', '-z'], timeout=30).decode().split('\0')
            source_files = {name: sha(product / name) for name in names if name and (name.startswith(prefixes)
                            or name in ('Cargo.lock', 'Cargo.toml', 'global.json', 'Directory.Build.props',
                                        'Directory.Build.targets', 'NuGet.Config', 'rust-toolchain.toml'))}
            for name, digest in source_files.items():
                ctx.pin(product / name, digest)
            record.update(source_files_sha256=source_files, boot_sha256=ctx.boot,
                          toolchain_sha256=inputs['toolchain']['sha256'], freeze_sha256=inputs['freeze']['sha256'])
            for name in ('entry_free_bytes', 'between_command_free_bytes'):
                need(type(inputs[name]) is int and inputs[name] > 0, 'Positive frozen disk floor required')
            need(shutil.disk_usage(root).free >= inputs['entry_free_bytes'], 'Entry free-space floor not met')
            for name in ('temp', 'dotnet-home', 'inventories'):
                (output / name).mkdir()
            environment = dict(ctx.environment)
            environment.update({k: os.environ[k] for k in ('HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY') if k in os.environ})
            environment.update(NUGET_PACKAGES=str(output / 'producer-cache'), TMPDIR=str(output / 'temp'),
                               DOTNET_CLI_HOME=str(output / 'dotnet-home'))
            environment['PATH'] = str(Path(tools['python']['path']).parent) + os.pathsep + environment['PATH']
            for name, key in (('python3', 'python'), ('dotnet', 'dotnet')):
                need(Path(shutil.which(name, path=environment['PATH']) or '').resolve() == Path(tools[key]['executable_path']),
                     'Nested executable differs: ' + name)
            rows, binaries = recipes.plan(product, output, native, tools, design)
            need(len(rows) == 29 and len({row['label'] for row in rows}) == 29, 'Original command population differs')
            record['planned_commands'] = rows
            record['environment'] = {k: v for k, v in environment.items() if k not in ('HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY')}
            owner.save(output / 'admission.json', dict(files_sha256=ctx.pins,
                       source_identities=record['source_identities'], prerequisites=record['prerequisites'],
                       producer_inputs=record['producer_inputs'], producer_source_indices=record['producer_source_indices'],
                       functional_prerequisites=record['functional_prerequisites'], final_binding=ctx.final_binding))
            owner.save(control / 'execution.json', record)
            owner.enable_subreaper()
            tree_type = owner.public_tree(ctx.driver)

            def stable():
                ctx.stable()
                ctx.build.source(design, DESIGN)

            async def execute():
                loop, task = asyncio.get_running_loop(), asyncio.current_task()
                for sig in (signal.SIGINT, signal.SIGTERM):
                    loop.add_signal_handler(sig, task.cancel)
                for row in rows:
                    stable()
                    need(shutil.disk_usage(root).free >= inputs['between_command_free_bytes'], 'Between-command free-space floor not met')
                    label = row['label']
                    if label in binaries:
                        before = results.binary_inputs(native=native, **binaries[label])
                        inventory = output / 'inventories' / (label + '.json')
                        owner.save(inventory, dict(label=label, phase='immediately-before-execution', files_sha256=before))
                        record['binary_inventories'].append(str(inventory))
                    record['active_command'] = label
                    owner.save(control / 'execution.json', record)
                    actual = await owner.command(row, dict(environment, **row['environment_overrides']), control / label, tree_type)
                    record['commands'].append(actual)
                    if label in binaries:
                        need(results.binary_inputs(native=native, **binaries[label]) == before,
                             'Fixture changed its executable/native inputs')
                        owner.save(inventory, dict(label=label, phase='immediately-before-execution', files_sha256=before,
                                                   identical_after=True, rechecked_after_utc=owner.utc()))
                    record.pop('active_command')
                    owner.save(control / 'execution.json', record)

            asyncio.run(execute())
            stable()
            result = results.collect(output, product, ctx.selected, native, record['commands'], record['binary_inventories'])
            result.update(source_index_sha256=args.source_index_sha256,
                          measurement_source_index_sha256=ctx.index_sha256, final_binding=ctx.final_binding,
                          prerequisites=record['prerequisites'], producer_inputs=record['producer_inputs'],
                          producer_source_indices=record['producer_source_indices'],
                          functional_prerequisites=record['functional_prerequisites'],
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
