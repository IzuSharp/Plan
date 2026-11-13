#!/usr/bin/env python3
"""Regression cases for summary/delegate run identity; synthetic data, no native runs."""
from copy import deepcopy
from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile

P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lifecycle',P/'tools/verify_source_lifecycle.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
manifest={'run_id':42,'tested_source_commit':'1'*40,'successful_jobs':4,'preserved_raw_files':56,
          'distinct_tests':12,'platform_test_executions':24,'formal_contract_accepted':False,'product_delivery_executed':False}
raw=json.dumps(manifest,sort_keys=True).encode();path='verification/source-lifecycle/results.json';sha=hashlib.sha256(raw).hexdigest()
checkpoint={'native_research_ci':{'manifest_path':path,'manifest_sha256':sha,'run_id':'42','tested_source_commit':'1'*40},
            'design_input_files':[{'path':path,'bytes':len(raw),'sha256':sha}]}
delegate={'passed':True,'tested_source_commit':'1'*40,'raw_files':56,'platform_test_executions':24,'accepted_contracts':0,'product_delivery_executed':False}
results=[]

def case(name,change=None,expected_failure=False):
    with tempfile.TemporaryDirectory(prefix='nw-lifecycle-binding-') as temp:
        root=Path(temp);file=root/path;file.parent.mkdir(parents=True);file.write_bytes(raw)
        cp=deepcopy(checkpoint);result=deepcopy(delegate)
        if change:change(cp,result,root)
        failed=False
        try:
            found=v.verify_ci_manifest(cp,root);v.verify_ci_result(found,result)
        except AssertionError:failed=True
        assert failed==expected_failure,(name,failed,expected_failure)
        results.append({'case':name,'passed':True,'expected_rejection':expected_failure})

case('same_hashed_manifest_and_delegate_source_pass')
case('alternate_summary_path_cannot_replace_fixed_design_manifest',lambda c,r,p:c['native_research_ci'].update(manifest_path='other-run.json'),True)
case('manifest_must_be_in_exact_design_input_list',lambda c,r,p:c.update(design_input_files=[]),True)
case('manifest_input_cannot_be_duplicated',lambda c,r,p:c['design_input_files'].append(deepcopy(c['design_input_files'][0])),True)
case('checkpoint_manifest_digest_must_match_preserved_bytes',lambda c,r,p:c['native_research_ci'].update(manifest_sha256='0'*64),True)
case('checkpoint_source_cannot_name_another_run',lambda c,r,p:c['native_research_ci'].update(tested_source_commit='2'*40),True)
case('delegate_cannot_verify_run_y_for_summary_run_x',lambda c,r,p:r.update(tested_source_commit='2'*40),True)
case('delegate_passed_must_be_boolean_true',lambda c,r,p:r.update(passed='true'),True)
case('delegate_counts_must_match_same_manifest',lambda c,r,p:r.update(platform_test_executions=12),True)

report={'ok':True,'scope':'Synthetic manifest/delegate identity regression only; no native execution or acceptance',
        'case_count':len(results),'cases':results,
        'checked_files_sha256':{file:hashlib.sha256((P/file).read_bytes()).hexdigest() for file in ('tools/verify_source_lifecycle.py','tools/source_lifecycle_binding_checks.py')}}
(P/'verification/source-lifecycle-binding-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
