#!/usr/bin/env python3
"""Close metadata and receipt-bound coverage without rehashing large originals."""
import datetime
import hashlib
import json
import os
import stat
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def read(name):
    return json.loads((HERE / name).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_bytes(data)
    os.replace(temporary, path)
    assert path.read_bytes() == data

checks = []
def check(name, okay):
    checks.append({'name': name, 'passed': bool(okay)})
    if not okay:
        raise AssertionError(name)

selection = read('selection.json')
index = read('raw-archives/index.json')
expanded = read('expanded-all-files.json')
members = {f['path']: f for f in expanded['files']}
selected = {f['path']: f for group in selection['groups'].values() for f in group}
check('unique-expanded-members', len(members) == len(expanded['files']))
check('unique-selected-members', len(selected) == sum(map(len, selection['groups'].values())))
check('selected-expanded-identical-set', set(members) == set(selected))
check('selection-hash-bound', expanded['selectionSha256'] == sha(HERE / 'selection.json'))
check('all-five-groups-in-index', set(selection['groups']) == {e['name'] for e in index['archives']})
for path, original in selected.items():
    check('member-size:' + path, members[path]['bytes'] == original['stamp'][0])
    current = (ROOT / path).lstat()
    check('original-stamp:' + path, stat.S_ISREG(current.st_mode) and
          [current.st_size, current.st_mtime_ns, current.st_ino] == original['stamp'])
    check('original-mode:' + path, stat.S_IMODE(current.st_mode) == members[path]['mode'])
for entry in index['archives']:
    receipt = read(entry['name'] + '-receipt.json')
    check('passed-stream:' + entry['name'], receipt['passed'] and receipt['verification']['passed'])
    check('same-entry:' + entry['name'], receipt['archive'] == entry)
    group = read('raw-archives/' + entry['expandedFileManifest'])['files']
    check('exact-group:' + entry['name'], {f['path']: f for f in group} ==
          {p: members[p] for p in selected if p in {x['path'] for x in selection['groups'][entry['name']]}})
check('exact-size-totals', len(members) == 748 and sum(f['bytes'] for f in members.values()) == 88231426 and
      sum(e['archive']['bytes'] for e in index['archives']) == 33549868 and
      sum(len(e['parts']) for e in index['archives']) == 12)
for forbidden in ('/postgres-data/', '/runtime-spin-dedup-08/', '/relation-final-frame-readonly-08/'):
    check('excluded:' + forbidden, not any(forbidden in '/' + p for p in members))
check('no-physical-sqlite', not any(p.endswith(('.sqlite', '.sqlite-wal', '.sqlite-shm', '.db', '.db-wal', '.db-shm')) for p in members))
unified = read('unified-stream-check-01.json')
check('one-command-five-archives', unified['exitCode'] == 0 and unified['terminalResult']['passed'] and
      unified['terminalResult']['archives'] == 5 and unified['terminalResult']['members'] == 748 and
      not unified['terminalResult']['extracted'])
closure = read('package-path-closure-05.json')
check('package-path-closure', closure['passed'] and closure['checkCount'] == 185)
review = read('alias-independent-review-01/receipt.json')
check('independent-alias-review', review['sealed'] and review['passed'] and review['checkCount'] == 64)
for name, identity in review['files'].items():
    check('review-file:' + name, sha(HERE / 'alias-independent-review-01' / name) == identity['sha256'])
for name, key in [('streaming_archive.py', 'reviewedStreamingVerifierSha256'),
                  ('restore_archive05.py', 'restoreWrapperSha256'),
                  ('restore_artifact_aliases.py', 'aliasHelperSha256'),
                  ('select_closed07.py', 'selectorSha256'), ('build_closed07.py', 'builderSha256')]:
    check('frozen-source:' + name, sha(HERE / name) == read('source-identity.json')[key])
result = {'task': 'DB-Exec-Parity-01', 'passed': True, 'checks': checks, 'checkCount': len(checks),
          'finishedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'archives': 5, 'parts': 12, 'members': len(members),
          'expandedBytes': 88231426, 'compressedBytes': 33549868,
          'originalMetadataRechecked': True, 'originalLargeBytesRehashedByThisScript': False,
          'payloadByteValidation': 'Prior per-group full stream verification and unified check, bound by metadata.',
          'selectionSha256': sha(HERE / 'selection.json'),
          'indexSha256': sha(HERE / 'raw-archives/index.json'),
          'expandedManifestSha256': sha(HERE / 'expanded-all-files.json'),
          'packagePathClosureSha256': sha(HERE / 'package-path-closure-05.json'),
          'noCanonicalOrRoundtripCopy': True, 'noNewPerformanceCredit': True,
          'remotePublication': False,
          'freeBytesObserved': os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize}
dump(HERE / 'archive-completion-validation.json', result)
old = HERE / 'resume-selection-frozen.json'
if not old.exists():
    old.write_bytes((HERE / 'resume.json').read_bytes())
dump(HERE / 'resume.json', {'task': 'DB-Exec-Parity-01', 'stage': 'all-payload-verified-and-blobs-uploaded-metadata-finalizing',
     'updatedUtc': result['finishedUtc'], 'remotePublication': False, 'originalsRetained': True,
     'partsRetained': True, 'candidateRejected': True, 'selectedCommit': selection['selectedProductCommit'],
     'longMeasurementsCancelled': True, 'next': 'Upload final metadata and give exact tree mapping to root; root alone publishes and reads remote bytes.'})
print(json.dumps({k: v for k, v in result.items() if k != 'checks'}))
