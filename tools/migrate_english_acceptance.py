#!/usr/bin/env python3
"""Migrate accepted Chinese inputs through actual independent English review.

Old evidence and review files remain immutable. New records are prepared separately
and may be accepted only after the same independent reviewers attest their exact
binding hashes. This tool does not translate, invent reviews, or execute research.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess

import prepare_acceptance as original
from validate_graphs import node_digest

P = original.P
D = original.D
DESIGN_BASE = '08e3aaee73aad174620dcff18ed21b3b14c5e632'
PLAN_BASE = 'eff98a38068478cd4c2abb4ea66c62330156941b'
DESIGN_DIR = D/'verification/english-translation/contracts'
PLAN_DIR = P/'ledger/english-translation/acceptance'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def prior_bytes(root, commit, path):
    return original.git_bytes(root, commit, path)

def prior_record(root, commit, path):
    return {'repository':root.name, 'commit':commit, 'path':path,
            'sha256':sha(prior_bytes(root,commit,path))}

def configure(kind):
    if kind == 'contract':
        original.REPORT_DIR = D/'docs/traceability/reviews/english-translation'
        original.REPORT_NAMES = ('contracts.json',)
    else:
        original.REPORT_DIR = P/'ledger/english-translation/reviews'
        original.REPORT_NAMES = ('research-planning.json','design-tasks.json')

def preserve_prior_records():
    for root, commit, prefixes in (
        (D,DESIGN_BASE,('verification/design-acceptance/',
                       'docs/traceability/reviews/final-2026-11-13/')),
        (P,PLAN_BASE,('ledger/acceptance/',))):
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',commit],
                                      cwd=root,text=True).splitlines()
        for path in paths:
            if path.startswith(prefixes):
                assert (root/path).read_bytes()==prior_bytes(root,commit,path), ('prior evidence changed',root.name,path)

def verify_translation_provenance(kind):
    """New provenance claims must equal the actual previously accepted objects."""
    check=original.checker()
    if kind=='contract':
        old=json.loads(prior_bytes(D,DESIGN_BASE,'docs/contracts/registry.json'))['contracts']
        current=original.read(D/'docs/contracts/registry.json')['contracts']
        root,base,index_path=D,DESIGN_BASE,'docs/contracts/acceptance-index.json'
    else:
        old=[]
        for name in ('research','documentation'):
            old.extend(json.loads(prior_bytes(P,PLAN_BASE,name+'-graph.json'))['nodes'])
        current=[n for n in check.nodes.values() if check.kind[n['id']] in {'research','documentation'}]
        root,base,index_path=P,PLAN_BASE,'ledger/completion-acceptance.json'
    prior={v['id']:v for v in old}
    assert {v['id'] for v in current}==set(prior)
    index=original.read(root/index_path)
    migration=index['translation_migration']
    assert migration['prior_acceptance']==prior_record(root,base,index_path)
    assert migration['source_language']=='zh' and migration['authoritative_language']=='en'
    assert migration['native_experiments_rerun'] is False
    old_index=json.loads(prior_bytes(root,base,index_path))
    assert old_index['state']=='accepted_research_and_detailed_design'
    for value in current:
        before=prior[value['id']];assert before['status']=='accepted'
        if kind=='contract':
            expected={'id':value['id'],'version':before['version'],'content_sha256':before['content_sha256'],
                      'source_commit':before['source_commit'],'evidence':before['evidence'],'reviews':before['reviews']}
        else:
            expected={'id':value['id'],'revision':before['revision'],'content_sha256':node_digest(before),
                      'source_commit':before['source_commit'],'evidence':before['acceptance_evidence'],
                      'reviews':before['independent_reviewers']}
        for entry in value['evidence' if kind=='contract' else 'acceptance_evidence']:
            evidence=original.read(check.resolve(entry['manifest_path']))
            snapshot=original.read(check.resolve(evidence['artifact']['path']))
            provenance=snapshot['translation_provenance']
            assert provenance['original_accepted_repository_commit']==base
            assert provenance['original_accepted_subject']==expected
            assert provenance['native_experiments_rerun'] is False
            assert evidence['prior_accepted_evidence']==expected['evidence']
            assert evidence['prior_accepted_reviews']==expected['reviews']
        for entry in value['reviews' if kind=='contract' else 'independent_reviewers']:
            wrapper=original.read(check.resolve(entry['manifest_path']))
            assert wrapper['prior_accepted_source']==base
    return len(current)

def translated_records(check,kind,value,subject,sources,directory,recorded_at,prior):
    evidence_refs,review_refs=original.create_records(
        check,kind,value,subject,sources,directory,recorded_at)
    snapshot_path=directory/(value['id']+'.inputs.json')
    snapshot=original.read(snapshot_path)
    snapshot['translation_provenance']={
        'original_accepted_repository_commit':DESIGN_BASE if kind=='contract' else PLAN_BASE,
        'original_accepted_subject':prior,
        'relationship':'English semantic-equivalent rendering of the accepted input; technical requirements and implementation authorization are unchanged.',
        'native_experiments_rerun':False}
    original.dump(snapshot_path,snapshot)
    evidence_path=directory/(value['id']+'.evidence.json')
    evidence=original.read(evidence_path)
    evidence['artifact']=original.file_ref(snapshot_path)
    evidence['scope']='Committed English inputs, preserved original accepted research/design evidence, and actual independent translation-equivalence review; no new experiment or product result.'
    evidence['prior_accepted_evidence']=prior['evidence']
    evidence['prior_accepted_reviews']=prior['reviews']
    original.dump(evidence_path,evidence)
    review_path=directory/(value['id']+'.review.json')
    review=original.read(review_path)
    review['reviewed_evidence_sha256']=[sha(evidence_path.read_bytes())]
    review['review_scope']='Independent technical translation-equivalence review and preservation of prior accepted conclusions; not a claim of rerunning the original technical research.'
    review['prior_accepted_source']=snapshot['translation_provenance']['original_accepted_repository_commit']
    original.dump(review_path,review)
    return [original.manifest_ref(evidence_path)],[original.manifest_ref(review_path)]

def prepare_contracts(source):
    configure('contract');preserve_prior_records()
    check=original.checker()
    registry=original.read(D/'docs/contracts/registry.json')
    old=json.loads(prior_bytes(D,DESIGN_BASE,'docs/contracts/registry.json'))
    prior={c['id']:c for c in old['contracts']}
    assert len(registry['contracts'])==21 and all(c['status']=='accepted' for c in old['contracts'])
    check.contracts={(c['id'],c['version']):c for c in registry['contracts']}
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for c in original.ordered(registry['contracts'],lambda c:[d['id'] for d in c['dependencies']]):
        previous=prior[c['id']]
        for key in ('id','version','author','spec_path','dependencies','documentation_task_id','acceptance_scope','product_verification'):
            assert c[key]==previous[key],(c['id'],'untranslated structural field changed',key)
        assert c['content_sha256']==sha((D/c['spec_path']).read_bytes())
        c['source_commit']=source
        c['status']='proposed'
        subject={'kind':'contract','id':c['id'],'version':c['version'],'content_sha256':c['content_sha256']}
        prior_subject={'id':c['id'],'version':previous['version'],'content_sha256':previous['content_sha256'],
                       'source_commit':previous['source_commit'],'evidence':previous['evidence'],'reviews':previous['reviews']}
        c['evidence'],c['reviews']=translated_records(check,'contract',c,subject,
            {'NativeWeave-Design':source},DESIGN_DIR,now,prior_subject)
        c['reviewers']=[original.select_report('contract',c['id'])[1]['reviewer']]
    registry['status']='translation_acceptance_prepared'
    original.dump(D/'docs/contracts/registry.json',registry)
    index={'schema_version':'1.0.0','state':'prepared_not_accepted','recorded_at':now,
           'design_source_commit':source,'product_implementation_authorized':False,
           'subjects':[original.index_subject('contract',c) for c in registry['contracts']],
           'binding_attestations':[],
           'translation_migration':{'source_language':'zh','authoritative_language':'en',
               'prior_acceptance':prior_record(D,DESIGN_BASE,'docs/contracts/acceptance-index.json'),
               'technical_versions_unchanged':True,'native_experiments_rerun':False}}
    original.dump(D/'docs/contracts/acceptance-index.json',index)
    verify_translation_provenance('contract')
    print(json.dumps({'prepared_contracts':21,'accepted':0,'independent_binding_attestation_required':True}))

def prepare_tasks(design_source,plan_source):
    configure('task');preserve_prior_records()
    check=original.checker()
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=D,text=True).strip()==design_source
    assert (D/'docs/contracts/registry.json').read_bytes()==prior_bytes(D,design_source,'docs/contracts/registry.json')
    assert all(c['status']=='accepted' for c in check.contracts.values())
    previous={}
    for kind in ('research','documentation'):
        previous.update({n['id']:n for n in json.loads(prior_bytes(P,PLAN_BASE,kind+'-graph.json'))['nodes']})
    values=[n for n in check.nodes.values() if check.kind[n['id']] in {'research','documentation'}]
    assert len(values)==66 and all(n['status']=='accepted' for n in previous.values())
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    for n in values:
        n['source_commit']=plan_source;n['status']='review_ready'
    for n in original.ordered(values,lambda n:check.active_start_dependencies(n)+check.active_acceptance_dependencies(n)):
        before=previous[n['id']]
        for key in ('id','revision','author','start_dependencies','acceptance_dependencies','contract_inputs','research_refs','documentation_refs','outputs','write_scopes','dependency_pins'):
            assert n[key]==before[key],(n['id'],'untranslated structural field changed',key)
        assert node_digest(original.read_graph_node(plan_source,check.kind[n['id']],n['id']))==node_digest(n)
        subject=check.task_subject(n['id'],n)
        prior_subject={'id':n['id'],'revision':before['revision'],'content_sha256':node_digest(before),
                       'source_commit':before['source_commit'],'evidence':before['acceptance_evidence'],
                       'reviews':before['independent_reviewers']}
        n['acceptance_evidence'],n['independent_reviewers']=translated_records(check,'task',n,subject,
            {'Plan':plan_source,'NativeWeave-Design':design_source},PLAN_DIR,now,prior_subject)
    for kind in ('research','documentation'):original.dump(P/(kind+'-graph.json'),check.graphs[kind])
    index={'schema_version':'1.0.0','state':'prepared_not_accepted','recorded_at':now,
           'plan_source_commit':plan_source,'design_source_commit':design_source,
           'product_implementation_authorized':False,
           'subjects':[original.index_subject('task',n) for n in values],
           'binding_attestations':[],
           'translation_migration':{'source_language':'zh','authoritative_language':'en',
               'prior_acceptance':prior_record(P,PLAN_BASE,'ledger/completion-acceptance.json'),
               'task_revisions_unchanged':True,'native_experiments_rerun':False}}
    original.dump(P/'ledger/completion-acceptance.json',index)
    verify_translation_provenance('task')
    print(json.dumps({'prepared_tasks':66,'accepted':0,'independent_binding_attestation_required':True}))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['prepare-contracts','accept-contracts','verify-contracts','prepare-tasks','accept-tasks','verify-tasks'])
    p.add_argument('--design-source');p.add_argument('--plan-source')
    p.add_argument('--attestation',action='append',default=[])
    args=p.parse_args();kind='contract' if args.action.endswith('contracts') else 'task'
    configure(kind)
    if args.action=='prepare-contracts':
        assert args.design_source;prepare_contracts(args.design_source)
    elif args.action=='prepare-tasks':
        assert args.design_source and args.plan_source;prepare_tasks(args.design_source,args.plan_source)
    elif args.action.startswith('accept-'):
        preserve_prior_records();verify_translation_provenance(kind);original.accept(kind,args.attestation)
    else:
        preserve_prior_records();verify_translation_provenance(kind);original.verify_prepared(kind)
        print(json.dumps({'verified_prepared_kind':kind,'acceptance_applied':False}))

if __name__=='__main__':
    main()
