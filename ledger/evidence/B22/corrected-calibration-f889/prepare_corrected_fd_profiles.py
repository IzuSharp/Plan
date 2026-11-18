#!/usr/bin/env python3
"""Prepare review-only FD supplements after complete fresh corrected calibrations."""
from pathlib import Path
import bisect,copy,hashlib,json
root=Path('/workspace/scratch/58d2a6adf1c3/task07-runs')
source=Path('/workspace/scratch/58d2a6adf1c3/.worktree/Task-07-B22-corrected-f889-linux/NativeWeave')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
old_build=json.loads((root/'b22-observer-build-006/manifest.json').read_text())
new_build=json.loads((root/'b22-observer-build-007-f889/manifest.json').read_text())
for name in('BlobStore.cs','ServiceConfiguration.cs'):
    assert old_build['referenceSources'][name]==new_build['referenceSources'][name]
for name,value in old_build['builds']['aot']['files'].items():
    if name.endswith('.so'):assert new_build['builds']['aot']['files'][name]==value
monitor=source/'tests/Verification.EndToEnd/descriptor_profile.py'
launch=root/'b22-corrected-calibration-launch-001-f889'
output=root/'b22-corrected-frozen-candidates-001-f889'
output.mkdir(exist_ok=False)
for provider,previous in(('sqlite','b22-streaming-fd-supplement-sqlite-f889'),('postgresql','b22-streaming-fd-supplement-f889')):
    cal=root/f'b22-corrected-calibration-{provider}-001-f889'
    receipt=json.loads((cal/'receipt.json').read_text())
    assert receipt['status']=='calibration-passed' and receipt['completedCycles']==3
    assert receipt['completedStageSeconds']>=900
    original=cal/'profile-candidate.json';candidate=json.loads(original.read_text())
    previous_candidate=json.loads((root/previous/(provider+'-candidate.json')).read_text())
    supplement=copy.deepcopy(previous_candidate['fdThresholdSupplement'])
    for key in('calibrationReuse','previousCandidateSha256','previousFrozenProfileSha256','descriptorMonitorSource','descriptorMonitorSha256'):
        if key in supplement:supplement['historical_'+key]=supplement.pop(key)
    rows=[json.loads(line)for line in(cal/'resources.jsonl').read_text().splitlines()]
    resources=[row for row in rows if 'monotonicNs'in row]
    times=[row['monotonicNs']for row in resources]
    inventory_path=launch/(provider+'-descriptor-inventories.jsonl')
    inventory=[json.loads(line)for line in inventory_path.read_text().splitlines()]
    final_by_cycle={}
    for frame in inventory:
        if frame['phase']!='idle':continue
        index=bisect.bisect_right(times,frame['startedMonotonicNs'])-1
        assert index>=0
        cycle=resources[index]['controlSequence']
        if cycle>0:final_by_cycle[cycle]=frame
    assert sorted(final_by_cycle)==[1,2,3]
    for cycle,frame in final_by_cycle.items():
        roles=frame['socketRoles']
        assert frame['vanishedDuringRead']==0 and frame['enumerated']==frame['resolved']
        assert not roles.get('unmatched',0)and not roles.get('unclassified',0)
        assert roles.get('listener',0)==1 and roles.get('acceptedHttp',0)==0 and frame['openStagingParts']==0
        if provider=='postgresql':assert 0<roles.get('postgresql',0)<=16
        else:assert roles.get('postgresql',0)==0
        for category,count in frame['categories'].items():
            if category!='socket':assert category in supplement['idleDescriptorClassCaps']and count<=supplement['idleDescriptorClassCaps'][category]
        files={}
        for item in frame['inventory']:
            if item['category']=='fixtureFile':files[item['owner']]=files.get(item['owner'],0)+1
        assert all(name in supplement['idlePersistentFixtureOwnerCaps']and count<=supplement['idlePersistentFixtureOwnerCaps'][name]for name,count in files.items())
    assert 0<=receipt['stageCompletedBeforeClosureNs']-final_by_cycle[3]['endedMonotonicNs']<=3_300_000_000
    idle_cap = 56 if provider == 'sqlite' else 37
    peak_cap = 64 if provider == 'sqlite' else 45
    assert receipt['observedMax']['fileDescriptors']<=peak_cap
    assert all(frame['enumerated']<=idle_cap for frame in final_by_cycle.values())
    supplement.update(descriptorMonitorSource=str(monitor),descriptorMonitorSha256=sha(monitor),freshCandidateSha256=sha(original),freshCalibrationReceiptSha256=sha(cal/'receipt.json'),freshObserverBuildManifestSha256=sha(root/'b22-observer-build-007-f889/manifest.json'),freshClassifiedDescriptorCountsSha256=sha(launch/(provider+'-descriptor-counts.jsonl')),freshClassifiedDescriptorInventoriesSha256=sha(inventory_path),freshClassifiedIdleWitnesses=final_by_cycle,historicalRoleReuse='The006 four-admitted-upload overlap supplies only the witnessed4 HTTP+4 part classes under byte-identical BlobStore, ServiceConfiguration and native modules.007 has its own complete fresh900s calibration and three current classified live-idle witnesses. No former application/calibration duration or native-owner threshold is reused.',unchangedRoleSourceHashes={name:new_build['referenceSources'][name]for name in('BlobStore.cs','ServiceConfiguration.cs')},unchangedNativeModuleHashes={name:value for name,value in new_build['builds']['aot']['files'].items()if name.endswith('.so')})
    candidate['fdThresholdSupplement']=supplement
    candidate['peakCaps']['fileDescriptors']=peak_cap
    candidate['idleCaps']['fileDescriptors']=idle_cap
    candidate['thresholdDerivation']+='; FD bands retain the independently reviewed physical-pool and transient role envelope with fresh007 classified idle witnesses'
    destination=output/(provider+'-candidate.json')
    destination.write_text(json.dumps(candidate,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'provider':provider,'candidate':str(destination),'sha256':sha(destination),'calibrationSeconds':receipt['completedStageSeconds'],'freshIdleDescriptors':[frame['enumerated']for frame in final_by_cycle.values()]}))
