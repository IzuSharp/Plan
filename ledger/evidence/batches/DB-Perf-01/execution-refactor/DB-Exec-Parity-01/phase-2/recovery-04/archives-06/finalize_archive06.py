#!/usr/bin/env python3
"""Bind verified groups, metadata paths and published dependencies; no source rehash."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import stat

from restore_archive06 import bind_alias_sources

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(name):
    return json.loads((HERE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    assert not path.exists(), str(path)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


checks = 0


def require(condition, name):
    global checks
    checks += 1
    if not condition:
        raise ValueError(name)


selection = read('selection.json')
index = read('raw-archives/index.json')
resume = read('resume.json')
require(resume['stage'] == 'all-groups-verified', 'group controller incomplete')
require(resume['completedGroups'] == selection['groupOrder'], 'serial group order differs')
require(set(selection['groups']) == {e['name'] for e in index['archives']}, 'six group set differs')
require(len(index['archives']) == len(selection['groups']), 'duplicate group')
members, parts, group_results = {}, [], []
for entry in index['archives']:
    name = entry['name']
    receipt = read(name + '-receipt.json')
    verification = read(name + '-verification.json')
    gate = read(name + '-disk-gate.json')
    require(receipt['passed'] and verification['passed'], 'failed group:' + name)
    require(receipt['archive'] == entry and receipt['verification'] == verification, 'unbound receipt:' + name)
    require(gate['passed'] and gate['actualFreeBytes'] >= gate['conservativeTarBudgetBytes'] + gate['metadataHeadroomBytes'], 'disk gate:' + name)
    group = read('raw-archives/' + entry['expandedFileManifest'])['files']
    require({f['path'] for f in group} == {f['path'] for f in selection['groups'][name]}, 'group paths:' + name)
    require(verification['members'] == len(group), 'member count:' + name)
    require(verification['expandedBytes'] == sum(x['bytes'] for x in group), 'expanded bytes:' + name)
    require(verification['compressedBytes'] == entry['archive']['bytes'], 'compressed bytes:' + name)
    for f in group:
        require(f['path'] not in members, 'cross-group duplicate:' + f['path'])
        members[f['path']] = f
    for p in entry['parts']:
        source = HERE / 'raw-archives' / p['path']
        st = source.lstat()
        require(stat.S_ISREG(st.st_mode) and not source.is_symlink() and st.st_size == p['bytes'], 'part stat:' + p['path'])
        parts.append(dict(p, path='raw-archives/' + p['path'], sourcePath=str(source), mode='100644'))
    group_results.append({'name': name, 'members': len(group), 'expandedBytes': verification['expandedBytes'],
                          'compressedBytes': verification['compressedBytes'], 'parts': len(entry['parts']),
                          'receiptSha256': sha(HERE / (name + '-receipt.json')),
                          'verificationSha256': sha(HERE / (name + '-verification.json')),
                          'diskGateSha256': sha(HERE / (name + '-disk-gate.json'))})
selected = {x['path']: x for files in selection['groups'].values() for x in files}
require(set(members) == set(selected), 'selected and expanded path sets differ')
require(len(selected) == selection['totalFiles'], 'selected count differs')
for path, original in selected.items():
    st = (ROOT / path).lstat()
    require(stat.S_ISREG(st.st_mode) and [st.st_size, st.st_mtime_ns, st.st_ino] == original['stamp'], 'source stat changed:' + path)
    require(stat.S_IMODE(st.st_mode) == members[path]['mode'], 'source mode changed:' + path)
    require(members[path]['bytes'] == original['stamp'][0], 'source size changed:' + path)
for name, expected in read('source-identity.json').items():
    require(sha(HERE / name) == expected, 'frozen controller identity changed:' + name)
require(not any('/postgres-data/' in p or '/public-package-verification-13/' in p for p in members), 'forbidden active/physical directory')
require(not any(p.endswith(('.sqlite', '.sqlite-wal', '.sqlite-shm', '.db', '.db-wal', '.db-shm')) for p in members), 'physical SQLite file')

aliases = read('restore-alias-manifest.json')['aliases']
bindings = bind_alias_sources(members, aliases)
require(len(aliases) == 10 and bindings['priorPublishedAliasSources'] == 6 and bindings['currentPayloadAliasSources'] == 4, 'alias coverage')
require(not any(a['destination'] in members for a in aliases), 'aliased destination is duplicated as payload')
package_closure = read('package-path-closure-06.json')
require(package_closure['actualPackageReferences'] == 16 and len(package_closure['newUniqueProviderArchives']) == 4 and len(package_closure['priorUniqueCompilerArchives']) == 3, 'package closure coverage')
for a in package_closure['newUniqueProviderArchives']:
    m = members[a['source']]
    require((m['bytes'], m['sha256'], m['mode']) == (a['bytes'], a['sha256'], a['mode']), 'packed package identity:' + a['source'])
generated = read('historical-generated-closure-01.json')
require(generated['totalUnknown'] == 0, 'unknown historical generated source')
for row in generated['records']:
    m = members[row['archivePath']]
    require((m['bytes'], m['sha256']) == (row['expectedBytes'], row['expectedSha256']), 'generated identity:' + row['archivePath'])
    if row['state'] == 'reconstructed-byte-identical':
        current = members[row['originalPath']]
        require(current['sha256'] == row['currentSha256'], 'historical overwrite:' + row['originalPath'])

unified = read('unified-stream-check-01.json')
require(unified['exitCode'] == 0 and unified['terminalResult']['passed'], 'unified stream validation failed')
require(unified['terminalResult']['archives'] == len(index['archives']) and unified['terminalResult']['members'] == len(members) and not unified['terminalResult']['extracted'], 'unified stream coverage')
expanded = {'task': 'DB-Exec-Parity-01', 'files': sorted(members.values(), key=lambda x: x['path']),
            'fileCount': len(members), 'expandedBytes': sum(x['bytes'] for x in members.values()),
            'selectionSha256': sha(HERE / 'selection.json'), 'indexSha256': sha(HERE / 'raw-archives/index.json'),
            'noNewPerformanceCredit': True}
require(expanded['expandedBytes'] == selection['expandedBytes'], 'expanded total differs')
write(HERE / 'expanded-all-files.json', expanded)
write(HERE / 'upload-parts-manifest-06.json', {'task': 'DB-Exec-Parity-01', 'parts': parts,
      'partCount': len(parts), 'bytes': sum(p['bytes'] for p in parts),
      'identityScope': 'Part bytes/SHA256/GitBlobSha from the unchanged writer; every part and complete stream verified per-group and again by the unified verifier. Finalizer rechecks part size/type, not large payload hashes.',
      'remotePublication': False})
result = {'task': 'DB-Exec-Parity-01', 'passed': True, 'checkCount': checks,
          'finishedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'groups': group_results, 'archives': len(index['archives']), 'parts': len(parts),
          'members': len(members), 'expandedBytes': expanded['expandedBytes'],
          'compressedBytes': sum(p['bytes'] for p in parts), 'aliasSourceBindings': bindings,
          'historicalGeneratedRecords': len(generated['records']),
          'originalMetadataRechecked': True, 'originalLargeBytesRehashedByFinalizer': False,
          'fullExtractionRun': False, 'noCanonicalOrRoundtripCopy': True,
          'selectionSha256': sha(HERE / 'selection.json'), 'indexSha256': sha(HERE / 'raw-archives/index.json'),
          'expandedManifestSha256': sha(HERE / 'expanded-all-files.json'),
          'unifiedVerifierReceiptSha256': sha(HERE / 'unified-stream-check-01.json'),
          'remotePublication': False, 'noNewPerformanceCredit': True,
          'freeBytesObserved': os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize}
write(HERE / 'archive-completion-validation.json', result)
write(HERE / 'resume-before-publication.json', {'task': 'DB-Exec-Parity-01',
      'stage': 'all-six-payload-groups-stream-verified-awaiting-root-publication',
      'updatedUtc': result['finishedUtc'], 'remotePublication': False,
      'candidate08Rejected': True, 'selectedMeasuredBaseline': '69b2383dadc280f1a81de592592a1442069eed0c',
      'selectedPublishedSource': '106fe68b6f6c2537f478daf65a71ab97cc4b15ff',
      'longMeasurementsCanceled': True, 'noFurther08ExperimentsPending': True,
      'wholeTaskCompleted': False, 'originalsAndPartsRetained': True,
      'validationSha256': sha(HERE / 'archive-completion-validation.json'),
      'next': 'Root publishes actual verified parts plus bounded metadata, then verifies remote bytes. Release/CI receipts live outside this closed candidate archive.'})
print(json.dumps(result), flush=True)
