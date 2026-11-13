#!/usr/bin/env python3
"""Verify the pinned research migration pair without rerunning native fixtures.

This checks archived bytes, source identities and Plan updates. It is not an
independent technical review, a GitHub approval, or new Windows/Linux execution.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def blob_digest(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def contained(root, path):
    target = (root/path.replace('\\', '/')).resolve()
    require(target.is_relative_to(root.resolve()), 'path escapes root: '+path)
    require(target.is_file(), 'missing file: '+str(target))
    return target


def git(root, *arguments):
    return subprocess.check_output(['git', '-C', str(root), *arguments])


def validate(plan):
    design = plan.parent/'NativeWeave-Design'
    native = plan.parent/'NativeWeave'
    baseline = read_json(plan/'source-driven-baseline.json')
    checkpoint = read_json(plan/'ledger/checkpoints/research-assets-migration-2026-11-12.json')
    pairing = baseline['research_asset_migration']
    require(baseline['design_merge_commit'] == checkpoint['design_merge_commit'] == pairing['design_merge_commit'], 'Design pair drift')
    require(git(design, 'rev-parse', 'HEAD').decode().strip() == checkpoint['design_merge_commit'], 'wrong Design checkout')
    require(git(native, 'rev-parse', 'HEAD').decode().strip() == checkpoint['original_source_commit'], 'wrong original source checkout')
    require(not git(design, 'diff', checkpoint['design_pr_head'], checkpoint['design_merge_commit'], '--'), 'Design PR head differs from merge')
    require(not git(design, 'diff', 'HEAD', '--'), 'Design working tree differs from pinned snapshot')
    require(not git(native, 'diff', 'HEAD', '--'), 'original source working tree differs from pinned snapshot')
    require(digest((design/'docs/contracts/registry.json').read_bytes()) == baseline['contract_registry_sha256'], 'contract registry hash mismatch')
    require((design/'docs/contracts/registry.json').read_bytes() == git(design, 'show', baseline['prior_native_slice_design_baseline']['design_merge_commit']+':docs/contracts/registry.json'), 'migration changed contracts')

    mapping_path = contained(design, checkpoint['migration_map_path'])
    results_path = contained(design, checkpoint['migration_results_path'])
    mapping, results = read_json(mapping_path), read_json(results_path)
    require(digest(mapping_path.read_bytes()) == checkpoint['migration_map_sha256'] == pairing['map_sha256'], 'migration map hash mismatch')
    require(digest(results_path.read_bytes()) == checkpoint['migration_results_sha256'] == pairing['results_sha256'], 'migration result hash mismatch')
    require(mapping['source_head'] == checkpoint['original_source_commit'], 'original source identity drift')
    require(mapping['source_base'] == checkpoint['original_source_base'], 'original base identity drift')
    rows = mapping['records']
    require(len(rows) == mapping['mapped_files'] == checkpoint['expected_mapped_assets'], 'incomplete migration inventory')
    source_paths = [r['source_path'] for r in rows]
    target_paths = [r['destination_path'] for r in rows]
    require(len(set(source_paths)) == len(rows) == len(set(target_paths)), 'duplicate source/destination migration path')
    pr_paths = git(native, 'diff', '--name-only', checkpoint['original_source_base'], checkpoint['original_source_commit'], '--').decode().splitlines()
    require(sorted(pr_paths) == sorted(source_paths), 'PR file list differs from migration inventory')
    by_source = {r['source_path']: r for r in rows}
    for row in rows:
        original = contained(native, row['source_path']).read_bytes()
        relocated = contained(design, row['destination_path']).read_bytes()
        require(row['source_commit'] == checkpoint['original_source_commit'], 'mixed original source commit')
        require(digest(original) == row['source_sha256'], 'original SHA256: '+row['source_path'])
        require(blob_digest(original) == row['source_blob_sha1'], 'original Git blob: '+row['source_path'])
        require(digest(relocated) == row['destination_sha256'], 'relocated SHA256: '+row['destination_path'])
        require(blob_digest(relocated) == row['destination_blob_sha1'], 'relocated Git blob: '+row['destination_path'])
        require(row['byte_exact'] == (original == relocated), 'byte-exact flag mismatch: '+row['source_path'])
    require(sum(r['byte_exact'] for r in rows) == checkpoint['expected_byte_exact_assets'], 'byte-exact count mismatch')
    adapted = {r['source_path'] for r in rows if not r['byte_exact']}
    require(adapted == {'experiments/interop/run.py', 'experiments/run_domains.py'}, 'unexpected source adaptation')
    require(len(adapted) == checkpoint['expected_adapted_drivers'], 'adapted driver count mismatch')

    original_path = contained(design, pairing['original_evidence_manifest'])
    original_manifest = read_json(original_path)
    require(original_path.read_bytes() == contained(native, 'verification/native-slices/manifest.json').read_bytes(), 'original manifest was rewritten')
    original_count = 0
    for record in original_manifest['records']:
        for file in record['files']:
            row = by_source[file['path']]
            raw = contained(design, row['destination_path']).read_bytes()
            require(digest(raw) == file['sha256'], 'original evidence hash mismatch: '+file['path'])
            original_count += 1
    require(original_count == checkpoint['expected_original_raw_files'], 'original raw evidence count mismatch')
    require(len(original_manifest['records']) == checkpoint['expected_original_records'], 'original record count mismatch')
    require(sum(r['success'] for r in original_manifest['records']) == checkpoint['expected_original_successes'], 'original success count mismatch')
    require(sum(not r['success'] for r in original_manifest['records']) == checkpoint['expected_original_failed_attempts'], 'original failure evidence missing')

    require(results['migration_map_sha256'] == checkpoint['migration_map_sha256'], 'execution used a different migration map')
    require(results['repository'] == pairing['repository'] == 'IzuSharp/NativeWeave-Design', 'new evidence repository mismatch')
    require(results['tested_design_commit'] == checkpoint['tested_design_commit'] == pairing['tested_design_commit'], 'new tested source mismatch')
    require(str(results['run_id']) == checkpoint['design_run_id'] == pairing['run_id'], 'new run identity mismatch')
    require(results['all_six_jobs_passed'] is True and len(results['records']) == checkpoint['expected_new_platform_jobs'], 'new platform execution incomplete')
    require(results['original_history_relabelled'] is False and results['product_delivery_executed'] is False, 'evidence scope changed')
    expected_artifacts = {f'relocated-{domain}-{osname}' for domain in ('interop','database','server') for osname in ('ubuntu-24.04','windows-2022')}
    require({r['artifact'] for r in results['records']} == expected_artifacts, 'domain/platform matrix mismatch')
    evidence_paths = []
    checked_sources = 0
    matrix = []
    for record in results['records']:
        require(record['success'] is True and record['tested_design_commit'] == checkpoint['tested_design_commit'], 'unsuccessful or mismatched new record')
        require(re.fullmatch(r'[0-9a-f]{64}', record['artifact_zip_sha256']) is not None, 'invalid artifact hash')
        for file in record['files']:
            raw = contained(design, file['path']).read_bytes()
            require(digest(raw) == file['sha256'] and len(raw) == file['bytes'], 'new raw evidence mismatch: '+file['path'])
            evidence_paths.append(file['path'])
        paths = [f['path'] for f in record['files'] if f['path'].endswith('/result.json')]
        require(len(paths) == 1, 'missing/duplicate fixture result')
        result = read_json(contained(design, paths[0]))
        require(result['success'] is True and result['source_commit'] == checkpoint['tested_design_commit'], 'fixture source/result mismatch')
        require(str(result['run_id']) == checkpoint['design_run_id'], 'fixture run mismatch')
        for path, expected_hash in result['source_files'].items():
            require(digest(contained(design/'experiments/native-slices', path).read_bytes()) == expected_hash, 'executed source or lock differs: '+path)
            checked_sources += 1
        if record['artifact'].startswith('relocated-interop-'):
            require(result['clean_rust_free_host'] is False, 'clean-host scope was incorrectly upgraded')
            for field in ('native_sha256','package_sha256','aot_executable_sha256'):
                require(re.fullmatch(r'[0-9a-f]{64}', result[field]) is not None, 'missing binary identity')
        matrix.append({'artifact': record['artifact'], 'success': True, 'source_commit': result['source_commit'], 'platform': result['platform']})
    require(len(evidence_paths) == len(set(evidence_paths)) == checkpoint['expected_new_raw_files'], 'new raw evidence count/uniqueness mismatch')

    old_checkpoint = contained(plan, checkpoint['original_checkpoint_path'])
    require(digest(old_checkpoint.read_bytes()) == checkpoint['original_checkpoint_sha256'], 'historical checkpoint rewritten')
    require(old_checkpoint.read_bytes() == git(plan, 'show', checkpoint['plan_base']+':'+checkpoint['original_checkpoint_path']), 'historical checkpoint changed from base')
    changed = []
    counts = {}
    for kind in ('research','documentation','delivery'):
        graph = read_json(plan/f'{kind}-graph.json')
        before = json.loads(git(plan, 'show', checkpoint['plan_base']+f':{kind}-graph.json'))
        prior = {node['id']: node for node in before['nodes']}
        require({n['id'] for n in graph['nodes']} == set(prior), 'task IDs changed: '+kind)
        counts[kind] = len(graph['nodes'])
        for node in graph['nodes']:
            nid = node['id']
            require(node['status'] == prior[nid]['status'], 'migration changed task state: '+nid)
            packet = contained(plan, node['prompt']).read_bytes()
            require(digest(packet) == node['packet_sha256'], 'packet hash mismatch: '+nid)
            require(('Revision: **'+node['revision']+'**').encode() in packet, 'packet revision mismatch: '+nid)
            previous = git(plan, 'show', checkpoint['plan_base']+':'+node['prompt'])
            if packet != previous:
                changed.append(nid)
            if nid in checkpoint['directly_updated_tasks']:
                continuation = node['continuation_evidence']
                require(continuation[:-1] == prior[nid]['continuation_evidence'], 'historical task evidence rewritten: '+nid)
                latest = continuation[-1]
                require(latest['repository'] == pairing['repository'] and latest['design_commit'] == checkpoint['design_merge_commit'], 'task Design identity mismatch: '+nid)
                require(latest['evidence_manifest_sha256'] == checkpoint['migration_results_sha256'] and latest['migration_map_sha256'] == checkpoint['migration_map_sha256'], 'task migration hash mismatch: '+nid)
                require(latest['original_evidence_commit'] == checkpoint['original_source_commit'] and latest['tested_design_commit'] == checkpoint['tested_design_commit'], 'task execution identity mismatch: '+nid)
                require(latest['product_acceptance'] is False, 'migration promoted task acceptance: '+nid)
    require(counts == {'research':34,'documentation':32,'delivery':48}, 'graph counts changed')
    require(sorted(changed) == checkpoint['changed_packets'] and len(changed) == 33, 'unexpected packet changes')
    require(114-len(changed) == checkpoint['unchanged_packets'], 'unchanged packet count mismatch')
    require((plan/'delivery-graph.json').read_bytes() == git(plan, 'show', checkpoint['plan_base']+':delivery-graph.json'), 'future Delivery graph changed')
    return {
        'ok':True,'scope':'Saved evidence and Plan-pair integrity only; no new native execution or product acceptance',
        'design_merge_commit':checkpoint['design_merge_commit'],'tested_design_commit':checkpoint['tested_design_commit'],
        'design_run_id':checkpoint['design_run_id'],'original_source_commit':checkpoint['original_source_commit'],
        'mapped_assets_verified':len(rows),'byte_exact_assets':sum(r['byte_exact'] for r in rows),'adapted_drivers':sorted(adapted),
        'original_raw_files_verified':original_count,'original_success_records':6,'original_failed_attempts_preserved':2,
        'new_raw_files_verified':len(evidence_paths),'executed_source_hashes_verified':checked_sources,'matrix':matrix,
        'task_counts':counts,'changed_packets':sorted(changed),'unchanged_packets':81,'task_states_changed':False,
        'delivery_graph_changed':False,'contract_registry_changed':False,
        'limitations':['This run checks archived evidence and identity, not the execution of the original commands.',
                       'Artifact ZIP and binary hashes are preserved references; this check does not redownload binaries.',
                       'No independent technical acceptance, GitHub review approval or NativeWeave PR closure is inferred.'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    try:
        report = validate(args.root.resolve())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print('FAIL: '+str(error),file=sys.stderr)
        return 1
    rendered = json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(rendered,encoding='utf-8')
    print(rendered,end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
