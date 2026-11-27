#!/usr/bin/env python3
"""Copy finite review receipts into Plan; raw archives are tracked separately."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
base = root / 'worktrees/Plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01'
out = base / 'phase-2/recovery-03/ordinary-screen-03'
if (out / 'inventory.json').exists():
    raise SystemExit('Completed checkpoint is immutable; use a fresh name')
out.mkdir(exist_ok=True)
inventory = []
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
def copy(source, name):
    source = root / source
    dest = out / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    inventory.append({'workspaceSource': str(source), 'path': name, 'bytes': dest.stat().st_size, 'sha256': sha(dest)})
ordinary = 'experiments/ordinary-ab-recovery-03-attempt-02'
groups = ['workerd-sqlite', 'workerd-postgresql', 'codec-postgresql', 'sqliteprepare-sqlite', 'relations-sqlite', 'relations-postgresql']
copy(ordinary + '/window.json', 'ordinary/window.json')
for group in groups:
    copy(f'{ordinary}/{group}/summary.json', f'ordinary/{group}.summary.json')
    copy(f'{ordinary}/{group}.plan.json', f'ordinary/{group}.plan.json')
risk = 'experiments/ordinary-risk-recovery-03'
copy(risk + '/window.json', 'risk/window.json')
for group in ['workerd-sqlite-early-stop', 'codec-postgresql-small', 'sqliteprepare-text', 'relations-postgresql-union']:
    copy(f'{risk}/{group}/summary.json', f'risk/{group}.summary.json')
    copy(f'{risk}/{group}.plan.json', f'risk/{group}.plan.json')
for filename in ['sqlite-rounds-01.json', 'remaining-groups-rounds-01.json']:
    copy('observations/worker-d-ordinary-review/' + filename, 'independent-review/' + filename)
copy('experiments/relations-recovery-03/review-ordinary-ab.md', 'independent-review/relations.md')
copy('experiments/relations-recovery-03/review-ordinary-ab.json', 'independent-review/relations.json')
copy('observations/worker-d-ready-scheduling-aot-mask-fixed/receipt.json', 'correctness/worker-d-mask-fixed-aot.json')
copy('observations/builds/worker-d-compiler-profile-comparison.json', 'identity/worker-d-native-compiler-profile.json')
copy('experiments/relations-recovery-03/candidate-diagnostic/comparison.json', 'mechanism/relations-both-databases.json')
copy('experiments/relations-recovery-03/ordinary/input-identity.json', 'identity/relations-ordinary.json')
sample = 'experiments/codec-recovery-03/sampled-small-03'
copy(sample + '/attribution-summary.json', 'sampling/attribution-summary.json')
copy(sample + '/sampling-summary.json', 'sampling/summary.json')
for name in ['r1-money1-prepared-baseline', 'r1-money1-prepared-candidate']:
    copy(f'{sample}/{name}-analysis/hot-00.objdump.txt', f'sampling/{name}.RhSpinWait.objdump.txt')
    copy(f'{sample}/{name}.window.json', f'sampling/{name}.window.json')
    copy(f'{sample}/{name}-sample-identity.json', f'sampling/{name}.identity.json')
for helper in ['run_causal_ab.py', 'run_screening_window.py', 'run_risk_screening.py', 'profile_existing_consumers.py', 'checkpoint_ordinary_screen.py']:
    copy('local-tools/' + helper, 'local-only-tools/' + helper)
(out / 'inventory.json').write_text(json.dumps({'capturedUtc': datetime.now(timezone.utc).isoformat(), 'files': inventory,
    'rawArchiveStatus': 'Complete raw results, observers, traces and exact candidate ELFs remain in the named workspace; foundation archive and experiment archive are in progress. These summaries do not substitute for raw bytes.'}, indent=2) + '\n')
status = json.loads((base / 'status.json').read_text())
status.update(captured_utc=datetime.now(timezone.utc).isoformat(),
    state='recovery_03_ordinary_screens_and_targeted_risks_complete_mechanism_and_combined_gates_next',
    resume='phase-2/recovery-03/ordinary-screen-03/README.md', product_integration_completed=False,
    new_final_cells_completed=0, final_cells_completed=0)
(base / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
live = base / 'live-recovery.md'
live.write_text('## Recovery 03 ordinary and risk screens complete\n\n'
    'Read [the current checkpoint](phase-2/recovery-03/ordinary-screen-03/README.md). '
    'Corrected full Worker-D AOT passed; six ordinary groups and four targeted risk groups completed. '
    'Separate current-ELF samples passed identity/loss/coverage checks. '
    'The main product branch is still unchanged; Worker-D causal markers and next relation allocation scopes are active. '
    'Final campaign remains 0/4. No performance CI is added.\n\n---\n\n' + live.read_text())
print(json.dumps({'checkpoint': str(out), 'copiedFiles': len(inventory)}))
