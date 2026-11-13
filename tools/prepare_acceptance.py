#!/usr/bin/env python3
"""Bind actual reviewed R/D outputs; apply acceptance only after independent attestations.

No synthetic run, GitHub approval, product implementation or release is created.
Preparation and acceptance are separate operations. Inputs must already be committed.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess

from validate_graphs import Validator, node_digest
from review_bindings import (acceptance_index_subject, decision_for, required_paths,
                             verify_acceptance_index, verify_scoped_review)
from verify_completion import input_manifest

P=Path(__file__).resolve().parents[1]
D=P.parent/'NativeWeave-Design'
REPORT_DIR=D/'docs/traceability/reviews/final-2026-11-13'
REPORT_NAMES=('interop-review.json','database-review.json','platform-review.json',
              'server-review.json','integrity-review.json')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_bytes())
def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def ref(path):
    root=P if path.is_relative_to(P) else D
    return root.name+':'+path.relative_to(root).as_posix()
def file_ref(path):return {'path':ref(path),'sha256':sha(path.read_bytes())}
def manifest_ref(path):return {'manifest_path':ref(path),'sha256':sha(path.read_bytes())}
def git_bytes(repo,commit,path):
    assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit),commit
    return subprocess.check_output(['git','show',commit+':'+path],cwd=repo)

def checker():
    value=Validator(P);value.load();value.references();value.architecture();value.fragments()
    assert not value.errors,value.errors
    return value

def select_report(kind,identity):
    found=[]
    for name in REPORT_NAMES:
        path=REPORT_DIR/name
        if not path.exists():continue
        data=read(path)
        rows=data.get('contract_reviews',[]) if kind=='contract' else data.get('task_reviews',data.get('task_decisions',[]))
        if any(row.get('id',row.get('task_id'))==identity for row in rows):
            decision_for(data,kind,identity)
            found.append((path,data))
    assert len(found)==1,(identity,'expected one attributable accepted scoped review',len(found))
    return found[0]

def dependency_snapshot(check,contract):
    result={}
    for pin in contract['dependencies']:
        c=check.contracts[(pin['id'],pin['version'])]
        result[c['id']+'@'+c['version']]={
            'spec_path':c['spec_path'],'content_sha256':c['content_sha256'],
            'evidence_sha256':[e['sha256'] for e in c['evidence']],
            'review_sha256':[r['sha256'] for r in c['reviews']]}
    return result

def create_records(check,kind,value,subject,sources,directory,recorded_at):
    report_path,report=select_report(kind,value['id'])
    own,required=verify_scoped_review(check,report,kind,value)
    rows=[]
    for path in sorted(required):
        repository,relative=path.split(':',1)
        actual=check.resolve(path).read_bytes()
        commit=sources[repository]
        assert actual==git_bytes(P.parent/repository,commit,relative),(value['id'],path,'uncommitted input')
        rows.append({'path':path,'sha256':sha(actual),'bytes':len(actual),'source_commit':commit})
    snapshot={'schema_version':'1.0.0','record_kind':'research_design_input_snapshot',
              'subject':subject,'source_commits':sources,'files':rows,
              'product_execution':False,'scope':'Reviewed research/design inputs and precise existing-task plan; not product validation.'}
    if kind=='contract':snapshot['contract_dependency_snapshot']=dependency_snapshot(check,value)
    snapshot_path=directory/(value['id']+'.inputs.json');dump(snapshot_path,snapshot)
    evidence={'schema_version':'1.0.0','is_template':False,'subject':subject,
              'status':'passed','kind':'design_analysis','producer':'/root','recorded_at':recorded_at,
              'artifact':file_ref(snapshot_path),
              'scope':'Exact committed inputs, preserved source/finite experiment records and actual independent scoped review; no new native run or product result.'}
    evidence_path=directory/(value['id']+'.evidence.json');dump(evidence_path,evidence)
    reviewed_at=report.get('reviewed_at_utc',report.get('observed_at_utc',report.get('date_utc',report.get('reviewed_at'))))
    assert reviewed_at,(value['id'],'review date missing')
    review={'schema_version':'1.0.0','is_template':False,'subject':subject,
            'verdict':'accepted','blocking_findings':[],'reviewer':report['reviewer'],
            'author':value['author'],'reviewed_at':reviewed_at,
            'reviewed_evidence_sha256':[sha(evidence_path.read_bytes())],
            'review_kind':'binding_of_actual_independent_technical_review','recorded_by':'/root',
            'independent_report':file_ref(report_path),
            'binding_boundary':'Integrator-generated binding of the cited real review. Formal status requires the same independent executor to attest these exact manifest hashes.',
            'github_approval_identity_claimed':False,'product_verification_accepted':False}
    review_path=directory/(value['id']+'.review.json');dump(review_path,review)
    return [manifest_ref(evidence_path)],[manifest_ref(review_path)]

def ordered(values,dependencies):
    remaining={value['id']:value for value in values};done=set();result=[]
    while remaining:
        available=[v for v in remaining.values() if set(dependencies(v))<=done]
        assert available,('cyclic or outside acceptance dependency',sorted(remaining))
        for value in sorted(available,key=lambda x:x['id']):
            result.append(value);done.add(value['id']);del remaining[value['id']]
    return result

def index_subject(kind,value):
    return acceptance_index_subject(kind,value)

def prepare_contracts(design_source):
    check=checker();registry=read(D/'docs/contracts/registry.json')
    assert all(c['status']=='proposed' for c in registry['contracts'])
    # Use the same objects while constructing dependency snapshots in topological order.
    check.contracts={(c['id'],c['version']):c for c in registry['contracts']}
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for c in ordered(registry['contracts'],lambda x:[d['id'] for d in x['dependencies']]):
        c['source_commit']=design_source
        subject={'kind':'contract','id':c['id'],'version':c['version'],'content_sha256':c['content_sha256']}
        c['evidence'],c['reviews']=create_records(check,'contract',c,subject,
            {'NativeWeave-Design':design_source},D/'verification/design-acceptance/contracts',now)
        c['reviewers']=[select_report('contract',c['id'])[1]['reviewer']]
    dump(D/'docs/contracts/registry.json',registry)
    index={'schema_version':'1.0.0','state':'prepared_not_accepted','recorded_at':now,
           'design_source_commit':design_source,'product_implementation_authorized':False,
           'subjects':[index_subject('contract',c) for c in registry['contracts']],
           'binding_attestations':[]}
    dump(D/'docs/contracts/acceptance-index.json',index)
    print(json.dumps({'prepared_contracts':len(index['subjects']),'accepted':0,'requires_independent_exact_binding':True}))

def prepare_tasks(design_source,plan_source):
    check=checker()
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=D,text=True).strip()==design_source
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()==plan_source
    assert (D/'docs/contracts/registry.json').read_bytes()==git_bytes(D,design_source,'docs/contracts/registry.json')
    assert all(c['status']=='accepted' for c in check.contracts.values())
    values=[n for n in check.nodes.values() if check.kind[n['id']] in {'research','documentation'}]
    assert all(n['status']=='review_ready' for n in values)
    for n in values:n['source_commit']=plan_source
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for n in ordered(values,lambda x:check.active_start_dependencies(x)+check.active_acceptance_dependencies(x)):
        original=read_graph_node(plan_source,check.kind[n['id']],n['id'])
        assert node_digest(original)==node_digest(n),(n['id'],'source task semantics changed')
        subject=check.task_subject(n['id'],n)
        n['acceptance_evidence'],n['independent_reviewers']=create_records(check,'task',n,subject,
            {'Plan':plan_source,'NativeWeave-Design':design_source},P/'ledger/acceptance',now)
    for kind in ('research','documentation'):dump(P/(kind+'-graph.json'),check.graphs[kind])
    index={'schema_version':'1.0.0','state':'prepared_not_accepted','recorded_at':now,
           'plan_source_commit':plan_source,'design_source_commit':design_source,
           'product_implementation_authorized':False,'subjects':[index_subject('task',n) for n in values],
           'binding_attestations':[]}
    dump(P/'ledger/completion-acceptance.json',index)
    print(json.dumps({'prepared_tasks':len(values),'accepted':0,'requires_independent_exact_binding':True}))

def read_graph_node(commit,kind,identity):
    graph=json.loads(git_bytes(P,commit,kind+'-graph.json'))
    return next(n for n in graph['nodes'] if n['id']==identity)

def verify_prepared(kind):
    check=checker()
    registry=read(D/'docs/contracts/registry.json')
    values=registry['contracts'] if kind=='contract' else [n for n in check.nodes.values() if check.kind[n['id']] in {'research','documentation'}]
    for value in values:
        subject=({'kind':'contract','id':value['id'],'version':value['version'],'content_sha256':value['content_sha256']}
                 if kind=='contract' else check.task_subject(value['id'],value))
        ev=value['evidence'] if kind=='contract' else value['acceptance_evidence']
        rv=value['reviews'] if kind=='contract' else value['independent_reviewers']
        checked=check.evidence(ev,subject,value['id'])
        check.reviews(rv,subject,value['author'],[h for h,m in checked],value['id'])
        for _,evidence in checked:
            snapshot=input_manifest(check,evidence['artifact'],required_paths(check,kind,value)[1])
            assert snapshot['subject']==subject
            if kind=='contract':
                assert snapshot['contract_dependency_snapshot']==dependency_snapshot(check,value)
                assert snapshot['source_commits']['NativeWeave-Design']==value['source_commit']
            else:
                assert snapshot['source_commits']['Plan']==value['source_commit']
                assert node_digest(read_graph_node(value['source_commit'],check.kind[value['id']],value['id']))==node_digest(value)
        for entry in rv:
            wrapper=read(check.resolve(entry['manifest_path']));record=wrapper['independent_report']
            raw=check.require_file_hash(record['path'],record['sha256'],value['id']+'/review-report')
            assert raw is not None
            report=json.loads(raw)
            assert report['reviewer']==wrapper['reviewer']
            verify_scoped_review(check,report,kind,value)
    index_path=D/'docs/contracts/acceptance-index.json' if kind=='contract' else P/'ledger/completion-acceptance.json'
    verify_acceptance_index(check,read(index_path),kind,values,
        {'prepared_not_accepted','accepted_research_and_detailed_design'})
    assert not check.errors,check.errors
    return check,registry,values

def accept(kind,attestation_paths):
    check,registry,values=verify_prepared(kind)
    index_path=D/'docs/contracts/acceptance-index.json' if kind=='contract' else P/'ledger/completion-acceptance.json'
    index=read(index_path)
    assert index['state']=='prepared_not_accepted'
    subjects=[index_subject(kind,value) for value in values]
    assert index['subjects']==subjects
    attestations=[];refs=[]
    for value in attestation_paths:
        path=Path(value).resolve();assert path.is_relative_to(P) or path.is_relative_to(D)
        data=read(path)
        assert data['verdict']=='accepted' and data['blocking_findings']==[]
        attestations.extend((data['reviewer'],item) for item in data['subjects'])
        refs.append(file_ref(path))
    for value,subject in zip(values,subjects):
        reviews=value['reviews'] if kind=='contract' else value['independent_reviewers']
        reviewers={read(check.resolve(r['manifest_path']))['reviewer'] for r in reviews}
        assert any(actor in reviewers and item==subject for actor,item in attestations),(kind,value['id'],'not independently attested')
    for value in values:
        value['status']='accepted'
        if kind=='contract':value['specification_status']='accepted_research_and_detailed_design'
    if kind=='contract':
        registry['status']='accepted_research_and_detailed_design'
        dump(D/'docs/contracts/registry.json',registry)
    else:
        for name in ('research','documentation'):
            check.graphs[name]['graph_status']='accepted_research_and_detailed_design'
            check.graphs[name]['scope']='Source-backed research and detailed design accepted for future implementation guidance; no product implementation, release or performance accepted.'
            dump(P/(name+'-graph.json'),check.graphs[name])
    index.update(state='accepted_research_and_detailed_design',binding_attestations=refs)
    dump(index_path,index)
    print(json.dumps({'accepted_kind':kind,'count':len(values),'product_implementation_authorized':False}))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare-contracts','prepare-tasks','verify-contracts','verify-tasks','accept-contracts','accept-tasks'])
    parser.add_argument('--design-source');parser.add_argument('--plan-source')
    parser.add_argument('--attestation',action='append',default=[])
    args=parser.parse_args()
    if args.action=='prepare-contracts':
        assert args.design_source;prepare_contracts(args.design_source)
    elif args.action=='prepare-tasks':
        assert args.design_source and args.plan_source;prepare_tasks(args.design_source,args.plan_source)
    elif args.action.startswith('verify-'):
        _,_,values=verify_prepared('contract' if args.action=='verify-contracts' else 'task')
        print(json.dumps({'verified_prepared':len(values),'acceptance_applied':False}))
    else:accept('contract' if args.action=='accept-contracts' else 'task',args.attestation)

if __name__=='__main__':main()
