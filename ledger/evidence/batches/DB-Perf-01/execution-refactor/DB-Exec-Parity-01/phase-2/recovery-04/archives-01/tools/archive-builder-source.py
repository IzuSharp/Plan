#!/usr/bin/env python3
"""Preserve completed recovery-03 evidence without changing original artifacts.

Run only outside ordinary timing. Default is a stat-only selection preview.
--execute hashes, snapshots source, archives, and checks every restored member.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import lzma
import os
from pathlib import Path
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '7ff7b57b907b689defb880b8af62d83679608603'
PLAN_COMMIT = 'e99b2291be9371c548a5d80a4133281bccb4bc2b'
PLAN_PREFIX = 'ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01'
FOUNDATION = ROOT / 'experiments/recovery/foundation-archive'
DIR_EXCLUSIONS = {'obj', 'bin', 'packages', 'nuget-packages', '__pycache__', '.git',
                  'postgres-data', 'CMakeFiles', '_deps', '.cmake'}
INTERMEDIATE_SUFFIXES = {'.o', '.obj', '.a'}
GROUPS = {
    'ordinary-risk-recovery03': [
        'experiments/ordinary-ab-recovery-03',
        'experiments/ordinary-ab-recovery-03-attempt-02',
        'experiments/ordinary-risk-recovery-03',
    ],
    'resource-diagnostics-recovery03': [
        'experiments/codec-recovery-03',
        'experiments/relations-recovery-03',
        'experiments/sqlite-prepare-recovery-03',
    ],
    'worker-d-diagnostics-recovery03': [
        'experiments/worker-d-diagnostic',
        'builds/worker-d-diagnostic',
        'consumers/worker-d-diagnostic',
        'observations/worker-d-diagnostic',
        'observations/worker-d-ready-scheduling-aot',
        'observations/worker-d-ready-scheduling-aot-mask-fixed',
        'observations/worker-d-ready-scheduling-review',
        'observations/worker-d-native',
        'observations/worker-d-ordinary-review',
        'builds/worker-d-native-check',
        'builds/worker-d-ready-scheduling-correctness-inputs',
        'builds/worker-d-ready-scheduling-correctness-inputs-mask-fixed',
    ],
    'candidate-artifacts-recovery03': [
        'builds/codec-matched-postgresql',
        'builds/codec-matched-sqlite',
        'builds/sqlite-prepare-matched',
        'builds/worker-d-matched',
        'builds/workerd-codec-risk-postgresql',
        'consumers/codec03-postgresql',
        'consumers/sqliteprepare03-sqlite',
        'consumers/workerd03-postgresql',
        'consumers/workerd03-sqlite',
        'observations/environment',
        'observations/builds',
        'observations/recovery',
        'local-tools',
    ],
    'server-runtime-recovery03': ['toolchain/postgres-18.0/install'],
}
SOURCES = [
    'Korda-codec', 'Korda-relations', 'Korda-relations-baseline',
    'Korda-relations-candidate-diagnostic', 'Korda-relations-deep-diagnostic',
    'Korda-relations-diagnostic', 'Korda-sqlite-prepare', 'Korda-worker-d',
    'Korda-worker-d-baseline-diagnostic', 'Korda-worker-d-candidate-diagnostic',
    'Korda-worker-d-codec-risk', 'Korda-worker-d-managed', 'Korda-worker-d-native',
    'Korda-worker-d-scheduling-tests',
]
EXCLUSION_NOTES = [
    'Existing Stage1 archives stay unchanged and supply the original baseline, diagnostic support tools, sampler and allocator shim.',
    'The two locally completed foundation archives are reused byte-for-byte, not recompressed.',
    'Physical PostgreSQL cluster data, SQLite fixture/WAL/SHM bytes, compiler obj/bin/CMake intermediate directories, static intermediate archives and caches are excluded. Fixture seed/SQL/DTO sources, exact initializer identities, commands, settings, process logs and raw measurements remain. This is not a physical database backup.',
    'New recovery-04 work and ongoing experiments are excluded by explicit source-root selection and recovery-04 path rejection. No uniqueness claim is made for those new results.',
    'SDK/LLVM/CMake/Ninja downloadable installations and NuGet caches are not copied; pinned dependency locks, source base commit, installation receipts, restored assets, actual consumer ELF/debug/native/packages and build commands are preserved.',
    'A symlink to a regular file within a selected tree is stored as the dereferenced file bytes at its original relative path; the original target is listed separately. No directory symlink is traversed.',
]


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(directory, *args):
    return subprocess.check_output(['git', '-C', str(directory), *args])


def excluded_name(path):
    name = path.name
    if 'recovery-04' in name or 'recovery04' in name:
        return 'current recovery-04 work'
    if path.suffix in INTERMEDIATE_SUFFIXES:
        return 'reproducible compiler/linker intermediate'
    if name.endswith(('.sqlite', '.sqlite-wal', '.sqlite-shm', '.db', '.db-wal', '.db-shm')):
        return 'deterministic physical database fixture; source and commands retained'
    return None


def collect():
    groups = {}
    excluded = []
    symlinks = []
    for group, trees in GROUPS.items():
        selected = {}
        for name in trees:
            tree = ROOT / name
            if not tree.is_dir():
                raise FileNotFoundError(tree)
            for current, directories, filenames in os.walk(tree):
                keep = []
                for child in sorted(directories):
                    path = Path(current, child)
                    snapshot_obj = child == 'obj' and 'compiler-generated-snapshot' in path.parts
                    reason = ('excluded directory component' if child in DIR_EXCLUSIONS and not snapshot_obj else
                              'current recovery-04 work' if 'recovery-04' in child or 'recovery04' in child else
                              'directory symlink not followed' if path.is_symlink() else None)
                    if reason:
                        excluded.append({'path': path.relative_to(ROOT).as_posix(), 'reason': reason})
                        if child == 'obj':
                            # Restore assets, actual AOT response/export files and
                            # generated C# are evidence even inside an obj tree.
                            for evidence in sorted(path.rglob('*')):
                                if evidence.is_file() and (evidence.suffix in {'.json', '.rsp', '.cs', '.xml', '.props', '.targets', '.exports'}
                                                           or evidence.name == 'runtimeconfig.bin'):
                                    selected[evidence.relative_to(ROOT).as_posix()] = evidence
                    else:
                        keep.append(child)
                directories[:] = keep
                for child in sorted(filenames):
                    path = Path(current, child)
                    reason = excluded_name(path)
                    if reason:
                        excluded.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size, 'reason': reason})
                        continue
                    if not path.is_file():
                        raise ValueError('Unexpected non-file: ' + str(path))
                    if path.is_symlink():
                        symlinks.append({'path': path.relative_to(ROOT).as_posix(), 'target': os.readlink(path),
                                         'storedAs': 'regular file with exact target bytes'})
                    selected[path.relative_to(ROOT).as_posix()] = path
        groups[group] = selected
    # Install/bin are actual measured server programs; the generic bin exclusion
    # above is for managed build intermediates only. Preserve the full PG install.
    pg = groups['server-runtime-recovery03']
    pg_bin = ROOT / 'toolchain/postgres-18.0/install/bin'
    for path in sorted(pg_bin.rglob('*')):
        if path.is_file():
            pg[path.relative_to(ROOT).as_posix()] = path
    excluded = [x for x in excluded if x['path'] != pg_bin.relative_to(ROOT).as_posix()]
    for name in ['build.log', 'configure.log', 'install.log', 'postgresql-18.0.tar.bz2']:
        path = ROOT / 'toolchain/postgres-18.0' / name
        pg[path.relative_to(ROOT).as_posix()] = path
    return groups, excluded, symlinks


def capture_sources(output):
    folder = output / 'source-snapshots'
    folder.mkdir()
    states = []
    for name in SOURCES:
        tree = ROOT / 'worktrees' / name
        head = git(tree, 'rev-parse', 'HEAD').decode().strip()
        status = git(tree, 'status', '--porcelain=v1').decode()
        if status:
            raise ValueError(f'Refuse mutable source snapshot {name}: {status}')
        target = folder / name
        target.mkdir()
        diff = git(tree, 'diff', '--binary', '--full-index', BASE, head)
        (target / 'from-main.patch').write_bytes(diff)
        paths = git(tree, 'diff', '--name-only', '-z', BASE, head).decode().split('\0')
        changed = []
        for path in filter(None, paths):
            probe = subprocess.run(['git', '-C', str(tree), 'cat-file', '-e', head + ':' + path], capture_output=True)
            if probe.returncode:
                changed.append({'path': path, 'deleted': True})
                continue
            content = git(tree, 'show', head + ':' + path)
            dest = target / 'changed-files' / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            changed.append({'path': path, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
        if head != BASE:
            bundle = target / 'commits.bundle'
            subprocess.run(['git', '-C', str(tree), 'bundle', 'create', str(bundle), 'HEAD', '^' + BASE],
                           check=True, capture_output=True)
            verification = subprocess.run(['git', '-C', str(tree), 'bundle', 'verify', str(bundle)],
                                          check=True, capture_output=True, text=True)
            (target / 'bundle-verification.txt').write_text(verification.stdout + verification.stderr)
        if git(tree, 'rev-parse', 'HEAD').decode().strip() != head:
            raise ValueError('Source HEAD changed during snapshot: ' + name)
        record = {'worktree': name, 'baseCommit': BASE, 'headCommit': head,
                  'tree': git(tree, 'rev-parse', head + '^{tree}').decode().strip(),
                  'statusAtSnapshot': status, 'changedFiles': changed, 'patchSha256': sha(target / 'from-main.patch')}
        dump(target / 'identity.json', record)
        states.append(record)
    dump(output / 'source-snapshots.json', states)
    selected = {p.relative_to(ROOT).as_posix(): p for p in folder.rglob('*') if p.is_file()}
    selected[(output / 'source-snapshots.json').relative_to(ROOT).as_posix()] = output / 'source-snapshots.json'
    return selected


def archive_one(name, selected, output, exclusions, links):
    files = []
    for relative, path in sorted(selected.items()):
        before = path.stat()
        digest = sha(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise RuntimeError('Source changed during archive selection: ' + str(path))
        files.append({'path': relative, 'bytes': before.st_size, 'sha256': digest})
    print(json.dumps({'phase': 'hashed', 'name': name, 'files': len(files),
                      'expandedBytes': sum(x['bytes'] for x in files)}), flush=True)
    package = output / 'evidence-packages'
    package.mkdir(exist_ok=True)
    tar_path = package / (name + '.tar')
    with tarfile.open(tar_path, 'w', format=tarfile.PAX_FORMAT, dereference=True) as tar:
        for item in files:
            path = selected[item['path']]
            info = tar.gettarinfo(str(path), arcname=item['path'])
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ''
            info.pax_headers = {}
            if not info.isfile():
                raise ValueError('Only regular bytes may enter archive: ' + str(path))
            with path.open('rb') as stream:
                tar.addfile(info, stream)
    tar_sha = sha(tar_path)
    xz_path = package / (name + '.tar.xz')
    command = ['xz', '--threads=1', '--check=crc64', '-3', '--stdout', str(tar_path)]
    with xz_path.open('xb') as stream:
        subprocess.run(command, stdout=stream, check=True)
    with lzma.open(xz_path, 'rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != tar_sha:
            raise RuntimeError('Compression byte mismatch: ' + name)
    record = {'path': xz_path.relative_to(output).as_posix(), 'bytes': xz_path.stat().st_size, 'sha256': sha(xz_path)}
    manifest = {'task': 'DB-Exec-Parity-01', 'name': name, 'files': files, 'fileCount': len(files),
                'expandedBytes': sum(x['bytes'] for x in files), 'archive': record,
                'originalWorkspaceRoot': str(ROOT), 'sourceBaseCommit': BASE,
                'noNewPerformanceCredit': True, 'noOriginalFileDeleted': True,
                'exclusionNotes': EXCLUSION_NOTES, 'excludedPaths': exclusions, 'dereferencedSymlinks': links}
    raw = output / 'raw-archives'
    folder = raw / name
    folder.mkdir(parents=True)
    parts = []
    with xz_path.open('rb') as stream:
        while block := stream.read(4 * 1024 * 1024):
            part = folder / f'part-{len(parts):04d}.bin'
            part.write_bytes(block)
            parts.append({'path': part.relative_to(raw).as_posix(), 'bytes': len(block),
                          'sha256': hashlib.sha256(block).hexdigest(),
                          'gitBlobSha': hashlib.sha1(f'blob {len(block)}\0'.encode() + block).hexdigest()})
    encoding = {'xz': record, 'tarSha256': tar_sha, 'command': command, 'singleThread': True,
                'nice': os.nice(0), 'cpus': sorted(os.sched_getaffinity(0)), 'byteVerificationPassed': True}
    dump(folder / 'expanded-file-manifest.json', manifest)
    dump(folder / 'compression-identity.json', encoding)
    dump(package / (name + '.json'), manifest)
    # Only this freshly generated, hash-verified uncompressed staging tar is removed.
    # No source evidence or existing artifact is touched.
    tar_path.unlink()
    entry = {'name': name, 'filename': xz_path.name, 'archive': record, 'tarSha256': tar_sha,
             'parts': parts, 'expandedFileManifest': f'{name}/expanded-file-manifest.json',
             'compressionIdentity': f'{name}/compression-identity.json'}
    print(json.dumps({'phase': 'compressed', 'name': name, 'bytes': record['bytes'], 'parts': len(parts)}), flush=True)
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    groups, exclusions, links = collect()
    selection = {'task': 'DB-Exec-Parity-01', 'originalRoot': str(ROOT), 'startedUtc': utc(),
                 'groups': {name: {'files': len(paths), 'bytes': sum(p.stat().st_size for p in paths.values())}
                            for name, paths in groups.items()},
                 'sourceWorktrees': SOURCES, 'exclusionNotes': EXCLUSION_NOTES,
                 'excludedPaths': exclusions, 'dereferencedSymlinks': links,
                 'ordinaryTimingWindowAllowed': False}
    if not args.execute:
        print(json.dumps(selection, indent=2))
        return
    os.sched_setaffinity(0, {8})
    os.nice(max(0, 19 - os.nice(0)))
    output = HERE / 'output'
    output.mkdir(exist_ok=False)
    dump(output / 'selection.json', selection)
    source_files = capture_sources(output)
    groups['candidate-artifacts-recovery03'].update(source_files)
    groups['candidate-artifacts-recovery03'][Path(__file__).relative_to(ROOT).as_posix()] = Path(__file__)
    groups['candidate-artifacts-recovery03'][(output / 'selection.json').relative_to(ROOT).as_posix()] = output / 'selection.json'
    # Exact prior upload-ready parts are linked into this standalone publication
    # set. Links do not rewrite the originals or reassign measured identities.
    raw = output / 'raw-archives'
    raw.mkdir()
    original_index = json.loads((FOUNDATION / 'raw-archives/index.json').read_text())
    entries = list(original_index['archives'])
    for entry in entries:
        names = [p['path'] for p in entry['parts']] + [entry['expandedFileManifest'], entry['compressionIdentity']]
        for relative in names:
            source = FOUNDATION / 'raw-archives' / relative
            target = raw / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.link(source, target)
    for name, paths in groups.items():
        entries.append(archive_one(name, paths, output, exclusions, links))
        dump(raw / 'index.json', {'task': 'DB-Exec-Parity-01', 'format': 'ordered concatenated xz tar parts',
                                 'archives': entries})
    restorer = FOUNDATION / 'restore_evidence.py'
    shutil.copy2(restorer, output / 'restore_evidence.py')
    command = ['python3', str(output / 'restore_evidence.py'), 'all', '--output', str(output / 'roundtrip')]
    with (output / 'roundtrip.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    receipt = {'task': 'DB-Exec-Parity-01', 'finishedUtc': utc(), 'originalWorkspaceRoot': str(ROOT),
               'archives': [{'name': x['name'], 'bytes': x['archive']['bytes'],
                             'sha256': x['archive']['sha256'], 'parts': len(x['parts'])} for x in entries],
               'allPartsAndEveryExpandedFileSha256Verified': True,
               'indexSha256': sha(raw / 'index.json'), 'restorerSha256': sha(output / 'restore_evidence.py'),
               'verifyCommand': command, 'verifyLogSha256': sha(output / 'roundtrip.log'),
               'files': sum(json.loads((raw / x['expandedFileManifest']).read_text())['fileCount'] for x in entries),
               'noNewPerformanceCredit': True, 'noOriginalSourceOrEvidenceDeleted': True,
               'planWorktreeModified': False, 'remotePublication': False,
               'sourceBaseCommit': BASE, 'requiredPriorEvidenceCommit': PLAN_COMMIT,
               'requiredPriorEvidencePath': PLAN_PREFIX + '/raw-archives',
               'existingStage1ArchivesUnchanged': True,
               'reusedFoundationIndexSha256': sha(FOUNDATION / 'raw-archives/index.json')}
    dump(output / 'verification.json', receipt)
    upload = []
    for p in sorted(raw.rglob('*')):
        if p.is_file():
            content = p.read_bytes()
            upload.append({'path': p.relative_to(output).as_posix(), 'bytes': len(content),
                           'sha256': hashlib.sha256(content).hexdigest(),
                           'gitBlobSha': hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()})
    for p in [output / 'verification.json', output / 'restore_evidence.py', output / 'roundtrip.log']:
        content = p.read_bytes()
        upload.append({'path': p.relative_to(output).as_posix(), 'bytes': len(content),
                       'sha256': hashlib.sha256(content).hexdigest(),
                       'gitBlobSha': hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()})
    dump(output / 'upload-manifest.json', {'task': 'DB-Exec-Parity-01', 'files': upload,
                                         'bytes': sum(x['bytes'] for x in upload), 'remotePublication': False})
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
