#!/usr/bin/env python3
"""Normalize the actual scoped review formats without inventing review decisions."""
ACCEPT = {'accepted', 'accept_research_design', 'recommend_accept_research_design',
          'recommend_accept_research_and_detailed_design'}
BLOCKERS = ('open_blocking_findings', 'unresolved_blocking_findings',
            'remaining_blocking_findings', 'blocking_findings')

def review_pins(report):
    pins = {}
    def add(path, value):
        assert isinstance(path, str) and ':' in path, path
        assert path not in pins or pins[path] == value, ('conflicting review input', path)
        pins[path] = value
    for path, value in report.get('review_inputs_sha256', {}).items():
        add(path, value)
    for key in ('reviewed_inputs', 'reviewed_outputs', 'supporting_inputs'):
        for row in report.get(key, []):
            path = row['path']
            if ':' not in path:
                path = row['repository'].split('/')[-1]+':'+path
            add(path, row['sha256'])
    return pins

def decision_for(report, kind, identity):
    assert report.get('decision') in ACCEPT, ('report not accepted', identity)
    present = [key for key in BLOCKERS if key in report]
    assert present and all(report[key] == [] for key in present), ('report blocked', identity)
    key = 'contract_reviews' if kind == 'contract' else ('task_reviews' if 'task_reviews' in report else 'task_decisions')
    rows = report.get(key, [])
    assert isinstance(rows, list), key
    found = [row for row in rows if row.get('id', row.get('task_id')) == identity]
    assert len(found) == 1 and found[0].get('decision') in ACCEPT, ('subject not reviewed/accepted', identity)
    return found[0]

def required_paths(checker, kind, value):
    if kind == 'contract':
        task = checker.nodes[value['documentation_task_id']]
        own = {'NativeWeave-Design:'+value['spec_path']}
        required = set(own)
        for dep in value['dependencies']:
            contract = checker.contracts[(dep['id'], dep['version'])]
            required.add('NativeWeave-Design:'+contract['spec_path'])
    else:
        task = value
        own = set(task['outputs']) | {'Plan:'+task['prompt']}
        required = set(own)
    for identity in task.get('research_refs', [])+task.get('documentation_refs', []):
        required.update(checker.nodes[identity]['outputs'])
    for pin in task.get('contract_inputs', []):
        contract = checker.contracts[(pin['id'], pin['version'])]
        required.add('NativeWeave-Design:'+contract['spec_path'])
    assert not any(path.startswith('NativeWeave:') for path in required)
    return own, required

def verify_scoped_review(checker, report, kind, value):
    identity = value['id']
    decision = decision_for(report, kind, identity)
    pins = review_pins(report)
    own, required = required_paths(checker, kind, value)
    assert own <= set(pins), (identity, 'missing reviewed input paths', sorted(own-set(pins)))
    for path in own | (required & set(pins)):
        assert checker.require_file_hash(path, pins[path], identity+'/actual-review-input') is not None, path
    if kind == 'contract':
        assert decision['version'] == value['version']
        assert decision['spec_path'] == value['spec_path']
        assert decision['content_sha256'] == value['content_sha256']
    else:
        if 'packet_sha256' in decision:
            assert decision['packet_sha256'] == value['packet_sha256']
        for key, expected in decision.get('semantic_node_projection', {}).items():
            assert value.get(key) == expected, (identity, 'reviewed task semantics changed', key)
    return own, required
