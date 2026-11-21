"""Verify the pinned retained Perf-01 archives without extracting payloads."""
from pathlib import Path, PurePosixPath
import datetime
import hashlib
import json
import os
import tarfile
import sys

if sys.flags.optimize != 0 or not __debug__:
    raise RuntimeError("Archive verification requires enabled assertions")

BASE = Path('/workspace/scratch/eb7ad1c3d03c')
OUT = BASE / 'perf01-historical-closeout-verified-001'
rows = json.loads((BASE / 'perf01-post-reset-input.private.json').read_text())
OUT.mkdir(exist_ok=False)
verified = []
identities = []
for row in rows:
    path = Path(row['transfer']['workspace_path'])
    assert path.parent == BASE / 'perf01-post-reset-readback-001'
    assert path.stat().st_size == row['bytes']
    with path.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256']
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        assert len(members) == row['member_count']
        names = [m.name for m in members]
        assert len(names) == len(set(names))
        assert all(m.isfile() and not PurePosixPath(m.name).is_absolute() and '..' not in PurePosixPath(m.name).parts for m in members)
        id_members = [m for m in members if m.name.endswith('.identity.json')]
        assert len(id_members) == 1
        id_member = id_members[0]
        id_bytes = archive.extractfile(id_member).read()
        assert hashlib.sha256(id_bytes).hexdigest() == row['identity_sha256']
        identity = json.loads(id_bytes)
        assert identity['task'] == 'Perf-01'
        assert identity['archive_filename'] == row['filename']
        expected = {m['member']: m for m in identity['members']}
        assert len(expected) == len(identity['members']) == len(members) - 1
        assert set(names) == set(expected) | {id_member.name}
        total = 0
        previously_recorded = 0
        for member in members:
            if member.name == id_member.name:
                continue
            record = expected[member.name]
            assert member.size == record['bytes'] and member.mode == record['mode']
            assert hashlib.file_digest(archive.extractfile(member), 'sha256').hexdigest() == record['sha256']
            if record['recorded_sha256'] is not None:
                assert record['recorded_sha256'] == record['sha256']
                previously_recorded += 1
            total += member.size
        assert total == row['payload_bytes'] == identity['payload_bytes']
    verified.append({k: row[k] for k in ('filename','file_id','library_file_id','version','sha256','bytes','identity_sha256','member_count','payload_bytes')} | {
        'original_members': len(expected), 'all_member_hashes_verified': True,
        'previously_recorded_member_hashes': previously_recorded,
        'archive_time_observed_member_hashes': len(expected) - previously_recorded,
        'link': 'https://chatgpt.com/library?file_id=' + row['library_file_id'] + '&account_id=personal',
    })
    identities.append(identity)
assert len(verified) == 21
assert sum(x['bytes'] for x in verified) == 128686740
assert sum(x['original_members'] for x in verified) == 379
assert sum(x['member_count'] for x in verified) == 400
assert sum(x['payload_bytes'] for x in verified) == 662573236
record = {
    'task':'Perf-01', 'status':'post-runtime-replacement-readback-verified',
    'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'host_boot_sha256': hashlib.sha256(Path('/proc/sys/kernel/random/boot_id').read_bytes()).hexdigest(),
    'archive_count':len(verified), 'compressed_bytes':128686740,
    'python_flags_optimize':sys.flags.optimize,
    'python_assertions_enabled_verified':__debug__,
    'python_orig_argv':sys.orig_argv,
    'python_version':sys.version,
    'original_member_count':379, 'readback_member_count':400,
    'payload_bytes':662573236, 'performance_credit_seconds':0,
    'archive_execution_sha256':'62ff9208f0ec2b8bcba11e834588fb7f184a78c9606232a5f4a1cff3c9d4e80e',
    'archive_verification_sha256':'7c85b37998af3eb3a2d682aa187b51855e16ebf4ee4b852c2576680fb086254a',
    'earlier_distinct_readback_utc':'2026-11-21T11:37:46.754745+00:00',
    'earlier_distinct_readback_basis':'Previously observed completed readback; current source bytes were independently retrieved and verified again.',
    'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'retention':'No automatic expiration was reported. Availability was verified at checked_utc, not guaranteed for a minimum future term. The owner may remove items. Public identities remain while Plan history is retained.',
    'access':'Owner-authorized file links; publication of these identifiers does not grant other GitHub readers access.',
    'scope':'Completed retry TLS, scalar and full SQLite C16 diagnostics, A06 principals, and selected actual principal binaries/packages. Later prefix TLS raw data and a complete runnable old-host environment are outside this archive scope.',
    'archives':verified,
}
(OUT/'completed-diagnostics-retention-001.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
(OUT/'completed-diagnostics-members-001.json').write_text(json.dumps({'task':'Perf-01','identities':identities},indent=2,sort_keys=True)+'\n')
print(json.dumps({k:record[k] for k in ('status','checked_utc','archive_count','original_member_count','readback_member_count','compressed_bytes')}))
print(json.dumps({'previously_recorded_hashes':sum(x['previously_recorded_member_hashes'] for x in verified),'archive_time_observed_hashes':sum(x['archive_time_observed_member_hashes'] for x in verified)}))
