# Exact independent candidate build inputs

`build_public_inputs.py` adapts the retained command-completion build driver for
one clean, already published producer checkout. Supply its full commit and tree
IDs, one provider, a new output directory outside that checkout and the pinned
PostgreSQL binary directory. Source the retained task-local tool environment
before invoking it. This script is local evidence tooling, not a CI action.

It verifies the actual diff/module plan before building. The expected scopes
are interop, Linux correctness and the two independently checked provider
packages; the selected provider is built in this checkout. The output contains
the source-bound native manifest, native correctness logs, independent public
NuGet package and receipt, real package-consumption result, and ordinary
external Release Native AOT phase and mixed-workload consumers. It does not run
the benchmark consumers or earn performance credit. Existing repository drivers
own all builds, tests, packaging and consumption. The PostgreSQL wrapper starts
and stops its own isolated server in the same process namespace.

Every stage is logged before execution and records its argv, times, exit status,
log hash and unchanged-source check. Failure leaves those bytes intact; choose
a fresh attempt directory. Consumer builds isolate their NuGet application
packages and have no product project references. Build-only .NET concurrency
and NuGet audit settings are recorded and are not measurement environment
settings. Exact package and native identities remain in the normal producer and
consumer receipts; later input freezing binds them to the actual measured ELFs.

The script's complete CI-plan assertion is intentionally strict. If the actual
plan changes, stop and explain the selection before adapting this local driver.
Do not modify the repository's CI routing to satisfy an obsolete assertion.
