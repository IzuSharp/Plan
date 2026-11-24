#!/usr/bin/env python3
"""Check the rename task and preserve complete preceding execution evidence."""
from pathlib import Path
import copy
import json
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FROZEN = '85f7f83e29e67f6865c14c64585139541b8a1a1f'
BASELINES = {'Korda': 'ea72031db6f9111a31c6f743b5babc345f96862d',
             'NativeWeave-Design': 'fcc2b3599066a467ce3d8bf52e4753bdeea6cd86',
             'Plan': FROZEN}
PREFIX = 'ledger/evidence/batches/DB-Rename-01/'


def validate(current):
    assert current['task'] == 'DB-Rename-01' and current['branch'] == 'task/DB-Rename-01-linux'
    assert current['platforms'] == ['linux-x64'] and current['source_main'] == BASELINES
    assert current['status'] in {'in_progress', 'blocked', 'awaiting_review'}
    assert current['stop_condition'] == 'passing_pr_checks_awaiting_maintainer_review'
    assert current['merge_authorized'] is False and current['publication_authorized'] is False
    assert current['plan'] == PREFIX + 'plan.md' and current['handoff'] == PREFIX + 'handoff-linux.md'


def main():
    graph = json.loads((ROOT / 'delivery-graph.json').read_text())
    old = json.loads(subprocess.check_output(['git', 'show', FROZEN + ':delivery-graph.json'], cwd=ROOT))
    for key, value in old.items():
        if key not in {'current_execution', 'completed_executions'}:
            assert graph[key] == value, 'Historical graph field changed: ' + key
    assert graph['completed_executions'] == {**old['completed_executions'], 'DB-API-01': old['current_execution']}
    validate(graph['current_execution'])
    protected = ['ledger/evidence/batches/DB-API-01', 'ledger/evidence/batches/DB-CPP-01',
                 'ledger/evidence/batches/DB-Scope-01', 'research-graph.json', 'documentation-graph.json',
                 'source-driven-baseline.json', 'tasks', 'fragments', 'research-tasks',
                 'documentation-tasks', 'verification', 'tools/verify_db_api.py',
                 'tools/verify_db_cpp.py', 'tools/verify_db_cpp_negative.py', 'tools/verify_db_scope.py']
    changed = subprocess.check_output(['git', 'diff', '--name-only', FROZEN, '--', *protected],
                                      cwd=ROOT, text=True)
    assert not changed.strip(), 'Historical accepted inputs changed: ' + changed
    for name in ('plan.md', 'handoff-linux.md'):
        path = ROOT / PREFIX / name
        assert not re.search(r'\bWeave(?:Table|Column|Key|Version|Ignore|Projection|Constructor|Parameter|Codec|UseCodec)(?:Attribute)?\b', path.read_text())
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            assert (path.parent / target.split('#', 1)[0]).is_file(), 'Broken link: ' + target
    invalid = []
    bad = copy.deepcopy(graph['current_execution']); bad['source_main']['Korda'] = '0' * 40; invalid.append(bad)
    bad = copy.deepcopy(graph['current_execution']); bad['merge_authorized'] = True; invalid.append(bad)
    bad = copy.deepcopy(graph['current_execution']); bad['publication_authorized'] = True; invalid.append(bad)
    bad = copy.deepcopy(graph['current_execution']); bad['status'] = 'accepted'; invalid.append(bad)
    for bad in invalid:
        try:
            validate(bad)
        except AssertionError:
            continue
        raise AssertionError('Invalid current task accepted')
    with tempfile.TemporaryDirectory(prefix='db-rename-history-', dir=ROOT.parent) as temp:
        work = Path(temp) / 'Plan'
        subprocess.run(['git', 'worktree', 'add', '--detach', str(work), FROZEN], cwd=ROOT, check=True)
        try:
            subprocess.run(['python3', 'tools/verify_db_api.py', '--require-complete'], cwd=work, check=True)
        finally:
            subprocess.run(['git', 'worktree', 'remove', '--force', str(work)], cwd=ROOT, check=True)
    print(json.dumps({'task': 'DB-Rename-01', 'document_gate': 'passed',
                      'negative_controls': len(invalid), 'history': 'passed_at_immutable_input',
                      'product_execution_claimed': False}, indent=2))


if __name__ == '__main__':
    main()
