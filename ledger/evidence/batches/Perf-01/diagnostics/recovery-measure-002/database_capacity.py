#!/usr/bin/env python3
"""Original DB capacity loop with explicit epoch-002 role admission.

The root measure.py process owns this complete command tree through c752.
No process owner, workload, timer, percentile or noise algorithm is added here.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess

from admission import Context, need, read, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--admission', type=Path, required=True)
    parser.add_argument('--admission-sha256', required=True)
    parser.add_argument('--source-index-sha256', required=True)
    parser.add_argument('--final-binding', type=Path)
    parser.add_argument('--final-binding-sha256')
    parser.add_argument('--role', choices=('before', 'after', 'direct'), required=True)
    parser.add_argument('--group', choices=('postgresql', 'sqlite'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(os.sched_getaffinity(0) == {2, 3}, 'Original DB capacity controller must start on service CPUs2,3')
    ctx = Context(args.root, args.admission, args.admission_sha256, args.source_index_sha256,
                  args.final_binding, args.final_binding_sha256)
    need(args.role != 'after' or ctx.selected is not None, 'After capacity requires an actual final binding')
    output = args.output.resolve()
    need(output.is_relative_to(ctx.output) and not output.exists(), 'Fresh admitted capacity output required')
    output.mkdir(parents=True)
    calibration = ctx.policy['calibration']
    need((calibration['stage_seconds'], calibration['confirmation_seconds'], calibration['confirmation_fresh_processes'],
          calibration['confirmation_attempt_limit'], calibration['short_idle_seconds']) == (30, 60, 3, 10, 5),
         'Original finite capacity settings changed')
    rows = []
    receipt = dict(task='Perf-01', epoch='recovery-002', group=args.group, variant=args.role, state='running',
        admission_sha256=ctx.sha256, measurement_source_index_sha256=ctx.index_sha256,
        script_sha256=sha(__file__), policy_sha256=sha(ctx.policy_path), compact_observation=True,
        source_roles=dict(application_driver=ctx.freeze['driver_checkout_commit'],
                          before_runtime=ctx.freeze['baseline_product_commit'], final_runtime=ctx.selected),
        scheduler_gc_policy=ctx.gc_policy, resource_sampling_policy=ctx.sampling,
        kernel_boot_sha256=ctx.boot, cells=rows)

    def checkpoint():
        ctx.owner.save(output / 'controller.json', receipt)

    def cell(rate, seconds=None, phase='ladder'):
        ctx.stable()
        seconds = calibration['stage_seconds'] if seconds is None else seconds
        need(0 < rate <= 10000 and math.ceil(seconds * 1e9 / round(1e9 / rate)) + 1 <= 1_000_000,
             'Requested cell exceeds the original DB finite bound')
        index = len(rows)
        path = output / f'{index:02}-{phase}-{rate:g}'
        cmd = ctx.database_controller.command(ctx.db_args(args.role), ctx.policy, args.group, rate, seconds, path)
        row = dict(index=index, phase=phase, rate=rate, seconds=seconds, directory=str(path),
                   start_utc=ctx.owner.utc(), state='running', commands=[list(map(str, cmd))])
        rows.append(row)
        checkpoint()
        print(json.dumps(row), flush=True)
        try:
            with (output / f'{index:02}.log').open('x') as log:
                completed = subprocess.run(cmd, cwd=ctx.driver, stdout=log, stderr=subprocess.STDOUT)
        except BaseException as error:
            row.update(state='interrupted-or-failed', end_utc=ctx.owner.utc(), error=type(error).__name__)
            checkpoint()
            raise
        row.update(exit_code=completed.returncode, end_utc=ctx.owner.utc(), state='completed')
        result_path = path / 'summary.json'
        if not result_path.is_file():
            row.update(valid=False, qualifies=False, error='Missing final result')
            checkpoint()
            raise RuntimeError('Incomplete cell; retain original supervision/partial evidence')
        result = read(result_path)
        # Admission binds common application source independently of actual
        # runtime packages; original per-cell correctness/GC/observer/retirement
        # and actual loaded-role assertions are retained by this checked reader.
        ctx.check_db(path, args.role, passing=False)
        resources = result.get('resources', {}).get('measurement', {})
        qualifies = completed.returncode == 0 and result.get('valid') is True and result.get('qualifies_service_standard') is True
        row.update(valid=result.get('valid', False), qualifies=qualifies, p99_ns=result.get('p99_ns'),
            rss_peak_bytes=resources.get('rss_peak_bytes'), successes=result.get('successful'), offered=result.get('offered'),
            throughput=result.get('successful_per_second'), cpu_percent_one_core=resources.get('app_cpu_percent_one_core'),
            invalid_reasons=result.get('invalid_reasons'), summary_sha256=sha(result_path),
            frozen_inputs_sha256=sha(path / 'frozen-inputs.json'),
            scheduler_gc_policy_sha256=result['scheduler_gc_policy_sha256'],
            scheduler_gc_receipt_sha256=result['scheduler_gc_receipt']['sha256'],
            resource_sampling_policy_sha256=result['resource_sampling_policy_sha256'],
            generator_resources_sha256=result['generator_resource_observer']['sha256'])
        ctx.stable()
        checkpoint()
        print(json.dumps(row), flush=True)
        return qualifies

    checkpoint()
    low = high = None
    try:
        # Same ordered ladder, extension, integer refinement and confirmation
        # statements as database_observer_calibrate.py. No stage is rerun.
        for rate in calibration['database_rates']:
            if cell(rate): low = rate
            else: high = rate; break
        need(low is not None, 'No passing low point; inspect without relaxing criteria')
        while high is None:
            rate = low * 2
            if rate > 10000 or math.ceil(calibration['confirmation_seconds'] * 1e9 / round(1e9 / rate)) + 1 > 1_000_000:
                break
            if cell(rate): low = rate
            else: high = rate
        while high is not None and high - low > max(1, low * .1):
            rate = (low + high) // 2
            if cell(rate, phase='refine'): low = rate
            else: high = rate
        for attempt in range(calibration['confirmation_attempt_limit']):
            passed = [cell(low, seconds=calibration['confirmation_seconds'], phase=f'confirmation-{index}')
                      for index in range(calibration['confirmation_fresh_processes'])]
            if all(passed): break
            high = low; low = max(1, math.floor(low * .9))
            cell(low, phase='confirmation-step-down')
        else:
            raise RuntimeError('No consistently passing confirmation point')
        ctx.stable()
        receipt.update(state='completed', completed_utc=ctx.owner.utc())
        checkpoint()
        fixed = ctx.freeze['long_groups'][args.group]['rate_per_second']
        selection = dict(group=args.group, variant=args.role, compact_observation=True,
            highest_consistently_passing_rate=low, first_failing_bracket_rate=high,
            long_rate=fixed if args.role == 'before' else None, paired_long_rate_already_frozen=fixed,
            fixed_long_rate_within_confirmed_capacity=low >= fixed, concurrency=16, completed_utc=ctx.owner.utc(),
            policy_sha256=sha(ctx.policy_path), controller_sha256=sha(output / 'controller.json'),
            higher_failed_points=[{key: row.get(key) for key in ('rate', 'phase', 'valid', 'qualifies', 'invalid_reasons')}
                                  for row in rows if row['rate'] > low and not row.get('qualifies')],
            capacity_scope='Largest consistently passing sampled offered rate; generator failures do not establish a server-capacity upper bound. An unbracketed result is a measured lower bound.',
            long_rate_scope='Epoch-002 retains PG144/SQLite40. The original 80% proposal cannot retune either paired long rate.')
        ctx.owner.save(output / 'selection.json', selection)
        print(json.dumps(selection), flush=True)
    except BaseException as error:
        receipt.update(state='interrupted-or-failed', finished_utc=ctx.owner.utc(), error=type(error).__name__ + ': ' + str(error))
        checkpoint()
        raise


if __name__ == '__main__':
    main()
