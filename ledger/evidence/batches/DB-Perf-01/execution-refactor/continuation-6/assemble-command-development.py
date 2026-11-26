from __future__ import annotations

import gzip
import hashlib
import io
import json
import pathlib
import subprocess
import tarfile
import tempfile

WORKSPACE = pathlib.Path('/workspace/scratch/4a65d70f0fe1')
ROOT = WORKSPACE / 'worktrees/DB-Exec-07-command-tests'
OUTPUT = WORKSPACE / 'artifacts'
PREFIX = 'command-completion-development-01'
FINAL_SOURCE = '21fd325cc528eab720f06e681c1f5cd9aee64da2'
ROOT_SOURCE = 'd8beff6dc31f6190caaed333a28847511b7adbc5'
PRODUCER_SOURCE = '374a253f09f47d0b42f9d18491677158287ba18b'
data: dict[str, bytes] = {}
origins: dict[str, str] = {}


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def add(path: pathlib.Path, name: str) -> None:
    assert name not in data, name
    data[name] = path.read_bytes()
    origins[name] = str(path)


def document(name: str, value: object) -> None:
    assert name not in data, name
    data[name] = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    origins[name] = 'assembled observation; original run records remain separate'


def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=ROOT)


# Deliberate whitelist: no ELF, obj/bin, database cluster, or certificate files.
for stem, count in [('command-completion', 12), ('command-managed', 5)]:
    for number in range(1, count + 1):
        folder = ROOT / 'artifacts' / f'{stem}-{number:02d}'
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix in {'.log', '.json', '.py', '.txt', '.md'}:
                add(path, f'attempts/{folder.name}/{path.name}')
            elif path.is_dir() and path.name.endswith('-providers'):
                for leaf in ('consumer.log', 'postgres-init.log', 'postgres.log'):
                    if (path / leaf).is_file():
                        add(path / leaf, f'attempts/{folder.name}/{path.name}/{leaf}')

for path in sorted((ROOT / 'artifacts/command-final-audit').iterdir()):
    if path.is_file():
        add(path, 'final-audit/' + path.name)
for leaf in ('command-impact.json', 'command-impact.log'):
    if (ROOT / 'artifacts' / leaf).is_file():
        add(ROOT / 'artifacts' / leaf, 'earlier-impact/' + leaf)

for number in (1, 2):
    for provider in ('sqlite', 'postgresql'):
        folder = OUTPUT / f'command-dev-native-{provider}-{number:02d}'
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix in {'.json', '.log'}:
                add(path, f'producers/{folder.name}/{path.name}')
    path = OUTPUT / f'command-dev-native-{number:02d}-result.json'
    if path.exists():
        add(path, 'producers/' + path.name)

# Preserve final test and build inputs directly, in addition to their git IDs.
source_paths = git('ls-files', 'tests/Data.NativeHost', 'tests/ProviderProfileChecks.cs',
                   'native/cpp/tests/command_completion_tests.cpp', 'native/cpp/tests/query_tests.cpp',
                   'native/cpp/tests/CMakeLists.txt', 'CMakeLists.txt', 'CMakePresets.json',
                   'global.json', 'Directory.Build.props', 'Directory.Build.targets',
                   'Directory.Packages.props', 'NuGet.Config').decode().splitlines()
for relative in source_paths:
    value = git('show', FINAL_SOURCE + ':' + relative)
    name = 'final-source/' + relative
    data[name] = value
    origins[name] = f'git:{FINAL_SOURCE}:{relative}'

commits = ['c4904dd', 'a4ddcf6', '3b31a1d', '16eaebc', 'ca5cea2', '283995f',
           'bd11445', '97861ee', '8eaac4e', 'c86be2c', '8f0cae5', '21fd325']
for commit in commits:
    sha = git('rev-parse', commit).decode().strip()
    name = 'test-and-fix-patches/' + sha + '.patch'
    data[name] = git('format-patch', '-1', '--stdout', sha)
    origins[name] = 'git:' + sha

# Read every recorded source blob from its recorded commit. This validates the
# original hash manifests without relabeling old attempts as the final source.
cache: dict[str, bytes] = {}
cat = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                       stdin=subprocess.PIPE, stdout=subprocess.PIPE)
assert cat.stdin is not None and cat.stdout is not None


def blob(ref: str) -> bytes:
    if ref in cache:
        return cache[ref]
    cat.stdin.write((ref + '\n').encode()); cat.stdin.flush()
    header = cat.stdout.readline().decode().strip().split()
    assert len(header) == 3 and header[1] == 'blob', (ref, header)
    size = int(header[2]); value = cat.stdout.read(size)
    assert len(value) == size and cat.stdout.read(1) == b'\n'
    cache[ref] = value
    return value


bindings = []
for name, value in list(data.items()):
    if not name.endswith(('/source-manifest.json', '/input.json')):
        continue
    record = json.loads(value)
    source = record.get('head', record.get('source'))
    files = record.get('files', record.get('sourceFiles'))
    if not source or not files:
        continue
    differences = []
    for path, expected in files.items():
        actual = digest(blob(source + ':' + path))
        if actual != expected:
            differences.append({'path': path, 'expected': expected, 'gitBlobSha256': actual})
    bindings.append({'manifest': name, 'source': source, 'filesChecked': len(files), 'mismatches': differences})
for entry in bindings:
    for difference in entry['mismatches']:
        # Native attempts ran while the managed fixture was being written.
        # Preserve those dirty-but-unused source hashes rather than pretending
        # that the complete worktree was the recorded clean commit.
        assert entry['manifest'] in {
            'attempts/command-completion-07/source-manifest.json',
            'attempts/command-completion-08/source-manifest.json',
            'attempts/command-completion-09/source-manifest.json',
        }, entry
        assert difference['path'].startswith('tests/Data.NativeHost/') or difference['path'] == 'tests/ProviderProfileChecks.cs'
        difference['scope'] = 'Uncommitted managed test draft, not compiled or executed by this native attempt. Native product/test inputs match the recorded commit.'
        later = blob('bd11445:' + difference['path'])
        if digest(later) == difference['expected']:
            name = 'recovered-unused-drafts/' + difference['path']
            data[name] = later; origins[name] = 'git:bd11445:' + difference['path']
            difference['recoveredExactDraft'] = name
        else:
            difference['recoveredExactDraft'] = None
            difference['limitation'] = 'Hash retained; exact unused draft bytes were not committed or archived. No managed test credit is assigned to this native attempt.'
cat.stdin.close(); assert cat.wait() == 0
document('source-manifest-validation.json', bindings)
source_mismatches = sum(len(entry['mismatches']) for entry in bindings)
for leaf in ('command-evidence-assembly-01.py', 'command-evidence-assembly-01.log'):
    add(OUTPUT / leaf, 'assembly-attempts/' + leaf)

product_paths = ['src', 'native/cpp/src', 'native/cpp/include', 'native/database/binding']
parities = []
for before, after, paths in [(PRODUCER_SOURCE, FINAL_SOURCE, product_paths),
                             (PRODUCER_SOURCE, ROOT_SOURCE, product_paths),
                             (FINAL_SOURCE, ROOT_SOURCE, ['tests/Data.NativeHost', 'native/cpp/tests/command_completion_tests.cpp', 'native/cpp/tests/query_tests.cpp'])]:
    argv = ['git', 'diff', '--name-only', before, after, '--', *paths]
    difference = subprocess.check_output(argv, cwd=ROOT).decode().splitlines()
    assert not difference, (argv, difference)
    parities.append({'argv': argv, 'differentPaths': difference, 'identical': True})
document('final-integrated-parity.json', {'developerSource': FINAL_SOURCE, 'rootSource': ROOT_SOURCE,
         'rootTree': git('rev-parse', ROOT_SOURCE + '^{tree}').decode().strip(),
         'producerSource': PRODUCER_SOURCE, 'comparisons': parities,
         'scope': 'Development product and relevant test byte identity only; not a new execution at rootSource and not a public-package gate.'})

executables = []
for path in [ROOT / 'artifacts/cmake/linux-x64-release/tests/nw_command_completion_tests',
             *sorted((ROOT / 'artifacts/command-completion-frozen').iterdir()),
             *[ROOT / f'artifacts/command-managed-{n:02d}/aot/Korda.Data.NativeHost.Tests' for n in range(1, 6)]]:
    assert path.is_file(), path
    executables.append({'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path.read_bytes()),
                        'observation': 'Rehashed during archive assembly; binaries are intentionally excluded. Prior build/run receipts retain their original hashes and source identities.'})
document('retained-executable-observation.json', executables)

native = [
    (1, 'build fails: fixture duplicated module_identity supplied by actual host_abi; no runtime credit'),
    (2, 'build passes; wrong fixture expectation: scalar BLOB actual ShapeMismatch/code4, expected code3'),
    (3, 'same failure with exact SQL/status/code/message printed'),
    (4, '338 checks pass on f8; preset cleanup in all cancellation cases did not test missing-secondary attachment'),
    (5, 'deterministic f8 failure after strengthening no-existing-cleanup case; cleanup fault cleared and real joins performed before failure assertion'),
    (6, 'bd78 fixed: same strengthened 338 checks pass'),
    (7, 'runner target typo nw_host_review: ninja unknown target; no compile or runtime credit'),
    (8, 'four adjacent native gates pass on bd78'),
    (9, 'atomic f115 plus scalar transaction/cleanup additions: command374 and four adjacent gates pass'),
    (10, 'actual module capability closure deterministically rejected: reserved database capability bits'),
    (11, 'query capability guard fixed: six gates pass; query970 plus52 SQL/argument goldens, command377, transactions120, streaming369, host review and frozen C ABI'),
    (12, 'test-only PG queued cancellation addition: command377 plus real PostgreSQL8 checks pass; no provider dispatch before queued cancel; zero side effect and owners'),
]
managed = [
    (1, 'AOT publish0, command-only250: actual public Fluent Count seal fails because native capability bit28 was rejected; full not run'),
    (2, 'AOT publish0 only with stage logging; not run because independently proven capability failure remained'),
    (3, 'fixed provider02: publish0, SQLite451 pass, PG fixture timed out expecting cancellation of an already dispatched write; full not run'),
    (4, 'publish0, command-only0 both providers; full250 because held-mapper SessionClose still waited for a generic retirement after migration to command kind7'),
    (5, 'publish0, command-only0 and full0; SQLite-only canceled recursive write, independently observed blocked PG dispatched write, and exact kind7 ready/taken/drained retirement observer; original buffer/mapper/zero-owner assertions preserved'),
]
document('attempt-classification.json', {'native': [{'attempt': n, 'finding': text} for n, text in native],
          'managed': [{'attempt': n, 'finding': text} for n, text in managed],
          'distinction': 'All earlier raw failures and successful isolated stages remain separate. These are development correctness gates, not benchmark, long-run, release, or frozen public-package results.'})

readme = '''# One-shot command completion development evidence

Final managed test source: `21fd325cc528eab720f06e681c1f5cd9aee64da2`.
Integrated root source: `d8beff6dc31f6190caaed333a28847511b7adbc5`.
No-hook independent provider assets were built at `374a253f09f47d0b42f9d18491677158287ba18b`; all product bytes in the final tested and root integrated sources are identical to that producer source. The precise comparisons are in `final-integrated-parity.json`.

## Final successful gates

- `attempts/command-completion-11`: six native gates, including actual capability closure positive/negative controls, new command completion, scalar Count at MaxBatchRows1, transactions, streaming, host review, and the frozen C ABI.
- `attempts/command-completion-12`: final new native tests, 377 default checks and 8 real PostgreSQL queued cancellation checks. A native before-work barrier proves cancel happens before any provider dispatch; an actual query proves no table side effect.
- `attempts/command-managed-05`: real Release Native AOT, command-only and full NativeHost suites both exit0 against two independent no-hook provider assets. Command-only observed 451 assertions per provider; full observed command451 SQLite /452 PostgreSQL, 438 main-suite assertions and36 genuine generic retirements, with all nested suites passing. Assertion totals are observations from each run, not a claimed fixed work count. All native owner diagnostics0..5/8/9 end at zero.
- Existing pull matrix retains exact one SQL execution, exact fetch request/ready/take/publication counts, exact final-close request/ready/take/publication counts, and zero normal generic operations for 0/1/32/64/100/1000 rows on both providers.
- Final AOT executable SHA256: `37a8b860029c98faba728da59f7cce56dca66260df00a449e622fcf7606dde44`. Its source, input manifest and both provider hashes remained unchanged across the tests.

## Failure boundaries retained

`attempt-classification.json` distinguishes actual product failures from fixture/compiler/runner mistakes. The original f8 missing-secondary cleanup failure and the bit28 query capability parser failure are retained. The PG cancellation fixture in managed03 incorrectly assumed that holding managed request return meant native dispatch had not happened; existing dispatched PostgreSQL nonquery semantics preserve the eventual confirmed write result. Final tests distinguish native pre-dispatch cancellation (zero SQL) from a real dispatched UPDATE blocked by a separately held row lock (task remains pending after cancellation intent, then confirms affected count and effect after lock release). The old pg_sleep branch was deleted.

Managed04's full-suite failure was an obsolete generic observer for session close. Final session-close checks require actual kind7/result101 accepted+ready+taken+published+fully-drained state, await real DisposeAsync and LocalResourcesReleased, and still require that the synchronous mapper remains blocked with exactly one live native result buffer. A transferred result owner is independent of the parent's provider join. Source close keeps its genuine generic retirement observer. Full classification of all TestRetirement sites is in the final attempt's retirement-observation-audit.json.

## Reproduction and scope

Original run scripts and argv/exit/timestamp records remain in each attempt. Historical CTest details are immutable copies saved during the corresponding attempt; no later LastTest.log was substituted. Final test/build inputs and all test/fix patches are included. Every source manifest is compared with its recorded git blobs in source-manifest-validation.json. Native attempts07/08/09 include hashes of then-uncommitted managed test drafts (6/6/9 entries). These files were not compiled or executed by those native attempts; all native inputs match their recorded commits. Recoverable exact later-committed draft bytes are included. Some unused probe-formatting draft bytes have only their original hashes; no managed credit is assigned to those attempts. All final native10–12 and managed01–05 manifests match their recorded commits in full. The initial archive audit correctly rejected a claim of universal clean-tree identity; its script/failure log is retained. The latest actual impact plan selects existing interop/linux plus independently validated PostgreSQL/SQLite packages; its actions contain no benchmark, calibration, profiling, or pressure workload.

This archive grants development correctness credit only. It does not grant public package, performance, final30-minute campaign, CI, or release credit. Original Fluent/Relations suites have separate receipts produced by another agent and are not relabeled as this suite. ELF/so files, bin/obj, restore caches, PostgreSQL cluster data and private certificates are excluded. Retained executable paths/hashes are recorded separately. Rebuild from the pinned sources and locked toolchain, using the supplied matching provider manifests; do not bypass the package asset hash check.

Archive metadata is deterministic (mtime/uid/gid0), with SHA256SUMS for every other member. Assembly creates the archive twice and requires byte identity, then extracts to a temporary directory and checks every file byte/hash. The external manifest includes the archive hash, member hashes, original file paths and verification results.
'''
data['README.md'] = readme.encode(); origins['README.md'] = 'assembled evidence explanation'
data['assemble.py'] = pathlib.Path(__file__).read_bytes(); origins['assemble.py'] = str(pathlib.Path(__file__))
checks = ''.join(f'{digest(value)}  {name}\n' for name, value in sorted(data.items()))
data['SHA256SUMS'] = checks.encode(); origins['SHA256SUMS'] = 'generated member hash list (excludes itself)'


def archive_bytes() -> bytes:
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode='w', format=tarfile.USTAR_FORMAT) as tar:
            for name, value in sorted(data.items()):
                member = tarfile.TarInfo(name); member.size = len(value)
                member.mode = 0o644; member.uid = member.gid = member.mtime = 0
                member.uname = member.gname = ''
                tar.addfile(member, io.BytesIO(value))
    return raw.getvalue()


first = archive_bytes(); second = archive_bytes(); assert first == second
target = OUTPUT / (PREFIX + '.tar.gz'); target.write_bytes(first)
with tempfile.TemporaryDirectory(prefix='command-evidence-verify-', dir=OUTPUT) as directory:
    with tarfile.open(target, 'r:gz') as tar:
        assert set(tar.getnames()) == set(data)
        for member in tar.getmembers():
            assert member.isfile() and member.uid == member.gid == member.mtime == 0
        tar.extractall(directory, filter='data')
    for name, value in data.items():
        extracted = (pathlib.Path(directory) / name).read_bytes()
        assert extracted == value and digest(extracted) == digest(value), name

manifest = {'schema': 'command-completion-development-v1', 'archive': str(target),
            'bytes': len(first), 'sha256': digest(first), 'members': len(data),
            'deterministicTwoBuilds': True, 'extractedEveryByteVerified': True,
            'sourceManifestFilesChecked': sum(item['filesChecked'] for item in bindings),
            'sourceManifestDifferences': source_mismatches,
            'executedSourceMismatches': 0,
            'developerSource': FINAL_SOURCE, 'rootSource': ROOT_SOURCE, 'producerSource': PRODUCER_SOURCE,
            'files': [{'path': name, 'bytes': len(value), 'sha256': digest(value), 'origin': origins[name]}
                      for name, value in sorted(data.items())]}
(OUTPUT / (PREFIX + '.manifest.json')).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(OUTPUT / (PREFIX + '.README.md')).write_text(readme)
print(json.dumps({key: manifest[key] for key in manifest if key != 'files'}, indent=2))
