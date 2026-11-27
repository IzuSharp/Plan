#!/usr/bin/env python3
"""Bind the already-executed unified stream output to exact current archive identities."""
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def write(name, value):
    p = HERE / name
    assert not p.exists(), name
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


checks = []


def check(name, okay):
    checks.append({'name': name, 'passed': bool(okay)})
    if not okay:
        raise ValueError(name)


original = read('archive-completion-validation.json')
original_sha = sha(HERE / 'archive-completion-validation.json')
receipt = read('unified-stream-check-01.json')
identity = read('source-identity.json')
index = read('raw-archives/index.json')
check('original-completion-passed', original['passed'])
check('index-remains-initial-identity', sha(HERE / 'raw-archives/index.json') == original['indexSha256'])
check('expanded-remains-initial-identity', sha(HERE / 'expanded-all-files.json') == original['expandedManifestSha256'])
check('selection-remains-initial-identity', sha(HERE / 'selection.json') == original['selectionSha256'])
check('unified-receipt-remains-initial-identity', sha(HERE / 'unified-stream-check-01.json') == original['unifiedVerifierReceiptSha256'])
wrapper_sha = sha(HERE / 'restore_archive06.py')
check('actual-wrapper-matches-source-freeze-and-execution', wrapper_sha == receipt['wrapperSha256'] == identity['restore_archive06.py'])
check('reviewed-engine-remains-frozen', sha(HERE / 'streaming_archive.py') == identity['streaming_archive.py'])
check('alias-helper-remains-frozen', sha(HERE / 'restore_artifact_aliases.py') == identity['restore_artifact_aliases.py'])
check('command-was-unified-no-extract', len(receipt['argv']) == 2 and Path(receipt['argv'][1]) == HERE / 'restore_archive06.py' and not receipt['extractionExecuted'])
check('actual-process-exited-zero', receipt['exitCode'] == 0)
stdout = HERE / 'unified-stream-check-01.stdout.log'
stderr = HERE / 'unified-stream-check-01.stderr.log'
check('actual-stdout-bytes-bound', sha(stdout) == receipt['stdoutSha256'])
check('actual-stderr-bytes-bound', sha(stderr) == receipt['stderrSha256'])
check('actual-stderr-empty', stderr.stat().st_size == 0)
rows = [json.loads(line) for line in stdout.read_text().splitlines()]
check('exact-six-rows-plus-terminal', len(rows) == len(index['archives']) + 1)
terminal = rows[-1]
check('terminal-is-executed-receipt-terminal', terminal == receipt['terminalResult'])
check('terminal-counts-and-scope', terminal['passed'] and terminal['archives'] == original['archives']
      and terminal['members'] == original['members'] and not terminal['extracted'])
check('terminal-alias-bindings-are-recomputed-completion-bindings', terminal['packageAliasSourcesBound']
      and terminal['aliasSourceBindings'] == original['aliasSourceBindings'])
actual = {r['name']: r for r in rows[:-1]}
check('no-duplicate-unified-name', len(actual) == len(rows) - 1)
check('same-unified-index-name-set', set(actual) == {e['name'] for e in index['archives']})
bindings = []
for entry in index['archives']:
    name = entry['name']
    row = actual[name]
    previous = read(name + '-verification.json')
    group = read('raw-archives/' + entry['expandedFileManifest'])
    expected = {'archiveSha256': entry['archive']['sha256'], 'tarSha256': entry['tarSha256'],
                'compressedBytes': entry['archive']['bytes'], 'parts': len(entry['parts']),
                'members': len(group['files']), 'expandedBytes': sum(f['bytes'] for f in group['files'])}
    check('unified-passed-no-extract:' + name, row['passed'] and not row['extracted'])
    for key, value in expected.items():
        check('unified-index-previous:' + name + ':' + key, row[key] == value == previous[key])
    check('unified-prior-verification-description:' + name, row['verification'] == previous['verification'])
    bindings.append({'name': name, 'identities': expected,
                     'unifiedVerifiedUtc': row['verifiedUtc'],
                     'priorVerificationSha256': sha(HERE / (name + '-verification.json'))})

result = {'task': 'DB-Exec-Parity-01', 'passed': True, 'checkCount': len(checks), 'checks': checks,
          'finishedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'originalCompletionSha256': original_sha,
          'executedUnifiedReceiptSha256': sha(HERE / 'unified-stream-check-01.json'),
          'stdoutSha256': sha(stdout), 'stderrSha256': sha(stderr), 'wrapperSha256': wrapper_sha,
          'bindings': bindings, 'validatorSha256': sha(Path(__file__)),
          'streamVerifierRerun': False, 'compressionRerun': False,
          'largePayloadRehashed': False, 'sourceOrOldReceiptModified': False,
          'scope': 'Identity-only audit of already-executed raw output. Initial completion stays intact; same-count old output cannot substitute for these six exact current archive/tar identities.'}
write('unified-binding-validation-02.json', result)
final = dict(original)
final.update(finishedUtc=result['finishedUtc'], initialCompletionSha256=original_sha,
             initialCheckCount=original['checkCount'], additionalIdentityCheckCount=result['checkCount'],
             checkCount=original['checkCount'] + result['checkCount'],
             exactUnifiedIdentityValidation={'path': 'unified-binding-validation-02.json',
                 'sha256': sha(HERE / 'unified-binding-validation-02.json')},
             originalFinalizerSourceSha256=sha(HERE / 'finalize_archive06.py'),
             identityValidatorSourceSha256=result['validatorSha256'],
             closureRevision=2, priorReceiptPreserved=True)
write('archive-completion-validation-02.json', final)
resume = read('resume-before-publication.json')
resume.update(updatedUtc=result['finishedUtc'], validationSha256=sha(HERE / 'archive-completion-validation-02.json'),
              validationPath='archive-completion-validation-02.json', closureRevision=2,
              priorResumeSha256=sha(HERE / 'resume-before-publication.json'))
write('resume-closure-02.json', resume)
print(json.dumps({'passed': True, 'additionalChecks': result['checkCount'],
                  'totalMetadataChecks': final['checkCount'],
                  'validation02Sha256': sha(HERE / 'archive-completion-validation-02.json'),
                  'binding02Sha256': sha(HERE / 'unified-binding-validation-02.json')}), flush=True)
