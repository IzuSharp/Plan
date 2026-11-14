#!/usr/bin/env python3
"""Check exact future API instructions; never accept or execute a Delivery task."""
from pathlib import Path
import json
import re
from validate_graphs import Validator
from verify_public_api_history import verify_preservation

P=Path(__file__).resolve().parents[1]

def main():
    _,preserved=verify_preservation()
    check=Validator(P);result=check.run()
    assert result['ok'],result['errors']
    assert result['counts']=={'research':34,'documentation':32,'delivery':48}
    inventory=json.loads((P.parent/'NativeWeave-Design/docs/api/public-api.json').read_bytes())
    policies=inventory['semantic_policies']
    paths=set();types=set()
    for identity,node in check.nodes.items():
        if check.kind[identity]!='delivery':continue
        assert node['status']=='planned_candidate'
        assert node['implementation_authorization']=={'status':'not_authorized','approval_record':None}
        assert node['revision']=='0.4.0'
        assert node['api_contract_types']==sorted(name for name,policy in policies.items() if identity in policy['tasks']),identity
        packet=(P/node['prompt']).read_text()
        assert '## Public API and Documentation Contract' in packet,identity
        assert node['documentation_owner_role'] in packet,identity
        paths.update(node['api_design_inputs']);types.update(node['api_contract_types'])
    assert types==set(policies), ('unassigned public type policies',sorted(set(policies)-types))
    current=[*P.glob('*.md'),*P.glob('*-graph.json'),*P.glob('fragments/*.json'),
             *P.glob('tasks/*.md'),*P.glob('research-tasks/*.md'),*P.glob('documentation-tasks/*.md')]
    for path in current:
        assert not re.search('[\u3400-\u4dbf\u4e00-\u9fff]',path.read_text()),('non-English authoritative content',path)
    cases=[]
    def case(name,mutate,expected):
        candidate=Validator(P);candidate.load();mutate(candidate.nodes['B13']);candidate.public_api()
        assert expected in {e['code'] for e in candidate.errors},(name,candidate.errors)
        cases.append({'case':name,'expected_error':expected,'passed':True})
    case('missing_api_inputs',lambda n:n.pop('api_design_inputs'),'API_INPUTS_REQUIRED')
    case('stale_api_input_hash',lambda n:n['api_design_input_sha256'].update({n['api_design_inputs'][0]:'0'*64}),'HASH_MISMATCH')
    case('missing_documentation_owner',lambda n:n.pop('documentation_owner_role'),'API_DOCUMENTATION_OWNER')
    case('unowned_guide',lambda n:n['documentation_outputs'].__setitem__(0,'NativeWeave:docs/unowned.md'),'API_DOCUMENTATION_NOT_OWNED')
    case('missing_api_verification',lambda n:n['verification_matrix'].pop('api_and_documentation'),'API_VERIFICATION_REQUIRED')
    candidate=Validator(P);candidate.load();candidate.graphs['delivery']['public_api_standard_version']='0.4.0';candidate.public_api()
    assert 'API_STANDARD_VERSION' in {e['code'] for e in candidate.errors}
    cases.append({'case':'refinement_version_is_not_standard_version','expected_error':'API_STANDARD_VERSION','passed':True})
    report={'ok':True,'delivery_tasks':48,'packets':114,'fragments':10,
            'unique_pinned_api_inputs':len(paths),'assigned_public_type_policies':len(types),
            'preserved_original_records':preserved,'negative_cases':cases,
            'research_states':sorted({n['status'] for n in check.graphs['research']['nodes']}),
            'documentation_states':sorted({n['status'] for n in check.graphs['documentation']['nodes']}),
            'product_implementation_authorized':False,'product_delivery_executed':False,
            'scope':'Current exact API instructions, ownership and fail-closed graph integrity; not actual independent acceptance or product execution.'}
    output=P/'verification/public-api-plan.json';output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
