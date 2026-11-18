"""Read-only B23 contract source/receipt binding; does not run an application or workload."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/scratch/58d2a6adf1c3')
REPO = ROOT / '.worktree/Task-07-B23-linux/NativeWeave'
COMP = ROOT / '.worktree/Task-07-B23-comparators-linux/NativeWeave'
HERE = ROOT / 'task07-b23/independent-contract-review'
RUN = ROOT / 'task07-b23/functional-review-003'
BASELINE = 'e85bc13c78b6983860ca36b9688d3535395ac88e'
FINAL = '92f9e6b5672ea4cd813b769ed7aaff60044763d8'
COMMIT = 'be0bf7f00892f0f2f8ac041a55f79ab146ac8ac9'
FILES = ['src/Benchmarks.Domain/run.py', 'src/Benchmarks.Domain/http_target.py',
    'src/Benchmarks.Domain/common.py', 'src/Benchmarks.Domain/profile-v1.json',
    'src/Benchmarks.Domain/README.md', 'docs/guides/benchmarks-domain.md']

def sha(value):
    if isinstance(value, Path):
        with value.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
    return hashlib.sha256(value).hexdigest()

def source(commit, file):
    return subprocess.check_output(['git', '-C', str(REPO), 'show', commit + ':' + file])

def load(path): return json.loads(path.read_text())

manifest_path = COMP / 'src/Benchmarks.Domain/comparators/comparators.json'
manifest = load(manifest_path)
assert sha(manifest_path) == 'e789eb77430c7284e98135ab083fbff78a3ecb79e8dce35e042f3706d58ba2d8'
summary = load(RUN / 'summary.json')
assert summary['controller_source']['commit'] == FINAL and summary['controller_source']['scope_status'] == ''
assert summary['state'] == 'completed' and summary['phase'] == 'functional' and summary['all_executed_cells_valid']
assert len(summary['runs']) == 9
inputs = summary['external_input_sha256']
assert len(inputs) == 6
for file, expected in inputs.items(): assert sha(Path(file)) == expected

expected_cells = {(name, provider, protocol) for name in ('nativeweave-aot-rust', 'managed-aot', 'direct-rust')
                  for provider, protocol in [('sqlite', 'http2-tls'), ('postgresql', 'http1-tls'), ('postgresql', 'http2-tls')]}
apps = []
for path in sorted((RUN / 'applications').glob('*/receipt.json')):
    record = load(path); profile = record['profile']; route = record['route']
    cell = (route, profile['provider'], profile['protocol'])
    assert cell in expected_cells; expected_cells.remove(cell)
    assert record['status'] == 'passed' and not record['errors'] and record['durable_oracle']['passed']
    assert record['durable_oracle']['operations'] == record['durable_oracle']['outbox'] == 6
    assert record['durable_oracle']['attachments'] == record['durable_oracle']['items'] == 3
    assert record['observed_http_protocols'] == ['HTTP/2' if profile['protocol'] == 'http2-tls' else 'HTTP/1.1']
    case = profile['id'] + '-' + profile['provider'] + '-' + profile['protocol']
    target_path = RUN / 'plans' / case / 'target.json'; target = load(target_path)
    assert record['source_manifest_sha256'] == sha(target_path)
    assert all(target['files'].get(file) == expected for file, expected in inputs.items())
    assert target['files'][str(REPO / FILES[0])] == sha(source(FINAL, FILES[0]))
    assert target['files'][str(REPO / FILES[1])] == sha(source(FINAL, FILES[1]))
    plan = load(target_path.with_name('plan.json'))
    for descriptor in plan['routes']:
        assert all(descriptor['artifacts'].get(file) == expected for file, expected in inputs.items())
    assert record['application_artifacts'] == summary['routes'][route]['artifacts']
    if route != 'nativeweave-aot-rust': assert record['application_artifacts'] == manifest['routes'][route]['artifacts']
    for file, expected in record['application_artifacts'].items(): assert sha(Path(file)) == expected
    config_path = path.parent / 'application/config.private.json'; config = load(config_path)
    assert config['provider'] == profile['provider'] and config['runWorkers'] is False
    assert config['maxUploads'] == 4 and config['maxBlobBytes'] == 268435456 and config['requestTimeoutSeconds'] == 120
    assert config['tlsCertificatePem'] in inputs and config['tlsPrivateKeyPem'] in inputs
    assert record['configuration_private_sha256'] == sha(config_path)
    stdout = path.parent / 'application/stdout.log'; stderr = path.parent / 'application/stderr.log'
    logs = stdout.read_text() + stderr.read_text()
    assert 'READY https://' in logs
    if route != 'direct-rust': assert 'RUNTIME dynamic=False' in logs
    observation = next(row for row in summary['runs'] if row['route'] == route and row['case'] == case)
    assert observation['valid'] and not observation['invalid_reasons'] and observation['outcome_counts'] == {'ok': 2}
    observation_path = RUN / observation['path']; assert sha(observation_path) == observation['sha256']
    apps.append({'route': route, 'case': case, 'status': 'passed',
        'application_receipt': str(path), 'application_receipt_sha256': sha(path),
        'target_manifest_sha256': sha(target_path), 'observation_sha256': observation['sha256'],
        'observed_http_protocols': record['observed_http_protocols'], 'configuration_private_sha256': sha(config_path),
        'durable_oracle': record['durable_oracle'],
        'artifact_files_equal': True, 'frozen_external_inputs_equal': True})
assert not expected_cells

baseline = {'reviewer': '/root/b21_service; author of comparators but not of the reviewed B23 controller, HTTP adapter, profile or report',
    'scope': 'Independent controller-to-comparator contract/configuration/immutable-identity review. Statistical validity and complete B23 acceptance are owned by the parent review.',
    'baseline_commit': BASELINE, 'baseline_file_sha256': {file: sha(source(BASELINE, file)) for file in FILES},
    'comparator_commit': COMMIT, 'comparator_manifest': str(manifest_path), 'comparator_manifest_sha256': sha(manifest_path),
    'findings': [
        {'id': 'B23-CONTRACT-C1', 'status': 'open', 'finding': 'Actual TLS certificate/key and PostgreSQL server/client/lifecycle binaries were not included in the calibration fingerprint or per-cell immutable file checks. Same-path replacements could retain a matching calibration fingerprint.'},
        {'id': 'B23-CONTRACT-C2', 'status': 'open', 'finding': 'Attachment success did not assert returned responseVersion/contentHash/contentLength. Equality between stored and HTTP response bytes alone could accept the same wrong DTO persisted and returned.'}],
    'other_observations': [
        'SQLite/PG provider selection, fresh isolated database/blob root, finite pool/admission/size settings and disabled worker policy match the selected comparator profile.',
        'Actual READY scheme, strict trusted TLS verification, observed HTTP/1.1 or HTTP/2, and managed NativeAOT witnesses are required.',
        'Executable/native/lock/source identity from the comparator manifest is retained and checked; accepted product artifacts are separate immutable inputs.',
        'Managed and Rust manifests declare the same 64KiB H2 stream/connection window,32KiB frame/header aggregate,32streams,200HTTP1headers; these are finite transport settings, not a global byte-credit equivalence claim.',
        'Missing comparator DI/diagnostics/overload/resource-owner variants are explicitly product_only and excluded from cross-route comparisons.',
        'Scope is foreground durable outbox publication with workers disabled; external consumer throughput is not claimed.',
        'The list cell selects the first100 rows from128 deterministic ordered fixtures; it does not measure an after-cursor seek operation.',
        'Runtime/pool/migration-ledger/query-route differences and cold OS-cache limitations remain disclosed. No universal backend or host substitution is introduced.']}
(HERE / 'baseline-review.json').write_text(json.dumps(baseline, indent=2, sort_keys=True) + '\n')
review = dict(baseline)
review.update(reviewed_commit=FINAL, reviewed_file_sha256={file: sha(source(FINAL, file)) for file in FILES},
    verdict='No open concrete comparator-contract blocker in the requested scope.',
    corrected_run={'path': str(RUN), 'summary_sha256': sha(RUN / 'summary.json'), 'phase': 'functional',
        'cells': apps, 'external_input_sha256': inputs, 'all_cells_valid': True,
        'scope': 'Nine targeted real streaming cells across all three routes. No performance conclusion and no relabelling of the retained earlier66-cell cohort.'},
    review_execution='Read-only source/artifact/receipt inspection. This review did not build or execute any application, workload or benchmark.',
    closure_script_sha256=sha(Path(__file__)))
review['findings'] = [dict(finding, status='closed', closure=(
    '92f9e6b adds both TLS files and postgres/psql/initdb/pg_ctl to external_input_sha256 and self.files before fingerprinting. Every target checks these files and A21 receives them as immutable artifacts. All six current hashes equal the recorded hashes in the successful targeted nine-cell cohort.' if finding['id'].endswith('C1') else
    '92f9e6b requires v1 responseVersion, version2, exact deterministic contentHash and contentLength before recording the attachment mutation. Exact operation/item identity and independent SQL/blob checks remain. All nine actual targeted streaming cells pass.')) for finding in baseline['findings']]
(HERE / 'review.json').write_text(json.dumps(review, indent=2, sort_keys=True) + '\n')
lines = ['# B23 controller/comparator contract review', '',
    'Reviewer: `/root/b21_service`. The reviewer authored the standalone comparators and did not author the reviewed controller, HTTP adapter, profile or report.', '',
    f'Baseline reviewed commit: `{BASELINE}`. Corrected reviewed commit: `{FINAL}`.', '',
    f'Comparator input: `{COMMIT}`, manifest SHA-256 `{sha(manifest_path)}`.', '',
    '**Verdict: both concrete findings are closed.** No remaining comparator-contract blocker was found within the requested scope.', '',
    '## Findings and closure', '']
for finding in review['findings']: lines += [f"- **{finding['id']}** — {finding['finding']} {finding['closure']}"]
lines += ['', '## Actual correction evidence', '',
    'The retained `functional-review-003` cohort completed all nine targeted cells: the three routes each ran SQLite HTTP/2 TLS, PostgreSQL HTTP/1 TLS and PostgreSQL HTTP/2 TLS streams. Each cell confirmed two requests after one warmup, six durable operations/outbox records, three items and attachments, one immutable content hash, exact HTTP version and HTTPS readiness. Managed routes emitted their actual NativeAOT witness. The independent review rechecked immutable artifact and external-input hashes, target/receipt identity, private configuration hashes and successful A21 observations.', '',
    'This is functional evidence. The earlier66-cell cohort remains attributed to its original source and is not relabelled. No app, build, network or timed workload was run by this review.', '',
    '## Contract and scope checks', '']
for observation in review['other_observations']: lines += ['- ' + observation]
lines += ['', 'Statistical/calibration validity and complete B23/B22 acceptance are outside this review and remain assigned to their owners.', '',
    '## Reviewed source SHA-256', '', '| File | Corrected SHA-256 |', '| --- | --- |']
for file, digest in review['reviewed_file_sha256'].items(): lines += [f'| `{file}` | `{digest}` |']
lines += ['', 'Baseline hashes, exact per-cell receipts, observation hashes and external input hashes are in `baseline-review.json` and `review.json`. No credential or private-key content is included.']
(HERE / 'review.md').write_text('\n'.join(lines) + '\n')
print(json.dumps({'verdict':review['verdict'], 'functional_cells':len(apps),
    'review_json_sha256':sha(HERE / 'review.json'), 'review_md_sha256':sha(HERE / 'review.md')},indent=2))
