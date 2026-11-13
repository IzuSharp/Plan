#!/usr/bin/env python3
"""Preserve historical selection tests and test today's mandatory Rust architecture."""
from pathlib import Path
import json
from history_gate import run_frozen
from verify_completion import verify
from validate_graphs import Validator

P=Path(__file__).resolve().parents[1]

def main():
    historical=run_frozen('host_selection_checks.py')
    current=verify()
    cases=[]
    def case(name,mutate,expected):
        check=Validator(P)
        check.load()
        mutate(check)
        check.architecture()
        codes={e['code'] for e in check.errors}
        assert expected in codes,(name,codes)
        ready,_,_=check.ready()
        assert not any(ready.values()),name
        cases.append({'case':name,'passed':True,'expected_error':expected})
    case('managed_sql_engine_rejected',lambda c:c.graphs['delivery']['architecture_policy'].update(database_engine='CSharp'),'ARCHITECTURE_POLICY')
    case('kestrel_product_host_rejected',lambda c:c.graphs['delivery']['architecture_policy'].update(server_host_task='B15'),'ARCHITECTURE_POLICY')
    case('optional_rust_host_rejected',lambda c:c.nodes['B17'].update(selection_required=True,selection_status='undecided'),'REQUIRED_NATIVE_ROLE_OPTIONAL')
    case('legacy_host_alternative_rejected',lambda c:c.nodes['B16'].update(required_selection_groups=[{'id':'server-host','task_ids':['B15','B17'],'minimum_selected':1}]),'LEGACY_HOST_SELECTION_GROUP')
    case('application_without_native_acceptance_rejected',lambda c:c.nodes['B15'].update(acceptance_dependencies=[]),'APPLICATION_NATIVE_HOST_ACCEPTANCE')
    case('duplicate_native_host_scope_rejected',lambda c:c.nodes['B15']['write_scopes'].append('NativeWeave:native/server/host/'),'DUPLICATE_PRODUCTION_HOST')
    case('conditional_required_release_host_rejected',lambda c:next(x for x in c.nodes['B24']['release_scope']['components'] if x['task_id']=='B17').update(when='selected'),'RELEASE_NATIVE_ROLE_REQUIRED')
    case('product_authorization_in_research_rejected',lambda c:c.nodes['A01']['implementation_authorization'].update(status='authorized'),'CURRENT_PHASE_PRODUCT_AUTHORIZATION')
    case('product_execution_in_research_rejected',lambda c:c.nodes['A01'].update(status='in_progress'),'CURRENT_PHASE_PRODUCT_EXECUTION')
    report={'ok':True,'scope':'Full historical gate at original pair plus current mandatory Rust architecture negatives; no product execution.',
            'historical':historical,'current':current,'case_count':len(cases),'policy_cases':cases}
    (P/'verification/host-selection-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
