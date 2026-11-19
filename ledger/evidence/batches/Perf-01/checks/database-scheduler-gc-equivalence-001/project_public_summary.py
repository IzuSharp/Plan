"""Publish only allowlisted synthetic performance numbers and audit checks."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analysis', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.analysis.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '5b0d75fed3ed26a06ed0d4ffd35196952eabfaf3627ec0bee93bb98acf981769'
    source = json.loads(raw)
    assert len(source['checklist']) == 104 and all(c['passed'] is True for c in source['checklist'])
    result = {k: source[k] for k in (
        'task', 'schema_version', 'kind', 'duration_credit_seconds',
        'formal_long_timing_eligible', 'product_performance_gain_claimed',
        'short_pair_semantic_and_declared_service_gate_passed',
        'scheduler_measurement_peak_rss_delta_bytes', 'long_resource_clearance',
        'limitations', 'extractor_sha256', 'started_utc', 'ended_utc')}
    result['original_private_analysis_sha256'] = hashlib.sha256(raw).hexdigest()
    result['projection_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['publication_scope'] = 'Synthetic comparison numbers, resource aggregates and audit checklist only; original raw controls and receipts remain local.'
    result['checklist'] = [{'name': c['name'], 'passed': c['passed']} for c in source['checklist']]
    result['cells'] = {}
    resource_keys = ('cpu_percent_one_core', 'cpu_samples', 'cpu_seconds',
                     'cpu_span_seconds', 'fd_peak_count', 'rss_peak_bytes',
                     'samples', 'socket_peak_count')
    for mode in ('automatic', 'deferred'):
        c = source['cells'][mode]
        out = {k: c[k] for k in (
            'all_expected_values_matched', 'arrival_latency_ns', 'dataset_sha256',
            'durable_counts_after_recovery', 'durable_counts_before_recovery',
            'idle_duration_ns', 'mix', 'observation_sha256', 'operations',
            'policy_gc_collections', 'recovery_operations',
            'successful_per_second', 'summary_sha256', 'supervision_cleanup_passed')}
        out['effective_duration_ns'] = c['measurement_window']['elapsed']
        out['dispatch'] = {k: c['dispatch'][k] for k in (
            'above_100ms', 'above_50ms', 'maximum_ns', 'mean_ns',
            'p50_ns', 'p95_ns', 'p99_ns', 'span_ns')}
        out['loaded_files_sha256'] = {Path(k).name: v for k, v in c['loaded_files'].items()}
        out['application_resource_aggregates'] = {
            phase: {k: metrics[k] for k in resource_keys if k in metrics}
            for phase, metrics in c['application_resources'].items()}
        out['generator_resource_aggregates'] = {}
        for role, phases in c['generator_resources'].items():
            out['generator_resource_aggregates'][role] = {}
            for phase, metrics in phases.items():
                selected = {k: metrics[k] for k in resource_keys if k in metrics}
                selected['first_rss_bytes'] = metrics['first']['rss_bytes']
                selected['last_rss_bytes'] = metrics['last']['rss_bytes']
                out['generator_resource_aggregates'][role][phase] = selected
        result['cells'][mode] = out
    assert not args.output.exists()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'output_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'checks': 104, 'duration_credit_seconds': 0}))


if __name__ == '__main__':
    main()
