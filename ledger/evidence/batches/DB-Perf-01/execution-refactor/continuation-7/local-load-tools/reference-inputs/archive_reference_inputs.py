#!/usr/bin/env python3
"""Preserve verified reference text bytes; hash-bound binary exclusions are explicit."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, required=True)
    parser.add_argument('--extra', action='append', type=Path, default=[])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.output.with_name(args.output.name.removesuffix('.tar.gz') + '.manifest.json')
    assert args.output.name.endswith('.tar.gz') and not args.output.exists() and not manifest_path.exists()
    index = json.loads(args.index.read_text())
    assert index['passed'] is True and index['inputsUnchanged'] is True
    sources = dict(index['inputFiles'])
    for path in [args.index, Path(__file__), *args.extra]:
        key = str(path.resolve(strict=True))
        digest = sha(key)
        assert key not in sources or sources[key] == digest
        sources[key] = digest
    payload, included, excluded = {}, [], []
    for number, (name, expected) in enumerate(sorted(sources.items())):
        path = Path(name)
        assert sha(path) == expected, name
        with path.open('rb') as stream:
            header = stream.read(4)
        item = {'origin': name, 'sha256': expected, 'bytes': path.stat().st_size}
        if header == b'\x7fELF' or path.suffix == '.nupkg':
            excluded.append({**item, 'reason': 'Original binary/package bytes not embedded; exact input hash retained'})
        else:
            member = 'inputs/' + str(number).zfill(4) + '/' + path.name
            payload[member] = path.read_bytes()
            assert hashlib.sha256(payload[member]).hexdigest() == expected
            included.append({**item, 'member': member})
    manifest = {'schemaVersion': 1, 'scope': __doc__, 'included': included, 'excluded': excluded,
                'timingCredit': False, 'currentFinalCredit': '0/4',
                'reproductionLimit': 'Original ELF/tool/package bytes are excluded. Recover those exact hashes to rerun the same binaries; a different rebuild is a new identity.'}
    payload['manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()

    def encode():
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode='w') as archive:
            for name, value in sorted(payload.items()):
                info = tarfile.TarInfo(name)
                info.mode, info.mtime, info.size = 0o644, 0, len(value)
                archive.addfile(info, io.BytesIO(value))
        return gzip.compress(out.getvalue(), mtime=0)

    content = encode()
    assert content == encode()
    with tarfile.open(fileobj=io.BytesIO(content), mode='r:gz') as archive:
        assert set(archive.getnames()) == set(payload)
        for name, value in payload.items():
            assert archive.extractfile(name).read() == value
    for name, expected in sources.items():
        assert sha(name) == expected, 'Input changed: ' + name
    with args.output.open('xb') as stream:
        stream.write(content)
    record = {'archive': {'path': args.output.name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)},
              'members': len(payload), 'deterministicDoubleEncodingEqual': True, 'allMembersReadbackEqual': True,
              'inputsUnchanged': True, 'manifest': manifest}
    with manifest_path.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps({**record['archive'], 'members': len(payload), 'excludedBinaryInputs': len(excluded)}))


if __name__ == '__main__':
    main()
