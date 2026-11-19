"""Publish only numerical gRPC profile observations and explicit identities."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def take(value, keys):
    return {key: value[key] for key in keys}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    base = args.root / 'perf01-evidence/profiling/before'
    execution_path = args.root / 'perf01-run/grpc-mode-profiles-before-001-execution.json'
    execution = json.loads(execution_path.read_text())
    assert execution['state'] == 'completed' and len(execution['commands']) == 16
    assert all(c['exit_code'] == 0 for c in execution['commands'])
    rows = []
    common_identity = None
    for mode in ('unary', 'server-stream', 'client-stream', 'duplex'):
        cell = base / ('grpc-' + mode + '-resources-001')
        observation = cell.with_name(cell.name + '-observation.json')
        o = json.loads(observation.read_text())['observation']
        result_path = cell / 'result.json'
        r = json.loads(result_path.read_text())
        assert o['result_sha256'] == sha(result_path)
        assert o['eligible'] is False
        assert o['issues'] == ['Profiling-only cell cannot establish a timing comparison']
        assert len(o['scenarios']) == 1
        scenario = next(iter(o['scenarios'].values()))
        assert scenario['offered'] == scenario['successful_calls'] == 323
        assert scenario['unexpected_errors'] == scenario['correctness_failures'] == 0
        assert scenario['wire_statuses'] == {'GrpcOK': 323}
        assert r['valid'] and r['service_standard_met'] and r['idle_owner_and_request_gauges_receded']
        assert r['recovery']['status'] == r['retirement']['status'] == 'passed'
        assert not r['retirement']['errors']
        assert all(v == 0 for v in o['resources']['after_idle_gauges'].values())
        identity = take(o['build'], ['product_source_commit', 'product_source_dirty',
                        'nativeweave_package_version', 'build_manifest_sha256',
                        'server_executable_sha256', 'client_executable_sha256',
                        'native_producer_manifest_sha256'])
        for field in ('actual_loaded_native_sha256', 'package_archives_sha256'):
            values = o['build'][field]
            identity[field] = {Path(k).name: v for k, v in values.items()}
            assert len(identity[field]) == len(values)
        if common_identity is None:
            common_identity = identity
        assert common_identity == identity
        resources = o['resources']
        processes = {role: take(value, ['cpu_percent_one_core', 'cpu_seconds',
                     'rss_bytes_first', 'rss_bytes_last', 'rss_bytes_maximum',
                     'threads_first', 'threads_last', 'threads_maximum',
                     'fd_count_maximum', 'socket_count_maximum'])
                     for role, value in resources['processes'].items()}
        rows.append({
            'mode': mode, 'profile_sha256': sha(cell / 'profiling.json'),
            'result_sha256': sha(result_path), 'observation_sha256': sha(observation),
            'window': take(o['measurement_window'], ['first_dispatch_utc', 'last_dispatch_utc',
                           'actual_dispatch_span_ns', 'elapsed_ns']),
            'configured_concurrency': 4, 'planned_calls_per_second': 16,
            'maximum_in_progress_calls': r['independent_client']['maximum_in_progress_calls'],
            'configured_payload_bytes': scenario['configured_payload_bytes'],
            'configured_messages': scenario['configured_messages'],
            'offered_calls': scenario['offered'], 'successful_calls': scenario['successful_calls'],
            'unexpected_errors': scenario['unexpected_errors'],
            'correctness_failures': scenario['correctness_failures'],
            'metrics': scenario['metrics'], 'successful_totals': scenario['successful_totals'],
            'managed_gc': resources['managed_gc'],
            'managed_allocation_bracket': take(resources['managed_gc_observation'],
                ['allocated_bytes_delta', 'allocated_mib_per_second', 'first_timestamp',
                 'last_timestamp', 'sample_count', 'seconds', 'timestamp_frequency']),
            'processes': processes,
            'native_gauges_maximum': resources['native_gauges_maximum'],
            'after_idle_gauges': resources['after_idle_gauges'],
            'checks': {'correctness_and_status_trailers_passed': True,
                       'resource_and_service_gates_passed': True, 'recovery_passed': True,
                       'normal_retirement_passed': True, 'all_idle_gauges_zero': True},
        })
    output = {'task': 'Perf-01', 'schema_version': 1, 'variant': 'before',
              'formal_timing_eligible': False, 'duration_credit_seconds': 0,
              'protocol_compression': 'identity',
              'scope': 'Whole-server allocation/GC observation brackets; descriptive single-process mode profiles, no stack attribution or formal timing comparison',
              'execution_started_utc': execution['started_utc'],
              'execution_ended_utc': execution['ended_utc'],
              'execution_sha256': sha(execution_path), 'all_sixteen_actual_exits_zero': True,
              'published_configuration_commit': execution['published_commit'],
              'commands_sha256': execution['commands_sha256'],
              'projection_source_sha256': sha(Path(__file__)), 'identity': common_identity,
              'modes': rows}
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    for row in rows:
        print(json.dumps({'mode': row['mode'], 'successful': row['successful_calls'],
              'p99_ms': row['metrics']['arrival_p99_ns'] / 1e6,
              'allocation_mib_s': row['managed_allocation_bracket']['allocated_mib_per_second'],
              'sampled_server_rss_mib': row['processes']['server']['rss_bytes_maximum'] / 2**20,
              'maximum_in_progress_calls': row['maximum_in_progress_calls']}))
    print(json.dumps({'summary_sha256': sha(args.output)}))


if __name__ == '__main__':
    main()
