# A02 cold-import finite diagnostic evidence

See [the diagnosis](../../source-a02-cold-import.md) for the conclusion, exact upstream ownership path and prospective candidate gates. No runtime implementation was changed by this investigation.

| Directory/file | Retained content |
| --- | --- |
| `original-a02/` | Original verifier commands/result, source identities, toolchain and native artifact metadata; original acceptance remains failed |
| `exact-reproduction/` | Same prebuilt executable/argv/CPU mask, actual -11 receipt and empty output |
| `trace-unavailable/` | strace launch failure caused by denied ptrace; no native stack obtained |
| `controls-001/`, `source-001/` | Plain-.NET initial cold/serial/warm/pointer/JIT controls; exact source, project, lock and actual results |
| `controls-002/`, `source-002/` | Late load/install/CWT controls; exact source/project/lock and actual results |
| `controls-003/`, `source-003/` | Eight-callback forced overlap, borrowed versus owned versus owned after unlink; exact source/project/lock/runner and actual results |
| `upstream-provenance.json`, `locked-ilcompiler.nuspec` | Exact upstream Git blob/SHA-256 provenance and actual installed compiler source/version/license binding |
| `review.json` | Hashes and original locations of all verbatim copies, execution/review scope and retention limits |

All controls are finite correctness diagnostics. In particular, `run.py` returning zero means the commands were collected, not that the borrowed case passed. Its per-command receipt records the borrowed process's expected investigative -11 failure. The original failed A02 receipt is not rewritten by any successful control.

## Reproduce the decisive control

Use the locked SDK 11.0.100 / Linux x64 Native AOT closure recorded in the lockfile and a rebuilt or retained exact A02 alpha fixture. The following commands are a reproduction template: choose fresh absolute work/output paths, supply an existing exact-version package cache, and preserve every mode's stdout/stderr/exit status. The retained `source-003/run.py` is the exact runner used in the original workspace and deliberately refuses to overwrite its recorded output.

```sh
# Set these paths for a fresh reproduction, then source the pinned environment.
source "$PERF01_ROOT/perf01-toolchain/env.sh"
export CARGO_BUILD_JOBS=3
mkdir "$PERF01_REPRO"
cp "$PERF01_PLAN/ledger/evidence/batches/Perf-01/checks/a02-cold-import-001/source-003/Program.cs" "$PERF01_REPRO/"
cp "$PERF01_PLAN/ledger/evidence/batches/Perf-01/checks/a02-cold-import-001/source-003/ImportRace.csproj" "$PERF01_REPRO/"
cp "$PERF01_PLAN/ledger/evidence/batches/Perf-01/checks/a02-cold-import-001/source-003/global.json" "$PERF01_REPRO/"
cp "$PERF01_PLAN/ledger/evidence/batches/Perf-01/checks/a02-cold-import-001/source-003/packages.linux-x64.aot.lock.json" "$PERF01_REPRO/"
cd "$PERF01_REPRO"
taskset -c 2,3 "$DOTNET_ROOT/dotnet" restore ImportRace.csproj --locked-mode -r linux-x64 -p:PublishAot=true -p:UseSharedCompilation=false -nr:false -m:1 -p:RestorePackagesPath="$PERF01_NUGET_CACHE"
taskset -c 2,3 "$DOTNET_ROOT/dotnet" publish ImportRace.csproj -c Release -r linux-x64 -p:PublishAot=true --no-restore -o "$PERF01_REPRO/aot" -p:UseSharedCompilation=false -nr:false -m:1 -p:RestorePackagesPath="$PERF01_NUGET_CACHE"
# Run each in a fresh process. A nonzero borrowed result is diagnostic evidence;
# retain it and continue to the owned controls instead of claiming a suite pass.
taskset -c 2,3 "$PERF01_REPRO/aot/ImportRace" borrowed "$PERF01_ALPHA_FIXTURE" "$PERF01_REPRO/borrowed-fixture" --require-aot
taskset -c 2,3 "$PERF01_REPRO/aot/ImportRace" owned "$PERF01_ALPHA_FIXTURE" "$PERF01_REPRO/owned-fixture" --require-aot
taskset -c 2,3 "$PERF01_REPRO/aot/ImportRace" owned-unlink "$PERF01_ALPHA_FIXTURE" "$PERF01_REPRO/unlinked-fixture" --require-aot
```

The original alpha fixture SHA-256 is `f40d6b9d44948562385b1174fee671212de40190dc5d6488f3423ef6dad87194`; the original AOT control is `30631326517134ee550097f95d3d1805a56a512c25ea0589eebcc2bf5cc7c267`. Rebuilt executable hashes can differ with output paths; record the actual bytes and do not substitute these identities. The archived project contains the original cache path, so the explicit `RestorePackagesPath` override above is required when reproducing elsewhere. It changes only the package location, with the lockfile still enforcing the exact dependency closure.
