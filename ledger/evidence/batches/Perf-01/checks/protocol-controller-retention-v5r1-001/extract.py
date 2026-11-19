from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, math, sys
root, nw = map(Path, sys.argv[1:])
reader_path = nw / 'tests/Perf01/verify_long.py'
reader_sha = '3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82'
def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
if sha(reader_path) != reader_sha: raise ValueError('Post-run reader identity differs')
spec = importlib.util.spec_from_file_location('memory_reader', reader_path)
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
require = v.require
output = root / 'perf01-evidence/diagnostic/protocol-controller-retention-v5r1-001'
require(not output.exists(), 'Use a new diagnostic directory')
receipt = {'scope': 'post-run sampled memory diagnostic, not long acceptance',
           'reader_sha256': reader_sha, 'groups': {}, 'unavailable': [
           'Python controller/adapter GC', 'C# client GC', 'controller postprocessing RSS peak']}
names = ['status', 'valid', 'service_standard_met', 'invalid_reasons', 'exit_code',
         'offered', 'actually_dispatched', 'successful', 'controller_pid', 'plan_sha256',
         'evidence_sha256', 'measurement_window', 'resources', 'managed_gc', 'host']
for group in ('http', 'grpc'):
    base = root / ('perf01-evidence/calibration/before-' + group + '-v5r1')
    outer = v.Evidence(base)
    selection = outer.load('selection.json')
    controller = outer.load('controller.json', selection['controller_sha256'])
    require(controller['state'] == 'completed' and selection['variant'] == 'before', 'Group not completed before')
    cells = controller['cells'][-3:]
    require([cell['phase'] for cell in cells] == ['confirmation-0', 'confirmation-1', 'confirmation-2'], 'Final triplet differs')
    rows = []
    for cell in cells:
        require(cell['state'] == 'completed' and cell['exit_code'] == 0 and cell['valid'] is True
                and cell['qualifies'] is True and cell['rate'] == selection['highest_consistently_passing_rate'], 'Nonpassing final cell')
        commands = cell['commands']
        prepare = commands[0]
        path = Path(prepare[prepare.index('--output') + 1]).resolve()
        require(path.parent == base.resolve(), 'Cell path outside chosen group')
        ev = v.Evidence(path)
        result = v.object_metadata(ev.pin(path / 'result.json', cell['result_sha256']), names)
        plan = ev.load('plan.json', cell['plan_sha256'])
        require(result['plan_sha256'] == cell['plan_sha256'] and result['offered'] == cell['offered']
                and result['valid'] is True and result['service_standard_met'] is True, 'Result/selection differs')
        window = result['measurement_window']
        roles = {role: {'pid': None, 'sample_count': 0, 'counters': {}} for role in ('controller', 'adapter', 'client', 'server')}
        for sample in ev.lines('execution/process-resources.jsonl', result['evidence_sha256']['execution/process-resources.jsonl']):
            if not window['start_monotonic_ns'] <= sample['monotonic_ns'] <= window['end_monotonic_ns']: continue
            for role, observed in roles.items():
                current = sample.get(role)
                if not current: continue
                require(observed['pid'] in (None, current['pid']), 'Sampled PID changed')
                observed['pid'] = current['pid']; observed['sample_count'] += 1
                for key in ('rss_bytes', 'peak_rss_bytes', 'private_working_set_bytes'):
                    target = observed['counters'].setdefault(key, {'available': 0, 'unavailable': 0, 'first': None, 'last': None, 'maximum': None})
                    value = current['counters'].get(key, {})
                    if value.get('availability') != 'measured' or value.get('value') is None:
                        target['unavailable'] += 1; continue
                    number = value['value']; require(type(number) is int and number >= 0, 'Invalid memory sample')
                    target['available'] += 1
                    if target['first'] is None: target['first'] = number
                    target['last'] = number; target['maximum'] = max(target['maximum'] or 0, number)
        require(roles['controller']['pid'] == result['controller_pid'], 'Controller PID differs')
        for role, observed in roles.items():
            rss = observed['counters'].get('rss_bytes', {})
            for field in ('first', 'last', 'maximum'):
                require(rss.get(field) == result['resources'][role]['rss_bytes_' + field], 'RSS summary/sample mismatch')
        long_period = round(1e9 / selection['long_rate'])
        long_n = math.ceil((1802_000_000_000 + plan['timing']['max_dispatch_lag_ns']) / long_period) + 1
        ratio = long_n / result['offered']
        peak = result['resources']['controller']['rss_bytes_maximum']
        rows.append({'cell': str(path), 'offered': result['offered'], 'successful': result['successful'],
                     'window': window, 'resources': result['resources'], 'sample_memory': roles,
                     'server_managed_gc_only': result['managed_gc'], 'measurement_cgroup_limits': result['host'].get('cgroup_limits'),
                     'long_planned_operations': long_n, 'population_ratio': ratio,
                     'illustrative_whole_controller_rss_times_population_ratio_bytes': None if peak is None else math.ceil(peak * ratio),
                     'input_sha256': dict(ev.files)})
        ev.unchanged()
    outer.unchanged()
    receipt['groups'][group] = {'selection': selection, 'metadata_sha256': dict(outer.files), 'cells': rows}
headroom = {'observed_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'extraction-time exposed host/cgroup files; not historical samples'}
for name in ('/proc/meminfo', '/sys/fs/cgroup/memory.max', '/sys/fs/cgroup/memory.high',
             '/sys/fs/cgroup/memory.current', '/sys/fs/cgroup/memory.events'):
    try: headroom[name] = Path(name).read_text()
    except OSError as error: headroom[name] = {'unavailable': type(error).__name__}
receipt['extraction_time_headroom'] = headroom
receipt['interpretation'] = 'Population-ratio scenarios are not proven memory bounds; no Python-GC or postprocessing-peak observation.'
output.mkdir(parents=True, exist_ok=False)
(output / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
print(str(output / 'receipt.json'))