#!/usr/bin/env python3
"""Present hash-bound Perf-01 epoch-002 receipts; never measure or grant credit."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
GROUPS = ('postgresql', 'sqlite', 'http', 'grpc', 'codec')
ROLES = ('before', 'after', 'direct')
BEFORE = 'ea5fa528035d025bd7a28698ee7c71194432236c'
DRIVER = '2e3995df8d86583ee9443348276ca8d918056bfc'
SHA = re.compile(r'[0-9a-f]{64}\Z')
PAIRS = {'after_minus_before': ('before', 'after'),
         'before_minus_direct': ('direct', 'before'), 'after_minus_direct': ('direct', 'after')}


def need(value, message):
    if not value:
        raise ValueError(message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def get(value, *keys):
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def scaled(value, divisor):
    return value / divisor if finite(value) else None


def total(values):
    return sum(values) if values and all(finite(v) for v in values) else None


def mean(values):
    value = total(values)
    return value / len(values) if value is not None else None


def changes(roles):
    result = {}
    for label, (old, new) in PAIRS.items():
        result[label] = {}
        for key in roles.get(old, {}).keys() | roles.get(new, {}).keys():
            left, right = roles.get(old, {}).get(key), roles.get(new, {}).get(key)
            available = finite(left) and finite(right)
            result[label][key] = dict(absolute=right-left if available else None,
                percent=100*(right-left)/left if available and left else None)
    return result


class Evidence:
    def __init__(self, root):
        self.root = root.resolve(strict=True)
        self.files, self.stamps, self.documents = {}, {}, {}
        self.reader = None

    def path(self, name):
        path = Path(name)
        path = (path if path.is_absolute() else self.root / path).resolve()
        need(path.is_relative_to(self.root), 'Input escapes the explicit root: ' + str(path))
        return path

    def pin(self, ref):
        need(isinstance(ref, dict) and SHA.fullmatch(ref.get('sha256', '')), 'Missing exact input SHA-256')
        path = self.path(ref['path'])
        key = str(path)
        if key not in self.files:
            before = path.stat()
            with path.open('rb') as stream:
                actual = hashlib.file_digest(stream, 'sha256').hexdigest()
            after = path.stat()
            signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
            need(signature(before) == signature(after), 'Input changed during hashing: ' + key)
            self.files[key], self.stamps[key] = actual, signature(after)
        need(self.files[key] == ref['sha256'], 'Input hash differs: ' + key)
        return path

    def read(self, ref, selection=None):
        path = self.pin(ref)
        if selection is not None:
            need(self.reader is not None, 'Original streaming reader is not bound')
            with path.open(encoding='utf-8') as stream:
                parser = self.reader.JsonStream(stream)
                value = parser.selected_object(selection)
                need(parser.peek() == '', 'Trailing protocol result content')
            return value
        if str(path) not in self.documents:
            need(path.stat().st_size <= 64*1024**2, 'Control file exceeds 64 MiB: ' + str(path))
            def invalid(value):
                raise ValueError('Nonfinite JSON value: ' + value)
            self.documents[str(path)] = json.loads(path.read_text(), parse_constant=invalid)
        return self.documents[str(path)]

    def finish(self):
        for name, stamp in self.stamps.items():
            s = Path(name).stat()
            need(stamp == (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns), 'Input changed while presenting: ' + name)


class Report:
    def __init__(self, evidence, manifest, manifest_ref, index_ref, schema_hashes):
        self.e, self.m = evidence, manifest
        need((manifest['schema_version'], manifest['task'], manifest['epoch']) == (1, 'Perf-01', 'recovery-002'), 'Wrong report manifest')
        self.admission = evidence.read(manifest['admission'])
        self.source = evidence.read(manifest['measurement_sources'])
        for section, files in schema_hashes.items():
            need(all(self.source[section].get(name) == digest for name, digest in files.items()), 'Input schema source differs: ' + section)
        need(self.admission['epoch'] == self.source['epoch'] == 'recovery-002'
             and self.admission['selected_final_commit'] is None
             and self.source['baseline_commit'] == BEFORE and self.source['driver_commit'] == DRIVER, 'Historical or wrong source/admission context')
        self.build_inputs = evidence.read(self.admission['build_inputs'])
        self.freeze = evidence.read(self.build_inputs['freeze'])
        need(self.freeze['epoch'] == 'recovery-002' and self.freeze['baseline_product_commit'] == BEFORE
             and self.freeze['driver_checkout_commit'] == DRIVER, 'Wrong frozen source roles')
        self.final = evidence.read(manifest['final_binding']) if manifest.get('final_binding') else None
        if self.final:
            need(self.final['epoch'] == 'recovery-002' and self.final['before_admission_sha256'] == manifest['admission']['sha256']
                 and re.fullmatch('[0-9a-f]{40}', self.final['selected_final_commit']), 'Wrong final binding')
        batch = evidence.path(self.admission['plan']) / 'ledger/evidence/batches/Perf-01'
        name = 'reproduction/workloads-001/workloads.json'
        self.workloads = evidence.read(dict(path=str(batch / name), sha256=self.source['plan_source_sha256'][name]))
        reader_path = evidence.path(self.build_inputs['driver']) / 'tests/Perf01/verify_long.py'
        evidence.pin(dict(path=str(reader_path), sha256=self.source['native_source_sha256']['tests/Perf01/verify_long.py']))
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location('perf01_report_original_reader', reader_path)
        evidence.reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evidence.reader)
        self.value = dict(schema_version=1, task='Perf-01', epoch='recovery-002', kind='presentation-only',
            created_utc=datetime.now(timezone.utc).isoformat(), manifest=manifest_ref, adapter_source_index=index_ref,
            rows=[], resources=[], capacity=[], long_ledger=[], attempts=[], issues=[],
            identities=dict(baseline_commit=BEFORE, driver_commit=DRIVER,
                design_commit=self.freeze['design_commit'], freeze=self.build_inputs['freeze'],
                build_inputs=self.admission['build_inputs'], build_source_index=self.admission['build_source_index'],
                toolchain=self.build_inputs['toolchain'], python_dependencies=self.build_inputs['python_dependencies'],
                selected_final_commit=self.final['selected_final_commit'] if self.final else None,
                admission=manifest['admission'], measurement_sources=manifest['measurement_sources'],
                final_binding=manifest.get('final_binding'), builds={}, measured_cells=[]),
            definitions=[
                'DB/protocol p99 is an equal-weight mean of process p99 values; codec p99 pools exact successful samples. No percentile is recomputed here.',
                'All latency starts at scheduled arrival unless explicitly called isolated codec call time. A21 decisions concern process means, not p99 or throughput changes.',
                'Resources describe whole mixed applications/profiles. Resource rows must not be summed across conditional scenarios or codec partitions.',
                'CPU is percent of one core. DB/protocol CPU is an equal-weight process mean; codec CPU is summed bracket CPU / summed observation time. RSS is the largest sampled process peak.',
                'Negative latency deltas mean lower latency. Percent is (candidate-reference)/reference*100; Rust is the direct-gap denominator. Zero or missing denominator gives N/A.',
                'Error/count totals are integers, not means. Expected protocol cancellation/deadline probes are separate from successful business throughput.',
                'Capacity is the original largest consistently passing sampled offered rate. A generator-invalid upper point is not a server-capacity bound.',
                'Existing accepted long seconds are copied from the bound original verifier. This adapter grants no acceptance or new measurement credit.',
                'A hash-bound receipt is presented without rerunning payload, persistence or binary checks. Historical rows are not transferred. Missing or failed inputs remain visible.'])

    def bindings(self, execution):
        for role, proof in execution['build_proofs'].items():
            existing = self.value['identities']['builds'].get(role)
            if existing:
                need(existing['proof'] == proof, 'One role has differing producing receipts')
                continue
            produced = self.e.read(dict(path=proof['execution'], sha256=proof['execution_sha256']))
            bound = self.e.read(dict(path=proof['binding'], sha256=proof['binding_sha256']))
            need(produced['epoch'] == 'recovery-002' and produced['status'] == 'completed'
                 and produced['inputs_sha256'] == self.admission['build_inputs']['sha256']
                 and produced['source_index_sha256'] == self.admission['build_source_index']['sha256']
                 and produced['toolchain_sha256'] == self.build_inputs['toolchain']['sha256']
                 and produced['freeze_sha256'] == self.build_inputs['freeze']['sha256']
                 and produced['binding_sha256'] == proof['binding_sha256'] and bound['status'] == 'built-and-bound', 'Producer binding differs')
            if role in ('before', 'after'):
                need(bound['product_commit'] == (BEFORE if role == 'before' else self.final['selected_final_commit'])
                     and bound['driver_commit'] == DRIVER, 'Producer source role differs')
            self.value['identities']['builds'][role] = dict(proof=proof,
                metadata={k: bound.get(k) for k in ('product_commit', 'driver_commit', 'selected_b24_version', 'resolved_packages', 'native_assets', 'files_sha256')})

    def execution(self, entry, stage):
        ref = entry.get('execution')
        if ref is None:
            return None
        x = self.e.read(ref)
        need((x['task'], x['epoch'], x['stage'], x['group']) == ('Perf-01', 'recovery-002', stage, entry['group'])
             and x['admission_sha256'] == self.m['admission']['sha256']
             and x['measurement_source_index_sha256'] == self.m['measurement_sources']['sha256'], 'Execution belongs to another context')
        need(stage != 'compare' or x['scene'] == entry['scene'], 'Comparison scene differs')
        need(stage not in ('long', 'capacity') or x['role'] == entry['role'], 'Execution role differs')
        if stage == 'compare' or x['role'] == 'after':
            need(self.final is not None and x['selected_final_commit'] == self.final['selected_final_commit']
                 and x['final_binding']['sha256'] == self.m['final_binding']['sha256'], 'Execution has another final product')
        self.bindings(x)
        attempt = dict(stage=stage, group=x['group'], scene=x.get('scene'), role=x['role'], execution=ref,
                       status=x['status'], started_utc=x.get('started_utc'), ended_utc=x.get('ended_utc'), failure=x.get('failure'))
        self.value['attempts'].append(attempt)
        if x['status'] != 'completed':
            return None
        need(len(x['commands']) == len(x['planned_commands']) > 0, 'Incomplete command population')
        for child in x['commands']:
            receipt = self.e.read(child)
            need(receipt['status'] == 'completed' and receipt['retired'] is True and receipt['exit_code'] == 0, 'Completed execution has failed/unretired command')
        return x

    def resource(self, group, scene, roles, aggregation):
        key = group + '/' + scene
        self.value['resources'].append(dict(key=key, group=group, scene=scene, scope='whole mixed application/profile',
            aggregation=aggregation, roles=roles, changes=changes(roles)))
        return key

    def row(self, group, scene, key, roles, load, aggregation, resource, interpretation, detail=None):
        self.value['rows'].append(dict(group=group, scene=scene, scenario=key, roles=roles, load=load,
            latency_aggregation=aggregation, resource_key=resource, changes=changes(roles),
            interpretation=interpretation, detail=detail))

    def compare(self, entry, x):
        r = self.e.read(x['comparison_receipt'])
        group, scene = entry['group'], entry['scene']
        expected = {(str(self.e.path(c['directory'])), c['role']): c['result'] for c in x['cells']}
        observed = {}
        for role, cohort in r['cohorts'].items():
            cells = cohort['processes'] if group in ('postgresql', 'sqlite') else cohort['cells'] if group == 'codec' else cohort
            for cell in cells:
                key = (str(self.e.path(cell['directory'])), role)
                need(key in expected and key not in observed, 'Comparison contains unbound/repeated process')
                digest = cell['evidence_sha256']['summary.json'] if group in ('postgresql', 'sqlite') else cell['summary_sha256'] if group == 'codec' else cell['result_sha256']
                need(digest == expected[key]['summary_sha256' if group in ('postgresql', 'sqlite', 'codec') else 'result_sha256'], 'Comparison process differs from outer execution')
                observed[key] = True
                identity_keys = ('route_identity', 'loaded_files', 'driver_source_files') if group in ('postgresql', 'sqlite') else ('source_commit', 'build_manifest_sha256', 'executable_sha256', 'actual_loaded_native') if group == 'codec' else ('build',)
                self.value['identities']['measured_cells'].append(dict(group=group, scene=scene, role=role,
                    directory=key[0], metadata={k: cell.get(k) for k in identity_keys}))
        need(set(observed) == set(expected), 'Comparison dropped an executed process')
        need(all(role in r['cohorts'] for role in ROLES), 'Missing before/after/direct cohort')
        resources = {}
        for role in ROLES:
            if group in ('postgresql', 'sqlite'):
                c = r['cohorts'][role]['resources']
                cpu, rss = c['app_cpu_percent_one_core']['mean'], c['rss_peak_bytes']['maximum']
            elif group == 'codec':
                c = r['cohorts'][role]['mixed_resource_summary']
                cpu, rss = c['target_cpu_percent_one_core'], c['target_rss_sample_peak_bytes']
            else:
                c = r['whole_profile_resources']['metrics']
                cpu, rss = c['server_cpu_percent_one_core']['routes'][role]['mean'], c['server_rss_bytes_maximum']['routes'][role]['maximum']
            resources[role] = dict(cpu_percent_one_core=cpu, sampled_peak_rss_mib=scaled(rss, 1048576))
        resource = self.resource(group, scene, resources, 'CPU: duration-weighted; RSS: maximum sampled peak' if group == 'codec' else 'CPU: equal-weight process mean; RSS: maximum process peak')
        if group in ('postgresql', 'sqlite'):
            config = r['configuration']
            need(config['provider'] == group, 'Database provider differs')
            for scope in r['cohorts']['before']['scopes']:
                roles = {}
                for role in ROLES:
                    c = r['cohorts'][role]['scopes'][scope]
                    roles[role] = dict(successful_per_second=c['successful_per_second']['mean'],
                        **{p+'_ms': scaled(c[p+'_ns']['mean'], 1e6) for p in ('p50', 'p95', 'p99')},
                        errors=total(c['errors']['values']), successful=total(c['successful']['values']), offered=total(c['offered']['values']))
                decisions = [d for d in r['comparisons'] if (d['baseline_role'], d['candidate_role'], d['scope']) == ('before', 'after', scope)]
                need(len(decisions) == 1, 'Missing original database comparison decision')
                self.row(group, scene, scope, roles, {k: config[k] for k in ('rate', 'concurrency', 'scenario')},
                    'mean of independent-process percentiles', resource,
                    dict(eligible=decisions[0]['eligible'], noise=decisions[0]['noise_on_process_means']),
                    {role: dict(counts=r['cohorts'][role]['counts'], outcomes=r['cohorts'][role]['scopes'][scope]['outcomes_total']) for role in ROLES})
        elif group == 'codec':
            need(r['kind'] == 'codec-observed-comparison', 'Wrong codec report schema')
            cell = r['cohorts']['before']['cells'][0]
            plan = self.e.read(dict(path=str(self.e.path(cell['directory']) / 'plan.json'), sha256=cell['files_sha256']['plan.json']))
            load = {k: plan[k] for k in ('planned_rate', 'workers', 'queue_capacity', 'max_in_flight')}
            for row in r['rows']:
                roles = {}
                for role in ROLES:
                    c = row['observed'][role]
                    roles[role] = dict(successful_per_second=c['successes_per_second'],
                        **{p+'_ms': scaled(c['latency']['arrival_ns'][p], 1e6) for p in ('p50', 'p95', 'p99')},
                        call_mean_us=scaled(c['latency']['call_ns']['mean_ns'], 1000), successful=c['successes'], errors=0,
                        raw_mib_per_second_wall=c['raw_mib_per_second_wall'], raw_mib_per_second_summed_call=c['raw_mib_per_second_summed_call'],
                        raw_over_encoded_ratio=c['raw_over_encoded_ratio'], **c['counter_per_success'])
                self.row(group, scene, row['key'], roles, load, 'pooled exact successful-sample percentiles', resource,
                    dict(eligible=True, basis='original codec extractor completed', noise=row['noise']['after_vs_before']),
                    dict(case=row['case'], action=row['action'], interface=row['interface'], managed_scope=row.get('managed_scope'),
                         managed_observation=row['observed'].get('managed')))
        else:
            need(r['kind'] == 'protocol-comparison', 'Wrong protocol report schema')
            load = {k: r['cohorts']['before'][0]['signature']['schedule'][k] for k in ('rate', 'concurrency', 'duration_seconds')}
            for key, row in r['ordinary_scenarios'].items():
                roles = {}
                for role in ROLES:
                    c = row['routes'][role]
                    roles[role] = dict(successful_per_second=c['metrics']['successful_calls_per_second']['mean'],
                        **{p+'_ms': scaled(c['metrics']['arrival_'+p+'_ns']['mean'], 1e6) for p in ('p50', 'p95', 'p99')},
                        errors=c['unexpected_errors'], successful=c['successful_calls'], offered=c['offered'],
                        **{k: v['mean'] for k, v in c['metrics'].items() if k.endswith('_per_second') and k != 'successful_calls_per_second'})
                self.row(group, scene, key, roles, load, 'mean of three process percentiles', resource,
                    dict(eligible=row['comparative_interpretation_eligible'], noise=row['noise']),
                    dict(successful_totals={role: row['routes'][role]['successful_totals'] for role in ROLES},
                         expected_probes=r['expected_probes'], profile_issues=r['issues']))

    def capacity(self, entry, x):
        selected = self.e.read(x['capacity']['selection'])
        controller = self.e.read(x['capacity']['controller'])
        need(selected['controller_sha256'] == x['capacity']['controller']['sha256'] and controller['state'] == 'completed', 'Capacity controller binding differs')
        cells = controller['cells'][-3:]
        low = selected['highest_consistently_passing_rate']
        need(len(cells) == 3 and all(c['phase'] == f'confirmation-{i}' and c['rate'] == low and c['seconds'] == 60
             and c['qualifies'] is True and c['exit_code'] == 0 for i, c in enumerate(cells)), 'Missing original three confirmations')
        protocol = entry['group'] in ('http', 'grpc')
        values = dict(offered_capacity_per_second=low,
            successful_per_second=mean([c.get('business_throughput' if protocol else 'throughput') for c in cells]),
            logical_successful_per_second=mean([c.get('throughput') for c in cells]),
            p99_ms=scaled(mean([c.get('p99_ns') for c in cells]), 1e6),
            cpu_percent_one_core=mean([c.get('cpu_percent_one_core') for c in cells]),
            sampled_peak_rss_mib=scaled(max([c['rss_peak_bytes'] for c in cells]) if all(finite(c.get('rss_peak_bytes')) for c in cells) else None, 1048576),
            errors=total([c['offered']-c['successes'] if finite(c.get('offered')) and finite(c.get('successes')) else None for c in cells]))
        return dict(values=values, selection=x['capacity']['selection'], controller=x['capacity']['controller'],
            confirmations=[{k: c.get(k) for k in ('directory', 'rate', 'seconds', 'phase', 'qualifies', 'offered', 'successes', 'business_successes', 'throughput', 'business_throughput', 'p99_ns', 'cpu_percent_one_core', 'rss_peak_bytes')} for c in cells],
            higher_failed_points=selected['higher_failed_points'], first_failing_bracket_rate=selected['first_failing_bracket_rate'],
            scope=selected['capacity_scope'], concurrency=selected.get('concurrency'), workers=selected.get('workers'))

    def long(self, entry, x):
        verification = self.e.read(x['long_verification'])
        need(verification['group'] == entry['group'] and verification['verifier_sha256'] == self.source['native_source_sha256']['tests/Perf01/verify_long.py'], 'Wrong long verifier/group')
        need(len(x['cells']) == 1 and x['cells'][0]['role'] == entry['role'], 'Long cell population differs')
        cell = x['cells'][0]
        root = self.e.path(cell['directory'])
        hashes = verification['evidence_sha256']
        def doc(name, selection=None):
            return self.e.read(dict(path=str(root/name), sha256=hashes[name]), selection)
        group = entry['group']
        accepted = verification['accepted'] is True
        need(verification['duration_credit_seconds'] == x['duration_credit_seconds'], 'Long credit differs between bound receipts')
        need(not accepted or verification['duration_credit_seconds'] >= 1800
             and get(verification, 'duration_proof', 'duration_proved') is True, 'Accepted long receipt lacks its recorded duration proof')
        value = dict(group=group, role=entry['role'], status='accepted' if accepted else 'rejected', execution=entry['execution'],
            verification=x['long_verification'], accepted=accepted, effective_seconds=verification['duration_credit_seconds'],
            duration_proof=verification.get('duration_proof'), failure_reasons=verification['failure_reasons'],
            p99_ms=scaled(verification.get('driver_arrival_p99_ns'), 1e6),
            sampled_peak_rss_mib=scaled(get(verification, 'resources', 'rss_peak_bytes'), 1048576),
            identities=verification['original_checked_identities'], load=self.freeze['long_groups'][group],
            raw_evidence_sha256=hashes, outer_started_utc=x['started_utc'], outer_ended_utc=x['ended_utc'])
        if group in ('postgresql', 'sqlite'):
            s = doc('summary.json')
            need(hashes['summary.json'] == cell['result']['summary_sha256'], 'Long DB result differs from execution')
            value.update(start_utc=s['phases']['load']['start_utc'], end_utc=s['phases']['load']['last_completion_utc'],
                utc_scope='actual target load dispatch to last observed completion', successful_per_second=s['successful_per_second'],
                p50_ms=scaled(s['p50_ns'], 1e6), p95_ms=scaled(s['p95_ns'], 1e6), outcomes=s['outcomes'],
                cpu_percent_one_core=get(s, 'resources', 'measurement', 'app_cpu_percent_one_core'),
                resources=s['resources'], generator_resources=s['generator_resources'], drain=s['closed'],
                recovery=s['phases']['recovery'], idle=s['phases']['idle'], correctness=s['durable_oracle'],
                persistence=s['persisted_before_recovery'], provider_errors=s['provider_errors'], business_retry_attempts=s['business_retry_attempts'])
        elif group == 'codec':
            s, result = doc('summary.json'), doc('result.json')
            need(hashes['summary.json'] == cell['result']['summary_sha256'] and hashes['result.json'] == cell['result']['result_sha256'], 'Long codec result differs from execution')
            value.update(start_utc=result['measurement_start_utc'], end_utc=result['measurement_end_utc'],
                utc_scope='scheduled measurement origin to last observed completion', successful_per_second=s['successful_operations_per_second'],
                p50_ms=scaled(s['arrival_success_ns']['p50'], 1e6), p95_ms=scaled(s['arrival_success_ns']['p95'], 1e6),
                outcomes=result['operation_outcomes'], cpu_percent_one_core=s['target_cpu_percent_one_core'],
                resources=dict(before=result['measurement_resources_before'], after=result['measurement_resources_after']),
                drain=dict(drained_at_utc=result['drained_at_utc'], checked_by_original_verifier=accepted),
                idle=dict(seconds=result['idle_observation_seconds']), recovery=dict(passed=result['recovery_standard_met'], counts=result['phase_counts']['recovery']),
                codec_partitions=s['groups'],
                codec_action_successes={action: sum(row['successes'] for key, row in s['groups'].items() if key.split('/')[0] == code) for action, code in (('compress', 'c'), ('decompress', 'd'))})
        else:
            selection = dict.fromkeys(('measurement_window', 'independent_client', 'resources', 'managed_gc', 'native_gauges_maximum',
                'after_idle_gauges', 'recovery', 'outcome_counts', 'idle_owner_and_request_gauges_receded'))
            selection['histograms'] = {'arrival_success': {'percentiles_from_exact_samples_ns': dict.fromkeys(('p50', 'p95', 'p99'))}}
            result, retirement = doc('result.json', selection), doc('execution/receipt.json')
            need(hashes['result.json'] == cell['result']['result_sha256'], 'Long protocol result differs from execution')
            window = result['measurement_window']
            value.update(start_utc=window['start_utc'], end_utc=window['end_utc'], utc_scope='scheduled measurement origin to last controller completion',
                first_dispatch_utc=window.get('first_dispatch_utc'), last_dispatch_utc=window.get('last_dispatch_utc'),
                successful_per_second=result['independent_client']['business_success_per_second'],
                p50_ms=scaled(result['histograms']['arrival_success']['percentiles_from_exact_samples_ns']['p50'], 1e6),
                p95_ms=scaled(result['histograms']['arrival_success']['percentiles_from_exact_samples_ns']['p95'], 1e6),
                latency_scope='whole-cell successful logical checks, including expected control probes', outcomes=result['outcome_counts'],
                cpu_percent_one_core=get(result, 'resources', 'server', 'cpu_percent_one_core'), resources=result['resources'],
                managed_gc=result['managed_gc'], native_gauges_maximum=result['native_gauges_maximum'], after_idle_gauges=result['after_idle_gauges'],
                drain=retirement['closed'], recovery=result['recovery'], idle={k: retirement[k] for k in ('idle_start_utc_ns', 'idle_end_utc_ns', 'after_idle_resources')},
                independent_client=result['independent_client'])
        outcomes = value['outcomes']
        value['errors'] = sum(count for name, count in outcomes.items() if name != 'ok')
        return value

    def execute(self):
        expected_comparisons = {(g, s['id']) for g in ('postgresql', 'sqlite') for s in self.workloads['database']['strata']}
        expected_comparisons |= {(p['group'], p['id']) for p in self.workloads['protocol']['profiles'] if p['kind'] == 'fixed-short'}
        expected_comparisons |= {('codec', s['id']) for s in self.workloads['codec']['strata']}
        def entries(name, expected, field):
            result = {}
            for entry in self.m[name]:
                key = (entry['group'], entry[field])
                need(key in expected and key not in result, 'Unknown/duplicate manifest slot: ' + repr(key))
                result[key] = entry
            return {key: result.get(key, dict(group=key[0], **{field: key[1]}, execution=None)) for key in sorted(expected)}
        slots = entries('comparisons', expected_comparisons, 'scene')
        self.value['comparison_slots'] = []
        for key, entry in slots.items():
            status = dict(group=key[0], scene=key[1], status='missing', execution=entry.get('execution'))
            lengths = {name: len(self.value[name]) for name in ('rows', 'resources')}
            identity_length = len(self.value['identities']['measured_cells'])
            try:
                x = self.execution(entry, 'compare')
                if x is not None:
                    self.compare(entry, x)
                    status.update(status='presented', receipt=x['comparison_receipt'])
                elif entry.get('execution'):
                    status['status'] = 'failed-or-incomplete'
            except (ValueError, KeyError, TypeError, OSError, IndexError) as error:
                for name, length in lengths.items(): del self.value[name][length:]
                del self.value['identities']['measured_cells'][identity_length:]
                status.update(status='binding-or-schema-error', reason=str(error))
                self.value['issues'].append(dict(slot=list(key), stage='compare', reason=str(error)))
            self.value['comparison_slots'].append(status)
        capacities = entries('capacities', {(g, r) for g in GROUPS for r in ROLES}, 'role')
        for group in GROUPS:
            row = dict(group=group, roles={}, details={})
            for role in ROLES:
                entry = capacities[(group, role)]
                try:
                    x = self.execution(entry, 'capacity')
                    detail = self.capacity(entry, x) if x is not None else dict(status='failed-or-incomplete' if entry.get('execution') else 'missing')
                    detail['execution'] = entry.get('execution')
                    row['details'][role] = detail
                    row['roles'][role] = detail.get('values', {})
                except (ValueError, KeyError, TypeError, OSError, IndexError) as error:
                    row['roles'][role] = {}
                    row['details'][role] = dict(status='binding-or-schema-error', reason=str(error), execution=entry.get('execution'))
                    self.value['issues'].append(dict(stage='capacity', group=group, role=role, reason=str(error)))
            row['changes'] = changes(row['roles'])
            self.value['capacity'].append(row)
        for key, entry in entries('long_runs', {(g, r) for g in GROUPS for r in ('before', 'after')}, 'role').items():
            row = dict(group=key[0], role=key[1], status='missing', accepted=False, effective_seconds=None)
            try:
                x = self.execution(entry, 'long')
                if x is not None:
                    row = self.long(entry, x)
                elif entry.get('execution'):
                    row.update(status='failed-or-incomplete', execution=entry['execution'])
            except (ValueError, KeyError, TypeError, OSError, IndexError) as error:
                row.update(status='binding-or-schema-error', reason=str(error), execution=entry.get('execution'))
                self.value['issues'].append(dict(stage='long', group=key[0], role=key[1], reason=str(error)))
            self.value['long_ledger'].append(row)
        for entry in self.m.get('failed_attempts', []):
            try:
                need(entry.get('execution') is not None, 'A failed-attempt entry needs an actual receipt')
                x = self.execution(entry, entry['stage'])
                need(x is None, 'Completed execution listed as a failed attempt')
            except (ValueError, KeyError, TypeError, OSError, IndexError) as error:
                self.value['issues'].append(dict(stage='failed-attempt', execution=entry.get('execution'), reason=str(error)))
        self.value['coverage'] = dict(comparisons_presented=sum(s['status'] == 'presented' for s in self.value['comparison_slots']),
            comparisons_expected=len(expected_comparisons), capacity_roles_presented=sum(bool(v) for row in self.value['capacity'] for v in row['roles'].values()),
            capacity_roles_expected=15, long_segments_accepted=sum(row['accepted'] for row in self.value['long_ledger']), long_segments_expected=10,
            existing_accepted_seconds=sum(row['effective_seconds'] for row in self.value['long_ledger'] if row['accepted']))
        self.e.finish()
        self.value['inputs_sha256'] = self.e.files
        return self.value


def shown(value, digits=3):
    if value is None:
        return 'N/A'
    return f'{value:.{digits}f}' if type(value) is float else str(value)


def table(lines, headers, rows):
    escape = lambda x: shown(x).replace('|', '\\|').replace('\n', ' ')
    lines += ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join('---' for _ in headers) + ' |']
    lines += ['| ' + ' | '.join(escape(x) for x in row) + ' |' for row in rows]
    lines.append('')


def markdown(report):
    lines = ['# Perf-01 Linux x64 measured comparison', '',
        'Presentation of current-epoch receipts only. Missing, failed or ineligible observations do not establish improvement.', '',
        'Coverage: ' + json.dumps(report['coverage'], sort_keys=True) + '.', '', '## Fixed-load comparison', '',
        'B = before; A = after; D = direct Rust. Throughput is successful business operations/s. See the named whole-profile resource row; no per-partition resource attribution is implied.', '']
    rows = []
    for row in report['rows']:
        role = row['roles']; delta = row['changes']
        noise = row['interpretation']['noise']
        decision = noise.get('decision') if 'decision' in noise else 'call: ' + str(get(noise, 'call_ns', 'decision')) + '; arrival: ' + str(get(noise, 'arrival_ns', 'decision'))
        rows.append([row['group']+'/'+row['scene']+'/'+row['scenario'], json.dumps(row['load'], sort_keys=True),
            ' / '.join(shown(get(role, r, 'successful_per_second')) for r in ROLES),
            ' / '.join(shown(get(role, r, 'p99_ms')) for r in ROLES),
            get(delta, 'after_minus_before', 'successful_per_second', 'absolute'), get(delta, 'after_minus_before', 'successful_per_second', 'percent'),
            get(delta, 'after_minus_before', 'p99_ms', 'absolute'), get(delta, 'after_minus_before', 'p99_ms', 'percent'),
            get(delta, 'before_minus_direct', 'p99_ms', 'percent'), get(delta, 'after_minus_direct', 'p99_ms', 'percent'),
            ' / '.join(shown(get(role, r, 'errors')) for r in ROLES), row['latency_aggregation'], row['resource_key'],
            str(row['interpretation']['eligible'])+'; '+str(decision)])
    table(lines, ['Domain / scene / operation', 'Load', 'B / A / D success/s', 'B / A / D p99 ms', 'Throughput delta', 'Throughput delta %',
        'p99 delta ms', 'p99 delta %', 'B gap to D %', 'A gap to D %', 'B / A / D errors', 'p99 statistic', 'Resource key', 'Eligible; original A21 decision'], rows)
    lines += ['## Direct Rust distance', '', 'All gaps use the same row and statistic as above. A negative success/s gap means fewer successful operations/s than direct Rust at this fixed offered load.', '']
    table(lines, ['Domain / scene / operation', 'B p99 gap ms / %', 'A p99 gap ms / %', 'B success/s gap / %', 'A success/s gap / %'],
        [[row['group']+'/'+row['scene']+'/'+row['scenario'],
          *[' / '.join(shown(get(row, 'changes', pair, metric, k)) for k in ('absolute', 'percent'))
            for metric, pair in (('p99_ms', 'before_minus_direct'), ('p99_ms', 'after_minus_direct'),
                                 ('successful_per_second', 'before_minus_direct'), ('successful_per_second', 'after_minus_direct'))]] for row in report['rows']])
    lines += ['## Codec call and payload observations', '', 'Wall MiB/s is a contribution to the fixed mixed load. Isolated public call time, output consumption and disposal are different intervals. Source-derived copy/FFI counters do not count all hardware/native work.', '']
    table(lines, ['Scene / partition', 'B / A / D raw MiB/s wall', 'B / A / D call mean us', 'B / A / D raw/encoded ratio', 'A allocated / copied bytes per success', 'A derived FFI/success'],
        [[row['scene']+'/'+row['scenario'], *[' / '.join(shown(get(row, 'roles', r, metric)) for r in ROLES)
          for metric in ('raw_mib_per_second_wall', 'call_mean_us', 'raw_over_encoded_ratio')],
          ' / '.join(shown(get(row, 'roles', 'after', metric)) for metric in ('managed_allocated_bytes', 'copied_bytes_derived')),
          get(row, 'roles', 'after', 'ffi_calls_derived')] for row in report['rows'] if row['group'] == 'codec'])
    lines += ['## Whole-profile resources', '', 'Peak RSS is the largest sampled process peak. CPU changes in the JSON/CSV include percentage points (absolute) and relative percent.', '']
    table(lines, ['Key', 'B / A / D CPU % one core', 'B / A / D peak RSS MiB', 'CPU delta pp / %', 'RSS delta MiB / %', 'Aggregation'],
        [[row['key'], *[' / '.join(shown(get(row, 'roles', r, metric)) for r in ROLES) for metric in ('cpu_percent_one_core', 'sampled_peak_rss_mib')],
          *[' / '.join(shown(get(row, 'changes', 'after_minus_before', metric, k)) for k in ('absolute', 'percent')) for metric in ('cpu_percent_one_core', 'sampled_peak_rss_mib')], row['aggregation']] for row in report['resources']])
    lines += ['## Confirmed capacity', '', 'Successful throughput and p99 are descriptive means of the original three final confirmations. The JSON retains all three values and higher failed points. Protocol successful throughput excludes expected probes; its whole-cell p99 includes successful probes.', '']
    table(lines, ['Group', 'B / A / D offered capacity/s', 'B / A / D business success/s', 'B / A / D mean confirmation p99 ms', 'Offered delta / %', 'A offered gap to D %'],
        [[row['group'], *[' / '.join(shown(get(row, 'roles', r, metric)) for r in ROLES) for metric in ('offered_capacity_per_second', 'successful_per_second', 'p99_ms')],
          ' / '.join(shown(get(row, 'changes', 'after_minus_before', 'offered_capacity_per_second', k)) for k in ('absolute', 'percent')),
          get(row, 'changes', 'after_minus_direct', 'offered_capacity_per_second', 'percent')] for row in report['capacity']])
    lines += ['## Ten-segment long ledger', '', 'UTC endpoints describe the recorded measurement window, not verifier runtime. Effective seconds use the original ordinary-operation completion-to-later-dispatch lower bound; warmup, recovery and idle are excluded.', '']
    table(lines, ['Group / role', 'Status', 'Start UTC', 'End UTC', 'Effective s', 'Offered / ordinary successes / expected probes', 'Business success/s', 'p50 / p95 / p99 ms', 'Errors', 'CPU % / peak RSS MiB', 'Drain / recovery'],
        [[row['group']+'/'+row['role'], row['status'], row.get('start_utc'), row.get('end_utc'), row.get('effective_seconds'),
          ' / '.join(shown(get(row, 'duration_proof', k)) for k in ('offered', 'ordinary_successes', 'expected_probe_successes')),
          row.get('successful_per_second'), ' / '.join(shown(row.get(p+'_ms')) for p in ('p50', 'p95', 'p99')), row.get('errors'),
          shown(row.get('cpu_percent_one_core'))+' / '+shown(row.get('sampled_peak_rss_mib')),
          'original verifier passed' if row['accepted'] else 'N/A; see failure record'] for row in report['long_ledger']])
    lines += ['## Missing, failed or incomplete inputs', '']
    for slot in report['comparison_slots']:
        if slot['status'] != 'presented': lines.append('- '+slot['group']+'/'+slot['scene']+': '+slot['status']+' '+slot.get('reason', ''))
    for attempt in report['attempts']:
        if attempt['status'] != 'completed': lines.append('- '+attempt['execution']['path']+': '+attempt['status']+'; '+str(attempt.get('failure')))
    for issue in report['issues']: lines.append('- '+json.dumps(issue, sort_keys=True))
    lines += ['', '## Definitions and evidence', ''] + ['- '+x for x in report['definitions']]
    lines += ['', 'Exact producing commits, package/native identities, measured cell identities, input paths/hashes, all per-process retained detail and receipt references are in `report.json`. `comparison.csv`, `resources.csv`, `capacity.csv` and `long-ledger.csv` expose the corresponding numeric fields.', '']
    return '\n'.join(lines)


def write_csv(path, rows):
    def flatten(value, prefix=''):
        result = {}
        for key, item in value.items():
            name = prefix + key
            if isinstance(item, dict): result.update(flatten(item, name+'.'))
            elif isinstance(item, list): result[name] = json.dumps(item, separators=(',', ':'), allow_nan=False)
            else: result[name] = item
        return result
    rows = [flatten(row) for row in rows]
    fields = sorted({key for row in rows for key in row})
    with path.open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--source-index-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(os.sched_getaffinity(0) == {8}, 'Run presentation outside timing on CPU8')
    e = Evidence(args.root)
    index_ref = dict(path=str(HERE/'sources.json'), sha256=args.source_index_sha256)
    index = e.read(index_ref)
    for name, digest in index['files_sha256'].items(): e.pin(dict(path=str(HERE/name), sha256=digest))
    manifest_ref = dict(path=str(args.manifest.resolve()), sha256=args.manifest_sha256)
    manifest = e.read(manifest_ref)
    admission = e.read(manifest['admission'])
    build_inputs = e.read(admission['build_inputs'])
    lock_path = e.path(build_inputs['exclusive_lock'])
    output = e.path(args.output)
    need(not output.exists(), 'Use a fresh presentation output directory')
    with lock_path.open('rb') as reservation:
        fcntl.flock(reservation.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        report = Report(e, manifest, manifest_ref, index_ref, index['measurement_schema_sha256']).execute()
        output.mkdir(parents=True)
        (output/'report.json').write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n')
        (output/'report.md').write_text(markdown(report))
        for name, key in (('comparison', 'rows'), ('resources', 'resources'), ('capacity', 'capacity'), ('long-ledger', 'long_ledger'),
                          ('comparison-slots', 'comparison_slots'), ('attempts', 'attempts')):
            write_csv(output/(name+'.csv'), report[key])
    print(json.dumps(dict(output=str(output), coverage=report['coverage'], presentation_only=True, new_acceptance_credit_seconds=0)))
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
