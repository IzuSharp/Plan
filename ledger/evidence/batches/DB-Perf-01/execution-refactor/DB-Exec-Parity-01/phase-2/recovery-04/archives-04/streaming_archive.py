#!/usr/bin/env python3
"""Closed Recovery04/05 evidence: tar -> single-thread liblzma -> 4 MiB parts.

No full tar, canonical xz, or verification extraction copy is created. Run only
outside ordinary measurement windows. `verify` reads and checks every member;
`restore --extract ROOT` additionally restores the original relative paths.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import lzma
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / 'supplement-02'
BASE = '7ff7b57b907b689defb880b8af62d83679608603'
PART_BYTES = 4 * 1024 * 1024
DIR_EXCLUSIONS = {'obj', 'bin', 'packages', 'nuget-packages', '__pycache__', '.git',
                  'postgres-data', 'CMakeFiles', '_deps', '.cmake'}
EVIDENCE_SUFFIXES = {'.json', '.rsp', '.cs', '.xml', '.props', '.targets', '.exports'}
GROUPS = {
    'sampler-caller04': ['experiments/sampler04', 'consumers/workerdcodec04-postgresql',
                         'builds/workerd-codec-risk-postgresql/package-consumer-04'],
    'relation-capacity04': ['experiments/relations-recovery-04'],
    'integrated-combined05': [
        'builds/integrated04-sqlite', 'builds/integrated04-postgresql',
        'builds/integrated05-sqlite', 'builds/integrated05-postgresql',
        'consumers/integrated04-sqlite', 'consumers/integrated04-postgresql',
        'consumers/integrated05-sqlite', 'consumers/integrated05-postgresql',
        'observations/recovery/integrated-build-intermediates-05',
        'experiments/recovery/combined-screen-05', 'local-tools',
        'experiments/worker-d-diagnostic/early-stop-review-05'],
    'closed-runner-review05': [
        'experiments/relations-recovery-04/runner-review',
        'experiments/recovery/run_proc_tree_observer.py',
        'experiments/recovery/check_proc_tree_observer.py',
        'experiments/recovery/check_proc_cpu_transfer.py',
        'experiments/recovery/analyze_proc_cpu_transfer.py'],
}
SOURCE_TREES = ['Korda', 'Korda-integrated04-sqlite', 'Korda-integrated04-postgresql',
                'Korda-integrated05-sqlite', 'Korda-integrated05-postgresql',
                'Korda-relations-capacity-04', 'Korda-relations-capacity-diagnostic-04']
NOTES = [
    'Only sealed experiments are selected. Failed attempts, parser errata, partial disk-full records and rejected callchains retain their original verdicts.',
    'This increment depends on archives-01 at Plan b54054bd1f3befe94e1817cc29f494bd782854b9 for baseline/Dapper actual consumers, server runtime, earlier diagnostics and locked foundation tools.',
    'relations-recovery-04/deep-layer is already preserved in archives-01/closed-diagnostics-recovery04 and is excluded here byte-for-byte.',
    'Physical PostgreSQL clusters and SQLite database/WAL/SHM fixtures are excluded; seed/SQL/DTO sources, exact commands, identities and process logs remain. This is not a physical database backup.',
    'Compiler intermediates/caches are excluded. Actual ELF, debug symbols, native libraries, nupkg, generated C#, restored assets and response/export files are retained. The prior retained-intermediates directory is kept in full.',
    'Sampler diagnostics are attribution only. combined-screen-05 contains short ordinary A/B evidence, not 30-minute final acceptance cells.',
    'Built local commit identities and connector-published commit identities are both preserved; same-tree mappings do not relabel measured artifacts.',
    'Symlink files, if any, are dereferenced with the original link target recorded. Directory symlinks are not followed.',
]


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    os.replace(temporary, path)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(directory, *arguments):
    return subprocess.check_output(['git', '-C', str(directory), *arguments])


def stamp(path):
    value = Path(path).stat()
    return [value.st_size, value.st_mtime_ns, value.st_ino]


def safe_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('Unsafe member path: ' + name)
    return path


def capture_sources():
    folder = OUTPUT / 'source-snapshots'
    folder.mkdir(parents=True, exist_ok=False)
    records = []
    for name in SOURCE_TREES:
        source = ROOT / 'worktrees' / name
        head = git(source, 'rev-parse', 'HEAD').decode().strip()
        status = git(source, 'status', '--porcelain=v1').decode()
        if status:
            raise RuntimeError('Source worktree is not clean: ' + name)
        target = folder / name
        target.mkdir()
        patch = target / 'from-main.patch'
        patch.write_bytes(git(source, 'diff', '--binary', '--full-index', BASE, head))
        changed = []
        for relative in filter(None, git(source, 'diff', '--name-only', '-z', BASE, head).decode().split('\0')):
            exists = subprocess.run(['git', '-C', str(source), 'cat-file', '-e', head + ':' + relative], capture_output=True)
            if exists.returncode:
                changed.append({'path': relative, 'deleted': True})
                continue
            content = git(source, 'show', head + ':' + relative)
            dest = target / 'changed-files' / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            changed.append({'path': relative, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
        bundle = target / 'commits.bundle'
        subprocess.run(['git', '-C', str(source), 'bundle', 'create', str(bundle), 'HEAD', '^' + BASE], check=True, capture_output=True)
        verify = subprocess.run(['git', '-C', str(source), 'bundle', 'verify', str(bundle)], check=True, capture_output=True, text=True)
        (target / 'bundle-verification.txt').write_text(verify.stdout + verify.stderr)
        if git(source, 'rev-parse', 'HEAD').decode().strip() != head or git(source, 'status', '--porcelain=v1').decode() != status:
            raise RuntimeError('Source changed during capture: ' + name)
        record = {'worktree': name, 'headCommit': head, 'tree': git(source, 'rev-parse', head + '^{tree}').decode().strip(),
                  'baseCommit': BASE, 'statusAtSnapshot': status, 'patchSha256': sha(patch),
                  'bundleSha256': sha(bundle), 'changedFiles': changed}
        dump(target / 'identity.json', record)
        records.append(record)
    dump(OUTPUT / 'source-snapshots.json', records)


def select():
    groups, exclusions, links = {}, {}, {}
    for name, roots in GROUPS.items():
        selected, rejected, symlinks = {}, [], []
        def add(path):
            relative = path.relative_to(ROOT).as_posix()
            if path.is_symlink():
                symlinks.append({'path': relative, 'target': os.readlink(path), 'storedAs': 'regular bytes'})
            selected[relative] = {'path': relative, 'stamp': stamp(path)}
        for relative in roots:
            tree = ROOT / relative
            if tree.is_file():
                add(tree)
                continue
            if not tree.is_dir():
                raise FileNotFoundError(tree)
            for current, directories, filenames in os.walk(tree, followlinks=False):
                keep = []
                for child in sorted(directories):
                    path = Path(current, child)
                    rel = path.relative_to(ROOT).as_posix()
                    reason = None
                    retained = 'integrated-build-intermediates-05/retained/' in rel
                    if rel == 'experiments/relations-recovery-04/deep-layer':
                        reason = 'already in archives-01/closed-diagnostics-recovery04'
                    elif rel == 'experiments/relations-recovery-04/runner-review':
                        reason = 'later runner review is still being written; original capacity evidence is sealed'
                    elif path.is_symlink():
                        reason = 'directory symlink not followed'
                    elif child in DIR_EXCLUSIONS and not retained:
                        reason = 'physical database or reproducible compiler/cache directory'
                    if reason:
                        rejected.append({'path': rel, 'reason': reason})
                        if child == 'obj':
                            for item in sorted(path.rglob('*')):
                                if item.is_file() and (item.suffix in EVIDENCE_SUFFIXES or item.name == 'runtimeconfig.bin'):
                                    add(item)
                    else:
                        keep.append(child)
                directories[:] = keep
                for child in sorted(filenames):
                    path = Path(current, child)
                    reason = ('compiler intermediate' if path.suffix in {'.o', '.obj', '.a'} else
                              'physical database fixture' if child.endswith(('.sqlite', '.sqlite-wal', '.sqlite-shm', '.db', '.db-wal', '.db-shm')) else None)
                    if reason:
                        rejected.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size, 'reason': reason})
                    elif path.is_file():
                        add(path)
                    else:
                        raise RuntimeError('Unexpected non-file: ' + str(path))
        if name == 'integrated-combined05':
            extras = list((OUTPUT / 'source-snapshots').rglob('*')) + [OUTPUT / 'source-snapshots.json']
            extras += list((ROOT / 'observations/builds').glob('integrated0[45]-*.log'))
            extras += [p for p in (ROOT / 'observations/recovery').iterdir() if p.is_file() and any(s in p.name for s in ('publication', 'published', 'checkpoint'))]
            extras += [ROOT / 'experiments/worker-d-diagnostic/integrated-independent-review-04.md',
                       ROOT / 'experiments/worker-d-diagnostic/common-a-combination-prediction-04.md']
            for path in extras:
                if path.is_file():
                    add(path)
        groups[name] = sorted(selected.values(), key=lambda x: x['path'])
        exclusions[name], links[name] = rejected, symlinks
    return {'task': 'DB-Exec-Parity-01', 'createdUtc': utc(), 'root': str(ROOT), 'groups': groups,
            'excludedPaths': exclusions, 'dereferencedSymlinks': links, 'notes': NOTES,
            'noNewPerformanceCredit': True, 'remotePublication': False}


class PartWriter:
    def __init__(self, folder, name):
        self.folder, self.name = folder, name
        folder.mkdir(parents=True, exist_ok=False)
        self.pending = bytearray()
        self.parts = []
        self.digest, self.count = hashlib.sha256(), 0

    def write(self, data):
        self.digest.update(data)
        self.count += len(data)
        self.pending.extend(data)
        while len(self.pending) >= PART_BYTES:
            self.flush_part(bytes(self.pending[:PART_BYTES]))
            del self.pending[:PART_BYTES]

    def flush_part(self, data):
        path = self.folder / ('part-%04d.bin' % len(self.parts))
        temporary = path.with_suffix('.partial')
        temporary.write_bytes(data)
        os.replace(temporary, path)
        self.parts.append({'path': self.name + '/' + path.name, 'bytes': len(data),
                           'sha256': hashlib.sha256(data).hexdigest(),
                           'gitBlobSha': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()})

    def finish(self):
        if self.pending:
            self.flush_part(bytes(self.pending))
            self.pending.clear()


class TarCompressor:
    def __init__(self, writer):
        self.writer = writer
        self.compressor = lzma.LZMACompressor(format=lzma.FORMAT_XZ, check=lzma.CHECK_CRC64, preset=3)
        self.digest, self.count = hashlib.sha256(), 0

    def write(self, data):
        self.digest.update(data)
        self.count += len(data)
        self.writer.write(self.compressor.compress(data))
        return len(data)

    def flush(self):
        pass

    def finish(self):
        self.writer.write(self.compressor.flush())
        self.writer.finish()


class HashingReader:
    def __init__(self, source):
        self.source = source
        self.digest, self.count = hashlib.sha256(), 0

    def read(self, count=-1):
        value = self.source.read(count)
        self.digest.update(value)
        self.count += len(value)
        return value


class PartReader(io.RawIOBase):
    def __init__(self, root, parts):
        self.root, self.parts = root, parts
        self.position, self.current = 0, None
        self.part_digest, self.part_count = None, 0
        self.digest, self.count = hashlib.sha256(), 0

    def readable(self):
        return True

    def readinto(self, buffer):
        while True:
            if self.current is None:
                if self.position == len(self.parts):
                    return 0
                part = self.parts[self.position]
                safe_path(part['path'])
                self.current = (self.root / part['path']).open('rb')
                self.part_digest, self.part_count = hashlib.sha256(), 0
            data = self.current.read(len(buffer))
            if data:
                self.part_digest.update(data)
                self.part_count += len(data)
                self.digest.update(data)
                self.count += len(data)
                buffer[:len(data)] = data
                return len(data)
            part = self.parts[self.position]
            self.current.close()
            self.current = None
            if self.part_count != part['bytes'] or self.part_digest.hexdigest() != part['sha256']:
                raise ValueError('Part verification failed: ' + part['path'])
            self.position += 1

    def close(self):
        if self.current is not None:
            self.current.close()
        super().close()


def verify_archive(raw_root, entry, extract=None, replace_existing=False):
    manifest = json.loads((raw_root / entry['expandedFileManifest']).read_text())
    expected = {f['path']: f for f in manifest['files']}
    if len(expected) != len(manifest['files']):
        raise ValueError('Duplicate manifest paths')
    parts = PartReader(raw_root, entry['parts'])
    compressed = io.BufferedReader(parts, buffer_size=1024 * 1024)
    seen, expanded = set(), 0
    if extract is not None:
        extract = Path(extract).resolve()
        extract.mkdir(parents=True, exist_ok=True)
    with lzma.LZMAFile(compressed, 'rb') as decoded:
        stream = HashingReader(decoded)
        with tarfile.open(fileobj=stream, mode='r|') as archive:
            for member in archive:
                safe_path(member.name)
                if not member.isfile() or member.name in seen or member.name not in expected:
                    raise ValueError('Unexpected member: ' + member.name)
                reference = expected[member.name]
                digest, count = hashlib.sha256(), 0
                output = None
                temporary = None
                if extract is not None:
                    target = extract / member.name
                    if not target.parent.resolve().is_relative_to(extract) or target.is_symlink():
                        raise ValueError('Restore target must be inside destination without links: ' + str(target))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if not target.parent.resolve().is_relative_to(extract) or target.is_symlink():
                        raise ValueError('Restore target changed while creating parent directories: ' + str(target))
                    same = target.is_file() and target.stat().st_size == reference['bytes'] and sha(target) == reference['sha256']
                    if target.exists() and not same and not replace_existing:
                        raise ValueError('Different existing file; use --replace-existing for an explicit archive overlay: ' + str(target))
                    if not same:
                        descriptor, temporary = tempfile.mkstemp(prefix='.archive-restore-', dir=target.parent)
                        output = os.fdopen(descriptor, 'wb')
                try:
                    source = archive.extractfile(member)
                    while True:
                        data = source.read(1024 * 1024)
                        if not data:
                            break
                        digest.update(data)
                        count += len(data)
                        if output:
                            output.write(data)
                finally:
                    if output:
                        output.close()
                if count != reference['bytes'] or digest.hexdigest() != reference['sha256'] or member.size != count:
                    raise ValueError('Expanded member mismatch: ' + member.name)
                if 'mode' in reference and member.mode != reference['mode']:
                    raise ValueError('Mode mismatch: ' + member.name)
                if extract is not None:
                    if temporary is not None:
                        os.replace(temporary, target)
                    os.chmod(target, member.mode & 0o777)
                seen.add(member.name)
                expanded += count
        # tarfile stops at zero end markers; consume padding too for full tar hash.
        while stream.read(1024 * 1024):
            pass
    # Force final part EOF validation even if liblzma buffered the end marker.
    if compressed.read(1):
        raise ValueError('Compressed bytes remain after decoded EOF')
    compressed.close()
    if seen != set(expected):
        raise ValueError('Missing members: ' + repr(sorted(set(expected) - seen)))
    if parts.count != entry['archive']['bytes'] or parts.digest.hexdigest() != entry['archive']['sha256']:
        raise ValueError('Whole compressed archive mismatch')
    if stream.digest.hexdigest() != entry['tarSha256']:
        raise ValueError('Whole uncompressed tar mismatch')
    return {'name': entry['name'], 'verifiedUtc': utc(), 'passed': True, 'members': len(seen),
            'expandedBytes': expanded, 'compressedBytes': parts.count, 'parts': len(entry['parts']),
            'archiveSha256': parts.digest.hexdigest(), 'tarSha256': stream.digest.hexdigest(),
            'verification': 'Every part, whole compressed stream, full decompressed tar including padding, and every member bytes/SHA256/mode verified without a full compressed reconstruction',
            'extracted': extract is not None, 'noNewPerformanceCredit': True}


def build(name):
    selection = json.loads((OUTPUT / 'selection.json').read_text())
    chosen = selection['groups'][name]
    started = utc()
    raw = OUTPUT / 'raw-archives'
    writer = PartWriter(raw / name, name)
    compressor = TarCompressor(writer)
    files = []
    try:
        with tarfile.open(fileobj=compressor, mode='w|', format=tarfile.PAX_FORMAT) as archive:
            for selected in chosen:
                relative = selected['path']
                path = ROOT / relative
                before = stamp(path)
                if before != selected['stamp']:
                    raise ValueError('Source changed since selection: ' + relative)
                info = tarfile.TarInfo(relative)
                info.size, info.mode = before[0], path.stat().st_mode & 0o777
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ''
                with path.open('rb') as source:
                    reader = HashingReader(source)
                    archive.addfile(info, reader)
                if stamp(path) != before or reader.count != before[0]:
                    raise ValueError('Source changed during archive: ' + relative)
                files.append({'path': relative, 'bytes': reader.count, 'sha256': reader.digest.hexdigest(), 'mode': info.mode})
        compressor.finish()
        entry = {'name': name, 'filename': name + '.tar.xz',
                 'archive': {'path': 'reconstructed/' + name + '.tar.xz', 'bytes': writer.count, 'sha256': writer.digest.hexdigest(), 'materialized': False},
                 'tarSha256': compressor.digest.hexdigest(), 'parts': writer.parts,
                 'expandedFileManifest': name + '/expanded-file-manifest.json',
                 'compressionIdentity': name + '/compression-identity.json'}
        dump(raw / entry['expandedFileManifest'], {'task': 'DB-Exec-Parity-01', 'name': name, 'originalWorkspaceRoot': str(ROOT),
             'fileCount': len(files), 'expandedBytes': sum(f['bytes'] for f in files), 'files': files,
             'excludedPaths': selection['excludedPaths'][name], 'dereferencedSymlinks': selection['dereferencedSymlinks'][name],
             'exclusionNotes': NOTES, 'noNewPerformanceCredit': True, 'noOriginalFileDeleted': True})
        dump(raw / entry['compressionIdentity'], {'startedUtc': started, 'finishedUtc': utc(), 'python': sys.version,
             'platform': platform.platform(), 'compression': 'CPython lzma.LZMACompressor / FORMAT_XZ / CHECK_CRC64 / preset=3; single thread',
             'lzmaModule': lzma.__file__, 'xzVersion': subprocess.check_output(['xz', '--version'], text=True).splitlines(),
             'tar': 'PAX, sorted regular paths, uid/gid/mtime=0, blank uname/gname, original mode',
             'partBytes': PART_BYTES, 'affinity': sorted(os.sched_getaffinity(0)), 'nice': os.getpriority(os.PRIO_PROCESS, 0),
             'writerSha256': sha(HERE / 'streaming_archive.py'), 'uncompressedTarBytes': compressor.count,
             'noCanonicalOrRoundtripCopy': True})
        dump(OUTPUT / (name + '-entry.json'), entry)
        result = verify_archive(raw, entry)
        dump(OUTPUT / (name + '-verification.json'), result)
        entries = [json.loads(p.read_text()) for p in sorted(OUTPUT.glob('*-entry.json'))]
        dump(raw / 'index.json', {'task': 'DB-Exec-Parity-01', 'format': 'ordered concatenated xz tar parts',
             'dependency': 'archives-01 at Plan b54054bd1f3befe94e1817cc29f494bd782854b9', 'archives': entries})
        dump(OUTPUT / (name + '-receipt.json'), {'startedUtc': started, 'finishedUtc': utc(), 'passed': True,
             'archive': entry, 'verification': result, 'remotePublication': False})
        print(json.dumps(result), flush=True)
    except BaseException as error:
        dump(OUTPUT / (name + '-failed-attempt.json'), {'startedUtc': started, 'failedUtc': utc(), 'passed': False,
             'error': repr(error), 'finishedParts': writer.parts, 'completedMembers': files, 'remotePublication': False})
        raise


def prepare():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if not (OUTPUT / 'source-snapshots.json').exists():
        capture_sources()
    value = select()
    dump(OUTPUT / 'selection.json', value)
    print(json.dumps({'groups': {n: {'files': len(v), 'expandedBytes': sum(x['stamp'][0] for x in v)} for n, v in value['groups'].items()},
                      'freeBytes': shutil.disk_usage(ROOT).free}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'build', 'verify', 'restore'])
    parser.add_argument('--name', choices=list(GROUPS))
    parser.add_argument('--index', type=Path, default=OUTPUT / 'raw-archives/index.json')
    parser.add_argument('--extract', type=Path)
    parser.add_argument('--replace-existing', action='store_true', help='Explicitly overlay differing archived files after each member passes its checksum')
    arguments = parser.parse_args()
    if arguments.action == 'prepare':
        prepare()
    elif arguments.action == 'build':
        if not arguments.name:
            parser.error('build requires --name')
        build(arguments.name)
    else:
        index = json.loads(arguments.index.read_text())
        for entry in index['archives']:
            if arguments.name is None or entry['name'] == arguments.name:
                print(json.dumps(verify_archive(arguments.index.parent, entry, arguments.extract, arguments.replace_existing)), flush=True)


if __name__ == '__main__':
    main()
