#!/usr/bin/env python3
"""Read-only independent B09 managed/ABI evidence audit; writes only this review directory."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path('/workspace/scratch/0898a75257bc')
SOURCE = ROOT / '.worktree/Task-02-B09-linux/NativeWeave'
DESIGN = ROOT / '.worktree/Task-02-linux/NativeWeave-Design'
OUT = Path(__file__).resolve().parent
RUN = SOURCE / 'artifacts/B09/attempt-002'
COMMIT = '5bfaaa2e15726321be8b06a21557f3f62cb389e9'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def git(*args):
    return subprocess.check_output(['git', *args], cwd=SOURCE, text=True).strip()


status = read(RUN / 'status.json')
inputs = read(RUN / 'source-inputs.json')
after = read(RUN / 'source-inputs-after.json')
commands = read(RUN / 'commands.json')
artifacts = read(RUN / 'artifact-identities.json')
assert git('rev-parse', 'HEAD') == COMMIT == status['candidate'] == inputs['commit']
assert not git('status', '--porcelain')
assert status['result'] == 'passed' and status['platform'] == 'linux-x64'
assert len(commands) == 31 and all(c['exit_code'] == 0 for c in commands)
assert inputs['inputs'] == after['inputs'] and after['unchanged']
source_checks = {name: sha(SOURCE / name) == digest for name, digest in inputs['inputs'].items()}
artifact_checks = {name: sha(SOURCE / name) == digest for name, digest in artifacts['sha256'].items()}
response_checks = {entry['path']: sha(SOURCE / entry['path']) == entry['sha256'] for entry in artifacts['native_aot_response_files']}
assert all(source_checks.values()) and all(artifact_checks.values()) and all(response_checks.values())

inventory_path = SOURCE / 'native/database/binding/signatures-v1.json'
inventory = read(inventory_path)
design_path = DESIGN / inventory['source']
assert sha(design_path) == inventory['source_sha256']
assert subprocess.check_output(['git', '-C', str(DESIGN), 'rev-parse', 'HEAD'], text=True).strip() == inventory['design_commit']
signatures = re.findall(r'^(?:nw_status|void) NW_CDECL nw_db_\w+\([^;]+\);$', design_path.read_text(), re.MULTILINE)
assert signatures == inventory['signatures'] and len(signatures) == 42

aliases = {
    'nw_status': 'uint', 'void': 'void', 'nw_db_ref': 'nint', 'nw_db_ref*': 'nint*',
    'nw_db_buffer*': 'nint', 'nw_db_buffer**': 'nint*', 'nw_db_token': 'ulong',
    'nw_db_token*': 'ulong*', 'uint32_t': 'uint', 'uint32_t*': 'uint*',
    'uint64_t': 'ulong', 'int64_t*': 'long*', 'nw_bytes_view_v1': 'NwBytesViewV1',
    'nw_bytes_view_v1*': 'NwBytesViewV1*', 'nw_error_info_v1*': 'NwErrorInfoV1*',
    'const nw_operation_callbacks_v1*': 'NwOperationCallbacksV1*',
}
expected = {}
for signature in signatures:
    match = re.fullmatch(r'(\w+) NW_CDECL (\w+)\((.*)\);', signature)
    result, name, parameters = match.groups()
    mapped = [aliases[p.strip().rsplit(' ', 1)[0]] for p in parameters.split(',')]
    expected[name] = mapped + [aliases[result]]

managed_path = SOURCE / 'src/Query.Binding/NativeCalls.g.cs'
managed = managed_path.read_text()
fields = {name: [t.strip() for t in types.split(',')] for types, name in re.findall(r'internal readonly delegate\* unmanaged\[Cdecl\]<([^>]+)> (nw_db_\w+);', managed)}
resolvers = {name: {'types': [t.strip() for t in types.split(',')], 'symbol': symbol} for name, types, symbol in re.findall(r'(nw_db_\w+) = \(delegate\* unmanaged\[Cdecl\]<([^>]+)>\)resolve\("(nw_db_\w+)"\);', managed)}
assert fields == expected and len(resolvers) == 42
assert all(resolvers[name] == {'types': types, 'symbol': name} for name, types in expected.items())

fixed = read(OUT / 'ownership-fixed-inputs.json')
assert fixed['sourceHead'] == COMMIT and not fixed['sourceDirty'] and fixed['probeUnchangedFromPreFix']
assert fixed['inputBinaries']['NativeWeave.Query.Binding.dll']['sha256'] == artifacts['sha256']['src/Query.Binding/bin/Release/net11.0/NativeWeave.Query.Binding.dll']
assert fixed['inputBinaries']['libnativeweave_query_binding_fixture.so']['sha256'] == artifacts['sha256']['tests/Query.Binding/native/target/release/libnativeweave_query_binding_fixture.so']
assert read(OUT / 'ownership-fixed-result.json')['passed']

result = {
    'reviewer': '/root/environment_review', 'read_only_product_tree': True,
    'candidate': COMMIT, 'design_commit': inventory['design_commit'],
    'formal_status': {'path': str(RUN / 'status.json'), 'sha256': sha(RUN / 'status.json')},
    'formal_source_inputs': {'path': str(RUN / 'source-inputs.json'), 'sha256': sha(RUN / 'source-inputs.json')},
    'formal_commands': {'path': str(RUN / 'commands.json'), 'sha256': sha(RUN / 'commands.json')},
    'formal_artifact_identities': {'path': str(RUN / 'artifact-identities.json'), 'sha256': sha(RUN / 'artifact-identities.json')},
    'source_hashes_checked': len(source_checks), 'artifact_hashes_checked': len(artifact_checks),
    'aot_response_hashes_checked': len(response_checks),
    'command_logs': {c['log']: {'sha256': sha(RUN / c['log']), 'exit_code': c['exit_code']} for c in commands},
    'pinned_signature_inventory': {'path': str(inventory_path), 'sha256': sha(inventory_path)},
    'pinned_design_api': {'path': str(design_path), 'sha256': sha(design_path)},
    'managed_declarations': {'path': str(managed_path), 'sha256': sha(managed_path)},
    'independently_mapped_signatures': expected,
    'managed_field_mapping_exact': fields == expected,
    'module_symbol_resolution_exact': True,
    'compiled_metadata_evidence': {'path': str(RUN / '16-compiled-api-xml-reference.log'), 'sha256': sha(RUN / '16-compiled-api-xml-reference.log'), 'method': 'Read actual formal gate result and reviewed gate source: PE field signature prefix 06 1b 01 for Cdecl plus compiled return/parameter types, zero exported types, complete XML/reference.'},
    'probe_binaries_equal_final_formal_binaries': True,
    'source_still_clean': not git('status', '--porcelain'),
    'all_checked_hashes_match': True,
    'existing_tests_rerun': False,
}
(OUT / 'receipt-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(f"PASS: {len(source_checks)} source hashes, {len(artifact_checks)} artifacts, {len(response_checks)} AOT response files, {len(commands)} actual logs, 42 independently mapped signatures")
print('receipt-audit SHA256', sha(OUT / 'receipt-audit.json'))
