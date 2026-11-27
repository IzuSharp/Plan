#!/usr/bin/env python3
"""Archive only sealed Recovery05 evidence using the reviewed fixed restorer."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / 'supplement-03'
FIXED = HERE / 'supplement-02/streaming_archive.py'
EXPECTED_FIXED_SHA = 'b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c'
assert hashlib.sha256(FIXED.read_bytes()).hexdigest() == EXPECTED_FIXED_SHA
spec = importlib.util.spec_from_file_location('reviewed_fixed_streaming_archive', FIXED)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.HERE, engine.ROOT, engine.OUTPUT = OUTPUT, ROOT, OUTPUT

LOCAL_FILES = [
    'run_mixed_cell.py', 'run_proc_tree_observer.py', 'run_verified_mixed_cell.py',
    'run_verified_series.py', 'freeze_verified_mixed_inputs.py',
    'check_verified_wrapper_abort.py', 'check_verified_wrapper_static.py',
    'retire_verified_fixture.py', 'check_fixture_retirement_static.py',
    'fixture-retirement-independent-review-01.md', 'check_proc_tree_observer.py',
    'check_proc_cpu_transfer.py', 'analyze_proc_cpu_transfer.py',
]
PUBLICATION_FILES = [
    'archive04-published.json', 'archive02-published.json', 'archive02-local-sync.json',
    'plan-archive04-local-sync.json', 'continuation06-publication.json',
    'ci-verified-heads-05.json', 'go-drafts-observed-06.json',
    'korda-design-combined05-published.json', 'plan-combined05-published.json',
    'combined05-publication-metadata.json', 'product05-published.json',
    'connector-publication-04.json', 'continuation05-publication-metadata.json',
]
CLEANUP_FILES = [
    'cleanup_published_archives_05.py', 'cleanup-published-archives-05.json',
    'cleanup-published-archives-receipt-05.json', 'df-after-published-archive-cleanup-05.txt',
    'local-archive-availability-05.json', 'LOCAL-RECOVERY-AFTER-CLEANUP-05.md',
    'publication-ready-04/path-to-sha.json', 'supplement-02/path-to-sha-corrected-final.json',
]
GROUPS = {
    'mixed-zero-pressure05': ['experiments/recovery/zero-cost-05', 'experiments/recovery/pressure-05'],
    'closed-controls05': [
        'experiments/recovery/early-stop-risk-05', 'experiments/recovery/plan-ci-timeout-05',
        'experiments/recovery/verified-wrapper-review-01',
        'experiments/recovery/verified-wrapper-independent-review-05',
        'experiments/recovery/fixture-retirement-review-01',
        *['experiments/recovery/'+name for name in LOCAL_FILES],
        'worktrees/Korda/benchmarks/db-perf/run.py',
        'worktrees/Korda/benchmarks/db-perf/campaign.py',
        'worktrees/Korda/benchmarks/db-perf/campaign_build.py',
        'worktrees/Korda/benchmarks/db-perf/plan_diagnostics.py',
        'worktrees/Korda/benchmarks/db-perf/workload/check_dapper_contract.py',
        'worktrees/Korda/benchmarks/db-perf/workload/queries-v3.json',
    ],
    'publication-cleanup05': [
        *['observations/recovery/'+name for name in PUBLICATION_FILES],
        *['experiments/recovery/archive-recovery-04/'+name for name in CLEANUP_FILES],
    ],
}
engine.GROUPS = GROUPS
engine.NOTES = [
    'Only sealed Recovery05 source, raw results, failed attempts, controls, reviews and publication/cleanup records are selected. The zero-cost and pressure controllers have completed.',
    'Active tail06 source/build/diagnostic trees are not selected. No new source bundles, large consumer artifacts, toolchain installation or archive parts from prior sets are duplicated.',
    'Actual baseline/Dapper/server/toolchain dependencies live in archives-01 at Plan b54054bd1f3befe94e1817cc29f494bd782854b9; integrated04/05 ELF/native/packages and prior controls live in archives-02 at 27e0f35709036b0737ed101ba6472ce1461c0538. Historical Stage1 dependencies remain as those indexes specify.',
    'Physical database directories and SQLite fixture/WAL/SHM bytes are excluded, including retired fixtures. Original raw/configuration and fixture retirement controls/receipts remain. No database directory is recreated.',
    'Compiler intermediates and caches are excluded. Generated response/assets/source evidence exceptions follow the reviewed selection logic.',
    'Finite zero-cost and pressure cells retain their original ordinary-timing identities and false final-credit fields. Profiling/controls/failures retain their original verdicts. This archive adds no performance credit.',
    'The corrected streaming verifier SHA256 is b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c. No full compressed, tar or roundtrip copy is created.',
    'Prior local compressed duplicates were deleted only after pinned remote publication/readback and exact SHA verification. Their manifests and cleanup/publication receipts are preserved in this increment.',
]


def prepare():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if (OUTPUT/'selection.json').exists():
        raise RuntimeError('Selection already frozen; resume builds without overwriting it')
    (OUTPUT/'streaming_archive.py').write_bytes(FIXED.read_bytes())
    for campaign in ('zero-cost-05','pressure-05'):
        state=json.loads((ROOT/'experiments/recovery'/campaign/'series-01.plan.resume.json').read_text())
        assert state['passed'] and state['stage']=='completed'
    wrapper=ROOT/'experiments/recovery/run_verified_mixed_cell.py'
    pressure_plan=json.loads((ROOT/'experiments/recovery/pressure-05/series-01.plan.json').read_text())
    assert hashlib.sha256(wrapper.read_bytes()).hexdigest()==pressure_plan['wrapperSha256']
    selection=engine.select()
    for files in selection['groups'].values():
        assert not any('tail06' in x['path'].lower() or 'tail-06' in x['path'].lower() for x in files)
    selection['reviewedStreamingVerifierSha256']=EXPECTED_FIXED_SHA
    selection['closedRootGroups']=GROUPS
    selection['dependencies']={'archives01':'b54054bd1f3befe94e1817cc29f494bd782854b9','archives02':'27e0f35709036b0737ed101ba6472ce1461c0538'}
    engine.dump(OUTPUT/'selection.json',selection)
    engine.dump(OUTPUT/'source-identity.json',{'builderPath':str(Path(__file__).resolve()),
        'builderSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'reviewedEnginePath':str(FIXED),'reviewedEngineSha256':EXPECTED_FIXED_SHA,
        'ordinaryWrapperSha256':pressure_plan['wrapperSha256'],'noNewPerformanceCredit':True})
    print(json.dumps({'groups':{n:{'files':len(v),'expandedBytes':sum(x['stamp'][0] for x in v)} for n,v in selection['groups'].items()},
                      'freeBytes':os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','build'])
    parser.add_argument('--name',choices=list(GROUPS))
    args=parser.parse_args()
    if args.action=='prepare':
        prepare()
    else:
        if not args.name:
            parser.error('--name is required')
        receipt=OUTPUT/(args.name+'-receipt.json')
        if receipt.exists() and json.loads(receipt.read_text()).get('passed'):
            print(json.dumps({'alreadyVerified':args.name,'receipt':str(receipt)}))
        else:
            engine.build(args.name)
