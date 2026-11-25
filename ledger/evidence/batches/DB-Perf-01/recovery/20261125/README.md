# DB-Perf-01 evidence recovery — 2026-11-25

This record identifies the exact evidence restored after the executor was replaced.
The starting Plan head was `4234eb6197cf52f7c776e0246be7d2c8823ebdbf`.
The recovery agent created 37 evidence files and these two metadata files in the
local task worktree. Every target was absent, every write used exclusive creation,
and no existing file was overwritten. Commit, publication, gates and review remain
with the parent agent. This record describes the local restoration before that work.

## Authorization and the historical rejection

The user's response was **“允许，现在继续 该合并的合并”**. It followed the
specific disclosure request for the eleven files listed below. The parent agent
confirmed authorization to publish those original runner, environment and failure
logs to `IzuSharp/Plan` and assigned this bounded local restoration.

The earlier automatic approval rejection remains part of the record. It rejected
raw upload batch 0003 because the files contained runner, environment and failure-log
metadata and required more specific disclosure authorization. See the
[historical handoff at the observed starting commit](https://github.com/IzuSharp/Plan/blob/4234eb6197cf52f7c776e0246be7d2c8823ebdbf/ledger/evidence/batches/DB-Perf-01/handoff-linux.md),
section `Existing raw-publication approval block`. This continuation records the
subsequent user permission; it does not erase the earlier rejection or extend the
permission to other rejected source, helper, runtime or opaque archives.

The original scope receipt's recorded SHA-256 is
`aecf0e5f56eb3dc4defbd422db88afa7b25447701c5304fdcfdc07f09c73210c`.
Its file and the original refusal-receipt bytes were not recovered. Historical
counts were 11 objects, 217,845 raw bytes and 224,366 API bytes. Those totals are
retained as historical context and have not been reverified against the lost scope
receipt. This manifest is a new partial-recovery record.

## Thirty-two existing Git objects

Two earlier successful uploads remain available as Git trees:

| Original tree | Recovered files |
| --- | ---: |
| `5ccfbbf2e3a0ed3c8479b180366f701dab486c0e` | 16 |
| `70107e62a7e7ab1b98626860949ab6074f50bd72` | 16 |

These are independent trees based on an older base. The second tree does not
contain the first tree's sixteen additions. Their 32 unique blobs, totaling
448,617 bytes, were restored to the original repository paths. Exact UTF-8 bytes
were checked against each remote blob's Git SHA-1 and size before writing, and
checked again after writing. No newline was inserted or normalized. Each path,
source tree, size, Git SHA-1 and SHA-256 is in
[recovery-manifest.json](recovery-manifest.json).

These existing objects are separate from the eleven-file batch. Their restored
source-reference manifests retain the old references; those references do not
establish that every original source or measurement file is now available.

## Eleven-file batch: three exact, two new reads, six missing

All eleven names refer to
`ledger/evidence/batches/DB-Perf-01/checkpoints/campaign-image-recovery-v1/raw/campaign-attempt3/`.
Only the five available files were created at their original paths.

| File | Recovery classification |
| --- | --- |
| `ci-registration-index.log` | Original bytes not recovered; no file created |
| `ci-registration-publication.json` | Original bytes not recovered; no file created |
| `ci-registration-tooling-v2.log` | Original bytes not recovered; no file created |
| `ci-registration-tooling.log` | Original bytes not recovered; no file created |
| `image-pin-publication.json` | Original bytes not recovered; no file created |
| `image-pin-validation.json` | Original bytes not recovered; its old SHA-256 is retained |
| `measureAttempt1Log.decoded-original.log` | Exact match to the previously recorded SHA-256 |
| `measureAttempt1Log.json` | Exact match to the previously recorded SHA-256 |
| `measureAttempt2Log.decoded-original.log` | Same original job read again; old local-byte identity unproved |
| `measureAttempt2Log.json` | Same original job read again; old local-byte identity unproved |
| `prepareLog.decoded-original.log` | Exact match to the previously recorded SHA-256 |

The five available files total 140,217 bytes. The two attempt-2 filenames preserve
the original requested path names; their names do not override the explicit
new-retrieval classification. Their current SHA-256 values identify the bytes
retrieved in this continuation, with no claim that they match the lost local files.

The exact matches are supported by the old independent review, restored unchanged
as part of the 32 blobs:

- Path: `checkpoints/campaign-image-recovery-v1/raw/campaign-attempt3-review/image-constraint-non-author-review.json`, relative to this batch.
- Git blob SHA-1: `c1bd30b925a80f9cc8b70dc02980da593d46472b`.
- SHA-256: `aa9a087599258d7080fda0223b37f47502f1c4c7b2bc277a940220d60049bd5a`.
- Source tree: `70107e62a7e7ab1b98626860949ab6074f50bd72`.

The source was the original completed
[Korda run 45449544703](https://github.com/IzuSharp/Korda/actions/runs/45449544703):
prepare job `138642517538`, first measure job `138645902342`, and second measure job
`138647852601` in run attempt 2. The first-measurement JSON envelope was accepted as
an exact recovery only after serialization of the actual tool response matched the
old independent SHA-256. No unmatched serialization was labeled an original.

An additional exact `prepareLog.json` was found locally, but it is outside the
approved eleven-name scope and was **not copied to Plan**. No substitute was
created for any of the six missing local files. The known old image-validation
SHA-256 remains in the manifest to support a possible later exact recovery.

## Verification

Run this from the Plan repository root. It reads the manifest and all restored
bytes, verifies Git SHA-1, SHA-256, sizes and unique paths, then checks that the six
missing files and the excluded extra prepare JSON have not been introduced by this
restoration. It performs no network call or database operation.

```bash
python3 - <<'PYVERIFY'
import hashlib
import json
from pathlib import Path

root = Path.cwd()
manifest = json.loads((root / 'ledger/evidence/batches/DB-Perf-01/recovery/20261125/recovery-manifest.json').read_text())
objects = manifest['previouslyUploadedObjects']['files']
scope = manifest['elevenFileScope']['files']
files = objects + [entry for entry in scope if entry['restored']]
paths = [entry.get('path', entry.get('targetPath')) for entry in files]
assert len(files) == len(set(paths)) == 37
for entry, path in zip(files, paths):
    data = (root / path).read_bytes()
    assert len(data) == entry['bytes'], path
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], path
    blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    assert hashlib.sha1(blob).hexdigest() == entry['gitBlobSha1'], path
for entry in scope:
    if not entry['restored']:
        assert not (root / entry['targetPath']).exists(), entry['targetPath']
extra = root / Path(scope[0]['targetPath']).parent / 'prepareLog.json'
assert not extra.exists(), str(extra)
assert sum(entry['bytes'] for entry in files) == 588834
print('Verified 32 exact existing blobs + 3 exact recovered files + 2 new reads; 6 originals remain missing.')
PYVERIFY
```

Acceptance remains incomplete. Restoring these records adds zero measurement
credit and does not establish a completed 8-segment campaign, a complete old Plan
history, public-package validation or final performance acceptance. No archived
command was executed, no database load was run, and the recovery agent performed
no remote mutation or Git staging, commit or push.
