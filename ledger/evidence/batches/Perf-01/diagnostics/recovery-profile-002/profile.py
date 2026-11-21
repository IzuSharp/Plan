#!/usr/bin/env python3
"""New epoch002 diagnostic caller; original probes/readers, zero timing credit."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import signal
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def confined(root, relative):
    value = Path(relative)
    need(not value.is_absolute() and '..' not in value.parts, 'Root-relative path required')
    result = (root / value).resolve()
    need(result.is_relative_to(root), 'Path escaped its root')
    return result


def pg_closed(ctx, path):
    identity, commands = read(path / 'postgres/identity.json'), read(path / 'postgres/commands.json')
    need(identity['observed_settings'] == '18.0|on|on|on'
         and identity['postgres_sha256'] == sha(ctx.pg / 'postgres')
         and identity['psql_sha256'] == sha(ctx.pg / 'psql'), 'PG version, durability or tool differs')
    need(commands and all(row['exit_code'] == 0 for row in commands)
         and commands[-1]['argv'] == [str(ctx.pg / 'pg_ctl'), '-D', str(path / 'postgres/data'),
                                      '-m', 'fast', '-w', 'stop'], 'Original PG shutdown did not complete')


async def execute(run, profile, index):
    ctx, role = run.ctx, run.args.role
    output, kind = run.output / 'cell', profile['kind']

    def retain(paths, **metadata):
        run.cell(output, role, dict(files_sha256={str(p): sha(p) for p in paths}, **metadata))

    if kind == 'inspect':
        build = run.output / 'inspect-consumer'
        producer = ctx.codec_build(role)
        # The original preparer keeps its new writable cache and copied product
        # feed. Only existing external packages may come from this role's cache.
        cache = producer.parent / 'consumer-cache'
        assets_path = producer.parent / 'consumer/obj/project.assets.json'
        ctx.pin(assets_path, ctx.built[role]['files_sha256'][str(assets_path)])
        assets = read(assets_path)
        need(list(assets['packageFolders']) in ([str(cache)], [str(cache) + '/']), 'Codec cache provenance differs')
        packages = {row['path'] for name, row in assets['libraries'].items()
                    if row['type'] == 'package' and not name.lower().startswith('nativeweave.')}
        for framework in assets['project']['frameworks'].values():
            for row in framework.get('downloadDependencies', []):
                match = re.fullmatch(r'\[([^,\s]+),\s*\1\]', row['version'])
                need(match and not row['name'].lower().startswith('nativeweave.'), 'Unpinned external runtime pack')
                packages.add(row['name'].lower() + '/' + match[1])
        fallback = run.output / 'inspect-external-fallback'
        fallback.mkdir()
        provenance = {}
        for relative in sorted(packages):
            parts = Path(relative).parts
            need(len(parts) == 2 and not parts[0].startswith('nativeweave.'), 'External fallback package required')
            folder = confined(cache, relative)
            need(folder == cache / relative, 'Codec fallback source must not be an alias')
            archive = folder / (parts[0] + '.' + parts[1] + '.nupkg')
            recorded = ctx.built[role]['files_sha256'].get(str(archive))
            digest = recorded or sha(archive)
            ctx.pin(archive, digest)
            provenance[relative] = dict(archive_sha256=digest, archive_bound_by_build=recorded is not None)
            for name in (archive.name + '.sha512', '.nupkg.metadata'):
                path = folder / name
                ctx.pin(path, ctx.built[role]['files_sha256'].get(str(path)) or sha(path))
            (fallback / parts[0]).mkdir(exist_ok=True)
            (fallback / relative).symlink_to(folder, target_is_directory=True)
        run.record['inspect_preparation_cache'] = dict(role=role, codec_manifest_sha256=sha(producer),
            assets_sha256=sha(assets_path), source_cache=str(cache), fallback_view=str(fallback),
            external_packages=provenance, nativeweave_packages_in_fallback=False,
            original_fresh_writable_cache=True, restored_environment_before_probes=False)
        run.checkpoint()
        environment = ctx.environment
        ctx.environment = dict(environment, NUGET_FALLBACK_PACKAGES=str(fallback))
        try:
            await run.command('inspect-prepare', [ctx.python, ctx.driver / 'tests/Perf01.InspectProfile/prepare.py',
                '--codec-manifest', producer, '--codec-manifest-sha256', sha(producer), '--output', build], 1800, service=True)
        finally:
            ctx.environment = environment
            run.record['inspect_preparation_cache']['restored_environment_before_probes'] = True
            run.checkpoint()
        manifest = build / 'manifest.json'
        value = read(manifest)
        need(value['state'] == 'built' and value['product_commit'] == ctx.built[role]['product_commit']
             and value['codec_manifest_sha256'] == sha(producer), 'Inspect consumer producer differs')
        ctx.pin(manifest, sha(manifest))
        for name, digest in value['artifacts'].items():
            ctx.pin(confined(build, name), digest)
        executable = build / 'aot/NativeWeave.Perf01.InspectProbe'
        output.mkdir()
        for repetition in range(profile['processes']):
            result = output / ('inspect-' + str(repetition) + '.json')
            await run.command('inspect-' + str(repetition), [executable, manifest, sha(manifest),
                profile['warmup_calls'], profile['batches'], profile['calls_per_batch'], result], 120, service=True)
            row = read(result)
            need(row['status'] == 'passed' and row['formal_timing_eligible'] is False
                 and row['duration_credit_seconds'] == 0 and row['manifest_sha256'] == sha(manifest)
                 and row['product_commit'] == value['product_commit']
                 and row['completed_warmup_calls'] == profile['warmup_calls']
                 and row['completed_batches'] == profile['batches']
                 and row['completed_measured_calls'] == profile['batches'] * profile['calls_per_batch']
                 and row['loaded_native_sha256'] == value['native_sha256'], 'Inspect result identity/completeness failed')
            retain([manifest, result], repetition=repetition)
    elif kind == 'shared':
        probe, provider = profile['probe'], profile['provider']
        manifest = ctx.build_root / role / ('shared-' + probe) / 'manifest.json'
        need(ctx.built[role]['files_sha256'].get(str(manifest)) == sha(manifest), 'Shared manifest lacks actual build binding')
        value = read(manifest)
        name = 'NativeWeave.Perf01.PageProbe' if probe == 'page' else 'NativeWeave.Data.NativeHost.Tests'
        executable = manifest.parent / 'aot' / name
        need(value['probe'] == probe and value['artifacts']['aot/' + name] == sha(executable), 'Wrong Shared executable')
        if provider == 'postgresql':
            await run.command('shared-postgresql', [ctx.python, HERE / 'pg_probe.py', '--driver', ctx.driver,
                '--domain-source-sha256', index['native_source_sha256']['src/Benchmarks.Domain/run.py'],
                '--postgres-bin', ctx.pg, '--executable', executable, '--executable-sha256', sha(executable),
                '--count', profile['count'], '--output', output], 900, service=True)
            pg_closed(ctx, output)
        else:
            output.mkdir()
            await run.command('shared-sqlite', [executable, provider, output / 'database.sqlite',
                profile['count'], output / 'result.json'], 600, service=True)
        row = read(output / 'result.json')
        loaded = row['LoadedNativeModules']
        allowed = {str(confined(manifest.parent, name)): digest for name, digest in value['artifacts'].items()}
        expected_native = next(x['sha256'] for x in ctx.built[role]['native_assets'] if x['engineId'] == 'database.' + provider)
        need(row['Provider'] == provider and row['SourceReleased'] is True and loaded
             and all(allowed.get(name) == digest for name, digest in loaded.items())
             and expected_native in loaded.values(), 'Shared loaded native identity or retirement failed')
        if probe == 'page':
            need(row['Status'] == 'passed' and row['CompletedPages'] == profile['count']
                 and row['ExecutableSha256'] == sha(executable) and row['BuildManifestSha256'] == sha(manifest)
                 and row['DynamicCodeSupported'] is False
                 and all(row[k] is True for k in ('SeedCommitted', 'SeedTransactionReleased', 'SeedSessionReleased',
                     'PageSessionReleased', 'CleanupSessionReleased', 'TableDropped')), 'Page correctness/drain failed')
        else:
            need(row['Calls'] == profile['count'] and len(row['PublicCallMilliseconds']) == profile['count']
                 and row['NativeOperations'], 'Retirement observations incomplete')
        retain([manifest, output / 'result.json'], selected_executable_sha256=sha(executable), loaded_native_sha256=loaded)
    elif kind == 'postgresql-application':
        db = ctx.db_args(role)
        await run.command('postgresql-profile', [ctx.python, ctx.driver / 'tests/Perf01.Database/profile_postgresql.py',
            '--package-probe', db.package_probe, '--observer', db.observer, '--comparators', db.comparators,
            '--route', {'before': 'nativeweave-aot-rust', 'after': 'nativeweave-aot-rust',
                        'direct': 'direct-rust', 'managed': 'managed-aot'}[role], '--postgres-bin', ctx.pg,
            '--protocol', profile['protocol'], '--scenario', profile['scenario'], '--rate', profile['rate'],
            '--seconds', profile['seconds'], '--concurrency', profile['concurrency'],
            '--wait-sample-ms', profile['wait_sample_ms'], '--output', output], 900, service=True)
        # Original diagnostic GC/default sampling differs from the formal caller.
        # Retain original policy and summary; do not call the formal check_db gate.
        row, observed = read(output / 'summary.json'), read(output / 'postgres-profile-summary.json')
        expected = read(db.observer)['artifacts'] if role in ('before', 'after') else read(db.comparators)['routes'][row['route']]['artifacts']
        loaded = row['loaded_files']
        need(row['valid'] is True and row['supervision'] == 'completed' and row['durable_oracle']['passed'] is True
             and loaded and all(expected.get(name) == item['sha256'] for name, item in loaded.items()),
             'PG diagnostic correctness or selected mapped artifacts failed')
        need(observed['formal_timing_eligible'] is False and observed['wait_observer_passed'] is True
             and observed['load_statement_logging_observed'] is True and not observed['missing_files'],
             'PG diagnostic observer/log evidence incomplete')
        pg_closed(ctx, output)
        retain([output / name for name in ('summary.json', 'frozen-inputs.json', 'postgres-profile-summary.json',
            'postgres/identity.json', 'postgres/commands.json')], loaded_files=loaded)
    else:
        need(kind == 'protocol', 'Unknown frozen diagnostic kind')
        driver, selected = ctx.driver / 'tests/Perf01.Protocols/run.py', ctx.batch / profile['profile']
        await run.command('protocol-prepare', [ctx.python, driver, 'prepare', '--build', ctx.protocol_build(role),
            '--client-build', ctx.protocol_build('before'), '--profile', selected, '--group', profile['group'],
            '--rate', profile['rate'], '--duration', profile['seconds'], '--concurrency', profile['concurrency'],
            '--generator-cpus', '0,1', '--certificate', ctx.certificate, '--private-key', ctx.private_key,
            '--output', output], 600, service=True)
        await run.command('protocol-run', [ctx.python, driver, 'run', '--plan', output / 'plan.json',
            '--exclusive-lock', ctx.timing_lock], 600, service=True)
        value = ctx.check_protocol(output, role, passing=False)
        need(value['eligible'] is False and value['issues'] == ['Profiling-only cell cannot establish a timing comparison'],
             'Original protocol reader found an issue beyond the required profiling exclusion')
        reader_output = output / 'diagnostic-reader.json'
        ctx.owner.save(reader_output, value)
        retain([output / 'result.json', reader_output], formal_comparison_eligible=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--admission', type=Path, required=True)
    parser.add_argument('--admission-sha256', required=True)
    parser.add_argument('--measurement-source-index-sha256', required=True)
    parser.add_argument('--profile-source-index-sha256', required=True)
    parser.add_argument('--final-binding', type=Path)
    parser.add_argument('--final-binding-sha256')
    parser.add_argument('--profile', required=True)
    parser.add_argument('--role', choices=('before', 'after', 'direct', 'managed'), default='before')
    parser.add_argument('--label', required=True)
    args = parser.parse_args()
    need(os.sched_getaffinity(0) == {8}, 'Outer diagnostic owner must use CPU8')
    need(re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', args.label), 'Fresh simple diagnostic label required')
    need(sha(HERE / 'sources.json') == args.profile_source_index_sha256, 'Diagnostic source index differs')
    index = read(HERE / 'sources.json')
    for name, digest in index['files_sha256'].items():
        need(sha(confined(HERE, name)) == digest, 'Diagnostic caller/plan changed')
    measurement = HERE.parent / 'recovery-measure-002'
    need(sha(measurement / 'measurement-sources.json') == args.measurement_source_index_sha256
         == index['measurement_source_index_sha256'], 'Reviewed measurement interface differs')
    measured = read(measurement / 'measurement-sources.json')
    for name in ('admission.py', 'measure.py'):
        need(sha(measurement / name) == measured['files_sha256'][name], 'Admission/owner caller changed before import')
    need(sha(args.admission) == args.admission_sha256, 'Actual admission descriptor changed')
    root, admission = args.root.resolve(strict=True), read(args.admission)
    build_input = confined(root, admission['build_inputs']['path'])
    need(sha(build_input) == admission['build_inputs']['sha256'], 'Actual build input differs')
    lock = confined(root, read(build_input)['exclusive_lock'])
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open('a+b') as reservation:
        fcntl.flock(reservation.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        sys.path.insert(0, str(measurement))
        module = importlib.import_module('measure')
        ctx = module.Context(root, args.admission, args.admission_sha256, args.measurement_source_index_sha256,
                             args.final_binding, args.final_binding_sha256)
        need(ctx.reservation == lock and (args.role != 'after' or ctx.selected is not None), 'Reservation/final binding differs')
        ctx.pin(HERE / 'sources.json', args.profile_source_index_sha256)
        for name, digest in index['files_sha256'].items():
            ctx.pin(confined(HERE, name), digest)
        for group, base in (('native_source_sha256', ctx.driver), ('plan_source_sha256', ctx.batch)):
            for name, digest in index[group].items():
                ctx.pin(confined(base, name), digest)
        plan = read(HERE / 'plan.json')
        profile = plan['profiles'][args.profile]
        need(args.role in profile['roles'], 'This original probe has no such comparator')
        args.stage, args.group, args.scene = 'profiling-only', profile.get('group', profile['kind']), args.profile
        output = ctx.output.parent / 'profiles-001' / args.label
        need(not output.is_relative_to(ctx.output) and not ctx.output.is_relative_to(output), 'Diagnostic/formal output overlap')
        output.mkdir(parents=True, exist_ok=False)
        run = module.Run(ctx, args, output)
        run.record.update(kind='new-epoch002-layered-diagnostic', profiling_source_index_sha256=args.profile_source_index_sha256,
            profiling_plan_sha256=sha(HERE / 'plan.json'), formal_timing_eligible=False, formal_comparison_credit=False,
            historical_wrapper_restored=False, new_statistics_algorithm=False,
            original_protocol_reader_reused=profile['kind'] == 'protocol')
        run.checkpoint()
        try:
            ctx.owner.enable_subreaper()
            run.tree = ctx.owner.public_tree(ctx.driver)
            async def owned():
                loop, task = asyncio.get_running_loop(), asyncio.current_task()
                for sig in (signal.SIGTERM, signal.SIGINT):
                    loop.add_signal_handler(sig, task.cancel)
                await execute(run, profile, index)
            asyncio.run(owned())
            ctx.stable()
            run.record['status'] = 'completed'
        except BaseException as error:
            run.record.update(status='failed', failure=type(error).__name__ + ': ' + str(error))
            raise
        finally:
            run.record.update(ended_utc=ctx.owner.utc(), duration_credit_seconds=0)
            run.checkpoint()
    print(json.dumps(dict(status=run.record['status'], execution=str(output / 'execution.json'), sha256=sha(output / 'execution.json'))))


if __name__ == '__main__':
    main()
