#!/usr/bin/env python3
"""Host-choice gate regression tests; no product execution or acceptance.

The small in-memory policy fixture suppresses unrelated evidence/authentication
checks to exercise positive and negative selection outcomes in isolation. The
unchanged mutation suite and the real full-graph check still enforce those gates.
No fixture authorization or acceptance record is written to the product ledger.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import tempfile

P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validator',P/'tools/validate_graphs.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
NODES={n['id']:n for n in json.loads((P/'delivery-graph.json').read_text())['nodes']}
RESULTS=[]

class PolicyFixture(v.Validator):
    """Only host selection/dependency/scope logic is under test in this fixture."""
    def authorization(self,nid,n):return True
    def evidence(self,*args):return []
    def reviews(self,*args):pass

def fixture(kestrel,rust,target='B16'):
    validator=PolicyFixture(P)
    validator.nodes={nid:deepcopy(NODES[nid]) for nid in ('B15','B17',target)}
    validator.kind={nid:'delivery' for nid in validator.nodes}
    for n in validator.nodes.values():
        n.update(start_dependencies=[],acceptance_dependencies=[],dependency_pins={},
                 contract_inputs=[],research_refs=[],documentation_refs=[],verification_requirements=[],
                 source_commit='1'*40)
    for host,choice in [('B15',kestrel),('B17',rust)]:
        validator.nodes[host]['selection_status']=choice
        validator.nodes[host]['status']='accepted' if choice=='selected' else 'planned_candidate'
    node=validator.nodes[target];node['status']='planned'
    node['conditional_dependencies']=[c for c in node['conditional_dependencies'] if c['task_id'] in {'B15','B17'}]
    node['selection_inputs']=['B15','B17']
    if node.get('release_scope'):
        node['release_scope']['status']='accepted'
        node['release_scope']['components']=[c for c in node['release_scope']['components'] if c['task_id'] in {'B15','B17'}]
    return validator,node

def record(name,fn):
    fn();RESULTS.append({'case':name,'passed':True})

def blocked_choices(kestrel,rust,expected):
    for target in ('B16','B24'):
        checker,node=fixture(kestrel,rust,target)
        ready,blocked,_=checker.ready()
        assert target not in ready['delivery'],(target,kestrel,rust)
        assert any(expected in reason for reason in blocked[target]),blocked[target]
        node['status']='accepted';checker.check_acceptance()
        assert expected in {e['code'] for e in checker.errors},checker.errors

def admitted_choices(kestrel,rust,expected):
    for target in ('B16','B24'):
        checker,node=fixture(kestrel,rust,target)
        checker.references();assert not checker.errors,checker.errors
        ready,_,_=checker.ready();assert target in ready['delivery']
        subject=checker.task_subject(target,node)
        assert set(subject['dependency_snapshot'])==set(expected),subject
        assert set(subject['selection_snapshot'])=={'B15','B17'}
        node['status']='accepted';checker.check_acceptance();assert not checker.errors,checker.errors

record('both_undecided_block_start_and_acceptance',lambda:blocked_choices('undecided','undecided','SELECTION_GROUP_UNSATISFIED'))
record('both_excluded_block_start_and_acceptance',lambda:blocked_choices('excluded','excluded','SELECTION_GROUP_UNSATISFIED'))
record('one_selected_other_unresolved_still_blocks',lambda:blocked_choices('selected','undecided','SELECTION_UNRESOLVED'))
record('kestrel_only_has_no_rust_dependency',lambda:admitted_choices('selected','excluded',['B15']))
record('rust_only_has_no_kestrel_dependency',lambda:admitted_choices('excluded','selected',['B17']))
record('both_selected_require_both_profiles_without_default',lambda:admitted_choices('selected','selected',['B15','B17']))

def unfinished_start():
    checker,node=fixture('excluded','selected')
    checker.nodes['B17']['status']='planned_candidate'
    ready,blocked,_=checker.ready()
    assert 'B16' not in ready['delivery'] and 'dependency=B17' in blocked['B16']
    node['status']='accepted';checker.check_acceptance()
    assert any(e['code']=='DEPENDENCY_NOT_ACCEPTED' and e['message']=='B16->B17' for e in checker.errors)
record('selected_conditional_start_requires_real_dependency',unfinished_start)

def unfinished_acceptance():
    checker,node=fixture('excluded','selected','B24');checker.nodes['B17']['status']='planned_candidate'
    ready,_,_=checker.ready();assert 'B24' in ready['delivery']
    node['status']='accepted';checker.check_acceptance()
    assert any(e['code']=='DEPENDENCY_NOT_ACCEPTED' and e['message']=='B24->B17' for e in checker.errors)
    assert any(e['code']=='RELEASE_COMPONENT_NOT_ACCEPTED' for e in checker.errors)
record('acceptance_only_edge_blocks_completion_not_start',unfinished_acceptance)

def changed_selection():
    checker,node=fixture('selected','excluded');old=checker.task_subject('B16',node)
    checker.nodes['B15']['selection_status']='excluded';checker.nodes['B17']['selection_status']='selected'
    new=checker.task_subject('B16',node)
    assert old!=new and old['selection_snapshot']!=new['selection_snapshot']
    assert set(old['dependency_snapshot'])=={'B15'} and set(new['dependency_snapshot'])=={'B17'}
record('selection_flip_invalidates_subject_and_dependency_snapshot',changed_selection)

def structural_error(name,change,code,target='B16'):
    def run():
        checker,node=fixture('excluded','selected',target);change(checker,node);checker.references()
        assert code in {e['code'] for e in checker.errors},checker.errors
        ready,_,_=checker.ready();assert not any(ready.values())
    record(name,run)

structural_error('conditional_revision_drift_rejected',lambda c,n:n['conditional_dependencies'][1].update(revision='9.9.9'),'CONDITIONAL_VERSION')
structural_error('group_member_missing_selection_snapshot_rejected',lambda c,n:n.update(selection_inputs=['B17']),'SELECTION_GROUP_REFERENCE')
structural_error('zero_host_minimum_rejected',lambda c,n:n['required_selection_groups'][0].update(minimum_selected=0),'SELECTION_GROUP_SCHEMA')
structural_error('duplicate_group_member_rejected',lambda c,n:n['required_selection_groups'][0].update(task_ids=['B17','B17']),'SELECTION_GROUP_SCHEMA')

def make_cycle(checker,node):
    checker.nodes['B17']['start_dependencies']=['B16']
    checker.nodes['B17']['dependency_pins']={'B16':node['revision']}
structural_error('conditional_start_cycle_rejected',make_cycle,'DEPENDENCY_CYCLE')
def drift_proposed_scope(checker,node):
    node['release_scope']['status']='proposed'
    node['release_scope']['components'][0]['revision']='9.9.9'
structural_error('proposed_release_component_revision_checked',drift_proposed_scope,'RELEASE_COMPONENT_VERSION','B24')

def optionalize_required_db(checker,node):
    db=deepcopy(NODES['B04']);db.update(start_dependencies=[],acceptance_dependencies=[],dependency_pins={},contract_inputs=[],research_refs=[],documentation_refs=[])
    checker.nodes['B04']=db;checker.kind['B04']='delivery'
    node['release_scope']['components'].append({'task_id':'B04','revision':db['revision'],'when':'selected'})
structural_error('required_database_cannot_be_conditionally_omitted',optionalize_required_db,'RELEASE_SELECTION_REFERENCE','B24')

def candidate_state_invariants():
    assert len(NODES)==48
    assert all(n['status']=='planned_candidate' and n['implementation_authorization']['status']=='not_authorized' for n in NODES.values())
    for host in ('B15','B17'):
        assert NODES[host]['selection_required'] and NODES[host]['selection_status']=='undecided'
    for target in ('B16','B18','B19','B20','B21','B22','B23','B24'):
        assert NODES[target]['required_selection_groups']==[{'id':'server-host','task_ids':['B15','B17'],'minimum_selected':1}]
        assert 'B15' not in NODES[target]['start_dependencies']
    scope={c['task_id']:c for c in NODES['B24']['release_scope']['components']}
    assert scope['B04']['when']=='always' and scope['B15']['when']==scope['B17']['when']=='selected'
record('real_candidate_graph_preserves_unselected_unauthorized_states',candidate_state_invariants)

def protocol_fixture(kestrel,rust,kestrel_protocol,rust_protocol,accepted=True):
    checker,node=fixture(kestrel,rust,'B18');node['selection_status']='selected'
    node['protocol_host_profiles'][0]['selection_status']=kestrel_protocol
    node['protocol_host_profiles'][1]['selection_status']=rust_protocol
    contract=deepcopy(node['protocol_host_profiles'][0]['contract_input'])
    node['contract_inputs']=[contract]
    key=(contract['id'],contract['version'])
    checker.fixture_directory=tempfile.TemporaryDirectory(prefix='nw-protocol-scope-')
    checker.bundle=Path(checker.fixture_directory.name);checker.plan=checker.bundle/'Plan'
    path=checker.bundle/'NativeWeave-Design/docs/protocol.md';path.parent.mkdir(parents=True)
    raw=b'# Synthetic selection test spec; not a product contract.\n\n```json nativeweave-protocol-host-profiles-v1\n{"host_task_ids":["B15"]}\n```\n'
    path.write_bytes(raw)
    checker.contracts[key]={**contract,'status':'accepted' if accepted else 'proposed','spec_path':'docs/protocol.md','content_sha256':hashlib.sha256(raw).hexdigest()}
    if accepted:checker.checked_contracts.add(key)
    return checker,node

def protocol_blocked(choices,code,accepted=True):
    checker,node=protocol_fixture(*choices,accepted=accepted)
    ready,blocked,_=checker.ready()
    assert 'B18' not in ready['delivery'] and any(code in r for r in blocked['B18']),blocked
    node['status']='accepted';checker.check_acceptance()
    assert code in {e['code'] for e in checker.errors},checker.errors

record('rust_only_protocol_requires_specific_accepted_design',lambda:protocol_blocked(('excluded','selected','excluded','selected'),'PROTOCOL_PROFILE_DESIGN_MISSING'))
record('enabled_protocol_matrix_cannot_remain_undecided',lambda:protocol_blocked(('selected','excluded','undecided','excluded'),'PROTOCOL_PROFILE_UNRESOLVED'))
record('proposed_protocol_contract_does_not_enable_profile',lambda:protocol_blocked(('selected','excluded','selected','excluded'),'PROTOCOL_PROFILE_CONTRACT_UNACCEPTED',False))
record('protocol_cannot_enable_an_unselected_host',lambda:protocol_blocked(('excluded','selected','selected','excluded'),'PROTOCOL_PROFILE_HOST_UNSELECTED'))
record('selected_protocol_cannot_exclude_every_host_profile',lambda:protocol_blocked(('selected','selected','excluded','excluded'),'PROTOCOL_PROFILE_EMPTY'))

def partial_protocol_matrix():
    checker,node=protocol_fixture('selected','selected','selected','excluded')
    checker.references();assert not checker.errors,checker.errors
    ready,_,_=checker.ready();assert 'B18' in ready['delivery']
    old=checker.task_subject('B18',node)
    assert set(old['dependency_snapshot'])=={'B15'},old
    node['status']='accepted';checker.check_acceptance();assert not checker.errors,checker.errors
    node['protocol_host_profiles'][1]['selection_status']='selected'
    assert checker.task_subject('B18',node)!=old
    assert ('PROTOCOL_PROFILE_DESIGN_MISSING','B17') in checker.protocol_profile_issues(node)
record('dual_hosts_can_publish_explicit_kestrel_only_protocol_matrix',partial_protocol_matrix)

def protocol_coverage():
    checker,node=protocol_fixture('selected','excluded','selected','excluded')
    node['protocol_host_profiles'].pop();checker.references()
    assert 'PROTOCOL_PROFILE_COVERAGE' in {e['code'] for e in checker.errors}
record('protocol_matrix_must_cover_declared_host_choices',protocol_coverage)

def protocol_contract_cannot_be_freeform_approval():
    checker,node=protocol_fixture('excluded','selected','excluded','selected')
    node['protocol_host_profiles'][1]['contract_input']={'approved':True}
    checker.references();assert 'PROTOCOL_PROFILE_CONTRACT' in {e['code'] for e in checker.errors}
record('protocol_profile_cannot_replace_contract_with_approved_flag',protocol_contract_cannot_be_freeform_approval)

def wrong_host_same_contract():
    checker,node=protocol_fixture('excluded','selected','excluded','selected')
    node['protocol_host_profiles'][1]['contract_input']=deepcopy(node['protocol_host_profiles'][0]['contract_input'])
    checker.references();assert not checker.errors,checker.errors
    ready,blocked,_=checker.ready()
    assert 'B18' not in ready['delivery'] and 'PROTOCOL_PROFILE_HOST_NOT_IN_CONTRACT=B17' in blocked['B18']
    node['status']='accepted';checker.check_acceptance()
    assert 'PROTOCOL_PROFILE_HOST_NOT_IN_CONTRACT' in {e['code'] for e in checker.errors}
record('rust_cannot_reuse_accepted_kestrel_only_contract',wrong_host_same_contract)

def host_scope_hash_cannot_change_after_review():
    checker,node=protocol_fixture('selected','excluded','selected','excluded')
    path=checker.bundle/'NativeWeave-Design/docs/protocol.md';path.write_text(path.read_text().replace('["B15"]','["B15","B17"]'))
    ready,_,_=checker.ready()
    assert not any(ready.values()) and 'HASH_MISMATCH' in {e['code'] for e in checker.errors}
record('host_scope_edit_invalidates_accepted_spec_hash',host_scope_hash_cannot_change_after_review)

def missing_scope_cannot_be_assumed():
    checker,node=protocol_fixture('selected','excluded','selected','excluded')
    path=checker.bundle/'NativeWeave-Design/docs/protocol.md';path.write_text('# Fixture with no host declaration.\n')
    key=next(iter(checker.contracts));checker.contracts[key]['content_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    ready,blocked,_=checker.ready()
    assert 'B18' not in ready['delivery'] and 'PROTOCOL_PROFILE_HOST_NOT_IN_CONTRACT=B15' in blocked['B18']
record('missing_hashed_host_scope_fails_closed',missing_scope_cannot_be_assumed)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--policy-only',action='store_true',help='Run isolated selection checks while paired Design input is still being finalized')
    args=parser.parse_args()
    full=None if args.policy_only else v.Validator(P).run()
    if full is not None:
        assert full['ok'],full['errors']
        assert full['accepted_contracts']==0 and not full['ready']['delivery'] and not full['continuable']['delivery']
    report={'scope':'Isolated host policy tests plus candidate graph invariants; not product acceptance or reviewer authentication',
            'ok':True,'policy_cases':RESULTS,'case_count':len(RESULTS),
            'full_graph_checked':full is not None,'delivery_ready':None if full is None else full['ready']['delivery'],
            'checked_files_sha256':{p:hashlib.sha256((P/p).read_bytes()).hexdigest() for p in ['delivery-graph.json','schemas/graph-v1.schema.json','tools/validate_graphs.py','tools/host_selection_checks.py']}}
    path=P/'verification/host-selection-checks.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
