# Controlled server close-tail diagnostic

Source only; not built or executed. This probe has no performance or functional
acceptance credit. It investigates the late response-completion window behind
the existing B20 `server-diagnostics --local` failure without changing product
code or claiming that the suspected cause has been reproduced.

The same `Program.cs` is used with before `ea5fa528035d025bd7a28698ee7c71194432236c`
and selected after `ccff42c0df4141984ef9de497af7cd768753704a`. Each uses its own
already-built native server library and managed project sources. The previous
unmodified-sample StartupHook run captured no exception in ten successful
processes; that result is inconclusive, not a fix or regression acceptance.

## Controlled path

The probe retains the original sample's explicit ActivityListener, MeterListener,
logging registration, and bounded warning/error sink. Its one strongly typed
`MapRaw("/tail", ["GET"], ...)` handler declares Content-Length 4, awaits
`WriteAsync`, then waits on a deliberately controlled gate. An independent
HttpClient reads and verifies the four bytes over real HTTP/1.1 loopback before
immediately starting `CloseAsync(TimeSpan.FromSeconds(5))`.

The gate releases when the close task completes or a **nominal 100 ms** timer
completes, whichever is observed first. Scheduling can extend actual elapsed
wall time; the emitted timestamp records that fact. This observation does **not**
prove that the native acceptor has joined. The handler then calls
`CompleteAsync()` with its default token, deliberately allowing the native Finish
path to be reached even if the request token was cancelled. The token state is
recorded. This diagnostic choice is not a claim about an equivalent production
workload. Actual exception type, message and stack are captured and rethrown into
the application's normal diagnostics path. Handler completion and the close
result are awaited; a real `DisposeAsync` follows. The existing external owner
bounds the whole process and preserves a stalled disposal as a failure.

`PERF01_SERVER_CLOSE_TAIL` records include UTC and monotonic ticks. A completed
diagnostic may exit zero even after capturing the target handler exception; read
the events, close counters, disposal result and owner receipt together. An
orchestration/disposal exception exits nonzero. No original sample acceptance
assertion is reused for this deliberately different one-request workload.

## Two fixed owner recipes

Use the unchanged c752 recovery owner, its existing supervision module, and the
successful actual B18 toolchain environment. Do not run concurrently with a
measurement or another owner of the existing exclusive timing lock. Use exact
.NET SDK 11.0.100; inherit proxy values only in memory. The public
`commands.example.json` supplies one fixed build recipe and one fixed run recipe,
each applied to both roles with explicit, receipt-bound local substitutions.

1. Create a fresh diagnostic product worktree at the role's exact commit. In it,
   create `samples/api/server-close-tail/`. Copy that role's original
   `samples/api/server-diagnostics/server-diagnostics.csproj` **unchanged**, and
   its `packages.lock.json`, into the new directory. Copy this one `Program.cs`
   into it. Keep the copied project filename: its relative ProjectReference then
   still resolves to `../../../src/Server.Application/NativeWeave.Server.csproj`.
   Record the copies' hashes and product commit; no edits belong in the measured
   product worktrees. Build with `NativeWeaveServerAssetPath` pointing at that
   role's existing receipt-bound `libnativeweave_server.so`; this property is the
   project's actual precompiled-asset input and does not invoke Cargo. Require
   locked restore, use a fresh output tree, and keep the complete build receipt.
2. Before running, inventory the resulting output files, including the probe DLL,
   Core/Server assemblies, runtime/deps configuration, assets manifest and native
   library. Run the resulting Debug net11.0 DLL under the unchanged owner with
   the already-built `server-close-capture-001` hook in `DOTNET_STARTUP_HOOKS`.
   The hook supplies actual loaded native basename/SHA-256 at exit or first
   capture. Require its READY event, no hook error, and the expected role native
   hash. A process killed before that observation has unavailable loaded-module
   evidence, not an assumed match. Save each stdout/stderr, exit, retirement,
   original source/project/lock hashes, hook hash and actual loaded-native hash.
   Use a fresh owned process/output directory per attempt, at most ten attempts
   per role, stopping on the first captured target exception, diagnostic error,
   missing identity, nonzero exit or retirement failure. Do not automatically
   turn this diagnostic into a product acceptance test.

Source, recipes and filename/hash provenance are public candidates. Populated
operational maps and raw exception stacks remain local intermediate evidence;
curate any public failure excerpt and exclude local paths and TLS material.
There is no new wrapper or generalized execution framework here.
