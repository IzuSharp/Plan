#!/usr/bin/env python3
"""Bounded stdout bridge for exact manifest payloads; never writes a duplicate."""
import base64
import hashlib
import json
import pathlib
import stat
import sys

BASE = pathlib.Path(__file__).resolve().parent
manifest = json.loads((BASE / 'upload-parts-manifest-06.json').read_text())
item = manifest['parts'][int(sys.argv[1])]
path = pathlib.Path(item['sourcePath'])
before = path.lstat()
assert stat.S_ISREG(before.st_mode) and not path.is_symlink()
stamp = [str(x) for x in (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)]
if len(sys.argv) == 2:
    data = path.read_bytes()
    assert len(data) == item['bytes']
    assert hashlib.sha256(data).hexdigest() == item['sha256']
    assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == item['gitBlobSha']
    after = path.lstat()
    assert stamp == [str(x) for x in (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)]
    print(json.dumps({'item': item, 'stamp': stamp}))
else:
    offset, count = map(int, sys.argv[2:4])
    assert stamp == json.loads(sys.argv[4])
    assert offset >= 0 and 0 < count <= 196608 and offset % 196608 == 0
    with path.open('rb') as stream:
        stream.seek(offset)
        data = stream.read(count)
    after = path.lstat()
    assert stamp == [str(x) for x in (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)]
    assert len(data) == min(count, item['bytes'] - offset)
    print(base64.b64encode(data).decode())
