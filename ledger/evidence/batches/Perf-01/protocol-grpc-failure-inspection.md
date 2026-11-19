# Perf-01 final gRPC calibration: bounded failed-operation inspection

## Timing and interpretation boundary

This recipe was prepared from source on CPU 8 while root's final v5r1 calibration
session 98397 was active. After that window ended, root authorized the bounded
inspection of the 256/192/176 cells. It **completed with exit 0** and wrote its
receipt at **2026-11-19T13:41:11.785211+00:00**. Before inspection, root reported
that the 256/s cell was invalid with three generic
`response/protobuf/hash correctness failure` entries, while the 192/s cell was
valid overload evidence but failed the zero-error service standard. Preserve
both original verdicts. No fixture, criterion, timing driver, or classification
changes are authorized by this note.

The existing driver uses that generic invalid reason for any client
`correctness_failure`. Its exact exception text is retained in the independent
client record. `Client/Program.cs:93-127,190-244` establishes the distinctions:

- `Wait headers were not committed.` is the required initial-header assertion
  before the probe reads a response message or requests cancellation. It does
  not establish corrupted protobuf or payload data. The row does not record the
  underlying terminal status/trailers after that early assertion.
- The exact protobuf/order/hash messages identify which content assertion
  failed. They still do not locate the responsible implementation or prove
  corruption on the transport.
- `RpcException` retains its observed wire status. `ResourceExhausted` supports
  an explicit status-8 rejection; it alone does not identify the failed native
  grant or distinguish per-request from global credit pressure.
- Intentional probes succeed only when their exact required behavior is
  observed. A failed probe remains a failure under the existing frozen checks.

The historical 224/s distinction and quota-path source analysis are in
`grpc-baseline-quota-observation.md`; they are not evidence of the cause of a
new operation. The actual inspection below joined each selected raw row to its
frozen token and controller completion before applying a narrow explanation.

## Actual preserved observations

The copied receipt is
`checks/grpc-v5r1-failed-operations-001/receipt.json`, SHA-256
`4b7d221db337ad2915dcf551becede54d43640e982e6549afdeba99f367e2925`.
It is byte-identical to
`ROOT/perf01-evidence/diagnostic/grpc-v5r1-failed-operations-001/receipt.json`.
The result, plan, client JSONL, request JSONL and Oracle hashes all matched their
existing recorded pins. Counts below exclude warmup and recovery IDs.

| Offered rate / cell | Offered / logical successes | Explicit status-8 rejection | Unexpected cancellation | Integrity assertion failure | Original validity / service standard |
| --- | ---: | ---: | ---: | ---: | --- |
| 256/s, `05-ladder-256` | 7,707 / 7,629 | 61 | 14 | 3 | invalid / failed |
| 192/s, `06-refine-192` | 5,781 / 5,776 | 5 | 0 | 0 | valid / failed |
| 176/s, `08-refine-176` | 5,299 / 5,297 | 2 | 0 | 0 | valid / failed |

All three integrity failures at 256/s have the exact failure text
**`Wait headers were not committed.`** and zero received messages/bytes:

| ID | Frozen token | Client-recorded wire status |
| --- | --- | --- |
| 728 | `grpc-cancel\|http2-tls\|64\|1` | `IntegrityFailure` |
| 2925 | `grpc-deadline\|http2-tls\|64\|1` | `IntegrityFailure` |
| 7225 | `grpc-deadline\|http2-tls\|64\|1` | `IntegrityFailure` |

These are missing required initial-header observations. **No protobuf field or
payload/hash assertion failed in these three records.** Their underlying gRPC
terminal statuses and trailers after that early assertion are unavailable.
In particular, the neighboring status-8 rejections do not establish status 8 for
these three probes. The generic invalid reasons stay unchanged in the original
result and selection.

At 256/s, the 61 explicit `ResourceExhausted` rejections comprise 22 unary,
23 server-stream, three client-stream, 12 duplex, and one cancellation probe.
The 14 unexpected `Cancelled` outcomes comprise 12 ordinary duplex and two
ordinary client-stream calls. The 192/s cell has four server-stream and one
unary `ResourceExhausted`; the 176/s cell has two unary `ResourceExhausted`.
None of those status-8 rows carries a client content-integrity failure. They
violate the frozen zero-unexpected-error service standard without changing the
valid-overload-evidence classification of the 192/176 cells.

The specific source results have these hashes:

| Rate | `result.json` SHA-256 |
| --- | --- |
| 256 | `3149588ad535feb5cc64b89e889739a215d7476760825bccf63f7f90a52c6985` |
| 192 | `7d576bf4b1867b3dd46b96515d3584dc9faf3540026d69e7f29dcb96dad1198c` |
| 176 | `0c5846d5ad1939fa26e68a2517f352ceeafe2b852f08f21a0f2166d51baa4452` |

Every selected full client row, controller scalar record and Oracle pair is in
the receipt. This is a bounded explanation of existing evidence, not a new
acceptance run or a captured native-grant attribution.

## Execute only after root ends the calibration window

The command requires the completed controller and selection, chooses only the
three explicitly reported failed rates, and bounds each cell to 10,000 planned
operations and at most 256 selected failure records. It streams client/request
JSONL and the Oracle, verifies their existing hashes, and saves every selected
row with its Oracle and controller event record. It reads no resource ledger,
response body, free-form server log, or TLS key. Its receipt is explanatory and
does not replace or edit any original result.

```bash
ROOT=/workspace/scratch/01c249676f47
NW="$ROOT/.worktree/Perf-01-linux/NativeWeave"
PY=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
taskset -c 8 "$PY" - "$ROOT" "$NW" <<'PY'
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib, importlib.util, json, sys
root, nw = map(Path, sys.argv[1:])
reader = nw / 'tests/Perf01/verify_long.py'
def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
reader_sha = '3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82'
if sha(reader) != reader_sha: raise ValueError('Post-run reader differs')
spec = importlib.util.spec_from_file_location('failure_reader', reader)
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
require = v.require
base = root / 'perf01-evidence/calibration/before-grpc-v5r1'
outer = v.Evidence(base)
selection = outer.load('selection.json')
controller = outer.load('controller.json', selection['controller_sha256'])
require(controller['state'] == 'completed' and selection['variant'] == 'before', 'Calibration still active or not before')
cells = [row for row in controller['cells'] if row['rate'] in (176, 192, 256) and not row.get('qualifies')]
require(len(cells) == 3 and {row['rate'] for row in cells} == {176, 192, 256}, 'Explicit failed-cell selection differs')
output = root / 'perf01-evidence/diagnostic/grpc-v5r1-failed-operations-001'
require(not output.exists(), 'Choose a fresh diagnostic directory')
receipt = {'scope': 'specific failed-operation evidence; original verdicts unchanged',
           'reader_sha256': reader_sha, 'cells': []}
for cell in cells:
    command = cell['commands'][0]
    path = Path(command[command.index('--output') + 1]).resolve()
    require(path.parent == base.resolve(), 'Cell outside selected calibration')
    ev = v.Evidence(path)
    result = v.object_metadata(ev.pin(path / 'result.json', cell['result_sha256']),
        ['status', 'valid', 'service_standard_met', 'invalid_reasons', 'offered', 'successful',
         'outcome_counts', 'evidence_sha256', 'plan_sha256'])
    plan = ev.load('plan.json', cell['plan_sha256'])
    require(result['status'] == 'completed' and result['plan_sha256'] == cell['plan_sha256'], 'Incomplete/mismatched cell')
    count = plan['timing']['requests']; require(0 < count <= 10000 and result['offered'] == count, 'Scope exceeds bounded inspection')
    selected = {}; counts = Counter(); seen = bytearray(count)
    for row in ev.lines('execution/client/operations.jsonl', result['evidence_sha256']['execution/client/operations.jsonl']):
        identifier = row['id']
        if not 0 <= identifier < count: continue
        require(not seen[identifier], 'Duplicate measured client ID'); seen[identifier] = 1
        counts[(row['logical_status'], row['wire_status'], row['correctness_failure'])] += 1
        if row['logical_status'] != 'ok' or row['correctness_failure']:
            require(len(selected) < 256, 'More failures than this bounded inspection allows')
            selected[identifier] = {'client': row}
    for row in ev.lines('requests.jsonl', result['evidence_sha256']['requests.jsonl']):
        if row['id'] in selected:
            require('controller' not in selected[row['id']], 'Duplicate selected controller ID')
            selected[row['id']]['controller'] = row
    oracle_path = ev.pin(path / 'oracle.json', plan['oracle']['sha256'])
    entries = 0
    for identifier, row in enumerate(v.array_records(oracle_path)):
        entries += 1
        if identifier not in selected: continue
        require(row['input'] == row['expected'], 'Unexpected fixture Oracle contract')
        client = selected[identifier]['client']; fields = row['input'].split('|')
        require(len(fields) == 4 and fields[:2] == [client['scenario'], client['protocol']], 'Client/Oracle scenario differs')
        selected[identifier]['oracle'] = row
    require(entries == count and all('controller' in row and 'oracle' in row for row in selected.values()), 'Missing joined evidence')
    for row in selected.values():
        failure = row['client']['failure']
        row['explanation_scope'] = ('required initial-header assertion; underlying terminal status unrecorded'
            if failure == 'Wait headers were not committed.' else 'retain exact client failure/wire fields; no inferred root cause')
    receipt['cells'].append({'cell': str(path), 'rate': cell['rate'], 'original_result': result,
        'measured_client_rows': sum(seen), 'client_outcomes': [dict(logical_status=k[0], wire_status=k[1], correctness_failure=k[2], count=n)
            for k, n in sorted(counts.items())], 'selected': [selected[key] for key in sorted(selected)], 'input_sha256': dict(ev.files)})
    ev.unchanged()
outer.unchanged()
receipt.update(extracted_utc=datetime.now(timezone.utc).isoformat(), metadata_sha256=dict(outer.files))
output.mkdir(parents=True, exist_ok=False)
(output / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
print(str(output / 'receipt.json'))
PY
```

Use the actual preserved rows to add a concise note beside the final calibration
table. Keep the generic invalid label verbatim and separately explain its
specific assertion, if observed. A missing header must not be renamed a quota
failure without another recorded source of that terminal status. Root owns any
additional diagnosis and all subsequent performance measurements.

## Independent review

The codec reviewer passed a bounded source and saved-receipt review, checking
the executed-body/receipt hashes, complete measured client counts, selected
controller/Oracle joins and each status/assertion distinction above. This was
independent review of the preserved extraction output; the reviewer did not
rescan raw ledgers, rerun extraction, or execute a test, build or workload.
