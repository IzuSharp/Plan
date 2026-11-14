#!/usr/bin/env python3
"""Reject malformed exact-binding claims using isolated synthetic records only."""
import copy
import hashlib
import json
from pathlib import Path
from review_bindings import acceptance_index_subject, verify_binding_attestations

P=Path(__file__).resolve().parents[1]
def raw(value):return (json.dumps(value,sort_keys=True)+'\n').encode()
def digest(value):return hashlib.sha256(value).hexdigest()

class Fixture:
    def __init__(self):
        self.files={};self.values=[]
        for identity in ('FIXTURE-01','FIXTURE-02'):
            path='Plan:fixture/'+identity+'.review.json'
            value=raw({'reviewer':'fixture/independent-reviewer'})
            self.files[path]=value
            self.values.append({'id':identity,'author':'fixture/author',
                'evidence':[{'sha256':digest(identity.encode())}],
                'reviews':[{'manifest_path':path,'sha256':digest(value)}]})
        self.attestation={'verdict':'accepted','blocking_findings':[],
            'reviewer':'fixture/independent-reviewer',
            'subjects':[acceptance_index_subject('contract',v) for v in self.values]}
        self.index={'binding_attestations':[]};self.save()
    def save(self):
        path='Plan:fixture/attestation.json';value=raw(self.attestation)
        self.files[path]=value
        self.index['binding_attestations']=[{'path':path,'sha256':digest(value)}]
    def require_file_hash(self,path,expected,where):
        value=self.files.get(path)
        return value if value is not None and digest(value)==expected else None
    def verify(self):return verify_binding_attestations(self,self.index,'contract',self.values)

def main():
    assert Fixture().verify()==2
    cases=[]
    def reject(name,change,save=False):
        fixture=Fixture();change(fixture)
        if save:fixture.save()
        try:fixture.verify()
        except AssertionError as error:cases.append({'case':name,'passed':True,'rejection':str(error)})
        else:raise AssertionError(('invalid binding accepted',name))
    reject('missing_attestation',lambda f:f.index.update(binding_attestations=[]))
    reject('stale_attestation_hash',lambda f:f.index['binding_attestations'][0].update(sha256='0'*64))
    reject('foreign_reviewer_with_valid_hash',lambda f:f.attestation.update(reviewer='fixture/unrelated-reviewer'),True)
    reject('changed_evidence_with_valid_hash',lambda f:f.attestation['subjects'][0].update(evidence_sha256=['0'*64]),True)
    reject('missing_subject_with_valid_hash',lambda f:f.attestation['subjects'].pop(),True)
    reject('self_attestation',lambda f:f.values[0].update(author='fixture/independent-reviewer'))
    reject('duplicate_subject_with_valid_hash',lambda f:f.attestation['subjects'].append(copy.deepcopy(f.attestation['subjects'][0])),True)
    report={'passed':True,'valid_synthetic_subjects':2,'negative_cases':cases,
        'scope':'Isolated exact-attestation validation witnesses; no actual research, contract or product acceptance created.',
        'product_implementation_authorized':False}
    (P/'verification/binding-attestation-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
