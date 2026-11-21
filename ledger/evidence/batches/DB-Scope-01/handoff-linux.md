# DB-Scope-01 Linux handoff

## Current checkpoint

- Active task: **DB-Scope-01**, Linux x64; branch `task/DB-Scope-01-linux` in all three repositories.
- Sequence: old PR closure and local cleanup complete; initial Plan is being committed/pushed for its PR. **No Design or product changes yet.**
- Continue from this file and the DB-Scope-01 PRs. Do not delete this new workspace, repeat completed cleanup, resume Perf-01, or relabel historical evidence.
- Read [plan.md](plan.md), [baseline.json](baseline.json), [acceptance.json](acceptance.json) and `delivery-graph.json.current_execution`.

## Completed stop/cleanup

Product PR19 and Plan PR23 were observed open and closed without merge on 2026-11-21, with an explicit scope-reduction/Perf-01 termination comment. Dependabot PRs 3/4/7 were untouched. The sole old completion automation `Automation_5cee7a136e348191bbefc5b2f398a189` was already disabled. No current old subagent or task process was found. 42 old worktrees, three old repository caches, old builds/native binaries/performance datasets/temporary databases/scripts and old task toolchain copies were removed. Exact deletion targets and post-deletion checks are in [cleanup-linux.json](cleanup-linux.json). System/account data and unrelated projects were preserved.

Only the current Linux execution host is exposed in this session. No other Linux/MCP/SSH connection was discovered, so no claim is made that inaccessible hosts were stopped. User systemd bus inspection is unavailable; no cron configuration or task-owned unit was found. Old Plan run [44902123431](https://github.com/IzuSharp/Plan/actions/runs/44902123431) still reported in progress after PR closure. The GitHub connector has no cancellation action and the browser is signed out; cancellation is unconfirmed and will be rechecked. No new old-branch writer or workload was started.

## Fresh main inputs

- Plan: `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2`.
- Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Product: `ea5fa528035d025bd7a28698ee7c71194432236c`.
- Local task root: `/workspace/scratch/6c5fd6ee7a2b/.worktree/DB-Scope-01-linux/`.
- New validation tools/caches will be prepared under `_validation/`; they are not old Perf-01 artifacts.

## Next actions

1. Verify/publish initial Plan and create Plan PR; record URL/commit here.
2. Prune Design current authority and preserve historical acceptance gates.
3. Prune product, migrate unique mixed database tests, reconcile packaging and CI.
4. Run real provider regressions and all four independent package JIT/AOT cells.
5. Review, merge required PRs, check merged-main CI, update final evidence, then stop.
