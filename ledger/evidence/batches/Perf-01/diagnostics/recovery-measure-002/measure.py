#!/usr/bin/env python3
"""Finite caller of original Perf-01 measurements; root is the sole executor."""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess

from admission import BEFORE, CODEC_ROUTES, Context, HERE, ROUTES, confined, need, noise_projection, read, sha


def scene_name(group, scene):
    return group + '-' + scene if group in ('postgresql', 'sqlite', 'codec') else scene


def completed_execution(ctx, path, expected, stage):
    need(sha(path) == expected, 'Actual measurement execution identity changed')
    value = read(path)
    need(value['status'] == 'completed' and value['stage'] == stage
         and value['admission_sha256'] == ctx.sha256 and value['measurement_source_index_sha256'] == ctx.index_sha256,
         'Wrong actual completed measurement execution')
    need(len(value['commands']) == len(value['planned_commands']) > 0, 'Measurement command population differs')
    for planned, actual in zip(value['planned_commands'], value['commands'], strict=True):
        child = ctx.pin(actual['path'], actual['sha256'])
        receipt = read(child)
        need(receipt['status'] == 'completed' and receipt['retired'] and receipt['exit_code'] == 0
             and all(receipt[k] == v for k, v in planned.items()), 'Actual measurement command/retirement differs')
        for name, digest in receipt['logs_sha256'].items():
            ctx.pin(child.parent / name, digest)
    return value


def noise_gate(ctx, descriptor_path, expected):
    need(descriptor_path is not None and expected, 'Fresh published/read-back before-noise descriptor required')
    need(sha(descriptor_path) == expected, 'Noise publication descriptor changed')
    doc = read(descriptor_path)
    need(doc['epoch'] == 'recovery-002' and doc['admission_sha256'] == ctx.sha256,
         'Noise publication belongs to another actual runtime context')
    projection_path, projection = ctx.document(doc['projection'])
    readback_path, _ = ctx.file(doc['readback'])
    _, retrieval = ctx.document(doc['retrieval_receipt'])
    need(sha(readback_path) == sha(projection_path) == doc['projection']['sha256'], 'Published numeric projection readback differs')
    publication = doc['publication']
    need(publication['repository'] == 'IzuSharp/Plan' and re.fullmatch('[0-9a-f]{40}', publication['commit'])
         and re.fullmatch('[0-9a-f]{40}', publication['blob_oid'])
         and publication['path'].startswith('ledger/evidence/batches/Perf-01/'), 'Wrong project publication identity')
    need(retrieval['status'] == 'retrieved' and retrieval['repository'] == publication['repository']
         and retrieval['commit'] == publication['commit'] and retrieval['path'] == publication['path']
         and retrieval['blob_oid'] == publication['blob_oid']
         and retrieval['sha256'] == sha(projection_path) and retrieval['retrieved_utc']
         and retrieval['url'].startswith('https://'), 'Missing actual remote readback receipt')
    need(datetime.fromisoformat(retrieval['retrieved_utc']) <= datetime.now(timezone.utc), 'Remote retrieval time is in the future')
    committed = subprocess.check_output(['git', '-C', str(ctx.plan), 'show', publication['commit'] + ':' + publication['path']], timeout=30)
    need(hashlib.sha256(committed).hexdigest() == sha(projection_path), 'Exact published commit/path differs from readback')
    blob = subprocess.check_output(['git', '-C', str(ctx.plan), 'rev-parse', publication['commit'] + ':' + publication['path']], text=True, timeout=30).strip()
    need(blob == publication['blob_oid'], 'Published blob identity differs')
    need(projection['epoch'] == 'recovery-002' and projection['admission_sha256'] == ctx.sha256,
         'Numeric projection context differs')
    expected_scenes = {'postgresql-c16', 'sqlite-c16', 'codec-w1', 'codec-w2'} | {
        x['id'] for x in ctx.workloads['protocol']['profiles'] if x['kind'] == 'fixed-short'}
    need(set(doc['noise']) == set(projection['noise']) == expected_scenes, 'All ten before-only scene bands must be frozen before candidate timing')
    result = {}
    for scene, item in doc['noise'].items():
        execution_path, _ = ctx.file(item['execution'])
        execution = completed_execution(ctx, execution_path, item['execution']['sha256'], 'noise')
        need(execution['role'] == 'before' and scene_name(execution['group'], execution['scene']) == scene,
             'Noise publication scene differs from its actual before-only execution')
        noise_path, noise = ctx.document(item['receipt'])
        need(execution['status'] == 'completed' and execution['stage'] == 'noise'
             and execution['admission_sha256'] == ctx.sha256 and execution['measurement_source_index_sha256'] == ctx.index_sha256
             and execution['noise_receipt']['path'] == str(noise_path)
             and execution['noise_receipt']['sha256'] == sha(noise_path), 'Noise does not have its actual completed execution')
        expected_projection = noise_projection(scene, noise)
        expected_projection['noise_sha256'] = sha(noise_path)
        need(projection['noise'][scene] == expected_projection, 'Published band/provenance differs from original before-only receipt')
        need(datetime.fromisoformat(noise['created_utc']) <= datetime.fromisoformat(retrieval['retrieved_utc']), 'Readback predates noise creation')
        result[scene] = noise_path
    return result, dict(path=str(Path(descriptor_path).resolve()), sha256=expected,
                        published_commit=publication['commit'], projection_sha256=sha(projection_path))


class Run:
    def __init__(self, ctx, args, output):
        self.ctx, self.args, self.output = ctx, args, output
        self.record = dict(schema_version=1, task='Perf-01', epoch='recovery-002', status='running',
            stage=args.stage, group=args.group, scene=args.scene, role=args.role,
            started_utc=ctx.owner.utc(), admission_sha256=ctx.sha256,
            measurement_source_index_sha256=ctx.index_sha256, selected_final_commit=ctx.selected,
            final_binding=ctx.final_binding,
            build_proofs=ctx.build_proofs, planned_commands=[], commands=[], cells=[],
            historical_credit_transferred=False, duration_credit_seconds=0)
        self.tree = None

    def checkpoint(self):
        self.ctx.owner.save(self.output / 'execution.json', self.record)

    async def command(self, label, argv, timeout, cwd=None, service=False):
        self.ctx.stable()
        spec = dict(label=label, argv=(['taskset', '--cpu-list', '2,3'] if service else []) + list(map(str, argv)),
                    cwd=str(cwd or self.ctx.driver), timeout_seconds=timeout, environment_overrides={})
        self.record['planned_commands'].append(spec)
        self.checkpoint()
        directory = self.output / 'commands' / label
        try:
            actual = await self.ctx.owner.command(spec, self.ctx.environment, directory, self.tree)
        except BaseException:
            receipt = directory / 'receipt.json'
            if receipt.exists():
                self.record['commands'].append(dict(path=str(receipt), sha256=sha(receipt), failed=True))
                self.checkpoint()
            raise
        self.record['commands'].append(actual)
        self.checkpoint()
        self.ctx.stable()
        return actual

    def cell(self, path, role, result):
        self.record['cells'].append(dict(directory=str(path), role=role, result=result))
        self.checkpoint()

    async def database(self, role, path, config, repetition=0):
        ctx = self.ctx
        argv = ctx.database_controller.command(ctx.db_args(role), ctx.policy, self.args.group,
                                              config['rate'], config['seconds'], path)
        overrides = {'--concurrency': config['concurrency'], '--idle-seconds': config.get('idle_seconds', 5),
                     '--recovery-requests': config.get('recovery_requests', 16),
                     '--stage': config.get('stage', 'short')}
        for flag, value in overrides.items():
            argv[argv.index(flag) + 1] = str(value)
        argv.extend(('--repetition', str(repetition)))
        await self.command(path.name, argv, config['seconds'] + 900, service=True)
        value = ctx.check_db(path, role)
        self.cell(path, role, dict(summary_sha256=sha(path / 'summary.json'), eligible=value['eligible'],
                                   actual_loaded_files=value['loaded_files']))
        return value

    async def protocol(self, role, path, profile, rate, seconds, concurrency):
        ctx = self.ctx
        driver = ctx.driver / 'tests/Perf01.Protocols/run.py'
        argv = [ctx.python, driver, 'prepare', '--build', ctx.protocol_build(role),
                '--client-build', ctx.protocol_build('before'), '--profile', profile,
                '--group', self.args.group, '--rate', rate, '--duration', seconds,
                '--concurrency', concurrency, '--generator-cpus', '0,1',
                '--certificate', ctx.certificate, '--private-key', ctx.private_key, '--output', path]
        await self.command(path.name + '-prepare', argv, 600, service=True)
        await self.command(path.name + '-run', [ctx.python, driver, 'run', '--plan', path / 'plan.json',
                           '--exclusive-lock', ctx.timing_lock], seconds + 600, service=True)
        value = ctx.check_protocol(path, role, long=self.args.stage == 'long')
        self.cell(path, role, dict(result_sha256=sha(path / 'result.json'), eligible=value['eligible'], build=value['build']))

    async def codec(self, role, path, config):
        ctx = self.ctx
        argv = [ctx.python, ctx.driver / 'tests/Perf01.Codec/driver.py', 'run',
                '--manifest', ctx.codec_build(role), '--corpus', ctx.corpus, '--route', CODEC_ROUTES[role],
                '--workers', config['workers'], '--rate', config['rate'], '--duration-seconds', config['seconds'],
                '--queue', 64, '--inflight', 256, '--deadline-ms', 1000, '--max-lag-ms', 100,
                '--action', 'mixed', '--interface', 'mixed', '--generator-cpus', '0,1',
                '--warmup-seconds', 20, '--recovery-seconds', 10, '--recovery-rate', 1,
                '--idle-seconds', config.get('idle_seconds', 5), '--output', path]
        await self.command(path.name, argv, config['seconds'] + 600, service=True)
        ctx.check_codec_identity(path, role)
        result = read(path / 'result.json')
        need(all(result.get(k) is True for k in ('valid', 'complete', 'service_standard_met', 'recovery_standard_met')), 'Codec cell failed original validity/service checks')
        self.cell(path, role, dict(result_sha256=sha(path / 'result.json'), summary_sha256=sha(path / 'summary.json')))

    async def short(self, frozen_noise):
        ctx, args = self.ctx, self.args
        paths = {role: [] for role in ('before', 'after', 'direct', 'managed')}
        noise = args.stage == 'noise'
        if args.group in ('postgresql', 'sqlite'):
            strata = {x['id']: x for x in ctx.workloads['database']['strata']}
            need(args.scene in strata and (not noise or args.scene == 'c16'), 'DB noise uses the original c16 fixed anchor')
            row = strata[args.scene]
            config = dict(row, rate=row.get('rate', row.get('rates', {}).get(args.group)))
            repetitions = range(3) if noise else row['repetitions']
            values = []
            for repetition in repetitions:
                order = ['before'] if noise else ctx.workloads['database']['order_by_repetition'][str(repetition)]
                for role in order:
                    path = self.output / 'cells' / f'{repetition}-{role}'
                    values.append(await self.database(role, path, config))
                    paths[role].append(path)
            if noise:
                # Original anchor triplet checks and unchanged band formula.
                from admission import module
                source = module('perf01_epoch002_anchor_rules', ctx.batch / 'database_freeze_anchor_noise.py')
                signatures = [dict(c['configuration'], source_files=c['driver_source_files'], route=c['route_identity']) for c in values]
                source.triplet_gate(values, signatures)
                means = {key: [c['scopes'][scope]['mean_ns'] for c in values]
                         for key, scope in (('mixed', 'whole'), ('cycle', 'cycle'), ('page', 'page'))}
                identities = {str(path / name): digest for path, cell in zip(paths['before'], values, strict=True)
                              for name, digest in cell['evidence_sha256'].items()}
                identity = source.canonical(identities)
                bands = {key: dict(baseline_id=f'Perf-01/{args.group}/mixed/c16/{config["rate"]}/gc-deferred-threaded-anchor/{key}/{identity}',
                                   absolute_noise_ns=max(1000, max(items) - min(items)), relative_noise=0) for key, items in means.items()}
                result = dict(task='Perf-01', created_utc=ctx.owner.utc(), scope='Fresh epoch-002 before-only original fixed anchor',
                    provider=args.group, rate=config['rate'], concurrency=16, process_means_ns=means, bands=bands,
                    processes=values, configuration=signatures[0], inputs_sha256=identities,
                    admission_sha256=ctx.sha256, measurement_source_index_sha256=ctx.index_sha256)
                destination = self.output / 'noise.json'
                ctx.owner.save(destination, result)
            else:
                selected_noise = frozen_noise[args.group + '-c16']
                argv = [ctx.python, HERE / 'readers/database_compare.py', '--nativeweave', ctx.driver,
                        '--noise-receipt', selected_noise, '--noise-sha256', sha(selected_noise), '--output', self.output / 'comparison']
                for role in paths:
                    argv += ['--' + role, *paths[role]]
                await self.command('extract-comparison', argv, 600)
                destination = self.output / 'comparison/comparison.json'
                result = read(destination)
                if args.scene == 'c16':
                    need(all(x['eligible'] for x in result['comparisons']), 'DB comparison has an ineligible supplied process/band')
                else:
                    self.record['interpretation'] = 'Original one-process descriptive stratum; no statistical improvement claim or reused c16 noise inference'
        elif args.group in ('http', 'grpc'):
            rows = [x for x in ctx.workloads['protocol']['profiles'] if x['id'] == args.scene and x['kind'] == 'fixed-short']
            need(len(rows) == 1 and rows[0]['group'] == args.group, 'Unknown frozen short protocol scene')
            row = rows[0]
            profile = ctx.workload_path.parent / row['profile']
            need(sha(profile) == row['sha256'], 'Frozen protocol profile differs')
            for repetition in range(3):
                order = ['before'] if noise else ctx.workloads['protocol']['short_order_by_repetition'][str(repetition)]
                for role in order:
                    path = self.output / 'cells' / f'{repetition}-{role}'
                    await self.protocol(role, path, profile, row['rate'], row['seconds'], row['concurrency'])
                    paths[role].append(path)
            extraction = self.output / ('noise' if noise else 'comparison')
            argv = [ctx.python, ctx.batch / 'protocol_compare.py', '--nativeweave', ctx.driver, '--output', extraction]
            if noise:
                argv += ['freeze-noise', '--before', *paths['before'], '--direct-build', ctx.protocol_build('direct'),
                         '--direct-build-sha256', sha(ctx.protocol_build('direct'))]
            else:
                selected_noise = frozen_noise[args.scene]
                argv += ['compare', '--noise', selected_noise, '--noise-sha256', sha(selected_noise)]
                for role in ('before', 'after', 'direct'):
                    argv += ['--' + role, *paths[role]]
            await self.command('extract-' + args.stage, argv, 600)
            destination = extraction / ('noise.json' if noise else 'comparison.json')
        else:
            rows = [x for x in ctx.workloads['codec']['strata'] if x['id'] == args.scene]
            need(len(rows) == 1, 'Unknown frozen codec stratum')
            config = rows[0]
            for repetition in range(3):
                order = ['before'] if noise else ctx.workloads['codec']['order_by_repetition'][str(repetition)]
                for role in order:
                    path = self.output / 'cells' / f'{repetition}-{role}'
                    await self.codec(role, path, config)
                    paths[role].append(path)
            argv = [ctx.python, ctx.batch / 'codec_compare.py', 'freeze' if noise else 'compare',
                    '--corpus', ctx.corpus / 'manifest.json', '--a21', ctx.a21_path]
            if noise:
                destination = self.output / 'noise.json'
                argv += ['--cells', *paths['before'], '--build', ctx.codec_build('before'),
                         '--resolution-ns', 1000, '--p99-max-ms', 500, '--rss-max-mib', 256, '--output', destination]
            else:
                selected_noise = frozen_noise['codec-' + args.scene]
                argv += ['--noise', selected_noise, '--noise-sha256', sha(selected_noise), '--output', self.output / 'comparison']
                for role in paths:
                    argv += ['--' + role, *paths[role], '--' + role + '-build', ctx.codec_build(role)]
                destination = self.output / 'comparison/comparison.json'
            await self.command('extract-' + args.stage, argv, 900)
        self.record['noise_receipt' if noise else 'comparison_receipt'] = dict(path=str(destination), sha256=sha(destination))
        if noise:
            projection = noise_projection(scene_name(args.group, args.scene), read(destination))
            projection['noise_sha256'] = sha(destination)
            ctx.owner.save(self.output / 'numeric-noise-projection.json', projection)

    async def capacity(self):
        ctx, args = self.ctx, self.args
        need(args.role in ('before', 'after', 'direct'), 'Capacity routes are before, after and direct')
        if args.group in ('postgresql', 'sqlite'):
            argv = [ctx.python, HERE / 'database_capacity.py', '--root', ctx.root, '--admission', ctx.path,
                    '--admission-sha256', ctx.sha256, '--source-index-sha256', ctx.index_sha256,
                    '--role', args.role, '--group', args.group, '--output', self.output / 'capacity']
            if ctx.final_binding is not None:
                argv += ['--final-binding', ctx.final_binding['path'], '--final-binding-sha256', ctx.final_binding['sha256']]
            directory = self.output / 'capacity'
        elif args.group in ('http', 'grpc'):
            argv = [ctx.python, ctx.batch / 'protocol_calibrate.py', '--nativeweave', ctx.driver,
                    '--policy', ctx.policy_path, '--policy-sha256', sha(ctx.policy_path),
                    '--build', ctx.protocol_build(args.role), '--build-sha256', sha(ctx.protocol_build(args.role)),
                    '--client-build', ctx.protocol_build('before'), '--client-build-sha256', sha(ctx.protocol_build('before')),
                    '--certificate', ctx.certificate, '--private-key', ctx.private_key,
                    '--exclusive-lock', ctx.timing_lock, '--variant', args.role, '--groups', args.group,
                    '--attempt', 'epoch002', '--output-root', self.output / 'capacity']
            directory = self.output / 'capacity' / f'{args.role}-{args.group}-epoch002'
        else:
            argv = [ctx.python, ctx.batch / 'codec_calibrate.py', '--nativeweave', ctx.driver,
                    '--policy', ctx.policy_path, '--policy-sha256', sha(ctx.policy_path),
                    '--build', ctx.codec_build(args.role), '--build-sha256', sha(ctx.codec_build(args.role)),
                    '--corpus', ctx.corpus, '--corpus-sha256', sha(ctx.corpus / 'manifest.json'),
                    '--variant', args.role, '--output', self.output / 'capacity']
            directory = self.output / 'capacity'
        await self.command('original-capacity', argv, 14400, service=True)
        selection = read(directory / 'selection.json')
        controller = read(directory / 'controller.json')
        need(controller['state'] == 'completed' and sha(directory / 'controller.json') == selection['controller_sha256'], 'Capacity controller incomplete')
        for row in controller['cells']:
            path = Path(row['directory'])
            if args.group in ('postgresql', 'sqlite'):
                ctx.check_db(path, args.role, passing=False)
            elif args.group in ('http', 'grpc'):
                ctx.check_protocol(path, args.role, passing=False)
            else:
                ctx.check_codec_identity(path, args.role)
        low = selection['highest_consistently_passing_rate']
        last = controller['cells'][-3:]
        need(len(last) == 3 and all(x['phase'] == f'confirmation-{i}' and x['rate'] == low
             and x['seconds'] == 60 and x['qualifies'] is True and x['exit_code'] == 0 for i, x in enumerate(last)),
             'Capacity lacks its original final three independent confirmations')
        fixed = ctx.freeze['long_groups'][args.group]['rate_per_second']
        self.record['capacity'] = dict(selection=dict(path=str(directory / 'selection.json'), sha256=sha(directory / 'selection.json')),
            controller=dict(path=str(directory / 'controller.json'), sha256=sha(directory / 'controller.json')),
            highest_consistently_passing_rate=low, fixed_paired_long_rate=fixed,
            fixed_rate_within_confirmed_capacity=low >= fixed,
            original_long_rate_proposal_ignored=selection.get('long_rate'))

    def capacity_gate(self):
        ctx, args = self.ctx, self.args
        need(args.capacity_proof is not None and args.capacity_proof_sha256, 'Actual current capacity execution required before long load')
        record = completed_execution(ctx, args.capacity_proof, args.capacity_proof_sha256, 'capacity')
        need(record['status'] == 'completed' and record['stage'] == 'capacity' and record['group'] == args.group
             and record['role'] == args.role and record['admission_sha256'] == ctx.sha256
             and record['measurement_source_index_sha256'] == ctx.index_sha256
             and record['capacity']['fixed_rate_within_confirmed_capacity'] is True, 'Wrong/failed role capacity qualification')
        need(args.role != 'after' or record['selected_final_commit'] == ctx.selected
             and record['final_binding'] == ctx.final_binding, 'After capacity uses another final product binding')
        capacity = record['capacity']
        selection = read(ctx.pin(capacity['selection']['path'], capacity['selection']['sha256']))
        controller = read(ctx.pin(capacity['controller']['path'], capacity['controller']['sha256']))
        need(selection['controller_sha256'] == capacity['controller']['sha256'] and controller['state'] == 'completed', 'Capacity controller identity changed')
        low = selection['highest_consistently_passing_rate']
        last = controller['cells'][-3:]
        need(len(last) == 3 and all(row['phase'] == f'confirmation-{i}' and row['qualifies'] is True and row['exit_code'] == 0
             and row['seconds'] == 60 and row['rate'] == low for i, row in enumerate(last)), 'Missing three successful capacity confirmations')
        need(low >= ctx.freeze['long_groups'][args.group]['rate_per_second'], 'Frozen long rate exceeds current confirmed capacity')
        self.record['capacity_qualification'] = dict(path=str(args.capacity_proof.resolve()), sha256=args.capacity_proof_sha256)

    async def long(self):
        ctx, args = self.ctx, self.args
        need(args.role in ('before', 'after'), 'Exactly the two actual product versions receive paired long credit')
        self.capacity_gate()
        config = ctx.freeze['long_groups'][args.group]
        path = self.output / 'cell'
        if args.group in ('postgresql', 'sqlite'):
            await self.database(args.role, path, dict(rate=config['rate_per_second'], seconds=config['requested_seconds'],
                concurrency=config['concurrency'], idle_seconds=config['idle_seconds'],
                recovery_requests=config['recovery_requests'], stage='soak'))
        elif args.group in ('http', 'grpc'):
            profile = ctx.driver / config['profile'] if args.group == 'http' else ctx.workload_path.parent / config['profile']
            need(sha(profile) == config['profile_sha256'], 'Original long protocol profile changed')
            await self.protocol(args.role, path, profile, config['rate_per_second'], config['requested_seconds'], config['concurrency'])
        else:
            await self.codec(args.role, path, dict(rate=config['rate_per_second'], seconds=config['requested_seconds'],
                                                  workers=config['workers'], idle_seconds=config['idle_seconds']))
        destination = self.output / 'long-verification.json'
        await self.command('original-long-verifier', [ctx.python, ctx.driver / 'tests/Perf01/verify_long.py',
                           '--group', args.group, '--output', path, '--receipt', destination], 1200)
        result = read(destination)
        need(result['accepted'] is True and result['duration_credit_seconds'] >= 1800, 'Original effective D-C duration/correctness/resource proof failed')
        self.record.update(long_verification=dict(path=str(destination), sha256=sha(destination)),
                           duration_credit_seconds=result['duration_credit_seconds'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--admission', type=Path, required=True)
    parser.add_argument('--admission-sha256', required=True)
    parser.add_argument('--source-index-sha256', required=True)
    parser.add_argument('--final-binding', type=Path)
    parser.add_argument('--final-binding-sha256')
    parser.add_argument('--stage', choices=('noise', 'compare', 'capacity', 'long'), required=True)
    parser.add_argument('--group', choices=('postgresql', 'sqlite', 'http', 'grpc', 'codec'), required=True)
    parser.add_argument('--scene')
    parser.add_argument('--role', choices=('before', 'after', 'direct'), default='before')
    parser.add_argument('--label', required=True, help='Fresh simple directory name; partial/failed outputs are never resumed')
    parser.add_argument('--noise-publication', type=Path)
    parser.add_argument('--noise-publication-sha256')
    parser.add_argument('--capacity-proof', type=Path)
    parser.add_argument('--capacity-proof-sha256')
    args = parser.parse_args()
    need(os.sched_getaffinity(0) == {8}, 'Outer root owner must use CPU8')
    need(re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', args.label), 'Simple fresh stage label required')
    # Acquire the shared build/orchestration reservation before full artifact
    # admission; another live measurement must not overlap these file reads.
    need(sha(args.admission) == args.admission_sha256, 'Admission document changed')
    initial = read(args.admission)
    root = args.root.resolve(strict=True)
    build_input_path = confined(root, initial['build_inputs']['path'])
    need(sha(build_input_path) == initial['build_inputs']['sha256'], 'Actual build input changed')
    reservation_path = confined(root, read(build_input_path)['exclusive_lock'])
    reservation_path.parent.mkdir(parents=True, exist_ok=True)
    with reservation_path.open('a+b') as reservation:
        fcntl.flock(reservation.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        ctx = Context(args.root, args.admission, args.admission_sha256, args.source_index_sha256,
                      args.final_binding, args.final_binding_sha256)
        need(ctx.reservation == reservation_path, 'Reservation identity changed during admission')
        need(args.stage != 'compare' and args.role != 'after' or ctx.selected is not None, 'Comparison/after stages require the exact final binding')
        need(args.stage != 'noise' or args.role == 'before', 'Noise can measure only the before product')
        output = ctx.output / args.label
        need(not output.exists(), 'Fresh stage output required; retain prior partial/failed evidence')
        output.mkdir(parents=True)
        (output / 'cells').mkdir()
        run = Run(ctx, args, output)
        run.checkpoint()
        try:
            frozen_noise = None
            if args.stage in ('compare', 'long') or args.stage == 'capacity' and args.role != 'before':
                frozen_noise, run.record['noise_publication'] = noise_gate(ctx, args.noise_publication, args.noise_publication_sha256)
                run.checkpoint()
            ctx.owner.enable_subreaper()
            run.tree = ctx.owner.public_tree(ctx.driver)
            async def execute():
                loop, task = asyncio.get_running_loop(), asyncio.current_task()
                for sig in (signal.SIGTERM, signal.SIGINT):
                    loop.add_signal_handler(sig, task.cancel)
                if args.stage in ('noise', 'compare'):
                    await run.short(frozen_noise)
                elif args.stage == 'capacity':
                    await run.capacity()
                else:
                    await run.long()
            asyncio.run(execute())
            ctx.stable()
            run.record['status'] = 'completed'
        except BaseException as error:
            run.record.update(status='failed', failure=type(error).__name__ + ': ' + str(error), duration_credit_seconds=0)
            raise
        finally:
            run.record['ended_utc'] = ctx.owner.utc()
            run.checkpoint()
    print(json.dumps(dict(status=run.record['status'], execution=str(output / 'execution.json'), sha256=sha(output / 'execution.json'))))


if __name__ == '__main__':
    main()
