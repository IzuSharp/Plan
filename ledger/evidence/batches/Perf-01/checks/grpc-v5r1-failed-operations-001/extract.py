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