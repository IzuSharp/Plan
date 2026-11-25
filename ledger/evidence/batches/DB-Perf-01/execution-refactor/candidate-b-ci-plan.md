# Initial candidate B: actual CI selection

The first integrated product commit is `dc82792c519ee90be30f5c49b2f785ecd33ad915`. The worktree was clean after committing 72 reviewed files. The required command was executed without changing its selection rules:

```sh
python3 eng/ci/impact.py origin/main --output artifacts/plan.json
```

The retained [actual plan](candidate-b-ci-plan.json) compares the **whole open PR** with main `e063f2eb6e2e857e3f19f96bf263cae372651a27`; it does not compare only this round with `f0078da7`. Consequently some reasons belong to the preceding authorized commits already in PR #37.

| Selected scope | Why it is selected | Existing checks |
| --- | --- | --- |
| `interop` | The open PR contains the earlier `Interop.Async` result/retirement changes and their tests. The new isolated scheduler experiments are not part of B. | `interop.async` |
| `linux` | C++ Host/provider/query/contracts, native binding extensions, shared managed parameters/streaming, package inventory and their tests changed. Their shared dependency edges also cover transaction, migration, relation and Fluent consumers. Existing public/API-reference edits elsewhere in the PR retain their normal API checks. | Native build and dependency graph; shared managed build/API; retained full database regressions; Fluent, API tool, migrations and relations API checks |
| `postgresql` | PostgreSQL includes the changed shared database/native modules and has real provider fixture changes. | Independent provider build/dependencies/test, one top-level package, packed DLL/API checks, actual AOT package consumer and public metadata validation |
| `sqlite` | SQLite includes the same changed shared modules and its real provider fixture changes. | The corresponding independent provider build/dependencies/test, package, packed API, AOT consumption and metadata validation |

Both public checks are selected with the existing PR version `0.1.0-ci.1`. Their package/input fingerprints are in the JSON plan. Main publication remains governed by each package's actual changed inputs and the existing release rule; this PR plan has no release rows and is not itself a publication receipt.

The registered `database-perf-probes` and `db-perf-benchmarks` owners explain benchmark source paths but select **no execution actions**. Their historical workflow copies are archival inputs under `benchmarks/`, not runnable `.github/workflows` entries. This commit adds no workflow, job, button, schedule or benchmark invocation to a correctness/release script. New result-extension files, native test helpers and Dapper phase sources fall under existing registered directory owners and require no new module.

There is no unexplained selected scope or missing provider consumer in this plan. Any later production or scheduler edit requires rerunning the same command and retaining its new plan. Selection is not execution: exact candidate correctness, package-consumption and CI results will be recorded separately.
