# Epoch-002 Inspect preparation cache review

**Verdict: ACCEPT this exact preparation-only source delta for actual execution.**
No restore, build, target-module import, profile or service was executed in this
independent review. The previous layered-profile review remains applicable to
the unchanged probe and measurement logic.

| Input | Identity |
| --- | --- |
| Prepared Plan source | `c2478587e1fe46f5277cc2ccb133ce3d14b0d631` |
| Profile source index | `ccea3bd075bbd088b5d013cd8f86ffdcbd8afdc4a882293aad2edb8df82e923d` |
| `profile.py` | `55fddb02388c06d5b0c4ddfa46c5dbc13f037825b29a4521398d09fe3a787763` |
| Unchanged measurement index | `a71deb1272c3b29dd1573e5dacfccc0c53db01d72807dd091b4b78e18456728b` |

Independent inspection of both actual codec assets files and caches found
**six external package/version directories per role**. Three archive identities
were already in each role's build binding; the other three are exact-version
runtime-download entries in the bound assets file, with current archive
snapshots explicitly distinguished from earlier build-bound evidence. Actual
archives match the [recorded identity projection](inspect-preparation-cache-review.json).
No `NativeWeave.*` directory enters the fallback view.

The original preparer still creates a fresh writable cache and copies the
same role's two project packages into its own verified local feed. This
separation matters: the official [NuGet environment-variable reference](https://learn.microsoft.com/en-us/nuget/reference/cli-reference/cli-ref-environment-variables)
and [fallback folder reference](https://learn.microsoft.com/en-us/nuget/reference/nuget-config-file#fallbackpackagefolders-section),
read on 2026-11-21, document fallback-package lookup before source downloads.
Project package exclusion preserves the copied candidate feed as the source
for the product under test.

Only `inspect-prepare` receives the fallback environment variable. A `finally`
block restores the original environment before every Inspect probe, including
on preparation failure. Source cleanliness, exact product/manifest/native
checks, no-Rust traps, original command ownership and the three independent
Inspect process counts remain. Shared, PostgreSQL and protocol profile paths
are unchanged. All four current indexed source hashes match, and the new
caller parses as Python AST without execution.

This is existing-cache reuse. It does not establish a pristine-machine restore,
new signature validation or a new complete extracted-payload inventory.
Runtime-download snapshots retain their explicit prior-binding limitation.
NuGet audit, TLS, proxy and package source settings are unchanged; an audit
endpoint can still fail. Root must retain the first actual restore result and
original logs. Source acceptance supplies no numeric result or long-test credit.
