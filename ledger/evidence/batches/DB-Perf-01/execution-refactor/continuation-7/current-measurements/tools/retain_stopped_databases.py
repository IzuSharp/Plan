#!/usr/bin/env python3
"""Archive one explicitly selected, stopped task fixture, verify it, then remove pgdata.

This is a local disk-retention operation, not a benchmark or CI entry point.
Only the four named directories below are admitted. Measurement logs/JSON are
read-only. Existing archives, manifests and receipts are never overwritten.
No subprocess, PostgreSQL command or network operation is started.

Usage:
  python3 retain_stopped_databases.py retain --measurement-dir /absolute/task/directory
  python3 retain_stopped_databases.py verify-restored --measurement-dir /absolute/task/directory

An error after deletion starts may leave a partially removed pgdata. The already
verified archive and durable manifest remain available; do not start that partial
cluster. Restore into an absent pgdata using the manifest's exact commands.
"""

import argparse
import contextlib
import datetime
import decimal
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import stat
import sys
import tarfile
import uuid


ROOT = Path('/workspace/scratch/fd78534029f7/measurements')
ALLOWED = frozenset({
    'close-paired-postgresql-r1', 'close-paired-postgresql-r2',
    'postgresql-offered-01', 'postgresql-baseline-01',
})
OUT_NAME = 'retained-databases'
CHUNK = 1024 * 1024
EMPTY_SHA256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
FILE_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def strict_json(data):
    return json.loads(data, object_pairs_hook=strict_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + value)))


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def selected_directory(raw):
    path = Path(raw)
    need(path.is_absolute() and '..' not in path.parts, 'An absolute non-traversing path is required')
    need(path.parent == ROOT and path.name in ALLOWED, 'Directory is outside the explicit task allowlist')
    return path


@contextlib.contextmanager
def real_directory(path):
    """Open each ancestor without following a symlink, including task roots."""
    need(path.is_absolute() and '..' not in path.parts, 'Invalid directory path')
    fd = os.open('/', DIR_FLAGS)
    try:
        for part in path.parts[1:]:
            next_fd = os.open(part, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        yield fd
    finally:
        os.close(fd)


@contextlib.contextmanager
def beneath(root_fd, parts):
    fd = os.dup(root_fd)
    try:
        for part in parts:
            need(part not in ('', '.', '..') and '/' not in part, 'Invalid relative component')
            next_fd = os.open(part, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        yield fd
    finally:
        os.close(fd)


def absent(fd, name):
    try:
        os.stat(name, dir_fd=fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise ValueError('Path already exists: ' + name)


def stopped(pg_fd):
    absent(pg_fd, 'postmaster.pid')


def signature(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
            value.st_nlink, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def record(path, value, kind):
    return {'path': path, 'type': kind, 'size': value.st_size if kind == 'file' else 0,
            'mode': stat.S_IMODE(value.st_mode), 'uid': value.st_uid, 'gid': value.st_gid,
            'mtimeNs': value.st_mtime_ns,
            'sourceIdentity': list(signature(value)),
            'sha256': EMPTY_SHA256 if kind == 'directory' else None}


def no_extended_metadata(fd):
    # Reject instead of silently losing ACLs, security labels or user xattrs.
    need(not os.listxattr(fd), 'Extended attributes require a separately reviewed archive method')


class DigestReader:
    def __init__(self, stream):
        self.stream, self.digest, self.size = stream, hashlib.sha256(), 0

    def read(self, count=-1):
        value = self.stream.read(count)
        self.digest.update(value)
        self.size += len(value)
        return value


class DigestWriter:
    def __init__(self, stream):
        self.stream, self.digest, self.size = stream, hashlib.sha256(), 0

    def write(self, value):
        count = self.stream.write(value)
        need(count == len(value), 'Short archive write')
        self.digest.update(value)
        self.size += count
        return count

    def flush(self):
        self.stream.flush()


def file_digest(stream):
    reader = DigestReader(stream)
    while reader.read(CHUNK):
        pass
    return reader.digest.hexdigest(), reader.size


def inventory(pg_fd, with_hash):
    entries = []

    def walk(fd, relative):
        before = os.fstat(fd)
        need(stat.S_ISDIR(before.st_mode), 'Non-directory in tree')
        no_extended_metadata(fd)
        entries.append(record(relative, before, 'directory'))
        with os.scandir(fd) as iterator:
            names = sorted(item.name for item in iterator)
        for name in names:
            name.encode('utf-8', errors='strict')
            need(name not in ('.', '..', 'postmaster.pid') and '/' not in name, 'Forbidden database member: ' + name)
            value = os.stat(name, dir_fd=fd, follow_symlinks=False)
            child_path = relative + '/' + name
            if stat.S_ISDIR(value.st_mode):
                child = os.open(name, DIR_FLAGS, dir_fd=fd)
                try:
                    need(signature(os.fstat(child)) == signature(value), 'Directory changed before open')
                    walk(child, child_path)
                finally:
                    os.close(child)
            else:
                need(stat.S_ISREG(value.st_mode) and value.st_nlink == 1,
                     'Only non-linked regular files/directories are allowed: ' + child_path)
                child = os.open(name, FILE_FLAGS, dir_fd=fd)
                with os.fdopen(child, 'rb') as stream:
                    need(signature(os.fstat(stream.fileno())) == signature(value), 'File changed before open')
                    no_extended_metadata(stream.fileno())
                    item = record(child_path, value, 'file')
                    if with_hash:
                        item['sha256'], length = file_digest(stream)
                        need(length == item['size'], 'File length changed while hashing')
                    need(signature(os.fstat(stream.fileno())) == signature(value), 'File changed while reading')
                    entries.append(item)
        need(signature(os.fstat(fd)) == signature(before), 'Directory changed during inventory')

    stopped(pg_fd)
    walk(pg_fd, 'pgdata')
    return sorted(entries, key=lambda item: item['path'])


def owner_receipt(measurement_fd, directory):
    fd = os.open('postgres-owner.json', FILE_FLAGS, dir_fd=measurement_fd)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= 2 * CHUNK,
             'Invalid PostgreSQL owner receipt file')
        data = stream.read(2 * CHUNK + 1)
        need(len(data) == before.st_size and signature(os.fstat(stream.fileno())) == signature(before),
             'Owner receipt changed while reading')
    value = strict_json(data)
    need(type(value.get('exitCode')) is int and value['exitCode'] == 0, 'PostgreSQL owner did not exit successfully')
    finished = value.get('finishedUtc')
    need(type(finished) is str and bool(finished), 'PostgreSQL owner has no finishedUtc')
    when = datetime.datetime.fromisoformat(finished.replace('Z', '+00:00'))
    need(when.tzinfo is not None and when.utcoffset() == datetime.timedelta(0), 'finishedUtc is not an aware UTC timestamp')
    need(when <= datetime.datetime.now(datetime.timezone.utc), 'PostgreSQL owner finish is in the future')
    if 'timedOut' in value:
        need(value['timedOut'] is False, 'PostgreSQL owner timed out')
    argv = value.get('argv')
    need(type(argv) is list and all(type(item) is str for item in argv), 'Owner argv is missing')
    need(argv.count('-D') == 1 and argv.index('-D') + 1 < len(argv), 'Owner argv has no unique data directory')
    need(argv[argv.index('-D') + 1] == str(directory / 'pgdata'), 'Owner receipt belongs to another PostgreSQL data directory')
    need(any(Path(item).name == 'postgres' for item in argv), 'Owner argv does not identify postgres')
    return {'path': str(directory / 'postgres-owner.json'), 'sha256': hashlib.sha256(data).hexdigest(),
            'bytes': len(data), 'sourceIdentity': list(signature(before)),
            'finishedUtc': finished, 'exitCode': 0, 'argv': argv}


def mtime_text(nanoseconds):
    return format(decimal.Decimal(nanoseconds) / decimal.Decimal(1_000_000_000), '.9f')


def archive_object(value):
    # Publication changes link count/ctime. Content-bearing identity and all
    # other relevant metadata must still match the object that was read back.
    return (value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid,
            value.st_size, value.st_mtime_ns)


def make_archive(pg_fd, out_fd, temporary, entries):
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=out_fd)
    with os.fdopen(fd, 'wb') as stream:
        writer = DigestWriter(stream)
        with gzip.GzipFile(filename='', mode='wb', compresslevel=6, mtime=0, fileobj=writer) as compressed:
            with tarfile.open(mode='w|', fileobj=compressed, format=tarfile.PAX_FORMAT) as archive:
                for item in entries:
                    member = tarfile.TarInfo(item['path'])
                    member.mode, member.uid, member.gid = item['mode'], item['uid'], item['gid']
                    member.uname = member.gname = ''
                    member.mtime = item['mtimeNs'] // 1_000_000_000
                    member.pax_headers = {'mtime': mtime_text(item['mtimeNs'])}
                    member.size = item['size']
                    member.type = tarfile.DIRTYPE if item['type'] == 'directory' else tarfile.REGTYPE
                    if item['type'] == 'directory':
                        archive.addfile(member)
                        continue
                    parts = PurePosixPath(item['path']).parts[1:]
                    with beneath(pg_fd, parts[:-1]) as parent:
                        child = os.open(parts[-1], FILE_FLAGS, dir_fd=parent)
                        with os.fdopen(child, 'rb') as original:
                            need(list(signature(os.fstat(original.fileno()))) == item['sourceIdentity'], 'Source changed before archive read')
                            no_extended_metadata(original.fileno())
                            reader = DigestReader(original)
                            archive.addfile(member, reader)
                            need(reader.size == item['size'], 'Archive source length differs')
                            need(list(signature(os.fstat(original.fileno()))) == item['sourceIdentity'], 'Source changed during archive read')
                            item['sha256'] = reader.digest.hexdigest()
        writer.flush()
        os.fsync(stream.fileno())
        return {'sha256': writer.digest.hexdigest(), 'bytes': writer.size}


def verify_archive(out_fd, name, entries, expected_archive):
    fd = os.open(name, FILE_FLAGS, dir_fd=out_fd)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'Archive is not a private regular file')
        reader = DigestReader(stream)
        seen = []
        with gzip.GzipFile(mode='rb', fileobj=reader) as compressed:
            with tarfile.open(mode='r|', fileobj=compressed) as archive:
                for member in archive:
                    need(len(seen) < len(entries), 'Archive contains an extra member')
                    item = entries[len(seen)]
                    name_in_tar = member.name.rstrip('/')
                    need(name_in_tar == item['path'], 'Archive member order/path differs')
                    need(member.type == (tarfile.DIRTYPE if item['type'] == 'directory' else tarfile.REGTYPE),
                         'Archive contains a link/special or wrong member type')
                    need(member.size == item['size'] and member.mode == item['mode']
                         and member.uid == item['uid'] and member.gid == item['gid'], 'Archive length/mode/ownership differs')
                    need(member.pax_headers.get('mtime') == mtime_text(item['mtimeNs']), 'Archive timestamp differs')
                    need(not member.linkname and member.uname == member.gname == '', 'Unexpected archive link/owner name')
                    if item['type'] == 'directory':
                        digest, size = EMPTY_SHA256, 0
                    else:
                        content = archive.extractfile(member)
                        need(content is not None, 'Archive file payload missing')
                        with content:
                            digest, size = file_digest(content)
                    need(digest == item['sha256'] and size == item['size'], 'Archive member digest/length differs')
                    seen.append(name_in_tar)
            # Force gzip's complete stream, trailer/CRC and any concatenated data
            # to be read; stopping at tar's end markers alone is insufficient.
            while compressed.read(CHUNK):
                pass
        need(len(seen) == len(entries), 'Archive is missing members')
        need(reader.digest.hexdigest() == expected_archive['sha256'] and reader.size == expected_archive['bytes'],
             'Compressed archive digest/length differs')
        need(signature(os.fstat(stream.fileno())) == signature(before), 'Archive changed during readback')
        return archive_object(before)


def publish_file(out_fd, temporary, final):
    # link+unlink supplies atomic no-replace publication without rename overwrite.
    os.link(temporary, final, src_dir_fd=out_fd, dst_dir_fd=out_fd, follow_symlinks=False)
    os.unlink(temporary, dir_fd=out_fd)
    os.fsync(out_fd)


def write_json_new(out_fd, name, value):
    data = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
    temporary = '.' + name + '.' + uuid.uuid4().hex + '.partial'
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=out_fd)
    with os.fdopen(fd, 'wb') as stream:
        need(stream.write(data) == len(data), 'Short JSON write')
        stream.flush()
        os.fsync(stream.fileno())
    publish_file(out_fd, temporary, name)
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def remove_recorded_tree(measurement_fd, pg_fd, entries):
    """Delete only checked original members, never a newly added unarchived file."""
    for item in reversed(entries):
        stopped(pg_fd)
        parts = PurePosixPath(item['path']).parts[1:]
        if not parts:
            value = os.stat('pgdata', dir_fd=measurement_fd, follow_symlinks=False)
            need((value.st_dev, value.st_ino) == tuple(item['sourceIdentity'][:2]), 'Root directory was replaced')
            os.rmdir('pgdata', dir_fd=measurement_fd)
            continue
        with beneath(pg_fd, parts[:-1]) as parent:
            value = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            if item['type'] == 'file':
                need(list(signature(value)) == item['sourceIdentity'], 'File changed before deletion: ' + item['path'])
                os.unlink(parts[-1], dir_fd=parent)
            else:
                # Own child removals change directory size/mtime/ctime/link count.
                need(stat.S_ISDIR(value.st_mode) and (value.st_dev, value.st_ino) == tuple(item['sourceIdentity'][:2])
                     and stat.S_IMODE(value.st_mode) == item['mode'] and value.st_uid == item['uid']
                     and value.st_gid == item['gid'], 'Directory changed before deletion')
                os.rmdir(parts[-1], dir_fd=parent)  # New/unrecorded members make this fail closed.
    os.fsync(measurement_fd)


def archive_names(directory):
    stem = directory.name + '.pgdata'
    return stem + '.tar.gz', stem + '.manifest.json', stem + '.retention.json'


def retained_manifest(directory, owner, entries, archive_name, archive_identity):
    archive = ROOT / OUT_NAME / archive_name
    restore = ['tar', '--extract', '--gzip', '--numeric-owner', '--same-owner', '--same-permissions',
               '--file', str(archive), '--directory', str(directory)]
    verify = ['python3', str(Path(__file__).absolute()), 'verify-restored', '--measurement-dir', str(directory)]
    return {'schemaVersion': 1, 'kind': 'stopped-task-postgresql-fixture',
            'createdUtc': utc_now(), 'measurementDirectory': str(directory), 'originalPgdata': str(directory / 'pgdata'),
            'postgresOwnerReceipt': owner, 'archive': {'path': str(archive), **archive_identity},
            'archiveFormat': 'PAX tar, lexical member order, gzip level 6, empty gzip filename and mtime=0',
            'metadataPreserved': ['type', 'content', 'size', 'mode', 'uid', 'gid', 'mtimeNs'],
            'metadataScope': 'No symlinks, hardlinks, special files or xattrs accepted. Inode/ctime identity is retained for source-change checks, not restorable filesystem identity.',
            'members': entries, 'membersCount': len(entries),
            'regularFileBytes': sum(item['size'] for item in entries if item['type'] == 'file'),
            'restore': {'preconditions': 'Keep PostgreSQL stopped. Require pgdata absent. Use an account able to restore the recorded numeric ownership. Do not extract over a partial cluster.',
                        'extractArgv': restore, 'extractCommand': shlex.join(restore),
                        'verifyArgv': verify, 'verifyCommand': shlex.join(verify)},
            'measurementLogsAndJsonModified': False, 'performanceCredit': False}


def retain(directory):
    archive_name, manifest_name, receipt_name = archive_names(directory)
    temporary = '.' + archive_name + '.' + uuid.uuid4().hex + '.partial'
    stage, deletion_started = 'admission', False
    with real_directory(ROOT) as root_fd, beneath(root_fd, [directory.name]) as measurement_fd:
        with beneath(measurement_fd, ['pgdata']) as pg_fd:
            owner = owner_receipt(measurement_fd, directory)
            stopped(pg_fd)
            try:
                os.mkdir(OUT_NAME, 0o700, dir_fd=root_fd)
            except FileExistsError:
                pass
            with beneath(root_fd, [OUT_NAME]) as out_fd:
                for name in (archive_name, manifest_name, receipt_name):
                    absent(out_fd, name)
                try:
                    stage = 'inventory'
                    entries = inventory(pg_fd, False)
                    stage = 'archive'
                    archive_identity = make_archive(pg_fd, out_fd, temporary, entries)
                    stage = 'archive-readback'
                    verified_object = verify_archive(out_fd, temporary, entries, archive_identity)
                    stage = 'source-recheck'
                    need(inventory(pg_fd, True) == entries, 'Original database changed after archival')
                    need(owner_receipt(measurement_fd, directory) == owner, 'Owner receipt changed after archival')
                    need(list(signature(os.stat('pgdata', dir_fd=measurement_fd, follow_symlinks=False))) ==
                         entries[0]['sourceIdentity'], 'Original pgdata path changed after archival')
                    live_measurement = os.stat(directory.name, dir_fd=root_fd, follow_symlinks=False)
                    held_measurement = os.fstat(measurement_fd)
                    need(stat.S_ISDIR(live_measurement.st_mode) and
                         (live_measurement.st_dev, live_measurement.st_ino) ==
                         (held_measurement.st_dev, held_measurement.st_ino), 'Measurement directory was replaced')
                    stopped(pg_fd)
                    stage = 'publish'
                    publish_file(out_fd, temporary, archive_name)
                    manifest = retained_manifest(directory, owner, entries, archive_name, archive_identity)
                    manifest_identity = write_json_new(out_fd, manifest_name, manifest)
                    # Verify archive publication itself still names the object whose
                    # content was read back; no path replacement may authorize removal.
                    final_archive = os.stat(archive_name, dir_fd=out_fd, follow_symlinks=False)
                    need(final_archive.st_nlink == 1 and archive_object(final_archive) == verified_object,
                         'Published archive differs from the object that passed readback')
                    need(owner_receipt(measurement_fd, directory) == owner, 'Owner changed before source removal')
                    stopped(pg_fd)
                    stage, deletion_started = 'remove-verified-original', True
                    remove_recorded_tree(measurement_fd, pg_fd, entries)
                    absent(measurement_fd, 'pgdata')
                    receipt = {'schemaVersion': 1, 'status': 'retained-and-original-removed', 'finishedUtc': utc_now(),
                               'measurementDirectory': str(directory), 'originalPgdata': str(directory / 'pgdata'),
                               'archive': manifest['archive'], 'manifest': {'path': str(ROOT / OUT_NAME / manifest_name), **manifest_identity},
                               'postgresOwnerReceipt': owner, 'membersVerified': len(entries),
                               'originalContentAndIdentityRechecked': True, 'pgdataRemoved': True,
                               'measurementLogsAndJsonModified': False, 'performanceCredit': False}
                    write_json_new(out_fd, receipt_name, receipt)
                    print(json.dumps(receipt, ensure_ascii=False))
                except BaseException as failure:
                    # Preserve partial archive and a fresh failure record. No old
                    # archive/manifest/measurement record is edited to imply success.
                    record_name = directory.name + '.retention-failure.' + uuid.uuid4().hex + '.json'
                    try:
                        write_json_new(out_fd, record_name,
                                       {'schemaVersion': 1, 'status': 'failed', 'stage': stage,
                                        'measurementDirectory': str(directory), 'deletionStarted': deletion_started,
                                        'errorType': type(failure).__name__, 'error': str(failure),
                                        'partialArchive': str(ROOT / OUT_NAME / temporary),
                                        'archive': str(ROOT / OUT_NAME / archive_name), 'manifest': str(ROOT / OUT_NAME / manifest_name),
                                        'postgresOwnerReceipt': owner, 'finishedUtc': utc_now()})
                    except Exception as recording_failure:
                        print('Failure receipt could not be saved: ' + str(recording_failure), file=sys.stderr)
                    raise


def verify_restored(directory):
    archive_name, manifest_name, unused_receipt = archive_names(directory)
    with real_directory(ROOT) as root_fd, beneath(root_fd, [OUT_NAME]) as out_fd:
        fd = os.open(manifest_name, FILE_FLAGS, dir_fd=out_fd)
        with os.fdopen(fd, 'rb') as stream:
            need(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'Manifest is not a regular file')
            manifest = strict_json(stream.read())
        need(manifest['schemaVersion'] == 1 and manifest['measurementDirectory'] == str(directory)
             and manifest['originalPgdata'] == str(directory / 'pgdata')
             and manifest['archive']['path'] == str(ROOT / OUT_NAME / archive_name), 'Restore manifest belongs to another task path')
        verify_archive(out_fd, archive_name, manifest['members'], manifest['archive'])
        with beneath(root_fd, [directory.name]) as measurement_fd, beneath(measurement_fd, ['pgdata']) as pg_fd:
            current = inventory(pg_fd, True)
            expected = manifest['members']
            need(len(current) == len(expected), 'Restored member inventory differs')
            for left, right in zip(current, expected):
                need({k: v for k, v in left.items() if k != 'sourceIdentity'} ==
                     {k: v for k, v in right.items() if k != 'sourceIdentity'}, 'Restored member differs: ' + left['path'])
        print(json.dumps({'status': 'restored-content-and-metadata-verified', 'measurementDirectory': str(directory),
                          'membersVerified': len(expected), 'performanceCredit': False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('retain', 'verify-restored'))
    parser.add_argument('--measurement-dir', required=True)
    args = parser.parse_args()
    directory = selected_directory(args.measurement_dir)
    if args.action == 'retain':
        retain(directory)
    else:
        verify_restored(directory)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'status': 'failed', 'errorType': type(error).__name__, 'error': str(error)}), file=sys.stderr)
        raise SystemExit(1)
