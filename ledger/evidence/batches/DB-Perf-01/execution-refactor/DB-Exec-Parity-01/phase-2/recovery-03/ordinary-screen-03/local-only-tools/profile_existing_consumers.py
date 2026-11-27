#!/usr/bin/env python3
"""Self-thread samples of existing AOT consumers; never grants timing credit.

The real workload's monotonic steady window is adapted to the archived phase
analyzer schema. Original result and trace bytes remain unchanged. No product or
consumer source is modified, and no CPU timestamps from different threads are
subtracted.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--provider', choices=['sqlite', 'postgresql'], required=True)
p.add_argument('--baseline', type=Path, required=True)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--scenario', action='append', required=True)
p.add_argument('--operations', type=int, default=8192)
p.add_argument('--rounds', type=int, default=2)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--analyze-only', action='store_true')
a = p.parse_args()
out = a.output.resolve()
library = root / 'restored-stage1/diagnostics/native_sampler/builds/03/libparity_sampler.so'
def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
def save(path, value): path.write_text(json.dumps(value, indent=2) + '\n')
if not a.analyze_only:
    argv = ['python3', root / 'local-tools/run_causal_ab.py', '--provider', a.provider,
            '--baseline', a.baseline.resolve(), '--candidate', a.candidate.resolve(),
            '--operations', str(a.operations), '--rounds', str(a.rounds), '--warmup', '256',
            '--output', out, '--prepare-only']
    for scenario in a.scenario: argv += ['--scenario', scenario]
    subprocess.run(list(map(str, argv)), check=True)
    ordinary_plan = out.with_suffix('.plan.json')
    plan = json.loads(ordinary_plan.read_text())
    plan.update(ordinaryTiming=False, instrumented=True, newFinalCellCredit=False,
                scope='Self-thread CPU sampling of existing AOT ELFs; diagnostic only; no timing/allocation/RSS credit',
                sampler={'path': str(library), 'sha256': sha(library)},
                sourcePlan={'path': str(ordinary_plan), 'sha256': sha(ordinary_plan)},
                diagnosticHelperSha256=sha(__file__))
    for command in plan['commands'][1:]:
        command['phase'] = 'diagnostic-cpu-sampling'
        command['argv'] = ['env', 'LD_PRELOAD=' + str(library),
            'PARITY_SAMPLE_DIR={output}/' + command['name'] + '-trace', *command['argv']]
    diagnostic_plan = out.with_suffix('.sample.plan.json')
    save(diagnostic_plan, plan)
    subprocess.run(['taskset', '-c', '8', 'python3', str(root / 'worktrees/Korda/benchmarks/db-perf/run.py'),
                    str(diagnostic_plan), '--output', str(out), '--sample-seconds', '0.25'], check=True)

plan = json.loads((out / 'plan.json').read_text())
original_analyzer = root / 'restored-stage1/diagnostics/native_sampler/analyze_phases.py'
analyzer_path = out / 'analyze_workload_windows.py'
text = original_analyzer.read_text()
assert text.count("base/(client+'-1000.json')") == 1
text = text.replace("base/(client+'-1000.json')", "base/(client+'.window.json')")
text = text.replace("base/(client+'-sampled.command.json')", "base/(client+'.command.json')")
analyzer_path.write_text(text)
spec = importlib.util.spec_from_file_location('workload_window_analysis', analyzer_path)
analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer)
reports = []
for command in plan['commands'][1:]:
    name = command['name']
    original = out / (name + '.json')
    result = json.loads(original.read_text())
    assert result['NativeAot'] and result['Completed'] == a.operations
    assert result['Failed'] == result['OracleFailures'] == result['Retries'] == 0
    assert result['OwnersReturnedToZero'] and not result['Errors']
    assert result['ExecutableSha256'] == command['executableSha256']
    trace = out / (name + '-trace')
    assert (trace / 'manifest.json').is_file()
    modules = {}
    for path in trace.glob('modules-*.jsonl'):
        for line in path.read_text().splitlines():
            item = json.loads(line)
            file = Path(item['path'])
            if file.is_file(): modules[str(file)] = {'sha256': sha(file), 'runtimeBuildId': item['build_id']}
    save(out / (name + '-sample-identity.json'), {
        'modules': modules, 'files': {f.name: sha(f) for f in trace.iterdir() if f.is_file()}})
    def cpu_ticks(endpoint):
        reading = result[endpoint]
        return round((reading['UserCpuSeconds'] + reading['SystemCpuSeconds']) * 10_000_000)
    save(out / (name + '.window.json'), {
        'schemaAdapter': 'Original RunReceipt steady monotonic nanoseconds mapped to archived phase window schema',
        'sourceResult': str(original), 'sourceResultSha256': sha(original),
        'adapterSha256': sha(__file__), 'originalAnalyzerSha256': sha(original_analyzer),
        'analyzerAdapterSha256': sha(analyzer_path), 'timingCredit': False,
        'rawTimingComparisonEligibleIgnored': result['TimingComparisonEligible'],
        'cpuTicksConversion': 'Original process user+system seconds * 1e7 rounded; diagnostic metadata only',
        'Provider': result['Provider'], 'ExecutableSha256': result['ExecutableSha256'],
        'NativePath': result['LoadedNativePath'], 'NativeSha256': result['LoadedNativeSha256'],
        'StopwatchFrequency': 1_000_000_000,
        'Windows': [{'Route': name, 'Index': 0, 'Operations': result['Completed'],
                     'StartedTicks': result['SteadyStartMonotonicNs'], 'FinishedTicks': result['SteadyEndMonotonicNs'],
                     'CpuBeforeTicks': cpu_ticks('ProcessBefore'), 'CpuAfterTicks': cpu_ticks('ProcessAfter')}],
    })
    directory = out / (name + '-analysis')
    directory.mkdir(exist_ok=False)
    report = analyzer.analyze(out, name, directory)
    reports.append({'name': name, 'passed': report['passed'], 'analysisSha256': sha(directory / 'analysis.json'),
                    'samples': report['warm_samples'], 'topLeafSymbols': report['routes'][0]['top_leaf_symbols'][:10]})
save(out / 'sampling-summary.json', {'passed': all(x['passed'] for x in reports), 'reports': reports,
    'scope': 'Diagnostic attribution only; original reports retain their own flags but are not ordinary comparison evidence'})
if not all(x['passed'] for x in reports): raise SystemExit('Sampling identity/coverage/clock validation failed')
