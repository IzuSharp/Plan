# Perf-01 protocol controller retention: source review and bounded extraction

## Scope and execution status

This follow-up to `protocol-long-footprint-preflight.md` is source and small
completed-metadata work on CPU 8 during root's exclusive calibration session
98397. Root subsequently ended that window and authorized the bounded extraction;
the command below **completed with exit 0 on CPU 8**, with its final headroom
observation at **2026-11-19T13:40:59.533314+00:00**. The extraction preserved the
existing evidence and created a separate diagnostic receipt. It performed no
server, client, codec, database, or benchmark workload and grants no acceptance
credit.

The completed HTTP v5r1 metadata is retained in
`checks/protocol-http-v5r1-selection/`. Its three final processes each scheduled
65,390 operations. That metadata records server RSS, but **does not record
controller RSS**. The subsequent extraction below obtains live-load controller
memory from the existing result and process samples. At the selected long rate of
500/s, the frozen 1802-second preparation formula produces 901,051 operations,
approximately 13.78 times that short population. A population ratio is not a
measured memory ratio or a safe upper bound.

The inspected source bytes are unchanged from the final before calibration:

| Source | SHA-256 |
| --- | --- |
| Protocol `run.py` | `ee5867cfd5c29b52595b96a69328fc612c88ebdd38fd5796ed7582102c4c49b4` |
| Protocol `adapter.py` | `21254a039396e8de485d5729cc3a7236e4c12ae7b41a4427f703af86e3e77f69` |
| A21 `nativeweave_bench.py` | `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53` |
| Post-run `verify_long.py` reader | `3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82` |

`run.py:173-178` constructs the ordinary `Oracle` and `RunState`; both compact
options remain off. A21 retains the full array of short input/expected token
pairs, one scalar request dictionary per planned operation, and completion-set
membership. This is O(N) controller retention. Actual HTTP/protobuf bodies are
not stored in those Python records.

The 19 unavailable per-operation counter observations are **one shared
dictionary** created once at `run.py:176`. Each completion receives that same
object immediately before `state.event` (`:209-210`); request output removes the
reference before serialization (`:315-318`). There is no N-times duplication of
those 19 counter objects. A21's compact mode still keeps the scalar records,
completion set and Oracle, while adding a kind bytearray and signed-64-bit raw
ordinal array (9N payload bytes); its omitted per-row counter references and
short token values are not the principal existing Oracle/record population.

That API is also **not a drop-in flag** for this driver. Compact events require
a persisted `raw_event_index`, and replay validates `wire_base64`, counters,
accepted event identity and the live raw digest. Protocol events currently
persist a `wire` string before the common counters are injected, and do not
supply that index/digest (`A21:379-461,463-516`; `run.py:190-210`). This review
proposes no mode change, new replay path, or speculative retainer patch.

Pending operations are capped at 1024; the fixed client worker count is 64 and
its command channel capacity is 1024. The deadline heap is time-bounded by the
25-second request timeout, rather than the full completed population. At 500/s
its source count bound is 12,501. The earlier footprint note documents the
additional finalization arrays, sparse histograms and whole-document JSON text.
Those are separate from the live pending-work bounds.

## What the existing observations can establish

| Evidence | Exact fields / scope |
| --- | --- |
| Per-cell `result.json` | `resources.controller`, `.adapter`, `.client`, `.server`: `rss_bytes_first`, `rss_bytes_last`, `rss_bytes_maximum`, `cpu_seconds`, `cpu_percent_one_core`, thread/descriptor maxima; each uses samples inside `measurement_window.start_monotonic_ns..end_monotonic_ns` |
| `execution/process-resources.jsonl` | Per-role PID and `counters.rss_bytes`, `.peak_rss_bytes` (Linux VmHWM), `.private_working_set_bytes`; values include explicit availability/method/unit. Samples occur approximately once per second. VmHWM includes earlier process lifetime, not only measurement. |
| `result.managed_gc` | **Server-only** managed allocation and gen0/1/2 collection deltas, managed heap/committed maxima. These use first/last phase-tagged measurement samples and are approximate interval observations. |
| Python controller/adapter GC | Not observed: no collection counts, pause duration, or allocation trace in these timed cells. |
| Common C# client GC | Not observed by this harness; server GC cannot substitute for it. |
| Controller postprocessing peak | Not observed: adapter sampling stops before the controller builds histograms and serializes final JSON. |
| `result.host.cgroup_limits` | Limits exposed at measurement time; no recorded host `MemTotal`/`MemAvailable`. Later host-headroom readings describe extraction time only. |

The result sampler logic is `run.py:448-470`; GC is `:471-500` and
`Server/Program.cs:190-228`. Resource rows originate at `adapter.py:86-97` and
A21 `observe_process:266-295`. Keep a missing counter as unavailable. A first to
last live-load RSS difference omits the Oracle and record allocations that
already occurred before the first sample and is therefore not total bytes per
operation.

## Actual bounded extraction results

The complete diagnostic receipt is
`checks/protocol-controller-retention-v5r1-001/receipt.json`, SHA-256
`2966f2f0611dd208bebc7cd7500fe7d208449b038afcb22d37768ab264e997f8`.
It is a byte-identical copy of
`ROOT/perf01-evidence/diagnostic/protocol-controller-retention-v5r1-001/receipt.json`.
All six source results, plans and resource files matched the existing recorded
hashes. Their first/last/maximum sampled RSS values reconciled exactly with the
existing `result.resources` fields. This extraction did not rescan workload
correctness or grant long-run credit.

All values below are bytes. The controller peak was also its last observed RSS.
There were 60/60/60 available HTTP and 60/59/60 available gRPC controller
measurement samples, with no unavailable RSS, private-working-set or VmHWM values.

| Group / final confirmation | Operations | Controller first RSS | Controller maximum RSS | Adapter maximum RSS | Client maximum RSS |
| --- | ---: | ---: | ---: | ---: | ---: |
| HTTP 0, 1088/s | 65,390 | 64,421,888 | 103,882,752 | 21,037,056 | 77,496,320 |
| HTTP 1, 1088/s | 65,390 | 64,450,560 | 103,866,368 | 21,024,768 | 81,387,520 |
| HTTP 2, 1088/s | 65,390 | 64,409,600 | 103,862,272 | 21,041,152 | 79,839,232 |
| gRPC 0, 160/s | 9,617 | 29,495,296 | 34,938,880 | 20,844,544 | 66,998,272 |
| gRPC 1, 160/s | 9,617 | 29,519,872 | 34,877,440 | 20,848,640 | 66,973,696 |
| gRPC 2, 160/s | 9,617 | 29,499,392 | 34,951,168 | 20,860,928 | 66,592,768 |

At the selected 500/s long HTTP rate, scaling each complete controller peak by
`901051/65390` yields **1,431,185,259 to 1,431,467,466 bytes** (about 1.333 GiB).
This deliberately scales fixed costs too; it is an illustrative scenario, not
a fitted per-operation cost or upper bound. The selected 128/s long gRPC rate
has **230,670** planned operations; the analogous whole-controller scenarios
are 836,558,084 to 838,326,498 bytes. They remain separate serial groups.

At extraction time, `/proc/meminfo` exposed `MemTotal=10,206,472 KiB` and
`MemAvailable=7,026,552 KiB` (6.701 GiB), with no swap. The exposed cgroup
`memory.max`, `memory.high`, `memory.current` and `memory.events` files were
unavailable; the recorded measurement-time cgroup memory limits were also
unavailable. Do not call this evidence of an unlimited container budget. The
available host memory makes the observed linear live-retention scenario
plausible, but does not establish the missing postprocessing peak or future
generator scheduling validity. No retainer change is justified by a proven
out-of-memory failure in these six cells.

The existing **server-only** approximate managed-allocation deltas were
20,508,202,704 / 20,551,662,432 / 20,514,579,696 bytes for HTTP and
104,311,616,736 / 104,856,563,800 / 104,525,491,696 bytes for gRPC.
The receipt preserves the corresponding gen0/1/2 and heap/committed observations.
These describe cumulative allocation across phase-tagged samples, not retained
controller memory, exact whole-operation allocation attribution, or Python GC.

## After-window extraction command

This selects only the final three passing confirmations for each completed
group, checks their recorded result/plan/resource hashes, projects result
metadata with the already reviewed bounded reader, and scans the short resource
JSONL files one row at a time. It does not decode request, event, Oracle, client,
or histogram populations. It records existing validity rather than revalidating
the complete workload. Choose a fresh output suffix if `001` already exists.

```bash
ROOT=/workspace/scratch/01c249676f47
NW="$ROOT/.worktree/Perf-01-linux/NativeWeave"
PY=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
taskset -c 8 "$PY" - "$ROOT" "$NW" <<'PY'
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
PY
```

Assess the three actual controller peaks and their sample availability first.
Report adapter and client memory separately and identify the extraction-time
host/cgroup headroom. Do not subtract the fixed client backing arrays from RSS.
Multiplying the whole controller RSS by the population ratio intentionally also
scales fixed costs; it is only a rough scenario, not an allocation attribution.
Allocator fragmentation, GC behavior, sorting/histogram temporaries and final
serialization can be nonlinear. A large apparent host margin can make a long
run plausible, but these short samples alone cannot establish generator
validity or a safe postprocessing peak. The actual long run must still satisfy
all original scheduling, correctness, service, drain and duration gates.

The separate gRPC failure-row recipe in
`protocol-grpc-failure-inspection.md` preserves overload classifications and
joins specific failed operations after the same exclusive window ends.

## Independent review

The codec reviewer independently passed a bounded source and saved-receipt
review. It checked receipt and executed-body hashes, the six RSS reconciliations
and sample counts, long-population arithmetic, server-only GC scope and the
limits of extrapolation. It did not rerun extraction, read raw measurement
ledgers, or execute a test, build or workload. The original derived receipts and
the exact executed bodies remain unchanged after that review.
