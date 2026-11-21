# Capture first-chance Server exceptions during the original B20 sample

Status: **diagnostic source only; not built, imported or executed**. There is no
functional or performance acceptance credit. The source hypothesis concerns a
late response finish during immediate close; this hook does not assert its
cause. The observed gate failure remains 25 passed / 1 failed / 3 unexecuted,
and this preparation changes none of those outcomes.

## Minimal hook

The assembly uses SDK **11.0.100**, `net11.0`, an empty locked dependency graph
and no third-party packages. The
[.NET host startup-hook contract](https://github.com/dotnet/runtime/blob/main/docs/design/features/host-startup-hook.md)
names a namespace-free `StartupHook` with `public static void Initialize()`.
That interface reference is not a claim that this new assembly has executed on
the pinned runtime.

`DOTNET_STARTUP_HOOKS` attaches the hook to the **existing original Debug sample
DLL**. No Entity/Handler/sample/product source or existing binary is rebuilt or
edited. First-chance events are emitted only when the exception stack contains
`NativeWeave.Server.` or the notification stack does. The fallback is explicitly
labelled. The exact expected sample exception message
`Application details stay out of diagnostic output.` is excluded; no blanket
filter hides other application failures.

Each process captures at most **32 events**, with exception type, bounded
message/stack, UTC, PID and managed thread ID on stderr. The hook uses a thread
reentrancy guard and never propagates a diagnostic writer exception into the
sample. Messages are capped at 4096 characters and stacks at 32768 characters;
truncation is explicit. It does not suppress or catch the original business
exception. Startup, event, writer-error and exit markers are distinct:

```text
PERF01_SERVER_HOOK_READY
PERF01_SERVER_FIRST_CHANCE {"number":...,"type":...,"message":...,"stack":...}
PERF01_SERVER_HOOK_ERROR
PERF01_SERVER_HOOK_EXIT {"captured":...,"hook_failures":...,"observed_server_modules":[...]}
PERF01_SERVER_HOOK_EXIT_ERROR
```

The first captured event and normal process exit inspect only the current
process's loaded modules, emitting `libnativeweave_server.so` **basename and
SHA-256**, never its full path. Module lookup failure is recorded separately and
does not discard the exception stack. An absent marker, module error or empty
observation means unavailable; it is not proof that a particular native file
loaded. No other process is enumerated and no external command is launched.
This observation and exception logging can affect scheduling. Every run is
diagnostic-only and cannot enter formal timing/noise.

## Two fixed recipes; root reuses the existing owner

`commands.example.json` contains only the build and sample command shapes. Root
can use the existing regression input validation and unchanged c752
`owner.command(spec, environment, fresh_directory, tree_type)`; no new owner or
general wrapper is introduced. Keep the existing exclusive timing reservation
for the entire finite diagnostic. The owner and public supervision hashes are
pinned in `sources.json`.

1. Bind the actual selected-after producer receipt
   `a4abd107860ed9ca34edc71b45341cd3a68849e541ebaf25e6d5b44c7f77bc7a`, source
   `ccff42c0df4141984ef9de497af7cd768753704a`, and successful actual B18 receipt
   `8b79ac99a39a5870053934abd68a6527fe3f98bbceca000708b1ddbd1229c47d`.
   Reuse its pinned dotnet executable and recorded environment. Proxy values
   may be inherited from the root process **in memory only**; never save them
   in the recipe, receipt environment, source index or logs. Remove any inherited
   startup-hook variable before building, then set exactly this hook for the
   sample process. Preserve the original sample runtime/environment otherwise.
2. Copy the five hook project inputs into a fresh local diagnostic staging
   directory, checking their source hashes. Execute the fixed build command
   with its 180-second owner deadline. It builds only the staged hook. Record
   the resulting DLL, deps/PDB if present, source, SDK and command/log hashes.
3. Execute the existing `server-diagnostics.dll --local` in **fresh owned
   processes**, with one attempt per directory, labels `sample-00` through
   `sample-09`, and a fixed maximum of **10**. The per-process deadline is 90
   seconds. Set only the listed `DOTNET_STARTUP_HOOKS` override. Do not rebuild
   or edit the sample to insert exception handling or alter close timing.
4. After each owner returns, retain both logs and its exit/retirement receipt,
   including a nonzero-exit exception from `owner.command`. Stop on the first
   `PERF01_SERVER_FIRST_CHANCE` event, any sample/owner failure, missing readiness,
   hook-error marker or failed retirement. Do not repeat a failed attempt to
   obtain a favorable result. Otherwise stop after ten complete processes.
5. Record actual sample/runtime binary and native hashes before and after the
   finite batch. The expected Server native hash is
   `1f023b7506bde3f8c4a13b12de92e3e9503004ca3afc2d41a53bec17e44f1d97`.
   Compare any hook-observed module hash to that identity. Preserve the first
   useful stack exactly; a capture is evidence for diagnosis, not proof of the
   proposed race. No capture in ten processes is inconclusive.

Root's populated command/input file belongs outside the public source directory.
It binds actual operational paths, the complete existing sample file inventory,
native input, hook outputs after building and every owner receipt. Keep these
maps, proxy values and raw local-path stacks local. A public diagnostic note may
curate the relevant exception type/message/stack locations and filename-plus-hash
provenance under the existing freeze. This source creates no publication step.
